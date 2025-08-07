"""
Audit module for URL Analyzer.

This module provides functionality for tracking and auditing user activities
in the system. It enables accountability, security monitoring, and compliance
with regulatory requirements.

Features:
- Activity logging for all user actions
- Audit trail for security-relevant events
- Filtering and searching audit logs
- Export capabilities for compliance reporting
- Retention policies for audit data
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4


class AuditLog:
    """
    Represents an audit log entry for a user action.
    
    Audit logs track user activities in the system for security,
    compliance, and troubleshooting purposes.
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        timestamp: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ):
        """
        Initialize an AuditLog object.
        
        Args:
            id: Unique identifier for the audit log entry
            user_id: ID of the user who performed the action
            action: Type of action performed (create, update, delete, etc.)
            resource_type: Type of resource affected (url, report, user, etc.)
            resource_id: ID of the resource affected
            timestamp: When the action occurred
            ip_address: Optional IP address of the user
            user_agent: Optional user agent of the client
            details: Additional details about the action
            status: Outcome of the action (success, failure, etc.)
        """
        self.id = id
        self.user_id = user_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.timestamp = timestamp or datetime.now()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.details = details or {}
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the audit log entry to a dictionary.
        
        Returns:
            Dictionary representation of the audit log entry
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        """
        Create an AuditLog object from a dictionary.
        
        Args:
            data: Dictionary containing audit log data
            
        Returns:
            AuditLog object
        """
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            action=data["action"],
            resource_type=data["resource_type"],
            resource_id=data["resource_id"],
            timestamp=timestamp,
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            details=data.get("details", {}),
            status=data.get("status", "success")
        )


class AuditManager:
    """
    Manages audit logs in the system.
    
    This class provides methods for creating, retrieving, and managing audit logs.
    """
    
    def __init__(self, max_logs: int = 10000):
        """
        Initialize an AuditManager.
        
        Args:
            max_logs: Maximum number of audit logs to keep in memory
        """
        # In-memory storage for audit logs
        # In a production system, this would be replaced with a database
        self._audit_logs: Dict[str, AuditLog] = {}
        self._max_logs = max_logs
    
    def log_activity(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> AuditLog:
        """
        Log a user activity.
        
        Args:
            user_id: ID of the user who performed the action
            action: Type of action performed
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            ip_address: Optional IP address of the user
            user_agent: Optional user agent of the client
            details: Additional details about the action
            status: Outcome of the action
            
        Returns:
            The created AuditLog object
        """
        log_id = str(uuid4())
        audit_log = AuditLog(
            id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            status=status
        )
        
        # Add the log to the in-memory storage
        self._audit_logs[log_id] = audit_log
        
        # If we've exceeded the maximum number of logs, remove the oldest ones
        if len(self._audit_logs) > self._max_logs:
            # Sort logs by timestamp (oldest first)
            sorted_logs = sorted(self._audit_logs.items(), key=lambda x: x[1].timestamp)
            # Remove the oldest logs
            for i in range(len(sorted_logs) - self._max_logs):
                del self._audit_logs[sorted_logs[i][0]]
        
        return audit_log
    
    def get_audit_log(self, log_id: str) -> Optional[AuditLog]:
        """
        Get an audit log by ID.
        
        Args:
            log_id: ID of the audit log to retrieve
            
        Returns:
            The AuditLog object if found, None otherwise
        """
        return self._audit_logs.get(log_id)
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Get audit logs based on various filters.
        
        Args:
            user_id: Optional filter for user ID
            action: Optional filter for action type
            resource_type: Optional filter for resource type
            resource_id: Optional filter for resource ID
            start_time: Optional filter for minimum timestamp
            end_time: Optional filter for maximum timestamp
            status: Optional filter for status
            limit: Maximum number of logs to return
            offset: Offset for pagination
            
        Returns:
            List of AuditLog objects matching the filters
        """
        # Filter logs based on the provided criteria
        filtered_logs = [
            log for log in self._audit_logs.values()
            if (user_id is None or log.user_id == user_id)
            and (action is None or log.action == action)
            and (resource_type is None or log.resource_type == resource_type)
            and (resource_id is None or log.resource_id == resource_id)
            and (start_time is None or log.timestamp >= start_time)
            and (end_time is None or log.timestamp <= end_time)
            and (status is None or log.status == status)
        ]
        
        # Sort logs by timestamp (newest first)
        filtered_logs.sort(key=lambda log: log.timestamp, reverse=True)
        
        # Apply pagination
        return filtered_logs[offset:offset + limit]
    
    def export_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Export audit logs as a list of dictionaries.
        
        Args:
            user_id: Optional filter for user ID
            action: Optional filter for action type
            resource_type: Optional filter for resource type
            resource_id: Optional filter for resource ID
            start_time: Optional filter for minimum timestamp
            end_time: Optional filter for maximum timestamp
            status: Optional filter for status
            
        Returns:
            List of dictionaries representing audit logs
        """
        # Get filtered logs without pagination
        filtered_logs = self.get_audit_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
            limit=100000,  # Large limit to get all logs
            offset=0
        )
        
        # Convert logs to dictionaries
        return [log.to_dict() for log in filtered_logs]


# Create a global instance of AuditManager
_audit_manager = AuditManager()


def log_activity(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = "success"
) -> AuditLog:
    """
    Log a user activity.
    
    Args:
        user_id: ID of the user who performed the action
        action: Type of action performed
        resource_type: Type of resource affected
        resource_id: ID of the resource affected
        ip_address: Optional IP address of the user
        user_agent: Optional user agent of the client
        details: Additional details about the action
        status: Outcome of the action
        
    Returns:
        The created AuditLog object
    """
    return _audit_manager.log_activity(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        status=status
    )


def get_audit_log(log_id: str) -> Optional[AuditLog]:
    """
    Get an audit log by ID.
    
    Args:
        log_id: ID of the audit log to retrieve
        
    Returns:
        The AuditLog object if found, None otherwise
    """
    return _audit_manager.get_audit_log(log_id)


def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """
    Get audit logs based on various filters.
    
    Args:
        user_id: Optional filter for user ID
        action: Optional filter for action type
        resource_type: Optional filter for resource type
        resource_id: Optional filter for resource ID
        start_time: Optional filter for minimum timestamp
        end_time: Optional filter for maximum timestamp
        status: Optional filter for status
        limit: Maximum number of logs to return
        offset: Offset for pagination
        
    Returns:
        List of AuditLog objects matching the filters
    """
    return _audit_manager.get_audit_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_time=start_time,
        end_time=end_time,
        status=status,
        limit=limit,
        offset=offset
    )


def export_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Export audit logs as a list of dictionaries.
    
    Args:
        user_id: Optional filter for user ID
        action: Optional filter for action type
        resource_type: Optional filter for resource type
        resource_id: Optional filter for resource ID
        start_time: Optional filter for minimum timestamp
        end_time: Optional filter for maximum timestamp
        status: Optional filter for status
        
    Returns:
        List of dictionaries representing audit logs
    """
    return _audit_manager.export_audit_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_time=start_time,
        end_time=end_time,
        status=status
    )