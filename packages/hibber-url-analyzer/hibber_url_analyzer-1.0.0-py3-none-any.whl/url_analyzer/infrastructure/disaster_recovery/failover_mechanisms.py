"""
Failover Mechanisms Module for URL Analyzer

This module implements comprehensive failover mechanisms for the URL Analyzer system,
including automatic failover, health monitoring, and high availability features.
"""

import os
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import socket
import subprocess
import psutil


class FailoverTrigger(Enum):
    """Types of failover triggers."""
    HEALTH_CHECK_FAILURE = "health_check_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SERVICE_UNAVAILABLE = "service_unavailable"
    MANUAL_TRIGGER = "manual_trigger"
    NETWORK_FAILURE = "network_failure"
    DISK_FAILURE = "disk_failure"


class FailoverStatus(Enum):
    """Status of failover operations."""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILED_OVER = "failed_over"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"


@dataclass
class FailoverConfig:
    """Configuration for failover mechanisms."""
    health_check_interval_seconds: int = 30
    failover_timeout_seconds: int = 300
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 10
    enable_automatic_failover: bool = True
    enable_automatic_recovery: bool = True
    recovery_delay_seconds: int = 60
    health_check_endpoints: List[str] = None
    resource_thresholds: Dict[str, float] = None
    notification_webhooks: List[str] = None
    
    def __post_init__(self):
        if self.health_check_endpoints is None:
            self.health_check_endpoints = ["http://localhost:8000/health"]
        if self.resource_thresholds is None:
            self.resource_thresholds = {
                "cpu_percent": 90.0,
                "memory_percent": 85.0,
                "disk_percent": 95.0
            }
        if self.notification_webhooks is None:
            self.notification_webhooks = []


@dataclass
class FailoverEvent:
    """Record of a failover event."""
    event_id: str
    timestamp: datetime
    trigger: FailoverTrigger
    source_node: str
    target_node: Optional[str]
    success: bool
    duration_seconds: float
    error_message: Optional[str] = None
    recovery_timestamp: Optional[datetime] = None


@dataclass
class NodeStatus:
    """Status information for a node."""
    node_id: str
    status: FailoverStatus
    last_health_check: datetime
    health_score: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_latency_ms: float
    active_connections: int
    uptime_seconds: float


