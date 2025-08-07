"""
Test script for the collaboration features of URL Analyzer.

This script tests the functionality of the collaboration module, including:
- User management
- Role-based access control
- Shared workspaces
- Commenting and annotations
- Notification system
- Audit trails
"""

import unittest
from datetime import datetime
from uuid import uuid4

from url_analyzer.collaboration.user_management import (
    User,
    UserManager,
    create_user,
    get_user,
    update_user,
    delete_user,
    authenticate_user,
)
from url_analyzer.collaboration.access_control import (
    Role,
    Permission,
    RoleManager,
    check_permission,
    assign_role,
    revoke_role,
)
from url_analyzer.collaboration.workspace import (
    Workspace,
    WorkspaceManager,
    create_workspace,
    get_workspace,
    update_workspace,
    delete_workspace,
    add_user_to_workspace,
    remove_user_from_workspace,
)
from url_analyzer.collaboration.annotations import (
    Comment,
    Annotation,
    create_comment,
    delete_comment,
    get_comment,
    update_comment,
    get_comments_for_target,
    get_comment_replies,
    create_annotation,
    delete_annotation,
    get_annotation,
    update_annotation,
    get_annotations_for_target,
)
from url_analyzer.collaboration.notifications import (
    Notification,
    create_notification,
    get_notification,
    get_user_notifications,
    mark_as_read,
    mark_all_as_read,
    delete_notification,
    set_notification_preference,
    get_notification_preference,
)
from url_analyzer.collaboration.audit import (
    AuditLog,
    log_activity,
    get_audit_log,
    get_audit_logs,
    export_audit_logs,
)


class TestUserManagement(unittest.TestCase):
    """Test user management functionality."""
    
    def test_create_user(self):
        """Test creating a user."""
        username = f"test_user_{str(uuid4())[:8]}"
        email = f"{username}@example.com"
        
        user = create_user(
            username=username,
            email=email,
            password="password123",
            full_name="Test User"
        )
        
        # Store the user_id for later use
        user_id = user.user_id
        
        self.assertEqual(user.user_id, user_id)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertEqual(user.full_name, "Test User")
        # Note: User class uses preferences instead of metadata
        self.assertIsInstance(user.preferences, dict)
        
        # Verify we can retrieve the user
        retrieved_user = get_user(user_id)
        self.assertEqual(retrieved_user.user_id, user_id)
        
        # Clean up
        delete_user(user_id)
        self.assertIsNone(get_user(user_id))


class TestAccessControl(unittest.TestCase):
    """Test access control functionality."""
    
    def test_role_and_permissions(self):
        """Test roles and permissions."""
        # Create a user
        username = f"test_user_{str(uuid4())[:8]}"
        user = create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            full_name="Test User"
        )
        user_id = user.user_id
        
        # Create a role
        role_name = "test_role"
        permissions = [
            Permission.VIEW_ANALYSIS,
            Permission.RUN_ANALYSIS,
            Permission.VIEW_REPORT
        ]
        
        role_manager = RoleManager()
        role = role_manager.create_role(role_name, permissions)
        
        # Assign the role to the user
        assign_role(user_id, role_name)
        
        # Check permissions
        self.assertTrue(check_permission(user_id, Permission.VIEW_ANALYSIS))
        self.assertTrue(check_permission(user_id, Permission.RUN_ANALYSIS))
        self.assertTrue(check_permission(user_id, Permission.VIEW_REPORT))
        self.assertFalse(check_permission(user_id, Permission.EDIT_REPORT))
        
        # Revoke the role
        revoke_role(user_id, role_name)
        
        # Verify permissions are revoked
        self.assertFalse(check_permission(user_id, Permission.VIEW_ANALYSIS))
        
        # Clean up
        delete_user(user_id)


