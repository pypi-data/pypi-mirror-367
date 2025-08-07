#!/usr/bin/env python3
"""
Test script for the performance monitoring components.

This script tests the performance monitoring utilities and benchmarking framework,
including timing metrics, memory usage tracking, profiling, and benchmarking.
"""

import os
import sys
import unittest
import time
import tempfile
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import performance monitoring utilities
from url_analyzer.utils.performance import (
    timer, timed, track_memory_usage, get_memory_usage,
    reset_metrics, get_metrics, generate_performance_report,
    save_performance_report, increment_counter, set_gauge,
    record_histogram_value, get_histogram_stats,
    enable_monitoring, is_monitoring_enabled
)

# Import benchmarking framework
from url_analyzer.benchmark.benchmark_framework import (
    Benchmark, BenchmarkResult, run_benchmark_module,
    generate_benchmark_report
)

# Import logging
from url_analyzer.utils.logging import get_logger, setup_logging

# Configure logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


class TestPerformanceMonitoring(unittest.TestCase):
    """Test cases for the performance monitoring utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset metrics before each test
        reset_metrics()
        # Ensure monitoring is enabled
        enable_monitoring(True)
    
    def test_timer_context_manager(self):
        """Test the timer context manager."""
        # Use the timer context manager
        with timer("test_operation"):
            # Simulate some work
            time.sleep(0.1)
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the timer was recorded
        self.assertIn("timings", metrics)
        self.assertIn("test_operation", metrics["timings"])
        
        # Check that the timer recorded a reasonable time
        timing = metrics["timings"]["test_operation"]
        self.assertGreaterEqual(timing["total"], 0.1)
        self.assertEqual(timing["count"], 1)
    
    def test_timed_decorator(self):
        """Test the timed decorator."""
        # Define a function with the timed decorator
        @timed
        def test_function():
            time.sleep(0.1)
            return "test"
        
        # Call the function
        result = test_function()
        
        # Check that the function returned the expected result
        self.assertEqual(result, "test")
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the timer was recorded
        self.assertIn("timings", metrics)
        
        # The timer name should be the fully qualified function name
        timer_name = f"{test_function.__module__}.{test_function.__qualname__}"
        self.assertIn(timer_name, metrics["timings"])
        
        # Check that the timer recorded a reasonable time
        timing = metrics["timings"][timer_name]
        self.assertGreaterEqual(timing["total"], 0.1)
        self.assertEqual(timing["count"], 1)
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking."""
        # Track memory usage
        track_memory_usage("test_memory")
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that memory usage was recorded
        self.assertIn("memory", metrics)
        self.assertIn("test_memory", metrics["memory"])
        
        # Check that memory usage has reasonable values
        memory = metrics["memory"]["test_memory"]
        self.assertGreater(memory["rss"], 0)
    
    def test_counters(self):
        """Test counter metrics."""
        # Increment a counter
        increment_counter("test_counter")
        increment_counter("test_counter", 2)
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the counter was recorded
        self.assertIn("counters", metrics)
        self.assertIn("test_counter", metrics["counters"])
        
        # Check that the counter has the expected value
        self.assertEqual(metrics["counters"]["test_counter"], 3)
    
    def test_gauges(self):
        """Test gauge metrics."""
        # Set a gauge
        set_gauge("test_gauge", 42)
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the gauge was recorded
        self.assertIn("gauges", metrics)
        self.assertIn("test_gauge", metrics["gauges"])
        
        # Check that the gauge has the expected value
        self.assertEqual(metrics["gauges"]["test_gauge"], 42)
    
    def test_histograms(self):
        """Test histogram metrics."""
        # Record histogram values
        record_histogram_value("test_histogram", 1)
        record_histogram_value("test_histogram", 2)
        record_histogram_value("test_histogram", 3)
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the histogram was recorded
        self.assertIn("histograms", metrics)
        self.assertIn("test_histogram", metrics["histograms"])
        
        # Check that the histogram has the expected values
        self.assertEqual(metrics["histograms"]["test_histogram"], [1, 2, 3])
        
        # Check histogram stats
        stats = get_histogram_stats("test_histogram")
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min"], 1)
        self.assertEqual(stats["max"], 3)
        self.assertEqual(stats["avg"], 2)
    
    def test_enable_disable_monitoring(self):
        """Test enabling and disabling monitoring."""
        # Disable monitoring
        enable_monitoring(False)
        
        # Check that monitoring is disabled
        self.assertFalse(is_monitoring_enabled())
        
        # Use the timer context manager
        with timer("disabled_timer"):
            time.sleep(0.1)
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the timer was not recorded
        self.assertNotIn("disabled_timer", metrics["timings"])
        
        # Enable monitoring
        enable_monitoring(True)
        
        # Check that monitoring is enabled
        self.assertTrue(is_monitoring_enabled())
        
        # Use the timer context manager
        with timer("enabled_timer"):
            time.sleep(0.1)
        
        # Get the metrics
        metrics = get_metrics()
        
        # Check that the timer was recorded
        self.assertIn("enabled_timer", metrics["timings"])
    
    def test_performance_report(self):
        """Test generating and saving a performance report."""
        # Record some metrics
        with timer("operation1"):
            time.sleep(0.1)
        
        with timer("operation2"):
            time.sleep(0.2)
        
        increment_counter("counter1", 5)
        set_gauge("gauge1", 42)
        
        # Generate a report
        report = generate_performance_report()
        
        # Check that the report contains the expected information
        self.assertIn("Performance Report", report)
        self.assertIn("operation1", report)
        self.assertIn("operation2", report)
        self.assertIn("counter1", report)
        self.assertIn("gauge1", report)
        
        # Save the report to a file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            save_performance_report(temp_filename)
            
            # Check that the file exists and contains the report
            self.assertTrue(os.path.exists(temp_filename))
            
            with open(temp_filename, 'r') as f:
                file_content = f.read()
            
            self.assertEqual(file_content, report)
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestBenchmarkFramework(unittest.TestCase):
    """Test cases for the benchmarking framework."""
    
    def test_benchmark_class(self):
        """Test the Benchmark class."""
        # Create a benchmark
        benchmark = Benchmark("test_benchmark", "Test benchmark description")
        
        # Set benchmark parameters
        benchmark.set_iterations(3)
        benchmark.set_operation_count(100)
        benchmark.set_warmup(1)
        
        # Define benchmark functions
        @benchmark.setup
        def setup():
            return {"data": list(range(100))}
        
        @benchmark.benchmark
        def run_benchmark(data):
            result = 0
            for i in data["data"]:
                result += i
            # Add a small delay to make execution time measurable
            time.sleep(0.001)  # 1ms delay
            return result
        
        @benchmark.teardown
        def teardown(data):
            data.clear()
        
        # Run the benchmark
        result = benchmark.run()
        
        # Check that the benchmark result has the expected properties
        self.assertEqual(result.name, "test_benchmark")
        self.assertEqual(result.description, "Test benchmark description")
        self.assertEqual(result.iterations, 3)
        self.assertEqual(result.operation_count, 100)
        self.assertIsNotNone(result.start_time)
        self.assertIsNotNone(result.end_time)
        self.assertGreater(result.execution_time, 0)
        self.assertIsNone(result.error)
    
    def test_benchmark_result(self):
        """Test the BenchmarkResult class."""
        # Create a benchmark result
        result = BenchmarkResult("test_result", "Test result description")
        
        # Set properties
        result.iterations = 3
        result.operation_count = 100
        result.set_execution_time(0.5)
        
        # Set memory usage
        memory_before = {"rss": 100, "vms": 200}
        memory_after = {"rss": 110, "vms": 220}
        result.set_memory_usage(memory_before, memory_after)
        
        # Complete the benchmark
        result.complete()
        
        # Check properties
        self.assertEqual(result.name, "test_result")
        self.assertEqual(result.description, "Test result description")
        self.assertEqual(result.iterations, 3)
        self.assertEqual(result.operation_count, 100)
        self.assertEqual(result.execution_time, 0.5)
        self.assertEqual(result.memory_before, memory_before)
        self.assertEqual(result.memory_after, memory_after)
        self.assertEqual(result.memory_diff, {"rss": 10, "vms": 20})
        self.assertIsNotNone(result.start_time)
        self.assertIsNotNone(result.end_time)
        
        # Check operations per second
        self.assertEqual(result.get_operations_per_second(), 200)  # 100 operations / 0.5 seconds
        
        # Check summary
        summary = result.get_summary()
        self.assertEqual(summary["name"], "test_result")
        self.assertEqual(summary["description"], "Test result description")
        self.assertEqual(summary["iterations"], 3)
        self.assertEqual(summary["operation_count"], 100)
        self.assertEqual(summary["execution_time"], 0.5)
        self.assertEqual(summary["operations_per_second"], 200)
        
        # Check JSON serialization
        json_str = result.to_json()
        self.assertIn("test_result", json_str)
        self.assertIn("Test result description", json_str)
    
    def test_benchmark_report(self):
        """Test generating a benchmark report."""
        # Create benchmark results
        result1 = BenchmarkResult("benchmark1", "Benchmark 1 description")
        result1.iterations = 3
        result1.operation_count = 100
        result1.set_execution_time(0.5)
        result1.set_memory_usage({"rss": 100}, {"rss": 110})
        result1.complete()
        
        result2 = BenchmarkResult("benchmark2", "Benchmark 2 description")
        result2.iterations = 3
        result2.operation_count = 200
        result2.set_execution_time(0.8)
        result2.set_memory_usage({"rss": 100}, {"rss": 120})
        result2.complete()
        
        # Generate a report
        report = generate_benchmark_report([result1, result2])
        
        # Check that the report contains the expected information
        self.assertIn("Benchmark Report", report)
        self.assertIn("benchmark1", report)
        self.assertIn("benchmark2", report)
        self.assertIn("200.00", report)  # Operations per second for benchmark1
        self.assertIn("250.00", report)  # Operations per second for benchmark2
        
        # Save the report to a file
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            report_path = generate_benchmark_report([result1, result2], temp_filename)
            
            # Check that the file exists and contains the report
            self.assertTrue(os.path.exists(report_path))
            
            with open(report_path, 'r') as f:
                file_content = f.read()
            
            self.assertEqual(file_content, report)
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


if __name__ == "__main__":
    unittest.main()