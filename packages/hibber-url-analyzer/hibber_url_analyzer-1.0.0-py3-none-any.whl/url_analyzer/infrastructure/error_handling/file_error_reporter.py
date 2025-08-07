"""
File Error Reporter

This module provides a file-based implementation of the ErrorReporter interface.
It reports errors to a file in various formats (JSON, HTML, text).
"""

import os
import json
import html
from datetime import datetime
from typing import Dict, List, Optional, Any

from url_analyzer.domain.errors import DomainError
from url_analyzer.application.error_handling import ErrorReporter
from url_analyzer.application.interfaces import FileStorageService, LoggingService


class FileErrorReporter(ErrorReporter):
    """
    File-based implementation of the ErrorReporter interface.
    
    This class reports errors to a file in various formats (JSON, HTML, text).
    """
    
    def __init__(
        self,
        file_storage_service: FileStorageService,
        logging_service: LoggingService,
        report_directory: str
    ):
        """
        Initialize the error reporter.
        
        Args:
            file_storage_service: Service for storing files
            logging_service: Service for logging
            report_directory: Directory for storing error reports
        """
        self.file_storage_service = file_storage_service
        self.logging_service = logging_service
        self.report_directory = report_directory
        
        # Ensure the report directory exists
        if not os.path.exists(report_directory):
            os.makedirs(report_directory)
    
    def report_error(self, error: DomainError) -> None:
        """
        Report an error.
        
        Args:
            error: The error to report
        """
        # Log that we're reporting the error
        self.logging_service.debug(
            f"Reporting error: {error.message}",
            category=error.category.name,
            severity=error.severity.name
        )
        
        # Report the error as JSON
        self._report_error_as_json(error)
    
    def report_errors(self, errors: List[DomainError]) -> None:
        """
        Report multiple errors.
        
        Args:
            errors: The errors to report
        """
        # Log that we're reporting multiple errors
        self.logging_service.debug(
            f"Reporting {len(errors)} errors",
            count=len(errors)
        )
        
        # Report each error individually
        for error in errors:
            self.report_error(error)
        
        # Generate a combined report if there are multiple errors
        if len(errors) > 1:
            self._generate_combined_report(errors)
    
    def generate_error_report(self, errors: List[DomainError], format: str = 'json') -> str:
        """
        Generate an error report.
        
        Args:
            errors: The errors to include in the report
            format: The report format (json, html, text)
            
        Returns:
            The generated report
        """
        if format.lower() == 'json':
            return self._generate_json_report(errors)
        elif format.lower() == 'html':
            return self._generate_html_report(errors)
        elif format.lower() == 'text':
            return self._generate_text_report(errors)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    def _report_error_as_json(self, error: DomainError) -> None:
        """
        Report an error as JSON.
        
        Args:
            error: The error to report
        """
        # Generate a filename based on the error timestamp and category
        timestamp = error.context.timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"error_{timestamp}_{error.category.name.lower()}.json"
        file_path = os.path.join(self.report_directory, filename)
        
        # Convert the error to a dictionary
        error_dict = error.to_dict()
        
        # Add additional metadata
        error_dict['reported_at'] = datetime.now().isoformat()
        
        # Convert to JSON
        error_json = json.dumps(error_dict, indent=2)
        
        # Save to file
        self.file_storage_service.save(file_path, error_json)
        
        # Log that the error was reported
        self.logging_service.debug(
            f"Error reported to {file_path}",
            file_path=file_path
        )
    
    def _generate_combined_report(self, errors: List[DomainError]) -> None:
        """
        Generate a combined report for multiple errors.
        
        Args:
            errors: The errors to include in the report
        """
        # Generate a filename based on the current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate reports in different formats
        json_report = self._generate_json_report(errors)
        html_report = self._generate_html_report(errors)
        text_report = self._generate_text_report(errors)
        
        # Save the reports
        json_file_path = os.path.join(self.report_directory, f"errors_{timestamp}.json")
        html_file_path = os.path.join(self.report_directory, f"errors_{timestamp}.html")
        text_file_path = os.path.join(self.report_directory, f"errors_{timestamp}.txt")
        
        self.file_storage_service.save(json_file_path, json_report)
        self.file_storage_service.save(html_file_path, html_report)
        self.file_storage_service.save(text_file_path, text_report)
        
        # Log that the reports were generated
        self.logging_service.debug(
            f"Combined error reports generated: {json_file_path}, {html_file_path}, {text_file_path}",
            json_file=json_file_path,
            html_file=html_file_path,
            text_file=text_file_path
        )
    
    def _generate_json_report(self, errors: List[DomainError]) -> str:
        """
        Generate a JSON report for multiple errors.
        
        Args:
            errors: The errors to include in the report
            
        Returns:
            The generated JSON report
        """
        # Convert errors to dictionaries
        error_dicts = [error.to_dict() for error in errors]
        
        # Add report metadata
        report = {
            'report_type': 'error_report',
            'generated_at': datetime.now().isoformat(),
            'error_count': len(errors),
            'errors': error_dicts
        }
        
        # Convert to JSON
        return json.dumps(report, indent=2)
    
    def _generate_html_report(self, errors: List[DomainError]) -> str:
        """
        Generate an HTML report for multiple errors.
        
        Args:
            errors: The errors to include in the report
            
        Returns:
            The generated HTML report
        """
        # Start with the HTML header
        html_report = """<!DOCTYPE html>
<html>
<head>
    <title>Error Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .error { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .error-critical { background-color: #ffdddd; }
        .error-error { background-color: #ffeeee; }
        .error-warning { background-color: #ffffdd; }
        .error-info { background-color: #eeeeff; }
        .error-debug { background-color: #ddffdd; }
        .error-header { font-weight: bold; margin-bottom: 5px; }
        .error-message { margin-bottom: 10px; }
        .error-details { margin-left: 20px; }
        .error-suggestions { margin-top: 10px; }
        .error-suggestion { margin-left: 20px; }
    </style>
</head>
<body>
    <h1>Error Report</h1>
    <p>Generated at: {}</p>
    <p>Total errors: {}</p>
""".format(datetime.now().isoformat(), len(errors))
        
        # Add each error
        for error in errors:
            # Escape HTML special characters in the message
            message = html.escape(error.message)
            
            # Add the error with appropriate styling based on severity
            html_report += f"""
    <div class="error error-{error.severity.name.lower()}">
        <div class="error-header">[{error.severity.name}] [{error.category.name}] {message}</div>
        <div class="error-details">
            <div>Component: {error.context.component}</div>
            <div>Operation: {error.context.operation}</div>
            <div>Timestamp: {error.context.timestamp.isoformat()}</div>
"""
            
            # Add error code if available
            if error.error_code:
                html_report += f'            <div>Error Code: {error.error_code}</div>\n'
            
            # Add input data if available
            if error.context.input_data:
                input_data_str = ", ".join(f"{k}={html.escape(str(v))}" for k, v in error.context.input_data.items())
                html_report += f'            <div>Input Data: {input_data_str}</div>\n'
            
            # Add environment data if available
            if error.context.environment:
                env_data_str = ", ".join(f"{k}={html.escape(str(v))}" for k, v in error.context.environment.items())
                html_report += f'            <div>Environment: {env_data_str}</div>\n'
            
            # Add suggestions if available
            if error.suggestions:
                html_report += '            <div class="error-suggestions">Suggestions:</div>\n'
                for suggestion in error.suggestions:
                    html_report += f'            <div class="error-suggestion">- {html.escape(suggestion)}</div>\n'
            
            # Add stack trace if available
            if error.stack_trace:
                html_report += '            <div>Stack Trace:</div>\n'
                html_report += f'            <pre>{html.escape(error.stack_trace)}</pre>\n'
            
            html_report += '        </div>\n    </div>\n'
        
        # Add the HTML footer
        html_report += """
</body>
</html>
"""
        
        return html_report
    
    def _generate_text_report(self, errors: List[DomainError]) -> str:
        """
        Generate a text report for multiple errors.
        
        Args:
            errors: The errors to include in the report
            
        Returns:
            The generated text report
        """
        # Start with the report header
        text_report = f"Error Report\n"
        text_report += f"Generated at: {datetime.now().isoformat()}\n"
        text_report += f"Total errors: {len(errors)}\n\n"
        
        # Add each error
        for i, error in enumerate(errors):
            text_report += f"Error {i+1}:\n"
            text_report += f"  Severity: {error.severity.name}\n"
            text_report += f"  Category: {error.category.name}\n"
            text_report += f"  Message: {error.message}\n"
            text_report += f"  Component: {error.context.component}\n"
            text_report += f"  Operation: {error.context.operation}\n"
            text_report += f"  Timestamp: {error.context.timestamp.isoformat()}\n"
            
            # Add error code if available
            if error.error_code:
                text_report += f"  Error Code: {error.error_code}\n"
            
            # Add input data if available
            if error.context.input_data:
                input_data_str = ", ".join(f"{k}={v}" for k, v in error.context.input_data.items())
                text_report += f"  Input Data: {input_data_str}\n"
            
            # Add environment data if available
            if error.context.environment:
                env_data_str = ", ".join(f"{k}={v}" for k, v in error.context.environment.items())
                text_report += f"  Environment: {env_data_str}\n"
            
            # Add suggestions if available
            if error.suggestions:
                text_report += "  Suggestions:\n"
                for suggestion in error.suggestions:
                    text_report += f"    - {suggestion}\n"
            
            # Add stack trace if available
            if error.stack_trace:
                text_report += "  Stack Trace:\n"
                for line in error.stack_trace.split('\n'):
                    text_report += f"    {line}\n"
            
            text_report += "\n"
        
        return text_report