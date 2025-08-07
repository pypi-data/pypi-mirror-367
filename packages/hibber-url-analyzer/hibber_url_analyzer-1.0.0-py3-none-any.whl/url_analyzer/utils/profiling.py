"""
Performance profiling module for URL Analyzer.

This module provides tools for automated performance benchmarks, continuous performance
monitoring, performance regression detection, and performance reports with actionable insights.
It also includes utilities for adding performance annotations to critical code paths.
"""

import os
import sys
import time
import json
import logging
import functools
import statistics
import datetime
from typing import Dict, List, Any, Callable, Optional, Union, Tuple, Set
from pathlib import Path
import traceback

# Try to import profiling tools
try:
    import cProfile
    import pstats
    import io
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Import from url_analyzer
from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.performance import (
    timer, timed, track_memory_usage, get_memory_usage,
    reset_metrics, get_metrics, generate_performance_report
)

# Create logger
logger = get_logger(__name__)

# Global variables
_performance_history: Dict[str, List[Dict[str, Any]]] = {}
_regression_thresholds: Dict[str, Dict[str, float]] = {}
_critical_paths: Set[str] = set()
_baseline_metrics: Dict[str, Dict[str, Any]] = {}
_monitoring_enabled = False
_history_file_path = None


def enable_profiling(enabled: bool = True) -> None:
    """
    Enable or disable performance profiling.
    
    Args:
        enabled: Whether to enable profiling
    """
    global _monitoring_enabled
    _monitoring_enabled = enabled
    logger.info(f"Performance profiling {'enabled' if enabled else 'disabled'}")


def is_profiling_enabled() -> bool:
    """
    Check if performance profiling is enabled.
    
    Returns:
        True if profiling is enabled, False otherwise
    """
    return _monitoring_enabled


def set_history_file(file_path: str) -> None:
    """
    Set the file path for storing performance history.
    
    Args:
        file_path: Path to the history file
    """
    global _history_file_path
    _history_file_path = file_path
    logger.info(f"Performance history file set to: {file_path}")
    
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    # Create empty file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)


