"""
Web Rate Limiting Module

This module provides Flask decorators and middleware for applying rate limiting
to web interface endpoints using the existing RateLimiter infrastructure.
"""

import time
from functools import wraps
from typing import Optional, Dict, Any

from flask import request, jsonify, flash, redirect, url_for, current_app
from werkzeug.exceptions import TooManyRequests

from url_analyzer.api.security import RateLimiter
from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import APIRateLimitError

logger = get_logger(__name__)

# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def web_rate_limit(
    per_minute: Optional[int] = None,
    error_message: str = "Too many requests. Please try again later.",
    redirect_endpoint: Optional[str] = None
):
    """
    Decorator to apply rate limiting to Flask web endpoints.
    
    Args:
        per_minute: Custom rate limit per minute (overrides default)
        error_message: Custom error message for rate limit exceeded
        redirect_endpoint: Endpoint to redirect to on rate limit (for web pages)
    
    Returns:
        Decorated function with rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP address
            client_ip = get_client_ip()
            
            # Get rate limiter
            rate_limiter = get_rate_limiter()
            
            # Check rate limit
            is_allowed, rate_limit_info = rate_limiter.check_rate_limit(
                client_ip=client_ip
            )
            
            # If custom per_minute limit is specified, override the check
            if per_minute is not None:
                is_allowed, rate_limit_info = check_custom_rate_limit(
                    client_ip, per_minute
                )
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip} on endpoint {request.endpoint}"
                )
                
                # Handle rate limit exceeded
                if request.is_json or request.path.startswith('/api/'):
                    # Return JSON response for API-like requests
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'message': error_message,
                        'rate_limit': rate_limit_info
                    })
                    response.status_code = 429
                    
                    # Add rate limit headers
                    response.headers['X-RateLimit-Limit'] = str(rate_limit_info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(rate_limit_info['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(rate_limit_info['reset'])
                    
                    return response
                else:
                    # Handle web page requests
                    flash(error_message, 'error')
                    if redirect_endpoint:
                        return redirect(url_for(redirect_endpoint))
                    else:
                        # Return a simple error page
                        return f"""
                        <html>
                        <head><title>Rate Limit Exceeded</title></head>
                        <body>
                        <h1>Rate Limit Exceeded</h1>
                        <p>{error_message}</p>
                        <p>Please wait {rate_limit_info['reset']} seconds before trying again.</p>
                        <a href="javascript:history.back()">Go Back</a>
                        </body>
                        </html>
                        """, 429
            
            # Add rate limit headers to successful responses
            response = f(*args, **kwargs)
            
            # Add rate limit headers if response supports it
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(rate_limit_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_limit_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_limit_info['reset'])
            
            return response
        
        return decorated_function
    return decorator


def get_client_ip() -> str:
    """
    Get the client IP address from the request.
    
    Returns:
        Client IP address
    """
    # Check for forwarded headers (for reverse proxies)
    if request.headers.get('X-Forwarded-For'):
        # Get the first IP in the chain
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or 'unknown'


def check_custom_rate_limit(
    client_ip: str, 
    per_minute: int
) -> tuple[bool, Dict[str, Any]]:
    """
    Check custom rate limit for a specific endpoint.
    
    Args:
        client_ip: Client IP address
        per_minute: Requests allowed per minute
    
    Returns:
        Tuple of (is_allowed, rate_limit_info)
    """
    # Use a simple in-memory store for custom rate limits
    # In production, this should use Redis or similar
    if not hasattr(current_app, '_custom_rate_limits'):
        current_app._custom_rate_limits = {}
    
    store = current_app._custom_rate_limits
    current_time = time.time()
    reset_interval = 60  # 1 minute
    
    # Initialize or reset counter if needed
    if (
        client_ip not in store or
        store[client_ip]['reset_time'] <= current_time
    ):
        store[client_ip] = {
            'count': 0,
            'reset_time': current_time + reset_interval
        }
    
    # Increment counter
    store[client_ip]['count'] += 1
    
    # Check if limit exceeded
    count = store[client_ip]['count']
    reset_time = store[client_ip]['reset_time']
    
    # Calculate remaining and reset time
    remaining = max(0, per_minute - count)
    reset_seconds = max(0, int(reset_time - current_time))
    
    rate_limit_info = {
        'limit': per_minute,
        'remaining': remaining,
        'reset': reset_seconds
    }
    
    return count <= per_minute, rate_limit_info


# Predefined decorators for common use cases
def web_rate_limit_strict(f):
    """Strict rate limiting: 10 requests per minute."""
    return web_rate_limit(per_minute=10)(f)


def web_rate_limit_moderate(f):
    """Moderate rate limiting: 30 requests per minute."""
    return web_rate_limit(per_minute=30)(f)


def web_rate_limit_lenient(f):
    """Lenient rate limiting: 60 requests per minute."""
    return web_rate_limit(per_minute=60)(f)