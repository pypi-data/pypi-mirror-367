"""
Continuous performance monitoring script for URL Analyzer.

This script demonstrates how to set up continuous performance monitoring for critical
code paths in the URL Analyzer application. It can be run as a standalone script or
integrated into a CI/CD pipeline to detect performance regressions.

Usage:
    python -m url_analyzer.benchmark.continuous_monitoring [--report-file REPORT_FILE] [--visualize]
"""

import os
import sys
import argparse
import json
import datetime
import time
from typing import Dict, Any, List, Optional
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import from url_analyzer
from url_analyzer.utils.logging import setup_logging, get_logger
from url_analyzer.utils.profiling import (
    enable_profiling, set_history_file, load_performance_history,
    set_baseline, mark_critical_path, profile,
    generate_profiling_report, visualize_profiling_report,
    init_module
)

# Mock functions for demonstration purposes
# In a real implementation, these would be imported from the actual modules
def classify_url(url: str) -> str:
    """Mock function for URL classification."""
    if "facebook" in url or "twitter" in url:
        return "Social"
    elif "google" in url:
        if "analytics" in url:
            return "Analytics"
        elif "ads" in url:
            return "Advertising"
        else:
            return "Search"
    elif "github" in url or "linkedin" in url:
        return "Professional"
    else:
        return "Other"

def analyze_url(url: str) -> dict:
    """Mock function for URL analysis."""
    category = classify_url(url)
    return {
        "url": url,
        "category": category,
        "timestamp": datetime.datetime.now().isoformat()
    }

def process_file(file_path: str) -> dict:
    """Mock function for file processing."""
    # Simulate processing delay
    time.sleep(0.2)
    return {
        "file_path": file_path,
        "processed_urls": 10,
        "categories": {
            "Social": 2,
            "Search": 1,
            "Analytics": 1,
            "Advertising": 1,
            "Professional": 2,
            "Other": 3
        }
    }

def generate_report(data: dict, output_file: Optional[str] = None) -> str:
    """Mock function for report generation."""
    # Simulate report generation delay
    time.sleep(0.3)
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "data": data,
        "summary": {
            "total_urls": data.get("total_urls", 0),
            "categories": data.get("categories", {})
        }
    }
    
    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
    
    return "Report generated successfully"

# Create logger
logger = get_logger(__name__)


def setup_profiling(history_file: str) -> None:
    """
    Set up performance profiling with the specified history file.
    
    Args:
        history_file: Path to the history file
    """
    # Initialize the profiling module
    init_module({
        'enabled': True,
        'history_file': history_file,
        'regression_thresholds': {
            'classify_url': {'execution_time': 1.2},  # 20% increase threshold
            'analyze_url': {'execution_time': 1.2},
            'process_file': {'execution_time': 1.3},  # 30% increase threshold
            'generate_report': {'execution_time': 1.2}
        },
        'critical_paths': [
            'classify_url',
            'analyze_url',
            'process_file',
            'generate_report'
        ]
    })
    
    # Enable profiling
    enable_profiling(True)
    
    logger.info("Performance profiling set up with history file: %s", history_file)


@profile(name='classify_url')
def profile_classify_url() -> None:
    """Profile the URL classification function with sample data."""
    # Sample URLs to classify
    urls = [
        "https://www.example.com",
        "https://www.google.com",
        "https://www.facebook.com",
        "https://www.twitter.com",
        "https://analytics.google.com",
        "https://ads.google.com",
        "https://user.github.com/profile",
        "https://www.linkedin.com/in/username",
        "https://www.example.com/products?id=123",
        "https://www.example.org/blog/article/123"
    ]
    
    # Classify each URL
    for url in urls:
        classify_url(url)
    
    logger.info("Profiled URL classification with %d sample URLs", len(urls))


