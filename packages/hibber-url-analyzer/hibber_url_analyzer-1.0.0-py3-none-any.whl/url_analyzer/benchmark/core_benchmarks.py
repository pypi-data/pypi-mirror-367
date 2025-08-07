"""
Core Operations Benchmarks

This module contains benchmarks for core operations in the URL Analyzer,
including URL classification, data processing, and report generation.
"""

import os
import sys
import time
import random
import pandas as pd
from typing import Dict, List, Any, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from url_analyzer.utils.logging import setup_logging, get_logger
from url_analyzer.config.manager import load_config
from url_analyzer.core.classification import classify_url
from url_analyzer.core.strategies import create_classification_strategy
from url_analyzer.data.processing import classify_urls_with_progress
from url_analyzer.reporting.html_report import generate_html_report
from url_analyzer.benchmark.benchmark_framework import Benchmark

# Create logger
logger = get_logger(__name__)

# Load configuration
config = load_config()

# Create benchmarks
url_classification_benchmark = Benchmark(
    name="URL Classification",
    description="Benchmark for URL classification operations"
)

data_processing_benchmark = Benchmark(
    name="Data Processing",
    description="Benchmark for data processing operations"
)

report_generation_benchmark = Benchmark(
    name="Report Generation",
    description="Benchmark for report generation operations"
)


@url_classification_benchmark.setup
def setup_url_classification():
    """
    Setup for URL classification benchmark.
    
    Returns:
        Dictionary with test data
    """
    # Generate test URLs
    protocols = ['http', 'https']
    domains = [
        'example.com', 'test.org', 'sample.net', 'demo.io',
        'facebook.com', 'twitter.com', 'instagram.com',
        'news.google.com', 'mail.yahoo.com', 'github.com',
        'stackoverflow.com', 'reddit.com', 'wikipedia.org',
        'amazon.com', 'ebay.com', 'etsy.com',
        'analytics.google.com', 'ads.doubleclick.net', 'adservice.google.com'
    ]
    paths = [
        '', '/', '/index.html', '/about', '/contact', '/products', '/services',
        '/blog', '/news', '/article/12345', '/post/67890',
        '/user/profile', '/profile/settings', '/account',
        '/search', '/category/electronics', '/tag/popular',
        '/api/v1/data', '/static/images/logo.png', '/assets/css/style.css'
    ]
    query_params = [
        '', '?id=123', '?page=1', '?q=search+term',
        '?utm_source=google&utm_medium=cpc', '?ref=homepage',
        '?session=abc123&user=456', '?filter=popular&sort=date',
        '?lang=en&region=us', '?theme=dark&size=large'
    ]
    
    # Generate URLs
    urls = []
    for _ in range(1000):  # Generate 1000 test URLs
        protocol = random.choice(protocols)
        domain = random.choice(domains)
        path = random.choice(paths)
        query = random.choice(query_params)
        
        url = f"{protocol}://{domain}{path}{query}"
        urls.append(url)
    
    # Create classification strategy
    strategy = create_classification_strategy(config)
    
    return {
        'urls': urls,
        'strategy': strategy
    }


@url_classification_benchmark.benchmark
def benchmark_url_classification(data):
    """
    Benchmark URL classification.
    
    Args:
        data: Dictionary with test data
    """
    urls = data['urls']
    strategy = data['strategy']
    
    for url in urls:
        result = strategy.classify_url(url)


