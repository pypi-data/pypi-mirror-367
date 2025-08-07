import unittest
import os
import pandas as pd
import sys
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the functions to test
from url_analyzer.core.classification import classify_url, get_base_domain
from url_analyzer.core.classification import compile_patterns
from url_analyzer.config.manager import load_config

class TestURLAnalyzer(unittest.TestCase):
    """Test cases for the URL Analyzer application."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = load_config()
        self.patterns = compile_patterns(self.config)
        
        # Create a temporary CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        self.temp_filename = self.temp_file.name
        
        # Create test data
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
        
        # Save test data to CSV
        test_data.to_csv(self.temp_filename, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)
    
    def test_should_extract_base_domain_from_valid_url(self):
        """Test that get_base_domain extracts the correct base domain from a valid URL."""
        result = get_base_domain('https://www.google.com')
        self.assertEqual(result, 'google.com')
    
    def test_should_extract_base_domain_from_subdomain_url(self):
        """Test that get_base_domain extracts the correct base domain from a subdomain URL."""
        result = get_base_domain('https://subdomain.example.co.uk')
        self.assertEqual(result, 'example.co.uk')
    
    def test_should_return_empty_string_for_invalid_url(self):
        """Test that get_base_domain returns empty string when given an invalid URL."""
        result = get_base_domain('invalid-url')
        self.assertEqual(result, '')
    
    def test_should_classify_facebook_url_as_sensitive(self):
        """Test that classify_url correctly identifies Facebook URLs as sensitive."""
        category, is_sensitive = classify_url('https://www.facebook.com', self.patterns)
        self.assertTrue(is_sensitive, "Facebook URL should be classified as sensitive")
    
    def test_should_classify_corporate_url_correctly(self):
        """Test that classify_url correctly classifies corporate URLs as non-sensitive."""
        category, is_sensitive = classify_url('https://www.example.com/about', self.patterns)
        self.assertEqual(category, 'Corporate', "URL should be classified as Corporate")
        self.assertFalse(is_sensitive, "Corporate URL should not be classified as sensitive")
    
    def test_should_classify_analytics_url_correctly(self):
        """Test that classify_url correctly classifies analytics URLs as non-sensitive."""
        category, is_sensitive = classify_url('https://analytics.google.com', self.patterns)
        self.assertEqual(category, 'Analytics', "URL should be classified as Analytics")
        self.assertFalse(is_sensitive, "Analytics URL should not be classified as sensitive")

if __name__ == '__main__':
    unittest.main()