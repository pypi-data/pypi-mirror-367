"""
Optimized Concurrency Module

This module provides optimized concurrent processing utilities that dynamically
adjust thread pool sizes based on system resources, workload characteristics,
and performance metrics.
"""

import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from contextlib import contextmanager

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WorkloadProfile:
    """Profile of a workload for optimization decisions."""
    task_count: int
    estimated_task_duration: float
    is_io_bound: bool = True
    is_cpu_bound: bool = False
    memory_per_task: Optional[float] = None
    requires_rate_limiting: bool = False


@dataclass
class ConcurrencyMetrics:
    """Metrics for monitoring concurrent execution performance."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    average_task_time: float = 0.0
    peak_memory_usage: float = 0.0
    thread_pool_efficiency: float = 0.0


class OptimizedThreadPoolExecutor:
    """
    An optimized ThreadPoolExecutor that dynamically adjusts worker count
    based on system resources and workload characteristics.
    """
    
    def __init__(
        self,
        workload_profile: Optional[WorkloadProfile] = None,
        min_workers: int = 1,
        max_workers: Optional[int] = None,
        adaptive: bool = True,
        monitor_performance: bool = True
    ):
        """
        Initialize the optimized thread pool executor.
        
        Args:
            workload_profile: Profile of the expected workload
            min_workers: Minimum number of worker threads
            max_workers: Maximum number of worker threads (auto-calculated if None)
            adaptive: Whether to adapt worker count during execution
            monitor_performance: Whether to collect performance metrics
        """
        self.workload_profile = workload_profile or WorkloadProfile(
            task_count=0, estimated_task_duration=1.0
        )
        self.min_workers = min_workers
        self.max_workers = max_workers or self._calculate_optimal_max_workers()
        self.adaptive = adaptive
        self.monitor_performance = monitor_performance
        
        self.metrics = ConcurrencyMetrics()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._lock = threading.Lock()
        
        logger.debug(
            f"Initialized OptimizedThreadPoolExecutor: "
            f"min_workers={self.min_workers}, max_workers={self.max_workers}, "
            f"adaptive={self.adaptive}"
        )
    
    def _calculate_optimal_max_workers(self) -> int:
        """Calculate optimal maximum worker count based on system resources."""
        cpu_count = os.cpu_count() or 1
        
        if self.workload_profile.is_io_bound:
            # For I/O-bound tasks, we can use more threads than CPU cores
            # Formula: min(32, cpu_count * 4) for I/O-bound tasks
            optimal = min(32, cpu_count * 4)
        elif self.workload_profile.is_cpu_bound:
            # For CPU-bound tasks, limit to CPU cores + 1
            optimal = cpu_count + 1
        else:
            # Mixed workload: balance between I/O and CPU considerations
            optimal = min(20, cpu_count * 2)
        
        # Adjust based on task count if known
        if self.workload_profile.task_count > 0:
            # Don't create more threads than tasks
            optimal = min(optimal, self.workload_profile.task_count)
        
        # Ensure we have at least min_workers
        optimal = max(optimal, self.min_workers)
        
        logger.debug(f"Calculated optimal max_workers: {optimal}")
        return optimal
    
    def _calculate_current_optimal_workers(self, pending_tasks: int) -> int:
        """Calculate optimal worker count for current conditions."""
        if not self.adaptive:
            return self.max_workers
        
        # Base calculation on pending tasks and system load
        cpu_count = os.cpu_count() or 1
        
        if self.workload_profile.is_io_bound:
            # For I/O-bound: scale with pending tasks but respect limits
            optimal = min(
                self.max_workers,
                max(self.min_workers, min(pending_tasks, cpu_count * 2))
            )
        else:
            # For CPU-bound: limit to CPU cores
            optimal = min(self.max_workers, max(self.min_workers, cpu_count))
        
        return optimal
    
    @contextmanager
    def get_executor(self, task_count: Optional[int] = None):
        """
        Get an optimized ThreadPoolExecutor as a context manager.
        
        Args:
            task_count: Number of tasks to be executed (for optimization)
            
        Yields:
            ThreadPoolExecutor: Optimized executor instance
        """
        # Update workload profile if task count provided
        if task_count is not None:
            self.workload_profile.task_count = task_count
        
        # Calculate optimal worker count
        optimal_workers = self._calculate_current_optimal_workers(
            task_count or self.workload_profile.task_count
        )
        
        start_time = time.time()
        
        try:
            with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
                self._executor = executor
                
                if self.monitor_performance:
                    self.metrics.total_tasks = task_count or 0
                
                logger.debug(f"Created ThreadPoolExecutor with {optimal_workers} workers")
                yield executor
                
        finally:
            self._executor = None
            
            if self.monitor_performance:
                self.metrics.total_execution_time = time.time() - start_time
                if self.metrics.total_tasks > 0:
                    self.metrics.average_task_time = (
                        self.metrics.total_execution_time / self.metrics.total_tasks
                    )
    
    def execute_tasks(
        self,
        func: Callable,
        tasks: List[Any],
        timeout: Optional[float] = None,
        return_exceptions: bool = False
    ) -> List[Any]:
        """
        Execute tasks using the optimized thread pool.
        
        Args:
            func: Function to execute for each task
            tasks: List of task arguments
            timeout: Timeout for each task
            return_exceptions: Whether to return exceptions instead of raising
            
        Returns:
            List of results from task execution
        """
        results = []
        
        with self.get_executor(len(tasks)) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(func, task): task for task in tasks
            }
            
            # Collect results
            for future in as_completed(future_to_task, timeout=timeout):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if self.monitor_performance:
                        self.metrics.completed_tasks += 1
                        
                except Exception as e:
                    if self.monitor_performance:
                        self.metrics.failed_tasks += 1
                    
                    if return_exceptions:
                        results.append(e)
                    else:
                        logger.error(f"Task failed: {e}")
                        raise
        
        return results
    
    def get_metrics(self) -> ConcurrencyMetrics:
        """Get performance metrics for the executor."""
        return self.metrics
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = ConcurrencyMetrics()


def create_optimized_executor(
    workload_type: str = "io_bound",
    task_count: Optional[int] = None,
    estimated_duration: float = 1.0,
    **kwargs
) -> OptimizedThreadPoolExecutor:
    """
    Create an optimized thread pool executor for common workload types.
    
    Args:
        workload_type: Type of workload ("io_bound", "cpu_bound", "mixed")
        task_count: Expected number of tasks
        estimated_duration: Estimated duration per task in seconds
        **kwargs: Additional arguments for OptimizedThreadPoolExecutor
        
    Returns:
        OptimizedThreadPoolExecutor: Configured executor
    """
    # Create workload profile based on type
    if workload_type == "io_bound":
        profile = WorkloadProfile(
            task_count=task_count or 0,
            estimated_task_duration=estimated_duration,
            is_io_bound=True,
            is_cpu_bound=False
        )
    elif workload_type == "cpu_bound":
        profile = WorkloadProfile(
            task_count=task_count or 0,
            estimated_task_duration=estimated_duration,
            is_io_bound=False,
            is_cpu_bound=True
        )
    else:  # mixed
        profile = WorkloadProfile(
            task_count=task_count or 0,
            estimated_task_duration=estimated_duration,
            is_io_bound=True,
            is_cpu_bound=True
        )
    
    return OptimizedThreadPoolExecutor(workload_profile=profile, **kwargs)


# Convenience functions for common use cases
def execute_io_bound_tasks(
    func: Callable,
    tasks: List[Any],
    max_workers: Optional[int] = None,
    timeout: Optional[float] = None
) -> List[Any]:
    """
    Execute I/O-bound tasks with optimized concurrency.
    
    Args:
        func: Function to execute for each task
        tasks: List of task arguments
        max_workers: Maximum number of workers (auto-calculated if None)
        timeout: Timeout for task execution
        
    Returns:
        List of results
    """
    executor = create_optimized_executor(
        workload_type="io_bound",
        task_count=len(tasks),
        max_workers=max_workers
    )
    
    return executor.execute_tasks(func, tasks, timeout=timeout)


def execute_cpu_bound_tasks(
    func: Callable,
    tasks: List[Any],
    max_workers: Optional[int] = None,
    timeout: Optional[float] = None
) -> List[Any]:
    """
    Execute CPU-bound tasks with optimized concurrency.
    
    Args:
        func: Function to execute for each task
        tasks: List of task arguments
        max_workers: Maximum number of workers (auto-calculated if None)
        timeout: Timeout for task execution
        
    Returns:
        List of results
    """
    executor = create_optimized_executor(
        workload_type="cpu_bound",
        task_count=len(tasks),
        max_workers=max_workers
    )
    
    return executor.execute_tasks(func, tasks, timeout=timeout)


@contextmanager
def optimized_thread_pool(
    workload_type: str = "io_bound",
    task_count: Optional[int] = None,
    **kwargs
):
    """
    Context manager for optimized thread pool execution.
    
    Args:
        workload_type: Type of workload ("io_bound", "cpu_bound", "mixed")
        task_count: Expected number of tasks
        **kwargs: Additional arguments for OptimizedThreadPoolExecutor
        
    Yields:
        ThreadPoolExecutor: Optimized executor instance
    """
    executor = create_optimized_executor(
        workload_type=workload_type,
        task_count=task_count,
        **kwargs
    )
    
    with executor.get_executor(task_count) as thread_pool:
        yield thread_pool