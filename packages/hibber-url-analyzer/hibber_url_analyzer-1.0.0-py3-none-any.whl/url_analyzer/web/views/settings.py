"""
Settings views for the URL Analyzer web interface.

This module contains the settings blueprint with routes for configuring
application settings, user preferences, and system configuration.
"""

import os
import json
from typing import Dict, Any, Optional

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.exceptions import BadRequest

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.validation import validate_string, validate_integer, validate_url, validate_json
from url_analyzer.utils.errors import ValidationError
from url_analyzer.utils.sanitization import sanitize_filename
from url_analyzer.config_manager import load_config, save_config, validate_config

logger = get_logger(__name__)

# Create blueprint
settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
def index():
    """Render the settings home page."""
    return render_template('settings/index.html', title='Settings')


@settings_bp.route('/application', methods=['GET', 'POST'])
def application():
    """
    Manage application settings.
    
    GET: Show the application settings form
    POST: Update application settings
    """
    # Get the configuration file path
    config_path = current_app.config.get('CONFIG_PATH', os.path.join(current_app.root_path, '..', '..', 'config.json'))
    
    if request.method == 'POST':
        try:
            # Get and validate form data
            sensitive_patterns_str = request.form.get('sensitive_patterns', '').strip()
            ugc_patterns_str = request.form.get('ugc_patterns', '').strip()
            junk_subcategories_str = request.form.get('junk_subcategories', '').strip()
            api_url = request.form.get('api_url', '').strip()
            max_workers_str = request.form.get('max_workers', '20')
            timeout_str = request.form.get('timeout', '7')
            cache_file = request.form.get('cache_file', 'scan_cache.json').strip()
            
            # Validate API URL if provided
            if api_url:
                validate_url(api_url, error_message="Please enter a valid API URL")
            
            # Validate and convert numeric parameters
            validate_integer(int(max_workers_str), min_value=1, max_value=100, 
                           error_message="Max workers must be between 1 and 100")
            max_workers = int(max_workers_str)
            
            validate_integer(int(timeout_str), min_value=1, max_value=300,
                           error_message="Timeout must be between 1 and 300 seconds")
            timeout = int(timeout_str)
            
            # Validate cache file name
            validate_string(cache_file, min_length=1, max_length=100,
                          pattern=r'^[a-zA-Z0-9_\-\.]+$',
                          error_message="Cache file name must contain only letters, numbers, underscores, hyphens, and periods")
            cache_file = sanitize_filename(cache_file)
            
            # Validate JSON format for junk subcategories
            if junk_subcategories_str:
                validate_json(junk_subcategories_str, error_message="Invalid JSON format for junk subcategories")
                junk_subcategories = json.loads(junk_subcategories_str)
            else:
                junk_subcategories = {}
            
            # Process pattern lists
            sensitive_patterns = [p.strip() for p in sensitive_patterns_str.split('\n') if p.strip()]
            ugc_patterns = [p.strip() for p in ugc_patterns_str.split('\n') if p.strip()]
            
            # Validate pattern lists (basic regex validation)
            for pattern in sensitive_patterns + ugc_patterns:
                validate_string(pattern, min_length=1, max_length=200,
                              error_message=f"Pattern '{pattern}' is too long (max 200 characters)")
        
        except (ValueError, ValidationError) as e:
            logger.warning(f"Settings validation error: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('settings.application'))
        
        try:
            
            # Create the updated configuration
            config = {
                "sensitive_patterns": sensitive_patterns,
                "ugc_patterns": ugc_patterns,
                "junk_subcategories": junk_subcategories,
                "api_settings": {
                    "gemini_api_url": api_url
                },
                "scan_settings": {
                    "max_workers": max_workers,
                    "timeout": timeout,
                    "cache_file": cache_file
                }
            }
            
            # Validate the configuration
            if not validate_config(config):
                flash('Invalid configuration format.', 'error')
                return redirect(url_for('settings.application'))
            
            # Save the configuration
            save_config(config, config_path)
            
            flash('Application settings updated successfully.', 'success')
            return redirect(url_for('settings.application'))
            
        except Exception as e:
            logger.error(f"Error updating application settings: {str(e)}")
            flash(f'Error updating settings: {str(e)}', 'error')
            return redirect(url_for('settings.application'))
    
    # GET request - show the form
    try:
        # Load the current configuration
        config = load_config(config_path)
        
        # Prepare the form data
        sensitive_patterns = '\n'.join(config.get('sensitive_patterns', []))
        ugc_patterns = '\n'.join(config.get('ugc_patterns', []))
        junk_subcategories = json.dumps(config.get('junk_subcategories', {}), indent=2)
        
        api_settings = config.get('api_settings', {})
        api_url = api_settings.get('gemini_api_url', '')
        
        scan_settings = config.get('scan_settings', {})
        max_workers = scan_settings.get('max_workers', 20)
        timeout = scan_settings.get('timeout', 7)
        cache_file = scan_settings.get('cache_file', 'scan_cache.json')
        
        return render_template(
            'settings/application.html',
            title='Application Settings',
            sensitive_patterns=sensitive_patterns,
            ugc_patterns=ugc_patterns,
            junk_subcategories=junk_subcategories,
            api_url=api_url,
            max_workers=max_workers,
            timeout=timeout,
            cache_file=cache_file
        )
        
    except Exception as e:
        logger.error(f"Error loading application settings: {str(e)}")
        flash(f'Error loading settings: {str(e)}', 'error')
        return render_template('settings/application.html', title='Application Settings')


@settings_bp.route('/user')
def user():
    """Manage user preferences."""
    # Get current user preferences from cookies
    theme = request.cookies.get('theme', current_app.config.get('DEFAULT_THEME', 'default'))
    locale = request.cookies.get('locale', 'en')
    
    # Get available themes
    themes = current_app.config.get('THEMES', {
        'default': 'Default',
        'dark': 'Dark Mode',
        'light': 'Light Mode',
        'high-contrast': 'High Contrast'
    })
    
    # Get available languages
    languages = {
        'en': 'English',
        'fr': 'Français',
        'es': 'Español',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語'
    }
    
    return render_template(
        'settings/user.html',
        title='User Preferences',
        current_theme=theme,
        available_themes=themes,
        current_locale=locale,
        available_languages=languages
    )


@settings_bp.route('/system')
def system():
    """View system information."""
    # Get system information
    import platform
    import sys
    import pandas as pd
    import numpy as np
    
    # Python information
    python_info = {
        'version': platform.python_version(),
        'implementation': platform.python_implementation(),
        'compiler': platform.python_compiler(),
        'build': platform.python_build(),
        'path': sys.executable
    }
    
    # Platform information
    platform_info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }
    
    # Package information
    package_info = {
        'pandas': pd.__version__,
        'numpy': np.__version__,
        'flask': current_app.version if hasattr(current_app, 'version') else 'Unknown'
    }
    
    # Try to get additional package versions
    try:
        import plotly
        package_info['plotly'] = plotly.__version__
    except ImportError:
        package_info['plotly'] = 'Not installed'
    
    try:
        import jinja2
        package_info['jinja2'] = jinja2.__version__
    except ImportError:
        package_info['jinja2'] = 'Not installed'
    
    try:
        import werkzeug
        package_info['werkzeug'] = werkzeug.__version__
    except ImportError:
        package_info['werkzeug'] = 'Not installed'
    
    # Application information
    try:
        # Try to get version from package metadata
        import importlib.metadata
        version = importlib.metadata.version('url-analyzer')
    except (ImportError, importlib.metadata.PackageNotFoundError):
        # Fallback to hardcoded version if package not installed
        version = '1.0.0'
    
    app_info = {
        'name': 'URL Analyzer',
        'version': version,
        'environment': current_app.env,
        'debug': current_app.debug,
        'config_path': current_app.config.get('CONFIG_PATH', 'Unknown')
    }
    
    return render_template(
        'settings/system.html',
        title='System Information',
        python_info=python_info,
        platform_info=platform_info,
        package_info=package_info,
        app_info=app_info
    )


