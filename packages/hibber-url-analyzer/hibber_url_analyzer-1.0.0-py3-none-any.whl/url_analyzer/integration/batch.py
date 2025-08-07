"""
Batch processing module for URL Analyzer.

This module provides batch processing capabilities for URL Analyzer,
allowing it to process large datasets efficiently and integrate with other systems.
"""

import concurrent.futures
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Union, TypeVar, Generic, Iterator, Tuple

from url_analyzer.api.core import URLAnalyzerAPI
from url_analyzer.api.models import AnalysisResult, BatchAnalysisResult
from url_analyzer.integration.exporters import export_data
from url_analyzer.integration.importers import import_urls_from_file, import_data
from url_analyzer.integration.queue import send_message, MessagePriority

# Configure logger
logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Batch job status."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    
    def __str__(self) -> str:
        """Return string representation of the status."""
        return self.name


@dataclass
class BatchJob:
    """
    Batch job configuration.
    
    This class represents a batch job for processing URLs.
    
    Args:
        name: The name of the job
        urls: List of URLs to process or input file path
        output_path: Path to save the results
        output_format: Format to save the results (json, csv, excel, html)
        include_content: Whether to fetch and analyze page content
        include_summary: Whether to generate a summary of the URL content
        max_workers: Maximum number of concurrent workers
        timeout: Request timeout in seconds
        notify_on_completion: Whether to send a notification when the job completes
        id: Unique identifier for the job
        created_at: When the job was created
        status: The current status of the job
        progress: The progress of the job (0-100)
        result: The result of the job
        error: Error message if the job failed
    """
    name: str
    urls: Union[List[str], str]
    output_path: str
    output_format: str = "json"
    include_content: bool = False
    include_summary: bool = False
    max_workers: int = 20
    timeout: int = 7
    notify_on_completion: bool = True
    id: str = field(default_factory=lambda: f"batch-{int(time.time())}")
    created_at: datetime = field(default_factory=datetime.now)
    status: BatchStatus = BatchStatus.PENDING
    progress: float = 0.0
    result: Optional[BatchAnalysisResult] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the batch job to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "urls": self.urls,
            "output_path": self.output_path,
            "output_format": self.output_format,
            "include_content": self.include_content,
            "include_summary": self.include_summary,
            "max_workers": self.max_workers,
            "timeout": self.timeout,
            "notify_on_completion": self.notify_on_completion,
            "created_at": self.created_at.isoformat(),
            "status": str(self.status),
            "progress": self.progress,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error
        }


