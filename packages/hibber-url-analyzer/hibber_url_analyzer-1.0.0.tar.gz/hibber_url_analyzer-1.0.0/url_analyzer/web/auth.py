"""
Authentication Module for URL Analyzer Web Interface

This module provides authentication functionality including user management,
login/logout, session handling, and security features.
"""

import os
import hashlib
import secrets
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Tuple
from functools import wraps

from flask import request, session, redirect, url_for, flash, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

# Try to import Flask-Login for enhanced features, but provide fallback
try:
    from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
    FLASK_LOGIN_AVAILABLE = True
except ImportError:
    FLASK_LOGIN_AVAILABLE = False
    # Provide simple fallbacks
    class UserMixin:
        pass
    
    def is_authenticated():
        """Check if user is authenticated."""
        return 'user_id' in session
    
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Please log in to access this page.', 'info')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def login_user(user, remember=False):
        """Simple login function fallback."""
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = remember
        return True
    
    def logout_user():
        """Simple logout function fallback."""
        session.pop('user_id', None)
        session.pop('username', None)
        return True
    
    class CurrentUserProxy:
        """Simple current user proxy."""
        @property
        def is_authenticated(self):
            return 'user_id' in session
        
        @property
        def username(self):
            return session.get('username')
        
        @property
        def id(self):
            return session.get('user_id')
        
        def is_admin(self):
            if self.is_authenticated:
                user = user_manager.get_user(self.id)
                return user and user.is_admin()
            return False
    
    current_user = CurrentUserProxy()

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


