"""
Business Continuity Planning Module for URL Analyzer

This module implements comprehensive business continuity planning for the URL Analyzer system,
including continuity strategies, impact analysis, and recovery planning.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ImpactLevel(Enum):
    """Impact levels for business continuity assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryPriority(Enum):
    """Recovery priorities for business functions."""
    P1_CRITICAL = "p1_critical"
    P2_HIGH = "p2_high"
    P3_MEDIUM = "p3_medium"
    P4_LOW = "p4_low"


@dataclass
class BusinessFunction:
    """Represents a business function for continuity planning."""
    function_id: str
    name: str
    description: str
    owner: str
    dependencies: List[str]
    recovery_priority: RecoveryPriority
    maximum_tolerable_downtime: int  # minutes
    recovery_time_objective: int  # minutes
    recovery_point_objective: int  # minutes
    impact_level: ImpactLevel
    critical_resources: List[str]


@dataclass
class ContinuityPlan:
    """Business continuity plan for a specific scenario."""
    plan_id: str
    scenario: str
    description: str
    affected_functions: List[str]
    recovery_steps: List[Dict[str, Any]]
    estimated_recovery_time: int  # minutes
    required_resources: List[str]
    communication_plan: Dict[str, Any]
    last_updated: datetime
    last_tested: Optional[datetime]


