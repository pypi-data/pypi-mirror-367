"""
Error Handling Module

This module provides a centralized error handling framework for the URL Analyzer,
including specific exception types for different error scenarios and utilities
for error handling and recovery.

Key Components:
    - URLAnalyzerError: Base exception class for all URL Analyzer exceptions
    - Specialized exception classes for different error categories
    - Error handling utilities (handle_error, error_handler, convert_exception)

Exception Hierarchy:
    - URLAnalyzerError (base class)
        - ConfigurationError
            - InvalidConfigurationError
            - MissingConfigurationError
        - IOError
            - FileNotFoundError
            - FilePermissionError
            - InvalidFileFormatError
        - DataProcessingError
            - MissingColumnError
            - InvalidDataError
            - EmptyDataError
        - ValidationError
            - TypeValidationError
            - ValueValidationError
            - SchemaValidationError
            - PathValidationError
            - URLValidationError
        - URLAnalysisError
            - URLFetchError
            - URLClassificationError
        - APIError
            - APIConnectionError
            - APIAuthenticationError
            - APIRateLimitError
        - ReportingError
            - TemplateError
            - ChartGenerationError

Usage Examples:
    Basic exception handling:
        try:
            result = process_file(file_path)
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
        except InvalidFileFormatError as e:
            logger.error(f"Invalid file format: {e}")
    
    Using the error_handler decorator:
        @error_handler(error_types=[FileNotFoundError, InvalidFileFormatError],
                      log_level="error",
                      default_return=None)
        def process_file_safely(file_path):
            return process_file(file_path)
            
    Converting exceptions:
        @convert_exception(from_exception=OSError, 
                          to_exception=FilePermissionError,
                          message="Permission denied when accessing file")
        def read_file(file_path):
            with open(file_path, 'r') as f:
                return f.read()
"""

from typing import Dict, Any, Optional, Union, List, Callable, Type
import traceback
import sys
import os
from functools import wraps

from url_analyzer.utils.logging import get_logger

# Create a logger for this module
logger = get_logger(__name__)


# Base exception class for all URL Analyzer exceptions
class URLAnalyzerError(Exception):
    """
    Base exception class for all URL Analyzer exceptions.
    
    This is the parent class for all custom exceptions in the URL Analyzer.
    It provides a consistent interface for error handling, including support
    for detailed error information.
    
    Attributes:
        message: The error message
        details: A dictionary of additional details about the error
        
    Examples:
        Raising a basic error:
            raise URLAnalyzerError("An error occurred")
            
        Raising an error with details:
            details = {"file": "example.csv", "line": 42}
            raise URLAnalyzerError("Data processing error", details)
            
        Catching and handling the error:
            try:
                process_data()
            except URLAnalyzerError as e:
                logger.error(f"Error: {e}")
                if "file" in e.details:
                    logger.debug(f"Error in file: {e.details['file']}")
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception with a message and optional details.
        
        Args:
            message: Error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


# Configuration errors
class ConfigurationError(URLAnalyzerError):
    """Exception raised for configuration errors."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Exception raised when the configuration is invalid."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Exception raised when a required configuration value is missing."""
    pass


# Input/output errors
class IOError(URLAnalyzerError):
    """Exception raised for input/output errors."""
    pass


class FileNotFoundError(IOError):
    """Exception raised when a file is not found."""
    pass


class FilePermissionError(IOError):
    """Exception raised when there's a permission error with a file."""
    pass


class InvalidFileFormatError(IOError):
    """Exception raised when a file has an invalid format."""
    pass


# Data processing errors
class DataProcessingError(URLAnalyzerError):
    """
    Exception raised for data processing errors.
    
    This exception is raised when there's an error processing data, such as
    when reading from a file, transforming data, or performing analysis operations.
    It serves as the base class for more specific data processing error types like
    MissingColumnError, InvalidDataError, and EmptyDataError.
    
    Examples:
        Raising a data processing error:
            if len(data) == 0:
                raise DataProcessingError("No data to process")
                
        Handling data processing errors:
            try:
                results = process_data(data_frame)
            except MissingColumnError as e:
                logger.error(f"Missing column: {e}")
                return None
            except DataProcessingError as e:
                logger.error(f"Data processing failed: {e}")
                return None
    """
    pass


