"""
Utility functions for the web scraper.
"""
import re
from bs4 import BeautifulSoup
import hashlib
from typing import Optional, Set, List
from urllib.parse import urlparse, urljoin, urlunparse, parse_qs, urlencode
from urllib.robotparser import RobotFileParser
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from url_normalize import url_normalize as normalize_url


def url_normalize(url: str, base_url: Optional[str] = None) -> str:
    """
    Advanced URL normalization for consistent comparison and storage.
    Handles common duplicate patterns like www vs non-www domains.
    
    Args:
        url: The URL to normalize
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Normalized URL string
    """
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    
    try:
        # First apply standard URL normalization
        normalized = normalize_url(url)
        parsed = urlparse(normalized)
        
        # Advanced normalization for duplicate detection
        netloc = parsed.netloc.lower()
        
        # Remove www subdomain for consistency
        # This treats www.example.com and example.com as the same
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # Normalize path - remove trailing slash except for root
        path = parsed.path
        if path != '/' and path.endswith('/'):
            path = path.rstrip('/')
        elif not path:
            path = ''
        
        # Reconstruct normalized URL
        return urlunparse((
            parsed.scheme,
            netloc,
            path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment for consistency
        ))
    except Exception:
        return url


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid and has a supported scheme.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ('http', 'https') and
            parsed.netloc and
            len(url) < 2048  # Reasonable URL length limit
        )
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain string
    """
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs belong to the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if same domain, False otherwise
    """
    return extract_domain(url1) == extract_domain(url2)


def clean_url(url: str) -> str:
    """
    Clean URL by removing common tracking parameters and fragments.
    
    Args:
        url: URL to clean
        
    Returns:
        Cleaned URL
    """
    # Common tracking parameters to remove
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'msclkid', 'ref', 'source', 'campaign',
        'mc_cid', 'mc_eid', 'mc_tc', 'mc_cc'
    }
    
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove tracking parameters
        cleaned_params = {
            k: v for k, v in query_params.items()
            if k.lower() not in tracking_params
        }
        
        # Rebuild query string
        new_query = urlencode(cleaned_params, doseq=True) if cleaned_params else ''
        
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            ''  # Remove fragment
        ))
    except Exception:
        return url


def generate_url_hash(url: str) -> str:
    """
    Generate a hash for a URL for deduplication.
    
    Args:
        url: URL to hash
        
    Returns:
        Hash string
    """
    normalized = url_normalize(url)
    return hashlib.sha256(normalized.encode()).hexdigest()


def extract_links_from_html(html: str, base_url: str) -> Set[str]:
    """
    Extract all links from HTML content using BeautifulSoup.
    
    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
        
    Returns:
        Set of normalized URLs
    """
    links = set()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all anchor tags
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            if is_valid_url(href):
                normalized = url_normalize(href, base_url)
                if normalized:
                    links.add(normalized)
    return links


def should_follow_link(url: str, base_domain: str, allowed_domains: Optional[List[str]] = None) -> bool:
    """
    Determine if a link should be followed based on domain restrictions.
    
    Args:
        url: URL to check
        base_domain: Domain of the current page
        allowed_domains: List of allowed domains (None for all)
        
    Returns:
        True if link should be followed, False otherwise
    """
    url_domain = extract_domain(url)
    
    if not url_domain:
        return False
    
    # If no domain restrictions, follow all links
    if allowed_domains is None:
        return True
    
    # Check if URL domain is in allowed domains
    return url_domain in allowed_domains


