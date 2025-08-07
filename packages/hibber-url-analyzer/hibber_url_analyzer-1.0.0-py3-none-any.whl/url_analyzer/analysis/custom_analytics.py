"""
Custom Analytics Module for URL Analysis.

This module provides support for user-defined metrics and custom analytics
for URL data analysis. It allows users to define their own metrics, filters,
and analysis functions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from datetime import datetime, timedelta
import json
from collections import Counter
import math
import logging
import os
import re

from url_analyzer.analysis.interfaces import ContentAnalyzer
from url_analyzer.analysis.domain import URLContent, AnalysisResult, AnalysisOptions

logger = logging.getLogger(__name__)

class CustomMetric:
    """
    Represents a user-defined metric for URL analysis.
    
    This class encapsulates a custom metric definition, including
    the calculation function, name, description, and any parameters.
    """
    
    def __init__(
        self,
        name: str,
        calculation_fn: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a custom metric.
        
        Args:
            name: Name of the metric
            calculation_fn: Function that calculates the metric
            description: Description of the metric
            parameters: Parameters for the calculation function
        """
        self.name = name
        self.calculation_fn = calculation_fn
        self.description = description
        self.parameters = parameters or {}
    
    def calculate(self, data: Any) -> Any:
        """
        Calculate the metric value for the given data.
        
        Args:
            data: Data to calculate the metric for
            
        Returns:
            Calculated metric value
        """
        try:
            return self.calculation_fn(data, **self.parameters)
        except Exception as e:
            logger.error(f"Error calculating metric '{self.name}': {str(e)}")
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metric to a dictionary.
        
        Returns:
            Dictionary representation of the metric
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class CustomAnalyzer:
    """
    Analyzer for custom metrics and analytics.
    
    This class provides functionality for defining and calculating
    custom metrics for URL data analysis.
    """
    
    def __init__(self):
        """Initialize the custom analyzer."""
        self.metrics: Dict[str, CustomMetric] = {}
    
    def register_metric(self, metric: CustomMetric) -> None:
        """
        Register a custom metric.
        
        Args:
            metric: Custom metric to register
        """
        self.metrics[metric.name] = metric
        logger.info(f"Registered custom metric: {metric.name}")
    
    def unregister_metric(self, metric_name: str) -> bool:
        """
        Unregister a custom metric.
        
        Args:
            metric_name: Name of the metric to unregister
            
        Returns:
            True if the metric was unregistered, False otherwise
        """
        if metric_name in self.metrics:
            del self.metrics[metric_name]
            logger.info(f"Unregistered custom metric: {metric_name}")
            return True
        return False
    
    def get_metric(self, metric_name: str) -> Optional[CustomMetric]:
        """
        Get a custom metric by name.
        
        Args:
            metric_name: Name of the metric to get
            
        Returns:
            Custom metric if found, None otherwise
        """
        return self.metrics.get(metric_name)
    
    def list_metrics(self) -> List[Dict[str, Any]]:
        """
        List all registered custom metrics.
        
        Returns:
            List of dictionaries containing metric information
        """
        return [metric.to_dict() for metric in self.metrics.values()]
    
    def calculate_metrics(
        self,
        data: Any,
        metric_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate custom metrics for the given data.
        
        Args:
            data: Data to calculate metrics for
            metric_names: Names of metrics to calculate (if None, calculate all)
            
        Returns:
            Dictionary mapping metric names to calculated values
        """
        results = {}
        
        metrics_to_calculate = (
            [self.metrics[name] for name in metric_names if name in self.metrics]
            if metric_names
            else self.metrics.values()
        )
        
        for metric in metrics_to_calculate:
            results[metric.name] = metric.calculate(data)
        
        return results
    
    def analyze_urls(
        self,
        urls: List[str],
        metric_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze URLs using custom metrics.
        
        Args:
            urls: List of URLs to analyze
            metric_names: Names of metrics to calculate (if None, calculate all)
            
        Returns:
            Dictionary containing analysis results
        """
        if not urls:
            return {"error": "No URLs provided"}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame({"url": urls})
        
        # Extract basic URL components
        df["domain"] = df["url"].apply(lambda url: url.split("/")[0] if "/" in url else url)
        df["path"] = df["url"].apply(
            lambda url: "/" + "/".join(url.split("/")[1:]) if "/" in url else ""
        )
        df["has_query"] = df["url"].apply(lambda url: "?" in url)
        df["has_fragment"] = df["url"].apply(lambda url: "#" in url)
        
        # Calculate metrics
        results = self.calculate_metrics(df, metric_names)
        
        # Add basic statistics
        results["url_count"] = len(urls)
        results["unique_domains"] = df["domain"].nunique()
        
        return results
    
    def analyze_url_data(
        self,
        url_data: List[Dict[str, Any]],
        metric_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze URL data using custom metrics.
        
        Args:
            url_data: List of URL data dictionaries
            metric_names: Names of metrics to calculate (if None, calculate all)
            
        Returns:
            Dictionary containing analysis results
        """
        if not url_data:
            return {"error": "No URL data provided"}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(url_data)
        
        # Calculate metrics
        results = self.calculate_metrics(df, metric_names)
        
        # Add basic statistics
        results["record_count"] = len(df)
        
        return results


class CustomContentAnalyzer(ContentAnalyzer):
    """
    Content analyzer that applies custom metrics to URL content.
    
    This class implements the ContentAnalyzer interface to provide
    custom analysis of URL content.
    """
    
    def __init__(
        self,
        name: str = "Custom Content Analyzer",
        metrics: Optional[List[CustomMetric]] = None
    ):
        """
        Initialize the custom content analyzer.
        
        Args:
            name: Name of the analyzer
            metrics: List of custom metrics to use
        """
        self.name = name
        self.custom_analyzer = CustomAnalyzer()
        
        if metrics:
            for metric in metrics:
                self.custom_analyzer.register_metric(metric)
    
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> AnalysisResult:
        """
        Analyze URL content using custom metrics.
        
        Args:
            content: URL content to analyze
            options: Analysis options
            
        Returns:
            Analysis result
        """
        if not content.is_success():
            return AnalysisResult(
                url=content.url,
                success=False,
                error="Content fetch was not successful",
                metadata={}
            )
        
        metadata = {}
        metadata["analyzer"] = self.name
        
        try:
            # Extract text content
            text_content = ""
            if content.is_html():
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content.content, 'html.parser')
                    text_content = soup.get_text()
                except ImportError:
                    # Fall back to simple regex if BeautifulSoup is not available
                    import re
                    text_content = re.sub(r'<[^>]+>', ' ', content.content)
            elif content.is_json():
                # Convert JSON to string representation
                try:
                    json_data = json.loads(content.content)
                    text_content = json.dumps(json_data)
                except json.JSONDecodeError:
                    text_content = content.content
            else:
                text_content = content.content
            
            if not text_content:
                metadata["error"] = "No text content available for analysis"
                return AnalysisResult(
                    url=content.url,
                    success=False,
                    metadata=metadata
                )
            
            # Create data dictionary for custom metrics
            data = {
                "url": content.url,
                "content": text_content,
                "content_type": content.content_type,
                "headers": content.headers,
                "status_code": content.status_code,
                "size_bytes": content.size_bytes
            }
            
            # Calculate custom metrics
            custom_results = self.custom_analyzer.calculate_metrics(data)
            
            # Add custom metrics to metadata
            metadata.update(custom_results)
            
            return AnalysisResult(
                url=content.url,
                success=True,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error in custom content analysis: {str(e)}")
            metadata["error"] = str(e)
            return AnalysisResult(
                url=content.url,
                success=False,
                metadata=metadata
            )
    
    def get_name(self) -> str:
        """
        Get the name of the analyzer.
        
        Returns:
            Analyzer name
        """
        return self.name
    
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types
        """
        return {"text/html", "application/json", "text/plain"}
    
    def register_metric(self, metric: CustomMetric) -> None:
        """
        Register a custom metric.
        
        Args:
            metric: Custom metric to register
        """
        self.custom_analyzer.register_metric(metric)
    
    def unregister_metric(self, metric_name: str) -> bool:
        """
        Unregister a custom metric.
        
        Args:
            metric_name: Name of the metric to unregister
            
        Returns:
            True if the metric was unregistered, False otherwise
        """
        return self.custom_analyzer.unregister_metric(metric_name)
    
    def list_metrics(self) -> List[Dict[str, Any]]:
        """
        List all registered custom metrics.
        
        Returns:
            List of dictionaries containing metric information
        """
        return self.custom_analyzer.list_metrics()


# Example custom metrics

def word_frequency_distribution(data: Any, top_n: int = 10) -> Dict[str, int]:
    """
    Calculate word frequency distribution.
    
    Args:
        data: Data containing text content
        top_n: Number of top words to return
        
    Returns:
        Dictionary mapping words to frequencies
    """
    if isinstance(data, dict) and "content" in data:
        text = data["content"]
    elif isinstance(data, pd.DataFrame) and "content" in data.columns:
        text = " ".join(data["content"].astype(str))
    else:
        text = str(data)
    
    # Tokenize text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Return top N words
    return dict(word_counts.most_common(top_n))


def readability_score(data: Any) -> float:
    """
    Calculate readability score (simplified Flesch-Kincaid).
    
    Args:
        data: Data containing text content
        
    Returns:
        Readability score (higher is easier to read)
    """
    if isinstance(data, dict) and "content" in data:
        text = data["content"]
    elif isinstance(data, pd.DataFrame) and "content" in data.columns:
        text = " ".join(data["content"].astype(str))
    else:
        text = str(data)
    
    # Count sentences, words, and syllables
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    # Simplified syllable count (count vowel groups)
    syllable_pattern = re.compile(r'[aeiouy]+', re.IGNORECASE)
    syllable_count = sum(len(re.findall(syllable_pattern, word)) for word in words)
    
    if sentence_count == 0 or word_count == 0:
        return 0
    
    # Simplified Flesch-Kincaid formula
    return 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)


def sentiment_analysis(data: Any) -> Dict[str, float]:
    """
    Perform simple sentiment analysis.
    
    Args:
        data: Data containing text content
        
    Returns:
        Dictionary with positive, negative, and compound sentiment scores
    """
    if isinstance(data, dict) and "content" in data:
        text = data["content"]
    elif isinstance(data, pd.DataFrame) and "content" in data.columns:
        text = " ".join(data["content"].astype(str))
    else:
        text = str(data)
    
    # Simple sentiment analysis using word lists
    positive_words = [
        "good", "great", "excellent", "best", "positive", "nice", "love", "perfect",
        "happy", "joy", "wonderful", "fantastic", "amazing", "awesome", "superb"
    ]
    negative_words = [
        "bad", "worst", "terrible", "poor", "negative", "hate", "awful", "horrible",
        "sad", "anger", "angry", "disappointing", "disappointed", "failure", "fail"
    ]
    
    # Tokenize text
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    if word_count == 0:
        return {"positive": 0, "negative": 0, "compound": 0}
    
    # Count positive and negative words
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    # Calculate scores
    positive_score = positive_count / word_count
    negative_score = negative_count / word_count
    compound_score = positive_score - negative_score
    
    return {
        "positive": positive_score,
        "negative": negative_score,
        "compound": compound_score
    }


def domain_category_distribution(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate distribution of URL categories by domain.
    
    Args:
        data: DataFrame containing URL data
        
    Returns:
        Dictionary mapping categories to proportions
    """
    if not isinstance(data, pd.DataFrame):
        return {}
    
    if "domain" not in data.columns or "category" not in data.columns:
        return {}
    
    # Count categories by domain
    category_counts = data.groupby("domain")["category"].value_counts().unstack().fillna(0)
    
    # Calculate proportions
    category_props = category_counts.sum() / category_counts.sum().sum()
    
    return category_props.to_dict()


def url_complexity_score(data: Any) -> float:
    """
    Calculate URL complexity score.
    
    Args:
        data: Data containing URLs
        
    Returns:
        Complexity score (higher is more complex)
    """
    if isinstance(data, dict) and "url" in data:
        url = data["url"]
    elif isinstance(data, pd.DataFrame) and "url" in data.columns:
        # Average complexity across all URLs
        return data["url"].apply(url_complexity_score).mean()
    else:
        url = str(data)
    
    # Count components that contribute to complexity
    score = 0
    
    # Length
    score += len(url) * 0.1
    
    # Special characters
    score += url.count('/') * 0.5
    score += url.count('?') * 2
    score += url.count('&') * 1
    score += url.count('=') * 0.5
    score += url.count('#') * 1
    score += url.count('%') * 2  # URL encoding
    
    # Query parameters
    if '?' in url:
        query_part = url.split('?', 1)[1].split('#', 1)[0]
        params = query_part.split('&')
        score += len(params) * 2
    
    return score


# Register default custom metrics
default_metrics = [
    CustomMetric(
        name="word_frequency",
        calculation_fn=word_frequency_distribution,
        description="Word frequency distribution in content",
        parameters={"top_n": 10}
    ),
    CustomMetric(
        name="readability",
        calculation_fn=readability_score,
        description="Readability score (higher is easier to read)"
    ),
    CustomMetric(
        name="sentiment",
        calculation_fn=sentiment_analysis,
        description="Sentiment analysis scores"
    ),
    CustomMetric(
        name="url_complexity",
        calculation_fn=url_complexity_score,
        description="URL complexity score (higher is more complex)"
    )
]