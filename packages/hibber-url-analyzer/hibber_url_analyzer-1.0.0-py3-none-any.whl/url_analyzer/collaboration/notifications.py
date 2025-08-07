"""
Notifications module for URL Analyzer.

This module provides functionality for sending and managing notifications to users
about various events in the system, such as mentions, comments, and workspace changes.

Features:
- In-app notifications
- User notification preferences
- Notification read/unread status
- Notification filtering and sorting
- Notification aggregation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4


class Notification:
    """
    Represents a notification sent to a user.
    
    Notifications inform users about events in the system, such as mentions,
    comments, or workspace changes.
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        type: str,
        content: str,
        resource_type: str,
        resource_id: str,
        actor_id: Optional[str] = None,
        read: bool = False,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Notification object.
        
        Args:
            id: Unique identifier for the notification
            user_id: ID of the user receiving the notification
            type: Type of notification (mention, comment, etc.)
            content: Text content of the notification
            resource_type: Type of resource the notification is about
            resource_id: ID of the resource the notification is about
            actor_id: Optional ID of the user who triggered the notification
            read: Whether the notification has been read
            created_at: Timestamp when the notification was created
            metadata: Additional metadata for the notification
        """
        self.id = id
        self.user_id = user_id
        self.type = type
        self.content = content
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.actor_id = actor_id
        self.read = read
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the notification to a dictionary.
        
        Returns:
            Dictionary representation of the notification
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "content": self.content,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "actor_id": self.actor_id,
            "read": self.read,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """
        Create a Notification object from a dictionary.
        
        Args:
            data: Dictionary containing notification data
            
        Returns:
            Notification object
        """
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            type=data["type"],
            content=data["content"],
            resource_type=data["resource_type"],
            resource_id=data["resource_id"],
            actor_id=data.get("actor_id"),
            read=data.get("read", False),
            created_at=created_at,
            metadata=data.get("metadata", {})
        )


class NotificationManager:
    """
    Manages notifications for users in the system.
    
    This class provides methods for creating, retrieving, and managing notifications.
    """
    
    def __init__(self):
        """
        Initialize a NotificationManager.
        """
        # In-memory storage for notifications
        # In a production system, this would be replaced with a database
        self._notifications: Dict[str, Notification] = {}
        
        # User notification preferences
        # In a production system, this would be stored in a database
        self._user_preferences: Dict[str, Dict[str, bool]] = {}
    
    def create_notification(
        self,
        user_id: str,
        type: str,
        content: str,
        resource_type: str,
        resource_id: str,
        actor_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create a new notification for a user.
        
        Args:
            user_id: ID of the user receiving the notification
            type: Type of notification (mention, comment, etc.)
            content: Text content of the notification
            resource_type: Type of resource the notification is about
            resource_id: ID of the resource the notification is about
            actor_id: Optional ID of the user who triggered the notification
            metadata: Additional metadata for the notification
            
        Returns:
            The created Notification object
        """
        # Check if the user has disabled this type of notification
        if not self._should_notify(user_id, type):
            return None
        
        notification_id = str(uuid4())
        notification = Notification(
            id=notification_id,
            user_id=user_id,
            type=type,
            content=content,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            metadata=metadata
        )
        
        self._notifications[notification_id] = notification
        return notification
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a notification by ID.
        
        Args:
            notification_id: ID of the notification to retrieve
            
        Returns:
            The Notification object if found, None otherwise
        """
        return self._notifications.get(notification_id)
    
    def get_user_notifications(
        self,
        user_id: str,
        read: Optional[bool] = None,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get notifications for a specific user.
        
        Args:
            user_id: ID of the user
            read: Optional filter for read/unread notifications
            type: Optional filter for notification type
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            
        Returns:
            List of Notification objects for the user
        """
        notifications = [
            n for n in self._notifications.values()
            if n.user_id == user_id
            and (read is None or n.read == read)
            and (type is None or n.type == type)
        ]
        
        # Sort by creation time (newest first)
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        
        # Apply pagination
        return notifications[offset:offset + limit]
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification to mark as read
            user_id: ID of the user marking the notification as read
            
        Returns:
            True if the notification was marked as read, False otherwise
        """
        notification = self._notifications.get(notification_id)
        if not notification or notification.user_id != user_id:
            return False
        
        notification.read = True
        self._notifications[notification_id] = notification
        return True
    
    def mark_all_as_read(self, user_id: str, type: Optional[str] = None) -> int:
        """
        Mark all notifications for a user as read.
        
        Args:
            user_id: ID of the user
            type: Optional filter for notification type
            
        Returns:
            Number of notifications marked as read
        """
        count = 0
        for notification in self._notifications.values():
            if (notification.user_id == user_id and 
                not notification.read and
                (type is None or notification.type == type)):
                notification.read = True
                count += 1
        
        return count
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: ID of the notification to delete
            user_id: ID of the user deleting the notification
            
        Returns:
            True if the notification was deleted, False otherwise
        """
        notification = self._notifications.get(notification_id)
        if not notification or notification.user_id != user_id:
            return False
        
        del self._notifications[notification_id]
        return True
    
    def set_user_preference(self, user_id: str, notification_type: str, enabled: bool) -> None:
        """
        Set a user's preference for a specific notification type.
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification
            enabled: Whether notifications of this type should be enabled
        """
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = {}
        
        self._user_preferences[user_id][notification_type] = enabled
    
    def get_user_preference(self, user_id: str, notification_type: str) -> bool:
        """
        Get a user's preference for a specific notification type.
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification
            
        Returns:
            Whether notifications of this type are enabled (default: True)
        """
        if user_id not in self._user_preferences:
            return True
        
        return self._user_preferences[user_id].get(notification_type, True)
    
    def _should_notify(self, user_id: str, notification_type: str) -> bool:
        """
        Check if a user should receive a specific type of notification.
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification
            
        Returns:
            Whether the user should receive the notification
        """
        return self.get_user_preference(user_id, notification_type)


