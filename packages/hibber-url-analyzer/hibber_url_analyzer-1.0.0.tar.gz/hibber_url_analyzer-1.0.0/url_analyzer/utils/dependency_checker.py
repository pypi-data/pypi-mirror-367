"""
Dependency Checker Module

This module provides utilities for checking the availability of optional dependencies
and managing feature flags based on available dependencies.
"""

import importlib
import sys
from typing import Dict, List, Set, Tuple, Optional, Any, Callable

from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


# Define dependency groups
DEPENDENCY_GROUPS = {
    "network": ["requests"],
    "html_parsing": ["beautifulsoup4", "lxml"],
    "domain_extraction": ["tldextract"],
    "visualization": ["plotly"],
    "geolocation": ["geoip2", "pycountry"],
    "pdf_generation": ["weasyprint"],
    "progress_bars": ["tqdm"],
    "excel_support": ["openpyxl"],
    "rich_ui": ["rich", "prompt_toolkit"]
}

# Define feature dependencies
FEATURE_DEPENDENCIES = {
    "url_fetching": ["network"],
    "html_content_analysis": ["network", "html_parsing"],
    "domain_analysis": ["domain_extraction"],
    "advanced_visualizations": ["visualization"],
    "geographical_mapping": ["geolocation"],
    "pdf_reports": ["pdf_generation"],
    "progress_tracking": ["progress_bars"],
    "excel_file_support": ["excel_support"],
    "interactive_cli": ["rich_ui"]
}

# Store available dependencies
available_dependencies: Set[str] = set()
available_features: Set[str] = set()


def check_dependency(dependency: str) -> bool:
    """
    Check if a dependency is available.
    
    Args:
        dependency: Name of the dependency to check
        
    Returns:
        True if the dependency is available, False otherwise
    """
    try:
        importlib.import_module(dependency)
        return True
    except ImportError:
        return False


def check_all_dependencies() -> Dict[str, bool]:
    """
    Check all dependencies and return their availability status.
    
    Returns:
        Dictionary mapping dependency names to their availability status
    """
    global available_dependencies
    
    # Flatten dependency groups
    all_dependencies = set()
    for deps in DEPENDENCY_GROUPS.values():
        all_dependencies.update(deps)
    
    # Check each dependency
    dependency_status = {}
    for dep in all_dependencies:
        is_available = check_dependency(dep)
        dependency_status[dep] = is_available
        if is_available:
            available_dependencies.add(dep)
            logger.debug(f"Dependency '{dep}' is available")
        else:
            logger.debug(f"Dependency '{dep}' is not available")
    
    # Update available features
    update_available_features()
    
    return dependency_status


def update_available_features() -> None:
    """
    Update the set of available features based on available dependencies.
    """
    global available_features
    available_features.clear()
    
    for feature, dep_groups in FEATURE_DEPENDENCIES.items():
        # Check if all dependency groups for this feature are available
        feature_available = True
        missing_deps = []
        
        for group in dep_groups:
            # Check if all dependencies in this group are available
            if group in DEPENDENCY_GROUPS:
                for dep in DEPENDENCY_GROUPS[group]:
                    if dep not in available_dependencies:
                        feature_available = False
                        missing_deps.append(dep)
        
        if feature_available:
            available_features.add(feature)
            logger.debug(f"Feature '{feature}' is available")
        else:
            logger.debug(f"Feature '{feature}' is not available (missing: {', '.join(missing_deps)})")


def is_feature_available(feature: str) -> bool:
    """
    Check if a feature is available based on its dependencies.
    
    Args:
        feature: Name of the feature to check
        
    Returns:
        True if the feature is available, False otherwise
    """
    return feature in available_features


def require_feature(feature: str) -> Callable:
    """
    Decorator to require a feature for a function.
    
    Args:
        feature: Name of the feature required by the function
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_feature_available(feature):
                missing_deps = get_missing_dependencies_for_feature(feature)
                logger.warning(
                    f"Feature '{feature}' is not available. "
                    f"Missing dependencies: {', '.join(missing_deps)}"
                )
                
                # Try to use error_handler if available
                try:
                    from url_analyzer.utils.error_handler import display_error, ErrorCategory
                    display_error(
                        f"Feature '{feature}' is not available",
                        category=ErrorCategory.DEPENDENCY,
                        severity="warning",
                        suggestions=[
                            f"Install missing dependencies: {', '.join(missing_deps)}",
                            "Run 'pip install -r requirements.txt' to install all dependencies"
                        ]
                    )
                except ImportError:
                    print(f"Warning: Feature '{feature}' is not available.")
                    print(f"Missing dependencies: {', '.join(missing_deps)}")
                    print("Install them with: pip install " + " ".join(missing_deps))
                
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_missing_dependencies_for_feature(feature: str) -> List[str]:
    """
    Get the list of missing dependencies for a feature.
    
    Args:
        feature: Name of the feature
        
    Returns:
        List of missing dependencies
    """
    missing_deps = []
    
    if feature in FEATURE_DEPENDENCIES:
        for group in FEATURE_DEPENDENCIES[feature]:
            if group in DEPENDENCY_GROUPS:
                for dep in DEPENDENCY_GROUPS[group]:
                    if dep not in available_dependencies:
                        missing_deps.append(dep)
    
    return missing_deps


def print_dependency_status() -> None:
    """
    Print the status of all dependencies and features.
    """
    # Check dependencies
    dependency_status = check_all_dependencies()
    
    # Print dependency status
    print("\nDependency Status:")
    print("-----------------")
    
    for group, deps in DEPENDENCY_GROUPS.items():
        print(f"\n{group.replace('_', ' ').title()}:")
        for dep in deps:
            status = "✓ Available" if dependency_status.get(dep, False) else "✗ Missing"
            print(f"  - {dep}: {status}")
    
    # Print feature status
    print("\nFeature Status:")
    print("--------------")
    
    for feature, dep_groups in FEATURE_DEPENDENCIES.items():
        status = "✓ Available" if is_feature_available(feature) else "✗ Missing dependencies"
        print(f"  - {feature.replace('_', ' ').title()}: {status}")
        
        if not is_feature_available(feature):
            missing = get_missing_dependencies_for_feature(feature)
            print(f"    Missing: {', '.join(missing)}")
    
    print()


def get_dependency_report() -> Dict[str, Any]:
    """
    Get a report of dependency and feature status.
    
    Returns:
        Dictionary with dependency and feature status information
    """
    # Check dependencies
    dependency_status = check_all_dependencies()
    
    # Create report
    report = {
        "dependencies": {},
        "features": {},
        "python_version": sys.version,
        "total_available_dependencies": len(available_dependencies),
        "total_available_features": len(available_features)
    }
    
    # Add dependency status to report
    for group, deps in DEPENDENCY_GROUPS.items():
        report["dependencies"][group] = {
            dep: dependency_status.get(dep, False) for dep in deps
        }
    
    # Add feature status to report
    for feature in FEATURE_DEPENDENCIES:
        is_available = is_feature_available(feature)
        report["features"][feature] = {
            "available": is_available,
            "missing_dependencies": get_missing_dependencies_for_feature(feature) if not is_available else []
        }
    
    return report


# Note: Dependencies are checked on-demand to avoid import-time failures
# Call check_all_dependencies() explicitly when needed