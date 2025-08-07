"""
Core functionality package for URL Analyzer.

This package contains the consolidated core business logic, analysis, 
classification, and processing functionality.

Consolidated from packages: analysis, classification, core, processing, domain
"""

# Import functionality with graceful degradation - avoiding wildcard imports
# Note: Many submodules are placeholders, so we use dynamic imports with fallbacks

import logging
logger = logging.getLogger(__name__)

# Dynamic import helper function
def _safe_import(module_path, item_name, fallback=None):
    """Safely import an item from a module with fallback."""
    try:
        module = __import__(module_path, fromlist=[item_name])
        return getattr(module, item_name, fallback)
    except (ImportError, AttributeError) as e:
        logger.debug(f"Could not import {item_name} from {module_path}: {e}")
        return fallback

# Try to import from submodules, but provide fallbacks for missing components
# This approach avoids wildcard imports while handling missing implementations gracefully

# Analysis functionality - using dynamic imports
AdvancedAnalyzer = _safe_import('url_analyzer.core.analysis', 'AdvancedAnalyzer')
StatisticalAnalyzer = _safe_import('url_analyzer.core.analysis', 'StatisticalAnalyzer')
PredictiveAnalyzer = _safe_import('url_analyzer.core.analysis', 'PredictiveAnalyzer')
AnomalyDetector = _safe_import('url_analyzer.core.analysis', 'AnomalyDetector')
CustomAnalyzer = _safe_import('url_analyzer.core.analysis', 'CustomAnalyzer')
DeepLearningAnalyzer = _safe_import('url_analyzer.core.analysis', 'DeepLearningAnalyzer')
TopicModeler = _safe_import('url_analyzer.core.analysis', 'TopicModeler')
TrendAnalyzer = _safe_import('url_analyzer.core.analysis', 'TrendAnalyzer')
RelationshipMapper = _safe_import('url_analyzer.core.analysis', 'RelationshipMapper')

# Classification functionality
URLClassifier = _safe_import('url_analyzer.core.classification', 'URLClassifier')
MLClassifier = _safe_import('url_analyzer.core.classification', 'MLClassifier')
PatternMatcher = _safe_import('url_analyzer.core.classification', 'PatternMatcher')

# Processing functionality
ContentProcessor = _safe_import('url_analyzer.core.processing', 'ContentProcessor')
ProcessingService = _safe_import('url_analyzer.core.processing', 'ProcessingService')

# Domain entities
URLEntity = _safe_import('url_analyzer.core.domain', 'URLEntity')
AnalysisResult = _safe_import('url_analyzer.core.domain', 'AnalysisResult')
ClassificationResult = _safe_import('url_analyzer.core.domain', 'ClassificationResult')
ProcessingResult = _safe_import('url_analyzer.core.domain', 'ProcessingResult')

# Interfaces
AnalysisInterface = _safe_import('url_analyzer.core.interfaces', 'AnalysisInterface')
ClassificationInterface = _safe_import('url_analyzer.core.interfaces', 'ClassificationInterface')
ProcessingInterface = _safe_import('url_analyzer.core.interfaces', 'ProcessingInterface')

# Services
AnalysisService = _safe_import('url_analyzer.core.services', 'AnalysisService')
ClassificationService = _safe_import('url_analyzer.core.services', 'ClassificationService')

# Rules and strategies with lazy loading
def get_business_rules():
    """Lazy load business rules to avoid initialization issues."""
    return _safe_import('url_analyzer.core.rules', 'BusinessRules')

def get_analysis_strategy():
    """Lazy load analysis strategy to avoid initialization issues."""
    return _safe_import('url_analyzer.core.strategies', 'AnalysisStrategy')

# For backward compatibility, provide direct access
BusinessRules = get_business_rules()
AnalysisStrategy = get_analysis_strategy()

from typing import Final

__all__: Final = [
    # Analysis functionality
    'AdvancedAnalyzer',
    'StatisticalAnalyzer', 
    'PredictiveAnalyzer',
    'AnomalyDetector',
    'CustomAnalyzer',
    'DeepLearningAnalyzer',
    'TopicModeler',
    'TrendAnalyzer',
    'RelationshipMapper',
    
    # Classification functionality
    'URLClassifier',
    'MLClassifier',
    'PatternMatcher',
    
    # Processing functionality
    'ContentProcessor',
    'ProcessingService',
    
    # Domain entities
    'URLEntity',
    'AnalysisResult',
    'ClassificationResult',
    'ProcessingResult',
    
    # Interfaces
    'AnalysisInterface',
    'ClassificationInterface',
    'ProcessingInterface',
    
    # Services
    'AnalysisService',
    'ClassificationService',
    
    # Rules and strategies
    'BusinessRules',
    'AnalysisStrategy',
]