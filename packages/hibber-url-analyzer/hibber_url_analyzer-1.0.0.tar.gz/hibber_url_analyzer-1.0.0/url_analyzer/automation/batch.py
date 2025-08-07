"""
Batch Processing Module

This module provides batch processing capabilities for the URL Analyzer,
allowing users to process large sets of URLs or files in an automated fashion.
It supports parallel processing, checkpointing, and error handling.
"""

import os
import json
import time
import uuid
import datetime
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import concurrent.futures

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import BatchProcessingError, AutomationError
from url_analyzer.data.processing import process_file

# Create logger
logger = get_logger(__name__)

# Default path for storing batch jobs
DEFAULT_BATCH_DIR = os.path.join(os.path.expanduser("~"), ".url_analyzer", "batch")


class JobStatus(Enum):
    """Status of a batch job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """
    Represents a batch processing job.
    
    Attributes:
        id: Unique identifier for the job
        name: Human-readable name for the job
        description: Optional description of the job
        input_files: List of input files to process
        output_dir: Directory for output files
        options: Processing options
        status: Current status of the job
        progress: Progress information (files processed, total files, etc.)
        created_at: Timestamp when the job was created
        updated_at: Timestamp when the job was last updated
        start_time: Timestamp when the job started
        end_time: Timestamp when the job completed
        error: Error message if the job failed
    """
    id: str
    name: str
    input_files: List[str]
    output_dir: str
    options: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    status: JobStatus = field(default=JobStatus.PENDING)
    progress: Dict[str, Any] = field(default_factory=lambda: {"processed": 0, "total": 0, "failed": 0})
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the job to a dictionary for serialization."""
        data = asdict(self)
        # Convert enum to string
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchJob':
        """Create a job from a dictionary."""
        # Convert string to enum
        if "status" in data:
            data["status"] = JobStatus(data["status"])
        return cls(**data)


