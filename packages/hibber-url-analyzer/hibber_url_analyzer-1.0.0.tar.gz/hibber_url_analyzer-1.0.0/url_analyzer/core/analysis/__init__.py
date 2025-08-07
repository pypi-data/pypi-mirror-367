"""
Analysis functionality for URL Analyzer core package.

This module consolidates analysis functionality from the original analysis package.
"""

from typing import Tuple, Dict, Any, Optional
from url_analyzer.analysis import RequestsURLFetcher, AnalysisOptions, DefaultAnalysisService

# Global cache for live scan results
LIVE_SCAN_CACHE = {}

# Global fetcher instance
_fetcher = RequestsURLFetcher()
_analysis_service = DefaultAnalysisService()

def fetch_url_data(url: str, summarize: bool = False, config: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Fetch URL data and return status and content information.
    
    This function provides backward compatibility with the legacy API.
    
    Args:
        url: The URL to fetch
        summarize: Whether to generate content summary (legacy parameter)
        config: Configuration dictionary (legacy parameter)
        
    Returns:
        Tuple of (url, result_dict) where result_dict contains:
        - status_code: HTTP status code
        - title: Page title if available
        - content: Page content if available
        - error: Error message if fetch failed
    """
    try:
        # Check cache first
        if url in LIVE_SCAN_CACHE:
            return url, LIVE_SCAN_CACHE[url]
        
        # Create analysis options
        options = AnalysisOptions(
            fetch_content=True,
            analyze_content=True,
            generate_summary=summarize
        )
        
        # Fetch URL using the new service
        fetch_result = _fetcher.fetch_url(url, options)
        
        # Convert to legacy format
        result_dict = {
            'status_code': fetch_result.status_code,
            'title': fetch_result.content.title if fetch_result.content else '',
            'content': fetch_result.content.text_content if fetch_result.content else '',
            'error': fetch_result.error_message if not fetch_result.success else None
        }
        
        # Cache the result
        LIVE_SCAN_CACHE[url] = result_dict
        
        return url, result_dict
        
    except Exception as e:
        error_result = {
            'status_code': 0,
            'title': '',
            'content': '',
            'error': str(e)
        }
        return url, error_result

def load_cache(cache_file: str) -> Dict[str, Any]:
    """Load cache from file (legacy compatibility function)."""
    # For now, return empty dict - can be implemented later if needed
    return {}

def save_cache(cache_data: Dict[str, Any], cache_file: str) -> None:
    """Save cache to file (legacy compatibility function)."""
    # For now, do nothing - can be implemented later if needed
    pass

__all__ = ['fetch_url_data', 'LIVE_SCAN_CACHE', 'load_cache', 'save_cache']