# Create a global instance of NotificationManager
_notification_manager = NotificationManager()


def create_notification(
    user_id: str,
    type: str,
    content: str,
    resource_type: str,
    resource_id: str,
    actor_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Notification]:
    """
    Create a new notification for a user.
    
    Args:
        user_id: ID of the user receiving the notification
        type: Type of notification (mention, comment, etc.)
        content: Text content of the notification
        resource_type: Type of resource the notification is about
        resource_id: ID of the resource the notification is about
        actor_id: Optional ID of the user who triggered the notification
        metadata: Additional metadata for the notification
        
    Returns:
        The created Notification object, or None if notifications are disabled
    """
    return _notification_manager.create_notification(
        user_id=user_id,
        type=type,
        content=content,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor_id,
        metadata=metadata
    )


def get_notification(notification_id: str) -> Optional[Notification]:
    """
    Get a notification by ID.
    
    Args:
        notification_id: ID of the notification to retrieve
        
    Returns:
        The Notification object if found, None otherwise
    """
    return _notification_manager.get_notification(notification_id)


def get_user_notifications(
    user_id: str,
    read: Optional[bool] = None,
    type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Notification]:
    """
    Get notifications for a specific user.
    
    Args:
        user_id: ID of the user
        read: Optional filter for read/unread notifications
        type: Optional filter for notification type
        limit: Maximum number of notifications to return
        offset: Offset for pagination
        
    Returns:
        List of Notification objects for the user
    """
    return _notification_manager.get_user_notifications(
        user_id=user_id,
        read=read,
        type=type,
        limit=limit,
        offset=offset
    )


def mark_as_read(notification_id: str, user_id: str) -> bool:
    """
    Mark a notification as read.
    
    Args:
        notification_id: ID of the notification to mark as read
        user_id: ID of the user marking the notification as read
        
    Returns:
        True if the notification was marked as read, False otherwise
    """
    return _notification_manager.mark_as_read(notification_id, user_id)


def mark_all_as_read(user_id: str, type: Optional[str] = None) -> int:
    """
    Mark all notifications for a user as read.
    
    Args:
        user_id: ID of the user
        type: Optional filter for notification type
        
    Returns:
        Number of notifications marked as read
    """
    return _notification_manager.mark_all_as_read(user_id, type)


def delete_notification(notification_id: str, user_id: str) -> bool:
    """
    Delete a notification.
    
    Args:
        notification_id: ID of the notification to delete
        user_id: ID of the user deleting the notification
        
    Returns:
        True if the notification was deleted, False otherwise
    """
    return _notification_manager.delete_notification(notification_id, user_id)


def set_notification_preference(user_id: str, notification_type: str, enabled: bool) -> None:
    """
    Set a user's preference for a specific notification type.
    
    Args:
        user_id: ID of the user
        notification_type: Type of notification
        enabled: Whether notifications of this type should be enabled
    """
    _notification_manager.set_user_preference(user_id, notification_type, enabled)


def get_notification_preference(user_id: str, notification_type: str) -> bool:
    """
    Get a user's preference for a specific notification type.
    
    Args:
        user_id: ID of the user
        notification_type: Type of notification
        
    Returns:
        Whether notifications of this type are enabled (default: True)
    """
    return _notification_manager.get_user_preference(user_id, notification_type)