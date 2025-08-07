"""
Advanced visualization module for URL Analyzer.

This module provides advanced visualization capabilities for URL analysis data,
including interactive charts, geospatial visualizations, and time-series visualizations.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import os
import json
from datetime import datetime

import pandas as pd

# Optional imports for advanced visualizations
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from url_analyzer.utils.logging import get_logger
from url_analyzer.reporting.domain import ChartType

logger = get_logger(__name__)


def is_visualization_available() -> bool:
    """
    Check if visualization libraries are available.
    
    Returns:
        bool: True if Plotly is available, False otherwise
    """
    return PLOTLY_AVAILABLE


def create_interactive_bar_chart(
    df: pd.DataFrame, 
    x_column: str, 
    y_column: str, 
    title: str = "Bar Chart", 
    color_column: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500
) -> Optional[str]:
    """
    Create an interactive bar chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_column: Column to use for x-axis
        y_column: Column to use for y-axis
        title: Chart title
        color_column: Column to use for color differentiation
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create interactive bar chart.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Create the bar chart
    if color_column and color_column in df.columns:
        fig = px.bar(
            df, 
            x=x_column, 
            y=y_column, 
            color=color_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            height=height,
            width=width
        )
    else:
        fig = px.bar(
            df, 
            x=x_column, 
            y=y_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            height=height,
            width=width
        )
    
    # Add interactive features
    fig.update_layout(
        hovermode='closest',
        clickmode='event+select',
        dragmode='zoom',
        selectdirection='h',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_interactive_pie_chart(
    df: pd.DataFrame, 
    names_column: str, 
    values_column: str, 
    title: str = "Pie Chart",
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500
) -> Optional[str]:
    """
    Create an interactive pie chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        names_column: Column to use for pie slice names
        values_column: Column to use for pie slice values
        title: Chart title
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create interactive pie chart.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Create the pie chart
    fig = px.pie(
        df, 
        names=names_column, 
        values=values_column,
        title=title,
        height=height,
        width=width
    )
    
    # Add interactive features
    fig.update_layout(
        hovermode='closest',
        clickmode='event+select',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # Add hover information
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_interactive_line_chart(
    df: pd.DataFrame, 
    x_column: str, 
    y_column: str, 
    title: str = "Line Chart", 
    color_column: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500
) -> Optional[str]:
    """
    Create an interactive line chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_column: Column to use for x-axis
        y_column: Column to use for y-axis
        title: Chart title
        color_column: Column to use for color differentiation
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create interactive line chart.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Create the line chart
    if color_column and color_column in df.columns:
        fig = px.line(
            df, 
            x=x_column, 
            y=y_column, 
            color=color_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            height=height,
            width=width
        )
    else:
        fig = px.line(
            df, 
            x=x_column, 
            y=y_column,
            title=title,
            labels={x_column: x_column.replace('_', ' ').title(), 
                   y_column: y_column.replace('_', ' ').title()},
            height=height,
            width=width
        )
    
    # Add interactive features
    fig.update_layout(
        hovermode='x unified',
        clickmode='event+select',
        dragmode='zoom',
        selectdirection='h',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_interactive_scatter_chart(
    df: pd.DataFrame, 
    x_column: str, 
    y_column: str, 
    title: str = "Scatter Plot", 
    color_column: Optional[str] = None,
    size_column: Optional[str] = None,
    hover_data: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500
) -> Optional[str]:
    """
    Create an interactive scatter plot using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_column: Column to use for x-axis
        y_column: Column to use for y-axis
        title: Chart title
        color_column: Column to use for color differentiation
        size_column: Column to use for point size
        hover_data: List of columns to show in hover tooltip
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create interactive scatter plot.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Create the scatter plot
    fig = px.scatter(
        df, 
        x=x_column, 
        y=y_column,
        color=color_column if color_column and color_column in df.columns else None,
        size=size_column if size_column and size_column in df.columns else None,
        hover_data=hover_data if hover_data else None,
        title=title,
        labels={x_column: x_column.replace('_', ' ').title(), 
               y_column: y_column.replace('_', ' ').title()},
        height=height,
        width=width
    )
    
    # Add interactive features
    fig.update_layout(
        hovermode='closest',
        clickmode='event+select',
        dragmode='zoom',
        selectdirection='any',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_interactive_heatmap(
    df: pd.DataFrame, 
    x_column: str, 
    y_column: str, 
    z_column: str,
    title: str = "Heatmap", 
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500
) -> Optional[str]:
    """
    Create an interactive heatmap using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_column: Column to use for x-axis
        y_column: Column to use for y-axis
        z_column: Column to use for color intensity
        title: Chart title
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create interactive heatmap.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Pivot the data for the heatmap
    pivot_df = df.pivot_table(index=y_column, columns=x_column, values=z_column, aggfunc='mean')
    
    # Create the heatmap
    fig = px.imshow(
        pivot_df,
        title=title,
        labels=dict(x=x_column.replace('_', ' ').title(), 
                   y=y_column.replace('_', ' ').title(),
                   color=z_column.replace('_', ' ').title()),
        height=height,
        width=width
    )
    
    # Add interactive features
    fig.update_layout(
        hovermode='closest',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_geospatial_visualization(
    df: pd.DataFrame,
    lat_column: str,
    lon_column: str,
    title: str = "Geospatial Visualization",
    color_column: Optional[str] = None,
    size_column: Optional[str] = None,
    hover_data: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500
) -> Optional[str]:
    """
    Create an interactive geospatial visualization using Plotly.
    
    Args:
        df: DataFrame containing the data
        lat_column: Column containing latitude values
        lon_column: Column containing longitude values
        title: Chart title
        color_column: Column to use for color differentiation
        size_column: Column to use for point size
        hover_data: List of columns to show in hover tooltip
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create geospatial visualization.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Create the map
    fig = px.scatter_mapbox(
        df,
        lat=lat_column,
        lon=lon_column,
        color=color_column if color_column and color_column in df.columns else None,
        size=size_column if size_column and size_column in df.columns else None,
        hover_name=hover_data[0] if hover_data and hover_data[0] in df.columns else None,
        hover_data=hover_data[1:] if hover_data and len(hover_data) > 1 else None,
        title=title,
        height=height,
        width=width,
        zoom=1
    )
    
    # Use OpenStreetMap style (doesn't require API key)
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_time_series_visualization(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    title: str = "Time Series Visualization",
    color_column: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500,
    include_trend: bool = False
) -> Optional[str]:
    """
    Create an interactive time series visualization using Plotly.
    
    Args:
        df: DataFrame containing the data
        date_column: Column containing date/time values
        value_column: Column containing values to plot
        title: Chart title
        color_column: Column to use for color differentiation
        filters: Dictionary of filters to apply to the data
        width: Chart width in pixels
        height: Chart height in pixels
        include_trend: Whether to include a trend line
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create time series visualization.")
        return None
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
    
    # Ensure date column is datetime type
    if df[date_column].dtype != 'datetime64[ns]':
        try:
            df[date_column] = pd.to_datetime(df[date_column])
        except Exception as e:
            logger.error(f"Failed to convert {date_column} to datetime: {e}")
            return None
    
    # Sort by date
    df = df.sort_values(by=date_column)
    
    # Create the time series plot
    if color_column and color_column in df.columns:
        fig = px.line(
            df,
            x=date_column,
            y=value_column,
            color=color_column,
            title=title,
            labels={date_column: date_column.replace('_', ' ').title(), 
                   value_column: value_column.replace('_', ' ').title()},
            height=height,
            width=width
        )
    else:
        fig = px.line(
            df,
            x=date_column,
            y=value_column,
            title=title,
            labels={date_column: date_column.replace('_', ' ').title(), 
                   value_column: value_column.replace('_', ' ').title()},
            height=height,
            width=width
        )
    
    # Add trend line if requested
    if include_trend:
        # Create a simple moving average
        window_size = max(3, len(df) // 10)  # Use at least 3 points or 10% of data
        df['trend'] = df[value_column].rolling(window=window_size, center=True).mean()
        
        fig.add_scatter(
            x=df[date_column],
            y=df['trend'],
            mode='lines',
            line=dict(width=3, dash='dash', color='red'),
            name='Trend'
        )
    
    # Add interactive features
    fig.update_layout(
        hovermode='x unified',
        clickmode='event+select',
        dragmode='zoom',
        selectdirection='h',
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_interactive_dashboard(
    df: pd.DataFrame,
    charts: List[Dict[str, Any]],
    title: str = "Interactive Dashboard",
    width: int = 1200,
    height: int = 800
) -> Optional[str]:
    """
    Create an interactive dashboard with multiple charts using Plotly.
    
    Args:
        df: DataFrame containing the data
        charts: List of chart configurations, each containing:
            - type: Chart type (bar, pie, line, scatter, heatmap, geo, timeseries)
            - x_column: Column for x-axis (if applicable)
            - y_column: Column for y-axis (if applicable)
            - title: Chart title
            - ... other chart-specific parameters
        title: Dashboard title
        width: Dashboard width in pixels
        height: Dashboard height in pixels
        
    Returns:
        HTML string containing the interactive dashboard or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create interactive dashboard.")
        return None
    
    # Determine grid layout based on number of charts
    num_charts = len(charts)
    if num_charts <= 1:
        rows, cols = 1, 1
    elif num_charts <= 2:
        rows, cols = 1, 2
    elif num_charts <= 4:
        rows, cols = 2, 2
    elif num_charts <= 6:
        rows, cols = 2, 3
    else:
        rows, cols = 3, 3
    
    # Create subplot grid with appropriate specs for each chart type
    specs = []
    for r in range(rows):
        row_specs = []
        for c in range(cols):
            chart_idx = r * cols + c
            if chart_idx < len(charts):
                chart_type = charts[chart_idx].get('type', 'bar')
                # Use 'domain' type for pie charts, 'xy' for others
                if chart_type == 'pie':
                    row_specs.append({"type": "domain"})
                else:
                    row_specs.append({"type": "xy"})
            else:
                row_specs.append({"type": "xy"})
        specs.append(row_specs)
    
    fig = make_subplots(
        rows=rows, 
        cols=cols, 
        subplot_titles=[chart.get('title', f"Chart {i+1}") for i, chart in enumerate(charts[:rows*cols])],
        specs=specs
    )
    
    # Add each chart to the dashboard
    for i, chart_config in enumerate(charts[:rows*cols]):
        row = i // cols + 1
        col = i % cols + 1
        chart_type = chart_config.get('type', 'bar')
        
        # Apply filters if provided
        filtered_df = df.copy()
        filters = chart_config.get('filters')
        if filters:
            for column, value in filters.items():
                if column in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        # Create the appropriate chart type
        if chart_type == 'bar':
            x_column = chart_config.get('x_column')
            y_column = chart_config.get('y_column')
            color_column = chart_config.get('color_column')
            
            if color_column and color_column in filtered_df.columns:
                for color_val in filtered_df[color_column].unique():
                    color_df = filtered_df[filtered_df[color_column] == color_val]
                    fig.add_trace(
                        go.Bar(
                            x=color_df[x_column],
                            y=color_df[y_column],
                            name=f"{color_val}",
                        ),
                        row=row, col=col
                    )
            else:
                fig.add_trace(
                    go.Bar(
                        x=filtered_df[x_column],
                        y=filtered_df[y_column],
                    ),
                    row=row, col=col
                )
                
        elif chart_type == 'pie':
            names_column = chart_config.get('names_column')
            values_column = chart_config.get('values_column')
            
            fig.add_trace(
                go.Pie(
                    labels=filtered_df[names_column],
                    values=filtered_df[values_column],
                    textinfo='percent+label',
                ),
                row=row, col=col
            )
            
        elif chart_type == 'line':
            x_column = chart_config.get('x_column')
            y_column = chart_config.get('y_column')
            color_column = chart_config.get('color_column')
            
            if color_column and color_column in filtered_df.columns:
                for color_val in filtered_df[color_column].unique():
                    color_df = filtered_df[filtered_df[color_column] == color_val]
                    fig.add_trace(
                        go.Scatter(
                            x=color_df[x_column],
                            y=color_df[y_column],
                            mode='lines',
                            name=f"{color_val}",
                        ),
                        row=row, col=col
                    )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=filtered_df[x_column],
                        y=filtered_df[y_column],
                        mode='lines',
                    ),
                    row=row, col=col
                )
                
        elif chart_type == 'scatter':
            x_column = chart_config.get('x_column')
            y_column = chart_config.get('y_column')
            color_column = chart_config.get('color_column')
            
            if color_column and color_column in filtered_df.columns:
                for color_val in filtered_df[color_column].unique():
                    color_df = filtered_df[filtered_df[color_column] == color_val]
                    fig.add_trace(
                        go.Scatter(
                            x=color_df[x_column],
                            y=color_df[y_column],
                            mode='markers',
                            name=f"{color_val}",
                        ),
                        row=row, col=col
                    )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=filtered_df[x_column],
                        y=filtered_df[y_column],
                        mode='markers',
                    ),
                    row=row, col=col
                )
    
    # Update layout
    fig.update_layout(
        title_text=title,
        height=height,
        width=width,
        showlegend=True,
        hovermode='closest',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def create_chart_by_type(
    df: pd.DataFrame,
    chart_type: Union[str, ChartType],
    **kwargs
) -> Optional[str]:
    """
    Create a chart based on the specified chart type.
    
    Args:
        df: DataFrame containing the data
        chart_type: Type of chart to create (string or ChartType enum)
        **kwargs: Additional parameters for the specific chart type
        
    Returns:
        HTML string containing the interactive chart or None if Plotly is not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly is not available. Cannot create chart.")
        return None
    
    # Convert ChartType enum to string if needed
    if isinstance(chart_type, ChartType):
        chart_type = chart_type.name.lower()
    
    # Create the appropriate chart type
    if chart_type == 'bar':
        return create_interactive_bar_chart(df, **kwargs)
    elif chart_type == 'pie':
        return create_interactive_pie_chart(df, **kwargs)
    elif chart_type == 'line':
        return create_interactive_line_chart(df, **kwargs)
    elif chart_type == 'scatter':
        return create_interactive_scatter_chart(df, **kwargs)
    elif chart_type == 'heatmap':
        return create_interactive_heatmap(df, **kwargs)
    elif chart_type == 'geo' or chart_type == 'geospatial':
        return create_geospatial_visualization(df, **kwargs)
    elif chart_type == 'timeseries' or chart_type == 'time_series':
        return create_time_series_visualization(df, **kwargs)
    else:
        logger.warning(f"Unknown chart type: {chart_type}")
        return None