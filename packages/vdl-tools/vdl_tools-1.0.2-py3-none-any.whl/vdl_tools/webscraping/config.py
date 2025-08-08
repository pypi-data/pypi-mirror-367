"""
Configuration module for the scalable web scraper.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
import asyncio


@dataclass
class ScraperConfig:
    """
    Configuration for the scalable web scraper.

    Attributes:
        max_depth: Maximum depth for recursive crawling
        max_urls: Maximum total URLs to scrape
        max_urls_per_domain: Maximum URLs per domain
        concurrency: Number of concurrent requests
        timeout: Request timeout in seconds
        retries: Number of retries for failed requests
        delay: Delay between requests in seconds
        user_agent: User agent string
        respect_robots_txt: Whether to respect robots.txt
        use_playwright_fallback: Whether to use Playwright as fallback
        playwright_timeout: Playwright timeout in seconds
        storage_backend: Storage backend type ('sqlite', 's3', etc.)
        storage_config: Configuration for storage backend
        domain_configs: Per-domain configuration overrides
        allowed_domains: List of allowed domains (None for all)
        blocked_domains: List of blocked domains
        allowed_content_types: List of allowed content types
        max_content_size: Maximum content size in bytes
        extract_links: Whether to extract and follow links
        extract_images: Whether to extract image URLs
        extract_metadata: Whether to extract metadata
        same_domain_only: Whether to restrict links to the same domain as parent URL
        force_rescrape: Whether to rescrape URLs even if they already exist in storage
        rescrape_after_days: Rescrape pages older than X days (None = disabled)
        rescrape_after_months: Rescrape pages older than X months (None = disabled)
        use_browser_headers: Whether to use browser-like headers (disable if causing issues)
    """
    
    # Crawling limits
    max_depth: int = 3
    max_urls: int = None # None for no limit
    max_urls_per_domain: int = 100

    # Performance settings
    concurrency: int = 10
    timeout: int = 30
    retries: int = 3
    delay: float = 0.1
    retry_delay: float = 2.0  # Base delay for retries (exponential backoff)

    # Request settings
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    respect_robots_txt: bool = True

    # JavaScript rendering
    use_playwright_fallback: bool = True
    playwright_timeout: int = 30
    
    # Storage
    storage_backend: str = "sqlite"
    storage_config: Dict = field(default_factory=dict)

    # Domain filtering
    domain_configs: Dict[str, Dict] = field(default_factory=dict)
    allowed_domains: Optional[List[str]] = None
    blocked_domains: List[str] = field(default_factory=list)

    # Content filtering
    allowed_content_types: List[str] = field(default_factory=lambda: [
        "text/html", "application/xhtml+xml", "text/plain"
    ])
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    
    # Extraction settings
    extract_links: bool = True
    extract_images: bool = False
    extract_metadata: bool = True
    same_domain_only: bool = True  # Only follow links from the same domain as parent URL
    
    # Storage behavior
    force_rescrape: bool = False  # Whether to rescrape URLs even if they already exist in storage
    rescrape_after_days: Optional[int] = None  # Rescrape pages older than X days (None = disabled)
    rescrape_after_months: Optional[int] = None  # Rescrape pages older than X months (None = disabled)
    
    # Request behavior
    use_browser_headers: bool = True  # Whether to use browser-like headers

    def get_domain_config(self, domain: str) -> Dict:
        """Get configuration for a specific domain."""
        return self.domain_configs.get(domain, {})

    def is_domain_allowed(self, domain: str) -> bool:
        """Check if a domain is allowed to be scraped."""
        if domain in self.blocked_domains:
            return False
        
        if self.allowed_domains is None:
            return True
        
        return domain in self.allowed_domains
    
    def get_delay_for_domain(self, domain: str) -> float:
        """Get delay for a specific domain."""
        domain_config = self.get_domain_config(domain)
        return domain_config.get('delay', self.delay)
    
    def get_concurrency_for_domain(self, domain: str) -> int:
        """Get concurrency for a specific domain."""
        domain_config = self.get_domain_config(domain)
        return domain_config.get('concurrency', self.concurrency)


@dataclass
class DomainConfig:
    """Configuration for a specific domain."""
    delay: float = 0.1
    concurrency: int = 5
    max_depth: int = 3
    max_urls: int = 100
    use_playwright: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_extractors: Dict[str, str] = field(default_factory=dict)


def create_config_from_dict(config_dict: Dict) -> ScraperConfig:
    """Create a ScraperConfig from a dictionary."""
    return ScraperConfig(**config_dict)


def load_config_from_file(file_path: str) -> ScraperConfig:
    """Load configuration from a JSON or YAML file."""
    import json
    import yaml
    
    with open(file_path, 'r') as f:
        if file_path.endswith('.json'):
            config_dict = json.load(f)
        elif file_path.endswith(('.yml', '.yaml')):
            config_dict = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported config file format. Use JSON or YAML.")
    
    return create_config_from_dict(config_dict) 