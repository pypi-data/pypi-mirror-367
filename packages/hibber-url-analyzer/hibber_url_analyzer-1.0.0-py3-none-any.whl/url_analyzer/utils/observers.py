"""
Progress Tracking Observer Module

This module provides observer pattern implementations for progress tracking.
It defines ProgressSubject and ProgressObserver interfaces and concrete
implementations for different progress tracking approaches.
"""

from abc import ABC, abstractmethod
import time
from typing import List, Any, Optional, Dict, Callable, Union

from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Check if Rich is available
try:
    from rich.progress import Progress, Task
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logger.debug("Rich library not available, RichProgressObserver will be disabled")


class ProgressObserver(ABC):
    """
    Abstract base class for progress observers.
    
    This class defines the interface that all progress observers must implement.
    """
    
    @abstractmethod
    def update(self, progress: float, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the observer with progress information.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
            data: Optional additional data about the progress
        """
        pass
    
    @abstractmethod
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        pass
    
    @abstractmethod
    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish progress tracking.
        
        Args:
            message: Optional message describing the completion
        """
        pass


class ProgressSubject(ABC):
    """
    Abstract base class for progress subjects.
    
    This class defines the interface that all progress subjects must implement.
    """
    
    def __init__(self):
        """
        Initialize the progress subject.
        """
        self._observers: List[ProgressObserver] = []
    
    def attach(self, observer: ProgressObserver) -> None:
        """
        Attach an observer to this subject.
        
        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: ProgressObserver) -> None:
        """
        Detach an observer from this subject.
        
        Args:
            observer: Observer to detach
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, progress: float, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Notify all observers of progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
            data: Optional additional data about the progress
        """
        for observer in self._observers:
            observer.update(progress, message, data)
    
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        self._total = total
        for observer in self._observers:
            observer.start(total, description)
    
    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish progress tracking.
        
        Args:
            message: Optional message describing the completion
        """
        for observer in self._observers:
            observer.finish(message)


class ConsoleProgressObserver(ProgressObserver):
    """
    Console-based progress observer.
    
    This observer displays progress information in the console.
    """
    
    def __init__(self, show_percentage: bool = True, show_bar: bool = True, width: int = 50):
        """
        Initialize the console progress observer.
        
        Args:
            show_percentage: Whether to show percentage
            show_bar: Whether to show progress bar
            width: Width of the progress bar
        """
        self.show_percentage = show_percentage
        self.show_bar = show_bar
        self.width = width
        self.total = 0
        self.current = 0
        self.description = None
    
    def update(self, progress: float, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the observer with progress information.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
            data: Optional additional data about the progress
        """
        self.current = int(progress * self.total) if self.total > 0 else 0
        
        # Create progress bar
        if self.show_bar:
            filled_width = int(self.width * progress)
            bar = f"[{'#' * filled_width}{' ' * (self.width - filled_width)}]"
        else:
            bar = ""
        
        # Create percentage
        if self.show_percentage:
            percentage = f"{progress * 100:.1f}%"
        else:
            percentage = ""
        
        # Create message
        if message:
            msg = f" {message}"
        else:
            msg = ""
        
        # Print progress
        print(f"\r{self.description or 'Processing'}: {bar} {percentage}{msg}", end="")
    
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        self.total = total
        self.current = 0
        self.description = description or "Processing"
        print(f"{self.description} started...")
    
    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish progress tracking.
        
        Args:
            message: Optional message describing the completion
        """
        if message:
            print(f"\n{self.description} completed: {message}")
        else:
            print(f"\n{self.description} completed.")


class LoggingProgressObserver(ProgressObserver):
    """
    Logging-based progress observer.
    
    This observer logs progress information using the logging module.
    """
    
    def __init__(self, log_interval: float = 0.1):
        """
        Initialize the logging progress observer.
        
        Args:
            log_interval: Minimum progress interval between log entries
        """
        self.log_interval = log_interval
        self.total = 0
        self.current = 0
        self.description = None
        self.last_logged_progress = -1.0
    
    def update(self, progress: float, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the observer with progress information.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
            data: Optional additional data about the progress
        """
        self.current = int(progress * self.total) if self.total > 0 else 0
        
        # Only log if progress has increased by at least log_interval
        if progress - self.last_logged_progress >= self.log_interval:
            if message:
                logger.info(f"{self.description}: {progress * 100:.1f}% - {message}")
            else:
                logger.info(f"{self.description}: {progress * 100:.1f}%")
            self.last_logged_progress = progress
    
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        self.total = total
        self.current = 0
        self.description = description or "Processing"
        self.last_logged_progress = -1.0
        logger.info(f"{self.description} started (total: {total})")
    
    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish progress tracking.
        
        Args:
            message: Optional message describing the completion
        """
        if message:
            logger.info(f"{self.description} completed: {message}")
        else:
            logger.info(f"{self.description} completed")


class TqdmProgressObserver(ProgressObserver):
    """
    TQDM-based progress observer.
    
    This observer displays progress using the tqdm library.
    """
    
    def __init__(self):
        """
        Initialize the tqdm progress observer.
        """
        self.tqdm = None
        self.total = 0
        self.current = 0
        self.description = None
    
    def update(self, progress: float, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the observer with progress information.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
            data: Optional additional data about the progress
        """
        if self.tqdm is None:
            return
        
        new_current = int(progress * self.total) if self.total > 0 else 0
        increment = new_current - self.current
        
        if increment > 0:
            self.tqdm.update(increment)
            self.current = new_current
        
        if message:
            self.tqdm.set_description(message)
    
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        try:
            from tqdm import tqdm
            self.total = total
            self.current = 0
            self.description = description or "Processing"
            self.tqdm = tqdm(total=total, desc=self.description)
        except ImportError:
            logger.warning("tqdm not installed. Using console progress observer instead.")
            self.tqdm = None
    
    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish progress tracking.
        
        Args:
            message: Optional message describing the completion
        """
        if self.tqdm is not None:
            self.tqdm.close()
            if message:
                print(f"{self.description} completed: {message}")


class ProgressTracker(ProgressSubject):
    """
    Progress tracker for monitoring progress of operations.
    
    This class tracks progress and notifies observers of changes.
    """
    
    def __init__(self, total: int = 0, description: Optional[str] = None):
        """
        Initialize the progress tracker.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        super().__init__()
        self._total = total
        self._current = 0
        self._description = description
    
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        self._total = total
        self._current = 0
        self._description = description
        super().start(total, description)
    
    def increment(self, amount: int = 1, message: Optional[str] = None) -> None:
        """
        Increment progress by the given amount.
        
        Args:
            amount: Amount to increment progress by
            message: Optional message describing the current progress
        """
        self._current += amount
        progress = self._current / self._total if self._total > 0 else 0
        self.notify(progress, message)
    
    def update(self, current: int, message: Optional[str] = None) -> None:
        """
        Update progress to the given current value.
        
        Args:
            current: Current progress value
            message: Optional message describing the current progress
        """
        self._current = current
        progress = self._current / self._total if self._total > 0 else 0
        self.notify(progress, message)
    
    def set_progress(self, progress: float, message: Optional[str] = None) -> None:
        """
        Set progress to the given value.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
        """
        self._current = int(progress * self._total) if self._total > 0 else 0
        self.notify(progress, message)
    
    @property
    def progress(self) -> float:
        """
        Get the current progress.
        
        Returns:
            Progress value between 0.0 and 1.0
        """
        return self._current / self._total if self._total > 0 else 0
    
    @property
    def total(self) -> int:
        """
        Get the total number of items to process.
        
        Returns:
            Total number of items
        """
        return self._total
    
    @property
    def current(self) -> int:
        """
        Get the current progress value.
        
        Returns:
            Current progress value
        """
        return self._current


class RichProgressObserver(ProgressObserver):
    """
    Rich-based progress observer.
    
    This observer displays progress using the Rich library's Progress class.
    It provides a more visually appealing progress display with colors,
    spinners, and other rich formatting.
    """
    
    def __init__(self, progress: Optional['Progress'] = None, task_id: Optional[int] = None):
        """
        Initialize the Rich progress observer.
        
        Args:
            progress: Optional Rich Progress instance to use
            task_id: Optional task ID if progress is provided
        """
        if not RICH_AVAILABLE:
            logger.warning("Rich library not available, RichProgressObserver will not function")
            self.progress = None
            self.task_id = None
            return
            
        self.progress = progress
        self.task_id = task_id
        self.total = 0
        self.current = 0
        self.description = None
        self._external_progress = progress is not None
    
    def update(self, progress: float, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the observer with progress information.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message describing the current progress
            data: Optional additional data about the progress
        """
        if not RICH_AVAILABLE or self.progress is None or self.task_id is None:
            return
        
        new_current = int(progress * self.total) if self.total > 0 else 0
        
        # Calculate processing rate
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        if time_diff >= 0.5:  # Update rate every 0.5 seconds
            value_diff = new_current - self.last_update_value
            if time_diff > 0:
                self.rate = value_diff / time_diff
            self.last_update_time = current_time
            self.last_update_value = new_current
        
        # Prepare context information
        context = ""
        if data:
            # Extract relevant information from data
            if 'file_size' in data:
                size_mb = data['file_size'] / (1024 * 1024)
                context += f"Size: {size_mb:.2f} MB "
            if 'rows' in data:
                context += f"Rows: {data['rows']} "
            if 'columns' in data:
                context += f"Cols: {data['columns']} "
            if 'memory_usage' in data:
                mem_mb = data['memory_usage'] / (1024 * 1024)
                context += f"Mem: {mem_mb:.2f} MB "
        
        # Update the task description if a message is provided
        if message:
            self.progress.update(self.task_id, description=f"{self.description}: {message}")
        
        # Update the task progress, speed, and context
        self.progress.update(
            self.task_id, 
            completed=new_current,
            speed=self.rate,
            context=context
        )
        self.current = new_current
    
    def start(self, total: int, description: Optional[str] = None) -> None:
        """
        Start progress tracking with the given total.
        
        Args:
            total: Total number of items to process
            description: Optional description of the task
        """
        if not RICH_AVAILABLE:
            return
            
        self.total = total
        self.current = 0
        self.description = description or "Processing"
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_update_value = 0
        self.rate = 0.0
        
        # If no external progress was provided, create one
        if not self._external_progress:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, ProgressColumn
            from rich.text import Text
            
            class RateColumn(ProgressColumn):
                """Renders the processing rate."""
                def render(self, task):
                    """Show processing rate."""
                    if task.speed is None:
                        return Text("?", style="progress.percentage")
                    return Text(f"{task.speed:.2f}/s", style="progress.percentage")
            
            class ContextColumn(ProgressColumn):
                """Renders additional context information."""
                def render(self, task):
                    """Show context information."""
                    context = task.fields.get("context", "")
                    return Text(context, style="blue")
            
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}[/bold blue]"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                RateColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                ContextColumn(),
            )
            self.progress.start()
        
        # Add a new task if no task_id was provided
        if self.task_id is None:
            self.task_id = self.progress.add_task(self.description, total=total, completed=0, context="")
    
    def finish(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Finish progress tracking.
        
        Args:
            message: Optional message describing the completion
            data: Optional additional data about the completion
        """
        if not RICH_AVAILABLE or self.progress is None or self.task_id is None:
            return
            
        # Update the task to 100% completion
        self.progress.update(self.task_id, completed=self.total)
        
        # If we created the progress instance, stop it
        if not self._external_progress:
            self.progress.stop()
            
            # Calculate total time and processing rate
            total_time = time.time() - self.start_time
            avg_rate = self.total / total_time if total_time > 0 else 0
            
            # Create a summary panel with statistics
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            
            console = Console()
            
            # Create a table for the summary statistics
            table = Table(show_header=False, box=None)
            table.add_column("Statistic", style="bold blue")
            table.add_column("Value")
            
            # Add basic statistics
            table.add_row("Total items", f"{self.total:,}")
            table.add_row("Total time", f"{total_time:.2f} seconds")
            table.add_row("Average rate", f"{avg_rate:.2f} items/second")
            
            # Add additional statistics from data
            if data:
                if 'file_size' in data:
                    size_mb = data['file_size'] / (1024 * 1024)
                    table.add_row("File size", f"{size_mb:.2f} MB")
                if 'rows' in data:
                    table.add_row("Rows processed", f"{data['rows']:,}")
                if 'columns' in data:
                    table.add_row("Columns", f"{data['columns']}")
                if 'memory_usage' in data:
                    mem_mb = data['memory_usage'] / (1024 * 1024)
                    table.add_row("Memory usage", f"{mem_mb:.2f} MB")
                if 'errors' in data:
                    table.add_row("Errors", f"{data['errors']}")
                if 'warnings' in data:
                    table.add_row("Warnings", f"{data['warnings']}")
            
            # Create the panel with the table
            title = f"✅ {self.description} completed"
            if message:
                title += f": {message}"
                
            panel = Panel(
                table,
                title=title,
                border_style="green",
                padding=(1, 2)
            )
            
            # Print the panel
            console.print(panel)


def create_progress_tracker(total: int = 0, description: Optional[str] = None,
                           console: bool = True, logging: bool = True, tqdm: bool = True,
                           rich: bool = True) -> ProgressTracker:
    """
    Create a progress tracker with the specified observers.
    
    Args:
        total: Total number of items to process
        description: Optional description of the task
        console: Whether to add a console observer
        logging: Whether to add a logging observer
        tqdm: Whether to add a tqdm observer
        rich: Whether to add a rich observer
        
    Returns:
        ProgressTracker instance
    """
    tracker = ProgressTracker(total, description)
    
    if console:
        tracker.attach(ConsoleProgressObserver())
    
    if logging:
        tracker.attach(LoggingProgressObserver())
    
    if tqdm:
        tracker.attach(TqdmProgressObserver())
    
    if rich and RICH_AVAILABLE:
        tracker.attach(RichProgressObserver())
    
    return tracker


def create_pandas_progress_callback(tracker: ProgressTracker) -> Callable[[int, int, Optional[str]], None]:
    """
    Create a callback function for pandas progress_apply.
    
    Args:
        tracker: ProgressTracker instance
        
    Returns:
        Callback function for pandas progress_apply
    """
    def callback(current: int, total: int, message: Optional[str] = None) -> None:
        """
        Callback function for pandas progress_apply.
        
        Args:
            current: Current progress value
            total: Total number of items to process
            message: Optional message describing the current progress
        """
        if tracker.total != total:
            tracker.start(total, tracker._description)
        tracker.update(current, message)
        if current >= total:
            tracker.finish()
    
    return callback