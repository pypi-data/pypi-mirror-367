"""
Access Control Module

This module provides functionality for controlling access to URL data,
supporting data privacy and security requirements.
"""

import logging
import os
import json
import hashlib
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AccessControlManager:
    """
    Access control manager for URL data.
    
    This class provides methods for controlling access to URL data based on
    user roles, permissions, and data sensitivity.
    """
    
    def __init__(self, access_control_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the access control manager.
        
        Args:
            access_control_config: Configuration for access control
        """
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, Dict[str, Any]] = {}
        self.user_roles: Dict[str, List[str]] = {}
        
        # Load configuration if provided
        if access_control_config:
            self.configure(access_control_config)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the access control manager.
        
        Args:
            config: Configuration dictionary
        """
        # Load roles
        if "roles" in config:
            self.roles = config["roles"]
        
        # Load permissions
        if "permissions" in config:
            self.permissions = config["permissions"]
        
        # Load user roles
        if "user_roles" in config:
            self.user_roles = config["user_roles"]
    
    def save_configuration(self, file_path: str) -> bool:
        """
        Save the access control configuration to a file.
        
        Args:
            file_path: Path to save the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create configuration dictionary
            config = {
                "roles": self.roles,
                "permissions": self.permissions,
                "user_roles": self.user_roles
            }
            
            # Save configuration
            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved access control configuration to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving access control configuration: {str(e)}")
            return False
    
    def load_configuration(self, file_path: str) -> bool:
        """
        Load the access control configuration from a file.
        
        Args:
            file_path: Path to load the configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Access control configuration file not found: {file_path}")
                return False
            
            # Load configuration
            with open(file_path, "r") as f:
                config = json.load(f)
            
            # Configure the manager
            self.configure(config)
            
            logger.info(f"Loaded access control configuration from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading access control configuration: {str(e)}")
            return False
    
    def add_role(
        self,
        role_name: str,
        description: str = "",
        permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new role.
        
        Args:
            role_name: Name of the role
            description: Description of the role
            permissions: List of permission names for the role
            
        Returns:
            Dictionary containing the role information
        """
        # Create role
        role = {
            "name": role_name,
            "description": description,
            "permissions": permissions or []
        }
        
        # Add role to roles dictionary
        self.roles[role_name] = role
        
        return role
    
    def add_permission(
        self,
        permission_name: str,
        description: str = "",
        resource_type: str = "*",
        actions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new permission.
        
        Args:
            permission_name: Name of the permission
            description: Description of the permission
            resource_type: Type of resource the permission applies to
            actions: List of actions allowed by the permission
            
        Returns:
            Dictionary containing the permission information
        """
        # Create permission
        permission = {
            "name": permission_name,
            "description": description,
            "resource_type": resource_type,
            "actions": actions or ["*"]
        }
        
        # Add permission to permissions dictionary
        self.permissions[permission_name] = permission
        
        return permission
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: Identifier for the user
            role_name: Name of the role to assign
            
        Returns:
            True if successful, False otherwise
        """
        # Check if role exists
        if role_name not in self.roles:
            logger.error(f"Role not found: {role_name}")
            return False
        
        # Initialize user roles if not already present
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        # Add role to user if not already assigned
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
        
        return True
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: Identifier for the user
            role_name: Name of the role to remove
            
        Returns:
            True if successful, False otherwise
        """
        # Check if user has roles
        if user_id not in self.user_roles:
            logger.error(f"User has no roles: {user_id}")
            return False
        
        # Check if user has the role
        if role_name not in self.user_roles[user_id]:
            logger.error(f"User does not have role: {role_name}")
            return False
        
        # Remove role from user
        self.user_roles[user_id].remove(role_name)
        
        return True
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get the roles assigned to a user.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            List of role names
        """
        return self.user_roles.get(user_id, [])
    
    def get_user_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get the permissions for a user based on their roles.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            List of permission dictionaries
        """
        # Get user roles
        user_roles = self.get_user_roles(user_id)
        
        # Collect permissions from all roles
        permission_names = set()
        for role_name in user_roles:
            role = self.roles.get(role_name)
            if role:
                permission_names.update(role.get("permissions", []))
        
        # Get permission details
        permissions = []
        for permission_name in permission_names:
            permission = self.permissions.get(permission_name)
            if permission:
                permissions.append(permission)
        
        return permissions
    
    def check_permission(
        self,
        user_id: str,
        permission_name: str,
        resource_type: Optional[str] = None,
        action: Optional[str] = None
    ) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: Identifier for the user
            permission_name: Name of the permission to check
            resource_type: Type of resource to check permission for
            action: Action to check permission for
            
        Returns:
            True if the user has the permission, False otherwise
        """
        # Get user permissions
        user_permissions = self.get_user_permissions(user_id)
        
        # Check if the user has the specific permission
        for permission in user_permissions:
            # Check permission name
            if permission["name"] != permission_name and permission["name"] != "*":
                continue
            
            # Check resource type if specified
            if resource_type and permission["resource_type"] != "*" and permission["resource_type"] != resource_type:
                continue
            
            # Check action if specified
            if action and "*" not in permission["actions"] and action not in permission["actions"]:
                continue
            
            # Permission matches all criteria
            return True
        
        # Permission not found
        return False
    
    def filter_data_by_permission(
        self,
        df: pd.DataFrame,
        user_id: str,
        permission_name: str,
        resource_column: Optional[str] = None,
        action: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter a DataFrame based on user permissions.
        
        Args:
            df: DataFrame to filter
            user_id: Identifier for the user
            permission_name: Name of the permission to check
            resource_column: Name of the column containing resource identifiers
            action: Action to check permission for
            
        Returns:
            Filtered DataFrame
        """
        # If no resource column specified, check general permission
        if not resource_column:
            # If user has the permission, return the full DataFrame
            if self.check_permission(user_id, permission_name, action=action):
                return df
            # Otherwise, return an empty DataFrame
            else:
                return df.iloc[0:0]
        
        # Get unique resources
        resources = df[resource_column].unique()
        
        # Check permission for each resource
        allowed_resources = []
        for resource in resources:
            # Skip null/NaN resources
            if pd.isna(resource):
                continue
            
            # Check permission for this resource
            if self.check_permission(user_id, permission_name, str(resource), action):
                allowed_resources.append(resource)
        
        # Filter DataFrame to include only allowed resources
        return df[df[resource_column].isin(allowed_resources)]
    
    def apply_data_access_controls(
        self,
        df: pd.DataFrame,
        user_id: str,
        sensitive_columns: Optional[List[str]] = None,
        resource_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Apply data access controls to a DataFrame.
        
        Args:
            df: DataFrame to apply access controls to
            user_id: Identifier for the user
            sensitive_columns: List of sensitive columns to check permissions for
            resource_column: Name of the column containing resource identifiers
            
        Returns:
            DataFrame with access controls applied
        """
        # If user has full access permission, return the full DataFrame
        if self.check_permission(user_id, "full_data_access"):
            return df
        
        # Filter by resource permission if resource column is specified
        if resource_column:
            df = self.filter_data_by_permission(df, user_id, "resource_access", resource_column, "view")
        
        # If no sensitive columns specified, return the filtered DataFrame
        if not sensitive_columns:
            return df
        
        # Check permissions for sensitive columns
        allowed_columns = []
        for column in df.columns:
            # If column is not sensitive, include it
            if column not in sensitive_columns:
                allowed_columns.append(column)
                continue
            
            # Check permission for sensitive column
            if self.check_permission(user_id, "sensitive_data_access", column, "view"):
                allowed_columns.append(column)
        
        # Return DataFrame with only allowed columns
        return df[allowed_columns]
    
    def generate_access_control_report(
        self,
        output_path: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a report of access control configuration.
        
        Args:
            output_path: Path to save the report
            include_details: Whether to include detailed configuration
            
        Returns:
            Dictionary containing report generation results
        """
        # Create report data
        report_data = {
            "report_id": f"ACCESS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_date": datetime.now().isoformat(),
            "role_count": len(self.roles),
            "permission_count": len(self.permissions),
            "user_count": len(self.user_roles)
        }
        
        # Add summary information
        summary = {
            "roles": list(self.roles.keys()),
            "permissions": list(self.permissions.keys()),
            "users": list(self.user_roles.keys())
        }
        report_data["summary"] = summary
        
        # Add detailed configuration if requested
        if include_details:
            report_data["roles"] = self.roles
            report_data["permissions"] = self.permissions
            report_data["user_roles"] = self.user_roles
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write report to file
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        return {
            "success": True,
            "report_id": report_data["report_id"],
            "output_path": output_path
        }