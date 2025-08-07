"""
Logging Module

This module provides a structured logging system for the URL Analyzer application,
with support for different log levels, file output, and contextual information.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime


# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Default log directory
DEFAULT_LOG_DIR = "logs"

# Default log file name
DEFAULT_LOG_FILE = "url_analyzer.log"

# Maximum log file size (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024

# Maximum number of backup log files
MAX_LOG_BACKUPS = 5


def setup_logging(
    log_level: Union[int, str] = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    console: bool = True,
    file_output: bool = True,
    rotation: str = "size",
    max_size: int = MAX_LOG_SIZE,
    max_backups: int = MAX_LOG_BACKUPS,
    rotation_interval: int = 1,
    rotation_when: str = "midnight",
    compress_logs: bool = False,
    log_file_pattern: Optional[str] = None,
    include_hostname: bool = False,
    include_process_id: bool = False
) -> logging.Logger:
    """
    Set up the logging system with the specified configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (if None, uses DEFAULT_LOG_FILE)
        log_format: Format string for log messages
        console: Whether to log to console
        file_output: Whether to log to file
        rotation: Log rotation strategy ("size", "time", "hourly", "daily", "weekly", "monthly")
        max_size: Maximum log file size in bytes (for "size" rotation)
        max_backups: Maximum number of backup log files
        rotation_interval: Interval for time-based rotation (default: 1)
        rotation_when: When to rotate for time-based rotation (default: "midnight")
                      Options: S=seconds, M=minutes, H=hours, D=days, W0-W6=weekday (0=Monday),
                      midnight=roll over at midnight
        compress_logs: Whether to compress rotated logs
        log_file_pattern: Pattern for log file names (e.g., "{name}_{date}.log")
                         Available variables: {name}, {date}, {hostname}, {pid}
        include_hostname: Whether to include hostname in log format
        include_process_id: Whether to include process ID in log format
        
    Returns:
        Configured logger instance
    """
    import socket
    import os
    
    # Convert string log level to numeric if needed
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), DEFAULT_LOG_LEVEL)
    
    # Create logger
    logger = logging.getLogger("url_analyzer")
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Enhance log format with hostname and process ID if requested
    enhanced_log_format = log_format
    if include_hostname or include_process_id:
        # Extract the existing format without the trailing newline if any
        format_parts = []
        if include_hostname:
            hostname = socket.gethostname()
            format_parts.append(f"host={hostname}")
        if include_process_id:
            pid = os.getpid()
            format_parts.append(f"pid={pid}")
        
        # Add the additional information to the format
        if format_parts:
            enhanced_log_format = f"{log_format} [{' '.join(format_parts)}]"
    
    # Create formatter
    formatter = logging.Formatter(enhanced_log_format)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if file_output:
        # Use default log file if none specified
        if log_file is None:
            log_dir = DEFAULT_LOG_DIR
            os.makedirs(log_dir, exist_ok=True)
            
            # Apply log file pattern if specified
            if log_file_pattern:
                # Get variables for the pattern
                now = datetime.now()
                date_str = now.strftime("%Y%m%d")
                hostname = socket.gethostname()
                pid = os.getpid()
                
                # Replace variables in the pattern
                log_filename = log_file_pattern.format(
                    name="url_analyzer",
                    date=date_str,
                    hostname=hostname,
                    pid=pid
                )
            else:
                log_filename = DEFAULT_LOG_FILE
                
            log_file = os.path.join(log_dir, log_filename)
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(os.path.abspath(log_file))
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler with appropriate rotation strategy
        if rotation.lower() == "size":
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_size, backupCount=max_backups
            )
        elif rotation.lower() in ["time", "daily", "midnight"]:
            file_handler = TimedRotatingFileHandler(
                log_file, when="midnight", interval=1, backupCount=max_backups
            )
        elif rotation.lower() == "hourly":
            file_handler = TimedRotatingFileHandler(
                log_file, when="H", interval=1, backupCount=max_backups
            )
        elif rotation.lower() == "weekly":
            file_handler = TimedRotatingFileHandler(
                log_file, when="W0", interval=1, backupCount=max_backups
            )
        elif rotation.lower() == "monthly":
            # For monthly rotation, we use day-based rotation with interval=30
            # This is an approximation since months have different numbers of days
            file_handler = TimedRotatingFileHandler(
                log_file, when="D", interval=30, backupCount=max_backups
            )
        else:
            # Custom time-based rotation
            file_handler = TimedRotatingFileHandler(
                log_file, when=rotation_when, interval=rotation_interval, 
                backupCount=max_backups
            )
        
        # Enable compression for rotated logs if requested
        if compress_logs:
            file_handler.rotator = _gzip_rotator
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def _gzip_rotator(source, dest):
    """
    Custom log rotator that compresses the rotated log file.
    
    Args:
        source: Source file path
        dest: Destination file path
    """
    import gzip
    import shutil
    
    # If the destination already exists, remove it (required by gzip module)
    if os.path.exists(dest):
        os.remove(dest)
    
    # Compress the source file to the destination
    with open(source, 'rb') as f_in:
        with gzip.open(f"{dest}.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Remove the source file
    os.remove(source)


def get_logger(name: str = "url_analyzer") -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class ContextualLogger:
    """
    A logger that adds contextual information to log messages.
    
    This enhanced logger supports:
    - Request ID tracking
    - User ID and session information
    - Performance metrics
    - System information
    - Custom context values
    """
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any] = None):
        """
        Initialize the contextual logger.
        
        Args:
            logger: Base logger to use
            context: Initial context dictionary
        """
        self.logger = logger
        self.context = context or {}
        self._timers = {}  # For tracking execution times
        
        # Add system information to context by default
        self._add_system_info()
    
    def _add_system_info(self) -> None:
        """Add system information to the context."""
        import socket
        import os
        import platform
        
        self.context.update({
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
            "python_version": platform.python_version(),
            "platform": platform.platform()
        })
    
    def add_context(self, **kwargs) -> None:
        """
        Add context values to the logger.
        
        Args:
            **kwargs: Key-value pairs to add to the context
        """
        self.context.update(kwargs)
    
    def remove_context(self, *keys) -> None:
        """
        Remove context values from the logger.
        
        Args:
            *keys: Keys to remove from the context
        """
        for key in keys:
            if key in self.context:
                del self.context[key]
    
    def set_request_id(self, request_id: str = None) -> str:
        """
        Set a request ID for tracking related log messages.
        
        Args:
            request_id: Request ID to use (if None, generates a new UUID)
            
        Returns:
            The request ID
        """
        import uuid
        
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        self.context["request_id"] = request_id
        return request_id
    
    def set_user_info(self, user_id: str = None, session_id: str = None, 
                     username: str = None, role: str = None) -> None:
        """
        Set user information for the current context.
        
        Args:
            user_id: User ID
            session_id: Session ID
            username: Username
            role: User role
        """
        if user_id:
            self.context["user_id"] = user_id
        if session_id:
            self.context["session_id"] = session_id
        if username:
            self.context["username"] = username
        if role:
            self.context["role"] = role
    
    def start_timer(self, name: str) -> None:
        """
        Start a timer for measuring execution time.
        
        Args:
            name: Name of the timer
        """
        import time
        self._timers[name] = time.time()
    
    def stop_timer(self, name: str) -> float:
        """
        Stop a timer and return the elapsed time.
        
        Args:
            name: Name of the timer
            
        Returns:
            Elapsed time in seconds
            
        Raises:
            KeyError: If the timer doesn't exist
        """
        import time
        
        if name not in self._timers:
            raise KeyError(f"Timer '{name}' not found")
        
        elapsed = time.time() - self._timers[name]
        self.context[f"time_{name}"] = f"{elapsed:.6f}s"
        del self._timers[name]
        
        return elapsed
    
    def log_performance(self, operation: str, elapsed: float, 
                       details: Dict[str, Any] = None) -> None:
        """
        Log performance information.
        
        Args:
            operation: Name of the operation
            elapsed: Elapsed time in seconds
            details: Additional details about the operation
        """
        perf_context = {
            "operation": operation,
            "elapsed": f"{elapsed:.6f}s"
        }
        
        if details:
            perf_context.update(details)
        
        # Create a temporary context with performance information
        temp_context = self.context.copy()
        temp_context.update(perf_context)
        
        # Format the message with the temporary context
        context_str = " | ".join(f"{k}={v}" for k, v in temp_context.items())
        msg = f"Performance: {operation} completed in {elapsed:.6f}s [{context_str}]"
        
        self.logger.info(msg)
    
    def _format_message(self, msg: str) -> str:
        """
        Format a message with context information.
        
        Args:
            msg: Original message
            
        Returns:
            Formatted message with context
        """
        if not self.context:
            return msg
        
        # Format context as key=value pairs
        context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
        
        # Add context to the message
        return f"{msg} [{context_str}]"
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message with context."""
        self.logger.debug(self._format_message(msg), *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an info message with context."""
        self.logger.info(self._format_message(msg), *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message with context."""
        self.logger.warning(self._format_message(msg), *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message with context."""
        self.logger.error(self._format_message(msg), *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a critical message with context."""
        self.logger.critical(self._format_message(msg), *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception message with context."""
        self.logger.exception(self._format_message(msg), *args, **kwargs)
        
    def with_context(self, **kwargs):
        """
        Context manager for temporarily adding context to the logger.
        
        Args:
            **kwargs: Context values to add
            
        Returns:
            Context manager
        """
        class LoggerContextManager:
            def __init__(self, logger, context):
                self.logger = logger
                self.context = context
                self.original_context = {}
                
            def __enter__(self):
                # Save original values
                for key, value in self.context.items():
                    if key in self.logger.context:
                        self.original_context[key] = self.logger.context[key]
                
                # Add new context
                self.logger.add_context(**self.context)
                return self.logger
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Restore original values
                for key in self.context:
                    if key in self.original_context:
                        self.logger.context[key] = self.original_context[key]
                    else:
                        del self.logger.context[key]
        
        return LoggerContextManager(self, kwargs)


def create_contextual_logger(
    name: str = "url_analyzer", context: Dict[str, Any] = None
) -> ContextualLogger:
    """
    Create a contextual logger with the specified name and context.
    
    Args:
        name: Name of the logger
        context: Initial context dictionary
        
    Returns:
        ContextualLogger instance
    """
    return ContextualLogger(get_logger(name), context)


def log_function_call(logger: Union[logging.Logger, ContextualLogger], level: int = logging.DEBUG):
    """
    Decorator to log function calls with arguments and return values.
    
    Args:
        logger: Logger to use
        level: Log level to use
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            args_str = ", ".join([str(arg) for arg in args])
            kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            params_str = ", ".join(filter(None, [args_str, kwargs_str]))
            
            logger.log(level, f"Calling {func_name}({params_str})")
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"{func_name} returned: {result}")
                return result
            except Exception as e:
                logger.exception(f"{func_name} raised exception: {e}")
                raise
        return wrapper
    return decorator


class LogAnalyzer:
    """
    A utility class for analyzing log files.
    
    This class provides functions to:
    - Parse log files
    - Search and filter logs
    - Perform statistical analysis
    - Visualize log data
    """
    
    def __init__(self, log_file: str = None, log_format: str = DEFAULT_LOG_FORMAT):
        """
        Initialize the log analyzer.
        
        Args:
            log_file: Path to the log file to analyze
            log_format: Format string for parsing log messages
        """
        self.log_file = log_file
        self.log_format = log_format
        self.log_entries = []
        self.parsed = False
        
        # Compile regex pattern for parsing log entries
        self._compile_pattern()
    
    def _compile_pattern(self) -> None:
        """Compile regex pattern for parsing log entries based on log format."""
        import re
        
        # Convert log format to regex pattern
        pattern = self.log_format
        
        # Replace format specifiers with regex groups
        # Use double backslashes to properly escape the regex patterns
        pattern = re.sub(r'%\(asctime\)s', r'(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2},\\d{3})', pattern)
        pattern = re.sub(r'%\(name\)s', r'(?P<name>[^-]+)', pattern)  # Fixed 'n' to 'name'
        pattern = re.sub(r'%\(levelname\)s', r'(?P<level>[A-Z]+)', pattern)
        pattern = re.sub(r'%\(message\)s', r'(?P<message>.*)', pattern)
        
        # Compile the pattern
        self.pattern = re.compile(pattern)
    
    def parse_file(self, log_file: str = None) -> List[Dict[str, Any]]:
        """
        Parse the log file and return a list of log entries.
        
        Args:
            log_file: Path to the log file to parse (if None, uses the one from initialization)
            
        Returns:
            List of dictionaries containing parsed log entries
        """
        import re
        from datetime import datetime
        
        if log_file:
            self.log_file = log_file
        
        if not self.log_file:
            raise ValueError("No log file specified")
        
        self.log_entries = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                current_entry = None
                
                for line in f:
                    # Try to match the line with the pattern
                    match = self.pattern.match(line)
                    
                    if match:
                        # If we have a current entry, add it to the list
                        if current_entry:
                            self.log_entries.append(current_entry)
                        
                        # Create a new entry
                        current_entry = match.groupdict()
                        
                        # Parse timestamp
                        if 'timestamp' in current_entry:
                            try:
                                current_entry['timestamp'] = datetime.strptime(
                                    current_entry['timestamp'], 
                                    '%Y-%m-%d %H:%M:%S,%f'
                                )
                            except ValueError:
                                # If timestamp format doesn't match, keep it as string
                                pass
                        
                        # Parse context from message
                        if 'message' in current_entry:
                            context_match = re.search(r'\[(.*)\]$', current_entry['message'])
                            if context_match:
                                context_str = context_match.group(1)
                                context = {}
                                
                                # Parse key=value pairs
                                for pair in context_str.split(' | '):
                                    if '=' in pair:
                                        key, value = pair.split('=', 1)
                                        context[key.strip()] = value.strip()
                                
                                current_entry['context'] = context
                                
                                # Remove context from message
                                current_entry['message'] = current_entry['message'].replace(f" [{context_str}]", "")
                    else:
                        # If the line doesn't match the pattern, it's a continuation of the previous message
                        if current_entry:
                            current_entry['message'] += f"\n{line.strip()}"
                
                # Add the last entry
                if current_entry:
                    self.log_entries.append(current_entry)
        
        except Exception as e:
            print(f"Error parsing log file: {e}")
        
        self.parsed = True
        return self.log_entries
    
    def filter_logs(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Filter log entries based on criteria.
        
        Args:
            **kwargs: Criteria for filtering (e.g., level='ERROR', name='url_analyzer')
            
        Returns:
            List of filtered log entries
        """
        if not self.parsed:
            self.parse_file()
        
        filtered = self.log_entries
        
        # Filter by basic fields
        for key, value in kwargs.items():
            if key in ['level', 'name', 'message']:
                filtered = [entry for entry in filtered if key in entry and value in entry[key]]
            elif key == 'timestamp':
                if isinstance(value, tuple) and len(value) == 2:
                    # Filter by timestamp range
                    start, end = value
                    filtered = [
                        entry for entry in filtered 
                        if 'timestamp' in entry and start <= entry['timestamp'] <= end
                    ]
                else:
                    # Filter by exact timestamp
                    filtered = [
                        entry for entry in filtered 
                        if 'timestamp' in entry and entry['timestamp'] == value
                    ]
            elif key.startswith('context.'):
                # Filter by context field
                context_key = key[8:]  # Remove 'context.' prefix
                filtered = [
                    entry for entry in filtered 
                    if 'context' in entry and context_key in entry['context'] and 
                    value in entry['context'][context_key]
                ]
        
        return filtered
    
    def search(self, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search log entries for a query string.
        
        Args:
            query: Query string to search for
            case_sensitive: Whether the search is case-sensitive
            
        Returns:
            List of matching log entries
        """
        if not self.parsed:
            self.parse_file()
        
        if not case_sensitive:
            query = query.lower()
            return [
                entry for entry in self.log_entries 
                if query in entry.get('message', '').lower() or 
                (
                    'context' in entry and 
                    any(query in str(v).lower() for v in entry['context'].values())
                )
            ]
        else:
            return [
                entry for entry in self.log_entries 
                if query in entry.get('message', '') or 
                (
                    'context' in entry and 
                    any(query in str(v) for v in entry['context'].values())
                )
            ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the log entries.
        
        Returns:
            Dictionary containing statistics
        """
        if not self.parsed:
            self.parse_file()
        
        if not self.log_entries:
            return {}
        
        from collections import Counter
        from datetime import datetime, timedelta
        
        # Count log levels
        level_counts = Counter(entry.get('level') for entry in self.log_entries if 'level' in entry)
        
        # Count log sources
        source_counts = Counter(entry.get('name') for entry in self.log_entries if 'name' in entry)
        
        # Calculate time range
        timestamps = [entry['timestamp'] for entry in self.log_entries if 'timestamp' in entry and isinstance(entry['timestamp'], datetime)]
        
        time_range = {}
        if timestamps:
            time_range = {
                'start': min(timestamps),
                'end': max(timestamps),
                'duration': str(max(timestamps) - min(timestamps))
            }
        
        # Calculate entries per hour
        entries_per_hour = {}
        for entry in self.log_entries:
            if 'timestamp' in entry and isinstance(entry['timestamp'], datetime):
                hour = entry['timestamp'].replace(minute=0, second=0, microsecond=0)
                entries_per_hour[hour] = entries_per_hour.get(hour, 0) + 1
        
        # Find most common context values
        context_values = {}
        for entry in self.log_entries:
            if 'context' in entry:
                for key, value in entry['context'].items():
                    if key not in context_values:
                        context_values[key] = Counter()
                    context_values[key][value] += 1
        
        # Get most common context values
        most_common_context = {}
        for key, counter in context_values.items():
            most_common_context[key] = counter.most_common(5)
        
        return {
            'total_entries': len(self.log_entries),
            'level_counts': dict(level_counts),
            'source_counts': dict(source_counts),
            'time_range': time_range,
            'entries_per_hour': dict(sorted(entries_per_hour.items())),
            'most_common_context': most_common_context
        }
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a report of the log analysis.
        
        Args:
            output_file: Path to the output file (if None, returns the report as a string)
            
        Returns:
            Report as a string if output_file is None, otherwise the path to the output file
        """
        if not self.parsed:
            self.parse_file()
        
        stats = self.get_statistics()
        
        # Generate report
        report = []
        report.append("# Log Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Log File: {self.log_file}")
        report.append("")
        
        report.append("## Summary")
        report.append(f"Total Entries: {stats.get('total_entries', 0)}")
        
        if 'time_range' in stats and stats['time_range']:
            report.append(f"Time Range: {stats['time_range'].get('start')} to {stats['time_range'].get('end')}")
            report.append(f"Duration: {stats['time_range'].get('duration')}")
        
        report.append("")
        report.append("## Log Levels")
        for level, count in stats.get('level_counts', {}).items():
            report.append(f"- {level}: {count}")
        
        report.append("")
        report.append("## Log Sources")
        for source, count in stats.get('source_counts', {}).items():
            report.append(f"- {source}: {count}")
        
        report.append("")
        report.append("## Most Common Context Values")
        for key, values in stats.get('most_common_context', {}).items():
            report.append(f"### {key}")
            for value, count in values:
                report.append(f"- {value}: {count}")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                return output_file
            except Exception as e:
                print(f"Error writing report to file: {e}")
                return report_text
        else:
            return report_text
    
    def visualize(self, output_file: str = None):
        """
        Generate visualizations of the log data.
        
        Args:
            output_file: Path to the output file (if None, displays the visualizations)
            
        Returns:
            Path to the output file if output_file is not None
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter
            import numpy as np
        except ImportError:
            print("Matplotlib is required for visualization. Install it with 'pip install matplotlib'.")
            return None
        
        if not self.parsed:
            self.parse_file()
        
        stats = self.get_statistics()
        
        # Create figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f"Log Analysis: {self.log_file}", fontsize=16)
        
        # Plot log levels
        level_counts = stats.get('level_counts', {})
        if level_counts:
            axs[0, 0].bar(level_counts.keys(), level_counts.values())
            axs[0, 0].set_title("Log Levels")
            axs[0, 0].set_ylabel("Count")
            axs[0, 0].tick_params(axis='x', rotation=45)
        
        # Plot log sources
        source_counts = stats.get('source_counts', {})
        if source_counts:
            axs[0, 1].bar(source_counts.keys(), source_counts.values())
            axs[0, 1].set_title("Log Sources")
            axs[0, 1].set_ylabel("Count")
            axs[0, 1].tick_params(axis='x', rotation=45)
        
        # Plot entries per hour
        entries_per_hour = stats.get('entries_per_hour', {})
        if entries_per_hour:
            hours = list(entries_per_hour.keys())
            counts = list(entries_per_hour.values())
            
            axs[1, 0].plot(hours, counts, marker='o')
            axs[1, 0].set_title("Entries per Hour")
            axs[1, 0].set_ylabel("Count")
            axs[1, 0].set_xlabel("Time")
            axs[1, 0].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
            axs[1, 0].tick_params(axis='x', rotation=45)
        
        # Plot most common context value
        most_common_context = stats.get('most_common_context', {})
        if most_common_context:
            # Find the context key with the most values
            max_key = max(most_common_context.items(), key=lambda x: sum(count for _, count in x[1]))[0]
            values = most_common_context[max_key]
            
            labels = [str(value) for value, _ in values]
            counts = [count for _, count in values]
            
            axs[1, 1].pie(counts, labels=labels, autopct='%1.1f%%')
            axs[1, 1].set_title(f"Most Common {max_key}")
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
            plt.close()
            return output_file
        else:
            plt.show()
            return None


# Initialize the default logger
default_logger = setup_logging()