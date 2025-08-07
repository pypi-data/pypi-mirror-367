"""
Validation Module

This module provides utilities for validating inputs and configuration values.
"""

import os
import re
import json
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Type, cast, get_type_hints, Literal, Final, TypedDict
from functools import wraps
import inspect
import re

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import ValidationError

# Create logger
logger = get_logger(__name__)

# Type variable for generic functions
T = TypeVar('T')

# Import custom types
try:
    from url_analyzer.utils.types import *
except ImportError:
    logger.warning("Custom type definitions not available. Some type validations may be limited.")


def validate_string(value: Any, min_length: int = 0, max_length: Optional[int] = None, 
                   pattern: Optional[str] = None, allow_empty: bool = False,
                   error_message: Optional[str] = None) -> str:
    """
    Validates that a value is a string with optional length and pattern constraints.
    
    Args:
        value: Value to validate
        min_length: Minimum length of the string
        max_length: Maximum length of the string (if None, no maximum)
        pattern: Regular expression pattern the string must match
        allow_empty: Whether to allow empty strings
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated string
        
    Raises:
        ValidationError: If the value is not a valid string
    """
    # Check if the value is a string
    if not isinstance(value, str):
        raise ValidationError(error_message or f"Expected a string, got {type(value).__name__}")
    
    # Check if the string is empty
    if not allow_empty and not value:
        raise ValidationError(error_message or "String cannot be empty")
    
    # Check minimum length
    if len(value) < min_length:
        raise ValidationError(error_message or f"String must be at least {min_length} characters long")
    
    # Check maximum length
    if max_length is not None and len(value) > max_length:
        raise ValidationError(error_message or f"String cannot be longer than {max_length} characters")
    
    # Check pattern
    if pattern is not None and not re.match(pattern, value):
        raise ValidationError(error_message or f"String does not match pattern: {pattern}")
    
    return value


def validate_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None,
                    error_message: Optional[str] = None) -> int:
    """
    Validates that a value is an integer with optional range constraints.
    
    Args:
        value: Value to validate
        min_value: Minimum value (if None, no minimum)
        max_value: Maximum value (if None, no maximum)
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated integer
        
    Raises:
        ValidationError: If the value is not a valid integer
    """
    # Try to convert to integer
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(error_message or f"Expected an integer, got {type(value).__name__}")
    
    # Check minimum value
    if min_value is not None and int_value < min_value:
        raise ValidationError(error_message or f"Value must be at least {min_value}")
    
    # Check maximum value
    if max_value is not None and int_value > max_value:
        raise ValidationError(error_message or f"Value cannot be greater than {max_value}")
    
    return int_value


def validate_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None,
                  error_message: Optional[str] = None) -> float:
    """
    Validates that a value is a float with optional range constraints.
    
    Args:
        value: Value to validate
        min_value: Minimum value (if None, no minimum)
        max_value: Maximum value (if None, no maximum)
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated float
        
    Raises:
        ValidationError: If the value is not a valid float
    """
    # Try to convert to float
    try:
        float_value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(error_message or f"Expected a float, got {type(value).__name__}")
    
    # Check minimum value
    if min_value is not None and float_value < min_value:
        raise ValidationError(error_message or f"Value must be at least {min_value}")
    
    # Check maximum value
    if max_value is not None and float_value > max_value:
        raise ValidationError(error_message or f"Value cannot be greater than {max_value}")
    
    return float_value


def validate_boolean(value: Any, error_message: Optional[str] = None) -> bool:
    """
    Validates that a value is a boolean or can be converted to a boolean.
    
    Args:
        value: Value to validate
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated boolean
        
    Raises:
        ValidationError: If the value is not a valid boolean
    """
    # Check if the value is already a boolean
    if isinstance(value, bool):
        return value
    
    # Try to convert string values
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ('true', 'yes', '1', 'y', 't'):
            return True
        elif value_lower in ('false', 'no', '0', 'n', 'f'):
            return False
    
    # Try to convert numeric values
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        elif value == 0:
            return False
    
    # If we get here, the value is not a valid boolean
    raise ValidationError(error_message or f"Expected a boolean, got {type(value).__name__}: {value}")


