# Docker Usage for VDL Web Scraper

## Quick Start

### Option 1: From Webscraping Directory (Recommended)

```bash
# Navigate to webscraping directory
cd vdl_tools/webscraping

# Build and run the web scraper
docker build -f Dockerfile.simple -t vdl-webscraper .
docker run vdl-webscraper
```

### Option 2: From Project Root

```bash
# Build from project root
docker build -f vdl_tools/webscraping/Dockerfile -t vdl-webscraper .
docker run vdl-webscraper

# Or use docker-compose
docker-compose -f docker-compose.webscraper.yml up --build
```

### Test the Scraper

```bash
# Run the test profile
docker-compose -f docker-compose.webscraper.yml --profile test up --build
```

## Building the Image

### Option 1: From Webscraping Directory (Recommended)

```bash
cd vdl_tools/webscraping
docker build -f Dockerfile.simple -t vdl-webscraper .
```

This approach:
- ✅ Uses only web scraping dependencies
- ✅ Avoids conflicts with main project dependencies
- ✅ Simpler and more reliable
- ✅ Faster build times

### Option 2: From Project Root

```bash
# Build with full project context
docker build -f vdl_tools/webscraping/Dockerfile -t vdl-webscraper .
```

This approach:
- ⚠️ May have dependency conflicts
- ⚠️ Slower build times
- ⚠️ More complex setup

## Running the Container

### Basic Usage

```bash
# Run with default test
docker run vdl-webscraper

# Run with custom command
docker run vdl-webscraper python -m examples

# Run with volume mounts
docker run -v $(pwd)/data:/app/data vdl-webscraper
```

### Interactive Mode

```bash
# Run with interactive shell
docker run -it vdl-webscraper /bin/bash

# Inside the container, you can run:
python run_test.py
python -m examples
python -m cli https://example.com
```

### Using Docker Compose

```bash
# Start the service
docker-compose -f docker-compose.webscraper.yml up -d

# View logs
docker-compose -f docker-compose.webscraper.yml logs -f

# Stop the service
docker-compose -f docker-compose.webscraper.yml down
```

## Environment Variables

You can set environment variables when running the container:

```bash
docker run -e MAX_URLS=1000 -e CONCURRENCY=20 vdl-webscraper
```

## Volume Mounts

Mount directories for persistent storage:

```bash
# Mount data directory
docker run -v $(pwd)/data:/app/data vdl-webscraper

# Mount logs directory
docker run -v $(pwd)/logs:/app/logs vdl-webscraper

# Mount both
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs vdl-webscraper
```

## Troubleshooting

### Module Not Found Error

If you get a "ModuleNotFoundError", try building from the webscraping directory:

```bash
# ✅ Recommended approach
cd vdl_tools/webscraping
docker build -f Dockerfile.simple -t vdl-webscraper .

# ❌ Alternative (may have dependency issues)
docker build -f vdl_tools/webscraping/Dockerfile -t vdl-webscraper .
```

### Dependency Conflicts

If you encounter dependency conflicts, use the simple Dockerfile:

```bash
cd vdl_tools/webscraping
docker build -f Dockerfile.simple -t vdl-webscraper .
```

### Permission Issues

The container runs as a non-root user. If you need to write to mounted volumes, ensure proper permissions:

```bash
# Create directories with proper permissions
mkdir -p data logs
chmod 777 data logs

# Then run the container
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs vdl-webscraper
```

### Playwright Issues

If Playwright fails to install browsers, you can rebuild with:

```bash
docker build --no-cache -f Dockerfile.simple -t vdl-webscraper .
```

## Production Deployment

For production use, consider:

1. **Using a multi-stage build** to reduce image size
2. **Setting up proper logging** to external systems
3. **Using secrets management** for API keys
4. **Setting up health checks**

Example production docker-compose:

```yaml
version: '3.8'
services:
  webscraper:
    build:
      context: ./vdl_tools/webscraping
      dockerfile: Dockerfile.simple
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "run_test.py"]
      interval: 30s
      timeout: 10s
      retries: 3
``` 