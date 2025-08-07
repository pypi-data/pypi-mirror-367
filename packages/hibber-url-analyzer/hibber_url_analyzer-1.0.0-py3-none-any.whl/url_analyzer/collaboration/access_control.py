"""
Access control module for URL Analyzer collaboration features.

This module provides functionality for role-based access control, including:
- Role and permission definitions
- Role assignment and management
- Permission checking
- Access control enforcement

These features enable secure multi-user collaboration with appropriate
access restrictions based on user roles.
"""

import enum
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union

from url_analyzer.collaboration.user_management import User


class Permission(enum.Enum):
    """
    Enumeration of permissions available in the system.
    
    Each permission represents a specific action that can be performed.
    Permissions are grouped by functionality area.
    """
    # User management permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    # Workspace permissions
    CREATE_WORKSPACE = "create_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    EDIT_WORKSPACE = "edit_workspace"
    VIEW_WORKSPACE = "view_workspace"
    
    # URL analysis permissions
    RUN_ANALYSIS = "run_analysis"
    VIEW_ANALYSIS = "view_analysis"
    EXPORT_ANALYSIS = "export_analysis"
    
    # Report permissions
    CREATE_REPORT = "create_report"
    EDIT_REPORT = "edit_report"
    VIEW_REPORT = "view_report"
    SHARE_REPORT = "share_report"
    
    # Comment and annotation permissions
    ADD_COMMENT = "add_comment"
    EDIT_OWN_COMMENT = "edit_own_comment"
    EDIT_ANY_COMMENT = "edit_any_comment"
    DELETE_OWN_COMMENT = "delete_own_comment"
    DELETE_ANY_COMMENT = "delete_any_comment"
    
    # Configuration permissions
    EDIT_CONFIGURATION = "edit_configuration"
    VIEW_CONFIGURATION = "view_configuration"
    
    # System permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM = "manage_system"


