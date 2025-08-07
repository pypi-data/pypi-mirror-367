"""
Statistical Analysis Module

This module provides statistical analysis tools for URL data.
It includes functions for descriptive statistics, correlation analysis,
trend detection, and anomaly detection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import json
import math
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.neighbors import NearestNeighbors
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from url_analyzer.analysis.interfaces import ContentAnalyzer
from url_analyzer.analysis.domain import URLContent, AnalysisResult, AnalysisOptions


class StatisticalAnalyzer:
    """
    Provides statistical analysis tools for URL data.
    
    This class contains methods for analyzing URL data using statistical
    techniques, including descriptive statistics, correlation analysis,
    trend detection, anomaly detection, clustering, and pattern recognition.
    """
    
    @staticmethod
    def calculate_descriptive_stats(data: List[float]) -> Dict[str, float]:
        """
        Calculate descriptive statistics for a list of values.
        
        Args:
            data: List of numeric values
            
        Returns:
            Dictionary containing descriptive statistics
        """
        if not data:
            return {
                "count": 0,
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "q1": None,
                "q3": None
            }
        
        # Convert to numpy array for efficient calculations
        arr = np.array(data)
        
        return {
            "count": len(arr),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "q1": float(np.percentile(arr, 25)),
            "q3": float(np.percentile(arr, 75))
        }
    
    @staticmethod
    def calculate_frequency_distribution(
        data: List[Any], 
        bins: Optional[int] = None,
        normalize: bool = False
    ) -> Dict[str, Union[int, float]]:
        """
        Calculate frequency distribution for categorical or binned numerical data.
        
        Args:
            data: List of values
            bins: Number of bins for numerical data
            normalize: Whether to normalize frequencies to proportions
            
        Returns:
            Dictionary mapping categories/bins to frequencies/proportions
        """
        if not data:
            return {}
        
        # Check if data is numeric
        is_numeric = all(isinstance(x, (int, float)) for x in data if x is not None)
        
        if is_numeric and bins is not None:
            # Bin numerical data
            arr = np.array([x for x in data if x is not None])
            hist, bin_edges = np.histogram(arr, bins=bins)
            
            # Create bin labels
            bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]
            
            # Create frequency dictionary
            freq_dict = {bin_labels[i]: int(hist[i]) for i in range(len(hist))}
            
            # Normalize if requested
            if normalize and sum(hist) > 0:
                freq_dict = {k: float(v) / sum(hist) for k, v in freq_dict.items()}
            
            return freq_dict
        else:
            # Count frequencies for categorical data
            counter = Counter(data)
            
            # Normalize if requested
            if normalize and sum(counter.values()) > 0:
                return {str(k): float(v) / sum(counter.values()) for k, v in counter.items()}
            else:
                return {str(k): v for k, v in counter.items()}
    
    @staticmethod
    def calculate_correlation(
        x: List[float], 
        y: List[float],
        method: str = "pearson"
    ) -> Dict[str, float]:
        """
        Calculate correlation between two variables.
        
        Args:
            x: First variable
            y: Second variable
            method: Correlation method (pearson, spearman, kendall)
            
        Returns:
            Dictionary containing correlation coefficient and p-value
        """
        if not x or not y or len(x) != len(y):
            return {
                "coefficient": None,
                "p_value": None,
                "method": method
            }
        
        # Remove pairs with None values
        valid_pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
        if not valid_pairs:
            return {
                "coefficient": None,
                "p_value": None,
                "method": method
            }
        
        x_valid, y_valid = zip(*valid_pairs)
        
        # Calculate correlation
        if method.lower() == "pearson":
            coef, p_value = stats.pearsonr(x_valid, y_valid)
        elif method.lower() == "spearman":
            coef, p_value = stats.spearmanr(x_valid, y_valid)
        elif method.lower() == "kendall":
            coef, p_value = stats.kendalltau(x_valid, y_valid)
        else:
            raise ValueError(f"Unsupported correlation method: {method}")
        
        return {
            "coefficient": float(coef),
            "p_value": float(p_value),
            "method": method
        }
    
    @staticmethod
    def detect_trends(
        time_series: List[Tuple[datetime, float]],
        window_size: int = 7,
        method: str = "linear"
    ) -> Dict[str, Any]:
        """
        Detect trends in time series data.
        
        Args:
            time_series: List of (timestamp, value) tuples
            window_size: Size of the moving window for trend detection
            method: Trend detection method (linear, moving_average)
            
        Returns:
            Dictionary containing trend information
        """
        if not time_series or len(time_series) < 2:
            return {
                "trend": None,
                "slope": None,
                "p_value": None,
                "method": method
            }
        
        # Sort by timestamp
        time_series.sort(key=lambda x: x[0])
        
        # Extract timestamps and values
        timestamps = [ts for ts, _ in time_series]
        values = [val for _, val in time_series]
        
        # Convert timestamps to numeric values (days since first timestamp)
        first_timestamp = timestamps[0]
        days = [(ts - first_timestamp).total_seconds() / (24 * 3600) for ts in timestamps]
        
        if method.lower() == "linear":
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(days, values)
            
            # Determine trend direction
            if p_value <= 0.05:
                trend = "increasing" if slope > 0 else "decreasing"
            else:
                trend = "no_trend"
            
            return {
                "trend": trend,
                "slope": float(slope),
                "p_value": float(p_value),
                "r_squared": float(r_value ** 2),
                "method": method
            }
        
        elif method.lower() == "moving_average":
            # Calculate moving average
            if len(values) < window_size:
                window_size = len(values)
            
            moving_avg = []
            for i in range(len(values) - window_size + 1):
                window = values[i:i+window_size]
                moving_avg.append(sum(window) / window_size)
            
            # Calculate trend based on moving average
            if len(moving_avg) >= 2:
                # Linear regression on moving average
                ma_days = days[window_size-1:]
                slope, intercept, r_value, p_value, std_err = stats.linregress(ma_days, moving_avg)
                
                # Determine trend direction
                if p_value <= 0.05:
                    trend = "increasing" if slope > 0 else "decreasing"
                else:
                    trend = "no_trend"
                
                return {
                    "trend": trend,
                    "slope": float(slope),
                    "p_value": float(p_value),
                    "r_squared": float(r_value ** 2),
                    "method": method,
                    "window_size": window_size
                }
            else:
                return {
                    "trend": None,
                    "slope": None,
                    "p_value": None,
                    "method": method,
                    "window_size": window_size
                }
        
        else:
            raise ValueError(f"Unsupported trend detection method: {method}")
    
    @staticmethod
    def detect_anomalies(
        data: List[float],
        method: str = "isolation_forest",
        contamination: float = 0.05
    ) -> Dict[str, Any]:
        """
        Detect anomalies in a dataset.
        
        Args:
            data: List of values
            method: Anomaly detection method (isolation_forest, zscore, dbscan)
            contamination: Expected proportion of anomalies (for isolation_forest)
            
        Returns:
            Dictionary containing anomaly information
        """
        if not data or len(data) < 3:
            return {
                "anomalies": [],
                "anomaly_indices": [],
                "method": method
            }
        
        # Convert to numpy array and handle None values
        valid_data = [x for x in data if x is not None]
        if not valid_data:
            return {
                "anomalies": [],
                "anomaly_indices": [],
                "method": method
            }
        
        arr = np.array(valid_data).reshape(-1, 1)
        
        if method.lower() == "isolation_forest" and SKLEARN_AVAILABLE:
            # Isolation Forest algorithm
            model = IsolationForest(contamination=contamination, random_state=42)
            predictions = model.fit_predict(arr)
            
            # -1 indicates anomaly, 1 indicates normal
            anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
            anomalies = [valid_data[i] for i in anomaly_indices]
            
            return {
                "anomalies": anomalies,
                "anomaly_indices": anomaly_indices,
                "method": method,
                "contamination": contamination
            }
        elif method.lower() == "isolation_forest" and not SKLEARN_AVAILABLE:
            # Fallback to simple statistical method if sklearn is not available
            logger.warning("Isolation Forest method requested but sklearn is not available. Falling back to zscore method.")
            return StatisticalAnalyzer.detect_anomalies(data, method="zscore", contamination=contamination)
        
        elif method.lower() == "zscore":
            # Z-score method
            mean = np.mean(arr)
            std = np.std(arr)
            
            if std == 0:
                return {
                    "anomalies": [],
                    "anomaly_indices": [],
                    "method": method,
                    "threshold": 3.0
                }
            
            z_scores = [(x - mean) / std for x in valid_data]
            threshold = 3.0  # Common threshold for outliers
            
            anomaly_indices = [i for i, z in enumerate(z_scores) if abs(z) > threshold]
            anomalies = [valid_data[i] for i in anomaly_indices]
            
            return {
                "anomalies": anomalies,
                "anomaly_indices": anomaly_indices,
                "method": method,
                "threshold": threshold
            }
        
        elif method.lower() == "dbscan" and SKLEARN_AVAILABLE:
            # DBSCAN clustering
            scaler = StandardScaler()
            arr_scaled = scaler.fit_transform(arr)
            
            # Estimate epsilon based on data
            nn = NearestNeighbors(n_neighbors=min(len(arr_scaled), 5))
            nn.fit(arr_scaled)
            distances, _ = nn.kneighbors(arr_scaled)
            distances = np.sort(distances[:, 1:], axis=0)
            eps = np.mean(distances[:, 0]) * 2
            
            # Apply DBSCAN
            dbscan = DBSCAN(eps=eps, min_samples=max(3, int(len(arr_scaled) * 0.05)))
            clusters = dbscan.fit_predict(arr_scaled)
            
            # -1 indicates noise points (anomalies)
            anomaly_indices = [i for i, cluster in enumerate(clusters) if cluster == -1]
            anomalies = [valid_data[i] for i in anomaly_indices]
            
            return {
                "anomalies": anomalies,
                "anomaly_indices": anomaly_indices,
                "method": method,
                "eps": float(eps)
            }
        elif method.lower() == "dbscan" and not SKLEARN_AVAILABLE:
            # Fallback to simple statistical method if sklearn is not available
            logger.warning("DBSCAN method requested but sklearn is not available. Falling back to zscore method.")
            return StatisticalAnalyzer.detect_anomalies(data, method="zscore", contamination=contamination)
        
        else:
            raise ValueError(f"Unsupported anomaly detection method: {method}")
    
    @staticmethod
    def analyze_url_patterns(urls: List[str]) -> Dict[str, Any]:
        """
        Analyze patterns in a list of URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            Dictionary containing URL pattern analysis
        """
        if not urls:
            return {
                "domain_distribution": {},
                "path_length_stats": {},
                "query_param_stats": {},
                "common_path_segments": [],
                "common_query_params": []
            }
        
        import urllib.parse
        
        # Parse URLs
        parsed_urls = [urllib.parse.urlparse(url) for url in urls]
        
        # Domain distribution
        domains = [parsed.netloc for parsed in parsed_urls]
        domain_distribution = StatisticalAnalyzer.calculate_frequency_distribution(domains)
        
        # Path length statistics
        path_lengths = [len(parsed.path.split('/')) - 1 for parsed in parsed_urls]
        path_length_stats = StatisticalAnalyzer.calculate_descriptive_stats(path_lengths)
        
        # Query parameter statistics
        query_param_counts = []
        all_query_params = []
        
        for parsed in parsed_urls:
            if parsed.query:
                params = urllib.parse.parse_qs(parsed.query)
                query_param_counts.append(len(params))
                all_query_params.extend(params.keys())
            else:
                query_param_counts.append(0)
        
        query_param_stats = StatisticalAnalyzer.calculate_descriptive_stats(query_param_counts)
        
        # Common path segments
        all_path_segments = []
        for parsed in parsed_urls:
            segments = [s for s in parsed.path.split('/') if s]
            all_path_segments.extend(segments)
        
        path_segment_distribution = StatisticalAnalyzer.calculate_frequency_distribution(all_path_segments)
        common_path_segments = sorted(
            [(segment, count) for segment, count in path_segment_distribution.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 common segments
        
        # Common query parameters
        query_param_distribution = StatisticalAnalyzer.calculate_frequency_distribution(all_query_params)
        common_query_params = sorted(
            [(param, count) for param, count in query_param_distribution.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 common query parameters
        
        return {
            "domain_distribution": domain_distribution,
            "path_length_stats": path_length_stats,
            "query_param_stats": query_param_stats,
            "common_path_segments": common_path_segments,
            "common_query_params": common_query_params
        }


class StatisticalContentAnalyzer(ContentAnalyzer):
    """
    Content analyzer that performs statistical analysis on URL content.
    
    This analyzer extracts statistical information from URL content,
    such as word frequencies, content length statistics, and sentiment analysis.
    """
    
    def __init__(self, name: str = "Statistical Content Analyzer"):
        """
        Initialize the statistical content analyzer.
        
        Args:
            name: Name of the analyzer
        """
        self._name = name
    
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> AnalysisResult:
        """
        Analyze URL content using statistical methods.
        
        Args:
            content: URL content to analyze
            options: Analysis options
            
        Returns:
            Analysis result containing statistical information
        """
        if not content.is_success():
            return AnalysisResult(
                url=content.url,
                success=False,
                error="Content fetch was not successful",
                metadata={}
            )
        
        metadata = {}
        
        # Basic content statistics
        content_length = len(content.content) if content.content else 0
        metadata["content_length"] = content_length
        
        if content.is_text() or content.is_html():
            # Word frequency analysis
            import re
            from collections import Counter
            
            # Extract text from HTML if needed
            if content.is_html():
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content.content, 'html.parser')
                    text = soup.get_text()
                except ImportError:
                    # Fall back to simple regex if BeautifulSoup is not available
                    text = re.sub(r'<[^>]+>', ' ', content.content)
            else:
                text = content.content
            
            # Tokenize and count words
            words = re.findall(r'\b\w+\b', text.lower())
            word_count = len(words)
            metadata["word_count"] = word_count
            
            # Word frequency
            word_freq = Counter(words)
            top_words = word_freq.most_common(20)  # Top 20 words
            metadata["top_words"] = top_words
            
            # Sentence statistics
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            metadata["sentence_count"] = sentence_count
            
            if sentence_count > 0:
                sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
                metadata["avg_sentence_length"] = sum(sentence_lengths) / sentence_count
                metadata["sentence_length_stats"] = StatisticalAnalyzer.calculate_descriptive_stats(sentence_lengths)
            
            # Try sentiment analysis if nltk is available
            try:
                from nltk.sentiment import SentimentIntensityAnalyzer
                sia = SentimentIntensityAnalyzer()
                sentiment = sia.polarity_scores(text)
                metadata["sentiment"] = sentiment
            except ImportError:
                # Skip sentiment analysis if nltk is not available
                pass
        
        elif content.is_json():
            # JSON structure analysis
            try:
                json_data = json.loads(content.content)
                
                # Analyze JSON structure
                metadata["json_depth"] = self._calculate_json_depth(json_data)
                metadata["json_breadth"] = self._calculate_json_breadth(json_data)
                metadata["json_leaf_count"] = self._count_json_leaves(json_data)
                
                # Extract and analyze arrays
                arrays = self._extract_arrays(json_data)
                if arrays:
                    array_lengths = [len(arr) for arr in arrays]
                    metadata["array_length_stats"] = StatisticalAnalyzer.calculate_descriptive_stats(array_lengths)
            except json.JSONDecodeError:
                # Skip JSON analysis if content is not valid JSON
                pass
        
        return AnalysisResult(
            url=content.url,
            success=True,
            metadata=metadata
        )
    
    def get_name(self) -> str:
        """
        Get the name of this analyzer.
        
        Returns:
            Analyzer name
        """
        return self._name
    
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types
        """
        return {"text/html", "application/json", "text/plain"}
    
    def _calculate_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """
        Calculate the maximum depth of a JSON object.
        
        Args:
            obj: JSON object
            current_depth: Current depth in the recursion
            
        Returns:
            Maximum depth of the JSON object
        """
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_json_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_json_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _calculate_json_breadth(self, obj: Any) -> int:
        """
        Calculate the maximum breadth of a JSON object.
        
        Args:
            obj: JSON object
            
        Returns:
            Maximum breadth of the JSON object
        """
        if isinstance(obj, dict):
            dict_breadth = len(obj)
            child_breadth = max([self._calculate_json_breadth(v) for v in obj.values()], default=0)
            return max(dict_breadth, child_breadth)
        elif isinstance(obj, list):
            list_breadth = len(obj)
            child_breadth = max([self._calculate_json_breadth(item) for item in obj], default=0)
            return max(list_breadth, child_breadth)
        else:
            return 0
    
    def _count_json_leaves(self, obj: Any) -> int:
        """
        Count the number of leaf nodes in a JSON object.
        
        Args:
            obj: JSON object
            
        Returns:
            Number of leaf nodes
        """
        if isinstance(obj, dict):
            return sum(self._count_json_leaves(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(self._count_json_leaves(item) for item in obj)
        else:
            return 1
    
    def _extract_arrays(self, obj: Any, arrays: Optional[List[List[Any]]] = None) -> List[List[Any]]:
        """
        Extract arrays from a JSON object.
        
        Args:
            obj: JSON object
            arrays: List to store extracted arrays
            
        Returns:
            List of extracted arrays
        """
        if arrays is None:
            arrays = []
        
        if isinstance(obj, dict):
            for v in obj.values():
                self._extract_arrays(v, arrays)
        elif isinstance(obj, list):
            # Only consider non-empty arrays of primitive types
            if obj and all(not isinstance(item, (dict, list)) for item in obj):
                arrays.append(obj)
            
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._extract_arrays(item, arrays)
        
        return arrays