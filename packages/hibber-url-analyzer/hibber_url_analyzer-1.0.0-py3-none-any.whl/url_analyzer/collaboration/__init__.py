"""
Collaboration module for URL Analyzer.

This module provides functionality for multi-user collaboration, including:
- User management
- Role-based access control
- Shared workspaces
- Commenting and annotations
- Notification system
- Audit trails

These features enable teams to work together on URL analysis projects,
share insights, and maintain security through proper access controls.
"""

from url_analyzer.collaboration.user_management import (
    User,
    UserManager,
    authenticate_user,
    create_user,
    delete_user,
    get_user,
    update_user,
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
    delete_workspace,
    get_workspace,
    update_workspace,
    add_user_to_workspace,
    remove_user_from_workspace,
)
from url_analyzer.collaboration.annotations import (
    Comment,
    Annotation,
    create_comment,
    delete_comment,
    create_annotation,
    delete_annotation,
)
from url_analyzer.collaboration.notifications import (
    Notification,
    NotificationManager,
    create_notification,
    mark_as_read,
    get_user_notifications,
)
from url_analyzer.collaboration.audit import (
    AuditLog,
    AuditManager,
    log_activity,
    get_audit_logs,
)

__all__ = [
    # User management
    'User',
    'UserManager',
    'authenticate_user',
    'create_user',
    'delete_user',
    'get_user',
    'update_user',
    
    # Access control
    'Role',
    'Permission',
    'RoleManager',
    'check_permission',
    'assign_role',
    'revoke_role',
    
    # Workspace management
    'Workspace',
    'WorkspaceManager',
    'create_workspace',
    'delete_workspace',
    'get_workspace',
    'update_workspace',
    'add_user_to_workspace',
    'remove_user_from_workspace',
    
    # Annotations
    'Comment',
    'Annotation',
    'create_comment',
    'delete_comment',
    'create_annotation',
    'delete_annotation',
    
    # Notifications
    'Notification',
    'NotificationManager',
    'create_notification',
    'mark_as_read',
    'get_user_notifications',
    
    # Audit
    'AuditLog',
    'AuditManager',
    'log_activity',
    'get_audit_logs',
]