def load_performance_history() -> None:
    """
    Load performance history from the history file.
    """
    global _performance_history
    
    if not _history_file_path or not os.path.exists(_history_file_path):
        logger.warning("Performance history file not found")
        return
    
    try:
        with open(_history_file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                logger.info("Performance history file is empty, starting with empty history")
                return
            history_data = json.loads(content)
            
        # Convert to the internal format
        for entry in history_data:
            if 'name' in entry and 'timestamp' in entry and 'metrics' in entry:
                name = entry['name']
                if name not in _performance_history:
                    _performance_history[name] = []
                _performance_history[name].append({
                    'timestamp': entry['timestamp'],
                    'metrics': entry['metrics']
                })
        
        logger.info(f"Loaded performance history for {len(_performance_history)} benchmarks")
    except Exception as e:
        logger.error(f"Error loading performance history: {e}")


def save_performance_history() -> None:
    """
    Save performance history to the history file.
    """
    if not _history_file_path:
        logger.warning("Performance history file path not set")
        return
    
    try:
        # Convert to a serializable format
        history_data = []
        for name, entries in _performance_history.items():
            for entry in entries:
                history_data.append({
                    'name': name,
                    'timestamp': entry['timestamp'],
                    'metrics': entry['metrics']
                })
        
        with open(_history_file_path, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        logger.info(f"Saved performance history to {_history_file_path}")
    except Exception as e:
        logger.error(f"Error saving performance history: {e}")


def record_benchmark_result(name: str, metrics: Dict[str, Any]) -> None:
    """
    Record a benchmark result in the performance history.
    
    Args:
        name: Name of the benchmark
        metrics: Benchmark metrics
    """
    if not _monitoring_enabled:
        return
    
    if name not in _performance_history:
        _performance_history[name] = []
    
    _performance_history[name].append({
        'timestamp': datetime.datetime.now().isoformat(),
        'metrics': metrics
    })
    
    logger.debug(f"Recorded benchmark result for {name}")
    
    # Save history after each recording
    save_performance_history()


def set_baseline(name: str, metrics: Dict[str, Any]) -> None:
    """
    Set a baseline for a benchmark.
    
    Args:
        name: Name of the benchmark
        metrics: Baseline metrics
    """
    global _baseline_metrics
    
    _baseline_metrics[name] = {
        'timestamp': datetime.datetime.now().isoformat(),
        'metrics': metrics
    }
    
    logger.info(f"Set baseline for {name}")


def get_baseline(name: str) -> Optional[Dict[str, Any]]:
    """
    Get the baseline for a benchmark.
    
    Args:
        name: Name of the benchmark
        
    Returns:
        Baseline metrics or None if no baseline exists
    """
    return _baseline_metrics.get(name)


def set_regression_threshold(name: str, metric: str, threshold: float) -> None:
    """
    Set a regression threshold for a benchmark metric.
    
    Args:
        name: Name of the benchmark
        metric: Name of the metric
        threshold: Threshold value (as a multiplier, e.g., 1.2 for 20% increase)
    """
    if name not in _regression_thresholds:
        _regression_thresholds[name] = {}
    
    _regression_thresholds[name][metric] = threshold
    
    logger.info(f"Set regression threshold for {name}.{metric} to {threshold}")


def detect_regressions(name: str, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect performance regressions by comparing current metrics with the baseline.
    
    Args:
        name: Name of the benchmark
        current_metrics: Current benchmark metrics
        
    Returns:
        List of detected regressions
    """
    if not _monitoring_enabled:
        return []
    
    baseline = get_baseline(name)
    if not baseline:
        logger.warning(f"No baseline found for {name}")
        return []
    
    thresholds = _regression_thresholds.get(name, {})
    default_threshold = 1.1  # 10% increase by default
    
    regressions = []
    
    for metric, current_value in current_metrics.items():
        if metric not in baseline['metrics']:
            continue
        
        baseline_value = baseline['metrics'][metric]
        
        # Skip non-numeric values
        if not isinstance(current_value, (int, float)) or not isinstance(baseline_value, (int, float)):
            continue
        
        # Skip zero values to avoid division by zero
        if baseline_value == 0:
            continue
        
        # Calculate the ratio
        ratio = current_value / baseline_value
        
        # Get the threshold for this metric
        threshold = thresholds.get(metric, default_threshold)
        
        # Check if the ratio exceeds the threshold
        if ratio > threshold:
            regressions.append({
                'name': name,
                'metric': metric,
                'baseline_value': baseline_value,
                'current_value': current_value,
                'ratio': ratio,
                'threshold': threshold
            })
    
    return regressions


def mark_critical_path(name: str) -> None:
    """
    Mark a code path as critical for performance monitoring.
    
    Args:
        name: Name of the critical path
    """
    _critical_paths.add(name)
    logger.info(f"Marked {name} as a critical path")


def is_critical_path(name: str) -> bool:
    """
    Check if a code path is marked as critical.
    
    Args:
        name: Name of the code path
        
    Returns:
        True if the path is critical, False otherwise
    """
    return name in _critical_paths


def profile(func=None, *, name: Optional[str] = None) -> Callable:
    """
    Decorator for profiling a function.
    
    Args:
        func: Function to profile
        name: Name for the profile (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(fn):
        nonlocal name
        if name is None:
            name = fn.__qualname__
        
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not _monitoring_enabled or not PROFILING_AVAILABLE:
                return fn(*args, **kwargs)
            
            # Create a profile
            pr = cProfile.Profile()
            pr.enable()
            
            # Track memory usage
            mem_before = get_memory_usage()
            
            # Track time
            start_time = time.time()
            
            try:
                # Run the function
                result = fn(*args, **kwargs)
                return result
            finally:
                # Stop timing
                execution_time = time.time() - start_time
                
                # Get memory usage after
                mem_after = get_memory_usage()
                
                # Disable profiling
                pr.disable()
                
                # Get profiling stats
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                ps.print_stats(20)  # Print top 20 functions
                
                # Record metrics
                metrics = {
                    'execution_time': execution_time,
                    'memory_before': mem_before,
                    'memory_after': mem_after,
                    'memory_diff': {
                        k: mem_after[k] - mem_before[k] for k in mem_before
                    },
                    'profile_stats': s.getvalue()
                }
                
                # Record the result
                record_benchmark_result(name, metrics)
                
                # Check for regressions
                regressions = detect_regressions(name, metrics)
                if regressions:
                    for reg in regressions:
                        logger.warning(
                            f"Performance regression detected in {reg['name']}.{reg['metric']}: "
                            f"{reg['baseline_value']:.4f} -> {reg['current_value']:.4f} "
                            f"({(reg['ratio']-1)*100:.1f}% increase, threshold: {(reg['threshold']-1)*100:.1f}%)"
                        )
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def generate_profiling_report(output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a comprehensive profiling report with actionable insights.
    
    Args:
        output_file: Path to save the report (optional)
        
    Returns:
        Report data
    """
    report = {
        'timestamp': datetime.datetime.now().isoformat(),
        'benchmarks': {},
        'critical_paths': list(_critical_paths),
        'regressions': [],
        'insights': [],
        'recommendations': []
    }
    
    # Process each benchmark
    for name, entries in _performance_history.items():
        if not entries:
            continue
        
        # Get the latest entry
        latest = entries[-1]
        
        # Get baseline
        baseline = get_baseline(name)
        
        # Calculate statistics for execution time
        times = [entry['metrics'].get('execution_time', 0) for entry in entries if 'execution_time' in entry['metrics']]
        
        time_stats = {}
        if times:
            time_stats = {
                'min': min(times),
                'max': max(times),
                'mean': statistics.mean(times),
                'median': statistics.median(times),
                'stdev': statistics.stdev(times) if len(times) > 1 else 0
            }
        
        # Add benchmark to report
        report['benchmarks'][name] = {
            'latest': latest,
            'baseline': baseline,
            'history_count': len(entries),
            'time_stats': time_stats,
            'is_critical': name in _critical_paths
        }
        
        # Check for regressions
        if baseline:
            regressions = detect_regressions(name, latest['metrics'])
            if regressions:
                report['regressions'].extend(regressions)
    
    # Generate insights
    if report['regressions']:
        report['insights'].append({
            'type': 'regression',
            'message': f"Detected {len(report['regressions'])} performance regressions",
            'details': report['regressions']
        })
    
    # Add insights for critical paths
    critical_benchmarks = [name for name in report['benchmarks'] if name in _critical_paths]
    if critical_benchmarks:
        report['insights'].append({
            'type': 'critical_paths',
            'message': f"Monitoring {len(critical_benchmarks)} critical paths",
            'details': critical_benchmarks
        })
    
    # Generate recommendations
    if report['regressions']:
        report['recommendations'].append({
            'type': 'investigate_regressions',
            'message': "Investigate performance regressions in the following areas",
            'details': [f"{r['name']}.{r['metric']}" for r in report['regressions']]
        })
    
    # Add recommendation for missing baselines
    missing_baselines = [
        name for name in report['benchmarks'] 
        if not report['benchmarks'][name]['baseline'] and name in _critical_paths
    ]
    if missing_baselines:
        report['recommendations'].append({
            'type': 'set_baselines',
            'message': "Set performance baselines for critical paths",
            'details': missing_baselines
        })
    
    # Save report to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Saved profiling report to {output_file}")
        except Exception as e:
            logger.error(f"Error saving profiling report: {e}")
    
    return report


def visualize_profiling_report(report: Dict[str, Any], output_file: Optional[str] = None) -> bool:
    """
    Create visualizations for a profiling report.
    
    Args:
        report: Profiling report data
        output_file: Path to save the visualization (optional)
        
    Returns:
        True if visualization was created, False otherwise
    """
    if not VISUALIZATION_AVAILABLE:
        logger.warning("Visualization libraries not available")
        return False
    
    try:
        # Create a new figure
        plt.figure(figsize=(12, 10))
        
        # Plot execution times for benchmarks
        benchmark_names = []
        latest_times = []
        baseline_times = []
        
        for name, data in report['benchmarks'].items():
            if 'latest' in data and 'execution_time' in data['latest']['metrics']:
                benchmark_names.append(name)
                latest_times.append(data['latest']['metrics']['execution_time'])
                
                if data['baseline'] and 'execution_time' in data['baseline']['metrics']:
                    baseline_times.append(data['baseline']['metrics']['execution_time'])
                else:
                    baseline_times.append(0)
        
        # Sort by latest execution time
        if benchmark_names:
            sorted_indices = np.argsort(latest_times)
            benchmark_names = [benchmark_names[i] for i in sorted_indices]
            latest_times = [latest_times[i] for i in sorted_indices]
            baseline_times = [baseline_times[i] for i in sorted_indices]
            
            # Plot execution times
            plt.subplot(2, 1, 1)
            x = np.arange(len(benchmark_names))
            width = 0.35
            
            plt.bar(x - width/2, latest_times, width, label='Latest')
            plt.bar(x + width/2, baseline_times, width, label='Baseline')
            
            plt.xlabel('Benchmark')
            plt.ylabel('Execution Time (s)')
            plt.title('Benchmark Execution Times')
            plt.xticks(x, benchmark_names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
        
        # Plot regressions
        if report['regressions']:
            plt.subplot(2, 1, 2)
            
            regression_names = [f"{r['name']}.{r['metric']}" for r in report['regressions']]
            regression_ratios = [r['ratio'] for r in report['regressions']]
            regression_thresholds = [r['threshold'] for r in report['regressions']]
            
            x = np.arange(len(regression_names))
            
            plt.bar(x, regression_ratios, label='Regression Ratio')
            plt.plot(x, regression_thresholds, 'r--', label='Threshold')
            
            plt.xlabel('Metric')
            plt.ylabel('Ratio (Current/Baseline)')
            plt.title('Performance Regressions')
            plt.xticks(x, regression_names, rotation=45, ha='right')
            plt.axhline(y=1.0, color='g', linestyle='-', label='Baseline')
            plt.legend()
        
        plt.tight_layout()
        
        # Save to file if requested
        if output_file:
            plt.savefig(output_file)
            logger.info(f"Saved visualization to {output_file}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return False


def init_module(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the profiling module.
    
    Args:
        config: Configuration dictionary
    """
    global _monitoring_enabled, _history_file_path
    
    if config is None:
        config = {}
    
    # Set default configuration
    _monitoring_enabled = config.get('enabled', False)
    
    # Set history file path
    history_file = config.get('history_file', 'performance_history.json')
    if history_file:
        set_history_file(history_file)
        load_performance_history()
    
    # Set regression thresholds
    thresholds = config.get('regression_thresholds', {})
    for name, metrics in thresholds.items():
        for metric, threshold in metrics.items():
            set_regression_threshold(name, metric, threshold)
    
    # Mark critical paths
    critical_paths = config.get('critical_paths', [])
    for path in critical_paths:
        mark_critical_path(path)
    
    logger.info(f"Initialized profiling module (enabled: {_monitoring_enabled})")


# Initialize the module with default settings
init_module()