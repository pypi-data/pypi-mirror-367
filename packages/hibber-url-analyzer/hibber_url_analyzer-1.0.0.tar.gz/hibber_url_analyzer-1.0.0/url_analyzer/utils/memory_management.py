"""
Memory Management Module

This module provides centralized memory management functionality for the URL Analyzer,
including a global memory profiler instance, memory pooling configuration,
and memory optimization utilities.
"""

import os
import gc
import threading
from typing import Dict, Any, Optional, List, Callable

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Import memory pooling and profiling
from url_analyzer.utils.memory_pool import (
    string_pool, pattern_pool, ObjectPool, StringPool, PatternPool, 
    get_memory_usage, MemoryTracker
)
from url_analyzer.utils.memory_profiler import MemoryProfiler

# Global memory profiler instance
_memory_profiler: Optional[MemoryProfiler] = None
_profiler_lock = threading.Lock()

# Global object pools
_object_pools: Dict[str, ObjectPool] = {}
_pools_lock = threading.Lock()

# Default memory limit (in MB)
DEFAULT_MEMORY_LIMIT_MB = 1024  # 1 GB

# Memory optimization level
# 0: Minimal optimization (development mode)
# 1: Standard optimization (default)
# 2: Aggressive optimization (for large datasets)
MEMORY_OPTIMIZATION_LEVEL = 1


def get_memory_profiler() -> MemoryProfiler:
    """
    Get the global memory profiler instance.
    
    Returns:
        Global MemoryProfiler instance
    """
    global _memory_profiler
    
    if _memory_profiler is None:
        with _profiler_lock:
            if _memory_profiler is None:
                # Check if memory profiling is enabled via environment variable
                enabled = os.environ.get('URL_ANALYZER_MEMORY_PROFILING', '1').lower() in ('1', 'true', 'yes')
                
                # Get memory limit from environment variable or use default
                try:
                    memory_limit = float(os.environ.get('URL_ANALYZER_MEMORY_LIMIT_MB', str(DEFAULT_MEMORY_LIMIT_MB)))
                except (ValueError, TypeError):
                    memory_limit = DEFAULT_MEMORY_LIMIT_MB
                    
                # Create memory profiler
                _memory_profiler = MemoryProfiler(
                    enabled=enabled,
                    sampling_interval=5.0,  # Sample every 5 seconds
                    track_allocations=False,  # Disable by default as it has overhead
                    memory_limit_mb=memory_limit,
                    log_level="INFO"
                )
                
                # Register default callbacks for memory limit exceeded
                _memory_profiler.register_limit_callback(force_garbage_collection)
                _memory_profiler.register_limit_callback(clear_caches)
                
                # Start sampling if enabled
                if enabled:
                    _memory_profiler.start_sampling()
                    logger.info(f"Started memory profiler with limit {memory_limit} MB")
    
    return _memory_profiler


def get_object_pool(pool_name: str, factory: Optional[Callable] = None, max_size: int = 1000) -> ObjectPool:
    """
    Get or create an object pool with the given name.
    
    Args:
        pool_name: Name of the pool
        factory: Function to create new objects if not found in the pool
        max_size: Maximum number of objects to keep in the pool
        
    Returns:
        ObjectPool instance
    """
    global _object_pools
    
    if pool_name not in _object_pools:
        with _pools_lock:
            if pool_name not in _object_pools:
                # Adjust max_size based on optimization level
                adjusted_max_size = max_size
                if MEMORY_OPTIMIZATION_LEVEL == 0:
                    adjusted_max_size = max_size // 2  # Smaller pools in development mode
                elif MEMORY_OPTIMIZATION_LEVEL == 2:
                    adjusted_max_size = max_size * 2  # Larger pools in aggressive mode
                
                # Create pool with appropriate eviction policy
                eviction_policy = 'lru'  # Default
                if MEMORY_OPTIMIZATION_LEVEL == 2:
                    # Use LFU for aggressive optimization as it's better for long-running processes
                    eviction_policy = 'lfu'
                
                _object_pools[pool_name] = ObjectPool(
                    factory=factory,
                    max_size=adjusted_max_size,
                    eviction_policy=eviction_policy
                )
                
                logger.debug(f"Created object pool '{pool_name}' with max size {adjusted_max_size}")
    
    return _object_pools[pool_name]


