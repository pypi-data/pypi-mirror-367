#!/usr/bin/env python3
"""
Memory Usage Profiling Script

This script profiles the current memory usage of the URL Analyzer application
to identify potential memory leaks, excessive usage patterns, and optimization opportunities.
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from url_analyzer.utils.memory_profiler import MemoryProfiler, ProfileMemoryBlock
from url_analyzer.utils.memory_management import get_memory_profiler
from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


def profile_url_analysis_memory():
    """Profile memory usage during URL analysis operations."""
    logger.info("Starting URL analysis memory profiling...")
    
    # Create a memory profiler instance
    profiler = MemoryProfiler(
        enabled=True,
        sampling_interval=0.5,
        track_allocations=True,
        memory_limit_mb=500,  # 500MB limit for testing
        log_level="INFO"
    )
    
    # Start memory sampling
    profiler.start_sampling()
    
    try:
        # Test data for profiling
        test_urls = [
            "https://example.com",
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://python.org"
        ] * 10  # 50 URLs total
        
        # Profile URL fetching
        with ProfileMemoryBlock("URL Fetching"):
            from url_analyzer.analysis.services import RequestsURLFetcher
            from url_analyzer.analysis.domain import AnalysisOptions
            
            fetcher = RequestsURLFetcher()
            options = AnalysisOptions(timeout=5, max_retries=1)
            
            # Take initial snapshot
            profiler.take_snapshot("Before URL fetching")
            
            # Fetch URLs (this will use ThreadPoolExecutor)
            results = fetcher.fetch_urls(test_urls, options)
            
            # Take snapshot after fetching
            profiler.take_snapshot("After URL fetching")
        
        # Profile content analysis
        with ProfileMemoryBlock("Content Analysis"):
            from url_analyzer.analysis.services import HTMLContentAnalyzer
            
            analyzer = HTMLContentAnalyzer()
            
            # Take snapshot before analysis
            profiler.take_snapshot("Before content analysis")
            
            # Analyze successful results
            for url, result in results.items():
                if result.success and result.content:
                    try:
                        summary = analyzer.analyze_content(result.content, options)
                    except Exception as e:
                        logger.warning(f"Analysis failed for {url}: {e}")
            
            # Take snapshot after analysis
            profiler.take_snapshot("After content analysis")
        
        # Profile classification
        with ProfileMemoryBlock("URL Classification"):
            from url_analyzer.classification.services import PatternURLClassifier
            
            classifier = PatternURLClassifier()
            
            # Take snapshot before classification
            profiler.take_snapshot("Before classification")
            
            # Classify URLs
            for url in test_urls:
                try:
                    classification = classifier.classify_url(url)
                except Exception as e:
                    logger.warning(f"Classification failed for {url}: {e}")
            
            # Take snapshot after classification
            profiler.take_snapshot("After classification")
        
        # Wait a bit to capture any delayed memory operations
        time.sleep(2)
        
        # Take final snapshot
        profiler.take_snapshot("Final state")
        
        # Compare snapshots to identify memory growth
        logger.info("Analyzing memory usage patterns...")
        
        # Compare initial vs final state
        profiler.compare_snapshots(0, -1, top_n=15)
        
        # Detect potential memory leaks
        leaks = profiler.detect_leaks()
        if leaks:
            logger.warning(f"Potential memory leaks detected: {len(leaks)} objects")
            for obj_type, count, size in leaks[:10]:
                logger.warning(f"  {obj_type}: {count} objects, ~{size} bytes")
        
        # Generate comprehensive memory report
        report = profiler.get_memory_report()
        logger.info("Memory profiling report:")
        logger.info(report)
        
    except Exception as e:
        logger.error(f"Memory profiling failed: {e}")
        raise
    finally:
        # Stop memory sampling
        profiler.stop_sampling()
    
    logger.info("Memory profiling completed")


def profile_concurrent_processing():
    """Profile memory usage of concurrent processing patterns."""
    logger.info("Profiling concurrent processing memory usage...")
    
    profiler = get_memory_profiler()
    
    with ProfileMemoryBlock("Concurrent Processing"):
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        # Test different ThreadPoolExecutor configurations
        test_data = list(range(100))
        
        def cpu_intensive_task(n):
            """Simulate CPU-intensive work."""
            result = 0
            for i in range(n * 1000):
                result += i ** 2
            return result
        
        # Test with current pattern (hardcoded max_workers=20)
        profiler.take_snapshot("Before ThreadPool (max_workers=20)")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(cpu_intensive_task, n) for n in test_data]
            results = [future.result() for future in futures]
        
        profiler.take_snapshot("After ThreadPool (max_workers=20)")
        
        # Test with optimized pattern (dynamic max_workers)
        import os
        optimal_workers = min(32, (os.cpu_count() or 1) + 4)
        
        profiler.take_snapshot(f"Before ThreadPool (max_workers={optimal_workers})")
        
        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            futures = [executor.submit(cpu_intensive_task, n) for n in test_data]
            results = [future.result() for future in futures]
        
        profiler.take_snapshot(f"After ThreadPool (max_workers={optimal_workers})")
        
        # Compare the two approaches
        profiler.compare_snapshots(-4, -2, top_n=10)  # Compare hardcoded approach
        profiler.compare_snapshots(-2, -1, top_n=10)  # Compare optimized approach


def profile_caching_performance():
    """Profile memory usage of caching mechanisms."""
    logger.info("Profiling caching memory usage...")
    
    profiler = get_memory_profiler()
    
    with ProfileMemoryBlock("Cache Performance"):
        from url_analyzer.utils.cache import Cache
        
        # Create cache instance
        cache = Cache(max_size=1000, ttl=300)
        
        profiler.take_snapshot("Before cache operations")
        
        # Fill cache with test data
        for i in range(500):
            cache.set(f"key_{i}", f"value_{i}" * 100)  # ~600 bytes per entry
        
        profiler.take_snapshot("After filling cache")
        
        # Access cached data
        for i in range(250):
            value = cache.get(f"key_{i}")
        
        profiler.take_snapshot("After cache access")
        
        # Test cache eviction
        for i in range(500, 1500):  # Add 1000 more entries to trigger eviction
            cache.set(f"key_{i}", f"value_{i}" * 100)
        
        profiler.take_snapshot("After cache eviction")
        
        # Compare cache memory usage
        profiler.compare_snapshots(-4, -1, top_n=10)


def main():
    """Main function to run memory profiling."""
    parser = argparse.ArgumentParser(description="Profile URL Analyzer memory usage")
    parser.add_argument(
        "--component",
        choices=["all", "analysis", "concurrent", "cache"],
        default="all",
        help="Component to profile (default: all)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for profiling results"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting memory usage profiling...")
    
    try:
        if args.component in ["all", "analysis"]:
            profile_url_analysis_memory()
        
        if args.component in ["all", "concurrent"]:
            profile_concurrent_processing()
        
        if args.component in ["all", "cache"]:
            profile_caching_performance()
        
        logger.info("Memory profiling completed successfully")
        
    except Exception as e:
        logger.error(f"Memory profiling failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()