@data_processing_benchmark.setup
def setup_data_processing():
    """
    Setup for data processing benchmark.
    
    Returns:
        Dictionary with test data
    """
    # Generate test data
    num_rows = 1000
    
    # Create a DataFrame with random URLs
    data = {
        'URL': [f"https://example.com/page/{i}" for i in range(num_rows)],
        'Title': [f"Page {i}" for i in range(num_rows)],
        'Visit_Count': [random.randint(1, 100) for _ in range(num_rows)],
        'Last_Visit': [f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" for _ in range(num_rows)]
    }
    
    df = pd.DataFrame(data)
    
    return {
        'dataframe': df,
        'config': config
    }


@data_processing_benchmark.benchmark
def benchmark_data_processing(data):
    """
    Benchmark data processing.
    
    Args:
        data: Dictionary with test data
    """
    df = data['dataframe']
    config_data = data['config']
    
    # Process the DataFrame - classify URLs
    strategy = create_classification_strategy(config_data)
    compiled_patterns = {
        'sensitive': config_data.get('sensitive_patterns', []),
        'ugc': config_data.get('ugc_patterns', []),
        'junk': config_data.get('junk_subcategories', {})
    }
    result_df = classify_urls_with_progress(df, compiled_patterns, "benchmark")


@report_generation_benchmark.setup
def setup_report_generation():
    """
    Setup for report generation benchmark.
    
    Returns:
        Dictionary with test data
    """
    # Generate test data
    num_rows = 500
    
    # Create a DataFrame with processed data
    data = {
        'URL': [f"https://example.com/page/{i}" for i in range(num_rows)],
        'Title': [f"Page {i}" for i in range(num_rows)],
        'Visit_Count': [random.randint(1, 100) for _ in range(num_rows)],
        'Last_Visit': [f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" for _ in range(num_rows)],
        'Category': [random.choice(['Normal', 'Sensitive', 'UGC', 'Junk']) for _ in range(num_rows)],
        'Subcategory': [random.choice(['', 'Advertising', 'Analytics', 'Social']) for _ in range(num_rows)],
        'Is_Sensitive': [random.choice([True, False]) for _ in range(num_rows)],
        'Base_Domain': [f"example{random.randint(1, 10)}.com" for _ in range(num_rows)]
    }
    
    df = pd.DataFrame(data)
    
    # Create a temporary output file
    output_file = os.path.join(os.path.dirname(__file__), 'benchmark_report.html')
    
    return {
        'dataframe': df,
        'output_file': output_file,
        'config': config
    }


@report_generation_benchmark.benchmark
def benchmark_report_generation(data):
    """
    Benchmark report generation.
    
    Args:
        data: Dictionary with test data
    """
    df = data['dataframe']
    output_file = data['output_file']
    config_data = data['config']
    
    # Generate report
    # Create a simple stats dictionary for the benchmark
    stats = {
        'total_urls': len(df),
        'sensitive_urls': df['Is_Sensitive'].sum() if 'Is_Sensitive' in df.columns else 0,
        'categories': {
            'Normal': len(df[df['Category'] == 'Normal']) if 'Category' in df.columns else 0,
            'Sensitive': len(df[df['Category'] == 'Sensitive']) if 'Category' in df.columns else 0,
            'UGC': len(df[df['Category'] == 'UGC']) if 'Category' in df.columns else 0,
            'Junk': len(df[df['Category'] == 'Junk']) if 'Category' in df.columns else 0
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    generate_html_report(df, output_file, stats)


@report_generation_benchmark.teardown
def teardown_report_generation(data):
    """
    Teardown for report generation benchmark.
    
    Args:
        data: Dictionary with test data
    """
    # Remove temporary output file
    output_file = data['output_file']
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            logger.debug(f"Removed temporary file: {output_file}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {output_file}: {e}")


if __name__ == "__main__":
    # Configure logging
    setup_logging(log_level="INFO")
    
    # Configure benchmarks
    url_classification_benchmark.set_iterations(3).set_warmup(1).set_operation_count(1000)
    data_processing_benchmark.set_iterations(3).set_warmup(1).set_operation_count(1000)
    report_generation_benchmark.set_iterations(3).set_warmup(1).set_operation_count(500)
    
    # Run benchmarks
    print("\nRunning URL Classification Benchmark...")
    url_result = url_classification_benchmark.run()
    
    print("\nRunning Data Processing Benchmark...")
    data_result = data_processing_benchmark.run()
    
    print("\nRunning Report Generation Benchmark...")
    report_result = report_generation_benchmark.run()
    
    # Print results
    print("\nBenchmark Results:")
    print(f"URL Classification: {url_result.get_operations_per_second():.2f} ops/sec")
    print(f"Data Processing: {data_result.get_operations_per_second():.2f} ops/sec")
    print(f"Report Generation: {report_result.get_operations_per_second():.2f} ops/sec")