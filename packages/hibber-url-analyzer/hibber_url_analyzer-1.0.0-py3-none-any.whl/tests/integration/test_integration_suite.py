"""
Comprehensive integration test suite for URL Analyzer.

This module contains integration tests that verify the interaction between
different components of the URL Analyzer system. These tests ensure that
the components work together correctly in real-world scenarios.
"""

import unittest
import tempfile
import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

# Import the modules to test
from url_analyzer.analysis import (
    URLContent, 
    ContentSummary,
    FetchResult,
    AnalysisResult,
    AnalysisOptions,
    RequestsURLFetcher,
    HTMLContentAnalyzer,
    DefaultAnalysisService,
    AdvancedAnalytics,
    RelationshipMapper
)
from url_analyzer.analysis.topic_modeling import TopicModeler
from url_analyzer.analysis.relationship_mapping import analyze_url_relationships
from config_manager import load_config, save_config, create_default_config


class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests with common setup and teardown."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a temporary config file
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.default_config = create_default_config()
        save_config(self.default_config, self.config_file)
        
        # Create a temporary cache file
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")
        
        # Sample URL data for testing
        self.sample_url_data = [
            {
                "url": "https://example.com/page1",
                "content": "This is a sample page about technology and programming.",
                "html": "<html><body>This is a sample page about technology and programming.</body></html>",
                "timestamp": datetime.now() - timedelta(days=5),
                "category": "Technology",
                "domain": "example.com"
            },
            {
                "url": "https://example.com/page2",
                "content": "Another page about science and research projects.",
                "html": "<html><body>Another page about science and research projects.</body></html>",
                "timestamp": datetime.now() - timedelta(days=4),
                "category": "Science",
                "domain": "example.com"
            },
            {
                "url": "https://example.org/page1",
                "content": "Information about data analysis and statistics.",
                "html": "<html><body>Information about data analysis and statistics.</body></html>",
                "timestamp": datetime.now() - timedelta(days=3),
                "category": "Technology",
                "domain": "example.org"
            }
        ]
        
        # Sample URLs for testing
        self.sample_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.org/page1"
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)


class TestAnalysisIntegration(IntegrationTestBase):
    """Integration tests for the analysis components."""
    
    def test_fetch_and_analyze_integration(self):
        """Test the integration of URL fetching and content analysis."""
        # Skip this test if we're not connected to the internet
        try:
            import socket
            socket.create_connection(("www.example.com", 80), timeout=1)
        except (socket.timeout, socket.error):
            self.skipTest("No internet connection available")
        
        # Create the components
        fetcher = RequestsURLFetcher(timeout=5)
        analyzer = HTMLContentAnalyzer()
        service = DefaultAnalysisService(fetcher=fetcher, analyzers=[analyzer])
        
        # Fetch and analyze a URL
        url = "https://example.com"
        options = AnalysisOptions({"include_metadata": True})
        
        result = service.analyze_url(url, options)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result.url, url)
        self.assertIsNotNone(result.content)
        self.assertIsNotNone(result.analysis_results)
        self.assertGreaterEqual(len(result.analysis_results), 1)
    
    def test_advanced_analytics_integration(self):
        """Test the integration of advanced analytics components."""
        # Create the components
        advanced_analytics = AdvancedAnalytics()
        
        # Analyze the sample URL data
        results = advanced_analytics.comprehensive_analysis(self.sample_url_data)
        
        # Verify the results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)
        self.assertGreaterEqual(len(results), 1)
    
    def test_relationship_mapping_integration(self):
        """Test the integration of relationship mapping components."""
        # Create the components
        mapper = RelationshipMapper()
        
        # Map relationships in the sample URL data
        try:
            results = mapper.map_url_relationships(self.sample_url_data)
            
            # Verify the results if NetworkX is available
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)
            self.assertIn("url_relationships", results)
            self.assertIn("domain_relationships", results)
            
        except Exception as e:
            # Skip if NetworkX is not available
            if "NetworkX library is required" in str(e):
                self.skipTest("NetworkX library is not available")
            else:
                raise


class TestConfigIntegration(IntegrationTestBase):
    """Integration tests for configuration management."""
    
    def test_config_load_save_integration(self):
        """Test the integration of configuration loading and saving."""
        # Load the config
        config = load_config(self.config_file)
        
        # Modify the config
        config["scan_settings"]["timeout"] = 10
        config["scan_settings"]["cache_file"] = self.cache_file
        
        # Save the config
        save_config(config, self.config_file)
        
        # Load the config again
        reloaded_config = load_config(self.config_file)
        
        # Verify the changes were saved
        self.assertEqual(reloaded_config["scan_settings"]["timeout"], 10)
        self.assertEqual(reloaded_config["scan_settings"]["cache_file"], self.cache_file)


class TestEndToEndAnalysis(IntegrationTestBase):
    """End-to-end tests for URL analysis workflow."""
    
    def test_complete_analysis_workflow(self):
        """Test the complete URL analysis workflow."""
        # Skip this test if we're not connected to the internet
        try:
            import socket
            socket.create_connection(("www.example.com", 80), timeout=1)
        except (socket.timeout, socket.error):
            self.skipTest("No internet connection available")
        
        # 1. Load configuration
        config = load_config(self.config_file)
        
        # 2. Set up components
        fetcher = RequestsURLFetcher(timeout=config["scan_settings"]["timeout"])
        analyzers = [HTMLContentAnalyzer()]
        service = DefaultAnalysisService(fetcher=fetcher, analyzers=analyzers)
        
        # 3. Fetch and analyze URLs
        results = []
        for url in self.sample_urls[:1]:  # Just analyze one URL to keep the test fast
            options = AnalysisOptions({"include_metadata": True})
            result = service.analyze_url(url, options)
            results.append({
                "url": result.url,
                "content": result.content,
                "timestamp": datetime.now(),
                "status_code": result.status_code
            })
        
        # 4. Perform advanced analytics
        advanced_analytics = AdvancedAnalytics()
        analytics_results = advanced_analytics.comprehensive_analysis(results)
        
        # 5. Map relationships
        try:
            mapper = RelationshipMapper()
            relationship_results = mapper.map_url_relationships(results)
            
            # Verify relationship results if NetworkX is available
            self.assertIsNotNone(relationship_results)
            self.assertIsInstance(relationship_results, dict)
            
        except Exception as e:
            # Skip relationship mapping if NetworkX is not available
            if "NetworkX library is required" in str(e):
                self.skipTest("NetworkX library is not available for relationship mapping")
            else:
                raise
        
        # 6. Verify overall results
        self.assertIsNotNone(results)
        self.assertGreaterEqual(len(results), 1)
        self.assertIsNotNone(analytics_results)
        self.assertIsInstance(analytics_results, dict)


if __name__ == "__main__":
    unittest.main()