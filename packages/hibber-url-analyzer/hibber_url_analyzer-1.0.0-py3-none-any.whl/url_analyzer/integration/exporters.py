"""
Data exporters module for URL Analyzer.

This module provides data export functionality for URL Analyzer,
allowing it to export analysis results in various formats.
"""

import csv
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, BinaryIO, TextIO

# Configure logger
logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available, some export features will be limited")


class DataExporter(ABC):
    """
    Abstract base class for data exporters.
    
    This class defines the interface for data exporters.
    """
    
    @abstractmethod
    def export(self, data: Any, output: Union[str, BinaryIO, TextIO], **kwargs) -> None:
        """
        Export data to the specified output.
        
        Args:
            data: The data to export
            output: The output file path or file-like object
            **kwargs: Additional export options
        """
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get the name of the export format."""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Get the file extension for the export format."""
        pass


class JSONExporter(DataExporter):
    """
    JSON data exporter.
    
    This class exports data in JSON format.
    """
    
    def export(self, data: Any, output: Union[str, TextIO], **kwargs) -> None:
        """
        Export data to JSON.
        
        Args:
            data: The data to export
            output: The output file path or file-like object
            **kwargs: Additional export options
                indent: Indentation level (default: 2)
                ensure_ascii: Whether to escape non-ASCII characters (default: False)
        """
        indent = kwargs.get('indent', 2)
        ensure_ascii = kwargs.get('ensure_ascii', False)
        
        if isinstance(output, str):
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
                logger.info(f"Exported data to JSON file: {output}")
        else:
            json.dump(data, output, indent=indent, ensure_ascii=ensure_ascii)
            logger.info("Exported data to JSON stream")
    
    @property
    def format_name(self) -> str:
        """Get the name of the export format."""
        return "JSON"
    
    @property
    def file_extension(self) -> str:
        """Get the file extension for the export format."""
        return ".json"


class CSVExporter(DataExporter):
    """
    CSV data exporter.
    
    This class exports data in CSV format.
    """
    
    def export(self, data: Any, output: Union[str, TextIO], **kwargs) -> None:
        """
        Export data to CSV.
        
        Args:
            data: The data to export (list of dictionaries or pandas DataFrame)
            output: The output file path or file-like object
            **kwargs: Additional export options
                delimiter: Field delimiter (default: ',')
                quotechar: Quote character (default: '"')
                header: Whether to include header row (default: True)
                columns: List of columns to include (default: all)
        """
        delimiter = kwargs.get('delimiter', ',')
        quotechar = kwargs.get('quotechar', '"')
        header = kwargs.get('header', True)
        columns = kwargs.get('columns')
        
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            # Export pandas DataFrame
            if isinstance(output, str):
                data.to_csv(
                    output,
                    sep=delimiter,
                    header=header,
                    columns=columns,
                    index=False,
                    quotechar=quotechar
                )
                logger.info(f"Exported DataFrame to CSV file: {output}")
            else:
                data.to_csv(
                    output,
                    sep=delimiter,
                    header=header,
                    columns=columns,
                    index=False,
                    quotechar=quotechar
                )
                logger.info("Exported DataFrame to CSV stream")
        else:
            # Export list of dictionaries
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise ValueError("Data must be a list of dictionaries for CSV export")
            
            # Determine columns if not specified
            if columns is None and data:
                columns = list(data[0].keys())
            
            if isinstance(output, str):
                with open(output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=columns,
                        delimiter=delimiter,
                        quotechar=quotechar
                    )
                    
                    if header:
                        writer.writeheader()
                    
                    for item in data:
                        writer.writerow(item)
                
                logger.info(f"Exported data to CSV file: {output}")
            else:
                writer = csv.DictWriter(
                    output,
                    fieldnames=columns,
                    delimiter=delimiter,
                    quotechar=quotechar
                )
                
                if header:
                    writer.writeheader()
                
                for item in data:
                    writer.writerow(item)
                
                logger.info("Exported data to CSV stream")
    
    @property
    def format_name(self) -> str:
        """Get the name of the export format."""
        return "CSV"
    
    @property
    def file_extension(self) -> str:
        """Get the file extension for the export format."""
        return ".csv"


