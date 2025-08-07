"""
Data Processing Services

This module provides services for data processing based on the interfaces
defined in the interfaces module. It implements the core functionality for
processing data files containing URLs.
"""

import os
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from threading import Lock

from url_analyzer.utils.optimized_concurrency import optimized_thread_pool, create_optimized_executor

import pandas as pd
from tqdm.auto import tqdm

from url_analyzer.processing.domain import (
    DataSource, DataSink, ProcessingOptions, ProcessingJob, ProcessingResult,
    DataSourceType, DataSinkType, ProcessingStatus
)
from url_analyzer.processing.interfaces import (
    DataReader, DataWriter, DataProcessor, JobRepository, ResultRepository,
    BatchProcessingService
)
from url_analyzer.classification import URLClassifier


class CSVDataReader(DataReader):
    """
    Data reader for CSV files.
    """
    
    def __init__(self, name: str = "CSV Data Reader"):
        """
        Initialize the reader.
        
        Args:
            name: Name of this reader
        """
        self._name = name
    
    def read_data(self, source: DataSource) -> pd.DataFrame:
        """
        Read data from a CSV file.
        
        Args:
            source: Data source to read from
            
        Returns:
            DataFrame containing the data
        """
        # Check if source is a CSV file
        if source.source_type != DataSourceType.CSV:
            raise ValueError(f"Source type {source.source_type} is not supported by {self._name}")
        
        # Check if file exists
        if not source.file_exists:
            raise FileNotFoundError(f"File {source.location} does not exist")
        
        # Read the CSV file
        options = source.options.copy()
        return pd.read_csv(source.location, **options)
    
    def get_supported_source_types(self) -> Set[str]:
        """
        Get the source types supported by this reader.
        
        Returns:
            Set of supported source types
        """
        return {DataSourceType.CSV.name}
    
    def get_name(self) -> str:
        """
        Get the name of this reader.
        
        Returns:
            Reader name
        """
        return self._name


class ExcelDataReader(DataReader):
    """
    Data reader for Excel files.
    """
    
    def __init__(self, name: str = "Excel Data Reader"):
        """
        Initialize the reader.
        
        Args:
            name: Name of this reader
        """
        self._name = name
    
    def read_data(self, source: DataSource) -> pd.DataFrame:
        """
        Read data from an Excel file.
        
        Args:
            source: Data source to read from
            
        Returns:
            DataFrame containing the data
        """
        # Check if source is an Excel file
        if source.source_type != DataSourceType.EXCEL:
            raise ValueError(f"Source type {source.source_type} is not supported by {self._name}")
        
        # Check if file exists
        if not source.file_exists:
            raise FileNotFoundError(f"File {source.location} does not exist")
        
        # Read the Excel file
        options = source.options.copy()
        return pd.read_excel(source.location, **options)
    
    def get_supported_source_types(self) -> Set[str]:
        """
        Get the source types supported by this reader.
        
        Returns:
            Set of supported source types
        """
        return {DataSourceType.EXCEL.name}
    
    def get_name(self) -> str:
        """
        Get the name of this reader.
        
        Returns:
            Reader name
        """
        return self._name


class CSVDataWriter(DataWriter):
    """
    Data writer for CSV files.
    """
    
    def __init__(self, name: str = "CSV Data Writer"):
        """
        Initialize the writer.
        
        Args:
            name: Name of this writer
        """
        self._name = name
    
    def write_data(self, data: pd.DataFrame, sink: DataSink) -> bool:
        """
        Write data to a CSV file.
        
        Args:
            data: DataFrame containing the data to write
            sink: Data sink to write to
            
        Returns:
            True if successful, False otherwise
        """
        # Check if sink is a CSV file
        if sink.sink_type != DataSinkType.CSV:
            raise ValueError(f"Sink type {sink.sink_type} is not supported by {self._name}")
        
        # Check if directory exists
        if not sink.directory_exists:
            os.makedirs(os.path.dirname(sink.location), exist_ok=True)
        
        try:
            # Write the CSV file
            options = sink.options.copy()
            data.to_csv(sink.location, **options)
            return True
        except Exception as e:
            logging.error(f"Error writing CSV file: {e}")
            return False
    
    def get_supported_sink_types(self) -> Set[str]:
        """
        Get the sink types supported by this writer.
        
        Returns:
            Set of supported sink types
        """
        return {DataSinkType.CSV.name}
    
    def get_name(self) -> str:
        """
        Get the name of this writer.
        
        Returns:
            Writer name
        """
        return self._name


