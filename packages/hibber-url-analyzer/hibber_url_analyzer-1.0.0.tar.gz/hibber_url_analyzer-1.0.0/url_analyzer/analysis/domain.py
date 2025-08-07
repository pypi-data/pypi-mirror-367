"""
URL Analysis Domain Models

This module defines the domain models and value objects for the URL Analysis domain.
These models represent the core concepts in URL analysis and encapsulate domain logic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime


@dataclass(frozen=True)
class URLContent:
    """Value object representing the content of a URL."""
    
    url: str
    content_type: str
    status_code: int
    content: str
    headers: Dict[str, str]
    fetch_time: datetime
    size_bytes: int
    
    @property
    def is_success(self) -> bool:
        """
        Check if the fetch was successful.
        
        Returns:
            True if the status code is in the 2xx range, False otherwise
        """
        return 200 <= self.status_code < 300
    
    @property
    def is_html(self) -> bool:
        """
        Check if the content is HTML.
        
        Returns:
            True if the content type indicates HTML, False otherwise
        """
        return self.content_type.lower().startswith('text/html')
    
    @property
    def is_json(self) -> bool:
        """
        Check if the content is JSON.
        
        Returns:
            True if the content type indicates JSON, False otherwise
        """
        return self.content_type.lower().startswith('application/json')
    
    @property
    def is_text(self) -> bool:
        """
        Check if the content is text.
        
        Returns:
            True if the content type indicates text, False otherwise
        """
        return self.content_type.lower().startswith('text/')


@dataclass(frozen=True)
class ContentSummary:
    """Value object representing a summary of URL content."""
    
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    main_topics: List[str] = field(default_factory=list)
    sentiment_score: Optional[float] = None
    language: Optional[str] = None
    word_count: int = 0
    
    @property
    def has_title(self) -> bool:
        """
        Check if the summary has a title.
        
        Returns:
            True if the title is not None and not empty, False otherwise
        """
        return bool(self.title and self.title.strip())
    
    @property
    def has_description(self) -> bool:
        """
        Check if the summary has a description.
        
        Returns:
            True if the description is not None and not empty, False otherwise
        """
        return bool(self.description and self.description.strip())
    
    @property
    def sentiment(self) -> str:
        """
        Get the sentiment as a string.
        
        Returns:
            "Positive", "Neutral", or "Negative" based on the sentiment score,
            or "Unknown" if the sentiment score is None
        """
        if self.sentiment_score is None:
            return "Unknown"
        
        if self.sentiment_score > 0.1:
            return "Positive"
        elif self.sentiment_score < -0.1:
            return "Negative"
        else:
            return "Neutral"


@dataclass(frozen=True)
class FetchResult:
    """Value object representing the result of fetching a URL."""
    
    url: str
    success: bool
    status_code: Optional[int] = None
    content: Optional[URLContent] = None
    error_message: Optional[str] = None
    fetch_time: datetime = field(default_factory=datetime.now)
    
    @property
    def is_success(self) -> bool:
        """
        Check if the fetch was successful.
        
        Returns:
            True if the fetch was successful, False otherwise
        """
        return self.success and self.content is not None
    
    @property
    def is_error(self) -> bool:
        """
        Check if the fetch resulted in an error.
        
        Returns:
            True if the fetch resulted in an error, False otherwise
        """
        return not self.success or self.error_message is not None
    
    @property
    def is_redirect(self) -> bool:
        """
        Check if the fetch resulted in a redirect.
        
        Returns:
            True if the status code indicates a redirect, False otherwise
        """
        return self.status_code is not None and 300 <= self.status_code < 400


@dataclass(frozen=True)
class AnalysisResult:
    """Value object representing the result of analyzing a URL."""
    
    url: str
    fetch_result: FetchResult
    content_summary: Optional[ContentSummary] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_time: datetime = field(default_factory=datetime.now)
    
    @property
    def is_success(self) -> bool:
        """
        Check if the analysis was successful.
        
        Returns:
            True if the fetch was successful and a content summary was generated,
            False otherwise
        """
        return self.fetch_result.is_success and self.content_summary is not None
    
    @property
    def has_metadata(self) -> bool:
        """
        Check if the analysis result has metadata.
        
        Returns:
            True if the metadata dictionary is not empty, False otherwise
        """
        return bool(self.metadata)
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the metadata dictionary.
        
        Args:
            key: Key to look up
            default: Default value to return if the key is not found
            
        Returns:
            Value associated with the key, or the default value if the key is not found
        """
        return self.metadata.get(key, default)


@dataclass(frozen=True)
class AnalysisOptions:
    """Value object representing options for URL analysis."""
    
    fetch_timeout: int = 10
    follow_redirects: bool = True
    max_redirects: int = 5
    user_agent: str = "URL Analyzer"
    extract_metadata: bool = True
    extract_summary: bool = True
    extract_sentiment: bool = False
    extract_keywords: bool = False
    extract_language: bool = True
    max_content_size: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def with_timeout(self, timeout: int) -> 'AnalysisOptions':
        """
        Create a new options object with a different timeout.
        
        Args:
            timeout: New timeout value
            
        Returns:
            New AnalysisOptions instance with the updated timeout
        """
        return AnalysisOptions(
            fetch_timeout=timeout,
            follow_redirects=self.follow_redirects,
            max_redirects=self.max_redirects,
            user_agent=self.user_agent,
            extract_metadata=self.extract_metadata,
            extract_summary=self.extract_summary,
            extract_sentiment=self.extract_sentiment,
            extract_keywords=self.extract_keywords,
            extract_language=self.extract_language,
            max_content_size=self.max_content_size,
            headers=self.headers
        )
    
    def with_user_agent(self, user_agent: str) -> 'AnalysisOptions':
        """
        Create a new options object with a different user agent.
        
        Args:
            user_agent: New user agent value
            
        Returns:
            New AnalysisOptions instance with the updated user agent
        """
        return AnalysisOptions(
            fetch_timeout=self.fetch_timeout,
            follow_redirects=self.follow_redirects,
            max_redirects=self.max_redirects,
            user_agent=user_agent,
            extract_metadata=self.extract_metadata,
            extract_summary=self.extract_summary,
            extract_sentiment=self.extract_sentiment,
            extract_keywords=self.extract_keywords,
            extract_language=self.extract_language,
            max_content_size=self.max_content_size,
            headers=self.headers
        )
    
    def with_header(self, name: str, value: str) -> 'AnalysisOptions':
        """
        Create a new options object with an additional header.
        
        Args:
            name: Header name
            value: Header value
            
        Returns:
            New AnalysisOptions instance with the added header
        """
        headers = dict(self.headers)
        headers[name] = value
        return AnalysisOptions(
            fetch_timeout=self.fetch_timeout,
            follow_redirects=self.follow_redirects,
            max_redirects=self.max_redirects,
            user_agent=self.user_agent,
            extract_metadata=self.extract_metadata,
            extract_summary=self.extract_summary,
            extract_sentiment=self.extract_sentiment,
            extract_keywords=self.extract_keywords,
            extract_language=self.extract_language,
            max_content_size=self.max_content_size,
            headers=headers
        )