"""
Cache Module

This module provides caching functionality for the URL Analyzer application,
with support for different cache backends, expiration, and invalidation.
"""

import os
import json
import time
import hashlib
import pickle
import inspect
import functools
import zlib
import gzip
import base64
from typing import Dict, Any, Optional, Union, Callable, TypeVar, Generic, List, Set, Tuple
from datetime import datetime, timedelta
import threading

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Type variable for cache value type
T = TypeVar('T')

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.debug("Redis not available. Redis cache backend will not be available.")

# Try to import Memcached client
try:
    import pymemcache
    from pymemcache.client.base import Client as MemcachedClient
    MEMCACHED_AVAILABLE = True
except ImportError:
    MEMCACHED_AVAILABLE = False
    logger.debug("pymemcache not available. Memcached cache backend will not be available.")


class CacheEntry(Generic[T]):
    """
    A cache entry with value, expiration, and metadata.
    """
    
    def __init__(
        self, 
        value: T, 
        expires_at: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a cache entry.
        
        Args:
            value: The cached value
            expires_at: Timestamp when the entry expires (None for no expiration)
            metadata: Additional metadata for the entry
        """
        self.value = value
        self.expires_at = expires_at
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """
        Check if the cache entry is expired.
        
        Returns:
            True if the entry is expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self) -> None:
        """Update the last accessed timestamp."""
        self.last_accessed = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the cache entry to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the cache entry
        """
        return {
            "value": self.value,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """
        Create a cache entry from a dictionary.
        
        Args:
            data: Dictionary representation of a cache entry
            
        Returns:
            CacheEntry instance
        """
        entry = cls(data["value"], data.get("expires_at"), data.get("metadata", {}))
        entry.created_at = data.get("created_at", time.time())
        entry.last_accessed = data.get("last_accessed", entry.created_at)
        return entry


class Cache:
    """
    A generic cache implementation with support for different backends.
    """
    
    def __init__(
        self, 
        backend: str = "memory",
        file_path: Optional[str] = None,
        default_ttl: Optional[int] = None,
        max_size: Optional[int] = None,
        eviction_policy: str = "lru",
        redis_url: Optional[str] = None,
        redis_prefix: str = "url_analyzer:",
        memcached_servers: Optional[List[str]] = None,
        memcached_prefix: str = "url_analyzer:",
        compression: bool = False,
        compression_level: int = 6,
        invalidation_strategy: str = "ttl",
        prefetch_enabled: bool = False,
        prefetch_threshold: float = 0.8,
        prefetch_patterns: Optional[List[str]] = None,
        analytics_enabled: bool = False,
        adaptive_ttl: bool = False
    ):
        """
        Initialize the cache.
        
        Args:
            backend: Cache backend ("memory", "file", "redis", or "memcached")
            file_path: Path to the cache file (required for "file" backend)
            default_ttl: Default time-to-live in seconds (None for no expiration)
            max_size: Maximum number of entries in the cache (None for unlimited)
            eviction_policy: Policy for evicting entries when the cache is full ("lru" or "fifo")
            redis_url: Redis connection URL (required for "redis" backend)
            redis_prefix: Prefix for Redis keys
            memcached_servers: List of Memcached server addresses (required for "memcached" backend)
            memcached_prefix: Prefix for Memcached keys
            compression: Whether to enable compression for cached values
            compression_level: Compression level (1-9, with 9 being highest compression)
            invalidation_strategy: Strategy for cache invalidation ("ttl", "pattern", or "event")
            prefetch_enabled: Whether to enable intelligent prefetching
            prefetch_threshold: Threshold for prefetching (0.0-1.0, percentage of TTL elapsed)
            prefetch_patterns: List of key patterns to prefetch
            analytics_enabled: Whether to enable detailed cache analytics
            adaptive_ttl: Whether to enable adaptive TTL based on access patterns
        """
        self.backend = backend.lower()
        self.file_path = file_path
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.eviction_policy = eviction_policy.lower()
        self.invalidation_strategy = invalidation_strategy.lower()
        self.prefetch_enabled = prefetch_enabled
        self.prefetch_threshold = max(0.0, min(1.0, prefetch_threshold))  # Clamp to 0.0-1.0
        self.prefetch_patterns = prefetch_patterns or []
        self.prefetch_queue: Set[str] = set()
        self.access_counts: Dict[str, int] = {}
        
        # Initialize compression settings
        self.compression = compression
        self.compression_level = max(1, min(9, compression_level))  # Clamp to 1-9
        
        # Initialize analytics settings
        self.analytics_enabled = analytics_enabled
        if self.analytics_enabled:
            self.hit_count = 0
            self.miss_count = 0
            self.set_count = 0
            self.delete_count = 0
            self.eviction_count = 0
            self.expiration_count = 0
            self.key_access_times: Dict[str, List[float]] = {}
            self.key_size_stats: Dict[str, int] = {}
            self.analytics_start_time = time.time()
        
        # Initialize adaptive TTL settings
        self.adaptive_ttl = adaptive_ttl
        if self.adaptive_ttl:
            self.access_frequency: Dict[str, int] = {}
            self.last_access_time: Dict[str, float] = {}
            self.ttl_adjustments: Dict[str, float] = {}
            self.min_ttl_factor = 0.5  # Minimum TTL adjustment factor
            self.max_ttl_factor = 2.0  # Maximum TTL adjustment factor
        
        # Initialize backend-specific attributes
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        self.redis_client = None
        self.redis_prefix = redis_prefix
        self.memcached_client = None
        self.memcached_prefix = memcached_prefix
        
        # Initialize Redis client if using Redis backend
        if self.backend == "redis":
            if not REDIS_AVAILABLE:
                logger.warning("Redis backend requested but Redis is not available. Falling back to memory backend.")
                self.backend = "memory"
            elif not redis_url:
                logger.warning("Redis backend requested but no Redis URL provided. Falling back to memory backend.")
                self.backend = "memory"
            else:
                try:
                    self.redis_client = redis.from_url(redis_url)
                    # Test connection
                    self.redis_client.ping()
                    logger.info(f"Connected to Redis at {redis_url}")
                except Exception as e:
                    logger.error(f"Failed to connect to Redis at {redis_url}: {e}")
                    logger.warning("Falling back to memory backend.")
                    self.backend = "memory"
        
        # Initialize Memcached client if using Memcached backend
        elif self.backend == "memcached":
            if not MEMCACHED_AVAILABLE:
                logger.warning("Memcached backend requested but pymemcache is not available. Falling back to memory backend.")
                self.backend = "memory"
            elif not memcached_servers:
                logger.warning("Memcached backend requested but no servers provided. Falling back to memory backend.")
                self.backend = "memory"
            else:
                try:
                    # Use the first server for now (could be extended to support multiple servers)
                    server = memcached_servers[0]
                    host, port = server.split(':') if ':' in server else (server, 11211)
                    self.memcached_client = MemcachedClient((host, int(port)))
                    # Test connection
                    self.memcached_client.stats()
                    logger.info(f"Connected to Memcached at {server}")
                except Exception as e:
                    logger.error(f"Failed to connect to Memcached at {memcached_servers}: {e}")
                    logger.warning("Falling back to memory backend.")
                    self.backend = "memory"
        
        # Load cache from file if using file backend
        if self.backend == "file" and self.file_path and os.path.exists(self.file_path):
            self.load()
            
        # Start prefetch thread if enabled
        if self.prefetch_enabled:
            self._start_prefetch_thread()
    
    def _get_expiration_time(self, ttl: Optional[int] = None) -> Optional[float]:
        """
        Calculate the expiration timestamp for a cache entry.
        
        Args:
            ttl: Time-to-live in seconds (None to use default_ttl)
            
        Returns:
            Expiration timestamp or None if no expiration
        """
        ttl = ttl if ttl is not None else self.default_ttl
        if ttl is None:
            return None
        return time.time() + ttl
        
    def _start_prefetch_thread(self) -> None:
        """
        Start a background thread for intelligent prefetching.
        """
        def prefetch_worker():
            """Worker function for prefetching thread."""
            import time
            
            while True:
                try:
                    # Sleep to avoid consuming too many resources
                    time.sleep(5)
                    
                    # Process prefetch queue
                    with self.lock:
                        queue = list(self.prefetch_queue)
                        self.prefetch_queue.clear()
                    
                    # Prefetch items in queue
                    for key in queue:
                        try:
                            # Skip if already in cache
                            if self.backend == "memory" or self.backend == "file":
                                with self.lock:
                                    if key in self.cache and not self.cache[key].is_expired():
                                        continue
                            elif self.backend == "redis" and self.redis_client:
                                if self.redis_client.exists(self._get_redis_key(key)):
                                    continue
                            
                            # Call the prefetch function
                            if key in self._prefetch_callbacks:
                                value = self._prefetch_callbacks[key]()
                                if value is not None:
                                    self.set(key, value)
                                    logger.debug(f"Prefetched value for key: {key}")
                        except Exception as e:
                            logger.error(f"Error prefetching value for key {key}: {e}")
                except Exception as e:
                    logger.error(f"Error in prefetch worker: {e}")
        
        # Initialize prefetch callbacks dictionary
        self._prefetch_callbacks: Dict[str, Callable[[], Any]] = {}
        
        # Start thread
        thread = threading.Thread(target=prefetch_worker, daemon=True)
        thread.start()
        logger.debug("Started prefetch thread")
    
    def _get_redis_key(self, key: str) -> str:
        """
        Get the full Redis key with prefix.
        
        Args:
            key: Cache key
            
        Returns:
            Full Redis key with prefix
        """
        return f"{self.redis_prefix}{key}"
        
    def _compress_data(self, data: bytes) -> bytes:
        """
        Compress data using the configured compression method.
        
        Args:
            data: Data to compress
            
        Returns:
            Compressed data as bytes
        """
        if not self.compression:
            return data
            
        try:
            # Use zlib for compression
            compressed_data = zlib.compress(data, level=self.compression_level)
            logger.debug(f"Compressed data from {len(data)} to {len(compressed_data)} bytes "
                        f"({len(compressed_data)/len(data):.2%} of original size)")
            return compressed_data
        except Exception as e:
            logger.error(f"Error compressing data: {e}")
            return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """
        Decompress data using the configured compression method.
        
        Args:
            data: Compressed data
            
        Returns:
            Decompressed data as bytes
        """
        if not self.compression:
            return data
            
        try:
            # Use zlib for decompression
            return zlib.decompress(data)
        except Exception as e:
            logger.error(f"Error decompressing data: {e}")
            return data
    
    def _serialize_value(self, value: Any) -> bytes:
        """
        Serialize a value for storage in Redis or Memcached.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized value as bytes
        """
        try:
            # First pickle the value
            pickled_data = pickle.dumps(value)
            
            # Then compress if enabled
            return self._compress_data(pickled_data)
        except Exception as e:
            logger.error(f"Error serializing value: {e}")
            return pickle.dumps(None)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """
        Deserialize a value from Redis or Memcached storage.
        
        Args:
            data: Serialized data
            
        Returns:
            Deserialized value
        """
        try:
            # First decompress if enabled
            decompressed_data = self._decompress_data(data)
            
            # Then unpickle
            return pickle.loads(decompressed_data)
        except Exception as e:
            logger.error(f"Error deserializing value: {e}")
            return None
            
    def _get_memcached_key(self, key: str) -> str:
        """
        Get the full Memcached key with prefix.
        
        Args:
            key: Cache key
            
        Returns:
            Full Memcached key with prefix
        """
        return f"{self.memcached_prefix}{key}"
            
    def _should_prefetch(self, key: str) -> bool:
        """
        Determine if a key should be prefetched.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key should be prefetched, False otherwise
        """
        # Check if prefetching is enabled
        if not self.prefetch_enabled:
            return False
            
        # Check if key matches any prefetch patterns
        if self.prefetch_patterns:
            if not any(pattern in key for pattern in self.prefetch_patterns):
                return False
                
        # Check access count
        access_count = self.access_counts.get(key, 0)
        if access_count < 2:  # Only prefetch keys accessed multiple times
            return False
            
        return True
    
    def _evict_if_needed(self) -> None:
        """
        Evict entries if the cache is full.
        """
        if self.max_size is None or len(self.cache) <= self.max_size:
            return
        
        # Remove expired entries first
        self._remove_expired()
        
        # If still over max size, evict based on policy
        if len(self.cache) <= self.max_size:
            return
        
        # Sort entries based on eviction policy
        if self.eviction_policy == "lru":
            # Least Recently Used
            sorted_keys = sorted(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        else:
            # First In First Out (default)
            sorted_keys = sorted(self.cache.keys(), key=lambda k: self.cache[k].created_at)
        
        # Evict entries until under max size
        entries_to_evict = len(self.cache) - self.max_size
        for key in sorted_keys[:entries_to_evict]:
            logger.debug(f"Evicting cache entry: {key}")
            del self.cache[key]
    
    def _remove_expired(self) -> None:
        """
        Remove expired entries from the cache.
        """
        expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
        for key in expired_keys:
            logger.debug(f"Removing expired cache entry: {key}")
            del self.cache[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value to return if key not found
            
        Returns:
            Cached value or default if not found
        """
        # Track access for prefetching and analytics
        current_time = time.time()
        if self.prefetch_enabled:
            with self.lock:
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
        
        # Track for adaptive TTL
        if self.adaptive_ttl:
            with self.lock:
                self.access_frequency[key] = self.access_frequency.get(key, 0) + 1
                self.last_access_time[key] = current_time
        
        # Handle Redis backend
        if self.backend == "redis" and self.redis_client:
            try:
                redis_key = self._get_redis_key(key)
                data = self.redis_client.get(redis_key)
                
                # Track analytics
                if self.analytics_enabled:
                    with self.lock:
                        if data is None:
                            self.miss_count += 1
                        else:
                            self.hit_count += 1
                            if key not in self.key_access_times:
                                self.key_access_times[key] = []
                            self.key_access_times[key].append(current_time)
                
                if data is None:
                    return default
                
                value = self._deserialize_value(data)
                
                # Check if we should queue for prefetching
                if self._should_prefetch(key):
                    self.prefetch_queue.add(key)
                
                return value
            except Exception as e:
                logger.error(f"Error getting value from Redis for key {key}: {e}")
                return default
        
        # Handle Memcached backend
        elif self.backend == "memcached" and self.memcached_client:
            try:
                memcached_key = self._get_memcached_key(key)
                data = self.memcached_client.get(memcached_key)
                
                # Track analytics
                if self.analytics_enabled:
                    with self.lock:
                        if data is None:
                            self.miss_count += 1
                        else:
                            self.hit_count += 1
                            if key not in self.key_access_times:
                                self.key_access_times[key] = []
                            self.key_access_times[key].append(current_time)
                
                if data is None:
                    return default
                
                value = self._deserialize_value(data)
                
                # Check if we should queue for prefetching
                if self._should_prefetch(key):
                    self.prefetch_queue.add(key)
                
                return value
            except Exception as e:
                logger.error(f"Error getting value from Memcached for key {key}: {e}")
                return default
        
        # Handle memory/file backend
        with self.lock:
            self._remove_expired()
            
            # Track analytics
            if self.analytics_enabled:
                if key not in self.cache or self.cache[key].is_expired():
                    self.miss_count += 1
                else:
                    self.hit_count += 1
                    if key not in self.key_access_times:
                        self.key_access_times[key] = []
                    self.key_access_times[key].append(current_time)
            
            if key not in self.cache:
                return default
            
            entry = self.cache[key]
            if entry.is_expired():
                if self.analytics_enabled:
                    self.expiration_count += 1
                del self.cache[key]
                return default
            
            entry.access()
            
            # Check if we should queue for prefetching
            if self._should_prefetch(key):
                # Check if entry is approaching expiration
                if entry.expires_at is not None:
                    time_remaining = entry.expires_at - time.time()
                    total_ttl = entry.expires_at - entry.created_at
                    if time_remaining / total_ttl < self.prefetch_threshold:
                        self.prefetch_queue.add(key)
            
            return entry.value
    
    def _calculate_adaptive_ttl(self, key: str, base_ttl: Optional[int]) -> Optional[int]:
        """
        Calculate an adaptive TTL based on access patterns.
        
        Args:
            key: Cache key
            base_ttl: Base TTL in seconds
            
        Returns:
            Adjusted TTL in seconds, or None if base_ttl is None
        """
        if not self.adaptive_ttl or base_ttl is None:
            return base_ttl
            
        # Get access frequency and time since last access
        frequency = self.access_frequency.get(key, 0)
        last_access = self.last_access_time.get(key, 0)
        time_since_last_access = time.time() - last_access
        
        # Calculate adjustment factor based on frequency and recency
        # Higher frequency and more recent access = longer TTL
        frequency_factor = min(frequency / 10.0, 1.0)  # Cap at 1.0
        recency_factor = max(1.0 - (time_since_last_access / (24 * 60 * 60)), 0.0)  # Use 24 hours as baseline
        
        # Combine factors (weight frequency more than recency)
        adjustment_factor = (0.7 * frequency_factor) + (0.3 * recency_factor)
        
        # Scale between min and max TTL factors
        ttl_factor = self.min_ttl_factor + (adjustment_factor * (self.max_ttl_factor - self.min_ttl_factor))
        
        # Apply the factor to the base TTL
        adjusted_ttl = int(base_ttl * ttl_factor)
        
        # Store the adjustment for analytics
        self.ttl_adjustments[key] = ttl_factor
        
        logger.debug(f"Adaptive TTL for {key}: {base_ttl} -> {adjusted_ttl} (factor: {ttl_factor:.2f})")
        
        return adjusted_ttl
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None to use default_ttl)
            metadata: Additional metadata for the entry
        """
        # Track analytics
        if self.analytics_enabled:
            with self.lock:
                self.set_count += 1
                # Track size of the value for analytics
                try:
                    serialized = self._serialize_value(value)
                    self.key_size_stats[key] = len(serialized)
                except Exception:
                    pass
        
        # Calculate adaptive TTL if enabled
        if self.adaptive_ttl:
            ttl = self._calculate_adaptive_ttl(key, ttl if ttl is not None else self.default_ttl)
        
        # Handle Redis backend
        if self.backend == "redis" and self.redis_client:
            try:
                redis_key = self._get_redis_key(key)
                serialized_value = self._serialize_value(value)
                
                # Set with expiration if TTL is provided
                if ttl is not None or self.default_ttl is not None:
                    ttl_seconds = ttl if ttl is not None else self.default_ttl
                    self.redis_client.setex(redis_key, ttl_seconds, serialized_value)
                else:
                    self.redis_client.set(redis_key, serialized_value)
                
                # Store metadata if provided
                if metadata:
                    metadata_key = f"{redis_key}:metadata"
                    self.redis_client.set(metadata_key, self._serialize_value(metadata))
                
                return
            except Exception as e:
                logger.error(f"Error setting value in Redis for key {key}: {e}")
                # Fall back to memory cache if Redis fails
        
        # Handle Memcached backend
        elif self.backend == "memcached" and self.memcached_client:
            try:
                memcached_key = self._get_memcached_key(key)
                serialized_value = self._serialize_value(value)
                
                # Set with expiration if TTL is provided
                if ttl is not None or self.default_ttl is not None:
                    ttl_seconds = ttl if ttl is not None else self.default_ttl
                    self.memcached_client.set(memcached_key, serialized_value, expire=ttl_seconds)
                else:
                    self.memcached_client.set(memcached_key, serialized_value)
                
                # Store metadata if provided (Memcached doesn't support metadata directly, so we use a separate key)
                if metadata:
                    metadata_key = f"{memcached_key}:metadata"
                    self.memcached_client.set(metadata_key, self._serialize_value(metadata))
                
                return
            except Exception as e:
                logger.error(f"Error setting value in Memcached for key {key}: {e}")
                # Fall back to memory cache if Memcached fails
        
        # Handle memory/file backend
        with self.lock:
            expires_at = self._get_expiration_time(ttl)
            self.cache[key] = CacheEntry(value, expires_at, metadata)
            self._evict_if_needed()
            
            # Save to file if using file backend
            if self.backend == "file" and self.file_path:
                self.save()
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        # Track analytics
        if self.analytics_enabled:
            with self.lock:
                self.delete_count += 1
        
        # Handle Redis backend
        if self.backend == "redis" and self.redis_client:
            try:
                redis_key = self._get_redis_key(key)
                result = self.redis_client.delete(redis_key)
                
                # Also delete metadata if it exists
                metadata_key = f"{redis_key}:metadata"
                self.redis_client.delete(metadata_key)
                
                # Clean up analytics and adaptive TTL data
                if self.analytics_enabled:
                    with self.lock:
                        if key in self.key_access_times:
                            del self.key_access_times[key]
                        if key in self.key_size_stats:
                            del self.key_size_stats[key]
                
                if self.adaptive_ttl:
                    with self.lock:
                        if key in self.access_frequency:
                            del self.access_frequency[key]
                        if key in self.last_access_time:
                            del self.last_access_time[key]
                        if key in self.ttl_adjustments:
                            del self.ttl_adjustments[key]
                
                return result > 0
            except Exception as e:
                logger.error(f"Error deleting value from Redis for key {key}: {e}")
                # Fall back to memory cache if Redis fails
        
        # Handle Memcached backend
        elif self.backend == "memcached" and self.memcached_client:
            try:
                memcached_key = self._get_memcached_key(key)
                result = self.memcached_client.delete(memcached_key)
                
                # Also delete metadata if it exists
                metadata_key = f"{memcached_key}:metadata"
                self.memcached_client.delete(metadata_key)
                
                # Clean up analytics and adaptive TTL data
                if self.analytics_enabled:
                    with self.lock:
                        if key in self.key_access_times:
                            del self.key_access_times[key]
                        if key in self.key_size_stats:
                            del self.key_size_stats[key]
                
                if self.adaptive_ttl:
                    with self.lock:
                        if key in self.access_frequency:
                            del self.access_frequency[key]
                        if key in self.last_access_time:
                            del self.last_access_time[key]
                        if key in self.ttl_adjustments:
                            del self.ttl_adjustments[key]
                
                return result
            except Exception as e:
                logger.error(f"Error deleting value from Memcached for key {key}: {e}")
                # Fall back to memory cache if Memcached fails
        
        # Handle memory/file backend
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                
                # Clean up analytics and adaptive TTL data
                if self.analytics_enabled:
                    if key in self.key_access_times:
                        del self.key_access_times[key]
                    if key in self.key_size_stats:
                        del self.key_size_stats[key]
                
                if self.adaptive_ttl:
                    if key in self.access_frequency:
                        del self.access_frequency[key]
                    if key in self.last_access_time:
                        del self.last_access_time[key]
                    if key in self.ttl_adjustments:
                        del self.ttl_adjustments[key]
                
                # Save to file if using file backend
                if self.backend == "file" and self.file_path:
                    self.save()
                
                return True
            return False
    
    def clear(self) -> None:
        """
        Clear all entries from the cache.
        """
        # Handle Redis backend
        if self.backend == "redis" and self.redis_client:
            try:
                # Delete all keys with the cache prefix
                pattern = f"{self.redis_prefix}*"
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor, pattern, 100)
                    if keys:
                        self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
                
                # Track analytics
                if self.analytics_enabled:
                    with self.lock:
                        self.key_access_times.clear()
                        self.key_size_stats.clear()
                
                # Clear adaptive TTL data
                if self.adaptive_ttl:
                    with self.lock:
                        self.access_frequency.clear()
                        self.last_access_time.clear()
                        self.ttl_adjustments.clear()
                
                return
            except Exception as e:
                logger.error(f"Error clearing Redis cache: {e}")
                # Fall back to memory cache if Redis fails
        
        # Handle Memcached backend
        elif self.backend == "memcached" and self.memcached_client:
            try:
                # Memcached doesn't have a way to clear all keys with a prefix
                # We would need to track keys separately or use a different approach
                # For now, we'll just flush all keys (this will affect all applications using the same Memcached instance)
                self.memcached_client.flush_all()
                
                # Track analytics
                if self.analytics_enabled:
                    with self.lock:
                        self.key_access_times.clear()
                        self.key_size_stats.clear()
                
                # Clear adaptive TTL data
                if self.adaptive_ttl:
                    with self.lock:
                        self.access_frequency.clear()
                        self.last_access_time.clear()
                        self.ttl_adjustments.clear()
                
                return
            except Exception as e:
                logger.error(f"Error clearing Memcached cache: {e}")
                # Fall back to memory cache if Memcached fails
        
        # Handle memory/file backend
        with self.lock:
            self.cache.clear()
            
            # Clear analytics data
            if self.analytics_enabled:
                self.key_access_times.clear()
                self.key_size_stats.clear()
            
            # Clear adaptive TTL data
            if self.adaptive_ttl:
                self.access_frequency.clear()
                self.last_access_time.clear()
                self.ttl_adjustments.clear()
            
            # Save to file if using file backend
            if self.backend == "file" and self.file_path:
                self.save()
                
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match against cache keys
            
        Returns:
            Number of entries invalidated
        """
        count = 0
        
        # Handle Redis backend
        if self.backend == "redis" and self.redis_client:
            try:
                # Find keys matching the pattern
                full_pattern = f"{self.redis_prefix}*{pattern}*"
                cursor = 0
                keys_to_delete = []
                
                while True:
                    cursor, keys = self.redis_client.scan(cursor, full_pattern, 100)
                    keys_to_delete.extend(keys)
                    if cursor == 0:
                        break
                
                # Delete the keys
                if keys_to_delete:
                    count = self.redis_client.delete(*keys_to_delete)
                
                return count
            except Exception as e:
                logger.error(f"Error invalidating Redis cache by pattern {pattern}: {e}")
                # Fall back to memory cache if Redis fails
        
        # Handle memory/file backend
        with self.lock:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
                count += 1
            
            # Save to file if using file backend
            if count > 0 and self.backend == "file" and self.file_path:
                self.save()
            
            return count
    
    def register_prefetch_callback(self, key: str, callback: Callable[[], Any]) -> None:
        """
        Register a callback function for prefetching a key.
        
        Args:
            key: Cache key
            callback: Function to call to get the value for prefetching
        """
        if not self.prefetch_enabled:
            return
            
        with self.lock:
            self._prefetch_callbacks[key] = callback
    
    def get_or_set(
        self, 
        key: str, 
        default_factory: Callable[[], T],
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Get a value from the cache, or set it if not found.
        
        Args:
            key: Cache key
            default_factory: Function to call to get the default value
            ttl: Time-to-live in seconds (None to use default_ttl)
            metadata: Additional metadata for the entry
            
        Returns:
            Cached value or newly computed value
        """
        # Handle Redis backend with atomic operation if possible
        if self.backend == "redis" and self.redis_client:
            try:
                redis_key = self._get_redis_key(key)
                data = self.redis_client.get(redis_key)
                
                if data is not None:
                    value = self._deserialize_value(data)
                    
                    # Check if we should queue for prefetching
                    if self.prefetch_enabled and self._should_prefetch(key):
                        # Register the default_factory as a prefetch callback
                        self.register_prefetch_callback(key, default_factory)
                        self.prefetch_queue.add(key)
                    
                    return value
                
                # Key not found, compute value
                value = default_factory()
                
                # Set in Redis
                serialized_value = self._serialize_value(value)
                if ttl is not None or self.default_ttl is not None:
                    ttl_seconds = ttl if ttl is not None else self.default_ttl
                    self.redis_client.setex(redis_key, ttl_seconds, serialized_value)
                else:
                    self.redis_client.set(redis_key, serialized_value)
                
                # Store metadata if provided
                if metadata:
                    metadata_key = f"{redis_key}:metadata"
                    self.redis_client.set(metadata_key, self._serialize_value(metadata))
                
                # Register the default_factory as a prefetch callback
                if self.prefetch_enabled:
                    self.register_prefetch_callback(key, default_factory)
                
                return value
            except Exception as e:
                logger.error(f"Error in get_or_set for Redis key {key}: {e}")
                # Fall back to memory cache if Redis fails
        
        # Handle memory/file backend
        with self.lock:
            value = self.get(key)
            if value is None:
                value = default_factory()
                self.set(key, value, ttl, metadata)
                
                # Register the default_factory as a prefetch callback
                if self.prefetch_enabled:
                    self.register_prefetch_callback(key, default_factory)
            
            return value
    
    def save(self) -> None:
        """
        Save the cache to a file (for "file" backend).
        """
        if self.backend != "file" or not self.file_path:
            return
        
        with self.lock:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
                
                # Convert cache to serializable format
                cache_data = {k: v.to_dict() for k, v in self.cache.items()}
                
                # Add prefetch callbacks and access counts
                if self.prefetch_enabled:
                    cache_data["__prefetch_metadata__"] = {
                        "access_counts": self.access_counts,
                        "prefetch_patterns": self.prefetch_patterns,
                        "prefetch_threshold": self.prefetch_threshold
                    }
                
                # Write to file
                with open(self.file_path, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                
                logger.debug(f"Cache saved to {self.file_path}")
            except Exception as e:
                logger.error(f"Error saving cache to {self.file_path}: {e}")
    
    def load(self) -> None:
        """
        Load the cache from a file (for "file" backend).
        """
        if self.backend != "file" or not self.file_path or not os.path.exists(self.file_path):
            return
        
        with self.lock:
            try:
                # Read from file
                with open(self.file_path, 'r') as f:
                    cache_data = json.load(f)
                
                # Extract prefetch metadata if present
                if "__prefetch_metadata__" in cache_data:
                    prefetch_metadata = cache_data.pop("__prefetch_metadata__")
                    if self.prefetch_enabled:
                        self.access_counts = prefetch_metadata.get("access_counts", {})
                        if not self.prefetch_patterns:  # Only use if not explicitly set
                            self.prefetch_patterns = prefetch_metadata.get("prefetch_patterns", [])
                        if self.prefetch_threshold == 0.8:  # Only use if not explicitly set
                            self.prefetch_threshold = prefetch_metadata.get("prefetch_threshold", 0.8)
                
                # Convert to cache entries
                self.cache = {k: CacheEntry.from_dict(v) for k, v in cache_data.items()}
                
                # Remove expired entries
                self._remove_expired()
                
                logger.debug(f"Cache loaded from {self.file_path}")
            except Exception as e:
                logger.error(f"Error loading cache from {self.file_path}: {e}")
                self.cache = {}
                
    def invalidate_all(self) -> None:
        """
        Invalidate all cache entries (clear the cache).
        
        This is an alias for clear() for consistency with other invalidation methods.
        """
        self.clear()
    
    def invalidate_by_prefix(self, prefix: str) -> int:
        """
        Invalidate cache entries with a specific prefix.
        
        Args:
            prefix: Prefix to match against cache keys
            
        Returns:
            Number of entries invalidated
        """
        count = 0
        
        # Handle Redis backend
        if self.backend == "redis" and self.redis_client:
            try:
                # Find keys with the prefix
                full_prefix = f"{self.redis_prefix}{prefix}"
                cursor = 0
                keys_to_delete = []
                
                while True:
                    cursor, keys = self.redis_client.scan(cursor, f"{full_prefix}*", 100)
                    keys_to_delete.extend(keys)
                    if cursor == 0:
                        break
                
                # Delete the keys
                if keys_to_delete:
                    count = self.redis_client.delete(*keys_to_delete)
                
                return count
            except Exception as e:
                logger.error(f"Error invalidating Redis cache by prefix {prefix}: {e}")
                # Fall back to memory cache if Redis fails
        
        # Handle memory/file backend
        with self.lock:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.cache[key]
                count += 1
            
            # Save to file if using file backend
            if count > 0 and self.backend == "file" and self.file_path:
                self.save()
            
            return count
    
    def add_to_prefetch_patterns(self, pattern: str) -> None:
        """
        Add a pattern to the list of prefetch patterns.
        
        Args:
            pattern: Pattern to add
        """
        if not self.prefetch_enabled:
            return
            
        with self.lock:
            if pattern not in self.prefetch_patterns:
                self.prefetch_patterns.append(pattern)
                
    def remove_from_prefetch_patterns(self, pattern: str) -> None:
        """
        Remove a pattern from the list of prefetch patterns.
        
        Args:
            pattern: Pattern to remove
        """
        if not self.prefetch_enabled:
            return
            
        with self.lock:
            if pattern in self.prefetch_patterns:
                self.prefetch_patterns.remove(pattern)
    
    def keys(self) -> List[str]:
        """
        Get all keys in the cache.
        
        Returns:
            List of cache keys
        """
        with self.lock:
            self._remove_expired()
            return list(self.cache.keys())
    
    def values(self) -> List[Any]:
        """
        Get all values in the cache.
        
        Returns:
            List of cache values
        """
        with self.lock:
            self._remove_expired()
            return [entry.value for entry in self.cache.values()]
    
    def items(self) -> List[tuple]:
        """
        Get all key-value pairs in the cache.
        
        Returns:
            List of (key, value) tuples
        """
        with self.lock:
            self._remove_expired()
            return [(k, v.value) for k, v in self.cache.items()]
    
    def __len__(self) -> int:
        """
        Get the number of entries in the cache.
        
        Returns:
            Number of cache entries
        """
        with self.lock:
            self._remove_expired()
            return len(self.cache)
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a key is in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key is in the cache, False otherwise
        """
        with self.lock:
            self._remove_expired()
            return key in self.cache
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value
            
        Raises:
            KeyError: If the key is not found
        """
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.set(key, value)
    
    def __delitem__(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Raises:
            KeyError: If the key is not found
        """
        if not self.delete(key):
            raise KeyError(key)
            
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get detailed analytics about cache performance.
        
        Returns:
            Dictionary with cache analytics data
        """
        if not self.analytics_enabled:
            return {"analytics_enabled": False}
        
        with self.lock:
            # Calculate hit rate
            total_requests = self.hit_count + self.miss_count
            hit_rate = (self.hit_count / total_requests) * 100 if total_requests > 0 else 0
            
            # Calculate average item size
            total_size = sum(self.key_size_stats.values())
            avg_size = total_size / len(self.key_size_stats) if self.key_size_stats else 0
            
            # Calculate access frequency for each key
            access_frequency = {}
            for key, times in self.key_access_times.items():
                access_frequency[key] = len(times)
            
            # Calculate most and least accessed keys
            most_accessed = sorted(access_frequency.items(), key=lambda x: x[1], reverse=True)[:10] if access_frequency else []
            least_accessed = sorted(access_frequency.items(), key=lambda x: x[1])[:10] if access_frequency else []
            
            # Calculate largest items
            largest_items = sorted(self.key_size_stats.items(), key=lambda x: x[1], reverse=True)[:10] if self.key_size_stats else []
            
            # Calculate adaptive TTL stats if enabled
            adaptive_ttl_stats = {}
            if self.adaptive_ttl:
                adaptive_ttl_stats = {
                    "enabled": True,
                    "average_adjustment_factor": sum(self.ttl_adjustments.values()) / len(self.ttl_adjustments) if self.ttl_adjustments else 0,
                    "min_adjustment_factor": min(self.ttl_adjustments.values()) if self.ttl_adjustments else 0,
                    "max_adjustment_factor": max(self.ttl_adjustments.values()) if self.ttl_adjustments else 0,
                    "adjustment_factors": dict(sorted(self.ttl_adjustments.items(), key=lambda x: x[1], reverse=True)[:10]) if self.ttl_adjustments else {}
                }
            else:
                adaptive_ttl_stats = {"enabled": False}
            
            # Calculate compression stats if enabled
            compression_stats = {}
            if self.compression:
                # Calculate average compression ratio
                original_sizes = []
                compressed_sizes = []
                for key, value in self.cache.items():
                    try:
                        # Get original size by serializing without compression
                        original_data = pickle.dumps(value.value)
                        original_sizes.append(len(original_data))
                        
                        # Get compressed size
                        compressed_data = self._serialize_value(value.value)
                        compressed_sizes.append(len(compressed_data))
                    except Exception:
                        pass
                
                avg_compression_ratio = 0
                if original_sizes and compressed_sizes:
                    total_original = sum(original_sizes)
                    total_compressed = sum(compressed_sizes)
                    avg_compression_ratio = (total_compressed / total_original) if total_original > 0 else 0
                
                compression_stats = {
                    "enabled": True,
                    "compression_level": self.compression_level,
                    "average_compression_ratio": avg_compression_ratio,
                    "total_original_size": sum(original_sizes) if original_sizes else 0,
                    "total_compressed_size": sum(compressed_sizes) if compressed_sizes else 0,
                    "space_saved": sum(original_sizes) - sum(compressed_sizes) if original_sizes and compressed_sizes else 0
                }
            else:
                compression_stats = {"enabled": False}
            
            # Calculate uptime and operations per second
            uptime = time.time() - self.analytics_start_time
            ops_per_second = (self.hit_count + self.miss_count + self.set_count + self.delete_count) / uptime if uptime > 0 else 0
            
            return {
                "analytics_enabled": True,
                "backend": self.backend,
                "hit_count": self.hit_count,
                "miss_count": self.miss_count,
                "set_count": self.set_count,
                "delete_count": self.delete_count,
                "eviction_count": self.eviction_count,
                "expiration_count": self.expiration_count,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "total_operations": self.hit_count + self.miss_count + self.set_count + self.delete_count,
                "operations_per_second": ops_per_second,
                "uptime_seconds": uptime,
                "current_size": len(self.cache) if self.backend in ["memory", "file"] else None,
                "max_size": self.max_size,
                "eviction_policy": self.eviction_policy,
                "total_size_bytes": total_size,
                "average_item_size_bytes": avg_size,
                "most_accessed_keys": most_accessed,
                "least_accessed_keys": least_accessed,
                "largest_items": largest_items,
                "adaptive_ttl": adaptive_ttl_stats,
                "compression": compression_stats,
                "timestamp": time.time()
            }


# Create a default cache instance
default_cache = Cache()