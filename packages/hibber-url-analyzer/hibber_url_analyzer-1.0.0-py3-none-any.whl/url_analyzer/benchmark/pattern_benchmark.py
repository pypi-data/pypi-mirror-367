"""
Pattern Matching Benchmark Script

This script benchmarks the performance of different pattern matching strategies
for URL classification, comparing the legacy pattern-based approach with the
optimized pattern matcher.
"""

import os
import sys
import time
import argparse
import json
import random
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Visualization features will be disabled.")

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from url_analyzer.utils.logging import setup_logging, get_logger
from url_analyzer.config.manager import load_config
from url_analyzer.core.strategies import (
    PatternBasedStrategy, create_classification_strategy,
    OPTIMIZED_MATCHER_AVAILABLE
)
from url_analyzer.core.classification import compile_patterns

# Import optimized pattern matcher if available
if OPTIMIZED_MATCHER_AVAILABLE:
    from url_analyzer.core.pattern_matcher import (
        OptimizedPatternMatcher, OptimizedPatternStrategy,
        create_optimized_pattern_matcher, benchmark_pattern_matching
    )

# Create logger
logger = get_logger(__name__)


def load_test_urls(file_path: str, column: str = 'URL', limit: Optional[int] = None) -> List[str]:
    """
    Load test URLs from a CSV or Excel file.
    
    Args:
        file_path: Path to the file containing URLs
        column: Column name containing URLs
        limit: Maximum number of URLs to load (if None, load all)
        
    Returns:
        List of URLs
    """
    try:
        # Determine file type
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Check if column exists
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in {file_path}")
        
        # Extract URLs
        urls = df[column].dropna().astype(str).tolist()
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            urls = urls[:limit]
        
        logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        return urls
    except Exception as e:
        logger.error(f"Error loading URLs from {file_path}: {e}")
        return []


def generate_test_urls(count: int = 1000, seed: int = 42) -> List[str]:
    """
    Generate synthetic test URLs.
    
    Args:
        count: Number of URLs to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of generated URLs
    """
    random.seed(seed)
    
    # Define URL components
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
    for _ in range(count):
        protocol = random.choice(protocols)
        domain = random.choice(domains)
        path = random.choice(paths)
        query = random.choice(query_params)
        
        url = f"{protocol}://{domain}{path}{query}"
        urls.append(url)
    
    logger.info(f"Generated {len(urls)} synthetic URLs")
    return urls


def benchmark_strategies(urls: List[str], config: Dict[str, Any], iterations: int = 3) -> Dict[str, Any]:
    """
    Benchmark different classification strategies.
    
    Args:
        urls: List of URLs to classify
        config: Configuration dictionary
        iterations: Number of iterations for each benchmark
        
    Returns:
        Dictionary of benchmark results
    """
    results = {}
    
    # Benchmark legacy pattern-based strategy
    logger.info("Benchmarking legacy pattern-based strategy...")
    
    # Create legacy strategy
    legacy_patterns = {
        'sensitive': re.compile('|'.join(config['sensitive_patterns']), re.IGNORECASE),
        'ugc': re.compile('|'.join(config['ugc_patterns']), re.IGNORECASE),
        'junk': {
            cat: re.compile('|'.join(cat_patterns), re.IGNORECASE)
            for cat, cat_patterns in config['junk_subcategories'].items()
        }
    }
    legacy_strategy = PatternBasedStrategy(legacy_patterns)
    
    # Benchmark legacy strategy
    legacy_start = time.time()
    
    for _ in range(iterations):
        for url in urls:
            legacy_strategy.classify_url(url)
    
    legacy_end = time.time()
    legacy_total = legacy_end - legacy_start
    legacy_avg = legacy_total / (len(urls) * iterations)
    legacy_per_second = (len(urls) * iterations) / legacy_total
    
    results["legacy"] = {
        "total_time": legacy_total,
        "avg_time_per_url": legacy_avg,
        "urls_per_second": legacy_per_second,
        "iterations": iterations,
        "num_urls": len(urls)
    }
    
    logger.info(f"Legacy strategy: {legacy_per_second:.2f} URLs/second")
    
    # Benchmark optimized strategy if available
    if OPTIMIZED_MATCHER_AVAILABLE:
        logger.info("Benchmarking optimized pattern strategy...")
        
        # Create optimized strategy
        optimized_strategy = OptimizedPatternStrategy({
            'sensitive': config['sensitive_patterns'],
            'ugc': config['ugc_patterns'],
            'junk': config['junk_subcategories']
        })
        
        # Benchmark with cache disabled
        logger.info("Benchmarking with cache disabled...")
        optimized_strategy.matcher.use_cache = False
        
        nocache_start = time.time()
        
        for _ in range(iterations):
            for url in urls:
                optimized_strategy.classify_url(url)
        
        nocache_end = time.time()
        nocache_total = nocache_end - nocache_start
        nocache_avg = nocache_total / (len(urls) * iterations)
        nocache_per_second = (len(urls) * iterations) / nocache_total
        
        results["optimized_nocache"] = {
            "total_time": nocache_total,
            "avg_time_per_url": nocache_avg,
            "urls_per_second": nocache_per_second,
            "iterations": iterations,
            "num_urls": len(urls)
        }
        
        logger.info(f"Optimized strategy (no cache): {nocache_per_second:.2f} URLs/second")
        
        # Benchmark with cache enabled
        logger.info("Benchmarking with cache enabled...")
        optimized_strategy.matcher.use_cache = True
        
        # Clear cache before benchmarking
        optimized_strategy.matcher.cache.clear()
        
        # First iteration to warm up cache
        for url in urls:
            optimized_strategy.classify_url(url)
        
        # Benchmark with warm cache
        cache_start = time.time()
        
        for _ in range(iterations):
            for url in urls:
                optimized_strategy.classify_url(url)
        
        cache_end = time.time()
        cache_total = cache_end - cache_start
        cache_avg = cache_total / (len(urls) * iterations)
        cache_per_second = (len(urls) * iterations) / cache_total
        
        # Get cache stats
        cache_stats = optimized_strategy.matcher.cache.get_stats()
        
        results["optimized_cache"] = {
            "total_time": cache_total,
            "avg_time_per_url": cache_avg,
            "urls_per_second": cache_per_second,
            "iterations": iterations,
            "num_urls": len(urls),
            "cache_stats": cache_stats
        }
        
        logger.info(f"Optimized strategy (with cache): {cache_per_second:.2f} URLs/second")
        logger.info(f"Cache hit rate: {cache_stats['hit_rate']:.2%}")
    else:
        logger.warning("Optimized pattern matcher not available, skipping optimized benchmarks")
    
    return results