class BatchProcessor:
    """
    Processes batch jobs for URL analysis.
    """
    
    def __init__(self, batch_dir: str = DEFAULT_BATCH_DIR):
        """
        Initialize the batch processor.
        
        Args:
            batch_dir: Directory for storing batch jobs
        """
        self.batch_dir = batch_dir
        self._ensure_batch_dir()
        self.running_jobs: Dict[str, threading.Thread] = {}
    
    def _ensure_batch_dir(self) -> None:
        """Ensure the batch directory exists."""
        os.makedirs(self.batch_dir, exist_ok=True)
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all batch jobs.
        
        Returns:
            List of job metadata
        """
        jobs = []
        
        # Ensure the batch directory exists
        self._ensure_batch_dir()
        
        # Find all JSON files in the batch directory
        for filename in os.listdir(self.batch_dir):
            if filename.endswith(".json"):
                job_path = os.path.join(self.batch_dir, filename)
                try:
                    with open(job_path, "r") as f:
                        job_data = json.load(f)
                    
                    # Extract metadata
                    metadata = {
                        "id": job_data.get("id"),
                        "name": job_data.get("name"),
                        "description": job_data.get("description"),
                        "status": job_data.get("status"),
                        "progress": job_data.get("progress"),
                        "created_at": job_data.get("created_at"),
                        "updated_at": job_data.get("updated_at"),
                        "start_time": job_data.get("start_time"),
                        "end_time": job_data.get("end_time")
                    }
                    
                    jobs.append(metadata)
                except Exception as e:
                    logger.warning(f"Error loading job {job_path}: {e}")
        
        return jobs
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: ID of the job to get
            
        Returns:
            The job, or None if not found
        """
        job_path = os.path.join(self.batch_dir, f"{job_id}.json")
        if not os.path.exists(job_path):
            return None
        
        try:
            with open(job_path, "r") as f:
                job_data = json.load(f)
            
            return BatchJob.from_dict(job_data)
        except Exception as e:
            logger.warning(f"Error loading job {job_path}: {e}")
            return None
    
    def save_job(self, job: BatchJob) -> None:
        """
        Save a job.
        
        Args:
            job: The job to save
        """
        # Ensure the batch directory exists
        self._ensure_batch_dir()
        
        # Update the updated_at timestamp
        job.updated_at = time.time()
        
        # Save the job
        job_path = os.path.join(self.batch_dir, f"{job.id}.json")
        try:
            with open(job_path, "w") as f:
                json.dump(job.to_dict(), f, indent=2)
            
            logger.info(f"Saved job: {job.name} (ID: {job.id})")
        except Exception as e:
            logger.error(f"Error saving job {job.name} (ID: {job.id}): {e}")
            raise BatchProcessingError(f"Error saving job: {e}")
    
    def create_job(self, name: str, input_files: List[str], output_dir: str,
                  options: Optional[Dict[str, Any]] = None,
                  description: Optional[str] = None) -> BatchJob:
        """
        Create a new batch job.
        
        Args:
            name: Name of the job
            input_files: List of input files to process
            output_dir: Directory for output files
            options: Processing options
            description: Optional description of the job
            
        Returns:
            The created job
        """
        # Generate a unique ID
        job_id = str(uuid.uuid4())
        
        # Create the job
        job = BatchJob(
            id=job_id,
            name=name,
            input_files=input_files,
            output_dir=output_dir,
            options=options or {},
            description=description,
            progress={"processed": 0, "total": len(input_files), "failed": 0}
        )
        
        # Save the job
        self.save_job(job)
        
        return job
    
    def delete_job(self, job_id: str) -> None:
        """
        Delete a job.
        
        Args:
            job_id: ID of the job to delete
        """
        # Check if the job is running
        if job_id in self.running_jobs:
            raise BatchProcessingError(f"Cannot delete job {job_id} while it is running")
        
        job_path = os.path.join(self.batch_dir, f"{job_id}.json")
        if not os.path.exists(job_path):
            raise BatchProcessingError(f"Job with ID {job_id} does not exist")
        
        try:
            os.remove(job_path)
            logger.info(f"Deleted job with ID: {job_id}")
        except Exception as e:
            logger.error(f"Error deleting job with ID {job_id}: {e}")
            raise BatchProcessingError(f"Error deleting job: {e}")
    
    def run_job(self, job_id: str, async_mode: bool = True) -> Optional[BatchJob]:
        """
        Run a batch job.
        
        Args:
            job_id: ID of the job to run
            async_mode: Whether to run the job asynchronously
            
        Returns:
            The updated job if running synchronously, None if running asynchronously
        """
        # Get the job
        job = self.get_job(job_id)
        if job is None:
            raise BatchProcessingError(f"Job with ID {job_id} does not exist")
        
        # Check if the job is already running
        if job_id in self.running_jobs:
            raise BatchProcessingError(f"Job {job_id} is already running")
        
        # Update job status and start time
        job.status = JobStatus.RUNNING
        job.start_time = time.time()
        job.error = None
        
        # Save the job
        self.save_job(job)
        
        if async_mode:
            # Run the job in a separate thread
            thread = threading.Thread(target=self._run_job_thread, args=(job_id,))
            thread.daemon = True
            thread.start()
            
            # Store the thread
            self.running_jobs[job_id] = thread
            
            return None
        else:
            # Run the job synchronously
            return self._run_job(job)
    
    def _run_job_thread(self, job_id: str) -> None:
        """
        Run a job in a separate thread.
        
        Args:
            job_id: ID of the job to run
        """
        try:
            # Get the job
            job = self.get_job(job_id)
            if job is None:
                logger.error(f"Job with ID {job_id} does not exist")
                return
            
            # Run the job
            self._run_job(job)
        except Exception as e:
            logger.error(f"Error running job {job_id}: {e}")
        finally:
            # Remove the thread from running jobs
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
    
    def _run_job(self, job: BatchJob) -> BatchJob:
        """
        Run a batch job.
        
        Args:
            job: The job to run
            
        Returns:
            The updated job
        """
        logger.info(f"Running job: {job.name} (ID: {job.id})")
        
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(job.output_dir, exist_ok=True)
            
            # Get processing options
            max_workers = job.options.get("max_workers", 4)
            skip_errors = job.options.get("skip_errors", False)
            checkpoint_interval = job.options.get("checkpoint_interval", 5)  # minutes
            
            # Process files in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all files for processing
                future_to_file = {
                    executor.submit(self._process_file, job, file_path): file_path
                    for file_path in job.input_files
                }
                
                # Process results as they complete
                last_checkpoint = time.time()
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    
                    try:
                        # Get the result
                        result = future.result()
                        
                        # Update progress
                        job.progress["processed"] += 1
                        
                        # Log progress
                        logger.info(f"Processed file {job.progress['processed']}/{job.progress['total']}: {file_path}")
                    except Exception as e:
                        # Update progress
                        job.progress["processed"] += 1
                        job.progress["failed"] += 1
                        
                        # Log error
                        logger.error(f"Error processing file {file_path}: {e}")
                        
                        # If not skipping errors, fail the job
                        if not skip_errors:
                            raise BatchProcessingError(f"Error processing file {file_path}: {e}")
                    
                    # Save checkpoint if needed
                    current_time = time.time()
                    if current_time - last_checkpoint > checkpoint_interval * 60:
                        self.save_job(job)
                        last_checkpoint = current_time
            
            # Update job status and end time
            job.status = JobStatus.COMPLETED
            job.end_time = time.time()
            
            # Save the job
            self.save_job(job)
            
            logger.info(f"Job completed: {job.name} (ID: {job.id})")
            
            return job
        except Exception as e:
            # Update job status and end time
            job.status = JobStatus.FAILED
            job.end_time = time.time()
            job.error = str(e)
            
            # Save the job
            self.save_job(job)
            
            logger.error(f"Job failed: {job.name} (ID: {job.id}): {e}")
            
            raise BatchProcessingError(f"Error running job: {e}")
    
    def _process_file(self, job: BatchJob, file_path: str) -> Dict[str, Any]:
        """
        Process a single file.
        
        Args:
            job: The batch job
            file_path: Path to the file to process
            
        Returns:
            Processing result
        """
        logger.info(f"Processing file: {file_path}")
        
        # Determine output file path
        base_name = os.path.basename(file_path)
        output_file = os.path.join(job.output_dir, f"{os.path.splitext(base_name)[0]}.html")
        
        # Get processing options
        options = job.options.copy()
        
        # Process the file
        from url_analyzer.data.processing import process_file
        result = process_file(file_path, output_file=output_file, **options)
        
        return result
    
    def cancel_job(self, job_id: str) -> None:
        """
        Cancel a running job.
        
        Args:
            job_id: ID of the job to cancel
        """
        # Check if the job is running
        if job_id not in self.running_jobs:
            raise BatchProcessingError(f"Job {job_id} is not running")
        
        # Get the job
        job = self.get_job(job_id)
        if job is None:
            raise BatchProcessingError(f"Job with ID {job_id} does not exist")
        
        # Update job status
        job.status = JobStatus.CANCELLED
        job.end_time = time.time()
        
        # Save the job
        self.save_job(job)
        
        logger.info(f"Cancelled job: {job.name} (ID: {job.id})")
        
        # Note: We can't actually stop the thread, but we can mark the job as cancelled
        # The thread will continue running but will not update the job status


