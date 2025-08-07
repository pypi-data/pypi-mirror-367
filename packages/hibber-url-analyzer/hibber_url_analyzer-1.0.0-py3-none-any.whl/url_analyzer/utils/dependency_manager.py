"""
Dependency management utilities for URL Analyzer.

This module provides functions for checking and managing dependencies,
ensuring that all required and optional dependencies are properly installed
and configured.
"""

import importlib
import importlib.util
import importlib.metadata
import logging
import os
import sys
from typing import Dict, List, Optional, Set, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

# Define dependency groups
CORE_DEPENDENCIES = {
    'pandas': '1.3.0',
    'numpy': '1.20.0',
    'jinja2': '3.1.6',
}

OPTIONAL_DEPENDENCIES = {
    'URL Fetching': {
        'requests': '2.32.4',
    },
    'HTML Parsing': {
        'beautifulsoup4': '4.9.0',
        'lxml': '4.6.0',
    },
    'Domain Extraction': {
        'tldextract': '3.1.0',
    },
    'Visualization': {
        'plotly': '5.3.0',
    },
    'Geolocation': {
        'geoip2': '4.6.0',
        'pycountry': '22.3.5',
    },
    'PDF Generation': {
        'weasyprint': '57.1',
    },
    'Progress Tracking': {
        'tqdm': '4.60.0',
    },
    'Excel Support': {
        'openpyxl': '3.0.0',
    },
    'Terminal UI': {
        'rich': '13.3.0',
        'prompt_toolkit': '3.0.30',
    },
    'System Monitoring': {
        'psutil': '5.9.0',
    }
}

# Known dependency conflicts and their resolutions
DEPENDENCY_CONFLICTS = {
    'weasyprint': {
        'conflict': 'May conflict with system libraries on some platforms',
        'resolution': 'Install system dependencies first: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html'
    },
    'lxml': {
        'conflict': 'Requires C compiler and libxml2/libxslt development packages',
        'resolution': 'Install system dependencies before pip install'
    }
}


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