class MissingColumnError(DataProcessingError):
    """Exception raised when a required column is missing from the data."""
    pass


class InvalidDataError(DataProcessingError):
    """Exception raised when the data is invalid."""
    pass


class EmptyDataError(DataProcessingError):
    """Exception raised when the data is empty."""
    pass


# Validation errors
class ValidationError(URLAnalyzerError):
    """
    Exception raised for validation errors.
    
    This exception is raised when input validation fails. It serves as the base class
    for more specific validation error types like TypeValidationError, ValueValidationError,
    PathValidationError, etc.
    
    Examples:
        Raising a validation error:
            if not isinstance(value, str):
                raise ValidationError(f"Expected string, got {type(value).__name__}")
                
        Handling validation errors:
            try:
                validated_value = validate_input(user_input)
            except ValidationError as e:
                logger.error(f"Invalid input: {e}")
                return None
    """
    pass


class TypeValidationError(ValidationError):
    """Exception raised when a value has an incorrect type."""
    pass


class ValueValidationError(ValidationError):
    """Exception raised when a value is invalid."""
    pass


class SchemaValidationError(ValidationError):
    """Exception raised when data doesn't match a schema."""
    pass


class PathValidationError(ValidationError):
    """Exception raised when a file or directory path is invalid."""
    pass


class URLValidationError(ValidationError):
    """Exception raised when a URL is invalid."""
    pass


# URL analysis errors
class URLAnalysisError(URLAnalyzerError):
    """
    Exception raised for URL analysis errors.
    
    This exception is raised when there's an error analyzing a URL, such as
    when fetching a URL's content, parsing HTML, or classifying a URL.
    It serves as the base class for more specific URL analysis error types like
    URLFetchError and URLClassificationError.
    
    Attributes:
        url: The URL that caused the error (available if provided in details)
        
    Examples:
        Raising a URL analysis error:
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
            except requests.RequestException as e:
                raise URLAnalysisError(f"Failed to analyze URL: {url}", {"url": url, "original_error": str(e)})
                
        Handling URL analysis errors:
            try:
                category, is_sensitive = analyze_url(url)
            except URLFetchError as e:
                logger.warning(f"Could not fetch URL: {e}")
                return "Unknown", False
            except URLClassificationError as e:
                logger.error(f"Could not classify URL: {e}")
                return "Uncategorized", False
            except URLAnalysisError as e:
                logger.error(f"URL analysis failed: {e}")
                return "Error", False
    """
    
    @property
    def url(self) -> Optional[str]:
        """Get the URL that caused the error, if available in details."""
        return self.details.get("url")
    
    pass


class URLFetchError(URLAnalysisError):
    """Exception raised when there's an error fetching a URL."""
    pass


class URLClassificationError(URLAnalysisError):
    """Exception raised when there's an error classifying a URL."""
    pass


# API errors
class APIError(URLAnalyzerError):
    """Exception raised for API errors."""
    pass


class APIConnectionError(APIError):
    """Exception raised when there's an error connecting to an API."""
    pass


class APIAuthenticationError(APIError):
    """Exception raised when there's an authentication error with an API."""
    pass


class APIRateLimitError(APIError):
    """Exception raised when an API rate limit is exceeded."""
    pass


# Reporting errors
class ReportingError(URLAnalyzerError):
    """Exception raised for reporting errors."""
    pass


class TemplateError(ReportingError):
    """Exception raised when there's an error with a report template."""
    pass


class ChartGenerationError(ReportingError):
    """Exception raised when there's an error generating a chart."""
    pass


