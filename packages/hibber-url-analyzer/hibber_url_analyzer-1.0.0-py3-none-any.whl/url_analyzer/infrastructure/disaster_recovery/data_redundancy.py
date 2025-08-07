"""
Data Redundancy Module for URL Analyzer

This module implements comprehensive data redundancy strategies for the URL Analyzer system,
including data replication, synchronization, and integrity verification.
"""

import os
import json
import shutil
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time


class RedundancyLevel(Enum):
    """Levels of data redundancy."""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"


class SyncStatus(Enum):
    """Status of data synchronization."""
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class RedundancyConfig:
    """Configuration for data redundancy."""
    primary_location: str = "."
    replica_locations: List[str] = None
    sync_interval_seconds: int = 300
    integrity_check_interval_seconds: int = 3600
    max_sync_retries: int = 3
    sync_timeout_seconds: int = 60
    enable_real_time_sync: bool = False
    compression_enabled: bool = True
    encryption_enabled: bool = False
    
    def __post_init__(self):
        if self.replica_locations is None:
            self.replica_locations = ["replica1", "replica2"]


@dataclass
class DataLocation:
    """Represents a data storage location."""
    location_id: str
    path: str
    is_primary: bool
    redundancy_level: RedundancyLevel
    last_sync: Optional[datetime]
    sync_status: SyncStatus
    integrity_hash: Optional[str]
    available: bool


@dataclass
class SyncOperation:
    """Record of a synchronization operation."""
    operation_id: str
    timestamp: datetime
    source_location: str
    target_location: str
    files_synced: int
    bytes_synced: int
    duration_seconds: float
    success: bool
    error_message: Optional[str]


