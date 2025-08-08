"""
Example usage of the scalable web scraper.
"""

import asyncio
import json
from typing import List
from .config import ScraperConfig
from .scraper import ScalableWebScraper, scrape_urls, scrape_single_url


async def basic_scraping_example():
    """Basic example of scraping a few URLs."""
    print("=== Basic Scraping Example ===")
    
    # Create configuration
    config = ScraperConfig(
        max_urls=10,
        max_depth=2,
        concurrency=5,
        delay=0.5
    )
    
    # URLs to scrape
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com"
    ]
    
    # Scrape URLs
    results = await scrape_urls(urls, config)
    
    # Print results
    for url, result in results.items():
        print(f"\nURL: {url}")
        print(f"Success: {result.success}")
        print(f"Title: {result.title[:100]}...")
        print(f"Links found: {len(result.links)}")
        if result.error:
            print(f"Error: {result.error}")


async def domain_specific_config_example():
    """Example with domain-specific configuration."""
    print("\n=== Domain-Specific Configuration Example ===")
    
    config = ScraperConfig(
        max_urls=20,
        max_depth=2,
        concurrency=3,
        domain_configs={
            'example.com': {
                'delay': 1.0,  # Slower for example.com
                'max_urls': 5
            },
            'quotes.toscrape.com': {
                'delay': 0.2,  # Faster for quotes site
                'max_urls': 15
            }
        }
    )
    
    urls = [
        "https://example.com",
        "https://quotes.toscrape.com",
        "https://httpbin.org/html"
    ]
    
    results = await scrape_urls(urls, config)
    
    for url, result in results.items():
        print(f"\nURL: {url}")
        print(f"Success: {result.success}")
        print(f"Processing time: {result.processing_time:.2f}s")


async def s3_storage_example():
    """Example using S3 storage backend."""
    print("\n=== S3 Storage Example ===")
    
    config = ScraperConfig(
        max_urls=5,
        storage_backend='s3',
        storage_config={
            'bucket_name': 'my-scraping-bucket',
            'aws_access_key_id': 'your-access-key',
            'aws_secret_access_key': 'your-secret-key',
            'region_name': 'us-east-1'
        }
    )
    
    urls = ["https://example.com"]
    
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        # Get storage stats
        storage_stats = await scraper.get_storage_stats()
        print(f"Storage stats: {storage_stats}")


async def javascript_fallback_example():
    """Example showing JavaScript rendering fallback."""
    print("\n=== JavaScript Fallback Example ===")
    
    config = ScraperConfig(
        max_urls=3,
        use_playwright_fallback=True,
        playwright_timeout=30
    )
    
    # URLs that might need JavaScript
    urls = [
        "https://quotes.toscrape.com/js",  # JavaScript-heavy site
        "https://httpbin.org/html",        # Simple HTML
        "https://example.com"              # Basic site
    ]
    
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            print(f"\nURL: {url}")
            print(f"Success: {result.success}")
            print(f"Used Playwright: {result.used_playwright}")
            if result.error:
                print(f"Error: {result.error}")


async def custom_extraction_example():
    """Example with custom content extraction."""
    print("\n=== Custom Extraction Example ===")
    
    from .extractors import ContentExtractor, LinkExtractor
    
    class CustomContentExtractor(ContentExtractor):
        def extract_title(self, html: str) -> str:
            # Custom title extraction logic
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE)
            return title_match.group(1).strip() if title_match else ""
        
        def extract_content(self, html: str) -> str:
            # Custom content extraction logic
            import re
            # Remove scripts and styles
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
            
            # Extract text from body
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
            if body_match:
                content = body_match.group(1)
                # Remove HTML tags
                content = re.sub(r'<[^>]+>', ' ', content)
                # Clean whitespace
                content = re.sub(r'\s+', ' ', content)
                return content.strip()
            return ""
        
        def extract_metadata(self, html: str) -> dict:
            # Custom metadata extraction
            metadata = {}
            import re
            
            # Extract meta description
            desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html)
            if desc_match:
                metadata['description'] = desc_match.group(1)
            
            return metadata
    
    config = ScraperConfig(
        max_urls=2,
        extract_metadata=True
    )
    
    urls = ["https://example.com"]
    
    async with ScalableWebScraper(config) as scraper:
        # Replace the default extractor with custom one
        scraper.content_extractor = CustomContentExtractor()
        
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            print(f"\nURL: {url}")
            print(f"Title: {result.title}")
            print(f"Content length: {len(result.content)}")
            print(f"Metadata: {result.metadata}")