class User(UserMixin):
    """User class for authentication."""
    
    def __init__(self, user_id: str, username: str, email: str, password_hash: str,
                 role: str = 'user', created_at: Optional[datetime] = None,
                 last_login: Optional[datetime] = None, is_active: bool = True,
                 failed_login_attempts: int = 0, locked_until: Optional[datetime] = None):
        """
        Initialize a user.
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: User email
            password_hash: Hashed password
            role: User role (admin, user)
            created_at: Account creation timestamp
            last_login: Last login timestamp
            is_active: Whether the account is active
            failed_login_attempts: Number of failed login attempts
            locked_until: Account lock expiration time
        """
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.is_active = is_active
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self.role == 'admin'
    
    def is_locked(self) -> bool:
        """Check if the account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def get_id(self) -> str:
        """Return the user ID as required by Flask-Login."""
        return self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for storage."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        return cls(
            user_id=data['id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'user'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            last_login=datetime.fromisoformat(data['last_login']) if data.get('last_login') else None,
            is_active=data.get('is_active', True),
            failed_login_attempts=data.get('failed_login_attempts', 0),
            locked_until=datetime.fromisoformat(data['locked_until']) if data.get('locked_until') else None
        )


class UserManager:
    """Manages user storage and operations."""
    
    def __init__(self, users_file: str = 'users.json'):
        """
        Initialize the user manager.
        
        Args:
            users_file: Path to the users storage file
        """
        self.users_file = users_file
        self.users: Dict[str, User] = {}
        self.load_users()
        
        # Create default admin user if no users exist
        if not self.users:
            self.create_default_admin()
    
    def load_users(self) -> None:
        """Load users from storage file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = User.from_dict(user_data)
                        self.users[user.id] = user
                logger.info(f"Loaded {len(self.users)} users from {self.users_file}")
            except Exception as e:
                logger.error(f"Error loading users: {e}")
    
    def save_users(self) -> None:
        """Save users to storage file."""
        try:
            users_data = [user.to_dict() for user in self.users.values()]
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            logger.debug(f"Saved {len(self.users)} users to {self.users_file}")
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def create_default_admin(self) -> None:
        """Create a default admin user."""
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_user = self.create_user(
            username='admin',
            email='admin@localhost',
            password=admin_password,
            role='admin'
        )
        logger.warning(f"Created default admin user with password: {admin_password}")
        logger.warning("Please change the admin password immediately!")
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            email: User email
            password: Plain text password
            role: User role
            
        Returns:
            Created user
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username:
                raise ValueError(f"Username '{username}' already exists")
            if user.email == email:
                raise ValueError(f"Email '{email}' already exists")
        
        # Generate user ID and hash password
        user_id = secrets.token_urlsafe(16)
        password_hash = generate_password_hash(password)
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        # Store user
        self.users[user_id] = user
        self.save_users()
        
        logger.info(f"Created user: {username} ({email})")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            username: Username or email
            password: Password
            
        Returns:
            User if authentication successful, None otherwise
        """
        # Find user by username or email
        user = self.get_user_by_username(username) or self.get_user_by_email(username)
        
        if not user:
            logger.warning(f"Authentication failed: user not found: {username}")
            return None
        
        # Check if account is locked
        if user.is_locked():
            logger.warning(f"Authentication failed: account locked: {username}")
            return None
        
        # Check if account is active
        if not user.is_active:
            logger.warning(f"Authentication failed: account inactive: {username}")
            return None
        
        # Check password
        if user.check_password(password):
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            user.locked_until = None
            self.save_users()
            
            logger.info(f"User authenticated successfully: {username}")
            return user
        else:
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                logger.warning(f"Account locked due to failed login attempts: {username}")
            
            self.save_users()
            logger.warning(f"Authentication failed: incorrect password: {username}")
            return None
    
    def update_user(self, user: User) -> None:
        """Update user information."""
        self.users[user.id] = user
        self.save_users()
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if user_id in self.users:
            username = self.users[user_id].username
            del self.users[user_id]
            self.save_users()
            logger.info(f"Deleted user: {username}")
            return True
        return False
    
    def list_users(self) -> List[User]:
        """Get list of all users."""
        return list(self.users.values())


# Global user manager instance
user_manager = UserManager()


def init_auth(app):
    """Initialize authentication for the Flask app."""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return user_manager.get_user(user_id)
    
    # Register security headers middleware
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)
    
    # Register authentication blueprint
    from url_analyzer.web.views.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Register template functions
    register_auth_template_functions(app)
    
    logger.info("Authentication system initialized with enhanced security features")


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def rate_limit_login(max_attempts: int = 10, window_minutes: int = 15):
    """Rate limiting decorator for login attempts."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Check rate limit (simplified implementation)
            # In production, use Redis or similar for distributed rate limiting
            session_key = f'login_attempts_{client_ip}'
            attempts = session.get(session_key, [])
            
            # Clean old attempts
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            attempts = [attempt for attempt in attempts if datetime.fromisoformat(attempt) > cutoff_time]
            
            # Check if rate limit exceeded
            if len(attempts) >= max_attempts:
                flash(f'Too many login attempts. Please try again in {window_minutes} minutes.', 'error')
                return redirect(url_for('auth.login'))
            
            # Record this attempt
            attempts.append(datetime.utcnow().isoformat())
            session[session_key] = attempts
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_csrf_token():
    """Generate CSRF token for forms."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return session['_csrf_token']


def validate_csrf_token(token):
    """Validate CSRF token."""
    return token == session.get('_csrf_token')


def validate_password_strength(password: str) -> Tuple[bool, List[str], int]:
    """
    Validate password strength and return detailed feedback.
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, error_messages, strength_score)
        strength_score: 0-100 indicating password strength
    """
    errors = []
    score = 0
    
    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15
    
    # Character type checks
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not has_lower:
        errors.append("Password must contain at least one lowercase letter")
    else:
        score += 15
        
    if not has_upper:
        errors.append("Password must contain at least one uppercase letter")
    else:
        score += 15
        
    if not has_digit:
        errors.append("Password must contain at least one number")
    else:
        score += 15
        
    if not has_special:
        errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
    else:
        score += 20
    
    # Additional strength checks
    if len(set(password)) >= len(password) * 0.7:  # Good character diversity
        score += 10
    
    # Common patterns check
    common_patterns = [
        r'123456', r'password', r'qwerty', r'abc123', r'admin',
        r'(.)\1{2,}',  # Repeated characters
        r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
        r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)'  # Sequential letters
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            errors.append("Password contains common patterns or sequences")
            score = max(0, score - 20)
            break
    
    is_valid = len(errors) == 0
    return is_valid, errors, min(100, score)


def check_session_timeout(timeout_minutes: int = 30) -> bool:
    """
    Check if the current session has timed out.
    
    Args:
        timeout_minutes: Session timeout in minutes
        
    Returns:
        True if session is valid, False if timed out
    """
    if 'last_activity' not in session:
        session['last_activity'] = datetime.utcnow().isoformat()
        return True
    
    try:
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.utcnow() - last_activity > timedelta(minutes=timeout_minutes):
            # Session timed out
            session.clear()
            return False
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        return True
    except (ValueError, TypeError):
        # Invalid timestamp, clear session
        session.clear()
        return False


def session_timeout_required(timeout_minutes: int = 30):
    """
    Decorator to enforce session timeout on protected routes.
    
    Args:
        timeout_minutes: Session timeout in minutes
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and not check_session_timeout(timeout_minutes):
                flash('Your session has expired. Please log in again.', 'warning')
                logout_user()
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def add_security_headers(response):
    """
    Add security headers to HTTP responses.
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response with security headers
    """
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Strict transport security (HTTPS only)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions policy
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "gyroscope=(), "
        "speaker=()"
    )
    
    return response


# Make functions available in templates
def register_auth_template_functions(app):
    """Register authentication-related template functions."""
    @app.template_global()
    def csrf_token():
        return generate_csrf_token()
    
    @app.template_global()
    def current_user_info():
        if current_user.is_authenticated:
            return {
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'is_admin': current_user.is_admin()
            }
        return None