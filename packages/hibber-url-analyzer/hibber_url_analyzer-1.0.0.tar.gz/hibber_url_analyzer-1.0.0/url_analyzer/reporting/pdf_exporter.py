"""
PDF export functionality for URL Analyzer reports.

This module provides functionality to export URL analysis reports to PDF format
with customizable templates and styling.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import tempfile

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

from url_analyzer.utils.logging import get_logger
from url_analyzer.reporting.report_builder import ReportBuilder

logger = get_logger(__name__)

class PDFExporter:
    """
    Handles the export of URL analysis data to PDF format.
    
    This class provides functionality to generate PDF reports from URL analysis data
    using customizable templates and styling.
    """
    
    def __init__(self, template_dir: Optional[str] = None, static_dir: Optional[str] = None):
        """
        Initialize the PDF exporter.
        
        Args:
            template_dir: Directory containing PDF templates. If None, uses default templates.
            static_dir: Directory containing static assets (CSS, images). If None, uses default assets.
        """
        # Use default directories if not specified
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = template_dir or os.path.join(base_dir, 'templates', 'pdf')
        self.static_dir = static_dir or os.path.join(base_dir, 'static')
        
        # Set up Jinja environment for templates
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        
        # Register custom filters
        self._register_filters()
        
        logger.debug(f"Initialized PDFExporter with template_dir={self.template_dir}, static_dir={self.static_dir}")
    
    def _register_filters(self) -> None:
        """Register custom Jinja filters for PDF templates."""
        # Format date filter
        def format_date(value, format_str='%Y-%m-%d'):
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    return value
            if isinstance(value, datetime):
                return value.strftime(format_str)
            return value
        
        # Truncate URL filter
        def truncate_url(url, length=50):
            if not url or len(url) <= length:
                return url
            return url[:length-3] + '...'
        
        # Register filters
        self.env.filters['format_date'] = format_date
        self.env.filters['truncate_url'] = truncate_url
    
    def export_to_pdf(self, 
                      data: Dict[str, Any], 
                      output_path: str, 
                      template_name: str = 'standard_report.html',
                      css_files: Optional[List[str]] = None,
                      title: Optional[str] = None,
                      metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Export analysis data to a PDF file.
        
        Args:
            data: Dictionary containing the analysis data
            output_path: Path where the PDF file will be saved
            template_name: Name of the template to use
            css_files: List of CSS files to apply (relative to static_dir/css)
            title: Title for the PDF document
            metadata: Additional metadata for the PDF document
            
        Returns:
            Path to the generated PDF file
            
        Raises:
            FileNotFoundError: If template or CSS files are not found
            ValueError: If data is invalid
            IOError: If there's an error writing the PDF file
        """
        try:
            # Prepare template data
            template_data = data.copy()
            template_data['title'] = title or 'URL Analysis Report'
            template_data['generated_at'] = datetime.now()
            
            # Render HTML from template
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html_path = temp_html.name
                temp_html.write(html_content.encode('utf-8'))
            
            # Prepare CSS files
            stylesheets = []
            if css_files:
                for css_file in css_files:
                    css_path = os.path.join(self.static_dir, 'css', css_file)
                    if os.path.exists(css_path):
                        stylesheets.append(CSS(filename=css_path))
                    else:
                        logger.warning(f"CSS file not found: {css_path}")
            
            # Add default CSS if no custom CSS provided
            if not stylesheets:
                default_css = os.path.join(self.static_dir, 'css', 'pdf_report.css')
                if os.path.exists(default_css):
                    stylesheets.append(CSS(filename=default_css))
            
            # Prepare metadata
            pdf_metadata = {
                'title': title or 'URL Analysis Report',
                'creator': 'URL Analyzer',
                'created': datetime.now().isoformat(),
            }
            if metadata:
                pdf_metadata.update(metadata)
            
            # Generate PDF
            html = HTML(filename=temp_html_path)
            html.write_pdf(
                output_path,
                stylesheets=stylesheets,
                presentational_hints=True,
                metadata=pdf_metadata
            )
            
            # Clean up temporary file
            os.unlink(temp_html_path)
            
            logger.info(f"PDF report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
            raise
    
    def export_from_report_builder(self, 
                                  report_builder: ReportBuilder, 
                                  output_path: str,
                                  template_name: Optional[str] = None,
                                  css_files: Optional[List[str]] = None) -> str:
        """
        Export a report directly from a ReportBuilder instance.
        
        Args:
            report_builder: ReportBuilder instance containing the report data
            output_path: Path where the PDF file will be saved
            template_name: Name of the template to use (if None, uses the template from report_builder)
            css_files: List of CSS files to apply (if None, uses default CSS)
            
        Returns:
            Path to the generated PDF file
        """
        # Get report data from builder
        report_data = report_builder.get_report_data()
        
        # Use template from builder if not specified
        template = template_name or report_builder.template_name or 'standard_report.html'
        
        # Get report title and metadata
        title = report_data.get('title', 'URL Analysis Report')
        metadata = {
            'report_id': str(report_data.get('report_id', '')),
            'author': report_data.get('author', 'URL Analyzer'),
            'keywords': ', '.join(report_data.get('tags', [])),
        }
        
        # Export to PDF
        return self.export_to_pdf(
            data=report_data,
            output_path=output_path,
            template_name=template,
            css_files=css_files,
            title=title,
            metadata=metadata
        )


def generate_pdf_report(data: Dict[str, Any], 
                        output_path: str, 
                        template: Optional[str] = None,
                        css_files: Optional[List[str]] = None,
                        title: Optional[str] = None) -> str:
    """
    Convenience function to generate a PDF report.
    
    Args:
        data: Dictionary containing the analysis data
        output_path: Path where the PDF file will be saved
        template: Name of the template to use (if None, uses standard_report.html)
        css_files: List of CSS files to apply (if None, uses default CSS)
        title: Title for the PDF document
        
    Returns:
        Path to the generated PDF file
    """
    exporter = PDFExporter()
    return exporter.export_to_pdf(
        data=data,
        output_path=output_path,
        template_name=template or 'standard_report.html',
        css_files=css_files,
        title=title
    )