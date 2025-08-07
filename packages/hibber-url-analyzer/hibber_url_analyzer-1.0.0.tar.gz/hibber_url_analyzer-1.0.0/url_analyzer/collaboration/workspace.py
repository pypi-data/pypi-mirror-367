"""
Workspace module for URL Analyzer collaboration features.

This module provides functionality for shared workspaces, including:
- Workspace creation, retrieval, updating, and deletion
- User workspace membership management
- Workspace resource management
- Workspace permissions and access control

These features enable team collaboration on URL analysis projects.
"""

import datetime
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union

from url_analyzer.collaboration.access_control import Permission, check_permission


@dataclass
class WorkspaceResource:
    """
    Represents a resource (file, report, analysis) in a workspace.
    
    Attributes:
        resource_id: Unique identifier for the resource
        name: Name of the resource
        resource_type: Type of resource (e.g., 'file', 'report', 'analysis')
        path: Path to the resource file or data
        created_by: ID of the user who created the resource
        created_at: Timestamp when the resource was created
        updated_at: Timestamp when the resource was last updated
        metadata: Additional metadata about the resource
    """
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    resource_type: str = ""
    path: str = ""
    created_by: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the resource to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the resource
        """
        data = asdict(self)
        # Convert datetime objects to strings for JSON serialization
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['updated_at']:
            data['updated_at'] = data['updated_at'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceResource':
        """
        Create a WorkspaceResource object from a dictionary.
        
        Args:
            data: Dictionary containing resource data
            
        Returns:
            WorkspaceResource object created from the dictionary
        """
        # Convert string timestamps back to datetime objects
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class Workspace:
    """
    Represents a shared workspace for collaboration.
    
    Attributes:
        workspace_id: Unique identifier for the workspace
        name: Name of the workspace
        description: Description of the workspace
        created_by: ID of the user who created the workspace
        created_at: Timestamp when the workspace was created
        updated_at: Timestamp when the workspace was last updated
        members: Set of user IDs who are members of the workspace
        resources: Dictionary mapping resource IDs to WorkspaceResource objects
        is_public: Whether the workspace is public (visible to all users)
        metadata: Additional metadata about the workspace
    """
    workspace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_by: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    members: Set[str] = field(default_factory=set)
    resources: Dict[str, WorkspaceResource] = field(default_factory=dict)
    is_public: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_member(self, user_id: str) -> None:
        """
        Add a user to the workspace.
        
        Args:
            user_id: ID of the user to add
        """
        self.members.add(user_id)
        self.updated_at = datetime.datetime.now()
    
    def remove_member(self, user_id: str) -> bool:
        """
        Remove a user from the workspace.
        
        Args:
            user_id: ID of the user to remove
            
        Returns:
            True if the user was removed, False if not found
        """
        if user_id in self.members:
            self.members.remove(user_id)
            self.updated_at = datetime.datetime.now()
            return True
        return False
    
    def add_resource(self, resource: WorkspaceResource) -> None:
        """
        Add a resource to the workspace.
        
        Args:
            resource: WorkspaceResource to add
        """
        self.resources[resource.resource_id] = resource
        self.updated_at = datetime.datetime.now()
    
    def remove_resource(self, resource_id: str) -> bool:
        """
        Remove a resource from the workspace.
        
        Args:
            resource_id: ID of the resource to remove
            
        Returns:
            True if the resource was removed, False if not found
        """
        if resource_id in self.resources:
            del self.resources[resource_id]
            self.updated_at = datetime.datetime.now()
            return True
        return False
    
    def get_resource(self, resource_id: str) -> Optional[WorkspaceResource]:
        """
        Get a resource from the workspace.
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            WorkspaceResource if found, None otherwise
        """
        return self.resources.get(resource_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workspace to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the workspace
        """
        data = {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "members": list(self.members),
            "resources": {
                resource_id: resource.to_dict()
                for resource_id, resource in self.resources.items()
            },
            "is_public": self.is_public,
            "metadata": self.metadata
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workspace':
        """
        Create a Workspace object from a dictionary.
        
        Args:
            data: Dictionary containing workspace data
            
        Returns:
            Workspace object created from the dictionary
        """
        # Create a copy of the data to avoid modifying the original
        workspace_data = data.copy()
        
        # Convert string timestamps back to datetime objects
        if 'created_at' in workspace_data and workspace_data['created_at']:
            workspace_data['created_at'] = datetime.datetime.fromisoformat(workspace_data['created_at'])
        if 'updated_at' in workspace_data and workspace_data['updated_at']:
            workspace_data['updated_at'] = datetime.datetime.fromisoformat(workspace_data['updated_at'])
        
        # Convert members list to set
        if 'members' in workspace_data:
            workspace_data['members'] = set(workspace_data['members'])
        
        # Convert resources dictionary
        if 'resources' in workspace_data:
            resources_dict = workspace_data['resources']
            workspace_data['resources'] = {
                resource_id: WorkspaceResource.from_dict(resource_data)
                for resource_id, resource_data in resources_dict.items()
            }
        
        return cls(**workspace_data)


class WorkspaceManager:
    """
    Manages workspaces and their resources.
    
    This class provides functionality for creating, updating, and deleting workspaces,
    as well as managing workspace membership and resources.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the WorkspaceManager.
        
        Args:
            storage_path: Path to the workspace data storage file
        """
        if storage_path is None:
            # Default to a workspaces.json file in the application data directory
            app_data_dir = Path(os.path.expanduser("~")) / ".url_analyzer"
            app_data_dir.mkdir(exist_ok=True)
            self.storage_path = app_data_dir / "workspaces.json"
        else:
            self.storage_path = Path(storage_path)
        
        # Create the storage file if it doesn't exist
        if not self.storage_path.exists():
            self._save_workspaces({})
    
    def _load_workspaces(self) -> Dict[str, Workspace]:
        """
        Load workspaces from the storage file.
        
        Returns:
            Dictionary mapping workspace IDs to Workspace objects
        """
        try:
            with open(self.storage_path, 'r') as f:
                workspace_data = json.load(f)
                return {
                    workspace_id: Workspace.from_dict(data)
                    for workspace_id, data in workspace_data.items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_workspaces(self, workspaces: Dict[str, Workspace]) -> None:
        """
        Save workspaces to the storage file.
        
        Args:
            workspaces: Dictionary mapping workspace IDs to Workspace objects
        """
        workspace_data = {
            workspace_id: workspace.to_dict()
            for workspace_id, workspace in workspaces.items()
        }
        
        # Create directory if it doesn't exist
        self.storage_path.parent.mkdir(exist_ok=True)
        
        with open(self.storage_path, 'w') as f:
            json.dump(workspace_data, f, indent=2)
    
    def create_workspace(self, name: str, description: str, created_by: str, 
                         is_public: bool = False) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            name: Name of the workspace
            description: Description of the workspace
            created_by: ID of the user creating the workspace
            is_public: Whether the workspace is public (visible to all users)
            
        Returns:
            Newly created Workspace object
            
        Raises:
            ValueError: If the user doesn't have permission to create workspaces
        """
        # Check if the user has permission to create workspaces
        if not check_permission(created_by, Permission.CREATE_WORKSPACE):
            raise ValueError("User does not have permission to create workspaces")
        
        # Create the new workspace
        workspace = Workspace(
            name=name,
            description=description,
            created_by=created_by,
            is_public=is_public
        )
        
        # Add the creator as a member
        workspace.add_member(created_by)
        
        # Save the workspace
        workspaces = self._load_workspaces()
        workspaces[workspace.workspace_id] = workspace
        self._save_workspaces(workspaces)
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: ID of the workspace to retrieve
            
        Returns:
            Workspace object if found, None otherwise
        """
        workspaces = self._load_workspaces()
        return workspaces.get(workspace_id)
    
    def update_workspace(self, workspace_id: str, user_id: str, **kwargs) -> Optional[Workspace]:
        """
        Update a workspace.
        
        Args:
            workspace_id: ID of the workspace to update
            user_id: ID of the user making the update
            **kwargs: Fields to update (can include name, description, is_public, metadata)
            
        Returns:
            Updated Workspace object if found and user has permission, None otherwise
            
        Raises:
            ValueError: If the user doesn't have permission to edit the workspace
        """
        workspaces = self._load_workspaces()
        workspace = workspaces.get(workspace_id)
        
        if workspace is None:
            return None
        
        # Check if the user has permission to edit the workspace
        if not (user_id == workspace.created_by or 
                user_id in workspace.members and check_permission(user_id, Permission.EDIT_WORKSPACE)):
            raise ValueError("User does not have permission to edit this workspace")
        
        # Update the workspace fields
        for key, value in kwargs.items():
            if key in ['name', 'description', 'is_public', 'metadata']:
                setattr(workspace, key, value)
        
        # Update the updated_at timestamp
        workspace.updated_at = datetime.datetime.now()
        
        # Save the updated workspaces
        self._save_workspaces(workspaces)
        
        return workspace
    
    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            user_id: ID of the user requesting deletion
            
        Returns:
            True if the workspace was deleted, False if not found or user doesn't have permission
            
        Raises:
            ValueError: If the user doesn't have permission to delete the workspace
        """
        workspaces = self._load_workspaces()
        
        if workspace_id not in workspaces:
            return False
        
        workspace = workspaces[workspace_id]
        
        # Check if the user has permission to delete the workspace
        if not (user_id == workspace.created_by or check_permission(user_id, Permission.DELETE_WORKSPACE)):
            raise ValueError("User does not have permission to delete this workspace")
        
        # Delete the workspace
        del workspaces[workspace_id]
        self._save_workspaces(workspaces)
        
        return True
    
    def add_user_to_workspace(self, workspace_id: str, user_id: str, added_by: str) -> bool:
        """
        Add a user to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user to add
            added_by: ID of the user adding the new member
            
        Returns:
            True if the user was added, False if the workspace wasn't found
            
        Raises:
            ValueError: If the user adding doesn't have permission
        """
        workspaces = self._load_workspaces()
        workspace = workspaces.get(workspace_id)
        
        if workspace is None:
            return False
        
        # Check if the user has permission to add members
        if not (added_by == workspace.created_by or 
                added_by in workspace.members and check_permission(added_by, Permission.EDIT_WORKSPACE)):
            raise ValueError("User does not have permission to add members to this workspace")
        
        # Add the user to the workspace
        workspace.add_member(user_id)
        
        # Save the updated workspaces
        self._save_workspaces(workspaces)
        
        return True
    
    def remove_user_from_workspace(self, workspace_id: str, user_id: str, removed_by: str) -> bool:
        """
        Remove a user from a workspace.
        
        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user to remove
            removed_by: ID of the user removing the member
            
        Returns:
            True if the user was removed, False if the workspace wasn't found or the user wasn't a member
            
        Raises:
            ValueError: If the user removing doesn't have permission or is trying to remove the creator
        """
        workspaces = self._load_workspaces()
        workspace = workspaces.get(workspace_id)
        
        if workspace is None:
            return False
        
        # Check if the user is trying to remove the creator
        if user_id == workspace.created_by:
            raise ValueError("Cannot remove the workspace creator")
        
        # Check if the user has permission to remove members
        if not (removed_by == workspace.created_by or 
                removed_by in workspace.members and check_permission(removed_by, Permission.EDIT_WORKSPACE) or
                removed_by == user_id):  # Users can remove themselves
            raise ValueError("User does not have permission to remove members from this workspace")
        
        # Remove the user from the workspace
        result = workspace.remove_member(user_id)
        
        if result:
            # Save the updated workspaces
            self._save_workspaces(workspaces)
        
        return result
    
    def add_resource_to_workspace(self, workspace_id: str, resource: WorkspaceResource, 
                                 user_id: str) -> bool:
        """
        Add a resource to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            resource: WorkspaceResource to add
            user_id: ID of the user adding the resource
            
        Returns:
            True if the resource was added, False if the workspace wasn't found
            
        Raises:
            ValueError: If the user doesn't have permission
        """
        workspaces = self._load_workspaces()
        workspace = workspaces.get(workspace_id)
        
        if workspace is None:
            return False
        
        # Check if the user has permission to add resources
        if not (user_id == workspace.created_by or 
                user_id in workspace.members and check_permission(user_id, Permission.EDIT_WORKSPACE)):
            raise ValueError("User does not have permission to add resources to this workspace")
        
        # Set the created_by field if not already set
        if not resource.created_by:
            resource.created_by = user_id
        
        # Add the resource to the workspace
        workspace.add_resource(resource)
        
        # Save the updated workspaces
        self._save_workspaces(workspaces)
        
        return True
    
    def remove_resource_from_workspace(self, workspace_id: str, resource_id: str, 
                                      user_id: str) -> bool:
        """
        Remove a resource from a workspace.
        
        Args:
            workspace_id: ID of the workspace
            resource_id: ID of the resource to remove
            user_id: ID of the user removing the resource
            
        Returns:
            True if the resource was removed, False if the workspace or resource wasn't found
            
        Raises:
            ValueError: If the user doesn't have permission
        """
        workspaces = self._load_workspaces()
        workspace = workspaces.get(workspace_id)
        
        if workspace is None:
            return False
        
        resource = workspace.get_resource(resource_id)
        if resource is None:
            return False
        
        # Check if the user has permission to remove resources
        if not (user_id == workspace.created_by or 
                user_id == resource.created_by or
                user_id in workspace.members and check_permission(user_id, Permission.EDIT_WORKSPACE)):
            raise ValueError("User does not have permission to remove resources from this workspace")
        
        # Remove the resource from the workspace
        result = workspace.remove_resource(resource_id)
        
        if result:
            # Save the updated workspaces
            self._save_workspaces(workspaces)
        
        return result
    
    def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """
        Get all workspaces that a user is a member of.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Workspace objects that the user is a member of
        """
        workspaces = self._load_workspaces()
        
        # Filter workspaces where the user is a member
        user_workspaces = [
            workspace for workspace in workspaces.values()
            if user_id in workspace.members
        ]
        
        return user_workspaces
    
    def get_public_workspaces(self) -> List[Workspace]:
        """
        Get all public workspaces.
        
        Returns:
            List of public Workspace objects
        """
        workspaces = self._load_workspaces()
        
        # Filter public workspaces
        public_workspaces = [
            workspace for workspace in workspaces.values()
            if workspace.is_public
        ]
        
        return public_workspaces


# Module-level functions that use the WorkspaceManager

def create_workspace(name: str, description: str, created_by: str, is_public: bool = False,
                    storage_path: str = None) -> Workspace:
    """
    Create a new workspace.
    
    Args:
        name: Name of the workspace
        description: Description of the workspace
        created_by: ID of the user creating the workspace
        is_public: Whether the workspace is public (visible to all users)
        storage_path: Optional path to the workspace data storage file
        
    Returns:
        Newly created Workspace object
        
    Raises:
        ValueError: If the user doesn't have permission to create workspaces
    """
    manager = WorkspaceManager(storage_path)
    return manager.create_workspace(name, description, created_by, is_public)


def get_workspace(workspace_id: str, storage_path: str = None) -> Optional[Workspace]:
    """
    Get a workspace by ID.
    
    Args:
        workspace_id: ID of the workspace to retrieve
        storage_path: Optional path to the workspace data storage file
        
    Returns:
        Workspace object if found, None otherwise
    """
    manager = WorkspaceManager(storage_path)
    return manager.get_workspace(workspace_id)


def update_workspace(workspace_id: str, user_id: str, storage_path: str = None, **kwargs) -> Optional[Workspace]:
    """
    Update a workspace.
    
    Args:
        workspace_id: ID of the workspace to update
        user_id: ID of the user making the update
        storage_path: Optional path to the workspace data storage file
        **kwargs: Fields to update (can include name, description, is_public, metadata)
        
    Returns:
        Updated Workspace object if found and user has permission, None otherwise
        
    Raises:
        ValueError: If the user doesn't have permission to edit the workspace
    """
    manager = WorkspaceManager(storage_path)
    return manager.update_workspace(workspace_id, user_id, **kwargs)


def delete_workspace(workspace_id: str, user_id: str, storage_path: str = None) -> bool:
    """
    Delete a workspace.
    
    Args:
        workspace_id: ID of the workspace to delete
        user_id: ID of the user requesting deletion
        storage_path: Optional path to the workspace data storage file
        
    Returns:
        True if the workspace was deleted, False if not found or user doesn't have permission
        
    Raises:
        ValueError: If the user doesn't have permission to delete the workspace
    """
    manager = WorkspaceManager(storage_path)
    return manager.delete_workspace(workspace_id, user_id)


def add_user_to_workspace(workspace_id: str, user_id: str, added_by: str, 
                         storage_path: str = None) -> bool:
    """
    Add a user to a workspace.
    
    Args:
        workspace_id: ID of the workspace
        user_id: ID of the user to add
        added_by: ID of the user adding the new member
        storage_path: Optional path to the workspace data storage file
        
    Returns:
        True if the user was added, False if the workspace wasn't found
        
    Raises:
        ValueError: If the user adding doesn't have permission
    """
    manager = WorkspaceManager(storage_path)
    return manager.add_user_to_workspace(workspace_id, user_id, added_by)


def remove_user_from_workspace(workspace_id: str, user_id: str, removed_by: str,
                              storage_path: str = None) -> bool:
    """
    Remove a user from a workspace.
    
    Args:
        workspace_id: ID of the workspace
        user_id: ID of the user to remove
        removed_by: ID of the user removing the member
        storage_path: Optional path to the workspace data storage file
        
    Returns:
        True if the user was removed, False if the workspace wasn't found or the user wasn't a member
        
    Raises:
        ValueError: If the user removing doesn't have permission or is trying to remove the creator
    """
    manager = WorkspaceManager(storage_path)
    return manager.remove_user_from_workspace(workspace_id, user_id, removed_by)