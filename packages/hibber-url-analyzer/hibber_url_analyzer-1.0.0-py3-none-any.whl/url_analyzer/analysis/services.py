"""
URL Analysis Services

This module provides services for URL analysis based on the interfaces
defined in the interfaces module. It implements the core functionality for
fetching and analyzing URL content.
"""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urlparse

from url_analyzer.utils.optimized_concurrency import optimized_thread_pool
from url_analyzer.utils.rate_limiter import rate_limited, get_rate_limiter_status

from url_analyzer.analysis.domain import (
    URLContent, ContentSummary, FetchResult, AnalysisResult, AnalysisOptions
)
from url_analyzer.analysis.interfaces import (
    URLFetcher, ContentAnalyzer, CacheRepository, AnalysisService
)


class RequestsURLFetcher(URLFetcher):
    """
    URL fetcher implementation using the requests library.
    """
    
    def __init__(self, name: str = "Requests URL Fetcher"):
        """
        Initialize the fetcher.
        
        Args:
            name: Name of this fetcher
        """
        self._name = name
        
        # Import requests here to allow graceful degradation if not available
        try:
            import requests
            self._requests = requests
            self._requests_available = True
        except ImportError:
            self._requests = None
            self._requests_available = False
    
    def fetch_url(self, url: str, options: AnalysisOptions) -> FetchResult:
        """
        Fetch a URL using the requests library with rate limiting.
        
        Args:
            url: URL to fetch
            options: Options for the fetch operation
            
        Returns:
            FetchResult containing the result of the fetch operation
        """
        # Check if requests is available
        if not self._requests_available:
            return FetchResult(
                url=url,
                success=False,
                error_message="The requests library is not available"
            )
        
        # Check if URL is empty
        if not url or not url.strip():
            return FetchResult(
                url=url,
                success=False,
                error_message="Empty URL provided"
            )
        
        # Extract domain for rate limiting
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Determine endpoint type based on URL patterns
            endpoint_type = 'default'
            if 'api' in domain.lower() or '/api/' in url.lower():
                endpoint_type = 'api'
            elif any(pattern in domain.lower() for pattern in ['github.com', 'stackoverflow.com', 'reddit.com']):
                endpoint_type = 'web'
            
        except Exception:
            domain = 'unknown'
            endpoint_type = 'default'
        
        # Apply rate limiting
        from url_analyzer.utils.rate_limiter import _global_rate_limiter
        if not _global_rate_limiter.acquire(domain, endpoint_type, tokens=1, timeout=10.0):
            return FetchResult(
                url=url,
                success=False,
                error_message=f"Rate limit exceeded for domain {domain}"
            )
        
        # Prepare headers
        headers = dict(options.headers)
        if options.user_agent:
            headers['User-Agent'] = options.user_agent
        
        try:
            # Fetch the URL
            response = self._requests.get(
                url,
                headers=headers,
                timeout=options.fetch_timeout,
                allow_redirects=options.follow_redirects,
                stream=True  # Use streaming to avoid loading large content into memory
            )
            
            # Get content size
            content_size = int(response.headers.get('Content-Length', 0))
            
            # Check if content size exceeds the maximum
            if options.max_content_size and content_size > options.max_content_size:
                return FetchResult(
                    url=url,
                    success=False,
                    status_code=response.status_code,
                    error_message=f"Content size ({content_size} bytes) exceeds maximum ({options.max_content_size} bytes)"
                )
            
            # Get content
            content = response.text
            
            # Create URLContent object
            url_content = URLContent(
                url=url,
                content_type=response.headers.get('Content-Type', 'text/plain'),
                status_code=response.status_code,
                content=content,
                headers={k.lower(): v for k, v in response.headers.items()},
                fetch_time=datetime.now(),
                size_bytes=len(content.encode('utf-8'))
            )
            
            # Create FetchResult
            return FetchResult(
                url=url,
                success=True,
                status_code=response.status_code,
                content=url_content
            )
            
        except Exception as e:
            # Handle fetch errors
            return FetchResult(
                url=url,
                success=False,
                error_message=str(e)
            )
    
    def fetch_urls(self, urls: List[str], options: AnalysisOptions) -> Dict[str, FetchResult]:
        """
        Fetch multiple URLs using the requests library.
        
        Args:
            urls: List of URLs to fetch
            options: Options for the fetch operations
            
        Returns:
            Dictionary mapping URLs to their fetch results
        """
        results = {}
        
        # Use optimized ThreadPoolExecutor for parallel fetching
        with optimized_thread_pool(
            workload_type="io_bound",
            task_count=len(urls)
        ) as executor:
            future_to_url = {executor.submit(self.fetch_url, url, options): url for url in urls}
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    # Handle fetch errors
                    results[url] = FetchResult(
                        url=url,
                        success=False,
                        error_message=str(e)
                    )
        
        return results
    
    def get_name(self) -> str:
        """
        Get the name of this fetcher.
        
        Returns:
            Fetcher name
        """
        return self._name


