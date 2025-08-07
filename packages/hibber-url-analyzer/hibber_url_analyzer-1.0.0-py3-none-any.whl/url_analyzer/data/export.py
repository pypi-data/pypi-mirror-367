"""
Data Export Module

This module provides functionality for exporting URL analysis data
to various formats, including CSV, JSON, Excel, XML, HTML, and Markdown.
"""

import os
import json
import csv
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from xml.dom import minidom
from xml.etree import ElementTree as ET
import jinja2
from url_analyzer.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


def export_to_csv(df: pd.DataFrame, output_path: str) -> str:
    """
    Export DataFrame to CSV file.
    
    Args:
        df: DataFrame to export
        output_path: Path where to save the CSV file
        
    Returns:
        Path to the exported file
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Export to CSV
        df.to_csv(output_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
        logger.info(f"Successfully exported data to CSV file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return ""


def export_to_json(df: pd.DataFrame, output_path: str) -> str:
    """
    Export DataFrame to JSON file.
    
    Args:
        df: DataFrame to export
        output_path: Path where to save the JSON file
        
    Returns:
        Path to the exported file
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict(orient='records')
        
        # Export to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2)
        
        logger.info(f"Successfully exported data to JSON file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return ""


def export_to_excel(df: pd.DataFrame, output_path: str) -> str:
    """
    Export DataFrame to Excel file.
    
    Args:
        df: DataFrame to export
        output_path: Path where to save the Excel file
        
    Returns:
        Path to the exported file
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Export to Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
        logger.info(f"Successfully exported data to Excel file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        return ""


def export_to_xml(df: pd.DataFrame, output_path: str) -> str:
    """
    Export DataFrame to XML file.
    
    Args:
        df: DataFrame to export
        output_path: Path where to save the XML file
        
    Returns:
        Path to the exported file
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Create root element
        root = ET.Element("data")
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict(orient='records')
        
        # Add each record as a child element
        for record in records:
            record_elem = ET.SubElement(root, "record")
            for key, value in record.items():
                # Skip None values
                if value is None:
                    continue
                
                # Create child element for each field
                field_elem = ET.SubElement(record_elem, key.replace(" ", "_"))
                field_elem.text = str(value)
        
        # Create XML string with pretty formatting
        xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        logger.info(f"Successfully exported data to XML file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error exporting to XML: {e}")
        return ""


def export_to_html(df: pd.DataFrame, output_path: str, title: str = "URL Analysis Results") -> str:
    """
    Export DataFrame to HTML file.
    
    Args:
        df: DataFrame to export
        output_path: Path where to save the HTML file
        title: Title for the HTML document
        
    Returns:
        Path to the exported file
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Create a simple HTML template
        template_str = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .metadata {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="metadata">
        <p>Generated: {{ timestamp }}</p>
        <p>Total Records: {{ record_count }}</p>
    </div>
    {{ table_html }}
</body>
</html>"""
        
        # Create Jinja2 template
        template = jinja2.Template(template_str)
        
        # Convert DataFrame to HTML table
        table_html = df.to_html(index=False, classes="data-table", escape=True)
        
        # Render template with data
        html_content = template.render(
            title=title,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            record_count=len(df),
            table_html=table_html
        )
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Successfully exported data to HTML file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error exporting to HTML: {e}")
        return ""


def export_to_markdown(df: pd.DataFrame, output_path: str, title: str = "URL Analysis Results") -> str:
    """
    Export DataFrame to Markdown file.
    
    Args:
        df: DataFrame to export
        output_path: Path where to save the Markdown file
        title: Title for the Markdown document
        
    Returns:
        Path to the exported file
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Create markdown content
        markdown_lines = []
        
        # Add title and metadata
        markdown_lines.append(f"# {title}")
        markdown_lines.append("")
        markdown_lines.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_lines.append(f"Total Records: {len(df)}")
        markdown_lines.append("")
        
        # Add table header
        header = "| " + " | ".join(df.columns) + " |"
        separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
        markdown_lines.append(header)
        markdown_lines.append(separator)
        
        # Add table rows
        for _, row in df.iterrows():
            row_values = []
            for value in row:
                # Handle None values and escape pipe characters
                if value is None:
                    row_values.append("")
                else:
                    # Escape pipe characters and newlines
                    row_values.append(str(value).replace("|", "\\|").replace("\n", "<br>"))
            
            markdown_lines.append("| " + " | ".join(row_values) + " |")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(markdown_lines))
        
        logger.info(f"Successfully exported data to Markdown file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error exporting to Markdown: {e}")
        return ""


def export_data(df: pd.DataFrame, output_path: str, format: str = 'csv', 
               title: str = "URL Analysis Results") -> str:
    """
    Export DataFrame to the specified format.
    
    Args:
        df: DataFrame to export
        output_path: Base path for the output file (without extension)
        format: Export format ('csv', 'json', 'excel', 'xml', 'html', or 'markdown')
        title: Title for the document (used for HTML and Markdown formats)
        
    Returns:
        Path to the exported file
    """
    # Map of format to file extension
    format_extensions = {
        'csv': 'csv',
        'json': 'json',
        'excel': 'xlsx',
        'xml': 'xml',
        'html': 'html',
        'markdown': 'md'
    }
    
    # Normalize format
    format_lower = format.lower()
    
    # Check if format is supported
    if format_lower not in format_extensions:
        logger.error(f"Unsupported export format: {format}")
        return ""
    
    # Add appropriate extension if not present
    extension = format_extensions[format_lower]
    if not output_path.lower().endswith(f'.{extension}'):
        output_path = f"{output_path}.{extension}"
    
    # Export based on format
    if format_lower == 'csv':
        return export_to_csv(df, output_path)
    elif format_lower == 'json':
        return export_to_json(df, output_path)
    elif format_lower == 'excel':
        return export_to_excel(df, output_path)
    elif format_lower == 'xml':
        return export_to_xml(df, output_path)
    elif format_lower == 'html':
        return export_to_html(df, output_path, title)
    elif format_lower == 'markdown':
        return export_to_markdown(df, output_path, title)
    else:
        # This should never happen due to the check above, but just in case
        logger.error(f"Unsupported export format: {format}")
        return ""


def export_filtered_data(
    df: pd.DataFrame, 
    output_path: str, 
    format: str = 'csv', 
    filters: Optional[Dict[str, Any]] = None,
    filter_mode: str = 'exact',
    title: str = "URL Analysis Results"
) -> str:
    """
    Export filtered DataFrame to the specified format with advanced filtering options.
    
    Args:
        df: DataFrame to export
        output_path: Base path for the output file (without extension)
        format: Export format ('csv', 'json', 'excel', 'xml', 'html', or 'markdown')
        filters: Dictionary of column-value pairs for filtering
        filter_mode: Filtering mode ('exact', 'contains', 'regex', 'range')
        title: Title for the document (used for HTML and Markdown formats)
        
    Returns:
        Path to the exported file
    """
    # Apply filters if provided
    if filters:
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns:
                # Handle different filter modes
                if filter_mode == 'exact':
                    # Exact match filtering (default behavior)
                    if isinstance(value, list):
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                    else:
                        filtered_df = filtered_df[filtered_df[column] == value]
                
                elif filter_mode == 'contains':
                    # Contains filtering (case-insensitive)
                    if isinstance(value, list):
                        # Any of the values must be contained
                        mask = filtered_df[column].fillna('').astype(str).str.lower().apply(
                            lambda x: any(v.lower() in x for v in value)
                        )
                        filtered_df = filtered_df[mask]
                    else:
                        # Value must be contained
                        filtered_df = filtered_df[
                            filtered_df[column].fillna('').astype(str).str.lower().str.contains(
                                str(value).lower(), regex=False
                            )
                        ]
                
                elif filter_mode == 'regex':
                    # Regular expression filtering
                    import re
                    
                    if isinstance(value, list):
                        # Any of the regex patterns must match
                        patterns = [re.compile(v, re.IGNORECASE) for v in value]
                        mask = filtered_df[column].fillna('').astype(str).apply(
                            lambda x: any(pattern.search(x) for pattern in patterns)
                        )
                        filtered_df = filtered_df[mask]
                    else:
                        # Regex pattern must match
                        try:
                            pattern = re.compile(value, re.IGNORECASE)
                            filtered_df = filtered_df[
                                filtered_df[column].fillna('').astype(str).apply(
                                    lambda x: bool(pattern.search(x))
                                )
                            ]
                        except re.error as e:
                            logger.error(f"Invalid regex pattern '{value}': {e}")
                
                elif filter_mode == 'range':
                    # Range filtering for numeric or date columns
                    if isinstance(value, tuple) and len(value) == 2:
                        min_val, max_val = value
                        
                        # Check if column is numeric
                        if pd.api.types.is_numeric_dtype(filtered_df[column]):
                            # Numeric range filtering
                            filtered_df = filtered_df[
                                (filtered_df[column] >= min_val) & 
                                (filtered_df[column] <= max_val)
                            ]
                        
                        # Check if column contains datetime-like values
                        elif pd.api.types.is_datetime64_dtype(filtered_df[column]):
                            # Date range filtering
                            filtered_df = filtered_df[
                                (filtered_df[column] >= min_val) & 
                                (filtered_df[column] <= max_val)
                            ]
                        
                        else:
                            # Try to convert to datetime if possible
                            try:
                                # Convert min and max values to datetime if they're strings
                                if isinstance(min_val, str):
                                    min_val = pd.to_datetime(min_val)
                                if isinstance(max_val, str):
                                    max_val = pd.to_datetime(max_val)
                                
                                # Convert column to datetime
                                datetime_col = pd.to_datetime(filtered_df[column])
                                
                                # Apply date range filtering
                                mask = (datetime_col >= min_val) & (datetime_col <= max_val)
                                filtered_df = filtered_df[mask]
                            
                            except (ValueError, TypeError):
                                logger.warning(
                                    f"Range filtering not applicable for column '{column}' "
                                    f"with non-numeric, non-date values"
                                )
                    else:
                        logger.warning(
                            f"Range filtering requires a tuple of (min, max) values. "
                            f"Got {value} instead."
                        )
                
                else:
                    logger.warning(f"Unknown filter mode: {filter_mode}. Using exact match instead.")
                    # Fall back to exact match
                    if isinstance(value, list):
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                    else:
                        filtered_df = filtered_df[filtered_df[column] == value]
            else:
                logger.warning(f"Column '{column}' not found in DataFrame. Skipping this filter.")
    else:
        filtered_df = df
    
    # Export the filtered DataFrame
    return export_data(filtered_df, output_path, format, title)