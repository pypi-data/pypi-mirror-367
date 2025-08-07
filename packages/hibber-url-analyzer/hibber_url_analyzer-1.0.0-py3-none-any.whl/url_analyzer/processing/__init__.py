"""
Data Processing Package

This package provides functionality for processing data files containing URLs.
It implements a domain-driven design approach with clear separation of concerns.

Key Components:
- Domain models: DataSource, DataSink, ProcessingOptions, ProcessingJob, etc.
- Interfaces: DataReader, DataWriter, DataProcessor, BatchProcessingService, etc.
- Services: CSVDataReader, ExcelDataWriter, DefaultBatchProcessingService, etc.
"""

# Import domain models
from url_analyzer.processing.domain import (
    DataSourceType,
    DataSinkType,
    ProcessingStatus,
    DataSource,
    DataSink,
    ProcessingOptions,
    ProcessingJob,
    ProcessingResult
)

# Import interfaces
from url_analyzer.processing.interfaces import (
    DataReader,
    DataWriter,
    DataProcessor,
    JobRepository,
    ResultRepository,
    BatchProcessingService
)

# Import services
from url_analyzer.processing.services import (
    CSVDataReader,
    ExcelDataReader,
    CSVDataWriter,
    ExcelDataWriter,
    HTMLDataWriter,
    URLClassificationProcessor,
    InMemoryJobRepository,
    InMemoryResultRepository,
    DefaultBatchProcessingService
)

# Define public API
__all__ = [
    # Domain models
    'DataSourceType',
    'DataSinkType',
    'ProcessingStatus',
    'DataSource',
    'DataSink',
    'ProcessingOptions',
    'ProcessingJob',
    'ProcessingResult',
    
    # Interfaces
    'DataReader',
    'DataWriter',
    'DataProcessor',
    'JobRepository',
    'ResultRepository',
    'BatchProcessingService',
    
    # Services
    'CSVDataReader',
    'ExcelDataReader',
    'CSVDataWriter',
    'ExcelDataWriter',
    'HTMLDataWriter',
    'URLClassificationProcessor',
    'InMemoryJobRepository',
    'InMemoryResultRepository',
    'DefaultBatchProcessingService'
]