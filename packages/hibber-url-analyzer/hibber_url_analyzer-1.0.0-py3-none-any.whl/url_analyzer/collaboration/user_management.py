"""
User management module for URL Analyzer collaboration features.

This module provides functionality for managing users, including:
- User creation, retrieval, updating, and deletion
- User authentication
- User profile management
- Password management with secure hashing

These features enable multi-user support for the URL Analyzer application.
"""

import datetime
import hashlib
import json
import os
import secrets
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any


@dataclass
class User:
    """
    Represents a user in the system.
    
    Attributes:
        username: Unique username for the user
        email: User's email address
        password_hash: Hashed password (not stored in plain text)
        full_name: User's full name
        created_at: Timestamp when the user was created
        last_login: Timestamp of the last login
        is_active: Whether the user account is active
        user_id: Unique identifier for the user
        preferences: User preferences as a dictionary
    """
    username: str
    email: str
    password_hash: str
    full_name: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_login: Optional[datetime.datetime] = None
    is_active: bool = True
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the user object to a dictionary.
        
        Returns:
            Dict containing user data with datetime objects converted to ISO format strings
        """
        data = asdict(self)
        # Convert datetime objects to strings for JSON serialization
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['last_login']:
            data['last_login'] = data['last_login'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User object from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User object created from the dictionary
        """
        # Convert string timestamps back to datetime objects
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if 'last_login' in data and data['last_login']:
            data['last_login'] = datetime.datetime.fromisoformat(data['last_login'])
        return cls(**data)


class UserManager:
    """
    Manages user operations including creation, retrieval, updating, and deletion.
    
    This class provides a centralized way to manage users and their data,
    with methods for common operations and persistence.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the UserManager.
        
        Args:
            storage_path: Path to the user data storage file
        """
        if storage_path is None:
            # Default to a users.json file in the application data directory
            app_data_dir = Path(os.path.expanduser("~")) / ".url_analyzer"
            app_data_dir.mkdir(exist_ok=True)
            self.storage_path = app_data_dir / "users.json"
        else:
            self.storage_path = Path(storage_path)
        
        # Create the storage file if it doesn't exist
        if not self.storage_path.exists():
            self._save_users({})
    
    def _load_users(self) -> Dict[str, User]:
        """
        Load users from the storage file.
        
        Returns:
            Dictionary mapping user IDs to User objects
        """
        try:
            with open(self.storage_path, 'r') as f:
                user_data = json.load(f)
                return {
                    user_id: User.from_dict(data)
                    for user_id, data in user_data.items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict[str, User]) -> None:
        """
        Save users to the storage file.
        
        Args:
            users: Dictionary mapping user IDs to User objects
        """
        user_data = {
            user_id: user.to_dict()
            for user_id, user in users.items()
        }
        
        # Create directory if it doesn't exist
        self.storage_path.parent.mkdir(exist_ok=True)
        
        with open(self.storage_path, 'w') as f:
            json.dump(user_data, f, indent=2)
    
    def create_user(self, username: str, email: str, password: str, full_name: str) -> User:
        """
        Create a new user.
        
        Args:
            username: Unique username for the user
            email: User's email address
            password: Plain text password (will be hashed)
            full_name: User's full name
            
        Returns:
            Newly created User object
            
        Raises:
            ValueError: If a user with the given username or email already exists
        """
        # Load existing users
        users = self._load_users()
        
        # Check if username or email already exists
        for user in users.values():
            if user.username == username:
                raise ValueError(f"Username '{username}' is already taken")
            if user.email == email:
                raise ValueError(f"Email '{email}' is already registered")
        
        # Hash the password
        password_hash = self._hash_password(password)
        
        # Create the new user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )
        
        # Add the user to the dictionary and save
        users[user.user_id] = user
        self._save_users(users)
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        users = self._load_users()
        return users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        users = self._load_users()
        for user in users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        users = self._load_users()
        for user in users.values():
            if user.email == email:
                return user
        return None
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update a user's information.
        
        Args:
            user_id: ID of the user to update
            **kwargs: Fields to update (can include email, full_name, is_active, preferences)
            
        Returns:
            Updated User object if found, None otherwise
            
        Raises:
            ValueError: If trying to update username or password_hash directly
                       (use change_password for password updates)
        """
        # Prevent direct updates to username and password_hash
        if 'username' in kwargs:
            raise ValueError("Username cannot be updated directly")
        if 'password_hash' in kwargs:
            raise ValueError("Use change_password method to update password")
        
        users = self._load_users()
        user = users.get(user_id)
        
        if user is None:
            return None
        
        # Update the user fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        # Save the updated users
        self._save_users(users)
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if the user was deleted, False if not found
        """
        users = self._load_users()
        
        if user_id not in users:
            return False
        
        del users[user_id]
        self._save_users(users)
        
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username of the user to authenticate
            password: Plain text password to check
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.get_user_by_username(username)
        
        if user is None or not user.is_active:
            return None
        
        # Check the password
        if self._verify_password(password, user.password_hash):
            # Update last login time
            user.last_login = datetime.datetime.now()
            users = self._load_users()
            users[user.user_id] = user
            self._save_users(users)
            return user
        
        return None
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: ID of the user
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password was changed successfully, False otherwise
        """
        users = self._load_users()
        user = users.get(user_id)
        
        if user is None:
            return False
        
        # Verify the current password
        if not self._verify_password(current_password, user.password_hash):
            return False
        
        # Update the password
        user.password_hash = self._hash_password(new_password)
        self._save_users(users)
        
        return True
    
    def reset_password(self, user_id: str) -> Optional[str]:
        """
        Reset a user's password and generate a temporary one.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Temporary password if successful, None if user not found
        """
        users = self._load_users()
        user = users.get(user_id)
        
        if user is None:
            return None
        
        # Generate a temporary password
        temp_password = secrets.token_urlsafe(12)
        
        # Update the password
        user.password_hash = self._hash_password(temp_password)
        self._save_users(users)
        
        return temp_password
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password for secure storage.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        # Generate a random salt
        salt = secrets.token_hex(16)
        
        # Hash the password with the salt
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        
        # Return the salt and hash together
        return f"{salt}${password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash
            
        Returns:
            True if the password matches, False otherwise
        """
        # Split the stored hash into salt and hash
        salt, stored_hash = password_hash.split('$')
        
        # Hash the provided password with the same salt
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode('utf-8'))
        calculated_hash = hash_obj.hexdigest()
        
        # Compare the hashes
        return calculated_hash == stored_hash


