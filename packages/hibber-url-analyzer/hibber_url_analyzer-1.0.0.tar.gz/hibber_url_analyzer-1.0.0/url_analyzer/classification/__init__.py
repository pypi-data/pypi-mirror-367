"""
URL Classification Package

This package provides functionality for classifying URLs based on patterns and rules.
It implements a domain-driven design approach with clear separation of concerns.

Key Components:
- Domain models: URLCategory, ClassificationPattern, ClassificationRule, etc.
- Interfaces: URLClassifier, RuleRepository, PatternRepository, etc.
- Services: PatternBasedClassifier, RuleBasedClassifier, DefaultClassificationService, etc.
"""

# Import domain models
from url_analyzer.classification.domain import (
    URLCategory,
    ClassificationPattern,
    ClassificationRule,
    ClassificationResult,
    RuleSet
)

# Import interfaces
from url_analyzer.classification.interfaces import (
    URLClassifier,
    RuleRepository,
    PatternRepository,
    ClassificationService
)

# Import services
from url_analyzer.classification.services import (
    PatternBasedClassifier,
    RuleBasedClassifier,
    CompositeClassifier,
    InMemoryRuleRepository,
    InMemoryPatternRepository,
    DefaultClassificationService,
    create_pattern_based_classifier_from_config,
    create_rule_based_classifier_from_config
)

# Define public API
__all__ = [
    # Domain models
    'URLCategory',
    'ClassificationPattern',
    'ClassificationRule',
    'ClassificationResult',
    'RuleSet',
    
    # Interfaces
    'URLClassifier',
    'RuleRepository',
    'PatternRepository',
    'ClassificationService',
    
    # Services
    'PatternBasedClassifier',
    'RuleBasedClassifier',
    'CompositeClassifier',
    'InMemoryRuleRepository',
    'InMemoryPatternRepository',
    'DefaultClassificationService',
    'create_pattern_based_classifier_from_config',
    'create_rule_based_classifier_from_config'
]