@settings_bp.route('/accessibility')
def accessibility():
    """Manage accessibility settings."""
    # Get current accessibility settings from cookies
    font_size = request.cookies.get('font_size', 'medium')
    contrast = request.cookies.get('contrast', 'normal')
    animations = request.cookies.get('animations', 'enabled')
    
    return render_template(
        'settings/accessibility.html',
        title='Accessibility Settings',
        font_size=font_size,
        contrast=contrast,
        animations=animations
    )


@settings_bp.route('/accessibility/update', methods=['POST'])
def update_accessibility():
    """Update accessibility settings."""
    try:
        # Get form data
        font_size = request.form.get('font_size', 'medium')
        contrast = request.form.get('contrast', 'normal')
        animations = request.form.get('animations', 'enabled')
        
        # Validate settings
        valid_font_sizes = ['small', 'medium', 'large', 'x-large']
        valid_contrasts = ['normal', 'high', 'very-high']
        valid_animations = ['enabled', 'reduced', 'disabled']
        
        if font_size not in valid_font_sizes:
            font_size = 'medium'
        
        if contrast not in valid_contrasts:
            contrast = 'normal'
        
        if animations not in valid_animations:
            animations = 'enabled'
        
        # Set cookies and redirect
        response = redirect(url_for('settings.accessibility'))
        response.set_cookie('font_size', font_size, max_age=31536000)  # 1 year
        response.set_cookie('contrast', contrast, max_age=31536000)
        response.set_cookie('animations', animations, max_age=31536000)
        
        flash('Accessibility settings updated successfully.', 'success')
        return response
        
    except Exception as e:
        logger.error(f"Error updating accessibility settings: {str(e)}")
        flash(f'Error updating settings: {str(e)}', 'error')
        return redirect(url_for('settings.accessibility'))


@settings_bp.route('/reset', methods=['POST'])
def reset_settings():
    """Reset all settings to defaults."""
    try:
        # Reset cookies
        response = redirect(url_for('settings.index'))
        response.delete_cookie('theme')
        response.delete_cookie('locale')
        response.delete_cookie('font_size')
        response.delete_cookie('contrast')
        response.delete_cookie('animations')
        
        flash('All settings have been reset to defaults.', 'success')
        return response
        
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        flash(f'Error resetting settings: {str(e)}', 'error')
        return redirect(url_for('settings.index'))