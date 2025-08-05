Extending Backends
==================

This guide explains how to create custom cache backends for the Cache Middleware, including implementation patterns, best practices, and complete examples.

Backend Interface
-----------------

Abstract Base Class
~~~~~~~~~~~~~~~~~~~

All cache backends must implement the ``CacheBackend`` interface:

.. code-block:: python

   from abc import ABC, abstractmethod
   from typing import Optional

   class CacheBackend(ABC):
       """
       Abstract base class for cache backends.
       
       All cache backends must implement these methods to provide
       consistent caching functionality across different storage systems.
       """
       
       @abstractmethod
       async def get(self, key: str) -> Optional[str]:
           """
           Retrieve a value from the cache.
           
           Parameters
           ----------
           key : str
               The cache key to retrieve
               
           Returns
           -------
           Optional[str]
               The cached value if found and not expired, None otherwise
           """
           pass
       
       @abstractmethod
       async def set(self, key: str, value: str, timeout: int) -> None:
           """
           Store a value in the cache with expiration.
           
           Parameters
           ----------
           key : str
               The cache key to store
           value : str
               The value to cache (JSON serialized response)
           timeout : int
               Expiration time in seconds
           """
           pass
       
       @abstractmethod
       async def delete(self, key: str) -> None:
           """
           Remove a key from the cache.
           
           Parameters
           ----------
           key : str
               The cache key to delete
           """
           pass
       
       @abstractmethod
       async def close(self) -> None:
           """
           Close backend connections and clean up resources.
           
           This method is called when the application shuts down
           to ensure proper cleanup of connections and resources.
           """
           pass

Implementation Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~

**Required Methods:**

1. **get()**: Must return ``None`` for missing or expired keys
2. **set()**: Must handle expiration correctly
3. **delete()**: Must be idempotent (safe to call on non-existent keys)
4. **close()**: Must clean up all resources properly

**Optional Methods:**

You can add additional methods for backend-specific functionality:

.. code-block:: python

   class ExtendedBackend(CacheBackend):
       async def exists(self, key: str) -> bool:
           """Check if a key exists without retrieving the value."""
           value = await self.get(key)
           return value is not None
       
       async def clear(self) -> None:
           """Clear all cached data."""
           pass
       
       async def keys(self, pattern: str = "*") -> list[str]:
           """Get all keys matching a pattern."""
           pass

Simple Custom Backend
---------------------

File-Based Cache Backend
~~~~~~~~~~~~~~~~~~~~~~~~

Here's a complete implementation of a file-based cache backend:

