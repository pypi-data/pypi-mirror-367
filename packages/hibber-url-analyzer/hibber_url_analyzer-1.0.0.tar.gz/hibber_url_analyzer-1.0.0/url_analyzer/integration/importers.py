"""
Data importers module for URL Analyzer.

This module provides data import functionality for URL Analyzer,
allowing it to import data from various formats.
"""

import csv
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, BinaryIO, TextIO, Iterator

# Configure logger
logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available, some import features will be limited")


class DataImporter(ABC):
    """
    Abstract base class for data importers.
    
    This class defines the interface for data importers.
    """
    
    @abstractmethod
    def import_data(self, input_source: Union[str, BinaryIO, TextIO], **kwargs) -> Any:
        """
        Import data from the specified input source.
        
        Args:
            input_source: The input file path or file-like object
            **kwargs: Additional import options
            
        Returns:
            The imported data
        """
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get the name of the import format."""
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """Get the file extensions for the import format."""
        pass


class JSONImporter(DataImporter):
    """
    JSON data importer.
    
    This class imports data from JSON format.
    """
    
    def import_data(self, input_source: Union[str, TextIO], **kwargs) -> Any:
        """
        Import data from JSON.
        
        Args:
            input_source: The input file path or file-like object
            **kwargs: Additional import options
                as_dataframe: Whether to return a pandas DataFrame (default: False)
                
        Returns:
            The imported data as a dictionary, list, or pandas DataFrame
        """
        as_dataframe = kwargs.get('as_dataframe', False)
        
        if isinstance(input_source, str):
            with open(input_source, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Imported data from JSON file: {input_source}")
        else:
            data = json.load(input_source)
            logger.info("Imported data from JSON stream")
        
        if as_dataframe and PANDAS_AVAILABLE:
            return pd.DataFrame(data)
        
        return data
    
    @property
    def format_name(self) -> str:
        """Get the name of the import format."""
        return "JSON"
    
    @property
    def file_extensions(self) -> List[str]:
        """Get the file extensions for the import format."""
        return [".json"]


class CSVImporter(DataImporter):
    """
    CSV data importer.
    
    This class imports data from CSV format.
    """
    
    def import_data(self, input_source: Union[str, TextIO], **kwargs) -> Any:
        """
        Import data from CSV.
        
        Args:
            input_source: The input file path or file-like object
            **kwargs: Additional import options
                delimiter: Field delimiter (default: ',')
                quotechar: Quote character (default: '"')
                as_dataframe: Whether to return a pandas DataFrame (default: True)
                as_dict_list: Whether to return a list of dictionaries (default: False)
                columns: List of columns to include (default: all)
                dtype: Data types for columns (default: None)
                
        Returns:
            The imported data as a pandas DataFrame or list of dictionaries
        """
        delimiter = kwargs.get('delimiter', ',')
        quotechar = kwargs.get('quotechar', '"')
        as_dataframe = kwargs.get('as_dataframe', True)
        as_dict_list = kwargs.get('as_dict_list', False)
        columns = kwargs.get('columns')
        dtype = kwargs.get('dtype')
        
        if as_dataframe and PANDAS_AVAILABLE:
            # Import as pandas DataFrame
            if isinstance(input_source, str):
                df = pd.read_csv(
                    input_source,
                    sep=delimiter,
                    quotechar=quotechar,
                    usecols=columns,
                    dtype=dtype
                )
                logger.info(f"Imported data from CSV file: {input_source}")
            else:
                df = pd.read_csv(
                    input_source,
                    sep=delimiter,
                    quotechar=quotechar,
                    usecols=columns,
                    dtype=dtype
                )
                logger.info("Imported data from CSV stream")
            
            if as_dict_list:
                return df.to_dict('records')
            return df
        else:
            # Import as list of dictionaries
            if isinstance(input_source, str):
                with open(input_source, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=delimiter, quotechar=quotechar)
                    if columns:
                        data = [{k: row[k] for k in columns if k in row} for row in reader]
                    else:
                        data = [row for row in reader]
                logger.info(f"Imported data from CSV file: {input_source}")
            else:
                reader = csv.DictReader(input_source, delimiter=delimiter, quotechar=quotechar)
                if columns:
                    data = [{k: row[k] for k in columns if k in row} for row in reader]
                else:
                    data = [row for row in reader]
                logger.info("Imported data from CSV stream")
            
            if as_dataframe and PANDAS_AVAILABLE:
                return pd.DataFrame(data)
            return data
    
    @property
    def format_name(self) -> str:
        """Get the name of the import format."""
        return "CSV"
    
    @property
    def file_extensions(self) -> List[str]:
        """Get the file extensions for the import format."""
        return [".csv", ".tsv"]


class ExcelImporter(DataImporter):
    """
    Excel data importer.
    
    This class imports data from Excel format.
    """
    
    def __init__(self):
        """Initialize the Excel importer."""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas and openpyxl are required for Excel import")
    
    def import_data(self, input_source: Union[str, BinaryIO], **kwargs) -> Any:
        """
        Import data from Excel.
        
        Args:
            input_source: The input file path or file-like object
            **kwargs: Additional import options
                sheet_name: Name or index of the worksheet (default: 0)
                as_dict_list: Whether to return a list of dictionaries (default: False)
                header: Row to use as column names (default: 0)
                columns: List of columns to include (default: all)
                dtype: Data types for columns (default: None)
                
        Returns:
            The imported data as a pandas DataFrame or list of dictionaries
        """
        sheet_name = kwargs.get('sheet_name', 0)
        as_dict_list = kwargs.get('as_dict_list', False)
        header = kwargs.get('header', 0)
        columns = kwargs.get('columns')
        dtype = kwargs.get('dtype')
        
        # Import as pandas DataFrame
        if isinstance(input_source, str):
            df = pd.read_excel(
                input_source,
                sheet_name=sheet_name,
                header=header,
                usecols=columns,
                dtype=dtype
            )
            logger.info(f"Imported data from Excel file: {input_source}")
        else:
            df = pd.read_excel(
                input_source,
                sheet_name=sheet_name,
                header=header,
                usecols=columns,
                dtype=dtype
            )
            logger.info("Imported data from Excel stream")
        
        if as_dict_list:
            return df.to_dict('records')
        return df
    
    @property
    def format_name(self) -> str:
        """Get the name of the import format."""
        return "Excel"
    
    @property
    def file_extensions(self) -> List[str]:
        """Get the file extensions for the import format."""
        return [".xlsx", ".xls"]


class HTMLImporter(DataImporter):
    """
    HTML data importer.
    
    This class imports data from HTML tables.
    """
    
    def __init__(self):
        """Initialize the HTML importer."""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas and lxml are required for HTML import")
    
    def import_data(self, input_source: Union[str, TextIO], **kwargs) -> Any:
        """
        Import data from HTML tables.
        
        Args:
            input_source: The input file path or file-like object
            **kwargs: Additional import options
                table_index: Index of the table to import (default: 0)
                as_dict_list: Whether to return a list of dictionaries (default: False)
                header: Row to use as column names (default: 0)
                
        Returns:
            The imported data as a pandas DataFrame or list of dictionaries
        """
        table_index = kwargs.get('table_index', 0)
        as_dict_list = kwargs.get('as_dict_list', False)
        header = kwargs.get('header', 0)
        
        # Import as pandas DataFrame
        if isinstance(input_source, str):
            df = pd.read_html(input_source, header=header)[table_index]
            logger.info(f"Imported data from HTML file: {input_source}")
        else:
            html_content = input_source.read()
            df = pd.read_html(html_content, header=header)[table_index]
            logger.info("Imported data from HTML stream")
        
        if as_dict_list:
            return df.to_dict('records')
        return df
    
    @property
    def format_name(self) -> str:
        """Get the name of the import format."""
        return "HTML"
    
    @property
    def file_extensions(self) -> List[str]:
        """Get the file extensions for the import format."""
        return [".html", ".htm"]


def get_importer(format_name: str) -> DataImporter:
    """
    Get an importer for the specified format.
    
    Args:
        format_name: The name of the import format
        
    Returns:
        A data importer for the specified format
        
    Raises:
        ValueError: If the format is not supported
    """
    format_name = format_name.lower()
    
    if format_name == 'json':
        return JSONImporter()
    elif format_name in ('csv', 'tsv'):
        return CSVImporter()
    elif format_name in ('excel', 'xlsx', 'xls'):
        return ExcelImporter()
    elif format_name in ('html', 'htm'):
        return HTMLImporter()
    else:
        raise ValueError(f"Unsupported import format: {format_name}")


def import_data(input_source: Union[str, BinaryIO, TextIO], format_name: Optional[str] = None, **kwargs) -> Any:
    """
    Import data from the specified format.
    
    Args:
        input_source: The input file path or file-like object
        format_name: The name of the import format (default: inferred from file extension)
        **kwargs: Additional import options
        
    Returns:
        The imported data
        
    Raises:
        ValueError: If the format cannot be determined or is not supported
    """
    # Determine format from file extension if not specified
    if format_name is None:
        if isinstance(input_source, str):
            _, ext = os.path.splitext(input_source)
            if ext:
                format_name = ext[1:].lower()  # Remove leading dot
            else:
                raise ValueError("Cannot determine import format from file extension")
        else:
            raise ValueError("Format must be specified when importing from a stream")
    
    # Get importer and import data
    importer = get_importer(format_name)
    data = importer.import_data(input_source, **kwargs)
    
    logger.info(f"Imported data from {importer.format_name} format")
    return data


def import_urls_from_file(input_source: Union[str, BinaryIO, TextIO], format_name: Optional[str] = None, **kwargs) -> List[str]:
    """
    Import URLs from a file.
    
    This is a specialized import function that extracts URLs from a file.
    
    Args:
        input_source: The input file path or file-like object
        format_name: The name of the import format (default: inferred from file extension)
        **kwargs: Additional import options
            url_column: The name or index of the column containing URLs (default: 'url' or 'URL' or first column)
            
    Returns:
        A list of URLs
        
    Raises:
        ValueError: If the format cannot be determined or is not supported
    """
    url_column = kwargs.get('url_column')
    
    # Import the data
    data = import_data(input_source, format_name, **kwargs)
    
    # Extract URLs from the data
    if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
        # Find URL column if not specified
        if url_column is None:
            if 'url' in data.columns:
                url_column = 'url'
            elif 'URL' in data.columns:
                url_column = 'URL'
            else:
                url_column = data.columns[0]
        
        # Extract URLs
        urls = data[url_column].tolist()
    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        # Find URL column if not specified
        if url_column is None:
            if data and 'url' in data[0]:
                url_column = 'url'
            elif data and 'URL' in data[0]:
                url_column = 'URL'
            else:
                url_column = list(data[0].keys())[0] if data else None
        
        # Extract URLs
        urls = [item.get(url_column, '') for item in data if url_column in item]
    elif isinstance(data, list) and all(isinstance(item, str) for item in data):
        # Data is already a list of strings (assumed to be URLs)
        urls = data
    else:
        raise ValueError("Cannot extract URLs from the imported data")
    
    # Filter out empty URLs
    urls = [url for url in urls if url]
    
    logger.info(f"Imported {len(urls)} URLs from {input_source}")
    return urls