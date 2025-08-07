"""
Plugin Marketplace Module

This module implements a marketplace for plugins, allowing users to discover,
install, update, and manage plugins for the URL Analyzer.
"""

import os
import json
import logging
import tempfile
import shutil
import zipfile
import requests
import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime

# Try to import semver for semantic versioning, but provide a fallback if not available
try:
    import semver
    SEMVER_AVAILABLE = True
except ImportError:
    SEMVER_AVAILABLE = False

from url_analyzer.plugins.domain import Plugin, PluginMetadata, PluginType, PluginStatus, PluginDependency
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.rate_limiter import rate_limited

# Create logger
logger = get_logger(__name__)

# Constants
DEFAULT_MARKETPLACE_URL = "https://plugins.urlanalyzer.example.com"
MARKETPLACE_CONFIG_FILE = "marketplace_config.json"
PLUGIN_CACHE_DIR = "plugin_cache"


@dataclass
class PluginPackage:
    """Value object representing a plugin package in the marketplace."""
    
    metadata: PluginMetadata
    package_url: str
    download_count: int = 0
    rating: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    description_long: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    changelog: Optional[str] = None
    
    @property
    def id(self) -> str:
        """
        Get the plugin package ID.
        
        Returns:
            Plugin package ID (name-version)
        """
        return self.metadata.id
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginPackage':
        """
        Create a PluginPackage from a dictionary.
        
        Args:
            data: Dictionary containing plugin package data
            
        Returns:
            PluginPackage instance
        """
        # Create PluginDependency objects from dependency data
        dependencies = []
        for dep in data.get('dependencies', []):
            dependencies.append(PluginDependency(
                name=dep['name'],
                version_constraint=dep['version_constraint'],
                optional=dep.get('optional', False)
            ))
        
        # Create PluginMetadata object
        metadata = PluginMetadata(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            author=data['author'],
            plugin_type=PluginType[data['plugin_type']],
            dependencies=dependencies,
            homepage=data.get('homepage'),
            license=data.get('license'),
            min_app_version=data.get('min_app_version'),
            max_app_version=data.get('max_app_version'),
            tags=data.get('tags', [])
        )
        
        # Parse last_updated datetime
        last_updated = datetime.now()
        if 'last_updated' in data:
            try:
                last_updated = datetime.fromisoformat(data['last_updated'])
            except (ValueError, TypeError):
                pass
        
        # Create PluginPackage object
        return cls(
            metadata=metadata,
            package_url=data['package_url'],
            download_count=data.get('download_count', 0),
            rating=data.get('rating', 0.0),
            last_updated=last_updated,
            description_long=data.get('description_long'),
            screenshots=data.get('screenshots', []),
            documentation_url=data.get('documentation_url'),
            changelog=data.get('changelog')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the PluginPackage to a dictionary.
        
        Returns:
            Dictionary representation of the PluginPackage
        """
        # Convert dependencies to dictionaries
        dependencies = []
        for dep in self.metadata.dependencies:
            dependencies.append({
                'name': dep.name,
                'version_constraint': dep.version_constraint,
                'optional': dep.optional
            })
        
        # Create the dictionary
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'description': self.metadata.description,
            'author': self.metadata.author,
            'plugin_type': self.metadata.plugin_type.name,
            'dependencies': dependencies,
            'homepage': self.metadata.homepage,
            'license': self.metadata.license,
            'min_app_version': self.metadata.min_app_version,
            'max_app_version': self.metadata.max_app_version,
            'tags': self.metadata.tags,
            'package_url': self.package_url,
            'download_count': self.download_count,
            'rating': self.rating,
            'last_updated': self.last_updated.isoformat(),
            'description_long': self.description_long,
            'screenshots': self.screenshots,
            'documentation_url': self.documentation_url,
            'changelog': self.changelog
        }


class PluginMarketplace:
    """
    Marketplace for discovering, installing, and managing plugins.
    
    The marketplace allows users to browse available plugins, install them,
    update them, and manage their dependencies.
    """
    
    def __init__(self, registry: PluginRegistry, marketplace_url: Optional[str] = None):
        """
        Initialize the plugin marketplace.
        
        Args:
            registry: Plugin registry to use for managing installed plugins
            marketplace_url: URL of the plugin marketplace API (optional)
        """
        self._registry = registry
        self._marketplace_url = marketplace_url or DEFAULT_MARKETPLACE_URL
        self._available_plugins: Dict[str, PluginPackage] = {}
        self._installed_plugins: Dict[str, Plugin] = {}
        self._plugin_cache_dir = os.path.join(os.path.dirname(__file__), PLUGIN_CACHE_DIR)
        
        # Create plugin cache directory if it doesn't exist
        os.makedirs(self._plugin_cache_dir, exist_ok=True)
        
        # Load marketplace configuration
        self._load_config()
        
        logger.info(f"Plugin marketplace initialized with URL: {self._marketplace_url}")
    
    def _load_config(self) -> None:
        """
        Load marketplace configuration from file.
        """
        config_path = os.path.join(os.path.dirname(__file__), MARKETPLACE_CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Update marketplace URL if specified in config
                if 'marketplace_url' in config:
                    self._marketplace_url = config['marketplace_url']
                
                logger.info(f"Loaded marketplace configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading marketplace configuration: {e}")
    
    def _save_config(self) -> None:
        """
        Save marketplace configuration to file.
        """
        config_path = os.path.join(os.path.dirname(__file__), MARKETPLACE_CONFIG_FILE)
        try:
            config = {
                'marketplace_url': self._marketplace_url
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Saved marketplace configuration to {config_path}")
        except Exception as e:
            logger.error(f"Error saving marketplace configuration: {e}")
            
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2, 0 if version1 == version2, 1 if version1 > version2
        """
        if SEMVER_AVAILABLE:
            try:
                return semver.compare(version1, version2)
            except Exception:
                # If there's any error in semver comparison, fall back to simple comparison
                pass
        
        # Simple version comparison using regex
        def parse_version(v):
            # Extract major, minor, patch versions
            match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?', v)
            if not match:
                return (0, 0, 0)
            
            major = int(match.group(1) or 0)
            minor = int(match.group(2) or 0)
            patch = int(match.group(3) or 0)
            
            return (major, minor, patch)
        
        v1_parts = parse_version(version1)
        v2_parts = parse_version(version2)
        
        for i in range(3):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    
    @rate_limited(endpoint_type='api', tokens=1, timeout=15.0)
    def refresh_available_plugins(self) -> bool:
        """
        Refresh the list of available plugins from the marketplace.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch the list of available plugins from the marketplace API
            response = requests.get(f"{self._marketplace_url}/api/plugins")
            response.raise_for_status()
            
            # Parse the response
            plugins_data = response.json()
            
            # Clear the current list of available plugins
            self._available_plugins.clear()
            
            # Add each plugin to the list
            for plugin_data in plugins_data:
                try:
                    plugin_package = PluginPackage.from_dict(plugin_data)
                    self._available_plugins[plugin_package.id] = plugin_package
                except Exception as e:
                    logger.error(f"Error parsing plugin data: {e}")
            
            logger.info(f"Refreshed available plugins: {len(self._available_plugins)} plugins found")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing available plugins: {e}")
            return False
    
    def get_available_plugins(self) -> List[PluginPackage]:
        """
        Get the list of available plugins.
        
        Returns:
            List of available plugin packages
        """
        return list(self._available_plugins.values())
    
    def get_available_plugin(self, plugin_id: str) -> Optional[PluginPackage]:
        """
        Get an available plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            PluginPackage instance or None if not found
        """
        return self._available_plugins.get(plugin_id)
    
    def search_plugins(self, query: str, tags: Optional[List[str]] = None, 
                      plugin_type: Optional[PluginType] = None) -> List[PluginPackage]:
        """
        Search for plugins matching the given criteria.
        
        Args:
            query: Search query string
            tags: List of tags to filter by (optional)
            plugin_type: Plugin type to filter by (optional)
            
        Returns:
            List of matching plugin packages
        """
        results = []
        
        # Convert query to lowercase for case-insensitive search
        query = query.lower()
        
        for plugin in self._available_plugins.values():
            # Check if the plugin matches the query
            name_match = query in plugin.metadata.name.lower()
            desc_match = query in plugin.metadata.description.lower()
            author_match = query in plugin.metadata.author.lower()
            
            # Check if the plugin matches the tags
            tags_match = True
            if tags:
                tags_match = all(tag in plugin.metadata.tags for tag in tags)
            
            # Check if the plugin matches the type
            type_match = True
            if plugin_type:
                type_match = plugin.metadata.plugin_type == plugin_type
            
            # Add the plugin to the results if it matches all criteria
            if (name_match or desc_match or author_match) and tags_match and type_match:
                results.append(plugin)
        
        return results
    
    @rate_limited(endpoint_type='web', tokens=1, timeout=30.0)
    def install_plugin(self, plugin_id: str) -> bool:
        """
        Install a plugin from the marketplace.
        
        Args:
            plugin_id: ID of the plugin to install
            
        Returns:
            True if successful, False otherwise
        """
        # Check if the plugin is available
        plugin_package = self._available_plugins.get(plugin_id)
        if not plugin_package:
            logger.error(f"Plugin not found in marketplace: {plugin_id}")
            return False
        
        try:
            # Download the plugin package
            response = requests.get(plugin_package.package_url, stream=True)
            response.raise_for_status()
            
            # Create a temporary file to store the downloaded package
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                # Write the package data to the temporary file
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                
                temp_file_path = temp_file.name
            
            # Extract the plugin package
            plugin_dir = os.path.join(self._plugin_cache_dir, plugin_package.metadata.name)
            os.makedirs(plugin_dir, exist_ok=True)
            
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(plugin_dir)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Load the plugin
            plugin = self._load_plugin_from_directory(plugin_dir)
            if not plugin:
                logger.error(f"Failed to load plugin: {plugin_id}")
                return False
            
            # Register the plugin
            self._registry.register_plugin(plugin)
            self._installed_plugins[plugin_id] = plugin
            
            logger.info(f"Installed plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error installing plugin {plugin_id}: {e}")
            return False
    
    def _load_plugin_from_directory(self, plugin_dir: str) -> Optional[Plugin]:
        """
        Load a plugin from a directory.
        
        Args:
            plugin_dir: Directory containing the plugin
            
        Returns:
            Plugin instance or None if loading failed
        """
        try:
            # Look for the plugin metadata file
            metadata_path = os.path.join(plugin_dir, 'plugin.json')
            if not os.path.exists(metadata_path):
                logger.error(f"Plugin metadata file not found: {metadata_path}")
                return None
            
            # Load the plugin metadata
            with open(metadata_path, 'r') as f:
                metadata_dict = json.load(f)
            
            # Create PluginDependency objects from dependency data
            dependencies = []
            for dep in metadata_dict.get('dependencies', []):
                dependencies.append(PluginDependency(
                    name=dep['name'],
                    version_constraint=dep['version_constraint'],
                    optional=dep.get('optional', False)
                ))
            
            # Create PluginMetadata object
            metadata = PluginMetadata(
                name=metadata_dict['name'],
                version=metadata_dict['version'],
                description=metadata_dict['description'],
                author=metadata_dict['author'],
                plugin_type=PluginType[metadata_dict['plugin_type']],
                dependencies=dependencies,
                homepage=metadata_dict.get('homepage'),
                license=metadata_dict.get('license'),
                min_app_version=metadata_dict.get('min_app_version'),
                max_app_version=metadata_dict.get('max_app_version'),
                tags=metadata_dict.get('tags', [])
            )
            
            # Look for the plugin module file
            module_path = os.path.join(plugin_dir, 'plugin.py')
            if not os.path.exists(module_path):
                logger.error(f"Plugin module file not found: {module_path}")
                return None
            
            # Create the Plugin object
            plugin = Plugin.create(metadata, module_path)
            
            # Activate the plugin
            if not plugin.activate():
                logger.error(f"Failed to activate plugin: {metadata.name}")
                return None
            
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin from directory {plugin_dir}: {e}")
            return None
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin.
        
        Args:
            plugin_id: ID of the plugin to uninstall
            
        Returns:
            True if successful, False otherwise
        """
        # Check if the plugin is installed
        plugin = self._installed_plugins.get(plugin_id)
        if not plugin:
            logger.error(f"Plugin not installed: {plugin_id}")
            return False
        
        try:
            # Unregister the plugin
            self._registry.unregister_plugin(plugin.metadata.name)
            
            # Remove the plugin from the installed plugins list
            del self._installed_plugins[plugin_id]
            
            # Remove the plugin directory
            plugin_dir = os.path.dirname(plugin.module_path)
            shutil.rmtree(plugin_dir, ignore_errors=True)
            
            logger.info(f"Uninstalled plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
            return False
    
    def update_plugin(self, plugin_id: str) -> bool:
        """
        Update a plugin to the latest version.
        
        Args:
            plugin_id: ID of the plugin to update
            
        Returns:
            True if successful, False otherwise
        """
        # Check if the plugin is installed
        plugin = self._installed_plugins.get(plugin_id)
        if not plugin:
            logger.error(f"Plugin not installed: {plugin_id}")
            return False
        
        # Get the plugin name (without version)
        plugin_name = plugin.metadata.name
        
        # Find the latest version of the plugin in the marketplace
        latest_version = None
        latest_plugin_id = None
        
        for available_id, available_plugin in self._available_plugins.items():
            if available_plugin.metadata.name == plugin_name:
                if latest_version is None or self._compare_versions(available_plugin.metadata.version, latest_version) > 0:
                    latest_version = available_plugin.metadata.version
                    latest_plugin_id = available_id
        
        if not latest_plugin_id:
            logger.error(f"Plugin not found in marketplace: {plugin_name}")
            return False
        
        # Check if the installed version is already the latest
        if self._compare_versions(plugin.metadata.version, latest_version) >= 0:
            logger.info(f"Plugin {plugin_name} is already at the latest version: {plugin.metadata.version}")
            return True
        
        # Uninstall the current version
        if not self.uninstall_plugin(plugin_id):
            logger.error(f"Failed to uninstall current version of plugin: {plugin_id}")
            return False
        
        # Install the latest version
        if not self.install_plugin(latest_plugin_id):
            logger.error(f"Failed to install latest version of plugin: {latest_plugin_id}")
            return False
        
        logger.info(f"Updated plugin {plugin_name} from version {plugin.metadata.version} to {latest_version}")
        return True
    
    @rate_limited(endpoint_type='web', tokens=1, timeout=20.0)
    def get_plugin_documentation(self, plugin_id: str) -> Optional[str]:
        """
        Get the documentation for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Documentation string or None if not available
        """
        # Check if the plugin is available
        plugin_package = self._available_plugins.get(plugin_id)
        if not plugin_package:
            logger.error(f"Plugin not found in marketplace: {plugin_id}")
            return None
        
        # Check if the plugin has a documentation URL
        if not plugin_package.documentation_url:
            logger.error(f"Plugin does not have documentation URL: {plugin_id}")
            return None
        
        try:
            # Fetch the documentation
            response = requests.get(plugin_package.documentation_url)
            response.raise_for_status()
            
            # Return the documentation content
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching documentation for plugin {plugin_id}: {e}")
            return None
    
    def get_plugin_changelog(self, plugin_id: str) -> Optional[str]:
        """
        Get the changelog for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Changelog string or None if not available
        """
        # Check if the plugin is available
        plugin_package = self._available_plugins.get(plugin_id)
        if not plugin_package:
            logger.error(f"Plugin not found in marketplace: {plugin_id}")
            return None
        
        # Return the changelog
        return plugin_package.changelog
    
    def check_for_updates(self) -> Dict[str, Tuple[str, str]]:
        """
        Check for updates for installed plugins.
        
        Returns:
            Dictionary mapping plugin IDs to tuples of (current_version, latest_version)
            for plugins that have updates available
        """
        updates = {}
        
        for plugin_id, plugin in self._installed_plugins.items():
            plugin_name = plugin.metadata.name
            current_version = plugin.metadata.version
            
            # Find the latest version of the plugin in the marketplace
            latest_version = None
            
            for available_plugin in self._available_plugins.values():
                if available_plugin.metadata.name == plugin_name:
                    if latest_version is None or self._compare_versions(available_plugin.metadata.version, latest_version) > 0:
                        latest_version = available_plugin.metadata.version
            
            # If a newer version is available, add it to the updates dictionary
            if latest_version and self._compare_versions(latest_version, current_version) > 0:
                updates[plugin_id] = (current_version, latest_version)
        
        return updates
    
    def resolve_dependencies(self, plugin_id: str) -> Tuple[bool, List[str], List[str]]:
        """
        Resolve dependencies for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Tuple of (success, missing_dependencies, conflicting_dependencies)
        """
        # Check if the plugin is available
        plugin_package = self._available_plugins.get(plugin_id)
        if not plugin_package:
            logger.error(f"Plugin not found in marketplace: {plugin_id}")
            return False, [], []
        
        missing_dependencies = []
        conflicting_dependencies = []
        
        # Check each dependency
        for dependency in plugin_package.metadata.dependencies:
            dependency_name = dependency.name
            dependency_constraint = dependency.version_constraint
            
            # Find the dependency in installed plugins
            dependency_found = False
            dependency_satisfied = False
            
            for installed_plugin in self._installed_plugins.values():
                if installed_plugin.metadata.name == dependency_name:
                    dependency_found = True
                    if dependency.is_satisfied_by(installed_plugin.metadata.version):
                        dependency_satisfied = True
                        break
            
            # If the dependency is not found or not satisfied
            if not dependency_found:
                if not dependency.optional:
                    missing_dependencies.append(f"{dependency_name} {dependency_constraint}")
            elif not dependency_satisfied:
                conflicting_dependencies.append(f"{dependency_name} {dependency_constraint}")
        
        # Return the results
        success = len(missing_dependencies) == 0 and len(conflicting_dependencies) == 0
        return success, missing_dependencies, conflicting_dependencies
    
    def get_installed_plugins(self) -> List[Plugin]:
        """
        Get the list of installed plugins.
        
        Returns:
            List of installed plugins
        """
        return list(self._installed_plugins.values())
    
    def get_installed_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get an installed plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            Plugin instance or None if not found
        """
        return self._installed_plugins.get(plugin_id)
    
    def set_marketplace_url(self, url: str) -> None:
        """
        Set the URL of the plugin marketplace API.
        
        Args:
            url: URL of the plugin marketplace API
        """
        self._marketplace_url = url
        self._save_config()
        logger.info(f"Set marketplace URL to: {url}")
    
    def get_marketplace_url(self) -> str:
        """
        Get the URL of the plugin marketplace API.
        
        Returns:
            URL of the plugin marketplace API
        """
        return self._marketplace_url