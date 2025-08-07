"""
Performance Monitoring Module

This module provides utilities for monitoring and tracking performance metrics
such as execution time, memory usage, and other performance indicators.
"""

import time
import functools
import logging
import os
import sys
import threading
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from contextlib import contextmanager

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Global performance metrics storage
_performance_metrics = {
    'timings': {},
    'memory': {},
    'counters': {},
    'gauges': {},
    'histograms': {}
}

# Thread-local storage for nested timers
_thread_local = threading.local()

# Lock for thread-safe operations
_metrics_lock = threading.Lock()

# Flag to enable/disable performance monitoring
_monitoring_enabled = True


def enable_monitoring(enabled: bool = True) -> None:
    """
    Enable or disable performance monitoring.
    
    Args:
        enabled: Whether to enable performance monitoring
    """
    global _monitoring_enabled
    _monitoring_enabled = enabled
    logger.info(f"Performance monitoring {'enabled' if enabled else 'disabled'}")


def is_monitoring_enabled() -> bool:
    """
    Check if performance monitoring is enabled.
    
    Returns:
        True if performance monitoring is enabled, False otherwise
    """
    return _monitoring_enabled


def reset_metrics() -> None:
    """Reset all performance metrics."""
    global _performance_metrics
    with _metrics_lock:
        _performance_metrics = {
            'timings': {},
            'memory': {},
            'counters': {},
            'gauges': {},
            'histograms': {}
        }
    logger.debug("Performance metrics reset")


