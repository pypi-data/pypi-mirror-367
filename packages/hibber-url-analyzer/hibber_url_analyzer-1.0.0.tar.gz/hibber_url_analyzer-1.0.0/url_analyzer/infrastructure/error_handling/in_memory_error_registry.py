"""
In-Memory Error Registry

This module provides an in-memory implementation of the ErrorRegistry interface.
It stores errors in memory and provides methods for retrieving them by various criteria.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from url_analyzer.domain.errors import DomainError, ErrorCategory, ErrorSeverity
from url_analyzer.application.error_handling import ErrorRegistry


class InMemoryErrorRegistry(ErrorRegistry):
    """
    In-memory implementation of the ErrorRegistry interface.
    
    This class stores errors in memory and provides methods for retrieving them by various criteria.
    """
    
    def __init__(self, max_errors: int = 1000):
        """
        Initialize the error registry.
        
        Args:
            max_errors: Maximum number of errors to store (default: 1000)
        """
        self.errors: Dict[str, DomainError] = {}
        self.max_errors = max_errors
    
    def register_error(self, error: DomainError) -> str:
        """
        Register an error in the registry.
        
        Args:
            error: The error to register
            
        Returns:
            The error ID
        """
        # Generate a unique ID for the error
        error_id = str(uuid.uuid4())
        
        # Store the error
        self.errors[error_id] = error
        
        # If we've exceeded the maximum number of errors, remove the oldest ones
        if len(self.errors) > self.max_errors:
            # Sort errors by timestamp (oldest first)
            sorted_errors = sorted(
                self.errors.items(),
                key=lambda item: item[1].context.timestamp
            )
            
            # Remove the oldest errors
            num_to_remove = len(self.errors) - self.max_errors
            for i in range(num_to_remove):
                del self.errors[sorted_errors[i][0]]
        
        return error_id
    
    def get_error(self, error_id: str) -> Optional[DomainError]:
        """
        Get an error by ID.
        
        Args:
            error_id: The error ID
            
        Returns:
            The error if found, None otherwise
        """
        return self.errors.get(error_id)
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[DomainError]:
        """
        Get errors by category.
        
        Args:
            category: The error category
            
        Returns:
            List of errors in the specified category
        """
        return [
            error for error in self.errors.values()
            if error.category == category
        ]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[DomainError]:
        """
        Get errors by severity.
        
        Args:
            severity: The error severity
            
        Returns:
            List of errors with the specified severity
        """
        return [
            error for error in self.errors.values()
            if error.severity == severity
        ]
    
    def get_errors_by_component(self, component: str) -> List[DomainError]:
        """
        Get errors by component.
        
        Args:
            component: The component name
            
        Returns:
            List of errors from the specified component
        """
        return [
            error for error in self.errors.values()
            if error.context.component == component
        ]
    
    def clear_errors(self) -> None:
        """Clear all errors from the registry."""
        self.errors.clear()
    
    def get_error_count(self) -> int:
        """
        Get the number of errors in the registry.
        
        Returns:
            The number of errors
        """
        return len(self.errors)
    
    def get_all_errors(self) -> List[DomainError]:
        """
        Get all errors in the registry.
        
        Returns:
            List of all errors
        """
        return list(self.errors.values())
    
    def get_errors_since(self, timestamp: datetime) -> List[DomainError]:
        """
        Get errors that occurred since a specific timestamp.
        
        Args:
            timestamp: The timestamp to filter by
            
        Returns:
            List of errors that occurred since the specified timestamp
        """
        return [
            error for error in self.errors.values()
            if error.context.timestamp >= timestamp
        ]
    
    def get_errors_by_message_contains(self, substring: str) -> List[DomainError]:
        """
        Get errors whose message contains a specific substring.
        
        Args:
            substring: The substring to search for
            
        Returns:
            List of errors whose message contains the specified substring
        """
        return [
            error for error in self.errors.values()
            if substring.lower() in error.message.lower()
        ]