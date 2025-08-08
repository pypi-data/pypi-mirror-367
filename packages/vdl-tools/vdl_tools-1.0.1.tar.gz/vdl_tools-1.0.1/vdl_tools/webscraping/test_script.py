import asyncio
from vdl_tools.webscraping import ScalableWebScraper, ScraperConfig
from vdl_tools.shared_tools.tools.config_utils import get_configuration

async def advanced_scraping():
    # Configuration for crawling with link discovery
    config = ScraperConfig(
        max_urls=None,         # Total URLs to scrape
        max_urls_per_domain=100,
        max_depth=10,          # How deep to follow links
        concurrency=10,       # Concurrent requests
        delay=0.2,           # Delay between requests
        extract_links=True,   # Enable link discovery
        same_domain_only=True, # Only follow links within same domain
        use_playwright_fallback=True,
        storage_backend='postgresql',
        storage_config=get_configuration()['postgres'],
        rescrape_after_days=30,

    )

    # Starting URLs
    start_urls = [
        "https://www.radiantnuclear.com",
        "https://vibrantdatalabs.org",
        "https://www.vibrantdatalabs.org",
        "https://emersoncollective.com",
        "https://emersoncollective.org",
        ""
    ]
    
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(start_urls)
        
        # Get statistics
        stats = scraper.get_stats()
        print(f"Scraped {stats['total_scraped']} URLs")
        print(f"Found {stats['total_links_found']} total links")
        
        # Process results
        for url, result in results.items():
            if result.success:
                print(f"✅ {url} - {result.title}")

asyncio.run(advanced_scraping())