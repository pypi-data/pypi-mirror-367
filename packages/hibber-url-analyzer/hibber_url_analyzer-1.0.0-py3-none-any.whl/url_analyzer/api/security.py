"""
API security implementation for URL Analyzer.

This module provides security features for the URL Analyzer API, including:
- Authentication and authorization
- Rate limiting
- Request validation
- API key management
- CORS support
- Audit logging
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any, Callable, Union, Tuple

from url_analyzer.utils.errors import (
    APIError, APIAuthenticationError, APIRateLimitError
)
from url_analyzer.utils.credentials import get_api_key, setup_api_key
from url_analyzer.config.manager import load_config, save_config

# Configure logger
logger = logging.getLogger(__name__)

# Default rate limits (requests per minute)
DEFAULT_RATE_LIMITS = {
    "anonymous": 10,      # Unauthenticated requests
    "basic": 60,          # Basic API key
    "premium": 300,       # Premium API key
    "unlimited": 0        # No limit (internal use)
}

# In-memory storage for rate limiting
# Structure: {api_key: {"count": int, "reset_time": float}}
rate_limit_store = {}

# In-memory API key store for development/testing
# In production, this would be replaced with a database
# Structure: {api_key: {"user_id": str, "role": str, "permissions": List[str], "created_at": str}}
api_key_store = {}

# In-memory audit log
# In production, this would be replaced with a database or log service
audit_log = []

# CORS settings
default_cors_settings = {
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["Content-Type", "Authorization"],
    "max_age": 86400  # 24 hours
}


class APIKeyManager:
    """
    Manages API keys for the URL Analyzer API.
    
    This class provides methods for creating, validating, and revoking API keys.
    It also handles role-based permissions for API access.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the API key manager with optional custom configuration."""
        self.config = load_config(config_path) if config_path else load_config()
        self._load_api_keys()
    
    def _load_api_keys(self) -> None:
        """Load API keys from configuration."""
        global api_key_store
        
        # In a real implementation, this would load from a database
        # For now, we'll use the in-memory store and initialize from config if available
        if "api_keys" in self.config.get("api_settings", {}):
            api_key_store = self.config["api_settings"]["api_keys"]
    
    def _save_api_keys(self) -> None:
        """Save API keys to configuration."""
        # In a real implementation, this would save to a database
        # For now, we'll update the config and save it
        if "api_settings" not in self.config:
            self.config["api_settings"] = {}
        
        self.config["api_settings"]["api_keys"] = api_key_store
        save_config(self.config)
    
    def create_api_key(
        self, 
        user_id: str, 
        role: str = "basic", 
        permissions: Optional[List[str]] = None
    ) -> str:
        """
        Create a new API key.
        
        Args:
            user_id: Identifier for the user or application
            role: Role for the API key (basic, premium, unlimited)
            permissions: List of specific permissions for the API key
            
        Returns:
            The newly created API key
        """
        # Generate a secure random API key
        # In production, use a more sophisticated method
        key_material = f"{user_id}:{role}:{time.time()}"
        api_key = hashlib.sha256(key_material.encode()).hexdigest()
        
        # Store the API key with metadata
        api_key_store[api_key] = {
            "user_id": user_id,
            "role": role,
            "permissions": permissions or [],
            "created_at": datetime.now().isoformat()
        }
        
        # Save the updated API keys
        self._save_api_keys()
        
        logger.info(f"Created API key for user {user_id} with role {role}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate an API key and return its metadata.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Dictionary containing the API key metadata
            
        Raises:
            APIAuthenticationError: If the API key is invalid
        """
        if api_key in api_key_store:
            return api_key_store[api_key]
        
        raise APIAuthenticationError("Invalid API key")
    
    def revoke_api_key(self, api_key: str) -> None:
        """
        Revoke an API key.
        
        Args:
            api_key: The API key to revoke
            
        Raises:
            APIAuthenticationError: If the API key is invalid
        """
        if api_key in api_key_store:
            user_id = api_key_store[api_key]["user_id"]
            del api_key_store[api_key]
            self._save_api_keys()
            logger.info(f"Revoked API key for user {user_id}")
        else:
            raise APIAuthenticationError("Invalid API key")
    
    def get_user_api_keys(self, user_id: str) -> List[str]:
        """
        Get all API keys for a user.
        
        Args:
            user_id: The user ID to get API keys for
            
        Returns:
            List of API keys for the user
        """
        return [
            key for key, metadata in api_key_store.items()
            if metadata["user_id"] == user_id
        ]


