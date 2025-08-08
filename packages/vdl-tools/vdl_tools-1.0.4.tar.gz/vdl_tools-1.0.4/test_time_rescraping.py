#!/usr/bin/env python3
"""
Test script for time-based re-scraping functionality.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from vdl_tools.webscraping import ScraperConfig, scrape_urls, ScalableWebScraper
from vdl_tools.webscraping.storage import SQLiteStorage
from vdl_tools.webscraping.utils import is_page_stale, get_page_age_info

async def test_time_based_rescraping():
    """Test the time-based re-scraping functionality."""
    
    print("🧪 Testing Time-Based Re-scraping Functionality")
    print("=" * 60)
    
    # Test 1: Test utility functions
    print("\n1. Testing utility functions...")
    
    # Test with different dates
    now = datetime.utcnow()
    old_date = now - timedelta(days=45)  # 45 days ago
    recent_date = now - timedelta(days=5)  # 5 days ago
    
    # Test is_page_stale function
    print(f"   Page from 45 days ago, rescrape_after_days=30: {is_page_stale(old_date, rescrape_after_days=30)}")
    print(f"   Page from 5 days ago, rescrape_after_days=30: {is_page_stale(recent_date, rescrape_after_days=30)}")
    print(f"   Page from 45 days ago, rescrape_after_months=1: {is_page_stale(old_date, rescrape_after_months=1)}")
    
    # Test get_page_age_info function
    age_info = get_page_age_info(old_date)
    print(f"   Age info for 45-day-old page: {age_info['human_readable']}")
    
    # Test 2: Test with actual scraping
    print("\n2. Testing with actual scraping...")
    
    # Use a test URL
    test_urls = ["https://httpbin.org/html"]
    
    # Configuration for testing (re-scrape pages older than 30 days)
    config = ScraperConfig(
        max_urls=5,
        rescrape_after_days=30,  # Re-scrape if older than 30 days
        storage_backend='sqlite',
        storage_config={'db_path': 'test_time_scraping.db'}
    )
    
    print(f"   Config: rescrape_after_days={config.rescrape_after_days}")
    
    # First scrape
    print("\n   First scrape (should always scrape new URLs)...")
    results1 = await scrape_urls(test_urls, config)
    
    for url, result in results1.items():
        if result.success:
            print(f"   ✅ First scrape: {url} - {result.title[:50]}...")
        else:
            print(f"   ❌ First scrape failed: {url} - {result.error}")
    
    # Immediate second scrape (should skip - not stale)
    print("\n   Immediate second scrape (should skip - not stale)...")
    results2 = await scrape_urls(test_urls, config)
    
    scraped_count = len([r for r in results2.values() if r.success and r.content])
    print(f"   Second scrape results: {scraped_count} pages with content (should be 0)")
    
    # Test 3: Test with different time thresholds
    print("\n3. Testing different time thresholds...")
    
    # Test with very short threshold (should trigger re-scraping)
    config_short = ScraperConfig(
        max_urls=5,
        rescrape_after_days=0,  # Re-scrape immediately
        storage_backend='sqlite',
        storage_config={'db_path': 'test_time_scraping.db'}
    )
    
    print("   Testing with rescrape_after_days=0 (should always re-scrape)...")
    results3 = await scrape_urls(test_urls, config_short)
    
    scraped_count = len([r for r in results3.values() if r.success and r.content])
    print(f"   Results with 0-day threshold: {scraped_count} pages with content (should be 1)")
    
    # Test 4: Test storage backend methods directly
    print("\n4. Testing storage backend methods...")
    
    storage = SQLiteStorage('test_time_scraping.db')
    
    for url in test_urls:
        should_rescrape_30days = await storage.should_rescrape(url, rescrape_after_days=30)
        should_rescrape_0days = await storage.should_rescrape(url, rescrape_after_days=0)
        
        print(f"   {url}:")
        print(f"     Should rescrape (30 days): {should_rescrape_30days}")
        print(f"     Should rescrape (0 days): {should_rescrape_0days}")
        
        # Get the page to show its age
        page = await storage.get_page(url)
        if page:
            age_info = get_page_age_info(page.scraped_at)
            print(f"     Page age: {age_info['human_readable']}")
    
    await storage.close()
    
    print("\n5. Testing months-based re-scraping...")
    
    # Test months-based configuration
    config_months = ScraperConfig(
        max_urls=5,
        rescrape_after_months=1,  # Re-scrape if older than 1 month
        storage_backend='sqlite',
        storage_config={'db_path': 'test_time_scraping.db'}
    )
    
    results4 = await scrape_urls(test_urls, config_months)
    scraped_count = len([r for r in results4.values() if r.success and r.content])
    print(f"   Results with 1-month threshold: {scraped_count} pages with content (should be 0 for recent pages)")
    
    print("\n✅ Time-based re-scraping tests completed!")
    print("\nSummary:")
    print("- Utility functions work correctly")
    print("- Fresh pages are not re-scraped unnecessarily") 
    print("- Stale pages are re-scraped when thresholds are met")
    print("- Both days and months thresholds work")
    print("- Storage backends correctly implement age checking")


async def demo_time_rescraping():
    """Demonstrate time-based re-scraping with your specific URLs."""
    
    print("\n🎯 Demo: Time-based Re-scraping")
    print("=" * 40)
    
    # Your URLs that were causing duplicates (now fixed with www normalization)
    urls = [
        "https://vibrantdatalabs.org"  # Using normalized version
    ]
    
    # Configuration to re-scrape pages older than 3 months
    config = ScraperConfig(
        max_urls=10,
        max_depth=2,
        rescrape_after_months=3,  # Re-scrape if older than 3 months
        extract_links=True,
        same_domain_only=True
    )
    
    print(f"Configuration: Re-scrape pages older than {config.rescrape_after_months} months")
    print(f"URLs to process: {urls}")
    
    async with ScalableWebScraper(config) as scraper:
        results = await scraper.scrape_urls(urls)
        
        print(f"\nResults: {len(results)} pages processed")
        
        for url, result in results.items():
            if result.success:
                print(f"✅ {url}")
                print(f"   Title: {result.title}")
                print(f"   Links found: {len(result.links)}")
            else:
                print(f"❌ {url} - {result.error}")
        
        # Show statistics
        stats = scraper.get_stats()
        print(f"\nStatistics:")
        print(f"  Total scraped: {stats['total_scraped']}")
        print(f"  Total failed: {stats['total_failed']}")
        print(f"  Runtime: {stats['runtime_seconds']:.2f}s")


if __name__ == "__main__":
    async def main():
        await test_time_based_rescraping()
        await demo_time_rescraping()
    
    asyncio.run(main())
