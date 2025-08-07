"""
Batch Processing Module

This module provides functionality for processing large batches of files,
with support for progress tracking, resumable operations, and error handling.
"""

import os
import glob
import json
import time
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import concurrent.futures
from datetime import datetime

# Import from other modules
from url_analyzer.utils.logging import get_logger
from url_analyzer.data.processing import process_file
from url_analyzer.core.analysis import save_cache, LIVE_SCAN_CACHE

# Create logger
logger = get_logger(__name__)

# Optional imports for progress tracking
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class BatchJob:
    """
    A batch job for processing multiple files.
    """
    
    def __init__(
        self,
        job_id: Optional[str] = None,
        files: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        max_workers: int = 1,
        checkpoint_interval: int = 5
    ):
        """
        Initialize a batch job.
        
        Args:
            job_id: Unique identifier for the job (default: timestamp)
            files: List of files to process
            output_dir: Directory for output files
            config: Configuration dictionary
            max_workers: Maximum number of worker threads
            checkpoint_interval: Interval for saving checkpoints (in minutes)
        """
        self.job_id = job_id or f"job_{int(time.time())}"
        self.files = files or []
        self.output_dir = output_dir or os.getcwd()
        self.config = config or {}
        self.max_workers = max_workers
        self.checkpoint_interval = checkpoint_interval
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize job state
        self.state = {
            "job_id": self.job_id,
            "total_files": len(self.files),
            "processed_files": 0,
            "failed_files": [],
            "successful_files": [],
            "start_time": None,
            "end_time": None,
            "status": "initialized",
            "last_checkpoint": None
        }
        
        # Path for checkpoint file
        self.checkpoint_file = os.path.join(self.output_dir, f"{self.job_id}_checkpoint.json")
        
        # Load checkpoint if it exists
        self._load_checkpoint()
    
    def _load_checkpoint(self) -> None:
        """
        Load job state from checkpoint file if it exists.
        """
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                
                # Update job state from checkpoint
                self.state.update(checkpoint_data)
                
                # Filter out already processed files
                self.files = [f for f in self.files if f not in self.state["successful_files"] and f not in self.state["failed_files"]]
                
                logger.info(f"Loaded checkpoint for job {self.job_id}. {self.state['processed_files']} files already processed.")
            except Exception as e:
                logger.error(f"Error loading checkpoint: {e}")
    
    def _save_checkpoint(self) -> None:
        """
        Save job state to checkpoint file.
        """
        try:
            self.state["last_checkpoint"] = datetime.now().isoformat()
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            
            logger.debug(f"Saved checkpoint for job {self.job_id}")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    def _process_file_with_error_handling(self, file_path: str, compiled_patterns: Dict[str, Any], args: Any) -> Optional[pd.DataFrame]:
        """
        Process a single file with error handling.
        
        Args:
            file_path: Path to the file to process
            compiled_patterns: Dictionary of compiled regex patterns
            args: Command-line arguments
            
        Returns:
            Processed DataFrame or None if processing failed
        """
        try:
            logger.info(f"Processing file: {file_path}")
            result = process_file(file_path, compiled_patterns, args)
            
            if result is not None:
                self.state["successful_files"].append(file_path)
            else:
                self.state["failed_files"].append(file_path)
                logger.warning(f"File processing returned None: {file_path}")
            
            return result
        except Exception as e:
            self.state["failed_files"].append(file_path)
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def run(self, compiled_patterns: Dict[str, Any], args: Any) -> Tuple[List[pd.DataFrame], str]:
        """
        Run the batch job.
        
        Args:
            compiled_patterns: Dictionary of compiled regex patterns
            args: Command-line arguments
            
        Returns:
            Tuple of (list of processed DataFrames, report path)
        """
        # Update job state
        self.state["status"] = "running"
        self.state["start_time"] = self.state.get("start_time") or datetime.now().isoformat()
        
        # Initialize result variables
        valid_dfs = []
        last_file = None
        
        # Set up progress tracking
        total_files = len(self.files)
        if total_files == 0:
            logger.info("No files to process.")
            return [], ""
        
        logger.info(f"Starting batch job {self.job_id} with {total_files} files")
        
        # Process files
        if self.max_workers > 1 and total_files > 1:
            # Import the concurrency utilities
            from url_analyzer.utils.concurrency import create_thread_pool_executor
            from url_analyzer.config.manager import load_config
            
            # Get configuration
            config = load_config()
            
            # Add max_workers to config for the executor
            config.setdefault("scan_settings", {})["max_workers"] = self.max_workers
            
            # Parallel processing with adaptive thread pool
            # Use "cpu" operation type since file processing is more CPU-bound
            with create_thread_pool_executor(config, operation_type="cpu") as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self._process_file_with_error_handling, file, compiled_patterns, args): file
                    for file in self.files
                }
                
                # Process results as they complete
                if TQDM_AVAILABLE:
                    for future in tqdm(concurrent.futures.as_completed(future_to_file), total=total_files, desc="Processing files"):
                        file = future_to_file[future]
                        result = future.result()
                        if result is not None:
                            valid_dfs.append(result)
                            last_file = file
                        
                        # Update processed count
                        self.state["processed_files"] += 1
                        
                        # Save checkpoint periodically
                        if self._should_save_checkpoint():
                            self._save_checkpoint()
                else:
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
                        file = future_to_file[future]
                        result = future.result()
                        if result is not None:
                            valid_dfs.append(result)
                            last_file = file
                        
                        # Update processed count
                        self.state["processed_files"] += 1
                        
                        # Log progress
                        logger.info(f"Processed {i+1}/{total_files} files ({(i+1)/total_files*100:.1f}%)")
                        
                        # Save checkpoint periodically
                        if self._should_save_checkpoint():
                            self._save_checkpoint()
        else:
            # Sequential processing
            if TQDM_AVAILABLE:
                files_iter = tqdm(self.files, desc="Processing files")
            else:
                files_iter = self.files
                logger.info(f"Processing {total_files} files sequentially")
            
            for i, file in enumerate(files_iter):
                result = self._process_file_with_error_handling(file, compiled_patterns, args)
                if result is not None:
                    valid_dfs.append(result)
                    last_file = file
                
                # Update processed count
                self.state["processed_files"] += 1
                
                # Log progress if tqdm not available
                if not TQDM_AVAILABLE:
                    logger.info(f"Processed {i+1}/{total_files} files ({(i+1)/total_files*100:.1f}%)")
                
                # Save checkpoint periodically
                if self._should_save_checkpoint():
                    self._save_checkpoint()
        
        # Update job state
        self.state["status"] = "completed"
        self.state["end_time"] = datetime.now().isoformat()
        
        # Save final checkpoint
        self._save_checkpoint()
        
        # Generate report path
        report_path = ""
        if last_file and valid_dfs:
            if args.aggregate:
                report_path = os.path.join(self.output_dir, f"{self.job_id}_aggregated_report.html")
            else:
                base_name = os.path.splitext(os.path.basename(last_file))[0]
                report_path = os.path.join(self.output_dir, f"{base_name}_report.html")
        
        # Generate summary
        self._generate_summary()
        
        return valid_dfs, report_path
    
    def _should_save_checkpoint(self) -> bool:
        """
        Check if a checkpoint should be saved.
        
        Returns:
            True if a checkpoint should be saved, False otherwise
        """
        if not self.state["last_checkpoint"]:
            return True
        
        last_checkpoint = datetime.fromisoformat(self.state["last_checkpoint"])
        now = datetime.now()
        
        # Check if checkpoint_interval minutes have passed
        return (now - last_checkpoint).total_seconds() / 60 >= self.checkpoint_interval
    
    def _generate_summary(self) -> None:
        """
        Generate a summary of the batch job.
        """
        # Calculate statistics
        total_files = self.state["total_files"]
        processed_files = self.state["processed_files"]
        successful_files = len(self.state["successful_files"])
        failed_files = len(self.state["failed_files"])
        
        # Calculate duration
        if self.state["start_time"] and self.state["end_time"]:
            start_time = datetime.fromisoformat(self.state["start_time"])
            end_time = datetime.fromisoformat(self.state["end_time"])
            duration = (end_time - start_time).total_seconds()
            duration_str = f"{duration:.1f} seconds"
            if duration > 60:
                duration_str = f"{duration/60:.1f} minutes"
            if duration > 3600:
                duration_str = f"{duration/3600:.1f} hours"
        else:
            duration_str = "unknown"
        
        # Log summary
        logger.info(f"\n--- Batch Job Summary ---")
        logger.info(f"Job ID: {self.job_id}")
        logger.info(f"Status: {self.state['status']}")
        logger.info(f"Total files: {total_files}")
        logger.info(f"Processed files: {processed_files}")
        logger.info(f"Successful files: {successful_files}")
        logger.info(f"Failed files: {failed_files}")
        logger.info(f"Duration: {duration_str}")
        
        # Save summary to file
        summary_file = os.path.join(self.output_dir, f"{self.job_id}_summary.txt")
        try:
            with open(summary_file, 'w') as f:
                f.write(f"--- Batch Job Summary ---\n")
                f.write(f"Job ID: {self.job_id}\n")
                f.write(f"Status: {self.state['status']}\n")
                f.write(f"Total files: {total_files}\n")
                f.write(f"Processed files: {processed_files}\n")
                f.write(f"Successful files: {successful_files}\n")
                f.write(f"Failed files: {failed_files}\n")
                f.write(f"Duration: {duration_str}\n")
                
                if failed_files > 0:
                    f.write("\nFailed files:\n")
                    for file in self.state["failed_files"]:
                        f.write(f"- {file}\n")
            
            logger.info(f"Summary saved to: {summary_file}")
        except Exception as e:
            logger.error(f"Error saving summary: {e}")


