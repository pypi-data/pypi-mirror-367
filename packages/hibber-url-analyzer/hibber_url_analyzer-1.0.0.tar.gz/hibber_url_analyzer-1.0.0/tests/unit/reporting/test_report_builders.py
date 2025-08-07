"""
Test Report Builders Module

This module tests the custom report builders functionality.
"""

import unittest
import os
import tempfile
import pandas as pd
from datetime import datetime

from url_analyzer.reporting.builders import (
    ReportComponent, ChartComponent, TableComponent, TextComponent, SummaryComponent,
    ReportLayout, CustomReportBuilder
)
from url_analyzer.reporting.domain import ChartType, ChartOptions
from url_analyzer.reporting.services import JinjaTemplateRenderer, PlotlyChartGenerator


class MockChartGenerator:
    """Mock chart generator for testing."""
    
    def generate_chart(self, data, options):
        """Generate a mock chart."""
        return f"<div>Mock Chart: {options.title}</div>"
    
    def get_supported_chart_types(self):
        """Get supported chart types."""
        return {ChartType.BAR, ChartType.PIE, ChartType.LINE, ChartType.SCATTER}
    
    def get_name(self):
        """Get the name of this generator."""
        return "Mock Chart Generator"


class MockTemplateRenderer:
    """Mock template renderer for testing."""
    
    def render_template(self, template, data):
        """Render a mock template."""
        return f"<div>Mock Template: {template.name}</div>"
    
    def get_name(self):
        """Get the name of this renderer."""
        return "Mock Template Renderer"


