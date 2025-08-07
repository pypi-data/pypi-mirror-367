"""
URL Classification Domain Models

This module defines the domain models and value objects for the URL Classification domain.
These models represent the core concepts in URL classification and encapsulate domain logic.
"""

from dataclasses import dataclass
from typing import List, Pattern, Optional, Set
import re


@dataclass(frozen=True)
class URLCategory:
    """Value object representing a URL category."""
    
    name: str
    description: Optional[str] = None
    parent_category: Optional['URLCategory'] = None
    
    def __str__(self) -> str:
        return self.name
    
    def get_full_hierarchy(self) -> List[str]:
        """
        Get the full category hierarchy as a list of category names.
        
        Returns:
            List of category names from root to this category
        """
        if self.parent_category is None:
            return [self.name]
        
        return self.parent_category.get_full_hierarchy() + [self.name]
    
    def is_subcategory_of(self, category: 'URLCategory') -> bool:
        """
        Check if this category is a subcategory of the given category.
        
        Args:
            category: Category to check against
            
        Returns:
            True if this category is a subcategory of the given category, False otherwise
        """
        if self == category:
            return True
        
        if self.parent_category is None:
            return False
        
        return self.parent_category.is_subcategory_of(category)


@dataclass(frozen=True)
class ClassificationPattern:
    """Value object representing a classification pattern."""
    
    pattern: str
    compiled_pattern: Pattern
    category: URLCategory
    is_sensitive: bool = False
    
    @classmethod
    def create(cls, pattern: str, category: URLCategory, is_sensitive: bool = False) -> 'ClassificationPattern':
        """
        Create a ClassificationPattern with a compiled regex pattern.
        
        Args:
            pattern: Regex pattern string
            category: Category for this pattern
            is_sensitive: Whether this pattern indicates sensitive content
            
        Returns:
            ClassificationPattern instance
        """
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        return cls(pattern=pattern, compiled_pattern=compiled_pattern, category=category, is_sensitive=is_sensitive)
    
    def matches(self, url: str) -> bool:
        """
        Check if this pattern matches the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if the pattern matches, False otherwise
        """
        return bool(self.compiled_pattern.search(url))


@dataclass(frozen=True)
class ClassificationRule:
    """Value object representing a classification rule."""
    
    rule_id: str
    name: str
    patterns: List[ClassificationPattern]
    category: URLCategory
    is_sensitive: bool = False
    priority: int = 0
    
    def matches(self, url: str) -> bool:
        """
        Check if this rule matches the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if any pattern matches, False otherwise
        """
        return any(pattern.matches(url) for pattern in self.patterns)


@dataclass(frozen=True)
class ClassificationResult:
    """Value object representing the result of a URL classification."""
    
    url: str
    category: URLCategory
    is_sensitive: bool
    matched_rule: Optional[ClassificationRule] = None
    matched_pattern: Optional[ClassificationPattern] = None
    confidence: float = 1.0
    
    def __str__(self) -> str:
        return f"{self.url}: {self.category} (Sensitive: {self.is_sensitive})"


@dataclass(frozen=True)
class RuleSet:
    """Value object representing a set of classification rules."""
    
    rules: List[ClassificationRule]
    name: str = "Default Rule Set"
    description: Optional[str] = None
    
    def get_matching_rules(self, url: str) -> List[ClassificationRule]:
        """
        Get all rules that match the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            List of matching rules, sorted by priority (highest first)
        """
        matching_rules = [rule for rule in self.rules if rule.matches(url)]
        return sorted(matching_rules, key=lambda r: r.priority, reverse=True)
    
    def get_best_match(self, url: str) -> Optional[ClassificationRule]:
        """
        Get the best matching rule for the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            Best matching rule or None if no rules match
        """
        matching_rules = self.get_matching_rules(url)
        return matching_rules[0] if matching_rules else None
    
    def get_categories(self) -> Set[URLCategory]:
        """
        Get all categories used by the rules in this rule set.
        
        Returns:
            Set of categories
        """
        return {rule.category for rule in self.rules}