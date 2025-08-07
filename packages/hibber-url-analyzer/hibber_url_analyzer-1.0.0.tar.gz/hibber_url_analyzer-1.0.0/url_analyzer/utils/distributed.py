"""
Distributed Processing Module

This module provides utilities for distributed processing across multiple
machines or processes, including task distribution, result collection,
and coordination.
"""

import os
import time
import json
import socket
import pickle
import uuid
import threading
import multiprocessing
from typing import Dict, Any, Optional, Union, Callable, List, Tuple, TypeVar, Set
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
import queue
import tempfile

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Type variables for generic typing
T = TypeVar('T')  # Task type
R = TypeVar('R')  # Result type

class Task:
    """
    Represents a distributed task with metadata.
    """
    
    def __init__(
        self,
        task_id: str,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: int = 0,
        timeout: Optional[float] = None
    ):
        """
        Initialize a task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Priority value (lower values = higher priority)
            timeout: Timeout in seconds
        """
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.worker_id = None
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary for serialization.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "task_id": self.task_id,
            "priority": self.priority,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "worker_id": self.worker_id,
            "status": self.status,
            "timeout": self.timeout
        }
    
    def __lt__(self, other):
        """Compare tasks by priority for priority queue."""
        if not isinstance(other, Task):
            return NotImplemented
        return self.priority < other.priority


class TaskResult:
    """
    Represents the result of a distributed task.
    """
    
    def __init__(
        self,
        task_id: str,
        worker_id: str,
        status: str,
        result: Any = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        """
        Initialize a task result.
        
        Args:
            task_id: Unique identifier for the task
            worker_id: Identifier of the worker that processed the task
            status: Status of the task (completed, failed)
            result: Result of the task
            error: Error message if the task failed
            execution_time: Time taken to execute the task in seconds
        """
        self.task_id = task_id
        self.worker_id = worker_id
        self.status = status
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.received_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for serialization.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            "task_id": self.task_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "error": self.error,
            "execution_time": self.execution_time,
            "received_at": self.received_at
        }


