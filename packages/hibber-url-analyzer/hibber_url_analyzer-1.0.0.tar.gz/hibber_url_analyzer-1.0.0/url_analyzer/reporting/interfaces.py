"""
Reporting Interfaces

This module defines interfaces for the Reporting domain.
These interfaces ensure proper separation of concerns and enable dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union

import pandas as pd

from url_analyzer.reporting.domain import (
    ReportTemplate, ReportData, ReportOptions, Report, ReportGenerationResult,
    ReportFormat, ReportType, ChartType, ChartOptions
)


class TemplateRenderer(ABC):
    """Interface for template renderers."""
    
    @abstractmethod
    def render_template(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """
        Render a template with data.
        
        Args:
            template: Template to render
            data: Data to use for rendering
            
        Returns:
            Rendered template as a string
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> Set[ReportFormat]:
        """
        Get the formats supported by this renderer.
        
        Returns:
            Set of supported formats
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this renderer.
        
        Returns:
            Renderer name
        """
        pass


class ChartGenerator(ABC):
    """Interface for chart generators."""
    
    @abstractmethod
    def generate_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a chart from data.
        
        Args:
            data: Data to use for the chart
            options: Options for the chart
            
        Returns:
            Chart as a string (e.g., HTML, SVG, etc.)
        """
        pass
    
    @abstractmethod
    def get_supported_chart_types(self) -> Set[ChartType]:
        """
        Get the chart types supported by this generator.
        
        Returns:
            Set of supported chart types
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this generator.
        
        Returns:
            Generator name
        """
        pass


class TemplateRepository(ABC):
    """Interface for template repositories."""
    
    @abstractmethod
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            ReportTemplate or None if not found
        """
        pass
    
    @abstractmethod
    def get_templates(self) -> List[ReportTemplate]:
        """
        Get all templates.
        
        Returns:
            List of templates
        """
        pass
    
    @abstractmethod
    def get_templates_by_format(self, format: ReportFormat) -> List[ReportTemplate]:
        """
        Get templates by format.
        
        Args:
            format: Format to filter by
            
        Returns:
            List of templates with the specified format
        """
        pass
    
    @abstractmethod
    def get_templates_by_type(self, type: ReportType) -> List[ReportTemplate]:
        """
        Get templates by type.
        
        Args:
            type: Type to filter by
            
        Returns:
            List of templates with the specified type
        """
        pass
    
    @abstractmethod
    def add_template(self, template: ReportTemplate) -> None:
        """
        Add a template.
        
        Args:
            template: Template to add
        """
        pass
    
    @abstractmethod
    def remove_template(self, template_id: str) -> bool:
        """
        Remove a template.
        
        Args:
            template_id: ID of the template to remove
            
        Returns:
            True if successful, False otherwise
        """
        pass


class ReportRepository(ABC):
    """Interface for report repositories."""
    
    @abstractmethod
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get a report by ID.
        
        Args:
            report_id: ID of the report to get
            
        Returns:
            Report or None if not found
        """
        pass
    
    @abstractmethod
    def get_reports(self) -> List[Report]:
        """
        Get all reports.
        
        Returns:
            List of reports
        """
        pass
    
    @abstractmethod
    def save_report(self, report: Report) -> None:
        """
        Save a report.
        
        Args:
            report: Report to save
        """
        pass
    
    @abstractmethod
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass


class ReportGenerator(ABC):
    """Interface for report generators."""
    
    @abstractmethod
    def generate_report(self, report: Report) -> ReportGenerationResult:
        """
        Generate a report.
        
        Args:
            report: Report to generate
            
        Returns:
            ReportGenerationResult containing the result of the generation
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> Set[ReportFormat]:
        """
        Get the formats supported by this generator.
        
        Returns:
            Set of supported formats
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this generator.
        
        Returns:
            Generator name
        """
        pass


class ReportingService(ABC):
    """Interface for reporting services."""
    
    @abstractmethod
    def create_report(self, name: str, template_id: str, data: ReportData, options: ReportOptions, output_path: str) -> Report:
        """
        Create a new report.
        
        Args:
            name: Name of the report
            template_id: ID of the template to use
            data: Data to include in the report
            options: Options for the report
            output_path: Path where the report will be saved
            
        Returns:
            Report instance
        """
        pass
    
    @abstractmethod
    def generate_report(self, report_id: str) -> ReportGenerationResult:
        """
        Generate a report.
        
        Args:
            report_id: ID of the report to generate
            
        Returns:
            ReportGenerationResult containing the result of the generation
        """
        pass
    
    @abstractmethod
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get a report by ID.
        
        Args:
            report_id: ID of the report to get
            
        Returns:
            Report or None if not found
        """
        pass
    
    @abstractmethod
    def get_reports(self) -> List[Report]:
        """
        Get all reports.
        
        Returns:
            List of reports
        """
        pass
    
    @abstractmethod
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            ReportTemplate or None if not found
        """
        pass
    
    @abstractmethod
    def get_templates(self) -> List[ReportTemplate]:
        """
        Get all templates.
        
        Returns:
            List of templates
        """
        pass
    
    @abstractmethod
    def add_template(self, template: ReportTemplate) -> None:
        """
        Add a template.
        
        Args:
            template: Template to add
        """
        pass
    
    @abstractmethod
    def remove_template(self, template_id: str) -> bool:
        """
        Remove a template.
        
        Args:
            template_id: ID of the template to remove
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_report_data(self, name: str, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> ReportData:
        """
        Create report data.
        
        Args:
            name: Name of the data
            data: DataFrame containing the data
            metadata: Optional metadata about the data
            
        Returns:
            ReportData instance
        """
        pass