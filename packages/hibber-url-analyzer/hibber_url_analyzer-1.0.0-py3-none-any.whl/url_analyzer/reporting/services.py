"""
Reporting Services

This module provides services for reporting based on the interfaces
defined in the interfaces module. It implements the core functionality for
generating reports about URL analysis.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from threading import Lock

import pandas as pd

from url_analyzer.reporting.domain import (
    ReportTemplate, ReportData, ReportOptions, Report, ReportGenerationResult,
    ReportFormat, ReportType, ChartType, ChartOptions
)
from url_analyzer.reporting.interfaces import (
    TemplateRenderer, ChartGenerator, TemplateRepository, ReportRepository,
    ReportGenerator, ReportingService
)


class JinjaTemplateRenderer(TemplateRenderer):
    """
    Template renderer using Jinja2.
    """
    
    def __init__(self, name: str = "Jinja Template Renderer"):
        """
        Initialize the renderer.
        
        Args:
            name: Name of this renderer
        """
        self._name = name
        
        # Import Jinja2 here to allow graceful degradation if not available
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            self._jinja2_available = True
            self._env = Environment(
                loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + '/templates'),
                autoescape=select_autoescape(['html', 'xml'])
            )
        except ImportError:
            self._jinja2_available = False
            self._env = None
    
    def render_template(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """
        Render a template with data using Jinja2.
        
        Args:
            template: Template to render
            data: Data to use for rendering
            
        Returns:
            Rendered template as a string
        """
        # Check if Jinja2 is available
        if not self._jinja2_available:
            raise ImportError("Jinja2 is required for template rendering")
        
        # Check if template file exists
        if not template.file_exists:
            raise FileNotFoundError(f"Template file {template.template_path} does not exist")
        
        try:
            # Load the template
            template_obj = self._env.get_template(os.path.basename(template.template_path))
            
            # Render the template
            return template_obj.render(**data)
            
        except Exception as e:
            logging.error(f"Error rendering template: {e}")
            raise
    
    def get_supported_formats(self) -> Set[ReportFormat]:
        """
        Get the formats supported by this renderer.
        
        Returns:
            Set of supported formats
        """
        return {ReportFormat.HTML, ReportFormat.TEXT}
    
    def get_name(self) -> str:
        """
        Get the name of this renderer.
        
        Returns:
            Renderer name
        """
        return self._name


class PlotlyChartGenerator(ChartGenerator):
    """
    Chart generator using Plotly.
    """
    
    def __init__(self, name: str = "Plotly Chart Generator"):
        """
        Initialize the generator.
        
        Args:
            name: Name of this generator
        """
        self._name = name
        
        # Import Plotly here to allow graceful degradation if not available
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            self._plotly_available = True
            self._px = px
            self._go = go
        except ImportError:
            self._plotly_available = False
            self._px = None
            self._go = None
    
    def generate_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a chart from data using Plotly.
        
        Args:
            data: Data to use for the chart
            options: Options for the chart
            
        Returns:
            Chart as an HTML string
        """
        # Check if Plotly is available
        if not self._plotly_available:
            raise ImportError("Plotly is required for chart generation")
        
        try:
            # Generate the chart based on the chart type
            if options.chart_type == ChartType.BAR:
                return self._generate_bar_chart(data, options)
            elif options.chart_type == ChartType.PIE:
                return self._generate_pie_chart(data, options)
            elif options.chart_type == ChartType.LINE:
                return self._generate_line_chart(data, options)
            elif options.chart_type == ChartType.SCATTER:
                return self._generate_scatter_chart(data, options)
            else:
                raise ValueError(f"Unsupported chart type: {options.chart_type}")
            
        except Exception as e:
            logging.error(f"Error generating chart: {e}")
            raise
    
    def get_supported_chart_types(self) -> Set[ChartType]:
        """
        Get the chart types supported by this generator.
        
        Returns:
            Set of supported chart types
        """
        return {ChartType.BAR, ChartType.PIE, ChartType.LINE, ChartType.SCATTER}
    
    def get_name(self) -> str:
        """
        Get the name of this generator.
        
        Returns:
            Generator name
        """
        return self._name
    
    def _generate_bar_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a bar chart.
        
        Args:
            data: Data to use for the chart
            options: Options for the chart
            
        Returns:
            Chart as an HTML string
        """
        # Apply filters if any
        filtered_data = self._apply_filters(data, options.filters)
        
        # Create the chart
        fig = self._px.bar(
            filtered_data,
            x=options.x_axis,
            y=options.y_axis,
            color=options.color_by,
            title=options.title,
            width=options.width,
            height=options.height,
            **options.options
        )
        
        # Return the chart as HTML
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def _generate_pie_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a pie chart.
        
        Args:
            data: Data to use for the chart
            options: Options for the chart
            
        Returns:
            Chart as an HTML string
        """
        # Apply filters if any
        filtered_data = self._apply_filters(data, options.filters)
        
        # Create the chart
        fig = self._px.pie(
            filtered_data,
            names=options.x_axis,
            color=options.color_by,
            title=options.title,
            width=options.width,
            height=options.height,
            **options.options
        )
        
        # Return the chart as HTML
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def _generate_line_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a line chart.
        
        Args:
            data: Data to use for the chart
            options: Options for the chart
            
        Returns:
            Chart as an HTML string
        """
        # Apply filters if any
        filtered_data = self._apply_filters(data, options.filters)
        
        # Create the chart
        fig = self._px.line(
            filtered_data,
            x=options.x_axis,
            y=options.y_axis,
            color=options.color_by,
            title=options.title,
            width=options.width,
            height=options.height,
            **options.options
        )
        
        # Return the chart as HTML
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def _generate_scatter_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a scatter chart.
        
        Args:
            data: Data to use for the chart
            options: Options for the chart
            
        Returns:
            Chart as an HTML string
        """
        # Apply filters if any
        filtered_data = self._apply_filters(data, options.filters)
        
        # Create the chart
        fig = self._px.scatter(
            filtered_data,
            x=options.x_axis,
            y=options.y_axis,
            color=options.color_by,
            title=options.title,
            width=options.width,
            height=options.height,
            **options.options
        )
        
        # Return the chart as HTML
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def _apply_filters(self, data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to data.
        
        Args:
            data: Data to filter
            filters: Filters to apply
            
        Returns:
            Filtered data
        """
        filtered_data = data.copy()
        
        for column, value in filters.items():
            if column in filtered_data.columns:
                if isinstance(value, list):
                    filtered_data = filtered_data[filtered_data[column].isin(value)]
                else:
                    filtered_data = filtered_data[filtered_data[column] == value]
        
        return filtered_data


class FileSystemTemplateRepository(TemplateRepository):
    """
    File system implementation of the template repository.
    """
    
    def __init__(self, template_dir: str):
        """
        Initialize the repository.
        
        Args:
            template_dir: Directory containing templates
        """
        self._template_dir = template_dir
        self._templates: Dict[str, ReportTemplate] = {}
        self._lock = Lock()
        
        # Create the template directory if it doesn't exist
        os.makedirs(template_dir, exist_ok=True)
        
        # Load templates from the directory
        self._load_templates()
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            ReportTemplate or None if not found
        """
        with self._lock:
            return self._templates.get(template_id)
    
    def get_templates(self) -> List[ReportTemplate]:
        """
        Get all templates.
        
        Returns:
            List of templates
        """
        with self._lock:
            return list(self._templates.values())
    
    def get_templates_by_format(self, format: ReportFormat) -> List[ReportTemplate]:
        """
        Get templates by format.
        
        Args:
            format: Format to filter by
            
        Returns:
            List of templates with the specified format
        """
        with self._lock:
            return [t for t in self._templates.values() if t.format == format]
    
    def get_templates_by_type(self, type: ReportType) -> List[ReportTemplate]:
        """
        Get templates by type.
        
        Args:
            type: Type to filter by
            
        Returns:
            List of templates with the specified type
        """
        with self._lock:
            return [t for t in self._templates.values() if t.type == type]
    
    def add_template(self, template: ReportTemplate) -> None:
        """
        Add a template.
        
        Args:
            template: Template to add
        """
        with self._lock:
            self._templates[template.template_id] = template
    
    def remove_template(self, template_id: str) -> bool:
        """
        Remove a template.
        
        Args:
            template_id: ID of the template to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if template_id in self._templates:
                del self._templates[template_id]
                return True
            return False
    
    def _load_templates(self) -> None:
        """
        Load templates from the template directory.
        """
        # Check if the template directory exists
        if not os.path.exists(self._template_dir):
            return
        
        # Get all HTML files in the template directory
        html_files = [f for f in os.listdir(self._template_dir) if f.endswith('.html')]
        
        for html_file in html_files:
            # Create a template for each HTML file
            template_path = os.path.join(self._template_dir, html_file)
            template_name = os.path.splitext(html_file)[0]
            
            template = ReportTemplate.create_html_template(
                name=template_name,
                template_path=template_path,
                description=f"Template for {template_name} reports"
            )
            
            self._templates[template.template_id] = template


class InMemoryReportRepository(ReportRepository):
    """
    In-memory implementation of the report repository.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        """
        self._reports: Dict[str, Report] = {}
        self._lock = Lock()
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get a report by ID.
        
        Args:
            report_id: ID of the report to get
            
        Returns:
            Report or None if not found
        """
        with self._lock:
            return self._reports.get(report_id)
    
    def get_reports(self) -> List[Report]:
        """
        Get all reports.
        
        Returns:
            List of reports
        """
        with self._lock:
            return list(self._reports.values())
    
    def save_report(self, report: Report) -> None:
        """
        Save a report.
        
        Args:
            report: Report to save
        """
        with self._lock:
            self._reports[report.report_id] = report
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if report_id in self._reports:
                del self._reports[report_id]
                return True
            return False


class HTMLReportGenerator(ReportGenerator):
    """
    Report generator for HTML reports.
    """
    
    def __init__(self, 
                 template_renderer: TemplateRenderer,
                 chart_generator: Optional[ChartGenerator] = None,
                 name: str = "HTML Report Generator"):
        """
        Initialize the generator.
        
        Args:
            template_renderer: Template renderer to use
            chart_generator: Optional chart generator to use
            name: Name of this generator
        """
        self._template_renderer = template_renderer
        self._chart_generator = chart_generator
        self._name = name
    
    def generate_report(self, report: Report) -> ReportGenerationResult:
        """
        Generate an HTML report.
        
        Args:
            report: Report to generate
            
        Returns:
            ReportGenerationResult containing the result of the generation
        """
        start_time = time.time()
        
        try:
            # Check if the template format is supported
            if report.template.format != ReportFormat.HTML:
                return ReportGenerationResult(
                    report=report,
                    success=False,
                    error_message=f"Unsupported template format: {report.template.format}"
                )
            
            # Prepare the data for the template
            template_data = self._prepare_template_data(report)
            
            # Render the template
            content = self._template_renderer.render_template(report.template, template_data)
            
            # Set the content on the report
            report.set_content(content)
            
            # Write the report to the output path
            self._write_report(report)
            
            # Calculate generation time
            generation_time = time.time() - start_time
            
            # Return the result
            return ReportGenerationResult(
                report=report,
                success=True,
                generation_time=generation_time
            )
            
        except Exception as e:
            # Calculate generation time
            generation_time = time.time() - start_time
            
            # Return the result with error
            return ReportGenerationResult(
                report=report,
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )
    
    def get_supported_formats(self) -> Set[ReportFormat]:
        """
        Get the formats supported by this generator.
        
        Returns:
            Set of supported formats
        """
        return {ReportFormat.HTML}
    
    def get_name(self) -> str:
        """
        Get the name of this generator.
        
        Returns:
            Generator name
        """
        return self._name
    
    def _prepare_template_data(self, report: Report) -> Dict[str, Any]:
        """
        Prepare data for the template.
        
        Args:
            report: Report to prepare data for
            
        Returns:
            Dictionary of data for the template
        """
        # Create the base data
        data = {
            'report': {
                'id': report.report_id,
                'name': report.name,
                'title': report.options.title,
                'description': report.options.description,
                'created_at': report.created_at.isoformat(),
                'generated_at': datetime.now().isoformat()
            },
            'data': report.data.data.to_dict(orient='records'),
            'metadata': report.data.metadata,
            'options': {
                'include_summary': report.options.include_summary,
                'include_charts': report.options.include_charts,
                'include_data_table': report.options.include_data_table,
                'include_metadata': report.options.include_metadata,
                'include_timestamp': report.options.include_timestamp
            },
            'summary': self._generate_summary(report.data.data),
            'charts': []
        }
        
        # Add charts if requested and chart generator is available
        if report.options.include_charts and self._chart_generator and report.options.charts:
            for chart_options in report.options.charts:
                try:
                    chart_html = self._chart_generator.generate_chart(report.data.data, chart_options)
                    data['charts'].append({
                        'title': chart_options.title,
                        'html': chart_html
                    })
                except Exception as e:
                    logging.error(f"Error generating chart: {e}")
                    data['charts'].append({
                        'title': chart_options.title,
                        'html': f"<div class='error'>Error generating chart: {e}</div>"
                    })
        
        return data
    
    def _generate_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a summary of the data.
        
        Args:
            data: Data to summarize
            
        Returns:
            Dictionary containing the summary
        """
        # Create a basic summary
        summary = {
            'row_count': len(data),
            'column_count': len(data.columns),
            'columns': list(data.columns),
            'column_types': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'missing_values': {col: int(data[col].isna().sum()) for col in data.columns},
            'unique_values': {col: int(data[col].nunique()) for col in data.columns}
        }
        
        # Add numeric column statistics if any
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            summary['numeric_stats'] = {}
            for col in numeric_columns:
                summary['numeric_stats'][col] = {
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'mean': float(data[col].mean()),
                    'median': float(data[col].median()),
                    'std': float(data[col].std())
                }
        
        # Add categorical column statistics if any
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_columns) > 0:
            summary['categorical_stats'] = {}
            for col in categorical_columns:
                value_counts = data[col].value_counts().head(10).to_dict()
                summary['categorical_stats'][col] = {
                    'top_values': {str(k): int(v) for k, v in value_counts.items()}
                }
        
        return summary
    
    def _write_report(self, report: Report) -> None:
        """
        Write the report to the output path.
        
        Args:
            report: Report to write
        """
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(report.output_path), exist_ok=True)
        
        # Write the report
        with open(report.output_path, 'w', encoding='utf-8') as f:
            f.write(report.content)


class DefaultReportingService(ReportingService):
    """
    Default implementation of the reporting service.
    """
    
    def __init__(self,
                 template_repository: TemplateRepository,
                 report_repository: ReportRepository,
                 report_generators: Optional[List[ReportGenerator]] = None):
        """
        Initialize the service.
        
        Args:
            template_repository: Repository for templates
            report_repository: Repository for reports
            report_generators: Optional list of report generators
        """
        self._template_repository = template_repository
        self._report_repository = report_repository
        self._report_generators = report_generators or []
        
        # Create a map for faster lookup
        self._generator_map: Dict[ReportFormat, ReportGenerator] = {}
        for generator in self._report_generators:
            for format in generator.get_supported_formats():
                self._generator_map[format] = generator
    
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
        # Get the template
        template = self._template_repository.get_template(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        # Create the report
        report = Report.create(name, template, data, options, output_path)
        
        # Save the report
        self._report_repository.save_report(report)
        
        return report
    
    def generate_report(self, report_id: str) -> ReportGenerationResult:
        """
        Generate a report.
        
        Args:
            report_id: ID of the report to generate
            
        Returns:
            ReportGenerationResult containing the result of the generation
        """
        # Get the report
        report = self._report_repository.get_report(report_id)
        if not report:
            raise ValueError(f"Report with ID {report_id} not found")
        
        # Get the generator for the report format
        generator = self._generator_map.get(report.template.format)
        if not generator:
            return ReportGenerationResult(
                report=report,
                success=False,
                error_message=f"No generator found for format {report.template.format}"
            )
        
        # Generate the report
        result = generator.generate_report(report)
        
        # Save the report
        self._report_repository.save_report(report)
        
        return result
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get a report by ID.
        
        Args:
            report_id: ID of the report to get
            
        Returns:
            Report or None if not found
        """
        return self._report_repository.get_report(report_id)
    
    def get_reports(self) -> List[Report]:
        """
        Get all reports.
        
        Returns:
            List of reports
        """
        return self._report_repository.get_reports()
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            True if successful, False otherwise
        """
        return self._report_repository.delete_report(report_id)
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            ReportTemplate or None if not found
        """
        return self._template_repository.get_template(template_id)
    
    def get_templates(self) -> List[ReportTemplate]:
        """
        Get all templates.
        
        Returns:
            List of templates
        """
        return self._template_repository.get_templates()
    
    def add_template(self, template: ReportTemplate) -> None:
        """
        Add a template.
        
        Args:
            template: Template to add
        """
        self._template_repository.add_template(template)
    
    def remove_template(self, template_id: str) -> bool:
        """
        Remove a template.
        
        Args:
            template_id: ID of the template to remove
            
        Returns:
            True if successful, False otherwise
        """
        return self._template_repository.remove_template(template_id)
    
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
        return ReportData.create(name, data, metadata)