class TestReportComponents(unittest.TestCase):
    """Test report components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data
        self.test_data = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B', 'C'],
            'value': [10, 20, 15, 25, 30, 35],
            'date': pd.date_range(start='2025-01-01', periods=6)
        })
        
        # Create context
        self.context = {
            'chart_generator': MockChartGenerator()
        }
    
    def test_chart_component(self):
        """Test chart component."""
        # Create a chart component
        chart = ChartComponent(
            component_id="test-chart",
            title="Test Chart",
            chart_type=ChartType.BAR,
            x_axis="category",
            y_axis="value",
            description="Test chart description"
        )
        
        # Render the chart
        html = chart.render(self.test_data, self.context)
        
        # Check that the chart was rendered
        self.assertIn("Test Chart", html)
        self.assertIn("Test chart description", html)
        self.assertIn("Mock Chart", html)
    
    def test_table_component(self):
        """Test table component."""
        # Create a table component
        table = TableComponent(
            component_id="test-table",
            title="Test Table",
            columns=["category", "value"],
            sort_by="value",
            sort_ascending=False,
            max_rows=3,
            description="Test table description"
        )
        
        # Render the table
        html = table.render(self.test_data, self.context)
        
        # Check that the table was rendered
        self.assertIn("Test Table", html)
        self.assertIn("Test table description", html)
        self.assertIn("table", html)
        
        # Check that sorting and limiting worked
        # The table should show the top 3 values in descending order
        # First row should be the highest value (35)
        self.assertIn("35", html)
    
    def test_text_component(self):
        """Test text component."""
        # Create a text component
        text = TextComponent(
            component_id="test-text",
            title="Test Text",
            content="<p>This is a test</p>",
            format="html",
            description="Test text description"
        )
        
        # Render the text
        html = text.render(self.test_data, self.context)
        
        # Check that the text was rendered
        self.assertIn("Test Text", html)
        self.assertIn("Test text description", html)
        self.assertIn("<p>This is a test</p>", html)
    
    def test_summary_component(self):
        """Test summary component."""
        # Create a summary component
        summary = SummaryComponent(
            component_id="test-summary",
            title="Test Summary",
            metrics=[
                {
                    "name": "Total Count",
                    "type": "count",
                    "description": "Total number of rows"
                },
                {
                    "name": "Average Value",
                    "type": "mean",
                    "column": "value",
                    "format": "{:.1f}",
                    "description": "Average value"
                },
                {
                    "name": "Max Value",
                    "type": "max",
                    "column": "value",
                    "description": "Maximum value"
                }
            ],
            description="Test summary description"
        )
        
        # Render the summary
        html = summary.render(self.test_data, self.context)
        
        # Check that the summary was rendered
        self.assertIn("Test Summary", html)
        self.assertIn("Test summary description", html)
        self.assertIn("Total Count", html)
        self.assertIn("Average Value", html)
        self.assertIn("Max Value", html)
        
        # Check that metrics were calculated correctly
        self.assertIn("6", html)  # Total count
        self.assertIn("22.5", html)  # Average value (formatted to 1 decimal place)
        self.assertIn("35", html)  # Max value


class TestReportBuilder(unittest.TestCase):
    """Test report builder."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B', 'C'],
            'value': [10, 20, 15, 25, 30, 35],
            'date': pd.date_range(start='2025-01-01', periods=6)
        })
        
        # Create mock renderer and generator
        self.template_renderer = MockTemplateRenderer()
        self.chart_generator = MockChartGenerator()
        
        # Create report builder
        self.builder = CustomReportBuilder(
            template_renderer=self.template_renderer,
            chart_generator=self.chart_generator
        )
        
        # Create components
        self.chart = ChartComponent(
            component_id="test-chart",
            title="Test Chart",
            chart_type=ChartType.BAR,
            x_axis="category",
            y_axis="value",
            description="Test chart description"
        )
        
        self.table = TableComponent(
            component_id="test-table",
            title="Test Table",
            columns=["category", "value"],
            sort_by="value",
            sort_ascending=False,
            max_rows=3,
            description="Test table description"
        )
        
        self.text = TextComponent(
            component_id="test-text",
            title="Test Text",
            content="<p>This is a test</p>",
            format="html",
            description="Test text description"
        )
        
        self.summary = SummaryComponent(
            component_id="test-summary",
            title="Test Summary",
            metrics=[
                {
                    "name": "Total Count",
                    "type": "count",
                    "description": "Total number of rows"
                },
                {
                    "name": "Average Value",
                    "type": "mean",
                    "column": "value",
                    "format": "{:.1f}",
                    "description": "Average value"
                }
            ],
            description="Test summary description"
        )
        
        # Add components to builder
        self.builder.add_component(self.chart)
        self.builder.add_component(self.table)
        self.builder.add_component(self.text)
        self.builder.add_component(self.summary)
        
        # Create layout
        self.layout = ReportLayout(
            layout_id="test-layout",
            name="Test Layout",
            description="Test layout description",
            sections=[
                {
                    "id": "summary-section",
                    "title": "Summary",
                    "description": "Summary section",
                    "components": ["test-summary"]
                },
                {
                    "id": "details-section",
                    "title": "Details",
                    "description": "Details section",
                    "components": ["test-chart", "test-table", "test-text"]
                }
            ]
        )
        
        # Add layout to builder
        self.builder.add_layout(self.layout)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_build_report(self):
        """Test building a report."""
        # Build the report
        output_path = os.path.join(self.temp_dir, "test_report.html")
        html = self.builder.build_report(
            data=self.test_data,
            layout_id="test-layout",
            title="Test Report",
            description="Test report description",
            output_path=output_path
        )
        
        # Check that the report was generated
        self.assertIn("Test Report", html)
        self.assertIn("Test report description", html)
        self.assertIn("Summary", html)
        self.assertIn("Details", html)
        self.assertIn("Test Chart", html)
        self.assertIn("Test Table", html)
        self.assertIn("Test Text", html)
        self.assertIn("Test Summary", html)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check file content
        with open(output_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        self.assertEqual(html, file_content)
    
    def test_save_load_configuration(self):
        """Test saving and loading configuration."""
        # Save configuration
        config_path = os.path.join(self.temp_dir, "test_config.json")
        result = self.builder.save_configuration(config_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(config_path))
        
        # Create a new builder
        new_builder = CustomReportBuilder(
            template_renderer=self.template_renderer,
            chart_generator=self.chart_generator
        )
        
        # Load configuration
        result = new_builder.load_configuration(config_path)
        self.assertTrue(result)
        
        # Check that components were loaded
        self.assertEqual(len(new_builder.components), 4)
        self.assertIn("test-chart", new_builder.components)
        self.assertIn("test-table", new_builder.components)
        self.assertIn("test-text", new_builder.components)
        self.assertIn("test-summary", new_builder.components)
        
        # Check that layouts were loaded
        self.assertEqual(len(new_builder.layouts), 1)
        self.assertIn("test-layout", new_builder.layouts)
        
        # Build a report with the new builder
        html = new_builder.build_report(
            data=self.test_data,
            layout_id="test-layout",
            title="Test Report",
            description="Test report description"
        )
        
        # Check that the report was generated
        self.assertIn("Test Report", html)
        self.assertIn("Test Chart", html)
        self.assertIn("Test Table", html)
        self.assertIn("Test Text", html)
        self.assertIn("Test Summary", html)


if __name__ == "__main__":
    unittest.main()