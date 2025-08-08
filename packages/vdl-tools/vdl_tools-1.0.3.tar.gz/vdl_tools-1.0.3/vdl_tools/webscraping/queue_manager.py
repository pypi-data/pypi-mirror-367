"""
Queue management for web scraping tasks.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import time
from collections import defaultdict

# Handle both package and direct imports
try:
    from .utils import url_normalize, generate_url_hash, extract_domain
except ImportError:
    from utils import url_normalize, generate_url_hash, extract_domain

logger = logging.getLogger(__name__)


@dataclass
class ScrapingTask:
    """Represents a scraping task."""
    url: str
    depth: int = 0
    parent_url: Optional[str] = None
    priority: int = 0
    domain: str = ""
    created_at: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.domain:
            self.domain = extract_domain(self.url)
        if not self.created_at:
            self.created_at = time.time()
    
    def __hash__(self):
        return hash(self.url)
    
    def __eq__(self, other):
        return self.url == other.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for storage."""
        return {
            'url': self.url,
            'depth': self.depth,
            'parent_url': self.parent_url,
            'priority': self.priority,
            'domain': self.domain,
            'created_at': self.created_at,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapingTask':
        """Create task from dictionary."""
        return cls(
            url=data['url'],
            depth=data.get('depth', 0),
            parent_url=data.get('parent_url'),
            priority=data.get('priority', 0),
            domain=data.get('domain', ''),
            created_at=data.get('created_at', time.time()),
            metadata=data.get('metadata', {})
        )


class ScrapingQueue:
    """
    Queue system for managing URLs to be scraped.
    
    Features:
    - Priority-based queuing
    - Domain-based rate limiting
    - Deduplication
    - Depth tracking
    - Statistics tracking
    """
    
    def __init__(self):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._seen_urls: Set[str] = set()
        self._domain_stats: Dict[str, Dict] = defaultdict(lambda: {
            'added': 0,
            'processed': 0,
            'failed': 0,
            'last_processed': 0.0
        })
        self._total_added = 0
        self._total_processed = 0
        self._total_failed = 0
    
    async def add_url(self, url: str, depth: int = 0, parent_url: Optional[str] = None, 
                     priority: int = 0) -> bool:
        """
        Add a URL to the scraping queue.
        
        Args:
            url: URL to add
            depth: Current depth level
            parent_url: Parent URL that led to this URL
            priority: Priority (lower number = higher priority)
            
        Returns:
            True if URL was added, False if already seen
        """
        normalized_url = url_normalize(url)
        url_hash = generate_url_hash(normalized_url)
        
        if url_hash in self._seen_urls:
            return False
        
        task = ScrapingTask(
            url=normalized_url,
            depth=depth,
            parent_url=parent_url,
            priority=priority,
            domain=extract_domain(normalized_url)
        )
        
        # Add to queue with priority
        await self._queue.put((priority, task.created_at, task))
        self._seen_urls.add(url_hash)
        
        # Update statistics
        self._total_added += 1
        self._domain_stats[task.domain]['added'] += 1
        
        return True
    
    async def get_next_url(self) -> Optional[ScrapingTask]:
        """
        Get the next URL from the queue.
        
        Returns:
            ScrapingTask or None if queue is empty
        """
        try:
            # Use timeout to avoid blocking indefinitely
            _, _, task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            self._total_processed += 1
            self._domain_stats[task.domain]['processed'] += 1
            self._domain_stats[task.domain]['last_processed'] = time.time()
            return task
        except asyncio.TimeoutError:
            # Queue is empty or timeout reached
            return None
        except asyncio.QueueEmpty:
            return None
    
    def mark_failed(self, url: str):
        """Mark a URL as failed."""
        domain = extract_domain(url)
        self._total_failed += 1
        self._domain_stats[domain]['failed'] += 1
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()
    
    def size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()
    
    def get_stats(self) -> Dict:
        """Get queue statistics."""
        return {
            'total_added': self._total_added,
            'total_processed': self._total_processed,
            'total_failed': self._total_failed,
            'queue_size': self.size(),
            'unique_urls_seen': len(self._seen_urls),
            'domain_stats': dict(self._domain_stats)
        }
    
    def get_domain_stats(self, domain: str) -> Dict:
        """Get statistics for a specific domain."""
        return self._domain_stats.get(domain, {
            'added': 0,
            'processed': 0,
            'failed': 0,
            'last_processed': 0.0
        })
    
    def clear(self):
        """Clear the queue and reset statistics."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self._seen_urls.clear()
        self._domain_stats.clear()
        self._total_added = 0
        self._total_processed = 0
        self._total_failed = 0


class DomainRateLimiter:
    """
    Rate limiter for managing requests per domain.
    """
    
    def __init__(self):
        self._last_request: Dict[str, float] = {}
        self._domain_delays: Dict[str, float] = {}
    
    def set_delay(self, domain: str, delay: float):
        """Set delay for a domain."""
        self._domain_delays[domain] = delay
    
    def get_delay(self, domain: str) -> float:
        """Get delay for a domain."""
        return self._domain_delays.get(domain, 0.1)
    
    async def wait_if_needed(self, domain: str):
        """Wait if rate limiting is needed for a domain."""
        delay = self.get_delay(domain)
        if delay <= 0:
            return
        
        last_request = self._last_request.get(domain, 0)
        time_since_last = time.time() - last_request
        
        if time_since_last < delay:
            wait_time = delay - time_since_last
            await asyncio.sleep(wait_time)
        
        self._last_request[domain] = time.time()
    
    def reset_domain(self, domain: str):
        """Reset the last request time for a domain."""
        self._last_request[domain] = 0.0


class TaskQueue:
    """Priority queue for managing scraping tasks."""
    
    def __init__(self):
        self._tasks: List[ScrapingTask] = []
        self._processed_urls: set = set()
        self._failed_urls: Dict[str, int] = {}  # url -> failure count
        self._max_retries = 3
    
    def add_task(self, task: ScrapingTask) -> bool:
        """Add a task to the queue if not already processed."""
        if task.url in self._processed_urls:
            logger.debug(f"URL already processed: {task.url}")
            return False
        
        if task.url in self._failed_urls and self._failed_urls[task.url] >= self._max_retries:
            logger.debug(f"URL failed too many times: {task.url}")
            return False
        
        # Insert based on priority (higher priority first)
        for i, existing_task in enumerate(self._tasks):
            if task.priority > existing_task.priority:
                self._tasks.insert(i, task)
                break
        else:
            self._tasks.append(task)
        
        logger.debug(f"Added task: {task.url} (priority: {task.priority})")
        return True
    
    def add_url(self, url: str, priority: int = 1, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a URL as a task."""
        task = ScrapingTask(url=url, priority=priority, metadata=metadata)
        return self.add_task(task)
    
    def get_next_task(self) -> Optional[ScrapingTask]:
        """Get the next task from the queue."""
        if not self._tasks:
            return None
        
        task = self._tasks.pop(0)
        logger.debug(f"Retrieved task: {task.url}")
        return task
    
    def mark_completed(self, url: str):
        """Mark a URL as successfully processed."""
        self._processed_urls.add(url)
        if url in self._failed_urls:
            del self._failed_urls[url]
        logger.debug(f"Marked completed: {url}")
    
    def mark_failed(self, url: str, error: str = None):
        """Mark a URL as failed."""
        self._failed_urls[url] = self._failed_urls.get(url, 0) + 1
        logger.warning(f"Marked failed: {url} (attempt {self._failed_urls[url]})")
        if error:
            logger.error(f"Error: {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'pending_tasks': len(self._tasks),
            'processed_urls': len(self._processed_urls),
            'failed_urls': len(self._failed_urls),
            'total_failures': sum(self._failed_urls.values())
        }
    
    def save_state(self, filepath: str):
        """Save queue state to file."""
        state = {
            'tasks': [task.to_dict() for task in self._tasks],
            'processed_urls': list(self._processed_urls),
            'failed_urls': self._failed_urls
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved queue state to {filepath}")
    
    def load_state(self, filepath: str):
        """Load queue state from file."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self._tasks = [ScrapingTask.from_dict(task_data) for task_data in state['tasks']]
            self._processed_urls = set(state['processed_urls'])
            self._failed_urls = state['failed_urls']
            
            logger.info(f"Loaded queue state from {filepath}")
        except FileNotFoundError:
            logger.info(f"No existing state file found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading state: {e}")


class AsyncTaskQueue:
    """Asynchronous version of the task queue."""
    
    def __init__(self):
        self._queue = asyncio.Queue()
        self._processed_urls: set = set()
        self._failed_urls: Dict[str, int] = {}
        self._max_retries = 3
    
    async def add_task(self, task: ScrapingTask) -> bool:
        """Add a task to the async queue."""
        if task.url in self._processed_urls:
            return False
        
        if task.url in self._failed_urls and self._failed_urls[task.url] >= self._max_retries:
            return False
        
        await self._queue.put(task)
        return True
    
    async def add_url(self, url: str, priority: int = 1, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a URL as a task."""
        task = ScrapingTask(url=url, priority=priority, metadata=metadata)
        return await self.add_task(task)
    
    async def get_next_task(self) -> Optional[ScrapingTask]:
        """Get the next task from the async queue."""
        try:
            task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            return task
        except asyncio.TimeoutError:
            return None
    
    def mark_completed(self, url: str):
        """Mark a URL as successfully processed."""
        self._processed_urls.add(url)
        if url in self._failed_urls:
            del self._failed_urls[url]
    
    def mark_failed(self, url: str, error: str = None):
        """Mark a URL as failed."""
        self._failed_urls[url] = self._failed_urls.get(url, 0) + 1
        if error:
            logger.error(f"Task failed: {url} - {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'pending_tasks': self._queue.qsize(),
            'processed_urls': len(self._processed_urls),
            'failed_urls': len(self._failed_urls),
            'total_failures': sum(self._failed_urls.values())
        } 