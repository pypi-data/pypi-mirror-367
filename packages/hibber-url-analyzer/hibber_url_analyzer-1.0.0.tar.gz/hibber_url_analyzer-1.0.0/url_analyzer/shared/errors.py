"""
Shared Error Definitions

This module defines error classes that are used across multiple domains.
These error classes provide a standardized way to handle errors in the domain model.
"""

from typing import Optional, Any, Dict, List


class DomainError(Exception):
    """
    Base class for all domain errors.
    
    Domain errors represent exceptional conditions that occur within the domain model.
    They provide context about what went wrong and why.
    """
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", details: Optional[Dict[str, Any]] = None):
        """
        Initialize a domain error.
        
        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        """
        Convert the error to a string.
        
        Returns:
            String representation of the error
        """
        if self.details:
            return f"{self.code}: {self.message} - {self.details}"
        return f"{self.code}: {self.message}"


class ValidationError(DomainError):
    """
    Error that occurs when validation fails.
    
    Validation errors provide information about which validation rules failed
    and why they failed.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 validation_errors: Optional[List[Dict[str, Any]]] = None,
                 code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        """
        Initialize a validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            validation_errors: List of validation errors
            code: Error code
            details: Additional error details
        """
        self.field = field
        self.validation_errors = validation_errors or []
        
        # Add field and validation errors to details
        details = details or {}
        if field:
            details["field"] = field
        if validation_errors:
            details["validation_errors"] = validation_errors
            
        super().__init__(message, code, details)


class NotFoundError(DomainError):
    """
    Error that occurs when an entity is not found.
    
    Not found errors provide information about which entity was not found
    and what identifier was used to look for it.
    """
    
    def __init__(self, message: str, entity_type: Optional[str] = None, 
                 identifier: Optional[Any] = None,
                 code: str = "NOT_FOUND_ERROR", details: Optional[Dict[str, Any]] = None):
        """
        Initialize a not found error.
        
        Args:
            message: Error message
            entity_type: Type of entity that was not found
            identifier: Identifier used to look for the entity
            code: Error code
            details: Additional error details
        """
        self.entity_type = entity_type
        self.identifier = identifier
        
        # Add entity type and identifier to details
        details = details or {}
        if entity_type:
            details["entity_type"] = entity_type
        if identifier:
            details["identifier"] = str(identifier)
            
        super().__init__(message, code, details)


class AuthorizationError(DomainError):
    """
    Error that occurs when an operation is not authorized.
    
    Authorization errors provide information about which operation was not authorized
    and why it was not authorized.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 resource: Optional[str] = None, user: Optional[str] = None,
                 code: str = "AUTHORIZATION_ERROR", details: Optional[Dict[str, Any]] = None):
        """
        Initialize an authorization error.
        
        Args:
            message: Error message
            operation: Operation that was not authorized
            resource: Resource that was being accessed
            user: User who attempted the operation
            code: Error code
            details: Additional error details
        """
        self.operation = operation
        self.resource = resource
        self.user = user
        
        # Add operation, resource, and user to details
        details = details or {}
        if operation:
            details["operation"] = operation
        if resource:
            details["resource"] = resource
        if user:
            details["user"] = user
            
        super().__init__(message, code, details)