"""
Pattern-based URL Classification Service

This module provides a pattern-based implementation of the URLClassificationService interface.
It classifies URLs based on regex patterns and rules.
"""

import json
import os
import re
from typing import Dict, List, Tuple, Any, Optional

from url_analyzer.domain.value_objects import URLPattern, URLClassificationRule
from url_analyzer.application.interfaces import URLClassificationService


class PatternURLClassificationService(URLClassificationService):
    """
    Pattern-based implementation of the URLClassificationService interface.
    
    This class classifies URLs based on regex patterns and rules.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the service with a configuration file.
        
        Args:
            config_path: Path to the configuration file containing classification patterns
        """
        self.config_path = config_path
        self.rules: List[URLClassificationRule] = []
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load classification rules from the configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load sensitive patterns
            sensitive_patterns = config.get('sensitive_patterns', [])
            for pattern_str in sensitive_patterns:
                pattern = URLPattern(pattern_str)
                rule = URLClassificationRule(
                    name=f"Sensitive: {pattern_str}",
                    patterns=[pattern],
                    category="SENSITIVE",
                    sensitivity=True,
                    priority=100
                )
                self.rules.append(rule)
            
            # Load UGC patterns
            ugc_patterns = config.get('ugc_patterns', [])
            for pattern_str in ugc_patterns:
                pattern = URLPattern(pattern_str)
                rule = URLClassificationRule(
                    name=f"UGC: {pattern_str}",
                    patterns=[pattern],
                    category="UGC",
                    sensitivity=True,
                    priority=90
                )
                self.rules.append(rule)
            
            # Load junk subcategories
            junk_subcategories = config.get('junk_subcategories', {})
            for subcategory, patterns in junk_subcategories.items():
                for pattern_str in patterns:
                    pattern = URLPattern(pattern_str)
                    rule = URLClassificationRule(
                        name=f"Junk ({subcategory}): {pattern_str}",
                        patterns=[pattern],
                        category=subcategory.upper(),
                        sensitivity=False,
                        priority=80
                    )
                    self.rules.append(rule)
            
            # Sort rules by priority (highest first)
            self.rules.sort(key=lambda r: r.priority, reverse=True)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Error loading configuration: {str(e)}")
    
    def classify(self, url: str) -> Tuple[str, bool]:
        """
        Classify a URL.
        
        Args:
            url: The URL to classify
            
        Returns:
            A tuple of (category, is_sensitive)
        """
        # Default classification
        category = "UNKNOWN"
        is_sensitive = False
        
        # Check each rule in order of priority
        for rule in self.rules:
            if rule.matches(url):
                category, is_sensitive = rule.get_classification()
                break
        
        return category, is_sensitive
    
    def get_rules(self) -> List[URLClassificationRule]:
        """
        Get all classification rules.
        
        Returns:
            A list of all classification rules
        """
        return self.rules.copy()
    
    def add_rule(self, rule: URLClassificationRule) -> None:
        """
        Add a classification rule.
        
        Args:
            rule: The rule to add
        """
        # Check if a rule with the same name already exists
        for existing_rule in self.rules:
            if existing_rule.name == rule.name:
                # Replace the existing rule
                self.rules.remove(existing_rule)
                break
        
        # Add the new rule
        self.rules.append(rule)
        
        # Re-sort rules by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a classification rule.
        
        Args:
            rule_name: The name of the rule to remove
            
        Returns:
            True if the rule was removed, False otherwise
        """
        for rule in self.rules:
            if rule.name == rule_name:
                self.rules.remove(rule)
                return True
        
        return False