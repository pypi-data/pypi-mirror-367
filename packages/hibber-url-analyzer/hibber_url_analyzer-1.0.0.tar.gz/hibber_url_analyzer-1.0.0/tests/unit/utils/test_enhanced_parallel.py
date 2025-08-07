"""
Test Enhanced Parallel Processing

This script tests the enhanced parallel processing capabilities including:
- Asynchronous processing with asyncio
- Distributed processing
- Optimized thread pool configuration
- Work stealing
- Priority queues
"""

import os
import time
import asyncio
import random
import concurrent.futures
from typing import List, Dict, Any
import argparse

# Import URL Analyzer modules
from url_analyzer.utils.async_processing import (
    process_batch_async, 
    AsyncTaskManager,
    run_async_in_thread
)
from url_analyzer.utils.distributed import (
    process_batch_distributed,
    DistributedTaskManager
)
from url_analyzer.utils.thread_pool import (
    create_optimized_thread_pool,
    AdaptiveThreadPoolExecutor,
    track_thread_metrics
)
from url_analyzer.utils.concurrency import create_thread_pool_executor
from url_analyzer.config.manager import load_config

# Configure simple logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample tasks for testing
def cpu_bound_task(n: int) -> int:
    """
    A CPU-bound task that computes the sum of prime numbers up to n.
    
    Args:
        n: Upper limit for prime number calculation
        
    Returns:
        Sum of prime numbers up to n
    """
    def is_prime(num):
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True
    
    return sum(i for i in range(2, n) if is_prime(i))

def io_bound_task(delay: float) -> float:
    """
    An I/O-bound task that simulates network or disk I/O with a delay.
    
    Args:
        delay: Delay in seconds
        
    Returns:
        The delay value
    """
    time.sleep(delay)
    return delay

async def async_io_task(delay: float) -> float:
    """
    An asynchronous I/O-bound task.
    
    Args:
        delay: Delay in seconds
        
    Returns:
        The delay value
    """
    await asyncio.sleep(delay)
    return delay

def mixed_task(n: int, delay: float) -> Dict[str, Any]:
    """
    A mixed task with both CPU and I/O components.
    
    Args:
        n: Upper limit for prime number calculation
        delay: Delay in seconds
        
    Returns:
        Dictionary with results
    """
    # I/O component
    time.sleep(delay)
    
    # CPU component
    result = cpu_bound_task(n)
    
    return {
        "n": n,
        "delay": delay,
        "result": result
    }

async def async_mixed_task(n: int, delay: float) -> Dict[str, Any]:
    """
    An asynchronous mixed task with both CPU and I/O components.
    
    Args:
        n: Upper limit for prime number calculation
        delay: Delay in seconds
        
    Returns:
        Dictionary with results
    """
    # I/O component (asynchronous)
    await asyncio.sleep(delay)
    
    # CPU component
    result = cpu_bound_task(n)
    
    return {
        "n": n,
        "delay": delay,
        "result": result
    }

def test_thread_pool_executor():
    """Test the optimized thread pool executor."""
    logger.info("Testing optimized thread pool executor...")
    
    # Load configuration
    config = load_config()
    
    # Create optimized thread pool for I/O-bound operations
    io_executor = create_optimized_thread_pool(
        config=config,
        operation_type="io",
        thread_name_prefix="io-test-"
    )
    
    # Create optimized thread pool for CPU-bound operations
    cpu_executor = create_optimized_thread_pool(
        config=config,
        operation_type="cpu",
        thread_name_prefix="cpu-test-"
    )
    
    # Create tasks
    io_tasks = [random.uniform(0.1, 0.5) for _ in range(20)]
    cpu_tasks = [random.randint(1000, 5000) for _ in range(10)]
    
    # Execute I/O-bound tasks
    start_time = time.time()
    io_futures = [io_executor.submit(io_bound_task, delay) for delay in io_tasks]
    io_results = [future.result() for future in concurrent.futures.as_completed(io_futures)]
    io_time = time.time() - start_time
    
    # Execute CPU-bound tasks
    start_time = time.time()
    cpu_futures = [cpu_executor.submit(cpu_bound_task, n) for n in cpu_tasks]
    cpu_results = [future.result() for future in concurrent.futures.as_completed(cpu_futures)]
    cpu_time = time.time() - start_time
    
    # Log results
    logger.info(f"I/O tasks completed in {io_time:.2f} seconds")
    logger.info(f"CPU tasks completed in {cpu_time:.2f} seconds")
    
    # Shutdown executors
    io_executor.shutdown()
    cpu_executor.shutdown()
    
    return {
        "io_time": io_time,
        "cpu_time": cpu_time,
        "io_results": io_results,
        "cpu_results": cpu_results
    }