class Worker:
    """
    Represents a worker in a distributed system.
    """
    
    def __init__(
        self,
        worker_id: str,
        host: str,
        port: int,
        capabilities: Dict[str, Any] = None,
        max_tasks: int = 10
    ):
        """
        Initialize a worker.
        
        Args:
            worker_id: Unique identifier for the worker
            host: Hostname or IP address
            port: Port number
            capabilities: Dictionary of worker capabilities
            max_tasks: Maximum number of concurrent tasks
        """
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.capabilities = capabilities or {}
        self.max_tasks = max_tasks
        self.current_tasks = 0
        self.total_tasks_processed = 0
        self.last_heartbeat = time.time()
        self.status = "idle"  # idle, busy, offline
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert worker to dictionary for serialization.
        
        Returns:
            Dictionary representation of the worker
        """
        return {
            "worker_id": self.worker_id,
            "host": self.host,
            "port": self.port,
            "capabilities": self.capabilities,
            "max_tasks": self.max_tasks,
            "current_tasks": self.current_tasks,
            "total_tasks_processed": self.total_tasks_processed,
            "last_heartbeat": self.last_heartbeat,
            "status": self.status
        }
    
    def update_heartbeat(self):
        """Update the last heartbeat timestamp."""
        self.last_heartbeat = time.time()
    
    def is_available(self) -> bool:
        """
        Check if the worker is available to process tasks.
        
        Returns:
            True if the worker is available, False otherwise
        """
        return (
            self.status != "offline" and
            self.current_tasks < self.max_tasks
        )


class LocalWorkerPool:
    """
    A pool of local worker processes for distributed processing.
    """
    
    def __init__(
        self,
        num_workers: Optional[int] = None,
        max_tasks_per_worker: int = 10,
        worker_timeout: float = 30.0
    ):
        """
        Initialize a local worker pool.
        
        Args:
            num_workers: Number of worker processes (defaults to CPU count)
            max_tasks_per_worker: Maximum tasks per worker
            worker_timeout: Timeout for worker processes in seconds
        """
        if num_workers is None:
            num_workers = multiprocessing.cpu_count()
        
        self.num_workers = num_workers
        self.max_tasks_per_worker = max_tasks_per_worker
        self.worker_timeout = worker_timeout
        
        # Create worker processes
        self.workers = []
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.stop_event = multiprocessing.Event()
        
        # Create worker processes
        for i in range(num_workers):
            worker_id = f"worker-{i}"
            worker = multiprocessing.Process(
                target=self._worker_process,
                args=(worker_id, self.task_queue, self.result_queue, self.stop_event)
            )
            worker.daemon = True
            self.workers.append((worker_id, worker))
        
        # Statistics
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0
        }
        self._lock = threading.Lock()
    
    def start(self):
        """Start all worker processes."""
        logger.info(f"Starting {self.num_workers} worker processes")
        for _, worker in self.workers:
            worker.start()
    
    def stop(self):
        """Stop all worker processes."""
        logger.info("Stopping worker processes")
        self.stop_event.set()
        
        # Wait for workers to terminate
        for _, worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=2.0)
                if worker.is_alive():
                    worker.terminate()
    
    def _worker_process(
        self,
        worker_id: str,
        task_queue: multiprocessing.Queue,
        result_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event
    ):
        """
        Worker process function.
        
        Args:
            worker_id: Unique identifier for the worker
            task_queue: Queue for receiving tasks
            result_queue: Queue for sending results
            stop_event: Event for signaling worker to stop
        """
        logger.info(f"Worker {worker_id} started")
        
        while not stop_event.is_set():
            try:
                # Try to get a task with timeout
                try:
                    task_data = task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Deserialize task
                task_id, func, args, kwargs, timeout = task_data
                
                # Execute task with timeout
                start_time = time.time()
                try:
                    if timeout:
                        # Use a separate process for timeout enforcement
                        with ProcessPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(func, *args, **kwargs)
                            result = future.result(timeout=timeout)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Task completed successfully
                    execution_time = time.time() - start_time
                    result_queue.put((
                        task_id,
                        worker_id,
                        "completed",
                        result,
                        None,
                        execution_time
                    ))
                    
                except Exception as e:
                    # Task failed
                    execution_time = time.time() - start_time
                    result_queue.put((
                        task_id,
                        worker_id,
                        "failed",
                        None,
                        str(e),
                        execution_time
                    ))
            
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Worker {worker_id} stopped")
    
    def submit(
        self,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: int = 0,
        timeout: Optional[float] = None
    ) -> str:
        """
        Submit a task to the worker pool.
        
        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Priority value (lower values = higher priority)
            timeout: Timeout in seconds
            
        Returns:
            Task ID
        """
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Submit task to queue
        self.task_queue.put((task_id, func, args, kwargs or {}, timeout))
        
        # Update statistics
        with self._lock:
            self.stats["tasks_submitted"] += 1
        
        return task_id
    
    def get_result(self, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """
        Get a result from the result queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            TaskResult or None if no results are available
        """
        try:
            # Get result from queue
            result_data = self.result_queue.get(timeout=timeout)
            
            # Create TaskResult object
            task_id, worker_id, status, result, error, execution_time = result_data
            task_result = TaskResult(
                task_id=task_id,
                worker_id=worker_id,
                status=status,
                result=result,
                error=error,
                execution_time=execution_time
            )
            
            # Update statistics
            with self._lock:
                if status == "completed":
                    self.stats["tasks_completed"] += 1
                else:
                    self.stats["tasks_failed"] += 1
            
            return task_result
        
        except queue.Empty:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the worker pool.
        
        Returns:
            Dictionary with worker pool statistics
        """
        with self._lock:
            return self.stats.copy()


