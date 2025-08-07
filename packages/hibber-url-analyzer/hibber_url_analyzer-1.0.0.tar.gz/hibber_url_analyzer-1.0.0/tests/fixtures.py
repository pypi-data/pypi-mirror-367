"""
Test fixtures and mocks for URL Analyzer tests.

This module provides mock implementations of external dependencies used by the URL Analyzer,
including HTTP requests, file system operations, external APIs, and HTML parsing.
"""

import os
import json
import tempfile
import unittest
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from unittest.mock import MagicMock, patch
import pandas as pd

# Try to import the dependencies we're mocking
try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
    BS4_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    BS4_AVAILABLE = False


class MockResponse:
    """Mock implementation of requests.Response."""
    
    def __init__(
        self,
        status_code: int = 200,
        content: bytes = b"",
        text: str = "",
        headers: Optional[Dict[str, str]] = None,
        url: str = "https://example.com",
        history: Optional[List[Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        raise_for_status_exception: Optional[Exception] = None
    ):
        """
        Initialize a mock response.
        
        Args:
            status_code: HTTP status code
            content: Response content as bytes
            text: Response text
            headers: Response headers
            url: Response URL
            history: Response history
            json_data: JSON data to return from .json() method
            raise_for_status_exception: Exception to raise from .raise_for_status() method
        """
        self.status_code = status_code
        self.content = content
        self.text = text
        self.headers = headers or {}
        self.url = url
        self.history = history or []
        self._json_data = json_data
        self._raise_for_status_exception = raise_for_status_exception
    
    def json(self) -> Dict[str, Any]:
        """Return JSON data."""
        if self._json_data is not None:
            return self._json_data
        
        if not self.text:
            return {}
        
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            raise ValueError("Response content is not valid JSON")
    
    def raise_for_status(self) -> None:
        """Raise an exception if the status code indicates an error."""
        if self._raise_for_status_exception:
            raise self._raise_for_status_exception
        
        if 400 <= self.status_code < 600:
            raise requests.HTTPError(f"HTTP Error: {self.status_code}")


class MockSession:
    """Mock implementation of requests.Session."""
    
    def __init__(self, responses: Optional[Dict[str, MockResponse]] = None):
        """
        Initialize a mock session.
        
        Args:
            responses: Dictionary mapping URLs to mock responses
        """
        self.responses = responses or {}
        self.requests = []
        self.headers = {}
        self.adapters = {'https://': MagicMock()}
        self.hooks = {'response': []}
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> MockResponse:
        """
        Mock GET request.
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Request headers
            timeout: Request timeout
            allow_redirects: Whether to follow redirects
            **kwargs: Additional arguments
            
        Returns:
            Mock response
        """
        # Record the request
        self.requests.append({
            'method': 'GET',
            'url': url,
            'params': params,
            'headers': headers,
            'timeout': timeout,
            'allow_redirects': allow_redirects,
            'kwargs': kwargs
        })
        
        # Return the mock response if it exists
        if url in self.responses:
            return self.responses[url]
        
        # Return a default response
        return MockResponse(
            status_code=200,
            text=f"<html><head><title>Mock Response for {url}</title></head><body>This is a mock response.</body></html>",
            url=url
        )
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> MockResponse:
        """
        Mock POST request.
        
        Args:
            url: URL to request
            data: Form data
            json: JSON data
            headers: Request headers
            timeout: Request timeout
            allow_redirects: Whether to follow redirects
            **kwargs: Additional arguments
            
        Returns:
            Mock response
        """
        # Record the request
        self.requests.append({
            'method': 'POST',
            'url': url,
            'data': data,
            'json': json,
            'headers': headers,
            'timeout': timeout,
            'allow_redirects': allow_redirects,
            'kwargs': kwargs
        })
        
        # Return the mock response if it exists
        if url in self.responses:
            return self.responses[url]
        
        # Return a default response
        return MockResponse(
            status_code=200,
            text='{"status": "success", "message": "This is a mock response."}',
            url=url
        )
    
    def close(self) -> None:
        """Close the session."""
        pass


class MockBeautifulSoup:
    """Mock implementation of BeautifulSoup."""
    
    def __init__(self, html: str, parser: str = "html.parser"):
        """
        Initialize a mock BeautifulSoup object.
        
        Args:
            html: HTML content
            parser: HTML parser
        """
        self.html = html
        self.parser = parser
        self.title = MockTag("title", "Mock Title")
        self.meta = [
            MockTag("meta", "", {"name": "description", "content": "Mock description"}),
            MockTag("meta", "", {"property": "og:title", "content": "Mock OG Title"})
        ]
    
    def find(self, tag_name: str, attrs: Optional[Dict[str, str]] = None) -> Optional["MockTag"]:
        """
        Find a tag in the HTML.
        
        Args:
            tag_name: Tag name
            attrs: Tag attributes
            
        Returns:
            Mock tag or None
        """
        if tag_name == "title":
            return self.title
        
        if tag_name == "meta" and attrs:
            for meta in self.meta:
                match = True
                for key, value in attrs.items():
                    if key not in meta.attrs or meta.attrs[key] != value:
                        match = False
                        break
                
                if match:
                    return meta
        
        return None
    
    def find_all(self, tag_name: str, attrs: Optional[Dict[str, str]] = None) -> List["MockTag"]:
        """
        Find all tags in the HTML.
        
        Args:
            tag_name: Tag name
            attrs: Tag attributes
            
        Returns:
            List of mock tags
        """
        if tag_name == "meta":
            if not attrs:
                return self.meta
            
            result = []
            for meta in self.meta:
                match = True
                for key, value in attrs.items():
                    if key not in meta.attrs or meta.attrs[key] != value:
                        match = False
                        break
                
                if match:
                    result.append(meta)
            
            return result
        
        return []


class MockTag:
    """Mock implementation of a BeautifulSoup tag."""
    
    def __init__(self, name: str, text: str = "", attrs: Optional[Dict[str, str]] = None):
        """
        Initialize a mock tag.
        
        Args:
            name: Tag name
            text: Tag text
            attrs: Tag attributes
        """
        self.name = name
        self.text = text
        self.attrs = attrs or {}
    
    def get(self, attr: str, default: Any = None) -> Any:
        """
        Get an attribute value.
        
        Args:
            attr: Attribute name
            default: Default value
            
        Returns:
            Attribute value or default
        """
        return self.attrs.get(attr, default)


class MockCache:
    """Mock implementation of the Cache class."""
    
    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        """
        Initialize a mock cache.
        
        Args:
            initial_data: Initial cache data
        """
        self.data = initial_data or {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value
            
        Returns:
            Cached value or default
        """
        if key in self.data:
            self.hits += 1
            return self.data[key]
        
        self.misses += 1
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.data[key] = value
    
    def clear(self) -> None:
        """Clear the cache."""
        self.data.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'pattern_cache_size': len(self.data),
            'result_cache_size': len(self.data)
        }


class MockFileSystem:
    """Mock implementation of file system operations."""
    
    def __init__(self, files: Optional[Dict[str, str]] = None):
        """
        Initialize a mock file system.
        
        Args:
            files: Dictionary mapping file paths to file contents
        """
        self.files = files or {}
    
    def read_file(self, path: str) -> str:
        """
        Read a file.
        
        Args:
            path: File path
            
        Returns:
            File contents
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        
        return self.files[path]
    
    def write_file(self, path: str, content: str) -> None:
        """
        Write a file.
        
        Args:
            path: File path
            content: File contents
        """
        self.files[path] = content
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: File path
            
        Returns:
            True if the file exists, False otherwise
        """
        return path in self.files
    
    def delete_file(self, path: str) -> None:
        """
        Delete a file.
        
        Args:
            path: File path
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        
        del self.files[path]


class MockAPI:
    """Mock implementation of external API calls."""
    
    def __init__(self, responses: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize a mock API.
        
        Args:
            responses: Dictionary mapping API endpoints to response data
        """
        self.responses = responses or {}
        self.requests = []
    
    def call(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call an API endpoint.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            ValueError: If the endpoint does not exist
        """
        # Record the request
        self.requests.append({
            'endpoint': endpoint,
            'data': data
        })
        
        # Return the mock response if it exists
        if endpoint in self.responses:
            return self.responses[endpoint]
        
        # Return a default response
        return {
            'status': 'success',
            'message': f'This is a mock response for {endpoint}',
            'data': {}
        }


# Create test data fixtures

def create_test_dataframe(num_rows: int = 10) -> pd.DataFrame:
    """
    Create a test DataFrame with URL data.
    
    Args:
        num_rows: Number of rows in the DataFrame
        
    Returns:
        Test DataFrame
    """
    data = {
        'Domain_name': [f"https://example{i}.com/page/{i}" for i in range(num_rows)],
        'Access_time': [f"2025-08-{(i % 28) + 1:02d} {(i % 24):02d}:00:00" for i in range(num_rows)],
        'Client_Name': [f"Client {chr(65 + (i % 3))}" for i in range(num_rows)],
        'MAC_address': [f"00:11:22:33:44:{(55 + i):02x}" for i in range(num_rows)]
    }
    
    return pd.DataFrame(data)


def create_test_csv(num_rows: int = 10) -> str:
    """
    Create a test CSV file with URL data.
    
    Args:
        num_rows: Number of rows in the CSV file
        
    Returns:
        Path to the created CSV file
    """
    df = create_test_dataframe(num_rows)
    
    # Create a temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_filename = temp_file.name
    
    # Save the DataFrame to CSV
    df.to_csv(temp_filename, index=False)
    temp_file.close()
    
    return temp_filename


def create_test_config() -> Dict[str, Any]:
    """
    Create a test configuration.
    
    Returns:
        Test configuration
    """
    return {
        'sensitive_patterns': ['facebook\\.com', 'twitter\\.com'],
        'ugc_patterns': ['/user/', '/profile/'],
        'junk_subcategories': {
            'Advertising': ['adservice', 'doubleclick\\.net'],
            'Analytics': ['analytics', 'tracking']
        },
        'api_settings': {
            'gemini_api_url': 'https://api.example.com'
        },
        'scan_settings': {
            'max_workers': 2,
            'timeout': 2,
            'cache_file': 'test_cache.json'
        }
    }


# Create patch decorators for common mocks

def mock_requests(func: Callable) -> Callable:
    """
    Decorator to mock requests.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    if not REQUESTS_AVAILABLE:
        return func
    
    # Create mock responses
    mock_responses = {
        'https://www.example.com': MockResponse(
            status_code=200,
            text='<html><head><title>Example Domain</title></head><body>This is an example domain.</body></html>',
            url='https://www.example.com'
        ),
        'https://www.facebook.com': MockResponse(
            status_code=200,
            text='<html><head><title>Facebook</title></head><body>This is Facebook.</body></html>',
            url='https://www.facebook.com'
        ),
        'https://analytics.google.com': MockResponse(
            status_code=200,
            text='<html><head><title>Google Analytics</title></head><body>This is Google Analytics.</body></html>',
            url='https://analytics.google.com'
        ),
        'https://api.example.com': MockResponse(
            status_code=200,
            text='{"status": "success", "data": {"summary": "This is a summary."}}',
            url='https://api.example.com'
        ),
        'https://error.example.com': MockResponse(
            status_code=404,
            text='<html><head><title>404 Not Found</title></head><body>Page not found.</body></html>',
            url='https://error.example.com',
            raise_for_status_exception=requests.HTTPError('HTTP Error: 404')
        )
    }
    
    # Create a mock session
    mock_session = MockSession(mock_responses)
    
    # Create patch decorators
    patches = [
        patch('requests.get', side_effect=mock_session.get),
        patch('requests.post', side_effect=mock_session.post),
        patch('requests.Session', return_value=mock_session)
    ]
    
    # Apply all patches
    for p in patches:
        func = p(func)
    
    return func


def mock_beautifulsoup(func: Callable) -> Callable:
    """
    Decorator to mock BeautifulSoup.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    if not BS4_AVAILABLE:
        return func
    
    # Create a mock BeautifulSoup
    def mock_bs4(html, parser=None):
        return MockBeautifulSoup(html, parser)
    
    # Apply the patch
    return patch('bs4.BeautifulSoup', side_effect=mock_bs4)(func)


def mock_file_system(func: Callable) -> Callable:
    """
    Decorator to mock file system operations.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    # Create a mock file system
    mock_fs = MockFileSystem({
        'config.json': json.dumps(create_test_config()),
        'test_cache.json': json.dumps({
            'https://www.example.com': {
                'title': 'Example Domain',
                'description': 'This is an example domain.',
                'timestamp': '2025-08-05T01:00:00'
            }
        })
    })
    
    # Create patch decorators
    patches = [
        patch('builtins.open', side_effect=lambda path, mode='r', *args, **kwargs: MagicMock()),
        patch('os.path.exists', side_effect=mock_fs.file_exists),
        patch('os.path.isfile', side_effect=mock_fs.file_exists),
        patch('json.load', side_effect=lambda f: json.loads(mock_fs.read_file(f.name))),
        patch('json.dump', side_effect=lambda obj, f: mock_fs.write_file(f.name, json.dumps(obj)))
    ]
    
    # Apply all patches
    for p in patches:
        func = p(func)
    
    return func


def mock_all(func: Callable) -> Callable:
    """
    Decorator to mock all external dependencies.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    return mock_requests(mock_beautifulsoup(mock_file_system(func)))


# Utility functions for common test setup patterns

def create_test_config() -> Dict[str, Any]:
    """
    Create a test configuration dictionary.
    
    Returns:
        Test configuration dictionary
    """
    return {
        "sensitive_patterns": ["facebook\\.com", "twitter\\.com"],
        "ugc_patterns": ["/user/", "/profile/"],
        "junk_subcategories": {
            "Advertising": ["adservice", "doubleclick\\.net"],
            "Analytics": ["analytics", "tracking"]
        },
        "api_settings": {
            "gemini_api_url": "https://api.example.com"
        },
        "scan_settings": {
            "max_workers": 20,
            "timeout": 7,
            "cache_file": "test_cache.json"
        }
    }


def create_test_csv_file(temp_dir: str, filename: str = "test_urls.csv") -> str:
    """
    Create a test CSV file with sample URLs.
    
    Args:
        temp_dir: Temporary directory path
        filename: CSV filename
        
    Returns:
        Path to the created CSV file
    """
    import pandas as pd
    
    file_path = os.path.join(temp_dir, filename)
    
    test_data = pd.DataFrame({
        'Domain_name': [
            'https://www.google.com',
            'https://www.facebook.com',
            'https://www.example.com/about',
            'https://analytics.google.com'
        ],
        'Client_Name': ['TestClient'] * 4,
        'MAC_address': ['00:00:00:00:00:00'] * 4
    })
    
    test_data.to_csv(file_path, index=False)
    return file_path


def create_test_urls() -> List[str]:
    """
    Create a list of test URLs.
    
    Returns:
        List of test URLs
    """
    return [
        "https://example.com",
        "https://example.org",
        "https://example.net",
        "https://www.facebook.com",
        "https://analytics.google.com"
    ]


def create_temp_config_file(temp_dir: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a temporary configuration file.
    
    Args:
        temp_dir: Temporary directory path
        config: Configuration dictionary (uses default if None)
        
    Returns:
        Path to the created config file
    """
    if config is None:
        config = create_test_config()
    
    config_path = os.path.join(temp_dir, "test_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path


def create_temp_cache_file(temp_dir: str, cache_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a temporary cache file.
    
    Args:
        temp_dir: Temporary directory path
        cache_data: Cache data dictionary (uses default if None)
        
    Returns:
        Path to the created cache file
    """
    if cache_data is None:
        cache_data = {
            'https://www.example.com': {
                'title': 'Example Domain',
                'description': 'This is an example domain.',
                'timestamp': '2025-08-05T01:00:00'
            }
        }
    
    cache_path = os.path.join(temp_dir, "test_cache.json")
    with open(cache_path, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    return cache_path


# Base Test Classes for Common Patterns

class BaseURLAnalyzerTest(unittest.TestCase):
    """
    Base test class for URL analyzer tests with common setup and teardown.
    
    This class provides:
    - Configuration loading and pattern compilation
    - Temporary file management
    - Common test data
    - Cleanup handling
    """
    
    def setUp(self):
        """Set up common test fixtures."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create configuration
        self.config_path = create_temp_config_file(self.temp_dir)
        self.config = create_test_config()
        
        # Create test data file
        self.test_csv_path = create_test_csv_file(self.temp_dir)
        
        # Create cache file
        self.cache_path = create_temp_cache_file(self.temp_dir)
        
        # Common test URLs
        self.test_urls = create_test_urls()
        
        # Load and compile patterns (if classification module is available)
        try:
            from url_analyzer.core.classification import compile_patterns
            self.patterns = compile_patterns(self.config)
        except ImportError:
            self.patterns = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class BaseSecurityTest(unittest.TestCase):
    """
    Base test class for security tests with malicious input generation.
    
    This class provides:
    - Malicious input patterns
    - Security test utilities
    - Temporary file management
    - Common security test scenarios
    """
    
    def setUp(self):
        """Set up security test fixtures."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create configuration and test files
        self.config_path = create_temp_config_file(self.temp_dir)
        self.cache_path = create_temp_cache_file(self.temp_dir)
        self.input_file = create_test_csv_file(self.temp_dir)
        
        # Create output directory
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate malicious inputs
        self.malicious_inputs = self._generate_malicious_inputs()
    
    def tearDown(self):
        """Clean up security test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _generate_malicious_inputs(self) -> Dict[str, List[str]]:
        """Generate malicious inputs for security testing."""
        return generate_malicious_inputs()


class BaseIntegrationTest(unittest.TestCase):
    """
    Base test class for integration tests with comprehensive setup.
    
    This class provides:
    - Multiple temporary files and directories
    - Mock services and APIs
    - Integration test data
    - Service lifecycle management
    """
    
    def setUp(self):
        """Set up integration test fixtures."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create all necessary files
        self.config_path = create_temp_config_file(self.temp_dir)
        self.cache_path = create_temp_cache_file(self.temp_dir)
        self.input_file = create_test_csv_file(self.temp_dir)
        
        # Create output directories
        self.output_dir = os.path.join(self.temp_dir, "output")
        self.reports_dir = os.path.join(self.temp_dir, "reports")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Create test data
        self.test_data = create_integration_test_data()
        
        # Initialize mock services
        self.mock_api = MockAPI()
        self.mock_cache = MockCache()
        self.mock_filesystem = MockFileSystem()
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


# Additional Utility Functions

def generate_malicious_inputs() -> Dict[str, List[str]]:
    """
    Generate comprehensive malicious inputs for security testing.
    
    Returns:
        Dictionary of malicious input categories and examples
    """
    return {
        "sql_injection": [
            "example.com' OR 1=1 --",
            "example.com; DROP TABLE urls;",
            "example.com' UNION SELECT username, password FROM users --",
            "example.com'; INSERT INTO users VALUES ('admin', 'password'); --"
        ],
        "xss": [
            "example.com/<script>alert('XSS')</script>",
            "example.com/\"><img src=x onerror=alert('XSS')>",
            "example.com/javascript:alert('XSS')",
            "example.com/<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ],
        "path_traversal": [
            "example.com/../../../etc/passwd",
            "example.com/..\\..\\..\\Windows\\system.ini",
            "example.com/%2e%2e/%2e%2e/etc/passwd",
            "example.com/....//....//etc/passwd"
        ],
        "command_injection": [
            "example.com; ls -la",
            "example.com && cat /etc/passwd",
            "example.com | whoami",
            "example.com; rm -rf /"
        ],
        "large_input": [
            "example.com/" + "A" * 10000,
            "example.com?" + "x=" * 5000,
            "example.com#" + "fragment" * 1000,
            "example.com/" + "B" * 50000
        ],
        "special_chars": [
            "example.com/%00",  # Null byte
            "example.com/%0A",  # Newline
            "example.com/%22%27%3C%3E",  # Quotes and brackets
            "example.com/%FF%FE%FD"  # Invalid UTF-8
        ],
        "protocol_attacks": [
            "file:///etc/passwd",
            "ftp://malicious.com/",
            "ldap://attacker.com/",
            "gopher://evil.com/"
        ]
    }


def create_integration_test_data() -> List[Dict[str, Any]]:
    """
    Create comprehensive test data for integration tests.
    
    Returns:
        List of test data dictionaries
    """
    return [
        {
            "url": "https://example.com",
            "category": "Corporate",
            "is_sensitive": False,
            "title": "Example Domain",
            "description": "This domain is for use in illustrative examples"
        },
        {
            "url": "https://www.facebook.com",
            "category": "Social Media",
            "is_sensitive": True,
            "title": "Facebook",
            "description": "Social networking service"
        },
        {
            "url": "https://analytics.google.com",
            "category": "Analytics",
            "is_sensitive": False,
            "title": "Google Analytics",
            "description": "Web analytics service"
        },
        {
            "url": "https://ads.yahoo.com",
            "category": "Advertising",
            "is_sensitive": False,
            "title": "Yahoo Ads",
            "description": "Online advertising platform"
        }
    ]


def create_performance_test_urls(count: int = 1000) -> List[str]:
    """
    Create a large list of URLs for performance testing.
    
    Args:
        count: Number of URLs to generate
        
    Returns:
        List of test URLs
    """
    import random
    import string
    
    domains = [
        "example.com", "test.org", "sample.net", "demo.co.uk",
        "facebook.com", "twitter.com", "google.com", "yahoo.com"
    ]
    
    paths = [
        "/", "/about", "/contact", "/products", "/services",
        "/user/profile", "/admin/dashboard", "/api/v1/data"
    ]
    
    urls = []
    for i in range(count):
        domain = random.choice(domains)
        path = random.choice(paths)
        # Add some randomization
        if random.random() < 0.3:
            subdomain = ''.join(random.choices(string.ascii_lowercase, k=5))
            domain = f"{subdomain}.{domain}"
        if random.random() < 0.2:
            query = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            path += f"?q={query}"
        
        urls.append(f"https://{domain}{path}")
    
    return urls


def create_test_report_data() -> Dict[str, Any]:
    """
    Create test data for report generation tests.
    
    Returns:
        Dictionary with report test data
    """
    return {
        "summary": {
            "total_urls": 100,
            "sensitive_urls": 25,
            "categories": {
                "Corporate": 40,
                "Social Media": 25,
                "Analytics": 20,
                "Advertising": 15
            }
        },
        "analysis_results": create_integration_test_data(),
        "metadata": {
            "analysis_date": "2025-08-06",
            "version": "1.0.0",
            "configuration": "default"
        }
    }