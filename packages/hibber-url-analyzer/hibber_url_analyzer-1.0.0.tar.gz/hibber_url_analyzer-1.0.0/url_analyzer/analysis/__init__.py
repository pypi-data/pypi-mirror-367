"""
URL Analysis Package

This package provides functionality for fetching and analyzing URL content.
It implements a domain-driven design approach with clear separation of concerns.

Key Components:
- Domain models: URLContent, ContentSummary, FetchResult, etc.
- Interfaces: URLFetcher, ContentAnalyzer, CacheRepository, etc.
- Services: RequestsURLFetcher, HTMLContentAnalyzer, DefaultAnalysisService, etc.
- Advanced Analytics: Content analysis, topic modeling, sentiment analysis, etc.
- Relationship Mapping: URL and domain relationship analysis
"""

# Import domain models
from url_analyzer.analysis.domain import (
    URLContent,
    ContentSummary,
    FetchResult,
    AnalysisResult,
    AnalysisOptions
)

# Import interfaces
from url_analyzer.analysis.interfaces import (
    URLFetcher,
    ContentAnalyzer,
    CacheRepository,
    AnalysisService
)

# Import services
from url_analyzer.analysis.services import (
    RequestsURLFetcher,
    HTMLContentAnalyzer,
    JSONContentAnalyzer,
    InMemoryCacheRepository,
    DefaultAnalysisService
)

# Import advanced analytics
from url_analyzer.analysis.advanced_analytics import (
    AdvancedAnalytics,
    AdvancedContentAnalyzer
)

# Import relationship mapping
from url_analyzer.analysis.relationship_mapping import (
    RelationshipMapper,
    RelationshipAnalyzer,
    analyze_url_relationships
)

# Define public API
__all__ = [
    # Domain models
    'URLContent',
    'ContentSummary',
    'FetchResult',
    'AnalysisResult',
    'AnalysisOptions',
    
    # Interfaces
    'URLFetcher',
    'ContentAnalyzer',
    'CacheRepository',
    'AnalysisService',
    
    # Services
    'RequestsURLFetcher',
    'HTMLContentAnalyzer',
    'JSONContentAnalyzer',
    'InMemoryCacheRepository',
    'DefaultAnalysisService',
    
    # Advanced Analytics
    'AdvancedAnalytics',
    'AdvancedContentAnalyzer',
    
    # Relationship Mapping
    'RelationshipMapper',
    'RelationshipAnalyzer',
    'analyze_url_relationships'
]