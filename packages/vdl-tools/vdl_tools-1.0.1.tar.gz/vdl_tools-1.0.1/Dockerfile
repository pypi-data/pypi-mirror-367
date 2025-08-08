# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and its system dependencies (needed for webscraping)
RUN pip install playwright
RUN playwright install-deps

# Create non-root user
RUN useradd -m -u 1000 vdluser

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . /app/

# Install the vdl-tools package
RUN pip install --no-cache-dir -e .

# Install Playwright browsers as non-root user
USER vdluser
RUN playwright install chromium

# Switch back to root for final setup
USER root

# Create directories that might be needed
RUN mkdir -p /app/data /app/logs && chown -R vdluser:vdluser /app/data /app/logs

# Switch to non-root user for runtime
USER vdluser

# Expose common ports (can be overridden)
EXPOSE 8000

# Default command - can be overridden when running the container
CMD ["python", "-c", "import vdl_tools; print('VDL Tools package loaded successfully')"]
