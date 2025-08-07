"""
Report Builders Module

This module provides functionality for building custom reports with
configurable components and layouts.
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Set, Callable
import uuid

import pandas as pd

from url_analyzer.reporting.domain import (
    ReportTemplate, ReportData, ReportOptions, Report, ReportFormat, ReportType,
    ChartType, ChartOptions
)
from url_analyzer.reporting.interfaces import TemplateRenderer, ChartGenerator
from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


class ReportComponent:
    """
    Base class for report components.
    
    Report components are the building blocks of custom reports, such as
    charts, tables, text sections, etc.
    """
    
    def __init__(
        self,
        component_id: str,
        component_type: str,
        title: str,
        description: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a report component.
        
        Args:
            component_id: Unique identifier for the component
            component_type: Type of the component
            title: Title of the component
            description: Description of the component
            options: Additional options for the component
        """
        self.component_id = component_id
        self.component_type = component_type
        self.title = title
        self.description = description
        self.options = options or {}
    
    def render(self, data: pd.DataFrame, context: Dict[str, Any]) -> str:
        """
        Render the component.
        
        Args:
            data: Data to use for rendering
            context: Additional context for rendering
            
        Returns:
            Rendered component as a string
        """
        raise NotImplementedError("Subclasses must implement render()")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the component to a dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "title": self.title,
            "description": self.description,
            "options": self.options
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportComponent':
        """
        Create a component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            ReportComponent object
        """
        component_type = data.get("component_type", "")
        
        # Create the appropriate component type
        if component_type == "chart":
            return ChartComponent.from_dict(data)
        elif component_type == "table":
            return TableComponent.from_dict(data)
        elif component_type == "text":
            return TextComponent.from_dict(data)
        elif component_type == "summary":
            return SummaryComponent.from_dict(data)
        else:
            # Default to base component
            return cls(
                component_id=data.get("component_id", f"component-{uuid.uuid4()}"),
                component_type=component_type,
                title=data.get("title", ""),
                description=data.get("description", ""),
                options=data.get("options", {})
            )


