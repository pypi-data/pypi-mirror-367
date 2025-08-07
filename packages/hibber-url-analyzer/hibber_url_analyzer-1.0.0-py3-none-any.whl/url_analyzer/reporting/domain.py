"""
Reporting Domain Models

This module defines the domain models and value objects for the Reporting domain.
These models represent the core concepts in reporting and encapsulate domain logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Union
import os
import uuid

import pandas as pd


class ReportFormat(Enum):
    """Enumeration of report formats."""
    
    HTML = auto()
    PDF = auto()
    CSV = auto()
    EXCEL = auto()
    JSON = auto()
    TEXT = auto()
    CUSTOM = auto()


class ReportType(Enum):
    """Enumeration of report types."""
    
    SUMMARY = auto()
    DETAILED = auto()
    CHART = auto()
    DASHBOARD = auto()
    CUSTOM = auto()


class ChartType(Enum):
    """Enumeration of chart types."""
    
    BAR = auto()
    PIE = auto()
    LINE = auto()
    SCATTER = auto()
    HEATMAP = auto()
    TREEMAP = auto()
    GEOSPATIAL = auto()
    TIME_SERIES = auto()
    DASHBOARD = auto()
    CUSTOM = auto()


@dataclass(frozen=True)
class ReportTemplate:
    """Value object representing a report template."""
    
    template_id: str
    name: str
    description: str
    format: ReportFormat
    template_path: str
    type: ReportType
    options: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_html_template(cls, name: str, template_path: str, description: str = "", type: ReportType = ReportType.SUMMARY, options: Optional[Dict[str, Any]] = None) -> 'ReportTemplate':
        """
        Create an HTML report template.
        
        Args:
            name: Name of the template
            template_path: Path to the template file
            description: Optional description of the template
            type: Type of report this template is for
            options: Optional options for the template
            
        Returns:
            ReportTemplate instance
        """
        template_id = str(uuid.uuid4())
        options = options or {}
        
        return cls(
            template_id=template_id,
            name=name,
            description=description,
            format=ReportFormat.HTML,
            template_path=template_path,
            type=type,
            options=options
        )
    
    @property
    def file_exists(self) -> bool:
        """
        Check if the template file exists.
        
        Returns:
            True if the template file exists, False otherwise
        """
        return os.path.exists(self.template_path)


@dataclass(frozen=True)
class ReportData:
    """Value object representing data for a report."""
    
    data_id: str
    name: str
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, name: str, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> 'ReportData':
        """
        Create a report data object.
        
        Args:
            name: Name of the data
            data: DataFrame containing the data
            metadata: Optional metadata about the data
            
        Returns:
            ReportData instance
        """
        data_id = str(uuid.uuid4())
        metadata = metadata or {}
        
        return cls(
            data_id=data_id,
            name=name,
            data=data,
            metadata=metadata
        )
    
    @property
    def row_count(self) -> int:
        """
        Get the number of rows in the data.
        
        Returns:
            Number of rows
        """
        return len(self.data)
    
    @property
    def column_count(self) -> int:
        """
        Get the number of columns in the data.
        
        Returns:
            Number of columns
        """
        return len(self.data.columns)


@dataclass(frozen=True)
class ChartOptions:
    """Value object representing options for a chart."""
    
    chart_type: ChartType
    title: str
    x_axis: str
    y_axis: Optional[str] = None
    color_by: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    width: int = 800
    height: int = 600
    options: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_bar_chart(cls, title: str, x_axis: str, y_axis: str, color_by: Optional[str] = None, filters: Optional[Dict[str, Any]] = None, width: int = 800, height: int = 600, options: Optional[Dict[str, Any]] = None) -> 'ChartOptions':
        """
        Create options for a bar chart.
        
        Args:
            title: Chart title
            x_axis: Column to use for the x-axis
            y_axis: Column to use for the y-axis
            color_by: Optional column to use for coloring
            filters: Optional filters to apply to the data
            width: Chart width in pixels
            height: Chart height in pixels
            options: Optional additional options
            
        Returns:
            ChartOptions instance
        """
        filters = filters or {}
        options = options or {}
        
        return cls(
            chart_type=ChartType.BAR,
            title=title,
            x_axis=x_axis,
            y_axis=y_axis,
            color_by=color_by,
            filters=filters,
            width=width,
            height=height,
            options=options
        )
    
    @classmethod
    def create_pie_chart(cls, title: str, x_axis: str, color_by: Optional[str] = None, filters: Optional[Dict[str, Any]] = None, width: int = 800, height: int = 600, options: Optional[Dict[str, Any]] = None) -> 'ChartOptions':
        """
        Create options for a pie chart.
        
        Args:
            title: Chart title
            x_axis: Column to use for the pie segments
            color_by: Optional column to use for coloring
            filters: Optional filters to apply to the data
            width: Chart width in pixels
            height: Chart height in pixels
            options: Optional additional options
            
        Returns:
            ChartOptions instance
        """
        filters = filters or {}
        options = options or {}
        
        return cls(
            chart_type=ChartType.PIE,
            title=title,
            x_axis=x_axis,
            color_by=color_by,
            filters=filters,
            width=width,
            height=height,
            options=options
        )


@dataclass(frozen=True)
class ReportOptions:
    """Value object representing options for a report."""
    
    title: str
    description: str
    include_summary: bool = True
    include_charts: bool = True
    include_data_table: bool = True
    include_metadata: bool = True
    include_timestamp: bool = True
    charts: List[ChartOptions] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_default(cls, title: str, description: str) -> 'ReportOptions':
        """
        Create default report options.
        
        Args:
            title: Report title
            description: Report description
            
        Returns:
            ReportOptions instance
        """
        return cls(
            title=title,
            description=description
        )
    
    @classmethod
    def create_summary(cls, title: str, description: str) -> 'ReportOptions':
        """
        Create options for a summary report.
        
        Args:
            title: Report title
            description: Report description
            
        Returns:
            ReportOptions instance
        """
        return cls(
            title=title,
            description=description,
            include_charts=False,
            include_data_table=False
        )
    
    @classmethod
    def create_detailed(cls, title: str, description: str) -> 'ReportOptions':
        """
        Create options for a detailed report.
        
        Args:
            title: Report title
            description: Report description
            
        Returns:
            ReportOptions instance
        """
        return cls(
            title=title,
            description=description,
            include_summary=True,
            include_charts=True,
            include_data_table=True,
            include_metadata=True
        )


@dataclass
class Report:
    """Entity representing a report."""
    
    report_id: str
    name: str
    template: ReportTemplate
    data: ReportData
    options: ReportOptions
    output_path: str
    created_at: datetime = field(default_factory=datetime.now)
    generated_at: Optional[datetime] = None
    content: Optional[str] = None
    
    @classmethod
    def create(cls, name: str, template: ReportTemplate, data: ReportData, options: ReportOptions, output_path: str) -> 'Report':
        """
        Create a new report.
        
        Args:
            name: Name of the report
            template: Template to use for the report
            data: Data to include in the report
            options: Options for the report
            output_path: Path where the report will be saved
            
        Returns:
            Report instance
        """
        report_id = str(uuid.uuid4())
        
        return cls(
            report_id=report_id,
            name=name,
            template=template,
            data=data,
            options=options,
            output_path=output_path
        )
    
    def set_content(self, content: str) -> None:
        """
        Set the content of the report.
        
        Args:
            content: Report content
        """
        self.content = content
        self.generated_at = datetime.now()
    
    @property
    def is_generated(self) -> bool:
        """
        Check if the report has been generated.
        
        Returns:
            True if the report has been generated, False otherwise
        """
        return self.generated_at is not None and self.content is not None
    
    @property
    def file_exists(self) -> bool:
        """
        Check if the report file exists.
        
        Returns:
            True if the report file exists, False otherwise
        """
        return os.path.exists(self.output_path)


@dataclass(frozen=True)
class ReportGenerationResult:
    """Value object representing the result of report generation."""
    
    report: Report
    success: bool
    error_message: Optional[str] = None
    generation_time: float = 0.0
    
    @property
    def is_success(self) -> bool:
        """
        Check if the report generation was successful.
        
        Returns:
            True if the report generation was successful, False otherwise
        """
        return self.success and self.error_message is None