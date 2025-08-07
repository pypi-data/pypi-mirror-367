"""
Shared Domain Package

This package contains shared domain models, interfaces, error definitions,
logging utilities, and validation utilities that are used across multiple domains.
"""

# Import shared components with explicit imports and graceful degradation
import logging

# Domain components
try:
    from url_analyzer.shared.domain import Entity, ValueObject, Identifier
except ImportError as e:
    logging.getLogger(__name__).warning(f"Could not import domain components: {e}")
    Entity = ValueObject = Identifier = None

# Interface components
try:
    from url_analyzer.shared.interfaces import Repository, Service
except ImportError as e:
    logging.getLogger(__name__).warning(f"Could not import interface components: {e}")
    Repository = Service = None

# Error components
try:
    from url_analyzer.shared.errors import (
        DomainError, ValidationError, NotFoundError, AuthorizationError
    )
except ImportError as e:
    logging.getLogger(__name__).warning(f"Could not import error components: {e}")
    DomainError = ValidationError = NotFoundError = AuthorizationError = None

# Logging components
try:
    from url_analyzer.shared.logging import get_logger, configure_logging
except ImportError as e:
    logging.getLogger(__name__).warning(f"Could not import logging components: {e}")
    get_logger = configure_logging = None

# Validation components
try:
    from url_analyzer.shared.validation import (
        validate_not_none, validate_string, validate_number, validate_email,
        validate_url, Validator
    )
except ImportError as e:
    logging.getLogger(__name__).warning(f"Could not import validation components: {e}")
    validate_not_none = validate_string = validate_number = None
    validate_email = validate_url = Validator = None

__all__ = [
    # Re-export symbols from domain.py
    'Entity', 'ValueObject', 'Identifier',
    
    # Re-export symbols from interfaces.py
    'Repository', 'Service',
    
    # Re-export symbols from errors.py
    'DomainError', 'ValidationError', 'NotFoundError', 'AuthorizationError',
    
    # Re-export symbols from logging.py
    'get_logger', 'configure_logging',
    
    # Re-export symbols from validation.py
    'validate_not_none', 'validate_string', 'validate_number', 'validate_email',
    'validate_url', 'Validator'
]