class ExcelDataWriter(DataWriter):
    """
    Data writer for Excel files.
    """
    
    def __init__(self, name: str = "Excel Data Writer"):
        """
        Initialize the writer.
        
        Args:
            name: Name of this writer
        """
        self._name = name
    
    def write_data(self, data: pd.DataFrame, sink: DataSink) -> bool:
        """
        Write data to an Excel file.
        
        Args:
            data: DataFrame containing the data to write
            sink: Data sink to write to
            
        Returns:
            True if successful, False otherwise
        """
        # Check if sink is an Excel file
        if sink.sink_type != DataSinkType.EXCEL:
            raise ValueError(f"Sink type {sink.sink_type} is not supported by {self._name}")
        
        # Check if directory exists
        if not sink.directory_exists:
            os.makedirs(os.path.dirname(sink.location), exist_ok=True)
        
        try:
            # Write the Excel file
            options = sink.options.copy()
            data.to_excel(sink.location, **options)
            return True
        except Exception as e:
            logging.error(f"Error writing Excel file: {e}")
            return False
    
    def get_supported_sink_types(self) -> Set[str]:
        """
        Get the sink types supported by this writer.
        
        Returns:
            Set of supported sink types
        """
        return {DataSinkType.EXCEL.name}
    
    def get_name(self) -> str:
        """
        Get the name of this writer.
        
        Returns:
            Writer name
        """
        return self._name


class HTMLDataWriter(DataWriter):
    """
    Data writer for HTML files.
    """
    
    def __init__(self, name: str = "HTML Data Writer"):
        """
        Initialize the writer.
        
        Args:
            name: Name of this writer
        """
        self._name = name
    
    def write_data(self, data: pd.DataFrame, sink: DataSink) -> bool:
        """
        Write data to an HTML file.
        
        Args:
            data: DataFrame containing the data to write
            sink: Data sink to write to
            
        Returns:
            True if successful, False otherwise
        """
        # Check if sink is an HTML file
        if sink.sink_type != DataSinkType.HTML:
            raise ValueError(f"Sink type {sink.sink_type} is not supported by {self._name}")
        
        # Check if directory exists
        if not sink.directory_exists:
            os.makedirs(os.path.dirname(sink.location), exist_ok=True)
        
        try:
            # Write the HTML file
            options = sink.options.copy()
            data.to_html(sink.location, **options)
            return True
        except Exception as e:
            logging.error(f"Error writing HTML file: {e}")
            return False
    
    def get_supported_sink_types(self) -> Set[str]:
        """
        Get the sink types supported by this writer.
        
        Returns:
            Set of supported sink types
        """
        return {DataSinkType.HTML.name}
    
    def get_name(self) -> str:
        """
        Get the name of this writer.
        
        Returns:
            Writer name
        """
        return self._name


