"""
Sanitization Module

This module provides utilities for sanitizing inputs to prevent security issues
like path traversal attacks, command injection, and cross-site scripting (XSS).
"""

import os
import re
import html
import urllib.parse
from typing import Optional, Dict, Any, List

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import ValidationError, PathValidationError, URLValidationError

# Create logger
logger = get_logger(__name__)


def sanitize_filename(filename: str, replacement_char: str = '_') -> str:
    """
    Sanitizes a filename to prevent path traversal and other security issues.
    
    Args:
        filename: Filename to sanitize
        replacement_char: Character to replace invalid characters with
        
    Returns:
        Sanitized filename
        
    Raises:
        ValidationError: If the filename is empty after sanitization
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    # Remove any directory components
    filename = os.path.basename(filename)
    
    # Replace potentially dangerous characters
    # This regex matches any character that is not alphanumeric, a dot, underscore, or hyphen
    sanitized = re.sub(r'[^\w\.\-]', replacement_char, filename)
    
    # Ensure the filename doesn't start with a dot (hidden file)
    if sanitized.startswith('.'):
        sanitized = replacement_char + sanitized[1:]
    
    # Ensure the filename is not empty after sanitization
    if not sanitized:
        raise ValidationError("Filename is invalid or contains only invalid characters")
    
    return sanitized


def sanitize_path(path: str, allowed_dirs: Optional[List[str]] = None) -> str:
    """
    Sanitizes a file path to prevent path traversal attacks.
    
    Args:
        path: File path to sanitize
        allowed_dirs: List of allowed directory paths (if None, any directory is allowed)
        
    Returns:
        Sanitized file path
        
    Raises:
        PathValidationError: If the path is invalid or not in an allowed directory
    """
    if not path:
        raise PathValidationError("Path cannot be empty")
    
    # Normalize the path to resolve any '..' components
    normalized_path = os.path.normpath(os.path.abspath(path))
    
    # Check if the path is in an allowed directory
    if allowed_dirs:
        allowed = False
        for allowed_dir in allowed_dirs:
            allowed_dir = os.path.normpath(os.path.abspath(allowed_dir))
            if normalized_path.startswith(allowed_dir):
                allowed = True
                break
        
        if not allowed:
            raise PathValidationError(f"Path is not in an allowed directory: {path}")
    
    return normalized_path


def sanitize_url(url: str, allowed_schemes: Optional[List[str]] = None) -> str:
    """
    Sanitizes a URL to prevent security issues.
    
    Args:
        url: URL to sanitize
        allowed_schemes: List of allowed URL schemes (if None, http and https are allowed)
        
    Returns:
        Sanitized URL
        
    Raises:
        URLValidationError: If the URL is invalid or uses a disallowed scheme
    """
    if not url:
        raise URLValidationError("URL cannot be empty")
    
    # Set default allowed schemes if not provided
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    # Parse the URL
    try:
        parsed = urllib.parse.urlparse(url)
        
        # Check if the URL has a scheme
        if not parsed.scheme:
            # Add http scheme if missing
            url = 'http://' + url
            parsed = urllib.parse.urlparse(url)
        
        # Check if the scheme is allowed
        if parsed.scheme not in allowed_schemes:
            raise URLValidationError(f"URL scheme not allowed: {parsed.scheme}")
        
        # Check if the URL has a netloc (domain)
        if not parsed.netloc:
            raise URLValidationError("URL does not have a valid domain")
        
        # Reconstruct the URL
        return urllib.parse.urlunparse(parsed)
    
    except Exception as e:
        if not isinstance(e, URLValidationError):
            raise URLValidationError(f"Invalid URL: {url}")
        raise


def sanitize_html(html_content: str) -> str:
    """
    Sanitizes HTML content to prevent cross-site scripting (XSS) attacks.
    
    Args:
        html_content: HTML content to sanitize
        
    Returns:
        Sanitized HTML content
    """
    if not html_content:
        return ''
    
    # Escape HTML special characters
    return html.escape(html_content)


def sanitize_sql(sql_input: str) -> str:
    """
    Sanitizes SQL input to prevent SQL injection attacks.
    
    Note: This is a basic sanitization and should not be relied upon for
    direct use in SQL queries. Always use parameterized queries instead.
    
    Args:
        sql_input: SQL input to sanitize
        
    Returns:
        Sanitized SQL input
    """
    if not sql_input:
        return ''
    
    # Remove SQL comments
    sanitized = re.sub(r'--.*?$|/\*.*?\*/', '', sql_input, flags=re.MULTILINE | re.DOTALL)
    
    # Escape single quotes
    sanitized = sanitized.replace("'", "''")
    
    # Remove SQL keywords
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'EXEC', 'UNION', 'FROM', 'WHERE', 'JOIN', 'HAVING', 'GROUP'
    ]
    
    pattern = r'\b(' + '|'.join(sql_keywords) + r')\b'
    sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def sanitize_command(command: str) -> str:
    """
    Sanitizes a command to prevent command injection attacks.
    
    Note: This is a basic sanitization and should not be relied upon for
    direct use in shell commands. Avoid using shell commands with user input.
    
    Args:
        command: Command to sanitize
        
    Returns:
        Sanitized command
    """
    if not command:
        return ''
    
    # Remove shell special characters
    shell_chars = ['&', ';', '|', '>', '<', '`', '$', '\\', '!', '\n']
    sanitized = command
    
    for char in shell_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized


def sanitize_json_string(json_string: str) -> str:
    """
    Sanitizes a JSON string to prevent security issues.
    
    Args:
        json_string: JSON string to sanitize
        
    Returns:
        Sanitized JSON string
    """
    if not json_string:
        return ''
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', json_string)
    
    return sanitized


def sanitize_input(input_str: str, input_type: str = 'text') -> str:
    """
    Sanitizes input based on its type.
    
    Args:
        input_str: Input string to sanitize
        input_type: Type of input ('text', 'html', 'url', 'filename', 'path', 'sql', 'command', 'json')
        
    Returns:
        Sanitized input
        
    Raises:
        ValidationError: If the input type is not supported
    """
    if not input_str:
        return ''
    
    # Sanitize based on input type
    if input_type == 'text':
        # For plain text, just trim whitespace
        return input_str.strip()
    elif input_type == 'html':
        return sanitize_html(input_str)
    elif input_type == 'url':
        return sanitize_url(input_str)
    elif input_type == 'filename':
        return sanitize_filename(input_str)
    elif input_type == 'path':
        return sanitize_path(input_str)
    elif input_type == 'sql':
        return sanitize_sql(input_str)
    elif input_type == 'command':
        return sanitize_command(input_str)
    elif input_type == 'json':
        return sanitize_json_string(input_str)
    else:
        raise ValidationError(f"Unsupported input type: {input_type}")