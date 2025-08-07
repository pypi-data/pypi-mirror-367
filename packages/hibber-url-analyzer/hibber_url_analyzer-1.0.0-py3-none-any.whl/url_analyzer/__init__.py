"""
URL Analyzer - A tool for analyzing, categorizing, and reporting on URLs.

This package provides functionality for analyzing URLs, generating reports,
and visualizing browsing patterns.
"""

import logging
import os
import sys
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Initialize version
__version__ = "1.0.0"

def initialize(check_dependencies: bool = True) -> bool:
    """
    Initialize the URL Analyzer package.
    
    This function performs necessary setup tasks such as:
    - Checking dependencies
    - Setting up logging
    - Loading configuration
    
    Args:
        check_dependencies: Whether to check dependencies at startup
        
    Returns:
        True if initialization was successful, False otherwise
    """
    # Set up logging
    _setup_logging()
    
    # Check dependencies if requested
    if check_dependencies:
        from url_analyzer.utils.dependency_manager import check_dependencies_at_startup
        if not check_dependencies_at_startup():
            logger.error("Failed to initialize URL Analyzer due to missing dependencies.")
            return False
    
    logger.info("URL Analyzer initialized successfully.")
    return True


def _setup_logging(log_level: Optional[str] = None) -> None:
    """
    Set up logging for the URL Analyzer package.
    
    Args:
        log_level: The log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  If None, uses the value from environment variable URL_ANALYZER_LOG_LEVEL
                  or defaults to INFO
    """
    # Determine log level
    if log_level is None:
        log_level = os.environ.get("URL_ANALYZER_LOG_LEVEL", "INFO")
    
    # Convert string log level to numeric value
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
        except OSError as e:
            logger.warning(f"Could not create logs directory: {e}")
            return
    
    # Add file handler
    try:
        file_handler = logging.FileHandler(
            os.path.join(logs_dir, "url_analyzer.log"),
            encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S"
        ))
        logging.getLogger().addHandler(file_handler)
    except (OSError, IOError) as e:
        logger.warning(f"Could not set up file logging: {e}")


# Note: Initialization is now explicit - call initialize() when needed
# This prevents side effects during import and gives users control over initialization