def check_version(package_name: str, min_version: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a package meets the minimum version requirement.
    
    Args:
        package_name: Name of the package to check
        min_version: Minimum version required
        
    Returns:
        Tuple of (meets_requirement, installed_version)
        If package is not installed, installed_version will be None
    """
    if not is_package_installed(package_name):
        return False, None
    
    try:
        installed_version = importlib.metadata.version(package_name)
        meets_requirement = importlib.metadata.version_compare(installed_version, f">={min_version}")
        return meets_requirement, installed_version
    except importlib.metadata.PackageNotFoundError:
        return False, None


def check_core_dependencies() -> Dict[str, Dict[str, Union[bool, str, None]]]:
    """
    Check all core dependencies.
    
    Returns:
        Dictionary with dependency status information
    """
    results = {}
    all_satisfied = True
    
    for package, min_version in CORE_DEPENDENCIES.items():
        meets_req, installed_version = check_version(package, min_version)
        results[package] = {
            'installed': is_package_installed(package),
            'version': installed_version,
            'required_version': min_version,
            'meets_requirement': meets_req
        }
        
        if not meets_req:
            all_satisfied = False
            
    return {
        'dependencies': results,
        'all_satisfied': all_satisfied
    }


def check_optional_dependencies() -> Dict[str, Dict[str, Union[Dict, bool]]]:
    """
    Check all optional dependencies.
    
    Returns:
        Dictionary with dependency status information grouped by feature
    """
    results = {}
    
    for feature, dependencies in OPTIONAL_DEPENDENCIES.items():
        feature_results = {}
        feature_satisfied = True
        
        for package, min_version in dependencies.items():
            meets_req, installed_version = check_version(package, min_version)
            feature_results[package] = {
                'installed': is_package_installed(package),
                'version': installed_version,
                'required_version': min_version,
                'meets_requirement': meets_req
            }
            
            if not meets_req:
                feature_satisfied = False
                
        results[feature] = {
            'dependencies': feature_results,
            'all_satisfied': feature_satisfied
        }
            
    return results


def get_missing_core_dependencies() -> List[str]:
    """
    Get a list of missing core dependencies.
    
    Returns:
        List of package names that are missing or don't meet version requirements
    """
    missing = []
    core_check = check_core_dependencies()
    
    for package, info in core_check['dependencies'].items():
        if not info['meets_requirement']:
            if info['installed'] and info['version']:
                missing.append(f"{package}>={info['required_version']} (found {info['version']})")
            else:
                missing.append(f"{package}>={info['required_version']}")
                
    return missing


def get_missing_optional_dependencies() -> Dict[str, List[str]]:
    """
    Get a dictionary of missing optional dependencies by feature.
    
    Returns:
        Dictionary with feature names as keys and lists of missing packages as values
    """
    missing = {}
    optional_check = check_optional_dependencies()
    
    for feature, feature_info in optional_check.items():
        feature_missing = []
        
        for package, info in feature_info['dependencies'].items():
            if not info['meets_requirement']:
                if info['installed'] and info['version']:
                    feature_missing.append(f"{package}>={info['required_version']} (found {info['version']})")
                else:
                    feature_missing.append(f"{package}>={info['required_version']}")
                    
        if feature_missing:
            missing[feature] = feature_missing
                
    return missing


def check_dependencies_at_startup() -> bool:
    """
    Check dependencies at startup and log warnings for missing dependencies.
    
    Returns:
        True if all core dependencies are satisfied, False otherwise
    """
    logger.info("Checking dependencies...")
    
    # Check core dependencies
    core_check = check_core_dependencies()
    if not core_check['all_satisfied']:
        missing_core = get_missing_core_dependencies()
        logger.error("Missing required dependencies: %s", ", ".join(missing_core))
        logger.error("Please install required dependencies: pip install %s", " ".join(missing_core))
        return False
    
    # Check optional dependencies
    missing_optional = get_missing_optional_dependencies()
    if missing_optional:
        for feature, missing in missing_optional.items():
            logger.warning("Feature '%s' disabled due to missing dependencies: %s", 
                          feature, ", ".join(missing))
    
    # Log known conflicts
    for package in DEPENDENCY_CONFLICTS:
        if is_package_installed(package):
            conflict_info = DEPENDENCY_CONFLICTS[package]
            logger.info("Note about %s: %s. Resolution: %s", 
                       package, conflict_info['conflict'], conflict_info['resolution'])
    
    logger.info("All core dependencies satisfied.")
    return True


def generate_requirements_file(path: str = "requirements.txt") -> None:
    """
    Generate a requirements.txt file with all dependencies.
    
    Args:
        path: Path to the output file
    """
    with open(path, 'w') as f:
        f.write("# Core dependencies\n")
        for package, version in CORE_DEPENDENCIES.items():
            f.write(f"{package}>={version}\n")
        
        f.write("\n# Optional dependencies for advanced features\n")
        for feature, dependencies in OPTIONAL_DEPENDENCIES.items():
            f.write(f"# {feature}\n")
            for package, version in dependencies.items():
                f.write(f"{package}>={version}\n")
            f.write("\n")


def print_dependency_status() -> None:
    """
    Print the status of all dependencies to the console.
    """
    core_check = check_core_dependencies()
    optional_check = check_optional_dependencies()
    
    print("\n=== URL Analyzer Dependency Status ===\n")
    
    print("Core Dependencies:")
    for package, info in core_check['dependencies'].items():
        status = "✓" if info['meets_requirement'] else "✗"
        version_info = f"v{info['version']}" if info['version'] else "not installed"
        print(f"  {status} {package}: {version_info} (required: >={info['required_version']})")
    
    print("\nOptional Dependencies:")
    for feature, feature_info in optional_check.items():
        status = "✓" if feature_info['all_satisfied'] else "✗"
        print(f"  {feature} {status}")
        
        for package, info in feature_info['dependencies'].items():
            status = "✓" if info['meets_requirement'] else "✗"
            version_info = f"v{info['version']}" if info['version'] else "not installed"
            print(f"    {status} {package}: {version_info} (required: >={info['required_version']})")
    
    print("\nKnown Dependency Conflicts:")
    for package, conflict_info in DEPENDENCY_CONFLICTS.items():
        installed = "installed" if is_package_installed(package) else "not installed"
        print(f"  {package} ({installed}):")
        print(f"    Conflict: {conflict_info['conflict']}")
        print(f"    Resolution: {conflict_info['resolution']}")
    
    print("\n")


def create_virtual_environment(path: str = ".venv") -> bool:
    """
    Create a virtual environment for the project.
    
    Args:
        path: Path where the virtual environment should be created
        
    Returns:
        True if successful, False otherwise
    """
    import subprocess
    
    try:
        # Check if venv module is available
        import venv
    except ImportError:
        logger.error("Python venv module not available. Please install it first.")
        return False
    
    if os.path.exists(path):
        logger.warning("Virtual environment directory already exists: %s", path)
        return False
    
    try:
        logger.info("Creating virtual environment at %s", path)
        subprocess.check_call([sys.executable, '-m', 'venv', path])
        
        # Determine the pip path in the new environment
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(path, 'Scripts', 'pip.exe')
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(path, 'bin', 'pip')
        
        # Upgrade pip in the new environment
        subprocess.check_call([pip_path, 'install', '--upgrade', 'pip'])
        
        # Install dependencies
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'requirements.txt')
        if os.path.exists(requirements_path):
            logger.info("Installing dependencies from %s", requirements_path)
            subprocess.check_call([pip_path, 'install', '-r', requirements_path])
        else:
            logger.warning("requirements.txt not found at %s", requirements_path)
        
        logger.info("Virtual environment created successfully at %s", path)
        logger.info("To activate: ")
        if os.name == 'nt':  # Windows
            logger.info("  %s\\Scripts\\activate.bat", path)
        else:  # Unix/Linux/Mac
            logger.info("  source %s/bin/activate", path)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to create virtual environment: %s", str(e))
        return False
    except Exception as e:
        logger.error("Unexpected error creating virtual environment: %s", str(e))
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Print dependency status when run directly
    print_dependency_status()