def validate_list(value: Any, item_validator: Optional[Callable[[Any], Any]] = None,
                 min_length: int = 0, max_length: Optional[int] = None,
                 error_message: Optional[str] = None) -> List[Any]:
    """
    Validates that a value is a list with optional item validation and length constraints.
    
    Args:
        value: Value to validate
        item_validator: Function to validate each item in the list
        min_length: Minimum length of the list
        max_length: Maximum length of the list (if None, no maximum)
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated list
        
    Raises:
        ValidationError: If the value is not a valid list
    """
    # Check if the value is a list
    if not isinstance(value, list):
        raise ValidationError(error_message or f"Expected a list, got {type(value).__name__}")
    
    # Check minimum length
    if len(value) < min_length:
        raise ValidationError(error_message or f"List must have at least {min_length} items")
    
    # Check maximum length
    if max_length is not None and len(value) > max_length:
        raise ValidationError(error_message or f"List cannot have more than {max_length} items")
    
    # Validate each item if a validator is provided
    if item_validator is not None:
        validated_items = []
        for i, item in enumerate(value):
            try:
                validated_items.append(item_validator(item))
            except ValidationError as e:
                raise ValidationError(error_message or f"Invalid item at index {i}: {str(e)}")
        return validated_items
    
    return value


def validate_dict(value: Any, key_validator: Optional[Callable[[Any], Any]] = None,
                 value_validator: Optional[Callable[[Any], Any]] = None,
                 required_keys: Optional[List[str]] = None,
                 error_message: Optional[str] = None) -> Dict[Any, Any]:
    """
    Validates that a value is a dictionary with optional key/value validation.
    
    Args:
        value: Value to validate
        key_validator: Function to validate each key in the dictionary
        value_validator: Function to validate each value in the dictionary
        required_keys: List of keys that must be present in the dictionary
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated dictionary
        
    Raises:
        ValidationError: If the value is not a valid dictionary
    """
    # Check if the value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError(error_message or f"Expected a dictionary, got {type(value).__name__}")
    
    # Check required keys
    if required_keys is not None:
        missing_keys = [key for key in required_keys if key not in value]
        if missing_keys:
            raise ValidationError(error_message or f"Missing required keys: {', '.join(missing_keys)}")
    
    # Validate keys and values
    validated_dict = {}
    for k, v in value.items():
        # Validate key
        validated_key = k
        if key_validator is not None:
            try:
                validated_key = key_validator(k)
            except ValidationError as e:
                raise ValidationError(error_message or f"Invalid key '{k}': {str(e)}")
        
        # Validate value
        validated_value = v
        if value_validator is not None:
            try:
                validated_value = value_validator(v)
            except ValidationError as e:
                raise ValidationError(error_message or f"Invalid value for key '{k}': {str(e)}")
        
        validated_dict[validated_key] = validated_value
    
    return validated_dict


def validate_file_path(value: Any, must_exist: bool = True, file_type: Optional[str] = None,
                      error_message: Optional[str] = None) -> str:
    """
    Validates that a value is a valid file path.
    
    Args:
        value: Value to validate
        must_exist: Whether the file must exist
        file_type: File extension the file must have (without the dot)
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated file path
        
    Raises:
        ValidationError: If the value is not a valid file path
    """
    # Validate that the value is a string
    path = validate_string(value, allow_empty=False, error_message=error_message or "File path cannot be empty")
    
    # Check if the file exists
    if must_exist and not os.path.exists(path):
        raise ValidationError(error_message or f"File does not exist: {path}")
    
    # Check if the path is a file (not a directory)
    if must_exist and os.path.exists(path) and not os.path.isfile(path):
        raise ValidationError(error_message or f"Path is not a file: {path}")
    
    # Check file type
    if file_type is not None:
        ext = os.path.splitext(path)[1].lower()
        if not ext or ext[1:] != file_type.lower():
            raise ValidationError(error_message or f"File must be a {file_type} file")
    
    return path


