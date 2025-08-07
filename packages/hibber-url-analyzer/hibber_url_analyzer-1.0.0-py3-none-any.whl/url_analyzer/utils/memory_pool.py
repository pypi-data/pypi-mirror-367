"""
Memory Pool Module

This module provides memory pooling functionality to reduce memory usage
by reusing objects instead of creating new ones. This is particularly useful
for repetitive objects like strings, patterns, and other objects that are
created frequently.
"""

import re
import weakref
import time
import collections
from typing import Dict, Any, TypeVar, Generic, Optional, Set, List, Tuple, Pattern, Deque, OrderedDict
from functools import lru_cache

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Type variable for the pool
T = TypeVar('T')

class ObjectPool(Generic[T]):
    """
    A generic object pool that stores and reuses objects.
    
    This pool helps reduce memory usage by reusing objects instead of creating
    new ones. It's particularly useful for objects that are expensive to create
    or that are created frequently.
    
    The pool uses an LRU (Least Recently Used) eviction policy to maintain
    the most frequently used objects in the pool.
    """
    
    def __init__(self, factory=None, max_size: int = 1000, eviction_policy: str = 'lru'):
        """
        Initialize the object pool.
        
        Args:
            factory: Function to create new objects if not found in the pool
            max_size: Maximum number of objects to keep in the pool
            eviction_policy: Policy to use when evicting objects ('lru', 'lfu', or 'random')
        """
        self._factory = factory
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._eviction_policy = eviction_policy.lower()
        
        # Use OrderedDict for LRU policy (most recently used items at the end)
        if self._eviction_policy == 'lru':
            self._pool: OrderedDict[Any, T] = collections.OrderedDict()
        # Use a dict with access counts for LFU policy
        elif self._eviction_policy == 'lfu':
            self._pool: Dict[Any, T] = {}
            self._access_counts: Dict[Any, int] = {}
        # Use a regular dict for random policy
        else:  # 'random'
            self._pool: Dict[Any, T] = {}
        
        logger.debug(f"Created ObjectPool with {eviction_policy} eviction policy and max size {max_size}")
        
    def get(self, key: Any) -> T:
        """
        Get an object from the pool, or create a new one if not found.
        
        Args:
            key: Key to identify the object
            
        Returns:
            The object from the pool or a new one
        """
        # Check if the object is in the pool
        if key in self._pool:
            self._hits += 1
            
            # Update access information based on eviction policy
            if self._eviction_policy == 'lru':
                # Move the item to the end of the OrderedDict (most recently used)
                self._pool.move_to_end(key)
            elif self._eviction_policy == 'lfu':
                # Increment the access count for this key
                self._access_counts[key] += 1
            
            return self._pool[key]
        
        self._misses += 1
        
        # Create a new object if not found
        if self._factory:
            obj = self._factory(key)
        else:
            obj = key  # Use the key as the object if no factory is provided
            
        # Add to pool if not full
        if len(self._pool) < self._max_size:
            self._add_to_pool(key, obj)
        else:
            # If pool is full, evict an item based on the policy
            self._evict_and_add(key, obj)
                
        return obj
        
    def _add_to_pool(self, key: Any, obj: T) -> None:
        """
        Add an object to the pool with appropriate tracking based on eviction policy.
        
        Args:
            key: Key to identify the object
            obj: Object to add to the pool
        """
        if self._eviction_policy == 'lfu':
            self._pool[key] = obj
            self._access_counts[key] = 1
        else:  # 'lru' or 'random'
            self._pool[key] = obj
    
    def _evict_and_add(self, key: Any, obj: T) -> None:
        """
        Evict an item from the pool based on the eviction policy and add a new one.
        
        Args:
            key: Key to identify the new object
            obj: New object to add to the pool
        """
        if not self._pool:
            # If pool is empty (unlikely but possible), just add the new item
            self._add_to_pool(key, obj)
            return
            
        if self._eviction_policy == 'lru':
            # Remove the first item (least recently used)
            self._pool.popitem(last=False)
            # Add the new item (will be at the end - most recently used)
            self._pool[key] = obj
            
        elif self._eviction_policy == 'lfu':
            # Find the key with the lowest access count
            min_key = min(self._access_counts.items(), key=lambda x: x[1])[0]
            # Remove it from both dictionaries
            del self._pool[min_key]
            del self._access_counts[min_key]
            # Add the new item
            self._pool[key] = obj
            self._access_counts[key] = 1
            
        else:  # 'random'
            # Remove a random item
            random_key = next(iter(self._pool))
            del self._pool[random_key]
            # Add the new item
            self._pool[key] = obj
    
    def clear(self) -> None:
        """Clear the pool."""
        self._pool.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pool.
        
        Returns:
            Dictionary with pool statistics
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total) * 100 if total > 0 else 0
        
        return {
            "size": len(self._pool),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }
        
    def __len__(self) -> int:
        """Get the number of objects in the pool."""
        return len(self._pool)


