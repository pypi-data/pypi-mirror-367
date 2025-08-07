"""
Data Structures Module

This module provides memory-efficient data structures and utilities for
optimizing data structures for memory efficiency.
"""

import sys
import array
import collections
from typing import Dict, List, Any, Optional, Set, Tuple, TypeVar, Generic, Iterable, Iterator

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Import memory pooling
from url_analyzer.utils.memory_pool import string_pool

# Type variable for generic types
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class MemoryEfficientList(Generic[T]):
    """
    Memory-efficient list implementation.
    
    This class provides a memory-efficient list implementation that uses
    array.array for storing primitive types and regular lists for complex types.
    It also uses memory pooling for strings.
    """
    
    def __init__(self, items: Optional[Iterable[T]] = None, optimize: bool = True):
        """
        Initialize the memory-efficient list.
        
        Args:
            items: Initial items to add to the list
            optimize: Whether to optimize the list for memory efficiency
        """
        self._items = []
        self._optimize = optimize
        self._array = None
        self._array_type = None
        
        if items is not None:
            self.extend(items)
    
    def append(self, item: T) -> None:
        """
        Append an item to the list.
        
        Args:
            item: Item to append
        """
        # If we're using an array, check if the item is compatible
        if self._array is not None:
            try:
                self._array.append(item)
                return
            except (TypeError, OverflowError):
                # Convert array back to list if item is not compatible
                self._items = list(self._array)
                self._array = None
                self._array_type = None
        
        # For regular list, optimize strings
        if self._optimize and isinstance(item, str):
            item = string_pool.intern(item)
        
        self._items.append(item)
        
        # Check if we can convert to array
        if self._optimize and self._array is None and len(self._items) > 10:
            self._try_convert_to_array()
    
    def extend(self, items: Iterable[T]) -> None:
        """
        Extend the list with items from an iterable.
        
        Args:
            items: Iterable of items to add
        """
        # Convert items to list first to avoid multiple iterations
        items_list = list(items)
        
        # If we're using an array, check if all items are compatible
        if self._array is not None:
            try:
                self._array.extend(items_list)
                return
            except (TypeError, OverflowError):
                # Convert array back to list if items are not compatible
                self._items = list(self._array)
                self._array = None
                self._array_type = None
        
        # For regular list, optimize strings
        if self._optimize:
            for i, item in enumerate(items_list):
                if isinstance(item, str):
                    items_list[i] = string_pool.intern(item)
        
        self._items.extend(items_list)
        
        # Check if we can convert to array
        if self._optimize and self._array is None and len(self._items) > 10:
            self._try_convert_to_array()
    
    def _try_convert_to_array(self) -> None:
        """
        Try to convert the list to an array for memory efficiency.
        """
        # Check if all items are of the same primitive type
        if not self._items:
            return
        
        # Check the type of the first item
        first_item = self._items[0]
        
        # Determine array type based on first item
        array_type = None
        if isinstance(first_item, int):
            # Check the range of integers to use the smallest possible array type
            min_val = min(self._items)
            max_val = max(self._items)
            
            if min_val >= 0:
                if max_val <= 255:
                    array_type = 'B'  # unsigned char
                elif max_val <= 65535:
                    array_type = 'H'  # unsigned short
                elif max_val <= 4294967295:
                    array_type = 'I'  # unsigned int
                else:
                    array_type = 'L'  # unsigned long
            else:
                if min_val >= -128 and max_val <= 127:
                    array_type = 'b'  # signed char
                elif min_val >= -32768 and max_val <= 32767:
                    array_type = 'h'  # signed short
                elif min_val >= -2147483648 and max_val <= 2147483647:
                    array_type = 'i'  # signed int
                else:
                    array_type = 'l'  # signed long
        elif isinstance(first_item, float):
            array_type = 'd'  # double
        
        # Try to convert to array if a suitable type was found
        if array_type is not None:
            try:
                self._array = array.array(array_type, self._items)
                self._array_type = array_type
                self._items = []  # Free up memory
                logger.debug(f"Converted list to array of type '{array_type}'")
            except (TypeError, OverflowError):
                # If conversion fails, keep using regular list
                self._array = None
                self._array_type = None
    
    def __getitem__(self, index):
        """Get an item by index."""
        if self._array is not None:
            return self._array[index]
        return self._items[index]
    
    def __setitem__(self, index, value):
        """Set an item by index."""
        if self._array is not None:
            try:
                self._array[index] = value
                return
            except (TypeError, OverflowError):
                # Convert array back to list if value is not compatible
                self._items = list(self._array)
                self._array = None
                self._array_type = None
        
        # For regular list, optimize strings
        if self._optimize and isinstance(value, str):
            value = string_pool.intern(value)
        
        self._items[index] = value
    
    def __len__(self):
        """Get the length of the list."""
        if self._array is not None:
            return len(self._array)
        return len(self._items)
    
    def __iter__(self):
        """Iterate over the list."""
        if self._array is not None:
            return iter(self._array)
        return iter(self._items)
    
    def __repr__(self):
        """Get a string representation of the list."""
        if self._array is not None:
            return f"MemoryEfficientList({list(self._array)}, optimize={self._optimize})"
        return f"MemoryEfficientList({self._items}, optimize={self._optimize})"
    
    def get_memory_usage(self) -> int:
        """
        Get the memory usage of the list in bytes.
        
        Returns:
            Memory usage in bytes
        """
        if self._array is not None:
            # For array, use the itemsize
            return sys.getsizeof(self._array) + (len(self._array) * self._array.itemsize)
        
        # For regular list, estimate based on item types
        base_size = sys.getsizeof(self._items)
        item_size = 0
        
        for item in self._items:
            item_size += sys.getsizeof(item)
        
        return base_size + item_size