class HTMLContentAnalyzer(ContentAnalyzer):
    """
    Content analyzer for HTML content.
    """
    
    def __init__(self, name: str = "HTML Content Analyzer"):
        """
        Initialize the analyzer.
        
        Args:
            name: Name of this analyzer
        """
        self._name = name
        
        # Import BeautifulSoup here to allow graceful degradation if not available
        try:
            from bs4 import BeautifulSoup
            self._bs4 = BeautifulSoup
            self._bs4_available = True
        except ImportError:
            self._bs4 = None
            self._bs4_available = False
    
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> ContentSummary:
        """
        Analyze HTML content.
        
        Args:
            content: URL content to analyze
            options: Options for the analysis
            
        Returns:
            ContentSummary containing the analysis results
        """
        # Check if BeautifulSoup is available
        if not self._bs4_available:
            return ContentSummary(
                url=content.url,
                title="BeautifulSoup not available",
                description="The BeautifulSoup library is required for HTML analysis"
            )
        
        # Check if content is HTML
        if not content.is_html:
            return ContentSummary(
                url=content.url,
                title="Not HTML content",
                description=f"Content type is {content.content_type}"
            )
        
        try:
            # Parse HTML
            soup = self._bs4(content.content, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
            
            # Extract description
            description = None
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if meta_description:
                description = meta_description.get('content', '').strip()
            
            # Extract keywords
            keywords = []
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                keywords_text = meta_keywords.get('content', '')
                keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Extract language
            language = None
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                language = html_tag.get('lang').strip()
            
            # Count words
            text = soup.get_text()
            word_count = len(re.findall(r'\w+', text))
            
            # Create ContentSummary
            return ContentSummary(
                url=content.url,
                title=title,
                description=description,
                keywords=keywords,
                language=language,
                word_count=word_count
            )
            
        except Exception as e:
            # Handle analysis errors
            return ContentSummary(
                url=content.url,
                title="Error analyzing content",
                description=str(e)
            )
    
    def get_name(self) -> str:
        """
        Get the name of this analyzer.
        
        Returns:
            Analyzer name
        """
        return self._name
    
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types
        """
        return {'text/html'}


class JSONContentAnalyzer(ContentAnalyzer):
    """
    Content analyzer for JSON content.
    """
    
    def __init__(self, name: str = "JSON Content Analyzer"):
        """
        Initialize the analyzer.
        
        Args:
            name: Name of this analyzer
        """
        self._name = name
    
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> ContentSummary:
        """
        Analyze JSON content.
        
        Args:
            content: URL content to analyze
            options: Options for the analysis
            
        Returns:
            ContentSummary containing the analysis results
        """
        # Check if content is JSON
        if not content.is_json:
            return ContentSummary(
                url=content.url,
                title="Not JSON content",
                description=f"Content type is {content.content_type}"
            )
        
        try:
            # Parse JSON
            data = json.loads(content.content)
            
            # Extract title
            title = None
            if isinstance(data, dict):
                title = data.get('title', None)
                if title is None:
                    title = data.get('name', None)
            
            # Extract description
            description = None
            if isinstance(data, dict):
                description = data.get('description', None)
                if description is None:
                    description = data.get('summary', None)
            
            # Count words
            word_count = 0
            if isinstance(data, dict):
                text = json.dumps(data)
                word_count = len(re.findall(r'\w+', text))
            
            # Create ContentSummary
            return ContentSummary(
                url=content.url,
                title=title,
                description=description,
                word_count=word_count
            )
            
        except Exception as e:
            # Handle analysis errors
            return ContentSummary(
                url=content.url,
                title="Error analyzing content",
                description=str(e)
            )
    
    def get_name(self) -> str:
        """
        Get the name of this analyzer.
        
        Returns:
            Analyzer name
        """
        return self._name
    
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types
        """
        return {'application/json'}


class InMemoryCacheRepository(CacheRepository):
    """
    In-memory implementation of the cache repository.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the repository.
        
        Args:
            max_size: Maximum number of items to store in the cache
        """
        self._cache: Dict[str, AnalysisResult] = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def get_cached_result(self, url: str) -> Optional[AnalysisResult]:
        """
        Get a cached analysis result for a URL.
        
        Args:
            url: URL to get the cached result for
            
        Returns:
            Cached AnalysisResult or None if not found
        """
        result = self._cache.get(url)
        
        if result:
            self._hits += 1
        else:
            self._misses += 1
        
        return result
    
    def cache_result(self, result: AnalysisResult) -> None:
        """
        Cache an analysis result.
        
        Args:
            result: AnalysisResult to cache
        """
        # If cache is full, remove the oldest item
        if len(self._cache) >= self._max_size:
            oldest_url = next(iter(self._cache))
            del self._cache[oldest_url]
        
        # Add the new item
        self._cache[result.url] = result
    
    def clear_cache(self) -> None:
        """
        Clear the cache.
        """
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def get_cache_size(self) -> int:
        """
        Get the number of items in the cache.
        
        Returns:
            Number of cached items
        """
        return len(self._cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary of cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate
        }


class DefaultAnalysisService(AnalysisService):
    """
    Default implementation of the analysis service.
    """
    
    def __init__(self, 
                 fetcher: Optional[URLFetcher] = None,
                 analyzers: Optional[List[ContentAnalyzer]] = None,
                 cache_repository: Optional[CacheRepository] = None):
        """
        Initialize the service.
        
        Args:
            fetcher: Optional URL fetcher to use
            analyzers: Optional list of content analyzers to use
            cache_repository: Optional cache repository to use
        """
        self._fetcher = fetcher or RequestsURLFetcher()
        self._analyzers = analyzers or [HTMLContentAnalyzer(), JSONContentAnalyzer()]
        self._cache_repository = cache_repository
        self._analyzer_map: Dict[str, ContentAnalyzer] = {
            analyzer.get_name(): analyzer for analyzer in self._analyzers
        }
    
    def analyze_url(self, url: str, options: Optional[AnalysisOptions] = None) -> AnalysisResult:
        """
        Analyze a URL.
        
        Args:
            url: URL to analyze
            options: Optional analysis options
            
        Returns:
            AnalysisResult containing the analysis results
        """
        # Use default options if none provided
        if options is None:
            options = AnalysisOptions()
        
        # Check cache first if available
        if self._cache_repository:
            cached_result = self._cache_repository.get_cached_result(url)
            if cached_result:
                return cached_result
        
        # Fetch the URL
        fetch_result = self._fetcher.fetch_url(url, options)
        
        # If fetch failed, return analysis result with fetch error
        if not fetch_result.is_success:
            result = AnalysisResult(
                url=url,
                fetch_result=fetch_result
            )
            
            # Cache the result if caching is enabled
            if self._cache_repository:
                self._cache_repository.cache_result(result)
            
            return result
        
        # Find an analyzer for the content type
        content = fetch_result.content
        analyzer = self._find_analyzer_for_content(content)
        
        # If no analyzer found, return analysis result without content summary
        if not analyzer:
            result = AnalysisResult(
                url=url,
                fetch_result=fetch_result,
                metadata={'error': f"No analyzer found for content type: {content.content_type}"}
            )
            
            # Cache the result if caching is enabled
            if self._cache_repository:
                self._cache_repository.cache_result(result)
            
            return result
        
        # Analyze the content
        content_summary = analyzer.analyze_content(content, options)
        
        # Create analysis result
        result = AnalysisResult(
            url=url,
            fetch_result=fetch_result,
            content_summary=content_summary,
            metadata={
                'analyzer': analyzer.get_name(),
                'content_type': content.content_type
            }
        )
        
        # Cache the result if caching is enabled
        if self._cache_repository:
            self._cache_repository.cache_result(result)
        
        return result
    
    def analyze_urls(self, urls: List[str], options: Optional[AnalysisOptions] = None) -> Dict[str, AnalysisResult]:
        """
        Analyze multiple URLs.
        
        Args:
            urls: List of URLs to analyze
            options: Optional analysis options
            
        Returns:
            Dictionary mapping URLs to their analysis results
        """
        results = {}
        
        # Use optimized ThreadPoolExecutor for parallel analysis
        with optimized_thread_pool(
            workload_type="mixed",  # Analysis involves both I/O and CPU work
            task_count=len(urls)
        ) as executor:
            future_to_url = {executor.submit(self.analyze_url, url, options): url for url in urls}
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    # Handle analysis errors
                    fetch_result = FetchResult(
                        url=url,
                        success=False,
                        error_message=str(e)
                    )
                    results[url] = AnalysisResult(
                        url=url,
                        fetch_result=fetch_result,
                        metadata={'error': str(e)}
                    )
        
        return results
    
    def get_fetcher(self) -> URLFetcher:
        """
        Get the URL fetcher used by this service.
        
        Returns:
            URLFetcher instance
        """
        return self._fetcher
    
    def get_analyzers(self) -> List[ContentAnalyzer]:
        """
        Get the content analyzers used by this service.
        
        Returns:
            List of ContentAnalyzer instances
        """
        return self._analyzers
    
    def get_cache_repository(self) -> Optional[CacheRepository]:
        """
        Get the cache repository used by this service.
        
        Returns:
            CacheRepository instance or None if caching is disabled
        """
        return self._cache_repository
    
    def set_fetcher(self, fetcher: URLFetcher) -> None:
        """
        Set the URL fetcher to use.
        
        Args:
            fetcher: URLFetcher to use
        """
        self._fetcher = fetcher
    
    def add_analyzer(self, analyzer: ContentAnalyzer) -> None:
        """
        Add a content analyzer.
        
        Args:
            analyzer: ContentAnalyzer to add
        """
        self._analyzers.append(analyzer)
        self._analyzer_map[analyzer.get_name()] = analyzer
    
    def remove_analyzer(self, name: str) -> None:
        """
        Remove a content analyzer.
        
        Args:
            name: Name of the analyzer to remove
        """
        if name in self._analyzer_map:
            analyzer = self._analyzer_map[name]
            self._analyzers.remove(analyzer)
            del self._analyzer_map[name]
    
    def set_cache_repository(self, cache_repository: Optional[CacheRepository]) -> None:
        """
        Set the cache repository to use.
        
        Args:
            cache_repository: CacheRepository to use, or None to disable caching
        """
        self._cache_repository = cache_repository
    
    def _find_analyzer_for_content(self, content: URLContent) -> Optional[ContentAnalyzer]:
        """
        Find an analyzer that supports the content type.
        
        Args:
            content: URL content to find an analyzer for
            
        Returns:
            ContentAnalyzer that supports the content type, or None if none found
        """
        content_type = content.content_type.split(';')[0].strip().lower()
        
        for analyzer in self._analyzers:
            supported_types = analyzer.get_supported_content_types()
            if content_type in supported_types:
                return analyzer
        
        # If no exact match, try to find an analyzer that supports a broader content type
        for analyzer in self._analyzers:
            supported_types = analyzer.get_supported_content_types()
            for supported_type in supported_types:
                if content_type.startswith(supported_type.split('/')[0]):
                    return analyzer
        
        return None