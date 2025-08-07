"""
Error Handler Module

This module provides error handling utilities for the URL Analyzer application,
including rich terminal output for error messages.
"""

import sys
import traceback
from typing import Optional, Dict, Any, List, Union, Type

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.traceback import Traceback
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


class ErrorCategory:
    """Error categories for grouping similar errors."""
    INPUT = "Input Error"
    CONFIG = "Configuration Error"
    NETWORK = "Network Error"
    FILE = "File Error"
    DATA = "Data Error"
    DEPENDENCY = "Dependency Error"
    PERMISSION = "Permission Error"
    VALIDATION = "Validation Error"
    INTERNAL = "Internal Error"
    UNKNOWN = "Unknown Error"


class ErrorSeverity:
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RichErrorHandler:
    """
    Error handler with rich terminal output.
    
    This class provides methods for displaying error messages with rich formatting,
    including error details, suggestions for resolution, and stack traces when appropriate.
    """
    
    def __init__(self, console: Optional['Console'] = None):
        """
        Initialize the error handler.
        
        Args:
            console: Optional Rich Console instance to use
        """
        if not RICH_AVAILABLE:
            logger.warning("Rich library not available, RichErrorHandler will use plain text output")
            self.console = None
            return
            
        self.console = console or Console()
    
    def display_error(self, 
                     message: str, 
                     exception: Optional[Exception] = None,
                     category: str = ErrorCategory.UNKNOWN,
                     severity: str = ErrorSeverity.ERROR,
                     details: Optional[Dict[str, Any]] = None,
                     suggestions: Optional[List[str]] = None,
                     show_traceback: bool = False) -> None:
        """
        Display an error message with rich formatting.
        
        Args:
            message: The main error message
            exception: Optional exception that caused the error
            category: Error category for grouping similar errors
            severity: Error severity level
            details: Optional dictionary with additional error details
            suggestions: Optional list of suggestions for resolving the error
            show_traceback: Whether to show the exception traceback
        """
        if not RICH_AVAILABLE:
            self._display_plain_error(message, exception, category, severity, details, suggestions)
            return
        
        # Determine border style based on severity
        if severity == ErrorSeverity.INFO:
            border_style = "blue"
            icon = "ℹ️"
        elif severity == ErrorSeverity.WARNING:
            border_style = "yellow"
            icon = "⚠️"
        elif severity == ErrorSeverity.CRITICAL:
            border_style = "red bold"
            icon = "🚨"
        else:  # ERROR
            border_style = "red"
            icon = "❌"
        
        # Create content for the panel
        content = []
        
        # Add exception message if available
        if exception:
            exc_message = str(exception)
            if exc_message and exc_message != message:
                content.append(f"[bold]{type(exception).__name__}:[/bold] {exc_message}")
        
        # Add details if available
        if details:
            # Create a table for the details
            table = Table(show_header=False, box=None)
            table.add_column("Key", style="bold")
            table.add_column("Value")
            
            for key, value in details.items():
                table.add_row(key, str(value))
            
            content.append(table)
        
        # Add suggestions if available
        if suggestions:
            content.append("[bold]Suggestions:[/bold]")
            for i, suggestion in enumerate(suggestions, 1):
                content.append(f"{i}. {suggestion}")
        
        # Add traceback if requested
        if show_traceback and exception:
            content.append("[bold]Traceback:[/bold]")
            content.append(Traceback.from_exception(
                type(exception), 
                exception, 
                exception.__traceback__,
                show_locals=True,
                width=self.console.width - 10
            ))
        
        # Create the panel
        title = f"{icon} {category}: {message}"
        
        # Join content items with newlines
        panel_content = "\n\n".join([str(item) for item in content]) if content else ""
        
        panel = Panel(
            panel_content,
            title=title,
            border_style=border_style,
            padding=(1, 2)
        )
        
        # Print the panel
        self.console.print(panel)
        
        # Log the error
        log_message = f"{category}: {message}"
        if exception:
            log_message += f" - {type(exception).__name__}: {str(exception)}"
        
        if severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        else:  # ERROR
            logger.error(log_message)
    
    def _display_plain_error(self, 
                           message: str, 
                           exception: Optional[Exception] = None,
                           category: str = ErrorCategory.UNKNOWN,
                           severity: str = ErrorSeverity.ERROR,
                           details: Optional[Dict[str, Any]] = None,
                           suggestions: Optional[List[str]] = None) -> None:
        """
        Display an error message in plain text (fallback when Rich is not available).
        
        Args:
            message: The main error message
            exception: Optional exception that caused the error
            category: Error category for grouping similar errors
            severity: Error severity level
            details: Optional dictionary with additional error details
            suggestions: Optional list of suggestions for resolving the error
        """
        # Create header based on severity
        if severity == ErrorSeverity.INFO:
            header = "INFO"
        elif severity == ErrorSeverity.WARNING:
            header = "WARNING"
        elif severity == ErrorSeverity.CRITICAL:
            header = "CRITICAL ERROR"
        else:  # ERROR
            header = "ERROR"
        
        # Print header and message
        print(f"\n{header} - {category}: {message}")
        
        # Print exception if available
        if exception:
            print(f"{type(exception).__name__}: {str(exception)}")
        
        # Print details if available
        if details:
            print("\nDetails:")
            for key, value in details.items():
                print(f"  {key}: {value}")
        
        # Print suggestions if available
        if suggestions:
            print("\nSuggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print()  # Add a blank line at the end
        
        # Log the error
        log_message = f"{category}: {message}"
        if exception:
            log_message += f" - {type(exception).__name__}: {str(exception)}"
        
        if severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        else:  # ERROR
            logger.error(log_message)


# Create a global error handler instance
error_handler = RichErrorHandler()


def display_error(message: str, 
                 exception: Optional[Exception] = None,
                 category: str = ErrorCategory.UNKNOWN,
                 severity: str = ErrorSeverity.ERROR,
                 details: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None,
                 show_traceback: bool = False) -> None:
    """
    Display an error message with rich formatting.
    
    This is a convenience function that uses the global error handler instance.
    
    Args:
        message: The main error message
        exception: Optional exception that caused the error
        category: Error category for grouping similar errors
        severity: Error severity level
        details: Optional dictionary with additional error details
        suggestions: Optional list of suggestions for resolving the error
        show_traceback: Whether to show the exception traceback
    """
    error_handler.display_error(
        message, 
        exception, 
        category, 
        severity, 
        details, 
        suggestions, 
        show_traceback
    )


def handle_exception(exception: Exception, 
                    message: Optional[str] = None,
                    category: str = ErrorCategory.UNKNOWN,
                    severity: str = ErrorSeverity.ERROR,
                    details: Optional[Dict[str, Any]] = None,
                    suggestions: Optional[List[str]] = None,
                    show_traceback: bool = True,
                    exit_code: Optional[int] = None) -> None:
    """
    Handle an exception by displaying an error message and optionally exiting.
    
    Args:
        exception: The exception to handle
        message: Optional custom message (if not provided, uses str(exception))
        category: Error category for grouping similar errors
        severity: Error severity level
        details: Optional dictionary with additional error details
        suggestions: Optional list of suggestions for resolving the error
        show_traceback: Whether to show the exception traceback
        exit_code: If provided, exit the program with this code after displaying the error
    """
    # Use the exception message if no custom message is provided
    if message is None:
        message = str(exception)
    
    # Display the error
    display_error(
        message, 
        exception, 
        category, 
        severity, 
        details, 
        suggestions, 
        show_traceback
    )
    
    # Exit if requested
    if exit_code is not None:
        sys.exit(exit_code)


# Exception handler decorator
def exception_handler(category: str = ErrorCategory.UNKNOWN,
                     severity: str = ErrorSeverity.ERROR,
                     show_traceback: bool = False,
                     exit_on_error: bool = False,
                     exit_code: int = 1):
    """
    Decorator for handling exceptions in functions.
    
    Args:
        category: Error category for grouping similar errors
        severity: Error severity level
        show_traceback: Whether to show the exception traceback
        exit_on_error: Whether to exit the program on error
        exit_code: Exit code to use if exiting on error
    
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get function name for the error message
                func_name = getattr(func, "__name__", "function")
                
                # Handle the exception
                handle_exception(
                    e,
                    message=f"Error in {func_name}: {str(e)}",
                    category=category,
                    severity=severity,
                    show_traceback=show_traceback,
                    exit_code=exit_code if exit_on_error else None
                )
                
                # Return None if not exiting
                return None
        return wrapper
    return decorator