def validate_directory_path(value: Any, must_exist: bool = True,
                           error_message: Optional[str] = None) -> str:
    """
    Validates that a value is a valid directory path.
    
    Args:
        value: Value to validate
        must_exist: Whether the directory must exist
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated directory path
        
    Raises:
        ValidationError: If the value is not a valid directory path
    """
    # Validate that the value is a string
    path = validate_string(value, allow_empty=False, error_message=error_message or "Directory path cannot be empty")
    
    # Check if the directory exists
    if must_exist and not os.path.exists(path):
        raise ValidationError(error_message or f"Directory does not exist: {path}")
    
    # Check if the path is a directory (not a file)
    if must_exist and os.path.exists(path) and not os.path.isdir(path):
        raise ValidationError(error_message or f"Path is not a directory: {path}")
    
    return path


def validate_url(value: Any, error_message: Optional[str] = None) -> str:
    """
    Validates that a value is a valid URL.
    
    Args:
        value: Value to validate
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated URL
        
    Raises:
        ValidationError: If the value is not a valid URL
    """
    # URL regex pattern
    url_pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    
    # Validate that the value is a string matching the URL pattern
    return validate_string(
        value, 
        pattern=url_pattern, 
        error_message=error_message or "Invalid URL format"
    )


def validate_email(value: Any, error_message: Optional[str] = None) -> str:
    """
    Validates that a value is a valid email address.
    
    Args:
        value: Value to validate
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated email address
        
    Raises:
        ValidationError: If the value is not a valid email address
    """
    # Email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Validate that the value is a string matching the email pattern
    return validate_string(
        value, 
        pattern=email_pattern, 
        error_message=error_message or "Invalid email format"
    )


