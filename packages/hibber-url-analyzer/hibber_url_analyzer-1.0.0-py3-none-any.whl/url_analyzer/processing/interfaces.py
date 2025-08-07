"""
Data Processing Interfaces

This module defines interfaces for the Data Processing domain.
These interfaces ensure proper separation of concerns and enable dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union

import pandas as pd

from url_analyzer.processing.domain import (
    DataSource, DataSink, ProcessingOptions, ProcessingJob, ProcessingResult
)


class DataReader(ABC):
    """Interface for data readers."""
    
    @abstractmethod
    def read_data(self, source: DataSource) -> pd.DataFrame:
        """
        Read data from a source.
        
        Args:
            source: Data source to read from
            
        Returns:
            DataFrame containing the data
        """
        pass
    
    @abstractmethod
    def get_supported_source_types(self) -> Set[str]:
        """
        Get the source types supported by this reader.
        
        Returns:
            Set of supported source types
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this reader.
        
        Returns:
            Reader name
        """
        pass


class DataWriter(ABC):
    """Interface for data writers."""
    
    @abstractmethod
    def write_data(self, data: pd.DataFrame, sink: DataSink) -> bool:
        """
        Write data to a sink.
        
        Args:
            data: DataFrame containing the data to write
            sink: Data sink to write to
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_sink_types(self) -> Set[str]:
        """
        Get the sink types supported by this writer.
        
        Returns:
            Set of supported sink types
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this writer.
        
        Returns:
            Writer name
        """
        pass


class DataProcessor(ABC):
    """Interface for data processors."""
    
    @abstractmethod
    def process_data(self, data: pd.DataFrame, options: ProcessingOptions) -> pd.DataFrame:
        """
        Process data.
        
        Args:
            data: DataFrame containing the data to process
            options: Options for the processing
            
        Returns:
            DataFrame containing the processed data
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this processor.
        
        Returns:
            Processor name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the description of this processor.
        
        Returns:
            Processor description
        """
        pass


class JobRepository(ABC):
    """Interface for job repositories."""
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: ID of the job to get
            
        Returns:
            ProcessingJob or None if not found
        """
        pass
    
    @abstractmethod
    def get_jobs(self) -> List[ProcessingJob]:
        """
        Get all jobs.
        
        Returns:
            List of jobs
        """
        pass
    
    @abstractmethod
    def save_job(self, job: ProcessingJob) -> None:
        """
        Save a job.
        
        Args:
            job: Job to save
        """
        pass
    
    @abstractmethod
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_active_jobs(self) -> List[ProcessingJob]:
        """
        Get all active jobs.
        
        Returns:
            List of active jobs
        """
        pass


class ResultRepository(ABC):
    """Interface for result repositories."""
    
    @abstractmethod
    def get_result(self, job_id: str) -> Optional[ProcessingResult]:
        """
        Get a result by job ID.
        
        Args:
            job_id: ID of the job to get the result for
            
        Returns:
            ProcessingResult or None if not found
        """
        pass
    
    @abstractmethod
    def save_result(self, result: ProcessingResult) -> None:
        """
        Save a result.
        
        Args:
            result: Result to save
        """
        pass
    
    @abstractmethod
    def delete_result(self, job_id: str) -> bool:
        """
        Delete a result.
        
        Args:
            job_id: ID of the job to delete the result for
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_results(self) -> List[ProcessingResult]:
        """
        Get all results.
        
        Returns:
            List of results
        """
        pass


class BatchProcessingService(ABC):
    """Interface for batch processing services."""
    
    @abstractmethod
    def create_job(self, source: DataSource, sink: DataSink, name: Optional[str] = None, options: Optional[ProcessingOptions] = None) -> ProcessingJob:
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
        pass
    
    @abstractmethod
    def start_job(self, job_id: str) -> bool:
        """
        Start a job.
        
        Args:
            job_id: ID of the job to start
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a job.
        
        Args:
            job_id: ID of the job to get the status for
            
        Returns:
            Dictionary containing the job status or None if not found
        """
        pass
    
    @abstractmethod
    def get_job_result(self, job_id: str) -> Optional[ProcessingResult]:
        """
        Get the result of a job.
        
        Args:
            job_id: ID of the job to get the result for
            
        Returns:
            ProcessingResult or None if not found
        """
        pass
    
    @abstractmethod
    def process_data(self, data: pd.DataFrame, options: ProcessingOptions) -> pd.DataFrame:
        """
        Process data directly without creating a job.
        
        Args:
            data: DataFrame containing the data to process
            options: Options for the processing
            
        Returns:
            DataFrame containing the processed data
        """
        pass
    
    @abstractmethod
    def process_file(self, source_path: str, sink_path: str, options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """
        Process a file directly without creating a job.
        
        Args:
            source_path: Path to the source file
            sink_path: Path to the sink file
            options: Optional processing options
            
        Returns:
            ProcessingResult containing the result of the processing
        """
        pass