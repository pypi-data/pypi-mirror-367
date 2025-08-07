"""
Plugin Loader Module

This module provides functionality for loading plugins into the URL Analyzer system.
"""

import os
import sys
import importlib
from typing import Dict, List, Any, Optional, Type, Union, Tuple

from url_analyzer.plugins.interface import Plugin, URLClassifierPlugin, ReportGeneratorPlugin
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.plugins.discovery import discover_plugins, get_plugin_info
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


def load_plugin(
    plugin_class: Type[Plugin],
    registry: PluginRegistry,
    config: Optional[Dict[str, Any]] = None
) -> Optional[Plugin]:
    """
    Loads a plugin class into the registry.
    
    Args:
        plugin_class: Plugin class to load
        registry: Plugin registry to load the plugin into
        config: Configuration dictionary for the plugin
        
    Returns:
        Loaded plugin instance or None if loading failed
    """
    try:
        # Create an instance of the plugin
        plugin = plugin_class()
        
        # Register the plugin with the registry
        registry.register_plugin(plugin)
        
        # Initialize the plugin if config is provided
        if config is not None:
            success = registry.initialize_plugin(plugin.get_name(), config)
            if not success:
                logger.error(f"Failed to initialize plugin: {plugin.get_name()}")
                registry.unregister_plugin(plugin.get_name())
                return None
        
        logger.info(f"Loaded plugin: {plugin.get_name()} (v{plugin.get_version()})")
        return plugin
    
    except Exception as e:
        logger.error(f"Error loading plugin {plugin_class.__name__}: {e}")
        return None


def load_plugins(
    plugin_classes: List[Type[Plugin]],
    registry: PluginRegistry,
    config: Optional[Dict[str, Any]] = None
) -> List[Plugin]:
    """
    Loads multiple plugin classes into the registry.
    
    Args:
        plugin_classes: List of plugin classes to load
        registry: Plugin registry to load the plugins into
        config: Configuration dictionary for the plugins
        
    Returns:
        List of loaded plugin instances
    """
    loaded_plugins = []
    
    for plugin_class in plugin_classes:
        plugin = load_plugin(plugin_class, registry, config)
        if plugin is not None:
            loaded_plugins.append(plugin)
    
    logger.info(f"Loaded {len(loaded_plugins)} plugins")
    return loaded_plugins


def load_plugins_from_directory(
    directory: str,
    registry: PluginRegistry,
    config: Optional[Dict[str, Any]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> List[Plugin]:
    """
    Discovers and loads plugins from a directory.
    
    Args:
        directory: Directory path to search for plugin modules
        registry: Plugin registry to load the plugins into
        config: Configuration dictionary for the plugins
        exclude_patterns: List of patterns to exclude from discovery
        
    Returns:
        List of loaded plugin instances
    """
    # Discover plugin classes from the directory
    plugin_classes = discover_plugins(directories=[directory], exclude_patterns=exclude_patterns)
    
    # Load the discovered plugin classes
    return load_plugins(plugin_classes, registry, config)


def load_plugins_from_package(
    package_name: str,
    registry: PluginRegistry,
    config: Optional[Dict[str, Any]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> List[Plugin]:
    """
    Discovers and loads plugins from a package.
    
    Args:
        package_name: Name of the package to search for plugin modules
        registry: Plugin registry to load the plugins into
        config: Configuration dictionary for the plugins
        exclude_patterns: List of patterns to exclude from discovery
        
    Returns:
        List of loaded plugin instances
    """
    # Discover plugin classes from the package
    plugin_classes = discover_plugins(packages=[package_name], exclude_patterns=exclude_patterns)
    
    # Load the discovered plugin classes
    return load_plugins(plugin_classes, registry, config)


def load_plugins_from_config(
    config: Dict[str, Any],
    registry: PluginRegistry
) -> List[Plugin]:
    """
    Loads plugins based on configuration.
    
    Args:
        config: Configuration dictionary containing plugin information
        registry: Plugin registry to load the plugins into
        
    Returns:
        List of loaded plugin instances
    """
    loaded_plugins = []
    
    # Check if the config has a 'plugins' section
    if 'plugins' not in config:
        logger.warning("No 'plugins' section found in configuration")
        return loaded_plugins
    
    plugins_config = config['plugins']
    
    # Load plugins from directories
    if 'directories' in plugins_config:
        for directory in plugins_config['directories']:
            loaded_plugins.extend(load_plugins_from_directory(
                directory,
                registry,
                plugins_config.get('config'),
                plugins_config.get('exclude_patterns')
            ))
    
    # Load plugins from packages
    if 'packages' in plugins_config:
        for package_name in plugins_config['packages']:
            loaded_plugins.extend(load_plugins_from_package(
                package_name,
                registry,
                plugins_config.get('config'),
                plugins_config.get('exclude_patterns')
            ))
    
    # Load specific plugin classes
    if 'classes' in plugins_config:
        for class_info in plugins_config['classes']:
            try:
                module_name = class_info['module']
                class_name = class_info['class']
                
                # Import the module
                module = importlib.import_module(module_name)
                
                # Get the plugin class
                plugin_class = getattr(module, class_name)
                
                # Load the plugin
                plugin = load_plugin(
                    plugin_class,
                    registry,
                    class_info.get('config') or plugins_config.get('config')
                )
                
                if plugin is not None:
                    loaded_plugins.append(plugin)
            
            except Exception as e:
                logger.error(f"Error loading plugin class {class_info.get('class', 'unknown')}: {e}")
    
    logger.info(f"Loaded {len(loaded_plugins)} plugins from configuration")
    return loaded_plugins


def create_plugin_instance(
    plugin_class: Type[Plugin],
    config: Optional[Dict[str, Any]] = None
) -> Optional[Plugin]:
    """
    Creates an instance of a plugin class without registering it.
    
    This is useful for testing plugins or for creating temporary plugin instances.
    
    Args:
        plugin_class: Plugin class to instantiate
        config: Configuration dictionary for the plugin
        
    Returns:
        Plugin instance or None if creation failed
    """
    try:
        # Create an instance of the plugin
        plugin = plugin_class()
        
        # Initialize the plugin if config is provided
        if config is not None:
            success = plugin.initialize(config)
            if not success:
                logger.error(f"Failed to initialize plugin: {plugin.get_name()}")
                return None
        
        return plugin
    
    except Exception as e:
        logger.error(f"Error creating plugin instance {plugin_class.__name__}: {e}")
        return None