"""
Main views for the URL Analyzer web interface.

This module contains the main blueprint with routes for the home page,
about page, and other general pages.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.exceptions import NotFound

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the home page."""
    return render_template('main/index.html', title='URL Analyzer')


@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('main/about.html', title='About URL Analyzer')


@main_bp.route('/help')
def help_page():
    """Render the help page."""
    return render_template('main/help.html', title='Help')


@main_bp.route('/contact')
def contact():
    """Render the contact page."""
    return render_template('main/contact.html', title='Contact')


@main_bp.route('/theme/<theme_name>')
def set_theme(theme_name):
    """
    Set the user's theme preference.
    
    Args:
        theme_name: Name of the theme to set
        
    Returns:
        Redirect to the previous page
    """
    # Validate theme
    if theme_name not in current_app.config['THEMES']:
        flash('Invalid theme selected.', 'error')
        return redirect(request.referrer or url_for('main.index'))
    
    # Set theme cookie and redirect
    response = redirect(request.referrer or url_for('main.index'))
    response.set_cookie('theme', theme_name, max_age=31536000)  # 1 year
    
    flash(f'Theme changed to {current_app.config["THEMES"][theme_name]}.', 'success')
    return response


@main_bp.route('/language/<lang_code>')
def set_language(lang_code):
    """
    Set the user's language preference.
    
    Args:
        lang_code: Language code to set
        
    Returns:
        Redirect to the previous page
    """
    # Validate language
    supported_languages = ['en', 'fr', 'es', 'de', 'zh', 'ja']
    if lang_code not in supported_languages:
        flash('Unsupported language selected.', 'error')
        return redirect(request.referrer or url_for('main.index'))
    
    # Set language cookie and redirect
    response = redirect(request.referrer or url_for('main.index'))
    response.set_cookie('locale', lang_code, max_age=31536000)  # 1 year
    
    # Get language name for the flash message
    language_names = {
        'en': 'English',
        'fr': 'Français',
        'es': 'Español',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語'
    }
    
    flash(f'Language changed to {language_names.get(lang_code, lang_code)}.', 'success')
    return response