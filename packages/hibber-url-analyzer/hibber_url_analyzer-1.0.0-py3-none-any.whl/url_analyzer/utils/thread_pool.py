"""
Thread Pool Optimization Module

This module provides utilities for optimizing thread pool configuration
based on workload characteristics and system resources.
"""

import os
import time
import threading
import multiprocessing
import psutil
from typing import Dict, Any, Optional, Union, Callable, List, Tuple
import concurrent.futures
import logging
import math

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Global variables for tracking thread activity and performance
_thread_metrics = {
    'active_threads': 0,
    'total_threads': 0,
    'cpu_usage': [],
    'io_wait': [],
    'memory_usage': [],
    'task_durations': [],
    'last_update': 0,
    'lock': threading.Lock()
}

# Maximum samples to keep for metrics
MAX_SAMPLES = 100

def update_thread_metrics(active_delta=0, task_duration=None):
    """
    Update thread activity and performance metrics.
    
    Args:
        active_delta: Change in active thread count (+1 for new, -1 for completed)
        task_duration: Duration of a completed task in seconds
    """
    global _thread_metrics
    
    with _thread_metrics['lock']:
        # Update active threads
        _thread_metrics['active_threads'] = max(0, _thread_metrics['active_threads'] + active_delta)
        _thread_metrics['total_threads'] = threading.active_count()
        
        # Update system metrics
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            _thread_metrics['cpu_usage'].append(cpu_percent)
            if len(_thread_metrics['cpu_usage']) > MAX_SAMPLES:
                _thread_metrics['cpu_usage'].pop(0)
            
            # Get I/O wait (only available on Linux)
            if hasattr(psutil, 'cpu_times'):
                cpu_times = psutil.cpu_times_percent(interval=None)
                if hasattr(cpu_times, 'iowait'):
                    _thread_metrics['io_wait'].append(cpu_times.iowait)
                    if len(_thread_metrics['io_wait']) > MAX_SAMPLES:
                        _thread_metrics['io_wait'].pop(0)
            
            # Get memory usage
            memory_percent = psutil.virtual_memory().percent
            _thread_metrics['memory_usage'].append(memory_percent)
            if len(_thread_metrics['memory_usage']) > MAX_SAMPLES:
                _thread_metrics['memory_usage'].pop(0)
        except Exception as e:
            logger.warning(f"Error updating system metrics: {e}")
        
        # Update task duration if provided
        if task_duration is not None:
            _thread_metrics['task_durations'].append(task_duration)
            if len(_thread_metrics['task_durations']) > MAX_SAMPLES:
                _thread_metrics['task_durations'].pop(0)
        
        _thread_metrics['last_update'] = time.time()


def get_thread_metrics() -> Dict[str, Any]:
    """
    Get current thread and performance metrics.
    
    Returns:
        Dictionary with thread and performance metrics
    """
    global _thread_metrics
    
    with _thread_metrics['lock']:
        # Calculate average metrics
        avg_cpu = sum(_thread_metrics['cpu_usage']) / max(1, len(_thread_metrics['cpu_usage']))
        avg_memory = sum(_thread_metrics['memory_usage']) / max(1, len(_thread_metrics['memory_usage']))
        
        # Calculate I/O wait if available
        avg_io_wait = None
        if _thread_metrics['io_wait']:
            avg_io_wait = sum(_thread_metrics['io_wait']) / len(_thread_metrics['io_wait'])
        
        # Calculate average task duration if available
        avg_duration = None
        if _thread_metrics['task_durations']:
            avg_duration = sum(_thread_metrics['task_durations']) / len(_thread_metrics['task_durations'])
        
        # Calculate thread utilization
        thread_utilization = _thread_metrics['active_threads'] / max(1, _thread_metrics['total_threads'])
        
        return {
            'active_threads': _thread_metrics['active_threads'],
            'total_threads': _thread_metrics['total_threads'],
            'thread_utilization': thread_utilization,
            'avg_cpu_usage': avg_cpu,
            'avg_memory_usage': avg_memory,
            'avg_io_wait': avg_io_wait,
            'avg_task_duration': avg_duration,
            'last_update': _thread_metrics['last_update']
        }