class ExcelExporter(DataExporter):
    """
    Excel data exporter.
    
    This class exports data in Excel format.
    """
    
    def __init__(self):
        """Initialize the Excel exporter."""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas and openpyxl are required for Excel export")
    
    def export(self, data: Any, output: Union[str, BinaryIO], **kwargs) -> None:
        """
        Export data to Excel.
        
        Args:
            data: The data to export (list of dictionaries or pandas DataFrame)
            output: The output file path or file-like object
            **kwargs: Additional export options
                sheet_name: Name of the worksheet (default: 'Sheet1')
                header: Whether to include header row (default: True)
                columns: List of columns to include (default: all)
                index: Whether to include index column (default: False)
        """
        sheet_name = kwargs.get('sheet_name', 'Sheet1')
        header = kwargs.get('header', True)
        columns = kwargs.get('columns')
        index = kwargs.get('index', False)
        
        if isinstance(data, pd.DataFrame):
            # Export pandas DataFrame
            data.to_excel(
                output,
                sheet_name=sheet_name,
                header=header,
                columns=columns,
                index=index
            )
        else:
            # Convert list of dictionaries to DataFrame
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise ValueError("Data must be a list of dictionaries for Excel export")
            
            df = pd.DataFrame(data)
            
            if columns is not None:
                df = df[columns]
            
            df.to_excel(
                output,
                sheet_name=sheet_name,
                header=header,
                index=index
            )
        
        if isinstance(output, str):
            logger.info(f"Exported data to Excel file: {output}")
        else:
            logger.info("Exported data to Excel stream")
    
    @property
    def format_name(self) -> str:
        """Get the name of the export format."""
        return "Excel"
    
    @property
    def file_extension(self) -> str:
        """Get the file extension for the export format."""
        return ".xlsx"


class HTMLExporter(DataExporter):
    """
    HTML data exporter.
    
    This class exports data in HTML format.
    """
    
    def export(self, data: Any, output: Union[str, TextIO], **kwargs) -> None:
        """
        Export data to HTML.
        
        Args:
            data: The data to export (list of dictionaries or pandas DataFrame)
            output: The output file path or file-like object
            **kwargs: Additional export options
                title: Page title (default: 'URL Analyzer Export')
                table_id: HTML table ID (default: 'data-table')
                table_class: HTML table class (default: 'table table-striped')
                template: Custom HTML template (default: None)
        """
        title = kwargs.get('title', 'URL Analyzer Export')
        table_id = kwargs.get('table_id', 'data-table')
        table_class = kwargs.get('table_class', 'table table-striped')
        template = kwargs.get('template')
        
        if PANDAS_AVAILABLE:
            # Convert to DataFrame if not already
            if not isinstance(data, pd.DataFrame):
                if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                    raise ValueError("Data must be a list of dictionaries for HTML export")
                data = pd.DataFrame(data)
            
            # Generate HTML table
            html_table = data.to_html(
                index=False,
                classes=table_class,
                table_id=table_id,
                border=0
            )
            
            # Use template or create basic HTML
            if template:
                with open(template, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                html_content = html_content.replace('{{title}}', title)
                html_content = html_content.replace('{{table}}', html_table)
            else:
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .table {{ width: 100%; border-collapse: collapse; }}
        .table-striped tbody tr:nth-of-type(odd) {{ background-color: rgba(0,0,0,.05); }}
        .table th, .table td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        .table th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {html_table}
</body>
</html>"""
            
            # Write to output
            if isinstance(output, str):
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Exported data to HTML file: {output}")
            else:
                output.write(html_content)
                logger.info("Exported data to HTML stream")
        else:
            raise ImportError("pandas is required for HTML export")
    
    @property
    def format_name(self) -> str:
        """Get the name of the export format."""
        return "HTML"
    
    @property
    def file_extension(self) -> str:
        """Get the file extension for the export format."""
        return ".html"


def get_exporter(format_name: str) -> DataExporter:
    """
    Get an exporter for the specified format.
    
    Args:
        format_name: The name of the export format
        
    Returns:
        A data exporter for the specified format
        
    Raises:
        ValueError: If the format is not supported
    """
    format_name = format_name.lower()
    
    if format_name == 'json':
        return JSONExporter()
    elif format_name == 'csv':
        return CSVExporter()
    elif format_name == 'excel' or format_name == 'xlsx':
        return ExcelExporter()
    elif format_name == 'html':
        return HTMLExporter()
    else:
        raise ValueError(f"Unsupported export format: {format_name}")


def export_data(data: Any, output: Union[str, BinaryIO, TextIO], format_name: Optional[str] = None, **kwargs) -> None:
    """
    Export data to the specified format.
    
    Args:
        data: The data to export
        output: The output file path or file-like object
        format_name: The name of the export format (default: inferred from file extension)
        **kwargs: Additional export options
        
    Raises:
        ValueError: If the format cannot be determined or is not supported
    """
    # Determine format from file extension if not specified
    if format_name is None:
        if isinstance(output, str):
            _, ext = os.path.splitext(output)
            if ext:
                format_name = ext[1:].lower()  # Remove leading dot
            else:
                raise ValueError("Cannot determine export format from file extension")
        else:
            raise ValueError("Format must be specified when exporting to a stream")
    
    # Get exporter and export data
    exporter = get_exporter(format_name)
    exporter.export(data, output, **kwargs)
    
    logger.info(f"Exported data in {exporter.format_name} format")