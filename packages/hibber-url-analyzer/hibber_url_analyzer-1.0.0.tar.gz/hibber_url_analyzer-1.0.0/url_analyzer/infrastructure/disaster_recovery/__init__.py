"""
Disaster Recovery Module for URL Analyzer

This module provides comprehensive disaster recovery capabilities including:
- Backup strategies and management
- Recovery procedures and restoration
- Failover mechanisms and high availability
- Disaster recovery testing and validation
- Business continuity planning
- Data redundancy and replication

The module is designed to ensure system resilience and data protection
for the URL Analyzer application.
"""

from .backup_strategy import BackupStrategy, BackupConfig, BackupMetadata
from .recovery_procedures import RecoveryProcedures, RecoveryConfig, RecoveryResult, RecoveryType
from .failover_mechanisms import FailoverMechanisms, FailoverConfig, FailoverEvent, FailoverStatus
from .disaster_recovery_testing import DisasterRecoveryTesting, TestConfig, TestResult, TestSuite
from .business_continuity_planning import BusinessContinuityPlanning, BusinessFunction, ContinuityPlan
from .data_redundancy import DataRedundancy, RedundancyConfig, DataLocation, SyncOperation

__version__ = "1.0.0"
__author__ = "URL Analyzer Team"

__all__ = [
    # Backup Strategy
    "BackupStrategy",
    "BackupConfig", 
    "BackupMetadata",
    
    # Recovery Procedures
    "RecoveryProcedures",
    "RecoveryConfig",
    "RecoveryResult",
    "RecoveryType",
    
    # Failover Mechanisms
    "FailoverMechanisms",
    "FailoverConfig",
    "FailoverEvent",
    "FailoverStatus",
    
    # Disaster Recovery Testing
    "DisasterRecoveryTesting",
    "TestConfig",
    "TestResult",
    "TestSuite",
    
    # Business Continuity Planning
    "BusinessContinuityPlanning",
    "BusinessFunction",
    "ContinuityPlan",
    
    # Data Redundancy
    "DataRedundancy",
    "RedundancyConfig",
    "DataLocation",
    "SyncOperation",
]


def get_disaster_recovery_status():
    """
    Get comprehensive disaster recovery status across all components.
    
    Returns:
        Dict: Overall disaster recovery status
    """
    try:
        # Initialize components
        backup_strategy = BackupStrategy()
        recovery_procedures = RecoveryProcedures()
        failover_mechanisms = FailoverMechanisms()
        dr_testing = DisasterRecoveryTesting()
        bcp = BusinessContinuityPlanning()
        data_redundancy = DataRedundancy()
        
        # Collect status from all components
        status = {
            "timestamp": backup_strategy.get_backup_status()["last_backup"]["timestamp"] if backup_strategy.get_backup_status().get("last_backup") else None,
            "backup_status": backup_strategy.get_backup_status(),
            "recovery_status": recovery_procedures.get_recovery_status(),
            "failover_status": failover_mechanisms.get_failover_status(),
            "testing_status": dr_testing.get_test_status(),
            "continuity_status": bcp.get_continuity_status(),
            "redundancy_status": data_redundancy.get_redundancy_status(),
            "overall_health": "healthy"  # This would be calculated based on component statuses
        }
        
        return status
        
    except Exception as e:
        return {
            "timestamp": None,
            "error": f"Failed to get disaster recovery status: {str(e)}",
            "overall_health": "error"
        }


def initialize_disaster_recovery():
    """
    Initialize all disaster recovery components with default configurations.
    
    Returns:
        Dict: Initialization results
    """
    results = {
        "initialized_components": [],
        "failed_components": [],
        "overall_success": True
    }
    
    components = [
        ("BackupStrategy", BackupStrategy),
        ("RecoveryProcedures", RecoveryProcedures),
        ("FailoverMechanisms", FailoverMechanisms),
        ("DisasterRecoveryTesting", DisasterRecoveryTesting),
        ("BusinessContinuityPlanning", BusinessContinuityPlanning),
        ("DataRedundancy", DataRedundancy),
    ]
    
    for component_name, component_class in components:
        try:
            component = component_class()
            results["initialized_components"].append(component_name)
        except Exception as e:
            results["failed_components"].append({
                "component": component_name,
                "error": str(e)
            })
            results["overall_success"] = False
    
    return results