"""
URL Classification Services

This module provides services for URL classification based on the interfaces
defined in the interfaces module. It implements the core functionality for
classifying URLs using different strategies.
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from concurrent.futures import ThreadPoolExecutor

from url_analyzer.utils.optimized_concurrency import optimized_thread_pool

from url_analyzer.classification.domain import (
    URLCategory, ClassificationRule, ClassificationPattern, 
    ClassificationResult, RuleSet
)
from url_analyzer.classification.interfaces import (
    URLClassifier, RuleRepository, PatternRepository, ClassificationService
)


class PatternBasedClassifier(URLClassifier):
    """
    Classifier that uses regex patterns to classify URLs.
    """
    
    def __init__(self, 
                 patterns: Dict[URLCategory, List[ClassificationPattern]],
                 sensitive_patterns: Optional[List[ClassificationPattern]] = None,
                 name: str = "Pattern-Based Classifier"):
        """
        Initialize the classifier with patterns.
        
        Args:
            patterns: Dictionary mapping categories to lists of patterns
            sensitive_patterns: Optional list of patterns indicating sensitive content
            name: Name of this classifier
        """
        self._patterns = patterns
        self._sensitive_patterns = sensitive_patterns or []
        self._name = name
    
    def classify_url(self, url: str) -> ClassificationResult:
        """
        Classify a URL using regex patterns.
        
        Args:
            url: URL to classify
            
        Returns:
            ClassificationResult containing the classification details
        """
        # Check if URL is empty
        if not url or not url.strip():
            default_category = URLCategory(name="Empty or Invalid")
            return ClassificationResult(url=url, category=default_category, is_sensitive=False)
        
        # Check for sensitive content first
        is_sensitive = any(pattern.matches(url) for pattern in self._sensitive_patterns)
        
        # Check each category's patterns
        for category, patterns in self._patterns.items():
            for pattern in patterns:
                if pattern.matches(url):
                    return ClassificationResult(
                        url=url,
                        category=category,
                        is_sensitive=is_sensitive or pattern.is_sensitive,
                        matched_pattern=pattern
                    )
        
        # Default category if no patterns match
        default_category = URLCategory(name="Uncategorized")
        return ClassificationResult(url=url, category=default_category, is_sensitive=is_sensitive)
    
    def get_name(self) -> str:
        """
        Get the name of this classifier.
        
        Returns:
            Classifier name
        """
        return self._name
    
    def get_categories(self) -> List[URLCategory]:
        """
        Get the list of categories supported by this classifier.
        
        Returns:
            List of category objects
        """
        return list(self._patterns.keys())


class RuleBasedClassifier(URLClassifier):
    """
    Classifier that uses rules to classify URLs.
    """
    
    def __init__(self, rule_set: RuleSet, name: str = "Rule-Based Classifier"):
        """
        Initialize the classifier with a rule set.
        
        Args:
            rule_set: Rule set to use for classification
            name: Name of this classifier
        """
        self._rule_set = rule_set
        self._name = name
    
    def classify_url(self, url: str) -> ClassificationResult:
        """
        Classify a URL using rules.
        
        Args:
            url: URL to classify
            
        Returns:
            ClassificationResult containing the classification details
        """
        # Check if URL is empty
        if not url or not url.strip():
            default_category = URLCategory(name="Empty or Invalid")
            return ClassificationResult(url=url, category=default_category, is_sensitive=False)
        
        # Get the best matching rule
        rule = self._rule_set.get_best_match(url)
        
        if rule:
            return ClassificationResult(
                url=url,
                category=rule.category,
                is_sensitive=rule.is_sensitive,
                matched_rule=rule
            )
        
        # Default category if no rules match
        default_category = URLCategory(name="Uncategorized")
        return ClassificationResult(url=url, category=default_category, is_sensitive=False)
    
    def get_name(self) -> str:
        """
        Get the name of this classifier.
        
        Returns:
            Classifier name
        """
        return self._name
    
    def get_categories(self) -> List[URLCategory]:
        """
        Get the list of categories supported by this classifier.
        
        Returns:
            List of category objects
        """
        return list(self._rule_set.get_categories())


class CompositeClassifier(URLClassifier):
    """
    Classifier that combines multiple classifiers.
    """
    
    def __init__(self, classifiers: List[URLClassifier], name: str = "Composite Classifier"):
        """
        Initialize the classifier with a list of classifiers.
        
        Args:
            classifiers: List of classifiers to use
            name: Name of this classifier
        """
        self._classifiers = classifiers
        self._name = name
    
    def classify_url(self, url: str) -> ClassificationResult:
        """
        Classify a URL using multiple classifiers.
        
        Args:
            url: URL to classify
            
        Returns:
            ClassificationResult containing the classification details
        """
        # Check if URL is empty
        if not url or not url.strip():
            default_category = URLCategory(name="Empty or Invalid")
            return ClassificationResult(url=url, category=default_category, is_sensitive=False)
        
        # Try each classifier in order
        for classifier in self._classifiers:
            result = classifier.classify_url(url)
            if result.category.name != "Uncategorized":
                return result
        
        # If all classifiers return Uncategorized, use the last result
        if self._classifiers:
            return self._classifiers[-1].classify_url(url)
        
        # Default category if no classifiers are available
        default_category = URLCategory(name="Uncategorized")
        return ClassificationResult(url=url, category=default_category, is_sensitive=False)
    
    def get_name(self) -> str:
        """
        Get the name of this classifier.
        
        Returns:
            Classifier name
        """
        return self._name
    
    def get_categories(self) -> List[URLCategory]:
        """
        Get the list of categories supported by this classifier.
        
        Returns:
            List of category objects
        """
        categories = set()
        for classifier in self._classifiers:
            categories.update(classifier.get_categories())
        return list(categories)


class InMemoryRuleRepository(RuleRepository):
    """
    In-memory implementation of the rule repository.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        """
        self._rules: Dict[str, ClassificationRule] = {}
    
    def get_rules(self) -> List[ClassificationRule]:
        """
        Get all rules.
        
        Returns:
            List of rules
        """
        return list(self._rules.values())
    
    def add_rule(self, rule: ClassificationRule) -> None:
        """
        Add a rule.
        
        Args:
            rule: Rule to add
        """
        self._rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str) -> None:
        """
        Remove a rule.
        
        Args:
            rule_id: ID of the rule to remove
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
    
    def get_rule(self, rule_id: str) -> Optional[ClassificationRule]:
        """
        Get a rule by ID.
        
        Args:
            rule_id: ID of the rule to get
            
        Returns:
            Rule or None if not found
        """
        return self._rules.get(rule_id)
    
    def get_rule_set(self, name: Optional[str] = None) -> RuleSet:
        """
        Get a rule set.
        
        Args:
            name: Optional name of the rule set to get
            
        Returns:
            Rule set
        """
        return RuleSet(
            rules=list(self._rules.values()),
            name=name or "Default Rule Set"
        )


