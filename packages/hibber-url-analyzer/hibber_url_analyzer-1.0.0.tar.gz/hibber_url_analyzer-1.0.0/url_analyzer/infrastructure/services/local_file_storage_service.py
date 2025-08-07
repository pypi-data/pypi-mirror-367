"""
Local File Storage Service

This module provides a local file system implementation of the FileStorageService interface.
It handles storing and retrieving files from the local file system.
"""

import os
from typing import Optional

from url_analyzer.application.interfaces import FileStorageService


class LocalFileStorageService(FileStorageService):
    """
    Local file system implementation of the FileStorageService interface.
    
    This class handles storing and retrieving files from the local file system.
    """
    
    def __init__(self, base_directory: str = None):
        """
        Initialize the file storage service.
        
        Args:
            base_directory: Base directory for file storage (optional)
        """
        self.base_directory = base_directory
    
    def _get_full_path(self, file_path: str) -> str:
        """
        Get the full path for a file.
        
        Args:
            file_path: Relative or absolute file path
            
        Returns:
            Full file path
        """
        if self.base_directory and not os.path.isabs(file_path):
            return os.path.join(self.base_directory, file_path)
        return file_path
    
    def _ensure_directory_exists(self, file_path: str) -> None:
        """
        Ensure that the directory for a file exists.
        
        Args:
            file_path: Path to the file
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def save(self, file_path: str, content: str) -> bool:
        """
        Save content to a file.
        
        Args:
            file_path: The path to save the file to
            content: The content to save
            
        Returns:
            True if the file was saved successfully, False otherwise
        """
        try:
            full_path = self._get_full_path(file_path)
            self._ensure_directory_exists(full_path)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception:
            return False
    
    def save_binary(self, file_path: str, content: bytes) -> bool:
        """
        Save binary content to a file.
        
        Args:
            file_path: The path to save the file to
            content: The binary content to save
            
        Returns:
            True if the file was saved successfully, False otherwise
        """
        try:
            full_path = self._get_full_path(file_path)
            self._ensure_directory_exists(full_path)
            
            with open(full_path, 'wb') as f:
                f.write(content)
            
            return True
        except Exception:
            return False
    
    def load(self, file_path: str) -> Optional[str]:
        """
        Load content from a file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            The file content if found, None otherwise
        """
        try:
            full_path = self._get_full_path(file_path)
            
            if not os.path.exists(full_path):
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def load_binary(self, file_path: str) -> Optional[bytes]:
        """
        Load binary content from a file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            The binary file content if found, None otherwise
        """
        try:
            full_path = self._get_full_path(file_path)
            
            if not os.path.exists(full_path):
                return None
            
            with open(full_path, 'rb') as f:
                return f.read()
        except Exception:
            return None
    
    def delete(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: The path to the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        try:
            full_path = self._get_full_path(file_path)
            
            if not os.path.exists(full_path):
                return False
            
            os.remove(full_path)
            return True
        except Exception:
            return False
    
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: The path to check
            
        Returns:
            True if the file exists, False otherwise
        """
        full_path = self._get_full_path(file_path)
        return os.path.exists(full_path) and os.path.isfile(full_path)