@dataclass
class Role:
    """
    Represents a role in the system with associated permissions.
    
    Attributes:
        name: Name of the role
        description: Description of the role's purpose
        permissions: Set of permissions granted to this role
        role_id: Unique identifier for the role
    """
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    role_id: str = field(default_factory=lambda: os.urandom(16).hex())
    
    def add_permission(self, permission: Permission) -> None:
        """
        Add a permission to this role.
        
        Args:
            permission: Permission to add
        """
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """
        Remove a permission from this role.
        
        Args:
            permission: Permission to remove
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission: Permission) -> bool:
        """
        Check if this role has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if the role has the permission, False otherwise
        """
        return permission in self.permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the role to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the role
        """
        return {
            "name": self.name,
            "description": self.description,
            "permissions": [p.value for p in self.permissions],
            "role_id": self.role_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """
        Create a Role object from a dictionary.
        
        Args:
            data: Dictionary containing role data
            
        Returns:
            Role object created from the dictionary
        """
        # Convert permission strings back to Permission enum values
        permissions = {Permission(p) for p in data.get("permissions", [])}
        
        return cls(
            name=data["name"],
            description=data["description"],
            permissions=permissions,
            role_id=data["role_id"]
        )


class RoleManager:
    """
    Manages roles and user role assignments.
    
    This class provides functionality for creating, updating, and deleting roles,
    as well as assigning roles to users and checking permissions.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the RoleManager.
        
        Args:
            storage_path: Path to the role data storage file
        """
        if storage_path is None:
            # Default to a roles.json file in the application data directory
            app_data_dir = Path(os.path.expanduser("~")) / ".url_analyzer"
            app_data_dir.mkdir(exist_ok=True)
            self.storage_path = app_data_dir / "roles.json"
        else:
            self.storage_path = Path(storage_path)
        
        # Create the storage file if it doesn't exist
        if not self.storage_path.exists():
            self._save_data({}, {})
        
        # Create default roles if they don't exist
        self._ensure_default_roles()
    
    def _load_data(self) -> tuple[Dict[str, Role], Dict[str, List[str]]]:
        """
        Load roles and user role assignments from the storage file.
        
        Returns:
            Tuple containing:
            - Dictionary mapping role IDs to Role objects
            - Dictionary mapping user IDs to lists of role IDs
        """
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
                # Load roles
                roles = {
                    role_id: Role.from_dict(role_data)
                    for role_id, role_data in data.get("roles", {}).items()
                }
                
                # Load user role assignments
                user_roles = data.get("user_roles", {})
                
                return roles, user_roles
        except (FileNotFoundError, json.JSONDecodeError):
            return {}, {}
    
    def _save_data(self, roles: Dict[str, Role], user_roles: Dict[str, List[str]]) -> None:
        """
        Save roles and user role assignments to the storage file.
        
        Args:
            roles: Dictionary mapping role IDs to Role objects
            user_roles: Dictionary mapping user IDs to lists of role IDs
        """
        data = {
            "roles": {
                role_id: role.to_dict()
                for role_id, role in roles.items()
            },
            "user_roles": user_roles
        }
        
        # Create directory if it doesn't exist
        self.storage_path.parent.mkdir(exist_ok=True)
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _ensure_default_roles(self) -> None:
        """
        Create default roles if they don't exist.
        
        This method creates the following default roles:
        - Administrator: Has all permissions
        - Analyst: Can run analyses and create reports
        - Viewer: Can view analyses and reports
        """
        roles, user_roles = self._load_data()
        
        # Check if default roles already exist
        if any(role.name == "Administrator" for role in roles.values()):
            return
        
        # Create Administrator role with all permissions
        admin_role = Role(
            name="Administrator",
            description="Full system access with all permissions"
        )
        for permission in Permission:
            admin_role.add_permission(permission)
        
        # Create Analyst role
        analyst_role = Role(
            name="Analyst",
            description="Can run analyses and create reports"
        )
        analyst_permissions = [
            Permission.RUN_ANALYSIS,
            Permission.VIEW_ANALYSIS,
            Permission.EXPORT_ANALYSIS,
            Permission.CREATE_REPORT,
            Permission.EDIT_REPORT,
            Permission.VIEW_REPORT,
            Permission.SHARE_REPORT,
            Permission.ADD_COMMENT,
            Permission.EDIT_OWN_COMMENT,
            Permission.DELETE_OWN_COMMENT,
            Permission.VIEW_CONFIGURATION
        ]
        for permission in analyst_permissions:
            analyst_role.add_permission(permission)
        
        # Create Viewer role
        viewer_role = Role(
            name="Viewer",
            description="Can view analyses and reports"
        )
        viewer_permissions = [
            Permission.VIEW_ANALYSIS,
            Permission.VIEW_REPORT,
            Permission.ADD_COMMENT,
            Permission.EDIT_OWN_COMMENT,
            Permission.DELETE_OWN_COMMENT
        ]
        for permission in viewer_permissions:
            viewer_role.add_permission(permission)
        
        # Add roles to the dictionary
        roles[admin_role.role_id] = admin_role
        roles[analyst_role.role_id] = analyst_role
        roles[viewer_role.role_id] = viewer_role
        
        # Save the updated roles
        self._save_data(roles, user_roles)
    
    def create_role(self, name: str, description: str, permissions: List[Permission] = None) -> Role:
        """
        Create a new role.
        
        Args:
            name: Name of the role
            description: Description of the role's purpose
            permissions: List of permissions to assign to the role
            
        Returns:
            Newly created Role object
            
        Raises:
            ValueError: If a role with the given name already exists
        """
        roles, user_roles = self._load_data()
        
        # Check if a role with this name already exists
        if any(role.name == name for role in roles.values()):
            raise ValueError(f"Role with name '{name}' already exists")
        
        # Create the new role
        role = Role(name=name, description=description)
        
        # Add permissions if provided
        if permissions:
            for permission in permissions:
                role.add_permission(permission)
        
        # Add the role to the dictionary and save
        roles[role.role_id] = role
        self._save_data(roles, user_roles)
        
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """
        Get a role by ID.
        
        Args:
            role_id: ID of the role to retrieve
            
        Returns:
            Role object if found, None otherwise
        """
        roles, _ = self._load_data()
        return roles.get(role_id)
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            name: Name of the role to retrieve
            
        Returns:
            Role object if found, None otherwise
        """
        roles, _ = self._load_data()
        for role in roles.values():
            if role.name == name:
                return role
        return None
    
    def update_role(self, role_id: str, name: str = None, description: str = None,
                   permissions: List[Permission] = None) -> Optional[Role]:
        """
        Update a role.
        
        Args:
            role_id: ID of the role to update
            name: New name for the role (optional)
            description: New description for the role (optional)
            permissions: New set of permissions for the role (optional)
            
        Returns:
            Updated Role object if found, None otherwise
            
        Raises:
            ValueError: If trying to update the name to one that already exists
        """
        roles, user_roles = self._load_data()
        
        role = roles.get(role_id)
        if role is None:
            return None
        
        # Update name if provided
        if name is not None and name != role.name:
            # Check if the new name already exists
            if any(r.name == name and r.role_id != role_id for r in roles.values()):
                raise ValueError(f"Role with name '{name}' already exists")
            role.name = name
        
        # Update description if provided
        if description is not None:
            role.description = description
        
        # Update permissions if provided
        if permissions is not None:
            role.permissions = set(permissions)
        
        # Save the updated roles
        self._save_data(roles, user_roles)
        
        return role
    
    def delete_role(self, role_id: str) -> bool:
        """
        Delete a role.
        
        Args:
            role_id: ID of the role to delete
            
        Returns:
            True if the role was deleted, False if not found
            
        Note:
            This will also remove the role from all users who have it assigned.
        """
        roles, user_roles = self._load_data()
        
        if role_id not in roles:
            return False
        
        # Remove the role
        del roles[role_id]
        
        # Remove the role from all users who have it
        for user_id, role_ids in user_roles.items():
            if role_id in role_ids:
                user_roles[user_id] = [r for r in role_ids if r != role_id]
        
        # Save the updated data
        self._save_data(roles, user_roles)
        
        return True
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: ID of the user
            role_id: ID of the role to assign
            
        Returns:
            True if the role was assigned, False if the role doesn't exist
        """
        roles, user_roles = self._load_data()
        
        # Check if the role exists
        if role_id not in roles:
            return False
        
        # Get the user's current roles or initialize an empty list
        user_role_ids = user_roles.get(user_id, [])
        
        # Add the role if not already assigned
        if role_id not in user_role_ids:
            user_role_ids.append(role_id)
            user_roles[user_id] = user_role_ids
            self._save_data(roles, user_roles)
        
        return True
    
    def revoke_role_from_user(self, user_id: str, role_id: str) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            user_id: ID of the user
            role_id: ID of the role to revoke
            
        Returns:
            True if the role was revoked, False if the user doesn't have the role
        """
        roles, user_roles = self._load_data()
        
        # Check if the user has any roles
        if user_id not in user_roles:
            return False
        
        # Check if the user has the specified role
        user_role_ids = user_roles[user_id]
        if role_id not in user_role_ids:
            return False
        
        # Remove the role
        user_roles[user_id] = [r for r in user_role_ids if r != role_id]
        self._save_data(roles, user_roles)
        
        return True
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Role objects assigned to the user
        """
        roles, user_roles = self._load_data()
        
        # Get the user's role IDs
        user_role_ids = user_roles.get(user_id, [])
        
        # Return the corresponding Role objects
        return [roles[role_id] for role_id in user_role_ids if role_id in roles]
    
    def check_user_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: ID of the user
            permission: Permission to check
            
        Returns:
            True if the user has the permission through any of their roles, False otherwise
        """
        # Get all roles assigned to the user
        user_roles = self.get_user_roles(user_id)
        
        # Check if any of the roles has the permission
        for role in user_roles:
            if role.has_permission(permission):
                return True
        
        return False
    
    def get_all_roles(self) -> List[Role]:
        """
        Get all roles in the system.
        
        Returns:
            List of all Role objects
        """
        roles, _ = self._load_data()
        return list(roles.values())


# Module-level functions that use the RoleManager

def create_role(name: str, description: str, permissions: List[Permission] = None,
               storage_path: str = None) -> Role:
    """
    Create a new role.
    
    Args:
        name: Name of the role
        description: Description of the role's purpose
        permissions: List of permissions to assign to the role
        storage_path: Optional path to the role data storage file
        
    Returns:
        Newly created Role object
        
    Raises:
        ValueError: If a role with the given name already exists
    """
    manager = RoleManager(storage_path)
    return manager.create_role(name, description, permissions)


def get_role(role_id: str, storage_path: str = None) -> Optional[Role]:
    """
    Get a role by ID.
    
    Args:
        role_id: ID of the role to retrieve
        storage_path: Optional path to the role data storage file
        
    Returns:
        Role object if found, None otherwise
    """
    manager = RoleManager(storage_path)
    return manager.get_role(role_id)


def assign_role(user_id: str, role_id: str, storage_path: str = None) -> bool:
    """
    Assign a role to a user.
    
    Args:
        user_id: ID of the user
        role_id: ID of the role to assign
        storage_path: Optional path to the role data storage file
        
    Returns:
        True if the role was assigned, False if the role doesn't exist
    """
    manager = RoleManager(storage_path)
    return manager.assign_role_to_user(user_id, role_id)


def revoke_role(user_id: str, role_id: str, storage_path: str = None) -> bool:
    """
    Revoke a role from a user.
    
    Args:
        user_id: ID of the user
        role_id: ID of the role to revoke
        storage_path: Optional path to the role data storage file
        
    Returns:
        True if the role was revoked, False if the user doesn't have the role
    """
    manager = RoleManager(storage_path)
    return manager.revoke_role_from_user(user_id, role_id)


def check_permission(user_id: str, permission: Permission, storage_path: str = None) -> bool:
    """
    Check if a user has a specific permission.
    
    Args:
        user_id: ID of the user
        permission: Permission to check
        storage_path: Optional path to the role data storage file
        
    Returns:
        True if the user has the permission through any of their roles, False otherwise
    """
    manager = RoleManager(storage_path)
    return manager.check_user_permission(user_id, permission)