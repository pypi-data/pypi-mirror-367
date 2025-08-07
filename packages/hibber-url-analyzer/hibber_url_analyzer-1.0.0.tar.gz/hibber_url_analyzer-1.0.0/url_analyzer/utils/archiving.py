"""
Data Archiving Module

This module provides functionality for archiving old analysis results
and managing data retention policies.
"""

import os
import shutil
import datetime
import json
import gzip
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import URLAnalyzerError

logger = get_logger(__name__)


class DataArchiver:
    """
    Data archiver for managing old analysis results and implementing retention policies.
    """
    
    def __init__(self, archive_dir: str = "archives", retention_days: int = 90):
        """
        Initialize the data archiver.
        
        Args:
            archive_dir: Directory to store archived data
            retention_days: Number of days to retain data before archiving
        """
        self.archive_dir = Path(archive_dir)
        self.retention_days = retention_days
        self.archive_dir.mkdir(exist_ok=True)
        
    def archive_file(self, file_path: Union[str, Path], compress: bool = True) -> str:
        """
        Archive a single file.
        
        Args:
            file_path: Path to the file to archive
            compress: Whether to compress the archived file
            
        Returns:
            Path to the archived file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Create archive subdirectory based on current date
        archive_subdir = self.archive_dir / datetime.datetime.now().strftime("%Y/%m")
        archive_subdir.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        if compress:
            archive_name += ".gz"
            archive_path = archive_subdir / archive_name
            
            # Compress and archive the file
            with open(file_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            archive_path = archive_subdir / archive_name
            shutil.copy2(file_path, archive_path)
            
        logger.info(f"Archived file {file_path} to {archive_path}")
        return str(archive_path)
        
    def archive_directory(self, dir_path: Union[str, Path], compress: bool = True) -> str:
        """
        Archive an entire directory.
        
        Args:
            dir_path: Path to the directory to archive
            compress: Whether to compress the archived directory
            
        Returns:
            Path to the archived directory/file
        """
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
            
        # Create archive subdirectory
        archive_subdir = self.archive_dir / datetime.datetime.now().strftime("%Y/%m")
        archive_subdir.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{dir_path.name}_{timestamp}"
        
        if compress:
            archive_path = archive_subdir / f"{archive_name}.tar.gz"
            shutil.make_archive(str(archive_path).replace('.tar.gz', ''), 'gztar', dir_path.parent, dir_path.name)
        else:
            archive_path = archive_subdir / archive_name
            shutil.copytree(dir_path, archive_path)
            
        logger.info(f"Archived directory {dir_path} to {archive_path}")
        return str(archive_path)
        
    def archive_old_files(self, source_dir: Union[str, Path], file_pattern: str = "*") -> List[str]:
        """
        Archive files older than the retention period.
        
        Args:
            source_dir: Directory to scan for old files
            file_pattern: Pattern to match files (default: all files)
            
        Returns:
            List of archived file paths
        """
        source_dir = Path(source_dir)
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
        archived_files = []
        
        for file_path in source_dir.glob(file_pattern):
            if file_path.is_file():
                file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    try:
                        archived_path = self.archive_file(file_path)
                        archived_files.append(archived_path)
                        
                        # Remove original file after successful archiving
                        file_path.unlink()
                        logger.info(f"Removed original file: {file_path}")
                        
                    except Exception as e:
                        logger.error(f"Failed to archive file {file_path}: {e}")
                        
        logger.info(f"Archived {len(archived_files)} old files from {source_dir}")
        return archived_files
        
    def get_archive_info(self) -> Dict[str, Any]:
        """
        Get information about archived data.
        
        Returns:
            Dictionary containing archive statistics
        """
        total_files = 0
        total_size = 0
        archive_months = []
        
        for year_dir in self.archive_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir() and month_dir.name.isdigit():
                        archive_months.append(f"{year_dir.name}-{month_dir.name}")
                        
                        for file_path in month_dir.iterdir():
                            if file_path.is_file():
                                total_files += 1
                                total_size += file_path.stat().st_size
                                
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "archive_months": sorted(archive_months),
            "archive_directory": str(self.archive_dir),
            "retention_days": self.retention_days
        }
        
    def cleanup_old_archives(self, max_age_days: int = 365) -> int:
        """
        Clean up very old archives.
        
        Args:
            max_age_days: Maximum age in days for archives
            
        Returns:
            Number of files cleaned up
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
        cleaned_files = 0
        
        for year_dir in self.archive_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir() and month_dir.name.isdigit():
                        for file_path in month_dir.iterdir():
                            if file_path.is_file():
                                file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                                
                                if file_mtime < cutoff_date:
                                    try:
                                        file_path.unlink()
                                        cleaned_files += 1
                                        logger.info(f"Cleaned up old archive: {file_path}")
                                    except Exception as e:
                                        logger.error(f"Failed to clean up archive {file_path}: {e}")
                                        
        logger.info(f"Cleaned up {cleaned_files} old archive files")
        return cleaned_files


def create_archiver(archive_dir: str = "archives", retention_days: int = 90) -> DataArchiver:
    """
    Create a data archiver instance.
    
    Args:
        archive_dir: Directory to store archived data
        retention_days: Number of days to retain data before archiving
        
    Returns:
        DataArchiver instance
    """
    return DataArchiver(archive_dir, retention_days)


def archive_analysis_results(results_dir: str = "reports", archive_dir: str = "archives") -> List[str]:
    """
    Archive old analysis results.
    
    Args:
        results_dir: Directory containing analysis results
        archive_dir: Directory to store archived data
        
    Returns:
        List of archived file paths
    """
    archiver = create_archiver(archive_dir)
    return archiver.archive_old_files(results_dir, "*.html")