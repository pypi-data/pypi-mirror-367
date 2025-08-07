"""
Feature flags for URL Analyzer.

This module provides functionality for managing feature flags,
particularly for features that depend on optional dependencies.
"""

import importlib
import logging
from typing import Dict, List, Optional, Set, Tuple, Union, Callable

# Configure logging
logger = logging.getLogger(__name__)

# Define feature flags and their dependencies
FEATURE_FLAGS = {
    "url_fetching": {
        "dependencies": ["requests"],
        "description": "Fetch URL content for analysis",
        "fallback_available": True
    },
    "html_parsing": {
        "dependencies": ["beautifulsoup4", "lxml"],
        "description": "Parse HTML content from URLs",
        "fallback_available": True
    },
    "domain_extraction": {
        "dependencies": ["tldextract"],
        "description": "Extract domain information from URLs",
        "fallback_available": True
    },
    "advanced_visualization": {
        "dependencies": ["plotly"],
        "description": "Generate advanced interactive visualizations",
        "fallback_available": False
    },
    "geolocation": {
        "dependencies": ["geoip2", "pycountry"],
        "description": "Determine geographic location of IP addresses",
        "fallback_available": False
    },
    "pdf_export": {
        "dependencies": ["weasyprint"],
        "description": "Export reports to PDF format",
        "fallback_available": False
    },
    "progress_tracking": {
        "dependencies": ["tqdm"],
        "description": "Show progress bars for long-running operations",
        "fallback_available": True
    },
    "excel_support": {
        "dependencies": ["openpyxl"],
        "description": "Read and write Excel files",
        "fallback_available": False
    },
    "rich_terminal": {
        "dependencies": ["rich", "prompt_toolkit"],
        "description": "Enhanced terminal user interface",
        "fallback_available": True
    },
    "system_monitoring": {
        "dependencies": ["psutil"],
        "description": "Monitor system resource usage",
        "fallback_available": False
    }
}

# Cache for feature availability
_feature_availability_cache: Dict[str, bool] = {}


def is_package_installed(package_name: str) -> bool:
    """
    Check if a package is installed.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        True if the package is installed, False otherwise
    """
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except (ImportError, AttributeError):
        return False


def is_feature_available(feature_name: str) -> bool:
    """
    Check if a feature is available based on its dependencies.
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        True if the feature is available, False otherwise
    """
    # Check cache first
    if feature_name in _feature_availability_cache:
        return _feature_availability_cache[feature_name]
    
    # Check if feature exists
    if feature_name not in FEATURE_FLAGS:
        logger.warning(f"Unknown feature: {feature_name}")
        _feature_availability_cache[feature_name] = False
        return False
    
    # Check dependencies
    feature_info = FEATURE_FLAGS[feature_name]
    dependencies = feature_info["dependencies"]
    
    # Check if all dependencies are installed
    available = all(is_package_installed(dep) for dep in dependencies)
    
    # Cache result
    _feature_availability_cache[feature_name] = available
    
    return available


def get_available_features() -> Dict[str, bool]:
    """
    Get a dictionary of all features and their availability.
    
    Returns:
        Dictionary with feature names as keys and availability as values
    """
    return {
        feature_name: is_feature_available(feature_name)
        for feature_name in FEATURE_FLAGS
    }


def get_unavailable_features() -> Dict[str, List[str]]:
    """
    Get a dictionary of unavailable features and their missing dependencies.
    
    Returns:
        Dictionary with feature names as keys and lists of missing dependencies as values
    """
    unavailable_features = {}
    
    for feature_name, feature_info in FEATURE_FLAGS.items():
        if not is_feature_available(feature_name):
            missing_deps = [
                dep for dep in feature_info["dependencies"]
                if not is_package_installed(dep)
            ]
            if missing_deps:
                unavailable_features[feature_name] = missing_deps
    
    return unavailable_features


def print_feature_status() -> None:
    """
    Print the status of all features to the console.
    """
    print("\n=== URL Analyzer Feature Status ===\n")
    
    for feature_name, feature_info in FEATURE_FLAGS.items():
        available = is_feature_available(feature_name)
        status = "✓" if available else "✗"
        
        print(f"{status} {feature_name}: {feature_info['description']}")
        
        if not available:
            missing_deps = [
                dep for dep in feature_info["dependencies"]
                if not is_package_installed(dep)
            ]
            
            if feature_info["fallback_available"]:
                print(f"  - Limited functionality available (fallback mode)")
            else:
                print(f"  - Feature unavailable")
                
            print(f"  - Missing dependencies: {', '.join(missing_deps)}")
            print(f"  - Install with: pip install {' '.join(missing_deps)}")
    
    print("\n")


def with_feature(feature_name: str, fallback_result: Optional[any] = None) -> Callable:
    """
    Decorator to conditionally execute a function if a feature is available.
    
    Args:
        feature_name: Name of the required feature
        fallback_result: Result to return if feature is unavailable
        
    Returns:
        Decorated function that checks feature availability
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if is_feature_available(feature_name):
                return func(*args, **kwargs)
            else:
                feature_info = FEATURE_FLAGS.get(feature_name, {})
                logger.warning(
                    f"Feature '{feature_name}' is unavailable due to missing dependencies. "
                    f"Install {', '.join(feature_info.get('dependencies', []))} to enable this feature."
                )
                return fallback_result
        return wrapper
    return decorator


def initialize_features() -> None:
    """
    Initialize feature flags and log warnings for unavailable features.
    """
    logger.info("Initializing feature flags...")
    
    # Check all features
    unavailable = get_unavailable_features()
    
    # Log warnings for unavailable features
    for feature_name, missing_deps in unavailable.items():
        feature_info = FEATURE_FLAGS[feature_name]
        
        if feature_info["fallback_available"]:
            logger.warning(
                f"Feature '{feature_name}' will use limited functionality due to missing dependencies: "
                f"{', '.join(missing_deps)}"
            )
        else:
            logger.warning(
                f"Feature '{feature_name}' is unavailable due to missing dependencies: "
                f"{', '.join(missing_deps)}"
            )
    
    # Log available features
    available_features = [
        name for name, available in get_available_features().items()
        if available
    ]
    
    if available_features:
        logger.info(f"Available features: {', '.join(available_features)}")
    else:
        logger.warning("No optional features available. Only core functionality will work.")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Print feature status when run directly
    print_feature_status()