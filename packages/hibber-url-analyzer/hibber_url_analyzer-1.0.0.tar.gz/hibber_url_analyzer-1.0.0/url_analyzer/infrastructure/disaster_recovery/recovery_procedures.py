"""
Recovery Procedures Module for URL Analyzer

This module implements comprehensive recovery procedures for the URL Analyzer system,
including data restoration, system recovery, and rollback capabilities.
"""

import os
import json
import shutil
import zipfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .backup_strategy import BackupMetadata, BackupStrategy


class RecoveryType(Enum):
    """Types of recovery operations."""
    FULL_RESTORE = "full_restore"
    SELECTIVE_RESTORE = "selective_restore"
    POINT_IN_TIME_RESTORE = "point_in_time_restore"
    ROLLBACK = "rollback"


@dataclass
class RecoveryConfig:
    """Configuration for recovery operations."""
    backup_directory: str = "backups"
    recovery_directory: str = "recovery"
    verify_before_restore: bool = True
    create_restore_point: bool = True
    preserve_current_data: bool = True
    recovery_timeout_minutes: int = 30


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    recovery_id: str
    recovery_type: RecoveryType
    timestamp: datetime
    backup_id: str
    success: bool
    files_restored: int
    errors: List[str]
    duration_seconds: float
    restore_point_created: Optional[str] = None