async def performance_monitoring_example():
    """Example showing performance monitoring."""
    print("\n=== Performance Monitoring Example ===")
    
    config = ScraperConfig(
        max_urls=50,
        max_depth=3,
        concurrency=10,
        delay=0.1
    )
    
    urls = [
        "https://quotes.toscrape.com",
        "https://httpbin.org/html",
        "https://example.com"
    ]
    
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        # Get performance stats
        stats = scraper.get_stats()
        
        print("Performance Statistics:")
        print(f"Total URLs scraped: {stats['total_scraped']}")
        print(f"Failed URLs: {stats['total_failed']}")
        print(f"Total links found: {stats['total_links_found']}")
        print(f"Runtime: {stats['runtime_seconds']:.2f} seconds")
        print(f"URLs per second: {stats['urls_per_second']:.2f}")
        print(f"Playwright fallbacks: {stats['playwright_fallbacks']}")
        print(f"Playwright fallback rate: {stats['playwright_fallback_rate']:.2%}")


async def robots_txt_example():
    """Example showing robots.txt compliance."""
    print("\n=== Robots.txt Compliance Example ===")
    
    config = ScraperConfig(
        max_urls=5,
        respect_robots_txt=True,
        user_agent="MyBot/1.0"
    )
    
    urls = [
        "https://example.com",
        "https://httpbin.org/robots.txt",  # This site has robots.txt
        "https://quotes.toscrape.com"
    ]
    
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            print(f"\nURL: {url}")
            print(f"Success: {result.success}")
            if result.error == "Blocked by robots.txt":
                print("Blocked by robots.txt")
            elif result.error:
                print(f"Error: {result.error}")


async def example_same_domain_only():
    """Example: Scrape only links from the same domain as the parent URL."""
    print("\n=== Same Domain Only Example ===")
    
    # Create configuration with same_domain_only enabled
    config = ScraperConfig(
        max_depth=2,
        max_urls=50,
        same_domain_only=True,  # Only follow links from the same domain
        extract_links=True
    )
    
    # URLs to start scraping from
    start_urls = [
        "https://example.com/page1",
        "https://example.com/page2"
    ]
    
    # Scrape URLs - will only follow links within example.com
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(start_urls)
        
        print(f"Scraped {len(results)} URLs")
        for url, result in results.items():
            if result.success:
                print(f"✓ {url} - {len(result.links)} links found")
            else:
                print(f"✗ {url} - {result.error}")
        
        # Get statistics
        stats = scraper.get_stats()
        print(f"\nStatistics:")
        print(f"Total scraped: {stats['total_scraped']}")
        print(f"Total failed: {stats['total_failed']}")
        print(f"Total links found: {stats['total_links_found']}")