class TestWorkspace(unittest.TestCase):
    """Test workspace functionality."""
    
    def test_workspace_operations(self):
        """Test workspace creation and management."""
        # Create users
        username1 = f"test_user_1_{str(uuid4())[:8]}"
        user1 = create_user(
            username=username1,
            email=f"{username1}@example.com",
            password="password123",
            full_name="Test User 1"
        )
        user1_id = user1.user_id
        
        username2 = f"test_user_2_{str(uuid4())[:8]}"
        user2 = create_user(
            username=username2,
            email=f"{username2}@example.com",
            password="password123",
            full_name="Test User 2"
        )
        user2_id = user2.user_id
        
        # Create a workspace
        workspace_name = f"Test Workspace {str(uuid4())[:8]}"
        
        workspace = create_workspace(
            name=workspace_name,
            description="A test workspace",
            created_by=user1_id
        )
        
        # Store the workspace_id for later use
        workspace_id = workspace.workspace_id
        
        self.assertEqual(workspace.workspace_id, workspace_id)
        self.assertEqual(workspace.name, workspace_name)
        self.assertEqual(workspace.created_by, user1_id)
        
        # Add user2 to the workspace
        add_user_to_workspace(workspace_id, user2_id)
        
        # Verify user2 is in the workspace
        workspace = get_workspace(workspace_id)
        self.assertIn(user2_id, workspace.members)
        
        # Remove user2 from the workspace
        remove_user_from_workspace(workspace_id, user2_id)
        
        # Verify user2 is no longer in the workspace
        workspace = get_workspace(workspace_id)
        self.assertNotIn(user2_id, workspace.members)
        
        # Update the workspace
        update_workspace(
            workspace_id=workspace_id,
            name="Updated Workspace",
            description="An updated test workspace"
        )
        
        # Verify the update
        workspace = get_workspace(workspace_id)
        self.assertEqual(workspace.name, "Updated Workspace")
        self.assertEqual(workspace.description, "An updated test workspace")
        
        # Delete the workspace
        delete_workspace(workspace_id)
        
        # Verify the workspace is deleted
        self.assertIsNone(get_workspace(workspace_id))
        
        # Clean up
        delete_user(user1_id)
        delete_user(user2_id)


class TestAnnotations(unittest.TestCase):
    """Test annotations and comments functionality."""
    
    def test_annotations(self):
        """Test creating and managing annotations."""
        # Create a user
        username = f"test_user_{str(uuid4())[:8]}"
        user = create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            full_name="Test User"
        )
        user_id = user.user_id
        
        # Create an annotation
        target_id = str(uuid4())
        target_type = "url"
        content = "This is a test annotation"
        highlighted_text = "example.com/test"
        
        annotation = create_annotation(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type,
            content=content,
            highlighted_text=highlighted_text
        )
        
        # Verify the annotation
        self.assertEqual(annotation.user_id, user_id)
        self.assertEqual(annotation.target_id, target_id)
        self.assertEqual(annotation.target_type, target_type)
        self.assertEqual(annotation.content, content)
        self.assertEqual(annotation.highlighted_text, highlighted_text)
        
        # Get the annotation
        retrieved_annotation = get_annotation(annotation.id)
        self.assertEqual(retrieved_annotation.id, annotation.id)
        
        # Update the annotation
        updated_content = "Updated annotation content"
        updated_annotation = update_annotation(
            annotation_id=annotation.id,
            user_id=user_id,
            content=updated_content
        )
        
        # Verify the update
        self.assertEqual(updated_annotation.content, updated_content)
        
        # Get annotations for target
        target_annotations = get_annotations_for_target(target_id, target_type)
        self.assertEqual(len(target_annotations), 1)
        self.assertEqual(target_annotations[0].id, annotation.id)
        
        # Delete the annotation
        delete_annotation(annotation.id, user_id)
        
        # Verify the annotation is deleted
        self.assertIsNone(get_annotation(annotation.id))
        
        # Clean up
        delete_user(user_id)
    
    def test_comments(self):
        """Test creating and managing comments."""
        # Create a user
        username = f"test_user_{str(uuid4())[:8]}"
        user = create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            full_name="Test User"
        )
        user_id = user.user_id
        
        # Create a comment
        target_id = str(uuid4())
        target_type = "url"
        content = "This is a test comment"
        
        comment = create_comment(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type,
            content=content
        )
        
        # Verify the comment
        self.assertEqual(comment.user_id, user_id)
        self.assertEqual(comment.target_id, target_id)
        self.assertEqual(comment.target_type, target_type)
        self.assertEqual(comment.content, content)
        
        # Get the comment
        retrieved_comment = get_comment(comment.id)
        self.assertEqual(retrieved_comment.id, comment.id)
        
        # Create a reply
        reply_content = "This is a reply to the comment"
        reply = create_comment(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type,
            content=reply_content,
            parent_id=comment.id
        )
        
        # Verify the reply
        self.assertEqual(reply.parent_id, comment.id)
        
        # Get replies
        replies = get_comment_replies(comment.id)
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].id, reply.id)
        
        # Update the comment
        updated_content = "Updated comment content"
        updated_comment = update_comment(
            comment_id=comment.id,
            user_id=user_id,
            content=updated_content
        )
        
        # Verify the update
        self.assertEqual(updated_comment.content, updated_content)
        
        # Get comments for target
        target_comments = get_comments_for_target(target_id, target_type)
        self.assertEqual(len(target_comments), 1)  # Only top-level comments
        
        # Delete the comments
        delete_comment(reply.id, user_id)
        delete_comment(comment.id, user_id)
        
        # Verify the comments are deleted
        self.assertIsNone(get_comment(comment.id))
        self.assertIsNone(get_comment(reply.id))
        
        # Clean up
        delete_user(user_id)


