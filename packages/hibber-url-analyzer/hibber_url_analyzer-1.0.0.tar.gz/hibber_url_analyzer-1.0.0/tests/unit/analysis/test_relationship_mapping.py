"""
Test module for the relationship mapping functionality.

This module tests the relationship mapping capabilities added to the URL Analyzer.
"""

import unittest
from datetime import datetime, timedelta
import tempfile
import os
import json

from url_analyzer.analysis.relationship_mapping import (
    RelationshipMapper,
    RelationshipAnalyzer,
    analyze_url_relationships
)
from url_analyzer.analysis.domain import URLContent, AnalysisOptions


class TestRelationshipMapping(unittest.TestCase):
    """Test case for the relationship mapping functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mapper = RelationshipMapper()
        
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
            },
            {
                "url": "https://subdomain.example.org/page2",
                "content": "More details about machine learning algorithms.",
                "html": "<html><body>More details about machine learning algorithms.</body></html>",
                "timestamp": datetime.now() - timedelta(days=2),
                "category": "Technology",
                "domain": "example.org"
            },
            {
                "url": "https://another-example.com/page1",
                "content": "Information about web development and design.",
                "html": "<html><body>Information about web development and design.</body></html>",
                "timestamp": datetime.now() - timedelta(days=1),
                "category": "Technology",
                "domain": "another-example.com"
            }
        ]

    def test_initialization(self):
        """Test that the RelationshipMapper class initializes correctly."""
        self.assertIsNotNone(self.mapper)
        
        # Check if NetworkX is available
        try:
            import networkx as nx
            self.assertIsNotNone(self.mapper.url_graph)
            self.assertIsNotNone(self.mapper.domain_graph)
        except ImportError:
            self.assertIsNone(self.mapper.url_graph)
            self.assertIsNone(self.mapper.domain_graph)
            self.skipTest("NetworkX not available, skipping graph tests")

    def test_map_url_relationships(self):
        """Test the URL relationship mapping functionality."""
        try:
            import networkx as nx
            results = self.mapper.map_url_relationships(self.sample_url_data)
            
            # Check that the results contain the expected keys
            self.assertIn("url_relationships", results)
            self.assertIn("domain_relationships", results)
            self.assertIn("communities", results)
            self.assertIn("relationships_found", results)
            
            # Check URL relationships
            url_relationships = results["url_relationships"]
            self.assertEqual(url_relationships["node_count"], 5)  # 5 URLs
            self.assertGreaterEqual(url_relationships["edge_count"], 4)  # At least 4 sequential edges
            
            # Check domain relationships
            domain_relationships = results["domain_relationships"]
            self.assertEqual(domain_relationships["node_count"], 3)  # 3 domains
            
            # Check metrics
            self.assertIn("metrics", url_relationships)
            self.assertIn("metrics", domain_relationships)
            
        except ImportError:
            self.skipTest("NetworkX not available, skipping relationship mapping tests")

    def test_calculate_content_similarity(self):
        """Test the content similarity calculation."""
        content1 = "This is a sample page about technology and programming."
        content2 = "Another page about technology and programming concepts."
        content3 = "Information about data analysis and statistics."
        
        # Similar content
        similarity1 = self.mapper._calculate_content_similarity(content1, content2)
        self.assertGreaterEqual(similarity1, 0.3)
        
        # Less similar content
        similarity2 = self.mapper._calculate_content_similarity(content1, content3)
        self.assertLessEqual(similarity2, 0.3)
        
        # Same content
        similarity3 = self.mapper._calculate_content_similarity(content1, content1)
        self.assertEqual(similarity3, 1.0)
        
        # Empty content
        similarity4 = self.mapper._calculate_content_similarity("", "")
        self.assertEqual(similarity4, 0.0)

    def test_calculate_domain_similarity(self):
        """Test the domain similarity calculation."""
        # Same domain, different subdomains
        similarity1 = self.mapper._calculate_domain_similarity(
            "subdomain1.example.com", "subdomain2.example.com"
        )
        self.assertGreaterEqual(similarity1, 0.5)
        
        # Different domains
        similarity2 = self.mapper._calculate_domain_similarity(
            "example.com", "example.org"
        )
        self.assertLess(similarity2, 0.5)
        
        # Same domain
        similarity3 = self.mapper._calculate_domain_similarity(
            "example.com", "example.com"
        )
        self.assertEqual(similarity3, 1.0)
        
        # Empty domains
        similarity4 = self.mapper._calculate_domain_similarity("", "")
        self.assertEqual(similarity4, 0.0)

    def test_extract_domain(self):
        """Test the domain extraction functionality."""
        # Standard URL
        domain1 = self.mapper._extract_domain("https://example.com/page1")
        self.assertEqual(domain1, "example.com")
        
        # URL with subdomain
        domain2 = self.mapper._extract_domain("https://subdomain.example.org/page2")
        self.assertEqual(domain2, "subdomain.example.org")
        
        # URL with port
        domain3 = self.mapper._extract_domain("http://example.com:8080/page3")
        self.assertEqual(domain3, "example.com:8080")
        
        # Invalid URL
        domain4 = self.mapper._extract_domain("not a url")
        self.assertEqual(domain4, "not a url")


class TestRelationshipAnalyzer(unittest.TestCase):
    """Test case for the RelationshipAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = RelationshipAnalyzer()
        
        # Sample URL content for testing
        self.url_content = URLContent(
            url="https://example.com/page1",
            content_type="text/html",
            status_code=200,
            content="<html><body>This is a sample page about technology and programming.</body></html>",
            headers={"Content-Type": "text/html"},
            fetch_time=datetime.now(),
            size_bytes=len("<html><body>This is a sample page about technology and programming.</body></html>")
        )
        
        # Sample URL data for testing
        self.sample_url_data = [
            {
                "url": "https://example.com/page1",
                "content": "This is a sample page about technology and programming.",
                "timestamp": datetime.now() - timedelta(days=5)
            },
            {
                "url": "https://example.com/page2",
                "content": "Another page about science and research projects.",
                "timestamp": datetime.now() - timedelta(days=4)
            }
        ]
        
        # Sample analysis options
        self.options = AnalysisOptions({
            "url_data": self.sample_url_data
        })

    def test_initialization(self):
        """Test that the RelationshipAnalyzer class initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.get_name(), "Relationship Analyzer")
        self.assertIsNotNone(self.analyzer.mapper)

    def test_get_supported_content_types(self):
        """Test the supported content types."""
        content_types = self.analyzer.get_supported_content_types()
        self.assertIsInstance(content_types, set)
        self.assertIn("text/html", content_types)
        self.assertIn("text/plain", content_types)
        self.assertIn("application/json", content_types)

    def test_analyze_content(self):
        """Test the content analysis functionality."""
        try:
            import networkx as nx
            result = self.analyzer.analyze_content(self.url_content, self.options)
            self.assertIsNotNone(result)
            self.assertEqual(result.analyzer_name, "Relationship Analyzer")
            
            # Check that at least some analysis results are present
            self.assertGreaterEqual(len(result.results), 1)
            
        except ImportError:
            self.skipTest("NetworkX not available, skipping relationship analyzer tests")

    def test_analyze_content_without_url_data(self):
        """Test the content analysis functionality without URL data."""
        # Create options without url_data
        options_without_data = AnalysisOptions({})
        
        result = self.analyzer.analyze_content(self.url_content, options_without_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.analyzer_name, "Relationship Analyzer")
        
        # Check that error is present
        self.assertIn("error", result.results)


class TestAnalyzeUrlRelationships(unittest.TestCase):
    """Test case for the analyze_url_relationships function."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample URL data for testing
        self.sample_url_data = [
            {
                "url": "https://example.com/page1",
                "content": "This is a sample page about technology and programming.",
                "timestamp": datetime.now() - timedelta(days=5)
            },
            {
                "url": "https://example.com/page2",
                "content": "Another page about science and research projects.",
                "timestamp": datetime.now() - timedelta(days=4)
            }
        ]

    def test_analyze_url_relationships(self):
        """Test the analyze_url_relationships function."""
        try:
            import networkx as nx
            results = analyze_url_relationships(self.sample_url_data)
            
            # Check that the results contain the expected keys
            self.assertIn("url_relationships", results)
            self.assertIn("domain_relationships", results)
            self.assertIn("communities", results)
            self.assertIn("relationships_found", results)
            
        except ImportError:
            self.skipTest("NetworkX not available, skipping analyze_url_relationships tests")


if __name__ == "__main__":
    unittest.main()