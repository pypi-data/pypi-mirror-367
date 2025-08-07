"""
CLI Validation Module

This module provides utilities for validating command-line arguments
and ensuring they meet the requirements for safe and correct operation.
"""

import os
import argparse
from typing import Optional, Dict, Any, List, Union, Callable

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import ValidationError, PathValidationError
from url_analyzer.utils.validation import (
    validate_string, validate_file_path, validate_directory_path,
    validate_enum, validate_type
)
from url_analyzer.utils.sanitization import sanitize_path, sanitize_filename

# Create logger
logger = get_logger(__name__)


def validate_input_path(path: str, must_exist: bool = True) -> str:
    """
    Validates an input file or directory path from command-line arguments.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        
    Returns:
        Validated and sanitized path
        
    Raises:
        ValidationError: If the path is invalid
        PathValidationError: If the path does not exist and must_exist is True
    """
    try:
        # Validate that the path is a string
        validate_string(path, allow_empty=False, error_message="Path cannot be empty")
        
        # Sanitize the path to prevent path traversal attacks
        safe_path = sanitize_path(path)
        
        # Check if the path exists
        if must_exist and not os.path.exists(safe_path):
            raise PathValidationError(f"Path does not exist: {path}")
        
        return safe_path
    except ValidationError as e:
        logger.error(f"Invalid input path: {e}")
        raise


def validate_output_path(path: str, create_dirs: bool = True) -> str:
    """
    Validates an output file path from command-line arguments.
    
    Args:
        path: Path to validate
        create_dirs: Whether to create directories if they don't exist
        
    Returns:
        Validated and sanitized path
        
    Raises:
        ValidationError: If the path is invalid
    """
    try:
        # Validate that the path is a string
        validate_string(path, allow_empty=False, error_message="Output path cannot be empty")
        
        # Sanitize the path to prevent path traversal attacks
        safe_path = sanitize_path(path)
        
        # Get the directory part of the path
        directory = os.path.dirname(safe_path)
        
        # Create directories if they don't exist
        if directory and create_dirs and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
        
        return safe_path
    except ValidationError as e:
        logger.error(f"Invalid output path: {e}")
        raise


def validate_output_directory(directory: str, create_if_missing: bool = True) -> str:
    """
    Validates an output directory path from command-line arguments.
    
    Args:
        directory: Directory path to validate
        create_if_missing: Whether to create the directory if it doesn't exist
        
    Returns:
        Validated and sanitized directory path
        
    Raises:
        ValidationError: If the directory path is invalid
    """
    try:
        # Validate that the directory is a string
        validate_string(directory, allow_empty=False, error_message="Directory path cannot be empty")
        
        # Sanitize the path to prevent path traversal attacks
        safe_directory = sanitize_path(directory)
        
        # Create the directory if it doesn't exist
        if create_if_missing and not os.path.exists(safe_directory):
            os.makedirs(safe_directory, exist_ok=True)
            logger.debug(f"Created directory: {safe_directory}")
        elif not os.path.isdir(safe_directory):
            raise PathValidationError(f"Path is not a directory: {directory}")
        
        return safe_directory
    except ValidationError as e:
        logger.error(f"Invalid output directory: {e}")
        raise


def validate_file_format(file_path: str, allowed_formats: List[str]) -> str:
    """
    Validates that a file has an allowed format based on its extension.
    
    Args:
        file_path: Path to the file
        allowed_formats: List of allowed file extensions (without the dot)
        
    Returns:
        Validated file path
        
    Raises:
        ValidationError: If the file format is not allowed
    """
    try:
        # Validate that the file path is a string
        validate_string(file_path, allow_empty=False, error_message="File path cannot be empty")
        
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        if not ext:
            raise ValidationError(f"File has no extension: {file_path}")
        
        # Remove the dot from the extension
        ext = ext[1:].lower()
        
        # Validate that the extension is allowed
        validate_enum(ext, allowed_formats, error_message=f"Unsupported file format: {ext}")
        
        return file_path
    except ValidationError as e:
        logger.error(f"Invalid file format: {e}")
        raise


def validate_filter_expression(expression: str) -> Dict[str, str]:
    """
    Validates and parses a filter expression from command-line arguments.
    
    Args:
        expression: Filter expression to validate (e.g., "column=value")
        
    Returns:
        Dictionary with parsed filter (e.g., {"column": "value"})
        
    Raises:
        ValidationError: If the filter expression is invalid
    """
    try:
        # Validate that the expression is a string
        validate_string(expression, allow_empty=False, error_message="Filter expression cannot be empty")
        
        # Parse the filter expression
        if '=' not in expression:
            raise ValidationError(f"Invalid filter format: {expression}. Expected format: column=value")
        
        # Split the expression into column and value
        parts = expression.split('=', 1)
        if len(parts) != 2:
            raise ValidationError(f"Invalid filter format: {expression}. Expected format: column=value")
        
        column, value = parts
        
        # Validate column name (alphanumeric and underscore only)
        if not column.strip():
            raise ValidationError("Column name cannot be empty")
        
        if not all(c.isalnum() or c == '_' for c in column.strip()):
            raise ValidationError(f"Invalid column name: {column}. Only alphanumeric characters and underscores are allowed.")
        
        # Return the parsed filter
        return {"column": column.strip(), "value": value.strip()}
    except ValidationError as e:
        logger.error(f"Invalid filter expression: {e}")
        raise


def validate_template_name(template_name: str) -> str:
    """
    Validates a template name from command-line arguments.
    
    Args:
        template_name: Template name to validate
        
    Returns:
        Validated template name
        
    Raises:
        ValidationError: If the template name is invalid
    """
    try:
        # Validate that the template name is a string
        validate_string(template_name, allow_empty=False, error_message="Template name cannot be empty")
        
        # Sanitize the template name to prevent path traversal attacks
        safe_name = sanitize_filename(template_name)
        
        # Check if the sanitized name is different from the original
        if safe_name != template_name:
            logger.warning(f"Template name sanitized: {template_name} -> {safe_name}")
        
        return safe_name
    except ValidationError as e:
        logger.error(f"Invalid template name: {e}")
        raise


def validate_args(args: argparse.Namespace, validations: Dict[str, Callable]) -> argparse.Namespace:
    """
    Validates command-line arguments based on a dictionary of validation functions.
    
    Args:
        args: Command-line arguments
        validations: Dictionary mapping argument names to validation functions
        
    Returns:
        Validated arguments
        
    Raises:
        ValidationError: If any argument is invalid
    """
    validated_args = argparse.Namespace(**vars(args))
    
    for arg_name, validation_func in validations.items():
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            try:
                # Get the argument value
                arg_value = getattr(args, arg_name)
                
                # Validate the argument
                validated_value = validation_func(arg_value)
                
                # Update the validated arguments
                setattr(validated_args, arg_name, validated_value)
                
                logger.debug(f"Validated argument {arg_name}: {arg_value}")
            except ValidationError as e:
                logger.error(f"Invalid argument {arg_name}: {e}")
                raise ValidationError(f"Invalid argument {arg_name}: {e}")
    
    return validated_args