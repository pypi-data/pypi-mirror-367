"""
Application Service Facade for URL Analyzer.

This module provides a high-level facade that provides a simple interface 
for the CLI and other clients, reducing coupling to implementation details.
This facade works with the existing codebase structure.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import os

# Import only what we know exists
from url_analyzer.config_manager import load_config, save_config


class ApplicationService:
    """
    High-level application service that provides a facade over existing functionality.
    
    This service reduces coupling between the CLI and the implementation details
    by providing a simple, stable interface for common operations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the application service.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path or "config.json"
        self._config = None
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        if self._config is None:
            self._config = load_config(self.config_path)
        return self._config
    
    def save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save configuration.
        
        Args:
            config: Configuration to save
            
        Returns:
            Operation result
        """
        save_config(config, self.config_path)
        self._config = config  # Update cached config
        return {'status': 'success', 'message': 'Configuration saved'}
    
    def classify_single_url(self, url: str) -> Dict[str, Any]:
        """
        Classify a single URL using available classification functions.
        
        Args:
            url: URL to classify
            
        Returns:
            Classification result
        """
        try:
            # Import here to avoid import errors at module level
            from url_analyzer.core.classification import classify_url, compile_patterns
            
            config = self.get_config()
            patterns = compile_patterns(config)
            category, is_sensitive = classify_url(url, patterns)
            
            return {
                'url': url,
                'category': category,
                'is_sensitive': is_sensitive,
                'status': 'success'
            }
        except Exception as e:
            return {
                'url': url,
                'category': 'Error',
                'is_sensitive': False,
                'status': 'error',
                'error': str(e)
            }
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process URLs from a file.
        
        Args:
            file_path: Path to file containing URLs
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Import here to avoid import errors at module level
            from url_analyzer.data.processing import process_file
            
            if not os.path.exists(file_path):
                return {
                    'file_path': file_path,
                    'status': 'error',
                    'message': f'File not found: {file_path}'
                }
            
            # Use the existing process_file function
            result = process_file(file_path, self.get_config())
            
            return {
                'file_path': file_path,
                'status': 'success',
                'processed_count': len(result) if result else 0,
                'results': result
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'status': 'error',
                'message': f'Error processing file: {str(e)}'
            }
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available report templates.
        
        Returns:
            List of template names
        """
        try:
            # Import here to avoid import errors at module level
            from url_analyzer.reporting.html_report import list_available_templates
            return list_available_templates()
        except Exception as e:
            # Return default templates if import fails
            return ['default', 'detailed', 'summary']
    
    def export_data(
        self, 
        data: Any, 
        output_path: str, 
        format: str = 'csv'
    ) -> Dict[str, Any]:
        """
        Export data to various formats.
        
        Args:
            data: Data to export
            output_path: Output file path
            format: Export format
            
        Returns:
            Dictionary containing export results
        """
        try:
            # Import here to avoid import errors at module level
            from url_analyzer.data.export import export_data
            
            export_data(data, output_path, format)
            
            return {
                'output_path': output_path,
                'format': format,
                'status': 'success',
                'message': f'Data exported to {output_path}'
            }
        except Exception as e:
            return {
                'output_path': output_path,
                'format': format,
                'status': 'error',
                'message': f'Export failed: {str(e)}'
            }


def create_application_service(config_path: Optional[str] = None) -> ApplicationService:
    """
    Factory function to create a configured ApplicationService.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configured ApplicationService instance
    """
    return ApplicationService(config_path)