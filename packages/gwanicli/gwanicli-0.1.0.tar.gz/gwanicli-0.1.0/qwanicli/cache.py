"""
Caching layer for API responses to reduce network requests and improve performance.
Uses SQLite3 for persistent storage with TTL-based expiration.
"""

import sqlite3
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Cache:
    """SQLite-based cache for API responses with TTL support."""

    def __init__(self, cache_dir: Optional[str] = None, ttl: Optional[int] = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache database (optional)
            ttl: Time-to-live in seconds (optional, uses config default)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.cache' / 'gwanicli'

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / 'cache.db'

        self.ttl = ttl or 86400  # Default 24 hours
        self._init_database()

    def _init_database(self):
        """Initialize the cache database with required tables."""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        expires_at REAL NOT NULL
                    )
                ''')

                # Create index for faster expiration queries
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON cache_entries(expires_at)
                ''')

                conn.commit()
                logger.debug(f"Initialized cache database at {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _generate_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key from endpoint and parameters.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            SHA-256 hash of the normalized key data
        """
        key_data = {
            'endpoint': endpoint,
            'params': params or {}
        }

        # Normalize and serialize for consistent hashing
        key_string = json.dumps(
            key_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data for the given endpoint and parameters.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            Cached data if valid and not expired, None otherwise
        """
        key = self._generate_key(endpoint, params)
        current_time = time.time()

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'SELECT data, expires_at FROM cache_entries WHERE key = ? AND expires_at > ?',
                    (key, current_time)
                )
                row = cursor.fetchone()

                if row:
                    try:
                        data = json.loads(row['data'])
                        logger.debug(f"Cache hit for key: {key[:16]}...")
                        return data
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Invalid JSON in cache for key {key[:16]}...: {e}")
                        self._delete_key(key)
                        return None
                else:
                    logger.debug(f"Cache miss for key: {key[:16]}...")
                    return None

        except sqlite3.Error as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def set(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None,
            ttl: Optional[int] = None) -> bool:
        """
        Store data in cache with expiration.

        Args:
            endpoint: API endpoint
            data: Data to cache
            params: Request parameters
            ttl: Custom TTL in seconds (optional)

        Returns:
            True if cached successfully, False otherwise
        """
        key = self._generate_key(endpoint, params)
        current_time = time.time()
        expires_at = current_time + (ttl or self.ttl)

        try:
            data_json = json.dumps(data, separators=(',', ':'))

            with self._get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (key, data, created_at, expires_at) 
                    VALUES (?, ?, ?, ?)
                ''', (key, data_json, current_time, expires_at))

                conn.commit()
                logger.debug(f"Cached data for key: {key[:16]}...")
                return True

        except (sqlite3.Error, json.JSONEncodeError) as e:
            logger.error(f"Cache storage error: {e}")
            return False

    def _delete_key(self, key: str) -> bool:
        """Delete a specific cache entry."""
        try:
            with self._get_connection() as conn:
                conn.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def clear_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        current_time = time.time()

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'DELETE FROM cache_entries WHERE expires_at <= ?', (current_time,))
                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    logger.info(
                        f"Cleared {deleted_count} expired cache entries")

                return deleted_count

        except sqlite3.Error as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute('DELETE FROM cache_entries')
                conn.commit()
                logger.info("Cleared all cache entries")
                return True

        except sqlite3.Error as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()

        try:
            with self._get_connection() as conn:
                # Total entries
                cursor = conn.execute(
                    'SELECT COUNT(*) as total FROM cache_entries')
                total = cursor.fetchone()['total']

                # Valid (non-expired) entries
                cursor = conn.execute(
                    'SELECT COUNT(*) as valid FROM cache_entries WHERE expires_at > ?', (current_time,))
                valid = cursor.fetchone()['valid']

                # Expired entries
                expired = total - valid

                # Database size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

                return {
                    'total_entries': total,
                    'valid_entries': valid,
                    'expired_entries': expired,
                    'database_size_bytes': db_size,
                    'database_path': str(self.db_path)
                }

        except (sqlite3.Error, OSError) as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    def vacuum(self) -> bool:
        """
        Optimize the database by running VACUUM.

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute('VACUUM')
                logger.info("Database vacuum completed")
                return True

        except sqlite3.Error as e:
            logger.error(f"Error during database vacuum: {e}")
            return False


class CacheWrapper:
    """Wrapper to add caching functionality to API client methods."""

    def __init__(self, api_client, cache: Optional[Cache] = None):
        """
        Initialize cache wrapper.

        Args:
            api_client: API client instance to wrap
            cache: Cache instance (optional, creates new if None)
        """
        self.api_client = api_client
        self.cache = cache or Cache()

    def get_random_ayah(self, translation: str = "en.pickthall") -> Dict[str, Any]:
        """
        Get random ayah with caching.

        Note: Random endpoints typically shouldn't be cached,
        but this provides the option for testing or specific use cases.
        """
        # For random endpoints, we might want to skip caching or use short TTL
        endpoint = f"random_ayah"
        params = {'translation': translation}

        # Check cache first (with short TTL for random content)
        cached_data = self.cache.get(endpoint, params)
        if cached_data:
            return cached_data

        # Fetch from API
        data = self.api_client.get_random_ayah(translation)

        # Cache with short TTL (e.g., 5 minutes for random content)
        self.cache.set(endpoint, data, params, ttl=300)

        return data

    def get_ayah_from_surah(self, surah: Union[str, int], ayah: Optional[int] = None,
                            translation: str = "en.pickthall") -> Dict[str, Any]:
        """Get ayah from surah with caching."""
        endpoint = f"surah/{surah}/ayah/{ayah}" if ayah else f"surah/{surah}"
        params = {'translation': translation}

        # Check cache first
        cached_data = self.cache.get(endpoint, params)
        if cached_data:
            return cached_data

        # Fetch from API
        data = self.api_client.get_ayah_from_surah(surah, ayah, translation)

        # Cache the result
        self.cache.set(endpoint, data, params)

        return data
