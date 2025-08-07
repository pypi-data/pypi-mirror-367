"""
Application Layer Interfaces

This module defines interfaces for infrastructure services used by the application layer.
These interfaces follow the Dependency Inversion Principle, allowing the application layer
to depend on abstractions rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple, BinaryIO

from url_analyzer.domain.entities import URL, URLAnalysisResult, BatchAnalysisResult
from url_analyzer.domain.value_objects import URLClassificationRule


class URLRepository(ABC):
    """
    Interface for URL storage and retrieval.
    
    This interface defines methods for storing and retrieving URL entities.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def save(self, url: URL) -> None:
        """
        Save a URL entity.
        
        Args:
            url: The URL entity to save
        """
        pass
    
    @abstractmethod
    def get_by_url(self, url_string: str) -> Optional[URL]:
        """
        Get a URL entity by its URL string.
        
        Args:
            url_string: The URL string to look up
            
        Returns:
            The URL entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[URL]:
        """
        Get all URL entities.
        
        Returns:
            A list of all URL entities
        """
        pass
    
    @abstractmethod
    def get_by_category(self, category: str) -> List[URL]:
        """
        Get URL entities by category.
        
        Args:
            category: The category to filter by
            
        Returns:
            A list of URL entities in the specified category
        """
        pass
    
    @abstractmethod
    def get_by_domain(self, domain: str) -> List[URL]:
        """
        Get URL entities by domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            A list of URL entities with the specified domain
        """
        pass
    
    @abstractmethod
    def delete(self, url_string: str) -> bool:
        """
        Delete a URL entity.
        
        Args:
            url_string: The URL string to delete
            
        Returns:
            True if the URL was deleted, False otherwise
        """
        pass


class URLClassificationService(ABC):
    """
    Interface for URL classification.
    
    This interface defines methods for classifying URLs based on patterns and rules.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def classify(self, url: str) -> Tuple[str, bool]:
        """
        Classify a URL.
        
        Args:
            url: The URL to classify
            
        Returns:
            A tuple of (category, is_sensitive)
        """
        pass
    
    @abstractmethod
    def get_rules(self) -> List[URLClassificationRule]:
        """
        Get all classification rules.
        
        Returns:
            A list of all classification rules
        """
        pass
    
    @abstractmethod
    def add_rule(self, rule: URLClassificationRule) -> None:
        """
        Add a classification rule.
        
        Args:
            rule: The rule to add
        """
        pass
    
    @abstractmethod
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a classification rule.
        
        Args:
            rule_name: The name of the rule to remove
            
        Returns:
            True if the rule was removed, False otherwise
        """
        pass


class URLContentAnalysisService(ABC):
    """
    Interface for URL content analysis.
    
    This interface defines methods for analyzing URL content.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def analyze_content(self, url: str) -> Dict[str, Any]:
        """
        Analyze the content of a URL.
        
        Args:
            url: The URL to analyze
            
        Returns:
            A dictionary of analysis results
        """
        pass
    
    @abstractmethod
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get metadata for a URL.
        
        Args:
            url: The URL to get metadata for
            
        Returns:
            A dictionary of metadata
        """
        pass
    
    @abstractmethod
    def extract_links(self, url: str) -> List[str]:
        """
        Extract links from a URL.
        
        Args:
            url: The URL to extract links from
            
        Returns:
            A list of links found in the URL content
        """
        pass


class ReportingService(ABC):
    """
    Interface for generating reports.
    
    This interface defines methods for generating reports from analysis results.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def generate_html_report(self, results: BatchAnalysisResult, output_path: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            results: The batch analysis results to include in the report
            output_path: The path to write the report to
            
        Returns:
            The path to the generated report
        """
        pass
    
    @abstractmethod
    def generate_csv_report(self, results: BatchAnalysisResult, output_path: str) -> str:
        """
        Generate a CSV report.
        
        Args:
            results: The batch analysis results to include in the report
            output_path: The path to write the report to
            
        Returns:
            The path to the generated report
        """
        pass
    
    @abstractmethod
    def generate_json_report(self, results: BatchAnalysisResult, output_path: str) -> str:
        """
        Generate a JSON report.
        
        Args:
            results: The batch analysis results to include in the report
            output_path: The path to write the report to
            
        Returns:
            The path to the generated report
        """
        pass
    
    @abstractmethod
    def generate_pdf_report(self, results: BatchAnalysisResult, output_path: str) -> str:
        """
        Generate a PDF report.
        
        Args:
            results: The batch analysis results to include in the report
            output_path: The path to write the report to
            
        Returns:
            The path to the generated report
        """
        pass


class CacheService(ABC):
    """
    Interface for caching URL analysis results.
    
    This interface defines methods for caching and retrieving URL analysis results.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached results for a URL.
        
        Args:
            url: The URL to get cached results for
            
        Returns:
            The cached results if found, None otherwise
        """
        pass
    
    @abstractmethod
    def set(self, url: str, results: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Cache results for a URL.
        
        Args:
            url: The URL to cache results for
            results: The results to cache
            ttl: Time to live in seconds (optional)
        """
        pass
    
    @abstractmethod
    def delete(self, url: str) -> bool:
        """
        Delete cached results for a URL.
        
        Args:
            url: The URL to delete cached results for
            
        Returns:
            True if the cached results were deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached results."""
        pass
    
    @abstractmethod
    def get_size(self) -> int:
        """
        Get the size of the cache.
        
        Returns:
            The number of items in the cache
        """
        pass


class FileStorageService(ABC):
    """
    Interface for file storage.
    
    This interface defines methods for storing and retrieving files.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def save(self, file_path: str, content: str) -> bool:
        """
        Save content to a file.
        
        Args:
            file_path: The path to save the file to
            content: The content to save
            
        Returns:
            True if the file was saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def save_binary(self, file_path: str, content: bytes) -> bool:
        """
        Save binary content to a file.
        
        Args:
            file_path: The path to save the file to
            content: The binary content to save
            
        Returns:
            True if the file was saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, file_path: str) -> Optional[str]:
        """
        Load content from a file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            The file content if found, None otherwise
        """
        pass
    
    @abstractmethod
    def load_binary(self, file_path: str) -> Optional[bytes]:
        """
        Load binary content from a file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            The binary file content if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: The path to the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: The path to check
            
        Returns:
            True if the file exists, False otherwise
        """
        pass


class LoggingService(ABC):
    """
    Interface for logging.
    
    This interface defines methods for logging messages.
    It is implemented by the infrastructure layer.
    """
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        pass