class HealthChecker:
    """Performs health checks on system components."""
    
    def __init__(self, config: FailoverConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Dict: Health check results.
        """
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": True,
            "checks": {}
        }
        
        # Check system resources
        resource_health = self._check_system_resources()
        health_results["checks"]["resources"] = resource_health
        if not resource_health["healthy"]:
            health_results["overall_healthy"] = False
        
        # Check network connectivity
        network_health = self._check_network_connectivity()
        health_results["checks"]["network"] = network_health
        if not network_health["healthy"]:
            health_results["overall_healthy"] = False
        
        # Check disk health
        disk_health = self._check_disk_health()
        health_results["checks"]["disk"] = disk_health
        if not disk_health["healthy"]:
            health_results["overall_healthy"] = False
        
        # Check service endpoints
        endpoint_health = self._check_service_endpoints()
        health_results["checks"]["endpoints"] = endpoint_health
        if not endpoint_health["healthy"]:
            health_results["overall_healthy"] = False
        
        return health_results
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            cpu_healthy = cpu_percent < self.config.resource_thresholds["cpu_percent"]
            memory_healthy = memory.percent < self.config.resource_thresholds["memory_percent"]
            
            return {
                "healthy": cpu_healthy and memory_healthy,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "cpu_healthy": cpu_healthy,
                "memory_healthy": memory_healthy,
                "thresholds": self.config.resource_thresholds
            }
        except Exception as e:
            self.logger.error(f"Resource health check failed: {str(e)}")
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity."""
        try:
            # Test DNS resolution
            socket.gethostbyname("google.com")
            
            # Test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("8.8.8.8", 53))
            sock.close()
            
            network_healthy = result == 0
            
            return {
                "healthy": network_healthy,
                "dns_resolution": True,
                "external_connectivity": network_healthy
            }
        except Exception as e:
            self.logger.error(f"Network health check failed: {str(e)}")
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk health and space."""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            disk_healthy = disk_percent < self.config.resource_thresholds["disk_percent"]
            
            return {
                "healthy": disk_healthy,
                "disk_percent": disk_percent,
                "free_gb": disk_usage.free / (1024**3),
                "total_gb": disk_usage.total / (1024**3)
            }
        except Exception as e:
            self.logger.error(f"Disk health check failed: {str(e)}")
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def _check_service_endpoints(self) -> Dict[str, Any]:
        """Check service endpoint availability."""
        endpoint_results = []
        overall_healthy = True
        
        for endpoint in self.config.health_check_endpoints:
            try:
                import requests
                response = requests.get(endpoint, timeout=10)
                endpoint_healthy = response.status_code == 200
                
                endpoint_results.append({
                    "endpoint": endpoint,
                    "healthy": endpoint_healthy,
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                })
                
                if not endpoint_healthy:
                    overall_healthy = False
                    
            except Exception as e:
                endpoint_results.append({
                    "endpoint": endpoint,
                    "healthy": False,
                    "error": str(e)
                })
                overall_healthy = False
        
        return {
            "healthy": overall_healthy,
            "endpoints": endpoint_results
        }


class FailoverMechanisms:
    """
    Implements comprehensive failover mechanisms for the URL Analyzer system.
    
    This class provides functionality for automatic failover, health monitoring,
    and high availability management.
    """
    
    def __init__(self, config: Optional[FailoverConfig] = None):
        """
        Initialize the failover mechanisms.
        
        Args:
            config: Failover configuration. If None, uses default configuration.
        """
        self.config = config or FailoverConfig()
        self.logger = logging.getLogger(__name__)
        self.health_checker = HealthChecker(self.config)
        
        # Initialize state
        self.current_status = FailoverStatus.ACTIVE
        self.node_id = self._generate_node_id()
        self.failover_history: List[FailoverEvent] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Initialize storage
        self.failover_dir = Path("failover")
        self.failover_dir.mkdir(exist_ok=True)
        self.history_file = self.failover_dir / "failover_history.json"
        self.status_file = self.failover_dir / "node_status.json"
        
        # Load existing history
        self._load_failover_history()
    
    def start_monitoring(self):
        """Start continuous health monitoring and failover detection."""
        if self.monitoring_active:
            self.logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Failover monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("Failover monitoring stopped")
    
    def trigger_manual_failover(self, target_node: Optional[str] = None) -> FailoverEvent:
        """
        Manually trigger a failover operation.
        
        Args:
            target_node: Target node to failover to. If None, selects automatically.
            
        Returns:
            FailoverEvent: Result of the failover operation.
        """
        return self._execute_failover(
            trigger=FailoverTrigger.MANUAL_TRIGGER,
            target_node=target_node,
            reason="Manual failover triggered"
        )
    
    def get_node_status(self) -> NodeStatus:
        """
        Get current node status information.
        
        Returns:
            NodeStatus: Current node status.
        """
        health_results = self.health_checker.check_system_health()
        
        # Calculate health score
        health_score = self._calculate_health_score(health_results)
        
        # Get system metrics
        cpu_percent = health_results["checks"]["resources"].get("cpu_percent", 0)
        memory_percent = health_results["checks"]["resources"].get("memory_percent", 0)
        disk_percent = health_results["checks"]["disk"].get("disk_percent", 0)
        
        # Calculate network latency (simplified)
        network_latency = 0.0
        if health_results["checks"]["network"]["healthy"]:
            network_latency = 10.0  # Placeholder value
        
        return NodeStatus(
            node_id=self.node_id,
            status=self.current_status,
            last_health_check=datetime.now(),
            health_score=health_score,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_latency_ms=network_latency,
            active_connections=len(psutil.net_connections()),
            uptime_seconds=time.time() - psutil.boot_time()
        )
    
    def get_failover_status(self) -> Dict[str, Any]:
        """
        Get comprehensive failover status information.
        
        Returns:
            Dict: Failover status information.
        """
        node_status = self.get_node_status()
        
        total_failovers = len(self.failover_history)
        successful_failovers = len([e for e in self.failover_history if e.success])
        failed_failovers = len([e for e in self.failover_history if not e.success])
        
        last_failover = max(self.failover_history, key=lambda x: x.timestamp) if self.failover_history else None
        
        return {
            "node_id": self.node_id,
            "current_status": self.current_status.value,
            "monitoring_active": self.monitoring_active,
            "health_score": node_status.health_score,
            "total_failovers": total_failovers,
            "successful_failovers": successful_failovers,
            "failed_failovers": failed_failovers,
            "success_rate": (successful_failovers / total_failovers * 100) if total_failovers > 0 else 0,
            "last_failover": {
                "event_id": last_failover.event_id,
                "timestamp": last_failover.timestamp.isoformat(),
                "trigger": last_failover.trigger.value,
                "success": last_failover.success
            } if last_failover else None,
            "configuration": {
                "automatic_failover": self.config.enable_automatic_failover,
                "automatic_recovery": self.config.enable_automatic_recovery,
                "health_check_interval": self.config.health_check_interval_seconds,
                "resource_thresholds": self.config.resource_thresholds
            }
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop for health checks and failover detection."""
        self.logger.info("Starting monitoring loop")
        
        consecutive_failures = 0
        
        while self.monitoring_active:
            try:
                # Perform health check
                health_results = self.health_checker.check_system_health()
                
                # Update node status
                self._update_node_status(health_results)
                
                if not health_results["overall_healthy"]:
                    consecutive_failures += 1
                    self.logger.warning(f"Health check failed ({consecutive_failures} consecutive failures)")
                    
                    # Trigger failover if threshold reached
                    if consecutive_failures >= self.config.max_retry_attempts and self.config.enable_automatic_failover:
                        self._execute_failover(
                            trigger=FailoverTrigger.HEALTH_CHECK_FAILURE,
                            reason=f"Health check failed {consecutive_failures} times"
                        )
                        consecutive_failures = 0
                else:
                    consecutive_failures = 0
                
                # Check for resource exhaustion
                self._check_resource_thresholds(health_results)
                
                time.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(self.config.health_check_interval_seconds)
    
    def _execute_failover(self, trigger: FailoverTrigger, target_node: Optional[str] = None, reason: str = "") -> FailoverEvent:
        """Execute a failover operation."""
        start_time = datetime.now()
        event_id = self._generate_event_id()
        
        self.logger.info(f"Executing failover: {event_id} (trigger: {trigger.value})")
        
        try:
            # Update status to indicate failover in progress
            old_status = self.current_status
            self.current_status = FailoverStatus.FAILED_OVER
            
            # Perform failover steps
            success = self._perform_failover_steps(target_node)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create failover event
            event = FailoverEvent(
                event_id=event_id,
                timestamp=start_time,
                trigger=trigger,
                source_node=self.node_id,
                target_node=target_node,
                success=success,
                duration_seconds=duration,
                error_message=None if success else "Failover steps failed"
            )
            
            # Save event
            self.failover_history.append(event)
            self._save_failover_history()
            
            # Send notifications
            self._send_failover_notifications(event, reason)
            
            if success:
                self.logger.info(f"Failover completed successfully: {event_id}")
            else:
                self.logger.error(f"Failover failed: {event_id}")
                self.current_status = old_status  # Revert status on failure
            
            return event
            
        except Exception as e:
            error_msg = f"Failover execution failed: {str(e)}"
            self.logger.error(error_msg)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            event = FailoverEvent(
                event_id=event_id,
                timestamp=start_time,
                trigger=trigger,
                source_node=self.node_id,
                target_node=target_node,
                success=False,
                duration_seconds=duration,
                error_message=error_msg
            )
            
            self.failover_history.append(event)
            self._save_failover_history()
            
            return event
    
    def _perform_failover_steps(self, target_node: Optional[str] = None) -> bool:
        """Perform the actual failover steps."""
        try:
            # Step 1: Stop current services gracefully
            self.logger.info("Stopping current services")
            # Implementation would stop actual services
            
            # Step 2: Create backup of current state
            self.logger.info("Creating state backup")
            # Implementation would backup current state
            
            # Step 3: Transfer control to target node (if applicable)
            if target_node:
                self.logger.info(f"Transferring control to {target_node}")
                # Implementation would transfer control
            
            # Step 4: Update configuration
            self.logger.info("Updating failover configuration")
            # Implementation would update configuration
            
            # Step 5: Verify failover success
            self.logger.info("Verifying failover success")
            # Implementation would verify the failover
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failover steps failed: {str(e)}")
            return False
    
    def _check_resource_thresholds(self, health_results: Dict[str, Any]):
        """Check if resource thresholds are exceeded and trigger failover if needed."""
        resources = health_results["checks"].get("resources", {})
        
        if not resources.get("healthy", True):
            cpu_exceeded = resources.get("cpu_percent", 0) > self.config.resource_thresholds["cpu_percent"]
            memory_exceeded = resources.get("memory_percent", 0) > self.config.resource_thresholds["memory_percent"]
            
            if cpu_exceeded or memory_exceeded:
                self.logger.warning("Resource thresholds exceeded")
                
                if self.config.enable_automatic_failover:
                    self._execute_failover(
                        trigger=FailoverTrigger.RESOURCE_EXHAUSTION,
                        reason="Resource thresholds exceeded"
                    )
    
    def _calculate_health_score(self, health_results: Dict[str, Any]) -> float:
        """Calculate overall health score from health check results."""
        if not health_results["overall_healthy"]:
            return 0.0
        
        # Simple scoring based on resource usage
        resources = health_results["checks"].get("resources", {})
        cpu_score = max(0, 100 - resources.get("cpu_percent", 0)) / 100
        memory_score = max(0, 100 - resources.get("memory_percent", 0)) / 100
        disk_score = max(0, 100 - resources.get("disk_percent", 0)) / 100
        
        # Network and endpoint scores
        network_score = 1.0 if health_results["checks"].get("network", {}).get("healthy", False) else 0.0
        endpoint_score = 1.0 if health_results["checks"].get("endpoints", {}).get("healthy", False) else 0.0
        
        # Weighted average
        total_score = (cpu_score * 0.2 + memory_score * 0.2 + disk_score * 0.2 + 
                      network_score * 0.2 + endpoint_score * 0.2)
        
        return round(total_score * 100, 2)
    
    def _update_node_status(self, health_results: Dict[str, Any]):
        """Update and save current node status."""
        node_status = self.get_node_status()
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(asdict(node_status), f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save node status: {str(e)}")
    
    def _send_failover_notifications(self, event: FailoverEvent, reason: str):
        """Send notifications about failover events."""
        if not self.config.notification_webhooks:
            return
        
        notification_data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "trigger": event.trigger.value,
            "source_node": event.source_node,
            "target_node": event.target_node,
            "success": event.success,
            "reason": reason,
            "duration_seconds": event.duration_seconds
        }
        
        for webhook_url in self.config.notification_webhooks:
            try:
                import requests
                requests.post(webhook_url, json=notification_data, timeout=10)
                self.logger.info(f"Notification sent to {webhook_url}")
            except Exception as e:
                self.logger.error(f"Failed to send notification to {webhook_url}: {str(e)}")
    
    def _generate_node_id(self) -> str:
        """Generate a unique node identifier."""
        import uuid
        hostname = socket.gethostname()
        return f"{hostname}_{uuid.uuid4().hex[:8]}"
    
    def _generate_event_id(self) -> str:
        """Generate a unique event identifier."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"failover_{timestamp}_{len(self.failover_history)}"
    
    def _load_failover_history(self):
        """Load failover history from file."""
        if not self.history_file.exists():
            return
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                self.failover_history = [
                    FailoverEvent(
                        event_id=item['event_id'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        trigger=FailoverTrigger(item['trigger']),
                        source_node=item['source_node'],
                        target_node=item.get('target_node'),
                        success=item['success'],
                        duration_seconds=item['duration_seconds'],
                        error_message=item.get('error_message'),
                        recovery_timestamp=datetime.fromisoformat(item['recovery_timestamp']) if item.get('recovery_timestamp') else None
                    )
                    for item in data
                ]
        except Exception as e:
            self.logger.error(f"Failed to load failover history: {str(e)}")
    
    def _save_failover_history(self):
        """Save failover history to file."""
        try:
            data = []
            for event in self.failover_history:
                item = asdict(event)
                item['timestamp'] = event.timestamp.isoformat()
                item['trigger'] = event.trigger.value
                if event.recovery_timestamp:
                    item['recovery_timestamp'] = event.recovery_timestamp.isoformat()
                data.append(item)
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save failover history: {str(e)}")