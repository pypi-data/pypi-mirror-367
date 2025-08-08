"""
Storage backends for scraped content.
"""

import json
import sqlite3
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import aiofiles
import aiofiles.os
from vdl_tools.webscraping.utils import generate_url_hash, is_page_stale, extract_domain
import boto3
from botocore.exceptions import ClientError
import asyncpg
from vdl_tools.shared_tools.tools.config_utils import get_configuration

@dataclass
class ScrapedPage:
    """Represents a scraped page."""
    
    url: str
    title: str = ""
    content: str = ""
    html: str = ""
    status_code: int = 0
    content_type: str = ""
    headers: Dict[str, str] = None
    links: List[str] = None
    images: List[str] = None
    metadata: Dict[str, Any] = None
    depth: int = 0
    parent_url: Optional[str] = None
    scraped_at: datetime = None
    domain: str = ""
    content_hash: str = ""
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.links is None:
            self.links = []
        if self.images is None:
            self.images = []
        if self.metadata is None:
            self.metadata = {}
        if self.scraped_at is None:
            self.scraped_at = datetime.now(timezone.utc)
        if not self.domain:
            self.domain = extract_domain(self.url)
        if not self.content_hash:
            self.content_hash = self._generate_content_hash()
    
    def _generate_content_hash(self) -> str:
        """Generate hash of content for deduplication."""
        content = f"{self.url}{self.content}{self.html}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['scraped_at'] = self.scraped_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapedPage':
        """Create from dictionary."""
        if 'scraped_at' in data and isinstance(data['scraped_at'], str):
            data['scraped_at'] = datetime.fromisoformat(data['scraped_at'])
        return cls(**data)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    async def store_page(self, page: ScrapedPage) -> bool:
        """Store a scraped page."""
        pass
    
    @abstractmethod
    async def get_page(self, url: str) -> Optional[ScrapedPage]:
        """Retrieve a scraped page by URL."""
        pass
    
    @abstractmethod
    async def page_exists(self, url: str) -> bool:
        """Check if a page exists in storage."""
        pass
    
    @abstractmethod
    async def should_rescrape(self, url: str, rescrape_after_days: Optional[int] = None, 
                             rescrape_after_months: Optional[int] = None) -> bool:
        """Check if a page should be re-scraped based on age."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        pass
    
    @abstractmethod
    async def close(self):
        """Close storage connection."""
        pass


class SQLiteStorage(StorageBackend):
    """SQLite storage backend."""
    
    def __init__(self, db_path: str = "scraped_pages.db"):
        self.db_path = db_path
        self._conn = None
        self._lock = asyncio.Lock()
    
    async def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            await self._init_db()
        return self._conn
    
    async def _init_db(self):
        """Initialize database tables."""
        conn = await self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_pages (
                url TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                html TEXT,
                status_code INTEGER,
                content_type TEXT,
                headers TEXT,
                links TEXT,
                images TEXT,
                metadata TEXT,
                depth INTEGER,
                parent_url TEXT,
                scraped_at TEXT,
                domain TEXT,
                content_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain ON scraped_pages(domain)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scraped_at ON scraped_pages(scraped_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash ON scraped_pages(content_hash)
        """)
        
        conn.commit()
    
    async def store_page(self, page: ScrapedPage) -> bool:
        """Store a scraped page."""
        async with self._lock:
            try:
                conn = await self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO scraped_pages 
                    (url, title, content, html, status_code, content_type, 
                     headers, links, images, metadata, depth, parent_url, 
                     scraped_at, domain, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    page.url,
                    page.title,
                    page.content,
                    page.html,
                    page.status_code,
                    page.content_type,
                    json.dumps(page.headers),
                    json.dumps(page.links),
                    json.dumps(page.images),
                    json.dumps(page.metadata),
                    page.depth,
                    page.parent_url,
                    page.scraped_at.isoformat(),
                    page.domain,
                    page.content_hash
                ))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error storing page {page.url}: {e}")
                return False
    
    async def get_page(self, url: str) -> Optional[ScrapedPage]:
        """Retrieve a scraped page by URL."""
        async with self._lock:
            try:
                conn = await self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM scraped_pages WHERE url = ?
                """, (url,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_page(row)
                return None
            except Exception as e:
                print(f"Error retrieving page {url}: {e}")
                return None
    
    def _row_to_page(self, row) -> ScrapedPage:
        """Convert database row to ScrapedPage."""
        return ScrapedPage(
            url=row[0],
            title=row[1] or "",
            content=row[2] or "",
            html=row[3] or "",
            status_code=row[4] or 0,
            content_type=row[5] or "",
            headers=json.loads(row[6]) if row[6] else {},
            links=json.loads(row[7]) if row[7] else [],
            images=json.loads(row[8]) if row[8] else [],
            metadata=json.loads(row[9]) if row[9] else {},
            depth=row[10] or 0,
            parent_url=row[11],
            scraped_at=datetime.fromisoformat(row[12]) if row[12] else datetime.now(timezone.utc),
            domain=row[13] or "",
            content_hash=row[14] or ""
        )
    
    async def page_exists(self, url: str) -> bool:
        """Check if a page exists in storage."""
        async with self._lock:
            try:
                conn = await self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM scraped_pages WHERE url = ?
                """, (url,))
                
                count = cursor.fetchone()[0]
                return count > 0
            except Exception:
                return False
    
    async def should_rescrape(self, url: str, rescrape_after_days: Optional[int] = None, 
                             rescrape_after_months: Optional[int] = None) -> bool:
        """Check if a page should be re-scraped based on age."""
        async with self._lock:
            try:
                conn = await self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT scraped_at FROM scraped_pages WHERE url = ?
                """, (url,))
                
                row = cursor.fetchone()
                if not row:
                    return True  # Page doesn't exist, should scrape
                
                scraped_at_str = row[0]
                if not scraped_at_str:
                    return True  # No scrape date, should scrape
                
                # Parse the stored datetime
                try:
                    scraped_at = datetime.fromisoformat(scraped_at_str)
                except (ValueError, TypeError):
                    return True  # Invalid date, should scrape
                
                # Use the utility function to check if stale
                return is_page_stale(scraped_at, rescrape_after_days, rescrape_after_months)
                
            except Exception as e:
                print(f"Error checking page age for {url}: {e}")
                return True  # On error, default to scraping
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        async with self._lock:
            try:
                conn = await self._get_connection()
                cursor = conn.cursor()
                
                # Total pages
                cursor.execute("SELECT COUNT(*) FROM scraped_pages")
                total_pages = cursor.fetchone()[0]
                
                # Pages by domain
                cursor.execute("""
                    SELECT domain, COUNT(*) FROM scraped_pages 
                    GROUP BY domain ORDER BY COUNT(*) DESC
                """)
                domain_stats = dict(cursor.fetchall())
                
                # Recent pages
                cursor.execute("""
                    SELECT COUNT(*) FROM scraped_pages 
                    WHERE scraped_at > datetime('now', '-1 hour')
                """)
                recent_pages = cursor.fetchone()[0]
                
                return {
                    'total_pages': total_pages,
                    'domain_stats': domain_stats,
                    'recent_pages': recent_pages,
                    'storage_type': 'sqlite',
                    'db_path': self.db_path
                }
            except Exception as e:
                return {'error': str(e)}
    
    async def close(self):
        """Close storage connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


