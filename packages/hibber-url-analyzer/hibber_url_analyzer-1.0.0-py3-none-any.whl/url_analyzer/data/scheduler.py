"""
Export Scheduler Module

This module provides functionality for scheduling automated exports of URL analysis data
at specified intervals.
"""

import os
import time
import threading
import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import pandas as pd

from url_analyzer.utils.logging import get_logger
from url_analyzer.data.export import export_data, export_filtered_data

# Initialize logger
logger = get_logger(__name__)


class ExportScheduler:
    """
    A scheduler for automated exports of URL analysis data.
    
    This class provides functionality to schedule exports at specified intervals,
    with support for different export formats and filtering options.
    """
    
    def __init__(self):
        """Initialize the export scheduler."""
        self.scheduled_tasks = {}
        self.running = False
        self.scheduler_thread = None
        self.lock = threading.Lock()
    
    def schedule_export(
        self,
        task_id: str,
        df: pd.DataFrame,
        output_path: str,
        format: str = 'csv',
        interval: int = 86400,  # Default: daily (24 hours)
        filters: Optional[Dict[str, Any]] = None,
        filter_mode: str = 'exact',
        title: str = "URL Analysis Results",
        start_time: Optional[datetime.datetime] = None
    ) -> str:
        """
        Schedule an export task to run at specified intervals.
        
        Args:
            task_id: Unique identifier for the task
            df: DataFrame to export
            output_path: Base path for the output file (without extension)
            format: Export format ('csv', 'json', 'excel', 'xml', 'html', or 'markdown')
            interval: Export interval in seconds
            filters: Dictionary of column-value pairs for filtering
            filter_mode: Filtering mode ('exact', 'contains', 'regex', 'range')
            title: Title for the document (used for HTML and Markdown formats)
            start_time: When to start the first export (if None, starts immediately)
            
        Returns:
            Task ID
        """
        with self.lock:
            # Generate a task ID if not provided
            if not task_id:
                task_id = f"export_{int(time.time())}"
            
            # Calculate next run time
            now = datetime.datetime.now()
            if start_time and start_time > now:
                next_run = start_time
            else:
                next_run = now
            
            # Create task
            task = {
                'id': task_id,
                'df': df.copy(),  # Make a copy to avoid modifications
                'output_path': output_path,
                'format': format,
                'interval': interval,
                'filters': filters,
                'filter_mode': filter_mode,
                'title': title,
                'next_run': next_run,
                'last_run': None,
                'last_status': None,
                'runs': 0
            }
            
            # Add task to scheduled tasks
            self.scheduled_tasks[task_id] = task
            
            logger.info(f"Scheduled export task '{task_id}' to run every {interval} seconds")
            
            # Start scheduler if not already running
            if not self.running:
                self.start()
            
            return task_id
    
    def update_task(
        self,
        task_id: str,
        **kwargs
    ) -> bool:
        """
        Update a scheduled export task.
        
        Args:
            task_id: ID of the task to update
            **kwargs: Task parameters to update
            
        Returns:
            True if the task was updated, False otherwise
        """
        with self.lock:
            if task_id not in self.scheduled_tasks:
                logger.warning(f"Task '{task_id}' not found")
                return False
            
            task = self.scheduled_tasks[task_id]
            
            # Update task parameters
            for key, value in kwargs.items():
                if key in task and key not in ['id', 'next_run', 'last_run', 'last_status', 'runs']:
                    task[key] = value
            
            logger.info(f"Updated export task '{task_id}'")
            return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a scheduled export task.
        
        Args:
            task_id: ID of the task to remove
            
        Returns:
            True if the task was removed, False otherwise
        """
        with self.lock:
            if task_id not in self.scheduled_tasks:
                logger.warning(f"Task '{task_id}' not found")
                return False
            
            del self.scheduled_tasks[task_id]
            logger.info(f"Removed export task '{task_id}'")
            
            # Stop scheduler if no tasks left
            if not self.scheduled_tasks and self.running:
                self.stop()
            
            return True
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a scheduled export task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task information or None if not found
        """
        with self.lock:
            if task_id not in self.scheduled_tasks:
                logger.warning(f"Task '{task_id}' not found")
                return None
            
            task = self.scheduled_tasks[task_id].copy()
            
            # Remove DataFrame from result to avoid large output
            if 'df' in task:
                task['df'] = f"DataFrame with {len(task['df'])} rows"
            
            return task
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all scheduled export tasks.
        
        Returns:
            List of task information
        """
        with self.lock:
            tasks = []
            
            for task_id, task in self.scheduled_tasks.items():
                task_info = task.copy()
                
                # Remove DataFrame from result to avoid large output
                if 'df' in task_info:
                    task_info['df'] = f"DataFrame with {len(task_info['df'])} rows"
                
                tasks.append(task_info)
            
            return tasks
    
    def start(self) -> None:
        """Start the scheduler."""
        with self.lock:
            if self.running:
                logger.warning("Scheduler is already running")
                return
            
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("Export scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        with self.lock:
            if not self.running:
                logger.warning("Scheduler is not running")
                return
            
            self.running = False
            
            # Wait for scheduler thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Export scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            try:
                self._check_tasks()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Sleep for a short time to avoid high CPU usage
            time.sleep(1)
    
    def _check_tasks(self) -> None:
        """Check tasks and run those that are due."""
        now = datetime.datetime.now()
        tasks_to_run = []
        
        # Find tasks that are due
        with self.lock:
            for task_id, task in self.scheduled_tasks.items():
                if task['next_run'] <= now:
                    tasks_to_run.append(task_id)
        
        # Run tasks
        for task_id in tasks_to_run:
            self._run_task(task_id)
    
    def _run_task(self, task_id: str) -> None:
        """
        Run a scheduled export task.
        
        Args:
            task_id: ID of the task to run
        """
        with self.lock:
            if task_id not in self.scheduled_tasks:
                return
            
            task = self.scheduled_tasks[task_id]
            
            # Update next run time
            now = datetime.datetime.now()
            task['next_run'] = now + datetime.timedelta(seconds=task['interval'])
        
        # Run the export
        try:
            logger.info(f"Running export task '{task_id}'")
            
            # Generate output path with timestamp
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            output_path = task['output_path']
            
            # Add timestamp to output path if it doesn't have a placeholder
            if '{timestamp}' not in output_path:
                base, ext = os.path.splitext(output_path)
                output_path = f"{base}_{timestamp}{ext}"
            else:
                output_path = output_path.format(timestamp=timestamp)
            
            # Run export
            if task['filters']:
                result_path = export_filtered_data(
                    task['df'],
                    output_path,
                    task['format'],
                    task['filters'],
                    task['filter_mode'],
                    task['title']
                )
            else:
                result_path = export_data(
                    task['df'],
                    output_path,
                    task['format'],
                    task['title']
                )
            
            # Update task status
            with self.lock:
                if task_id in self.scheduled_tasks:
                    task = self.scheduled_tasks[task_id]
                    task['last_run'] = now
                    task['runs'] += 1
                    
                    if result_path:
                        task['last_status'] = 'success'
                        logger.info(f"Export task '{task_id}' completed successfully: {result_path}")
                    else:
                        task['last_status'] = 'error'
                        logger.error(f"Export task '{task_id}' failed")
        
        except Exception as e:
            logger.error(f"Error running export task '{task_id}': {e}")
            
            # Update task status
            with self.lock:
                if task_id in self.scheduled_tasks:
                    task = self.scheduled_tasks[task_id]
                    task['last_run'] = now
                    task['last_status'] = 'error'


# Create a singleton instance
_scheduler_instance = None

def get_scheduler() -> ExportScheduler:
    """
    Get the singleton scheduler instance.
    
    Returns:
        ExportScheduler instance
    """
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = ExportScheduler()
    
    return _scheduler_instance


def schedule_export(
    df: pd.DataFrame,
    output_path: str,
    format: str = 'csv',
    interval: int = 86400,  # Default: daily (24 hours)
    filters: Optional[Dict[str, Any]] = None,
    filter_mode: str = 'exact',
    title: str = "URL Analysis Results",
    start_time: Optional[datetime.datetime] = None,
    task_id: Optional[str] = None
) -> str:
    """
    Schedule an export task to run at specified intervals.
    
    This is a convenience function that uses the singleton scheduler instance.
    
    Args:
        df: DataFrame to export
        output_path: Base path for the output file (without extension)
        format: Export format ('csv', 'json', 'excel', 'xml', 'html', or 'markdown')
        interval: Export interval in seconds
        filters: Dictionary of column-value pairs for filtering
        filter_mode: Filtering mode ('exact', 'contains', 'regex', 'range')
        title: Title for the document (used for HTML and Markdown formats)
        start_time: When to start the first export (if None, starts immediately)
        task_id: Unique identifier for the task (if None, generates one)
        
    Returns:
        Task ID
    """
    scheduler = get_scheduler()
    
    return scheduler.schedule_export(
        task_id,
        df,
        output_path,
        format,
        interval,
        filters,
        filter_mode,
        title,
        start_time
    )