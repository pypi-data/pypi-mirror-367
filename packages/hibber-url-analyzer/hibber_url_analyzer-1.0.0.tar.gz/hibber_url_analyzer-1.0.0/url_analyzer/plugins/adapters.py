"""
Plugin Adapters Module

This module provides adapter classes that bridge the existing URL classification
and report generation systems with the plugin system.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Type

from url_analyzer.core.strategies import ClassificationStrategy
from url_analyzer.reporting.generators import ReportGenerator
from url_analyzer.plugins.interface import Plugin, URLClassifierPlugin, ReportGeneratorPlugin
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


class PluginClassificationStrategy(ClassificationStrategy):
    """
    Adapter that allows a URLClassifierPlugin to be used as a ClassificationStrategy.
    
    This adapter bridges the gap between the plugin system and the existing
    URL classification system, allowing plugins to be used seamlessly.
    """
    
    def __init__(self, plugin: URLClassifierPlugin):
        """
        Initializes a new PluginClassificationStrategy.
        
        Args:
            plugin: URLClassifierPlugin instance to adapt
        """
        self.plugin = plugin
        logger.info(f"Created PluginClassificationStrategy for plugin: {plugin.get_name()}")
    
    def classify_url(self, url: str) -> Tuple[str, bool]:
        """
        Classifies a URL using the plugin's classify_url method.
        
        Args:
            url: URL to classify
            
        Returns:
            Tuple of (category, is_sensitive)
        """
        return self.plugin.classify_url(url)
    
    def get_name(self) -> str:
        """
        Returns the name of the strategy.
        
        Returns:
            String name of the strategy
        """
        return f"Plugin: {self.plugin.get_name()}"


class PluginReportGenerator(ReportGenerator):
    """
    Adapter that allows a ReportGeneratorPlugin to be used as a ReportGenerator.
    
    This adapter bridges the gap between the plugin system and the existing
    report generation system, allowing plugins to be used seamlessly.
    """
    
    def __init__(self, plugin: ReportGeneratorPlugin):
        """
        Initializes a new PluginReportGenerator.
        
        Args:
            plugin: ReportGeneratorPlugin instance to adapt
        """
        self.plugin = plugin
        logger.info(f"Created PluginReportGenerator for plugin: {plugin.get_name()}")
    
    def generate_report(self, df: pd.DataFrame, output_path: str, stats: Dict[str, Any]) -> str:
        """
        Generates a report using the plugin's generate_report method.
        
        Args:
            df: DataFrame containing URL data
            output_path: Path where to save the report
            stats: Dictionary of statistics for the report
            
        Returns:
            Path to the generated report
        """
        return self.plugin.generate_report(df, output_path, stats)
    
    def get_format(self) -> str:
        """
        Returns the format name supported by this generator.
        
        Returns:
            String format name
        """
        return self.plugin.get_format()


def get_plugin_classification_strategies(registry: PluginRegistry) -> List[ClassificationStrategy]:
    """
    Gets ClassificationStrategy instances for all URL classifier plugins in the registry.
    
    Args:
        registry: Plugin registry containing the plugins
        
    Returns:
        List of ClassificationStrategy instances
    """
    strategies = []
    
    for plugin in registry.get_all_url_classifier_plugins():
        # Only include initialized plugins
        if registry.is_plugin_initialized(plugin.get_name()):
            strategy = PluginClassificationStrategy(plugin)
            strategies.append(strategy)
    
    logger.info(f"Found {len(strategies)} plugin classification strategies")
    return strategies


def get_plugin_report_generators(registry: PluginRegistry) -> List[ReportGenerator]:
    """
    Gets ReportGenerator instances for all report generator plugins in the registry.
    
    Args:
        registry: Plugin registry containing the plugins
        
    Returns:
        List of ReportGenerator instances
    """
    generators = []
    
    for plugin in registry.get_all_report_generator_plugins():
        # Only include initialized plugins
        if registry.is_plugin_initialized(plugin.get_name()):
            generator = PluginReportGenerator(plugin)
            generators.append(generator)
    
    logger.info(f"Found {len(generators)} plugin report generators")
    return generators


def register_plugin_report_generators(registry: PluginRegistry) -> None:
    """
    Registers all plugin report generators with the ReportGeneratorFactory.
    
    This function makes plugin report generators available to the existing
    report generation system.
    
    Args:
        registry: Plugin registry containing the plugins
    """
    from url_analyzer.reporting.generators import ReportGeneratorFactory
    
    for plugin in registry.get_all_report_generator_plugins():
        # Only include initialized plugins
        if registry.is_plugin_initialized(plugin.get_name()):
            generator = PluginReportGenerator(plugin)
            format_name = generator.get_format()
            
            # Register the generator with the factory
            # This is a bit of a hack, but it works for now
            ReportGeneratorFactory._generators[format_name] = generator.__class__
            
            logger.info(f"Registered plugin report generator for format: {format_name}")