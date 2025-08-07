"""
Plugin System Module

This module provides a plugin system for extending URL Analyzer functionality,
including custom URL classifiers and report generators.
"""

from url_analyzer.plugins.interface import Plugin, URLClassifierPlugin, ReportGeneratorPlugin
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.plugins.discovery import discover_plugins
from url_analyzer.plugins.loader import load_plugin

# Initialize the plugin registry
registry = PluginRegistry()

__all__ = [
    'Plugin', 
    'URLClassifierPlugin', 
    'ReportGeneratorPlugin',
    'PluginRegistry', 
    'registry',
    'discover_plugins',
    'load_plugin'
]