"""
Plugin Discovery Module

This module provides functionality for discovering plugins from various sources,
such as directories and installed packages.
"""

import os
import sys
import importlib
import importlib.util
import pkgutil
import inspect
from typing import Dict, List, Any, Optional, Type, Set, Tuple

from url_analyzer.plugins.interface import Plugin
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


def discover_plugins(
    directories: Optional[List[str]] = None,
    packages: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> List[Type[Plugin]]:
    """
    Discovers plugin classes from directories and packages.
    
    Args:
        directories: List of directory paths to search for plugin modules
        packages: List of package names to search for plugin modules
        exclude_patterns: List of patterns to exclude from discovery
        
    Returns:
        List of discovered plugin classes
    """
    plugin_classes = []
    
    # Discover plugins from directories
    if directories:
        for directory in directories:
            plugin_classes.extend(_discover_plugins_from_directory(directory, exclude_patterns))
    
    # Discover plugins from packages
    if packages:
        for package_name in packages:
            plugin_classes.extend(_discover_plugins_from_package(package_name, exclude_patterns))
    
    # If no directories or packages specified, use default locations
    if not directories and not packages:
        # Default to the 'plugins' directory in the current working directory
        default_plugins_dir = os.path.join(os.getcwd(), 'plugins')
        if os.path.isdir(default_plugins_dir):
            plugin_classes.extend(_discover_plugins_from_directory(default_plugins_dir, exclude_patterns))
        
        # Default to the 'url_analyzer_plugins' package if installed
        try:
            importlib.import_module('url_analyzer_plugins')
            plugin_classes.extend(_discover_plugins_from_package('url_analyzer_plugins', exclude_patterns))
        except ImportError:
            pass
    
    logger.info(f"Discovered {len(plugin_classes)} plugin classes")
    return plugin_classes


def _discover_plugins_from_directory(
    directory: str,
    exclude_patterns: Optional[List[str]] = None
) -> List[Type[Plugin]]:
    """
    Discovers plugin classes from Python files in a directory.
    
    This is an internal function used by discover_plugins.
    
    Args:
        directory: Directory path to search for plugin modules
        exclude_patterns: List of patterns to exclude from discovery
        
    Returns:
        List of discovered plugin classes
    """
    plugin_classes = []
    
    if not os.path.isdir(directory):
        logger.warning(f"Directory not found: {directory}")
        return plugin_classes
    
    logger.info(f"Searching for plugins in directory: {directory}")
    
    # Add the directory to the Python path temporarily
    sys.path.insert(0, os.path.abspath(os.path.dirname(directory)))
    
    try:
        # Get all Python files in the directory
        for filename in os.listdir(directory):
            if not filename.endswith('.py') or filename.startswith('_'):
                continue
            
            module_name = os.path.splitext(filename)[0]
            
            # Skip modules matching exclude patterns
            if exclude_patterns and any(pattern in module_name for pattern in exclude_patterns):
                logger.debug(f"Skipping excluded module: {module_name}")
                continue
            
            # Import the module
            try:
                module_path = os.path.join(directory, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    logger.warning(f"Could not load module spec: {module_path}")
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Plugin) and 
                        obj.__module__ == module.__name__ and
                        obj is not Plugin):
                        plugin_classes.append(obj)
                        logger.debug(f"Discovered plugin class: {obj.__name__} in {module_name}")
            
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {e}")
    
    finally:
        # Remove the directory from the Python path
        if directory in sys.path:
            sys.path.remove(os.path.abspath(os.path.dirname(directory)))
    
    return plugin_classes


def _discover_plugins_from_package(
    package_name: str,
    exclude_patterns: Optional[List[str]] = None
) -> List[Type[Plugin]]:
    """
    Discovers plugin classes from modules in a package.
    
    This is an internal function used by discover_plugins.
    
    Args:
        package_name: Name of the package to search for plugin modules
        exclude_patterns: List of patterns to exclude from discovery
        
    Returns:
        List of discovered plugin classes
    """
    plugin_classes = []
    
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        logger.warning(f"Package not found: {package_name}")
        return plugin_classes
    
    logger.info(f"Searching for plugins in package: {package_name}")
    
    # Get the package path
    if not hasattr(package, '__path__'):
        logger.warning(f"{package_name} is not a package")
        return plugin_classes
    
    # Iterate through all modules in the package
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package_name + '.'):
        # Skip modules matching exclude patterns
        if exclude_patterns and any(pattern in module_name for pattern in exclude_patterns):
            logger.debug(f"Skipping excluded module: {module_name}")
            continue
        
        # Skip subpackages
        if is_pkg:
            continue
        
        # Import the module
        try:
            module = importlib.import_module(module_name)
            
            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj.__module__ == module.__name__ and
                    obj is not Plugin):
                    plugin_classes.append(obj)
                    logger.debug(f"Discovered plugin class: {obj.__name__} in {module_name}")
        
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
    
    return plugin_classes


def get_plugin_info(plugin_class: Type[Plugin]) -> Dict[str, Any]:
    """
    Gets information about a plugin class.
    
    Args:
        plugin_class: Plugin class to get information about
        
    Returns:
        Dictionary containing plugin information
    """
    # Create a temporary instance to get plugin information
    try:
        plugin = plugin_class()
        info = {
            'name': plugin.get_name(),
            'version': plugin.get_version(),
            'description': plugin.get_description(),
            'author': plugin.get_author(),
            'class': plugin_class.__name__,
            'module': plugin_class.__module__
        }
    except Exception as e:
        logger.error(f"Error getting plugin info for {plugin_class.__name__}: {e}")
        info = {
            'name': plugin_class.__name__,
            'version': 'Unknown',
            'description': 'Error getting plugin info',
            'author': 'Unknown',
            'class': plugin_class.__name__,
            'module': plugin_class.__module__,
            'error': str(e)
        }
    
    return info