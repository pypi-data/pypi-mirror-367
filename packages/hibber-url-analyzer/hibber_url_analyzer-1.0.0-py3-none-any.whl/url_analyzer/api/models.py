"""
API data models for URL Analyzer.

This module defines the data models used by the URL Analyzer API.
These models provide a clean interface for data exchange between
the API and client applications.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union


class APIVersion(Enum):
    """API version enumeration."""
    V1 = "v1"
    V2 = "v2"
    
    def __str__(self) -> str:
        """Return string representation of the API version."""
        return self.value


@dataclass
class AnalysisRequest:
    """
    Request model for URL analysis.
    
    This class represents a request to analyze one or more URLs.
    
    Args:
        urls: List of URLs to analyze
        include_content: Whether to fetch and analyze page content
        include_summary: Whether to generate a summary of the URL content
        timeout: Request timeout in seconds
        max_workers: Maximum number of concurrent workers for batch processing
        custom_patterns: Optional custom patterns to use for classification
    """
    urls: List[str]
    include_content: bool = False
    include_summary: bool = False
    timeout: int = 7
    max_workers: int = 20
    custom_patterns: Optional[Dict[str, List[str]]] = None
    
    def __post_init__(self):
        """Validate the request data."""
        if not self.urls:
            raise ValueError("At least one URL must be provided")
        
        if not all(isinstance(url, str) for url in self.urls):
            raise TypeError("All URLs must be strings")
        
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_workers <= 0:
            raise ValueError("Max workers must be positive")


@dataclass
class URLMetadata:
    """
    Metadata about a URL.
    
    This class represents metadata extracted from a URL.
    
    Args:
        domain: The domain of the URL
        path: The path component of the URL
        query_params: The query parameters of the URL
        fragment: The fragment component of the URL
        protocol: The protocol of the URL
        port: The port of the URL
    """
    domain: str
    path: str
    query_params: Dict[str, str] = field(default_factory=dict)
    fragment: Optional[str] = None
    protocol: str = "https"
    port: Optional[int] = None


@dataclass
class ContentAnalysis:
    """
    Analysis of URL content.
    
    This class represents the analysis of the content of a URL.
    
    Args:
        title: The title of the page
        description: The meta description of the page
        keywords: The meta keywords of the page
        text_length: The length of the text content
        links_count: The number of links on the page
        images_count: The number of images on the page
        summary: A summary of the page content
    """
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    text_length: int = 0
    links_count: int = 0
    images_count: int = 0
    summary: Optional[str] = None


@dataclass
class AnalysisResult:
    """
    Result of URL analysis.
    
    This class represents the result of analyzing a URL.
    
    Args:
        url: The analyzed URL
        category: The category of the URL
        is_sensitive: Whether the URL is sensitive
        metadata: Metadata about the URL
        content: Analysis of the URL content
        status_code: HTTP status code from fetching the URL
        error: Error message if analysis failed
        subcategory: Subcategory of the URL
        score: Confidence score for the classification
        tags: Tags associated with the URL
    """
    url: str
    category: Optional[str] = None
    is_sensitive: bool = False
    metadata: Optional[URLMetadata] = None
    content: Optional[ContentAnalysis] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    subcategory: Optional[str] = None
    score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Return whether the analysis was successful."""
        return self.error is None and self.category is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        result = {
            "url": self.url,
            "success": self.success,
            "category": self.category,
            "is_sensitive": self.is_sensitive,
        }
        
        if self.subcategory:
            result["subcategory"] = self.subcategory
            
        if self.score is not None:
            result["score"] = self.score
            
        if self.tags:
            result["tags"] = self.tags
            
        if self.status_code:
            result["status_code"] = self.status_code
            
        if self.error:
            result["error"] = self.error
            
        if self.metadata:
            result["metadata"] = {
                "domain": self.metadata.domain,
                "path": self.metadata.path,
                "protocol": self.metadata.protocol,
            }
            
            if self.metadata.query_params:
                result["metadata"]["query_params"] = self.metadata.query_params
                
            if self.metadata.fragment:
                result["metadata"]["fragment"] = self.metadata.fragment
                
            if self.metadata.port:
                result["metadata"]["port"] = self.metadata.port
                
        if self.content:
            result["content"] = {}
            
            if self.content.title:
                result["content"]["title"] = self.content.title
                
            if self.content.description:
                result["content"]["description"] = self.content.description
                
            if self.content.keywords:
                result["content"]["keywords"] = self.content.keywords
                
            if self.content.text_length:
                result["content"]["text_length"] = self.content.text_length
                
            if self.content.links_count:
                result["content"]["links_count"] = self.content.links_count
                
            if self.content.images_count:
                result["content"]["images_count"] = self.content.images_count
                
            if self.content.summary:
                result["content"]["summary"] = self.content.summary
                
        return result


@dataclass
class BatchAnalysisResult:
    """
    Result of batch URL analysis.
    
    This class represents the result of analyzing multiple URLs.
    
    Args:
        results: List of individual URL analysis results
        total_urls: Total number of URLs analyzed
        successful_urls: Number of URLs successfully analyzed
        failed_urls: Number of URLs that failed analysis
        execution_time: Time taken to analyze all URLs in seconds
    """
    results: List[AnalysisResult]
    total_urls: int
    successful_urls: int
    failed_urls: int
    execution_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the batch result to a dictionary."""
        return {
            "total_urls": self.total_urls,
            "successful_urls": self.successful_urls,
            "failed_urls": self.failed_urls,
            "execution_time": self.execution_time,
            "results": [result.to_dict() for result in self.results]
        }


@dataclass
class APIResponse:
    """
    API response model.
    
    This class represents a response from the URL Analyzer API.
    
    Args:
        success: Whether the request was successful
        data: Response data
        error: Error message if the request failed
        version: API version
        headers: HTTP headers to include in the response
        status_code: HTTP status code for the response
    """
    success: bool
    data: Optional[Union[AnalysisResult, BatchAnalysisResult, Dict[str, Any]]] = None
    error: Optional[str] = None
    version: APIVersion = APIVersion.V1
    headers: Optional[Dict[str, str]] = None
    status_code: int = 200
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        result = {
            "success": self.success,
            "version": str(self.version),
        }
        
        if self.data:
            if hasattr(self.data, "to_dict"):
                result["data"] = self.data.to_dict()
            else:
                result["data"] = self.data
                
        if self.error:
            result["error"] = self.error
            
        return result


@dataclass
class APIKeyMetadata:
    """
    API key metadata model.
    
    This class represents metadata about an API key.
    
    Args:
        user_id: Identifier for the user or application
        role: Role for the API key (basic, premium, unlimited)
        permissions: List of specific permissions for the API key
        created_at: Timestamp when the API key was created
    """
    user_id: str
    role: str
    permissions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary."""
        return {
            "user_id": self.user_id,
            "role": self.role,
            "permissions": self.permissions,
            "created_at": self.created_at
        }


@dataclass
class RateLimitInfo:
    """
    Rate limit information model.
    
    This class represents information about rate limits.
    
    Args:
        limit: Maximum number of requests allowed in the time window
        remaining: Number of requests remaining in the current time window
        reset: Time in seconds until the rate limit resets
    """
    limit: Union[int, str]
    remaining: Union[int, str]
    reset: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the rate limit info to a dictionary."""
        return {
            "limit": self.limit,
            "remaining": self.remaining,
            "reset": self.reset
        }
    
    def to_headers(self) -> Dict[str, str]:
        """Convert the rate limit info to HTTP headers."""
        return {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(self.reset)
        }