def get_metrics() -> Dict[str, Any]:
    """
    Get a copy of all performance metrics.
    
    Returns:
        Dictionary containing all performance metrics
    """
    with _metrics_lock:
        return {k: v.copy() for k, v in _performance_metrics.items()}


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage information.
    
    Returns:
        Dictionary with memory usage information in MB
    """
    memory_info = {'rss': 0, 'vms': 0, 'shared': 0, 'data': 0, 'available': 0, 'percent': 0}
    
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        
        # Convert to MB
        memory_info['rss'] = mem.rss / (1024 * 1024)  # Resident Set Size
        memory_info['vms'] = mem.vms / (1024 * 1024)  # Virtual Memory Size
        
        # Additional metrics if available
        if hasattr(mem, 'shared'):
            memory_info['shared'] = mem.shared / (1024 * 1024)
        if hasattr(mem, 'data'):
            memory_info['data'] = mem.data / (1024 * 1024)
        
        # System memory
        system_mem = psutil.virtual_memory()
        memory_info['available'] = system_mem.available / (1024 * 1024)
        memory_info['percent'] = system_mem.percent
        
    except ImportError:
        # Fallback to simpler memory tracking if psutil is not available
        import resource
        memory_info['rss'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # KB to MB
    except Exception as e:
        logger.warning(f"Error getting memory usage: {e}")
    
    return memory_info


def track_memory_usage(label: str) -> None:
    """
    Track current memory usage with the given label.
    
    Args:
        label: Label for the memory usage measurement
    """
    if not _monitoring_enabled:
        return
    
    memory_info = get_memory_usage()
    
    with _metrics_lock:
        _performance_metrics['memory'][label] = memory_info
    
    logger.debug(f"Memory usage for {label}: {memory_info['rss']:.2f} MB RSS")


@contextmanager
def timer(label: str, log_level: int = logging.DEBUG) -> None:
    """
    Context manager for timing code blocks.
    
    Args:
        label: Label for the timer
        log_level: Logging level for the timing message
    
    Example:
        ```python
        with timer("process_file"):
            process_file(file_path)
        ```
    """
    if not hasattr(_thread_local, 'timer_stack'):
        _thread_local.timer_stack = []
    
    start_time = time.time()
    parent_timer = _thread_local.timer_stack[-1] if _thread_local.timer_stack else None
    _thread_local.timer_stack.append(label)
    
    try:
        yield
    finally:
        if _thread_local.timer_stack and _thread_local.timer_stack[-1] == label:
            _thread_local.timer_stack.pop()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if _monitoring_enabled:
            with _metrics_lock:
                if label not in _performance_metrics['timings']:
                    _performance_metrics['timings'][label] = {
                        'count': 0,
                        'total': 0,
                        'min': float('inf'),
                        'max': 0,
                        'avg': 0
                    }
                
                metrics = _performance_metrics['timings'][label]
                metrics['count'] += 1
                metrics['total'] += elapsed
                metrics['min'] = min(metrics['min'], elapsed)
                metrics['max'] = max(metrics['max'], elapsed)
                metrics['avg'] = metrics['total'] / metrics['count']
            
            # Track memory usage at the end of the timer
            if parent_timer is None:  # Only track memory for top-level timers
                track_memory_usage(f"{label}_end")
        
        # Log the timing
        prefix = '  ' * len(_thread_local.timer_stack)
        logger.log(log_level, f"{prefix}{label}: {elapsed:.6f} seconds")


def timed(func=None, *, label: Optional[str] = None, log_level: int = logging.DEBUG):
    """
    Decorator for timing function calls.
    
    Args:
        func: Function to time
        label: Label for the timer (defaults to function name)
        log_level: Logging level for the timing message
    
    Returns:
        Decorated function
    
    Example:
        ```python
        @timed
        def process_file(file_path):
            # Process the file
            pass
        
        @timed(label="custom_label", log_level=logging.INFO)
        def another_function():
            # Do something
            pass
        ```
    """
    def decorator(fn):
        nonlocal label
        if label is None:
            label = f"{fn.__module__}.{fn.__qualname__}"
        
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with timer(label, log_level):
                return fn(*args, **kwargs)
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def increment_counter(name: str, value: int = 1) -> None:
    """
    Increment a counter metric.
    
    Args:
        name: Name of the counter
        value: Value to increment by (default: 1)
    """
    if not _monitoring_enabled:
        return
    
    with _metrics_lock:
        if name not in _performance_metrics['counters']:
            _performance_metrics['counters'][name] = 0
        _performance_metrics['counters'][name] += value


def set_gauge(name: str, value: float) -> None:
    """
    Set a gauge metric to a specific value.
    
    Args:
        name: Name of the gauge
        value: Value to set
    """
    if not _monitoring_enabled:
        return
    
    with _metrics_lock:
        _performance_metrics['gauges'][name] = value


def record_histogram_value(name: str, value: float) -> None:
    """
    Record a value in a histogram metric.
    
    Args:
        name: Name of the histogram
        value: Value to record
    """
    if not _monitoring_enabled:
        return
    
    with _metrics_lock:
        if name not in _performance_metrics['histograms']:
            _performance_metrics['histograms'][name] = []
        _performance_metrics['histograms'][name].append(value)


def get_histogram_stats(name: str) -> Dict[str, float]:
    """
    Get statistics for a histogram metric.
    
    Args:
        name: Name of the histogram
    
    Returns:
        Dictionary with histogram statistics (count, min, max, avg)
    """
    with _metrics_lock:
        if name not in _performance_metrics['histograms']:
            return {'count': 0, 'min': 0, 'max': 0, 'avg': 0}
        
        values = _performance_metrics['histograms'][name]
        if not values:
            return {'count': 0, 'min': 0, 'max': 0, 'avg': 0}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }


def generate_performance_report() -> str:
    """
    Generate a human-readable performance report.
    
    Returns:
        String containing the performance report
    """
    metrics = get_metrics()
    
    lines = ["Performance Report", "================="]
    
    # Timings
    lines.append("\nTimings:")
    for label, data in sorted(metrics['timings'].items()):
        lines.append(f"  {label}:")
        lines.append(f"    Count: {data['count']}")
        lines.append(f"    Total: {data['total']:.6f} seconds")
        lines.append(f"    Avg: {data['avg']:.6f} seconds")
        lines.append(f"    Min: {data['min']:.6f} seconds")
        lines.append(f"    Max: {data['max']:.6f} seconds")
    
    # Memory
    lines.append("\nMemory Usage:")
    for label, data in sorted(metrics['memory'].items()):
        lines.append(f"  {label}:")
        for k, v in data.items():
            if isinstance(v, float):
                lines.append(f"    {k}: {v:.2f} MB")
            else:
                lines.append(f"    {k}: {v}")
    
    # Counters
    lines.append("\nCounters:")
    for name, value in sorted(metrics['counters'].items()):
        lines.append(f"  {name}: {value}")
    
    # Gauges
    lines.append("\nGauges:")
    for name, value in sorted(metrics['gauges'].items()):
        lines.append(f"  {name}: {value}")
    
    # Histograms
    lines.append("\nHistograms:")
    for name in sorted(metrics['histograms'].keys()):
        stats = get_histogram_stats(name)
        lines.append(f"  {name}:")
        lines.append(f"    Count: {stats['count']}")
        lines.append(f"    Min: {stats['min']}")
        lines.append(f"    Max: {stats['max']}")
        lines.append(f"    Avg: {stats['avg']}")
    
    return "\n".join(lines)


def save_performance_report(file_path: str) -> None:
    """
    Save a performance report to a file.
    
    Args:
        file_path: Path to save the report to
    """
    report = generate_performance_report()
    
    try:
        with open(file_path, 'w') as f:
            f.write(report)
        logger.info(f"Performance report saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving performance report to {file_path}: {e}")


# Initialize performance monitoring
def init_module(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the performance monitoring module.
    
    Args:
        config: Configuration dictionary
    """
    global _monitoring_enabled
    
    if config is None:
        config = {}
    
    # Get performance monitoring settings from config
    monitoring_enabled = config.get("performance_monitoring", {}).get("enabled", True)
    enable_monitoring(monitoring_enabled)
    
    # Track initial memory usage
    if monitoring_enabled:
        track_memory_usage("init")
        logger.info("Performance monitoring initialized")