.. code-block:: python

   import os
   import json
   import time
   import aiofiles
   import asyncio
   from pathlib import Path
   from typing import Optional
   from cache_middleware.backends.base import CacheBackend

   class FileBackend(CacheBackend):
       """
       File-based cache backend that stores cache entries as JSON files.
       
       Parameters
       ----------
       cache_dir : str
           Directory to store cache files
       cleanup_interval : int
           Seconds between cleanup runs (default: 300)
       max_file_age : int
           Maximum age of cache files in seconds (default: 3600)
       """
       
       def __init__(
           self, 
           cache_dir: str = "/tmp/cache", 
           cleanup_interval: int = 300,
           max_file_age: int = 3600
       ):
           self.cache_dir = Path(cache_dir)
           self.cleanup_interval = cleanup_interval
           self.max_file_age = max_file_age
           self._cleanup_task = None
           
           # Ensure cache directory exists
           self.cache_dir.mkdir(parents=True, exist_ok=True)
           
           # Start background cleanup task
           self._start_cleanup_task()
       
       def _get_file_path(self, key: str) -> Path:
           """Generate file path for cache key."""
           # Use key hash as filename to avoid filesystem issues
           import hashlib
           key_hash = hashlib.sha256(key.encode()).hexdigest()
           return self.cache_dir / f"{key_hash}.json"
       
       async def get(self, key: str) -> Optional[str]:
           """Retrieve value from file cache."""
           file_path = self._get_file_path(key)
           
           try:
               async with aiofiles.open(file_path, 'r') as f:
                   data = json.loads(await f.read())
               
               # Check if expired
               if data['expires'] < time.time():
                   # Remove expired file
                   await self._remove_file(file_path)
                   return None
               
               return data['value']
           
           except (FileNotFoundError, json.JSONDecodeError, KeyError):
               return None
       
       async def set(self, key: str, value: str, timeout: int) -> None:
           """Store value in file cache."""
           file_path = self._get_file_path(key)
           expires = time.time() + timeout
           
           data = {
               'key': key,
               'value': value,
               'expires': expires,
               'created': time.time()
           }
           
           async with aiofiles.open(file_path, 'w') as f:
               await f.write(json.dumps(data))
       
       async def delete(self, key: str) -> None:
           """Delete key from file cache."""
           file_path = self._get_file_path(key)
           await self._remove_file(file_path)
       
       async def _remove_file(self, file_path: Path) -> None:
           """Safely remove a cache file."""
           try:
               file_path.unlink()
           except FileNotFoundError:
               pass  # File already removed
       
       def _start_cleanup_task(self) -> None:
           """Start background cleanup task."""
           async def cleanup_loop():
               while True:
                   await asyncio.sleep(self.cleanup_interval)
                   await self._cleanup_expired_files()
           
           self._cleanup_task = asyncio.create_task(cleanup_loop())
       
       async def _cleanup_expired_files(self) -> None:
           """Remove expired cache files."""
           current_time = time.time()
           
           for file_path in self.cache_dir.glob("*.json"):
               try:
                   # Check file modification time first (faster)
                   if file_path.stat().st_mtime < current_time - self.max_file_age:
                       await self._remove_file(file_path)
                       continue
                   
                   # Check expiration time in file content
                   async with aiofiles.open(file_path, 'r') as f:
                       data = json.loads(await f.read())
                   
                   if data.get('expires', 0) < current_time:
                       await self._remove_file(file_path)
               
               except (json.JSONDecodeError, KeyError, OSError):
                   # Remove corrupted files
                   await self._remove_file(file_path)
       
       async def close(self) -> None:
           """Clean up resources and stop background tasks."""
           if self._cleanup_task:
               self._cleanup_task.cancel()
               try:
                   await self._cleanup_task
               except asyncio.CancelledError:
                   pass
       
       # Additional utility methods
       async def clear(self) -> None:
           """Remove all cache files."""
           for file_path in self.cache_dir.glob("*.json"):
               await self._remove_file(file_path)
       
       async def size(self) -> int:
           """Get number of cached items."""
           return len(list(self.cache_dir.glob("*.json")))

Advanced Custom Backend
-----------------------

Database-Backed Cache
~~~~~~~~~~~~~~~~~~~~~

A more sophisticated backend using SQLite for persistence:

