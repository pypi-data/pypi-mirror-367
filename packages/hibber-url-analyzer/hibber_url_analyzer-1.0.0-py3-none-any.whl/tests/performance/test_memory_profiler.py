"""
Memory Profiler Test Script

This script demonstrates the use of the memory profiler to identify memory leaks
and optimize memory usage in the URL Analyzer application.
"""

import os
import time
import argparse
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# Import memory profiler
from url_analyzer.utils.memory_profiler import (
    profile_memory, start_memory_tracking, stop_memory_tracking,
    take_memory_snapshot, generate_memory_report, detect_memory_leaks
)

# Import logging
from url_analyzer.shared.logging import get_logger, configure_logging

# Configure logging
configure_logging(level="INFO")
logger = get_logger(__name__)


def create_large_dataframe(rows: int = 100000, cols: int = 10) -> pd.DataFrame:
    """
    Create a large DataFrame for testing memory usage.
    
    Args:
        rows: Number of rows
        cols: Number of columns
        
    Returns:
        Large DataFrame
    """
    logger.info(f"Creating DataFrame with {rows} rows and {cols} columns")
    
    # Create random data
    data = {}
    for i in range(cols):
        col_name = f"col_{i}"
        data[col_name] = np.random.rand(rows)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add a URL column
    df["Domain_name"] = [f"https://example{i}.com/path/to/page?query=value" for i in range(rows)]
    
    return df


