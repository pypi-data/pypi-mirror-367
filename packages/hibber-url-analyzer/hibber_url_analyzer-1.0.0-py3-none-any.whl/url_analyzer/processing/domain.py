"""
Data Processing Domain Models

This module defines the domain models and value objects for the Data Processing domain.
These models represent the core concepts in data processing and encapsulate domain logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Union
import os
import uuid

import pandas as pd


class DataSourceType(Enum):
    """Enumeration of data source types."""
    
    CSV = auto()
    EXCEL = auto()
    JSON = auto()
    DATABASE = auto()
    API = auto()
    TEXT = auto()
    CUSTOM = auto()


class DataSinkType(Enum):
    """Enumeration of data sink types."""
    
    CSV = auto()
    EXCEL = auto()
    JSON = auto()
    DATABASE = auto()
    HTML = auto()
    PDF = auto()
    CUSTOM = auto()


class ProcessingStatus(Enum):
    """Enumeration of processing job statuses."""
    
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass(frozen=True)
class DataSource:
    """Value object representing a data source."""
    
    source_id: str
    name: str
    source_type: DataSourceType
    location: str
    options: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_csv_source(cls, file_path: str, name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> 'DataSource':
        """
        Create a CSV data source.
        
        Args:
            file_path: Path to the CSV file
            name: Optional name for the source
            options: Optional options for reading the CSV file
            
        Returns:
            DataSource instance
        """
        source_id = str(uuid.uuid4())
        name = name or os.path.basename(file_path)
        options = options or {}
        
        return cls(
            source_id=source_id,
            name=name,
            source_type=DataSourceType.CSV,
            location=file_path,
            options=options
        )
    
    @classmethod
    def create_excel_source(cls, file_path: str, name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> 'DataSource':
        """
        Create an Excel data source.
        
        Args:
            file_path: Path to the Excel file
            name: Optional name for the source
            options: Optional options for reading the Excel file
            
        Returns:
            DataSource instance
        """
        source_id = str(uuid.uuid4())
        name = name or os.path.basename(file_path)
        options = options or {}
        
        return cls(
            source_id=source_id,
            name=name,
            source_type=DataSourceType.EXCEL,
            location=file_path,
            options=options
        )
    
    @property
    def is_file_based(self) -> bool:
        """
        Check if this source is file-based.
        
        Returns:
            True if the source is file-based, False otherwise
        """
        return self.source_type in {DataSourceType.CSV, DataSourceType.EXCEL, DataSourceType.JSON, DataSourceType.TEXT}
    
    @property
    def file_exists(self) -> bool:
        """
        Check if the source file exists.
        
        Returns:
            True if the source file exists, False otherwise
        """
        if not self.is_file_based:
            return False
        
        return os.path.exists(self.location)


@dataclass(frozen=True)
class DataSink:
    """Value object representing a data sink."""
    
    sink_id: str
    name: str
    sink_type: DataSinkType
    location: str
    options: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_csv_sink(cls, file_path: str, name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> 'DataSink':
        """
        Create a CSV data sink.
        
        Args:
            file_path: Path to the CSV file
            name: Optional name for the sink
            options: Optional options for writing the CSV file
            
        Returns:
            DataSink instance
        """
        sink_id = str(uuid.uuid4())
        name = name or os.path.basename(file_path)
        options = options or {}
        
        return cls(
            sink_id=sink_id,
            name=name,
            sink_type=DataSinkType.CSV,
            location=file_path,
            options=options
        )
    
    @classmethod
    def create_excel_sink(cls, file_path: str, name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> 'DataSink':
        """
        Create an Excel data sink.
        
        Args:
            file_path: Path to the Excel file
            name: Optional name for the sink
            options: Optional options for writing the Excel file
            
        Returns:
            DataSink instance
        """
        sink_id = str(uuid.uuid4())
        name = name or os.path.basename(file_path)
        options = options or {}
        
        return cls(
            sink_id=sink_id,
            name=name,
            sink_type=DataSinkType.EXCEL,
            location=file_path,
            options=options
        )
    
    @classmethod
    def create_html_sink(cls, file_path: str, name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> 'DataSink':
        """
        Create an HTML data sink.
        
        Args:
            file_path: Path to the HTML file
            name: Optional name for the sink
            options: Optional options for writing the HTML file
            
        Returns:
            DataSink instance
        """
        sink_id = str(uuid.uuid4())
        name = name or os.path.basename(file_path)
        options = options or {}
        
        return cls(
            sink_id=sink_id,
            name=name,
            sink_type=DataSinkType.HTML,
            location=file_path,
            options=options
        )
    
    @property
    def is_file_based(self) -> bool:
        """
        Check if this sink is file-based.
        
        Returns:
            True if the sink is file-based, False otherwise
        """
        return self.sink_type in {DataSinkType.CSV, DataSinkType.EXCEL, DataSinkType.JSON, DataSinkType.HTML, DataSinkType.PDF}
    
    @property
    def directory_exists(self) -> bool:
        """
        Check if the sink directory exists.
        
        Returns:
            True if the sink directory exists, False otherwise
        """
        if not self.is_file_based:
            return False
        
        return os.path.exists(os.path.dirname(self.location))


@dataclass(frozen=True)
class ProcessingOptions:
    """Value object representing options for data processing."""
    
    url_column: str = "url"
    batch_size: int = 1000
    max_workers: int = 10
    timeout: int = 10
    follow_redirects: bool = True
    user_agent: str = "URL Analyzer"
    include_metadata: bool = True
    include_content: bool = False
    include_headers: bool = False
    max_retries: int = 3
    retry_delay: int = 1
    show_progress: bool = True
    
    def with_batch_size(self, batch_size: int) -> 'ProcessingOptions':
        """
        Create a new options object with a different batch size.
        
        Args:
            batch_size: New batch size value
            
        Returns:
            New ProcessingOptions instance with the updated batch size
        """
        return ProcessingOptions(
            url_column=self.url_column,
            batch_size=batch_size,
            max_workers=self.max_workers,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            user_agent=self.user_agent,
            include_metadata=self.include_metadata,
            include_content=self.include_content,
            include_headers=self.include_headers,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            show_progress=self.show_progress
        )
    
    def with_max_workers(self, max_workers: int) -> 'ProcessingOptions':
        """
        Create a new options object with a different max workers value.
        
        Args:
            max_workers: New max workers value
            
        Returns:
            New ProcessingOptions instance with the updated max workers
        """
        return ProcessingOptions(
            url_column=self.url_column,
            batch_size=self.batch_size,
            max_workers=max_workers,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            user_agent=self.user_agent,
            include_metadata=self.include_metadata,
            include_content=self.include_content,
            include_headers=self.include_headers,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            show_progress=self.show_progress
        )


@dataclass
class ProcessingJob:
    """Entity representing a data processing job."""
    
    job_id: str
    name: str
    source: DataSource
    sink: DataSink
    options: ProcessingOptions
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    result_stats: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, source: DataSource, sink: DataSink, name: Optional[str] = None, options: Optional[ProcessingOptions] = None) -> 'ProcessingJob':
        """
        Create a new processing job.
        
        Args:
            source: Data source
            sink: Data sink
            name: Optional name for the job
            options: Optional processing options
            
        Returns:
            ProcessingJob instance
        """
        job_id = str(uuid.uuid4())
        name = name or f"Job {job_id[:8]}"
        options = options or ProcessingOptions()
        
        return cls(
            job_id=job_id,
            name=name,
            source=source,
            sink=sink,
            options=options
        )
    
    def start(self) -> None:
        """Mark the job as started."""
        self.status = ProcessingStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, result_stats: Dict[str, Any]) -> None:
        """
        Mark the job as completed.
        
        Args:
            result_stats: Statistics about the processing results
        """
        self.status = ProcessingStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 1.0
        self.result_stats = result_stats
    
    def fail(self, error_message: str) -> None:
        """
        Mark the job as failed.
        
        Args:
            error_message: Error message describing the failure
        """
        self.status = ProcessingStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
    
    def cancel(self) -> None:
        """Mark the job as cancelled."""
        self.status = ProcessingStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def update_progress(self, progress: float) -> None:
        """
        Update the job progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
        """
        self.progress = max(0.0, min(1.0, progress))
    
    @property
    def duration(self) -> Optional[float]:
        """
        Get the job duration in seconds.
        
        Returns:
            Duration in seconds or None if the job hasn't started
        """
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def is_active(self) -> bool:
        """
        Check if the job is active.
        
        Returns:
            True if the job is pending or running, False otherwise
        """
        return self.status in {ProcessingStatus.PENDING, ProcessingStatus.RUNNING}
    
    @property
    def is_completed(self) -> bool:
        """
        Check if the job is completed.
        
        Returns:
            True if the job is completed, False otherwise
        """
        return self.status == ProcessingStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """
        Check if the job is failed.
        
        Returns:
            True if the job is failed, False otherwise
        """
        return self.status == ProcessingStatus.FAILED
    
    @property
    def is_cancelled(self) -> bool:
        """
        Check if the job is cancelled.
        
        Returns:
            True if the job is cancelled, False otherwise
        """
        return self.status == ProcessingStatus.CANCELLED


@dataclass(frozen=True)
class ProcessingResult:
    """Value object representing the result of a data processing operation."""
    
    job: ProcessingJob
    data: Optional[pd.DataFrame] = None
    success: bool = True
    error_message: Optional[str] = None
    stats: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """
        Check if the processing was successful.
        
        Returns:
            True if the processing was successful, False otherwise
        """
        return self.success and self.data is not None
    
    @property
    def row_count(self) -> int:
        """
        Get the number of rows in the result data.
        
        Returns:
            Number of rows or 0 if no data
        """
        return len(self.data) if self.data is not None else 0
    
    @property
    def column_count(self) -> int:
        """
        Get the number of columns in the result data.
        
        Returns:
            Number of columns or 0 if no data
        """
        return len(self.data.columns) if self.data is not None else 0
    
    @property
    def has_stats(self) -> bool:
        """
        Check if the result has statistics.
        
        Returns:
            True if the result has statistics, False otherwise
        """
        return bool(self.stats)