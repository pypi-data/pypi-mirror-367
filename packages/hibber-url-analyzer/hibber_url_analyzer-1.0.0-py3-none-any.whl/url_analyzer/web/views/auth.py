"""
Authentication Views for URL Analyzer Web Interface

This module provides authentication-related routes including login, logout,
user registration, and user management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash

from url_analyzer.web.auth import (
    user_manager, login_user, logout_user, login_required, current_user,
    admin_required, rate_limit_login, generate_csrf_token, validate_csrf_token,
    validate_password_strength, session_timeout_required
)
from url_analyzer.utils.logging import get_logger
from url_analyzer.collaboration.audit import log_activity

logger = get_logger(__name__)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit_login(max_attempts=10, window_minutes=15)
def login():
    """Login page and handler."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        csrf_token = request.form.get('csrf_token', '')
        
        # Validate CSRF token
        if not validate_csrf_token(csrf_token):
            flash('Invalid security token. Please try again.', 'error')
            return render_template('auth/login.html')
        
        # Validate input
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = user_manager.authenticate_user(username, password)
        if user:
            # Log in the user
            login_user(user, remember=bool(remember))
            
            # Audit log successful login
            log_activity(
                user_id=user.id,
                action="login",
                resource_type="authentication",
                resource_id=user.username,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                details={"remember": bool(remember)},
                status="success"
            )
            
            # Get next page from query parameter
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            # Audit log failed login attempt
            log_activity(
                user_id="unknown",
                action="login_failed",
                resource_type="authentication",
                resource_id=username,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                details={"attempted_username": username},
                status="failure"
            )
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Logout handler."""
    if current_user.is_authenticated:
        username = current_user.username
        user_id = current_user.id
        
        # Audit log logout
        log_activity(
            user_id=user_id,
            action="logout",
            resource_type="authentication",
            resource_id=username,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            status="success"
        )
        
        logout_user()
        flash(f'You have been logged out, {username}.', 'info')
    
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        csrf_token = request.form.get('csrf_token', '')
        
        # Validate CSRF token
        if not validate_csrf_token(csrf_token):
            flash('Invalid security token. Please try again.', 'error')
            return render_template('auth/register.html')
        
        # Validate input
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        # Enhanced password validation
        if not password:
            errors.append('Password is required.')
        else:
            is_valid, password_errors, strength_score = validate_password_strength(password)
            if not is_valid:
                errors.extend(password_errors)
            elif strength_score < 60:
                errors.append(f'Password strength is too weak (score: {strength_score}/100). Please use a stronger password.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create user
        try:
            user = user_manager.create_user(username, email, password)
            
            # Audit log successful registration
            log_activity(
                user_id=user.id,
                action="register",
                resource_type="user_account",
                resource_id=username,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                details={"email": email, "username": username},
                status="success"
            )
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            # Audit log failed registration
            log_activity(
                user_id="unknown",
                action="register_failed",
                resource_type="user_account",
                resource_id=username,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                details={"email": email, "username": username, "error": str(e)},
                status="failure"
            )
            flash(str(e), 'error')
    
    return render_template('auth/register.html')


@auth_bp.route('/profile')
@login_required
@session_timeout_required(timeout_minutes=30)
def profile():
    """User profile page."""
    user = user_manager.get_user(current_user.id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('auth/profile.html', user=user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@session_timeout_required(timeout_minutes=30)
def change_password():
    """Change password page and handler."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        csrf_token = request.form.get('csrf_token', '')
        
        # Validate CSRF token
        if not validate_csrf_token(csrf_token):
            flash('Invalid security token. Please try again.', 'error')
            return render_template('auth/change_password.html')
        
        # Get current user
        user = user_manager.get_user(current_user.id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('main.index'))
        
        # Validate input
        errors = []
        if not current_password:
            errors.append('Please enter your current password.')
        elif not user.check_password(current_password):
            errors.append('Current password is incorrect.')
        
        # Enhanced password validation
        if not new_password:
            errors.append('New password is required.')
        else:
            is_valid, password_errors, strength_score = validate_password_strength(new_password)
            if not is_valid:
                errors.extend(password_errors)
            elif strength_score < 60:
                errors.append(f'Password strength is too weak (score: {strength_score}/100). Please use a stronger password.')
        
        if new_password != confirm_password:
            errors.append('New passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(new_password)
        user_manager.update_user(user)
        
        # Audit log password change
        log_activity(
            user_id=user.id,
            action="password_change",
            resource_type="user_account",
            resource_id=user.username,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            details={"username": user.username},
            status="success"
        )
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')


@auth_bp.route('/users')
@admin_required
@session_timeout_required(timeout_minutes=30)
def list_users():
    """List all users (admin only)."""
    users = user_manager.list_users()
    return render_template('auth/users.html', users=users)


@auth_bp.route('/users/<user_id>/toggle-active', methods=['POST'])
@admin_required
@session_timeout_required(timeout_minutes=30)
def toggle_user_active(user_id):
    """Toggle user active status (admin only)."""
    csrf_token = request.form.get('csrf_token', '')
    
    # Validate CSRF token
    if not validate_csrf_token(csrf_token):
        flash('Invalid security token.', 'error')
        return redirect(url_for('auth.list_users'))
    
    user = user_manager.get_user(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.list_users'))
    
    # Don't allow deactivating the current admin user
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('auth.list_users'))
    
    old_status = user.is_active
    user.is_active = not user.is_active
    user_manager.update_user(user)
    
    status = 'activated' if user.is_active else 'deactivated'
    
    # Audit log user status change
    log_activity(
        user_id=current_user.id,
        action="user_status_change",
        resource_type="user_account",
        resource_id=user.username,
        ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
        details={
            "target_user": user.username,
            "target_user_id": user.id,
            "old_status": "active" if old_status else "inactive",
            "new_status": "active" if user.is_active else "inactive",
            "admin_user": current_user.username
        },
        status="success"
    )
    
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('auth.list_users'))


