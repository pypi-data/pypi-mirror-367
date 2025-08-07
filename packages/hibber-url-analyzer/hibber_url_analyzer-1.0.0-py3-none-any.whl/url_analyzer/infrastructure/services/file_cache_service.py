"""
File-based Cache Service

This module provides a file-based implementation of the CacheService interface.
It stores cached results in a JSON file with TTL support.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Optional, Any


from url_analyzer.application.interfaces import CacheService


class FileCacheService(CacheService):
    """
    File-based implementation of the CacheService interface.
    
    This class stores cached results in a JSON file with TTL support.
    """
    
    def __init__(self, cache_file: str, default_ttl: int = 86400):
        """
        Initialize the cache service with a cache file.
        
        Args:
            cache_file: Path to the cache file
            default_ttl: Default time-to-live in seconds (default: 1 day)
        """
        self.cache_file = cache_file
        self.default_ttl = default_ttl
        self._ensure_cache_file_exists()
    
    def _ensure_cache_file_exists(self) -> None:
        """Ensure that the cache file exists."""
        if not os.path.exists(self.cache_file):
            # Create the directory if it doesn't exist
            directory = os.path.dirname(self.cache_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Create an empty cache file
            with open(self.cache_file, 'w') as f:
                json.dump({}, f)
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the cache from the cache file.
        
        Returns:
            Dictionary of cached results keyed by URL
        """
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or invalid, return an empty dictionary
            return {}
    
    def _save_cache(self, cache: Dict[str, Dict[str, Any]]) -> None:
        """
        Save the cache to the cache file.
        
        Args:
            cache: Dictionary of cached results keyed by URL
        """
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    
    def _clean_expired_entries(self, cache: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Remove expired entries from the cache.
        
        Args:
            cache: Dictionary of cached results keyed by URL
            
        Returns:
            Cleaned cache with expired entries removed
        """
        now = time.time()
        cleaned_cache = {}
        
        for url, entry in cache.items():
            # Check if the entry has an expiration time and if it's still valid
            if 'expires_at' not in entry or entry['expires_at'] > now:
                cleaned_cache[url] = entry
        
        return cleaned_cache
    
    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached results for a URL.
        
        Args:
            url: The URL to get cached results for
            
        Returns:
            The cached results if found and not expired, None otherwise
        """
        cache = self._load_cache()
        
        # Clean expired entries
        cache = self._clean_expired_entries(cache)
        
        # Get the cached entry
        entry = cache.get(url)
        
        if entry:
            # Return the cached data (without metadata)
            return entry.get('data')
        
        return None
    
    def set(self, url: str, results: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Cache results for a URL.
        
        Args:
            url: The URL to cache results for
            results: The results to cache
            ttl: Time to live in seconds (optional, uses default if not provided)
        """
        cache = self._load_cache()
        
        # Clean expired entries
        cache = self._clean_expired_entries(cache)
        
        # Calculate expiration time
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl
        
        # Create cache entry
        cache[url] = {
            'data': results,
            'created_at': time.time(),
            'expires_at': expires_at
        }
        
        # Save the cache
        self._save_cache(cache)
    
    def delete(self, url: str) -> bool:
        """
        Delete cached results for a URL.
        
        Args:
            url: The URL to delete cached results for
            
        Returns:
            True if the cached results were deleted, False otherwise
        """
        cache = self._load_cache()
        
        if url in cache:
            del cache[url]
            self._save_cache(cache)
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all cached results."""
        self._save_cache({})
    
    def get_size(self) -> int:
        """
        Get the size of the cache.
        
        Returns:
            The number of items in the cache
        """
        cache = self._load_cache()
        
        # Clean expired entries
        cache = self._clean_expired_entries(cache)
        
        return len(cache)