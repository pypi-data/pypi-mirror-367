"""
Mock infrastructure implementations for the URL Analyzer API.

This module provides mock implementations of the infrastructure interfaces
required by the URL Analyzer API. These implementations are simplified versions
that allow the API to function without requiring the full infrastructure layer.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime

from url_analyzer.application.interfaces import (
    URLRepository, URLClassificationService, URLContentAnalysisService,
    CacheService, LoggingService
)
from url_analyzer.domain.entities import URL, URLAnalysisResult
from url_analyzer.domain.value_objects import URLClassificationRule
from url_analyzer.core.classification import classify_url as core_classify_url


class URLRepositoryImpl(URLRepository):
    """
    Mock implementation of the URL repository.
    
    This implementation stores URLs in memory for the duration of the API session.
    """
    
    def __init__(self):
        """Initialize the repository with an empty storage."""
        self._storage: Dict[str, URL] = {}
    
    def get_by_url(self, url_string: str) -> Optional[URL]:
        """
        Get a URL entity by its URL string.
        
        Args:
            url_string: The URL string to look up
            
        Returns:
            The URL entity if found, None otherwise
        """
        return self._storage.get(url_string)
    
    def save(self, url_entity: URL) -> None:
        """
        Save a URL entity to the repository.
        
        Args:
            url_entity: The URL entity to save
        """
        self._storage[url_entity.url] = url_entity
    
    def get_all(self) -> List[URL]:
        """
        Get all URL entities in the repository.
        
        Returns:
            A list of all URL entities
        """
        return list(self._storage.values())
    
    def get_by_category(self, category: str) -> List[URL]:
        """
        Get URL entities by category.
        
        Args:
            category: The category to filter by
            
        Returns:
            A list of URL entities in the specified category
        """
        return [url for url in self._storage.values() if url.category == category]
    
    def get_by_domain(self, domain: str) -> List[URL]:
        """
        Get URL entities by domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            A list of URL entities with the specified domain
        """
        from urllib.parse import urlparse
        return [url for url in self._storage.values() 
                if urlparse(url.url).netloc == domain]
    
    def delete(self, url_string: str) -> bool:
        """
        Delete a URL entity from the repository.
        
        Args:
            url_string: The URL string to delete
            
        Returns:
            True if the URL was deleted, False otherwise
        """
        if url_string in self._storage:
            del self._storage[url_string]
            return True
        return False


class URLClassificationServiceImpl(URLClassificationService):
    """
    Mock implementation of the URL classification service.
    
    This implementation uses the core classification functionality directly.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the service with configuration.
        
        Args:
            config: Configuration dictionary with classification patterns
        """
        self.config = config
    
    def classify_url(self, url: str) -> URLClassificationRule:
        """
        Classify a URL.
        
        Args:
            url: The URL to classify
            
        Returns:
            A classification rule with category, sensitivity, and subcategory
        """
        category, is_sensitive, subcategory = core_classify_url(url, self.config)
        return URLClassificationRule(
            category=category,
            is_sensitive=is_sensitive,
            subcategory=subcategory
        )
    
    def classify(self, url: str) -> Tuple[str, bool]:
        """
        Classify a URL.
        
        Args:
            url: The URL to classify
            
        Returns:
            A tuple of (category, is_sensitive)
        """
        category, is_sensitive, _ = core_classify_url(url, self.config)
        return (category, is_sensitive)
    
    def get_rules(self) -> List[URLClassificationRule]:
        """
        Get all classification rules.
        
        Returns:
            A list of all classification rules
        """
        # For this mock implementation, we'll create rules from the config patterns
        rules = []
        
        # Add sensitive patterns as rules
        if 'sensitive_patterns' in self.config:
            for pattern in self.config['sensitive_patterns']:
                rules.append(URLClassificationRule(
                    name=f"sensitive_{pattern}",
                    pattern=pattern,
                    category="Sensitive",
                    is_sensitive=True,
                    subcategory=None
                ))
        
        # Add junk subcategory patterns as rules
        if 'junk_subcategories' in self.config:
            for subcategory, patterns in self.config['junk_subcategories'].items():
                for pattern in patterns:
                    rules.append(URLClassificationRule(
                        name=f"junk_{subcategory}_{pattern}",
                        pattern=pattern,
                        category="Junk",
                        is_sensitive=False,
                        subcategory=subcategory
                    ))
        
        return rules
    
    def add_rule(self, rule: URLClassificationRule) -> None:
        """
        Add a classification rule.
        
        Args:
            rule: The rule to add
        """
        # For this mock implementation, we'll add the pattern to the appropriate config section
        if rule.is_sensitive:
            if 'sensitive_patterns' not in self.config:
                self.config['sensitive_patterns'] = []
            if rule.pattern not in self.config['sensitive_patterns']:
                self.config['sensitive_patterns'].append(rule.pattern)
        elif rule.category == "Junk" and rule.subcategory:
            if 'junk_subcategories' not in self.config:
                self.config['junk_subcategories'] = {}
            if rule.subcategory not in self.config['junk_subcategories']:
                self.config['junk_subcategories'][rule.subcategory] = []
            if rule.pattern not in self.config['junk_subcategories'][rule.subcategory]:
                self.config['junk_subcategories'][rule.subcategory].append(rule.pattern)
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a classification rule.
        
        Args:
            rule_name: The name of the rule to remove
            
        Returns:
            True if the rule was removed, False otherwise
        """
        # For this mock implementation, we'll try to find and remove the pattern
        # This is a simplified approach based on rule naming convention
        
        if rule_name.startswith("sensitive_"):
            pattern = rule_name[10:]  # Remove "sensitive_" prefix
            if 'sensitive_patterns' in self.config and pattern in self.config['sensitive_patterns']:
                self.config['sensitive_patterns'].remove(pattern)
                return True
        elif rule_name.startswith("junk_"):
            # Parse junk rule name: junk_{subcategory}_{pattern}
            parts = rule_name.split("_", 2)
            if len(parts) >= 3:
                subcategory = parts[1]
                pattern = parts[2]
                if ('junk_subcategories' in self.config and 
                    subcategory in self.config['junk_subcategories'] and
                    pattern in self.config['junk_subcategories'][subcategory]):
                    self.config['junk_subcategories'][subcategory].remove(pattern)
                    return True
        
        return False
    
    def update_patterns(self, patterns: Dict[str, Any]) -> None:
        """
        Update the classification patterns.
        
        Args:
            patterns: New classification patterns
        """
        self.config.update(patterns)