def validate_json(value: Any, schema: Optional[Dict[str, Any]] = None,
                 error_message: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates that a value is valid JSON.
    
    Args:
        value: Value to validate (string or dictionary)
        schema: JSON schema to validate against (if None, no schema validation)
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated JSON as a dictionary
        
    Raises:
        ValidationError: If the value is not valid JSON
    """
    # If the value is a string, try to parse it as JSON
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise ValidationError(error_message or "Invalid JSON format")
    
    # Check if the value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError(error_message or f"Expected a dictionary, got {type(value).__name__}")
    
    # Validate against schema if provided
    if schema is not None:
        try:
            import jsonschema
            jsonschema.validate(value, schema)
        except ImportError:
            logger.warning("jsonschema package not installed, skipping schema validation")
        except jsonschema.exceptions.ValidationError as e:
            raise ValidationError(error_message or f"JSON does not match schema: {str(e)}")
    
    return value


def validate_type(value: Any, expected_type: Type[T], error_message: Optional[str] = None) -> T:
    """
    Validates that a value is of the expected type.
    
    Args:
        value: Value to validate
        expected_type: Type the value should be
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated value
        
    Raises:
        ValidationError: If the value is not of the expected type
    """
    if not isinstance(value, expected_type):
        raise ValidationError(error_message or f"Expected {expected_type.__name__}, got {type(value).__name__}")
    
    return cast(T, value)


def validate_enum(value: Any, enum_values: List[Any], error_message: Optional[str] = None) -> Any:
    """
    Validates that a value is one of the allowed enum values.
    
    Args:
        value: Value to validate
        enum_values: List of allowed values
        error_message: Custom error message to use if validation fails
        
    Returns:
        The validated value
        
    Raises:
        ValidationError: If the value is not one of the allowed values
    """
    if value not in enum_values:
        raise ValidationError(error_message or f"Value must be one of: {', '.join(map(str, enum_values))}")
    
    return value


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a configuration dictionary against a schema.
    
    Args:
        config: Configuration dictionary to validate
        schema: Schema to validate against
        
    Returns:
        The validated configuration dictionary
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    try:
        import jsonschema
        jsonschema.validate(config, schema)
        return config
    except ImportError:
        logger.warning("jsonschema package not installed, skipping schema validation")
        return config
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(f"Invalid configuration: {str(e)}")


def validate_params(func: Callable) -> Callable:
    """
    Decorator that validates function parameters based on type hints.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        
        # Get parameter bindings
        bound_args = sig.bind(*args, **kwargs)
        
        # Get type hints
        type_hints = get_type_hints(func)
        
        # Validate each parameter
        for param_name, param_value in bound_args.arguments.items():
            # Skip return annotation
            if param_name == 'return':
                continue
            
            # Get expected type
            if (expected_type := type_hints.get(param_name)) is None:
                continue
            
            # Validate parameter
            try:
                # Handle Optional types
                if getattr(expected_type, '__origin__', None) is Union and type(None) in expected_type.__args__:
                    if param_value is not None:
                        # Get the non-None type
                        non_none_types = [t for t in expected_type.__args__ if t is not type(None)]
                        if len(non_none_types) == 1:
                            validate_type(param_value, non_none_types[0])
                else:
                    validate_type(param_value, expected_type)
            except ValidationError as e:
                raise ValidationError(f"Invalid parameter '{param_name}': {str(e)}")
        
        # Call the function
        return func(*args, **kwargs)
    
    return wrapper


def validate_input_params(input_types: Dict[str, str]) -> Callable:
    """
    Decorator that validates and sanitizes function parameters based on input types.
    
    Args:
        input_types: Dictionary mapping parameter names to input types
                    (e.g., {'filename': 'filename', 'url': 'url'})
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            
            # Get parameter bindings
            bound_args = sig.bind(*args, **kwargs)
            
            # Sanitize parameters
            for param_name, input_type in input_types.items():
                if param_name in bound_args.arguments:
                    param_value = bound_args.arguments[param_name]
                    
                    # Skip None values
                    if param_value is None:
                        continue
                    
                    # Import sanitization module
                    from url_analyzer.utils.sanitization import sanitize_input
                    
                    # Sanitize the parameter
                    try:
                        sanitized_value = sanitize_input(param_value, input_type)
                        bound_args.arguments[param_name] = sanitized_value
                    except ValidationError as e:
                        raise ValidationError(f"Invalid parameter '{param_name}': {str(e)}")
            
            # Call the function with sanitized parameters
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    
    return decorator


def validate_config_param(param_name: str, schema: Dict[str, Any]) -> Callable:
    """
    Decorator that validates a configuration parameter against a schema.
    
    Args:
        param_name: Name of the parameter to validate
        schema: JSON schema to validate against
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            
            # Get parameter bindings
            bound_args = sig.bind(*args, **kwargs)
            
            # Validate the parameter
            if param_name in bound_args.arguments:
                param_value = bound_args.arguments[param_name]
                
                # Skip None values
                if param_value is None:
                    return func(*args, **kwargs)
                
                # Validate the parameter
                try:
                    validate_config(param_value, schema)
                except ValidationError as e:
                    raise ValidationError(f"Invalid configuration: {str(e)}")
            
            # Call the function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def validate_return_type(func: Callable) -> Callable:
    """
    Decorator that validates the return value of a function based on its return type hint.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the function
        result = func(*args, **kwargs)
        
        # Get return type hint
        type_hints = get_type_hints(func)
        return_type = type_hints.get('return')
        if return_type is None:
            return result
        
        # Validate return value
        try:
            # Handle Optional types
            if getattr(return_type, '__origin__', None) is Union and type(None) in return_type.__args__:
                if result is not None:
                    # Get the non-None type
                    non_none_types = [t for t in return_type.__args__ if t is not type(None)]
                    if len(non_none_types) == 1:
                        validate_type(result, non_none_types[0])
            else:
                validate_type(result, return_type)
        except ValidationError as e:
            raise ValidationError(f"Invalid return value: {str(e)}")
        
        return result
    
    return wrapper


def validate_types(func: Callable) -> Callable:
    """
    Enhanced decorator that validates function parameters and return value
    based on type hints, with support for custom type definitions.
    
    This decorator combines the functionality of validate_params and
    validate_return_type, and adds support for custom type definitions
    from url_analyzer.utils.types.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    
    Example:
        ```python
        from url_analyzer.utils.validation import validate_types
        from url_analyzer.utils.types import ConfigDict, UrlCategory
        
        @validate_types
        def process_config(config: ConfigDict) -> UrlCategory:
            # Function implementation
            return category, is_sensitive
        ```
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        
        # Get parameter bindings
        bound_args = sig.bind(*args, **kwargs)
        
        # Get type hints using get_type_hints which resolves string annotations
        type_hints = get_type_hints(func)
        
        # Validate each parameter
        for param_name, param_value in bound_args.arguments.items():
            # Skip return annotation
            if param_name == 'return':
                continue
            
            # Get expected type
            if (expected_type := type_hints.get(param_name)) is None:
                continue
            
            # Validate parameter
            try:
                # Handle Optional types
                if getattr(expected_type, '__origin__', None) is Union and type(None) in expected_type.__args__:
                    if param_value is not None:
                        # Get the non-None type
                        non_none_types = [t for t in expected_type.__args__ if t is not type(None)]
                        if len(non_none_types) == 1:
                            validate_type(param_value, non_none_types[0])
                # Handle custom Dict types
                elif getattr(expected_type, '__origin__', None) is dict:
                    validate_dict(param_value)
                    # Additional validation could be added here for key/value types
                # Handle custom List types
                elif getattr(expected_type, '__origin__', None) is list:
                    validate_list(param_value)
                    # Additional validation could be added here for item types
                # Handle NewType
                elif hasattr(expected_type, '__supertype__'):
                    validate_type(param_value, expected_type.__supertype__)
                else:
                    validate_type(param_value, expected_type)
            except ValidationError as e:
                raise ValidationError(f"Invalid parameter '{param_name}': {str(e)}")
        
        # Call the function
        result = func(*args, **kwargs)
        
        # Validate return value
        if (return_type := type_hints.get('return')) is not None:
            try:
                # Handle Optional types
                if getattr(return_type, '__origin__', None) is Union and type(None) in return_type.__args__:
                    if result is not None:
                        # Get the non-None type
                        non_none_types = [t for t in return_type.__args__ if t is not type(None)]
                        if len(non_none_types) == 1:
                            validate_type(result, non_none_types[0])
                # Handle custom Dict types
                elif getattr(return_type, '__origin__', None) is dict:
                    validate_dict(result)
                    # Additional validation could be added here for key/value types
                # Handle custom List types
                elif getattr(return_type, '__origin__', None) is list:
                    validate_list(result)
                    # Additional validation could be added here for item types
                # Handle NewType
                elif hasattr(return_type, '__supertype__'):
                    validate_type(result, return_type.__supertype__)
                else:
                    validate_type(result, return_type)
            except ValidationError as e:
                raise ValidationError(f"Invalid return value: {str(e)}")
        
        return result
    
    return wrapper


def validate_file_param(param_name: str, must_exist: bool = True, file_type: Optional[str] = None) -> Callable:
    """
    Decorator that validates a file path parameter.
    
    Args:
        param_name: Name of the parameter to validate
        must_exist: Whether the file must exist
        file_type: File extension the file must have (without the dot)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            
            # Get parameter bindings
            bound_args = sig.bind(*args, **kwargs)
            
            # Validate the parameter
            if param_name in bound_args.arguments:
                param_value = bound_args.arguments[param_name]
                
                # Skip None values
                if param_value is None:
                    return func(*args, **kwargs)
                
                # Validate the parameter
                try:
                    validated_path = validate_file_path(param_value, must_exist, file_type)
                    bound_args.arguments[param_name] = validated_path
                except ValidationError as e:
                    raise ValidationError(f"Invalid file path parameter '{param_name}': {str(e)}")
            
            # Call the function with validated parameters
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    
    return decorator


def validate_url_param(param_name: str, allowed_schemes: Optional[List[str]] = None) -> Callable:
    """
    Decorator that validates a URL parameter.
    
    Args:
        param_name: Name of the parameter to validate
        allowed_schemes: List of allowed URL schemes (if None, http and https are allowed)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            
            # Get parameter bindings
            bound_args = sig.bind(*args, **kwargs)
            
            # Validate the parameter
            if param_name in bound_args.arguments:
                param_value = bound_args.arguments[param_name]
                
                # Skip None values
                if param_value is None:
                    return func(*args, **kwargs)
                
                # Import sanitization module
                from url_analyzer.utils.sanitization import sanitize_url
                
                # Validate and sanitize the parameter
                try:
                    sanitized_url = sanitize_url(param_value, allowed_schemes)
                    bound_args.arguments[param_name] = sanitized_url
                except ValidationError as e:
                    raise ValidationError(f"Invalid URL parameter '{param_name}': {str(e)}")
            
            # Call the function with validated parameters
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    
    return decorator