async def beautifulsoup_link_extraction_example():
    """Example demonstrating BeautifulSoup-based link extraction."""
    print("\n=== BeautifulSoup Link Extraction Example ===")
    
    from utils import extract_links_from_html
    
    # Test HTML with various link types
    test_html = """
    <!DOCTYPE html>
    <html>
    <body>
        <!-- Standard anchor links -->
        <a href="https://example.com/page1">Page 1</a>
        <a href="/relative/page2">Relative Page</a>
        
        <!-- Data attributes -->
        <div data-href="https://example.com/page3">Page 3</div>
        
        <!-- Iframe sources -->
        <iframe src="https://example.com/embed/page4"></iframe>
        
        <!-- Form actions -->
        <form action="https://example.com/submit" method="post">
            <input type="text" name="search">
        </form>
        
        <!-- Links to ignore -->
        <a href="#section1">Anchor</a>
        <a href="javascript:void(0)">JavaScript</a>
        <a href="mailto:test@example.com">Email</a>
    </body>
    </html>
    """
    
    base_url = "https://example.com/current-page"
    
    # Extract links using BeautifulSoup
    links = extract_links_from_html(test_html, base_url)
    
    print("Extracted links:")
    for link in sorted(links):
        print(f"  ✓ {link}")
    
    print(f"\nTotal links found: {len(links)}")
    print("Note: JavaScript, mailto, and anchor links are filtered out")


async def force_rescrape_example():
    """Example demonstrating force_rescrape functionality."""
    print("\n=== Force Rescrape Example ===")
    
    # Create configuration with force_rescrape enabled
    config = ScraperConfig(
        max_urls=5,
        force_rescrape=True,  # Force rescraping even if URLs already exist
        extract_links=False   # Disable link extraction for this example
    )
    
    # URLs to scrape
    urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    print("First scraping run:")
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            if result.success:
                print(f"✓ {url} - Status: {result.status_code}")
            else:
                print(f"✗ {url} - Error: {result.error}")
    
    print("\nSecond scraping run (with force_rescrape=True):")
    # Run the same URLs again - they should be rescraped
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            if result.success:
                print(f"✓ {url} - Status: {result.status_code} (rescraped)")
            else:
                print(f"✗ {url} - Error: {result.error}")
    
    print("\nThird scraping run (with force_rescrape=False):")
    # Run with force_rescrape disabled - should skip existing URLs
    config.force_rescrape = False
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            if result.success:
                print(f"✓ {url} - Status: {result.status_code}")
            else:
                print(f"✗ {url} - Error: {result.error}")


async def postgresql_storage_example():
    """Example using PostgreSQL storage backend."""
    print("\n=== PostgreSQL Storage Example ===")
    
    # Note: This requires PostgreSQL server running and asyncpg installed
    try:
        config = ScraperConfig(
            max_urls=5,
            storage_backend='postgresql',
            storage_config={
                # Option 1: Using connection URL
                'database_url': 'postgresql://postgres:password@localhost:5432/webscraper'
                
                # Option 2: Using individual parameters
                # 'host': 'localhost',
                # 'port': 5432,
                # 'database': 'webscraper',
                # 'user': 'postgres',
                # 'password': 'password'
            }
        )
        
        urls = ["https://example.com", "https://httpbin.org/html"]
        
        print("Scraping with PostgreSQL storage...")
        async with ScalableWebScraper(config) as scraper:
            results = await scraper.scrape_urls(urls)
            
            for url, result in results.items():
                if result.success:
                    print(f"✅ {url} - {result.title}")
                else:
                    print(f"❌ {url} - {result.error}")
            
            # Get storage stats (PostgreSQL-specific features)
            stats = await scraper.get_storage_stats()
            print(f"\nPostgreSQL Storage Stats:")
            print(f"  Total pages: {stats.get('total_pages', 0)}")
            print(f"  Database size: {stats.get('database_size', 'Unknown')}")
            print(f"  Recent pages: {stats.get('recent_pages', 0)}")
            
            # Demonstrate PostgreSQL-specific features
            if hasattr(scraper.storage, 'get_pages_by_domain'):
                domain_pages = await scraper.storage.get_pages_by_domain('example.com', limit=10)
                print(f"  Pages from example.com: {len(domain_pages)}")
            
            if hasattr(scraper.storage, 'delete_old_pages'):
                # This would delete pages older than 365 days (just for demo)
                # deleted_count = await scraper.storage.delete_old_pages(365)
                # print(f"  Old pages cleaned up: {deleted_count}")
                print("  Cleanup available via delete_old_pages() method")
    
    except ImportError:
        print("❌ PostgreSQL storage requires 'asyncpg' package")
        print("   Install with: pip install asyncpg")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("   Make sure PostgreSQL is running and credentials are correct")


