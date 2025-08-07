"""
Property-based tests for URL Analyzer.

This module contains property-based tests using the Hypothesis library.
These tests verify that the system behaves correctly for a wide range of inputs
by generating random test cases.
"""

import unittest
from hypothesis import given, strategies as st, settings, example
import tempfile
import os
import json
import re
from urllib.parse import urlparse
from datetime import datetime, timedelta

# Import the modules to test
from url_analyzer.analysis.relationship_mapping import RelationshipMapper
from url_analyzer.analysis.topic_modeling import TopicModeler
from url_analyzer.analysis.custom_analytics import CustomAnalyzer
from url_analyzer.analysis.domain import URLContent, AnalysisOptions


class TestURLValidation(unittest.TestCase):
    """Property-based tests for URL validation."""

    @given(url=st.text())
    @settings(max_examples=200)
    def test_url_parsing_never_crashes(self, url):
        """Test that URL parsing never crashes regardless of input."""
        try:
            # This should never raise an exception
            parsed = urlparse(url)
            # We don't assert anything specific, just that it doesn't crash
        except Exception as e:
            self.fail(f"URL parsing crashed with exception: {e}")

    @given(url=st.from_regex(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'))
    @settings(max_examples=100)
    @example("https://example.com")
    @example("http://example.com/path?query=value")
    def test_valid_url_extraction(self, url):
        """Test that domain extraction works correctly for valid URLs."""
        mapper = RelationshipMapper()
        domain = mapper._extract_domain(url)
        
        # Domain should not be empty for valid URLs
        self.assertTrue(domain)
        
        # Domain should be part of the original URL
        self.assertIn(domain, url)


class TestContentSimilarity(unittest.TestCase):
    """Property-based tests for content similarity calculations."""

    @given(
        content1=st.text(min_size=1),
        content2=st.text(min_size=1)
    )
    @settings(max_examples=100)
    def test_similarity_bounds(self, content1, content2):
        """Test that similarity is always between 0 and 1."""
        mapper = RelationshipMapper()
        similarity = mapper._calculate_content_similarity(content1, content2)
        
        # Similarity should be between 0 and 1
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    @given(content=st.text(min_size=1))
    @settings(max_examples=50)
    def test_self_similarity(self, content):
        """Test that content is always 100% similar to itself."""
        mapper = RelationshipMapper()
        similarity = mapper._calculate_content_similarity(content, content)
        
        # Content should be identical to itself
        self.assertEqual(similarity, 1.0)

    @given(
        content1=st.text(min_size=1),
        content2=st.text(min_size=1)
    )
    @settings(max_examples=100)
    def test_similarity_symmetry(self, content1, content2):
        """Test that similarity is symmetric (A to B equals B to A)."""
        mapper = RelationshipMapper()
        similarity1 = mapper._calculate_content_similarity(content1, content2)
        similarity2 = mapper._calculate_content_similarity(content2, content1)
        
        # Similarity should be symmetric
        self.assertAlmostEqual(similarity1, similarity2)


class TestDomainSimilarity(unittest.TestCase):
    """Property-based tests for domain similarity calculations."""

    @given(
        domain1=st.text(min_size=1),
        domain2=st.text(min_size=1)
    )
    @settings(max_examples=100)
    def test_domain_similarity_bounds(self, domain1, domain2):
        """Test that domain similarity is always between 0 and 1."""
        mapper = RelationshipMapper()
        similarity = mapper._calculate_domain_similarity(domain1, domain2)
        
        # Similarity should be between 0 and 1
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    @given(domain=st.from_regex(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'))
    @settings(max_examples=50)
    def test_domain_self_similarity(self, domain):
        """Test that a domain is always 100% similar to itself."""
        mapper = RelationshipMapper()
        similarity = mapper._calculate_domain_similarity(domain, domain)
        
        # Domain should be identical to itself
        self.assertEqual(similarity, 1.0)


class TestLevenshteinDistance(unittest.TestCase):
    """Property-based tests for Levenshtein distance calculation."""

    @given(
        s1=st.text(),
        s2=st.text()
    )
    @settings(max_examples=100)
    def test_levenshtein_properties(self, s1, s2):
        """Test that Levenshtein distance has expected properties."""
        mapper = RelationshipMapper()
        distance = mapper._levenshtein_distance(s1, s2)
        
        # Distance should be non-negative
        self.assertGreaterEqual(distance, 0)
        
        # Distance should be at most the length of the longer string
        self.assertLessEqual(distance, max(len(s1), len(s2)))
        
        # Distance should be zero if and only if strings are identical
        if s1 == s2:
            self.assertEqual(distance, 0)
        else:
            self.assertGreater(distance, 0)

    @given(s=st.text())
    @settings(max_examples=50)
    def test_levenshtein_identity(self, s):
        """Test that Levenshtein distance to self is zero."""
        mapper = RelationshipMapper()
        distance = mapper._levenshtein_distance(s, s)
        
        # Distance to self should be zero
        self.assertEqual(distance, 0)

    @given(
        s1=st.text(),
        s2=st.text()
    )
    @settings(max_examples=100)
    def test_levenshtein_symmetry(self, s1, s2):
        """Test that Levenshtein distance is symmetric."""
        mapper = RelationshipMapper()
        distance1 = mapper._levenshtein_distance(s1, s2)
        distance2 = mapper._levenshtein_distance(s2, s1)
        
        # Distance should be symmetric
        self.assertEqual(distance1, distance2)


class TestURLContent(unittest.TestCase):
    """Property-based tests for URLContent class."""

    @given(
        url=st.from_regex(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'),
        content=st.text(),
        status_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_url_content_creation(self, url, content, status_code):
        """Test that URLContent objects can be created with various inputs."""
        try:
            # Create URLContent object
            url_content = URLContent(
                url=url,
                content_type="text/html",
                status_code=status_code,
                content=content,
                headers={"Content-Type": "text/html"},
                fetch_time=datetime.now(),
                size_bytes=len(content)
            )
            
            # Check that attributes are set correctly
            self.assertEqual(url_content.url, url)
            self.assertEqual(url_content.content, content)
            self.assertEqual(url_content.status_code, status_code)
            self.assertEqual(url_content.size_bytes, len(content))
            
        except Exception as e:
            self.fail(f"URLContent creation crashed with exception: {e}")


class TestAnalysisOptions(unittest.TestCase):
    """Property-based tests for AnalysisOptions class."""

    @given(
        options_dict=st.dictionaries(
            keys=st.text(min_size=1),
            values=st.one_of(
                st.booleans(),
                st.integers(),
                st.text(),
                st.lists(st.text())
            )
        )
    )
    @settings(max_examples=100)
    def test_analysis_options_creation(self, options_dict):
        """Test that AnalysisOptions objects can be created with various inputs."""
        try:
            # Create AnalysisOptions object
            options = AnalysisOptions(options_dict)
            
            # Check that attributes are set correctly
            for key, value in options_dict.items():
                self.assertEqual(getattr(options, key), value)
            
        except Exception as e:
            self.fail(f"AnalysisOptions creation crashed with exception: {e}")


if __name__ == "__main__":
    unittest.main()