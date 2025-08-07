"""
Backup Strategy Module for URL Analyzer

This module implements comprehensive backup strategies for the URL Analyzer system,
including configuration data, cache files, reports, and system state.
"""

import os
import json
import shutil
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class BackupConfig:
    """Configuration for backup operations."""
    backup_directory: str = "backups"
    retention_days: int = 30
    compression_enabled: bool = True
    verify_backups: bool = True
    max_backup_size_mb: int = 1000
    backup_schedule: str = "daily"  # daily, weekly, monthly
    include_cache: bool = True
    include_reports: bool = True
    include_logs: bool = False


@dataclass
class BackupMetadata:
    """Metadata for backup operations."""
    backup_id: str
    timestamp: datetime
    backup_type: str
    file_count: int
    total_size_bytes: int
    checksum: str
    status: str
    error_message: Optional[str] = None


class BackupStrategy:
    """
    Implements comprehensive backup strategies for the URL Analyzer system.
    
    This class provides functionality for creating, managing, and verifying backups
    of critical system components including configuration, data, and reports.
    """
    
    def __init__(self, config: Optional[BackupConfig] = None):
        """
        Initialize the backup strategy.
        
        Args:
            config: Backup configuration. If None, uses default configuration.
        """
        self.config = config or BackupConfig()
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path(self.config.backup_directory)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize backup metadata storage
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata_history: List[BackupMetadata] = self._load_metadata_history()
    
    def create_full_backup(self) -> BackupMetadata:
        """
        Create a full system backup.
        
        Returns:
            BackupMetadata: Metadata about the created backup.
        """
        backup_id = self._generate_backup_id("full")
        self.logger.info(f"Starting full backup: {backup_id}")
        
        try:
            backup_path = self.backup_dir / f"{backup_id}.zip"
            file_count = 0
            total_size = 0
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED if self.config.compression_enabled else zipfile.ZIP_STORED) as zipf:
                # Backup configuration files
                config_files = self._get_config_files()
                for file_path in config_files:
                    if file_path.exists():
                        zipf.write(file_path, f"config/{file_path.name}")
                        file_count += 1
                        total_size += file_path.stat().st_size
                
                # Backup cache files if enabled
                if self.config.include_cache:
                    cache_files = self._get_cache_files()
                    for file_path in cache_files:
                        if file_path.exists():
                            zipf.write(file_path, f"cache/{file_path.name}")
                            file_count += 1
                            total_size += file_path.stat().st_size
                
                # Backup reports if enabled
                if self.config.include_reports:
                    reports_dir = Path("reports")
                    if reports_dir.exists():
                        for file_path in reports_dir.rglob("*"):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(reports_dir)
                                zipf.write(file_path, f"reports/{rel_path}")
                                file_count += 1
                                total_size += file_path.stat().st_size
                
                # Backup logs if enabled
                if self.config.include_logs:
                    logs_dir = Path("logs")
                    if logs_dir.exists():
                        for file_path in logs_dir.rglob("*.log"):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(logs_dir)
                                zipf.write(file_path, f"logs/{rel_path}")
                                file_count += 1
                                total_size += file_path.stat().st_size
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(backup_path)
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type="full",
                file_count=file_count,
                total_size_bytes=total_size,
                checksum=checksum,
                status="completed"
            )
            
            # Verify backup if enabled
            if self.config.verify_backups:
                if not self._verify_backup(backup_path, metadata):
                    metadata.status = "verification_failed"
                    metadata.error_message = "Backup verification failed"
            
            self._save_metadata(metadata)
            self.logger.info(f"Full backup completed: {backup_id}")
            
            return metadata
            
        except Exception as e:
            error_msg = f"Full backup failed: {str(e)}"
            self.logger.error(error_msg)
            
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type="full",
                file_count=0,
                total_size_bytes=0,
                checksum="",
                status="failed",
                error_message=error_msg
            )
            
            self._save_metadata(metadata)
            return metadata
    
    def create_incremental_backup(self, last_backup_time: Optional[datetime] = None) -> BackupMetadata:
        """
        Create an incremental backup of files modified since the last backup.
        
        Args:
            last_backup_time: Time of the last backup. If None, uses the most recent backup.
            
        Returns:
            BackupMetadata: Metadata about the created backup.
        """
        if last_backup_time is None:
            last_backup_time = self._get_last_backup_time()
        
        backup_id = self._generate_backup_id("incremental")
        self.logger.info(f"Starting incremental backup: {backup_id}")
        
        try:
            backup_path = self.backup_dir / f"{backup_id}.zip"
            file_count = 0
            total_size = 0
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED if self.config.compression_enabled else zipfile.ZIP_STORED) as zipf:
                # Get modified files since last backup
                modified_files = self._get_modified_files(last_backup_time)
                
                for file_path, category in modified_files:
                    if file_path.exists():
                        zipf.write(file_path, f"{category}/{file_path.name}")
                        file_count += 1
                        total_size += file_path.stat().st_size
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(backup_path)
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type="incremental",
                file_count=file_count,
                total_size_bytes=total_size,
                checksum=checksum,
                status="completed"
            )
            
            # Verify backup if enabled
            if self.config.verify_backups:
                if not self._verify_backup(backup_path, metadata):
                    metadata.status = "verification_failed"
                    metadata.error_message = "Backup verification failed"
            
            self._save_metadata(metadata)
            self.logger.info(f"Incremental backup completed: {backup_id}")
            
            return metadata
            
        except Exception as e:
            error_msg = f"Incremental backup failed: {str(e)}"
            self.logger.error(error_msg)
            
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type="incremental",
                file_count=0,
                total_size_bytes=0,
                checksum="",
                status="failed",
                error_message=error_msg
            )
            
            self._save_metadata(metadata)
            return metadata
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy.
        
        Returns:
            int: Number of backups removed.
        """
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        removed_count = 0
        
        # Get backups to remove
        backups_to_remove = [
            metadata for metadata in self.metadata_history
            if metadata.timestamp < cutoff_date
        ]
        
        for metadata in backups_to_remove:
            backup_path = self.backup_dir / f"{metadata.backup_id}.zip"
            try:
                if backup_path.exists():
                    backup_path.unlink()
                    self.logger.info(f"Removed old backup: {metadata.backup_id}")
                    removed_count += 1
                
                # Remove from metadata history
                self.metadata_history.remove(metadata)
                
            except Exception as e:
                self.logger.error(f"Failed to remove backup {metadata.backup_id}: {str(e)}")
        
        # Save updated metadata
        self._save_metadata_history()
        
        return removed_count
    
    def get_backup_status(self) -> Dict:
        """
        Get the current backup status and statistics.
        
        Returns:
            Dict: Backup status information.
        """
        total_backups = len(self.metadata_history)
        successful_backups = len([m for m in self.metadata_history if m.status == "completed"])
        failed_backups = len([m for m in self.metadata_history if m.status == "failed"])
        
        total_size = sum(m.total_size_bytes for m in self.metadata_history if m.status == "completed")
        
        last_backup = max(self.metadata_history, key=lambda x: x.timestamp) if self.metadata_history else None
        
        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0,
            "total_size_mb": total_size / (1024 * 1024),
            "last_backup": {
                "backup_id": last_backup.backup_id,
                "timestamp": last_backup.timestamp.isoformat(),
                "status": last_backup.status,
                "type": last_backup.backup_type
            } if last_backup else None,
            "backup_directory": str(self.backup_dir),
            "retention_days": self.config.retention_days
        }
    
    def _generate_backup_id(self, backup_type: str) -> str:
        """Generate a unique backup ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{backup_type}_{timestamp}"
    
    def _get_config_files(self) -> List[Path]:
        """Get list of configuration files to backup."""
        config_files = [
            Path("config.json"),
            Path("pyproject.toml"),
            Path("requirements.txt"),
            Path("mypy.ini")
        ]
        return [f for f in config_files if f.exists()]
    
    def _get_cache_files(self) -> List[Path]:
        """Get list of cache files to backup."""
        cache_files = [
            Path("scan_cache.json"),
            Path("performance_history.json")
        ]
        return [f for f in cache_files if f.exists()]
    
    def _get_modified_files(self, since: datetime) -> List[Tuple[Path, str]]:
        """Get files modified since the specified time."""
        modified_files = []
        
        # Check config files
        for file_path in self._get_config_files():
            if file_path.stat().st_mtime > since.timestamp():
                modified_files.append((file_path, "config"))
        
        # Check cache files if enabled
        if self.config.include_cache:
            for file_path in self._get_cache_files():
                if file_path.stat().st_mtime > since.timestamp():
                    modified_files.append((file_path, "cache"))
        
        return modified_files
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _verify_backup(self, backup_path: Path, metadata: BackupMetadata) -> bool:
        """Verify the integrity of a backup file."""
        try:
            # Check if file exists and is readable
            if not backup_path.exists():
                return False
            
            # Verify checksum
            actual_checksum = self._calculate_file_checksum(backup_path)
            if actual_checksum != metadata.checksum:
                return False
            
            # Verify ZIP file integrity
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Test the ZIP file
                bad_file = zipf.testzip()
                if bad_file is not None:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {str(e)}")
            return False
    
    def _get_last_backup_time(self) -> datetime:
        """Get the timestamp of the most recent backup."""
        if not self.metadata_history:
            return datetime.min
        
        successful_backups = [m for m in self.metadata_history if m.status == "completed"]
        if not successful_backups:
            return datetime.min
        
        return max(successful_backups, key=lambda x: x.timestamp).timestamp
    
    def _load_metadata_history(self) -> List[BackupMetadata]:
        """Load backup metadata history from file."""
        if not self.metadata_file.exists():
            return []
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                return [
                    BackupMetadata(
                        backup_id=item['backup_id'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        backup_type=item['backup_type'],
                        file_count=item['file_count'],
                        total_size_bytes=item['total_size_bytes'],
                        checksum=item['checksum'],
                        status=item['status'],
                        error_message=item.get('error_message')
                    )
                    for item in data
                ]
        except Exception as e:
            self.logger.error(f"Failed to load metadata history: {str(e)}")
            return []
    
    def _save_metadata(self, metadata: BackupMetadata):
        """Save backup metadata to history."""
        self.metadata_history.append(metadata)
        self._save_metadata_history()
    
    def _save_metadata_history(self):
        """Save metadata history to file."""
        try:
            data = []
            for metadata in self.metadata_history:
                item = asdict(metadata)
                item['timestamp'] = metadata.timestamp.isoformat()
                data.append(item)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metadata history: {str(e)}")