# Global batch processor instance
_batch_processor = None


def get_batch_processor() -> BatchProcessor:
    """
    Get the global batch processor instance.
    
    Returns:
        The global batch processor instance
    """
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor


def create_batch_job(
    name: str,
    input_files: List[str],
    output_dir: str,
    options: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None
) -> str:
    """
    Create a new batch job.
    
    Args:
        name: Name of the job
        input_files: List of input files to process
        output_dir: Directory for output files
        options: Processing options
        description: Optional description of the job
        
    Returns:
        ID of the created job
    """
    processor = get_batch_processor()
    job = processor.create_job(name, input_files, output_dir, options, description)
    return job.id


def process_batch_job(job_id: str, async_mode: bool = True) -> Optional[Dict[str, Any]]:
    """
    Process a batch job.
    
    Args:
        job_id: ID of the job to process
        async_mode: Whether to process the job asynchronously
        
    Returns:
        Dictionary with job data if running synchronously, None if running asynchronously
    """
    processor = get_batch_processor()
    job = processor.run_job(job_id, async_mode)
    if job is not None:
        return job.to_dict()
    return None


def list_batch_jobs() -> List[Dict[str, Any]]:
    """
    List all batch jobs.
    
    Returns:
        List of job metadata
    """
    processor = get_batch_processor()
    return processor.list_jobs()


def get_batch_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a batch job by ID.
    
    Args:
        job_id: ID of the job to get
        
    Returns:
        Dictionary with job data, or None if not found
    """
    processor = get_batch_processor()
    job = processor.get_job(job_id)
    if job is None:
        return None
    return job.to_dict()


def cancel_batch_job(job_id: str) -> None:
    """
    Cancel a running batch job.
    
    Args:
        job_id: ID of the job to cancel
    """
    processor = get_batch_processor()
    processor.cancel_job(job_id)


def delete_batch_job(job_id: str) -> None:
    """
    Delete a batch job.
    
    Args:
        job_id: ID of the job to delete
    """
    processor = get_batch_processor()
    processor.delete_job(job_id)