class RateLimiter:
    """
    Rate limiter for the URL Analyzer API.
    
    This class provides methods for rate limiting API requests based on
    API key or IP address.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the rate limiter with optional custom configuration."""
        self.config = load_config(config_path) if config_path else load_config()
        self._load_rate_limits()
    
    def _load_rate_limits(self) -> None:
        """Load rate limits from configuration."""
        # Load rate limits from config if available, otherwise use defaults
        self.rate_limits = self.config.get("api_settings", {}).get(
            "rate_limits", DEFAULT_RATE_LIMITS
        )
    
    def check_rate_limit(
        self, 
        api_key: Optional[str] = None, 
        client_ip: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is within rate limits.
        
        Args:
            api_key: Optional API key for the request
            client_ip: Optional client IP address for the request
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        global rate_limit_store
        
        # Determine the identifier for rate limiting
        # Prefer API key if available, otherwise use IP
        identifier = api_key or client_ip or "anonymous"
        
        # Determine the rate limit based on role
        limit = self.rate_limits["anonymous"]
        reset_interval = 60  # 1 minute in seconds
        
        if api_key and api_key in api_key_store:
            role = api_key_store[api_key]["role"]
            limit = self.rate_limits.get(role, self.rate_limits["basic"])
        
        # If limit is 0, it means unlimited requests
        if limit == 0:
            return True, {
                "limit": "unlimited",
                "remaining": "unlimited",
                "reset": 0
            }
        
        # Get current time
        current_time = time.time()
        
        # Initialize or reset counter if needed
        if (
            identifier not in rate_limit_store or
            rate_limit_store[identifier]["reset_time"] <= current_time
        ):
            rate_limit_store[identifier] = {
                "count": 0,
                "reset_time": current_time + reset_interval
            }
        
        # Increment the counter
        rate_limit_store[identifier]["count"] += 1
        
        # Check if the limit is exceeded
        count = rate_limit_store[identifier]["count"]
        reset_time = rate_limit_store[identifier]["reset_time"]
        
        # Calculate remaining requests and reset time
        remaining = max(0, limit - count)
        reset_seconds = max(0, int(reset_time - current_time))
        
        # Prepare rate limit information
        rate_limit_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_seconds
        }
        
        # Return whether the request is allowed and rate limit info
        return count <= limit, rate_limit_info


