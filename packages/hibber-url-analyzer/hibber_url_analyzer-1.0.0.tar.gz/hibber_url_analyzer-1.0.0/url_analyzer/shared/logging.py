"""
Shared Logging Utilities

This module provides logging utilities that are used across multiple domains.
These utilities ensure consistent logging throughout the application.
"""

import logging
import os
import sys
import json
import traceback
from typing import Optional, Dict, Any, Union
from datetime import datetime
import threading
from contextlib import contextmanager


# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Global logger cache to avoid creating multiple loggers for the same name
_logger_cache: Dict[str, logging.Logger] = {}

# Thread-local storage for request context
_context = threading.local()


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with structured fields."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add context information if available
        context = getattr(_context, 'data', {})
        if context:
            log_data['context'] = context
        
        # Add any extra fields from the log record
        extra_fields = {k: v for k, v in record.__dict__.items() 
                       if k not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                                   'pathname', 'filename', 'module', 'lineno', 
                                   'funcName', 'created', 'msecs', 'relativeCreated', 
                                   'thread', 'threadName', 'processName', 'process',
                                   'getMessage', 'exc_info', 'exc_text', 'stack_info']}
        if extra_fields:
            log_data['extra'] = extra_fields
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class ContextualLogger:
    """
    Logger wrapper that supports structured logging and context management.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with additional context."""
        extra = kwargs.copy()
        if hasattr(_context, 'data'):
            extra.update(_context.data)
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with context."""
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, **kwargs)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    If a logger with the given name already exists, it will be returned.
    Otherwise, a new logger will be created.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    if name in _logger_cache:
        return _logger_cache[name]
    
    logger = logging.getLogger(name)
    _logger_cache[name] = logger
    
    return logger


@contextmanager
def log_context(**context_data):
    """
    Context manager for adding structured context to log messages.
    
    Args:
        **context_data: Key-value pairs to add to log context
    """
    if not hasattr(_context, 'data'):
        _context.data = {}
    
    old_context = _context.data.copy()
    _context.data.update(context_data)
    
    try:
        yield
    finally:
        _context.data = old_context


def get_structured_logger(name: str) -> ContextualLogger:
    """
    Get a structured logger with the given name.
    
    Args:
        name: Name of the logger
        
    Returns:
        ContextualLogger instance with structured logging capabilities
    """
    base_logger = get_logger(name)
    return ContextualLogger(base_logger)


def with_error_recovery(func, fallback_value=None, logger=None, context=None):
    """
    Decorator/wrapper for functions that need error recovery.
    
    Args:
        func: Function to wrap
        fallback_value: Value to return if function fails
        logger: Logger to use for error reporting
        context: Additional context for error logging
        
    Returns:
        Function result or fallback_value if error occurs
    """
    if logger is None:
        logger = get_logger(__name__)
    
    try:
        return func()
    except Exception as e:
        error_context = {'function': func.__name__}
        if context:
            error_context.update(context)
        
        log_exception(logger, e, error_context)
        return fallback_value


def configure_logging(
    log_level: Union[int, str] = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    structured: bool = False
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Log level (e.g., logging.INFO, logging.DEBUG)
        log_format: Log format string (ignored if structured=True)
        log_file: Path to log file, or None to disable file logging
        log_to_console: Whether to log to console
        structured: Whether to use structured JSON logging
    """
    # Convert string log level to int if necessary
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), DEFAULT_LOG_LEVEL)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter based on structured logging preference
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(log_format)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)


def log_exception(logger: logging.Logger, exception: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an exception with context.
    
    Args:
        logger: Logger to use
        exception: Exception to log
        context: Additional context to include in the log message
    """
    message = f"Exception: {type(exception).__name__}: {str(exception)}"
    if context:
        message += f" - Context: {context}"
    
    logger.exception(message)


def log_method_call(logger: logging.Logger, method_name: str, args: tuple, kwargs: Dict[str, Any]) -> None:
    """
    Log a method call.
    
    Args:
        logger: Logger to use
        method_name: Name of the method being called
        args: Positional arguments to the method
        kwargs: Keyword arguments to the method
    """
    args_str = ", ".join([str(arg) for arg in args])
    kwargs_str = ", ".join([f"{key}={value}" for key, value in kwargs.items()])
    
    if args_str and kwargs_str:
        params = f"{args_str}, {kwargs_str}"
    elif args_str:
        params = args_str
    elif kwargs_str:
        params = kwargs_str
    else:
        params = ""
    
    logger.debug(f"Calling {method_name}({params})")


def log_method_result(logger: logging.Logger, method_name: str, result: Any) -> None:
    """
    Log a method result.
    
    Args:
        logger: Logger to use
        method_name: Name of the method that returned the result
        result: Result of the method call
    """
    logger.debug(f"{method_name} returned: {result}")


def log_performance(logger: logging.Logger, method_name: str, start_time: datetime, end_time: datetime) -> None:
    """
    Log performance information for a method call.
    
    Args:
        logger: Logger to use
        method_name: Name of the method being measured
        start_time: Start time of the method call
        end_time: End time of the method call
    """
    duration = (end_time - start_time).total_seconds()
    logger.debug(f"{method_name} took {duration:.6f} seconds")


class CentralizedErrorHandler:
    """
    Centralized error handling with retry logic and fallback strategies.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or get_logger(__name__)
        self.error_counts = {}
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, 
                    operation: str = "unknown", retry_count: int = 0) -> bool:
        """
        Handle an error with logging, context, and retry logic.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            operation: Name of the operation that failed
            retry_count: Current retry attempt number
            
        Returns:
            True if the error should be retried, False otherwise
        """
        error_key = f"{operation}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        error_context = {
            'operation': operation,
            'retry_count': retry_count,
            'total_errors': self.error_counts[error_key],
            'error_type': type(error).__name__
        }
        
        if context:
            error_context.update(context)
        
        # Log the error with full context
        log_exception(self.logger, error, error_context)
        
        # Determine if we should retry
        should_retry = (
            retry_count < self.max_retries and
            self._is_retryable_error(error) and
            self.error_counts[error_key] < 10  # Circuit breaker
        )
        
        if should_retry:
            self.logger.info(f"Retrying {operation} (attempt {retry_count + 1}/{self.max_retries})")
        else:
            self.logger.error(f"Max retries exceeded for {operation} or error not retryable")
        
        return should_retry
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            error: The exception to check
            
        Returns:
            True if the error should be retried, False otherwise
        """
        # Network-related errors are typically retryable
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            OSError,
        )
        
        # Import errors and validation errors are typically not retryable
        non_retryable_errors = (
            ImportError,
            ModuleNotFoundError,
            SyntaxError,
            TypeError,
            ValueError,
        )
        
        if isinstance(error, non_retryable_errors):
            return False
        
        if isinstance(error, retryable_errors):
            return True
        
        # Default to not retryable for unknown errors
        return False
    
    def reset_error_counts(self):
        """Reset error counts (useful for testing or periodic cleanup)."""
        self.error_counts.clear()
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get a summary of error counts."""
        return self.error_counts.copy()


# Global error handler instance
_global_error_handler = CentralizedErrorHandler()


def get_error_handler() -> CentralizedErrorHandler:
    """Get the global error handler instance."""
    return _global_error_handler