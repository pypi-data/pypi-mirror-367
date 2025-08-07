"""
Test script for the enhanced logging system.

This script tests the enhanced logging features:
1. Log rotation and storage options
2. Contextual logging
3. Log analysis
"""

import os
import time
from datetime import datetime

# Import logging utilities
from url_analyzer.utils.logging import (
    setup_logging,
    get_logger,
    create_contextual_logger,
    LogAnalyzer
)

def test_basic_logging():
    """Test basic logging functionality."""
    print("\n=== Testing Basic Logging ===")
    
    # Set up logging with enhanced options
    logger = setup_logging(
        log_level="DEBUG",
        log_file="logs/test_basic.log",
        rotation="size",
        max_size=1024 * 1024,  # 1 MB
        max_backups=3,
        include_hostname=True,
        include_process_id=True
    )
    
    # Log messages at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    print("Basic logging test completed. Check logs/test_basic.log")

def test_contextual_logging():
    """Test contextual logging functionality."""
    print("\n=== Testing Contextual Logging ===")
    
    # Create a contextual logger
    logger = create_contextual_logger("test_contextual")
    
    # Set request ID
    request_id = logger.set_request_id()
    print(f"Generated request ID: {request_id}")
    
    # Set user information
    logger.set_user_info(
        user_id="user123",
        session_id="session456",
        username="testuser",
        role="admin"
    )
    
    # Log with context
    logger.info("User logged in")
    
    # Add more context
    logger.add_context(
        feature="login",
        action="authenticate",
        result="success"
    )
    
    # Log with additional context
    logger.info("Authentication successful")
    
    # Use context manager for temporary context
    with logger.with_context(operation="password_check"):
        logger.info("Password validated")
    
    # Log after context manager (operation context should be gone)
    logger.info("Redirecting to dashboard")
    
    # Performance tracking
    logger.start_timer("database_query")
    time.sleep(0.1)  # Simulate database query
    elapsed = logger.stop_timer("database_query")
    
    # Log performance information
    logger.log_performance(
        operation="database_query",
        elapsed=elapsed,
        details={
            "query": "SELECT * FROM users",
            "rows": 10
        }
    )
    
    print("Contextual logging test completed. Check logs/url_analyzer.log")

def test_log_rotation():
    """Test log rotation functionality."""
    print("\n=== Testing Log Rotation ===")
    
    # Set up logging with time-based rotation
    logger = setup_logging(
        log_level="INFO",
        log_file="logs/test_rotation.log",
        rotation="hourly",
        max_backups=5,
        compress_logs=True,
        log_file_pattern="{name}_{date}.log"
    )
    
    # Log some messages
    for i in range(10):
        logger.info(f"Test message {i}")
    
    print("Log rotation test completed. Check logs directory")

def test_log_analyzer():
    """Test log analyzer functionality."""
    print("\n=== Testing Log Analyzer ===")
    
    # Generate some test logs
    logger = setup_logging(
        log_level="DEBUG",
        log_file="logs/analyzer_test.log"
    )
    
    # Log messages with different levels and contexts
    contextual_logger = create_contextual_logger("analyzer_test")
    
    # Log different types of messages
    for i in range(5):
        contextual_logger.set_request_id()
        contextual_logger.set_user_info(user_id=f"user{i}", role=f"role{i%2}")
        
        contextual_logger.debug(f"Debug message {i}")
        contextual_logger.info(f"Info message {i}")
        
        if i % 2 == 0:
            contextual_logger.warning(f"Warning message {i}")
        
        if i % 3 == 0:
            contextual_logger.error(f"Error message {i}")
            
        time.sleep(0.1)  # Space out the timestamps
    
    # Create a log analyzer
    analyzer = LogAnalyzer("logs/analyzer_test.log")
    
    # Parse the log file
    entries = analyzer.parse_file()
    print(f"Parsed {len(entries)} log entries")
    
    # Filter logs
    error_logs = analyzer.filter_logs(level="ERROR")
    print(f"Found {len(error_logs)} error logs")
    
    # Search logs
    search_results = analyzer.search("message 3")
    print(f"Found {len(search_results)} entries containing 'message 3'")
    
    # Get statistics
    stats = analyzer.get_statistics()
    print("\nLog Statistics:")
    print(f"Total entries: {stats.get('total_entries', 0)}")
    print(f"Log levels: {stats.get('level_counts', {})}")
    
    # Generate report
    report_path = analyzer.generate_report("logs/analysis_report.md")
    print(f"\nGenerated report at: {report_path}")
    
    # Try to generate visualizations (will be skipped if matplotlib is not installed)
    try:
        viz_path = analyzer.visualize("logs/analysis_charts.png")
        if viz_path:
            print(f"Generated visualizations at: {viz_path}")
    except Exception as e:
        print(f"Visualization skipped: {e}")
    
    print("Log analyzer test completed")

def main():
    """Run all tests."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run tests
    test_basic_logging()
    test_contextual_logging()
    test_log_rotation()
    test_log_analyzer()
    
    print("\nAll logging tests completed successfully!")

if __name__ == "__main__":
    main()