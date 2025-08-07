"""
Asynchronous Processing Module

This module provides utilities for asynchronous processing using asyncio,
including task management, work stealing, and priority queues.
"""

import asyncio
import time
import heapq
import random
import os
import multiprocessing
from typing import Dict, Any, Optional, Union, Callable, List, Tuple, TypeVar, Generic, Set, Coroutine
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import threading
import logging

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Type variables for generic typing
T = TypeVar('T')  # Task type
R = TypeVar('R')  # Result type

class PriorityQueue(Generic[T]):
    """
    A priority queue implementation for task scheduling.
    
    Tasks with lower priority values are processed first.
    """
    
    def __init__(self):
        """Initialize an empty priority queue."""
        self._queue = []
        self._counter = 0  # For tie-breaking when priorities are equal
        self._lock = threading.Lock()
    
    def push(self, item: T, priority: int = 0) -> None:
        """
        Add an item to the priority queue.
        
        Args:
            item: The item to add
            priority: Priority value (lower values = higher priority)
        """
        with self._lock:
            # Use counter as tie-breaker to maintain FIFO order for same priority
            heapq.heappush(self._queue, (priority, self._counter, item))
            self._counter += 1
    
    def pop(self) -> Optional[Tuple[int, T]]:
        """
        Remove and return the highest priority item.
        
        Returns:
            Tuple of (priority, item) or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            priority, _, item = heapq.heappop(self._queue)
            return (priority, item)
    
    def peek(self) -> Optional[Tuple[int, T]]:
        """
        Return the highest priority item without removing it.
        
        Returns:
            Tuple of (priority, item) or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            priority, _, item = self._queue[0]
            return (priority, item)
    
    def __len__(self) -> int:
        """Return the number of items in the queue."""
        with self._lock:
            return len(self._queue)
    
    def __bool__(self) -> bool:
        """Return True if the queue is not empty."""
        with self._lock:
            return bool(self._queue)