# String interning pool
class StringPool:
    """
    A pool for interning strings to reduce memory usage.
    
    This pool helps reduce memory usage by reusing string objects instead of
    creating new ones. It's particularly useful for strings that are repeated
    frequently, such as domain names, categories, etc.
    
    The pool uses an LRU (Least Recently Used) eviction policy by default to maintain
    the most frequently used strings in the pool.
    """
    
    def __init__(self, max_size: int = 10000, eviction_policy: str = 'lru'):
        """
        Initialize the string pool.
        
        Args:
            max_size: Maximum number of strings to keep in the pool
            eviction_policy: Policy to use when evicting strings ('lru', 'lfu', or 'random')
        """
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._eviction_policy = eviction_policy.lower()
        
        # Use OrderedDict for LRU policy (most recently used items at the end)
        if self._eviction_policy == 'lru':
            self._pool: OrderedDict[str, str] = collections.OrderedDict()
        # Use a dict with access counts for LFU policy
        elif self._eviction_policy == 'lfu':
            self._pool: Dict[str, str] = {}
            self._access_counts: Dict[str, int] = {}
        # Use a regular dict for random policy
        else:  # 'random'
            self._pool: Dict[str, str] = {}
        
        logger.debug(f"Created StringPool with {eviction_policy} eviction policy and max size {max_size}")
        
    def intern(self, string: str) -> str:
        """
        Intern a string, returning a reference to a pooled string if available.
        
        Args:
            string: String to intern
            
        Returns:
            Interned string from the pool
        """
        # Check if the string is in the pool
        if string in self._pool:
            self._hits += 1
            
            # Update access information based on eviction policy
            if self._eviction_policy == 'lru':
                # Move the item to the end of the OrderedDict (most recently used)
                self._pool.move_to_end(string)
            elif self._eviction_policy == 'lfu':
                # Increment the access count for this string
                self._access_counts[string] += 1
            
            return self._pool[string]
        
        self._misses += 1
        
        # Add to pool if not full
        if len(self._pool) < self._max_size:
            self._add_to_pool(string)
        else:
            # If pool is full, evict an item based on the policy
            self._evict_and_add(string)
                
        return string
        
    def _add_to_pool(self, string: str) -> None:
        """
        Add a string to the pool with appropriate tracking based on eviction policy.
        
        Args:
            string: String to add to the pool
        """
        if self._eviction_policy == 'lfu':
            self._pool[string] = string
            self._access_counts[string] = 1
        else:  # 'lru' or 'random'
            self._pool[string] = string
    
    def _evict_and_add(self, string: str) -> None:
        """
        Evict a string from the pool based on the eviction policy and add a new one.
        
        Args:
            string: New string to add to the pool
        """
        if not self._pool:
            # If pool is empty (unlikely but possible), just add the new item
            self._add_to_pool(string)
            return
            
        if self._eviction_policy == 'lru':
            # Remove the first item (least recently used)
            self._pool.popitem(last=False)
            # Add the new item (will be at the end - most recently used)
            self._pool[string] = string
            
        elif self._eviction_policy == 'lfu':
            # Find the key with the lowest access count
            min_key = min(self._access_counts.items(), key=lambda x: x[1])[0]
            # Remove it from both dictionaries
            del self._pool[min_key]
            del self._access_counts[min_key]
            # Add the new item
            self._pool[string] = string
            self._access_counts[string] = 1
            
        else:  # 'random'
            # Remove a random item
            random_key = next(iter(self._pool))
            del self._pool[random_key]
            # Add the new item
            self._pool[string] = string
    
    def clear(self) -> None:
        """Clear the pool."""
        self._pool.clear()
        if self._eviction_policy == 'lfu':
            self._access_counts.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pool.
        
        Returns:
            Dictionary with pool statistics
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total) * 100 if total > 0 else 0
        
        stats = {
            "size": len(self._pool),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "eviction_policy": self._eviction_policy
        }
        
        # Add policy-specific stats
        if self._eviction_policy == 'lfu':
            # Add some LFU-specific stats if there are items in the pool
            if self._access_counts:
                stats["min_access_count"] = min(self._access_counts.values())
                stats["max_access_count"] = max(self._access_counts.values())
                stats["avg_access_count"] = sum(self._access_counts.values()) / len(self._access_counts)
        
        return stats
        
    def __len__(self) -> int:
        """Get the number of strings in the pool."""
        return len(self._pool)


