"""
General Benchmarking Framework

This module provides a general framework for benchmarking different operations
in the URL Analyzer. It allows for consistent measurement and reporting of
performance metrics across different components of the system.
"""

import os
import sys
import time
import json
import argparse
import importlib
from typing import Dict, List, Any, Callable, Optional, Union, Tuple
from datetime import datetime
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from url_analyzer.utils.logging import setup_logging, get_logger
from url_analyzer.utils.performance import (
    timer, timed, track_memory_usage, get_memory_usage,
    reset_metrics, get_metrics, generate_performance_report, save_performance_report
)

# Create logger
logger = get_logger(__name__)

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    logger.warning("Visualization libraries not available. Visualization features will be disabled.")

# Try to import profiling tools
try:
    import cProfile
    import pstats
    import io
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False
    logger.warning("Profiling tools not available. Profiling features will be disabled.")


class BenchmarkResult:
    """Class to store and analyze benchmark results."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a benchmark result.
        
        Args:
            name: Name of the benchmark
            description: Description of the benchmark
        """
        self.name = name
        self.description = description
        self.start_time = datetime.now()
        self.end_time = None
        self.iterations = 0
        self.operation_count = 0
        self.execution_time = 0.0
        self.memory_before = {}
        self.memory_after = {}
        self.memory_diff = {}
        self.metrics = {}
        self.profiling_stats = None
        self.error = None
    
    def set_execution_time(self, seconds: float) -> None:
        """
        Set the execution time for the benchmark.
        
        Args:
            seconds: Execution time in seconds
        """
        self.execution_time = seconds
    
    def set_memory_usage(self, before: Dict[str, float], after: Dict[str, float]) -> None:
        """
        Set memory usage information.
        
        Args:
            before: Memory usage before the benchmark
            after: Memory usage after the benchmark
        """
        self.memory_before = before
        self.memory_after = after
        
        # Calculate memory difference
        self.memory_diff = {
            key: after.get(key, 0) - before.get(key, 0)
            for key in set(before.keys()) | set(after.keys())
        }
    
    def set_profiling_stats(self, stats: Any) -> None:
        """
        Set profiling statistics.
        
        Args:
            stats: Profiling statistics object
        """
        self.profiling_stats = stats
    
    def set_error(self, error: Exception) -> None:
        """
        Set error information if the benchmark failed.
        
        Args:
            error: Exception that occurred during the benchmark
        """
        self.error = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc()
        }
    
    def set_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Set additional metrics for the benchmark.
        
        Args:
            metrics: Dictionary of metrics
        """
        self.metrics = metrics
    
    def complete(self) -> None:
        """Mark the benchmark as complete and record the end time."""
        self.end_time = datetime.now()
    
    def get_operations_per_second(self) -> float:
        """
        Calculate operations per second.
        
        Returns:
            Operations per second
        """
        if self.execution_time > 0 and self.operation_count > 0:
            return self.operation_count / self.execution_time
        return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the benchmark results.
        
        Returns:
            Dictionary with benchmark summary
        """
        return {
            'name': self.name,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'iterations': self.iterations,
            'operation_count': self.operation_count,
            'execution_time': self.execution_time,
            'operations_per_second': self.get_operations_per_second(),
            'memory_before': self.memory_before,
            'memory_after': self.memory_after,
            'memory_diff': self.memory_diff,
            'error': self.error,
            'metrics': self.metrics
        }
    
    def to_json(self) -> str:
        """
        Convert the benchmark results to JSON.
        
        Returns:
            JSON string with benchmark results
        """
        return json.dumps(self.get_summary(), indent=2, default=str)


