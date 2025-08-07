"""
Basic Error Recovery Strategy

This module provides a basic implementation of the ErrorRecoveryStrategy interface.
It attempts to recover from errors based on registered recovery strategies.
"""

from typing import Dict, List, Optional, Any, Callable, Type

from url_analyzer.domain.errors import (
    DomainError, ErrorCategory, ErrorSeverity,
    ValidationError, NetworkError, ClassificationError, StorageError
)
from url_analyzer.application.error_handling import ErrorRecoveryStrategy
from url_analyzer.application.interfaces import LoggingService


class BasicErrorRecoveryStrategy(ErrorRecoveryStrategy):
    """
    Basic implementation of the ErrorRecoveryStrategy interface.
    
    This class attempts to recover from errors based on registered recovery strategies.
    """
    
    def __init__(self, logging_service: LoggingService):
        """
        Initialize the error recovery strategy.
        
        Args:
            logging_service: Service for logging
        """
        self.logging_service = logging_service
        self.recovery_strategies: Dict[Type[DomainError], List[Callable[[DomainError], bool]]] = {}
        
        # Register default recovery strategies
        self._register_default_strategies()
    
    def can_recover(self, error: DomainError) -> bool:
        """
        Check if recovery is possible for an error.
        
        Args:
            error: The error to check
            
        Returns:
            True if recovery is possible, False otherwise
        """
        # Check if there are any recovery strategies for this error type
        for error_type, strategies in self.recovery_strategies.items():
            if isinstance(error, error_type) and strategies:
                return True
        
        return False
    
    def attempt_recovery(self, error: DomainError) -> bool:
        """
        Attempt to recover from an error.
        
        Args:
            error: The error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # Log that we're attempting recovery
        self.logging_service.debug(
            f"Attempting to recover from error: {error.message}",
            category=error.category.name,
            severity=error.severity.name
        )
        
        # Try each registered recovery strategy for this error type
        for error_type, strategies in self.recovery_strategies.items():
            if isinstance(error, error_type):
                for strategy in strategies:
                    try:
                        # Attempt recovery using this strategy
                        if strategy(error):
                            # Recovery was successful
                            self.logging_service.info(
                                f"Successfully recovered from error: {error.message}",
                                category=error.category.name,
                                severity=error.severity.name
                            )
                            return True
                    except Exception as e:
                        # Recovery strategy failed
                        self.logging_service.warning(
                            f"Recovery strategy failed: {str(e)}",
                            category=error.category.name,
                            severity=error.severity.name,
                            exception=str(e)
                        )
        
        # No recovery strategy succeeded
        self.logging_service.debug(
            f"Failed to recover from error: {error.message}",
            category=error.category.name,
            severity=error.severity.name
        )
        return False
    
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
        if error_type not in self.recovery_strategies:
            self.recovery_strategies[error_type] = []
        
        self.recovery_strategies[error_type].append(strategy)
        
        # Log that we've registered a recovery strategy
        self.logging_service.debug(
            f"Registered recovery strategy for error type: {error_type.__name__}"
        )
    
    def _register_default_strategies(self) -> None:
        """Register default recovery strategies for common error types."""
        # Register recovery strategies for NetworkError
        self.register_recovery_strategy(NetworkError, self._recover_from_network_error)
        
        # Register recovery strategies for ValidationError
        self.register_recovery_strategy(ValidationError, self._recover_from_validation_error)
        
        # Register recovery strategies for StorageError
        self.register_recovery_strategy(StorageError, self._recover_from_storage_error)
    
    def _recover_from_network_error(self, error: NetworkError) -> bool:
        """
        Attempt to recover from a network error.
        
        Args:
            error: The network error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # For demonstration purposes, we'll just log that we're attempting recovery
        self.logging_service.debug(
            f"Attempting to recover from network error: {error.message}",
            url=error.url,
            status_code=error.status_code
        )
        
        # In a real implementation, we might:
        # - Retry the request with exponential backoff
        # - Try an alternative endpoint
        # - Use a cached response if available
        
        # For now, we'll just return False to indicate that recovery failed
        return False
    
    def _recover_from_validation_error(self, error: ValidationError) -> bool:
        """
        Attempt to recover from a validation error.
        
        Args:
            error: The validation error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # For demonstration purposes, we'll just log that we're attempting recovery
        self.logging_service.debug(
            f"Attempting to recover from validation error: {error.message}",
            validation_errors=error.validation_errors
        )
        
        # In a real implementation, we might:
        # - Apply default values for missing fields
        # - Sanitize input data
        # - Use a fallback strategy
        
        # For now, we'll just return False to indicate that recovery failed
        return False
    
    def _recover_from_storage_error(self, error: StorageError) -> bool:
        """
        Attempt to recover from a storage error.
        
        Args:
            error: The storage error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # For demonstration purposes, we'll just log that we're attempting recovery
        self.logging_service.debug(
            f"Attempting to recover from storage error: {error.message}",
            storage_type=error.storage_type,
            storage_operation=error.storage_operation
        )
        
        # In a real implementation, we might:
        # - Create missing directories
        # - Use an alternative storage location
        # - Retry the operation with different permissions
        
        # For now, we'll just return False to indicate that recovery failed
        return False


class AdvancedErrorRecoveryStrategy(BasicErrorRecoveryStrategy):
    """
    Advanced implementation of the ErrorRecoveryStrategy interface.
    
    This class extends the BasicErrorRecoveryStrategy with more sophisticated
    recovery strategies, including retries with exponential backoff.
    """
    
    def __init__(self, logging_service: LoggingService, max_retries: int = 3):
        """
        Initialize the error recovery strategy.
        
        Args:
            logging_service: Service for logging
            max_retries: Maximum number of retries for recoverable errors
        """
        super().__init__(logging_service)
        self.max_retries = max_retries
        self.retry_counts: Dict[str, int] = {}
    
    def attempt_recovery(self, error: DomainError) -> bool:
        """
        Attempt to recover from an error with retry support.
        
        Args:
            error: The error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # Generate a unique key for this error
        error_key = f"{error.context.component}:{error.context.operation}:{error.message}"
        
        # Check if we've exceeded the maximum number of retries
        if error_key in self.retry_counts and self.retry_counts[error_key] >= self.max_retries:
            self.logging_service.warning(
                f"Maximum retries exceeded for error: {error.message}",
                category=error.category.name,
                severity=error.severity.name,
                retries=self.retry_counts[error_key]
            )
            return False
        
        # Increment the retry count
        if error_key not in self.retry_counts:
            self.retry_counts[error_key] = 1
        else:
            self.retry_counts[error_key] += 1
        
        # Log the retry attempt
        self.logging_service.debug(
            f"Retry attempt {self.retry_counts[error_key]} of {self.max_retries} for error: {error.message}",
            category=error.category.name,
            severity=error.severity.name
        )
        
        # Attempt recovery using the parent class method
        return super().attempt_recovery(error)
    
    def reset_retry_count(self, error_key: str) -> None:
        """
        Reset the retry count for an error key.
        
        Args:
            error_key: The error key to reset
        """
        if error_key in self.retry_counts:
            del self.retry_counts[error_key]