"""
Performance benchmarks for URL Analyzer.

This module contains performance tests that measure and validate the performance
of key components in the URL Analyzer system. These tests help identify performance
bottlenecks and ensure that the system meets performance requirements.
"""

import unittest
import tempfile
import os
import json
import shutil
import time
import statistics
from datetime import datetime, timedelta
from pathlib import Path
import csv
import random
import string
from typing import List, Dict, Any, Tuple

# Import the modules to test
from url_analyzer.analysis import (
    URLContent, 
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


class PerformanceTestBase(unittest.TestCase):
    """Base class for performance tests with common setup and teardown."""
    
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
        
        # Create a temporary performance log file
        self.perf_log_file = os.path.join(self.temp_dir, "performance.csv")
        
        # Sample URL data for testing
        self.sample_url_data = self._generate_sample_url_data(100)
        
        # Performance thresholds
        self.thresholds = {
            "url_processing": 0.5,  # seconds per URL
            "content_analysis": 0.2,  # seconds per content
            "relationship_mapping": 2.0,  # seconds for 100 URLs
            "topic_modeling": 3.0,  # seconds for 100 texts
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def _generate_sample_url_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample URL data for testing."""
        data = []
        domains = ["example.com", "example.org", "test.com", "sample.net", "demo.org"]
        
        for i in range(count):
            domain = random.choice(domains)
            path = ''.join(random.choices(string.ascii_lowercase, k=8))
            content = ' '.join(''.join(random.choices(string.ascii_lowercase, k=5)) for _ in range(50))
            
            data.append({
                "url": f"https://{domain}/{path}",
                "content": content,
                "html": f"<html><body>{content}</body></html>",
                "timestamp": datetime.now() - timedelta(days=random.randint(1, 30)),
                "category": random.choice(["Technology", "Science", "Business", "Health"]),
                "domain": domain
            })
        
        return data
    
    def _log_performance(self, test_name: str, operation: str, duration: float, 
                         item_count: int = 1, success: bool = True) -> None:
        """Log performance metrics to a CSV file."""
        # Create the log file if it doesn't exist
        if not os.path.exists(self.perf_log_file):
            with open(self.perf_log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Test", "Operation", "Duration (s)", 
                    "Item Count", "Per Item (ms)", "Success"
                ])
        
        # Calculate per-item duration in milliseconds
        per_item_ms = (duration / item_count) * 1000 if item_count > 0 else 0
        
        # Append the log entry
        with open(self.perf_log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                test_name,
                operation,
                f"{duration:.6f}",
                item_count,
                f"{per_item_ms:.2f}",
                "Yes" if success else "No"
            ])
    
    def _measure_execution_time(self, func, *args, **kwargs) -> Tuple[float, Any]:
        """Measure the execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        return duration, result


class TestContentAnalysisPerformance(PerformanceTestBase):
    """Performance tests for content analysis."""
    
    def test_html_content_analyzer_performance(self):
        """Test the performance of HTMLContentAnalyzer."""
        analyzer = HTMLContentAnalyzer()
        options = AnalysisOptions({"include_metadata": True})
        
        durations = []
        for i in range(10):  # Run 10 iterations for more stable results
            url_content = URLContent(
                url=f"https://example.com/page{i}",
                content_type="text/html",
                status_code=200,
                content=f"<html><body>Test content {i}</body></html>",
                headers={"Content-Type": "text/html"},
                fetch_time=datetime.now(),
                size_bytes=len(f"<html><body>Test content {i}</body></html>")
            )
            
            duration, result = self._measure_execution_time(
                analyzer.analyze_content, url_content, options
            )
            
            durations.append(duration)
            
            # Log the performance
            self._log_performance(
                "TestContentAnalysisPerformance",
                "html_content_analyzer",
                duration,
                success=(result is not None)
            )
        
        # Calculate statistics
        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print(f"\nHTMLContentAnalyzer Performance:")
        print(f"  Average: {avg_duration:.6f} seconds")
        print(f"  Maximum: {max_duration:.6f} seconds")
        print(f"  Minimum: {min_duration:.6f} seconds")
        
        # Assert that performance meets the threshold
        self.assertLessEqual(
            avg_duration, 
            self.thresholds["content_analysis"],
            f"HTMLContentAnalyzer performance ({avg_duration:.6f}s) exceeds threshold "
            f"({self.thresholds['content_analysis']}s)"
        )


class TestAdvancedAnalyticsPerformance(PerformanceTestBase):
    """Performance tests for advanced analytics."""
    
    def test_topic_modeling_performance(self):
        """Test the performance of topic modeling."""
        try:
            topic_modeler = TopicModeler()
            
            # Extract text content from sample data
            texts = [item.get("content", "") for item in self.sample_url_data]
            
            # Measure the execution time
            duration, result = self._measure_execution_time(
                topic_modeler.perform_topic_modeling, texts, n_topics=5
            )
            
            # Log the performance
            self._log_performance(
                "TestAdvancedAnalyticsPerformance",
                "topic_modeling",
                duration,
                item_count=len(texts),
                success=(result is not None and "error" not in result)
            )
            
            print(f"\nTopic Modeling Performance:")
            print(f"  Duration: {duration:.6f} seconds for {len(texts)} texts")
            print(f"  Per text: {(duration / len(texts) * 1000):.2f} ms")
            
            # Assert that performance meets the threshold
            self.assertLessEqual(
                duration, 
                self.thresholds["topic_modeling"],
                f"Topic modeling performance ({duration:.6f}s) exceeds threshold "
                f"({self.thresholds['topic_modeling']}s)"
            )
            
        except ImportError:
            self.skipTest("Required libraries for topic modeling are not available")
    
    def test_comprehensive_analysis_performance(self):
        """Test the performance of comprehensive analysis."""
        advanced_analytics = AdvancedAnalytics()
        
        # Measure the execution time
        duration, result = self._measure_execution_time(
            advanced_analytics.comprehensive_analysis, self.sample_url_data
        )
        
        # Log the performance
        self._log_performance(
            "TestAdvancedAnalyticsPerformance",
            "comprehensive_analysis",
            duration,
            item_count=len(self.sample_url_data),
            success=(result is not None)
        )
        
        print(f"\nComprehensive Analysis Performance:")
        print(f"  Duration: {duration:.6f} seconds for {len(self.sample_url_data)} URLs")
        print(f"  Per URL: {(duration / len(self.sample_url_data) * 1000):.2f} ms")
        
        # No specific threshold for comprehensive analysis as it depends on available components


class TestRelationshipMappingPerformance(PerformanceTestBase):
    """Performance tests for relationship mapping."""
    
    def test_relationship_mapping_performance(self):
        """Test the performance of relationship mapping."""
        try:
            mapper = RelationshipMapper()
            
            # Measure the execution time
            duration, result = self._measure_execution_time(
                mapper.map_url_relationships, self.sample_url_data
            )
            
            # Log the performance
            self._log_performance(
                "TestRelationshipMappingPerformance",
                "relationship_mapping",
                duration,
                item_count=len(self.sample_url_data),
                success=(result is not None and "error" not in result)
            )
            
            print(f"\nRelationship Mapping Performance:")
            print(f"  Duration: {duration:.6f} seconds for {len(self.sample_url_data)} URLs")
            print(f"  Per URL: {(duration / len(self.sample_url_data) * 1000):.2f} ms")
            
            # Assert that performance meets the threshold
            self.assertLessEqual(
                duration, 
                self.thresholds["relationship_mapping"],
                f"Relationship mapping performance ({duration:.6f}s) exceeds threshold "
                f"({self.thresholds['relationship_mapping']}s)"
            )
            
        except Exception as e:
            if "NetworkX library is required" in str(e):
                self.skipTest("NetworkX library is not available for relationship mapping")
            else:
                raise


class TestScalabilityPerformance(PerformanceTestBase):
    """Performance tests for scalability."""
    
    def test_url_processing_scalability(self):
        """Test the scalability of URL processing."""
        # Create datasets of different sizes
        dataset_sizes = [10, 50, 100]
        
        results = []
        for size in dataset_sizes:
            dataset = self._generate_sample_url_data(size)
            
            # Measure the execution time for processing the dataset
            start_time = time.time()
            
            # Process each URL (simplified simulation)
            for item in dataset:
                # Simulate URL processing
                url = item.get("url", "")
                content = item.get("content", "")
                domain = item.get("domain", "")
                
                # Perform some basic processing
                parsed_url = urlparse(url)
                content_length = len(content)
                domain_parts = domain.split(".")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Log the performance
            self._log_performance(
                "TestScalabilityPerformance",
                f"url_processing_{size}",
                duration,
                item_count=size,
                success=True
            )
            
            results.append((size, duration, duration / size))
        
        # Print the results
        print("\nURL Processing Scalability:")
        for size, duration, per_item in results:
            print(f"  {size} URLs: {duration:.6f} seconds ({per_item * 1000:.2f} ms per URL)")
        
        # Check if processing time scales linearly
        if len(results) >= 2:
            # Calculate the ratio of processing time to dataset size
            ratios = [duration / size for size, duration, _ in results]
            
            # Calculate the variation in ratios
            ratio_variation = max(ratios) / min(ratios) if min(ratios) > 0 else float('inf')
            
            # If the variation is less than 2x, consider it approximately linear
            is_linear = ratio_variation < 2.0
            
            print(f"  Scaling appears to be {'approximately linear' if is_linear else 'non-linear'}")
            print(f"  Ratio variation: {ratio_variation:.2f}x")


class TestMemoryUsagePerformance(PerformanceTestBase):
    """Performance tests for memory usage."""
    
    def test_memory_usage(self):
        """Test the memory usage of key operations."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            
            # Measure baseline memory usage
            baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            print(f"\nMemory Usage:")
            print(f"  Baseline: {baseline_memory:.2f} MB")
            
            # Test memory usage for different operations
            operations = [
                ("create_large_dataset", lambda: self._generate_sample_url_data(1000)),
                ("advanced_analytics", lambda: AdvancedAnalytics().comprehensive_analysis(self.sample_url_data[:20])),
            ]
            
            for name, operation in operations:
                # Measure memory before operation
                before_memory = process.memory_info().rss / (1024 * 1024)  # MB
                
                # Perform the operation
                result = operation()
                
                # Measure memory after operation
                after_memory = process.memory_info().rss / (1024 * 1024)  # MB
                
                # Calculate memory usage
                memory_usage = after_memory - before_memory
                
                print(f"  {name}: {memory_usage:.2f} MB")
                
                # Log the performance
                self._log_performance(
                    "TestMemoryUsagePerformance",
                    name,
                    0.0,  # No duration for memory tests
                    item_count=1,
                    success=True
                )
            
        except ImportError:
            self.skipTest("psutil library is not available for memory usage testing")


if __name__ == "__main__":
    unittest.main()