@auth_bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
@session_timeout_required(timeout_minutes=30)
def delete_user(user_id):
    """Delete a user (admin only)."""
    csrf_token = request.form.get('csrf_token', '')
    
    # Validate CSRF token
    if not validate_csrf_token(csrf_token):
        flash('Invalid security token.', 'error')
        return redirect(url_for('auth.list_users'))
    
    user = user_manager.get_user(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.list_users'))
    
    # Don't allow deleting the current admin user
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('auth.list_users'))
    
    # Store user details for audit log before deletion
    username = user.username
    user_email = user.email
    
    if user_manager.delete_user(user_id):
        # Audit log user deletion
        log_activity(
            user_id=current_user.id,
            action="user_delete",
            resource_type="user_account",
            resource_id=username,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            details={
                "deleted_user": username,
                "deleted_user_id": user_id,
                "deleted_user_email": user_email,
                "admin_user": current_user.username
            },
            status="success"
        )
        flash(f'User {username} has been deleted.', 'success')
    else:
        # Audit log failed deletion attempt
        log_activity(
            user_id=current_user.id,
            action="user_delete_failed",
            resource_type="user_account",
            resource_id=username,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            details={
                "target_user": username,
                "target_user_id": user_id,
                "admin_user": current_user.username,
                "error": "Failed to delete user"
            },
            status="failure"
        )
        flash('Failed to delete user.', 'error')
    
    return redirect(url_for('auth.list_users'))


@auth_bp.route('/api/check-auth')
def check_auth():
    """API endpoint to check authentication status."""
    if current_user.is_authenticated:
        user = user_manager.get_user(current_user.id)
        return jsonify({
            'authenticated': True,
            'username': user.username if user else 'Unknown',
            'role': user.role if user else 'user',
            'is_admin': user.is_admin() if user else False
        })
    else:
        return jsonify({'authenticated': False})


@auth_bp.route('/api/csrf-token')
def get_csrf_token():
    """API endpoint to get CSRF token."""
    return jsonify({'csrf_token': generate_csrf_token()})


# Context processor to make authentication info available in templates
@auth_bp.app_context_processor
def inject_auth():
    """Inject authentication information into template context."""
    auth_info = {
        'current_user': current_user,
        'csrf_token': generate_csrf_token()
    }
    
    if current_user.is_authenticated:
        user = user_manager.get_user(current_user.id)
        if user:
            auth_info.update({
                'user': user,
                'is_admin': user.is_admin()
            })
    
    return auth_info