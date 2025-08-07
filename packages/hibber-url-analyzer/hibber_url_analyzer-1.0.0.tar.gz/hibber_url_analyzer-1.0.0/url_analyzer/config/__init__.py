"""
Configuration management package for URL Analyzer.

This package provides centralized configuration management functionality,
consolidating configuration logic from across the application.
"""

from .manager import ConfigManager, load_config, save_config, create_default_config

__all__ = [
    'ConfigManager',
    'load_config', 
    'save_config',
    'create_default_config'
]