class DataRedundancy:
    """
    Implements comprehensive data redundancy for the URL Analyzer system.
    
    This class provides functionality for data replication, synchronization,
    and integrity verification across multiple storage locations.
    """
    
    def __init__(self, config: Optional[RedundancyConfig] = None):
        """
        Initialize the data redundancy system.
        
        Args:
            config: Redundancy configuration. If None, uses default configuration.
        """
        self.config = config or RedundancyConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize data locations
        self.data_locations: Dict[str, DataLocation] = {}
        self.sync_history: List[SyncOperation] = []
        
        # Initialize storage
        self.redundancy_dir = Path("redundancy")
        self.redundancy_dir.mkdir(exist_ok=True)
        
        # Initialize monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Load existing configuration
        self._load_data_locations()
        self._load_sync_history()
        
        # Initialize default locations if none exist
        if not self.data_locations:
            self._initialize_default_locations()
    
    def add_data_location(self, location: DataLocation):
        """Add a data storage location to the redundancy system."""
        self.data_locations[location.location_id] = location
        
        # Create directory if it doesn't exist
        Path(location.path).mkdir(parents=True, exist_ok=True)
        
        self._save_data_locations()
        self.logger.info(f"Added data location: {location.location_id}")
    
    def start_monitoring(self):
        """Start continuous data synchronization monitoring."""
        if self.monitoring_active:
            self.logger.warning("Data redundancy monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Data redundancy monitoring started")
    
    def stop_monitoring(self):
        """Stop data synchronization monitoring."""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("Data redundancy monitoring stopped")
    
    def sync_all_locations(self) -> List[SyncOperation]:
        """
        Synchronize data across all configured locations.
        
        Returns:
            List[SyncOperation]: Results of synchronization operations.
        """
        sync_operations = []
        primary_location = self._get_primary_location()
        
        if not primary_location:
            self.logger.error("No primary location configured")
            return sync_operations
        
        # Sync from primary to all replicas
        for location_id, location in self.data_locations.items():
            if location.is_primary or not location.available:
                continue
            
            sync_op = self._sync_locations(primary_location, location)
            sync_operations.append(sync_op)
        
        return sync_operations
    
    def verify_data_integrity(self) -> Dict[str, Any]:
        """
        Verify data integrity across all locations.
        
        Returns:
            Dict: Integrity verification results.
        """
        verification_results = {
            "timestamp": datetime.now().isoformat(),
            "locations_checked": 0,
            "locations_healthy": 0,
            "integrity_issues": [],
            "location_details": {}
        }
        
        for location_id, location in self.data_locations.items():
            if not location.available:
                continue
            
            verification_results["locations_checked"] += 1
            
            try:
                # Calculate current integrity hash
                current_hash = self._calculate_location_hash(location)
                
                # Compare with stored hash
                integrity_ok = True
                if location.integrity_hash and location.integrity_hash != current_hash:
                    integrity_ok = False
                    verification_results["integrity_issues"].append({
                        "location_id": location_id,
                        "issue": "Hash mismatch",
                        "expected_hash": location.integrity_hash,
                        "actual_hash": current_hash
                    })
                
                # Update stored hash
                location.integrity_hash = current_hash
                
                if integrity_ok:
                    verification_results["locations_healthy"] += 1
                
                verification_results["location_details"][location_id] = {
                    "integrity_ok": integrity_ok,
                    "hash": current_hash,
                    "last_checked": datetime.now().isoformat()
                }
                
            except Exception as e:
                verification_results["integrity_issues"].append({
                    "location_id": location_id,
                    "issue": f"Verification failed: {str(e)}"
                })
        
        # Save updated location information
        self._save_data_locations()
        
        return verification_results
    
    def get_redundancy_status(self) -> Dict[str, Any]:
        """
        Get current data redundancy status.
        
        Returns:
            Dict: Redundancy status information.
        """
        total_locations = len(self.data_locations)
        available_locations = len([l for l in self.data_locations.values() if l.available])
        in_sync_locations = len([l for l in self.data_locations.values() if l.sync_status == SyncStatus.IN_SYNC])
        
        primary_location = self._get_primary_location()
        
        recent_syncs = [
            op for op in self.sync_history
            if op.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        successful_syncs = len([op for op in recent_syncs if op.success])
        failed_syncs = len([op for op in recent_syncs if not op.success])
        
        return {
            "total_locations": total_locations,
            "available_locations": available_locations,
            "in_sync_locations": in_sync_locations,
            "primary_location": primary_location.location_id if primary_location else None,
            "monitoring_active": self.monitoring_active,
            "sync_statistics": {
                "recent_syncs_24h": len(recent_syncs),
                "successful_syncs_24h": successful_syncs,
                "failed_syncs_24h": failed_syncs,
                "success_rate": (successful_syncs / len(recent_syncs) * 100) if recent_syncs else 0
            },
            "configuration": {
                "sync_interval_seconds": self.config.sync_interval_seconds,
                "integrity_check_interval_seconds": self.config.integrity_check_interval_seconds,
                "real_time_sync": self.config.enable_real_time_sync,
                "compression_enabled": self.config.compression_enabled
            }
        }
    
    def _initialize_default_locations(self):
        """Initialize default data locations."""
        # Primary location
        primary = DataLocation(
            location_id="primary",
            path=self.config.primary_location,
            is_primary=True,
            redundancy_level=RedundancyLevel.CRITICAL,
            last_sync=None,
            sync_status=SyncStatus.IN_SYNC,
            integrity_hash=None,
            available=True
        )
        self.add_data_location(primary)
        
        # Replica locations
        for i, replica_path in enumerate(self.config.replica_locations):
            replica = DataLocation(
                location_id=f"replica_{i+1}",
                path=replica_path,
                is_primary=False,
                redundancy_level=RedundancyLevel.STANDARD,
                last_sync=None,
                sync_status=SyncStatus.UNKNOWN,
                integrity_hash=None,
                available=True
            )
            self.add_data_location(replica)
    
    def _get_primary_location(self) -> Optional[DataLocation]:
        """Get the primary data location."""
        for location in self.data_locations.values():
            if location.is_primary and location.available:
                return location
        return None
    
    def _sync_locations(self, source: DataLocation, target: DataLocation) -> SyncOperation:
        """Synchronize data between two locations."""
        operation_id = self._generate_operation_id()
        start_time = datetime.now()
        
        self.logger.info(f"Starting sync: {source.location_id} -> {target.location_id}")
        
        try:
            # Update target status
            target.sync_status = SyncStatus.SYNCING
            
            # Perform synchronization
            files_synced, bytes_synced = self._perform_sync(source.path, target.path)
            
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Update target location
            target.last_sync = end_time
            target.sync_status = SyncStatus.IN_SYNC
            
            # Create operation record
            sync_op = SyncOperation(
                operation_id=operation_id,
                timestamp=start_time,
                source_location=source.location_id,
                target_location=target.location_id,
                files_synced=files_synced,
                bytes_synced=bytes_synced,
                duration_seconds=duration,
                success=True,
                error_message=None
            )
            
            self.sync_history.append(sync_op)
            self._save_sync_history()
            self._save_data_locations()
            
            self.logger.info(f"Sync completed: {operation_id} ({files_synced} files, {bytes_synced} bytes)")
            
            return sync_op
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Update target status
            target.sync_status = SyncStatus.ERROR
            
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Create operation record
            sync_op = SyncOperation(
                operation_id=operation_id,
                timestamp=start_time,
                source_location=source.location_id,
                target_location=target.location_id,
                files_synced=0,
                bytes_synced=0,
                duration_seconds=duration,
                success=False,
                error_message=error_msg
            )
            
            self.sync_history.append(sync_op)
            self._save_sync_history()
            self._save_data_locations()
            
            return sync_op
    
    def _perform_sync(self, source_path: str, target_path: str) -> Tuple[int, int]:
        """Perform the actual file synchronization."""
        source_dir = Path(source_path)
        target_dir = Path(target_path)
        
        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        
        files_synced = 0
        bytes_synced = 0
        
        # Get list of files to sync (important files only)
        sync_patterns = [
            "*.json",
            "*.log",
            "*.csv",
            "*.html",
            "*.txt"
        ]
        
        files_to_sync = []
        for pattern in sync_patterns:
            files_to_sync.extend(source_dir.glob(pattern))
        
        # Also include specific directories
        important_dirs = ["reports", "templates", "logs"]
        for dir_name in important_dirs:
            dir_path = source_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                files_to_sync.extend(dir_path.rglob("*"))
        
        # Sync files
        for source_file in files_to_sync:
            if source_file.is_file():
                # Calculate relative path
                rel_path = source_file.relative_to(source_dir)
                target_file = target_dir / rel_path
                
                # Create target directory if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if file needs to be synced
                needs_sync = True
                if target_file.exists():
                    source_mtime = source_file.stat().st_mtime
                    target_mtime = target_file.stat().st_mtime
                    needs_sync = source_mtime > target_mtime
                
                if needs_sync:
                    # Copy file
                    shutil.copy2(source_file, target_file)
                    files_synced += 1
                    bytes_synced += source_file.stat().st_size
        
        return files_synced, bytes_synced
    
    def _calculate_location_hash(self, location: DataLocation) -> str:
        """Calculate integrity hash for a data location."""
        location_path = Path(location.path)
        
        if not location_path.exists():
            return ""
        
        # Calculate hash of important files
        hasher = hashlib.sha256()
        
        # Get list of files to hash
        important_files = []
        for pattern in ["*.json", "*.log"]:
            important_files.extend(location_path.glob(pattern))
        
        # Sort files for consistent hashing
        important_files.sort(key=lambda x: str(x))
        
        for file_path in important_files:
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hasher.update(chunk)
                except Exception as e:
                    self.logger.warning(f"Failed to hash file {file_path}: {str(e)}")
        
        return hasher.hexdigest()
    
    def _monitoring_loop(self):
        """Main monitoring loop for data synchronization."""
        self.logger.info("Starting data redundancy monitoring loop")
        
        last_sync_time = datetime.min
        last_integrity_check = datetime.min
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Check if it's time for synchronization
                if (current_time - last_sync_time).total_seconds() >= self.config.sync_interval_seconds:
                    self.logger.info("Performing scheduled synchronization")
                    sync_operations = self.sync_all_locations()
                    
                    # Log sync results
                    successful_syncs = len([op for op in sync_operations if op.success])
                    failed_syncs = len([op for op in sync_operations if not op.success])
                    
                    if failed_syncs > 0:
                        self.logger.warning(f"Sync completed with {failed_syncs} failures out of {len(sync_operations)} operations")
                    else:
                        self.logger.info(f"Sync completed successfully ({successful_syncs} operations)")
                    
                    last_sync_time = current_time
                
                # Check if it's time for integrity verification
                if (current_time - last_integrity_check).total_seconds() >= self.config.integrity_check_interval_seconds:
                    self.logger.info("Performing integrity verification")
                    integrity_results = self.verify_data_integrity()
                    
                    if integrity_results["integrity_issues"]:
                        self.logger.warning(f"Integrity check found {len(integrity_results['integrity_issues'])} issues")
                    else:
                        self.logger.info("Integrity check completed successfully")
                    
                    last_integrity_check = current_time
                
                # Sleep for a short interval
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _generate_operation_id(self) -> str:
        """Generate a unique operation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sync_{timestamp}_{len(self.sync_history)}"
    
    def _load_data_locations(self):
        """Load data locations from file."""
        locations_file = self.redundancy_dir / "data_locations.json"
        if not locations_file.exists():
            return
        
        try:
            with open(locations_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    location = DataLocation(
                        location_id=item['location_id'],
                        path=item['path'],
                        is_primary=item['is_primary'],
                        redundancy_level=RedundancyLevel(item['redundancy_level']),
                        last_sync=datetime.fromisoformat(item['last_sync']) if item.get('last_sync') else None,
                        sync_status=SyncStatus(item['sync_status']),
                        integrity_hash=item.get('integrity_hash'),
                        available=item['available']
                    )
                    self.data_locations[location.location_id] = location
        except Exception as e:
            self.logger.error(f"Failed to load data locations: {str(e)}")
    
    def _save_data_locations(self):
        """Save data locations to file."""
        locations_file = self.redundancy_dir / "data_locations.json"
        
        try:
            data = []
            for location in self.data_locations.values():
                item = asdict(location)
                item['redundancy_level'] = location.redundancy_level.value
                item['sync_status'] = location.sync_status.value
                if location.last_sync:
                    item['last_sync'] = location.last_sync.isoformat()
                data.append(item)
            
            with open(locations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save data locations: {str(e)}")
    
    def _load_sync_history(self):
        """Load synchronization history from file."""
        history_file = self.redundancy_dir / "sync_history.json"
        if not history_file.exists():
            return
        
        try:
            with open(history_file, 'r') as f:
                data = json.load(f)
                self.sync_history = [
                    SyncOperation(
                        operation_id=item['operation_id'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        source_location=item['source_location'],
                        target_location=item['target_location'],
                        files_synced=item['files_synced'],
                        bytes_synced=item['bytes_synced'],
                        duration_seconds=item['duration_seconds'],
                        success=item['success'],
                        error_message=item.get('error_message')
                    )
                    for item in data
                ]
        except Exception as e:
            self.logger.error(f"Failed to load sync history: {str(e)}")
    
    def _save_sync_history(self):
        """Save synchronization history to file."""
        history_file = self.redundancy_dir / "sync_history.json"
        
        try:
            # Keep only recent history (last 1000 operations)
            recent_history = self.sync_history[-1000:] if len(self.sync_history) > 1000 else self.sync_history
            
            data = []
            for operation in recent_history:
                item = asdict(operation)
                item['timestamp'] = operation.timestamp.isoformat()
                data.append(item)
            
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save sync history: {str(e)}")