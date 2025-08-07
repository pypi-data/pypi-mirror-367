"""
Plugin Manager Module

This module provides a unified interface for managing plugins in the URL Analyzer system.
It integrates the plugin registry, marketplace, configuration UI, and documentation generation.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import importlib
import sys

from url_analyzer.plugins.domain import Plugin, PluginMetadata, PluginType, PluginStatus
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.plugins.marketplace import PluginMarketplace
from url_analyzer.plugins.config_ui import create_config_ui, run_config_ui
from url_analyzer.plugins.documentation import generate_plugin_documentation
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Constants
DEFAULT_PLUGIN_DIRS = ["plugins"]


class PluginManager:
    """
    Manager for plugins in the URL Analyzer system.
    
    This class provides a unified interface for discovering, loading, configuring,
    and managing plugins. It integrates the plugin registry, marketplace,
    configuration UI, and documentation generation.
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_dirs: List of directories to search for plugins (optional)
        """
        self._registry = PluginRegistry()
        self._marketplace = PluginMarketplace(self._registry)
        self._plugin_dirs = plugin_dirs or DEFAULT_PLUGIN_DIRS
        
        # Ensure plugin directories exist
        for plugin_dir in self._plugin_dirs:
            os.makedirs(plugin_dir, exist_ok=True)
        
        logger.info(f"Plugin manager initialized with plugin directories: {self._plugin_dirs}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover plugins in the plugin directories.
        
        Returns:
            List of discovered plugin module paths
        """
        plugin_paths = []
        
        # Search for plugins in each plugin directory
        for plugin_dir in self._plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
            
            # Walk through the directory and its subdirectories
            for root, dirs, files in os.walk(plugin_dir):
                # Look for plugin.py files
                if "plugin.py" in files:
                    plugin_path = os.path.join(root, "plugin.py")
                    plugin_paths.append(plugin_path)
                    logger.info(f"Discovered plugin: {plugin_path}")
        
        return plugin_paths
    
    def load_plugin(self, plugin_path: str) -> Optional[Plugin]:
        """
        Load a plugin from a module path.
        
        Args:
            plugin_path: Path to the plugin module
            
        Returns:
            Plugin instance or None if loading failed
        """
        try:
            # Get the module name from the path
            module_name = os.path.splitext(os.path.basename(plugin_path))[0]
            module_dir = os.path.dirname(plugin_path)
            
            # Add the module directory to the Python path
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                logger.error(f"Could not load plugin module: {plugin_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Check if the module has the required function
            if not hasattr(module, "create_plugin"):
                logger.error(f"Plugin module does not have a create_plugin function: {plugin_path}")
                return None
            
            # Create the plugin instance
            plugin = module.create_plugin()
            
            # Register the plugin
            self._registry.register_plugin(plugin)
            
            logger.info(f"Loaded and registered plugin: {plugin.get_name()} (v{plugin.get_version()})")
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin from {plugin_path}: {e}")
            return None
    
    def load_all_plugins(self) -> List[Plugin]:
        """
        Discover and load all plugins in the plugin directories.
        
        Returns:
            List of loaded plugin instances
        """
        # Discover plugins
        plugin_paths = self.discover_plugins()
        
        # Load each plugin
        loaded_plugins = []
        for plugin_path in plugin_paths:
            plugin = self.load_plugin(plugin_path)
            if plugin:
                loaded_plugins.append(plugin)
        
        logger.info(f"Loaded {len(loaded_plugins)} plugins")
        return loaded_plugins
    
    def initialize_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Initialize a plugin with the given configuration.
        
        Args:
            plugin_name: Name of the plugin to initialize
            config: Configuration dictionary
            
        Returns:
            True if initialization was successful, False otherwise
        """
        return self._registry.initialize_plugin(plugin_name, config)
    
    def initialize_all_plugins(self, config: Dict[str, Any]) -> bool:
        """
        Initialize all registered plugins with the given configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if all initializations were successful, False otherwise
        """
        all_success = True
        
        for plugin_name in self._registry.list_plugins():
            success = self.initialize_plugin(plugin_name, config)
            all_success = all_success and success
        
        return all_success
    
    def get_registry(self) -> PluginRegistry:
        """
        Get the plugin registry.
        
        Returns:
            Plugin registry instance
        """
        return self._registry
    
    def get_marketplace(self) -> PluginMarketplace:
        """
        Get the plugin marketplace.
        
        Returns:
            Plugin marketplace instance
        """
        return self._marketplace
    
    def run_config_ui(self, ui_type: str = "auto") -> None:
        """
        Run the plugin configuration UI.
        
        Args:
            ui_type: Type of UI to run ('cli', 'web', or 'auto')
        """
        run_config_ui(self._registry, ui_type)
    
    def generate_documentation(self, plugin_name: Optional[str] = None, format: str = "html") -> List[str]:
        """
        Generate documentation for plugins.
        
        Args:
            plugin_name: Name of the plugin to document (None for all plugins)
            format: Documentation format ('html', 'markdown', or 'json')
            
        Returns:
            List of paths to the generated documentation files
        """
        return generate_plugin_documentation(self._registry, plugin_name, format)
    
    def install_plugin_from_marketplace(self, plugin_id: str) -> bool:
        """
        Install a plugin from the marketplace.
        
        Args:
            plugin_id: ID of the plugin to install
            
        Returns:
            True if installation was successful, False otherwise
        """
        return self._marketplace.install_plugin(plugin_id)
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        Uninstall a plugin.
        
        Args:
            plugin_name: Name of the plugin to uninstall
            
        Returns:
            True if uninstallation was successful, False otherwise
        """
        # Get the plugin ID
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_id = f"{plugin.get_name()}-{plugin.get_version()}"
        
        # Uninstall the plugin
        return self._marketplace.uninstall_plugin(plugin_id)
    
    def update_plugin(self, plugin_name: str) -> bool:
        """
        Update a plugin to the latest version.
        
        Args:
            plugin_name: Name of the plugin to update
            
        Returns:
            True if update was successful, False otherwise
        """
        # Get the plugin ID
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_id = f"{plugin.get_name()}-{plugin.get_version()}"
        
        # Update the plugin
        return self._marketplace.update_plugin(plugin_id)
    
    def check_for_updates(self) -> Dict[str, Tuple[str, str]]:
        """
        Check for updates for installed plugins.
        
        Returns:
            Dictionary mapping plugin IDs to tuples of (current_version, latest_version)
            for plugins that have updates available
        """
        return self._marketplace.check_for_updates()
    
    def refresh_marketplace(self) -> bool:
        """
        Refresh the list of available plugins from the marketplace.
        
        Returns:
            True if successful, False otherwise
        """
        return self._marketplace.refresh_available_plugins()
    
    def search_marketplace(self, query: str, tags: Optional[List[str]] = None, 
                          plugin_type: Optional[PluginType] = None) -> List[Any]:
        """
        Search for plugins in the marketplace.
        
        Args:
            query: Search query string
            tags: List of tags to filter by (optional)
            plugin_type: Plugin type to filter by (optional)
            
        Returns:
            List of matching plugin packages
        """
        return self._marketplace.search_plugins(query, tags, plugin_type)
    
    def get_plugin_documentation(self, plugin_name: str) -> Optional[str]:
        """
        Get the documentation for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Documentation string or None if not available
        """
        # Get the plugin ID
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return None
        
        plugin_id = f"{plugin.get_name()}-{plugin.get_version()}"
        
        # Get the documentation
        return self._marketplace.get_plugin_documentation(plugin_id)
    
    def get_plugin_changelog(self, plugin_name: str) -> Optional[str]:
        """
        Get the changelog for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Changelog string or None if not available
        """
        # Get the plugin ID
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return None
        
        plugin_id = f"{plugin.get_name()}-{plugin.get_version()}"
        
        # Get the changelog
        return self._marketplace.get_plugin_changelog(plugin_id)


# Create a singleton instance of the plugin manager
_plugin_manager = None

def get_plugin_manager(plugin_dirs: Optional[List[str]] = None) -> PluginManager:
    """
    Get the singleton instance of the plugin manager.
    
    Args:
        plugin_dirs: List of directories to search for plugins (optional)
        
    Returns:
        Plugin manager instance
    """
    global _plugin_manager
    
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugin_dirs)
    
    return _plugin_manager