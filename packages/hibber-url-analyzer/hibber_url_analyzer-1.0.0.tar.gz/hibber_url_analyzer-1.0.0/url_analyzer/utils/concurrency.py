"""
Concurrency Utilities Module

This module provides utilities for concurrent operations, including
thread pool management, backoff strategies, and rate limiting.
"""

import os
import multiprocessing
import time
import threading
import asyncio
from typing import Dict, Any, Optional, Union, Callable, TypeVar, Generic, List, Tuple, Coroutine

# Import logging
from url_analyzer.utils.logging import get_logger

# Import specialized modules
from url_analyzer.utils.async_processing import create_async_executor, process_batch_async
from url_analyzer.utils.distributed import create_distributed_executor, process_batch_distributed
from url_analyzer.utils.thread_pool import create_optimized_thread_pool

# Create logger
logger = get_logger(__name__)

# Global variables for tracking thread activity
_thread_activity = {
    'active_threads': 0,
    'total_threads': 0,
    'last_update': 0,
    'lock': threading.Lock()
}

def track_thread_activity(active=True):
    """
    Track thread activity for adaptive thread pool sizing.
    
    Args:
        active: Whether the thread is becoming active (True) or inactive (False)
    """
    global _thread_activity
    
    with _thread_activity['lock']:
        if active:
            _thread_activity['active_threads'] += 1
        else:
            _thread_activity['active_threads'] = max(0, _thread_activity['active_threads'] - 1)
        
        _thread_activity['last_update'] = time.time()

def get_thread_activity_metrics() -> Tuple[float, int, int]:
    """
    Get metrics about thread activity for adaptive thread pool sizing.
    
    Returns:
        Tuple of (activity_ratio, active_threads, total_threads)
    """
    global _thread_activity
    
    with _thread_activity['lock']:
        active_threads = _thread_activity['active_threads']
        total_threads = threading.active_count()
        _thread_activity['total_threads'] = total_threads
        
        # Calculate activity ratio (active threads / total threads)
        activity_ratio = active_threads / max(1, total_threads)
        
        return (activity_ratio, active_threads, total_threads)


def get_adaptive_thread_pool_size(
    config: Dict[str, Any],
    operation_type: str = "io",
    default_size: int = 20
) -> int:
    """
    Calculate the optimal thread pool size based on configuration and system resources.
    
    Args:
        config: Configuration dictionary
        operation_type: Type of operation ("io" or "cpu")
        default_size: Default thread pool size if not specified in config
        
    Returns:
        Optimal thread pool size
    """
    # Get thread pool settings from config
    thread_pool_type = config.get("scan_settings", {}).get("thread_pool_type", "fixed")
    max_workers = config.get("scan_settings", {}).get("max_workers", default_size)
    min_workers = config.get("scan_settings", {}).get("min_workers", 5)
    max_workers_per_cpu = config.get("scan_settings", {}).get("max_workers_per_cpu", 5)
    dynamic_adjustment = config.get("scan_settings", {}).get("dynamic_adjustment", False)
    
    # If using fixed thread pool, just return max_workers
    if thread_pool_type.lower() != "adaptive":
        return max_workers
    
    # Get number of CPU cores
    cpu_count = multiprocessing.cpu_count()
    
    # Calculate base optimal thread pool size based on operation type
    if operation_type.lower() == "io":
        # For I/O-bound operations, use more threads
        optimal_size = cpu_count * max_workers_per_cpu
    else:
        # For CPU-bound operations, use fewer threads (typically cpu_count + 1)
        optimal_size = cpu_count + 1
    
    # Apply dynamic adjustment based on thread activity if enabled
    if dynamic_adjustment:
        try:
            activity_ratio, active_threads, total_threads = get_thread_activity_metrics()
            
            # Adjust thread count based on thread activity
            # If activity ratio is high, increase thread count
            # If activity ratio is low, decrease thread count
            load_factor = 1.0
            
            if operation_type.lower() == "io":
                # For I/O operations, we can use more threads when activity is high
                # This assumes I/O operations spend a lot of time waiting
                if activity_ratio > 0.8:
                    # High activity, increase threads
                    load_factor = 1.2
                elif activity_ratio < 0.3:
                    # Low activity, decrease threads
                    load_factor = 0.8
            else:
                # For CPU operations, we want fewer threads when activity is high
                # This prevents CPU contention
                if activity_ratio > 0.8:
                    # High activity, decrease threads
                    load_factor = 0.7
                elif activity_ratio < 0.3:
                    # Low activity, can use more threads
                    load_factor = 1.1
            
            # Ensure load_factor is between 0.5 and 1.5
            load_factor = max(0.5, min(1.5, load_factor))
            
            # Apply load factor to optimal size
            adjusted_size = int(optimal_size * load_factor)
            
            logger.debug(f"Thread activity: ratio={activity_ratio:.2f}, active={active_threads}, total={total_threads}")
            logger.debug(f"Load factor: {load_factor:.2f}, Adjusted size: {adjusted_size} (from {optimal_size})")
            
            optimal_size = adjusted_size
        except Exception as e:
            logger.warning(f"Error in dynamic thread pool adjustment: {e}")
    
    # Clamp to min/max values
    optimal_size = max(min_workers, min(optimal_size, max_workers))
    
    logger.debug(f"Adaptive thread pool size for {operation_type} operations: {optimal_size} (CPU count: {cpu_count})")
    return optimal_size