def configure_memory_optimization(level: int) -> None:
    """
    Configure the memory optimization level.
    
    Args:
        level: Optimization level (0: minimal, 1: standard, 2: aggressive)
    """
    global MEMORY_OPTIMIZATION_LEVEL, string_pool, pattern_pool
    
    if level not in (0, 1, 2):
        logger.warning(f"Invalid memory optimization level: {level}, using default (1)")
        level = 1
    
    MEMORY_OPTIMIZATION_LEVEL = level
    
    # Configure string pool based on optimization level
    if level == 0:
        # Minimal optimization (development mode)
        string_pool._max_size = 5000
    elif level == 1:
        # Standard optimization (default)
        string_pool._max_size = 10000
    else:  # level == 2
        # Aggressive optimization (for large datasets)
        string_pool._max_size = 20000
        # Switch to LFU eviction policy for long-running processes
        if string_pool._eviction_policy != 'lfu':
            logger.info("Switching string pool to LFU eviction policy")
            new_pool = StringPool(max_size=20000, eviction_policy='lfu')
            # Copy existing strings to new pool
            for s in string_pool._pool.keys():
                new_pool.intern(s)
            # Assign new pool
            string_pool = new_pool
    
    # Configure pattern pool based on optimization level
    if level == 0:
        pattern_pool._max_size = 500
    elif level == 1:
        pattern_pool._max_size = 1000
    else:  # level == 2
        pattern_pool._max_size = 2000
        # Switch to LFU eviction policy
        if pattern_pool._eviction_policy != 'lfu':
            logger.info("Switching pattern pool to LFU eviction policy")
            new_pool = PatternPool(max_size=2000, eviction_policy='lfu')
            # Copy existing patterns to new pool
            for pattern, flags in pattern_pool._pool.keys():
                new_pool.get_pattern(pattern, flags)
            # Assign new pool
            pattern_pool = new_pool
    
    logger.info(f"Memory optimization level set to {level}")


def force_garbage_collection() -> int:
    """
    Force garbage collection to free memory.
    
    Returns:
        Number of objects collected
    """
    # Disable garbage collection during collection to prevent recursive collection
    gc_enabled = gc.isenabled()
    if gc_enabled:
        gc.disable()
    
    try:
        # Run garbage collection with full generational collection
        collected = gc.collect(2)
        logger.info(f"Forced garbage collection: {collected} objects collected")
        return collected
    finally:
        # Re-enable garbage collection if it was enabled before
        if gc_enabled:
            gc.enable()


def clear_caches() -> None:
    """
    Clear various caches to free memory.
    """
    # Clear object pools
    cleared_count = 0
    with _pools_lock:
        for pool_name, pool in _object_pools.items():
            pool_size = len(pool)
            pool.clear()
            cleared_count += pool_size
    
    logger.info(f"Cleared {cleared_count} objects from object pools")
    
    # Clear other caches
    # This is a hook for other modules to register their cache clearing functions
    for func in _cache_clearing_functions:
        try:
            func()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Registry for cache clearing functions
_cache_clearing_functions: List[Callable[[], None]] = []

def register_cache_clearing_function(func: Callable[[], None]) -> None:
    """
    Register a function to be called when caches need to be cleared.
    
    Args:
        func: Function to call when clearing caches
    """
    _cache_clearing_functions.append(func)
    logger.debug(f"Registered cache clearing function: {func.__name__}")


def optimize_dataframe(df, inplace: bool = False):
    """
    Optimize a pandas DataFrame for memory usage.
    
    This function reduces memory usage by:
    1. Converting numeric columns to the smallest possible dtype
    2. Converting object columns to categorical when appropriate
    3. Using string interning for repetitive string values
    
    Args:
        df: pandas DataFrame to optimize
        inplace: Whether to modify the DataFrame in place
        
    Returns:
        Optimized DataFrame
    """
    import pandas as pd
    import numpy as np
    
    if not inplace:
        df = df.copy()
    
    # Get memory usage before optimization
    start_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
    
    # Process each column
    for col in df.columns:
        col_type = df[col].dtype
        
        # Numeric columns: downcast to the smallest possible type
        if col_type in (np.int64, np.int32, np.int16, np.int8):
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif col_type in (np.float64, np.float32, np.float16):
            df[col] = pd.to_numeric(df[col], downcast='float')
            
        # Object columns: convert to categorical or intern strings
        elif col_type == 'object':
            # Check if column has few unique values relative to total values
            num_unique = df[col].nunique()
            num_total = len(df[col])
            
            # If column has many repeated values, convert to categorical
            if num_unique / num_total < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
            # Otherwise, intern strings to save memory
            elif df[col].map(lambda x: isinstance(x, str)).all():
                df[col] = df[col].map(lambda x: string_pool.intern(x))
    
    # Get memory usage after optimization
    end_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
    reduction = (start_memory - end_memory) / start_memory * 100
    
    logger.info(f"DataFrame memory optimization: {start_memory:.2f} MB -> {end_memory:.2f} MB ({reduction:.1f}% reduction)")
    
    return df


def lazy_import(module_name: str):
    """
    Decorator for lazy importing of modules.
    
    This decorator allows modules to be imported only when they are actually used,
    reducing memory usage during startup.
    
    Args:
        module_name: Name of the module to import lazily
        
    Returns:
        Proxy object that imports the module on first use
    """
    class LazyModule:
        def __init__(self):
            self._module = None
            
        def __getattr__(self, name):
            if self._module is None:
                import importlib
                self._module = importlib.import_module(module_name)
                logger.debug(f"Lazy imported module: {module_name}")
            return getattr(self._module, name)
    
    return LazyModule()


# Initialize memory optimization based on environment variable
try:
    optimization_level = int(os.environ.get('URL_ANALYZER_MEMORY_OPTIMIZATION', '1'))
    configure_memory_optimization(optimization_level)
except (ValueError, TypeError):
    configure_memory_optimization(1)  # Default to standard optimization