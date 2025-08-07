"""
Chart generator implementations for URL Analyzer.

This module provides implementations of the ChartGenerator interface
for generating charts in reports.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Union

import pandas as pd

from url_analyzer.reporting.interfaces import ChartGenerator
from url_analyzer.reporting.domain import ChartType, ChartOptions
from url_analyzer.reporting.visualization import (
    is_visualization_available,
    create_interactive_bar_chart,
    create_interactive_pie_chart,
    create_interactive_line_chart,
    create_interactive_scatter_chart,
    create_interactive_heatmap,
    create_geospatial_visualization,
    create_time_series_visualization,
    create_interactive_dashboard,
    create_chart_by_type
)
from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


class PlotlyChartGenerator(ChartGenerator):
    """
    Chart generator implementation using Plotly for interactive visualizations.
    """
    
    def __init__(self):
        """Initialize the Plotly chart generator."""
        self._is_available = is_visualization_available()
        if not self._is_available:
            logger.warning("Plotly is not available. Advanced visualizations will be disabled.")
    
    def generate_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a chart using Plotly.
        
        Args:
            data: DataFrame containing the data for the chart
            options: Options for generating the chart
            
        Returns:
            HTML string containing the chart
            
        Raises:
            ValueError: If the chart type is not supported
        """
        if not self._is_available:
            return self._generate_fallback_chart(options)
        
        chart_type = options.chart_type
        
        # Extract common parameters
        params = {
            "title": options.title,
            "width": options.width,
            "height": options.height,
            "filters": options.filters
        }
        
        # Add chart-specific parameters
        if chart_type == ChartType.BAR:
            params["x_column"] = options.x_axis
            params["y_column"] = options.y_axis
            params["color_column"] = options.color_by
            return create_interactive_bar_chart(data, **params)
            
        elif chart_type == ChartType.PIE:
            params["names_column"] = options.x_axis
            params["values_column"] = options.y_axis
            return create_interactive_pie_chart(data, **params)
            
        elif chart_type == ChartType.LINE:
            params["x_column"] = options.x_axis
            params["y_column"] = options.y_axis
            params["color_column"] = options.color_by
            return create_interactive_line_chart(data, **params)
            
        elif chart_type == ChartType.SCATTER:
            params["x_column"] = options.x_axis
            params["y_column"] = options.y_axis
            params["color_column"] = options.color_by
            params["size_column"] = options.options.get("size_column")
            params["hover_data"] = options.options.get("hover_data")
            return create_interactive_scatter_chart(data, **params)
            
        elif chart_type == ChartType.HEATMAP:
            params["x_column"] = options.x_axis
            params["y_column"] = options.y_axis
            params["z_column"] = options.options.get("z_column", options.y_axis)
            return create_interactive_heatmap(data, **params)
            
        elif chart_type == ChartType.GEOSPATIAL:
            params["lat_column"] = options.options.get("lat_column", "latitude")
            params["lon_column"] = options.options.get("lon_column", "longitude")
            params["color_column"] = options.color_by
            params["size_column"] = options.options.get("size_column")
            params["hover_data"] = options.options.get("hover_data")
            return create_geospatial_visualization(data, **params)
            
        elif chart_type == ChartType.TIME_SERIES:
            params["date_column"] = options.x_axis
            params["value_column"] = options.y_axis
            params["color_column"] = options.color_by
            params["include_trend"] = options.options.get("include_trend", False)
            return create_time_series_visualization(data, **params)
            
        elif chart_type == ChartType.DASHBOARD:
            charts = options.options.get("charts", [])
            return create_interactive_dashboard(data, charts, **params)
            
        elif chart_type == ChartType.TREEMAP:
            # Treemap is not directly implemented in the visualization module
            # Use a fallback or implement it if needed
            return self._generate_fallback_chart(options)
            
        elif chart_type == ChartType.CUSTOM:
            # For custom charts, use the chart_by_type function with the specified type
            custom_type = options.options.get("custom_type", "bar")
            return create_chart_by_type(data, custom_type, **params)
            
        else:
            logger.warning(f"Unsupported chart type: {chart_type}")
            return self._generate_fallback_chart(options)
    
    def get_supported_chart_types(self) -> Set[ChartType]:
        """
        Get the set of chart types supported by this generator.
        
        Returns:
            Set of supported ChartType values
        """
        if not self._is_available:
            return set()
        
        return {
            ChartType.BAR,
            ChartType.PIE,
            ChartType.LINE,
            ChartType.SCATTER,
            ChartType.HEATMAP,
            ChartType.GEOSPATIAL,
            ChartType.TIME_SERIES,
            ChartType.DASHBOARD,
            ChartType.CUSTOM
        }
    
    def get_name(self) -> str:
        """
        Get the name of this chart generator.
        
        Returns:
            Name of the chart generator
        """
        return "Plotly Chart Generator"
    
    def _generate_fallback_chart(self, options: ChartOptions) -> str:
        """
        Generate a fallback chart when Plotly is not available or the chart type is not supported.
        
        Args:
            options: Options for generating the chart
            
        Returns:
            HTML string containing a fallback chart
        """
        chart_type = options.chart_type.name
        title = options.title
        
        return f"""
        <div class="fallback-chart">
            <h4>{title}</h4>
            <p>Chart type '{chart_type}' is not available.</p>
            <p>Please install Plotly to enable advanced visualizations:</p>
            <pre>pip install plotly</pre>
        </div>
        """