def create_thread_pool_executor(
    config: Dict[str, Any],
    operation_type: str = "io",
    default_size: int = 20,
    thread_name_prefix: Optional[str] = None
) -> 'concurrent.futures.ThreadPoolExecutor':
    """
    Create a thread pool executor with optimal settings.
    
    Args:
        config: Configuration dictionary
        operation_type: Type of operation ("io", "cpu", or "mixed")
        default_size: Default thread pool size if not specified in config
        thread_name_prefix: Prefix for thread names (for debugging)
        
    Returns:
        ThreadPoolExecutor instance
    """
    import concurrent.futures
    
    # Check if we should use the optimized thread pool
    use_optimized = config.get("scan_settings", {}).get("use_optimized_thread_pool", True)
    
    if use_optimized:
        # Use the optimized thread pool implementation
        executor = create_optimized_thread_pool(
            config=config,
            operation_type=operation_type,
            thread_name_prefix=thread_name_prefix
        )
        
        # Log creation
        logger.debug(f"Created optimized thread pool executor for {operation_type} operations" + 
                     (f" with prefix '{thread_name_prefix}'" if thread_name_prefix else ""))
    else:
        # Use the legacy implementation for backward compatibility
        # Get optimal thread pool size
        max_workers = get_adaptive_thread_pool_size(config, operation_type, default_size)
        
        # Create thread pool executor with optional thread naming
        executor_kwargs = {"max_workers": max_workers}
        if thread_name_prefix:
            executor_kwargs["thread_name_prefix"] = thread_name_prefix
        
        executor = concurrent.futures.ThreadPoolExecutor(**executor_kwargs)
        
        # Log creation
        logger.debug(f"Created thread pool executor with {max_workers} workers" + 
                     (f" and prefix '{thread_name_prefix}'" if thread_name_prefix else ""))
    
    return executor


def create_process_pool_executor(
    config: Dict[str, Any],
    default_size: Optional[int] = None
) -> 'concurrent.futures.ProcessPoolExecutor':
    """
    Create a process pool executor for CPU-bound tasks.
    
    Args:
        config: Configuration dictionary
        default_size: Default process pool size (defaults to CPU count)
        
    Returns:
        ProcessPoolExecutor instance
    """
    import concurrent.futures
    
    # Get CPU count if default_size not specified
    if default_size is None:
        default_size = multiprocessing.cpu_count()
    
    # Get process pool settings from config
    max_processes = config.get("scan_settings", {}).get("max_processes", default_size)
    
    # Create process pool executor
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_processes)
    
    logger.debug(f"Created process pool executor with {max_processes} workers")
    return executor