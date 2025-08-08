"""
Command-line interface for the scalable web scraper.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from .config import ScraperConfig, load_config_from_file
from .scraper import ScalableWebScraper, scrape_urls


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="VDL Tools - Scalable Web Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scraping
  python -m vdl_tools.webscraping.cli https://example.com https://quotes.toscrape.com

  # With configuration file
  python -m vdl_tools.webscraping.cli --config config.json urls.txt

  # High-performance scraping
  python -m vdl_tools.webscraping.cli --max-urls 1000 --concurrency 50 urls.txt

  # Save results to JSON
  python -m vdl_tools.webscraping.cli --output results.json urls.txt

  # Re-scrape pages older than 30 days
  python -m vdl_tools.webscraping.cli --rescrape-after-days 30 urls.txt

  # Re-scrape pages older than 3 months
  python -m vdl_tools.webscraping.cli --rescrape-after-months 3 urls.txt

  # Use PostgreSQL storage
  python -m vdl_tools.webscraping.cli --storage-backend postgresql \\
    --postgres-host localhost --postgres-database webscraper urls.txt

  # Use PostgreSQL with connection URL
  python -m vdl_tools.webscraping.cli --storage-backend postgresql \\
    --postgres-url postgresql://user:pass@localhost:5432/webscraper urls.txt
        """
    )
    
    # Input arguments
    parser.add_argument(
        'urls',
        nargs='*',
        help='URLs to scrape (can also be provided in a file with --urls-file)'
    )
    parser.add_argument(
        '--urls-file',
        help='File containing URLs (one per line)'
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        help='Configuration file (JSON or YAML)'
    )
    
    # Basic settings
    parser.add_argument(
        '--max-urls',
        type=int,
        default=100,
        help='Maximum number of URLs to scrape (default: 100)'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum depth for recursive crawling (default: 3)'
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=10,
        help='Number of concurrent requests (default: 10)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between requests in seconds (default: 0.1)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    # JavaScript support
    parser.add_argument(
        '--use-playwright',
        action='store_true',
        help='Use Playwright for JavaScript rendering'
    )
    parser.add_argument(
        '--playwright-timeout',
        type=int,
        default=30,
        help='Playwright timeout in seconds (default: 30)'
    )
    
    # Storage
    parser.add_argument(
        '--storage-backend',
        choices=['sqlite', 'postgresql', 'postgres', 's3', 'file'],
        default='sqlite',
        help='Storage backend (default: sqlite)'
    )
    parser.add_argument(
        '--db-path',
        default='scraped_pages.db',
        help='SQLite database path (default: scraped_pages.db)'
    )
    parser.add_argument(
        '--s3-bucket',
        help='S3 bucket name (for S3 storage backend)'
    )
    parser.add_argument(
        '--file-path',
        default='scraped_pages',
        help='File storage path (default: scraped_pages)'
    )
    
    # PostgreSQL options
    parser.add_argument(
        '--postgres-url',
        help='PostgreSQL connection URL (e.g., postgresql://user:pass@host:port/db)'
    )
    parser.add_argument(
        '--postgres-host',
        default='localhost',
        help='PostgreSQL host (default: localhost)'
    )
    parser.add_argument(
        '--postgres-port',
        type=int,
        default=5432,
        help='PostgreSQL port (default: 5432)'
    )
    parser.add_argument(
        '--postgres-database',
        default='webscraper',
        help='PostgreSQL database name (default: webscraper)'
    )
    parser.add_argument(
        '--postgres-user',
        default='postgres',
        help='PostgreSQL username (default: postgres)'
    )
    parser.add_argument(
        '--postgres-password',
        help='PostgreSQL password'
    )
    
    # Output
    parser.add_argument(
        '--output',
        help='Output file for results (JSON format)'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Only show statistics, not detailed results'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    # Behavior
    parser.add_argument(
        '--no-robots',
        action='store_true',
        help='Do not respect robots.txt'
    )
    parser.add_argument(
        '--extract-links',
        action='store_true',
        default=True,
        help='Extract and follow links (default: True)'
    )
    parser.add_argument(
        '--extract-images',
        action='store_true',
        help='Extract image URLs'
    )
    parser.add_argument(
        '--extract-metadata',
        action='store_true',
        default=True,
        help='Extract metadata (default: True)'
    )
    
    # Time-based re-scraping
    parser.add_argument(
        '--rescrape-after-days',
        type=int,
        help='Re-scrape pages older than X days'
    )
    parser.add_argument(
        '--rescrape-after-months',
        type=int,
        help='Re-scrape pages older than X months'
    )
    
    return parser.parse_args()


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a file."""
    urls = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def create_config_from_args(args) -> ScraperConfig:
    """Create configuration from command line arguments."""
    if args.config:
        return load_config_from_file(args.config)
    
    # Build storage config
    storage_config = {}
    if args.storage_backend == 'sqlite':
        storage_config['db_path'] = args.db_path
    elif args.storage_backend in ('postgresql', 'postgres'):
        if args.postgres_url:
            storage_config['database_url'] = args.postgres_url
        else:
            storage_config.update({
                'host': args.postgres_host,
                'port': args.postgres_port,
                'database': args.postgres_database,
                'user': args.postgres_user,
                'password': args.postgres_password or ''
            })
    elif args.storage_backend == 's3':
        storage_config['bucket_name'] = args.s3_bucket
    elif args.storage_backend == 'file':
        storage_config['base_path'] = args.file_path
    
    return ScraperConfig(
        max_urls=args.max_urls,
        max_depth=args.max_depth,
        concurrency=args.concurrency,
        delay=args.delay,
        timeout=args.timeout,
        use_playwright_fallback=args.use_playwright,
        playwright_timeout=args.playwright_timeout,
        storage_backend=args.storage_backend,
        storage_config=storage_config,
        respect_robots_txt=not args.no_robots,
        extract_links=args.extract_links,
        extract_images=args.extract_images,
        extract_metadata=args.extract_metadata,
        rescrape_after_days=args.rescrape_after_days,
        rescrape_after_months=args.rescrape_after_months
    )


def print_stats(stats: Dict[str, Any]):
    """Print statistics in a formatted way."""
    print("\n" + "="*50)
    print("SCRAPING STATISTICS")
    print("="*50)
    print(f"Total URLs scraped: {stats['total_scraped']}")
    print(f"Failed URLs: {stats['total_failed']}")
    print(f"Total links found: {stats['total_links_found']}")
    print(f"Runtime: {stats['runtime_seconds']:.2f} seconds")
    print(f"URLs per second: {stats['urls_per_second']:.2f}")
    print(f"Playwright fallbacks: {stats['playwright_fallback_rate']:.2%}")
    print(f"Queue size: {stats['queue_size']}")
    print(f"Unique URLs seen: {stats['unique_urls_seen']}")
    
    if stats.get('domain_stats'):
        print("\nDomain Statistics:")
        for domain, domain_stats in stats['domain_stats'].items():
            print(f"  {domain}: {domain_stats['processed']} scraped, {domain_stats['failed']} failed")


def print_results(results: Dict[str, Any], verbose: bool = False):
    """Print scraping results."""
    print(f"\nScraping Results ({len(results)} URLs):")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for url, result in results.items():
        if result.success:
            successful += 1
            if verbose:
                print(f"✅ {url}")
                print(f"   Title: {result.title[:100]}...")
                print(f"   Links: {len(result.links)}")
                print(f"   Time: {result.processing_time:.2f}s")
                if result.used_playwright:
                    print(f"   Used Playwright: Yes")
                print()
            else:
                print(f"✅ {url}")
        else:
            failed += 1
            if verbose:
                print(f"❌ {url}")
                print(f"   Error: {result.error}")
                print(f"   Status: {result.status_code}")
                print(f"   Time: {result.processing_time:.2f}s")
                print()
            else:
                print(f"❌ {url}: {result.error}")
    
    print(f"\nSummary: {successful} successful, {failed} failed")


def save_results(results: Dict[str, Any], output_file: str):
    """Save results to JSON file."""
    # Convert results to serializable format
    serializable_results = {}
    for url, result in results.items():
        serializable_results[url] = {
            'success': result.success,
            'status_code': result.status_code,
            'title': result.title,
            'content_length': len(result.content),
            'links_count': len(result.links),
            'images_count': len(result.images),
            'processing_time': result.processing_time,
            'used_playwright': result.used_playwright,
            'error': result.error
        }
    
    with open(output_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")


async def main():
    """Main CLI function."""
    args = parse_args()
    
    # Load URLs
    urls = args.urls.copy()
    if args.urls_file:
        file_urls = load_urls_from_file(args.urls_file)
        urls.extend(file_urls)
    
    if not urls:
        print("Error: No URLs provided. Use --urls-file or provide URLs as arguments.")
        sys.exit(1)
    
    # Remove duplicates
    urls = list(set(urls))
    
    print(f"Starting scraping of {len(urls)} URLs...")
    print(f"Configuration: max_urls={args.max_urls}, max_depth={args.max_depth}, concurrency={args.concurrency}")
    
    # Create configuration
    config = create_config_from_args(args)
    
    # Run scraper
    try:
        async with ScalableWebScraper(config) as scraper:
            results = await scraper.scrape_urls(urls, max_depth=args.max_depth)
            stats = scraper.get_stats()
            
            # Print results
            if not args.stats_only:
                print_results(results, verbose=args.verbose)
            
            # Print statistics
            print_stats(stats)
            
            # Save results if requested
            if args.output:
                save_results(results, args.output)
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 