async def time_based_rescraping_example():
    """Example demonstrating time-based re-scraping functionality."""
    print("\n=== Time-Based Re-scraping Example ===")
    
    # Create configuration with time-based re-scraping
    config = ScraperConfig(
        max_urls=10,
        rescrape_after_months=3,  # Re-scrape pages older than 3 months
        # rescrape_after_days=30,  # Alternative: re-scrape pages older than 30 days
        extract_links=True,
        same_domain_only=True
    )
    
    urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    print("First scraping run (will scrape all URLs):")
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            if result.success:
                print(f"✅ {url} - {result.title}")
            else:
                print(f"❌ {url} - {result.error}")
    
    print("\nSecond scraping run (will skip recent pages):")
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        scraped_count = len([r for r in results.values() if r.success and r.content])
        print(f"Pages actually scraped: {scraped_count} (should be 0 for recent pages)")
    
    print("\nTesting with short threshold (should re-scrape):")
    config_short = ScraperConfig(
        max_urls=10,
        rescrape_after_days=0,  # Re-scrape immediately (for testing)
        extract_links=False
    )
    
    async with ScalableWebScraper(config_short) as scraper:
        results = await scraper.scrape_urls(urls)
        
        scraped_count = len([r for r in results.values() if r.success and r.content])
        print(f"Pages scraped with 0-day threshold: {scraped_count} (should re-scrape all)")
    
    # Show page ages
    print("\nPage age information:")
    from vdl_tools.webscraping.storage import SQLiteStorage
    from vdl_tools.webscraping.utils import get_page_age_info
    
    storage = SQLiteStorage()
    for url in urls:
        page = await storage.get_page(url)
        if page:
            age_info = get_page_age_info(page.scraped_at)
            print(f"  {url}: {age_info['human_readable']}")
    await storage.close()


async def improved_error_handling_example():
    """Example demonstrating improved error handling and retry logic."""
    print("\n=== Improved Error Handling Example ===")
    
    # Create configuration with retry logic and realistic user agent
    config = ScraperConfig(
        max_urls=3,
        retries=2,  # Retry failed requests up to 2 times
        delay=1.0,  # Base delay between retries
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # URLs that might have 403 issues
    urls = [
        "https://www.radiantnuclear.com/blog/about",  # This was failing with 403
        "https://example.com",
        "https://httpbin.org/status/403"  # Test URL that returns 403
    ]
    
    print("Testing with improved error handling:")
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        for url, result in results.items():
            print(f"\nURL: {url}")
            print(f"Success: {result.success}")
            print(f"Status Code: {result.status_code}")
            print(f"Processing Time: {result.processing_time:.2f}s")
            if result.error:
                print(f"Error: {result.error}")
            elif result.success:
                print(f"Title: {result.title[:50]}...")
                print(f"Content Length: {len(result.content)} chars")


def run_all_examples():
    """Run all examples."""
    async def main():
        await basic_scraping_example()
        await domain_specific_config_example()
        await javascript_fallback_example()
        await custom_extraction_example()
        await performance_monitoring_example()
        await robots_txt_example()
        await example_same_domain_only()
        await beautifulsoup_link_extraction_example()
        await force_rescrape_example()
        await time_based_rescraping_example()
        await improved_error_handling_example()
        
        # Storage backend examples (require external services)
        # await s3_storage_example()  # Requires AWS credentials
        # await postgresql_storage_example()  # Requires PostgreSQL server
    
    asyncio.run(main())


if __name__ == "__main__":
    run_all_examples() 