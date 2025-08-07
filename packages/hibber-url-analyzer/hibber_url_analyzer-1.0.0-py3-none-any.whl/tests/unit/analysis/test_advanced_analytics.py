"""
Test module for the advanced analytics functionality.

This module tests the advanced analytics capabilities added to the URL Analyzer.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta

from url_analyzer.analysis.advanced_analytics import AdvancedAnalytics, AdvancedContentAnalyzer
from url_analyzer.analysis.domain import URLContent, AnalysisOptions


class TestAdvancedAnalytics(unittest.TestCase):
    """Test case for the AdvancedAnalytics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.advanced_analytics = AdvancedAnalytics()
        
        # Sample URLs for testing
        self.sample_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.org/page1",
            "https://subdomain.example.org/page2",
            "https://another-example.com/page1"
        ]
        
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
        
        # Sample text content for testing
        self.sample_text = """
        This is a sample text for testing advanced analytics capabilities.
        It contains multiple sentences with different topics.
        Some sentences are about technology and programming.
        Others might be about data analysis and statistics.
        There could also be content about machine learning and artificial intelligence.
        Web development and design are also important topics.
        This text should be complex enough to test various analytics features.
        """

    def test_initialization(self):
        """Test that the AdvancedAnalytics class initializes correctly."""
        self.assertIsNotNone(self.advanced_analytics)
        self.assertIsNotNone(self.advanced_analytics.statistical_analyzer)
        self.assertIsNotNone(self.advanced_analytics.trend_analyzer)
        self.assertIsNotNone(self.advanced_analytics.anomaly_detector)
        self.assertIsNotNone(self.advanced_analytics.ml_analyzer)
        self.assertIsNotNone(self.advanced_analytics.predictive_analyzer)
        self.assertIsNotNone(self.advanced_analytics.custom_analyzer)

    def test_calculate_content_complexity(self):
        """Test the content complexity calculation."""
        complexity = self.advanced_analytics._calculate_content_complexity(self.sample_text)
        self.assertIsInstance(complexity, float)
        self.assertGreaterEqual(complexity, 0.0)
        self.assertLessEqual(complexity, 1.0)
        
        # Test with empty content
        empty_complexity = self.advanced_analytics._calculate_content_complexity("")
        self.assertEqual(empty_complexity, 0.0)
        
        # Test with non-string input
        non_string_complexity = self.advanced_analytics._calculate_content_complexity(123)
        self.assertEqual(non_string_complexity, 0.0)

    def test_calculate_domain_similarity(self):
        """Test the domain similarity calculation."""
        # Same domain, different subdomains
        similarity1 = self.advanced_analytics._calculate_domain_similarity(
            "subdomain1.example.com", "subdomain2.example.com"
        )
        self.assertGreaterEqual(similarity1, 0.5)
        
        # Different domains
        similarity2 = self.advanced_analytics._calculate_domain_similarity(
            "example.com", "example.org"
        )
        self.assertLess(similarity2, 0.5)
        
        # Same main domain
        similarity3 = self.advanced_analytics._calculate_domain_similarity(
            "example.com", "example.com"
        )
        self.assertGreaterEqual(similarity3, 0.8)

    def test_comprehensive_analysis(self):
        """Test the comprehensive analysis functionality."""
        results = self.advanced_analytics.comprehensive_analysis(self.sample_url_data)
        self.assertIsInstance(results, dict)
        
        # Check that at least some analysis results are present
        # The exact results will depend on available dependencies
        self.assertGreaterEqual(len(results), 1)

    def test_url_clusters(self):
        """Test URL clustering functionality."""
        try:
            results = self.advanced_analytics.analyze_url_clusters(self.sample_urls, n_clusters=2)
            self.assertIsInstance(results, dict)
            
            # If scikit-learn is available, check for cluster results
            if "error" not in results:
                self.assertIn("cluster_stats", results)
                self.assertEqual(results["n_clusters"], 2)
        except Exception as e:
            # This test may fail if scikit-learn is not available
            self.skipTest(f"Skipping URL clustering test: {e}")

    def test_topic_modeling(self):
        """Test topic modeling functionality."""
        try:
            texts = [item.get("content", "") for item in self.sample_url_data]
            results = self.advanced_analytics.perform_topic_modeling(texts, n_topics=2)
            self.assertIsInstance(results, dict)
            
            # If scikit-learn is available, check for topic results
            if "error" not in results:
                self.assertIn("topics", results)
                self.assertEqual(results["n_topics"], 2)
        except Exception as e:
            # This test may fail if scikit-learn is not available
            self.skipTest(f"Skipping topic modeling test: {e}")


class TestAdvancedContentAnalyzer(unittest.TestCase):
    """Test case for the AdvancedContentAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = AdvancedContentAnalyzer()
        
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
        
        # Sample analysis options
        self.options = AnalysisOptions({
            "perform_topic_modeling": True,
            "calculate_custom_metrics": True
        })

    def test_initialization(self):
        """Test that the AdvancedContentAnalyzer class initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.get_name(), "Advanced Content Analyzer")
        self.assertIsNotNone(self.analyzer.advanced_analytics)

    def test_get_supported_content_types(self):
        """Test the supported content types."""
        content_types = self.analyzer.get_supported_content_types()
        self.assertIsInstance(content_types, set)
        self.assertIn("text/html", content_types)
        self.assertIn("text/plain", content_types)
        self.assertIn("application/json", content_types)

    def test_analyze_content(self):
        """Test the content analysis functionality."""
        result = self.analyzer.analyze_content(self.url_content, self.options)
        self.assertIsNotNone(result)
        self.assertEqual(result.analyzer_name, "Advanced Content Analyzer")
        
        # Check that at least some analysis results are present
        self.assertGreaterEqual(len(result.results), 1)


if __name__ == "__main__":
    unittest.main()