"""
Rate Limiting Utilities

This module provides rate limiting functionality for controlling the frequency
of operations, particularly useful for external API calls and HTTP requests.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Optional, Any, Callable
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: float = 1.0
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    burst_size: int = 5
    backoff_factor: float = 1.5
    max_backoff: float = 60.0


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation.
    
    This rate limiter allows for burst requests up to the bucket capacity,
    then limits requests to the specified rate.
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize the rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.tokens = float(config.burst_size)
        self.last_update = time.time()
        self.lock = threading.Lock()
        
        # Calculate token refill rate (tokens per second)
        self.refill_rate = config.requests_per_second
        
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait for tokens (None for no timeout)
            
        Returns:
            True if tokens were acquired, False if timeout occurred
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                now = time.time()
                
                # Add tokens based on elapsed time
                elapsed = now - self.last_update
                self.tokens = min(
                    self.config.burst_size,
                    self.tokens + elapsed * self.refill_rate
                )
                self.last_update = now
                
                # Check if we have enough tokens
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                # Calculate wait time for next token
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
            # Check timeout
            if timeout is not None:
                elapsed_total = time.time() - start_time
                if elapsed_total + wait_time > timeout:
                    return False
            
            # Wait for tokens to be available
            time.sleep(min(wait_time, 0.1))  # Sleep in small increments
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limiter status."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            current_tokens = min(
                self.config.burst_size,
                self.tokens + elapsed * self.refill_rate
            )
            
            return {
                'current_tokens': current_tokens,
                'max_tokens': self.config.burst_size,
                'refill_rate': self.refill_rate,
                'requests_per_second': self.config.requests_per_second
            }


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter implementation.
    
    This rate limiter tracks requests in sliding time windows and enforces
    limits per minute and per hour.
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize the sliding window rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.requests = deque()
        self.lock = threading.Lock()
        
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Check if a request can be made within the rate limits.
        
        Args:
            timeout: Maximum time to wait (not used in sliding window)
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = datetime.now()
        
        with self.lock:
            # Clean old requests
            self._clean_old_requests(now)
            
            # Check per-minute limit
            if self.config.requests_per_minute:
                minute_ago = now - timedelta(minutes=1)
                recent_requests = sum(1 for req_time in self.requests if req_time > minute_ago)
                if recent_requests >= self.config.requests_per_minute:
                    logger.debug(f"Rate limit exceeded: {recent_requests} requests in last minute")
                    return False
            
            # Check per-hour limit
            if self.config.requests_per_hour:
                hour_ago = now - timedelta(hours=1)
                recent_requests = sum(1 for req_time in self.requests if req_time > hour_ago)
                if recent_requests >= self.config.requests_per_hour:
                    logger.debug(f"Rate limit exceeded: {recent_requests} requests in last hour")
                    return False
            
            # Record the request
            self.requests.append(now)
            return True
    
    def _clean_old_requests(self, now: datetime) -> None:
        """Remove requests older than 1 hour."""
        hour_ago = now - timedelta(hours=1)
        while self.requests and self.requests[0] < hour_ago:
            self.requests.popleft()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limiter status."""
        now = datetime.now()
        
        with self.lock:
            self._clean_old_requests(now)
            
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            requests_last_minute = sum(1 for req_time in self.requests if req_time > minute_ago)
            requests_last_hour = sum(1 for req_time in self.requests if req_time > hour_ago)
            
            return {
                'requests_last_minute': requests_last_minute,
                'requests_last_hour': requests_last_hour,
                'limit_per_minute': self.config.requests_per_minute,
                'limit_per_hour': self.config.requests_per_hour
            }