class BatchProcessor:
    """
    Batch processor for URL analysis.
    
    This class processes batch jobs for URL analysis.
    """
    
    def __init__(self, api: Optional[URLAnalyzerAPI] = None):
        """
        Initialize the batch processor.
        
        Args:
            api: The URL Analyzer API to use (default: create a new instance)
        """
        self.api = api or URLAnalyzerAPI()
        self.jobs: Dict[str, BatchJob] = {}
        self.running_jobs: Dict[str, concurrent.futures.Future] = {}
        
        logger.debug("Initialized BatchProcessor")
    
    def submit_job(self, job: BatchJob) -> str:
        """
        Submit a batch job for processing.
        
        Args:
            job: The batch job to submit
            
        Returns:
            The ID of the submitted job
        """
        self.jobs[job.id] = job
        
        # Start the job in a separate thread
        future = concurrent.futures.ThreadPoolExecutor(max_workers=1).submit(
            self._process_job, job
        )
        
        self.running_jobs[job.id] = future
        
        logger.info(f"Submitted batch job {job.name} ({job.id})")
        return job.id
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """
        Get a batch job by ID.
        
        Args:
            job_id: The ID of the job to get
            
        Returns:
            The batch job if found, None otherwise
        """
        return self.jobs.get(job_id)
    
    def get_jobs(self) -> List[BatchJob]:
        """
        Get all batch jobs.
        
        Returns:
            List of all batch jobs
        """
        return list(self.jobs.values())
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a batch job.
        
        Args:
            job_id: The ID of the job to cancel
            
        Returns:
            True if the job was cancelled, False otherwise
        """
        if job_id in self.jobs and job_id in self.running_jobs:
            job = self.jobs[job_id]
            
            if job.status == BatchStatus.RUNNING:
                # Cancel the future
                future = self.running_jobs[job_id]
                cancelled = future.cancel()
                
                if cancelled:
                    job.status = BatchStatus.CANCELLED
                    logger.info(f"Cancelled batch job {job.name} ({job.id})")
                    return True
                else:
                    logger.warning(f"Failed to cancel batch job {job.name} ({job.id})")
                    return False
            elif job.status == BatchStatus.PENDING:
                job.status = BatchStatus.CANCELLED
                logger.info(f"Cancelled pending batch job {job.name} ({job.id})")
                return True
        
        return False
    
    def _process_job(self, job: BatchJob) -> None:
        """
        Process a batch job.
        
        Args:
            job: The batch job to process
        """
        try:
            logger.info(f"Starting batch job {job.name} ({job.id})")
            job.status = BatchStatus.RUNNING
            job.progress = 0.0
            
            # Load URLs if input is a file path
            urls = self._load_urls(job)
            
            # Process URLs
            response = self.api.analyze_urls(
                urls=urls,
                include_content=job.include_content,
                include_summary=job.include_summary,
                max_workers=job.max_workers,
                timeout=job.timeout
            )
            
            if response.success:
                job.result = response.data
                job.status = BatchStatus.COMPLETED
                job.progress = 100.0
                
                # Export results
                self._export_results(job)
                
                logger.info(f"Completed batch job {job.name} ({job.id})")
                
                # Send notification if requested
                if job.notify_on_completion:
                    self._send_completion_notification(job)
            else:
                job.error = response.error
                job.status = BatchStatus.FAILED
                logger.error(f"Batch job {job.name} ({job.id}) failed: {response.error}")
                
                # Send notification if requested
                if job.notify_on_completion:
                    self._send_failure_notification(job)
        except Exception as e:
            job.error = str(e)
            job.status = BatchStatus.FAILED
            logger.exception(f"Error processing batch job {job.name} ({job.id})")
            
            # Send notification if requested
            if job.notify_on_completion:
                self._send_failure_notification(job)
    
    def _load_urls(self, job: BatchJob) -> List[str]:
        """
        Load URLs for a batch job.
        
        Args:
            job: The batch job
            
        Returns:
            List of URLs to process
        """
        if isinstance(job.urls, list):
            return job.urls
        elif isinstance(job.urls, str) and os.path.isfile(job.urls):
            try:
                return import_urls_from_file(job.urls)
            except Exception as e:
                raise ValueError(f"Error loading URLs from file {job.urls}: {e}")
        else:
            raise ValueError(f"Invalid URLs source: {job.urls}")
    
    def _export_results(self, job: BatchJob) -> None:
        """
        Export results for a batch job.
        
        Args:
            job: The batch job
        """
        if not job.result:
            return
        
        try:
            # Convert results to a list of dictionaries
            results_data = [result.to_dict() for result in job.result.results]
            
            # Export data
            export_data(results_data, job.output_path, job.output_format)
            
            logger.info(f"Exported results for batch job {job.name} ({job.id}) to {job.output_path}")
        except Exception as e:
            logger.error(f"Error exporting results for batch job {job.name} ({job.id}): {e}")
    
    def _send_completion_notification(self, job: BatchJob) -> None:
        """
        Send a completion notification for a batch job.
        
        Args:
            job: The batch job
        """
        try:
            send_message(
                message_type="batch_job_completed",
                payload={
                    "job_id": job.id,
                    "name": job.name,
                    "output_path": job.output_path,
                    "total_urls": job.result.total_urls if job.result else 0,
                    "successful_urls": job.result.successful_urls if job.result else 0,
                    "failed_urls": job.result.failed_urls if job.result else 0,
                    "execution_time": job.result.execution_time if job.result else 0
                },
                priority=MessagePriority.NORMAL,
                headers={"job_id": job.id}
            )
            
            logger.debug(f"Sent completion notification for batch job {job.name} ({job.id})")
        except Exception as e:
            logger.error(f"Error sending completion notification for batch job {job.name} ({job.id}): {e}")
    
    def _send_failure_notification(self, job: BatchJob) -> None:
        """
        Send a failure notification for a batch job.
        
        Args:
            job: The batch job
        """
        try:
            send_message(
                message_type="batch_job_failed",
                payload={
                    "job_id": job.id,
                    "name": job.name,
                    "error": job.error
                },
                priority=MessagePriority.HIGH,
                headers={"job_id": job.id}
            )
            
            logger.debug(f"Sent failure notification for batch job {job.name} ({job.id})")
        except Exception as e:
            logger.error(f"Error sending failure notification for batch job {job.name} ({job.id}): {e}")


# Create a default batch processor
default_processor = BatchProcessor()


def submit_batch_job(
    name: str,
    urls: Union[List[str], str],
    output_path: str,
    output_format: str = "json",
    include_content: bool = False,
    include_summary: bool = False,
    max_workers: int = 20,
    timeout: int = 7,
    notify_on_completion: bool = True
) -> str:
    """
    Submit a batch job for processing.
    
    This is a convenience function for submitting batch jobs.
    
    Args:
        name: The name of the job
        urls: List of URLs to process or input file path
        output_path: Path to save the results
        output_format: Format to save the results (json, csv, excel, html)
        include_content: Whether to fetch and analyze page content
        include_summary: Whether to generate a summary of the URL content
        max_workers: Maximum number of concurrent workers
        timeout: Request timeout in seconds
        notify_on_completion: Whether to send a notification when the job completes
        
    Returns:
        The ID of the submitted job
    """
    job = BatchJob(
        name=name,
        urls=urls,
        output_path=output_path,
        output_format=output_format,
        include_content=include_content,
        include_summary=include_summary,
        max_workers=max_workers,
        timeout=timeout,
        notify_on_completion=notify_on_completion
    )
    
    return default_processor.submit_job(job)


def get_batch_job(job_id: str) -> Optional[BatchJob]:
    """
    Get a batch job by ID.
    
    This is a convenience function for getting batch jobs.
    
    Args:
        job_id: The ID of the job to get
        
    Returns:
        The batch job if found, None otherwise
    """
    return default_processor.get_job(job_id)


def get_batch_jobs() -> List[BatchJob]:
    """
    Get all batch jobs.
    
    This is a convenience function for getting all batch jobs.
    
    Returns:
        List of all batch jobs
    """
    return default_processor.get_jobs()


def cancel_batch_job(job_id: str) -> bool:
    """
    Cancel a batch job.
    
    This is a convenience function for cancelling batch jobs.
    
    Args:
        job_id: The ID of the job to cancel
        
    Returns:
        True if the job was cancelled, False otherwise
    """
    return default_processor.cancel_job(job_id)