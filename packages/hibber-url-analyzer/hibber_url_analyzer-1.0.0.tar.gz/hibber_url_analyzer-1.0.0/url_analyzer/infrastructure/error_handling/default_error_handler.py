"""
Default Error Handler

This module provides a default implementation of the ErrorHandler interface.
It handles errors in a consistent way, including logging them and converting exceptions to domain errors.
"""

import traceback
from typing import Dict, List, Optional, Any

from url_analyzer.domain.errors import (
    DomainError, ErrorContext, ErrorSeverity, ErrorCategory,
    ValidationError, NetworkError, ClassificationError, StorageError
)
from url_analyzer.application.error_handling import ErrorHandler
from url_analyzer.application.interfaces import LoggingService


class DefaultErrorHandler(ErrorHandler):
    """
    Default implementation of the ErrorHandler interface.
    
    This class handles errors in a consistent way, including logging them
    and converting exceptions to domain errors.
    """
    
    def __init__(self, logging_service: LoggingService):
        """
        Initialize the error handler.
        
        Args:
            logging_service: Service for logging errors
        """
        self.logging_service = logging_service
    
    def handle_error(self, error: DomainError) -> None:
        """
        Handle an error.
        
        Args:
            error: The error to handle
        """
        # Log the error with appropriate severity
        if error.severity == ErrorSeverity.DEBUG:
            self.logging_service.debug(
                f"[{error.category.name}] {error.message}",
                error_code=error.error_code,
                component=error.context.component,
                operation=error.context.operation
            )
        elif error.severity == ErrorSeverity.INFO:
            self.logging_service.info(
                f"[{error.category.name}] {error.message}",
                error_code=error.error_code,
                component=error.context.component,
                operation=error.context.operation
            )
        elif error.severity == ErrorSeverity.WARNING:
            self.logging_service.warning(
                f"[{error.category.name}] {error.message}",
                error_code=error.error_code,
                component=error.context.component,
                operation=error.context.operation
            )
        elif error.severity == ErrorSeverity.ERROR:
            self.logging_service.error(
                f"[{error.category.name}] {error.message}",
                error_code=error.error_code,
                component=error.context.component,
                operation=error.context.operation
            )
        elif error.severity == ErrorSeverity.CRITICAL:
            self.logging_service.critical(
                f"[{error.category.name}] {error.message}",
                error_code=error.error_code,
                component=error.context.component,
                operation=error.context.operation
            )
    
    def handle_exception(
        self,
        exception: Exception,
        context: ErrorContext,
        category: ErrorCategory = ErrorCategory.UNEXPECTED,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> DomainError:
        """
        Handle an exception by converting it to a domain error.
        
        Args:
            exception: The exception to handle
            context: The error context
            category: The error category
            severity: The error severity
            
        Returns:
            The created domain error
        """
        # Get the stack trace
        stack_trace = traceback.format_exc()
        
        # Create a domain error based on the exception type
        if isinstance(exception, ValueError) and category == ErrorCategory.VALIDATION:
            error = ValidationError(
                message=str(exception),
                context=context,
                severity=severity,
                original_exception=exception,
                stack_trace=stack_trace
            )
        elif isinstance(exception, (ConnectionError, TimeoutError)) or category == ErrorCategory.NETWORK:
            error = NetworkError(
                message=str(exception),
                context=context,
                severity=severity,
                original_exception=exception,
                stack_trace=stack_trace
            )
        elif category == ErrorCategory.CLASSIFICATION:
            error = ClassificationError(
                message=str(exception),
                context=context,
                severity=severity,
                original_exception=exception,
                stack_trace=stack_trace
            )
        elif category == ErrorCategory.STORAGE:
            error = StorageError(
                message=str(exception),
                context=context,
                severity=severity,
                original_exception=exception,
                stack_trace=stack_trace
            )
        else:
            # Generic domain error
            error = DomainError(
                message=str(exception),
                context=context,
                category=category,
                severity=severity,
                original_exception=exception,
                stack_trace=stack_trace
            )
        
        # Add suggestions based on the error type
        self._add_suggestions(error)
        
        # Handle the error (log it)
        self.handle_error(error)
        
        return error
    
    def _add_suggestions(self, error: DomainError) -> None:
        """
        Add suggestions to an error based on its type and category.
        
        Args:
            error: The error to add suggestions to
        """
        if isinstance(error, ValidationError):
            error.add_suggestion("Check the input data for validation errors")
            error.add_suggestion("Ensure all required fields are provided")
        
        elif isinstance(error, NetworkError):
            error.add_suggestion("Check your internet connection")
            error.add_suggestion("Verify that the URL is correct")
            error.add_suggestion("Try again later as the server might be temporarily unavailable")
        
        elif isinstance(error, ClassificationError):
            error.add_suggestion("Check the URL format")
            error.add_suggestion("Verify that the classification patterns are correctly defined")
        
        elif isinstance(error, StorageError):
            error.add_suggestion("Check file permissions")
            error.add_suggestion("Ensure the storage location exists and is accessible")
            error.add_suggestion("Verify that there is enough disk space")
        
        elif error.category == ErrorCategory.CONFIGURATION:
            error.add_suggestion("Check the configuration file for errors")
            error.add_suggestion("Ensure all required configuration settings are provided")
        
        elif error.category == ErrorCategory.TIMEOUT:
            error.add_suggestion("Increase the timeout value")
            error.add_suggestion("Try again later when the system is less busy")
        
        # Add generic suggestions for all errors
        error.add_suggestion("Check the logs for more details")
        
        # Add severity-specific suggestions
        if error.severity == ErrorSeverity.CRITICAL:
            error.add_suggestion("Contact system administrator immediately")


class ContextAwareErrorHandler(DefaultErrorHandler):
    """
    Context-aware implementation of the ErrorHandler interface.
    
    This class extends the DefaultErrorHandler with context-aware error handling,
    including enriching error messages with context information.
    """
    
    def handle_error(self, error: DomainError) -> None:
        """
        Handle an error with context awareness.
        
        Args:
            error: The error to handle
        """
        # Enrich the error message with context information
        enriched_message = self._enrich_message(error)
        
        # Create a new error with the enriched message
        enriched_error = DomainError(
            message=enriched_message,
            context=error.context,
            category=error.category,
            severity=error.severity,
            error_code=error.error_code,
            original_exception=error.original_exception,
            stack_trace=error.stack_trace,
            suggestions=error.suggestions
        )
        
        # Handle the enriched error using the parent class method
        super().handle_error(enriched_error)
    
    def _enrich_message(self, error: DomainError) -> str:
        """
        Enrich an error message with context information.
        
        Args:
            error: The error to enrich
            
        Returns:
            The enriched error message
        """
        # Start with the original message
        message = error.message
        
        # Add context information
        context_info = []
        
        # Add component and operation
        context_info.append(f"Component: {error.context.component}")
        context_info.append(f"Operation: {error.context.operation}")
        
        # Add input data if available
        if error.context.input_data:
            input_data_str = ", ".join(f"{k}={v}" for k, v in error.context.input_data.items())
            context_info.append(f"Input: {input_data_str}")
        
        # Add environment data if available
        if error.context.environment:
            env_data_str = ", ".join(f"{k}={v}" for k, v in error.context.environment.items())
            context_info.append(f"Environment: {env_data_str}")
        
        # Add error code if available
        if error.error_code:
            context_info.append(f"Error Code: {error.error_code}")
        
        # Add timestamp
        context_info.append(f"Time: {error.context.timestamp.isoformat()}")
        
        # Combine the message with context information
        if context_info:
            message = f"{message} [{' | '.join(context_info)}]"
        
        return message