class TestNotifications(unittest.TestCase):
    """Test notification functionality."""
    
    def test_notifications(self):
        """Test creating and managing notifications."""
        # Create a user
        username = f"test_user_{str(uuid4())[:8]}"
        user = create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            full_name="Test User"
        )
        user_id = user.user_id
        
        # Create a notification
        resource_id = str(uuid4())
        resource_type = "url"
        notification_type = "mention"
        content = "You were mentioned in a comment"
        
        notification = create_notification(
            user_id=user_id,
            type=notification_type,
            content=content,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        # Verify the notification
        self.assertEqual(notification.user_id, user_id)
        self.assertEqual(notification.type, notification_type)
        self.assertEqual(notification.content, content)
        self.assertEqual(notification.resource_type, resource_type)
        self.assertEqual(notification.resource_id, resource_id)
        self.assertFalse(notification.read)
        
        # Get the notification
        retrieved_notification = get_notification(notification.id)
        self.assertEqual(retrieved_notification.id, notification.id)
        
        # Get user notifications
        user_notifications = get_user_notifications(user_id)
        self.assertEqual(len(user_notifications), 1)
        self.assertEqual(user_notifications[0].id, notification.id)
        
        # Mark as read
        mark_as_read(notification.id, user_id)
        
        # Verify the notification is marked as read
        retrieved_notification = get_notification(notification.id)
        self.assertTrue(retrieved_notification.read)
        
        # Create another notification
        notification2 = create_notification(
            user_id=user_id,
            type="comment",
            content="New comment on your URL",
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        # Mark all as read
        mark_all_as_read(user_id)
        
        # Verify all notifications are marked as read
        user_notifications = get_user_notifications(user_id)
        for notification in user_notifications:
            self.assertTrue(notification.read)
        
        # Set notification preference
        set_notification_preference(user_id, "mention", False)
        
        # Verify the preference
        preference = get_notification_preference(user_id, "mention")
        self.assertFalse(preference)
        
        # Delete the notifications
        delete_notification(notification.id, user_id)
        delete_notification(notification2.id, user_id)
        
        # Verify the notifications are deleted
        self.assertIsNone(get_notification(notification.id))
        self.assertIsNone(get_notification(notification2.id))
        
        # Clean up
        delete_user(user_id)


class TestAudit(unittest.TestCase):
    """Test audit functionality."""
    
    def test_audit_logs(self):
        """Test creating and retrieving audit logs."""
        # Create a user
        username = f"test_user_{str(uuid4())[:8]}"
        user = create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            full_name="Test User"
        )
        user_id = user.user_id
        
        # Log an activity
        resource_id = str(uuid4())
        resource_type = "url"
        action = "view"
        
        audit_log = log_activity(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"referrer": "search"}
        )
        
        # Verify the audit log
        self.assertEqual(audit_log.user_id, user_id)
        self.assertEqual(audit_log.action, action)
        self.assertEqual(audit_log.resource_type, resource_type)
        self.assertEqual(audit_log.resource_id, resource_id)
        self.assertEqual(audit_log.details.get("referrer"), "search")
        
        # Get the audit log
        retrieved_log = get_audit_log(audit_log.id)
        self.assertEqual(retrieved_log.id, audit_log.id)
        
        # Log another activity
        log_activity(
            user_id=user_id,
            action="analyze",
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        # Get audit logs for user
        user_logs = get_audit_logs(user_id=user_id)
        self.assertEqual(len(user_logs), 2)
        
        # Get audit logs for resource
        resource_logs = get_audit_logs(resource_id=resource_id)
        self.assertEqual(len(resource_logs), 2)
        
        # Get audit logs for action
        action_logs = get_audit_logs(action=action)
        self.assertEqual(len(action_logs), 1)
        
        # Export audit logs
        exported_logs = export_audit_logs(user_id=user_id)
        self.assertEqual(len(exported_logs), 2)
        
        # Clean up
        delete_user(user_id)


if __name__ == "__main__":
    unittest.main()