class RecoveryProcedures:
    """
    Implements comprehensive recovery procedures for the URL Analyzer system.
    
    This class provides functionality for restoring data from backups, performing
    system recovery, and managing rollback operations.
    """
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        """
        Initialize the recovery procedures.
        
        Args:
            config: Recovery configuration. If None, uses default configuration.
        """
        self.config = config or RecoveryConfig()
        self.logger = logging.getLogger(__name__)
        self.backup_strategy = BackupStrategy()
        
        # Create recovery directory
        self.recovery_dir = Path(self.config.recovery_directory)
        self.recovery_dir.mkdir(exist_ok=True)
        
        # Initialize recovery history
        self.recovery_history_file = self.recovery_dir / "recovery_history.json"
        self.recovery_history: List[RecoveryResult] = self._load_recovery_history()
    
    def restore_full_system(self, backup_id: Optional[str] = None) -> RecoveryResult:
        """
        Perform a full system restore from backup.
        
        Args:
            backup_id: ID of the backup to restore from. If None, uses the latest backup.
            
        Returns:
            RecoveryResult: Result of the recovery operation.
        """
        start_time = datetime.now()
        recovery_id = self._generate_recovery_id("full_restore")
        
        self.logger.info(f"Starting full system restore: {recovery_id}")
        
        try:
            # Get backup to restore from
            if backup_id is None:
                backup_metadata = self._get_latest_backup()
                if backup_metadata is None:
                    raise ValueError("No backups available for restore")
                backup_id = backup_metadata.backup_id
            else:
                backup_metadata = self._get_backup_metadata(backup_id)
                if backup_metadata is None:
                    raise ValueError(f"Backup not found: {backup_id}")
            
            # Verify backup before restore
            if self.config.verify_before_restore:
                if not self._verify_backup_integrity(backup_id):
                    raise ValueError(f"Backup verification failed: {backup_id}")
            
            # Create restore point if enabled
            restore_point_id = None
            if self.config.create_restore_point:
                restore_point_id = self._create_restore_point()
            
            # Perform the restore
            backup_path = Path(self.config.backup_directory) / f"{backup_id}.zip"
            files_restored = self._extract_backup(backup_path, restore_all=True)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create success result
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.FULL_RESTORE,
                timestamp=start_time,
                backup_id=backup_id,
                success=True,
                files_restored=files_restored,
                errors=[],
                duration_seconds=duration,
                restore_point_created=restore_point_id
            )
            
            self._save_recovery_result(result)
            self.logger.info(f"Full system restore completed: {recovery_id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Full system restore failed: {str(e)}"
            self.logger.error(error_msg)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.FULL_RESTORE,
                timestamp=start_time,
                backup_id=backup_id or "unknown",
                success=False,
                files_restored=0,
                errors=[error_msg],
                duration_seconds=duration
            )
            
            self._save_recovery_result(result)
            return result
    
    def restore_selective(self, backup_id: str, file_patterns: List[str]) -> RecoveryResult:
        """
        Perform a selective restore of specific files from backup.
        
        Args:
            backup_id: ID of the backup to restore from.
            file_patterns: List of file patterns to restore (supports wildcards).
            
        Returns:
            RecoveryResult: Result of the recovery operation.
        """
        start_time = datetime.now()
        recovery_id = self._generate_recovery_id("selective_restore")
        
        self.logger.info(f"Starting selective restore: {recovery_id}")
        
        try:
            # Verify backup exists
            backup_metadata = self._get_backup_metadata(backup_id)
            if backup_metadata is None:
                raise ValueError(f"Backup not found: {backup_id}")
            
            # Verify backup before restore
            if self.config.verify_before_restore:
                if not self._verify_backup_integrity(backup_id):
                    raise ValueError(f"Backup verification failed: {backup_id}")
            
            # Create restore point if enabled
            restore_point_id = None
            if self.config.create_restore_point:
                restore_point_id = self._create_restore_point()
            
            # Perform selective restore
            backup_path = Path(self.config.backup_directory) / f"{backup_id}.zip"
            files_restored = self._extract_selective(backup_path, file_patterns)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create success result
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.SELECTIVE_RESTORE,
                timestamp=start_time,
                backup_id=backup_id,
                success=True,
                files_restored=files_restored,
                errors=[],
                duration_seconds=duration,
                restore_point_created=restore_point_id
            )
            
            self._save_recovery_result(result)
            self.logger.info(f"Selective restore completed: {recovery_id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Selective restore failed: {str(e)}"
            self.logger.error(error_msg)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.SELECTIVE_RESTORE,
                timestamp=start_time,
                backup_id=backup_id,
                success=False,
                files_restored=0,
                errors=[error_msg],
                duration_seconds=duration
            )
            
            self._save_recovery_result(result)
            return result
    
    def restore_point_in_time(self, target_time: datetime) -> RecoveryResult:
        """
        Perform a point-in-time restore to a specific timestamp.
        
        Args:
            target_time: Target time to restore to.
            
        Returns:
            RecoveryResult: Result of the recovery operation.
        """
        start_time = datetime.now()
        recovery_id = self._generate_recovery_id("point_in_time_restore")
        
        self.logger.info(f"Starting point-in-time restore: {recovery_id}")
        
        try:
            # Find the best backup for the target time
            backup_metadata = self._find_backup_for_time(target_time)
            if backup_metadata is None:
                raise ValueError(f"No suitable backup found for time: {target_time}")
            
            # Perform full restore using the selected backup
            result = self.restore_full_system(backup_metadata.backup_id)
            
            # Update result type
            result.recovery_type = RecoveryType.POINT_IN_TIME_RESTORE
            result.recovery_id = recovery_id
            
            self.logger.info(f"Point-in-time restore completed: {recovery_id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Point-in-time restore failed: {str(e)}"
            self.logger.error(error_msg)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.POINT_IN_TIME_RESTORE,
                timestamp=start_time,
                backup_id="unknown",
                success=False,
                files_restored=0,
                errors=[error_msg],
                duration_seconds=duration
            )
            
            self._save_recovery_result(result)
            return result
    
    def rollback_to_restore_point(self, restore_point_id: str) -> RecoveryResult:
        """
        Rollback the system to a previous restore point.
        
        Args:
            restore_point_id: ID of the restore point to rollback to.
            
        Returns:
            RecoveryResult: Result of the rollback operation.
        """
        start_time = datetime.now()
        recovery_id = self._generate_recovery_id("rollback")
        
        self.logger.info(f"Starting rollback: {recovery_id}")
        
        try:
            # Verify restore point exists
            restore_point_path = self.recovery_dir / f"restore_point_{restore_point_id}.zip"
            if not restore_point_path.exists():
                raise ValueError(f"Restore point not found: {restore_point_id}")
            
            # Create new restore point before rollback
            new_restore_point_id = None
            if self.config.create_restore_point:
                new_restore_point_id = self._create_restore_point()
            
            # Perform rollback
            files_restored = self._extract_backup(restore_point_path, restore_all=True)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create success result
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.ROLLBACK,
                timestamp=start_time,
                backup_id=restore_point_id,
                success=True,
                files_restored=files_restored,
                errors=[],
                duration_seconds=duration,
                restore_point_created=new_restore_point_id
            )
            
            self._save_recovery_result(result)
            self.logger.info(f"Rollback completed: {recovery_id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Rollback failed: {str(e)}"
            self.logger.error(error_msg)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = RecoveryResult(
                recovery_id=recovery_id,
                recovery_type=RecoveryType.ROLLBACK,
                timestamp=start_time,
                backup_id=restore_point_id,
                success=False,
                files_restored=0,
                errors=[error_msg],
                duration_seconds=duration
            )
            
            self._save_recovery_result(result)
            return result
    
    def list_available_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups for recovery.
        
        Returns:
            List[Dict]: List of available backups with metadata.
        """
        backups = []
        backup_status = self.backup_strategy.get_backup_status()
        
        for metadata in self.backup_strategy.metadata_history:
            if metadata.status == "completed":
                backups.append({
                    "backup_id": metadata.backup_id,
                    "timestamp": metadata.timestamp.isoformat(),
                    "backup_type": metadata.backup_type,
                    "file_count": metadata.file_count,
                    "size_mb": metadata.total_size_bytes / (1024 * 1024),
                    "checksum": metadata.checksum
                })
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """
        Get the current recovery status and statistics.
        
        Returns:
            Dict: Recovery status information.
        """
        total_recoveries = len(self.recovery_history)
        successful_recoveries = len([r for r in self.recovery_history if r.success])
        failed_recoveries = len([r for r in self.recovery_history if not r.success])
        
        last_recovery = max(self.recovery_history, key=lambda x: x.timestamp) if self.recovery_history else None
        
        return {
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "failed_recoveries": failed_recoveries,
            "success_rate": (successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0,
            "last_recovery": {
                "recovery_id": last_recovery.recovery_id,
                "timestamp": last_recovery.timestamp.isoformat(),
                "success": last_recovery.success,
                "type": last_recovery.recovery_type.value,
                "files_restored": last_recovery.files_restored
            } if last_recovery else None,
            "available_backups": len(self.list_available_backups()),
            "recovery_directory": str(self.recovery_dir)
        }
    
    def _generate_recovery_id(self, recovery_type: str) -> str:
        """Generate a unique recovery ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{recovery_type}_{timestamp}"
    
    def _get_latest_backup(self) -> Optional[BackupMetadata]:
        """Get the latest successful backup."""
        successful_backups = [
            m for m in self.backup_strategy.metadata_history
            if m.status == "completed"
        ]
        
        if not successful_backups:
            return None
        
        return max(successful_backups, key=lambda x: x.timestamp)
    
    def _get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get metadata for a specific backup."""
        for metadata in self.backup_strategy.metadata_history:
            if metadata.backup_id == backup_id:
                return metadata
        return None
    
    def _find_backup_for_time(self, target_time: datetime) -> Optional[BackupMetadata]:
        """Find the best backup for a specific point in time."""
        suitable_backups = [
            m for m in self.backup_strategy.metadata_history
            if m.status == "completed" and m.timestamp <= target_time
        ]
        
        if not suitable_backups:
            return None
        
        return max(suitable_backups, key=lambda x: x.timestamp)
    
    def _verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify the integrity of a backup before restore."""
        try:
            backup_path = Path(self.config.backup_directory) / f"{backup_id}.zip"
            
            if not backup_path.exists():
                return False
            
            # Test ZIP file integrity
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                bad_file = zipf.testzip()
                return bad_file is None
                
        except Exception as e:
            self.logger.error(f"Backup integrity check failed: {str(e)}")
            return False
    
    def _create_restore_point(self) -> str:
        """Create a restore point before performing recovery operations."""
        restore_point_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        restore_point_path = self.recovery_dir / f"restore_point_{restore_point_id}.zip"
        
        try:
            with zipfile.ZipFile(restore_point_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup current configuration files
                config_files = [
                    Path("config.json"),
                    Path("scan_cache.json"),
                    Path("performance_history.json")
                ]
                
                for file_path in config_files:
                    if file_path.exists():
                        zipf.write(file_path, file_path.name)
            
            self.logger.info(f"Restore point created: {restore_point_id}")
            return restore_point_id
            
        except Exception as e:
            self.logger.error(f"Failed to create restore point: {str(e)}")
            raise
    
    def _extract_backup(self, backup_path: Path, restore_all: bool = True) -> int:
        """Extract files from a backup archive."""
        files_restored = 0
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            for file_info in zipf.filelist:
                if file_info.is_dir():
                    continue
                
                # Determine target path
                if file_info.filename.startswith('config/'):
                    target_path = Path(file_info.filename[7:])  # Remove 'config/' prefix
                elif file_info.filename.startswith('cache/'):
                    target_path = Path(file_info.filename[6:])   # Remove 'cache/' prefix
                elif file_info.filename.startswith('reports/'):
                    target_path = Path("reports") / file_info.filename[8:]  # Remove 'reports/' prefix
                elif file_info.filename.startswith('logs/'):
                    target_path = Path("logs") / file_info.filename[5:]     # Remove 'logs/' prefix
                else:
                    target_path = Path(file_info.filename)
                
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract file
                with zipf.open(file_info) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                files_restored += 1
        
        return files_restored
    
    def _extract_selective(self, backup_path: Path, file_patterns: List[str]) -> int:
        """Extract specific files from a backup archive based on patterns."""
        import fnmatch
        
        files_restored = 0
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            for file_info in zipf.filelist:
                if file_info.is_dir():
                    continue
                
                # Check if file matches any pattern
                matches_pattern = False
                for pattern in file_patterns:
                    if fnmatch.fnmatch(file_info.filename, pattern):
                        matches_pattern = True
                        break
                
                if not matches_pattern:
                    continue
                
                # Determine target path (same logic as _extract_backup)
                if file_info.filename.startswith('config/'):
                    target_path = Path(file_info.filename[7:])
                elif file_info.filename.startswith('cache/'):
                    target_path = Path(file_info.filename[6:])
                elif file_info.filename.startswith('reports/'):
                    target_path = Path("reports") / file_info.filename[8:]
                elif file_info.filename.startswith('logs/'):
                    target_path = Path("logs") / file_info.filename[5:]
                else:
                    target_path = Path(file_info.filename)
                
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract file
                with zipf.open(file_info) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                files_restored += 1
        
        return files_restored
    
    def _load_recovery_history(self) -> List[RecoveryResult]:
        """Load recovery history from file."""
        if not self.recovery_history_file.exists():
            return []
        
        try:
            with open(self.recovery_history_file, 'r') as f:
                data = json.load(f)
                return [
                    RecoveryResult(
                        recovery_id=item['recovery_id'],
                        recovery_type=RecoveryType(item['recovery_type']),
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        backup_id=item['backup_id'],
                        success=item['success'],
                        files_restored=item['files_restored'],
                        errors=item['errors'],
                        duration_seconds=item['duration_seconds'],
                        restore_point_created=item.get('restore_point_created')
                    )
                    for item in data
                ]
        except Exception as e:
            self.logger.error(f"Failed to load recovery history: {str(e)}")
            return []
    
    def _save_recovery_result(self, result: RecoveryResult):
        """Save recovery result to history."""
        self.recovery_history.append(result)
        self._save_recovery_history()
    
    def _save_recovery_history(self):
        """Save recovery history to file."""
        try:
            data = []
            for result in self.recovery_history:
                data.append({
                    'recovery_id': result.recovery_id,
                    'recovery_type': result.recovery_type.value,
                    'timestamp': result.timestamp.isoformat(),
                    'backup_id': result.backup_id,
                    'success': result.success,
                    'files_restored': result.files_restored,
                    'errors': result.errors,
                    'duration_seconds': result.duration_seconds,
                    'restore_point_created': result.restore_point_created
                })
            
            with open(self.recovery_history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save recovery history: {str(e)}")