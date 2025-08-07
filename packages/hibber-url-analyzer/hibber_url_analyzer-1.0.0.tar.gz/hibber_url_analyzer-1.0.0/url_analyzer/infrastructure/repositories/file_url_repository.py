"""
File-based URL Repository

This module provides a file-based implementation of the URLRepository interface.
It stores URLs in a JSON file and provides methods for retrieving and manipulating
URL entities.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from url_analyzer.domain.entities import URL, URLCategory, SensitivityLevel
from url_analyzer.domain.value_objects import DomainName
from url_analyzer.application.interfaces import URLRepository


class FileURLRepository(URLRepository):
    """
    File-based implementation of the URLRepository interface.
    
    This class stores URLs in a JSON file and provides methods for
    retrieving and manipulating URL entities.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the repository with a file path.
        
        Args:
            file_path: Path to the JSON file for storing URLs
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure that the repository file exists."""
        if not os.path.exists(self.file_path):
            # Create the directory if it doesn't exist
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Create an empty repository file
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
    
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load data from the repository file.
        
        Returns:
            Dictionary of URL data keyed by URL string
        """
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or invalid, return an empty dictionary
            return {}
    
    def _save_data(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Save data to the repository file.
        
        Args:
            data: Dictionary of URL data keyed by URL string
        """
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _url_to_dict(self, url: URL) -> Dict[str, Any]:
        """
        Convert a URL entity to a dictionary for storage.
        
        Args:
            url: URL entity to convert
            
        Returns:
            Dictionary representation of the URL entity
        """
        return {
            'url': url.url,
            'base_domain': url.base_domain,
            'category': url.category.name if isinstance(url.category, URLCategory) else url.category,
            'sensitivity_level': url.sensitivity_level.name if isinstance(url.sensitivity_level, SensitivityLevel) else url.sensitivity_level,
            'is_malicious': url.is_malicious,
            'metadata': url.metadata,
            'created_at': url.created_at.isoformat() if url.created_at else None,
            'last_analyzed': url.last_analyzed.isoformat() if url.last_analyzed else None
        }
    
    def _dict_to_url(self, data: Dict[str, Any]) -> URL:
        """
        Convert a dictionary to a URL entity.
        
        Args:
            data: Dictionary representation of a URL entity
            
        Returns:
            URL entity
        """
        # Convert string category to enum if needed
        if isinstance(data.get('category'), str):
            try:
                category = URLCategory[data['category']]
            except (KeyError, TypeError):
                category = URLCategory.UNKNOWN
        else:
            category = data.get('category', URLCategory.UNKNOWN)
        
        # Convert string sensitivity level to enum if needed
        if isinstance(data.get('sensitivity_level'), str):
            try:
                sensitivity_level = SensitivityLevel[data['sensitivity_level']]
            except (KeyError, TypeError):
                sensitivity_level = SensitivityLevel.LOW
        else:
            sensitivity_level = data.get('sensitivity_level', SensitivityLevel.LOW)
        
        # Parse datetime strings
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                created_at = datetime.now()
        
        last_analyzed = None
        if data.get('last_analyzed'):
            try:
                last_analyzed = datetime.fromisoformat(data['last_analyzed'])
            except (ValueError, TypeError):
                last_analyzed = None
        
        return URL(
            url=data['url'],
            base_domain=data.get('base_domain'),
            category=category,
            sensitivity_level=sensitivity_level,
            is_malicious=data.get('is_malicious', False),
            metadata=data.get('metadata', {}),
            created_at=created_at or datetime.now(),
            last_analyzed=last_analyzed
        )
    
    def save(self, url: URL) -> None:
        """
        Save a URL entity.
        
        Args:
            url: The URL entity to save
        """
        data = self._load_data()
        data[url.url] = self._url_to_dict(url)
        self._save_data(data)
    
    def get_by_url(self, url_string: str) -> Optional[URL]:
        """
        Get a URL entity by its URL string.
        
        Args:
            url_string: The URL string to look up
            
        Returns:
            The URL entity if found, None otherwise
        """
        data = self._load_data()
        url_data = data.get(url_string)
        
        if url_data:
            return self._dict_to_url(url_data)
        
        return None
    
    def get_all(self) -> List[URL]:
        """
        Get all URL entities.
        
        Returns:
            A list of all URL entities
        """
        data = self._load_data()
        return [self._dict_to_url(url_data) for url_data in data.values()]
    
    def get_by_category(self, category: str) -> List[URL]:
        """
        Get URL entities by category.
        
        Args:
            category: The category to filter by
            
        Returns:
            A list of URL entities in the specified category
        """
        data = self._load_data()
        return [
            self._dict_to_url(url_data)
            for url_data in data.values()
            if url_data.get('category') == category
        ]
    
    def get_by_domain(self, domain: str) -> List[URL]:
        """
        Get URL entities by domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            A list of URL entities with the specified domain
        """
        data = self._load_data()
        return [
            self._dict_to_url(url_data)
            for url_data in data.values()
            if url_data.get('base_domain') == domain
        ]
    
    def delete(self, url_string: str) -> bool:
        """
        Delete a URL entity.
        
        Args:
            url_string: The URL string to delete
            
        Returns:
            True if the URL was deleted, False otherwise
        """
        data = self._load_data()
        
        if url_string in data:
            del data[url_string]
            self._save_data(data)
            return True
        
        return False