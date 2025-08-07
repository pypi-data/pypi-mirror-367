"""
Memory Profiler Module

This module provides comprehensive memory profiling functionality to identify
memory leaks and inefficient memory usage patterns. It builds on the existing
memory tracking functionality in the memory_pool module.
"""

import os
import time
import gc
import weakref
import threading
import tracemalloc
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from functools import wraps
from collections import defaultdict

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Import memory tracking utilities
from url_analyzer.utils.memory_pool import get_memory_usage, MemoryTracker

# Optional imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, some memory profiling features will be disabled")

try:
    import objgraph
    OBJGRAPH_AVAILABLE = True
except ImportError:
    OBJGRAPH_AVAILABLE = False
    logger.warning("objgraph not available, object graph visualization will be disabled")


class MemoryProfiler:
    """
    Comprehensive memory profiler for tracking memory usage and identifying leaks.
    
    This class provides functionality for tracking memory usage over time,
    identifying memory leaks, and generating memory usage reports.
    """
    
    def __init__(self, 
                 enabled: bool = True, 
                 sampling_interval: float = 1.0,
                 track_allocations: bool = False,
                 memory_limit_mb: Optional[float] = None,
                 log_level: str = "INFO"):
        """
        Initialize the memory profiler.
        
        Args:
            enabled: Whether the profiler is enabled
            sampling_interval: Interval between memory usage samples (in seconds)
            track_allocations: Whether to track memory allocations using tracemalloc
            memory_limit_mb: Memory usage limit in MB (None for no limit)
            log_level: Log level for memory profiling messages
        """
        self.enabled = enabled
        self.sampling_interval = sampling_interval
        self.track_allocations = track_allocations
        self.memory_limit_mb = memory_limit_mb
        self.log_level = log_level.upper()
        
        # Memory usage history
        self.memory_history: List[Tuple[float, float]] = []
        
        # Memory allocation snapshots (if track_allocations is True)
        self.snapshots: List[Tuple[float, tracemalloc.Snapshot]] = []
        
        # Memory usage by component
        self.component_memory: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        
        # Memory leak detection
        self.object_counts: Dict[str, int] = {}
        
        # Sampling thread
        self._sampling_thread: Optional[threading.Thread] = None
        self._stop_sampling = threading.Event()
        
        # Callbacks for memory limit exceeded
        self._limit_callbacks: List[Callable[[], None]] = []
        
        # Initialize tracemalloc if tracking allocations
        if self.track_allocations:
            if not tracemalloc.is_tracing():
                tracemalloc.start()
                logger.debug("Started tracemalloc for memory allocation tracking")
        
        logger.debug(f"Initialized MemoryProfiler (enabled={enabled}, "
                    f"sampling_interval={sampling_interval}, "
                    f"track_allocations={track_allocations}, "
                    f"memory_limit_mb={memory_limit_mb})")
    
    def start_sampling(self) -> None:
        """
        Start sampling memory usage at regular intervals.
        """
        if not self.enabled:
            logger.debug("Memory profiler is disabled, not starting sampling")
            return
            
        if self._sampling_thread is not None and self._sampling_thread.is_alive():
            logger.warning("Memory sampling already running")
            return
            
        self._stop_sampling.clear()
        self._sampling_thread = threading.Thread(
            target=self._sampling_loop,
            daemon=True,
            name="MemoryProfilerSampling"
        )
        self._sampling_thread.start()
        logger.debug(f"Started memory usage sampling (interval={self.sampling_interval}s)")
    
    def stop_sampling(self) -> None:
        """
        Stop sampling memory usage.
        """
        if self._sampling_thread is None or not self._sampling_thread.is_alive():
            logger.debug("Memory sampling not running")
            return
            
        self._stop_sampling.set()
        self._sampling_thread.join(timeout=2.0)
        if self._sampling_thread.is_alive():
            logger.warning("Memory sampling thread did not stop gracefully")
        else:
            logger.debug("Stopped memory usage sampling")
            
        self._sampling_thread = None
    
    def _sampling_loop(self) -> None:
        """
        Internal method for sampling memory usage at regular intervals.
        """
        while not self._stop_sampling.is_set():
            try:
                # Get current memory usage
                memory_mb = get_memory_usage()
                timestamp = time.time()
                
                # Add to history
                self.memory_history.append((timestamp, memory_mb))
                
                # Check memory limit
                if self.memory_limit_mb is not None and memory_mb > self.memory_limit_mb:
                    self._handle_memory_limit_exceeded(memory_mb)
                
                # Take tracemalloc snapshot if tracking allocations
                if self.track_allocations and tracemalloc.is_tracing():
                    snapshot = tracemalloc.take_snapshot()
                    self.snapshots.append((timestamp, snapshot))
                
                # Log memory usage
                self._log_memory_usage(memory_mb)
                
            except Exception as e:
                logger.error(f"Error in memory sampling: {e}")
            
            # Sleep until next sample
            self._stop_sampling.wait(self.sampling_interval)
    
    def _log_memory_usage(self, memory_mb: float) -> None:
        """
        Log memory usage based on the configured log level.
        
        Args:
            memory_mb: Current memory usage in MB
        """
        message = f"Memory usage: {memory_mb:.2f} MB"
        
        if self.log_level == "DEBUG":
            logger.debug(message)
        elif self.log_level == "INFO":
            logger.info(message)
        elif self.log_level == "WARNING" and self.memory_limit_mb is not None:
            # Only log as warning if approaching the limit
            if memory_mb > self.memory_limit_mb * 0.8:
                logger.warning(f"{message} (approaching limit of {self.memory_limit_mb:.2f} MB)")
    
    def _handle_memory_limit_exceeded(self, current_memory_mb: float) -> None:
        """
        Handle the case where memory usage exceeds the configured limit.
        
        Args:
            current_memory_mb: Current memory usage in MB
        """
        logger.warning(
            f"Memory usage ({current_memory_mb:.2f} MB) exceeds limit ({self.memory_limit_mb:.2f} MB)"
        )
        
        # Run callbacks
        for callback in self._limit_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in memory limit callback: {e}")
        
        # Force garbage collection
        gc.collect()
        
        # Log top memory consumers if objgraph is available
        if OBJGRAPH_AVAILABLE:
            logger.info("Top 10 memory consumers:")
            for obj_type, count in objgraph.most_common_types(10):
                logger.info(f"  {obj_type}: {count} objects")
    
    def register_limit_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback to be called when memory usage exceeds the limit.
        
        Args:
            callback: Function to call when memory limit is exceeded
        """
        self._limit_callbacks.append(callback)
        logger.debug(f"Registered memory limit callback: {callback.__name__}")
    
    def track_component_memory(self, component_name: str) -> MemoryTracker:
        """
        Create a memory tracker for a specific component.
        
        Args:
            component_name: Name of the component to track
            
        Returns:
            MemoryTracker context manager
        """
        class ComponentMemoryTracker(MemoryTracker):
            def __init__(self, profiler, component):
                super().__init__(f"Memory usage for {component}")
                self.profiler = profiler
                self.component = component
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                super().__exit__(exc_type, exc_val, exc_tb)
                # Add to component memory history
                memory_diff = self.end_memory - self.start_memory
                self.profiler.component_memory[self.component].append(
                    (time.time(), memory_diff)
                )
        
        return ComponentMemoryTracker(self, component_name)
    
    def take_snapshot(self, label: str = "") -> None:
        """
        Take a memory allocation snapshot using tracemalloc.
        
        Args:
            label: Label for the snapshot
        """
        if not self.enabled:
            logger.debug("Memory profiler is disabled, not taking snapshot")
            return
            
        if not self.track_allocations:
            logger.warning("Memory allocation tracking is disabled, cannot take snapshot")
            return
            
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            logger.debug("Started tracemalloc for memory allocation tracking")
        
        timestamp = time.time()
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((timestamp, snapshot))
        logger.debug(f"Took memory allocation snapshot: {label}")
    
    def compare_snapshots(self, 
                          start_index: int = -2, 
                          end_index: int = -1, 
                          top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Compare two memory allocation snapshots to identify potential leaks.
        
        Args:
            start_index: Index of the start snapshot in the snapshots list
            end_index: Index of the end snapshot in the snapshots list
            top_n: Number of top memory consumers to return
            
        Returns:
            List of dictionaries with memory allocation statistics
        """
        if not self.enabled:
            logger.debug("Memory profiler is disabled, not comparing snapshots")
            return []
            
        if not self.track_allocations:
            logger.warning("Memory allocation tracking is disabled, cannot compare snapshots")
            return []
            
        if len(self.snapshots) < 2:
            logger.warning("Not enough snapshots to compare")
            return []
            
        try:
            start_time, start_snapshot = self.snapshots[start_index]
            end_time, end_snapshot = self.snapshots[end_index]
            
            # Compare snapshots
            top_stats = start_snapshot.compare_to(end_snapshot, 'lineno')
            
            # Format results
            results = []
            for stat in top_stats[:top_n]:
                results.append({
                    "file": stat.traceback[0].filename,
                    "line": stat.traceback[0].lineno,
                    "size_diff": stat.size_diff,
                    "count_diff": stat.count_diff,
                    "size": stat.size,
                    "count": stat.count
                })
            
            # Log results
            logger.info(f"Memory allocation comparison ({start_index} -> {end_index}):")
            for i, stat in enumerate(results):
                logger.info(f"  {i+1}. {stat['file']}:{stat['line']} - "
                           f"{stat['size_diff']/1024:.1f} KB ({stat['count_diff']} objects)")
            
            return results
            
        except Exception as e:
            logger.error(f"Error comparing snapshots: {e}")
            return []
    
    def detect_leaks(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect potential memory leaks by comparing object counts.
        
        Args:
            object_type: Specific object type to check (None for all types)
            
        Returns:
            Dictionary with leak detection results
        """
        if not self.enabled:
            logger.debug("Memory profiler is disabled, not detecting leaks")
            return {}
            
        if not OBJGRAPH_AVAILABLE:
            logger.warning("objgraph not available, cannot detect leaks")
            return {}
            
        # Force garbage collection
        gc.collect()
        
        # Get current object counts
        current_counts = {}
        for obj_type, count in objgraph.most_common_types(50):
            current_counts[obj_type] = count
        
        # Compare with previous counts
        if not self.object_counts:
            # First run, just store the counts
            self.object_counts = current_counts
            return {}
            
        # Find differences
        results = {}
        for obj_type, count in current_counts.items():
            if object_type is not None and obj_type != object_type:
                continue
                
            prev_count = self.object_counts.get(obj_type, 0)
            diff = count - prev_count
            
            if diff > 0:
                results[obj_type] = {
                    "previous_count": prev_count,
                    "current_count": count,
                    "difference": diff
                }
        
        # Update stored counts
        self.object_counts = current_counts
        
        # Log results
        if results:
            logger.warning("Potential memory leaks detected:")
            for obj_type, data in sorted(results.items(), key=lambda x: x[1]["difference"], reverse=True):
                logger.warning(f"  {obj_type}: {data['previous_count']} -> {data['current_count']} "
                              f"(+{data['difference']} objects)")
        
        return results
    
    def get_memory_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive memory usage report.
        
        Returns:
            Dictionary with memory usage statistics
        """
        if not self.enabled:
            logger.debug("Memory profiler is disabled, not generating report")
            return {}
            
        # Current memory usage
        current_memory = get_memory_usage()
        
        # Memory usage statistics
        memory_stats = {
            "current_memory_mb": current_memory,
            "peak_memory_mb": max([m for _, m in self.memory_history]) if self.memory_history else current_memory,
            "samples_count": len(self.memory_history),
            "tracking_duration_seconds": (self.memory_history[-1][0] - self.memory_history[0][0]) if len(self.memory_history) > 1 else 0
        }
        
        # Add memory limit information
        if self.memory_limit_mb is not None:
            memory_stats["memory_limit_mb"] = self.memory_limit_mb
            memory_stats["memory_usage_percent"] = (current_memory / self.memory_limit_mb) * 100
        
        # Add component memory usage
        component_stats = {}
        for component, history in self.component_memory.items():
            if history:
                component_stats[component] = {
                    "total_memory_diff_mb": sum([m for _, m in history]),
                    "samples_count": len(history)
                }
        
        # Add system memory information if psutil is available
        system_stats = {}
        if PSUTIL_AVAILABLE:
            try:
                virtual_memory = psutil.virtual_memory()
                system_stats = {
                    "total_system_memory_mb": virtual_memory.total / 1024 / 1024,
                    "available_system_memory_mb": virtual_memory.available / 1024 / 1024,
                    "system_memory_percent": virtual_memory.percent
                }
            except Exception as e:
                logger.error(f"Error getting system memory information: {e}")
        
        # Combine all statistics
        report = {
            "memory_stats": memory_stats,
            "component_stats": component_stats,
            "system_stats": system_stats,
            "timestamp": time.time()
        }
        
        # Log summary
        logger.info(f"Memory usage report: {current_memory:.2f} MB current, "
                   f"{memory_stats.get('peak_memory_mb', 0):.2f} MB peak")
        
        return report


# Decorator for memory profiling
def profile_memory(component_name: Optional[str] = None):
    """
    Decorator for profiling memory usage of a function.
    
    Args:
        component_name: Name of the component (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            import importlib
            try:
                memory_management = importlib.import_module('url_analyzer.utils.memory_management')
                profiler = memory_management.get_memory_profiler()
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import memory management module: {e}")
                # Fall back to just calling the function
                return func(*args, **kwargs)
            
            if not profiler.enabled:
                # If profiling is disabled, just call the function
                return func(*args, **kwargs)
            
            # Use function name if component_name is not provided
            comp_name = component_name or func.__name__
            
            # Track memory usage
            with profiler.track_component_memory(comp_name):
                # Take snapshot before if tracking allocations
                if profiler.track_allocations:
                    profiler.take_snapshot(f"{comp_name} - start")
                
                # Call the function
                result = func(*args, **kwargs)
                
                # Take snapshot after if tracking allocations
                if profiler.track_allocations:
                    profiler.take_snapshot(f"{comp_name} - end")
                    # Compare the last two snapshots
                    profiler.compare_snapshots()
                
                return result
                
        return wrapper
    
    return decorator


# Context manager for memory profiling
class ProfileMemoryBlock:
    """
    Context manager for profiling memory usage of a block of code.
    
    Example:
        with ProfileMemoryBlock("my_operation"):
            # Code to profile
            process_data()
    """
    
    def __init__(self, block_name: str):
        """
        Initialize the memory profiling block.
        
        Args:
            block_name: Name of the code block to profile
        """
        self.block_name = block_name
        
    def __enter__(self):
        """Enter the context manager."""
        # Import here to avoid circular imports
        import importlib
        try:
            memory_management = importlib.import_module('url_analyzer.utils.memory_management')
            self.profiler = memory_management.get_memory_profiler()
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not import memory management module: {e}")
            # Create a dummy profiler attribute to avoid errors
            self.profiler = type('DummyProfiler', (), {'enabled': False})
            return self
        
        if not self.profiler.enabled:
            return self
        
        # Start tracking
        self.tracker = self.profiler.track_component_memory(self.block_name)
        self.tracker.__enter__()
        
        # Take snapshot if tracking allocations
        if self.profiler.track_allocations:
            self.profiler.take_snapshot(f"{self.block_name} - start")
            
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        if not self.profiler.enabled:
            return
            
        # Take snapshot if tracking allocations
        if self.profiler.track_allocations:
            self.profiler.take_snapshot(f"{self.block_name} - end")
            # Compare the last two snapshots
            self.profiler.compare_snapshots()
        
        # End tracking
        self.tracker.__exit__(exc_type, exc_val, exc_tb)


# Function to check if an object is a memory leak candidate
def is_leak_candidate(obj: Any) -> bool:
    """
    Check if an object is a potential memory leak candidate.
    
    This function checks various properties of the object to determine
    if it might be a memory leak candidate, such as large collections,
    objects with circular references, etc.
    
    Args:
        obj: Object to check
        
    Returns:
        True if the object is a potential memory leak candidate, False otherwise
    """
    # Check for None
    if obj is None:
        return False
    
    try:
        # Check for large collections
        if isinstance(obj, (list, dict, set, tuple)):
            return len(obj) > 1000
        
        # Check for large strings
        if isinstance(obj, str):
            return len(obj) > 10000
        
        # Check for objects with __dict__
        if hasattr(obj, "__dict__"):
            return len(obj.__dict__) > 50
        
        # Default: not a leak candidate
        return False
    except Exception:
        # If we can't check the object, assume it's not a leak candidate
        return False


# Function to find memory leaks
def find_memory_leaks(top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Find potential memory leaks in the application.
    
    This function uses various techniques to identify potential memory leaks,
    such as tracking object counts, finding objects with circular references,
    and identifying large collections.
    
    Args:
        top_n: Number of top memory leak candidates to return
        
    Returns:
        List of dictionaries with memory leak information
    """
    if not OBJGRAPH_AVAILABLE:
        logger.warning("objgraph not available, cannot find memory leaks")
        return []
    
    # Force garbage collection
    gc.collect()
    
    # Find potential leaks
    leaks = []
    
    # Check for objects with many referrers
    for obj_type, count in objgraph.most_common_types(top_n * 2):
        # Skip built-in types that are unlikely to be leaks
        if obj_type in ("function", "type", "module", "method"):
            continue
            
        # Get some sample objects of this type
        try:
            objects = objgraph.by_type(obj_type)[:5]
            
            for obj in objects:
                # Check if this object is a leak candidate
                if is_leak_candidate(obj):
                    # Get referrers
                    referrers = gc.get_referrers(obj)
                    
                    leaks.append({
                        "type": obj_type,
                        "object": str(obj)[:100],
                        "referrers_count": len(referrers),
                        "size_estimate": _estimate_size(obj)
                    })
        except Exception as e:
            logger.debug(f"Error checking objects of type {obj_type}: {e}")
    
    # Sort by estimated size
    leaks.sort(key=lambda x: x["size_estimate"], reverse=True)
    
    # Log results
    if leaks:
        logger.warning(f"Found {len(leaks)} potential memory leaks:")
        for i, leak in enumerate(leaks[:top_n]):
            logger.warning(f"  {i+1}. {leak['type']}: {leak['object']} - "
                          f"{leak['size_estimate']/1024:.1f} KB, "
                          f"{leak['referrers_count']} referrers")
    
    return leaks[:top_n]


# Helper function to estimate object size
def _estimate_size(obj: Any) -> int:
    """
    Estimate the size of an object in bytes.
    
    Args:
        obj: Object to estimate size for
        
    Returns:
        Estimated size in bytes
    """
    try:
        import sys
        
        # For basic types, use sys.getsizeof
        if isinstance(obj, (int, float, bool, str, bytes)):
            return sys.getsizeof(obj)
        
        # For collections, estimate recursively
        if isinstance(obj, (list, tuple, set)):
            try:
                return sys.getsizeof(obj) + sum(_estimate_size(x) for x in obj)
            except Exception:
                return sys.getsizeof(obj)
        
        if isinstance(obj, dict):
            try:
                return sys.getsizeof(obj) + sum(_estimate_size(k) + _estimate_size(v) for k, v in obj.items())
            except Exception:
                return sys.getsizeof(obj)
        
        # For objects with __dict__, estimate based on attributes
        if hasattr(obj, "__dict__"):
            try:
                return sys.getsizeof(obj) + _estimate_size(obj.__dict__)
            except Exception:
                return sys.getsizeof(obj)
        
        # Default: use sys.getsizeof
        return sys.getsizeof(obj)
    except Exception:
        # If we can't estimate the size, return a default value
        return 1000  # 1 KB default