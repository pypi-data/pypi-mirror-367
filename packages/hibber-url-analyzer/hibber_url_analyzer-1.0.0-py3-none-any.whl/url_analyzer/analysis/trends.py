"""
Trend Analysis Module

This module provides tools for analyzing trends in URL data over time.
It includes functions for time series analysis, trend detection, and
forecasting.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import json
from collections import Counter
import math

from url_analyzer.analysis.statistical import StatisticalAnalyzer


class TrendAnalyzer:
    """
    Provides tools for analyzing trends in URL data over time.
    
    This class contains methods for time series analysis, trend detection,
    and forecasting of URL data patterns.
    """
    
    @staticmethod
    def analyze_domain_trends(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        interval: str = "day"
    ) -> Dict[str, Any]:
        """
        Analyze trends in domain popularity over time.
        
        Args:
            url_data: List of URL data dictionaries with domain and timestamp
            time_field: Field name containing the timestamp
            interval: Time interval for aggregation (hour, day, week, month)
            
        Returns:
            Dictionary containing domain trend analysis
        """
        if not url_data:
            return {
                "domains": [],
                "time_periods": [],
                "trends": {}
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
                "trends": {}
            }
        
        # Ensure domain field exists
        if "domain" not in df.columns:
            return {
                "error": "Domain field not found in data",
                "domains": [],
                "time_periods": [],
                "trends": {}
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
                "trends": {}
            }
        
        # Count domains per period
        domain_counts = df.groupby(["period", "domain"]).size().unstack(fill_value=0)
        
        # Get top domains by total count
        top_domains = domain_counts.sum().sort_values(ascending=False).head(10).index.tolist()
        
        # Filter to top domains
        domain_counts = domain_counts[top_domains]
        
        # Convert to time series format
        time_periods = domain_counts.index.tolist()
        time_periods_str = [period.strftime("%Y-%m-%d %H:%M:%S") for period in time_periods]
        
        # Analyze trends for each domain
        trends = {}
        for domain in top_domains:
            if domain in domain_counts.columns:
                # Get time series data
                time_series = [(period, count) for period, count in zip(time_periods, domain_counts[domain].tolist())]
                
                # Detect trend
                trend_info = StatisticalAnalyzer.detect_trends(time_series)
                
                # Store trend information
                trends[domain] = {
                    "trend": trend_info["trend"],
                    "slope": trend_info["slope"],
                    "p_value": trend_info["p_value"],
                    "data": domain_counts[domain].tolist()
                }
        
        return {
            "domains": top_domains,
            "time_periods": time_periods_str,
            "trends": trends
        }
    
    @staticmethod
    def analyze_category_trends(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        interval: str = "day"
    ) -> Dict[str, Any]:
        """
        Analyze trends in URL category distribution over time.
        
        Args:
            url_data: List of URL data dictionaries with category and timestamp
            time_field: Field name containing the timestamp
            interval: Time interval for aggregation (hour, day, week, month)
            
        Returns:
            Dictionary containing category trend analysis
        """
        if not url_data:
            return {
                "categories": [],
                "time_periods": [],
                "trends": {}
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
                "trends": {}
            }
        
        # Ensure category field exists
        if "category" not in df.columns:
            return {
                "error": "Category field not found in data",
                "categories": [],
                "time_periods": [],
                "trends": {}
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
                "trends": {}
            }
        
        # Count categories per period
        category_counts = df.groupby(["period", "category"]).size().unstack(fill_value=0)
        
        # Get all categories
        all_categories = category_counts.columns.tolist()
        
        # Convert to time series format
        time_periods = category_counts.index.tolist()
        time_periods_str = [period.strftime("%Y-%m-%d %H:%M:%S") for period in time_periods]
        
        # Analyze trends for each category
        trends = {}
        for category in all_categories:
            if category in category_counts.columns:
                # Get time series data
                time_series = [(period, count) for period, count in zip(time_periods, category_counts[category].tolist())]
                
                # Detect trend
                trend_info = StatisticalAnalyzer.detect_trends(time_series)
                
                # Store trend information
                trends[category] = {
                    "trend": trend_info["trend"],
                    "slope": trend_info["slope"],
                    "p_value": trend_info["p_value"],
                    "data": category_counts[category].tolist()
                }
        
        return {
            "categories": all_categories,
            "time_periods": time_periods_str,
            "trends": trends
        }
    
    @staticmethod
    def analyze_sensitivity_trends(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        interval: str = "day"
    ) -> Dict[str, Any]:
        """
        Analyze trends in URL sensitivity over time.
        
        Args:
            url_data: List of URL data dictionaries with is_sensitive and timestamp
            time_field: Field name containing the timestamp
            interval: Time interval for aggregation (hour, day, week, month)
            
        Returns:
            Dictionary containing sensitivity trend analysis
        """
        if not url_data:
            return {
                "time_periods": [],
                "sensitive_counts": [],
                "non_sensitive_counts": [],
                "sensitive_ratio": [],
                "trend": None
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
                "sensitive_counts": [],
                "non_sensitive_counts": [],
                "sensitive_ratio": [],
                "trend": None
            }
        
        # Ensure is_sensitive field exists
        if "is_sensitive" not in df.columns:
            return {
                "error": "is_sensitive field not found in data",
                "time_periods": [],
                "sensitive_counts": [],
                "non_sensitive_counts": [],
                "sensitive_ratio": [],
                "trend": None
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
                "sensitive_counts": [],
                "non_sensitive_counts": [],
                "sensitive_ratio": [],
                "trend": None
            }
        
        # Count sensitive and non-sensitive URLs per period
        sensitivity_counts = df.groupby(["period", "is_sensitive"]).size().unstack(fill_value=0)
        
        # Ensure both sensitive and non-sensitive columns exist
        if True not in sensitivity_counts.columns:
            sensitivity_counts[True] = 0
        if False not in sensitivity_counts.columns:
            sensitivity_counts[False] = 0
        
        # Calculate sensitive ratio
        total_counts = sensitivity_counts[True] + sensitivity_counts[False]
        sensitive_ratio = sensitivity_counts[True] / total_counts
        sensitive_ratio = sensitive_ratio.fillna(0)
        
        # Convert to time series format
        time_periods = sensitivity_counts.index.tolist()
        time_periods_str = [period.strftime("%Y-%m-%d %H:%M:%S") for period in time_periods]
        
        # Analyze trend in sensitive ratio
        time_series = [(period, ratio) for period, ratio in zip(time_periods, sensitive_ratio.tolist())]
        trend_info = StatisticalAnalyzer.detect_trends(time_series)
        
        return {
            "time_periods": time_periods_str,
            "sensitive_counts": sensitivity_counts[True].tolist(),
            "non_sensitive_counts": sensitivity_counts[False].tolist(),
            "sensitive_ratio": sensitive_ratio.tolist(),
            "trend": {
                "direction": trend_info["trend"],
                "slope": trend_info["slope"],
                "p_value": trend_info["p_value"]
            }
        }
    
    @staticmethod
    def forecast_trends(
        time_series: List[Tuple[datetime, float]],
        periods: int = 5,
        method: str = "linear"
    ) -> Dict[str, Any]:
        """
        Forecast future values based on historical trends.
        
        Args:
            time_series: List of (timestamp, value) tuples
            periods: Number of periods to forecast
            method: Forecasting method (linear, exponential, arima)
            
        Returns:
            Dictionary containing forecast results
        """
        if not time_series or len(time_series) < 2:
            return {
                "forecast": [],
                "confidence_intervals": [],
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
            from scipy import stats
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(days, values)
            
            # Generate forecast
            forecast_days = [days[-1] + (i + 1) for i in range(periods)]
            forecast_values = [slope * day + intercept for day in forecast_days]
            
            # Generate forecast timestamps
            forecast_timestamps = [
                first_timestamp + timedelta(days=day)
                for day in forecast_days
            ]
            
            # Calculate confidence intervals (95%)
            import math
            n = len(days)
            mean_x = sum(days) / n
            s_xx = sum((x - mean_x) ** 2 for x in days)
            
            confidence_intervals = []
            for day in forecast_days:
                # Standard error of prediction
                se = std_err * math.sqrt(1 + 1/n + ((day - mean_x) ** 2) / s_xx)
                # 95% confidence interval
                margin = 1.96 * se
                confidence_intervals.append((
                    max(0, slope * day + intercept - margin),
                    slope * day + intercept + margin
                ))
            
            return {
                "forecast": [
                    (ts.strftime("%Y-%m-%d %H:%M:%S"), val)
                    for ts, val in zip(forecast_timestamps, forecast_values)
                ],
                "confidence_intervals": [
                    {"lower": lower, "upper": upper}
                    for lower, upper in confidence_intervals
                ],
                "method": method,
                "r_squared": r_value ** 2,
                "p_value": p_value
            }
        
        elif method.lower() == "exponential":
            # Exponential smoothing
            try:
                from statsmodels.tsa.holtwinters import ExponentialSmoothing
                
                # Convert to pandas Series
                ts = pd.Series(values, index=pd.DatetimeIndex(timestamps))
                
                # Fit model
                model = ExponentialSmoothing(
                    ts, 
                    trend='add', 
                    seasonal=None, 
                    damped=True
                ).fit()
                
                # Generate forecast
                forecast = model.forecast(periods)
                
                # Generate forecast timestamps
                last_timestamp = timestamps[-1]
                avg_interval = (timestamps[-1] - timestamps[-2]).total_seconds()
                forecast_timestamps = [
                    last_timestamp + timedelta(seconds=avg_interval * (i + 1))
                    for i in range(periods)
                ]
                
                # Get prediction intervals
                pred_intervals = model.get_prediction(
                    start=len(ts), 
                    end=len(ts) + periods - 1
                ).conf_int(alpha=0.05)
                
                return {
                    "forecast": [
                        (ts.strftime("%Y-%m-%d %H:%M:%S"), float(val))
                        for ts, val in zip(forecast_timestamps, forecast)
                    ],
                    "confidence_intervals": [
                        {"lower": float(lower), "upper": float(upper)}
                        for lower, upper in zip(pred_intervals.iloc[:, 0], pred_intervals.iloc[:, 1])
                    ],
                    "method": method
                }
            except ImportError:
                # Fall back to linear regression if statsmodels is not available
                return TrendAnalyzer.forecast_trends(time_series, periods, "linear")
        
        elif method.lower() == "arima":
            # ARIMA model
            try:
                from statsmodels.tsa.arima.model import ARIMA
                
                # Convert to pandas Series
                ts = pd.Series(values, index=pd.DatetimeIndex(timestamps))
                
                # Fit model
                model = ARIMA(ts, order=(1, 1, 1)).fit()
                
                # Generate forecast
                forecast = model.forecast(periods)
                
                # Generate forecast timestamps
                last_timestamp = timestamps[-1]
                avg_interval = (timestamps[-1] - timestamps[-2]).total_seconds()
                forecast_timestamps = [
                    last_timestamp + timedelta(seconds=avg_interval * (i + 1))
                    for i in range(periods)
                ]
                
                # Get prediction intervals
                pred_intervals = model.get_forecast(periods).conf_int(alpha=0.05)
                
                return {
                    "forecast": [
                        (ts.strftime("%Y-%m-%d %H:%M:%S"), float(val))
                        for ts, val in zip(forecast_timestamps, forecast)
                    ],
                    "confidence_intervals": [
                        {"lower": float(lower), "upper": float(upper)}
                        for lower, upper in zip(pred_intervals.iloc[:, 0], pred_intervals.iloc[:, 1])
                    ],
                    "method": method
                }
            except ImportError:
                # Fall back to linear regression if statsmodels is not available
                return TrendAnalyzer.forecast_trends(time_series, periods, "linear")
        
        else:
            raise ValueError(f"Unsupported forecasting method: {method}")
    
    @staticmethod
    def detect_seasonal_patterns(
        time_series: List[Tuple[datetime, float]],
        freq: str = "D"
    ) -> Dict[str, Any]:
        """
        Detect seasonal patterns in time series data.
        
        Args:
            time_series: List of (timestamp, value) tuples
            freq: Frequency for seasonal decomposition (D=daily, W=weekly, M=monthly)
            
        Returns:
            Dictionary containing seasonal pattern information
        """
        if not time_series or len(time_series) < 2:
            return {
                "has_seasonality": False,
                "seasonal_periods": [],
                "seasonal_strengths": []
            }
        
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # Sort by timestamp
            time_series.sort(key=lambda x: x[0])
            
            # Extract timestamps and values
            timestamps = [ts for ts, _ in time_series]
            values = [val for _, val in time_series]
            
            # Convert to pandas Series
            ts = pd.Series(values, index=pd.DatetimeIndex(timestamps))
            
            # Ensure the series has a regular frequency
            ts = ts.asfreq(freq)
            
            # Fill missing values
            ts = ts.interpolate()
            
            # Determine period based on frequency
            if freq == "D":
                period = 7  # Weekly seasonality
            elif freq == "W":
                period = 52  # Yearly seasonality for weekly data
            elif freq == "M":
                period = 12  # Yearly seasonality for monthly data
            elif freq == "H":
                period = 24  # Daily seasonality for hourly data
            else:
                period = 7  # Default to weekly
            
            # Ensure we have enough data for decomposition
            if len(ts) < period * 2:
                return {
                    "has_seasonality": False,
                    "error": "Not enough data for seasonal decomposition",
                    "seasonal_periods": [],
                    "seasonal_strengths": []
                }
            
            # Perform seasonal decomposition
            result = seasonal_decompose(ts, model='additive', period=period)
            
            # Calculate seasonal strength
            seasonal_var = np.var(result.seasonal)
            residual_var = np.var(result.resid.dropna())
            total_var = seasonal_var + residual_var
            
            seasonal_strength = seasonal_var / total_var if total_var > 0 else 0
            
            # Determine if seasonality is significant
            has_seasonality = seasonal_strength > 0.3  # Common threshold
            
            # Get seasonal periods
            seasonal_component = result.seasonal.dropna()
            seasonal_periods = []
            
            if has_seasonality:
                # Find peaks in seasonal component
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(seasonal_component.values)
                
                if len(peaks) > 1:
                    # Calculate average distance between peaks
                    peak_distances = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
                    avg_period = sum(peak_distances) / len(peak_distances)
                    
                    # Convert to appropriate time unit
                    if freq == "D":
                        period_unit = "days"
                    elif freq == "W":
                        period_unit = "weeks"
                    elif freq == "M":
                        period_unit = "months"
                    elif freq == "H":
                        period_unit = "hours"
                    else:
                        period_unit = "periods"
                    
                    seasonal_periods.append({
                        "period": float(avg_period),
                        "unit": period_unit,
                        "strength": float(seasonal_strength)
                    })
            
            return {
                "has_seasonality": has_seasonality,
                "seasonal_strength": float(seasonal_strength),
                "seasonal_periods": seasonal_periods,
                "decomposition": {
                    "trend": result.trend.dropna().tolist(),
                    "seasonal": result.seasonal.dropna().tolist(),
                    "residual": result.resid.dropna().tolist()
                }
            }
        
        except ImportError:
            # Return basic result if statsmodels is not available
            return {
                "has_seasonality": False,
                "error": "statsmodels package not available",
                "seasonal_periods": [],
                "seasonal_strengths": []
            }
        except Exception as e:
            return {
                "has_seasonality": False,
                "error": str(e),
                "seasonal_periods": [],
                "seasonal_strengths": []
            }