class MemoryEfficientDict(Generic[K, V]):
    """
    Memory-efficient dictionary implementation.
    
    This class provides a memory-efficient dictionary implementation that uses
    memory pooling for string keys and values.
    """
    
    def __init__(self, items: Optional[Dict[K, V]] = None, optimize: bool = True):
        """
        Initialize the memory-efficient dictionary.
        
        Args:
            items: Initial items to add to the dictionary
            optimize: Whether to optimize the dictionary for memory efficiency
        """
        self._dict = {}
        self._optimize = optimize
        
        if items is not None:
            self.update(items)
    
    def __getitem__(self, key: K) -> V:
        """Get an item by key."""
        return self._dict[key]
    
    def __setitem__(self, key: K, value: V) -> None:
        """Set an item by key."""
        # Optimize string keys and values
        if self._optimize:
            if isinstance(key, str):
                key = string_pool.intern(key)
            if isinstance(value, str):
                value = string_pool.intern(value)
        
        self._dict[key] = value
    
    def __delitem__(self, key: K) -> None:
        """Delete an item by key."""
        del self._dict[key]
    
    def __contains__(self, key: K) -> bool:
        """Check if the dictionary contains a key."""
        return key in self._dict
    
    def __len__(self) -> int:
        """Get the length of the dictionary."""
        return len(self._dict)
    
    def __iter__(self) -> Iterator[K]:
        """Iterate over the dictionary keys."""
        return iter(self._dict)
    
    def __repr__(self) -> str:
        """Get a string representation of the dictionary."""
        return f"MemoryEfficientDict({self._dict}, optimize={self._optimize})"
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Get an item by key with a default value."""
        return self._dict.get(key, default)
    
    def update(self, other: Dict[K, V]) -> None:
        """Update the dictionary with items from another dictionary."""
        if self._optimize:
            for key, value in other.items():
                # Optimize string keys and values
                if isinstance(key, str):
                    key = string_pool.intern(key)
                if isinstance(value, str):
                    value = string_pool.intern(value)
                self._dict[key] = value
        else:
            self._dict.update(other)
    
    def keys(self) -> Iterable[K]:
        """Get the dictionary keys."""
        return self._dict.keys()
    
    def values(self) -> Iterable[V]:
        """Get the dictionary values."""
        return self._dict.values()
    
    def items(self) -> Iterable[Tuple[K, V]]:
        """Get the dictionary items."""
        return self._dict.items()
    
    def get_memory_usage(self) -> int:
        """
        Get the memory usage of the dictionary in bytes.
        
        Returns:
            Memory usage in bytes
        """
        # Base size of the dictionary
        base_size = sys.getsizeof(self._dict)
        
        # Estimate size of keys and values
        keys_size = 0
        values_size = 0
        
        for key, value in self._dict.items():
            keys_size += sys.getsizeof(key)
            values_size += sys.getsizeof(value)
        
        return base_size + keys_size + values_size


class MemoryEfficientSet(Generic[T]):
    """
    Memory-efficient set implementation.
    
    This class provides a memory-efficient set implementation that uses
    memory pooling for string items.
    """
    
    def __init__(self, items: Optional[Iterable[T]] = None, optimize: bool = True):
        """
        Initialize the memory-efficient set.
        
        Args:
            items: Initial items to add to the set
            optimize: Whether to optimize the set for memory efficiency
        """
        self._set = set()
        self._optimize = optimize
        
        if items is not None:
            self.update(items)
    
    def add(self, item: T) -> None:
        """
        Add an item to the set.
        
        Args:
            item: Item to add
        """
        # Optimize string items
        if self._optimize and isinstance(item, str):
            item = string_pool.intern(item)
        
        self._set.add(item)
    
    def update(self, items: Iterable[T]) -> None:
        """
        Update the set with items from an iterable.
        
        Args:
            items: Iterable of items to add
        """
        if self._optimize:
            for item in items:
                # Optimize string items
                if isinstance(item, str):
                    self._set.add(string_pool.intern(item))
                else:
                    self._set.add(item)
        else:
            self._set.update(items)
    
    def remove(self, item: T) -> None:
        """
        Remove an item from the set.
        
        Args:
            item: Item to remove
        """
        self._set.remove(item)
    
    def discard(self, item: T) -> None:
        """
        Discard an item from the set.
        
        Args:
            item: Item to discard
        """
        self._set.discard(item)
    
    def __contains__(self, item: T) -> bool:
        """Check if the set contains an item."""
        return item in self._set
    
    def __len__(self) -> int:
        """Get the length of the set."""
        return len(self._set)
    
    def __iter__(self) -> Iterator[T]:
        """Iterate over the set."""
        return iter(self._set)
    
    def __repr__(self) -> str:
        """Get a string representation of the set."""
        return f"MemoryEfficientSet({self._set}, optimize={self._optimize})"
    
    def get_memory_usage(self) -> int:
        """
        Get the memory usage of the set in bytes.
        
        Returns:
            Memory usage in bytes
        """
        # Base size of the set
        base_size = sys.getsizeof(self._set)
        
        # Estimate size of items
        items_size = 0
        
        for item in self._set:
            items_size += sys.getsizeof(item)
        
        return base_size + items_size


class LRUCache(Generic[K, V]):
    """
    LRU (Least Recently Used) cache implementation.
    
    This class provides a memory-efficient LRU cache implementation that
    automatically evicts the least recently used items when the cache is full.
    """
    
    def __init__(self, max_size: int = 1000, optimize: bool = True):
        """
        Initialize the LRU cache.
        
        Args:
            max_size: Maximum number of items to keep in the cache
            optimize: Whether to optimize the cache for memory efficiency
        """
        self._cache = collections.OrderedDict()
        self._max_size = max_size
        self._optimize = optimize
        self._hits = 0
        self._misses = 0
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Get an item from the cache.
        
        Args:
            key: Key to look up
            default: Default value to return if key is not found
            
        Returns:
            Value associated with the key, or default if not found
        """
        if key in self._cache:
            # Move the item to the end of the OrderedDict (most recently used)
            value = self._cache.pop(key)
            self._cache[key] = value
            self._hits += 1
            return value
        
        self._misses += 1
        return default
    
    def put(self, key: K, value: V) -> None:
        """
        Put an item in the cache.
        
        Args:
            key: Key to store
            value: Value to store
        """
        # Optimize string keys and values
        if self._optimize:
            if isinstance(key, str):
                key = string_pool.intern(key)
            if isinstance(value, str):
                value = string_pool.intern(value)
        
        # If key already exists, remove it first
        if key in self._cache:
            self._cache.pop(key)
        
        # Add the new item
        self._cache[key] = value
        
        # Evict the least recently used item if the cache is full
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
    
    def __getitem__(self, key: K) -> V:
        """Get an item by key."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: K, value: V) -> None:
        """Set an item by key."""
        self.put(key, value)
    
    def __contains__(self, key: K) -> bool:
        """Check if the cache contains a key."""
        return key in self._cache
    
    def __len__(self) -> int:
        """Get the length of the cache."""
        return len(self._cache)
    
    def __iter__(self) -> Iterator[K]:
        """Iterate over the cache keys."""
        return iter(self._cache)
    
    def __repr__(self) -> str:
        """Get a string representation of the cache."""
        return f"LRUCache(max_size={self._max_size}, optimize={self._optimize}, items={len(self._cache)})"
    
    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total) * 100 if total > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }
    
    def get_memory_usage(self) -> int:
        """
        Get the memory usage of the cache in bytes.
        
        Returns:
            Memory usage in bytes
        """
        # Base size of the OrderedDict
        base_size = sys.getsizeof(self._cache)
        
        # Estimate size of keys and values
        keys_size = 0
        values_size = 0
        
        for key, value in self._cache.items():
            keys_size += sys.getsizeof(key)
            values_size += sys.getsizeof(value)
        
        return base_size + keys_size + values_size


# Function to optimize a list for memory efficiency
def optimize_list(items: List[Any]) -> List[Any]:
    """
    Optimize a list for memory efficiency.
    
    This function optimizes a list by:
    1. Interning string items
    2. Converting to a typed array if possible
    
    Args:
        items: List to optimize
        
    Returns:
        Optimized list
    """
    # Check if the list is empty
    if not items:
        return items
    
    # Check if all items are of the same primitive type
    first_item = items[0]
    all_same_type = True
    
    for item in items:
        if not isinstance(item, type(first_item)):
            all_same_type = False
            break
    
    # If all items are strings, intern them
    if all_same_type and isinstance(first_item, str):
        return [string_pool.intern(item) for item in items]
    
    # If all items are integers or floats, convert to array
    if all_same_type and isinstance(first_item, (int, float)):
        try:
            if isinstance(first_item, int):
                # Determine the appropriate array type based on the range of values
                min_val = min(items)
                max_val = max(items)
                
                if min_val >= 0:
                    if max_val <= 255:
                        return array.array('B', items)  # unsigned char
                    elif max_val <= 65535:
                        return array.array('H', items)  # unsigned short
                    elif max_val <= 4294967295:
                        return array.array('I', items)  # unsigned int
                    else:
                        return array.array('L', items)  # unsigned long
                else:
                    if min_val >= -128 and max_val <= 127:
                        return array.array('b', items)  # signed char
                    elif min_val >= -32768 and max_val <= 32767:
                        return array.array('h', items)  # signed short
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        return array.array('i', items)  # signed int
                    else:
                        return array.array('l', items)  # signed long
            else:  # float
                return array.array('d', items)  # double
        except (TypeError, OverflowError):
            # If conversion fails, return the original list
            pass
    
    # If optimization failed, return the original list
    return items


# Function to optimize a dictionary for memory efficiency
def optimize_dict(d: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Optimize a dictionary for memory efficiency.
    
    This function optimizes a dictionary by:
    1. Interning string keys and values
    
    Args:
        d: Dictionary to optimize
        
    Returns:
        Optimized dictionary
    """
    # Check if the dictionary is empty
    if not d:
        return d
    
    # Create a new dictionary with optimized keys and values
    optimized = {}
    
    for key, value in d.items():
        # Optimize string keys
        if isinstance(key, str):
            key = string_pool.intern(key)
        
        # Optimize string values
        if isinstance(value, str):
            value = string_pool.intern(value)
        # Recursively optimize dictionary values
        elif isinstance(value, dict):
            value = optimize_dict(value)
        # Optimize list values
        elif isinstance(value, list):
            value = optimize_list(value)
        
        optimized[key] = value
    
    return optimized


# Function to optimize a set for memory efficiency
def optimize_set(s: Set[Any]) -> Set[Any]:
    """
    Optimize a set for memory efficiency.
    
    This function optimizes a set by:
    1. Interning string items
    
    Args:
        s: Set to optimize
        
    Returns:
        Optimized set
    """
    # Check if the set is empty
    if not s:
        return s
    
    # Create a new set with optimized items
    optimized = set()
    
    for item in s:
        # Optimize string items
        if isinstance(item, str):
            optimized.add(string_pool.intern(item))
        else:
            optimized.add(item)
    
    return optimized