class Benchmark:
    """Class for running benchmarks on different operations."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a benchmark.
        
        Args:
            name: Name of the benchmark
            description: Description of the benchmark
        """
        self.name = name
        self.description = description
        self.setup_func = None
        self.teardown_func = None
        self.benchmark_func = None
        self.iterations = 1
        self.operation_count = 1
        self.profile = False
        self.warmup_iterations = 0
    
    def setup(self, func: Callable) -> Callable:
        """
        Decorator to set the setup function.
        
        Args:
            func: Setup function
            
        Returns:
            The setup function
        """
        self.setup_func = func
        return func
    
    def teardown(self, func: Callable) -> Callable:
        """
        Decorator to set the teardown function.
        
        Args:
            func: Teardown function
            
        Returns:
            The teardown function
        """
        self.teardown_func = func
        return func
    
    def benchmark(self, func: Callable) -> Callable:
        """
        Decorator to set the benchmark function.
        
        Args:
            func: Benchmark function
            
        Returns:
            The benchmark function
        """
        self.benchmark_func = func
        return func
    
    def set_iterations(self, iterations: int) -> 'Benchmark':
        """
        Set the number of iterations for the benchmark.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Self for method chaining
        """
        self.iterations = iterations
        return self
    
    def set_operation_count(self, count: int) -> 'Benchmark':
        """
        Set the number of operations per iteration.
        
        Args:
            count: Number of operations
            
        Returns:
            Self for method chaining
        """
        self.operation_count = count
        return self
    
    def set_profile(self, profile: bool) -> 'Benchmark':
        """
        Enable or disable profiling.
        
        Args:
            profile: Whether to enable profiling
            
        Returns:
            Self for method chaining
        """
        self.profile = profile and PROFILING_AVAILABLE
        return self
    
    def set_warmup(self, iterations: int) -> 'Benchmark':
        """
        Set the number of warmup iterations.
        
        Args:
            iterations: Number of warmup iterations
            
        Returns:
            Self for method chaining
        """
        self.warmup_iterations = iterations
        return self
    
    def run(self, *args, **kwargs) -> BenchmarkResult:
        """
        Run the benchmark.
        
        Args:
            *args: Arguments to pass to the benchmark function
            **kwargs: Keyword arguments to pass to the benchmark function
            
        Returns:
            BenchmarkResult object with benchmark results
        """
        result = BenchmarkResult(self.name, self.description)
        result.iterations = self.iterations
        result.operation_count = self.operation_count
        
        # Check if benchmark function is set
        if self.benchmark_func is None:
            raise ValueError("Benchmark function not set")
        
        try:
            # Run setup if provided
            setup_data = None
            if self.setup_func:
                logger.info(f"Running setup for benchmark '{self.name}'")
                setup_data = self.setup_func(*args, **kwargs)
            
            # Track memory usage before benchmark
            memory_before = get_memory_usage()
            result.set_memory_usage(memory_before, {})  # Will be updated after benchmark
            
            # Run warmup iterations if specified
            if self.warmup_iterations > 0:
                logger.info(f"Running {self.warmup_iterations} warmup iterations")
                for _ in range(self.warmup_iterations):
                    if setup_data is not None:
                        self.benchmark_func(setup_data)
                    else:
                        self.benchmark_func(*args, **kwargs)
            
            # Run the benchmark with profiling if enabled
            if self.profile:
                logger.info(f"Running benchmark '{self.name}' with profiling")
                profiler = cProfile.Profile()
                profiler.enable()
                
                start_time = time.time()
                
                for _ in range(self.iterations):
                    if setup_data is not None:
                        self.benchmark_func(setup_data)
                    else:
                        self.benchmark_func(*args, **kwargs)
                
                end_time = time.time()
                
                profiler.disable()
                
                # Get profiling stats
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
                ps.print_stats(20)  # Print top 20 functions
                result.set_profiling_stats(s.getvalue())
            else:
                logger.info(f"Running benchmark '{self.name}'")
                
                start_time = time.time()
                
                for _ in range(self.iterations):
                    if setup_data is not None:
                        self.benchmark_func(setup_data)
                    else:
                        self.benchmark_func(*args, **kwargs)
                
                end_time = time.time()
            
            # Calculate execution time
            execution_time = end_time - start_time
            result.set_execution_time(execution_time)
            
            # Track memory usage after benchmark
            memory_after = get_memory_usage()
            result.set_memory_usage(memory_before, memory_after)
            
            # Run teardown if provided
            if self.teardown_func:
                logger.info(f"Running teardown for benchmark '{self.name}'")
                if setup_data is not None:
                    self.teardown_func(setup_data)
                else:
                    self.teardown_func(*args, **kwargs)
            
            # Get performance metrics
            result.set_metrics(get_metrics())
            
            # Mark benchmark as complete
            result.complete()
            
            # Log results
            logger.info(f"Benchmark '{self.name}' completed in {execution_time:.6f} seconds")
            logger.info(f"Operations per second: {result.get_operations_per_second():.2f}")
            logger.info(f"Memory usage diff: {result.memory_diff.get('rss', 0):.2f} MB RSS")
            
            return result
        
        except Exception as e:
            logger.error(f"Error running benchmark '{self.name}': {e}")
            result.set_error(e)
            result.complete()
            return result


def run_benchmark_module(module_name: str, **kwargs) -> List[BenchmarkResult]:
    """
    Run all benchmarks in a module.
    
    Args:
        module_name: Name of the module containing benchmarks
        **kwargs: Additional arguments to pass to the benchmarks
        
    Returns:
        List of BenchmarkResult objects
    """
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # Find all Benchmark instances in the module
        benchmarks = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, Benchmark):
                benchmarks.append(attr)
        
        if not benchmarks:
            logger.warning(f"No benchmarks found in module '{module_name}'")
            return []
        
        # Run each benchmark
        results = []
        for benchmark in benchmarks:
            logger.info(f"Running benchmark '{benchmark.name}'")
            result = benchmark.run(**kwargs)
            results.append(result)
        
        return results
    
    except Exception as e:
        logger.error(f"Error running benchmarks from module '{module_name}': {e}")
        return []