class PostgreSQLStorage(StorageBackend):
    """PostgreSQL storage backend using asyncpg."""
    
    def __init__(
        self,
        database_url: str = None,
        host: str = "localhost",
        port: int = 5432,
        database: str = "webscraper",
        user: str = "postgres",
        password: str = "",
        **kwargs
    ):
        # Build connection string if not provided
        if database_url:
            self.database_url = database_url
        else:
            self.database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        self._pool = None
        self._connection_kwargs = kwargs
    
    async def _get_pool(self) -> asyncpg.Pool:
        """Get connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.database_url, 
                min_size=1, 
                max_size=10,
                **self._connection_kwargs
            )
            await self._init_db()
        return self._pool
    
    async def _init_db(self):
        """Initialize database tables."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Create the scraped_pages table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_pages (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    html TEXT,
                    status_code INTEGER,
                    content_type TEXT,
                    headers JSONB,
                    links JSONB,
                    images JSONB,
                    metadata JSONB,
                    depth INTEGER,
                    parent_url TEXT,
                    scraped_at TIMESTAMP WITH TIME ZONE,
                    domain TEXT,
                    content_hash TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes for better performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scraped_pages_domain ON scraped_pages(domain)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scraped_pages_scraped_at ON scraped_pages(scraped_at)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scraped_pages_content_hash ON scraped_pages(content_hash)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scraped_pages_created_at ON scraped_pages(created_at)
            """)
    
    async def store_page(self, page: ScrapedPage) -> bool:
        """Store a scraped page."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO scraped_pages 
                    (url, title, content, html, status_code, content_type, 
                     headers, links, images, metadata, depth, parent_url, 
                     scraped_at, domain, content_hash)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        html = EXCLUDED.html,
                        status_code = EXCLUDED.status_code,
                        content_type = EXCLUDED.content_type,
                        headers = EXCLUDED.headers,
                        links = EXCLUDED.links,
                        images = EXCLUDED.images,
                        metadata = EXCLUDED.metadata,
                        depth = EXCLUDED.depth,
                        parent_url = EXCLUDED.parent_url,
                        scraped_at = EXCLUDED.scraped_at,
                        domain = EXCLUDED.domain,
                        content_hash = EXCLUDED.content_hash
                """, 
                    page.url,
                    page.title,
                    page.content,
                    page.html,
                    page.status_code,
                    page.content_type,
                    json.dumps(page.headers),
                    json.dumps(page.links),
                    json.dumps(page.images),
                    json.dumps(page.metadata),
                    page.depth,
                    page.parent_url,
                    page.scraped_at,
                    page.domain,
                    page.content_hash
                )
                return True
        except Exception as e:
            print(f"Error storing page {page.url}: {e}")
            return False
    
    async def get_page(self, url: str) -> Optional[ScrapedPage]:
        """Retrieve a scraped page by URL."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT url, title, content, html, status_code, content_type,
                           headers, links, images, metadata, depth, parent_url,
                           scraped_at, domain, content_hash
                    FROM scraped_pages WHERE url = $1
                """, url)
                
                if row:
                    return ScrapedPage(
                        url=row['url'],
                        title=row['title'] or "",
                        content=row['content'] or "",
                        html=row['html'] or "",
                        status_code=row['status_code'] or 0,
                        content_type=row['content_type'] or "",
                        headers=json.loads(row['headers']) if row['headers'] else {},
                        links=json.loads(row['links']) if row['links'] else [],
                        images=json.loads(row['images']) if row['images'] else [],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        depth=row['depth'] or 0,
                        parent_url=row['parent_url'],
                        scraped_at=row['scraped_at'] if row['scraped_at'] else datetime.now(timezone.utc),
                        domain=row['domain'] or "",
                        content_hash=row['content_hash'] or ""
                    )
                return None
        except Exception as e:
            print(f"Error retrieving page {url}: {e}")
            return None
    
    async def page_exists(self, url: str) -> bool:
        """Check if a page exists in storage."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM scraped_pages WHERE url = $1
                """, url)
                return count > 0
        except Exception:
            return False
    
    async def should_rescrape(self, url: str, rescrape_after_days: Optional[int] = None, 
                             rescrape_after_months: Optional[int] = None) -> bool:
        """Check if a page should be re-scraped based on age."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT scraped_at FROM scraped_pages WHERE url = $1
                """, url)
                
                if not row:
                    return True  # Page doesn't exist, should scrape
                
                scraped_at = row['scraped_at']
                if not scraped_at:
                    return True  # No scrape date, should scrape
                
                # Use the utility function to check if stale
                return is_page_stale(scraped_at, rescrape_after_days, rescrape_after_months)
                
        except Exception as e:
            print(f"Error checking page age for {url}: {e}")
            return True  # On error, default to scraping
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                # Total pages
                total_pages = await conn.fetchval("SELECT COUNT(*) FROM scraped_pages")
                
                # Pages by domain
                domain_rows = await conn.fetch("""
                    SELECT domain, COUNT(*) as count 
                    FROM scraped_pages 
                    GROUP BY domain 
                    ORDER BY count DESC
                """)
                domain_stats = {row['domain']: row['count'] for row in domain_rows}
                
                # Recent pages (last hour)
                recent_pages = await conn.fetchval("""
                    SELECT COUNT(*) FROM scraped_pages 
                    WHERE scraped_at > NOW() - INTERVAL '1 hour'
                """)
                
                # Database size (approximate)
                db_size = await conn.fetchval("""
                    SELECT pg_size_pretty(pg_total_relation_size('scraped_pages'))
                """)
                
                return {
                    'total_pages': total_pages,
                    'domain_stats': domain_stats,
                    'recent_pages': recent_pages,
                    'storage_type': 'postgresql',
                    'database_url': self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url,  # Hide credentials
                    'database_size': db_size
                }
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pages_by_domain(self, domain: str, limit: int = 100) -> List[ScrapedPage]:
        """Get pages for a specific domain."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT url, title, content, html, status_code, content_type,
                           headers, links, images, metadata, depth, parent_url,
                           scraped_at, domain, content_hash
                    FROM scraped_pages 
                    WHERE domain = $1 
                    ORDER BY scraped_at DESC 
                    LIMIT $2
                """, domain, limit)
                
                pages = []
                for row in rows:
                    pages.append(ScrapedPage(
                        url=row['url'],
                        title=row['title'] or "",
                        content=row['content'] or "",
                        html=row['html'] or "",
                        status_code=row['status_code'] or 0,
                        content_type=row['content_type'] or "",
                        headers=json.loads(row['headers']) if row['headers'] else {},
                        links=json.loads(row['links']) if row['links'] else [],
                        images=json.loads(row['images']) if row['images'] else [],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        depth=row['depth'] or 0,
                        parent_url=row['parent_url'],
                        scraped_at=row['scraped_at'] if row['scraped_at'] else datetime.now(timezone.utc),
                        domain=row['domain'] or "",
                        content_hash=row['content_hash'] or ""
                    ))
                return pages
        except Exception as e:
            print(f"Error retrieving pages for domain {domain}: {e}")
            return []
    
    async def delete_old_pages(self, older_than_days: int) -> int:
        """Delete pages older than specified days. Returns count of deleted pages."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM scraped_pages 
                    WHERE scraped_at < NOW() - INTERVAL '%s days'
                """, older_than_days)
                
                # Extract number of deleted rows from result
                deleted_count = int(result.split()[-1]) if result else 0
                return deleted_count
        except Exception as e:
            print(f"Error deleting old pages: {e}")
            return 0
    
    async def close(self):
        """Close PostgreSQL connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


