"""
Test file for the URL Analyzer API.

This file contains tests for the URL Analyzer API implementation.
"""

import unittest
from typing import Dict, Any, List

from url_analyzer.api.core import URLAnalyzerAPI
from url_analyzer.api.models import APIVersion


class TestURLAnalyzerAPI(unittest.TestCase):
    """Test cases for the URL Analyzer API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = URLAnalyzerAPI()
        self.test_urls = [
            "https://example.com",
            "https://facebook.com",
            "https://google.com/analytics"
        ]
    
    def test_api_initialization(self):
        """Test API initialization."""
        self.assertIsNotNone(self.api)
        self.assertEqual(self.api.version, APIVersion.V1)
        self.assertIsNotNone(self.api.config)
    
    def test_analyze_url(self):
        """Test analyzing a single URL."""
        response = self.api.analyze_url("https://example.com")
        
        # Check response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
        self.assertEqual(response.version, APIVersion.V1)
        
        # Check result
        result = response.data
        self.assertEqual(result.url, "https://example.com")
        self.assertIsNotNone(result.category)
        self.assertIsNotNone(result.metadata)
    
    def test_analyze_url_with_content(self):
        """Test analyzing a URL with content analysis."""
        response = self.api.analyze_url(
            "https://example.com",
            include_content=True
        )
        
        # Check response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
        
        # Check result
        result = response.data
        self.assertIsNotNone(result.content)
        self.assertIsNotNone(result.content.title)
        self.assertIsNotNone(result.content.description)
    
    def test_analyze_urls(self):
        """Test analyzing multiple URLs."""
        response = self.api.analyze_urls(self.test_urls)
        
        # Check response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
        
        # Check batch result
        batch_result = response.data
        self.assertEqual(batch_result.total_urls, len(self.test_urls))
        self.assertEqual(len(batch_result.results), len(self.test_urls))
        self.assertGreaterEqual(batch_result.successful_urls, 0)
        self.assertGreaterEqual(batch_result.execution_time, 0)
    
    def test_custom_patterns(self):
        """Test analyzing a URL with custom patterns."""
        custom_patterns = {
            "sensitive_patterns": ["private", "confidential"],
            "ugc_patterns": ["user", "profile", "comment"],
            "junk_subcategories": {
                "Advertising": ["ad", "sponsor", "promotion"],
                "Analytics": ["stat", "metric", "track"]
            }
        }
        
        response = self.api.analyze_url(
            "https://example.com/user/profile",
            custom_patterns=custom_patterns
        )
        
        # Check response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
    
    def test_api_version(self):
        """Test getting and setting API version."""
        # Get initial version
        initial_version = self.api.get_version()
        self.assertEqual(initial_version, APIVersion.V1)
        
        # Set new version
        self.api.set_version(APIVersion.V2)
        new_version = self.api.get_version()
        self.assertEqual(new_version, APIVersion.V2)
    
    def test_to_dict(self):
        """Test converting results to dictionaries."""
        response = self.api.analyze_url("https://example.com")
        
        # Convert response to dictionary
        response_dict = response.to_dict()
        
        # Check dictionary structure
        self.assertIsInstance(response_dict, dict)
        self.assertIn("success", response_dict)
        self.assertIn("version", response_dict)
        self.assertIn("data", response_dict)
        
        # Check data dictionary
        data_dict = response_dict["data"]
        self.assertIsInstance(data_dict, dict)
        self.assertIn("url", data_dict)
        self.assertIn("category", data_dict)
        self.assertIn("is_sensitive", data_dict)
    
    def test_error_handling(self):
        """Test error handling in the API."""
        # Test with an invalid URL
        response = self.api.analyze_url("not-a-valid-url")
        
        # The API should still return a response, but with error information
        self.assertIsNotNone(response)
        
        # The result should contain error information
        result = response.data
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()