def test_adaptive_thread_pool():
    """Test the adaptive thread pool executor."""
    logger.info("Testing adaptive thread pool executor...")
    
    # Create adaptive thread pool
    executor = AdaptiveThreadPoolExecutor(
        max_workers=4,  # Start with a small number
        thread_name_prefix="adaptive-test-",
        operation_type="mixed",
        adaptation_interval=5.0,  # Adapt every 5 seconds
        min_workers=2,
        max_workers_limit=20
    )
    
    # Create mixed tasks with varying CPU and I/O loads
    tasks = []
    for _ in range(30):
        n = random.randint(1000, 10000)
        delay = random.uniform(0.1, 1.0)
        tasks.append((n, delay))
    
    # Execute tasks in batches to observe adaptation
    results = []
    for i in range(0, len(tasks), 5):
        batch = tasks[i:i+5]
        logger.info(f"Submitting batch {i//5 + 1} with {len(batch)} tasks")
        
        # Submit batch
        futures = [executor.submit(mixed_task, n, delay) for n, delay in batch]
        batch_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        results.extend(batch_results)
        
        # Wait to allow adaptation
        time.sleep(2)
    
    # Shutdown executor
    executor.shutdown()
    
    return results

async def test_async_processing():
    """Test asynchronous processing with asyncio."""
    logger.info("Testing asynchronous processing...")
    
    # Create async task manager
    task_manager = AsyncTaskManager(
        max_workers=10,
        use_work_stealing=True
    )
    
    # Create async tasks
    tasks = []
    for _ in range(20):
        delay = random.uniform(0.1, 0.5)
        tasks.append(delay)
    
    # Process tasks with progress tracking
    def progress_callback(completed, total):
        logger.info(f"Progress: {completed}/{total} tasks completed")
    
    # Execute tasks
    start_time = time.time()
    results = await process_batch_async(
        items=tasks,
        process_func=async_io_task,
        max_workers=10,
        use_work_stealing=True,
        progress_callback=progress_callback
    )
    async_time = time.time() - start_time
    
    # Log results
    logger.info(f"Async tasks completed in {async_time:.2f} seconds")
    
    # Get task manager statistics
    stats = task_manager.get_stats()
    logger.info(f"Task manager statistics: {stats}")
    
    return {
        "async_time": async_time,
        "results": results
    }

def test_distributed_processing():
    """Test distributed processing."""
    logger.info("Testing distributed processing...")
    
    # Create tasks
    tasks = [random.randint(1000, 5000) for _ in range(10)]
    
    # Process tasks with progress tracking
    def progress_callback(completed, total):
        logger.info(f"Progress: {completed}/{total} tasks completed")
    
    # Execute tasks
    start_time = time.time()
    results = process_batch_distributed(
        items=tasks,
        process_func=cpu_bound_task,
        num_workers=4,
        mode="local",
        progress_callback=progress_callback
    )
    distributed_time = time.time() - start_time
    
    # Log results
    logger.info(f"Distributed tasks completed in {distributed_time:.2f} seconds")
    
    return {
        "distributed_time": distributed_time,
        "results": results
    }

def test_priority_queue():
    """Test priority queue processing."""
    logger.info("Testing priority queue processing...")
    
    # Create async task manager
    task_manager = AsyncTaskManager(
        max_workers=5,
        use_work_stealing=True
    )
    
    # Create tasks with priorities
    tasks = []
    for i in range(20):
        n = random.randint(1000, 5000)
        # Assign priority (lower value = higher priority)
        # Every 5th task is high priority
        priority = 0 if i % 5 == 0 else random.randint(1, 10)
        tasks.append((n, priority))
    
    # Define priority function
    def priority_func(item):
        _, priority = item
        return priority
    
    # Define processing function
    async def process_with_priority(item):
        n, priority = item
        logger.info(f"Processing task with n={n}, priority={priority}")
        # High priority tasks get less delay
        delay = 0.1 if priority == 0 else 0.5
        await asyncio.sleep(delay)
        result = cpu_bound_task(n)
        return {
            "n": n,
            "priority": priority,
            "result": result
        }
    
    # Execute tasks
    async def run_priority_test():
        results = await task_manager.map(
            func=process_with_priority,
            items=tasks,
            priority_func=priority_func
        )
        return results
    
    # Run the test
    start_time = time.time()
    results = run_async_in_thread(run_priority_test())
    priority_time = time.time() - start_time
    
    # Log results
    logger.info(f"Priority queue tasks completed in {priority_time:.2f} seconds")
    
    return {
        "priority_time": priority_time,
        "results": results
    }

