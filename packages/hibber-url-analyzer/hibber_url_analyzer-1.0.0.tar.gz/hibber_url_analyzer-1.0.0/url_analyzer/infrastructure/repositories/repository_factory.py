"""
Repository Factory

This module provides factory classes for creating repository instances.
It simplifies the creation and configuration of different repository implementations.
"""

from typing import Dict, Any, Optional, Type, Union
import os
import json

from url_analyzer.application.interfaces import URLRepository
from url_analyzer.infrastructure.repositories.file_url_repository import FileURLRepository
from url_analyzer.infrastructure.repositories.database_url_repository import DatabaseURLRepository
from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


class RepositoryFactory:
    """
    Factory for creating repository instances.
    
    This factory provides methods for creating different types of repositories
    with appropriate configuration.
    """
    
    @staticmethod
    def create_url_repository(
        repository_type: str = "file",
        config: Optional[Dict[str, Any]] = None
    ) -> URLRepository:
        """
        Create a URL repository instance.
        
        Args:
            repository_type: Type of repository to create (file, database)
            config: Configuration for the repository
            
        Returns:
            URLRepository instance
            
        Raises:
            ValueError: If the repository type is not supported
        """
        if config is None:
            config = {}
        
        if repository_type.lower() == "file":
            file_path = config.get("file_path", "urls.json")
            return FileURLRepository(file_path)
        
        elif repository_type.lower() == "database":
            db_type = config.get("db_type", "sqlite")
            connection_string = config.get("connection_string")
            table_name = config.get("table_name", "urls")
            version_table_name = config.get("version_table_name", "url_versions")
            archive_table_name = config.get("archive_table_name", "url_archives")
            compression = config.get("compression", False)
            compression_level = config.get("compression_level", 6)
            
            return DatabaseURLRepository(
                connection_string=connection_string,
                db_type=db_type,
                table_name=table_name,
                version_table_name=version_table_name,
                archive_table_name=archive_table_name,
                compression=compression,
                compression_level=compression_level
            )
        
        else:
            raise ValueError(f"Unsupported repository type: {repository_type}")


class RepositoryManager:
    """
    Manager for repository instances.
    
    This class manages the lifecycle of repository instances and provides
    a central point for accessing repositories.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the repository manager.
        
        Args:
            config_path: Path to the repository configuration file
        """
        self.repositories = {}
        self.config = {}
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load repository configuration: {str(e)}")
    
    def get_url_repository(
        self,
        repository_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> URLRepository:
        """
        Get a URL repository instance.
        
        If a repository of the specified type already exists, it will be returned.
        Otherwise, a new repository will be created.
        
        Args:
            repository_type: Type of repository to get (file, database)
            config: Configuration for the repository
            
        Returns:
            URLRepository instance
        """
        # Use configuration from file if not specified
        if repository_type is None:
            repository_type = self.config.get("url_repository", {}).get("type", "file")
        
        if config is None:
            config = self.config.get("url_repository", {}).get("config", {})
        
        # Check if repository already exists
        repo_key = f"url_{repository_type}"
        if repo_key in self.repositories:
            return self.repositories[repo_key]
        
        # Create new repository
        repository = RepositoryFactory.create_url_repository(repository_type, config)
        self.repositories[repo_key] = repository
        
        return repository
    
    def close_all(self):
        """Close all repositories."""
        for repo_key, repository in self.repositories.items():
            try:
                if hasattr(repository, 'close'):
                    repository.close()
            except Exception as e:
                logger.error(f"Failed to close repository {repo_key}: {str(e)}")
        
        self.repositories = {}


# Create a global repository manager instance
repository_manager = RepositoryManager()