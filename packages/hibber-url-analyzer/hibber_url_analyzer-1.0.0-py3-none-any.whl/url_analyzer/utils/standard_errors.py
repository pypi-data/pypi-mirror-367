"""
Standardized Error Handling Module

This module provides standardized error handling patterns and utilities
for consistent error management across all URL Analyzer packages.
"""

import functools
import logging
from typing import Optional, Dict, Any, List, Callable, Type, Union
from .error_handler import RichErrorHandler, ErrorCategory, ErrorSeverity
from .logging import get_logger

# Global error handler instance
_error_handler = RichErrorHandler()
logger = get_logger(__name__)


class URLAnalyzerError(Exception):
    """Base exception class for URL Analyzer."""
    
    def __init__(self, message: str, category: str = ErrorCategory.UNKNOWN, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.details = details or {}


class ConfigurationError(URLAnalyzerError):
    """Raised when there's a configuration-related error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.CONFIG, details)


class DataProcessingError(URLAnalyzerError):
    """Raised when there's a data processing error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.DATA, details)


class NetworkError(URLAnalyzerError):
    """Raised when there's a network-related error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.NETWORK, details)


class ValidationError(URLAnalyzerError):
    """Raised when there's a validation error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.VALIDATION, details)


def handle_error(exception: Exception, 
                context: str = "",
                severity: str = ErrorSeverity.ERROR,
                suggestions: Optional[List[str]] = None,
                show_traceback: bool = False) -> None:
    """
    Handle an exception using standardized error handling.
    
    Args:
        exception: The exception to handle
        context: Additional context about where the error occurred
        severity: Error severity level
        suggestions: Optional list of suggestions for resolving the error
        show_traceback: Whether to show the exception traceback
    """
    if isinstance(exception, URLAnalyzerError):
        category = exception.category
        details = exception.details
        message = f"{context}: {exception.message}" if context else exception.message
    else:
        category = ErrorCategory.UNKNOWN
        details = {"exception_type": type(exception).__name__}
        message = f"{context}: {str(exception)}" if context else str(exception)
    
    _error_handler.display_error(
        message=message,
        exception=exception,
        category=category,
        severity=severity,
        details=details,
        suggestions=suggestions,
        show_traceback=show_traceback
    )
    
    # Log the error
    logger.error(f"[{category}] {message}", exc_info=show_traceback)


def error_handler(category: str = ErrorCategory.UNKNOWN,
                 severity: str = ErrorSeverity.ERROR,
                 reraise: bool = True,
                 suggestions: Optional[List[str]] = None) -> Callable:
    """
    Decorator for standardized error handling in functions.
    
    Args:
        category: Error category for the function
        severity: Default severity level for errors
        reraise: Whether to reraise the exception after handling
        suggestions: Default suggestions for error resolution
    
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = f"Error in {func.__module__}.{func.__name__}"
                handle_error(
                    exception=e,
                    context=context,
                    severity=severity,
                    suggestions=suggestions,
                    show_traceback=severity == ErrorSeverity.CRITICAL
                )
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


def safe_execute(func: Callable, 
                *args, 
                default_return=None,
                context: str = "",
                suggestions: Optional[List[str]] = None,
                **kwargs) -> Any:
    """
    Safely execute a function with standardized error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default_return: Value to return if function fails
        context: Context description for error reporting
        suggestions: Suggestions for error resolution
        **kwargs: Keyword arguments for the function
    
    Returns:
        Function result or default_return if function fails
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(
            exception=e,
            context=context or f"Error executing {func.__name__}",
            suggestions=suggestions
        )
        return default_return


def validate_input(value: Any, 
                  validator: Callable[[Any], bool],
                  error_message: str,
                  suggestions: Optional[List[str]] = None) -> None:
    """
    Validate input using a validator function.
    
    Args:
        value: Value to validate
        validator: Function that returns True if value is valid
        error_message: Error message if validation fails
        suggestions: Suggestions for fixing validation errors
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        if not validator(value):
            raise ValidationError(
                error_message,
                details={"value": str(value), "validator": validator.__name__}
            )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            f"Validation failed: {error_message}",
            details={"value": str(value), "validation_error": str(e)}
        )


# Common error suggestions
COMMON_SUGGESTIONS = {
    "config": [
        "Check your configuration file syntax",
        "Verify all required configuration keys are present",
        "Ensure configuration values are of the correct type"
    ],
    "network": [
        "Check your internet connection",
        "Verify the URL is accessible",
        "Check if a proxy or firewall is blocking the request"
    ],
    "file": [
        "Check if the file exists and is readable",
        "Verify file permissions",
        "Ensure the file path is correct"
    ],
    "data": [
        "Check the data format and structure",
        "Verify the data contains required fields",
        "Ensure the data is not corrupted"
    ]
}