"""
VDL Tools - Scalable Web Scraping Module

A high-performance, scalable web scraper with support for:
- Queue-based architecture with configurable depth and URL limits
- Fast HTML scraping with httpx
- JavaScript rendering with Playwright as fallback
- Link discovery and recursive crawling
- Cloud-deployable with Docker support
- Modular and extensible architecture
"""

from vdl_tools.webscraping.scraper import ScalableWebScraper
from vdl_tools.webscraping.config import ScraperConfig
from vdl_tools.webscraping.storage import StorageBackend, S3Storage, SQLiteStorage, PostgreSQLStorage
from vdl_tools.webscraping.extractors import ContentExtractor, LinkExtractor
from vdl_tools.webscraping.queue_manager import ScrapingQueue
from vdl_tools.webscraping.utils import url_normalize, is_valid_url
from vdl_tools.webscraping.playwright_setup import ensure_playwright_setup, get_setup_instructions

__version__ = "1.0.0"

__all__ = [
    "ScalableWebScraper",
    "ScraperConfig", 
    "StorageBackend",
    "S3Storage",
    "SQLiteStorage",
    "PostgreSQLStorage",
    "ContentExtractor",
    "LinkExtractor",
    "ScrapingQueue",
    "url_normalize",
    "is_valid_url",
    "ensure_playwright_setup",
    "get_setup_instructions",
]
