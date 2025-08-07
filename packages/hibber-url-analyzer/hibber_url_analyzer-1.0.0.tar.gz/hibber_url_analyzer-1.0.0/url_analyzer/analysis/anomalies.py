"""
Anomaly Detection Module

This module provides tools for detecting anomalies in URL data.
It includes functions for outlier detection, change point detection,
and anomaly classification.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import json
from collections import Counter
import math

from url_analyzer.analysis.statistical import StatisticalAnalyzer


class AnomalyDetector:
    """
    Provides tools for detecting anomalies in URL data.
    
    This class contains methods for identifying outliers, change points,
    and unusual patterns in URL data.
    """
    
    @staticmethod
    def detect_url_volume_anomalies(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        interval: str = "day",
        method: str = "zscore",
        threshold: float = 3.0
    ) -> Dict[str, Any]:
        """
        Detect anomalies in URL volume over time.
        
        Args:
            url_data: List of URL data dictionaries with timestamps
            time_field: Field name containing the timestamp
            interval: Time interval for aggregation (hour, day, week, month)
            method: Anomaly detection method (zscore, isolation_forest, dbscan)
            threshold: Threshold for anomaly detection (for zscore method)
            
        Returns:
            Dictionary containing anomaly detection results
        """
        if not url_data:
            return {
                "time_periods": [],
                "url_counts": [],
                "anomalies": [],
                "method": method
            }
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(url_data)
        
        # Ensure timestamp is datetime
        if time_field in df.columns:
            if isinstance(df[time_field].iloc[0], str):
                df[time_field] = pd.to_datetime(df[time_field])
        else:
            return {
                "error": f"Time field '{time_field}' not found in data",
                "time_periods": [],
                "url_counts": [],
                "anomalies": [],
                "method": method
            }
        
        # Set time period based on interval
        if interval.lower() == "hour":
            df["period"] = df[time_field].dt.floor("H")
        elif interval.lower() == "day":
            df["period"] = df[time_field].dt.floor("D")
        elif interval.lower() == "week":
            df["period"] = df[time_field].dt.floor("W")
        elif interval.lower() == "month":
            df["period"] = df[time_field].dt.floor("M")
        else:
            return {
                "error": f"Unsupported interval: {interval}",
                "time_periods": [],
                "url_counts": [],
                "anomalies": [],
                "method": method
            }
        
        # Count URLs per period
        url_counts = df.groupby("period").size()
        
        # Convert to time series format
        time_periods = url_counts.index.tolist()
        time_periods_str = [period.strftime("%Y-%m-%d %H:%M:%S") for period in time_periods]
        counts = url_counts.tolist()
        
        # Detect anomalies
        anomaly_result = StatisticalAnalyzer.detect_anomalies(counts, method=method)
        
        # Get anomaly indices and values
        anomaly_indices = anomaly_result.get("anomaly_indices", [])
        anomaly_time_periods = [time_periods_str[i] for i in anomaly_indices]
        anomaly_counts = [counts[i] for i in anomaly_indices]
        
        return {
            "time_periods": time_periods_str,
            "url_counts": counts,
            "anomalies": [
                {"time_period": period, "count": count}
                for period, count in zip(anomaly_time_periods, anomaly_counts)
            ],
            "method": method,
            "anomaly_details": anomaly_result
        }
    
    @staticmethod
    def detect_domain_anomalies(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        interval: str = "day",
        method: str = "zscore",
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Detect anomalies in domain distribution over time.
        
        Args:
            url_data: List of URL data dictionaries with domain and timestamp
            time_field: Field name containing the timestamp
            interval: Time interval for aggregation (hour, day, week, month)
            method: Anomaly detection method (zscore, isolation_forest, dbscan)
            top_n: Number of top domains to analyze
            
        Returns:
            Dictionary containing domain anomaly detection results
        """
        if not url_data:
            return {
                "domains": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(url_data)
        
        # Ensure timestamp is datetime
        if time_field in df.columns:
            if isinstance(df[time_field].iloc[0], str):
                df[time_field] = pd.to_datetime(df[time_field])
        else:
            return {
                "error": f"Time field '{time_field}' not found in data",
                "domains": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Ensure domain field exists
        if "domain" not in df.columns:
            return {
                "error": "Domain field not found in data",
                "domains": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Set time period based on interval
        if interval.lower() == "hour":
            df["period"] = df[time_field].dt.floor("H")
        elif interval.lower() == "day":
            df["period"] = df[time_field].dt.floor("D")
        elif interval.lower() == "week":
            df["period"] = df[time_field].dt.floor("W")
        elif interval.lower() == "month":
            df["period"] = df[time_field].dt.floor("M")
        else:
            return {
                "error": f"Unsupported interval: {interval}",
                "domains": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Count domains per period
        domain_counts = df.groupby(["period", "domain"]).size().unstack(fill_value=0)
        
        # Get top domains by total count
        top_domains = domain_counts.sum().sort_values(ascending=False).head(top_n).index.tolist()
        
        # Filter to top domains
        domain_counts = domain_counts[top_domains]
        
        # Convert to time series format
        time_periods = domain_counts.index.tolist()
        time_periods_str = [period.strftime("%Y-%m-%d %H:%M:%S") for period in time_periods]
        
        # Detect anomalies for each domain
        anomalies = {}
        for domain in top_domains:
            if domain in domain_counts.columns:
                # Get domain counts
                counts = domain_counts[domain].tolist()
                
                # Detect anomalies
                anomaly_result = StatisticalAnalyzer.detect_anomalies(counts, method=method)
                
                # Get anomaly indices and values
                anomaly_indices = anomaly_result.get("anomaly_indices", [])
                anomaly_time_periods = [time_periods_str[i] for i in anomaly_indices]
                anomaly_counts = [counts[i] for i in anomaly_indices]
                
                if anomaly_indices:
                    anomalies[domain] = {
                        "anomalies": [
                            {"time_period": period, "count": count}
                            for period, count in zip(anomaly_time_periods, anomaly_counts)
                        ],
                        "data": counts,
                        "method": method
                    }
        
        return {
            "domains": top_domains,
            "time_periods": time_periods_str,
            "anomalies": anomalies
        }
    
    @staticmethod
    def detect_category_anomalies(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        interval: str = "day",
        method: str = "zscore"
    ) -> Dict[str, Any]:
        """
        Detect anomalies in category distribution over time.
        
        Args:
            url_data: List of URL data dictionaries with category and timestamp
            time_field: Field name containing the timestamp
            interval: Time interval for aggregation (hour, day, week, month)
            method: Anomaly detection method (zscore, isolation_forest, dbscan)
            
        Returns:
            Dictionary containing category anomaly detection results
        """
        if not url_data:
            return {
                "categories": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(url_data)
        
        # Ensure timestamp is datetime
        if time_field in df.columns:
            if isinstance(df[time_field].iloc[0], str):
                df[time_field] = pd.to_datetime(df[time_field])
        else:
            return {
                "error": f"Time field '{time_field}' not found in data",
                "categories": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Ensure category field exists
        if "category" not in df.columns:
            return {
                "error": "Category field not found in data",
                "categories": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Set time period based on interval
        if interval.lower() == "hour":
            df["period"] = df[time_field].dt.floor("H")
        elif interval.lower() == "day":
            df["period"] = df[time_field].dt.floor("D")
        elif interval.lower() == "week":
            df["period"] = df[time_field].dt.floor("W")
        elif interval.lower() == "month":
            df["period"] = df[time_field].dt.floor("M")
        else:
            return {
                "error": f"Unsupported interval: {interval}",
                "categories": [],
                "time_periods": [],
                "anomalies": {}
            }
        
        # Count categories per period
        category_counts = df.groupby(["period", "category"]).size().unstack(fill_value=0)
        
        # Get all categories
        all_categories = category_counts.columns.tolist()
        
        # Convert to time series format
        time_periods = category_counts.index.tolist()
        time_periods_str = [period.strftime("%Y-%m-%d %H:%M:%S") for period in time_periods]
        
        # Detect anomalies for each category
        anomalies = {}
        for category in all_categories:
            if category in category_counts.columns:
                # Get category counts
                counts = category_counts[category].tolist()
                
                # Detect anomalies
                anomaly_result = StatisticalAnalyzer.detect_anomalies(counts, method=method)
                
                # Get anomaly indices and values
                anomaly_indices = anomaly_result.get("anomaly_indices", [])
                anomaly_time_periods = [time_periods_str[i] for i in anomaly_indices]
                anomaly_counts = [counts[i] for i in anomaly_indices]
                
                if anomaly_indices:
                    anomalies[category] = {
                        "anomalies": [
                            {"time_period": period, "count": count}
                            for period, count in zip(anomaly_time_periods, anomaly_counts)
                        ],
                        "data": counts,
                        "method": method
                    }
        
        return {
            "categories": all_categories,
            "time_periods": time_periods_str,
            "anomalies": anomalies
        }
    
    @staticmethod
    def detect_change_points(
        time_series: List[Tuple[datetime, float]],
        method: str = "binary_segmentation",
        max_changes: int = 5
    ) -> Dict[str, Any]:
        """
        Detect change points in time series data.
        
        Args:
            time_series: List of (timestamp, value) tuples
            method: Change point detection method (binary_segmentation, window)
            max_changes: Maximum number of change points to detect
            
        Returns:
            Dictionary containing change point detection results
        """
        if not time_series or len(time_series) < 3:
            return {
                "change_points": [],
                "segments": [],
                "method": method
            }
        
        # Sort by timestamp
        time_series.sort(key=lambda x: x[0])
        
        # Extract timestamps and values
        timestamps = [ts for ts, _ in time_series]
        values = [val for _, val in time_series]
        
        try:
            # Try to use ruptures package for change point detection
            import ruptures as rpt
            
            # Create signal
            signal = np.array(values)
            
            # Detect change points
            if method == "binary_segmentation":
                algo = rpt.Binseg(model="l2").fit(signal)
                change_points = algo.predict(n_bkps=max_changes)
            elif method == "window":
                algo = rpt.Window(width=10, model="l2").fit(signal)
                change_points = algo.predict(n_bkps=max_changes)
            elif method == "bottom_up":
                algo = rpt.BottomUp(model="l2").fit(signal)
                change_points = algo.predict(n_bkps=max_changes)
            else:
                # Default to binary segmentation
                algo = rpt.Binseg(model="l2").fit(signal)
                change_points = algo.predict(n_bkps=max_changes)
            
            # Remove the last change point (end of signal)
            if change_points and change_points[-1] == len(signal):
                change_points = change_points[:-1]
            
            # Convert change points to timestamps
            change_point_timestamps = [timestamps[cp] for cp in change_points if cp < len(timestamps)]
            change_point_timestamps_str = [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in change_point_timestamps]
            
            # Create segments
            segments = []
            start_idx = 0
            
            for cp in change_points:
                if cp < len(signal):
                    segment_values = signal[start_idx:cp].tolist()
                    segment_timestamps = timestamps[start_idx:cp]
                    
                    # Calculate segment statistics
                    segment_stats = StatisticalAnalyzer.calculate_descriptive_stats(segment_values)
                    
                    segments.append({
                        "start": segment_timestamps[0].strftime("%Y-%m-%d %H:%M:%S"),
                        "end": segment_timestamps[-1].strftime("%Y-%m-%d %H:%M:%S"),
                        "length": len(segment_values),
                        "mean": segment_stats["mean"],
                        "std": segment_stats["std"],
                        "min": segment_stats["min"],
                        "max": segment_stats["max"]
                    })
                    
                    start_idx = cp
            
            # Add the last segment
            if start_idx < len(signal):
                segment_values = signal[start_idx:].tolist()
                segment_timestamps = timestamps[start_idx:]
                
                # Calculate segment statistics
                segment_stats = StatisticalAnalyzer.calculate_descriptive_stats(segment_values)
                
                segments.append({
                    "start": segment_timestamps[0].strftime("%Y-%m-%d %H:%M:%S"),
                    "end": segment_timestamps[-1].strftime("%Y-%m-%d %H:%M:%S"),
                    "length": len(segment_values),
                    "mean": segment_stats["mean"],
                    "std": segment_stats["std"],
                    "min": segment_stats["min"],
                    "max": segment_stats["max"]
                })
            
            return {
                "change_points": change_point_timestamps_str,
                "segments": segments,
                "method": method
            }
        
        except ImportError:
            # Fall back to simple change point detection if ruptures is not available
            return AnomalyDetector._simple_change_point_detection(timestamps, values, max_changes)
    
    @staticmethod
    def _simple_change_point_detection(
        timestamps: List[datetime],
        values: List[float],
        max_changes: int = 5
    ) -> Dict[str, Any]:
        """
        Simple change point detection using moving window.
        
        Args:
            timestamps: List of timestamps
            values: List of values
            max_changes: Maximum number of change points to detect
            
        Returns:
            Dictionary containing change point detection results
        """
        if len(values) < 10:
            return {
                "change_points": [],
                "segments": [],
                "method": "simple_window"
            }
        
        # Calculate moving average and standard deviation
        window_size = max(3, len(values) // 10)
        moving_avg = []
        moving_std = []
        
        for i in range(len(values) - window_size + 1):
            window = values[i:i+window_size]
            moving_avg.append(sum(window) / window_size)
            moving_std.append(np.std(window))
        
        # Calculate z-scores for changes in moving average
        z_scores = []
        for i in range(1, len(moving_avg)):
            if moving_std[i-1] > 0:
                z_scores.append(abs(moving_avg[i] - moving_avg[i-1]) / moving_std[i-1])
            else:
                z_scores.append(0)
        
        # Find potential change points
        threshold = 3.0  # Z-score threshold for change points
        potential_changes = [i+1 for i, z in enumerate(z_scores) if z > threshold]
        
        # Merge close change points
        min_distance = max(2, len(values) // 20)
        change_points = []
        
        for pc in potential_changes:
            if not change_points or pc - change_points[-1] >= min_distance:
                change_points.append(pc)
        
        # Limit to max_changes
        if len(change_points) > max_changes:
            # Sort by z-score and take the top max_changes
            change_points_with_scores = [(cp, z_scores[cp-1]) for cp in change_points if cp-1 < len(z_scores)]
            change_points_with_scores.sort(key=lambda x: x[1], reverse=True)
            change_points = [cp for cp, _ in change_points_with_scores[:max_changes]]
            change_points.sort()
        
        # Convert change points to timestamps
        change_point_timestamps = [timestamps[window_size + cp - 1] for cp in change_points if window_size + cp - 1 < len(timestamps)]
        change_point_timestamps_str = [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in change_point_timestamps]
        
        # Create segments
        segments = []
        start_idx = 0
        
        for cp in change_points:
            cp_idx = window_size + cp - 1
            if cp_idx < len(values):
                segment_values = values[start_idx:cp_idx]
                segment_timestamps = timestamps[start_idx:cp_idx]
                
                # Calculate segment statistics
                segment_stats = StatisticalAnalyzer.calculate_descriptive_stats(segment_values)
                
                segments.append({
                    "start": segment_timestamps[0].strftime("%Y-%m-%d %H:%M:%S"),
                    "end": segment_timestamps[-1].strftime("%Y-%m-%d %H:%M:%S"),
                    "length": len(segment_values),
                    "mean": segment_stats["mean"],
                    "std": segment_stats["std"],
                    "min": segment_stats["min"],
                    "max": segment_stats["max"]
                })
                
                start_idx = cp_idx
        
        # Add the last segment
        if start_idx < len(values):
            segment_values = values[start_idx:]
            segment_timestamps = timestamps[start_idx:]
            
            # Calculate segment statistics
            segment_stats = StatisticalAnalyzer.calculate_descriptive_stats(segment_values)
            
            segments.append({
                "start": segment_timestamps[0].strftime("%Y-%m-%d %H:%M:%S"),
                "end": segment_timestamps[-1].strftime("%Y-%m-%d %H:%M:%S"),
                "length": len(segment_values),
                "mean": segment_stats["mean"],
                "std": segment_stats["std"],
                "min": segment_stats["min"],
                "max": segment_stats["max"]
            })
        
        return {
            "change_points": change_point_timestamps_str,
            "segments": segments,
            "method": "simple_window"
        }
    
    @staticmethod
    def detect_unusual_urls(
        url_data: List[Dict[str, Any]],
        features: Optional[List[str]] = None,
        method: str = "isolation_forest",
        contamination: float = 0.05
    ) -> Dict[str, Any]:
        """
        Detect unusual URLs based on their features.
        
        Args:
            url_data: List of URL data dictionaries
            features: List of features to use for anomaly detection
            method: Anomaly detection method (isolation_forest, dbscan, lof)
            contamination: Expected proportion of anomalies
            
        Returns:
            Dictionary containing unusual URL detection results
        """
        if not url_data:
            return {
                "unusual_urls": [],
                "method": method
            }
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(url_data)
        
        # Default features if not specified
        if features is None:
            # Use available numeric features
            numeric_features = df.select_dtypes(include=np.number).columns.tolist()
            
            # Add derived features
            if "url" in df.columns:
                df["url_length"] = df["url"].str.len()
                numeric_features.append("url_length")
            
            if "domain" in df.columns:
                df["domain_length"] = df["domain"].str.len()
                numeric_features.append("domain_length")
            
            features = numeric_features
        
        # Ensure we have features to work with
        if not features or not all(f in df.columns for f in features):
            return {
                "error": "Invalid features specified",
                "unusual_urls": [],
                "method": method
            }
        
        # Extract feature values
        X = df[features].values
        
        # Handle missing values
        X = np.nan_to_num(X)
        
        try:
            if method == "isolation_forest":
                from sklearn.ensemble import IsolationForest
                
                # Train isolation forest model
                model = IsolationForest(contamination=contamination, random_state=42)
                predictions = model.fit_predict(X)
                
                # -1 indicates anomaly, 1 indicates normal
                anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
                
            elif method == "dbscan":
                from sklearn.cluster import DBSCAN
                from sklearn.preprocessing import StandardScaler
                
                # Standardize features
                X_scaled = StandardScaler().fit_transform(X)
                
                # Estimate epsilon based on data
                from sklearn.neighbors import NearestNeighbors
                nn = NearestNeighbors(n_neighbors=min(len(X_scaled), 5))
                nn.fit(X_scaled)
                distances, _ = nn.kneighbors(X_scaled)
                distances = np.sort(distances[:, 1:], axis=0)
                eps = np.mean(distances[:, 0]) * 2
                
                # Apply DBSCAN
                dbscan = DBSCAN(eps=eps, min_samples=max(3, int(len(X_scaled) * 0.05)))
                clusters = dbscan.fit_predict(X_scaled)
                
                # -1 indicates noise points (anomalies)
                anomaly_indices = [i for i, cluster in enumerate(clusters) if cluster == -1]
                
            elif method == "lof":
                from sklearn.neighbors import LocalOutlierFactor
                
                # Train LOF model
                model = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
                predictions = model.fit_predict(X)
                
                # -1 indicates anomaly, 1 indicates normal
                anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
                
            else:
                # Default to isolation forest
                from sklearn.ensemble import IsolationForest
                
                # Train isolation forest model
                model = IsolationForest(contamination=contamination, random_state=42)
                predictions = model.fit_predict(X)
                
                # -1 indicates anomaly, 1 indicates normal
                anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
            
            # Extract unusual URLs
            unusual_urls = df.iloc[anomaly_indices].to_dict(orient="records")
            
            return {
                "unusual_urls": unusual_urls,
                "unusual_count": len(unusual_urls),
                "total_count": len(df),
                "unusual_percentage": len(unusual_urls) / len(df) * 100 if len(df) > 0 else 0,
                "method": method,
                "features_used": features
            }
            
        except ImportError:
            # Fall back to simple anomaly detection if scikit-learn is not available
            return {
                "error": "scikit-learn package not available",
                "unusual_urls": [],
                "method": method
            }
        except Exception as e:
            return {
                "error": str(e),
                "unusual_urls": [],
                "method": method
            }