"""
URL Analysis Interfaces

This module defines interfaces for the URL Analysis domain.
These interfaces ensure proper separation of concerns and enable dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set

from url_analyzer.analysis.domain import (
    URLContent, ContentSummary, FetchResult, AnalysisResult, AnalysisOptions
)


class URLFetcher(ABC):
    """Interface for URL fetchers."""
    
    @abstractmethod
    def fetch_url(self, url: str, options: AnalysisOptions) -> FetchResult:
        """
        Fetch a URL.
        
        Args:
            url: URL to fetch
            options: Options for the fetch operation
            
        Returns:
            FetchResult containing the result of the fetch operation
        """
        pass
    
    @abstractmethod
    def fetch_urls(self, urls: List[str], options: AnalysisOptions) -> Dict[str, FetchResult]:
        """
        Fetch multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            options: Options for the fetch operations
            
        Returns:
            Dictionary mapping URLs to their fetch results
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this fetcher.
        
        Returns:
            Fetcher name
        """
        pass


class ContentAnalyzer(ABC):
    """Interface for content analyzers."""
    
    @abstractmethod
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> ContentSummary:
        """
        Analyze URL content.
        
        Args:
            content: URL content to analyze
            options: Options for the analysis
            
        Returns:
            ContentSummary containing the analysis results
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this analyzer.
        
        Returns:
            Analyzer name
        """
        pass
    
    @abstractmethod
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types (e.g., "text/html", "application/json")
        """
        pass


class CacheRepository(ABC):
    """Interface for cache repositories."""
    
    @abstractmethod
    def get_cached_result(self, url: str) -> Optional[AnalysisResult]:
        """
        Get a cached analysis result for a URL.
        
        Args:
            url: URL to get the cached result for
            
        Returns:
            Cached AnalysisResult or None if not found
        """
        pass
    
    @abstractmethod
    def cache_result(self, result: AnalysisResult) -> None:
        """
        Cache an analysis result.
        
        Args:
            result: AnalysisResult to cache
        """
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """
        Clear the cache.
        """
        pass
    
    @abstractmethod
    def get_cache_size(self) -> int:
        """
        Get the number of items in the cache.
        
        Returns:
            Number of cached items
        """
        pass
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary of cache statistics
        """
        pass


class AnalysisService(ABC):
    """Interface for analysis services."""
    
    @abstractmethod
    def analyze_url(self, url: str, options: Optional[AnalysisOptions] = None) -> AnalysisResult:
        """
        Analyze a URL.
        
        Args:
            url: URL to analyze
            options: Optional analysis options
            
        Returns:
            AnalysisResult containing the analysis results
        """
        pass
    
    @abstractmethod
    def analyze_urls(self, urls: List[str], options: Optional[AnalysisOptions] = None) -> Dict[str, AnalysisResult]:
        """
        Analyze multiple URLs.
        
        Args:
            urls: List of URLs to analyze
            options: Optional analysis options
            
        Returns:
            Dictionary mapping URLs to their analysis results
        """
        pass
    
    @abstractmethod
    def get_fetcher(self) -> URLFetcher:
        """
        Get the URL fetcher used by this service.
        
        Returns:
            URLFetcher instance
        """
        pass
    
    @abstractmethod
    def get_analyzers(self) -> List[ContentAnalyzer]:
        """
        Get the content analyzers used by this service.
        
        Returns:
            List of ContentAnalyzer instances
        """
        pass
    
    @abstractmethod
    def get_cache_repository(self) -> Optional[CacheRepository]:
        """
        Get the cache repository used by this service.
        
        Returns:
            CacheRepository instance or None if caching is disabled
        """
        pass
    
    @abstractmethod
    def set_fetcher(self, fetcher: URLFetcher) -> None:
        """
        Set the URL fetcher to use.
        
        Args:
            fetcher: URLFetcher to use
        """
        pass
    
    @abstractmethod
    def add_analyzer(self, analyzer: ContentAnalyzer) -> None:
        """
        Add a content analyzer.
        
        Args:
            analyzer: ContentAnalyzer to add
        """
        pass
    
    @abstractmethod
    def remove_analyzer(self, name: str) -> None:
        """
        Remove a content analyzer.
        
        Args:
            name: Name of the analyzer to remove
        """
        pass
    
    @abstractmethod
    def set_cache_repository(self, cache_repository: Optional[CacheRepository]) -> None:
        """
        Set the cache repository to use.
        
        Args:
            cache_repository: CacheRepository to use, or None to disable caching
        """
        pass