# Regular expression pattern pool
class PatternPool:
    """
    A pool for regular expression patterns to reduce memory usage.
    
    This pool helps reduce memory usage by reusing compiled regular expression
    patterns instead of compiling them repeatedly. It's particularly useful for
    patterns that are used frequently, such as URL patterns, domain patterns, etc.
    
    The pool uses an LRU (Least Recently Used) eviction policy by default to maintain
    the most frequently used patterns in the pool.
    """
    
    def __init__(self, max_size: int = 1000, eviction_policy: str = 'lru'):
        """
        Initialize the pattern pool.
        
        Args:
            max_size: Maximum number of patterns to keep in the pool
            eviction_policy: Policy to use when evicting patterns ('lru', 'lfu', or 'random')
        """
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._eviction_policy = eviction_policy.lower()
        
        # Use OrderedDict for LRU policy (most recently used items at the end)
        if self._eviction_policy == 'lru':
            self._pool: OrderedDict[Tuple[str, int], Pattern] = collections.OrderedDict()
        # Use a dict with access counts for LFU policy
        elif self._eviction_policy == 'lfu':
            self._pool: Dict[Tuple[str, int], Pattern] = {}
            self._access_counts: Dict[Tuple[str, int], int] = {}
        # Use a regular dict for random policy
        else:  # 'random'
            self._pool: Dict[Tuple[str, int], Pattern] = {}
        
        logger.debug(f"Created PatternPool with {eviction_policy} eviction policy and max size {max_size}")
        
    def get_pattern(self, pattern: str, flags: int = 0) -> Pattern:
        """
        Get a compiled pattern from the pool, or compile a new one if not found.
        
        Args:
            pattern: Regular expression pattern string
            flags: Regular expression flags
            
        Returns:
            Compiled regular expression pattern
        """
        key = (pattern, flags)
        
        # Check if the pattern is in the pool
        if key in self._pool:
            self._hits += 1
            
            # Update access information based on eviction policy
            if self._eviction_policy == 'lru':
                # Move the item to the end of the OrderedDict (most recently used)
                self._pool.move_to_end(key)
            elif self._eviction_policy == 'lfu':
                # Increment the access count for this pattern
                self._access_counts[key] += 1
            
            return self._pool[key]
        
        self._misses += 1
        
        # Compile the pattern
        compiled_pattern = re.compile(pattern, flags)
        
        # Add to pool if not full
        if len(self._pool) < self._max_size:
            self._add_to_pool(key, compiled_pattern)
        else:
            # If pool is full, evict an item based on the policy
            self._evict_and_add(key, compiled_pattern)
                
        return compiled_pattern
        
    def _add_to_pool(self, key: Tuple[str, int], pattern: Pattern) -> None:
        """
        Add a pattern to the pool with appropriate tracking based on eviction policy.
        
        Args:
            key: Key to identify the pattern (pattern string, flags)
            pattern: Compiled regular expression pattern
        """
        if self._eviction_policy == 'lfu':
            self._pool[key] = pattern
            self._access_counts[key] = 1
        else:  # 'lru' or 'random'
            self._pool[key] = pattern
    
    def _evict_and_add(self, key: Tuple[str, int], pattern: Pattern) -> None:
        """
        Evict a pattern from the pool based on the eviction policy and add a new one.
        
        Args:
            key: Key to identify the new pattern (pattern string, flags)
            pattern: New compiled regular expression pattern
        """
        if not self._pool:
            # If pool is empty (unlikely but possible), just add the new item
            self._add_to_pool(key, pattern)
            return
            
        if self._eviction_policy == 'lru':
            # Remove the first item (least recently used)
            self._pool.popitem(last=False)
            # Add the new item (will be at the end - most recently used)
            self._pool[key] = pattern
            
        elif self._eviction_policy == 'lfu':
            # Find the key with the lowest access count
            min_key = min(self._access_counts.items(), key=lambda x: x[1])[0]
            # Remove it from both dictionaries
            del self._pool[min_key]
            del self._access_counts[min_key]
            # Add the new item
            self._pool[key] = pattern
            self._access_counts[key] = 1
            
        else:  # 'random'
            # Remove a random item
            random_key = next(iter(self._pool))
            del self._pool[random_key]
            # Add the new item
            self._pool[key] = pattern
    
    def clear(self) -> None:
        """Clear the pool."""
        self._pool.clear()
        if self._eviction_policy == 'lfu':
            self._access_counts.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pool.
        
        Returns:
            Dictionary with pool statistics
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total) * 100 if total > 0 else 0
        
        stats = {
            "size": len(self._pool),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "eviction_policy": self._eviction_policy
        }
        
        # Add policy-specific stats
        if self._eviction_policy == 'lfu':
            # Add some LFU-specific stats if there are items in the pool
            if self._access_counts:
                stats["min_access_count"] = min(self._access_counts.values())
                stats["max_access_count"] = max(self._access_counts.values())
                stats["avg_access_count"] = sum(self._access_counts.values()) / len(self._access_counts)
        
        return stats
        
    def __len__(self) -> int:
        """Get the number of patterns in the pool."""
        return len(self._pool)