class S3Storage(StorageBackend):
    """S3 storage backend."""
    
    def __init__(self, bucket_name: str, aws_access_key_id: str = None, 
                 aws_secret_access_key: str = None, region_name: str = 'us-east-1'):
        
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    
    def _get_key(self, url: str) -> str:
        """Generate S3 key for URL."""
        return f"pages/{generate_url_hash(url)}.json"
    
    async def store_page(self, page: ScrapedPage) -> bool:
        """Store a scraped page to S3."""
        try:
            key = self._get_key(page.url)
            data = page.to_dict()
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=json.dumps(data, indent=2),
                    ContentType='application/json'
                )
            )
            return True
        except Exception as e:
            print(f"Error storing page {page.url} to S3: {e}")
            return False
    
    async def get_page(self, url: str) -> Optional[ScrapedPage]:
        """Retrieve a scraped page from S3."""
        try:
            key = self._get_key(url)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            )
            
            data = json.loads(response['Body'].read().decode('utf-8'))
            return ScrapedPage.from_dict(data)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            print(f"Error retrieving page {url} from S3: {e}")
            return None
        except Exception as e:
            print(f"Error retrieving page {url} from S3: {e}")
            return None
    
    async def page_exists(self, url: str) -> bool:
        """Check if a page exists in S3."""
        try:
            key = self._get_key(url)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            print(f"Error checking page {url} in S3: {e}")
            return False
        except Exception as e:
            print(f"Error checking page {url} in S3: {e}")
            return False
    
    async def should_rescrape(self, url: str, rescrape_after_days: Optional[int] = None, 
                             rescrape_after_months: Optional[int] = None) -> bool:
        """Check if a page should be re-scraped based on age."""
        try:
            # Get the page to check its scraped_at date
            page = await self.get_page(url)
            if not page:
                return True  # Page doesn't exist, should scrape
            
            # Use the utility function to check if stale
            # Handle both package and direct imports
            try:
                from .utils import is_page_stale
            except ImportError:
                from utils import is_page_stale
            
            return is_page_stale(page.scraped_at, rescrape_after_days, rescrape_after_months)
            
        except Exception as e:
            print(f"Error checking page age for {url}: {e}")
            return True  # On error, default to scraping
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get S3 storage statistics."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix='pages/'
                )
            )
            
            objects = response.get('Contents', [])
            total_size = sum(obj['Size'] for obj in objects)
            
            return {
                'total_pages': len(objects),
                'total_size_bytes': total_size,
                'storage_type': 's3',
                'bucket_name': self.bucket_name
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def close(self):
        """Close S3 connection."""
        # S3 client doesn't need explicit closing
        pass


class FileStorage(StorageBackend):
    """File-based storage backend."""
    
    def __init__(self, base_path: str = "scraped_pages"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def _get_file_path(self, url: str) -> Path:
        """Generate file path for URL."""
        return self.base_path / f"{generate_url_hash(url)}.json"
    
    async def store_page(self, page: ScrapedPage) -> bool:
        """Store a scraped page to file."""
        try:
            file_path = self._get_file_path(page.url)
            data = page.to_dict()
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error storing page {page.url} to file: {e}")
            return False
    
    async def get_page(self, url: str) -> Optional[ScrapedPage]:
        """Retrieve a scraped page from file."""
        try:
            file_path = self._get_file_path(url)
            
            if not await aiofiles.os.path.exists(file_path):
                return None
            
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                return ScrapedPage.from_dict(data)
        except Exception as e:
            print(f"Error retrieving page {url} from file: {e}")
            return None
    
    async def page_exists(self, url: str) -> bool:
        """Check if a page exists in file storage."""
        try:
            file_path = self._get_file_path(url)
            return await aiofiles.os.path.exists(file_path)
        except Exception:
            return False
    
    async def should_rescrape(self, url: str, rescrape_after_days: Optional[int] = None, 
                             rescrape_after_months: Optional[int] = None) -> bool:
        """Check if a page should be re-scraped based on age."""
        try:
            # Get the page to check its scraped_at date
            page = await self.get_page(url)
            if not page:
                return True  # Page doesn't exist, should scrape
            
            # Use the utility function to check if stale
            # Handle both package and direct imports
            try:
                from .utils import is_page_stale
            except ImportError:
                from utils import is_page_stale
            
            return is_page_stale(page.scraped_at, rescrape_after_days, rescrape_after_months)
            
        except Exception as e:
            print(f"Error checking page age for {url}: {e}")
            return True  # On error, default to scraping
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        try:
            files = list(self.base_path.glob("*.json"))
            total_size = sum(f.stat().st_size for f in files)
            
            return {
                'total_pages': len(files),
                'total_size_bytes': total_size,
                'storage_type': 'file',
                'base_path': str(self.base_path)
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def close(self):
        """Close file storage."""
        # File storage doesn't need explicit closing
        pass


def create_storage_backend(storage_type: str, **kwargs) -> StorageBackend:
    """Factory function to create storage backend."""
    if storage_type == 'sqlite':
        return SQLiteStorage(**kwargs)
    elif storage_type == 'postgresql' or storage_type == 'postgres':
        return PostgreSQLStorage(**kwargs)
    elif storage_type == 's3':
        return S3Storage(**kwargs)
    elif storage_type == 'file':
        return FileStorage(**kwargs)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}") 
    

def create_postgres_storage_from_config(config_path: str|None=None) -> PostgreSQLStorage:
    """Create PostgreSQL storage backend from configuration."""
    config = get_configuration(config_path)
    return PostgreSQLStorage(**config['postgres'])