class BasicChartGenerator(ChartGenerator):
    """
    Basic chart generator implementation using HTML tables and simple visualizations.
    This is a fallback when Plotly is not available.
    """
    
    def generate_chart(self, data: pd.DataFrame, options: ChartOptions) -> str:
        """
        Generate a basic chart using HTML.
        
        Args:
            data: DataFrame containing the data for the chart
            options: Options for generating the chart
            
        Returns:
            HTML string containing the chart
        """
        chart_type = options.chart_type
        title = options.title
        
        # Apply filters if provided
        filtered_data = data.copy()
        if options.filters:
            for column, value in options.filters.items():
                if column in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data[column] == value]
        
        if chart_type in [ChartType.BAR, ChartType.LINE, ChartType.SCATTER]:
            # For these chart types, create a simple table with x and y values
            x_axis = options.x_axis
            y_axis = options.y_axis
            
            if x_axis in filtered_data.columns and y_axis in filtered_data.columns:
                # Group by x_axis and calculate mean of y_axis
                grouped_data = filtered_data.groupby(x_axis)[y_axis].mean().reset_index()
                
                # Create an HTML table
                table_html = "<table class='basic-chart-table'>"
                table_html += f"<tr><th>{x_axis}</th><th>{y_axis}</th></tr>"
                
                for _, row in grouped_data.iterrows():
                    table_html += f"<tr><td>{row[x_axis]}</td><td>{row[y_axis]:.2f}</td></tr>"
                
                table_html += "</table>"
                
                return f"""
                <div class="basic-chart">
                    <h4>{title}</h4>
                    <p>Basic {chart_type.name.lower()} chart:</p>
                    {table_html}
                    <p><em>Note: Install Plotly for interactive visualizations.</em></p>
                </div>
                """
        
        elif chart_type == ChartType.PIE:
            # For pie charts, create a simple table with category and count/value
            names_column = options.x_axis
            values_column = options.y_axis
            
            if names_column in filtered_data.columns:
                # Group by names_column and calculate count or sum of values_column
                if values_column and values_column in filtered_data.columns:
                    grouped_data = filtered_data.groupby(names_column)[values_column].sum().reset_index()
                else:
                    grouped_data = filtered_data[names_column].value_counts().reset_index()
                    grouped_data.columns = [names_column, 'count']
                    values_column = 'count'
                
                # Create an HTML table
                table_html = "<table class='basic-chart-table'>"
                table_html += f"<tr><th>{names_column}</th><th>{values_column}</th></tr>"
                
                for _, row in grouped_data.iterrows():
                    table_html += f"<tr><td>{row[names_column]}</td><td>{row[values_column]}</td></tr>"
                
                table_html += "</table>"
                
                return f"""
                <div class="basic-chart">
                    <h4>{title}</h4>
                    <p>Basic pie chart data:</p>
                    {table_html}
                    <p><em>Note: Install Plotly for interactive visualizations.</em></p>
                </div>
                """
        
        # For other chart types or if specific columns are not found, return a generic message
        return f"""
        <div class="basic-chart">
            <h4>{title}</h4>
            <p>Basic chart for type '{chart_type.name}'</p>
            <p>Data summary: {len(filtered_data)} rows, {len(filtered_data.columns)} columns</p>
            <p><em>Note: Install Plotly for interactive visualizations.</em></p>
        </div>
        """
    
    def get_supported_chart_types(self) -> Set[ChartType]:
        """
        Get the set of chart types supported by this generator.
        
        Returns:
            Set of supported ChartType values
        """
        return {
            ChartType.BAR,
            ChartType.PIE,
            ChartType.LINE,
            ChartType.SCATTER
        }
    
    def get_name(self) -> str:
        """
        Get the name of this chart generator.
        
        Returns:
            Name of the chart generator
        """
        return "Basic Chart Generator"