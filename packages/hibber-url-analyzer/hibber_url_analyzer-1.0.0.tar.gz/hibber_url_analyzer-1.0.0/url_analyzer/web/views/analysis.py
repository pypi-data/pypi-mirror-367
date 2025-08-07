"""
Analysis views for the URL Analyzer web interface.

This module contains the analysis blueprint with routes for URL analysis,
file uploads, and analysis results.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask import send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.validation import validate_url, validate_string, validate_file_path
from url_analyzer.utils.errors import ValidationError, URLValidationError, PathValidationError
from url_analyzer.utils.sanitization import sanitize_url, sanitize_filename
from url_analyzer.web.rate_limiting import web_rate_limit_moderate, web_rate_limit_strict
from url_analyzer.core.classification import classify_url
from url_analyzer.data.processing import process_file

logger = get_logger(__name__)

# Create blueprint
analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/')
def index():
    """Render the analysis home page."""
    return render_template('analysis/index.html', title='URL Analysis')


@analysis_bp.route('/url', methods=['GET', 'POST'])
@web_rate_limit_moderate
def analyze_url():
    """
    Analyze a single URL.
    
    GET: Render the URL analysis form
    POST: Process the URL and show results
    """
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        
        try:
            # Validate the URL input
            validate_string(url, min_length=1, error_message="URL cannot be empty")
            validate_url(url, error_message="Please enter a valid URL")
            
            # Sanitize the URL
            url = sanitize_url(url)
            
            # Analyze the URL
            result = classify_url(url)
            
            # Render the results
            return render_template(
                'analysis/url_result.html',
                title='URL Analysis Result',
                url=url,
                result=result
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error for URL input: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('analysis.analyze_url'))
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {str(e)}")
            flash(f'Error analyzing URL: {str(e)}', 'error')
            return redirect(url_for('analysis.analyze_url'))
    
    # GET request - show the form
    return render_template('analysis/url_form.html', title='Analyze URL')


@analysis_bp.route('/file', methods=['GET', 'POST'])
@web_rate_limit_strict
def analyze_file():
    """
    Analyze URLs from a file.
    
    GET: Render the file upload form
    POST: Process the file and show results
    """
    if request.method == 'POST':
        try:
            # Check if a file was uploaded
            if 'file' not in request.files:
                raise ValidationError('No file selected.')
            
            file = request.files['file']
            
            # Validate file selection
            if file.filename == '':
                raise ValidationError('No file selected.')
            
            # Validate filename
            validate_string(file.filename, min_length=1, error_message="Filename cannot be empty")
            
            # Check file size (limit to 50MB)
            file.seek(0, 2)  # Seek to end of file
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            max_file_size = 50 * 1024 * 1024  # 50MB in bytes
            if file_size > max_file_size:
                raise ValidationError(f'File size too large. Maximum allowed size is 50MB.')
            
            if file_size == 0:
                raise ValidationError('File is empty.')
            
            # Validate file extension
            allowed_extensions = {'csv', 'xlsx', 'xls', 'txt'}
            file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                raise ValidationError(f'File type not supported. Please upload a CSV, Excel, or text file.')
            
        except ValidationError as e:
            logger.warning(f"File validation error: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('analysis.analyze_file'))
        
        try:
            # Save the file temporarily with sanitized filename
            filename = sanitize_filename(secure_filename(file.filename))
            temp_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', '/tmp'), filename)
            file.save(temp_path)
            
            # Process the file
            results_df = process_file(temp_path)
            
            # Generate a unique ID for this analysis
            import uuid
            analysis_id = str(uuid.uuid4())
            
            # Store the results in the session or a database
            # For simplicity, we'll use a file cache
            cache_dir = current_app.config.get('CACHE_FOLDER', '/tmp')
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, f'analysis_{analysis_id}.csv')
            results_df.to_csv(cache_path, index=False)
            
            # Clean up the temporary file
            os.remove(temp_path)
            
            # Redirect to the results page
            return redirect(url_for('analysis.file_results', analysis_id=analysis_id))
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('analysis.analyze_file'))
    
    # GET request - show the form
    return render_template('analysis/file_form.html', title='Analyze File')


@analysis_bp.route('/results/<analysis_id>')
def file_results(analysis_id):
    """
    Show the results of a file analysis.
    
    Args:
        analysis_id: ID of the analysis to show
    """
    # Load the results from the cache
    cache_dir = current_app.config.get('CACHE_FOLDER', '/tmp')
    cache_path = os.path.join(cache_dir, f'analysis_{analysis_id}.csv')
    
    if not os.path.exists(cache_path):
        flash('Analysis results not found.', 'error')
        return redirect(url_for('analysis.analyze_file'))
    
    try:
        # Load the results
        results_df = pd.read_csv(cache_path)
        
        # Calculate summary statistics
        stats = {
            'total_urls': len(results_df),
            'categories': results_df['category'].value_counts().to_dict(),
            'sensitive_count': results_df['is_sensitive'].sum(),
            'domains': len(results_df['domain'].unique())
        }
        
        # Render the results page
        return render_template(
            'analysis/file_results.html',
            title='File Analysis Results',
            analysis_id=analysis_id,
            stats=stats,
            sample_results=results_df.head(10).to_dict('records')
        )
        
    except Exception as e:
        logger.error(f"Error loading results for analysis {analysis_id}: {str(e)}")
        flash(f'Error loading results: {str(e)}', 'error')
        return redirect(url_for('analysis.analyze_file'))


@analysis_bp.route('/api/results/<analysis_id>')
def api_results(analysis_id):
    """
    API endpoint to get analysis results.
    
    Args:
        analysis_id: ID of the analysis to get
    """
    # Load the results from the cache
    cache_dir = current_app.config.get('CACHE_FOLDER', '/tmp')
    cache_path = os.path.join(cache_dir, f'analysis_{analysis_id}.csv')
    
    if not os.path.exists(cache_path):
        return jsonify({'error': 'Analysis results not found'}), 404
    
    try:
        # Load the results
        results_df = pd.read_csv(cache_path)
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Calculate start and end indices
        start = (page - 1) * per_page
        end = start + per_page
        
        # Get the requested page of results
        page_results = results_df.iloc[start:end].to_dict('records')
        
        # Return the results as JSON
        return jsonify({
            'results': page_results,
            'total': len(results_df),
            'page': page,
            'per_page': per_page,
            'pages': (len(results_df) + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f"Error loading API results for analysis {analysis_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/download/<analysis_id>')
def download_results(analysis_id):
    """
    Download analysis results.
    
    Args:
        analysis_id: ID of the analysis to download
    """
    # Load the results from the cache
    cache_dir = current_app.config.get('CACHE_FOLDER', '/tmp')
    cache_path = os.path.join(cache_dir, f'analysis_{analysis_id}.csv')
    
    if not os.path.exists(cache_path):
        flash('Analysis results not found.', 'error')
        return redirect(url_for('analysis.analyze_file'))
    
    # Get the requested format
    format = request.args.get('format', 'csv').lower()
    
    try:
        # Load the results
        results_df = pd.read_csv(cache_path)
        
        # Create a temporary file for the download
        download_dir = current_app.config.get('DOWNLOAD_FOLDER', '/tmp')
        os.makedirs(download_dir, exist_ok=True)
        
        if format == 'excel':
            # Export to Excel
            download_path = os.path.join(download_dir, f'analysis_{analysis_id}.xlsx')
            results_df.to_excel(download_path, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
        elif format == 'json':
            # Export to JSON
            download_path = os.path.join(download_dir, f'analysis_{analysis_id}.json')
            results_df.to_json(download_path, orient='records', lines=True)
            mimetype = 'application/json'
            
        else:
            # Default to CSV
            download_path = os.path.join(download_dir, f'analysis_{analysis_id}.csv')
            results_df.to_csv(download_path, index=False)
            mimetype = 'text/csv'
        
        # Send the file
        return send_file(
            download_path,
            as_attachment=True,
            download_name=os.path.basename(download_path),
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"Error downloading results for analysis {analysis_id}: {str(e)}")
        flash(f'Error downloading results: {str(e)}', 'error')
        return redirect(url_for('analysis.file_results', analysis_id=analysis_id))