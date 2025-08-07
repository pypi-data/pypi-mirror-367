"""
Scheduler Module

This module provides functionality for scheduling tasks to run at specified times
or intervals. It supports one-time and recurring tasks, and provides a simple
interface for managing scheduled tasks.
"""

import os
import json
import time
import logging
import datetime
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import AutomationError

# Create logger
logger = get_logger(__name__)

# Default path for storing scheduled tasks
DEFAULT_TASKS_FILE = os.path.join(os.path.expanduser("~"), ".url_analyzer", "scheduled_tasks.json")


@dataclass
class ScheduledTask:
    """
    Represents a scheduled task with its configuration and status.
    
    Attributes:
        id: Unique identifier for the task
        name: Human-readable name for the task
        command: Command to execute (as a list of arguments)
        schedule_type: Type of schedule (once, daily, weekly, monthly, interval)
        schedule_params: Parameters for the schedule (depends on schedule_type)
        enabled: Whether the task is enabled
        last_run: Timestamp of the last run (None if never run)
        next_run: Timestamp of the next scheduled run
        created_at: Timestamp when the task was created
        updated_at: Timestamp when the task was last updated
        description: Optional description of the task
        tags: Optional tags for categorizing tasks
    """
    id: str
    name: str
    command: List[str]
    schedule_type: str
    schedule_params: Dict[str, Any]
    enabled: bool = True
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledTask':
        """Create a task from a dictionary."""
        return cls(**data)
    
    def get_next_run_time(self) -> Optional[float]:
        """Calculate the next run time based on the schedule."""
        now = datetime.datetime.now()
        
        if self.schedule_type == 'once':
            # One-time schedule
            run_time = datetime.datetime.fromtimestamp(self.schedule_params['timestamp'])
            if run_time > now:
                return run_time.timestamp()
            return None
            
        elif self.schedule_type == 'daily':
            # Daily schedule
            hour = self.schedule_params.get('hour', 0)
            minute = self.schedule_params.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += datetime.timedelta(days=1)
            return next_run.timestamp()
            
        elif self.schedule_type == 'weekly':
            # Weekly schedule
            day_of_week = self.schedule_params.get('day_of_week', 0)  # 0 = Monday
            hour = self.schedule_params.get('hour', 0)
            minute = self.schedule_params.get('minute', 0)
            
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
                
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += datetime.timedelta(days=days_ahead)
            return next_run.timestamp()
            
        elif self.schedule_type == 'monthly':
            # Monthly schedule
            day = self.schedule_params.get('day', 1)
            hour = self.schedule_params.get('hour', 0)
            minute = self.schedule_params.get('minute', 0)
            
            next_run = now.replace(day=min(day, 28), hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # Move to next month
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run.timestamp()
            
        elif self.schedule_type == 'interval':
            # Interval schedule (in minutes)
            interval_minutes = self.schedule_params.get('minutes', 60)
            
            if self.last_run is None:
                # If never run, schedule immediately
                return now.timestamp()
            
            last_run_dt = datetime.datetime.fromtimestamp(self.last_run)
            next_run = last_run_dt + datetime.timedelta(minutes=interval_minutes)
            return next_run.timestamp()
            
        return None
    
    def update_next_run(self) -> None:
        """Update the next run time based on the schedule."""
        self.next_run = self.get_next_run_time()
        self.updated_at = time.time()


class TaskScheduler:
    """
    Manages scheduled tasks and ensures they run at the appropriate times.
    """
    def __init__(self, tasks_file: str = DEFAULT_TASKS_FILE):
        """
        Initialize the task scheduler.
        
        Args:
            tasks_file: Path to the file for storing scheduled tasks
        """
        self.tasks_file = tasks_file
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.thread = None
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load tasks from the tasks file."""
        if not os.path.exists(self.tasks_file):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            self.tasks = {}
            return
        
        try:
            with open(self.tasks_file, 'r') as f:
                tasks_data = json.load(f)
                
            self.tasks = {
                task_id: ScheduledTask.from_dict(task_data)
                for task_id, task_data in tasks_data.items()
            }
            
            # Update next run times
            for task in self.tasks.values():
                task.update_next_run()
                
            logger.info(f"Loaded {len(self.tasks)} scheduled tasks from {self.tasks_file}")
        except Exception as e:
            logger.error(f"Error loading scheduled tasks: {e}")
            self.tasks = {}
    
    def _save_tasks(self) -> None:
        """Save tasks to the tasks file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            
            tasks_data = {
                task_id: task.to_dict()
                for task_id, task in self.tasks.items()
            }
            
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
                
            logger.info(f"Saved {len(self.tasks)} scheduled tasks to {self.tasks_file}")
        except Exception as e:
            logger.error(f"Error saving scheduled tasks: {e}")
    
    def add_task(self, task: ScheduledTask) -> None:
        """
        Add a task to the scheduler.
        
        Args:
            task: The task to add
        """
        if task.id in self.tasks:
            raise AutomationError(f"Task with ID {task.id} already exists")
        
        task.update_next_run()
        self.tasks[task.id] = task
        self._save_tasks()
        logger.info(f"Added task: {task.name} (ID: {task.id})")
    
    def update_task(self, task: ScheduledTask) -> None:
        """
        Update an existing task.
        
        Args:
            task: The task to update
        """
        if task.id not in self.tasks:
            raise AutomationError(f"Task with ID {task.id} does not exist")
        
        task.update_next_run()
        self.tasks[task.id] = task
        self._save_tasks()
        logger.info(f"Updated task: {task.name} (ID: {task.id})")
    
    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the scheduler.
        
        Args:
            task_id: ID of the task to remove
        """
        if task_id not in self.tasks:
            raise AutomationError(f"Task with ID {task_id} does not exist")
        
        task = self.tasks.pop(task_id)
        self._save_tasks()
        logger.info(f"Removed task: {task.name} (ID: {task.id})")
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            The task, or None if not found
        """
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[ScheduledTask]:
        """
        List all scheduled tasks.
        
        Returns:
            List of all scheduled tasks
        """
        return list(self.tasks.values())
    
    def run_task(self, task_id: str) -> None:
        """
        Run a task immediately.
        
        Args:
            task_id: ID of the task to run
        """
        if task_id not in self.tasks:
            raise AutomationError(f"Task with ID {task_id} does not exist")
        
        task = self.tasks[task_id]
        
        try:
            logger.info(f"Running task: {task.name} (ID: {task.id})")
            
            # Import here to avoid circular imports
            from url_analyzer.cli.commands import main as cli_main
            
            # Run the command
            import sys
            original_argv = sys.argv
            sys.argv = task.command
            
            try:
                cli_main()
            finally:
                sys.argv = original_argv
            
            # Update task status
            task.last_run = time.time()
            task.update_next_run()
            self._save_tasks()
            
            logger.info(f"Task completed: {task.name} (ID: {task.id})")
        except Exception as e:
            logger.error(f"Error running task {task.name} (ID: {task.id}): {e}")
            raise AutomationError(f"Error running task: {e}")
    
    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        while self.running:
            now = time.time()
            
            # Check for tasks that need to run
            for task_id, task in list(self.tasks.items()):
                if not task.enabled or task.next_run is None:
                    continue
                
                if task.next_run <= now:
                    try:
                        self.run_task(task_id)
                    except Exception as e:
                        logger.error(f"Error running scheduled task {task.name} (ID: {task.id}): {e}")
            
            # Sleep for a short time
            time.sleep(1)


# Global scheduler instance
_scheduler = None


def get_scheduler() -> TaskScheduler:
    """
    Get the global scheduler instance.
    
    Returns:
        The global scheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def schedule_task(
    name: str,
    command: List[str],
    schedule_type: str,
    schedule_params: Dict[str, Any],
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    task_id: Optional[str] = None
) -> str:
    """
    Schedule a task to run at a specified time or interval.
    
    Args:
        name: Human-readable name for the task
        command: Command to execute (as a list of arguments)
        schedule_type: Type of schedule (once, daily, weekly, monthly, interval)
        schedule_params: Parameters for the schedule (depends on schedule_type)
        description: Optional description of the task
        tags: Optional tags for categorizing tasks
        task_id: Optional task ID (generated if not provided)
        
    Returns:
        The ID of the scheduled task
    """
    # Validate schedule type
    valid_schedule_types = ['once', 'daily', 'weekly', 'monthly', 'interval']
    if schedule_type not in valid_schedule_types:
        raise AutomationError(f"Invalid schedule type: {schedule_type}. "
                             f"Must be one of: {', '.join(valid_schedule_types)}")
    
    # Validate schedule parameters
    if schedule_type == 'once' and 'timestamp' not in schedule_params:
        raise AutomationError("Schedule type 'once' requires 'timestamp' parameter")
    
    if schedule_type == 'interval' and 'minutes' not in schedule_params:
        raise AutomationError("Schedule type 'interval' requires 'minutes' parameter")
    
    # Generate task ID if not provided
    if task_id is None:
        import uuid
        task_id = str(uuid.uuid4())
    
    # Create the task
    task = ScheduledTask(
        id=task_id,
        name=name,
        command=command,
        schedule_type=schedule_type,
        schedule_params=schedule_params,
        description=description,
        tags=tags or []
    )
    
    # Add the task to the scheduler
    scheduler = get_scheduler()
    scheduler.add_task(task)
    
    return task_id


def list_scheduled_tasks() -> List[Dict[str, Any]]:
    """
    List all scheduled tasks.
    
    Returns:
        List of scheduled tasks as dictionaries
    """
    scheduler = get_scheduler()
    return [task.to_dict() for task in scheduler.list_tasks()]


def remove_scheduled_task(task_id: str) -> None:
    """
    Remove a scheduled task.
    
    Args:
        task_id: ID of the task to remove
    """
    scheduler = get_scheduler()
    scheduler.remove_task(task_id)


def run_scheduled_task(task_id: str) -> None:
    """
    Run a scheduled task immediately.
    
    Args:
        task_id: ID of the task to run
    """
    scheduler = get_scheduler()
    scheduler.run_task(task_id)


def start_scheduler() -> None:
    """Start the scheduler in a background thread."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler() -> None:
    """Stop the scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()