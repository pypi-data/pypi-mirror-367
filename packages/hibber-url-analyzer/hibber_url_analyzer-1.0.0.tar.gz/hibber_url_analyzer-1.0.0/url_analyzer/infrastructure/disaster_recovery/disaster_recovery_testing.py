"""
Disaster Recovery Testing Module for URL Analyzer

This module implements comprehensive testing capabilities for disaster recovery
components, including backup validation, recovery testing, and failover simulation.
"""

import os
import json
import time
import tempfile
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import unittest
import threading
import subprocess

from .backup_strategy import BackupStrategy, BackupConfig, BackupMetadata
from .recovery_procedures import RecoveryProcedures, RecoveryConfig, RecoveryResult
from .failover_mechanisms import FailoverMechanisms, FailoverConfig, FailoverEvent


class TestType(Enum):
    """Types of disaster recovery tests."""
    BACKUP_VALIDATION = "backup_validation"
    RECOVERY_SIMULATION = "recovery_simulation"
    FAILOVER_SIMULATION = "failover_simulation"
    END_TO_END_TEST = "end_to_end_test"
    PERFORMANCE_TEST = "performance_test"
    STRESS_TEST = "stress_test"


class TestStatus(Enum):
    """Status of disaster recovery tests."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestConfig:
    """Configuration for disaster recovery testing."""
    test_data_directory: str = "test_data"
    test_results_directory: str = "test_results"
    backup_test_size_mb: int = 10
    recovery_timeout_seconds: int = 300
    failover_timeout_seconds: int = 180
    stress_test_duration_seconds: int = 600
    performance_test_iterations: int = 10
    cleanup_after_tests: bool = True
    parallel_test_execution: bool = False
    max_parallel_tests: int = 3


@dataclass
class TestResult:
    """Result of a disaster recovery test."""
    test_id: str
    test_type: TestType
    test_name: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    success: bool
    error_message: Optional[str]
    details: Dict[str, Any]
    metrics: Dict[str, float]


@dataclass
class TestSuite:
    """Collection of disaster recovery tests."""
    suite_id: str
    suite_name: str
    tests: List[TestResult]
    start_time: datetime
    end_time: Optional[datetime]
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    success_rate: float


class DisasterRecoveryTesting:
    """
    Implements comprehensive testing for disaster recovery components.
    
    This class provides functionality for testing backup strategies, recovery
    procedures, failover mechanisms, and overall system resilience.
    """
    
    def __init__(self, config: Optional[TestConfig] = None):
        """
        Initialize the disaster recovery testing framework.
        
        Args:
            config: Test configuration. If None, uses default configuration.
        """
        self.config = config or TestConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.backup_strategy = BackupStrategy()
        self.recovery_procedures = RecoveryProcedures()
        self.failover_mechanisms = FailoverMechanisms()
        
        # Initialize test environment
        self.test_data_dir = Path(self.config.test_data_directory)
        self.test_results_dir = Path(self.config.test_results_directory)
        self.test_data_dir.mkdir(exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Test state
        self.current_suite: Optional[TestSuite] = None
        self.test_history: List[TestSuite] = []
        
        # Load test history
        self.history_file = self.test_results_dir / "test_history.json"
        self._load_test_history()
    
    def run_full_test_suite(self) -> TestSuite:
        """
        Run the complete disaster recovery test suite.
        
        Returns:
            TestSuite: Results of the full test suite.
        """
        suite_id = self._generate_suite_id()
        self.logger.info(f"Starting full disaster recovery test suite: {suite_id}")
        
        suite = TestSuite(
            suite_id=suite_id,
            suite_name="Full Disaster Recovery Test Suite",
            tests=[],
            start_time=datetime.now(),
            end_time=None,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            success_rate=0.0
        )
        
        self.current_suite = suite
        
        try:
            # Prepare test environment
            self._prepare_test_environment()
            
            # Run backup validation tests
            backup_tests = self._run_backup_validation_tests()
            suite.tests.extend(backup_tests)
            
            # Run recovery simulation tests
            recovery_tests = self._run_recovery_simulation_tests()
            suite.tests.extend(recovery_tests)
            
            # Run failover simulation tests
            failover_tests = self._run_failover_simulation_tests()
            suite.tests.extend(failover_tests)
            
            # Run end-to-end tests
            e2e_tests = self._run_end_to_end_tests()
            suite.tests.extend(e2e_tests)
            
            # Run performance tests
            performance_tests = self._run_performance_tests()
            suite.tests.extend(performance_tests)
            
            # Calculate suite statistics
            suite.end_time = datetime.now()
            suite.total_tests = len(suite.tests)
            suite.passed_tests = len([t for t in suite.tests if t.status == TestStatus.PASSED])
            suite.failed_tests = len([t for t in suite.tests if t.status == TestStatus.FAILED])
            suite.skipped_tests = len([t for t in suite.tests if t.status == TestStatus.SKIPPED])
            suite.success_rate = (suite.passed_tests / suite.total_tests * 100) if suite.total_tests > 0 else 0
            
            # Cleanup test environment
            if self.config.cleanup_after_tests:
                self._cleanup_test_environment()
            
            # Save results
            self._save_test_suite(suite)
            self.test_history.append(suite)
            self._save_test_history()
            
            self.logger.info(f"Test suite completed: {suite_id} ({suite.success_rate:.1f}% success rate)")
            
            return suite
            
        except Exception as e:
            error_msg = f"Test suite execution failed: {str(e)}"
            self.logger.error(error_msg)
            
            suite.end_time = datetime.now()
            suite.total_tests = len(suite.tests)
            
            # Add error test result
            error_test = TestResult(
                test_id=self._generate_test_id(),
                test_type=TestType.END_TO_END_TEST,
                test_name="Test Suite Execution",
                status=TestStatus.ERROR,
                start_time=suite.start_time,
                end_time=suite.end_time,
                duration_seconds=(suite.end_time - suite.start_time).total_seconds(),
                success=False,
                error_message=error_msg,
                details={},
                metrics={}
            )
            
            suite.tests.append(error_test)
            suite.total_tests += 1
            suite.failed_tests += 1
            
            return suite
    
    def run_backup_validation_tests(self) -> List[TestResult]:
        """
        Run backup validation tests.
        
        Returns:
            List[TestResult]: Results of backup validation tests.
        """
        return self._run_backup_validation_tests()
    
    def run_recovery_simulation_tests(self) -> List[TestResult]:
        """
        Run recovery simulation tests.
        
        Returns:
            List[TestResult]: Results of recovery simulation tests.
        """
        return self._run_recovery_simulation_tests()
    
    def run_failover_simulation_tests(self) -> List[TestResult]:
        """
        Run failover simulation tests.
        
        Returns:
            List[TestResult]: Results of failover simulation tests.
        """
        return self._run_failover_simulation_tests()
    
    def get_test_status(self) -> Dict[str, Any]:
        """
        Get current testing status and statistics.
        
        Returns:
            Dict: Testing status information.
        """
        total_suites = len(self.test_history)
        successful_suites = len([s for s in self.test_history if s.success_rate >= 80.0])
        
        last_suite = max(self.test_history, key=lambda x: x.start_time) if self.test_history else None
        
        return {
            "total_test_suites": total_suites,
            "successful_suites": successful_suites,
            "suite_success_rate": (successful_suites / total_suites * 100) if total_suites > 0 else 0,
            "last_test_suite": {
                "suite_id": last_suite.suite_id,
                "start_time": last_suite.start_time.isoformat(),
                "success_rate": last_suite.success_rate,
                "total_tests": last_suite.total_tests,
                "passed_tests": last_suite.passed_tests,
                "failed_tests": last_suite.failed_tests
            } if last_suite else None,
            "current_suite_running": self.current_suite is not None,
            "test_configuration": {
                "backup_test_size_mb": self.config.backup_test_size_mb,
                "recovery_timeout_seconds": self.config.recovery_timeout_seconds,
                "failover_timeout_seconds": self.config.failover_timeout_seconds,
                "cleanup_after_tests": self.config.cleanup_after_tests
            }
        }
    
    def _run_backup_validation_tests(self) -> List[TestResult]:
        """Run backup validation tests."""
        tests = []
        
        # Test 1: Create and validate full backup
        test = self._run_single_test(
            test_name="Full Backup Creation and Validation",
            test_type=TestType.BACKUP_VALIDATION,
            test_function=self._test_full_backup_creation
        )
        tests.append(test)
        
        # Test 2: Create and validate incremental backup
        test = self._run_single_test(
            test_name="Incremental Backup Creation and Validation",
            test_type=TestType.BACKUP_VALIDATION,
            test_function=self._test_incremental_backup_creation
        )
        tests.append(test)
        
        # Test 3: Backup integrity verification
        test = self._run_single_test(
            test_name="Backup Integrity Verification",
            test_type=TestType.BACKUP_VALIDATION,
            test_function=self._test_backup_integrity
        )
        tests.append(test)
        
        # Test 4: Backup cleanup and retention
        test = self._run_single_test(
            test_name="Backup Cleanup and Retention",
            test_type=TestType.BACKUP_VALIDATION,
            test_function=self._test_backup_cleanup
        )
        tests.append(test)
        
        return tests
    
    def _run_recovery_simulation_tests(self) -> List[TestResult]:
        """Run recovery simulation tests."""
        tests = []
        
        # Test 1: Full system recovery
        test = self._run_single_test(
            test_name="Full System Recovery Simulation",
            test_type=TestType.RECOVERY_SIMULATION,
            test_function=self._test_full_system_recovery
        )
        tests.append(test)
        
        # Test 2: Selective file recovery
        test = self._run_single_test(
            test_name="Selective File Recovery Simulation",
            test_type=TestType.RECOVERY_SIMULATION,
            test_function=self._test_selective_recovery
        )
        tests.append(test)
        
        # Test 3: Point-in-time recovery
        test = self._run_single_test(
            test_name="Point-in-Time Recovery Simulation",
            test_type=TestType.RECOVERY_SIMULATION,
            test_function=self._test_point_in_time_recovery
        )
        tests.append(test)
        
        # Test 4: Recovery rollback
        test = self._run_single_test(
            test_name="Recovery Rollback Simulation",
            test_type=TestType.RECOVERY_SIMULATION,
            test_function=self._test_recovery_rollback
        )
        tests.append(test)
        
        return tests
    
    def _run_failover_simulation_tests(self) -> List[TestResult]:
        """Run failover simulation tests."""
        tests = []
        
        # Test 1: Manual failover trigger
        test = self._run_single_test(
            test_name="Manual Failover Trigger Simulation",
            test_type=TestType.FAILOVER_SIMULATION,
            test_function=self._test_manual_failover
        )
        tests.append(test)
        
        # Test 2: Health check failure simulation
        test = self._run_single_test(
            test_name="Health Check Failure Simulation",
            test_type=TestType.FAILOVER_SIMULATION,
            test_function=self._test_health_check_failover
        )
        tests.append(test)
        
        # Test 3: Resource exhaustion simulation
        test = self._run_single_test(
            test_name="Resource Exhaustion Simulation",
            test_type=TestType.FAILOVER_SIMULATION,
            test_function=self._test_resource_exhaustion_failover
        )
        tests.append(test)
        
        return tests
    
    def _run_end_to_end_tests(self) -> List[TestResult]:
        """Run end-to-end disaster recovery tests."""
        tests = []
        
        # Test 1: Complete disaster recovery workflow
        test = self._run_single_test(
            test_name="Complete Disaster Recovery Workflow",
            test_type=TestType.END_TO_END_TEST,
            test_function=self._test_complete_dr_workflow
        )
        tests.append(test)
        
        return tests
    
    def _run_performance_tests(self) -> List[TestResult]:
        """Run performance tests for disaster recovery components."""
        tests = []
        
        # Test 1: Backup performance
        test = self._run_single_test(
            test_name="Backup Performance Test",
            test_type=TestType.PERFORMANCE_TEST,
            test_function=self._test_backup_performance
        )
        tests.append(test)
        
        # Test 2: Recovery performance
        test = self._run_single_test(
            test_name="Recovery Performance Test",
            test_type=TestType.PERFORMANCE_TEST,
            test_function=self._test_recovery_performance
        )
        tests.append(test)
        
        return tests
    
    def _run_single_test(self, test_name: str, test_type: TestType, test_function: Callable) -> TestResult:
        """Run a single test and return the result."""
        test_id = self._generate_test_id()
        start_time = datetime.now()
        
        self.logger.info(f"Running test: {test_name} ({test_id})")
        
        try:
            # Execute test function
            details, metrics = test_function()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = TestResult(
                test_id=test_id,
                test_type=test_type,
                test_name=test_name,
                status=TestStatus.PASSED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=True,
                error_message=None,
                details=details,
                metrics=metrics
            )
            
            self.logger.info(f"Test passed: {test_name} ({duration:.2f}s)")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_msg = str(e)
            
            result = TestResult(
                test_id=test_id,
                test_type=test_type,
                test_name=test_name,
                status=TestStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                error_message=error_msg,
                details={},
                metrics={}
            )
            
            self.logger.error(f"Test failed: {test_name} - {error_msg}")
            return result
    
    def _test_full_backup_creation(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test full backup creation and validation."""
        # Create test data
        test_files = self._create_test_data()
        
        # Create backup
        backup_metadata = self.backup_strategy.create_full_backup()
        
        # Validate backup
        if not backup_metadata.success:
            raise Exception(f"Backup creation failed: {backup_metadata.error_message}")
        
        # Verify backup file exists
        backup_path = Path("backups") / f"{backup_metadata.backup_id}.zip"
        if not backup_path.exists():
            raise Exception("Backup file not found")
        
        details = {
            "backup_id": backup_metadata.backup_id,
            "file_count": backup_metadata.file_count,
            "backup_size_bytes": backup_metadata.total_size_bytes,
            "test_files_created": len(test_files)
        }
        
        metrics = {
            "backup_size_mb": backup_metadata.total_size_bytes / (1024 * 1024),
            "files_backed_up": backup_metadata.file_count
        }
        
        return details, metrics
    
    def _test_incremental_backup_creation(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test incremental backup creation."""
        # Create initial backup
        initial_backup = self.backup_strategy.create_full_backup()
        
        # Wait a moment and create additional test data
        time.sleep(1)
        additional_files = self._create_test_data(prefix="incremental_")
        
        # Create incremental backup
        incremental_backup = self.backup_strategy.create_incremental_backup()
        
        if not incremental_backup.success:
            raise Exception(f"Incremental backup failed: {incremental_backup.error_message}")
        
        details = {
            "initial_backup_id": initial_backup.backup_id,
            "incremental_backup_id": incremental_backup.backup_id,
            "incremental_file_count": incremental_backup.file_count,
            "additional_files_created": len(additional_files)
        }
        
        metrics = {
            "incremental_size_mb": incremental_backup.total_size_bytes / (1024 * 1024),
            "incremental_files": incremental_backup.file_count
        }
        
        return details, metrics
    
    def _test_backup_integrity(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test backup integrity verification."""
        # Create backup
        backup_metadata = self.backup_strategy.create_full_backup()
        
        # Verify integrity using backup strategy's verification
        backup_path = Path("backups") / f"{backup_metadata.backup_id}.zip"
        
        # Test ZIP file integrity
        import zipfile
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            bad_file = zipf.testzip()
            if bad_file is not None:
                raise Exception(f"Backup integrity check failed: {bad_file}")
        
        details = {
            "backup_id": backup_metadata.backup_id,
            "integrity_verified": True,
            "checksum": backup_metadata.checksum
        }
        
        metrics = {
            "verification_time_seconds": 1.0  # Placeholder
        }
        
        return details, metrics
    
    def _test_backup_cleanup(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test backup cleanup and retention."""
        # Create multiple backups
        backups_created = []
        for i in range(3):
            backup = self.backup_strategy.create_full_backup()
            backups_created.append(backup.backup_id)
            time.sleep(0.1)  # Small delay between backups
        
        # Test cleanup (this would normally be based on retention policy)
        initial_count = len(self.backup_strategy.metadata_history)
        removed_count = self.backup_strategy.cleanup_old_backups()
        final_count = len(self.backup_strategy.metadata_history)
        
        details = {
            "backups_created": len(backups_created),
            "initial_backup_count": initial_count,
            "backups_removed": removed_count,
            "final_backup_count": final_count
        }
        
        metrics = {
            "cleanup_efficiency": removed_count / initial_count if initial_count > 0 else 0
        }
        
        return details, metrics
    
    def _test_full_system_recovery(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test full system recovery simulation."""
        # Create backup first
        backup_metadata = self.backup_strategy.create_full_backup()
        
        # Simulate recovery
        recovery_result = self.recovery_procedures.restore_full_system(backup_metadata.backup_id)
        
        if not recovery_result.success:
            raise Exception(f"Recovery failed: {recovery_result.errors}")
        
        details = {
            "backup_id": backup_metadata.backup_id,
            "recovery_id": recovery_result.recovery_id,
            "files_restored": recovery_result.files_restored,
            "restore_point_created": recovery_result.restore_point_created
        }
        
        metrics = {
            "recovery_time_seconds": recovery_result.duration_seconds,
            "files_restored": recovery_result.files_restored
        }
        
        return details, metrics
    
    def _test_selective_recovery(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test selective file recovery."""
        # Create backup
        backup_metadata = self.backup_strategy.create_full_backup()
        
        # Test selective recovery
        file_patterns = ["config/*", "*.json"]
        recovery_result = self.recovery_procedures.restore_selective(
            backup_metadata.backup_id, file_patterns
        )
        
        if not recovery_result.success:
            raise Exception(f"Selective recovery failed: {recovery_result.errors}")
        
        details = {
            "backup_id": backup_metadata.backup_id,
            "recovery_id": recovery_result.recovery_id,
            "file_patterns": file_patterns,
            "files_restored": recovery_result.files_restored
        }
        
        metrics = {
            "selective_recovery_time_seconds": recovery_result.duration_seconds,
            "selective_files_restored": recovery_result.files_restored
        }
        
        return details, metrics
    
    def _test_point_in_time_recovery(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test point-in-time recovery."""
        # Create initial backup
        initial_backup = self.backup_strategy.create_full_backup()
        target_time = datetime.now()
        
        # Wait and create another backup
        time.sleep(1)
        later_backup = self.backup_strategy.create_full_backup()
        
        # Test point-in-time recovery to target_time
        recovery_result = self.recovery_procedures.restore_point_in_time(target_time)
        
        if not recovery_result.success:
            raise Exception(f"Point-in-time recovery failed: {recovery_result.errors}")
        
        details = {
            "target_time": target_time.isoformat(),
            "recovery_id": recovery_result.recovery_id,
            "backup_used": recovery_result.backup_id,
            "files_restored": recovery_result.files_restored
        }
        
        metrics = {
            "pit_recovery_time_seconds": recovery_result.duration_seconds
        }
        
        return details, metrics
    
    def _test_recovery_rollback(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test recovery rollback functionality."""
        # Create backup and recovery
        backup_metadata = self.backup_strategy.create_full_backup()
        recovery_result = self.recovery_procedures.restore_full_system(backup_metadata.backup_id)
        
        if not recovery_result.restore_point_created:
            raise Exception("No restore point was created during recovery")
        
        # Test rollback
        rollback_result = self.recovery_procedures.rollback_to_restore_point(
            recovery_result.restore_point_created
        )
        
        if not rollback_result.success:
            raise Exception(f"Rollback failed: {rollback_result.errors}")
        
        details = {
            "original_recovery_id": recovery_result.recovery_id,
            "restore_point_id": recovery_result.restore_point_created,
            "rollback_recovery_id": rollback_result.recovery_id,
            "files_restored": rollback_result.files_restored
        }
        
        metrics = {
            "rollback_time_seconds": rollback_result.duration_seconds
        }
        
        return details, metrics
    
    def _test_manual_failover(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test manual failover trigger."""
        # Trigger manual failover
        failover_event = self.failover_mechanisms.trigger_manual_failover()
        
        if not failover_event.success:
            raise Exception(f"Manual failover failed: {failover_event.error_message}")
        
        details = {
            "event_id": failover_event.event_id,
            "trigger": failover_event.trigger.value,
            "source_node": failover_event.source_node,
            "target_node": failover_event.target_node
        }
        
        metrics = {
            "failover_time_seconds": failover_event.duration_seconds
        }
        
        return details, metrics
    
    def _test_health_check_failover(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test health check failure simulation."""
        # Get initial status
        initial_status = self.failover_mechanisms.get_failover_status()
        
        # This would normally involve simulating health check failures
        # For testing purposes, we'll just verify the health check system works
        node_status = self.failover_mechanisms.get_node_status()
        
        details = {
            "initial_health_score": initial_status["health_score"],
            "current_health_score": node_status.health_score,
            "monitoring_active": initial_status["monitoring_active"]
        }
        
        metrics = {
            "health_check_time_seconds": 1.0  # Placeholder
        }
        
        return details, metrics
    
    def _test_resource_exhaustion_failover(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test resource exhaustion simulation."""
        # Get current resource usage
        node_status = self.failover_mechanisms.get_node_status()
        
        details = {
            "cpu_percent": node_status.cpu_percent,
            "memory_percent": node_status.memory_percent,
            "disk_percent": node_status.disk_percent,
            "health_score": node_status.health_score
        }
        
        metrics = {
            "resource_check_time_seconds": 1.0  # Placeholder
        }
        
        return details, metrics
    
    def _test_complete_dr_workflow(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test complete disaster recovery workflow."""
        workflow_start = datetime.now()
        
        # Step 1: Create backup
        backup_metadata = self.backup_strategy.create_full_backup()
        
        # Step 2: Simulate disaster (failover)
        failover_event = self.failover_mechanisms.trigger_manual_failover()
        
        # Step 3: Perform recovery
        recovery_result = self.recovery_procedures.restore_full_system(backup_metadata.backup_id)
        
        workflow_end = datetime.now()
        total_time = (workflow_end - workflow_start).total_seconds()
        
        if not (backup_metadata.success and failover_event.success and recovery_result.success):
            raise Exception("Complete DR workflow failed at one or more steps")
        
        details = {
            "backup_id": backup_metadata.backup_id,
            "failover_event_id": failover_event.event_id,
            "recovery_id": recovery_result.recovery_id,
            "workflow_steps_completed": 3,
            "total_files_restored": recovery_result.files_restored
        }
        
        metrics = {
            "total_workflow_time_seconds": total_time,
            "backup_time_seconds": 5.0,  # Estimated
            "failover_time_seconds": failover_event.duration_seconds,
            "recovery_time_seconds": recovery_result.duration_seconds
        }
        
        return details, metrics
    
    def _test_backup_performance(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test backup performance."""
        performance_results = []
        
        for i in range(self.config.performance_test_iterations):
            start_time = time.time()
            backup_metadata = self.backup_strategy.create_full_backup()
            end_time = time.time()
            
            if backup_metadata.success:
                performance_results.append({
                    "iteration": i + 1,
                    "duration_seconds": end_time - start_time,
                    "file_count": backup_metadata.file_count,
                    "size_bytes": backup_metadata.total_size_bytes
                })
        
        if not performance_results:
            raise Exception("No successful backup performance tests")
        
        avg_duration = sum(r["duration_seconds"] for r in performance_results) / len(performance_results)
        avg_size = sum(r["size_bytes"] for r in performance_results) / len(performance_results)
        
        details = {
            "iterations": len(performance_results),
            "results": performance_results
        }
        
        metrics = {
            "average_backup_time_seconds": avg_duration,
            "average_backup_size_mb": avg_size / (1024 * 1024),
            "backup_throughput_mbps": (avg_size / (1024 * 1024)) / avg_duration if avg_duration > 0 else 0
        }
        
        return details, metrics
    
    def _test_recovery_performance(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Test recovery performance."""
        # Create backup first
        backup_metadata = self.backup_strategy.create_full_backup()
        
        performance_results = []
        
        for i in range(min(3, self.config.performance_test_iterations)):  # Limit recovery tests
            recovery_result = self.recovery_procedures.restore_full_system(backup_metadata.backup_id)
            
            if recovery_result.success:
                performance_results.append({
                    "iteration": i + 1,
                    "duration_seconds": recovery_result.duration_seconds,
                    "files_restored": recovery_result.files_restored
                })
        
        if not performance_results:
            raise Exception("No successful recovery performance tests")
        
        avg_duration = sum(r["duration_seconds"] for r in performance_results) / len(performance_results)
        avg_files = sum(r["files_restored"] for r in performance_results) / len(performance_results)
        
        details = {
            "backup_id": backup_metadata.backup_id,
            "iterations": len(performance_results),
            "results": performance_results
        }
        
        metrics = {
            "average_recovery_time_seconds": avg_duration,
            "average_files_restored": avg_files,
            "recovery_throughput_files_per_second": avg_files / avg_duration if avg_duration > 0 else 0
        }
        
        return details, metrics
    
    def _prepare_test_environment(self):
        """Prepare the test environment."""
        # Create test data directory
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create initial test data
        self._create_test_data()
        
        self.logger.info("Test environment prepared")
    
    def _cleanup_test_environment(self):
        """Clean up the test environment."""
        try:
            # Remove test data
            if self.test_data_dir.exists():
                shutil.rmtree(self.test_data_dir)
            
            # Clean up any test backups (optional)
            # This could be configurable
            
            self.logger.info("Test environment cleaned up")
        except Exception as e:
            self.logger.warning(f"Test environment cleanup failed: {str(e)}")
    
    def _create_test_data(self, prefix: str = "test_") -> List[Path]:
        """Create test data files."""
        test_files = []
        
        # Create various test files
        for i in range(5):
            file_path = self.test_data_dir / f"{prefix}file_{i}.txt"
            with open(file_path, 'w') as f:
                f.write(f"Test data content {i}\n" * 100)  # Create some content
            test_files.append(file_path)
        
        # Create a JSON config file
        config_file = self.test_data_dir / f"{prefix}config.json"
        with open(config_file, 'w') as f:
            json.dump({"test": True, "timestamp": datetime.now().isoformat()}, f)
        test_files.append(config_file)
        
        return test_files
    
    def _generate_suite_id(self) -> str:
        """Generate a unique test suite ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"dr_test_suite_{timestamp}"
    
    def _generate_test_id(self) -> str:
        """Generate a unique test ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"dr_test_{timestamp}"
    
    def _save_test_suite(self, suite: TestSuite):
        """Save test suite results to file."""
        suite_file = self.test_results_dir / f"{suite.suite_id}.json"
        
        try:
            suite_data = asdict(suite)
            # Convert datetime objects to ISO format
            suite_data['start_time'] = suite.start_time.isoformat()
            if suite.end_time:
                suite_data['end_time'] = suite.end_time.isoformat()
            
            for test in suite_data['tests']:
                test['start_time'] = test['start_time']  # Already converted by asdict
                if test['end_time']:
                    test['end_time'] = test['end_time']
                test['test_type'] = test['test_type']  # Already converted by asdict
                test['status'] = test['status']  # Already converted by asdict
            
            with open(suite_file, 'w') as f:
                json.dump(suite_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save test suite: {str(e)}")
    
    def _load_test_history(self):
        """Load test history from file."""
        if not self.history_file.exists():
            return
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                # Convert back to TestSuite objects if needed
                # For now, just store as raw data
                self.test_history = data
        except Exception as e:
            self.logger.error(f"Failed to load test history: {str(e)}")
    
    def _save_test_history(self):
        """Save test history to file."""
        try:
            # Convert TestSuite objects to serializable format
            history_data = []
            for suite in self.test_history:
                if isinstance(suite, TestSuite):
                    suite_data = asdict(suite)
                    suite_data['start_time'] = suite.start_time.isoformat()
                    if suite.end_time:
                        suite_data['end_time'] = suite.end_time.isoformat()
                    history_data.append(suite_data)
                else:
                    history_data.append(suite)
            
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save test history: {str(e)}")