async def check_robots_txt(domain: str, user_agent: str = "*") -> Optional[RobotFileParser]:
    """
    Check robots.txt for a domain.
    
    Args:
        domain: Domain to check
        user_agent: User agent string
        
    Returns:
        RobotFileParser instance or None if not found
    """
    try:
        robots_url = f"https://{domain}/robots.txt"
        async with aiohttp.ClientSession() as session:
            async with session.get(robots_url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    rp = RobotFileParser()
                    rp.read(content.splitlines())
                    return rp
    except Exception:
        pass
    
    return None


def is_allowed_by_robots(robots_parser: RobotFileParser, url: str, user_agent: str) -> bool:
    """
    Check if a URL is allowed by robots.txt.
    
    Args:
        robots_parser: RobotFileParser instance
        url: URL to check
        user_agent: User agent string
        
    Returns:
        True if allowed, False otherwise
    """
    try:
        return robots_parser.can_fetch(user_agent, url)
    except Exception:
        return True  # Default to allowed if robots.txt parsing fails


def get_content_type_from_headers(headers: dict) -> str:
    """
    Extract content type from response headers.
    
    Args:
        headers: Response headers dictionary
        
    Returns:
        Content type string
    """
    content_type = headers.get('content-type', '')
    if ';' in content_type:
        content_type = content_type.split(';')[0].strip()
    return content_type.lower()


def is_html_content(content_type: str) -> bool:
    """
    Check if content type indicates HTML content.
    
    Args:
        content_type: Content type string
        
    Returns:
        True if HTML content, False otherwise
    """
    return content_type in ('text/html', 'application/xhtml+xml')


def calculate_depth_from_urls(start_url: str, current_url: str) -> int:
    """
    Calculate the depth of a URL relative to the start URL.
    
    Args:
        start_url: Starting URL
        current_url: Current URL to calculate depth for
        
    Returns:
        Depth as integer
    """
    try:
        start_parsed = urlparse(start_url)
        current_parsed = urlparse(current_url)
        
        if start_parsed.netloc != current_parsed.netloc:
            return 0
        
        start_path = start_parsed.path.rstrip('/')
        current_path = current_parsed.path.rstrip('/')
        
        if start_path == current_path:
            return 0
        
        # Simple depth calculation based on path segments
        start_segments = [s for s in start_path.split('/') if s]
        current_segments = [s for s in current_path.split('/') if s]
        
        # Find common prefix
        common_length = 0
        for i, (start_seg, current_seg) in enumerate(zip(start_segments, current_segments)):
            if start_seg == current_seg:
                common_length = i + 1
            else:
                break
        
        return len(current_segments) - common_length
        
    except Exception:
        return 0


async def rate_limit_delay(delay: float):
    """
    Async delay for rate limiting.
    
    Args:
        delay: Delay in seconds
    """
    if delay > 0:
        await asyncio.sleep(delay)


def is_page_stale(scraped_at: datetime, rescrape_after_days: Optional[int] = None, 
                  rescrape_after_months: Optional[int] = None) -> bool:
    """
    Check if a page is stale and should be re-scraped based on age.
    All datetimes are normalized to UTC for consistent comparison.
    
    Args:
        scraped_at: When the page was last scraped
        rescrape_after_days: Rescrape if older than X days
        rescrape_after_months: Rescrape if older than X months
        
    Returns:
        True if page should be re-scraped, False otherwise
    """
    if not scraped_at:
        return True  # No scrape date means we should scrape
    
    # Always use UTC timezone-aware datetime for consistency
    now = datetime.now(timezone.utc)
    
    # Convert scraped_at to UTC if it's not already timezone-aware
    if scraped_at.tzinfo is None:
        # Assume naive datetime is UTC
        scraped_at = scraped_at.replace(tzinfo=timezone.utc)
    elif scraped_at.tzinfo != timezone.utc:
        # Convert to UTC if it's in a different timezone
        scraped_at = scraped_at.astimezone(timezone.utc)
    
    # Check months first (takes precedence over days)
    if rescrape_after_months is not None:
        # Calculate months ago (approximate using 30 days per month)
        threshold_date = now - timedelta(days=rescrape_after_months * 30)
        if scraped_at < threshold_date:
            return True
    
    # Check days
    if rescrape_after_days is not None:
        threshold_date = now - timedelta(days=rescrape_after_days)
        if scraped_at < threshold_date:
            return True
    
    return False


def get_page_age_info(scraped_at: datetime) -> dict:
    """
    Get human-readable information about page age.
    All datetimes are normalized to UTC for consistent calculation.
    
    Args:
        scraped_at: When the page was scraped
        
    Returns:
        Dictionary with age information
    """
    if not scraped_at:
        return {"age_days": None, "age_months": None, "human_readable": "Never scraped"}
    
    # Always use UTC timezone-aware datetime for consistency
    now = datetime.now(timezone.utc)
    
    # Convert scraped_at to UTC if it's not already timezone-aware
    if scraped_at.tzinfo is None:
        # Assume naive datetime is UTC
        scraped_at = scraped_at.replace(tzinfo=timezone.utc)
    elif scraped_at.tzinfo != timezone.utc:
        # Convert to UTC if it's in a different timezone
        scraped_at = scraped_at.astimezone(timezone.utc)
    
    age_delta = now - scraped_at
    age_days = age_delta.days
    age_months = age_days // 30
    
    if age_days == 0:
        human_readable = "Today"
    elif age_days == 1:
        human_readable = "1 day ago"
    elif age_days < 30:
        human_readable = f"{age_days} days ago"
    elif age_months == 1:
        human_readable = "1 month ago"
    else:
        human_readable = f"{age_months} months ago"
    
    return {
        "age_days": age_days,
        "age_months": age_months,
        "human_readable": human_readable,
        "scraped_at": scraped_at.isoformat()
    } 