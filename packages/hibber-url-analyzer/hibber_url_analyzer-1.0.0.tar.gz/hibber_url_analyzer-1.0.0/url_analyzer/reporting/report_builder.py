"""
Report builder for URL Analyzer.

This module provides functionality to build reports from URL analysis data
with customizable templates, charts, and data processing.
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

import pandas as pd
import numpy as np

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)

class ReportBuilder:
    """
    Builder class for creating URL analysis reports.
    
    This class provides a fluent interface for building reports from URL analysis data,
    with customizable templates, charts, and data processing.
    """
    
    def __init__(self, title: Optional[str] = None, template_name: Optional[str] = None):
        """
        Initialize a new report builder.
        
        Args:
            title: Title for the report
            template_name: Name of the template to use for rendering
        """
        self.report_id = str(uuid.uuid4())
        self.title = title or 'URL Analysis Report'
        self.template_name = template_name or 'standard_report.html'
        self.created_at = datetime.now()
        self.author = None
        self.description = None
        self.tags = []
        
        # Data containers
        self.raw_data = None
        self.processed_data = None
        self.dataframe = None
        self.charts = {}
        self.stats = {}
        self.metadata = {}
        self.filters = {}
        
        logger.debug(f"Initialized ReportBuilder with ID {self.report_id}")
    
    def with_title(self, title: str) -> 'ReportBuilder':
        """Set the report title."""
        self.title = title
        return self
    
    def with_template(self, template_name: str) -> 'ReportBuilder':
        """Set the template to use for rendering."""
        self.template_name = template_name
        return self
    
    def with_author(self, author: str) -> 'ReportBuilder':
        """Set the report author."""
        self.author = author
        return self
    
    def with_description(self, description: str) -> 'ReportBuilder':
        """Set the report description."""
        self.description = description
        return self
    
    def with_tags(self, tags: List[str]) -> 'ReportBuilder':
        """Set the report tags."""
        self.tags = tags
        return self
    
    def with_raw_data(self, data: Dict[str, Any]) -> 'ReportBuilder':
        """
        Set the raw data for the report.
        
        Args:
            data: Dictionary containing the raw analysis data
        """
        self.raw_data = data
        return self
    
    def with_dataframe(self, df: pd.DataFrame) -> 'ReportBuilder':
        """
        Set the DataFrame for the report.
        
        Args:
            df: Pandas DataFrame containing the analysis data
        """
        self.dataframe = df
        return self
    
    def with_csv_data(self, csv_path: str, **kwargs) -> 'ReportBuilder':
        """
        Load data from a CSV file.
        
        Args:
            csv_path: Path to the CSV file
            **kwargs: Additional arguments to pass to pd.read_csv()
        """
        try:
            self.dataframe = pd.read_csv(csv_path, **kwargs)
            logger.debug(f"Loaded data from CSV: {csv_path}, shape: {self.dataframe.shape}")
        except Exception as e:
            logger.error(f"Error loading CSV data: {str(e)}", exc_info=True)
            raise
        return self
    
    def with_excel_data(self, excel_path: str, **kwargs) -> 'ReportBuilder':
        """
        Load data from an Excel file.
        
        Args:
            excel_path: Path to the Excel file
            **kwargs: Additional arguments to pass to pd.read_excel()
        """
        try:
            self.dataframe = pd.read_excel(excel_path, **kwargs)
            logger.debug(f"Loaded data from Excel: {excel_path}, shape: {self.dataframe.shape}")
        except Exception as e:
            logger.error(f"Error loading Excel data: {str(e)}", exc_info=True)
            raise
        return self
    
    def with_json_data(self, json_path: str) -> 'ReportBuilder':
        """
        Load data from a JSON file.
        
        Args:
            json_path: Path to the JSON file
        """
        try:
            with open(json_path, 'r') as f:
                self.raw_data = json.load(f)
            logger.debug(f"Loaded data from JSON: {json_path}")
        except Exception as e:
            logger.error(f"Error loading JSON data: {str(e)}", exc_info=True)
            raise
        return self
    
    def add_chart(self, chart_id: str, chart_data: Dict[str, Any]) -> 'ReportBuilder':
        """
        Add a chart to the report.
        
        Args:
            chart_id: Identifier for the chart
            chart_data: Dictionary containing chart data and configuration
        """
        self.charts[chart_id] = chart_data
        return self
    
    def add_stat(self, stat_id: str, stat_data: Dict[str, Any]) -> 'ReportBuilder':
        """
        Add a statistic to the report.
        
        Args:
            stat_id: Identifier for the statistic
            stat_data: Dictionary containing statistic data and configuration
        """
        self.stats[stat_id] = stat_data
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'ReportBuilder':
        """
        Add metadata to the report.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        return self
    
    def add_filter(self, filter_id: str, filter_config: Dict[str, Any]) -> 'ReportBuilder':
        """
        Add a filter to the report.
        
        Args:
            filter_id: Identifier for the filter
            filter_config: Dictionary containing filter configuration
        """
        self.filters[filter_id] = filter_config
        return self
    
    def process_data(self, processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> 'ReportBuilder':
        """
        Process the raw data using a custom processor function.
        
        Args:
            processor: Function that takes raw data and returns processed data
        """
        if self.raw_data is None:
            logger.warning("No raw data to process")
            return self
        
        try:
            self.processed_data = processor(self.raw_data)
            logger.debug("Processed raw data")
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}", exc_info=True)
            raise
        
        return self
    
    def generate_category_chart(self) -> 'ReportBuilder':
        """Generate a category distribution chart from the DataFrame."""
        if self.dataframe is None:
            logger.warning("No DataFrame available for category chart")
            return self
        
        try:
            # Check if 'Category' column exists
            if 'Category' not in self.dataframe.columns:
                logger.warning("No 'Category' column in DataFrame for category chart")
                return self
            
            # Count categories
            category_counts = self.dataframe['Category'].value_counts()
            
            # Prepare chart data
            chart_data = {
                'type': 'pie',
                'title': 'URL Categories',
                'labels': category_counts.index.tolist(),
                'data': category_counts.values.tolist(),
                'colors': self._generate_colors(len(category_counts)),
            }
            
            self.add_chart('category_chart', chart_data)
            logger.debug("Generated category chart")
            
        except Exception as e:
            logger.error(f"Error generating category chart: {str(e)}", exc_info=True)
        
        return self
    
    def generate_domain_chart(self, top_n: int = 10) -> 'ReportBuilder':
        """
        Generate a top domains chart from the DataFrame.
        
        Args:
            top_n: Number of top domains to include
        """
        if self.dataframe is None:
            logger.warning("No DataFrame available for domain chart")
            return self
        
        try:
            # Check if 'Domain' column exists
            domain_col = None
            for col in ['Domain', 'Domain_name', 'Hostname']:
                if col in self.dataframe.columns:
                    domain_col = col
                    break
            
            if domain_col is None:
                logger.warning("No domain column in DataFrame for domain chart")
                return self
            
            # Count domains
            domain_counts = self.dataframe[domain_col].value_counts().head(top_n)
            
            # Prepare chart data
            chart_data = {
                'type': 'bar',
                'title': f'Top {top_n} Domains',
                'labels': domain_counts.index.tolist(),
                'data': domain_counts.values.tolist(),
                'colors': self._generate_colors(len(domain_counts)),
            }
            
            self.add_chart('domain_chart', chart_data)
            logger.debug(f"Generated domain chart with top {top_n} domains")
            
        except Exception as e:
            logger.error(f"Error generating domain chart: {str(e)}", exc_info=True)
        
        return self
    
    def generate_summary_stats(self) -> 'ReportBuilder':
        """Generate summary statistics from the DataFrame."""
        if self.dataframe is None:
            logger.warning("No DataFrame available for summary stats")
            return self
        
        try:
            # Total URLs
            total_urls = len(self.dataframe)
            
            # Unique domains
            domain_col = None
            for col in ['Domain', 'Domain_name', 'Hostname']:
                if col in self.dataframe.columns:
                    domain_col = col
                    break
            
            unique_domains = 0
            if domain_col:
                unique_domains = self.dataframe[domain_col].nunique()
            
            # Categories
            categories = {}
            if 'Category' in self.dataframe.columns:
                category_counts = self.dataframe['Category'].value_counts()
                for category, count in category_counts.items():
                    categories[category] = {
                        'count': int(count),
                        'percentage': round(count / total_urls * 100, 1)
                    }
            
            # Prepare stats data
            stats_data = {
                'total_urls': total_urls,
                'unique_domains': unique_domains,
                'categories': categories,
                'generated_at': datetime.now().isoformat(),
            }
            
            self.add_stat('summary_stats', stats_data)
            logger.debug("Generated summary statistics")
            
        except Exception as e:
            logger.error(f"Error generating summary stats: {str(e)}", exc_info=True)
        
        return self
    
    def _generate_colors(self, count: int) -> List[str]:
        """
        Generate a list of colors for charts.
        
        Args:
            count: Number of colors to generate
            
        Returns:
            List of color strings in hex format
        """
        # Predefined color palette
        palette = [
            '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f',
            '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'
        ]
        
        # If we need more colors than in the palette, generate them
        if count <= len(palette):
            return palette[:count]
        else:
            # Generate additional colors using HSV color space
            import colorsys
            
            colors = palette.copy()
            for i in range(len(palette), count):
                h = i / count
                s = 0.7
                v = 0.9
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                hex_color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
                colors.append(hex_color)
            
            return colors
    
    def get_report_data(self) -> Dict[str, Any]:
        """
        Get the complete report data.
        
        Returns:
            Dictionary containing all report data
        """
        # Generate DataFrame HTML if available
        df_html = None
        if self.dataframe is not None:
            df_html = self.dataframe.to_html(
                classes='table table-striped table-hover',
                index=False,
                escape=True,
                border=0
            )
        
        # Compile report data
        report_data = {
            'report_id': self.report_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'author': self.author,
            'description': self.description,
            'tags': self.tags,
            'charts': self.charts,
            'stats': self.stats,
            'metadata': self.metadata,
            'filters': self.filters,
            'df_html': df_html,
            'raw_data': self.raw_data,
            'processed_data': self.processed_data,
        }
        
        return report_data
    
    def build(self) -> Dict[str, Any]:
        """
        Build the report.
        
        Returns:
            Dictionary containing the complete report data
        """
        logger.info(f"Building report {self.report_id}: {self.title}")
        return self.get_report_data()


def create_report_builder(title: Optional[str] = None, template: Optional[str] = None) -> ReportBuilder:
    """
    Convenience function to create a new report builder.
    
    Args:
        title: Title for the report
        template: Name of the template to use
        
    Returns:
        New ReportBuilder instance
    """
    return ReportBuilder(title=title, template_name=template)