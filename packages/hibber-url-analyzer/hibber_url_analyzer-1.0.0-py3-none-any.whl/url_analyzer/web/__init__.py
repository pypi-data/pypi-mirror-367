"""
Web interface package for URL Analyzer.

This package provides a web-based user interface for the URL Analyzer,
making it accessible through a browser with responsive design,
accessibility features, internationalization, and theme support.
"""

from url_analyzer.web.app import create_app

__all__ = ['create_app']