.. code-block:: python

   import aiosqlite
   import json
   import time
   from typing import Optional
   from cache_middleware.backends.base import CacheBackend

   class SQLiteBackend(CacheBackend):
       """
       SQLite-based cache backend with persistent storage.
       
       Parameters
       ----------
       db_path : str
           Path to SQLite database file
       table_name : str
           Name of cache table (default: 'cache_entries')
       max_entries : int
           Maximum number of cache entries (default: 10000)
       cleanup_interval : int
           Seconds between cleanup runs (default: 300)
       """
       
       def __init__(
           self, 
           db_path: str = "cache.db", 
           table_name: str = "cache_entries",
           max_entries: int = 10000,
           cleanup_interval: int = 300
       ):
           self.db_path = db_path
           self.table_name = table_name
           self.max_entries = max_entries
           self.cleanup_interval = cleanup_interval
           self._connection = None
           self._cleanup_task = None
       
       async def _get_connection(self) -> aiosqlite.Connection:
           """Get or create database connection."""
           if self._connection is None:
               self._connection = await aiosqlite.connect(self.db_path)
               await self._initialize_database()
               self._start_cleanup_task()
           return self._connection
       
       async def _initialize_database(self) -> None:
           """Create cache table if it doesn't exist."""
           await self._connection.execute(f"""
               CREATE TABLE IF NOT EXISTS {self.table_name} (
                   key TEXT PRIMARY KEY,
                   value TEXT NOT NULL,
                   expires REAL NOT NULL,
                   created REAL NOT NULL DEFAULT (julianday('now'))
               )
           """)
           
           # Create index on expires for efficient cleanup
           await self._connection.execute(f"""
               CREATE INDEX IF NOT EXISTS idx_{self.table_name}_expires 
               ON {self.table_name}(expires)
           """)
           
           await self._connection.commit()
       
       async def get(self, key: str) -> Optional[str]:
           """Retrieve value from SQLite cache."""
           conn = await self._get_connection()
           current_time = time.time()
           
           async with conn.execute(
               f"SELECT value FROM {self.table_name} WHERE key = ? AND expires > ?",
               (key, current_time)
           ) as cursor:
               row = await cursor.fetchone()
               return row[0] if row else None
       
       async def set(self, key: str, value: str, timeout: int) -> None:
           """Store value in SQLite cache."""
           conn = await self._get_connection()
           expires = time.time() + timeout
           
           # Use REPLACE to handle key conflicts
           await conn.execute(
               f"""REPLACE INTO {self.table_name} (key, value, expires) 
                   VALUES (?, ?, ?)""",
               (key, value, expires)
           )
           await conn.commit()
           
           # Enforce max entries limit
           await self._enforce_max_entries()
       
       async def delete(self, key: str) -> None:
           """Delete key from SQLite cache."""
           conn = await self._get_connection()
           await conn.execute(f"DELETE FROM {self.table_name} WHERE key = ?", (key,))
           await conn.commit()
       
       async def _enforce_max_entries(self) -> None:
           """Remove oldest entries if max_entries exceeded."""
           conn = await self._get_connection()
           
           # Count current entries
           async with conn.execute(f"SELECT COUNT(*) FROM {self.table_name}") as cursor:
               count = (await cursor.fetchone())[0]
           
           if count > self.max_entries:
               # Remove oldest entries
               excess = count - self.max_entries
               await conn.execute(f"""
                   DELETE FROM {self.table_name} 
                   WHERE key IN (
                       SELECT key FROM {self.table_name} 
                       ORDER BY created ASC 
                       LIMIT ?
                   )
               """, (excess,))
               await conn.commit()
       
       def _start_cleanup_task(self) -> None:
           """Start background cleanup task."""
           async def cleanup_loop():
               while True:
                   await asyncio.sleep(self.cleanup_interval)
                   await self._cleanup_expired_entries()
           
           self._cleanup_task = asyncio.create_task(cleanup_loop())
       
       async def _cleanup_expired_entries(self) -> None:
           """Remove expired entries from database."""
           conn = await self._get_connection()
           current_time = time.time()
           
           await conn.execute(
               f"DELETE FROM {self.table_name} WHERE expires <= ?", 
               (current_time,)
           )
           await conn.commit()
       
       async def close(self) -> None:
           """Close database connection and cleanup tasks."""
           if self._cleanup_task:
               self._cleanup_task.cancel()
               try:
                   await self._cleanup_task
               except asyncio.CancelledError:
                   pass
           
           if self._connection:
               await self._connection.close()
               self._connection = None
       
       # Extended functionality
       async def clear(self) -> None:
           """Remove all cache entries."""
           conn = await self._get_connection()
           await conn.execute(f"DELETE FROM {self.table_name}")
           await conn.commit()
       
       async def stats(self) -> dict:
           """Get cache statistics."""
           conn = await self._get_connection()
           current_time = time.time()
           
           # Total entries
           async with conn.execute(f"SELECT COUNT(*) FROM {self.table_name}") as cursor:
               total = (await cursor.fetchone())[0]
           
           # Active (non-expired) entries
           async with conn.execute(
               f"SELECT COUNT(*) FROM {self.table_name} WHERE expires > ?", 
               (current_time,)
           ) as cursor:
               active = (await cursor.fetchone())[0]
           
           # Database size
           async with conn.execute("PRAGMA page_count") as cursor:
               page_count = (await cursor.fetchone())[0]
           async with conn.execute("PRAGMA page_size") as cursor:
               page_size = (await cursor.fetchone())[0]
           
           return {
               "total_entries": total,
               "active_entries": active,
               "expired_entries": total - active,
               "database_size_bytes": page_count * page_size,
               "max_entries": self.max_entries
           }

External Service Backend
------------------------

HTTP API Cache Backend
~~~~~~~~~~~~~~~~~~~~~~

Backend that uses an external HTTP API for caching:

