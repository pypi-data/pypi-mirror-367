"""
Reports views for the URL Analyzer web interface.

This module contains the reports blueprint with routes for generating,
viewing, and managing reports.
"""

import os
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask import send_file, abort
from werkzeug.exceptions import NotFound

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.validation import validate_string, validate_file_path
from url_analyzer.utils.errors import ValidationError, PathValidationError
from url_analyzer.utils.sanitization import sanitize_filename
from url_analyzer.web.rate_limiting import web_rate_limit_moderate, web_rate_limit_strict
from url_analyzer.reporting.domain import ReportFormat, ReportType, ChartType
from url_analyzer.reporting import (
    ReportTemplate, ReportData, ReportOptions, Report,
    JinjaTemplateRenderer, PlotlyChartGenerator, HTMLReportGenerator
)

logger = get_logger(__name__)

# Create blueprint
reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
def index():
    """Render the reports home page."""
    return render_template('reports/index.html', title='Reports')


@reports_bp.route('/templates')
def templates():
    """Show available report templates."""
    # Get templates from the template directory
    template_dir = current_app.config.get('TEMPLATE_DIR', os.path.join(current_app.root_path, 'templates', 'reports'))
    
    # List of available templates
    available_templates = []
    
    # Check if the directory exists
    if os.path.exists(template_dir) and os.path.isdir(template_dir):
        # Get all HTML files in the directory
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                template_name = os.path.splitext(filename)[0]
                template_path = os.path.join(template_dir, filename)
                
                # Create a template object
                template = {
                    'name': template_name.replace('_', ' ').title(),
                    'id': template_name,
                    'path': template_path,
                    'description': f'Report template for {template_name.replace("_", " ").title()}'
                }
                
                available_templates.append(template)
    
    return render_template(
        'reports/templates.html',
        title='Report Templates',
        templates=available_templates
    )


