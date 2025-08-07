"""
Export Profiles Module

This module provides predefined export profiles for common use cases,
making it easier to export URL analysis data in standardized formats.
"""

import os
import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import pandas as pd

from url_analyzer.utils.logging import get_logger
from url_analyzer.data.export import export_data, export_filtered_data
from url_analyzer.data.scheduler import schedule_export

# Initialize logger
logger = get_logger(__name__)


class ExportProfile:
    """
    A profile for exporting URL analysis data with predefined settings.
    
    This class encapsulates export settings for a specific use case,
    making it easier to export data in a standardized format.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        format: str,
        filters: Optional[Dict[str, Any]] = None,
        filter_mode: str = 'exact',
        title: str = "URL Analysis Results",
        columns: Optional[List[str]] = None,
        sort_by: Optional[List[str]] = None,
        ascending: Union[bool, List[bool]] = True,
        max_rows: Optional[int] = None,
        output_dir: str = "reports",
        filename_template: str = "{name}_{timestamp}"
    ):
        """
        Initialize an export profile.
        
        Args:
            name: Profile name
            description: Profile description
            format: Export format ('csv', 'json', 'excel', 'xml', 'html', or 'markdown')
            filters: Dictionary of column-value pairs for filtering
            filter_mode: Filtering mode ('exact', 'contains', 'regex', 'range')
            title: Title for the document (used for HTML and Markdown formats)
            columns: List of columns to include (if None, includes all columns)
            sort_by: List of columns to sort by (if None, no sorting is applied)
            ascending: Whether to sort in ascending order (can be a list for multiple sort columns)
            max_rows: Maximum number of rows to export (if None, exports all rows)
            output_dir: Directory where to save the exported files
            filename_template: Template for the output filename
                               Available variables: {name}, {timestamp}, {format}
        """
        self.name = name
        self.description = description
        self.format = format
        self.filters = filters
        self.filter_mode = filter_mode
        self.title = title
        self.columns = columns
        self.sort_by = sort_by
        self.ascending = ascending
        self.max_rows = max_rows
        self.output_dir = output_dir
        self.filename_template = filename_template
    
    def export(
        self,
        df: pd.DataFrame,
        output_path: Optional[str] = None,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export data using this profile.
        
        Args:
            df: DataFrame to export
            output_path: Custom output path (if None, uses the profile's output_dir and filename_template)
            additional_filters: Additional filters to apply (combined with the profile's filters)
            
        Returns:
            Path to the exported file
        """
        # Make a copy of the DataFrame to avoid modifying the original
        export_df = df.copy()
        
        # Apply column selection if specified
        if self.columns:
            # Keep only columns that exist in the DataFrame
            valid_columns = [col for col in self.columns if col in export_df.columns]
            if valid_columns:
                export_df = export_df[valid_columns]
            else:
                logger.warning(f"None of the specified columns {self.columns} exist in the DataFrame")
        
        # Apply sorting if specified
        if self.sort_by:
            # Keep only sort columns that exist in the DataFrame
            valid_sort_columns = [col for col in self.sort_by if col in export_df.columns]
            if valid_sort_columns:
                export_df = export_df.sort_values(by=valid_sort_columns, ascending=self.ascending)
            else:
                logger.warning(f"None of the specified sort columns {self.sort_by} exist in the DataFrame")
        
        # Apply row limit if specified
        if self.max_rows and self.max_rows > 0:
            export_df = export_df.head(self.max_rows)
        
        # Generate output path if not provided
        if not output_path:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Generate filename from template
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.filename_template.format(
                name=self.name,
                timestamp=timestamp,
                format=self.format
            )
            
            # Add extension if not present
            if not filename.lower().endswith(f'.{self.format}'):
                filename = f"{filename}.{self.format}"
            
            output_path = os.path.join(self.output_dir, filename)
        
        # Combine filters if additional filters are provided
        filters = self.filters
        if additional_filters:
            if filters:
                filters = {**filters, **additional_filters}
            else:
                filters = additional_filters
        
        # Export the data
        if filters:
            result_path = export_filtered_data(
                export_df,
                output_path,
                self.format,
                filters,
                self.filter_mode,
                self.title
            )
        else:
            result_path = export_data(
                export_df,
                output_path,
                self.format,
                self.title
            )
        
        return result_path
    
    def schedule(
        self,
        df: pd.DataFrame,
        interval: int = 86400,  # Default: daily (24 hours)
        start_time: Optional[datetime.datetime] = None,
        task_id: Optional[str] = None,
        output_path: Optional[str] = None,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule exports using this profile.
        
        Args:
            df: DataFrame to export
            interval: Export interval in seconds
            start_time: When to start the first export (if None, starts immediately)
            task_id: Unique identifier for the task (if None, generates one)
            output_path: Custom output path (if None, uses the profile's output_dir and filename_template)
            additional_filters: Additional filters to apply (combined with the profile's filters)
            
        Returns:
            Task ID
        """
        # Generate output path if not provided
        if not output_path:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Generate filename from template with {timestamp} placeholder
            filename = self.filename_template.format(
                name=self.name,
                timestamp="{timestamp}",
                format=self.format
            )
            
            # Add extension if not present
            if not filename.lower().endswith(f'.{self.format}'):
                filename = f"{filename}.{self.format}"
            
            output_path = os.path.join(self.output_dir, filename)
        
        # Combine filters if additional filters are provided
        filters = self.filters
        if additional_filters:
            if filters:
                filters = {**filters, **additional_filters}
            else:
                filters = additional_filters
        
        # Apply column selection if specified
        if self.columns:
            # Keep only columns that exist in the DataFrame
            valid_columns = [col for col in self.columns if col in df.columns]
            if valid_columns:
                df = df[valid_columns]
            else:
                logger.warning(f"None of the specified columns {self.columns} exist in the DataFrame")
        
        # Apply sorting if specified
        if self.sort_by:
            # Keep only sort columns that exist in the DataFrame
            valid_sort_columns = [col for col in self.sort_by if col in df.columns]
            if valid_sort_columns:
                df = df.sort_values(by=valid_sort_columns, ascending=self.ascending)
            else:
                logger.warning(f"None of the specified sort columns {self.sort_by} exist in the DataFrame")
        
        # Apply row limit if specified
        if self.max_rows and self.max_rows > 0:
            df = df.head(self.max_rows)
        
        # Schedule the export
        return schedule_export(
            df,
            output_path,
            self.format,
            interval,
            filters,
            self.filter_mode,
            self.title,
            start_time,
            task_id
        )


# Predefined export profiles

# Security audit profile
SECURITY_AUDIT_PROFILE = ExportProfile(
    name="security_audit",
    description="Security audit report with sensitive URLs",
    format="excel",
    filters={"Is_Sensitive": True},
    filter_mode="exact",
    title="Security Audit Report - Sensitive URLs",
    columns=["Domain_name", "Category", "Access_time", "Client_Name", "MAC_address"],
    sort_by=["Access_time"],
    ascending=False,
    output_dir="reports/security",
    filename_template="security_audit_{timestamp}"
)

# Executive summary profile
EXECUTIVE_SUMMARY_PROFILE = ExportProfile(
    name="executive_summary",
    description="Executive summary report with high-level statistics",
    format="html",
    title="URL Analysis Executive Summary",
    columns=["Domain_name", "Category", "Access_time"],
    sort_by=["Category", "Access_time"],
    max_rows=100,
    output_dir="reports/executive",
    filename_template="executive_summary_{timestamp}"
)

# Detailed analysis profile
DETAILED_ANALYSIS_PROFILE = ExportProfile(
    name="detailed_analysis",
    description="Detailed analysis report with all data",
    format="csv",
    title="Detailed URL Analysis",
    sort_by=["Domain_name", "Access_time"],
    output_dir="reports/detailed",
    filename_template="detailed_analysis_{timestamp}"
)

# Junk traffic profile
JUNK_TRAFFIC_PROFILE = ExportProfile(
    name="junk_traffic",
    description="Report of junk traffic (ads, analytics, etc.)",
    format="json",
    filters={"Category": "Junk"},
    filter_mode="exact",
    title="Junk Traffic Analysis",
    columns=["Domain_name", "Subcategory", "Access_time", "Client_Name"],
    sort_by=["Subcategory", "Domain_name"],
    output_dir="reports/junk",
    filename_template="junk_traffic_{timestamp}"
)

# User activity profile
USER_ACTIVITY_PROFILE = ExportProfile(
    name="user_activity",
    description="User activity report grouped by client",
    format="markdown",
    title="User Activity Report",
    columns=["Client_Name", "Domain_name", "Category", "Access_time"],
    sort_by=["Client_Name", "Access_time"],
    output_dir="reports/users",
    filename_template="user_activity_{timestamp}"
)

# Domain summary profile
DOMAIN_SUMMARY_PROFILE = ExportProfile(
    name="domain_summary",
    description="Summary of domains by category",
    format="html",
    title="Domain Category Summary",
    columns=["Domain_name", "Category", "Subcategory", "Is_Sensitive"],
    sort_by=["Category", "Subcategory", "Domain_name"],
    output_dir="reports/domains",
    filename_template="domain_summary_{timestamp}"
)

# All predefined profiles
PREDEFINED_PROFILES = {
    "security_audit": SECURITY_AUDIT_PROFILE,
    "executive_summary": EXECUTIVE_SUMMARY_PROFILE,
    "detailed_analysis": DETAILED_ANALYSIS_PROFILE,
    "junk_traffic": JUNK_TRAFFIC_PROFILE,
    "user_activity": USER_ACTIVITY_PROFILE,
    "domain_summary": DOMAIN_SUMMARY_PROFILE
}


def get_profile(name: str) -> Optional[ExportProfile]:
    """
    Get a predefined export profile by name.
    
    Args:
        name: Profile name
        
    Returns:
        ExportProfile instance or None if not found
    """
    return PREDEFINED_PROFILES.get(name)


def list_profiles() -> Dict[str, str]:
    """
    List all predefined export profiles.
    
    Returns:
        Dictionary of profile names and descriptions
    """
    return {name: profile.description for name, profile in PREDEFINED_PROFILES.items()}


def export_with_profile(
    name: str,
    df: pd.DataFrame,
    output_path: Optional[str] = None,
    additional_filters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Export data using a predefined profile.
    
    Args:
        name: Profile name
        df: DataFrame to export
        output_path: Custom output path (if None, uses the profile's output_dir and filename_template)
        additional_filters: Additional filters to apply (combined with the profile's filters)
        
    Returns:
        Path to the exported file or empty string if profile not found
    """
    profile = get_profile(name)
    
    if profile:
        return profile.export(df, output_path, additional_filters)
    else:
        logger.error(f"Profile '{name}' not found")
        return ""


def schedule_with_profile(
    name: str,
    df: pd.DataFrame,
    interval: int = 86400,  # Default: daily (24 hours)
    start_time: Optional[datetime.datetime] = None,
    task_id: Optional[str] = None,
    output_path: Optional[str] = None,
    additional_filters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Schedule exports using a predefined profile.
    
    Args:
        name: Profile name
        df: DataFrame to export
        interval: Export interval in seconds
        start_time: When to start the first export (if None, starts immediately)
        task_id: Unique identifier for the task (if None, generates one)
        output_path: Custom output path (if None, uses the profile's output_dir and filename_template)
        additional_filters: Additional filters to apply (combined with the profile's filters)
        
    Returns:
        Task ID or empty string if profile not found
    """
    profile = get_profile(name)
    
    if profile:
        return profile.schedule(df, interval, start_time, task_id, output_path, additional_filters)
    else:
        logger.error(f"Profile '{name}' not found")
        return ""