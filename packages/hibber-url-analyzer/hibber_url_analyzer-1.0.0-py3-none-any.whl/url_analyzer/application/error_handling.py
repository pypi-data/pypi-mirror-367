"""
Application Layer Error Handling

This module defines interfaces and use cases for error handling in the URL Analyzer application.
It includes interfaces for error registry, error handling strategy, and error reporting.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Type, Union

from url_analyzer.domain.errors import (
    DomainError, ErrorContext, ErrorSeverity, ErrorCategory,
    ValidationError, NetworkError, ClassificationError, StorageError
)


class ErrorRegistry(ABC):
    """
    Interface for error registry.
    
    The error registry is responsible for storing and retrieving errors.
    It provides a centralized location for error management.
    """
    
    @abstractmethod
    def register_error(self, error: DomainError) -> str:
        """
        Register an error in the registry.
        
        Args:
            error: The error to register
            
        Returns:
            The error ID
        """
        pass
    
    @abstractmethod
    def get_error(self, error_id: str) -> Optional[DomainError]:
        """
        Get an error by ID.
        
        Args:
            error_id: The error ID
            
        Returns:
            The error if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_errors_by_category(self, category: ErrorCategory) -> List[DomainError]:
        """
        Get errors by category.
        
        Args:
            category: The error category
            
        Returns:
            List of errors in the specified category
        """
        pass
    
    @abstractmethod
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[DomainError]:
        """
        Get errors by severity.
        
        Args:
            severity: The error severity
            
        Returns:
            List of errors with the specified severity
        """
        pass
    
    @abstractmethod
    def get_errors_by_component(self, component: str) -> List[DomainError]:
        """
        Get errors by component.
        
        Args:
            component: The component name
            
        Returns:
            List of errors from the specified component
        """
        pass
    
    @abstractmethod
    def clear_errors(self) -> None:
        """Clear all errors from the registry."""
        pass
    
    @abstractmethod
    def get_error_count(self) -> int:
        """
        Get the number of errors in the registry.
        
        Returns:
            The number of errors
        """
        pass


class ErrorHandler(ABC):
    """
    Interface for error handler.
    
    The error handler is responsible for handling errors in a consistent way.
    It provides methods for handling different types of errors.
    """
    
    @abstractmethod
    def handle_error(self, error: DomainError) -> None:
        """
        Handle an error.
        
        Args:
            error: The error to handle
        """
        pass
    
    @abstractmethod
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
        pass


class ErrorReporter(ABC):
    """
    Interface for error reporter.
    
    The error reporter is responsible for reporting errors to external systems.
    It provides methods for reporting errors in different formats.
    """
    
    @abstractmethod
    def report_error(self, error: DomainError) -> None:
        """
        Report an error.
        
        Args:
            error: The error to report
        """
        pass
    
    @abstractmethod
    def report_errors(self, errors: List[DomainError]) -> None:
        """
        Report multiple errors.
        
        Args:
            errors: The errors to report
        """
        pass
    
    @abstractmethod
    def generate_error_report(self, errors: List[DomainError], format: str = 'json') -> str:
        """
        Generate an error report.
        
        Args:
            errors: The errors to include in the report
            format: The report format (json, html, text)
            
        Returns:
            The generated report
        """
        pass


class ErrorRecoveryStrategy(ABC):
    """
    Interface for error recovery strategy.
    
    The error recovery strategy is responsible for recovering from errors.
    It provides methods for attempting recovery from different types of errors.
    """
    
    @abstractmethod
    def can_recover(self, error: DomainError) -> bool:
        """
        Check if recovery is possible for an error.
        
        Args:
            error: The error to check
            
        Returns:
            True if recovery is possible, False otherwise
        """
        pass
    
    @abstractmethod
    def attempt_recovery(self, error: DomainError) -> bool:
        """
        Attempt to recover from an error.
        
        Args:
            error: The error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def register_recovery_strategy(
        self,
        error_type: Type[DomainError],
        strategy: Callable[[DomainError], bool]
    ) -> None:
        """
        Register a recovery strategy for an error type.
        
        Args:
            error_type: The error type
            strategy: The recovery strategy function
        """
        pass


# Use cases

class RegisterErrorUseCase:
    """
    Use case for registering an error.
    
    This use case orchestrates the registration of an error, including
    handling it and reporting it.
    """
    
    def __init__(
        self,
        error_registry: ErrorRegistry,
        error_handler: ErrorHandler,
        error_reporter: ErrorReporter
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            error_registry: Registry for storing errors
            error_handler: Handler for processing errors
            error_reporter: Reporter for reporting errors
        """
        self.error_registry = error_registry
        self.error_handler = error_handler
        self.error_reporter = error_reporter
    
    def execute(self, error: DomainError) -> str:
        """
        Execute the use case.
        
        Args:
            error: The error to register
            
        Returns:
            The error ID
        """
        # Handle the error
        self.error_handler.handle_error(error)
        
        # Register the error
        error_id = self.error_registry.register_error(error)
        
        # Report the error
        self.error_reporter.report_error(error)
        
        return error_id


class HandleExceptionUseCase:
    """
    Use case for handling an exception.
    
    This use case orchestrates the handling of an exception, including
    converting it to a domain error, registering it, and reporting it.
    """
    
    def __init__(
        self,
        error_registry: ErrorRegistry,
        error_handler: ErrorHandler,
        error_reporter: ErrorReporter
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            error_registry: Registry for storing errors
            error_handler: Handler for processing errors
            error_reporter: Reporter for reporting errors
        """
        self.error_registry = error_registry
        self.error_handler = error_handler
        self.error_reporter = error_reporter
    
    def execute(
        self,
        exception: Exception,
        context: ErrorContext,
        category: ErrorCategory = ErrorCategory.UNEXPECTED,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> str:
        """
        Execute the use case.
        
        Args:
            exception: The exception to handle
            context: The error context
            category: The error category
            severity: The error severity
            
        Returns:
            The error ID
        """
        # Convert the exception to a domain error
        error = self.error_handler.handle_exception(
            exception=exception,
            context=context,
            category=category,
            severity=severity
        )
        
        # Register the error
        error_id = self.error_registry.register_error(error)
        
        # Report the error
        self.error_reporter.report_error(error)
        
        return error_id


class AttemptErrorRecoveryUseCase:
    """
    Use case for attempting error recovery.
    
    This use case orchestrates the attempt to recover from an error.
    """
    
    def __init__(
        self,
        error_registry: ErrorRegistry,
        error_recovery_strategy: ErrorRecoveryStrategy
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            error_registry: Registry for storing errors
            error_recovery_strategy: Strategy for recovering from errors
        """
        self.error_registry = error_registry
        self.error_recovery_strategy = error_recovery_strategy
    
    def execute(self, error_id: str) -> bool:
        """
        Execute the use case.
        
        Args:
            error_id: The ID of the error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # Get the error
        error = self.error_registry.get_error(error_id)
        
        if not error:
            return False
        
        # Check if recovery is possible
        if not self.error_recovery_strategy.can_recover(error):
            return False
        
        # Attempt recovery
        return self.error_recovery_strategy.attempt_recovery(error)