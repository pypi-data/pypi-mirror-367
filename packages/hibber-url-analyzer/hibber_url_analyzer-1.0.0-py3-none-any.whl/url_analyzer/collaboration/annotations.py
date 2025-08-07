"""
Annotations module for URL Analyzer.

This module provides functionality for adding comments and annotations to URLs,
reports, and other elements in the URL Analyzer system. It enables collaborative
discussions and knowledge sharing among team members.

Features:
- Comments on URLs, reports, and analysis results
- Annotations with highlighted sections
- Reply threads for discussions
- Tagging users in comments
- Markdown support for rich text formatting
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from uuid import uuid4

from url_analyzer.collaboration.user_management import User
from url_analyzer.collaboration.audit import log_activity
from url_analyzer.collaboration.notifications import create_notification


class Annotation:
    """
    Represents an annotation on a specific element in the system.
    
    Annotations can be attached to URLs, reports, or specific sections of content.
    They include highlighted text and optional comments.
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        target_id: str,
        target_type: str,
        content: str,
        highlighted_text: Optional[str] = None,
        position: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an Annotation object.
        
        Args:
            id: Unique identifier for the annotation
            user_id: ID of the user who created the annotation
            target_id: ID of the element being annotated (URL, report, etc.)
            target_type: Type of element being annotated (url, report, etc.)
            content: Text content of the annotation
            highlighted_text: Optional text that is highlighted by this annotation
            position: Optional position information for the annotation
            created_at: Timestamp when the annotation was created
            updated_at: Timestamp when the annotation was last updated
            metadata: Additional metadata for the annotation
        """
        self.id = id
        self.user_id = user_id
        self.target_id = target_id
        self.target_type = target_type
        self.content = content
        self.highlighted_text = highlighted_text
        self.position = position or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the annotation to a dictionary.
        
        Returns:
            Dictionary representation of the annotation
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "content": self.content,
            "highlighted_text": self.highlighted_text,
            "position": self.position,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        """
        Create an Annotation object from a dictionary.
        
        Args:
            data: Dictionary containing annotation data
            
        Returns:
            Annotation object
        """
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        updated_at = datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"]
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            target_id=data["target_id"],
            target_type=data["target_type"],
            content=data["content"],
            highlighted_text=data.get("highlighted_text"),
            position=data.get("position", {}),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {})
        )


class Comment:
    """
    Represents a comment in the system.
    
    Comments can be attached to URLs, reports, or other comments (for replies).
    They support markdown formatting and user tagging.
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        target_id: str,
        target_type: str,
        content: str,
        parent_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Comment object.
        
        Args:
            id: Unique identifier for the comment
            user_id: ID of the user who created the comment
            target_id: ID of the element being commented on
            target_type: Type of element being commented on
            content: Text content of the comment
            parent_id: Optional ID of the parent comment (for replies)
            created_at: Timestamp when the comment was created
            updated_at: Timestamp when the comment was last updated
            metadata: Additional metadata for the comment
        """
        self.id = id
        self.user_id = user_id
        self.target_id = target_id
        self.target_type = target_type
        self.content = content
        self.parent_id = parent_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the comment to a dictionary.
        
        Returns:
            Dictionary representation of the comment
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "content": self.content,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        """
        Create a Comment object from a dictionary.
        
        Args:
            data: Dictionary containing comment data
            
        Returns:
            Comment object
        """
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        updated_at = datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"]
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            target_id=data["target_id"],
            target_type=data["target_type"],
            content=data["content"],
            parent_id=data.get("parent_id"),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {})
        )


# In-memory storage for annotations and comments
# In a production system, this would be replaced with a database
_annotations: Dict[str, Annotation] = {}
_comments: Dict[str, Comment] = {}


def create_annotation(
    user_id: str,
    target_id: str,
    target_type: str,
    content: str,
    highlighted_text: Optional[str] = None,
    position: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Annotation:
    """
    Create a new annotation.
    
    Args:
        user_id: ID of the user creating the annotation
        target_id: ID of the element being annotated
        target_type: Type of element being annotated
        content: Text content of the annotation
        highlighted_text: Optional text that is highlighted by this annotation
        position: Optional position information for the annotation
        metadata: Additional metadata for the annotation
        
    Returns:
        The created Annotation object
    """
    annotation_id = str(uuid4())
    annotation = Annotation(
        id=annotation_id,
        user_id=user_id,
        target_id=target_id,
        target_type=target_type,
        content=content,
        highlighted_text=highlighted_text,
        position=position,
        metadata=metadata
    )
    
    _annotations[annotation_id] = annotation
    
    # Log the activity
    log_activity(
        user_id=user_id,
        action="create_annotation",
        resource_type=target_type,
        resource_id=target_id,
        details={"annotation_id": annotation_id}
    )
    
    # Notify users who are mentioned in the content
    _notify_mentioned_users(user_id, content, target_id, target_type, "annotation")
    
    return annotation


def get_annotation(annotation_id: str) -> Optional[Annotation]:
    """
    Get an annotation by ID.
    
    Args:
        annotation_id: ID of the annotation to retrieve
        
    Returns:
        The Annotation object if found, None otherwise
    """
    return _annotations.get(annotation_id)


def update_annotation(
    annotation_id: str,
    user_id: str,
    content: Optional[str] = None,
    highlighted_text: Optional[str] = None,
    position: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Annotation]:
    """
    Update an existing annotation.
    
    Args:
        annotation_id: ID of the annotation to update
        user_id: ID of the user updating the annotation
        content: New text content of the annotation
        highlighted_text: New highlighted text
        position: New position information
        metadata: New metadata
        
    Returns:
        The updated Annotation object if found, None otherwise
    """
    annotation = _annotations.get(annotation_id)
    if not annotation:
        return None
    
    # Check if the user is the owner of the annotation
    if annotation.user_id != user_id:
        return None
    
    if content is not None:
        annotation.content = content
    
    if highlighted_text is not None:
        annotation.highlighted_text = highlighted_text
    
    if position is not None:
        annotation.position = position
    
    if metadata is not None:
        annotation.metadata.update(metadata)
    
    annotation.updated_at = datetime.now()
    _annotations[annotation_id] = annotation
    
    # Log the activity
    log_activity(
        user_id=user_id,
        action="update_annotation",
        resource_type="annotation",
        resource_id=annotation_id,
        details={}
    )
    
    return annotation


def delete_annotation(annotation_id: str, user_id: str) -> bool:
    """
    Delete an annotation.
    
    Args:
        annotation_id: ID of the annotation to delete
        user_id: ID of the user deleting the annotation
        
    Returns:
        True if the annotation was deleted, False otherwise
    """
    annotation = _annotations.get(annotation_id)
    if not annotation:
        return False
    
    # Check if the user is the owner of the annotation
    if annotation.user_id != user_id:
        return False
    
    del _annotations[annotation_id]
    
    # Log the activity
    log_activity(
        user_id=user_id,
        action="delete_annotation",
        resource_type="annotation",
        resource_id=annotation_id,
        details={}
    )
    
    return True


def get_annotations_for_target(target_id: str, target_type: str) -> List[Annotation]:
    """
    Get all annotations for a specific target.
    
    Args:
        target_id: ID of the target
        target_type: Type of the target
        
    Returns:
        List of Annotation objects for the target
    """
    return [
        annotation for annotation in _annotations.values()
        if annotation.target_id == target_id and annotation.target_type == target_type
    ]


def create_comment(
    user_id: str,
    target_id: str,
    target_type: str,
    content: str,
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Comment:
    """
    Create a new comment.
    
    Args:
        user_id: ID of the user creating the comment
        target_id: ID of the element being commented on
        target_type: Type of element being commented on
        content: Text content of the comment
        parent_id: Optional ID of the parent comment (for replies)
        metadata: Additional metadata for the comment
        
    Returns:
        The created Comment object
    """
    comment_id = str(uuid4())
    comment = Comment(
        id=comment_id,
        user_id=user_id,
        target_id=target_id,
        target_type=target_type,
        content=content,
        parent_id=parent_id,
        metadata=metadata
    )
    
    _comments[comment_id] = comment
    
    # Log the activity
    log_activity(
        user_id=user_id,
        action="create_comment",
        resource_type=target_type,
        resource_id=target_id,
        details={"comment_id": comment_id, "parent_id": parent_id}
    )
    
    # If this is a reply, notify the parent comment author
    if parent_id and parent_id in _comments:
        parent_comment = _comments[parent_id]
        if parent_comment.user_id != user_id:  # Don't notify if replying to own comment
            create_notification(
                user_id=parent_comment.user_id,
                type="comment_reply",
                content=f"New reply to your comment",
                resource_type="comment",
                resource_id=parent_id,
                actor_id=user_id
            )
    
    # Notify users who are mentioned in the content
    _notify_mentioned_users(user_id, content, target_id, target_type, "comment")
    
    return comment


def get_comment(comment_id: str) -> Optional[Comment]:
    """
    Get a comment by ID.
    
    Args:
        comment_id: ID of the comment to retrieve
        
    Returns:
        The Comment object if found, None otherwise
    """
    return _comments.get(comment_id)


def update_comment(
    comment_id: str,
    user_id: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Comment]:
    """
    Update an existing comment.
    
    Args:
        comment_id: ID of the comment to update
        user_id: ID of the user updating the comment
        content: New text content of the comment
        metadata: New metadata
        
    Returns:
        The updated Comment object if found, None otherwise
    """
    comment = _comments.get(comment_id)
    if not comment:
        return None
    
    # Check if the user is the owner of the comment
    if comment.user_id != user_id:
        return None
    
    comment.content = content
    
    if metadata is not None:
        comment.metadata.update(metadata)
    
    comment.updated_at = datetime.now()
    _comments[comment_id] = comment
    
    # Log the activity
    log_activity(
        user_id=user_id,
        action="update_comment",
        resource_type="comment",
        resource_id=comment_id,
        details={}
    )
    
    return comment


def delete_comment(comment_id: str, user_id: str) -> bool:
    """
    Delete a comment.
    
    Args:
        comment_id: ID of the comment to delete
        user_id: ID of the user deleting the comment
        
    Returns:
        True if the comment was deleted, False otherwise
    """
    comment = _comments.get(comment_id)
    if not comment:
        return False
    
    # Check if the user is the owner of the comment
    if comment.user_id != user_id:
        return False
    
    del _comments[comment_id]
    
    # Log the activity
    log_activity(
        user_id=user_id,
        action="delete_comment",
        resource_type="comment",
        resource_id=comment_id,
        details={}
    )
    
    return True


def get_comments_for_target(target_id: str, target_type: str, parent_id: Optional[str] = None) -> List[Comment]:
    """
    Get all comments for a specific target.
    
    Args:
        target_id: ID of the target
        target_type: Type of the target
        parent_id: Optional parent comment ID to filter replies
        
    Returns:
        List of Comment objects for the target
    """
    return [
        comment for comment in _comments.values()
        if comment.target_id == target_id 
        and comment.target_type == target_type
        and comment.parent_id == parent_id
    ]


def get_comment_replies(comment_id: str) -> List[Comment]:
    """
    Get all replies to a specific comment.
    
    Args:
        comment_id: ID of the parent comment
        
    Returns:
        List of Comment objects that are replies to the parent
    """
    return [
        comment for comment in _comments.values()
        if comment.parent_id == comment_id
    ]


def _notify_mentioned_users(user_id: str, content: str, target_id: str, target_type: str, source_type: str) -> None:
    """
    Notify users who are mentioned in the content.
    
    Args:
        user_id: ID of the user who created the content
        content: Text content to check for mentions
        target_id: ID of the target element
        target_type: Type of the target element
        source_type: Type of the source (comment or annotation)
    """
    # Simple mention detection using @username format
    # In a real implementation, this would be more sophisticated
    mentioned_users = []
    words = content.split()
    for word in words:
        if word.startswith('@') and len(word) > 1:
            username = word[1:]
            # In a real implementation, we would look up the user by username
            # For now, we'll just assume the username is the user ID
            if username != user_id:  # Don't notify the author
                mentioned_users.append(username)
    
    # Create notifications for mentioned users
    for mentioned_user_id in mentioned_users:
        create_notification(
            user_id=mentioned_user_id,
            type="mention",
            content=f"You were mentioned in a {source_type}",
            resource_type=source_type,
            resource_id=target_id,
            actor_id=user_id
        )