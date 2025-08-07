"""
Test module for the performance profiling functionality.

This module tests the performance profiling features including:
- Automated performance benchmarks
- Continuous performance monitoring
- Performance regression detection
- Performance reports with actionable insights
- Performance annotations for critical code paths
"""

import os
import sys
import unittest
import tempfile
import json
import time
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import profiling utilities
from url_analyzer.utils.profiling import (
    enable_profiling, is_profiling_enabled, set_history_file,
    load_performance_history, save_performance_history,
    record_benchmark_result, set_baseline, get_baseline,
    set_regression_threshold, detect_regressions,
    mark_critical_path, is_critical_path, profile,
    generate_profiling_report, visualize_profiling_report,
    init_module
)

# Import logging
from url_analyzer.utils.logging import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger(__name__)


class TestPerformanceProfiler(unittest.TestCase):
    """Test case for the performance profiler module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary file for performance history
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_filename = self.temp_file.name
        self.temp_file.close()
        
        # Initialize the profiling module with test settings
        init_module({
            'enabled': True,
            'history_file': self.temp_filename,
            'regression_thresholds': {
                'test_function': {
                    'execution_time': 1.5  # 50% increase threshold
                }
            },
            'critical_paths': ['test_critical_function']
        })
        
        # Enable profiling
        enable_profiling(True)
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary file
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)
    
    def test_enable_disable_profiling(self):
        """Test enabling and disabling profiling."""
        # Test initial state (enabled in setUp)
        self.assertTrue(is_profiling_enabled())
        
        # Test disabling
        enable_profiling(False)
        self.assertFalse(is_profiling_enabled())
        
        # Test re-enabling
        enable_profiling(True)
        self.assertTrue(is_profiling_enabled())
    
    def test_performance_history(self):
        """Test recording and loading performance history."""
        # Record a benchmark result
        metrics = {
            'execution_time': 0.1,
            'memory_usage': 1024
        }
        record_benchmark_result('test_benchmark', metrics)
        
        # Save and reload history
        save_performance_history()
        
        # Create a new module instance with the same history file
        init_module({
            'enabled': True,
            'history_file': self.temp_filename
        })
        
        # Record another result
        metrics2 = {
            'execution_time': 0.2,
            'memory_usage': 2048
        }
        record_benchmark_result('test_benchmark', metrics2)
        
        # Generate a report to check if both entries are there
        report = generate_profiling_report()
        
        # Check that the benchmark is in the report
        self.assertIn('test_benchmark', report['benchmarks'])
        
        # Check that we have at least the expected number of history entries
        self.assertGreaterEqual(report['benchmarks']['test_benchmark']['history_count'], 2)
    
    def test_baseline_and_regression_detection(self):
        """Test setting baselines and detecting regressions."""
        # Set a baseline
        baseline_metrics = {
            'execution_time': 0.1,
            'memory_usage': 1024
        }
        set_baseline('test_function', baseline_metrics)
        
        # Get the baseline
        baseline = get_baseline('test_function')
        self.assertIsNotNone(baseline)
        self.assertEqual(baseline['metrics']['execution_time'], 0.1)
        
        # Test with metrics below threshold (no regression)
        current_metrics = {
            'execution_time': 0.14,  # 40% increase, below 50% threshold
            'memory_usage': 1100
        }
        regressions = detect_regressions('test_function', current_metrics)
        self.assertEqual(len(regressions), 0)
        
        # Test with metrics above threshold (regression detected)
        current_metrics = {
            'execution_time': 0.16,  # 60% increase, above 50% threshold
            'memory_usage': 1100
        }
        regressions = detect_regressions('test_function', current_metrics)
        self.assertEqual(len(regressions), 1)
        self.assertEqual(regressions[0]['metric'], 'execution_time')
        self.assertAlmostEqual(regressions[0]['ratio'], 1.6)
    
    def test_critical_paths(self):
        """Test marking and checking critical paths."""
        # Check path marked in setUp
        self.assertTrue(is_critical_path('test_critical_function'))
        
        # Mark a new critical path
        mark_critical_path('another_critical_function')
        self.assertTrue(is_critical_path('another_critical_function'))
        
        # Check a non-critical path
        self.assertFalse(is_critical_path('non_critical_function'))
    
    @profile(name='test_profile_decorator')
    def test_function_for_profiling(self):
        """Test function that will be profiled."""
        # Simulate some work
        time.sleep(0.1)
        result = 0
        for i in range(1000000):
            result += i
        return result
    
    def test_profile_decorator(self):
        """Test the profile decorator."""
        # Call the profiled function
        self.test_function_for_profiling()
        
        # Generate a report
        report = generate_profiling_report()
        
        # Check that the profiled function is in the report
        self.assertIn('test_profile_decorator', report['benchmarks'])
        
        # Check that execution time was recorded
        self.assertIn('execution_time', report['benchmarks']['test_profile_decorator']['latest']['metrics'])
    
    def test_profiling_report(self):
        """Test generating a profiling report."""
        # Set up some test data
        set_baseline('test_function1', {'execution_time': 0.1})
        record_benchmark_result('test_function1', {'execution_time': 0.12})
        
        mark_critical_path('test_function2')
        set_baseline('test_function2', {'execution_time': 0.2})
        record_benchmark_result('test_function2', {'execution_time': 0.3})
        
        # Generate a report
        report = generate_profiling_report()
        
        # Check report structure
        self.assertIn('timestamp', report)
        self.assertIn('benchmarks', report)
        self.assertIn('critical_paths', report)
        self.assertIn('insights', report)
        self.assertIn('recommendations', report)
        
        # Check benchmarks
        self.assertIn('test_function1', report['benchmarks'])
        self.assertIn('test_function2', report['benchmarks'])
        
        # Check critical paths
        self.assertIn('test_function2', report['critical_paths'])
        
        # Save report to file
        temp_report_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_report_filename = temp_report_file.name
        temp_report_file.close()
        
        try:
            # Generate report to file
            generate_profiling_report(temp_report_filename)
            
            # Check that the file exists and contains valid JSON
            self.assertTrue(os.path.exists(temp_report_filename))
            with open(temp_report_filename, 'r') as f:
                report_data = json.load(f)
                self.assertIn('benchmarks', report_data)
        finally:
            # Clean up
            if os.path.exists(temp_report_filename):
                os.unlink(temp_report_filename)
    
    def test_visualization(self):
        """Test visualization of profiling reports."""
        # Skip if visualization libraries are not available
        try:
            import matplotlib
            import numpy
        except ImportError:
            self.skipTest("Visualization libraries not available")
        
        # Set up some test data
        set_baseline('test_function1', {'execution_time': 0.1})
        record_benchmark_result('test_function1', {'execution_time': 0.12})
        
        set_baseline('test_function2', {'execution_time': 0.2})
        record_benchmark_result('test_function2', {'execution_time': 0.3})
        
        # Generate a report
        report = generate_profiling_report()
        
        # Create a temporary file for the visualization
        temp_viz_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_viz_filename = temp_viz_file.name
        temp_viz_file.close()
        
        try:
            # Generate visualization
            result = visualize_profiling_report(report, temp_viz_filename)
            
            # Check that visualization was created
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_viz_filename))
        finally:
            # Clean up
            if os.path.exists(temp_viz_filename):
                os.unlink(temp_viz_filename)


def test_performance_profiling() -> bool:
    """
    Run the performance profiling tests.
    
    This function is called from the integration test script.
    
    Returns:
        True if all tests pass, False otherwise
    """
    try:
        # Run the tests
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceProfiler)
        result = unittest.TextTestRunner().run(suite)
        
        # Return True if all tests pass
        return result.wasSuccessful()
    except Exception as e:
        logger.error(f"Error running performance profiling tests: {e}")
        return False


if __name__ == '__main__':
    unittest.main()