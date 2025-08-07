"""
Plugin Registry Module

This module provides a registry for managing plugins in the URL Analyzer system.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Type, Union, Set

from url_analyzer.plugins.interface import Plugin, URLClassifierPlugin, ReportGeneratorPlugin
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


class PluginRegistry:
    """
    Registry for managing plugins in the URL Analyzer system.
    
    The registry maintains a collection of registered plugins and provides
    methods for registering, retrieving, and managing plugins.
    """
    
    def __init__(self):
        """
        Initializes a new plugin registry.
        """
        self._plugins: Dict[str, Plugin] = {}
        self._url_classifier_plugins: Dict[str, URLClassifierPlugin] = {}
        self._report_generator_plugins: Dict[str, ReportGeneratorPlugin] = {}
        self._initialized_plugins: Set[str] = set()
        logger.info("Plugin registry initialized")
    
    def register_plugin(self, plugin: Plugin) -> bool:
        """
        Registers a plugin with the registry.
        
        Args:
            plugin: Plugin instance to register
            
        Returns:
            Boolean indicating whether registration was successful
            
        Raises:
            ValueError: If a plugin with the same name is already registered
        """
        plugin_name = plugin.get_name()
        
        if plugin_name in self._plugins:
            error_msg = f"Plugin '{plugin_name}' is already registered"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Register the plugin in the main registry
        self._plugins[plugin_name] = plugin
        
        # Register the plugin in the appropriate specialized registry
        if isinstance(plugin, URLClassifierPlugin):
            self._url_classifier_plugins[plugin_name] = plugin
            logger.info(f"Registered URL classifier plugin: {plugin_name} (v{plugin.get_version()})")
        elif isinstance(plugin, ReportGeneratorPlugin):
            self._report_generator_plugins[plugin_name] = plugin
            logger.info(f"Registered report generator plugin: {plugin_name} (v{plugin.get_version()})")
        else:
            logger.info(f"Registered generic plugin: {plugin_name} (v{plugin.get_version()})")
        
        return True
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregisters a plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to unregister
            
        Returns:
            Boolean indicating whether unregistration was successful
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin '{plugin_name}' is not registered")
            return False
        
        # Shutdown the plugin if it's initialized
        if plugin_name in self._initialized_plugins:
            try:
                self._plugins[plugin_name].shutdown()
                self._initialized_plugins.remove(plugin_name)
            except Exception as e:
                logger.error(f"Error shutting down plugin '{plugin_name}': {e}")
        
        # Remove the plugin from the specialized registries
        if plugin_name in self._url_classifier_plugins:
            del self._url_classifier_plugins[plugin_name]
        if plugin_name in self._report_generator_plugins:
            del self._report_generator_plugins[plugin_name]
        
        # Remove the plugin from the main registry
        del self._plugins[plugin_name]
        logger.info(f"Unregistered plugin: {plugin_name}")
        
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Retrieves a plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to retrieve
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_name)
    
    def get_url_classifier_plugin(self, plugin_name: str) -> Optional[URLClassifierPlugin]:
        """
        Retrieves a URL classifier plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to retrieve
            
        Returns:
            URLClassifierPlugin instance or None if not found
        """
        return self._url_classifier_plugins.get(plugin_name)
    
    def get_report_generator_plugin(self, plugin_name: str) -> Optional[ReportGeneratorPlugin]:
        """
        Retrieves a report generator plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to retrieve
            
        Returns:
            ReportGeneratorPlugin instance or None if not found
        """
        return self._report_generator_plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[Plugin]:
        """
        Retrieves all registered plugins.
        
        Returns:
            List of all registered Plugin instances
        """
        return list(self._plugins.values())
    
    def get_all_url_classifier_plugins(self) -> List[URLClassifierPlugin]:
        """
        Retrieves all registered URL classifier plugins.
        
        Returns:
            List of all registered URLClassifierPlugin instances
        """
        return list(self._url_classifier_plugins.values())
    
    def get_all_report_generator_plugins(self) -> List[ReportGeneratorPlugin]:
        """
        Retrieves all registered report generator plugins.
        
        Returns:
            List of all registered ReportGeneratorPlugin instances
        """
        return list(self._report_generator_plugins.values())
    
    def initialize_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Initializes a plugin with the given configuration.
        
        Args:
            plugin_name: Name of the plugin to initialize
            config: Dictionary containing configuration values
            
        Returns:
            Boolean indicating whether initialization was successful
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin '{plugin_name}' is not registered")
            return False
        
        if plugin_name in self._initialized_plugins:
            logger.warning(f"Plugin '{plugin_name}' is already initialized")
            return True
        
        try:
            success = self._plugins[plugin_name].initialize(config)
            if success:
                self._initialized_plugins.add(plugin_name)
                logger.info(f"Initialized plugin: {plugin_name}")
            else:
                logger.error(f"Failed to initialize plugin: {plugin_name}")
            return success
        except Exception as e:
            logger.error(f"Error initializing plugin '{plugin_name}': {e}")
            return False
    
    def shutdown_plugin(self, plugin_name: str) -> bool:
        """
        Shuts down an initialized plugin.
        
        Args:
            plugin_name: Name of the plugin to shut down
            
        Returns:
            Boolean indicating whether shutdown was successful
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin '{plugin_name}' is not registered")
            return False
        
        if plugin_name not in self._initialized_plugins:
            logger.warning(f"Plugin '{plugin_name}' is not initialized")
            return True
        
        try:
            success = self._plugins[plugin_name].shutdown()
            if success:
                self._initialized_plugins.remove(plugin_name)
                logger.info(f"Shut down plugin: {plugin_name}")
            else:
                logger.error(f"Failed to shut down plugin: {plugin_name}")
            return success
        except Exception as e:
            logger.error(f"Error shutting down plugin '{plugin_name}': {e}")
            return False
    
    def shutdown_all_plugins(self) -> bool:
        """
        Shuts down all initialized plugins.
        
        Returns:
            Boolean indicating whether all plugins were shut down successfully
        """
        all_success = True
        for plugin_name in list(self._initialized_plugins):
            success = self.shutdown_plugin(plugin_name)
            all_success = all_success and success
        return all_success
    
    def is_plugin_initialized(self, plugin_name: str) -> bool:
        """
        Checks if a plugin is initialized.
        
        Args:
            plugin_name: Name of the plugin to check
            
        Returns:
            Boolean indicating whether the plugin is initialized
        """
        return plugin_name in self._initialized_plugins
    
    def get_plugin_count(self) -> int:
        """
        Returns the number of registered plugins.
        
        Returns:
            Integer count of registered plugins
        """
        return len(self._plugins)
    
    def get_url_classifier_plugin_count(self) -> int:
        """
        Returns the number of registered URL classifier plugins.
        
        Returns:
            Integer count of registered URL classifier plugins
        """
        return len(self._url_classifier_plugins)
    
    def get_report_generator_plugin_count(self) -> int:
        """
        Returns the number of registered report generator plugins.
        
        Returns:
            Integer count of registered report generator plugins
        """
        return len(self._report_generator_plugins)