"""
Content and link extractors for web scraping.
"""

import re
from typing import List, Dict, Optional, Set, Any
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse
import asyncio

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False


class ContentExtractor(ABC):
    """Abstract base class for content extractors."""
    
    @abstractmethod
    def extract_title(self, html: str) -> str:
        """Extract page title."""
        pass
    
    @abstractmethod
    def extract_content(self, html: str) -> str:
        """Extract main content."""
        pass
    
    @abstractmethod
    def extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract metadata."""
        pass


class LinkExtractor(ABC):
    """Abstract base class for link extractors."""
    
    @abstractmethod
    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract links from HTML."""
        pass
    
    @abstractmethod
    def extract_images(self, html: str, base_url: str) -> Set[str]:
        """Extract image URLs from HTML."""
        pass


class BeautifulSoupContentExtractor(ContentExtractor):
    """Content extractor using BeautifulSoup."""
    
    def __init__(self):
        if not BEAUTIFULSOUP_AVAILABLE:
            raise ImportError("BeautifulSoup is required for this extractor")
    
    def extract_title(self, html: str) -> str:
        """Extract page title."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            
            # Fallback to h1
            h1_tag = soup.find('h1')
            if h1_tag:
                return h1_tag.get_text().strip()
            
            return ""
        except Exception:
            return ""
    
    def extract_content(self, html: str) -> str:
        """Extract main content."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'main',
                '[role="main"]',
                '.content',
                '.main-content',
                '#content',
                '#main',
                'article',
                '.post-content',
                '.entry-content'
            ]
            
            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            if not content_element:
                # Fallback to body
                content_element = soup.find('body')
            
            if content_element:
                # Get text content
                text = content_element.get_text(separator=' ', strip=True)
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text)
                return text.strip()
            
            return ""
        except Exception:
            return ""
    
    def extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract metadata from HTML."""
        metadata = {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    metadata[name] = content
            
            # Open Graph tags
            og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
            for tag in og_tags:
                property_name = tag.get('property', '').replace('og:', '')
                content = tag.get('content')
                if property_name and content:
                    metadata[f'og_{property_name}'] = content
            
            # Twitter Card tags
            twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
            for tag in twitter_tags:
                name = tag.get('name', '').replace('twitter:', '')
                content = tag.get('content')
                if name and content:
                    metadata[f'twitter_{name}'] = content
            
            # Structured data (JSON-LD)
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    metadata['structured_data'] = data
                except Exception:
                    pass
            
            # Language
            lang = soup.find('html').get('lang') if soup.find('html') else None
            if lang:
                metadata['language'] = lang
            
            # Character encoding
            charset_meta = soup.find('meta', charset=True)
            if charset_meta:
                metadata['charset'] = charset_meta.get('charset')
            
        except Exception:
            pass
        
        return metadata


class RegexContentExtractor(ContentExtractor):
    """Simple regex-based content extractor."""
    
    def extract_title(self, html: str) -> str:
        """Extract page title using regex."""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Remove HTML tags from title
            title = re.sub(r'<[^>]+>', '', title)
            return title
        
        # Fallback to h1
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        if h1_match:
            h1 = h1_match.group(1).strip()
            h1 = re.sub(r'<[^>]+>', '', h1)
            return h1
        
        return ""
    
    def extract_content(self, html: str) -> str:
        """Extract content using regex."""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Extract text from body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
        if body_match:
            body_content = body_match.group(1)
        else:
            body_content = html
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', body_content)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract metadata using regex."""
        metadata = {}
        
        # Meta tags
        meta_pattern = r'<meta[^>]+(?:name|property)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']+)["\']'
        meta_matches = re.findall(meta_pattern, html, re.IGNORECASE)
        
        for name, content in meta_matches:
            metadata[name.lower()] = content
        
        # Language
        lang_match = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if lang_match:
            metadata['language'] = lang_match.group(1)
        
        return metadata


class BeautifulSoupLinkExtractor(LinkExtractor):
    """Link extractor using BeautifulSoup."""
    
    def __init__(self):
        if not BEAUTIFULSOUP_AVAILABLE:
            raise ImportError("BeautifulSoup is required for this extractor")
    
    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract links from HTML."""
        links = set()
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all anchor tags
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    absolute_url = urljoin(base_url, href)
                    links.add(absolute_url)
            
            # Find links in other elements (like data attributes)
            for element in soup.find_all(attrs={'data-href': True}):
                href = element['data-href']
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    absolute_url = urljoin(base_url, href)
                    links.add(absolute_url)
            
        except Exception:
            pass
        
        return links
    
    def extract_images(self, html: str, base_url: str) -> Set[str]:
        """Extract image URLs from HTML."""
        images = set()
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all img tags
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src and not src.startswith('data:'):
                    absolute_url = urljoin(base_url, src)
                    images.add(absolute_url)
            
            # Find images in picture elements
            for picture in soup.find_all('picture'):
                for source in picture.find_all('source', srcset=True):
                    srcset = source['srcset']
                    # Parse srcset (simplified)
                    for src in srcset.split(','):
                        url = src.strip().split()[0]
                        if url and not url.startswith('data:'):
                            absolute_url = urljoin(base_url, url)
                            images.add(absolute_url)
            
        except Exception:
            pass
        
        return images


class RegexLinkExtractor(LinkExtractor):
    """Simple regex-based link extractor."""
    
    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract links using regex."""
        links = set()
        
        # Find href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        href_matches = re.findall(href_pattern, html, re.IGNORECASE)
        
        for href in href_matches:
            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                absolute_url = urljoin(base_url, href)
                links.add(absolute_url)
        
        # Find data-href attributes
        data_href_pattern = r'data-href=["\']([^"\']+)["\']'
        data_href_matches = re.findall(data_href_pattern, html, re.IGNORECASE)
        
        for href in data_href_matches:
            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                absolute_url = urljoin(base_url, href)
                links.add(absolute_url)
        
        return links
    
    def extract_images(self, html: str, base_url: str) -> Set[str]:
        """Extract image URLs using regex."""
        images = set()
        
        # Find src attributes in img tags
        src_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        src_matches = re.findall(src_pattern, html, re.IGNORECASE)
        
        for src in src_matches:
            if src and not src.startswith('data:'):
                absolute_url = urljoin(base_url, src)
                images.add(absolute_url)
        
        # Find srcset attributes
        srcset_pattern = r'srcset=["\']([^"\']+)["\']'
        srcset_matches = re.findall(srcset_pattern, html, re.IGNORECASE)
        
        for srcset in srcset_matches:
            for src in srcset.split(','):
                url = src.strip().split()[0]
                if url and not url.startswith('data:'):
                    absolute_url = urljoin(base_url, url)
                    images.add(absolute_url)
        
        return images


def create_content_extractor(use_beautifulsoup: bool = True) -> ContentExtractor:
    """Factory function to create content extractor."""
    if use_beautifulsoup and BEAUTIFULSOUP_AVAILABLE:
        return BeautifulSoupContentExtractor()
    else:
        return RegexContentExtractor()


def create_link_extractor(use_beautifulsoup: bool = True) -> LinkExtractor:
    """Factory function to create link extractor."""
    if use_beautifulsoup and BEAUTIFULSOUP_AVAILABLE:
        return BeautifulSoupLinkExtractor()
    else:
        return RegexLinkExtractor() 