"""
Test package for URL Analyzer.

This package contains all test modules and fixtures for the URL Analyzer project.
"""

# Make fixtures easily accessible
from .fixtures import (
    # Mock classes
    MockResponse,
    MockSession,
    MockBeautifulSoup,
    MockTag,
    MockCache,
    MockFileSystem,
    MockAPI,
    # Base test classes
    BaseURLAnalyzerTest,
    BaseSecurityTest,
    BaseIntegrationTest,
    # Utility functions
    create_test_config,
    create_test_csv_file,
    create_test_urls,
    create_temp_config_file,
    create_temp_cache_file,
    generate_malicious_inputs,
    create_integration_test_data,
    create_performance_test_urls,
    create_test_report_data,
    # Mock decorators
    mock_requests,
    mock_beautifulsoup,
    mock_file_system,
    mock_all
)

__all__ = [
    # Mock classes
    'MockResponse',
    'MockSession', 
    'MockBeautifulSoup',
    'MockTag',
    'MockCache',
    'MockFileSystem',
    'MockAPI',
    # Base test classes
    'BaseURLAnalyzerTest',
    'BaseSecurityTest',
    'BaseIntegrationTest',
    # Utility functions
    'create_test_config',
    'create_test_csv_file',
    'create_test_urls',
    'create_temp_config_file',
    'create_temp_cache_file',
    'generate_malicious_inputs',
    'create_integration_test_data',
    'create_performance_test_urls',
    'create_test_report_data',
    # Mock decorators
    'mock_requests',
    'mock_beautifulsoup',
    'mock_file_system',
    'mock_all'
]