class URLClassificationProcessor(DataProcessor):
    """
    Data processor for URL classification.
    """
    
    def __init__(self, classifier: URLClassifier, name: str = "URL Classification Processor"):
        """
        Initialize the processor.
        
        Args:
            classifier: URL classifier to use
            name: Name of this processor
        """
        self._classifier = classifier
        self._name = name
    
    def process_data(self, data: pd.DataFrame, options: ProcessingOptions) -> pd.DataFrame:
        """
        Process data by classifying URLs.
        
        Args:
            data: DataFrame containing the data to process
            options: Options for the processing
            
        Returns:
            DataFrame containing the processed data
        """
        # Check if URL column exists
        if options.url_column not in data.columns:
            raise ValueError(f"URL column '{options.url_column}' not found in data")
        
        # Create a copy of the data
        result = data.copy()
        
        # Define a function to classify a URL
        def classify_url(url: str) -> Tuple[str, bool]:
            try:
                classification_result = self._classifier.classify_url(url)
                return str(classification_result.category), classification_result.is_sensitive
            except Exception as e:
                logging.error(f"Error classifying URL '{url}': {e}")
                return "Error", False
        
        # Process URLs in batches
        total_rows = len(result)
        batch_size = options.batch_size
        num_batches = (total_rows + batch_size - 1) // batch_size
        
        with tqdm(total=total_rows, desc="Classifying URLs", disable=not options.show_progress) as pbar:
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = min(start_idx + batch_size, total_rows)
                batch = result.iloc[start_idx:end_idx]
                
                # Process the batch with optimized concurrency
                with optimized_thread_pool(
                    workload_type="cpu_bound",  # URL classification is CPU-bound
                    task_count=len(batch)
                ) as executor:
                    urls = batch[options.url_column].tolist()
                    results = list(executor.map(classify_url, urls))
                
                # Update the result DataFrame
                result.loc[batch.index, 'category'] = [r[0] for r in results]
                result.loc[batch.index, 'is_sensitive'] = [r[1] for r in results]
                
                # Update progress
                pbar.update(end_idx - start_idx)
        
        return result
    
    def get_name(self) -> str:
        """
        Get the name of this processor.
        
        Returns:
            Processor name
        """
        return self._name
    
    def get_description(self) -> str:
        """
        Get the description of this processor.
        
        Returns:
            Processor description
        """
        return f"Classifies URLs using {self._classifier.get_name()}"


class InMemoryJobRepository(JobRepository):
    """
    In-memory implementation of the job repository.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        """
        self._jobs: Dict[str, ProcessingJob] = {}
        self._lock = Lock()
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: ID of the job to get
            
        Returns:
            ProcessingJob or None if not found
        """
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_jobs(self) -> List[ProcessingJob]:
        """
        Get all jobs.
        
        Returns:
            List of jobs
        """
        with self._lock:
            return list(self._jobs.values())
    
    def save_job(self, job: ProcessingJob) -> None:
        """
        Save a job.
        
        Args:
            job: Job to save
        """
        with self._lock:
            self._jobs[job.job_id] = job
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                return True
            return False
    
    def get_active_jobs(self) -> List[ProcessingJob]:
        """
        Get all active jobs.
        
        Returns:
            List of active jobs
        """
        with self._lock:
            return [job for job in self._jobs.values() if job.is_active]


class InMemoryResultRepository(ResultRepository):
    """
    In-memory implementation of the result repository.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        """
        self._results: Dict[str, ProcessingResult] = {}
        self._lock = Lock()
    
    def get_result(self, job_id: str) -> Optional[ProcessingResult]:
        """
        Get a result by job ID.
        
        Args:
            job_id: ID of the job to get the result for
            
        Returns:
            ProcessingResult or None if not found
        """
        with self._lock:
            return self._results.get(job_id)
    
    def save_result(self, result: ProcessingResult) -> None:
        """
        Save a result.
        
        Args:
            result: Result to save
        """
        with self._lock:
            self._results[result.job.job_id] = result
    
    def delete_result(self, job_id: str) -> bool:
        """
        Delete a result.
        
        Args:
            job_id: ID of the job to delete the result for
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if job_id in self._results:
                del self._results[job_id]
                return True
            return False
    
    def get_results(self) -> List[ProcessingResult]:
        """
        Get all results.
        
        Returns:
            List of results
        """
        with self._lock:
            return list(self._results.values())


