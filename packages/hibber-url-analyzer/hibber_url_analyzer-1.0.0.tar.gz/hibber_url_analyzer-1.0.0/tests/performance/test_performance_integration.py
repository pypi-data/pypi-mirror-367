#!/usr/bin/env python3
"""
Integration test for performance monitoring and benchmarking.

This script tests the performance monitoring and benchmarking functionality
in an end-to-end workflow, including command-line interface integration.
"""

import os
import sys
import tempfile
import subprocess
import json
from typing import Dict, Any, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import logging
from url_analyzer.utils.logging import setup_logging, get_logger

# Configure logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


def create_test_csv() -> str:
    """
    Create a test CSV file with URL data.
    
    Returns:
        Path to the created CSV file
    """
    import pandas as pd
    
    # Create a temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_filename = temp_file.name
    
    # Create test data
    data = {
        'Domain_name': [
            'https://www.google.com',
            'https://www.facebook.com',
            'https://www.example.com/about',
            'https://analytics.google.com',
            'https://ads.doubleclick.net',
            'https://www.example.com/user/123',
            'https://api.example.com',
            'https://cdn.example.com',
            'https://www.example.org',
            'https://www.example.net'
        ],
        'Access_time': [
            '2025-08-01 10:00:00',
            '2025-08-01 11:30:00',
            '2025-08-01 12:45:00',
            '2025-08-01 14:15:00',
            '2025-08-01 16:00:00',
            '2025-08-02 09:30:00',
            '2025-08-02 11:00:00',
            '2025-08-02 13:30:00',
            '2025-08-02 15:45:00',
            '2025-08-02 17:15:00'
        ]
    }
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(temp_filename, index=False)
    temp_file.close()
    
    logger.info(f"Created test CSV file: {temp_filename}")
    return temp_filename


def run_command(command: str) -> Tuple[int, str, str]:
    """
    Run a command and return the exit code, stdout, and stderr.
    
    Args:
        command: Command to run
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    logger.info(f"Running command: {command}")
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    exit_code = process.returncode
    
    logger.info(f"Command exited with code {exit_code}")
    
    return exit_code, stdout, stderr


def test_benchmark_command() -> bool:
    """
    Test the benchmark command.
    
    Returns:
        True if the test passed, False otherwise
    """
    logger.info("Testing benchmark command...")
    
    # Run the benchmark command
    command = "python -m url_analyzer.benchmark.pattern_benchmark --generate 100 --iterations 2 --verbose"
    exit_code, stdout, stderr = run_command(command)
    
    # Check if the command succeeded
    if exit_code != 0:
        logger.error(f"Benchmark command failed with exit code {exit_code}")
        logger.error(f"Stderr: {stderr}")
        return False
    
    # Check if the output contains expected information
    expected_outputs = [
        "Benchmarking legacy pattern-based strategy",
        "Benchmarking optimized pattern strategy",
        "URLs per second",
        "Benchmark report"
    ]
    
    for expected in expected_outputs:
        if expected not in stdout:
            logger.error(f"Expected output '{expected}' not found in stdout")
            return False
    
    logger.info("Benchmark command test passed")
    return True


def test_performance_monitoring() -> bool:
    """
    Test performance monitoring in an end-to-end workflow.
    
    Returns:
        True if the test passed, False otherwise
    """
    logger.info("Testing performance monitoring in end-to-end workflow...")
    
    # Create a test CSV file
    test_file = create_test_csv()
    
    try:
        # Create a temporary directory for output files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create paths for output files
            html_report = os.path.join(temp_dir, "report.html")
            perf_report = os.path.join(temp_dir, "performance.txt")
            
            # Run the URL analyzer with performance monitoring
            command = (
                f"python -m url_analyzer analyze --path \"{test_file}\" "
                f"--output \"{html_report}\" --performance-report \"{perf_report}\" "
                f"--live-scan --verbose"
            )
            
            exit_code, stdout, stderr = run_command(command)
            
            # Check if the command succeeded
            if exit_code != 0:
                logger.error(f"URL analyzer command failed with exit code {exit_code}")
                logger.error(f"Stderr: {stderr}")
                return False
            
            # Check if the output files exist
            if not os.path.exists(html_report):
                logger.error(f"HTML report file not found: {html_report}")
                return False
            
            if not os.path.exists(perf_report):
                logger.error(f"Performance report file not found: {perf_report}")
                return False
            
            # Check the content of the performance report
            with open(perf_report, 'r') as f:
                perf_content = f.read()
            
            expected_sections = [
                "Performance Report",
                "Timings:",
                "Memory Usage:",
                "Counters:"
            ]
            
            for section in expected_sections:
                if section not in perf_content:
                    logger.error(f"Expected section '{section}' not found in performance report")
                    return False
            
            logger.info("Performance monitoring test passed")
            return True
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
            logger.info(f"Deleted test file: {test_file}")


def test_custom_benchmark() -> bool:
    """
    Test running a custom benchmark.
    
    Returns:
        True if the test passed, False otherwise
    """
    logger.info("Testing custom benchmark...")
    
    # Create a temporary directory for output files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create paths for output files
        report_path = os.path.join(temp_dir, "benchmark_report.md")
        viz_path = os.path.join(temp_dir, "benchmark_viz.png")
        
        # Run the custom benchmark
        command = (
            f"python -m url_analyzer.benchmark.benchmark_framework "
            f"url_analyzer.benchmark.core_benchmarks "
            f"--iterations 2 --warmup 1 --profile "
            f"--report \"{report_path}\" "
            f"--visualization \"{viz_path}\" "
            f"--verbose"
        )
        
        exit_code, stdout, stderr = run_command(command)
        
        # Check if the command succeeded
        if exit_code != 0:
            logger.error(f"Custom benchmark command failed with exit code {exit_code}")
            logger.error(f"Stderr: {stderr}")
            return False
        
        # Check if the output files exist
        if not os.path.exists(report_path):
            logger.error(f"Benchmark report file not found: {report_path}")
            return False
        
        # Check the content of the benchmark report
        with open(report_path, 'r') as f:
            report_content = f.read()
        
        expected_sections = [
            "Benchmark Report",
            "Summary",
            "URL Classification",
            "Data Processing",
            "Report Generation",
            "Memory Usage"
        ]
        
        for section in expected_sections:
            if section not in report_content:
                logger.error(f"Expected section '{section}' not found in benchmark report")
                return False
        
        logger.info("Custom benchmark test passed")
        return True


def main() -> int:
    """
    Run all integration tests.
    
    Returns:
        0 if all tests passed, 1 otherwise
    """
    logger.info("Starting performance monitoring integration tests...")
    
    # Run tests
    benchmark_passed = test_benchmark_command()
    monitoring_passed = test_performance_monitoring()
    custom_passed = test_custom_benchmark()
    
    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"Benchmark Command Test: {'PASSED' if benchmark_passed else 'FAILED'}")
    logger.info(f"Performance Monitoring Test: {'PASSED' if monitoring_passed else 'FAILED'}")
    logger.info(f"Custom Benchmark Test: {'PASSED' if custom_passed else 'FAILED'}")
    
    # Check if all tests passed
    all_passed = benchmark_passed and monitoring_passed and custom_passed
    
    if all_passed:
        logger.info("\n✅ All performance monitoring integration tests passed!")
        return 0
    else:
        logger.error("\n❌ Some performance monitoring integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())