class RequestValidator:
    """
    Validator for API requests.
    
    This class provides methods for validating API requests, including
    parameter validation, content type validation, and security checks.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the request validator with optional custom configuration."""
        self.config = load_config(config_path) if config_path else load_config()
    
    def validate_request(
        self, 
        request_data: Dict[str, Any],
        required_params: List[str],
        optional_params: Optional[List[str]] = None,
        max_urls: int = 100
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a request.
        
        Args:
            request_data: The request data to validate
            required_params: List of required parameters
            optional_params: List of optional parameters
            max_urls: Maximum number of URLs allowed in a batch request
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        for param in required_params:
            if param not in request_data:
                return False, f"Missing required parameter: {param}"
        
        # Check for unknown parameters
        allowed_params = set(required_params)
        if optional_params:
            allowed_params.update(optional_params)
        
        for param in request_data:
            if param not in allowed_params:
                return False, f"Unknown parameter: {param}"
        
        # Validate URLs parameter if present
        if "urls" in request_data:
            urls = request_data["urls"]
            
            # Check if urls is a list
            if not isinstance(urls, list):
                return False, "URLs must be provided as a list"
            
            # Check if the list is empty
            if not urls:
                return False, "URLs list cannot be empty"
            
            # Check if the list exceeds the maximum size
            if len(urls) > max_urls:
                return False, f"Too many URLs. Maximum allowed: {max_urls}"
            
            # Check if all items are strings
            if not all(isinstance(url, str) for url in urls):
                return False, "All URLs must be strings"
        
        # Validate URL parameter if present
        if "url" in request_data:
            url = request_data["url"]
            
            # Check if url is a string
            if not isinstance(url, str):
                return False, "URL must be a string"
            
            # Check if the string is empty
            if not url:
                return False, "URL cannot be empty"
        
        # All validations passed
        return True, None


class AuditLogger:
    """
    Audit logger for the URL Analyzer API.
    
    This class provides methods for logging API usage for security
    and compliance purposes.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the audit logger with optional custom configuration."""
        self.config = load_config(config_path) if config_path else load_config()
    
    def log_request(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        client_ip: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log an API request.
        
        Args:
            endpoint: The API endpoint
            method: The HTTP method
            user_id: Optional user ID
            api_key: Optional API key (will be partially masked)
            client_ip: Optional client IP address
            request_data: Optional request data (sensitive data will be redacted)
            response_status: Optional response status code
            error: Optional error message
        """
        global audit_log
        
        # Mask the API key for security
        masked_api_key = None
        if api_key:
            # Only show the first 4 and last 4 characters
            if len(api_key) > 8:
                masked_api_key = f"{api_key[:4]}...{api_key[-4:]}"
            else:
                masked_api_key = "****"
        
        # Redact sensitive data from request data
        redacted_request_data = None
        if request_data:
            # Create a copy to avoid modifying the original
            redacted_request_data = request_data.copy()
            
            # Redact sensitive fields
            sensitive_fields = ["password", "api_key", "token", "secret"]
            for field in sensitive_fields:
                if field in redacted_request_data:
                    redacted_request_data[field] = "********"
        
        # Create the audit log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "api_key": masked_api_key,
            "client_ip": client_ip,
            "request_data": redacted_request_data,
            "response_status": response_status,
            "error": error
        }
        
        # Add to the in-memory audit log
        # In production, this would be sent to a database or log service
        audit_log.append(log_entry)
        
        # Log to the application logger as well
        log_message = (
            f"API Request: {method} {endpoint} | "
            f"User: {user_id or 'anonymous'} | "
            f"Status: {response_status or 'unknown'}"
        )
        if error:
            log_message += f" | Error: {error}"
        
        logger.info(log_message)
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with optional filtering.
        
        Args:
            user_id: Optional user ID to filter by
            start_time: Optional start time for the logs
            end_time: Optional end time for the logs
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        global audit_log
        
        # Filter the logs
        filtered_logs = audit_log
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
        
        if start_time:
            start_time_str = start_time.isoformat()
            filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_time_str]
        
        if end_time:
            end_time_str = end_time.isoformat()
            filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_time_str]
        
        # Sort by timestamp (newest first) and limit the results
        sorted_logs = sorted(
            filtered_logs,
            key=lambda log: log["timestamp"],
            reverse=True
        )
        
        return sorted_logs[:limit]


class CORSHandler:
    """
    CORS handler for the URL Analyzer API.
    
    This class provides methods for handling Cross-Origin Resource Sharing
    (CORS) for the API.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the CORS handler with optional custom configuration."""
        self.config = load_config(config_path) if config_path else load_config()
        self._load_cors_settings()
    
    def _load_cors_settings(self) -> None:
        """Load CORS settings from configuration."""
        # Load CORS settings from config if available, otherwise use defaults
        self.cors_settings = self.config.get("api_settings", {}).get(
            "cors", default_cors_settings
        )
    
    def get_cors_headers(self, origin: Optional[str] = None) -> Dict[str, str]:
        """
        Get CORS headers for a response.
        
        Args:
            origin: The Origin header from the request
            
        Returns:
            Dictionary of CORS headers
        """
        headers = {}
        
        # Handle Access-Control-Allow-Origin
        allow_origins = self.cors_settings["allow_origins"]
        if "*" in allow_origins:
            headers["Access-Control-Allow-Origin"] = "*"
        elif origin and origin in allow_origins:
            headers["Access-Control-Allow-Origin"] = origin
        
        # Add other CORS headers
        headers["Access-Control-Allow-Methods"] = ", ".join(
            self.cors_settings["allow_methods"]
        )
        headers["Access-Control-Allow-Headers"] = ", ".join(
            self.cors_settings["allow_headers"]
        )
        headers["Access-Control-Max-Age"] = str(self.cors_settings["max_age"])
        
        return headers


# Decorator for API authentication
def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key authentication for a function.
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function that requires API key authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract API key from kwargs
        api_key = kwargs.get("api_key")
        
        # If API key is not provided, return authentication error
        if not api_key:
            raise APIAuthenticationError("API key is required")
        
        # Validate the API key
        try:
            api_key_manager = APIKeyManager()
            api_key_metadata = api_key_manager.validate_api_key(api_key)
            
            # Add API key metadata to kwargs
            kwargs["api_key_metadata"] = api_key_metadata
            
            # Call the original function
            return f(*args, **kwargs)
        except APIAuthenticationError as e:
            # Re-raise the authentication error
            raise e
    
    return decorated


# Decorator for API rate limiting
def rate_limit(f: Callable) -> Callable:
    """
    Decorator to apply rate limiting to a function.
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function with rate limiting
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract API key and client IP from kwargs
        api_key = kwargs.get("api_key")
        client_ip = kwargs.get("client_ip")
        
        # Check rate limit
        rate_limiter = RateLimiter()
        is_allowed, rate_limit_info = rate_limiter.check_rate_limit(
            api_key=api_key,
            client_ip=client_ip
        )
        
        # If rate limit is exceeded, raise an error
        if not is_allowed:
            raise APIRateLimitError(
                f"Rate limit exceeded. Try again in {rate_limit_info['reset']} seconds."
            )
        
        # Add rate limit info to kwargs
        kwargs["rate_limit_info"] = rate_limit_info
        
        # Call the original function
        return f(*args, **kwargs)
    
    return decorated


# Decorator for request validation
def validate_request(
    required_params: List[str],
    optional_params: Optional[List[str]] = None,
    max_urls: int = 100
) -> Callable:
    """
    Decorator to validate request parameters.
    
    Args:
        required_params: List of required parameters
        optional_params: List of optional parameters
        max_urls: Maximum number of URLs allowed in a batch request
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Extract request data from kwargs
            request_data = kwargs.get("request_data", {})
            
            # Validate the request
            validator = RequestValidator()
            is_valid, error_message = validator.validate_request(
                request_data=request_data,
                required_params=required_params,
                optional_params=optional_params,
                max_urls=max_urls
            )
            
            # If validation fails, raise an error
            if not is_valid:
                raise APIError(f"Invalid request: {error_message}")
            
            # Call the original function
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


# Decorator for audit logging
def audit_log_request(
    endpoint: str,
    method: str
) -> Callable:
    """
    Decorator to log API requests for auditing.
    
    Args:
        endpoint: The API endpoint
        method: The HTTP method
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Extract information for audit logging
            user_id = kwargs.get("user_id")
            api_key = kwargs.get("api_key")
            client_ip = kwargs.get("client_ip")
            request_data = kwargs.get("request_data")
            
            # Initialize audit logger
            audit_logger = AuditLogger()
            
            try:
                # Call the original function
                result = f(*args, **kwargs)
                
                # Log the successful request
                response_status = 200  # Assume success
                audit_logger.log_request(
                    endpoint=endpoint,
                    method=method,
                    user_id=user_id,
                    api_key=api_key,
                    client_ip=client_ip,
                    request_data=request_data,
                    response_status=response_status
                )
                
                return result
            except Exception as e:
                # Log the failed request
                response_status = 500  # Assume server error
                if isinstance(e, APIAuthenticationError):
                    response_status = 401
                elif isinstance(e, APIRateLimitError):
                    response_status = 429
                elif isinstance(e, APIError):
                    response_status = 400
                
                audit_logger.log_request(
                    endpoint=endpoint,
                    method=method,
                    user_id=user_id,
                    api_key=api_key,
                    client_ip=client_ip,
                    request_data=request_data,
                    response_status=response_status,
                    error=str(e)
                )
                
                # Re-raise the exception
                raise e
        
        return decorated
    
    return decorator