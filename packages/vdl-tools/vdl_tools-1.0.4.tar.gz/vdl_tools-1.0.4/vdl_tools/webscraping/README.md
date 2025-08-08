# VDL Web Scraper

A high-performance, scalable web scraper built in Python with support for JavaScript rendering, multiple storage backends, and cloud deployment.

## Features

- **High Performance**: Async/await architecture with configurable concurrency
- **JavaScript Support**: Playwright fallback for dynamic content
- **Link Discovery**: Automatic extraction and crawling of discovered links
- **Modular Storage**: Support for SQLite, S3, and PostgreSQL backends
- **Rate Limiting**: Domain-based rate limiting with robots.txt support
- **Error Handling**: Retry logic with exponential backoff for 403 and timeout errors
- **Anti-Detection**: Browser-like headers and realistic user agent to avoid blocking
- **Cloud Ready**: Docker support for easy deployment to AWS Lambda, GCP Cloud Run, etc.
- **Extensible**: Plugin-based architecture for custom extractors and storage backends

## Quick Start

### Using Docker (Recommended)

The easiest way to get started is using Docker:

```bash
# Build the container
docker build -f Dockerfile.simple -t vdl-webscraper .

# Run the scraper
docker run vdl-webscraper
```

### Local Development

1. Install the vdl-tools package (which includes all webscraping dependencies):
```bash
# From the root of the vdl-tools repository
pip install -e .
```

2. Install Playwright (for JavaScript support):
```bash
playwright install chromium
```

3. Run the scraper:
```bash
python run_test.py
```

## Architecture

### Core Components

- **`scraper.py`**: Main scraper class with async support
- **`queue_manager.py`**: Priority queue and rate limiting
- **`storage.py`**: Modular storage backends
- **`extractors.py`**: Content and link extraction
- **`config.py`**: Configuration management
- **`utils.py`**: Utility functions

### Storage Backends

- **SQLite**: Local file-based storage (default)
- **S3**: Cloud storage for scalability
- **PostgreSQL**: Relational database storage

### Content Extraction

- **HTML Parsing**: BeautifulSoup-based content extraction
- **Link Discovery**: Robust link extraction using BeautifulSoup
- **Metadata**: Title, description, and other meta tags
- **Images**: Image URL extraction

## Configuration

The scraper is highly configurable through the `ScraperConfig` class:

```python
from config import ScraperConfig

config = ScraperConfig(
    concurrency=5,                    # Number of concurrent requests
    delay=1.0,                        # Delay between requests
    timeout=30,                       # Request timeout
    max_urls=1000,                    # Maximum URLs to scrape
    max_depth=3,                      # Maximum crawl depth
    use_playwright_fallback=True,     # Use Playwright for JS
    storage_backend='sqlite',         # Storage backend
    storage_config={'db_path': 'data.db'},
    same_domain_only=False,           # Only follow links from same domain
    force_rescrape=False              # Force rescraping of existing URLs
)
```

## Usage Examples

### Basic Scraping

```python
from scraper import scrape_single_url
from config import ScraperConfig

config = ScraperConfig()
result = await scrape_single_url('https://example.com', config)
print(f"Title: {result.title}")
print(f"Content: {result.content[:200]}...")
```

### Batch Scraping

```python
from scraper import scrape_urls

urls = [
    'https://example.com',
    'https://httpbin.org/html',
    'https://quotes.toscrape.com'
]

results = await scrape_urls(urls)
for url, result in results.items():
    print(f"{url}: {result.title}")
```

### Same Domain Crawling

To restrict link discovery to only follow links from the same domain as the parent URL:

```python
from scraper import scrape_urls
from config import ScraperConfig

config = ScraperConfig(
    same_domain_only=True,    # Only follow links from same domain
    max_depth=3,
    extract_links=True
)

# This will only crawl pages within example.com
urls = ['https://example.com']
results = await scrape_urls(urls, config)
```

### Force Rescraping

To force the scraper to rescrape URLs even if they already exist in storage:

```python
from scraper import scrape_urls
from config import ScraperConfig

config = ScraperConfig(
    force_rescrape=True,    # Force rescraping of existing URLs
    max_urls=100
)

# This will rescrape URLs even if they were scraped before
urls = ['https://example.com']
results = await scrape_urls(urls, config)
```

### Error Handling and Retry Logic

The scraper includes robust error handling with retry logic:

```python
from scraper import scrape_urls
from config import ScraperConfig

config = ScraperConfig(
    retries=3,        # Number of retry attempts
    delay=1.0,        # Base delay between retries (exponential backoff)
    timeout=30        # Request timeout
)

# The scraper will automatically retry on:
# - HTTP 403 errors (with exponential backoff)
# - Timeout errors
# - Network errors
urls = ['https://example.com']
results = await scrape_urls(urls, config)
```

### Custom Storage

```python
from storage import S3Storage
from config import ScraperConfig

config = ScraperConfig(
    storage_backend='s3',
    storage_config={
        'bucket_name': 'my-scraper-data',
        'aws_access_key_id': 'your-key',
        'aws_secret_access_key': 'your-secret'
    }
)
```

## Docker Deployment

### Building the Container

```bash
# Simple build (recommended for most use cases)
docker build -f Dockerfile.simple -t vdl-webscraper .

# Full build (includes all vdl_tools dependencies)
docker build -f Dockerfile -t vdl-webscraper-full .
```

### Running in Production

```bash
# Basic run
docker run vdl-webscraper

# With custom configuration
docker run -v $(pwd)/config:/app/config vdl-webscraper

# With persistent storage
docker run -v $(pwd)/data:/app/data vdl-webscraper
```

### Cloud Deployment

The scraper is designed for cloud deployment:

- **AWS Lambda**: Use the simple Dockerfile for smaller deployments
- **GCP Cloud Run**: Supports HTTP triggers and background processing
- **Kubernetes**: Scale horizontally with multiple replicas
- **Docker Compose**: Orchestrate with other services

## Development

### Project Structure

```
webscraping/
├── scraper.py          # Main scraper implementation
├── queue_manager.py    # Queue and rate limiting
├── storage.py          # Storage backends
├── extractors.py       # Content extraction
├── config.py           # Configuration
├── utils.py            # Utilities
├── pyproject.toml      # Dependencies (in root directory)
├── Dockerfile.simple   # Simple Docker build
├── Dockerfile          # Full Docker build
├── run_test.py         # Test script
└── test_imports.py     # Import validation
```

### Testing

```bash
# Test imports
python test_imports.py

# Run full test
python run_test.py

# Test in Docker
docker run vdl-webscraper
```

### Adding Custom Extractors

```python
from extractors import ContentExtractor

class CustomExtractor(ContentExtractor):
    def extract_custom_data(self, html: str) -> dict:
        # Your custom extraction logic
        return {'custom_field': 'value'}
```

## Performance

The scraper is optimized for high performance:

- **Async I/O**: Non-blocking HTTP requests
- **Connection Pooling**: Reuse HTTP connections
- **Rate Limiting**: Respect server limits
- **Caching**: Avoid re-scraping URLs
- **Parallel Processing**: Configurable concurrency

Typical performance:
- 100-500 URLs/minute (depending on server response times)
- 50-200 concurrent requests (configurable)
- <100ms per request (excluding network time)

## Troubleshooting

### Common Issues

1. **Import Errors**: Use `Dockerfile.simple` to avoid dependency conflicts
2. **Memory Issues**: Reduce concurrency or use streaming storage
3. **Rate Limiting**: Increase delays between requests
4. **JavaScript Content**: Ensure Playwright is installed

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is part of the VDL Tools suite.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request 