@profile_memory("process_dataframe")
def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process a DataFrame with memory profiling.
    
    Args:
        df: DataFrame to process
        
    Returns:
        Processed DataFrame
    """
    logger.info(f"Processing DataFrame with {len(df)} rows")
    
    # Perform some operations
    result = df.copy()
    
    # Add some columns
    result["url_length"] = result["Domain_name"].str.len()
    result["has_query"] = result["Domain_name"].str.contains(r"\?")
    result["domain"] = result["Domain_name"].str.extract(r"https?://([^/]+)")
    
    # Do some grouping operations
    domain_counts = result.groupby("domain").size().reset_index(name="count")
    result = result.merge(domain_counts, on="domain", how="left")
    
    # Sort by count
    result = result.sort_values("count", ascending=False)
    
    return result


def simulate_memory_leak(iterations: int = 10, leak_size_mb: float = 10.0) -> None:
    """
    Simulate a memory leak for testing the profiler.
    
    Args:
        iterations: Number of iterations
        leak_size_mb: Size of the leak in MB per iteration
    """
    logger.info(f"Simulating memory leak: {iterations} iterations, {leak_size_mb} MB per iteration")
    
    # Start memory tracking
    start_memory_tracking(interval=1.0)
    
    # Take initial snapshot
    take_memory_snapshot("leak-start")
    
    # Store references to prevent garbage collection
    stored_data = []
    
    try:
        # Simulate a memory leak by storing large objects
        for i in range(iterations):
            # Calculate number of elements needed for the specified leak size
            # Each float64 is 8 bytes, so we need leak_size_mb * 1024 * 1024 / 8 elements
            elements = int(leak_size_mb * 1024 * 1024 / 8)
            
            # Create a large array and store it
            data = np.random.rand(elements)
            stored_data.append(data)
            
            # Take a snapshot after each iteration
            take_memory_snapshot(f"leak-iter-{i+1}")
            
            # Log progress
            logger.info(f"Iteration {i+1}/{iterations}: Added {leak_size_mb} MB")
            
            # Sleep to allow tracking thread to take snapshots
            time.sleep(0.5)
    
    finally:
        # Stop memory tracking
        stop_memory_tracking()
    
    # Generate and print report
    report = generate_memory_report()
    print("\n--- Memory Leak Simulation Report ---")
    print(f"Number of snapshots: {report['num_snapshots']}")
    print(f"Duration: {report['duration_seconds']:.2f} seconds")
    print(f"Initial memory: {report['first_snapshot']['memory_usage']['rss_mb']:.2f} MB")
    print(f"Final memory: {report['last_snapshot']['memory_usage']['rss_mb']:.2f} MB")
    
    # Detect leaks
    leaks = detect_memory_leaks(threshold_mb_per_hour=5.0)
    
    if leaks:
        print("\nPotential memory leaks detected:")
        for i, leak in enumerate(leaks):
            print(f"\nLeak {i+1}:")
            print(f"  From: {leak['from_snapshot']} to {leak['to_snapshot']}")
            print(f"  Growth rate: {leak['growth_rate_mb_per_hour']:.2f} MB/hour")
            print(f"  Memory diff: {leak['memory_diff_mb'].get('rss_mb', 0):.2f} MB")
            
            # Print object differences if available
            if leak.get('object_diff'):
                print("\n  Top object count differences:")
                for obj_type, diff in list(leak['object_diff'].items())[:5]:
                    print(f"    {obj_type}: {diff}")
    else:
        print("\nNo memory leaks detected.")


def test_dataframe_optimization() -> None:
    """Test memory optimization techniques for DataFrames."""
    logger.info("Testing DataFrame memory optimization techniques")
    
    # Create a large DataFrame
    df = create_large_dataframe(rows=500000, cols=10)
    
    # Take a snapshot before optimization
    take_memory_snapshot("before-optimization")
    
    # Get initial memory usage
    initial_size = df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
    logger.info(f"Initial DataFrame size: {initial_size:.2f} MB")
    
    # Optimize the DataFrame
    optimized_df = optimize_dataframe(df)
    
    # Take a snapshot after optimization
    take_memory_snapshot("after-optimization")
    
    # Get optimized memory usage
    optimized_size = optimized_df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
    logger.info(f"Optimized DataFrame size: {optimized_size:.2f} MB")
    logger.info(f"Memory reduction: {initial_size - optimized_size:.2f} MB ({(1 - optimized_size/initial_size) * 100:.2f}%)")
    
    # Generate report
    report = generate_memory_report()
    comparison = report.get("overall_comparison", {})
    memory_diff = comparison.get("memory_diff_mb", {})
    
    print("\n--- DataFrame Optimization Report ---")
    print(f"Initial DataFrame size: {initial_size:.2f} MB")
    print(f"Optimized DataFrame size: {optimized_size:.2f} MB")
    print(f"Memory reduction: {initial_size - optimized_size:.2f} MB ({(1 - optimized_size/initial_size) * 100:.2f}%)")
    print(f"Process memory change: {memory_diff.get('rss_mb', 0):.2f} MB")


def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize a DataFrame for memory efficiency.
    
    Args:
        df: DataFrame to optimize
        
    Returns:
        Optimized DataFrame
    """
    logger.info("Optimizing DataFrame for memory efficiency")
    
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Optimize numeric columns by downcasting
    for col in result.select_dtypes(include=['int']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')
    
    for col in result.select_dtypes(include=['float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='float')
    
    # Optimize string columns by using categorical type for repeated values
    for col in result.select_dtypes(include=['object']).columns:
        # Check if the column has a low cardinality (many repeated values)
        num_unique = result[col].nunique()
        if num_unique < len(result) * 0.5:  # If less than 50% unique values
            result[col] = result[col].astype('category')
    
    # Optimize memory by removing unnecessary copies
    result = result.copy()
    
    return result


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Memory profiler test script")
    parser.add_argument("--test", choices=["dataframe", "leak", "all"], default="all",
                        help="Test to run (default: all)")
    parser.add_argument("--iterations", type=int, default=10,
                        help="Number of iterations for leak simulation (default: 10)")
    parser.add_argument("--leak-size", type=float, default=10.0,
                        help="Size of the leak in MB per iteration (default: 10.0)")
    args = parser.parse_args()
    
    if args.test in ["dataframe", "all"]:
        # Test DataFrame processing and optimization
        test_dataframe_optimization()
    
    if args.test in ["leak", "all"]:
        # Simulate a memory leak
        simulate_memory_leak(iterations=args.iterations, leak_size_mb=args.leak_size)


if __name__ == "__main__":
    main()