def test_work_stealing():
    """Test work stealing capabilities."""
    logger.info("Testing work stealing...")
    
    # Create tasks with imbalanced workloads
    tasks = []
    for i in range(20):
        # Create imbalanced workload
        # Some tasks are much heavier than others
        if i < 5:
            n = random.randint(8000, 10000)  # Heavy tasks
            delay = random.uniform(0.4, 0.6)  # Longer delay
        else:
            n = random.randint(1000, 3000)  # Light tasks
            delay = random.uniform(0.1, 0.2)  # Short delay
        tasks.append((n, delay))
    
    # Define processing function
    async def process_task(item):
        n, delay = item
        # Simulate I/O
        await asyncio.sleep(delay)
        # Perform CPU work
        result = cpu_bound_task(n)
        return {
            "n": n,
            "delay": delay,
            "result": result
        }
    
    # Execute tasks with work stealing
    async def run_with_stealing():
        results_with_stealing = await process_batch_async(
            items=tasks,
            process_func=process_task,
            max_workers=8,
            use_work_stealing=True
        )
        return results_with_stealing
    
    # Execute tasks without work stealing
    async def run_without_stealing():
        results_without_stealing = await process_batch_async(
            items=tasks,
            process_func=process_task,
            max_workers=8,
            use_work_stealing=False
        )
        return results_without_stealing
    
    # Run tests
    logger.info("Running with work stealing...")
    start_time = time.time()
    results_with_stealing = run_async_in_thread(run_with_stealing())
    time_with_stealing = time.time() - start_time
    
    logger.info("Running without work stealing...")
    start_time = time.time()
    results_without_stealing = run_async_in_thread(run_without_stealing())
    time_without_stealing = time.time() - start_time
    
    # Log results
    logger.info(f"Tasks with work stealing completed in {time_with_stealing:.2f} seconds")
    logger.info(f"Tasks without work stealing completed in {time_without_stealing:.2f} seconds")
    logger.info(f"Improvement: {(time_without_stealing - time_with_stealing) / time_without_stealing * 100:.2f}%")
    
    return {
        "time_with_stealing": time_with_stealing,
        "time_without_stealing": time_without_stealing,
        "improvement_percent": (time_without_stealing - time_with_stealing) / time_without_stealing * 100
    }

def run_all_tests():
    """Run all parallel processing tests."""
    results = {}
    
    # Test thread pool executor
    results["thread_pool"] = test_thread_pool_executor()
    
    # Test adaptive thread pool
    results["adaptive_pool"] = test_adaptive_thread_pool()
    
    # Test async processing
    results["async"] = run_async_in_thread(test_async_processing())
    
    # Test distributed processing
    results["distributed"] = test_distributed_processing()
    
    # Test priority queue
    results["priority_queue"] = test_priority_queue()
    
    # Test work stealing
    results["work_stealing"] = test_work_stealing()
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test enhanced parallel processing")
    parser.add_argument("--test", choices=["all", "thread_pool", "adaptive", "async", "distributed", "priority", "work_stealing"], 
                        default="all", help="Test to run")
    args = parser.parse_args()
    
    try:
        if args.test == "all":
            results = run_all_tests()
            logger.info("All tests completed successfully")
        elif args.test == "thread_pool":
            results = test_thread_pool_executor()
            logger.info("Thread pool test completed successfully")
        elif args.test == "adaptive":
            results = test_adaptive_thread_pool()
            logger.info("Adaptive thread pool test completed successfully")
        elif args.test == "async":
            results = run_async_in_thread(test_async_processing())
            logger.info("Async processing test completed successfully")
        elif args.test == "distributed":
            results = test_distributed_processing()
            logger.info("Distributed processing test completed successfully")
        elif args.test == "priority":
            results = test_priority_queue()
            logger.info("Priority queue test completed successfully")
        elif args.test == "work_stealing":
            results = test_work_stealing()
            logger.info("Work stealing test completed successfully")
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        raise