def find_files(path: str, extensions: List[str] = None) -> List[str]:
    """
    Find files in a directory with the specified extensions.
    
    Args:
        path: Path to a file or directory
        extensions: List of file extensions to include (default: ['.csv', '.xlsx', '.xls'])
        
    Returns:
        List of file paths
    """
    if extensions is None:
        extensions = ['.csv', '.xlsx', '.xls']
    
    files = []
    
    if os.path.isdir(path):
        logger.info(f"Searching for files in '{path}'...")
        for ext in extensions:
            pattern = os.path.join(path, f"*{ext}")
            files.extend(glob.glob(pattern))
    elif os.path.isfile(path):
        files.append(path)
    else:
        logger.error(f"Path is not a valid file or directory: {path}")
    
    return files


def process_batch(
    path: str,
    compiled_patterns: Dict[str, Any],
    args: Any,
    job_id: Optional[str] = None,
    max_workers: Optional[int] = None,
    checkpoint_interval: int = 5
) -> Tuple[List[pd.DataFrame], str]:
    """
    Process a batch of files.
    
    Args:
        path: Path to a file or directory
        compiled_patterns: Dictionary of compiled regex patterns
        args: Command-line arguments
        job_id: Unique identifier for the job
        max_workers: Maximum number of worker threads
        checkpoint_interval: Interval for saving checkpoints (in minutes)
        
    Returns:
        Tuple of (list of processed DataFrames, report path)
    """
    # Find files to process
    files = find_files(path)
    
    if not files:
        logger.error(f"No files found in {path}")
        return [], ""
    
    # Determine output directory
    output_dir = args.output if hasattr(args, 'output') and args.output else os.path.dirname(path)
    
    # Determine max workers
    if max_workers is None:
        if hasattr(args, 'max_workers') and args.max_workers:
            max_workers = args.max_workers
        else:
            from url_analyzer.config.manager import load_config
            from url_analyzer.utils.concurrency import get_adaptive_thread_pool_size
            config = load_config()
            
            # Get adaptive thread pool size for CPU-bound operations
            # File processing is more CPU-bound than I/O-bound
            max_workers = get_adaptive_thread_pool_size(config, operation_type="cpu")
    
    # Create batch job
    batch_job = BatchJob(
        job_id=job_id,
        files=files,
        output_dir=output_dir,
        config=None,  # We don't need to pass the config here
        max_workers=max_workers,
        checkpoint_interval=checkpoint_interval
    )
    
    # Run batch job
    valid_dfs, report_path = batch_job.run(compiled_patterns, args)
    
    # Save cache if live scan was performed
    if hasattr(args, 'live_scan') and args.live_scan:
        from url_analyzer.config.manager import load_config
        config = load_config()
        save_cache(LIVE_SCAN_CACHE, config)
    
    return valid_dfs, report_path