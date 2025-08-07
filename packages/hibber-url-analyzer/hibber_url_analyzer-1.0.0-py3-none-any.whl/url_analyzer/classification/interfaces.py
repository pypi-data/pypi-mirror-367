"""
URL Classification Interfaces

This module defines interfaces for the URL Classification domain.
These interfaces ensure proper separation of concerns and enable dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Set

from url_analyzer.classification.domain import URLCategory, ClassificationRule, ClassificationPattern, ClassificationResult, RuleSet


class URLClassifier(ABC):
    """Interface for URL classifiers."""
    
    @abstractmethod
    def classify_url(self, url: str) -> ClassificationResult:
        """
        Classify a URL.
        
        Args:
            url: URL to classify
            
        Returns:
            ClassificationResult containing the classification details
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this classifier.
        
        Returns:
            Classifier name
        """
        pass
    
    @abstractmethod
    def get_categories(self) -> List[URLCategory]:
        """
        Get the list of categories supported by this classifier.
        
        Returns:
            List of category objects
        """
        pass


class RuleRepository(ABC):
    """Interface for rule repositories."""
    
    @abstractmethod
    def get_rules(self) -> List[ClassificationRule]:
        """
        Get all rules.
        
        Returns:
            List of rules
        """
        pass
    
    @abstractmethod
    def add_rule(self, rule: ClassificationRule) -> None:
        """
        Add a rule.
        
        Args:
            rule: Rule to add
        """
        pass
    
    @abstractmethod
    def remove_rule(self, rule_id: str) -> None:
        """
        Remove a rule.
        
        Args:
            rule_id: ID of the rule to remove
        """
        pass
    
    @abstractmethod
    def get_rule(self, rule_id: str) -> Optional[ClassificationRule]:
        """
        Get a rule by ID.
        
        Args:
            rule_id: ID of the rule to get
            
        Returns:
            Rule or None if not found
        """
        pass
    
    @abstractmethod
    def get_rule_set(self, name: Optional[str] = None) -> RuleSet:
        """
        Get a rule set.
        
        Args:
            name: Optional name of the rule set to get
            
        Returns:
            Rule set
        """
        pass


class PatternRepository(ABC):
    """Interface for pattern repositories."""
    
    @abstractmethod
    def get_patterns(self) -> List[ClassificationPattern]:
        """
        Get all patterns.
        
        Returns:
            List of patterns
        """
        pass
    
    @abstractmethod
    def add_pattern(self, pattern: ClassificationPattern) -> None:
        """
        Add a pattern.
        
        Args:
            pattern: Pattern to add
        """
        pass
    
    @abstractmethod
    def remove_pattern(self, pattern_str: str) -> None:
        """
        Remove a pattern.
        
        Args:
            pattern_str: Pattern string to remove
        """
        pass
    
    @abstractmethod
    def get_patterns_by_category(self, category: URLCategory) -> List[ClassificationPattern]:
        """
        Get patterns by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of patterns for the given category
        """
        pass


class ClassificationService(ABC):
    """Interface for classification services."""
    
    @abstractmethod
    def classify_url(self, url: str) -> ClassificationResult:
        """
        Classify a URL.
        
        Args:
            url: URL to classify
            
        Returns:
            ClassificationResult containing the classification details
        """
        pass
    
    @abstractmethod
    def classify_urls(self, urls: List[str]) -> Dict[str, ClassificationResult]:
        """
        Classify multiple URLs.
        
        Args:
            urls: List of URLs to classify
            
        Returns:
            Dictionary mapping URLs to their classification results
        """
        pass
    
    @abstractmethod
    def get_classifiers(self) -> List[URLClassifier]:
        """
        Get all available classifiers.
        
        Returns:
            List of classifiers
        """
        pass
    
    @abstractmethod
    def add_classifier(self, classifier: URLClassifier) -> None:
        """
        Add a classifier.
        
        Args:
            classifier: Classifier to add
        """
        pass
    
    @abstractmethod
    def remove_classifier(self, name: str) -> None:
        """
        Remove a classifier.
        
        Args:
            name: Name of the classifier to remove
        """
        pass
    
    @abstractmethod
    def get_categories(self) -> Set[URLCategory]:
        """
        Get all available categories.
        
        Returns:
            Set of categories
        """
        pass