class DistributedTaskManager:
    """
    Manager for distributed tasks across multiple processes or machines.
    """
    
    def __init__(
        self,
        mode: str = "local",
        num_workers: Optional[int] = None,
        max_tasks_per_worker: int = 10,
        worker_timeout: float = 30.0,
        result_timeout: float = 5.0
    ):
        """
        Initialize the distributed task manager.
        
        Args:
            mode: Processing mode ("local" or "distributed")
            num_workers: Number of worker processes (defaults to CPU count)
            max_tasks_per_worker: Maximum tasks per worker
            worker_timeout: Timeout for worker processes in seconds
            result_timeout: Timeout for waiting for results in seconds
        """
        self.mode = mode
        self.result_timeout = result_timeout
        
        # Create worker pool based on mode
        if mode == "local":
            self.worker_pool = LocalWorkerPool(
                num_workers=num_workers,
                max_tasks_per_worker=max_tasks_per_worker,
                worker_timeout=worker_timeout
            )
            self.worker_pool.start()
        else:
            raise ValueError(f"Unsupported mode: {mode}")
        
        # Task tracking
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self._lock = threading.Lock()
        
        # Start result collection thread
        self._stop_event = threading.Event()
        self._result_thread = threading.Thread(target=self._collect_results)
        self._result_thread.daemon = True
        self._result_thread.start()
    
    def _collect_results(self):
        """Collect results from the worker pool."""
        while not self._stop_event.is_set():
            try:
                # Get result from worker pool
                result = self.worker_pool.get_result(timeout=self.result_timeout)
                if result:
                    # Store result
                    with self._lock:
                        self.results[result.task_id] = result
                        
                        # Update task status
                        if result.task_id in self.tasks:
                            task = self.tasks[result.task_id]
                            task.status = result.status
                            task.completed_at = time.time()
                            task.worker_id = result.worker_id
                            
                            if result.status == "completed":
                                task.result = result.result
                            else:
                                task.error = result.error
            
            except Exception as e:
                logger.error(f"Error collecting results: {e}")
    
    def submit(
        self,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: int = 0,
        timeout: Optional[float] = None
    ) -> str:
        """
        Submit a task for distributed processing.
        
        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Priority value (lower values = higher priority)
            timeout: Timeout in seconds
            
        Returns:
            Task ID
        """
        # Create task
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout
        )
        
        # Store task
        with self._lock:
            self.tasks[task_id] = task
        
        # Submit to worker pool
        self.worker_pool.submit(
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            timeout=timeout
        )
        
        return task_id
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get the result of a task.
        
        Args:
            task_id: Task ID
            timeout: Timeout in seconds
            
        Returns:
            Task result or None if not available
            
        Raises:
            ValueError: If the task does not exist
            Exception: If the task failed
        """
        # Check if task exists
        with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} does not exist")
        
        # Wait for result
        start_time = time.time()
        while timeout is None or time.time() - start_time < timeout:
            # Check if result is available
            with self._lock:
                if task_id in self.results:
                    result = self.results[task_id]
                    
                    # Check result status
                    if result.status == "completed":
                        return result.result
                    elif result.status == "failed":
                        raise Exception(f"Task {task_id} failed: {result.error}")
            
            # Wait for result
            time.sleep(0.1)
        
        # Timeout
        return None
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get the status of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status or None if the task does not exist
        """
        with self._lock:
            if task_id in self.tasks:
                return self.tasks[task_id].status
            return None
    
    def wait_for_tasks(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, str]:
        """
        Wait for multiple tasks to complete.
        
        Args:
            task_ids: List of task IDs
            timeout: Timeout in seconds
            
        Returns:
            Dictionary mapping task IDs to statuses
        """
        # Check if tasks exist
        with self._lock:
            for task_id in task_ids:
                if task_id not in self.tasks:
                    raise ValueError(f"Task {task_id} does not exist")
        
        # Wait for tasks to complete
        start_time = time.time()
        while timeout is None or time.time() - start_time < timeout:
            # Check if all tasks are completed
            with self._lock:
                statuses = {task_id: self.tasks[task_id].status for task_id in task_ids}
                if all(status in ("completed", "failed") for status in statuses.values()):
                    return statuses
            
            # Wait for tasks to complete
            time.sleep(0.1)
        
        # Timeout
        with self._lock:
            return {task_id: self.tasks[task_id].status for task_id in task_ids}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the distributed task manager.
        
        Returns:
            Dictionary with task manager statistics
        """
        worker_stats = self.worker_pool.get_stats()
        
        with self._lock:
            stats = {
                "mode": self.mode,
                "tasks_total": len(self.tasks),
                "tasks_pending": sum(1 for task in self.tasks.values() if task.status == "pending"),
                "tasks_running": sum(1 for task in self.tasks.values() if task.status == "running"),
                "tasks_completed": sum(1 for task in self.tasks.values() if task.status == "completed"),
                "tasks_failed": sum(1 for task in self.tasks.values() if task.status == "failed"),
                "results_total": len(self.results)
            }
        
        # Merge worker pool stats
        stats.update(worker_stats)
        
        return stats
    
    def shutdown(self):
        """Shutdown the distributed task manager."""
        logger.info("Shutting down distributed task manager")
        
        # Stop result collection thread
        self._stop_event.set()
        if self._result_thread.is_alive():
            self._result_thread.join(timeout=2.0)
        
        # Stop worker pool
        self.worker_pool.stop()


def process_batch_distributed(
    items: List[T],
    process_func: Callable[[T], R],
    num_workers: Optional[int] = None,
    mode: str = "local",
    timeout: Optional[float] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[R]:
    """
    Process a batch of items using distributed processing.
    
    Args:
        items: List of items to process
        process_func: Function to process each item
        num_workers: Number of worker processes
        mode: Processing mode ("local" or "distributed")
        timeout: Timeout for each task in seconds
        progress_callback: Callback function for progress updates
        
    Returns:
        List of results from processing each item
    """
    # Create distributed task manager
    task_manager = DistributedTaskManager(
        mode=mode,
        num_workers=num_workers
    )
    
    try:
        # Submit tasks
        task_ids = []
        for item in items:
            task_id = task_manager.submit(
                func=process_func,
                args=(item,),
                timeout=timeout
            )
            task_ids.append(task_id)
        
        # Wait for results
        results = []
        for i, task_id in enumerate(task_ids):
            try:
                result = task_manager.get_result(task_id, timeout=timeout)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing item {i}: {e}")
                results.append(None)
            
            # Update progress
            if progress_callback:
                progress_callback(i + 1, len(items))
        
        # Log statistics
        stats = task_manager.get_stats()
        logger.info(f"Distributed batch processing completed: {stats}")
        
        return results
    
    finally:
        # Shutdown task manager
        task_manager.shutdown()


def create_distributed_executor(
    config: Dict[str, Any],
    num_workers: Optional[int] = None,
    mode: str = "local"
) -> DistributedTaskManager:
    """
    Create a distributed task manager with configuration.
    
    Args:
        config: Configuration dictionary
        num_workers: Number of workers (overrides config)
        mode: Processing mode ("local" or "distributed")
        
    Returns:
        Configured DistributedTaskManager instance
    """
    # Get settings from config
    if num_workers is None:
        num_workers = config.get("scan_settings", {}).get("max_distributed_workers")
    
    if mode == "local":
        mode = config.get("scan_settings", {}).get("distributed_mode", "local")
    
    max_tasks_per_worker = config.get("scan_settings", {}).get("max_tasks_per_worker", 10)
    worker_timeout = config.get("scan_settings", {}).get("worker_timeout", 30.0)
    
    # Create task manager
    task_manager = DistributedTaskManager(
        mode=mode,
        num_workers=num_workers,
        max_tasks_per_worker=max_tasks_per_worker,
        worker_timeout=worker_timeout
    )
    
    return task_manager