class InMemoryPatternRepository(PatternRepository):
    """
    In-memory implementation of the pattern repository.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        """
        self._patterns: List[ClassificationPattern] = []
    
    def get_patterns(self) -> List[ClassificationPattern]:
        """
        Get all patterns.
        
        Returns:
            List of patterns
        """
        return self._patterns
    
    def add_pattern(self, pattern: ClassificationPattern) -> None:
        """
        Add a pattern.
        
        Args:
            pattern: Pattern to add
        """
        self._patterns.append(pattern)
    
    def remove_pattern(self, pattern_str: str) -> None:
        """
        Remove a pattern.
        
        Args:
            pattern_str: Pattern string to remove
        """
        self._patterns = [p for p in self._patterns if p.pattern != pattern_str]
    
    def get_patterns_by_category(self, category: URLCategory) -> List[ClassificationPattern]:
        """
        Get patterns by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of patterns for the given category
        """
        return [p for p in self._patterns if p.category == category]


class DefaultClassificationService(ClassificationService):
    """
    Default implementation of the classification service.
    """
    
    def __init__(self):
        """
        Initialize the service.
        """
        self._classifiers: Dict[str, URLClassifier] = {}
        self._default_classifier: Optional[URLClassifier] = None
    
    def classify_url(self, url: str) -> ClassificationResult:
        """
        Classify a URL.
        
        Args:
            url: URL to classify
            
        Returns:
            ClassificationResult containing the classification details
        """
        if self._default_classifier:
            return self._default_classifier.classify_url(url)
        
        # If no default classifier is set, use a composite of all classifiers
        if self._classifiers:
            composite = CompositeClassifier(list(self._classifiers.values()))
            return composite.classify_url(url)
        
        # Default category if no classifiers are available
        default_category = URLCategory(name="Uncategorized")
        return ClassificationResult(url=url, category=default_category, is_sensitive=False)
    
    def classify_urls(self, urls: List[str]) -> Dict[str, ClassificationResult]:
        """
        Classify multiple URLs.
        
        Args:
            urls: List of URLs to classify
            
        Returns:
            Dictionary mapping URLs to their classification results
        """
        results = {}
        
        # Use optimized ThreadPoolExecutor for parallel classification
        with optimized_thread_pool(
            workload_type="cpu_bound",  # Classification is primarily CPU-bound pattern matching
            task_count=len(urls)
        ) as executor:
            future_to_url = {executor.submit(self.classify_url, url): url for url in urls}
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    # Handle classification errors
                    default_category = URLCategory(name="Error")
                    results[url] = ClassificationResult(
                        url=url,
                        category=default_category,
                        is_sensitive=False,
                        confidence=0.0
                    )
        
        return results
    
    def get_classifiers(self) -> List[URLClassifier]:
        """
        Get all available classifiers.
        
        Returns:
            List of classifiers
        """
        return list(self._classifiers.values())
    
    def add_classifier(self, classifier: URLClassifier) -> None:
        """
        Add a classifier.
        
        Args:
            classifier: Classifier to add
        """
        self._classifiers[classifier.get_name()] = classifier
        
        # If no default classifier is set, use the first one added
        if self._default_classifier is None:
            self._default_classifier = classifier
    
    def remove_classifier(self, name: str) -> None:
        """
        Remove a classifier.
        
        Args:
            name: Name of the classifier to remove
        """
        if name in self._classifiers:
            # If removing the default classifier, set a new default
            if self._default_classifier == self._classifiers[name]:
                self._default_classifier = next(iter(self._classifiers.values())) if self._classifiers else None
            
            del self._classifiers[name]
    
    def get_categories(self) -> Set[URLCategory]:
        """
        Get all available categories.
        
        Returns:
            Set of categories
        """
        categories = set()
        for classifier in self._classifiers.values():
            categories.update(classifier.get_categories())
        return categories
    
    def set_default_classifier(self, name: str) -> bool:
        """
        Set the default classifier.
        
        Args:
            name: Name of the classifier to set as default
            
        Returns:
            True if successful, False if the classifier was not found
        """
        if name in self._classifiers:
            self._default_classifier = self._classifiers[name]
            return True
        return False