@reports_bp.route('/generate', methods=['GET', 'POST'])
def generate():
    """
    Generate a new report.
    
    GET: Show the report generation form
    POST: Generate the report
    """
    if request.method == 'POST':
        # Get form data
        report_name = request.form.get('report_name', '').strip()
        template_id = request.form.get('template_id', '').strip()
        analysis_id = request.form.get('analysis_id', '').strip()
        
        try:
            # Validate form data with comprehensive validation
            validate_string(report_name, min_length=1, max_length=100, 
                          pattern=r'^[a-zA-Z0-9\s\-_\.]+$',
                          error_message="Report name must be 1-100 characters and contain only letters, numbers, spaces, hyphens, underscores, and periods")
            
            validate_string(template_id, min_length=1, max_length=50,
                          pattern=r'^[a-zA-Z0-9_]+$',
                          error_message="Template ID must contain only letters, numbers, and underscores")
            
            validate_string(analysis_id, min_length=1, max_length=50,
                          pattern=r'^[a-zA-Z0-9\-]+$',
                          error_message="Analysis ID must contain only letters, numbers, and hyphens")
            
            # Sanitize the report name for file operations
            report_name = sanitize_filename(report_name)
            
        except ValidationError as e:
            logger.warning(f"Report generation validation error: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('reports.generate'))
        
        try:
            # Load the analysis data
            cache_dir = current_app.config.get('CACHE_FOLDER', '/tmp')
            cache_path = os.path.join(cache_dir, f'analysis_{analysis_id}.csv')
            
            if not os.path.exists(cache_path):
                flash('Analysis results not found.', 'error')
                return redirect(url_for('reports.generate'))
            
            # Load the data
            df = pd.read_csv(cache_path)
            
            # Create report data
            report_data = ReportData.create(
                name=report_name,
                data=df,
                metadata={
                    'analysis_id': analysis_id,
                    'generated_at': datetime.now().isoformat(),
                    'user': request.remote_addr
                }
            )
            
            # Get the template path
            template_dir = current_app.config.get('TEMPLATE_DIR', os.path.join(current_app.root_path, 'templates', 'reports'))
            template_path = os.path.join(template_dir, f'{template_id}.html')
            
            if not os.path.exists(template_path):
                flash('Report template not found.', 'error')
                return redirect(url_for('reports.generate'))
            
            # Create report template
            report_template = ReportTemplate.create_html_template(
                name=template_id.replace('_', ' ').title(),
                template_path=template_path,
                description=f'Report template for {template_id.replace("_", " ").title()}',
                type=ReportType.DETAILED
            )
            
            # Create report options
            report_options = ReportOptions.create_detailed(
                title=report_name,
                description=f'Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            )
            
            # Create report output directory
            reports_dir = current_app.config.get('REPORTS_FOLDER', os.path.join(current_app.root_path, 'static', 'reports'))
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate a unique ID for this report
            import uuid
            report_id = str(uuid.uuid4())
            
            # Create report output path
            output_path = os.path.join(reports_dir, f'report_{report_id}.html')
            
            # Create report
            report = Report.create(
                name=report_name,
                template=report_template,
                data=report_data,
                options=report_options,
                output_path=output_path
            )
            
            # Create renderer and generator
            template_renderer = JinjaTemplateRenderer()
            chart_generator = PlotlyChartGenerator()
            report_generator = HTMLReportGenerator(template_renderer, chart_generator)
            
            # Generate the report
            result = report_generator.generate_report(report)
            
            if result.is_success():
                # Store report metadata
                report_metadata = {
                    'id': report_id,
                    'name': report_name,
                    'template_id': template_id,
                    'analysis_id': analysis_id,
                    'created_at': datetime.now().isoformat(),
                    'path': output_path
                }
                
                # Store the metadata in a JSON file
                metadata_dir = current_app.config.get('METADATA_FOLDER', os.path.join(current_app.root_path, 'data', 'metadata'))
                os.makedirs(metadata_dir, exist_ok=True)
                metadata_path = os.path.join(metadata_dir, f'report_{report_id}.json')
                
                import json
                with open(metadata_path, 'w') as f:
                    json.dump(report_metadata, f)
                
                # Redirect to the report view
                flash('Report generated successfully.', 'success')
                return redirect(url_for('reports.view', report_id=report_id))
            else:
                flash(f'Error generating report: {result.error_message}', 'error')
                return redirect(url_for('reports.generate'))
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            flash(f'Error generating report: {str(e)}', 'error')
            return redirect(url_for('reports.generate'))
    
    # GET request - show the form
    
    # Get available templates
    template_dir = current_app.config.get('TEMPLATE_DIR', os.path.join(current_app.root_path, 'templates', 'reports'))
    available_templates = []
    
    if os.path.exists(template_dir) and os.path.isdir(template_dir):
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                template_name = os.path.splitext(filename)[0]
                available_templates.append({
                    'name': template_name.replace('_', ' ').title(),
                    'id': template_name
                })
    
    # Get available analyses
    cache_dir = current_app.config.get('CACHE_FOLDER', '/tmp')
    available_analyses = []
    
    if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
        for filename in os.listdir(cache_dir):
            if filename.startswith('analysis_') and filename.endswith('.csv'):
                analysis_id = filename[9:-4]  # Remove 'analysis_' prefix and '.csv' suffix
                
                # Try to get some metadata about the analysis
                try:
                    df = pd.read_csv(os.path.join(cache_dir, filename))
                    url_count = len(df)
                    domain_count = len(df['domain'].unique()) if 'domain' in df.columns else 0
                    
                    available_analyses.append({
                        'id': analysis_id,
                        'name': f'Analysis {analysis_id[:8]}',
                        'url_count': url_count,
                        'domain_count': domain_count
                    })
                except Exception as e:
                    logger.error(f"Error loading analysis metadata: {str(e)}")
    
    return render_template(
        'reports/generate.html',
        title='Generate Report',
        templates=available_templates,
        analyses=available_analyses
    )


@reports_bp.route('/view/<report_id>')
def view(report_id):
    """
    View a generated report.
    
    Args:
        report_id: ID of the report to view
    """
    # Get report metadata
    metadata_dir = current_app.config.get('METADATA_FOLDER', os.path.join(current_app.root_path, 'data', 'metadata'))
    metadata_path = os.path.join(metadata_dir, f'report_{report_id}.json')
    
    if not os.path.exists(metadata_path):
        flash('Report not found.', 'error')
        return redirect(url_for('reports.index'))
    
    try:
        # Load the metadata
        import json
        with open(metadata_path, 'r') as f:
            report_metadata = json.load(f)
        
        # Get the report path
        report_path = report_metadata.get('path')
        
        if not os.path.exists(report_path):
            flash('Report file not found.', 'error')
            return redirect(url_for('reports.index'))
        
        # Read the report content
        with open(report_path, 'r') as f:
            report_content = f.read()
        
        # Render the report view
        return render_template(
            'reports/view.html',
            title=f'Report: {report_metadata.get("name")}',
            report_id=report_id,
            metadata=report_metadata,
            content=report_content
        )
        
    except Exception as e:
        logger.error(f"Error viewing report {report_id}: {str(e)}")
        flash(f'Error viewing report: {str(e)}', 'error')
        return redirect(url_for('reports.index'))


@reports_bp.route('/list')
def list_reports():
    """List all generated reports."""
    # Get report metadata directory
    metadata_dir = current_app.config.get('METADATA_FOLDER', os.path.join(current_app.root_path, 'data', 'metadata'))
    
    # List of reports
    reports = []
    
    # Check if the directory exists
    if os.path.exists(metadata_dir) and os.path.isdir(metadata_dir):
        # Get all JSON files in the directory
        import json
        for filename in os.listdir(metadata_dir):
            if filename.startswith('report_') and filename.endswith('.json'):
                try:
                    # Load the metadata
                    with open(os.path.join(metadata_dir, filename), 'r') as f:
                        report_metadata = json.load(f)
                    
                    # Add to the list
                    reports.append(report_metadata)
                except Exception as e:
                    logger.error(f"Error loading report metadata {filename}: {str(e)}")
    
    # Sort reports by creation date (newest first)
    reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template(
        'reports/list.html',
        title='Reports',
        reports=reports
    )


@reports_bp.route('/download/<report_id>')
def download(report_id):
    """
    Download a generated report.
    
    Args:
        report_id: ID of the report to download
    """
    # Get report metadata
    metadata_dir = current_app.config.get('METADATA_FOLDER', os.path.join(current_app.root_path, 'data', 'metadata'))
    metadata_path = os.path.join(metadata_dir, f'report_{report_id}.json')
    
    if not os.path.exists(metadata_path):
        flash('Report not found.', 'error')
        return redirect(url_for('reports.index'))
    
    try:
        # Load the metadata
        import json
        with open(metadata_path, 'r') as f:
            report_metadata = json.load(f)
        
        # Get the report path
        report_path = report_metadata.get('path')
        
        if not os.path.exists(report_path):
            flash('Report file not found.', 'error')
            return redirect(url_for('reports.index'))
        
        # Send the file
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"{report_metadata.get('name', 'report')}.html",
            mimetype='text/html'
        )
        
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {str(e)}")
        flash(f'Error downloading report: {str(e)}', 'error')
        return redirect(url_for('reports.view', report_id=report_id))


@reports_bp.route('/delete/<report_id>', methods=['POST'])
def delete(report_id):
    """
    Delete a generated report.
    
    Args:
        report_id: ID of the report to delete
    """
    # Get report metadata
    metadata_dir = current_app.config.get('METADATA_FOLDER', os.path.join(current_app.root_path, 'data', 'metadata'))
    metadata_path = os.path.join(metadata_dir, f'report_{report_id}.json')
    
    if not os.path.exists(metadata_path):
        flash('Report not found.', 'error')
        return redirect(url_for('reports.index'))
    
    try:
        # Load the metadata
        import json
        with open(metadata_path, 'r') as f:
            report_metadata = json.load(f)
        
        # Get the report path
        report_path = report_metadata.get('path')
        
        # Delete the report file if it exists
        if os.path.exists(report_path):
            os.remove(report_path)
        
        # Delete the metadata file
        os.remove(metadata_path)
        
        flash('Report deleted successfully.', 'success')
        return redirect(url_for('reports.list_reports'))
        
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {str(e)}")
        flash(f'Error deleting report: {str(e)}', 'error')
        return redirect(url_for('reports.list_reports'))