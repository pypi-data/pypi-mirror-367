"""
Migration tests for URL Analyzer.

This module tests the modular implementation of the URL Analyzer package.
It ensures that all key functionality works correctly after the migration
from the monolithic script to the modular package.
"""

import unittest
import os
import sys
import tempfile
import pandas as pd
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import from modular package
from url_analyzer.config.manager import (
    load_config, save_config, compile_patterns,
    get_api_url, get_cache_file_path, get_max_workers,
    get_request_timeout, ConfigurationError, get_api_key
)
from url_analyzer.core.classification import classify_url, get_base_domain
from url_analyzer.core.analysis import fetch_url_data, load_cache, save_cache
from url_analyzer.data.processing import process_file, print_summary
from url_analyzer.reporting.html_report import (
    generate_html_report, generate_time_analysis_charts, 
    generate_sankey_diagram, list_available_templates,
    generate_report_from_template
)

class TestMigration(unittest.TestCase):
    """Test cases for the modular implementation of URL Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.temp_config_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_config_filename = self.temp_config_file.name
        
        # Create test config data
        self.test_config = {
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
                "max_workers": 10,
                "timeout": 5,
                "cache_file": "test_cache.json"
            }
        }
        
        # Write test config to file
        with open(self.temp_config_filename, 'w') as f:
            json.dump(self.test_config, f)
        
        self.temp_config_file.close()
        
        # Create a temporary CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        self.temp_filename = self.temp_file.name
        
        # Create test data
        test_data = pd.DataFrame({
            'Domain_name': [
                'https://www.google.com',
                'https://www.facebook.com',
                'https://www.example.com/about',
                'https://analytics.google.com',
                'https://www.example.com/user/123',
                'https://adservice.google.com'
            ],
            'Client_Name': ['TestClient'] * 6,
            'MAC_address': ['00:00:00:00:00:00'] * 6,
            'Access_time': [
                '2025-08-01 08:30:00',
                '2025-08-01 09:15:00',
                '2025-08-01 10:45:00',
                '2025-08-01 12:30:00',
                '2025-08-01 14:20:00',
                '2025-08-01 16:10:00'
            ]
        })
        
        # Save test data to CSV
        test_data.to_csv(self.temp_filename, index=False)
        self.temp_file.close()
        
        # Compile patterns
        self.compiled_patterns = compile_patterns(self.test_config)
        
        # Create a mock CLI args object
        self.mock_args = MagicMock()
        self.mock_args.live_scan = False
        self.mock_args.summarize = False
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_config_filename):
            os.unlink(self.temp_config_filename)
        
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)
    
    def test_config_management(self):
        """Test that config management functions work correctly."""
        # Test load_config
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertTrue('sensitive_patterns' in config)
        
        # Test save_config and load_config
        save_config(self.test_config, self.temp_config_filename)
        loaded_config = load_config(self.temp_config_filename)
        
        # Check that all keys from test_config are in loaded_config with the same values
        for key, value in self.test_config.items():
            self.assertIn(key, loaded_config)
            self.assertEqual(value, loaded_config[key])
    
    def test_url_classification(self):
        """Test that URL classification works correctly."""
        urls_to_test = [
            'https://www.google.com',
            'https://www.facebook.com',
            'https://www.example.com/about',
            'https://analytics.google.com',
            'https://www.example.com/user/123',
            'https://adservice.google.com'
        ]
        
        # Expected results based on our test configuration
        expected_results = {
            'https://www.google.com': ('Uncategorized', False),
            'https://www.facebook.com': ('Uncategorized', True),
            'https://www.example.com/about': ('Uncategorized', False),
            'https://analytics.google.com': ('Analytics', False),
            'https://www.example.com/user/123': ('User-Generated', False),
            'https://adservice.google.com': ('Advertising', False)
        }
        
        for url in urls_to_test:
            category, is_sensitive = classify_url(url, self.compiled_patterns)
            expected_category, expected_sensitive = expected_results[url]
            self.assertEqual(category, expected_category, f"Category differs for URL: {url}")
            self.assertEqual(is_sensitive, expected_sensitive, f"Sensitivity differs for URL: {url}")
    
    def test_base_domain_extraction(self):
        """Test that base domain extraction works correctly."""
        urls_to_test = [
            'https://www.google.com',
            'https://subdomain.example.co.uk',
            'invalid-url'
        ]
        
        expected_results = {
            'https://www.google.com': 'google.com',
            'https://subdomain.example.co.uk': 'example.co.uk',
            'invalid-url': ''
        }
        
        for url in urls_to_test:
            result = get_base_domain(url)
            self.assertEqual(result, expected_results[url], f"Base domain extraction incorrect for URL: {url}")
    
    def test_fetch_url_data(self):
        """Test that URL data fetching works correctly."""
        # Test the function without mocking
        url, result = fetch_url_data('https://example.com', False, self.test_config)
        
        # Verify the results
        self.assertEqual(url, 'https://example.com')
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIsInstance(result.get('title'), str)
        self.assertTrue(len(result.get('title')) > 0)
    
    def test_process_file(self):
        """Test that file processing works correctly."""
        # Process the file
        df = process_file(self.temp_filename, self.compiled_patterns, self.mock_args)
        
        # Verify the results
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        
        # Check that essential columns are present
        essential_columns = ['Domain_name', 'URL_Category', 'Is_Sensitive', 'Base_Domain']
        for col in essential_columns:
            self.assertIn(col, df.columns)
        
        # Check URL categories
        categories = df['URL_Category'].value_counts().to_dict()
        self.assertGreater(len(categories), 0)
        
        # Check that there's at least one sensitive URL (facebook.com)
        sensitive_count = df['Is_Sensitive'].sum()
        self.assertGreater(sensitive_count, 0)
        
        # Print all columns for debugging
        print(f"DataFrame columns: {df.columns.tolist()}")
    
    def test_html_report_generation(self):
        """Test that HTML report generation works in the modular implementation."""
        # Process the file to get a DataFrame
        df = process_file(self.temp_filename, self.compiled_patterns, self.mock_args)
        
        # Calculate stats for the report
        stats = {
            'total': len(df),
            'sensitive': df['Is_Sensitive'].sum(),
            'category_counts': df['URL_Category'].value_counts().to_dict()
        }
        
        # Create a temporary file for the report
        temp_report_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        temp_report_filename = temp_report_file.name
        temp_report_file.close()
        
        try:
            # Generate the report
            generate_html_report(df, temp_report_filename, stats)
            
            # Check that the report file exists and has content
            self.assertTrue(os.path.exists(temp_report_filename))
            with open(temp_report_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('URL Analysis Report', content)
                self.assertIn('Detailed URL Data', content)
        finally:
            # Clean up
            if os.path.exists(temp_report_filename):
                os.unlink(temp_report_filename)
    
    def test_visualization_functions(self):
        """Test that visualization functions work in the modular implementation."""
        # Process the file to get a DataFrame
        df = process_file(self.temp_filename, self.compiled_patterns, self.mock_args)
        
        # Test time analysis charts
        time_charts_html = generate_time_analysis_charts(df)
        self.assertIsInstance(time_charts_html, str)
        
        # Test sankey diagram
        sankey_html = generate_sankey_diagram(df)
        self.assertIsInstance(sankey_html, str)
    
    def test_template_listing(self):
        """Test that template listing works in the modular implementation."""
        templates = list_available_templates()
        self.assertIsInstance(templates, list)
        self.assertTrue(len(templates) > 0)
        self.assertTrue(all('name' in template and 'filename' in template for template in templates))
    
    def test_report_from_template(self):
        """Test that report generation from template works in the modular implementation."""
        # Process the file to get a DataFrame
        df = process_file(self.temp_filename, self.compiled_patterns, self.mock_args)
        
        # Calculate stats for the report
        stats = {
            'total': len(df),
            'sensitive': df['Is_Sensitive'].sum(),
            'category_counts': df['URL_Category'].value_counts().to_dict()
        }
        
        # Create a temporary file for the report
        temp_report_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        temp_report_filename = temp_report_file.name
        temp_report_file.close()
        
        try:
            # Generate the report using the default template
            report_path = generate_report_from_template(df, temp_report_filename, stats)
            
            # Check that the report file exists and has content
            self.assertTrue(os.path.exists(report_path))
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('URL Analysis Report', content)
        finally:
            # Clean up
            if os.path.exists(temp_report_filename):
                os.unlink(temp_report_filename)

if __name__ == '__main__':
    unittest.main()