def generate_benchmark_report(results: List[BenchmarkResult], output_file: Optional[str] = None) -> str:
    """
    Generate a benchmark report.
    
    Args:
        results: List of BenchmarkResult objects
        output_file: Path to the output file (if None, returns the report as a string)
        
    Returns:
        Report as a string if output_file is None, otherwise the path to the output file
    """
    # Generate report
    report = []
    report.append("# Benchmark Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Add summary
    report.append("## Summary")
    report.append("")
    report.append("| Benchmark | Operations/sec | Memory Diff (MB) | Status |")
    report.append("|-----------|---------------|-----------------|--------|")
    
    for result in results:
        status = "Error" if result.error else "Success"
        memory_diff = result.memory_diff.get('rss', 0)
        report.append(f"| {result.name} | {result.get_operations_per_second():.2f} | {memory_diff:.2f} | {status} |")
    
    # Add detailed results
    for result in results:
        report.append("")
        report.append(f"## {result.name}")
        report.append("")
        report.append(f"Description: {result.description}")
        report.append("")
        report.append(f"- Start Time: {result.start_time}")
        report.append(f"- End Time: {result.end_time}")
        report.append(f"- Iterations: {result.iterations}")
        report.append(f"- Operation Count: {result.operation_count}")
        report.append(f"- Execution Time: {result.execution_time:.6f} seconds")
        report.append(f"- Operations per Second: {result.get_operations_per_second():.2f}")
        
        # Memory usage
        report.append("")
        report.append("### Memory Usage")
        report.append("")
        report.append("| Metric | Before (MB) | After (MB) | Diff (MB) |")
        report.append("|--------|------------|-----------|-----------|")
        
        for key in sorted(set(result.memory_before.keys()) | set(result.memory_after.keys())):
            before = result.memory_before.get(key, 0)
            after = result.memory_after.get(key, 0)
            diff = result.memory_diff.get(key, 0)
            report.append(f"| {key} | {before:.2f} | {after:.2f} | {diff:.2f} |")
        
        # Profiling stats
        if result.profiling_stats:
            report.append("")
            report.append("### Profiling Statistics")
            report.append("")
            report.append("```")
            report.append(result.profiling_stats)
            report.append("```")
        
        # Error information
        if result.error:
            report.append("")
            report.append("### Error")
            report.append("")
            report.append(f"Type: {result.error['type']}")
            report.append(f"Message: {result.error['message']}")
            report.append("")
            report.append("```")
            report.append(result.error['traceback'])
            report.append("```")
    
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


def generate_benchmark_visualization(results: List[BenchmarkResult], output_file: Optional[str] = None):
    """
    Generate visualizations of benchmark results.
    
    Args:
        results: List of BenchmarkResult objects
        output_file: Path to the output file (if None, displays the visualizations)
        
    Returns:
        Path to the output file if output_file is not None
    """
    # Check if visualization libraries are available
    if not VISUALIZATION_AVAILABLE:
        logger.warning("Visualization libraries not available. Visualization skipped.")
        print("Visualization skipped: matplotlib and numpy are not available.")
        return None
    
    try:
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Extract data
        names = [result.name for result in results]
        ops_per_sec = [result.get_operations_per_second() for result in results]
        memory_diffs = [result.memory_diff.get('rss', 0) for result in results]
        
        # Create subplots
        plt.subplot(2, 1, 1)
        bars = plt.bar(names, ops_per_sec, color='#1f77b4')
        plt.ylabel('Operations per Second')
        plt.title('Benchmark Performance Comparison')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add values on top of bars
        for bar, value in zip(bars, ops_per_sec):
            plt.text(bar.get_x() + bar.get_width() / 2, value + 0.1, f"{value:.2f}", ha='center')
        
        plt.subplot(2, 1, 2)
        bars = plt.bar(names, memory_diffs, color='#ff7f0e')
        plt.ylabel('Memory Usage Diff (MB)')
        plt.title('Memory Usage Comparison')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add values on top of bars
        for bar, value in zip(bars, memory_diffs):
            plt.text(bar.get_x() + bar.get_width() / 2, value + 0.1, f"{value:.2f}", ha='center')
        
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
    """Main entry point for the benchmark framework."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run benchmarks for URL Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('module', help="Module containing benchmarks to run")
    parser.add_argument('--iterations', type=int, default=3,
                      help="Number of iterations for each benchmark (default: 3)")
    parser.add_argument('--warmup', type=int, default=1,
                      help="Number of warmup iterations (default: 1)")
    parser.add_argument('--profile', action='store_true', help="Enable profiling")
    parser.add_argument('--report', help="Path to save the benchmark report")
    parser.add_argument('--visualization', help="Path to save the benchmark visualization")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level=log_level)
    
    # Reset performance metrics
    reset_metrics()
    
    # Run benchmarks
    logger.info(f"Running benchmarks from module '{args.module}'")
    
    results = run_benchmark_module(
        args.module,
        iterations=args.iterations,
        warmup=args.warmup,
        profile=args.profile
    )
    
    if not results:
        logger.error("No benchmark results available")
        return 1
    
    # Generate report
    if args.report:
        report_path = generate_benchmark_report(results, args.report)
        print(f"\nBenchmark report saved to: {report_path}")
    else:
        report = generate_benchmark_report(results)
        print("\n" + report)
    
    # Generate visualization
    if args.visualization:
        viz_path = generate_benchmark_visualization(results, args.visualization)
        if viz_path:
            print(f"Benchmark visualization saved to: {viz_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())