@profile(name='analyze_url')
def profile_analyze_url() -> None:
    """Profile the URL analysis function with sample data."""
    # Sample URLs to analyze
    urls = [
        "https://www.example.com",
        "https://www.google.com",
        "https://www.facebook.com",
        "https://www.twitter.com",
        "https://analytics.google.com"
    ]
    
    # Analyze each URL
    for url in urls:
        try:
            analyze_url(url)
        except Exception as e:
            logger.warning("Error analyzing URL %s: %s", url, e)
    
    logger.info("Profiled URL analysis with %d sample URLs", len(urls))


@profile(name='process_file')
def profile_process_file() -> None:
    """Profile the file processing function with sample data."""
    # Create a sample file path
    sample_file = os.path.join(os.path.dirname(__file__), '..', '..', 'test_urls.csv')
    
    # Check if the file exists
    if not os.path.exists(sample_file):
        logger.warning("Sample file not found: %s", sample_file)
        return
    
    # Process the file
    try:
        process_file(sample_file)
        logger.info("Profiled file processing with sample file: %s", sample_file)
    except Exception as e:
        logger.error("Error processing file: %s", e)


@profile(name='generate_report')
def profile_generate_report() -> None:
    """Profile the report generation function with sample data."""
    # Create sample data for report generation
    sample_data = {
        'urls': [
            {'url': 'https://www.example.com', 'category': 'Business'},
            {'url': 'https://www.google.com', 'category': 'Search'},
            {'url': 'https://www.facebook.com', 'category': 'Social'},
            {'url': 'https://www.twitter.com', 'category': 'Social'},
            {'url': 'https://analytics.google.com', 'category': 'Analytics'}
        ],
        'categories': {
            'Business': 1,
            'Search': 1,
            'Social': 2,
            'Analytics': 1
        },
        'total_urls': 5
    }
    
    # Generate a report
    try:
        generate_report(sample_data, None)
        logger.info("Profiled report generation with sample data")
    except Exception as e:
        logger.error("Error generating report: %s", e)


def run_performance_benchmarks() -> None:
    """Run all performance benchmarks."""
    logger.info("Running performance benchmarks...")
    
    # Run each benchmark
    profile_classify_url()
    profile_analyze_url()
    profile_process_file()
    profile_generate_report()
    
    logger.info("Performance benchmarks completed")


def main() -> None:
    """Main entry point for the continuous monitoring script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Continuous performance monitoring for URL Analyzer')
    parser.add_argument('--report-file', type=str, help='Path to save the performance report')
    parser.add_argument('--history-file', type=str, default='performance_history.json',
                        help='Path to the performance history file')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization of the report')
    parser.add_argument('--set-baseline', action='store_true', help='Set current results as baseline')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Set up profiling
    setup_profiling(args.history_file)
    
    # Run benchmarks
    run_performance_benchmarks()
    
    # Generate report
    if args.report_file:
        report_file = args.report_file
    else:
        # Create a timestamped report file
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'performance_report_{timestamp}.json'
    
    # Generate the report
    report = generate_profiling_report(report_file)
    logger.info("Generated performance report: %s", report_file)
    
    # Check for regressions
    if report['regressions']:
        logger.warning("Performance regressions detected:")
        for regression in report['regressions']:
            logger.warning("  %s.%s: %.2f%% increase (threshold: %.2f%%)",
                          regression['name'], regression['metric'],
                          (regression['ratio'] - 1) * 100,
                          (regression['threshold'] - 1) * 100)
    else:
        logger.info("No performance regressions detected")
    
    # Generate visualization if requested
    if args.visualize:
        viz_file = report_file.replace('.json', '.png')
        if visualize_profiling_report(report, viz_file):
            logger.info("Generated visualization: %s", viz_file)
    
    # Set baseline if requested
    if args.set_baseline:
        logger.info("Setting current results as baseline")
        for name, data in report['benchmarks'].items():
            if 'latest' in data and 'metrics' in data['latest']:
                set_baseline(name, data['latest']['metrics'])
        logger.info("Baseline updated for %d benchmarks", len(report['benchmarks']))


if __name__ == '__main__':
    main()