class DefaultBatchProcessingService(BatchProcessingService):
    """
    Default implementation of the batch processing service.
    """
    
    def __init__(self, 
                 job_repository: JobRepository,
                 result_repository: ResultRepository,
                 readers: Optional[List[DataReader]] = None,
                 writers: Optional[List[DataWriter]] = None,
                 processors: Optional[List[DataProcessor]] = None):
        """
        Initialize the service.
        
        Args:
            job_repository: Repository for jobs
            result_repository: Repository for results
            readers: Optional list of data readers
            writers: Optional list of data writers
            processors: Optional list of data processors
        """
        self._job_repository = job_repository
        self._result_repository = result_repository
        self._readers = readers or [CSVDataReader(), ExcelDataReader()]
        self._writers = writers or [CSVDataWriter(), ExcelDataWriter(), HTMLDataWriter()]
        self._processors = processors or []
        
        # Create maps for faster lookup
        self._reader_map: Dict[str, Dict[str, DataReader]] = {}
        for reader in self._readers:
            for source_type in reader.get_supported_source_types():
                if source_type not in self._reader_map:
                    self._reader_map[source_type] = {}
                self._reader_map[source_type][reader.get_name()] = reader
        
        self._writer_map: Dict[str, Dict[str, DataWriter]] = {}
        for writer in self._writers:
            for sink_type in writer.get_supported_sink_types():
                if sink_type not in self._writer_map:
                    self._writer_map[sink_type] = {}
                self._writer_map[sink_type][writer.get_name()] = writer
        
        self._processor_map: Dict[str, DataProcessor] = {
            processor.get_name(): processor for processor in self._processors
        }
        
        # Create an optimized thread pool for job execution
        self._optimized_executor = create_optimized_executor(
            workload_type="mixed",  # Job execution can involve both I/O and CPU work
            max_workers=10
        )
        self._active_jobs: Dict[str, Any] = {}
    
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
        job = ProcessingJob.create(source, sink, name, options)
        self._job_repository.save_job(job)
        return job
    
    def start_job(self, job_id: str) -> bool:
        """
        Start a job.
        
        Args:
            job_id: ID of the job to start
            
        Returns:
            True if successful, False otherwise
        """
        job = self._job_repository.get_job(job_id)
        if not job:
            return False
        
        if job.status != ProcessingStatus.PENDING:
            return False
        
        # Start the job
        job.start()
        self._job_repository.save_job(job)
        
        # Submit the job for execution using optimized executor
        with self._optimized_executor.get_executor(1) as executor:
            future = executor.submit(self._execute_job, job)
            self._active_jobs[job_id] = future
        
        return True
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            True if successful, False otherwise
        """
        job = self._job_repository.get_job(job_id)
        if not job:
            return False
        
        if not job.is_active:
            return False
        
        # Cancel the job
        job.cancel()
        self._job_repository.save_job(job)
        
        # Cancel the future if it exists
        if job_id in self._active_jobs:
            future = self._active_jobs[job_id]
            future.cancel()
            del self._active_jobs[job_id]
        
        return True
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a job.
        
        Args:
            job_id: ID of the job to get the status for
            
        Returns:
            Dictionary containing the job status or None if not found
        """
        job = self._job_repository.get_job(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'name': job.name,
            'status': job.status.name,
            'progress': job.progress,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'duration': job.duration,
            'source': job.source.name,
            'sink': job.sink.name
        }
    
    def get_job_result(self, job_id: str) -> Optional[ProcessingResult]:
        """
        Get the result of a job.
        
        Args:
            job_id: ID of the job to get the result for
            
        Returns:
            ProcessingResult or None if not found
        """
        return self._result_repository.get_result(job_id)
    
    def process_data(self, data: pd.DataFrame, options: ProcessingOptions) -> pd.DataFrame:
        """
        Process data directly without creating a job.
        
        Args:
            data: DataFrame containing the data to process
            options: Options for the processing
            
        Returns:
            DataFrame containing the processed data
        """
        result = data.copy()
        
        # Apply each processor in sequence
        for processor in self._processors:
            result = processor.process_data(result, options)
        
        return result
    
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
        # Create source and sink
        source_ext = os.path.splitext(source_path)[1].lower()
        sink_ext = os.path.splitext(sink_path)[1].lower()
        
        if source_ext == '.csv':
            source = DataSource.create_csv_source(source_path)
        elif source_ext in ['.xls', '.xlsx']:
            source = DataSource.create_excel_source(source_path)
        else:
            raise ValueError(f"Unsupported source file extension: {source_ext}")
        
        if sink_ext == '.csv':
            sink = DataSink.create_csv_sink(sink_path)
        elif sink_ext in ['.xls', '.xlsx']:
            sink = DataSink.create_excel_sink(sink_path)
        elif sink_ext == '.html':
            sink = DataSink.create_html_sink(sink_path)
        else:
            raise ValueError(f"Unsupported sink file extension: {sink_ext}")
        
        # Create a job
        options = options or ProcessingOptions()
        job = ProcessingJob.create(source, sink, options=options)
        
        try:
            # Start the job
            job.start()
            
            # Read the data
            reader = self._get_reader(source)
            if not reader:
                raise ValueError(f"No reader found for source type {source.source_type}")
            
            data = reader.read_data(source)
            
            # Process the data
            processed_data = self.process_data(data, options)
            
            # Write the data
            writer = self._get_writer(sink)
            if not writer:
                raise ValueError(f"No writer found for sink type {sink.sink_type}")
            
            success = writer.write_data(processed_data, sink)
            
            # Create statistics
            stats = {
                'input_rows': len(data),
                'output_rows': len(processed_data),
                'input_columns': len(data.columns),
                'output_columns': len(processed_data.columns),
                'processing_time': job.duration
            }
            
            # Complete the job
            job.complete(stats)
            
            # Create the result
            result = ProcessingResult(
                job=job,
                data=processed_data,
                success=success,
                stats=stats
            )
            
            return result
            
        except Exception as e:
            # Fail the job
            job.fail(str(e))
            
            # Create the result
            result = ProcessingResult(
                job=job,
                success=False,
                error_message=str(e)
            )
            
            return result
    
    def add_processor(self, processor: DataProcessor) -> None:
        """
        Add a data processor.
        
        Args:
            processor: Data processor to add
        """
        self._processors.append(processor)
        self._processor_map[processor.get_name()] = processor
    
    def remove_processor(self, name: str) -> bool:
        """
        Remove a data processor.
        
        Args:
            name: Name of the processor to remove
            
        Returns:
            True if successful, False otherwise
        """
        if name in self._processor_map:
            processor = self._processor_map[name]
            self._processors.remove(processor)
            del self._processor_map[name]
            return True
        return False
    
    def get_processors(self) -> List[DataProcessor]:
        """
        Get all data processors.
        
        Returns:
            List of data processors
        """
        return self._processors
    
    def _execute_job(self, job: ProcessingJob) -> None:
        """
        Execute a job.
        
        Args:
            job: Job to execute
        """
        try:
            # Read the data
            reader = self._get_reader(job.source)
            if not reader:
                raise ValueError(f"No reader found for source type {job.source.source_type}")
            
            data = reader.read_data(job.source)
            job.update_progress(0.2)
            self._job_repository.save_job(job)
            
            # Process the data
            processed_data = self.process_data(data, job.options)
            job.update_progress(0.8)
            self._job_repository.save_job(job)
            
            # Write the data
            writer = self._get_writer(job.sink)
            if not writer:
                raise ValueError(f"No writer found for sink type {job.sink.sink_type}")
            
            success = writer.write_data(processed_data, job.sink)
            
            # Create statistics
            stats = {
                'input_rows': len(data),
                'output_rows': len(processed_data),
                'input_columns': len(data.columns),
                'output_columns': len(processed_data.columns),
                'processing_time': job.duration
            }
            
            # Complete the job
            job.complete(stats)
            self._job_repository.save_job(job)
            
            # Create the result
            result = ProcessingResult(
                job=job,
                data=processed_data,
                success=success,
                stats=stats
            )
            
            # Save the result
            self._result_repository.save_result(result)
            
        except Exception as e:
            # Fail the job
            job.fail(str(e))
            self._job_repository.save_job(job)
            
            # Create the result
            result = ProcessingResult(
                job=job,
                success=False,
                error_message=str(e)
            )
            
            # Save the result
            self._result_repository.save_result(result)
        
        finally:
            # Remove the job from active jobs
            if job.job_id in self._active_jobs:
                del self._active_jobs[job.job_id]
    
    def _get_reader(self, source: DataSource) -> Optional[DataReader]:
        """
        Get a reader for a source.
        
        Args:
            source: Data source
            
        Returns:
            DataReader or None if not found
        """
        source_type = source.source_type.name
        if source_type in self._reader_map:
            readers = self._reader_map[source_type]
            if readers:
                return next(iter(readers.values()))
        return None
    
    def _get_writer(self, sink: DataSink) -> Optional[DataWriter]:
        """
        Get a writer for a sink.
        
        Args:
            sink: Data sink
            
        Returns:
            DataWriter or None if not found
        """
        sink_type = sink.sink_type.name
        if sink_type in self._writer_map:
            writers = self._writer_map[sink_type]
            if writers:
                return next(iter(writers.values()))
        return None