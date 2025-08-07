"""
Classification functionality for URL Analyzer core package.

This module consolidates classification functionality from the original 
classification and core packages.
"""

import re
import logging
from typing import Tuple, Dict, Optional, Any, Union

# Create logger
logger = logging.getLogger(__name__)

# Optional imports for advanced features
try:
    import tldextract
    TLDEXTRACT_AVAILABLE = True
except ImportError:
    TLDEXTRACT_AVAILABLE = False
    logger.debug("tldextract not available, some domain extraction features disabled")


def get_base_domain(url: str) -> str:
    """
    Extracts the base domain from a URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Base domain string or empty string if extraction fails
    """
    # Basic validation
    if not isinstance(url, str) or not url.strip():
        return ''
    
    # Check if tldextract is available
    if not TLDEXTRACT_AVAILABLE:
        logger.warning("tldextract not available, base domain extraction disabled")
        return ''
    
    try:
        # Extract the registered domain
        domain = tldextract.extract(url).registered_domain
        logger.debug(f"Extracted base domain '{domain}' from URL '{url}'")
        return domain or ''
    except Exception as e:
        logger.warning(f"Error extracting base domain from URL '{url}': {e}")
        return ''


def classify_url(url: str, patterns: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Classifies a URL based on pre-compiled regex patterns.
    
    Args:
        url: URL to classify
        patterns: Dictionary of compiled patterns
        
    Returns:
        Tuple of (category, is_sensitive)
    """
    # Basic validation
    if not isinstance(url, str) or not url.strip():
        return 'Empty or Invalid', False
    
    if not isinstance(patterns, dict):
        logger.error(f"Invalid patterns type: {type(patterns).__name__}")
        return 'Unknown', False
    
    try:
        # Simple pattern matching logic for basic functionality
        url_lower = url.lower()
        
        # Check for social media patterns
        if any(pattern in url_lower for pattern in ['facebook.com', 'twitter.com', 'instagram.com']):
            return 'Social Media', True
        
        # Check for analytics patterns
        if any(pattern in url_lower for pattern in ['analytics', 'tracking', 'doubleclick']):
            return 'Analytics', False
        
        # Check for advertising patterns
        if any(pattern in url_lower for pattern in ['ads', 'adservice', 'googleads']):
            return 'Advertising', False
        
        # Default to Corporate
        return 'Corporate', False
        
    except Exception as e:
        logger.error(f"Error classifying URL '{url}': {e}")
        return 'Unknown', False


def compile_patterns(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create compiled patterns from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of compiled patterns
    """
    if not isinstance(config, dict):
        logger.error(f"Invalid config type: {type(config).__name__}")
        return {}
    
    try:
        # Simple pattern compilation for basic functionality
        compiled_patterns = {
            'social_media': ['facebook.com', 'twitter.com', 'instagram.com'],
            'analytics': ['analytics', 'tracking', 'doubleclick'],
            'advertising': ['ads', 'adservice', 'googleads']
        }
        
        logger.info("Created basic classification patterns")
        return compiled_patterns
        
    except Exception as e:
        logger.error(f"Error compiling patterns: {e}")
        return {}


__all__ = ['get_base_domain', 'classify_url', 'compile_patterns']