"""
Main scalable web scraper implementation.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional, Set, Any, Callable
from dataclasses import dataclass
import logging
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from vdl_tools.webscraping.config import ScraperConfig
from vdl_tools.webscraping.queue_manager import ScrapingQueue, DomainRateLimiter
from vdl_tools.webscraping.storage import StorageBackend, ScrapedPage, create_storage_backend
from vdl_tools.webscraping.extractors import create_content_extractor, create_link_extractor
from vdl_tools.webscraping.utils import (
        url_normalize, is_valid_url, extract_domain, check_robots_txt,
        is_allowed_by_robots, get_content_type_from_headers, is_html_content,
        rate_limit_delay
    )
from vdl_tools.webscraping.playwright_setup import ensure_playwright_setup, get_setup_instructions



@dataclass
class ScrapingResult:
    """Represents a result of a scraping operation."""
    
    url: str
    success: bool
    status_code: int = 0
    content_type: str = ""
    title: str = ""
    content: str = ""
    html: str = ""
    links: List[str] = None
    images: List[str] = None
    metadata: Dict[str, Any] = None
    error: str = ""
    processing_time: float = 0.0
    used_playwright: bool = False
    parent_url: str = ""
    
    def __post_init__(self):
        if self.links is None:
            self.links = []
        if self.images is None:
            self.images = []
        if self.metadata is None:
            self.metadata = {}


class ScalableWebScraper:
    """
    Scalable web scraper with support for:
    - Queue-based architecture
    - Fast HTML scraping with httpx
    - JavaScript rendering with Playwright as fallback
    - Link discovery and recursive crawling
    - Modular storage backends
    - Rate limiting and robots.txt support
    """
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.queue = ScrapingQueue()
        self.rate_limiter = DomainRateLimiter()
        self.storage = None
        self.content_extractor = None
        self.link_extractor = None
        self.session = None
        self.playwright = None
        self.browser = None
        self.robots_cache = {}
        self.stats = {
            'total_scraped': 0,
            'total_failed': 0,
            'total_links_found': 0,
            'playwright_fallbacks': 0,
            'start_time': time.time()
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize the scraper."""
        # Initialize storage
        self.storage = create_storage_backend(
            self.config.storage_backend,
            **self.config.storage_config
        )
        
        # Initialize extractors
        self.content_extractor = create_content_extractor(use_beautifulsoup=True)
        self.link_extractor = create_link_extractor(use_beautifulsoup=True)
        
        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(
            limit=self.config.concurrency * 2,
            limit_per_host=self.config.concurrency,
            ttl_dns_cache=300
        )
        
        # Headers configuration
        if self.config.use_browser_headers:
            # Browser-like headers to avoid detection
            default_headers = {
                'User-Agent': self.config.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        else:
            # Simple headers - just user agent
            default_headers = {
                'User-Agent': self.config.user_agent,
            }
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=default_headers
        )
        
        # Initialize Playwright if needed
        if self.config.use_playwright_fallback:
            try:
                # Ensure Playwright browsers are installed
                if not ensure_playwright_setup():
                    logging.warning(f"Failed to setup Playwright automatically. {get_setup_instructions()}")
                    # Continue without Playwright - will fallback to HTTP-only scraping
                    raise Exception("Failed to setup Playwright automatically. Please install Playwright manually.")
                else:
                    self.playwright = await async_playwright().start()
                    self.browser = await self.playwright.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-dev-shm-usage']
                    )
            except Exception as e:
                logging.warning(f"Failed to initialize Playwright: {e}. {get_setup_instructions()}")
                self.config.use_playwright_fallback = False
        
        # Setup rate limiting
        for domain, domain_config in self.config.domain_configs.items():
            self.rate_limiter.set_delay(domain, domain_config.get('delay', self.config.delay))
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        if self.storage:
            await self.storage.close()
    
    async def scrape_urls(self, urls: List[str], max_depth: int = None) -> Dict[str, ScrapingResult]:
        """
        Scrape a list of URLs with recursive link discovery.
        
        Args:
            urls: List of URLs to scrape
            max_depth: Maximum depth for recursive crawling
            
        Returns:
            Dictionary mapping URLs to scraping results
        """
        if max_depth is None:
            max_depth = self.config.max_depth
        
        # Add initial URLs to queue
        for url in urls:
            await self.queue.add_url(url, depth=0)
        
        results = {}
        workers = []
        
        # Start worker tasks
        for _ in range(self.config.concurrency):
            worker = asyncio.create_task(self._worker(max_depth, results))
            workers.append(worker)
        
        # Wait for all workers to complete
        await asyncio.gather(*workers, return_exceptions=True)
        
        return results
    
    async def _worker(self, max_depth: int, results: Dict[str, ScrapingResult]):
        """Worker task for processing URLs from the queue."""
        consecutive_empty = 0
        max_consecutive_empty = 3  # Exit after 3 consecutive empty checks
        
        while True:
            # Get next URL from queue
            task = await self.queue.get_next_url()
            
            if task is None:
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    # Queue is likely empty, exit worker
                    break
                # Brief pause before checking again
                await asyncio.sleep(0.1)
                continue
            
            # Reset consecutive empty counter
            consecutive_empty = 0
            
            # Check limits
            if self.config.max_urls and (self.stats['total_scraped'] >= self.config.max_urls or
                task.depth > max_depth):
                continue
            
            # Check domain limits
            domain_stats = self.queue.get_domain_stats(task.domain)
            if domain_stats['processed'] >= self.config.max_urls_per_domain:
                continue
            
            # Rate limiting
            await self.rate_limiter.wait_if_needed(task.domain)
            
            # Scrape the URL
            result = await self._scrape_single_url(task)
            results[task.url] = result
            
            if result.success:
                self.stats['total_scraped'] += 1
                
                # Store result
                page = ScrapedPage(
                    url=task.url,
                    title=result.title,
                    content=result.content,
                    html=result.html,
                    status_code=result.status_code,
                    content_type=result.content_type,
                    links=result.links,
                    images=result.images,
                    metadata=result.metadata,
                    depth=task.depth,
                    parent_url=task.parent_url
                )
                await self.storage.store_page(page)
                
                # Add discovered links to queue
                if task.depth < max_depth and self.config.extract_links:
                    await self._add_discovered_links(result.links, task.depth + 1, task.url)
            else:
                self.stats['total_failed'] += 1
                self.queue.mark_failed(task.url)
    
    async def _scrape_single_url(self, task) -> ScrapingResult:
        """Scrape a single URL."""
        start_time = time.time()
        result = ScrapingResult(url=task.url, success=False, parent_url=task.parent_url)

        try:
            # Check if already scraped (unless force_rescrape is enabled or page is stale)
            if not self.config.force_rescrape:
                # Check if page should be re-scraped based on age
                should_rescrape = await self.storage.should_rescrape(
                    task.url, 
                    self.config.rescrape_after_days,
                    self.config.rescrape_after_months
                )
                
                if not should_rescrape:
                    self.logger.info(f"URL already scraped and not stale: {task.url}")
                    return result
                elif await self.storage.page_exists(task.url):
                    self.logger.info(f"Re-scraping stale URL: {task.url}")
                else:
                    self.logger.info(f"Scraping new URL: {task.url}")
            
            # Check robots.txt
            if self.config.respect_robots_txt:
                domain = extract_domain(task.url)
                if domain not in self.robots_cache:
                    self.robots_cache[domain] = await check_robots_txt(domain, self.config.user_agent)
                
                robots_parser = self.robots_cache[domain]
                if robots_parser and not is_allowed_by_robots(robots_parser, task.url, self.config.user_agent):
                    result.error = "Blocked by robots.txt"
                    return result
            
            # Try HTTP scraping first
            http_result = await self._scrape_with_http(task.url, parent_url=task.parent_url)
            
            if http_result.success:
                result = http_result
            elif self.config.use_playwright_fallback:
                # Fallback to Playwright
                self.logger.info(f"HTTP scraping failed, trying Playwright: {task.url}")
                playwright_result = await self._scrape_with_playwright(task.url, parent_url=task.parent_url)
                if playwright_result.success:
                    result = playwright_result
                    result.used_playwright = True
                    self.stats['playwright_fallbacks'] += 1
                else:
                    result.error = f"HTTP failed: {http_result.error}, Playwright failed: {playwright_result.error}"
            else:
                result.error = http_result.error
            
        except Exception as e:
            result.error = str(e)
            self.logger.error(f"Error scraping {task.url}: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    async def _scrape_with_http(self, url: str, parent_url: str) -> ScrapingResult:
        """Scrape URL using HTTP client with retry logic."""
        result = ScrapingResult(url=url, success=False, parent_url=parent_url)
        
        # Retry logic for failed requests
        for attempt in range(self.config.retries + 1):
            try:
                # Add referer header if we have a parent URL
                headers = {}
                if parent_url:
                    headers['Referer'] = parent_url
                
                async with self.session.get(url, headers=headers) as response:
                    result.status_code = response.status
                    result.content_type = get_content_type_from_headers(response.headers)
                    
                    if response.status == 200:
                        # Check content type
                        if not is_html_content(result.content_type):
                            result.error = f"Unsupported content type: {result.content_type}"
                            return result
                        
                        # Check content size
                        content_length = response.headers.get('content-length')
                        if content_length and int(content_length) > self.config.max_content_size:
                            result.error = f"Content too large: {content_length} bytes"
                            return result
                        
                        # Read content
                        html = await response.text()
                        result.html = html
                        
                        # Extract content
                        result.title = self.content_extractor.extract_title(html)
                        result.content = self.content_extractor.extract_content(html)
                        result.metadata = self.content_extractor.extract_metadata(html)
                        
                        # Extract links and images
                        if self.config.extract_links:
                            result.links = list(self.link_extractor.extract_links(html, url))
                            self.stats['total_links_found'] += len(result.links)
                        
                        if self.config.extract_images:
                            result.images = list(self.link_extractor.extract_images(html, url))
                        
                        result.success = True
                        return result
                    
                    elif response.status == 403:
                        # 403 errors - don't retry as it usually means the site is blocking us
                        result.error = f"HTTP 403 (Forbidden) - site may be blocking automated requests"
                        self.logger.warning(f"HTTP 403 for {url} - site may be blocking automated requests")
                        return result
                    
                    else:
                        result.error = f"HTTP {response.status}"
                        return result
                        
            except asyncio.TimeoutError:
                if attempt < self.config.retries:
                    delay = (2 ** attempt) * self.config.delay
                    self.logger.warning(f"Timeout for {url}, retrying in {delay}s (attempt {attempt + 1}/{self.config.retries + 1})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    result.error = "Request timeout"
                    return result
                    
            except Exception as e:
                if attempt < self.config.retries:
                    delay = (2 ** attempt) * self.config.delay
                    self.logger.warning(f"Error for {url}: {e}, retrying in {delay}s (attempt {attempt + 1}/{self.config.retries + 1})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    result.error = str(e)
                    return result
        
        return result
    
    async def _scrape_with_playwright(self, url: str, parent_url: str) -> ScrapingResult:
        """Scrape URL using Playwright."""
        result = ScrapingResult(url=url, success=False, parent_url=parent_url)
        
        try:
            page = await self.browser.new_page()
            
            # Set user agent
            await page.set_extra_http_headers({'User-Agent': self.config.user_agent})
            
            # Navigate to page
            response = await page.goto(url, timeout=self.config.playwright_timeout * 1000)
            
            if not response:
                result.error = "No response from Playwright"
                await page.close()
                return result
            
            result.status_code = response.status
            result.content_type = response.headers.get('content-type', '')
            
            if response.status != 200:
                result.error = f"HTTP {response.status}"
                await page.close()
                return result
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Get HTML content
            html = await page.content()
            result.html = html
            
            # Extract content
            result.title = self.content_extractor.extract_title(html)
            result.content = self.content_extractor.extract_content(html)
            result.metadata = self.content_extractor.extract_metadata(html)
            
            # Extract links and images
            if self.config.extract_links:
                result.links = list(self.link_extractor.extract_links(html, url))
                self.stats['total_links_found'] += len(result.links)
            
            if self.config.extract_images:
                result.images = list(self.link_extractor.extract_images(html, url))
            
            result.success = True
            await page.close()
            
        except Exception as e:
            result.error = str(e)
            self.logger.error(f"Playwright error for {url}: {e}")
        
        return result
    
    async def _add_discovered_links(self, links: List[str], depth: int, parent_url: str):
        """Add discovered links to the queue."""
        # Extract parent domain if same_domain_only is enabled
        parent_domain = None
        if self.config.same_domain_only and parent_url:
            parent_domain = extract_domain(parent_url)
        
        for link in links:
            # Validate URL
            if not is_valid_url(link):
                continue
            
            # Check domain restrictions
            domain = extract_domain(link)
            if not self.config.is_domain_allowed(domain):
                continue
            
            # Check same domain restriction if enabled
            if self.config.same_domain_only and parent_domain and domain != parent_domain:
                continue
            
            # Add to queue
            await self.queue.add_url(link, depth=depth, parent_url=parent_url)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics."""
        queue_stats = self.queue.get_stats()
        runtime = time.time() - self.stats['start_time']
        
        return {
            **self.stats,
            **queue_stats,
            'runtime_seconds': runtime,
            'urls_per_second': self.stats['total_scraped'] / runtime if runtime > 0 else 0,
            'playwright_fallback_rate': (
                self.stats['playwright_fallbacks'] / self.stats['total_scraped']
                if self.stats['total_scraped'] > 0 else 0
            )
        }
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if self.storage:
            return await self.storage.get_stats()
        return {'error': 'Storage not initialized'}


# Convenience functions
async def scrape_urls(urls: List[str], config: ScraperConfig = None) -> Dict[str, ScrapingResult]:
    """Convenience function to scrape URLs."""
    if config is None:
        config = ScraperConfig()
    
    async with ScalableWebScraper(config) as scraper:
        return await scraper.scrape_urls(urls)


async def scrape_single_url(url: str, config: ScraperConfig = None) -> ScrapingResult:
    """Convenience function to scrape a single URL."""
    if config is None:
        config = ScraperConfig()
    
    async with ScalableWebScraper(config) as scraper:
        await scraper.initialize()
        task = type('Task', (), {'url': url, 'depth': 0, 'parent_url': None})()
        result = await scraper._scrape_single_url(task)
        await scraper.cleanup()
        return result 