class ChartComponent(ReportComponent):
    """
    Component for displaying charts in reports.
    """
    
    def __init__(
        self,
        component_id: str,
        title: str,
        chart_type: ChartType,
        x_axis: str,
        y_axis: Optional[str] = None,
        color_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        width: int = 800,
        height: int = 400,
        description: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a chart component.
        
        Args:
            component_id: Unique identifier for the component
            title: Title of the chart
            chart_type: Type of chart to display
            x_axis: Column to use for the x-axis
            y_axis: Column to use for the y-axis
            color_by: Column to use for coloring
            filters: Filters to apply to the data
            width: Width of the chart in pixels
            height: Height of the chart in pixels
            description: Description of the chart
            options: Additional options for the chart
        """
        super().__init__(
            component_id=component_id,
            component_type="chart",
            title=title,
            description=description,
            options=options
        )
        
        self.chart_type = chart_type
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.color_by = color_by
        self.filters = filters or {}
        self.width = width
        self.height = height
    
    def render(self, data: pd.DataFrame, context: Dict[str, Any]) -> str:
        """
        Render the chart component.
        
        Args:
            data: Data to use for the chart
            context: Additional context for rendering
            
        Returns:
            Rendered chart as an HTML string
        """
        # Get the chart generator from context
        chart_generator = context.get("chart_generator")
        if not chart_generator:
            return f"<div class='error'>Chart generator not available</div>"
        
        # Create chart options
        chart_options = ChartOptions(
            chart_type=self.chart_type,
            title=self.title,
            x_axis=self.x_axis,
            y_axis=self.y_axis,
            color_by=self.color_by,
            filters=self.filters,
            width=self.width,
            height=self.height,
            options=self.options
        )
        
        try:
            # Generate the chart
            chart_html = chart_generator.generate_chart(data, chart_options)
            
            # Wrap the chart in a component container
            return f"""
            <div class="report-component chart-component" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="chart-container">
                    {chart_html}
                </div>
            </div>
            """
        except Exception as e:
            logger.error(f"Error rendering chart component: {str(e)}")
            return f"""
            <div class="report-component chart-component error" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="error-message">Error generating chart: {str(e)}</div>
            </div>
            """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chart component to a dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        data = super().to_dict()
        data.update({
            "chart_type": self.chart_type.name,
            "x_axis": self.x_axis,
            "y_axis": self.y_axis,
            "color_by": self.color_by,
            "filters": self.filters,
            "width": self.width,
            "height": self.height
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChartComponent':
        """
        Create a chart component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            ChartComponent object
        """
        # Convert chart type from string to enum
        chart_type_str = data.get("chart_type", "BAR")
        try:
            chart_type = ChartType[chart_type_str]
        except (KeyError, TypeError):
            chart_type = ChartType.BAR
        
        return cls(
            component_id=data.get("component_id", f"chart-{uuid.uuid4()}"),
            title=data.get("title", ""),
            chart_type=chart_type,
            x_axis=data.get("x_axis", ""),
            y_axis=data.get("y_axis"),
            color_by=data.get("color_by"),
            filters=data.get("filters", {}),
            width=data.get("width", 800),
            height=data.get("height", 400),
            description=data.get("description", ""),
            options=data.get("options", {})
        )


class TableComponent(ReportComponent):
    """
    Component for displaying tables in reports.
    """
    
    def __init__(
        self,
        component_id: str,
        title: str,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_ascending: bool = True,
        max_rows: Optional[int] = None,
        description: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a table component.
        
        Args:
            component_id: Unique identifier for the component
            title: Title of the table
            columns: Columns to include in the table
            filters: Filters to apply to the data
            sort_by: Column to sort by
            sort_ascending: Whether to sort in ascending order
            max_rows: Maximum number of rows to display
            description: Description of the table
            options: Additional options for the table
        """
        super().__init__(
            component_id=component_id,
            component_type="table",
            title=title,
            description=description,
            options=options
        )
        
        self.columns = columns
        self.filters = filters or {}
        self.sort_by = sort_by
        self.sort_ascending = sort_ascending
        self.max_rows = max_rows
    
    def render(self, data: pd.DataFrame, context: Dict[str, Any]) -> str:
        """
        Render the table component.
        
        Args:
            data: Data to use for the table
            context: Additional context for rendering
            
        Returns:
            Rendered table as an HTML string
        """
        try:
            # Apply filters
            filtered_data = data.copy()
            for column, value in self.filters.items():
                if column in filtered_data.columns:
                    if isinstance(value, list):
                        filtered_data = filtered_data[filtered_data[column].isin(value)]
                    else:
                        filtered_data = filtered_data[filtered_data[column] == value]
            
            # Select columns if specified
            if self.columns:
                # Only include columns that exist in the data
                valid_columns = [col for col in self.columns if col in filtered_data.columns]
                if valid_columns:
                    filtered_data = filtered_data[valid_columns]
            
            # Sort if specified
            if self.sort_by and self.sort_by in filtered_data.columns:
                filtered_data = filtered_data.sort_values(
                    by=self.sort_by,
                    ascending=self.sort_ascending
                )
            
            # Limit rows if specified
            if self.max_rows is not None:
                filtered_data = filtered_data.head(self.max_rows)
            
            # Convert to HTML
            table_html = filtered_data.to_html(
                index=False,
                classes="table table-striped table-hover",
                border=0
            )
            
            # Wrap the table in a component container
            return f"""
            <div class="report-component table-component" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="table-container">
                    {table_html}
                </div>
            </div>
            """
        except Exception as e:
            logger.error(f"Error rendering table component: {str(e)}")
            return f"""
            <div class="report-component table-component error" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="error-message">Error generating table: {str(e)}</div>
            </div>
            """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the table component to a dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        data = super().to_dict()
        data.update({
            "columns": self.columns,
            "filters": self.filters,
            "sort_by": self.sort_by,
            "sort_ascending": self.sort_ascending,
            "max_rows": self.max_rows
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TableComponent':
        """
        Create a table component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            TableComponent object
        """
        return cls(
            component_id=data.get("component_id", f"table-{uuid.uuid4()}"),
            title=data.get("title", ""),
            columns=data.get("columns"),
            filters=data.get("filters", {}),
            sort_by=data.get("sort_by"),
            sort_ascending=data.get("sort_ascending", True),
            max_rows=data.get("max_rows"),
            description=data.get("description", ""),
            options=data.get("options", {})
        )


class TextComponent(ReportComponent):
    """
    Component for displaying text in reports.
    """
    
    def __init__(
        self,
        component_id: str,
        title: str,
        content: str,
        format: str = "html",
        description: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a text component.
        
        Args:
            component_id: Unique identifier for the component
            title: Title of the text component
            content: Text content
            format: Format of the content (html, markdown, plain)
            description: Description of the text component
            options: Additional options for the text component
        """
        super().__init__(
            component_id=component_id,
            component_type="text",
            title=title,
            description=description,
            options=options
        )
        
        self.content = content
        self.format = format
    
    def render(self, data: pd.DataFrame, context: Dict[str, Any]) -> str:
        """
        Render the text component.
        
        Args:
            data: Data to use for rendering
            context: Additional context for rendering
            
        Returns:
            Rendered text as an HTML string
        """
        try:
            # Process content based on format
            processed_content = self._process_content(data, context)
            
            # Wrap the content in a component container
            return f"""
            <div class="report-component text-component" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="text-content">
                    {processed_content}
                </div>
            </div>
            """
        except Exception as e:
            logger.error(f"Error rendering text component: {str(e)}")
            return f"""
            <div class="report-component text-component error" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="error-message">Error processing text: {str(e)}</div>
            </div>
            """
    
    def _process_content(self, data: pd.DataFrame, context: Dict[str, Any]) -> str:
        """
        Process the content based on its format.
        
        Args:
            data: Data to use for processing
            context: Additional context for processing
            
        Returns:
            Processed content as an HTML string
        """
        if self.format == "markdown":
            try:
                import markdown
                return markdown.markdown(self.content)
            except ImportError:
                logger.warning("Markdown package not available, using plain text")
                return f"<pre>{self.content}</pre>"
        elif self.format == "plain":
            return f"<pre>{self.content}</pre>"
        else:
            # Default to HTML
            return self.content
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the text component to a dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        data = super().to_dict()
        data.update({
            "content": self.content,
            "format": self.format
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextComponent':
        """
        Create a text component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            TextComponent object
        """
        return cls(
            component_id=data.get("component_id", f"text-{uuid.uuid4()}"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            format=data.get("format", "html"),
            description=data.get("description", ""),
            options=data.get("options", {})
        )


class SummaryComponent(ReportComponent):
    """
    Component for displaying data summaries in reports.
    """
    
    def __init__(
        self,
        component_id: str,
        title: str,
        metrics: List[Dict[str, Any]],
        description: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a summary component.
        
        Args:
            component_id: Unique identifier for the component
            title: Title of the summary component
            metrics: List of metrics to display
            description: Description of the summary component
            options: Additional options for the summary component
        """
        super().__init__(
            component_id=component_id,
            component_type="summary",
            title=title,
            description=description,
            options=options
        )
        
        self.metrics = metrics
    
    def render(self, data: pd.DataFrame, context: Dict[str, Any]) -> str:
        """
        Render the summary component.
        
        Args:
            data: Data to use for the summary
            context: Additional context for rendering
            
        Returns:
            Rendered summary as an HTML string
        """
        try:
            # Calculate metrics
            calculated_metrics = []
            for metric in self.metrics:
                metric_name = metric.get("name", "")
                metric_type = metric.get("type", "")
                metric_column = metric.get("column", "")
                metric_format = metric.get("format", "{:.2f}")
                metric_description = metric.get("description", "")
                
                # Skip if column doesn't exist
                if metric_column and metric_column not in data.columns:
                    calculated_metrics.append({
                        "name": metric_name,
                        "value": "N/A",
                        "description": metric_description,
                        "error": f"Column '{metric_column}' not found"
                    })
                    continue
                
                # Calculate metric value
                try:
                    if metric_type == "count":
                        value = len(data)
                    elif metric_type == "sum":
                        value = data[metric_column].sum()
                    elif metric_type == "mean":
                        value = data[metric_column].mean()
                    elif metric_type == "median":
                        value = data[metric_column].median()
                    elif metric_type == "min":
                        value = data[metric_column].min()
                    elif metric_type == "max":
                        value = data[metric_column].max()
                    elif metric_type == "std":
                        value = data[metric_column].std()
                    elif metric_type == "unique":
                        value = data[metric_column].nunique()
                    elif metric_type == "custom":
                        # Custom metric using a formula
                        formula = metric.get("formula", "")
                        if formula:
                            # Create a safe environment for evaluation
                            env = {"df": data, "pd": pd, "np": pd.np}
                            value = eval(formula, {"__builtins__": {}}, env)
                        else:
                            value = "N/A"
                    else:
                        value = "N/A"
                    
                    # Format the value
                    if isinstance(value, (int, float)):
                        formatted_value = metric_format.format(value)
                    else:
                        formatted_value = str(value)
                    
                    calculated_metrics.append({
                        "name": metric_name,
                        "value": formatted_value,
                        "description": metric_description
                    })
                except Exception as e:
                    calculated_metrics.append({
                        "name": metric_name,
                        "value": "Error",
                        "description": metric_description,
                        "error": str(e)
                    })
            
            # Generate HTML for metrics
            metrics_html = ""
            for metric in calculated_metrics:
                error_class = " error" if "error" in metric else ""
                error_msg = f"<div class='metric-error'>{metric.get('error', '')}</div>" if "error" in metric else ""
                
                metrics_html += f"""
                <div class="metric{error_class}">
                    <div class="metric-name">{metric['name']}</div>
                    <div class="metric-value">{metric['value']}</div>
                    <div class="metric-description">{metric['description']}</div>
                    {error_msg}
                </div>
                """
            
            # Wrap the metrics in a component container
            return f"""
            <div class="report-component summary-component" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="metrics-container">
                    {metrics_html}
                </div>
            </div>
            """
        except Exception as e:
            logger.error(f"Error rendering summary component: {str(e)}")
            return f"""
            <div class="report-component summary-component error" id="{self.component_id}">
                <h3 class="component-title">{self.title}</h3>
                <div class="component-description">{self.description}</div>
                <div class="error-message">Error generating summary: {str(e)}</div>
            </div>
            """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the summary component to a dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        data = super().to_dict()
        data.update({
            "metrics": self.metrics
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SummaryComponent':
        """
        Create a summary component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            SummaryComponent object
        """
        return cls(
            component_id=data.get("component_id", f"summary-{uuid.uuid4()}"),
            title=data.get("title", ""),
            metrics=data.get("metrics", []),
            description=data.get("description", ""),
            options=data.get("options", {})
        )


class ReportLayout:
    """
    Defines the layout of components in a report.
    """
    
    def __init__(
        self,
        layout_id: str,
        name: str,
        description: str = "",
        sections: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a report layout.
        
        Args:
            layout_id: Unique identifier for the layout
            name: Name of the layout
            description: Description of the layout
            sections: List of layout sections
        """
        self.layout_id = layout_id
        self.name = name
        self.description = description
        self.sections = sections or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the layout to a dictionary.
        
        Returns:
            Dictionary representation of the layout
        """
        return {
            "layout_id": self.layout_id,
            "name": self.name,
            "description": self.description,
            "sections": self.sections
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportLayout':
        """
        Create a layout from a dictionary.
        
        Args:
            data: Dictionary representation of the layout
            
        Returns:
            ReportLayout object
        """
        return cls(
            layout_id=data.get("layout_id", f"layout-{uuid.uuid4()}"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            sections=data.get("sections", [])
        )


class CustomReportBuilder:
    """
    Builder for creating custom reports with configurable components and layouts.
    """
    
    def __init__(
        self,
        template_renderer: TemplateRenderer,
        chart_generator: Optional[ChartGenerator] = None
    ):
        """
        Initialize the report builder.
        
        Args:
            template_renderer: Renderer for templates
            chart_generator: Generator for charts
        """
        self.template_renderer = template_renderer
        self.chart_generator = chart_generator
        self.components: Dict[str, ReportComponent] = {}
        self.layouts: Dict[str, ReportLayout] = {}
    
    def add_component(self, component: ReportComponent) -> None:
        """
        Add a component to the builder.
        
        Args:
            component: Component to add
        """
        self.components[component.component_id] = component
    
    def get_component(self, component_id: str) -> Optional[ReportComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: ID of the component
            
        Returns:
            ReportComponent or None if not found
        """
        return self.components.get(component_id)
    
    def remove_component(self, component_id: str) -> bool:
        """
        Remove a component.
        
        Args:
            component_id: ID of the component to remove
            
        Returns:
            True if the component was removed, False otherwise
        """
        if component_id in self.components:
            del self.components[component_id]
            return True
        return False
    
    def add_layout(self, layout: ReportLayout) -> None:
        """
        Add a layout to the builder.
        
        Args:
            layout: Layout to add
        """
        self.layouts[layout.layout_id] = layout
    
    def get_layout(self, layout_id: str) -> Optional[ReportLayout]:
        """
        Get a layout by ID.
        
        Args:
            layout_id: ID of the layout
            
        Returns:
            ReportLayout or None if not found
        """
        return self.layouts.get(layout_id)
    
    def remove_layout(self, layout_id: str) -> bool:
        """
        Remove a layout.
        
        Args:
            layout_id: ID of the layout to remove
            
        Returns:
            True if the layout was removed, False otherwise
        """
        if layout_id in self.layouts:
            del self.layouts[layout_id]
            return True
        return False
    
    def build_report(
        self,
        data: pd.DataFrame,
        layout_id: str,
        title: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Build a report using a layout and components.
        
        Args:
            data: Data to use for the report
            layout_id: ID of the layout to use
            title: Title of the report
            description: Description of the report
            metadata: Additional metadata for the report
            output_path: Path to save the report
            
        Returns:
            Generated report as an HTML string
        """
        # Get the layout
        layout = self.get_layout(layout_id)
        if not layout:
            raise ValueError(f"Layout not found: {layout_id}")
        
        # Create context for rendering
        context = {
            "chart_generator": self.chart_generator,
            "title": title,
            "description": description,
            "metadata": metadata or {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate HTML for each section
        sections_html = ""
        for section in layout.sections:
            section_title = section.get("title", "")
            section_description = section.get("description", "")
            section_class = section.get("class", "")
            component_ids = section.get("components", [])
            
            # Generate HTML for components in this section
            components_html = ""
            for component_id in component_ids:
                component = self.get_component(component_id)
                if component:
                    try:
                        component_html = component.render(data, context)
                        components_html += component_html
                    except Exception as e:
                        logger.error(f"Error rendering component {component_id}: {str(e)}")
                        components_html += f"""
                        <div class="report-component error">
                            <h3 class="component-title">Error</h3>
                            <div class="error-message">Error rendering component {component_id}: {str(e)}</div>
                        </div>
                        """
            
            # Add section to report
            sections_html += f"""
            <section class="report-section {section_class}" id="section-{section.get('id', '')}">
                <h2 class="section-title">{section_title}</h2>
                <div class="section-description">{section_description}</div>
                <div class="section-content">
                    {components_html}
                </div>
            </section>
            """
        
        # Generate the complete report
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .report-header {{
                    margin-bottom: 30px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 20px;
                }}
                .report-section {{
                    margin-bottom: 40px;
                }}
                .section-title {{
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                .report-component {{
                    margin-bottom: 30px;
                    padding: 15px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }}
                .component-title {{
                    margin-top: 0;
                }}
                .component-description {{
                    color: #666;
                    margin-bottom: 15px;
                }}
                .error {{
                    border-color: #f8d7da;
                    background-color: #fff5f5;
                }}
                .error-message {{
                    color: #721c24;
                    background-color: #f8d7da;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .metrics-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                }}
                .metric {{
                    flex: 1 1 200px;
                    padding: 15px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }}
                .metric-name {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .metric-value {{
                    font-size: 24px;
                    margin-bottom: 5px;
                }}
                .metric-description {{
                    color: #666;
                    font-size: 14px;
                }}
                .metric-error {{
                    color: #721c24;
                    font-size: 14px;
                    margin-top: 5px;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .table th, .table td {{
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                .table th {{
                    background-color: #f2f2f2;
                }}
                .table-striped tbody tr:nth-of-type(odd) {{
                    background-color: rgba(0, 0, 0, 0.05);
                }}
                .table-hover tbody tr:hover {{
                    background-color: rgba(0, 0, 0, 0.075);
                }}
                .report-footer {{
                    margin-top: 40px;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="report-header">
                <h1>{title}</h1>
                <p>{description}</p>
            </div>
            
            {sections_html}
            
            <div class="report-footer">
                <p>Generated at: {context['generated_at']}</p>
            </div>
        </body>
        </html>
        """
        
        # Save the report if output path is provided
        if output_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Write the report
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(report_html)
                
                logger.info(f"Report saved to: {output_path}")
            except Exception as e:
                logger.error(f"Error saving report: {str(e)}")
        
        return report_html
    
    def save_configuration(self, file_path: str) -> bool:
        """
        Save the builder configuration to a file.
        
        Args:
            file_path: Path to save the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create configuration data
            config = {
                "components": {
                    component_id: component.to_dict()
                    for component_id, component in self.components.items()
                },
                "layouts": {
                    layout_id: layout.to_dict()
                    for layout_id, layout in self.layouts.items()
                }
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Write configuration to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Configuration saved to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def load_configuration(self, file_path: str) -> bool:
        """
        Load the builder configuration from a file.
        
        Args:
            file_path: Path to load the configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Configuration file not found: {file_path}")
                return False
            
            # Read configuration from file
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Load components
            self.components = {}
            for component_id, component_data in config.get("components", {}).items():
                self.components[component_id] = ReportComponent.from_dict(component_data)
            
            # Load layouts
            self.layouts = {}
            for layout_id, layout_data in config.get("layouts", {}).items():
                self.layouts[layout_id] = ReportLayout.from_dict(layout_data)
            
            logger.info(f"Configuration loaded from: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False