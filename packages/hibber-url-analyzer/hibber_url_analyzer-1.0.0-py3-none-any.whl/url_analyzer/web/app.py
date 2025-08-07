"""
Flask application for URL Analyzer web interface.

This module provides the main Flask application factory and configuration
for the URL Analyzer web interface.
"""

import os
import logging
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from werkzeug.middleware.proxy_fix import ProxyFix

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)

# Initialize extensions
csrf = CSRFProtect()
babel = Babel()


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional configuration dictionary to override defaults
        
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        WTF_CSRF_ENABLED=True,
        BABEL_DEFAULT_LOCALE='en',
        BABEL_DEFAULT_TIMEZONE='UTC',
        THEMES={
            'default': 'Default',
            'dark': 'Dark Mode',
            'light': 'Light Mode',
            'high-contrast': 'High Contrast'
        },
        DEFAULT_THEME='default',
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB max upload size
    )
    
    # Override with provided configuration
    if config:
        app.config.from_mapping(config)
    
    # Define locale selector function
    def get_locale():
        """
        Select the locale for the current request.
        
        Returns:
            Locale code
        """
        # Try to get locale from query parameter
        locale = request.args.get('lang')
        if locale:
            return locale
        
        # Try to get locale from user preferences
        if hasattr(request, 'user') and hasattr(request.user, 'locale'):
            return request.user.locale
        
        # Try to get locale from cookie
        locale = request.cookies.get('locale')
        if locale:
            return locale
        
        # Fall back to accept-language header
        return request.accept_languages.best_match(['en', 'fr', 'es', 'de', 'zh', 'ja'])
    
    # Initialize extensions
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    
    # Fix for reverse proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    
    # Register blueprints
    from url_analyzer.web.views.main import main_bp
    from url_analyzer.web.views.analysis import analysis_bp
    from url_analyzer.web.views.reports import reports_bp
    from url_analyzer.web.views.settings import settings_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Initialize authentication system
    from url_analyzer.web.auth import init_auth, register_auth_template_functions
    init_auth(app)
    register_auth_template_functions(app)
    
    # Log application startup
    logger.info("URL Analyzer web interface initialized")
    
    return app


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application
    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(413)
    def request_entity_too_large(e):
        flash('The file is too large. Maximum size is 16MB.', 'error')
        return redirect(request.referrer or url_for('main.index'))


def register_context_processors(app: Flask) -> None:
    """
    Register context processors for the application.
    
    Args:
        app: Flask application
    """
    @app.context_processor
    def inject_theme():
        """Inject the current theme into templates."""
        theme = request.cookies.get('theme', app.config['DEFAULT_THEME'])
        if theme not in app.config['THEMES']:
            theme = app.config['DEFAULT_THEME']
        return {'current_theme': theme, 'available_themes': app.config['THEMES']}
    
    @app.context_processor
    def inject_version():
        """Inject the application version into templates."""
        try:
            # Try to get version from package metadata
            import importlib.metadata
            version = importlib.metadata.version('url-analyzer')
        except (ImportError, importlib.metadata.PackageNotFoundError):
            # Fallback to hardcoded version if package not installed
            version = '1.0.0'
        return {'version': version}


def register_template_filters(app: Flask) -> None:
    """
    Register custom template filters for the application.
    
    Args:
        app: Flask application
    """
    @app.template_filter('format_date')
    def format_date_filter(value, format='%Y-%m-%d'):
        """Format a date using the given format."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('truncate_url')
    def truncate_url_filter(url, length=50):
        """Truncate a URL to the given length."""
        if not url or len(url) <= length:
            return url
        return url[:length-3] + '...'


def register_cli_commands(app: Flask) -> None:
    """
    Register CLI commands for the application.
    
    Args:
        app: Flask application
    """
    @app.cli.command('create-demo-data')
    def create_demo_data():
        """Create demo data for development."""
        # TODO: Implement demo data creation
        print("Demo data created.")
    
    @app.cli.command('compile-translations')
    def compile_translations():
        """Compile translation files."""
        # TODO: Implement translation compilation
        print("Translations compiled.")




if __name__ == '__main__':
    # This is used when running the application directly for development
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)