# Create default pools with LRU (Least Recently Used) eviction policy
# LRU is a good default choice as it balances memory efficiency with performance
# by keeping the most recently used items in the pool
string_pool = StringPool(max_size=10000, eviction_policy='lru')
pattern_pool = PatternPool(max_size=1000, eviction_policy='lru')

# Decorator for memory-efficient functions
def memory_efficient(max_size: int = 128):
    """
    Decorator to make a function memory-efficient by caching its results.
    
    This is similar to lru_cache but with more control over the cache size
    and with memory usage in mind.
    
    Args:
        max_size: Maximum number of results to cache
        
    Returns:
        Decorated function
    """
    def decorator(func):
        # Use lru_cache with the specified max_size
        cached_func = lru_cache(maxsize=max_size)(func)
        
        # Add stats attribute to the function
        cached_func.get_stats = lambda: {
            "cache_info": cached_func.cache_info(),
            "max_size": max_size
        }
        
        return cached_func
    
    return decorator


# Function to get memory usage
def get_memory_usage() -> float:
    """
    Get the current memory usage of the process in MB.
    
    Returns:
        Memory usage in MB
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # Convert to MB
    except ImportError:
        logger.warning("psutil not available, cannot get memory usage")
        return 0.0


# Memory usage tracking context manager
class MemoryTracker:
    """
    Context manager for tracking memory usage.
    
    This context manager tracks memory usage before and after a block of code,
    and logs the difference.
    """
    
    def __init__(self, label: str = "Memory usage"):
        """
        Initialize the memory tracker.
        
        Args:
            label: Label for the memory usage log
        """
        self.label = label
        self.start_memory = 0.0
        self.end_memory = 0.0
        
    def __enter__(self):
        """Enter the context manager."""
        self.start_memory = get_memory_usage()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        self.end_memory = get_memory_usage()
        memory_diff = self.end_memory - self.start_memory
        logger.debug(f"{self.label}: {memory_diff:.2f} MB ({self.start_memory:.2f} MB -> {self.end_memory:.2f} MB)")
        
    def get_usage(self) -> Dict[str, float]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary with memory usage statistics
        """
        return {
            "start_memory_mb": self.start_memory,
            "end_memory_mb": self.end_memory,
            "memory_diff_mb": self.end_memory - self.start_memory
        }