# Automation errors
class AutomationError(URLAnalyzerError):
    """
    Exception raised for automation errors.
    
    This exception is raised when there's an error with automation features like
    scheduled tasks, scripting, batch processing, or workflow automation.
    
    Examples:
        Raising an automation error:
            if task_id not in tasks:
                raise AutomationError(f"Task with ID {task_id} does not exist")
                
        Handling automation errors:
            try:
                scheduler.run_task(task_id)
            except AutomationError as e:
                logger.error(f"Automation error: {e}")
                return False
    """
    pass


class SchedulerError(AutomationError):
    """Exception raised when there's an error with the task scheduler."""
    pass


class ScriptingError(AutomationError):
    """Exception raised when there's an error with scripting interfaces."""
    pass


class WorkflowError(AutomationError):
    """Exception raised when there's an error with workflow automation."""
    pass


class BatchProcessingError(AutomationError):
    """Exception raised when there's an error with batch processing."""
    pass


# Error handling utilities
def handle_error(error: Exception, 
                 log_level: str = "error", 
                 exit_on_error: bool = False,
                 exit_code: int = 1,
                 show_traceback: bool = False) -> None:
    """
    Handle an error by logging it and optionally exiting the program.
    
    Args:
        error: The exception to handle
        log_level: The log level to use ('debug', 'info', 'warning', 'error', 'critical')
        exit_on_error: Whether to exit the program on error
        exit_code: The exit code to use when exiting
        show_traceback: Whether to show the traceback in the log
    """
    # Get the appropriate logging method
    log_method = getattr(logger, log_level.lower(), logger.error)
    
    # Log the error
    if isinstance(error, URLAnalyzerError):
        log_method(f"{error.__class__.__name__}: {error}")
    else:
        log_method(f"Unexpected error: {error}")
    
    # Log the traceback if requested
    if show_traceback:
        logger.debug(f"Traceback: {''.join(traceback.format_tb(error.__traceback__))}")
    
    # Exit if requested
    if exit_on_error:
        sys.exit(exit_code)


def error_handler(
    error_types: Union[Type[Exception], List[Type[Exception]]] = Exception,
    log_level: str = "error",
    exit_on_error: bool = False,
    exit_code: int = 1,
    show_traceback: bool = False,
    default_return: Any = None,
    recovery_func: Optional[Callable] = None
) -> Callable:
    """
    Decorator for handling errors in functions.
    
    Args:
        error_types: The exception type(s) to catch
        log_level: The log level to use ('debug', 'info', 'warning', 'error', 'critical')
        exit_on_error: Whether to exit the program on error
        exit_code: The exit code to use when exiting
        show_traceback: Whether to show the traceback in the log
        default_return: The default value to return on error
        recovery_func: A function to call for recovery (takes the error as an argument)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                handle_error(
                    e, 
                    log_level=log_level, 
                    exit_on_error=exit_on_error, 
                    exit_code=exit_code,
                    show_traceback=show_traceback
                )
                
                # Call recovery function if provided
                if recovery_func is not None:
                    return recovery_func(e)
                
                # Return default value
                return default_return
        return wrapper
    return decorator


def convert_exception(
    from_exception: Union[Type[Exception], List[Type[Exception]]],
    to_exception: Type[URLAnalyzerError],
    message: Optional[str] = None
) -> Callable:
    """
    Decorator for converting exceptions from one type to another.
    
    Args:
        from_exception: The exception type(s) to convert from
        to_exception: The exception type to convert to
        message: Optional message to use for the new exception
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except from_exception as e:
                # Use the provided message or the original exception message
                error_message = message or str(e)
                
                # Include the original exception details
                details = {
                    'original_exception': e.__class__.__name__,
                    'original_message': str(e)
                }
                
                # Raise the new exception
                raise to_exception(error_message, details)
        return wrapper
    return decorator


# Update the existing ConfigurationError to use our new base class
# This is for backward compatibility
try:
    import config_manager
    config_manager.ConfigurationError = ConfigurationError
except ImportError:
    # config_manager not available in installed package, skip backward compatibility
    pass