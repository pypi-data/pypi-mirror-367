"""
File-based Logging Service

This module provides a file-based implementation of the LoggingService interface.
It logs messages to a file with timestamp and log level.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from url_analyzer.application.interfaces import LoggingService


class FileLoggingService(LoggingService):
    """
    File-based implementation of the LoggingService interface.
    
    This class logs messages to a file with timestamp and log level.
    """
    
    def __init__(self, log_file: str, log_level: int = logging.INFO):
        """
        Initialize the logging service with a log file.
        
        Args:
            log_file: Path to the log file
            log_level: Logging level (default: INFO)
        """
        self.log_file = log_file
        
        # Create the directory if it doesn't exist
        directory = os.path.dirname(log_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Configure logging
        self.logger = logging.getLogger('url_analyzer')
        self.logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def _format_context(self, **kwargs) -> str:
        """
        Format context information for logging.
        
        Args:
            **kwargs: Context information
            
        Returns:
            Formatted context string
        """
        if not kwargs:
            return ''
        
        context_parts = []
        for key, value in kwargs.items():
            context_parts.append(f"{key}={value}")
        
        return ' [' + ', '.join(context_parts) + ']'
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.debug(f"{message}{context}")
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.info(f"{message}{context}")
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.warning(f"{message}{context}")
    
    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.error(f"{message}{context}")
    
    def critical(self, message: str, **kwargs) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.critical(f"{message}{context}")


class ConsoleLoggingService(LoggingService):
    """
    Console-based implementation of the LoggingService interface.
    
    This class logs messages to the console with timestamp and log level.
    """
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize the logging service.
        
        Args:
            log_level: Logging level (default: INFO)
        """
        # Configure logging
        self.logger = logging.getLogger('url_analyzer_console')
        self.logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def _format_context(self, **kwargs) -> str:
        """
        Format context information for logging.
        
        Args:
            **kwargs: Context information
            
        Returns:
            Formatted context string
        """
        if not kwargs:
            return ''
        
        context_parts = []
        for key, value in kwargs.items():
            context_parts.append(f"{key}={value}")
        
        return ' [' + ', '.join(context_parts) + ']'
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.debug(f"{message}{context}")
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.info(f"{message}{context}")
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.warning(f"{message}{context}")
    
    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.error(f"{message}{context}")
    
    def critical(self, message: str, **kwargs) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        context = self._format_context(**kwargs)
        self.logger.critical(f"{message}{context}")


class CompositeLoggingService(LoggingService):
    """
    Composite implementation of the LoggingService interface.
    
    This class delegates logging to multiple logging services.
    """
    
    def __init__(self, logging_services: list[LoggingService]):
        """
        Initialize the composite logging service.
        
        Args:
            logging_services: List of logging services to delegate to
        """
        self.logging_services = logging_services
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        for service in self.logging_services:
            service.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        for service in self.logging_services:
            service.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        for service in self.logging_services:
            service.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        for service in self.logging_services:
            service.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        for service in self.logging_services:
            service.critical(message, **kwargs)