.. code-block:: python

   import aiohttp
   import json
   from typing import Optional
   from cache_middleware.backends.base import CacheBackend

   class HTTPAPIBackend(CacheBackend):
       """
       Cache backend that uses an external HTTP API.
       
       Parameters
       ----------
       base_url : str
           Base URL of the cache API
       auth_token : str, optional
           Authentication token for API access
       timeout : int
           Request timeout in seconds (default: 5)
       max_retries : int
           Maximum number of retry attempts (default: 3)
       """
       
       def __init__(
           self, 
           base_url: str, 
           auth_token: Optional[str] = None,
           timeout: int = 5,
           max_retries: int = 3
       ):
           self.base_url = base_url.rstrip('/')
           self.auth_token = auth_token
           self.timeout = aiohttp.ClientTimeout(total=timeout)
           self.max_retries = max_retries
           self._session = None
       
       async def _get_session(self) -> aiohttp.ClientSession:
           """Get or create HTTP session."""
           if self._session is None:
               headers = {}
               if self.auth_token:
                   headers['Authorization'] = f'Bearer {self.auth_token}'
               
               self._session = aiohttp.ClientSession(
                   headers=headers,
                   timeout=self.timeout,
                   connector=aiohttp.TCPConnector(limit=100)
               )
           return self._session
       
       async def _make_request(self, method: str, path: str, **kwargs) -> dict:
           """Make HTTP request with retry logic."""
           session = await self._get_session()
           url = f"{self.base_url}{path}"
           
           for attempt in range(self.max_retries):
               try:
                   async with session.request(method, url, **kwargs) as response:
                       if response.status == 200:
                           return await response.json()
                       elif response.status == 404:
                           return None
                       else:
                           response.raise_for_status()
               
               except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                   if attempt == self.max_retries - 1:
                       raise
                   await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
       
       async def get(self, key: str) -> Optional[str]:
           """Retrieve value from HTTP API cache."""
           try:
               result = await self._make_request('GET', f'/cache/{key}')
               return result.get('value') if result else None
           except Exception:
               # Return None on any error to fail gracefully
               return None
       
       async def set(self, key: str, value: str, timeout: int) -> None:
           """Store value in HTTP API cache."""
           data = {
               'value': value,
               'timeout': timeout
           }
           await self._make_request('PUT', f'/cache/{key}', json=data)
       
       async def delete(self, key: str) -> None:
           """Delete key from HTTP API cache."""
           try:
               await self._make_request('DELETE', f'/cache/{key}')
           except aiohttp.ClientResponseError as e:
               if e.status != 404:  # Ignore not found errors
                   raise
       
       async def close(self) -> None:
           """Close HTTP session."""
           if self._session:
               await self._session.close()
               self._session = None

Backend Composition
-------------------

Multi-Tier Cache Backend
~~~~~~~~~~~~~~~~~~~~~~~~

Combine multiple backends for a hierarchical cache:

.. code-block:: python

   from typing import List
   from cache_middleware.backends.base import CacheBackend
   from cache_middleware.backends.memory_backend import MemoryBackend
   from cache_middleware.backends.redis_backend import RedisBackend

   class MultiTierBackend(CacheBackend):
       """
       Multi-tier cache backend with L1 (memory) and L2 (Redis) cache.
       
       Parameters
       ----------
       l1_backend : CacheBackend
           Fast L1 cache (typically memory-based)
       l2_backend : CacheBackend
           Slower but larger L2 cache (typically Redis)
       l1_timeout_ratio : float
           Ratio of L1 to L2 timeout (default: 0.5)
       """
       
       def __init__(
           self, 
           l1_backend: CacheBackend, 
           l2_backend: CacheBackend,
           l1_timeout_ratio: float = 0.5
       ):
           self.l1_backend = l1_backend
           self.l2_backend = l2_backend
           self.l1_timeout_ratio = l1_timeout_ratio
       
       async def get(self, key: str) -> Optional[str]:
           """Get value from L1 cache, fallback to L2."""
           # Try L1 cache first
           value = await self.l1_backend.get(key)
           if value is not None:
               return value
           
           # Fallback to L2 cache
           value = await self.l2_backend.get(key)
           if value is not None:
               # Populate L1 cache for future requests
               l1_timeout = int(300 * self.l1_timeout_ratio)  # Shorter L1 timeout
               await self.l1_backend.set(key, value, l1_timeout)
           
           return value
       
       async def set(self, key: str, value: str, timeout: int) -> None:
           """Set value in both L1 and L2 caches."""
           # Set in L2 with full timeout
           await self.l2_backend.set(key, value, timeout)
           
           # Set in L1 with shorter timeout
           l1_timeout = int(timeout * self.l1_timeout_ratio)
           await self.l1_backend.set(key, value, max(l1_timeout, 60))
       
       async def delete(self, key: str) -> None:
           """Delete key from both caches."""
           await self.l1_backend.delete(key)
           await self.l2_backend.delete(key)
       
       async def close(self) -> None:
           """Close both backends."""
           await self.l1_backend.close()
           await self.l2_backend.close()

   # Usage example
   def create_multi_tier_backend():
       l1_cache = MemoryBackend(max_size=1000)  # Fast but limited
       l2_cache = RedisBackend(url="redis://localhost:6379")  # Slower but scalable
       return MultiTierBackend(l1_cache, l2_cache)

Testing Custom Backends
------------------------

Backend Test Suite
~~~~~~~~~~~~~~~~~~

Create comprehensive tests for your custom backend:

