"""
Test module for the advanced visualization features.

This module tests the visualization capabilities added in task 26.
"""

import unittest
import os
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import visualization module
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

# Import chart generators
from url_analyzer.reporting.chart_generators import (
    PlotlyChartGenerator,
    BasicChartGenerator
)

# Import domain models
from url_analyzer.reporting.domain import ChartType, ChartOptions


class TestVisualization(unittest.TestCase):
    """Test case for visualization module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample data for testing
        np.random.seed(42)  # For reproducible results
        
        # Sample data for general charts
        self.sample_data = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D', 'E'] * 5,
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y'] * 5,
            'value': np.random.randint(10, 100, 25),
            'count': np.random.randint(1, 50, 25)
        })
        
        # Sample data for geospatial visualization
        self.geo_data = pd.DataFrame({
            'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
            'latitude': [40.7128, 34.0522, 41.8781, 29.7604, 33.4484],
            'longitude': [-74.0060, -118.2437, -87.6298, -95.3698, -112.0740],
            'population': [8804190, 3898747, 2746388, 2304580, 1608139],
            'growth_rate': [0.2, 0.5, 0.1, 0.8, 1.2]
        })
        
        # Sample data for time series visualization
        dates = [datetime.now() - timedelta(days=i) for i in range(30)]
        self.time_data = pd.DataFrame({
            'date': dates,
            'value': np.random.normal(100, 15, 30),
            'category': ['A', 'B', 'C'] * 10
        })
    
    def test_visualization_availability(self):
        """Test if visualization is available."""
        # This test will pass regardless of whether Plotly is installed
        is_available = is_visualization_available()
        self.assertIsInstance(is_available, bool)
    
    def test_bar_chart_creation(self):
        """Test creating a bar chart."""
        chart_html = create_interactive_bar_chart(
            self.sample_data,
            x_column='category',
            y_column='value',
            title='Test Bar Chart',
            color_column='subcategory'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test bar chart', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_pie_chart_creation(self):
        """Test creating a pie chart."""
        chart_html = create_interactive_pie_chart(
            self.sample_data,
            names_column='category',
            values_column='value',
            title='Test Pie Chart'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test pie chart', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_line_chart_creation(self):
        """Test creating a line chart."""
        chart_html = create_interactive_line_chart(
            self.sample_data,
            x_column='category',
            y_column='value',
            title='Test Line Chart',
            color_column='subcategory'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test line chart', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_scatter_chart_creation(self):
        """Test creating a scatter chart."""
        chart_html = create_interactive_scatter_chart(
            self.sample_data,
            x_column='value',
            y_column='count',
            title='Test Scatter Chart',
            color_column='category',
            hover_data=['subcategory']
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test scatter chart', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_heatmap_creation(self):
        """Test creating a heatmap."""
        chart_html = create_interactive_heatmap(
            self.sample_data,
            x_column='category',
            y_column='subcategory',
            z_column='value',
            title='Test Heatmap'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test heatmap', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_geospatial_visualization(self):
        """Test creating a geospatial visualization."""
        chart_html = create_geospatial_visualization(
            self.geo_data,
            lat_column='latitude',
            lon_column='longitude',
            title='Test Geospatial Visualization',
            color_column='growth_rate',
            size_column='population',
            hover_data=['city']
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test geospatial visualization', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_time_series_visualization(self):
        """Test creating a time series visualization."""
        chart_html = create_time_series_visualization(
            self.time_data,
            date_column='date',
            value_column='value',
            title='Test Time Series Visualization',
            color_column='category',
            include_trend=True
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test time series visualization', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_dashboard_creation(self):
        """Test creating an interactive dashboard."""
        charts = [
            {
                'type': 'bar',
                'x_column': 'category',
                'y_column': 'value',
                'title': 'Bar Chart'
            },
            {
                'type': 'pie',
                'names_column': 'category',
                'values_column': 'value',
                'title': 'Pie Chart'
            }
        ]
        
        chart_html = create_interactive_dashboard(
            self.sample_data,
            charts=charts,
            title='Test Dashboard'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test dashboard', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_chart_by_type(self):
        """Test creating a chart by type."""
        chart_html = create_chart_by_type(
            self.sample_data,
            chart_type='bar',
            x_column='category',
            y_column='value',
            title='Test Chart By Type'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test chart by type', chart_html.lower())
        else:
            self.assertIsNone(chart_html)
    
    def test_chart_by_enum_type(self):
        """Test creating a chart using ChartType enum."""
        chart_html = create_chart_by_type(
            self.sample_data,
            chart_type=ChartType.BAR,
            x_column='category',
            y_column='value',
            title='Test Chart By Enum Type'
        )
        
        # If Plotly is not available, chart_html will be None
        if is_visualization_available():
            self.assertIsNotNone(chart_html)
            self.assertIn('plotly', chart_html.lower())
            self.assertIn('test chart by enum type', chart_html.lower())
        else:
            self.assertIsNone(chart_html)


class TestChartGenerators(unittest.TestCase):
    """Test case for chart generators."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample data for testing
        np.random.seed(42)  # For reproducible results
        
        self.sample_data = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D', 'E'] * 5,
            'subcategory': ['X', 'Y', 'Z', 'X', 'Y'] * 5,
            'value': np.random.randint(10, 100, 25),
            'count': np.random.randint(1, 50, 25)
        })
        
        # Create chart generators
        self.plotly_generator = PlotlyChartGenerator()
        self.basic_generator = BasicChartGenerator()
        
        # Create chart options
        self.bar_options = ChartOptions(
            chart_type=ChartType.BAR,
            title='Test Bar Chart',
            x_axis='category',
            y_axis='value',
            color_by='subcategory',
            filters={},
            width=800,
            height=400,
            options={}
        )
        
        self.pie_options = ChartOptions(
            chart_type=ChartType.PIE,
            title='Test Pie Chart',
            x_axis='category',
            y_axis='value',
            color_by=None,
            filters={},
            width=800,
            height=400,
            options={}
        )
    
    def test_plotly_chart_generator(self):
        """Test PlotlyChartGenerator."""
        # Get supported chart types
        supported_types = self.plotly_generator.get_supported_chart_types()
        
        # Check if the generator supports the expected chart types
        if is_visualization_available():
            self.assertIn(ChartType.BAR, supported_types)
            self.assertIn(ChartType.PIE, supported_types)
            self.assertIn(ChartType.LINE, supported_types)
            self.assertIn(ChartType.SCATTER, supported_types)
            self.assertIn(ChartType.HEATMAP, supported_types)
            self.assertIn(ChartType.GEOSPATIAL, supported_types)
            self.assertIn(ChartType.TIME_SERIES, supported_types)
            self.assertIn(ChartType.DASHBOARD, supported_types)
        else:
            self.assertEqual(set(), supported_types)
        
        # Test generating a chart
        try:
            chart_html = self.plotly_generator.generate_chart(self.sample_data, self.bar_options)
            
            if is_visualization_available():
                self.assertIsNotNone(chart_html)
                self.assertIn('plotly', chart_html.lower())
                self.assertIn('test bar chart', chart_html.lower())
            else:
                self.assertIn('fallback', chart_html.lower())
        except ImportError:
            # This is expected if Plotly is not available
            self.assertFalse(is_visualization_available())
    
    def test_basic_chart_generator(self):
        """Test BasicChartGenerator."""
        # Get supported chart types
        supported_types = self.basic_generator.get_supported_chart_types()
        
        # Check if the generator supports the expected chart types
        self.assertIn(ChartType.BAR, supported_types)
        self.assertIn(ChartType.PIE, supported_types)
        self.assertIn(ChartType.LINE, supported_types)
        self.assertIn(ChartType.SCATTER, supported_types)
        
        # Test generating a chart
        chart_html = self.basic_generator.generate_chart(self.sample_data, self.bar_options)
        self.assertIsNotNone(chart_html)
        self.assertIn('basic-chart', chart_html.lower())
        self.assertIn('test bar chart', chart_html.lower())
        
        # Test generating a pie chart
        chart_html = self.basic_generator.generate_chart(self.sample_data, self.pie_options)
        self.assertIsNotNone(chart_html)
        self.assertIn('basic-chart', chart_html.lower())
        self.assertIn('test pie chart', chart_html.lower())


if __name__ == '__main__':
    unittest.main()