class WorkStealingTaskPool:
    """
    A work-stealing task pool for balanced workload distribution.
    
    This implementation uses multiple queues (one per worker) and allows
    workers to steal tasks from other queues when their own queue is empty.
    """
    
    def __init__(self, num_workers: int = None):
        """
        Initialize a work-stealing task pool.
        
        Args:
            num_workers: Number of workers (defaults to CPU count)
        """
        if num_workers is None:
            num_workers = max(1, multiprocessing.cpu_count())
        
        self.num_workers = num_workers
        self.queues = [PriorityQueue() for _ in range(num_workers)]
        self.tasks_completed = 0
        self.tasks_stolen = 0
        self._lock = threading.Lock()
    
    def add_task(self, task: T, priority: int = 0, worker_id: Optional[int] = None) -> None:
        """
        Add a task to the pool.
        
        Args:
            task: The task to add
            priority: Priority value (lower values = higher priority)
            worker_id: Specific worker queue to add to (random if None)
        """
        if worker_id is None:
            # Distribute tasks randomly for load balancing
            worker_id = random.randrange(self.num_workers)
        else:
            # Ensure worker_id is valid
            worker_id = worker_id % self.num_workers
        
        self.queues[worker_id].push(task, priority)
    
    def get_task(self, worker_id: int) -> Optional[Tuple[int, T]]:
        """
        Get a task for the specified worker, stealing if necessary.
        
        Args:
            worker_id: ID of the worker requesting a task
            
        Returns:
            Tuple of (priority, task) or None if no tasks available
        """
        # First try the worker's own queue
        task = self.queues[worker_id].pop()
        if task is not None:
            return task
        
        # If no tasks in own queue, try to steal from other queues
        other_workers = list(range(self.num_workers))
        other_workers.remove(worker_id)
        random.shuffle(other_workers)  # Randomize stealing order
        
        for other_id in other_workers:
            task = self.queues[other_id].pop()
            if task is not None:
                with self._lock:
                    self.tasks_stolen += 1
                return task
        
        # No tasks available
        return None
    
    def mark_task_completed(self) -> None:
        """Mark a task as completed for statistics."""
        with self._lock:
            self.tasks_completed += 1
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the task pool.
        
        Returns:
            Dictionary with task statistics
        """
        with self._lock:
            return {
                "tasks_completed": self.tasks_completed,
                "tasks_stolen": self.tasks_stolen,
                "queued_tasks": sum(len(q) for q in self.queues)
            }


class AsyncTaskManager:
    """
    Manager for asynchronous tasks with support for prioritization and work stealing.
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        max_tasks_per_worker: int = 10,
        use_work_stealing: bool = True
    ):
        """
        Initialize the async task manager.
        
        Args:
            max_workers: Maximum number of worker tasks (defaults to CPU count * 2)
            max_tasks_per_worker: Maximum tasks per worker
            use_work_stealing: Whether to use work stealing for load balancing
        """
        if max_workers is None:
            # For async I/O tasks, we can use more workers than CPU count
            max_workers = multiprocessing.cpu_count() * 2
        
        self.max_workers = max_workers
        self.max_tasks_per_worker = max_tasks_per_worker
        self.use_work_stealing = use_work_stealing
        
        # Create task pool
        if use_work_stealing:
            self.task_pool = WorkStealingTaskPool(max_workers)
        else:
            self.task_pool = PriorityQueue()
        
        # Track active tasks
        self.active_tasks: Set[asyncio.Task] = set()
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0
        }
    
    async def submit(
        self,
        coro: Coroutine,
        priority: int = 0,
        worker_id: Optional[int] = None
    ) -> asyncio.Task:
        """
        Submit a coroutine for execution.
        
        Args:
            coro: Coroutine to execute
            priority: Priority value (lower values = higher priority)
            worker_id: Specific worker to assign to (if using work stealing)
            
        Returns:
            asyncio.Task representing the submitted coroutine
        """
        # Create task
        task = asyncio.create_task(coro)
        
        # Add to active tasks set
        with self._lock:
            self.active_tasks.add(task)
            self.stats["tasks_submitted"] += 1
        
        # Add completion callback
        task.add_done_callback(self._task_done_callback)
        
        # Add to task pool if using work stealing
        if self.use_work_stealing:
            self.task_pool.add_task(task, priority, worker_id)
        
        return task
    
    def _task_done_callback(self, task: asyncio.Task) -> None:
        """
        Callback for when a task is completed.
        
        Args:
            task: The completed task
        """
        with self._lock:
            # Remove from active tasks
            self.active_tasks.discard(task)
            
            # Update statistics
            if task.exception() is None:
                self.stats["tasks_completed"] += 1
                if self.use_work_stealing:
                    self.task_pool.mark_task_completed()
            else:
                self.stats["tasks_failed"] += 1
                logger.error(f"Task failed with exception: {task.exception()}")
    
    async def gather_with_concurrency(
        self,
        coros: List[Coroutine],
        limit: Optional[int] = None,
        return_exceptions: bool = False
    ) -> List[Any]:
        """
        Run coroutines with a concurrency limit.
        
        Args:
            coros: List of coroutines to execute
            limit: Maximum number of concurrent coroutines (defaults to max_workers)
            return_exceptions: Whether to return exceptions or raise them
            
        Returns:
            List of results from the coroutines
        """
        if limit is None:
            limit = self.max_workers
        
        semaphore = asyncio.Semaphore(limit)
        
        async def _wrapped_coro(coro):
            async with semaphore:
                return await coro
        
        return await asyncio.gather(
            *[_wrapped_coro(coro) for coro in coros],
            return_exceptions=return_exceptions
        )
    
    async def map(
        self,
        func: Callable[[T], Coroutine],
        items: List[T],
        limit: Optional[int] = None,
        return_exceptions: bool = False,
        priority_func: Optional[Callable[[T], int]] = None
    ) -> List[Any]:
        """
        Apply a coroutine function to each item with a concurrency limit.
        
        Args:
            func: Coroutine function to apply
            items: List of items to process
            limit: Maximum number of concurrent coroutines (defaults to max_workers)
            return_exceptions: Whether to return exceptions or raise them
            priority_func: Function to determine priority for each item
            
        Returns:
            List of results from the coroutines
        """
        if limit is None:
            limit = self.max_workers
        
        # Create tasks with priorities if specified
        tasks = []
        for i, item in enumerate(items):
            priority = priority_func(item) if priority_func else 0
            worker_id = i % self.max_workers if self.use_work_stealing else None
            task = await self.submit(func(item), priority=priority, worker_id=worker_id)
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the task manager.
        
        Returns:
            Dictionary with task statistics
        """
        with self._lock:
            stats = self.stats.copy()
            stats["active_tasks"] = len(self.active_tasks)
            
            if self.use_work_stealing and isinstance(self.task_pool, WorkStealingTaskPool):
                stats.update(self.task_pool.get_stats())
            
            return stats


async def process_batch_async(
    items: List[T],
    process_func: Callable[[T], Coroutine[Any, Any, R]],
    max_workers: Optional[int] = None,
    use_work_stealing: bool = True,
    priority_func: Optional[Callable[[T], int]] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[R]:
    """
    Process a batch of items asynchronously.
    
    Args:
        items: List of items to process
        process_func: Async function to process each item
        max_workers: Maximum number of concurrent workers
        use_work_stealing: Whether to use work stealing for load balancing
        priority_func: Function to determine priority for each item
        progress_callback: Callback function for progress updates
        
    Returns:
        List of results from processing each item
    """
    # Create task manager
    task_manager = AsyncTaskManager(max_workers=max_workers, use_work_stealing=use_work_stealing)
    
    # Track progress
    processed = 0
    total = len(items)
    
    async def _process_with_progress(item: T) -> R:
        nonlocal processed
        try:
            result = await process_func(item)
            return result
        finally:
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
    
    # Process items
    results = await task_manager.map(
        _process_with_progress,
        items,
        priority_func=priority_func,
        return_exceptions=False
    )
    
    # Log statistics
    stats = task_manager.get_stats()
    logger.info(f"Async batch processing completed: {stats}")
    
    return results


async def run_with_timeout(coro: Coroutine, timeout: float) -> Any:
    """
    Run a coroutine with a timeout.
    
    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        
    Returns:
        Result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If the coroutine times out
    """
    return await asyncio.wait_for(coro, timeout=timeout)


def run_async_in_thread(coro: Coroutine, timeout: Optional[float] = None) -> Any:
    """
    Run an async coroutine in a separate thread from synchronous code.
    
    Args:
        coro: Coroutine to run
        timeout: Optional timeout in seconds
        
    Returns:
        Result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If the coroutine times out
        concurrent.futures.TimeoutError: If the thread times out
    """
    def _run_coro(coro, timeout):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if timeout:
                return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
            else:
                return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_coro, coro, timeout)
        return future.result()


def create_async_executor(
    config: Dict[str, Any],
    max_workers: Optional[int] = None,
    use_work_stealing: bool = True
) -> AsyncTaskManager:
    """
    Create an async task manager with configuration.
    
    Args:
        config: Configuration dictionary
        max_workers: Maximum number of workers (overrides config)
        use_work_stealing: Whether to use work stealing (overrides config)
        
    Returns:
        Configured AsyncTaskManager instance
    """
    # Get settings from config
    if max_workers is None:
        max_workers = config.get("scan_settings", {}).get("max_async_workers")
    
    if use_work_stealing is True:
        use_work_stealing = config.get("scan_settings", {}).get("use_work_stealing", True)
    
    max_tasks_per_worker = config.get("scan_settings", {}).get("max_tasks_per_worker", 10)
    
    # Create task manager
    task_manager = AsyncTaskManager(
        max_workers=max_workers,
        max_tasks_per_worker=max_tasks_per_worker,
        use_work_stealing=use_work_stealing
    )
    
    return task_manager