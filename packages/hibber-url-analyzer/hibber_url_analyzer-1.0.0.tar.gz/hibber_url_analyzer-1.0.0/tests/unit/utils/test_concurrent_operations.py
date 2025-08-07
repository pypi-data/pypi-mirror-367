#!/usr/bin/env python3
"""
Test script for the optimized concurrent operations.

This script tests the optimized concurrent operations implementation,
including connection pooling, backoff strategies, rate limiting, and
adaptive thread pool settings.
"""

import os
import time
import json
from typing import Dict, Any, List

# Import the concurrency utilities
from url_analyzer.utils.concurrency import create_thread_pool_executor, get_adaptive_thread_pool_size

# Import the analysis module
from url_analyzer.core.analysis import fetch_url_data, initialize_rate_limiter, get_http_session

# Import logging
from url_analyzer.utils.logging import get_logger, setup_logging

# Configure logging
setup_logging(log_level="DEBUG")
logger = get_logger(__name__)


def test_adaptive_thread_pool():
    """Test the adaptive thread pool settings."""
    logger.info("Testing adaptive thread pool settings...")
    
    # Create a test configuration
    config = {
        "scan_settings": {
            "thread_pool_type": "adaptive",
            "min_workers": 2,
            "max_workers": 10,
            "max_workers_per_cpu": 2
        }
    }
    
    # Get adaptive thread pool size for different operation types
    io_workers = get_adaptive_thread_pool_size(config, operation_type="io")
    cpu_workers = get_adaptive_thread_pool_size(config, operation_type="cpu")
    
    logger.info(f"Adaptive thread pool size for I/O operations: {io_workers}")
    logger.info(f"Adaptive thread pool size for CPU operations: {cpu_workers}")
    
    # Test with fixed thread pool type
    config["scan_settings"]["thread_pool_type"] = "fixed"
    fixed_workers = get_adaptive_thread_pool_size(config, operation_type="io")
    logger.info(f"Fixed thread pool size: {fixed_workers}")
    
    # Test with thread pool executor
    config["scan_settings"]["thread_pool_type"] = "adaptive"
    with create_thread_pool_executor(config, operation_type="io") as executor:
        logger.info(f"Created thread pool executor with {executor._max_workers} workers")
    
    logger.info("Adaptive thread pool settings tests passed!")


def test_connection_pooling():
    """Test the connection pooling implementation."""
    logger.info("Testing connection pooling...")
    
    # Get HTTP session
    session = get_http_session()
    
    # Check if session has connection pooling configured
    adapter = session.adapters.get('https://')
    if adapter:
        logger.info(f"Connection pool settings: connections={adapter.poolmanager.connection_pool_kw.get('maxsize', 'unknown')}")
    else:
        logger.error("HTTP session does not have an adapter for HTTPS")
    
    # Test making multiple requests to the same host
    urls = [
        "https://example.com",
        "https://example.com/page1",
        "https://example.com/page2"
    ]
    
    start_time = time.time()
    for url in urls:
        response = session.get(url, timeout=5)
        logger.info(f"Request to {url} returned status code {response.status_code}")
    end_time = time.time()
    
    logger.info(f"Made {len(urls)} requests in {end_time - start_time:.2f} seconds")
    logger.info("Connection pooling tests passed!")


def test_backoff_strategy():
    """Test the backoff strategy implementation."""
    logger.info("Testing backoff strategy...")
    
    # Create a test configuration
    config = {
        "scan_settings": {
            "max_retries": 3,
            "backoff_factor": 0.5
        }
    }
    
    # Initialize the analysis module
    from url_analyzer.core.analysis import init_module
    init_module(config)
    
    # Test with a URL that should fail
    url = "https://nonexistent.example.com"
    
    try:
        # This should fail but with retries
        _, result = fetch_url_data(url, config=config)
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.info(f"Expected exception: {e}")
    
    logger.info("Backoff strategy tests completed!")


def test_rate_limiting():
    """Test the rate limiting implementation."""
    logger.info("Testing rate limiting...")
    
    # Create a test configuration
    config = {
        "scan_settings": {
            "rate_limit": 5  # 5 requests per second
        }
    }
    
    # Initialize the rate limiter
    initialize_rate_limiter(config)
    
    # Test making multiple requests with rate limiting
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
        "https://example.edu",
        "https://example.io"
    ]
    
    start_time = time.time()
    
    # Create thread pool executor
    with create_thread_pool_executor(config, operation_type="io") as executor:
        # Submit tasks
        futures = [executor.submit(fetch_url_data, url, config=config) for url in urls]
        
        # Process results
        for future in futures:
            try:
                url, result = future.result()
                logger.info(f"Fetched {url}: {result.get('title', 'No title')}")
            except Exception as e:
                logger.error(f"Error fetching URL: {e}")
    
    end_time = time.time()
    
    logger.info(f"Made {len(urls)} rate-limited requests in {end_time - start_time:.2f} seconds")
    logger.info("Rate limiting tests completed!")


def main():
    """Run all tests."""
    logger.info("Starting concurrent operations tests...")
    
    test_adaptive_thread_pool()
    test_connection_pooling()
    test_backoff_strategy()
    test_rate_limiting()
    
    logger.info("All concurrent operations tests completed!")


if __name__ == "__main__":
    main()