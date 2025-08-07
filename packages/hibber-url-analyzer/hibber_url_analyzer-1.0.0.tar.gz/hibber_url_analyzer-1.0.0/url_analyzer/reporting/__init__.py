"""
Reporting Package

This package provides functionality for generating reports about URL analysis.
It implements a domain-driven design approach with clear separation of concerns.

Key Components:
- Domain models: ReportTemplate, ReportData, ReportOptions, Report, etc.
- Interfaces: TemplateRenderer, ChartGenerator, ReportingService, etc.
- Services: JinjaTemplateRenderer, PlotlyChartGenerator, DefaultReportingService, etc.
"""

# Import domain models
from url_analyzer.reporting.domain import (
    ReportFormat,
    ReportType,
    ChartType,
    ReportTemplate,
    ReportData,
    ChartOptions,
    ReportOptions,
    Report,
    ReportGenerationResult
)

# Import interfaces
from url_analyzer.reporting.interfaces import (
    TemplateRenderer,
    ChartGenerator,
    TemplateRepository,
    ReportRepository,
    ReportGenerator,
    ReportingService
)

# Import services
from url_analyzer.reporting.services import (
    JinjaTemplateRenderer,
    FileSystemTemplateRepository,
    InMemoryReportRepository,
    HTMLReportGenerator,
    DefaultReportingService
)

# Import chart generators
from url_analyzer.reporting.chart_generators import (
    PlotlyChartGenerator,
    BasicChartGenerator
)

# Define public API
__all__ = [
    # Domain models
    'ReportFormat',
    'ReportType',
    'ChartType',
    'ReportTemplate',
    'ReportData',
    'ChartOptions',
    'ReportOptions',
    'Report',
    'ReportGenerationResult',
    
    # Interfaces
    'TemplateRenderer',
    'ChartGenerator',
    'TemplateRepository',
    'ReportRepository',
    'ReportGenerator',
    'ReportingService',
    
    # Services
    'JinjaTemplateRenderer',
    'FileSystemTemplateRepository',
    'InMemoryReportRepository',
    'HTMLReportGenerator',
    'DefaultReportingService',
    
    # Chart Generators
    'PlotlyChartGenerator',
    'BasicChartGenerator'
]