# Module-level functions that use the UserManager

def create_user(username: str, email: str, password: str, full_name: str, 
                storage_path: str = None) -> User:
    """
    Create a new user.
    
    Args:
        username: Unique username for the user
        email: User's email address
        password: Plain text password (will be hashed)
        full_name: User's full name
        storage_path: Optional path to the user data storage file
        
    Returns:
        Newly created User object
        
    Raises:
        ValueError: If a user with the given username or email already exists
    """
    manager = UserManager(storage_path)
    return manager.create_user(username, email, password, full_name)


def get_user(user_id: str, storage_path: str = None) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        user_id: ID of the user to retrieve
        storage_path: Optional path to the user data storage file
        
    Returns:
        User object if found, None otherwise
    """
    manager = UserManager(storage_path)
    return manager.get_user(user_id)


def update_user(user_id: str, storage_path: str = None, **kwargs) -> Optional[User]:
    """
    Update a user's information.
    
    Args:
        user_id: ID of the user to update
        storage_path: Optional path to the user data storage file
        **kwargs: Fields to update (can include email, full_name, is_active, preferences)
        
    Returns:
        Updated User object if found, None otherwise
    """
    manager = UserManager(storage_path)
    return manager.update_user(user_id, **kwargs)


def delete_user(user_id: str, storage_path: str = None) -> bool:
    """
    Delete a user.
    
    Args:
        user_id: ID of the user to delete
        storage_path: Optional path to the user data storage file
        
    Returns:
        True if the user was deleted, False if not found
    """
    manager = UserManager(storage_path)
    return manager.delete_user(user_id)


def authenticate_user(username: str, password: str, storage_path: str = None) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: Username of the user to authenticate
        password: Plain text password to check
        storage_path: Optional path to the user data storage file
        
    Returns:
        User object if authentication successful, None otherwise
    """
    manager = UserManager(storage_path)
    return manager.authenticate_user(username, password)