class URLContentAnalysisServiceImpl(URLContentAnalysisService):
    """
    Mock implementation of the URL content analysis service.
    
    This implementation returns mock content metadata.
    """
    
    def analyze_content(self, url: str) -> Dict[str, Any]:
        """
        Analyze the content of a URL.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Content metadata dictionary
        """
        # In a real implementation, this would fetch and analyze the content
        # For the mock, we return some basic metadata
        return {
            'title': f"Title for {url}",
            'description': f"Description for {url}",
            'keywords': ['url', 'analyzer', 'api'],
            'text_length': 1000,
            'links_count': 10,
            'images_count': 5,
            'status_code': 200,
            'summary': f"This is a summary of the content at {url}."
        }
    
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get metadata for a URL.
        
        Args:
            url: The URL to get metadata for
            
        Returns:
            A dictionary of metadata
        """
        # In a real implementation, this would fetch metadata from the URL
        # For the mock, we return some basic metadata
        return {
            'url': url,
            'title': f"Title for {url}",
            'description': f"Description for {url}",
            'keywords': ['url', 'analyzer', 'api'],
            'author': 'Unknown',
            'published_date': None,
            'content_type': 'text/html',
            'language': 'en',
            'charset': 'utf-8'
        }
    
    def extract_links(self, url: str) -> List[str]:
        """
        Extract links from a URL.
        
        Args:
            url: The URL to extract links from
            
        Returns:
            A list of links found in the URL content
        """
        # In a real implementation, this would fetch the page and extract links
        # For the mock, we return some sample links
        from urllib.parse import urljoin, urlparse
        
        base_domain = urlparse(url).netloc
        return [
            urljoin(url, '/page1'),
            urljoin(url, '/page2'),
            urljoin(url, '/about'),
            urljoin(url, '/contact'),
            f"https://{base_domain}/external1",
            f"https://{base_domain}/external2"
        ]


class CacheServiceImpl(CacheService):
    """
    Mock implementation of the cache service.
    
    This implementation provides a simple in-memory cache.
    """
    
    def __init__(self):
        """Initialize the cache with an empty storage."""
        self._storage: Dict[str, Any] = {}
        self._expiry: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value if found and not expired, None otherwise
        """
        if key not in self._storage:
            return None
            
        if key in self._expiry and self._expiry[key] < datetime.now():
            # Expired
            del self._storage[key]
            del self._expiry[key]
            return None
            
        return self._storage[key]
    
    def set(self, url: str, results: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Cache results for a URL.
        
        Args:
            url: The URL to cache results for
            results: The results to cache
            ttl: Time to live in seconds (optional)
        """
        self._storage[url] = results
        if ttl is not None:
            from datetime import timedelta
            self._expiry[url] = datetime.now() + timedelta(seconds=ttl)
        else:
            # Default TTL of 1 hour
            from datetime import timedelta
            self._expiry[url] = datetime.now() + timedelta(seconds=3600)
    
    def delete(self, url: str) -> bool:
        """
        Delete cached results for a URL.
        
        Args:
            url: The URL to delete cached results for
            
        Returns:
            True if the cached results were deleted, False otherwise
        """
        deleted = False
        if url in self._storage:
            del self._storage[url]
            deleted = True
            
        if url in self._expiry:
            del self._expiry[url]
            
        return deleted
    
    def clear(self) -> None:
        """Clear all cached results."""
        self._storage.clear()
        self._expiry.clear()
    
    def get_size(self) -> int:
        """
        Get the size of the cache.
        
        Returns:
            The number of items in the cache
        """
        return len(self._storage)


class LoggingServiceImpl(LoggingService):
    """
    Mock implementation of the logging service.
    
    This implementation uses the standard Python logging module.
    """
    
    def __init__(self):
        """Initialize the logging service."""
        self.logger = logging.getLogger('url_analyzer.api')
    
    def debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
        """
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
        """
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
        """
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
        """
        self.logger.critical(message)