def calculate_optimal_thread_count(
    operation_type: str = "io",
    cpu_count: Optional[int] = None,
    metrics: Optional[Dict[str, Any]] = None
) -> int:
    """
    Calculate the optimal thread count based on operation type and system metrics.
    
    Args:
        operation_type: Type of operation ("io", "cpu", or "mixed")
        cpu_count: Number of CPU cores (defaults to system CPU count)
        metrics: Thread and performance metrics (defaults to current metrics)
        
    Returns:
        Optimal thread count
    """
    if cpu_count is None:
        cpu_count = multiprocessing.cpu_count()
    
    if metrics is None:
        metrics = get_thread_metrics()
    
    # Base thread count based on operation type
    if operation_type.lower() == "io":
        # For I/O-bound operations, use more threads
        # Start with CPU count * 4 as a baseline
        base_count = cpu_count * 4
        
        # Adjust based on I/O wait if available
        if metrics.get('avg_io_wait') is not None:
            io_wait = metrics['avg_io_wait']
            # Higher I/O wait suggests more threads could be beneficial
            if io_wait > 20:
                # High I/O wait, increase threads
                base_count = int(base_count * 1.5)
            elif io_wait < 5:
                # Low I/O wait, decrease threads
                base_count = int(base_count * 0.8)
    
    elif operation_type.lower() == "cpu":
        # For CPU-bound operations, use fewer threads
        # Typically CPU count + 1 is optimal
        base_count = cpu_count + 1
        
        # Adjust based on CPU usage
        cpu_usage = metrics.get('avg_cpu_usage', 0)
        if cpu_usage > 80:
            # High CPU usage, decrease threads to reduce contention
            base_count = max(2, int(base_count * 0.8))
        elif cpu_usage < 30:
            # Low CPU usage, can add a few more threads
            base_count = int(base_count * 1.2)
    
    else:  # mixed
        # For mixed operations, use a balanced approach
        base_count = cpu_count * 2
        
        # Adjust based on both CPU and I/O metrics
        cpu_usage = metrics.get('avg_cpu_usage', 0)
        io_wait = metrics.get('avg_io_wait', 0)
        
        # Calculate a balance factor (higher means more I/O bound)
        if io_wait is not None and cpu_usage > 0:
            io_factor = io_wait / (io_wait + cpu_usage)
            # Adjust thread count based on I/O factor
            if io_factor > 0.7:
                # More I/O bound, increase threads
                base_count = int(base_count * 1.3)
            elif io_factor < 0.3:
                # More CPU bound, decrease threads
                base_count = int(base_count * 0.8)
    
    # Adjust based on memory usage
    memory_usage = metrics.get('avg_memory_usage', 0)
    if memory_usage > 85:
        # High memory usage, decrease threads to reduce memory pressure
        base_count = max(2, int(base_count * 0.7))
    
    # Adjust based on thread utilization
    utilization = metrics.get('thread_utilization', 0)
    if utilization > 0.9:
        # High utilization, increase threads
        base_count = int(base_count * 1.2)
    elif utilization < 0.5:
        # Low utilization, decrease threads
        base_count = max(2, int(base_count * 0.8))
    
    # Ensure a reasonable minimum and maximum
    min_threads = 2
    max_threads = cpu_count * 10  # Set an upper limit to prevent excessive threading
    
    return max(min_threads, min(base_count, max_threads))


class AdaptiveThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """
    A thread pool executor that adapts its size based on workload characteristics.
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        thread_name_prefix: str = "",
        initializer: Optional[Callable] = None,
        initargs: Tuple = (),
        operation_type: str = "mixed",
        adaptation_interval: float = 60.0,
        min_workers: Optional[int] = None,
        max_workers_limit: Optional[int] = None
    ):
        """
        Initialize an adaptive thread pool executor.
        
        Args:
            max_workers: Initial maximum worker threads
            thread_name_prefix: Prefix for thread names
            initializer: Callable to initialize worker threads
            initargs: Arguments for initializer
            operation_type: Type of operation ("io", "cpu", or "mixed")
            adaptation_interval: Interval for adapting thread count in seconds
            min_workers: Minimum number of worker threads
            max_workers_limit: Maximum limit for worker threads
        """
        # Calculate initial max_workers if not specified
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            if operation_type.lower() == "io":
                max_workers = cpu_count * 4
            elif operation_type.lower() == "cpu":
                max_workers = cpu_count + 1
            else:  # mixed
                max_workers = cpu_count * 2
        
        # Initialize parent class
        super().__init__(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=initializer,
            initargs=initargs
        )
        
        # Store additional parameters
        self.operation_type = operation_type
        self.adaptation_interval = adaptation_interval
        self.min_workers = min_workers or 2
        self.max_workers_limit = max_workers_limit or (multiprocessing.cpu_count() * 10)
        
        # Initialize adaptation state
        self.last_adaptation = time.time()
        self._lock = threading.Lock()
        
        # Start adaptation thread
        self._stop_event = threading.Event()
        self._adaptation_thread = threading.Thread(target=self._adaptation_loop)
        self._adaptation_thread.daemon = True
        self._adaptation_thread.start()
        
        logger.info(f"Created adaptive thread pool executor with initial max_workers={max_workers}")
    
    def _adaptation_loop(self):
        """Background thread for adapting thread pool size."""
        while not self._stop_event.is_set():
            try:
                # Sleep for a while
                time.sleep(self.adaptation_interval)
                
                # Check if adaptation is needed
                now = time.time()
                if now - self.last_adaptation >= self.adaptation_interval:
                    self._adapt_thread_pool()
                    self.last_adaptation = now
            
            except Exception as e:
                logger.error(f"Error in thread pool adaptation: {e}")
    
    def _adapt_thread_pool(self):
        """Adapt thread pool size based on current metrics."""
        try:
            # Get current metrics
            metrics = get_thread_metrics()
            
            # Calculate optimal thread count
            optimal_count = calculate_optimal_thread_count(
                operation_type=self.operation_type,
                metrics=metrics
            )
            
            # Apply min/max constraints
            optimal_count = max(self.min_workers, min(optimal_count, self.max_workers_limit))
            
            # Update max_workers if different
            with self._lock:
                current_max = self._max_workers
                if optimal_count != current_max:
                    # ThreadPoolExecutor doesn't support changing max_workers directly
                    # We need to use a private attribute, which is not ideal but necessary
                    self._max_workers = optimal_count
                    logger.info(f"Adapted thread pool size from {current_max} to {optimal_count} workers")
        
        except Exception as e:
            logger.error(f"Error adapting thread pool: {e}")
    
    def shutdown(self, wait=True, cancel_futures=False):
        """
        Shutdown the executor.
        
        Args:
            wait: Whether to wait for pending futures to complete
            cancel_futures: Whether to cancel pending futures
        """
        # Stop adaptation thread
        self._stop_event.set()
        if self._adaptation_thread.is_alive():
            self._adaptation_thread.join(timeout=1.0)
        
        # Call parent shutdown
        super().shutdown(wait=wait, cancel_futures=cancel_futures)


def create_optimized_thread_pool(
    config: Dict[str, Any],
    operation_type: str = "mixed",
    thread_name_prefix: Optional[str] = None
) -> concurrent.futures.ThreadPoolExecutor:
    """
    Create an optimized thread pool executor based on configuration and workload.
    
    Args:
        config: Configuration dictionary
        operation_type: Type of operation ("io", "cpu", or "mixed")
        thread_name_prefix: Prefix for thread names
        
    Returns:
        ThreadPoolExecutor instance
    """
    # Get configuration settings
    adaptive_pool = config.get("scan_settings", {}).get("adaptive_thread_pool", True)
    min_workers = config.get("scan_settings", {}).get("min_workers")
    max_workers = config.get("scan_settings", {}).get("max_workers")
    max_workers_limit = config.get("scan_settings", {}).get("max_workers_limit")
    adaptation_interval = config.get("scan_settings", {}).get("adaptation_interval", 60.0)
    
    # Create executor based on configuration
    if adaptive_pool:
        executor = AdaptiveThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix or f"{operation_type}-",
            operation_type=operation_type,
            adaptation_interval=adaptation_interval,
            min_workers=min_workers,
            max_workers_limit=max_workers_limit
        )
    else:
        # Calculate optimal thread count if max_workers not specified
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            if operation_type.lower() == "io":
                max_workers = cpu_count * 4
            elif operation_type.lower() == "cpu":
                max_workers = cpu_count + 1
            else:  # mixed
                max_workers = cpu_count * 2
        
        # Create standard thread pool executor
        executor_kwargs = {"max_workers": max_workers}
        if thread_name_prefix:
            executor_kwargs["thread_name_prefix"] = thread_name_prefix
        
        executor = concurrent.futures.ThreadPoolExecutor(**executor_kwargs)
    
    return executor


# Decorator for tracking thread metrics
def track_thread_metrics(func):
    """
    Decorator for tracking thread metrics for a function.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        # Mark thread as active
        update_thread_metrics(active_delta=1)
        
        # Execute function and track duration
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            # Mark thread as inactive and record duration
            duration = time.time() - start_time
            update_thread_metrics(active_delta=-1, task_duration=duration)
    
    return wrapper