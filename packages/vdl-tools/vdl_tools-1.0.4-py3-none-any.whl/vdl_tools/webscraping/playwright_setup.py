"""
Playwright setup utilities for automatic browser installation.
"""

import subprocess
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def is_playwright_installed() -> bool:
    """Check if Playwright browsers are installed."""
    try:
        import playwright
        # Try to get the browser executable path
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # This will raise if browsers aren't installed
            browser_path = p.chromium.executable_path
            return Path(browser_path).exists()
    except Exception:
        return False


def install_playwright_browsers(browser: str = "chromium") -> bool:
    """
    Install Playwright browsers automatically.
    
    Args:
        browser: Browser to install (chromium, firefox, webkit, or all)
        
    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        logger.info(f"Installing Playwright {browser} browser...")
        
        # Run playwright install command
        cmd = [sys.executable, "-m", "playwright", "install", browser]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info(f"Successfully installed Playwright {browser}")
            return True
        else:
            logger.error(f"Failed to install Playwright {browser}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Playwright installation timed out")
        return False
    except Exception as e:
        logger.error(f"Error installing Playwright browsers: {e}")
        return False


def install_playwright_deps() -> bool:
    """
    Install Playwright system dependencies (Linux only).
    
    Returns:
        True if installation succeeded or not needed, False otherwise
    """
    try:
        # Only install deps on Linux
        if sys.platform != "linux":
            logger.info("Playwright deps installation not needed on this platform")
            return True
            
        logger.info("Installing Playwright system dependencies...")
        
        cmd = [sys.executable, "-m", "playwright", "install-deps"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("Successfully installed Playwright system dependencies")
            return True
        else:
            logger.warning(f"Playwright deps installation had issues: {result.stderr}")
            # Don't fail completely - deps might not be strictly necessary
            return True
            
    except subprocess.TimeoutExpired:
        logger.error("Playwright deps installation timed out")
        return False
    except Exception as e:
        logger.error(f"Error installing Playwright deps: {e}")
        return False


def ensure_playwright_setup(browser: str = "chromium") -> bool:
    """
    Ensure Playwright is properly set up with browsers installed.
    
    Args:
        browser: Browser to ensure is installed
        
    Returns:
        True if setup is complete, False if setup failed
    """
    if is_playwright_installed():
        logger.debug("Playwright browsers already installed")
        return True
    
    logger.info("Playwright browsers not found, installing automatically...")
    
    # Install system deps first (Linux only)
    if not install_playwright_deps():
        logger.warning("Failed to install system dependencies, continuing anyway...")
    
    # Install browsers
    if not install_playwright_browsers(browser):
        logger.error("Failed to install Playwright browsers")
        return False
        
    return True


def get_setup_instructions() -> str:
    """Get manual setup instructions for users."""
    return """
To manually install Playwright browsers, run:
    python -m playwright install chromium

On Linux, you may also need system dependencies:
    python -m playwright install-deps
    """