class BusinessContinuityPlanning:
    """
    Implements comprehensive business continuity planning for the URL Analyzer system.
    
    This class provides functionality for business impact analysis, continuity planning,
    and recovery coordination.
    """
    
    def __init__(self):
        """Initialize the business continuity planning system."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage
        self.bcp_dir = Path("business_continuity")
        self.bcp_dir.mkdir(exist_ok=True)
        
        # Initialize business functions and plans
        self.business_functions: Dict[str, BusinessFunction] = {}
        self.continuity_plans: Dict[str, ContinuityPlan] = {}
        
        # Load existing data
        self._load_business_functions()
        self._load_continuity_plans()
        
        # Initialize default functions if none exist
        if not self.business_functions:
            self._initialize_default_functions()
    
    def add_business_function(self, function: BusinessFunction):
        """Add a business function to the continuity planning system."""
        self.business_functions[function.function_id] = function
        self._save_business_functions()
        self.logger.info(f"Added business function: {function.name}")
    
    def create_continuity_plan(self, plan: ContinuityPlan):
        """Create a new business continuity plan."""
        self.continuity_plans[plan.plan_id] = plan
        self._save_continuity_plans()
        self.logger.info(f"Created continuity plan: {plan.scenario}")
    
    def get_business_impact_analysis(self) -> Dict[str, Any]:
        """
        Generate a business impact analysis report.
        
        Returns:
            Dict: Business impact analysis results.
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_functions": len(self.business_functions),
            "impact_distribution": {},
            "priority_distribution": {},
            "critical_functions": [],
            "recovery_objectives": {},
            "dependencies": {}
        }
        
        # Analyze impact distribution
        for impact in ImpactLevel:
            count = len([f for f in self.business_functions.values() if f.impact_level == impact])
            analysis["impact_distribution"][impact.value] = count
        
        # Analyze priority distribution
        for priority in RecoveryPriority:
            count = len([f for f in self.business_functions.values() if f.recovery_priority == priority])
            analysis["priority_distribution"][priority.value] = count
        
        # Identify critical functions
        critical_functions = [
            f for f in self.business_functions.values()
            if f.impact_level == ImpactLevel.CRITICAL or f.recovery_priority == RecoveryPriority.P1_CRITICAL
        ]
        
        for func in critical_functions:
            analysis["critical_functions"].append({
                "function_id": func.function_id,
                "name": func.name,
                "owner": func.owner,
                "rto_minutes": func.recovery_time_objective,
                "rpo_minutes": func.recovery_point_objective,
                "mtd_minutes": func.maximum_tolerable_downtime
            })
        
        # Calculate recovery objectives
        rtos = [f.recovery_time_objective for f in self.business_functions.values()]
        rpos = [f.recovery_point_objective for f in self.business_functions.values()]
        mtds = [f.maximum_tolerable_downtime for f in self.business_functions.values()]
        
        analysis["recovery_objectives"] = {
            "average_rto_minutes": sum(rtos) / len(rtos) if rtos else 0,
            "average_rpo_minutes": sum(rpos) / len(rpos) if rpos else 0,
            "average_mtd_minutes": sum(mtds) / len(mtds) if mtds else 0,
            "min_rto_minutes": min(rtos) if rtos else 0,
            "max_rto_minutes": max(rtos) if rtos else 0
        }
        
        return analysis
    
    def get_continuity_status(self) -> Dict[str, Any]:
        """
        Get current business continuity status.
        
        Returns:
            Dict: Continuity status information.
        """
        total_plans = len(self.continuity_plans)
        tested_plans = len([p for p in self.continuity_plans.values() if p.last_tested])
        outdated_plans = len([
            p for p in self.continuity_plans.values()
            if p.last_updated < datetime.now() - timedelta(days=365)
        ])
        
        return {
            "total_business_functions": len(self.business_functions),
            "total_continuity_plans": total_plans,
            "tested_plans": tested_plans,
            "untested_plans": total_plans - tested_plans,
            "outdated_plans": outdated_plans,
            "plan_coverage": (total_plans / len(self.business_functions) * 100) if self.business_functions else 0,
            "test_coverage": (tested_plans / total_plans * 100) if total_plans > 0 else 0
        }
    
    def _initialize_default_functions(self):
        """Initialize default business functions for URL analysis."""
        default_functions = [
            BusinessFunction(
                function_id="url_analysis",
                name="URL Analysis Service",
                description="Core URL analysis and classification functionality",
                owner="System Administrator",
                dependencies=["data_storage", "configuration"],
                recovery_priority=RecoveryPriority.P1_CRITICAL,
                maximum_tolerable_downtime=60,
                recovery_time_objective=30,
                recovery_point_objective=15,
                impact_level=ImpactLevel.CRITICAL,
                critical_resources=["url_analyzer", "config.json", "scan_cache.json"]
            ),
            BusinessFunction(
                function_id="report_generation",
                name="Report Generation",
                description="Generation of analysis reports and visualizations",
                owner="System Administrator",
                dependencies=["url_analysis", "data_storage"],
                recovery_priority=RecoveryPriority.P2_HIGH,
                maximum_tolerable_downtime=240,
                recovery_time_objective=120,
                recovery_point_objective=60,
                impact_level=ImpactLevel.HIGH,
                critical_resources=["templates", "reports"]
            ),
            BusinessFunction(
                function_id="data_storage",
                name="Data Storage",
                description="Persistent storage of analysis data and configurations",
                owner="System Administrator",
                dependencies=[],
                recovery_priority=RecoveryPriority.P1_CRITICAL,
                maximum_tolerable_downtime=30,
                recovery_time_objective=15,
                recovery_point_objective=5,
                impact_level=ImpactLevel.CRITICAL,
                critical_resources=["config.json", "scan_cache.json", "performance_history.json"]
            )
        ]
        
        for func in default_functions:
            self.add_business_function(func)
        
        # Create default continuity plans
        self._create_default_plans()
    
    def _create_default_plans(self):
        """Create default continuity plans."""
        default_plans = [
            ContinuityPlan(
                plan_id="system_failure",
                scenario="Complete System Failure",
                description="Recovery plan for complete system failure",
                affected_functions=["url_analysis", "report_generation", "data_storage"],
                recovery_steps=[
                    {"step": 1, "action": "Assess system status", "duration": 5},
                    {"step": 2, "action": "Restore from backup", "duration": 15},
                    {"step": 3, "action": "Verify system functionality", "duration": 10}
                ],
                estimated_recovery_time=30,
                required_resources=["backup_system", "administrator"],
                communication_plan={
                    "stakeholders": ["users", "management"],
                    "notification_methods": ["email", "status_page"]
                },
                last_updated=datetime.now(),
                last_tested=None
            )
        ]
        
        for plan in default_plans:
            self.create_continuity_plan(plan)
    
    def _load_business_functions(self):
        """Load business functions from file."""
        functions_file = self.bcp_dir / "business_functions.json"
        if not functions_file.exists():
            return
        
        try:
            with open(functions_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    func = BusinessFunction(
                        function_id=item['function_id'],
                        name=item['name'],
                        description=item['description'],
                        owner=item['owner'],
                        dependencies=item['dependencies'],
                        recovery_priority=RecoveryPriority(item['recovery_priority']),
                        maximum_tolerable_downtime=item['maximum_tolerable_downtime'],
                        recovery_time_objective=item['recovery_time_objective'],
                        recovery_point_objective=item['recovery_point_objective'],
                        impact_level=ImpactLevel(item['impact_level']),
                        critical_resources=item['critical_resources']
                    )
                    self.business_functions[func.function_id] = func
        except Exception as e:
            self.logger.error(f"Failed to load business functions: {str(e)}")
    
    def _save_business_functions(self):
        """Save business functions to file."""
        functions_file = self.bcp_dir / "business_functions.json"
        
        try:
            data = []
            for func in self.business_functions.values():
                item = asdict(func)
                item['recovery_priority'] = func.recovery_priority.value
                item['impact_level'] = func.impact_level.value
                data.append(item)
            
            with open(functions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save business functions: {str(e)}")
    
    def _load_continuity_plans(self):
        """Load continuity plans from file."""
        plans_file = self.bcp_dir / "continuity_plans.json"
        if not plans_file.exists():
            return
        
        try:
            with open(plans_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    plan = ContinuityPlan(
                        plan_id=item['plan_id'],
                        scenario=item['scenario'],
                        description=item['description'],
                        affected_functions=item['affected_functions'],
                        recovery_steps=item['recovery_steps'],
                        estimated_recovery_time=item['estimated_recovery_time'],
                        required_resources=item['required_resources'],
                        communication_plan=item['communication_plan'],
                        last_updated=datetime.fromisoformat(item['last_updated']),
                        last_tested=datetime.fromisoformat(item['last_tested']) if item.get('last_tested') else None
                    )
                    self.continuity_plans[plan.plan_id] = plan
        except Exception as e:
            self.logger.error(f"Failed to load continuity plans: {str(e)}")
    
    def _save_continuity_plans(self):
        """Save continuity plans to file."""
        plans_file = self.bcp_dir / "continuity_plans.json"
        
        try:
            data = []
            for plan in self.continuity_plans.values():
                item = asdict(plan)
                item['last_updated'] = plan.last_updated.isoformat()
                if plan.last_tested:
                    item['last_tested'] = plan.last_tested.isoformat()
                data.append(item)
            
            with open(plans_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save continuity plans: {str(e)}")