.. code-block:: python

   import pytest
   import asyncio
   from your_backend import CustomBackend

   @pytest.fixture
   async def backend():
       """Create backend instance for testing."""
       backend = CustomBackend()
       yield backend
       await backend.close()

   @pytest.mark.asyncio
   class TestCustomBackend:
       async def test_get_nonexistent_key(self, backend):
           """Test getting a non-existent key returns None."""
           result = await backend.get("nonexistent")
           assert result is None
       
       async def test_set_and_get(self, backend):
           """Test basic set and get operations."""
           await backend.set("test_key", "test_value", 300)
           result = await backend.get("test_key")
           assert result == "test_value"
       
       async def test_expiration(self, backend):
           """Test that keys expire correctly."""
           await backend.set("expire_key", "value", 1)  # 1 second timeout
           
           # Should exist immediately
           result = await backend.get("expire_key")
           assert result == "value"
           
           # Should be expired after 2 seconds
           await asyncio.sleep(2)
           result = await backend.get("expire_key")
           assert result is None
       
       async def test_delete(self, backend):
           """Test key deletion."""
           await backend.set("delete_key", "value", 300)
           await backend.delete("delete_key")
           result = await backend.get("delete_key")
           assert result is None
       
       async def test_delete_nonexistent(self, backend):
           """Test deleting non-existent key doesn't raise error."""
           # Should not raise an exception
           await backend.delete("nonexistent")
       
       async def test_concurrent_operations(self, backend):
           """Test concurrent access to backend."""
           async def set_operation(i):
               await backend.set(f"key_{i}", f"value_{i}", 300)
           
           async def get_operation(i):
               return await backend.get(f"key_{i}")
           
           # Set values concurrently
           await asyncio.gather(*[set_operation(i) for i in range(10)])
           
           # Get values concurrently
           results = await asyncio.gather(*[get_operation(i) for i in range(10)])
           
           # Verify all values were set correctly
           for i, result in enumerate(results):
               assert result == f"value_{i}"

Performance Testing
~~~~~~~~~~~~~~~~~~~

Benchmark your custom backend:

.. code-block:: python

   import time
   import asyncio
   from typing import List

   async def benchmark_backend(backend: CacheBackend, operations: int = 1000):
       """Benchmark backend performance."""
       
       # Set operations
       start_time = time.time()
       for i in range(operations):
           await backend.set(f"benchmark_key_{i}", f"value_{i}", 300)
       set_duration = time.time() - start_time
       
       # Get operations
       start_time = time.time()
       for i in range(operations):
           await backend.get(f"benchmark_key_{i}")
       get_duration = time.time() - start_time
       
       # Cleanup
       for i in range(operations):
           await backend.delete(f"benchmark_key_{i}")
       
       return {
           "operations": operations,
           "set_ops_per_second": operations / set_duration,
           "get_ops_per_second": operations / get_duration,
           "set_duration": set_duration,
           "get_duration": get_duration
       }

Best Practices
--------------

Error Handling
~~~~~~~~~~~~~~

Implement robust error handling:

.. code-block:: python

   class RobustBackend(CacheBackend):
       async def get(self, key: str) -> Optional[str]:
           try:
               return await self._internal_get(key)
           except Exception as e:
               logger.warning(f"Cache get failed for key {key}: {e}")
               return None  # Fail gracefully
       
       async def set(self, key: str, value: str, timeout: int) -> None:
           try:
               await self._internal_set(key, value, timeout)
           except Exception as e:
               logger.error(f"Cache set failed for key {key}: {e}")
               # Don't raise - caching should not break the application

Resource Management
~~~~~~~~~~~~~~~~~~~

Proper resource cleanup:

.. code-block:: python

   class ResourceManagedBackend(CacheBackend):
       def __init__(self):
           self._connections = []
           self._tasks = []
       
       async def close(self) -> None:
           # Cancel all background tasks
           for task in self._tasks:
               task.cancel()
           
           if self._tasks:
               await asyncio.gather(*self._tasks, return_exceptions=True)
           
           # Close all connections
           for connection in self._connections:
               await connection.close()
           
           self._connections.clear()
           self._tasks.clear()

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~~

Validate configuration parameters:

.. code-block:: python

   class ValidatedBackend(CacheBackend):
       def __init__(self, timeout: int, max_size: int):
           if timeout <= 0:
               raise ValueError("timeout must be positive")
           if max_size <= 0:
               raise ValueError("max_size must be positive")
           
           self.timeout = timeout
           self.max_size = max_size

Next Steps
----------

- See complete working examples in :doc:`user-guide`
- Check the API reference in :doc:`api`
- Learn about configuration options in :doc:`middleware-configuration`
