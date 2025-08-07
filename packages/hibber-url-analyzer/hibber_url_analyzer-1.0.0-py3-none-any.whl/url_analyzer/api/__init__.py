"""
API module for URL Analyzer.

This module provides a clean API for programmatic access to URL Analyzer functionality.
It enables external applications to integrate with URL Analyzer's core features.
"""

from url_analyzer.api.core import URLAnalyzerAPI
from url_analyzer.api.models import AnalysisResult, AnalysisRequest, APIVersion

__all__ = ['URLAnalyzerAPI', 'AnalysisResult', 'AnalysisRequest', 'APIVersion']