class CompositeRateLimiter:
    """
    Composite rate limiter that combines token bucket and sliding window limiters.
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize the composite rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.token_bucket = TokenBucketRateLimiter(config)
        self.sliding_window = SlidingWindowRateLimiter(config)
        
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait for permission
            
        Returns:
            True if request is allowed, False otherwise
        """
        # Check sliding window limits first (fast check)
        if not self.sliding_window.acquire(timeout):
            return False
        
        # Then check token bucket (may wait)
        return self.token_bucket.acquire(tokens, timeout)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limiter status."""
        token_status = self.token_bucket.get_status()
        window_status = self.sliding_window.get_status()
        
        return {
            'token_bucket': token_status,
            'sliding_window': window_status,
            'config': {
                'requests_per_second': self.config.requests_per_second,
                'requests_per_minute': self.config.requests_per_minute,
                'requests_per_hour': self.config.requests_per_hour,
                'burst_size': self.config.burst_size
            }
        }


class GlobalRateLimiter:
    """
    Global rate limiter that manages rate limits for different domains/endpoints.
    """
    
    def __init__(self):
        """Initialize the global rate limiter."""
        self.limiters: Dict[str, CompositeRateLimiter] = {}
        self.lock = threading.Lock()
        
        # Default configurations for different types of endpoints
        self.default_configs = {
            'api': RateLimitConfig(
                requests_per_second=2.0,
                requests_per_minute=60,
                requests_per_hour=1000,
                burst_size=5
            ),
            'web': RateLimitConfig(
                requests_per_second=5.0,
                requests_per_minute=150,
                requests_per_hour=3000,
                burst_size=10
            ),
            'default': RateLimitConfig(
                requests_per_second=1.0,
                requests_per_minute=30,
                requests_per_hour=500,
                burst_size=3
            )
        }
    
    def get_limiter(self, domain: str, endpoint_type: str = 'default') -> CompositeRateLimiter:
        """
        Get or create a rate limiter for a specific domain.
        
        Args:
            domain: Domain name (e.g., 'api.example.com')
            endpoint_type: Type of endpoint ('api', 'web', 'default')
            
        Returns:
            Rate limiter for the domain
        """
        key = f"{domain}:{endpoint_type}"
        
        with self.lock:
            if key not in self.limiters:
                config = self.default_configs.get(endpoint_type, self.default_configs['default'])
                self.limiters[key] = CompositeRateLimiter(config)
                logger.debug(f"Created rate limiter for {key}")
            
            return self.limiters[key]
    
    def acquire(self, domain: str, endpoint_type: str = 'default', 
                tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request to a domain.
        
        Args:
            domain: Domain name
            endpoint_type: Type of endpoint
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait
            
        Returns:
            True if request is allowed, False otherwise
        """
        limiter = self.get_limiter(domain, endpoint_type)
        return limiter.acquire(tokens, timeout)
    
    def get_status(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of rate limiters.
        
        Args:
            domain: Specific domain to get status for (None for all)
            
        Returns:
            Dictionary with rate limiter statuses
        """
        with self.lock:
            if domain:
                matching_keys = [key for key in self.limiters.keys() if key.startswith(f"{domain}:")]
                return {key: self.limiters[key].get_status() for key in matching_keys}
            else:
                return {key: limiter.get_status() for key, limiter in self.limiters.items()}


# Global rate limiter instance
_global_rate_limiter = GlobalRateLimiter()


def rate_limited(domain: Optional[str] = None, endpoint_type: str = 'default', 
                tokens: int = 1, timeout: Optional[float] = 10.0):
    """
    Decorator to apply rate limiting to functions that make external requests.
    
    Args:
        domain: Domain to rate limit (extracted from URL if None)
        endpoint_type: Type of endpoint ('api', 'web', 'default')
        tokens: Number of tokens to acquire
        timeout: Maximum time to wait for rate limit
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract domain from URL if not provided
            target_domain = domain
            if not target_domain and args:
                # Try to extract domain from first argument (assuming it's a URL)
                url = str(args[0])
                if url.startswith(('http://', 'https://')):
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    target_domain = parsed.netloc
            
            if not target_domain:
                target_domain = 'unknown'
            
            # Acquire rate limit permission
            if not _global_rate_limiter.acquire(target_domain, endpoint_type, tokens, timeout):
                logger.warning(f"Rate limit exceeded for {target_domain} ({endpoint_type})")
                raise Exception(f"Rate limit exceeded for {target_domain}")
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_rate_limiter_status(domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the status of rate limiters.
    
    Args:
        domain: Specific domain to get status for (None for all)
        
    Returns:
        Dictionary with rate limiter statuses
    """
    return _global_rate_limiter.get_status(domain)


def configure_rate_limits(domain: str, config: RateLimitConfig, endpoint_type: str = 'default') -> None:
    """
    Configure rate limits for a specific domain.
    
    Args:
        domain: Domain name
        config: Rate limiting configuration
        endpoint_type: Type of endpoint
    """
    key = f"{domain}:{endpoint_type}"
    with _global_rate_limiter.lock:
        _global_rate_limiter.limiters[key] = CompositeRateLimiter(config)
        logger.info(f"Configured rate limits for {key}: {config}")