def generate_report(results: Dict[str, Any], output_file: Optional[str] = None) -> str:
    """
    Generate a benchmark report.
    
    Args:
        results: Benchmark results
        output_file: Path to the output file (if None, returns the report as a string)
        
    Returns:
        Report as a string if output_file is None, otherwise the path to the output file
    """
    # Generate report
    report = []
    report.append("# URL Classification Benchmark Report")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Add summary
    report.append("## Summary")
    
    if "legacy" in results:
        legacy = results["legacy"]
        report.append(f"- Legacy Pattern Strategy: {legacy['urls_per_second']:.2f} URLs/second")
    
    if "optimized_nocache" in results:
        nocache = results["optimized_nocache"]
        report.append(f"- Optimized Strategy (No Cache): {nocache['urls_per_second']:.2f} URLs/second")
    
    if "optimized_cache" in results:
        cache = results["optimized_cache"]
        report.append(f"- Optimized Strategy (With Cache): {cache['urls_per_second']:.2f} URLs/second")
    
    # Calculate speedups
    if "legacy" in results and "optimized_nocache" in results:
        legacy = results["legacy"]
        nocache = results["optimized_nocache"]
        speedup = nocache['urls_per_second'] / legacy['urls_per_second']
        report.append(f"- Speedup (No Cache vs Legacy): {speedup:.2f}x")
    
    if "legacy" in results and "optimized_cache" in results:
        legacy = results["legacy"]
        cache = results["optimized_cache"]
        speedup = cache['urls_per_second'] / legacy['urls_per_second']
        report.append(f"- Speedup (With Cache vs Legacy): {speedup:.2f}x")
    
    # Add detailed results
    report.append("")
    report.append("## Detailed Results")
    
    if "legacy" in results:
        legacy = results["legacy"]
        report.append("")
        report.append("### Legacy Pattern Strategy")
        report.append(f"- Total Time: {legacy['total_time']:.4f} seconds")
        report.append(f"- Average Time per URL: {legacy['avg_time_per_url'] * 1000:.4f} ms")
        report.append(f"- URLs per Second: {legacy['urls_per_second']:.2f}")
        report.append(f"- Iterations: {legacy['iterations']}")
        report.append(f"- Number of URLs: {legacy['num_urls']}")
    
    if "optimized_nocache" in results:
        nocache = results["optimized_nocache"]
        report.append("")
        report.append("### Optimized Strategy (No Cache)")
        report.append(f"- Total Time: {nocache['total_time']:.4f} seconds")
        report.append(f"- Average Time per URL: {nocache['avg_time_per_url'] * 1000:.4f} ms")
        report.append(f"- URLs per Second: {nocache['urls_per_second']:.2f}")
        report.append(f"- Iterations: {nocache['iterations']}")
        report.append(f"- Number of URLs: {nocache['num_urls']}")
    
    if "optimized_cache" in results:
        cache = results["optimized_cache"]
        report.append("")
        report.append("### Optimized Strategy (With Cache)")
        report.append(f"- Total Time: {cache['total_time']:.4f} seconds")
        report.append(f"- Average Time per URL: {cache['avg_time_per_url'] * 1000:.4f} ms")
        report.append(f"- URLs per Second: {cache['urls_per_second']:.2f}")
        report.append(f"- Iterations: {cache['iterations']}")
        report.append(f"- Number of URLs: {cache['num_urls']}")
        
        if "cache_stats" in cache:
            stats = cache["cache_stats"]
            report.append("")
            report.append("#### Cache Statistics")
            report.append(f"- Pattern Cache Size: {stats['pattern_cache_size']}")
            report.append(f"- Result Cache Size: {stats['result_cache_size']}")
            report.append(f"- Cache Hits: {stats['hits']}")
            report.append(f"- Cache Misses: {stats['misses']}")
            report.append(f"- Cache Hit Rate: {stats['hit_rate']:.2%}")
    
    report_text = "\n".join(report)
    
    if output_file:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"Benchmark report saved to: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error writing report to file: {e}")
            return report_text
    else:
        return report_text