def create_pattern_based_classifier_from_config(config: Dict[str, Any]) -> PatternBasedClassifier:
    """
    Create a pattern-based classifier from a configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        PatternBasedClassifier instance
    """
    # Create categories
    categories = {}
    for category_name in config.get("patterns", {}):
        categories[category_name] = URLCategory(name=category_name)
    
    # Create patterns
    patterns: Dict[URLCategory, List[ClassificationPattern]] = {category: [] for category in categories.values()}
    for category_name, pattern_strings in config.get("patterns", {}).items():
        category = categories[category_name]
        for pattern_string in pattern_strings:
            pattern = ClassificationPattern.create(
                pattern=pattern_string,
                category=category,
                is_sensitive=False
            )
            patterns[category].append(pattern)
    
    # Create sensitive patterns
    sensitive_patterns = []
    for pattern_string in config.get("sensitive_patterns", []):
        # Find the category for this pattern
        for category_name, pattern_strings in config.get("patterns", {}).items():
            if pattern_string in pattern_strings:
                category = categories[category_name]
                pattern = ClassificationPattern.create(
                    pattern=pattern_string,
                    category=category,
                    is_sensitive=True
                )
                sensitive_patterns.append(pattern)
                break
    
    return PatternBasedClassifier(
        patterns=patterns,
        sensitive_patterns=sensitive_patterns,
        name=config.get("name", "Pattern-Based Classifier")
    )


def create_rule_based_classifier_from_config(config: Dict[str, Any]) -> RuleBasedClassifier:
    """
    Create a rule-based classifier from a configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        RuleBasedClassifier instance
    """
    # Create categories
    categories = {}
    for category_name in config.get("categories", {}):
        categories[category_name] = URLCategory(name=category_name)
    
    # Create rules
    rules = []
    for rule_config in config.get("rules", []):
        category_name = rule_config.get("category", "Uncategorized")
        category = categories.get(category_name, URLCategory(name=category_name))
        
        # Create patterns for this rule
        patterns = []
        for pattern_string in rule_config.get("patterns", []):
            pattern = ClassificationPattern.create(
                pattern=pattern_string,
                category=category,
                is_sensitive=rule_config.get("is_sensitive", False)
            )
            patterns.append(pattern)
        
        # Create the rule
        rule = ClassificationRule(
            rule_id=rule_config.get("id", f"rule_{len(rules)}"),
            name=rule_config.get("name", f"Rule {len(rules)}"),
            patterns=patterns,
            category=category,
            is_sensitive=rule_config.get("is_sensitive", False),
            priority=rule_config.get("priority", 0)
        )
        rules.append(rule)
    
    # Create the rule set
    rule_set = RuleSet(
        rules=rules,
        name=config.get("name", "Default Rule Set")
    )
    
    return RuleBasedClassifier(
        rule_set=rule_set,
        name=config.get("name", "Rule-Based Classifier")
    )