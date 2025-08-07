"""
Plugin Interface Module

This module defines the interfaces that plugins must implement to be compatible
with the URL Analyzer plugin system.
"""

import os
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple

from url_analyzer.core.strategies import ClassificationStrategy
from url_analyzer.reporting.generators import ReportGenerator


class Plugin(ABC):
    """
    Base plugin interface that all plugins must implement.
    
    This abstract class defines the common methods that all plugins must implement,
    regardless of their specific functionality.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the plugin.
        
        Returns:
            String name of the plugin
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        Returns the version of the plugin.
        
        Returns:
            String version of the plugin (e.g., "1.0.0")
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Returns a description of the plugin.
        
        Returns:
            String description of the plugin
        """
        pass
    
    @abstractmethod
    def get_author(self) -> str:
        """
        Returns the author of the plugin.
        
        Returns:
            String author of the plugin
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initializes the plugin with the given configuration.
        
        Args:
            config: Dictionary containing configuration values
            
        Returns:
            Boolean indicating whether initialization was successful
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Performs cleanup when the plugin is being unloaded.
        
        Returns:
            Boolean indicating whether shutdown was successful
        """
        pass


class URLClassifierPlugin(Plugin):
    """
    Interface for URL classifier plugins.
    
    URL classifier plugins provide custom URL classification strategies that can
    be used by the URL Analyzer system.
    """
    
    @abstractmethod
    def get_strategy(self) -> ClassificationStrategy:
        """
        Returns the classification strategy implemented by this plugin.
        
        Returns:
            ClassificationStrategy instance
        """
        pass
    
    @abstractmethod
    def classify_url(self, url: str) -> Tuple[str, bool]:
        """
        Classifies a URL using the plugin's strategy.
        
        Args:
            url: URL to classify
            
        Returns:
            Tuple of (category, is_sensitive)
        """
        pass


class ReportGeneratorPlugin(Plugin):
    """
    Interface for report generator plugins.
    
    Report generator plugins provide custom report generation capabilities that
    can be used by the URL Analyzer system.
    """
    
    @abstractmethod
    def get_generator(self) -> ReportGenerator:
        """
        Returns the report generator implemented by this plugin.
        
        Returns:
            ReportGenerator instance
        """
        pass
    
    @abstractmethod
    def get_format(self) -> str:
        """
        Returns the format name supported by this plugin.
        
        Returns:
            String format name (e.g., "html", "csv", "custom")
        """
        pass
    
    @abstractmethod
    def generate_report(self, df: pd.DataFrame, output_path: str, stats: Dict[str, Any]) -> str:
        """
        Generates a report using the plugin's generator.
        
        Args:
            df: DataFrame containing URL data
            output_path: Path where to save the report
            stats: Dictionary of statistics for the report
            
        Returns:
            Path to the generated report
        """
        pass