def generate_visualization(results: Dict[str, Any], output_file: Optional[str] = None):
    """
    Generate visualizations of benchmark results.
    
    Args:
        results: Benchmark results
        output_file: Path to the output file (if None, displays the visualizations)
        
    Returns:
        Path to the output file if output_file is not None
    """
    # Check if matplotlib is available
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib is not available. Visualization skipped.")
        print("Visualization skipped: matplotlib is not available.")
        return None
    
    try:
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Extract data
        labels = []
        values = []
        
        if "legacy" in results:
            labels.append("Legacy")
            values.append(results["legacy"]["urls_per_second"])
        
        if "optimized_nocache" in results:
            labels.append("Optimized\n(No Cache)")
            values.append(results["optimized_nocache"]["urls_per_second"])
        
        if "optimized_cache" in results:
            labels.append("Optimized\n(With Cache)")
            values.append(results["optimized_cache"]["urls_per_second"])
        
        # Create bar chart
        plt.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        
        # Add labels and title
        plt.ylabel('URLs per Second')
        plt.title('URL Classification Performance Comparison')
        
        # Add values on top of bars
        for i, v in enumerate(values):
            plt.text(i, v + 0.1, f"{v:.2f}", ha='center')
        
        # Add grid
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Tight layout
        plt.tight_layout()
        
        # Save or display
        if output_file:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            plt.savefig(output_file)
            plt.close()
            
            logger.info(f"Benchmark visualization saved to: {output_file}")
            return output_file
        else:
            plt.show()
            return None
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        return None


def main():
    """Main entry point for the benchmark script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Benchmark URL classification strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--file', help="Path to a file containing URLs to benchmark")
    parser.add_argument('--column', default='URL', help="Column name containing URLs (default: URL)")
    parser.add_argument('--limit', type=int, help="Maximum number of URLs to load from file")
    parser.add_argument('--generate', type=int, default=1000, 
                      help="Number of synthetic URLs to generate if no file is provided (default: 1000)")
    parser.add_argument('--iterations', type=int, default=3,
                      help="Number of iterations for each benchmark (default: 3)")
    parser.add_argument('--report', help="Path to save the benchmark report")
    parser.add_argument('--visualization', help="Path to save the benchmark visualization")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level=log_level)
    
    # Load configuration
    config = load_config()
    
    # Load or generate URLs
    if args.file:
        urls = load_test_urls(args.file, args.column, args.limit)
        if not urls:
            logger.error(f"No URLs loaded from {args.file}")
            return 1
    else:
        urls = generate_test_urls(args.generate)
    
    # Run benchmarks
    results = benchmark_strategies(urls, config, args.iterations)
    
    # Generate report
    if args.report:
        report_path = generate_report(results, args.report)
        print(f"\nBenchmark report saved to: {report_path}")
    else:
        report = generate_report(results)
        print("\n" + report)
    
    # Generate visualization
    if args.visualization:
        viz_path = generate_visualization(results, args.visualization)
        if viz_path:
            print(f"Benchmark visualization saved to: {viz_path}")
    
    return 0


if __name__ == "__main__":
    import re  # Import here to avoid circular import
    sys.exit(main())