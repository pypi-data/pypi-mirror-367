#!/usr/bin/env python3
"""
Test script to demonstrate automatic Playwright setup.
"""

import asyncio
from vdl_tools.webscraping import ScalableWebScraper, ScraperConfig, ensure_playwright_setup


def test_manual_setup():
    """Test manual Playwright setup."""
    print("Testing manual Playwright setup...")
    
    if ensure_playwright_setup():
        print("✅ Playwright setup successful!")
        return True
    else:
        print("❌ Playwright setup failed!")
        return False


async def test_automatic_setup():
    """Test automatic setup through scraper initialization."""
    print("\nTesting automatic Playwright setup through scraper...")
    
    config = ScraperConfig(
        use_playwright_fallback=True,
        max_urls=1,
        max_depth=0
    )
    
    scraper = ScalableWebScraper(config)
    
    try:
        await scraper.initialize()
        
        if scraper.config.use_playwright_fallback and scraper.browser:
            print("✅ Scraper with Playwright initialized successfully!")
            success = True
        elif not scraper.config.use_playwright_fallback:
            print("⚠️  Scraper initialized without Playwright (fallback to HTTP-only)")
            success = True
        else:
            print("❌ Scraper initialization failed!")
            success = False
            
        await scraper.cleanup()
        return success
        
    except Exception as e:
        print(f"❌ Error during scraper test: {e}")
        return False


async def main():
    """Run all tests."""
    print("VDL Tools Webscraping - Playwright Setup Test")
    print("=" * 50)
    
    # Test manual setup
    manual_ok = test_manual_setup()
    
    # Test automatic setup
    auto_ok = await test_automatic_setup()
    
    print("\n" + "=" * 50)
    if manual_ok and auto_ok:
        print("🎉 All tests passed! Playwright is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nTo manually install Playwright browsers, run:")
        print("    python -m playwright install chromium")
        print("\nOn Linux, you may also need:")
        print("    python -m playwright install-deps")


if __name__ == "__main__":
    asyncio.run(main())
