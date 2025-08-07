"""
Predictive Analytics Module for URL Analysis.

This module provides predictive analytics capabilities for URL data,
including time series forecasting, trend prediction, and anomaly prediction.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import json
from collections import Counter
import math
import logging
import os

# Optional imports with fallbacks
try:
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split, TimeSeriesSplit
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import statsmodels.api as sm
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

logger = logging.getLogger(__name__)

class PredictiveAnalyzer:
    """
    Predictive Analytics for URL data.
    
    This class provides predictive analytics capabilities for URL data,
    including time series forecasting, trend prediction, and anomaly prediction.
    """
    
    @staticmethod
    def forecast_time_series(
        time_series: List[Tuple[datetime, float]],
        forecast_periods: int = 7,
        method: str = "auto",
        frequency: str = "D"
    ) -> Dict[str, Any]:
        """
        Forecast future values of a time series.
        
        Args:
            time_series: List of (datetime, value) tuples
            forecast_periods: Number of periods to forecast
            method: Forecasting method ('auto', 'arima', 'prophet', 'exponential_smoothing', 'linear')
            frequency: Time series frequency ('D' for daily, 'W' for weekly, etc.)
            
        Returns:
            Dictionary containing forecast results
        """
        if len(time_series) < 10:
            return {"error": "Need at least 10 data points for forecasting"}
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(time_series, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])
        
        # Sort by date
        df = df.sort_values("ds")
        
        # Check for missing values
        if df["y"].isna().any():
            df["y"] = df["y"].interpolate()
        
        # Determine best method if auto
        if method == "auto":
            if PROPHET_AVAILABLE:
                method = "prophet"
            elif STATSMODELS_AVAILABLE:
                method = "arima"
            elif SKLEARN_AVAILABLE:
                method = "linear"
            else:
                method = "naive"
        
        result = {
            "method": method,
            "input_data_points": len(df),
            "forecast_periods": forecast_periods,
            "frequency": frequency
        }
        
        try:
            if method == "prophet" and PROPHET_AVAILABLE:
                # Use Prophet for forecasting
                model = Prophet(
                    daily_seasonality=frequency == "D",
                    weekly_seasonality=frequency in ["D", "W"],
                    yearly_seasonality=len(df) > 365
                )
                model.fit(df)
                
                # Create future dataframe
                future = model.make_future_dataframe(periods=forecast_periods, freq=frequency)
                forecast = model.predict(future)
                
                # Extract results
                forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(forecast_periods)
                
                result["forecast"] = [
                    {
                        "date": row["ds"].strftime("%Y-%m-%d"),
                        "value": row["yhat"],
                        "lower_bound": row["yhat_lower"],
                        "upper_bound": row["yhat_upper"]
                    }
                    for _, row in forecast_df.iterrows()
                ]
                
                # Add components if available
                if "trend" in forecast.columns:
                    result["components"] = {
                        "trend": forecast["trend"].tail(len(df)).tolist(),
                        "weekly": forecast["weekly"].tail(len(df)).tolist() if "weekly" in forecast.columns else None,
                        "yearly": forecast["yearly"].tail(len(df)).tolist() if "yearly" in forecast.columns else None
                    }
                
            elif method == "arima" and STATSMODELS_AVAILABLE:
                # Use ARIMA for forecasting
                y = df["y"].values
                
                # Fit ARIMA model
                model = ARIMA(y, order=(5, 1, 0))
                model_fit = model.fit()
                
                # Forecast
                forecast = model_fit.forecast(steps=forecast_periods)
                
                # Create date range for forecast
                last_date = df["ds"].iloc[-1]
                if frequency == "D":
                    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_periods)]
                elif frequency == "W":
                    forecast_dates = [last_date + timedelta(weeks=i+1) for i in range(forecast_periods)]
                elif frequency == "M":
                    forecast_dates = [last_date + pd.DateOffset(months=i+1) for i in range(forecast_periods)]
                else:
                    forecast_dates = [last_date + pd.DateOffset(days=(i+1)) for i in range(forecast_periods)]
                
                # Extract results
                result["forecast"] = [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "value": float(value)
                    }
                    for date, value in zip(forecast_dates, forecast)
                ]
                
                # Add model summary
                result["model_info"] = {
                    "aic": model_fit.aic,
                    "bic": model_fit.bic
                }
                
            elif method == "exponential_smoothing" and STATSMODELS_AVAILABLE:
                # Use Exponential Smoothing for forecasting
                y = df["y"].values
                
                # Fit Exponential Smoothing model
                model = ExponentialSmoothing(
                    y,
                    trend="add",
                    seasonal="add" if len(df) > 12 else None,
                    seasonal_periods=7 if frequency == "D" else 12
                )
                model_fit = model.fit()
                
                # Forecast
                forecast = model_fit.forecast(forecast_periods)
                
                # Create date range for forecast
                last_date = df["ds"].iloc[-1]
                if frequency == "D":
                    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_periods)]
                elif frequency == "W":
                    forecast_dates = [last_date + timedelta(weeks=i+1) for i in range(forecast_periods)]
                elif frequency == "M":
                    forecast_dates = [last_date + pd.DateOffset(months=i+1) for i in range(forecast_periods)]
                else:
                    forecast_dates = [last_date + pd.DateOffset(days=(i+1)) for i in range(forecast_periods)]
                
                # Extract results
                result["forecast"] = [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "value": float(value)
                    }
                    for date, value in zip(forecast_dates, forecast)
                ]
                
            elif method == "linear" and SKLEARN_AVAILABLE:
                # Use Linear Regression for forecasting
                df["days_since_start"] = (df["ds"] - df["ds"].min()).dt.days
                
                # Create features
                X = df[["days_since_start"]].values
                y = df["y"].values
                
                # Add polynomial features
                poly = PolynomialFeatures(degree=2)
                X_poly = poly.fit_transform(X)
                
                # Fit model
                model = LinearRegression()
                model.fit(X_poly, y)
                
                # Create forecast dates
                last_date = df["ds"].iloc[-1]
                last_days = df["days_since_start"].iloc[-1]
                
                if frequency == "D":
                    forecast_days = [last_days + i + 1 for i in range(forecast_periods)]
                    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_periods)]
                elif frequency == "W":
                    forecast_days = [last_days + (i + 1) * 7 for i in range(forecast_periods)]
                    forecast_dates = [last_date + timedelta(weeks=i+1) for i in range(forecast_periods)]
                else:
                    forecast_days = [last_days + i + 1 for i in range(forecast_periods)]
                    forecast_dates = [last_date + pd.DateOffset(days=i+1) for i in range(forecast_periods)]
                
                # Predict
                X_forecast = np.array(forecast_days).reshape(-1, 1)
                X_forecast_poly = poly.transform(X_forecast)
                forecast = model.predict(X_forecast_poly)
                
                # Extract results
                result["forecast"] = [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "value": float(value)
                    }
                    for date, value in zip(forecast_dates, forecast)
                ]
                
                # Add model info
                result["model_info"] = {
                    "coefficients": model.coef_.tolist(),
                    "intercept": float(model.intercept_)
                }
                
            else:
                # Fallback to naive forecasting (last value)
                last_value = df["y"].iloc[-1]
                
                # Create date range for forecast
                last_date = df["ds"].iloc[-1]
                if frequency == "D":
                    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_periods)]
                elif frequency == "W":
                    forecast_dates = [last_date + timedelta(weeks=i+1) for i in range(forecast_periods)]
                elif frequency == "M":
                    forecast_dates = [last_date + pd.DateOffset(months=i+1) for i in range(forecast_periods)]
                else:
                    forecast_dates = [last_date + pd.DateOffset(days=(i+1)) for i in range(forecast_periods)]
                
                # Extract results
                result["forecast"] = [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "value": float(last_value)
                    }
                    for date in forecast_dates
                ]
                
                result["method"] = "naive"
            
            # Add evaluation metrics using last 20% of data
            if len(df) >= 10 and (SKLEARN_AVAILABLE or STATSMODELS_AVAILABLE):
                train_size = int(len(df) * 0.8)
                train_df = df.iloc[:train_size]
                test_df = df.iloc[train_size:]
                
                # Refit model on training data
                if method == "prophet" and PROPHET_AVAILABLE:
                    eval_model = Prophet(
                        daily_seasonality=frequency == "D",
                        weekly_seasonality=frequency in ["D", "W"],
                        yearly_seasonality=len(train_df) > 365
                    )
                    eval_model.fit(train_df)
                    
                    # Predict on test data
                    future = eval_model.make_future_dataframe(periods=len(test_df), freq=frequency)
                    forecast = eval_model.predict(future)
                    predictions = forecast["yhat"].tail(len(test_df)).values
                    
                elif method == "arima" and STATSMODELS_AVAILABLE:
                    eval_model = ARIMA(train_df["y"].values, order=(5, 1, 0))
                    eval_model_fit = eval_model.fit()
                    predictions = eval_model_fit.forecast(steps=len(test_df))
                    
                elif method == "exponential_smoothing" and STATSMODELS_AVAILABLE:
                    eval_model = ExponentialSmoothing(
                        train_df["y"].values,
                        trend="add",
                        seasonal="add" if len(train_df) > 12 else None,
                        seasonal_periods=7 if frequency == "D" else 12
                    )
                    eval_model_fit = eval_model.fit()
                    predictions = eval_model_fit.forecast(len(test_df))
                    
                elif method == "linear" and SKLEARN_AVAILABLE:
                    train_df["days_since_start"] = (train_df["ds"] - train_df["ds"].min()).dt.days
                    test_df["days_since_start"] = (test_df["ds"] - train_df["ds"].min()).dt.days
                    
                    # Create features
                    X_train = train_df[["days_since_start"]].values
                    y_train = train_df["y"].values
                    X_test = test_df[["days_since_start"]].values
                    
                    # Add polynomial features
                    eval_poly = PolynomialFeatures(degree=2)
                    X_train_poly = eval_poly.fit_transform(X_train)
                    X_test_poly = eval_poly.transform(X_test)
                    
                    # Fit model
                    eval_model = LinearRegression()
                    eval_model.fit(X_train_poly, y_train)
                    predictions = eval_model.predict(X_test_poly)
                    
                else:
                    # Naive forecast
                    predictions = np.full(len(test_df), train_df["y"].iloc[-1])
                
                # Calculate metrics
                if SKLEARN_AVAILABLE:
                    result["evaluation"] = {
                        "mse": mean_squared_error(test_df["y"].values, predictions),
                        "rmse": math.sqrt(mean_squared_error(test_df["y"].values, predictions)),
                        "mae": mean_absolute_error(test_df["y"].values, predictions),
                        "r2": r2_score(test_df["y"].values, predictions) if len(test_df) > 1 else None
                    }
                else:
                    # Calculate metrics manually
                    errors = test_df["y"].values - predictions
                    result["evaluation"] = {
                        "mse": float(np.mean(errors ** 2)),
                        "rmse": float(np.sqrt(np.mean(errors ** 2))),
                        "mae": float(np.mean(np.abs(errors)))
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in time series forecasting: {str(e)}")
            return {
                "error": str(e),
                "method": method
            }
    
    @staticmethod
    def predict_url_growth(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        value_field: str = "count",
        group_by: Optional[str] = None,
        forecast_periods: int = 7,
        frequency: str = "D"
    ) -> Dict[str, Any]:
        """
        Predict future growth of URL metrics.
        
        Args:
            url_data: List of URL data dictionaries
            time_field: Field containing timestamp
            value_field: Field containing value to predict
            group_by: Field to group by (e.g., "domain", "category")
            forecast_periods: Number of periods to forecast
            frequency: Time series frequency ('D' for daily, 'W' for weekly, etc.)
            
        Returns:
            Dictionary containing growth predictions
        """
        if not url_data:
            return {"error": "No data provided"}
        
        # Convert to DataFrame
        df = pd.DataFrame(url_data)
        
        # Ensure timestamp is datetime
        df[time_field] = pd.to_datetime(df[time_field])
        
        # Group by time and optional group field
        if group_by:
            if group_by not in df.columns:
                return {"error": f"Group by field '{group_by}' not found in data"}
            
            # Get top groups by count
            top_groups = df[group_by].value_counts().head(5).index.tolist()
            
            results = {}
            
            for group in top_groups:
                group_df = df[df[group_by] == group]
                
                # Group by time and aggregate
                time_series_df = group_df.groupby(pd.Grouper(key=time_field, freq=frequency))[value_field].sum().reset_index()
                
                # Convert to list of tuples
                time_series = [(row[time_field], row[value_field]) for _, row in time_series_df.iterrows()]
                
                # Forecast
                forecast_result = PredictiveAnalyzer.forecast_time_series(
                    time_series,
                    forecast_periods=forecast_periods,
                    method="auto",
                    frequency=frequency
                )
                
                results[group] = forecast_result
            
            return {
                "group_by": group_by,
                "forecasts": results
            }
        else:
            # Group by time only
            time_series_df = df.groupby(pd.Grouper(key=time_field, freq=frequency))[value_field].sum().reset_index()
            
            # Convert to list of tuples
            time_series = [(row[time_field], row[value_field]) for _, row in time_series_df.iterrows()]
            
            # Forecast
            forecast_result = PredictiveAnalyzer.forecast_time_series(
                time_series,
                forecast_periods=forecast_periods,
                method="auto",
                frequency=frequency
            )
            
            return forecast_result
    
    @staticmethod
    def predict_category_shifts(
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        category_field: str = "category",
        forecast_periods: int = 7,
        frequency: str = "D"
    ) -> Dict[str, Any]:
        """
        Predict shifts in URL category distribution over time.
        
        Args:
            url_data: List of URL data dictionaries
            time_field: Field containing timestamp
            category_field: Field containing category
            forecast_periods: Number of periods to forecast
            frequency: Time series frequency ('D' for daily, 'W' for weekly, etc.)
            
        Returns:
            Dictionary containing category shift predictions
        """
        if not url_data:
            return {"error": "No data provided"}
        
        # Convert to DataFrame
        df = pd.DataFrame(url_data)
        
        # Ensure timestamp is datetime
        df[time_field] = pd.to_datetime(df[time_field])
        
        if category_field not in df.columns:
            return {"error": f"Category field '{category_field}' not found in data"}
        
        # Get top categories
        top_categories = df[category_field].value_counts().head(5).index.tolist()
        
        # Create time series for each category
        category_series = {}
        category_forecasts = {}
        
        for category in top_categories:
            # Filter by category
            category_df = df[df[category_field] == category]
            
            # Count by time period
            time_series_df = category_df.groupby(pd.Grouper(key=time_field, freq=frequency)).size().reset_index(name="count")
            
            # Convert to list of tuples
            time_series = [(row[time_field], row["count"]) for _, row in time_series_df.iterrows()]
            
            category_series[category] = time_series
            
            # Forecast
            forecast_result = PredictiveAnalyzer.forecast_time_series(
                time_series,
                forecast_periods=forecast_periods,
                method="auto",
                frequency=frequency
            )
            
            category_forecasts[category] = forecast_result
        
        # Calculate category proportions over time
        total_by_time = df.groupby(pd.Grouper(key=time_field, freq=frequency)).size().reset_index(name="total")
        
        # Predict future proportions
        future_dates = []
        if "forecast" in next(iter(category_forecasts.values())):
            future_dates = [item["date"] for item in next(iter(category_forecasts.values()))["forecast"]]
        
        future_proportions = []
        
        for i in range(len(future_dates)):
            date_proportions = {"date": future_dates[i]}
            total = sum(category_forecasts[cat]["forecast"][i]["value"] for cat in top_categories)
            
            for category in top_categories:
                if total > 0:
                    proportion = category_forecasts[category]["forecast"][i]["value"] / total
                else:
                    proportion = 0
                date_proportions[category] = proportion
            
            future_proportions.append(date_proportions)
        
        return {
            "category_forecasts": category_forecasts,
            "future_proportions": future_proportions
        }
    
    @staticmethod
    def predict_anomalies(
        time_series: List[Tuple[datetime, float]],
        forecast_periods: int = 7,
        confidence_level: float = 0.95,
        frequency: str = "D"
    ) -> Dict[str, Any]:
        """
        Predict future anomalies in a time series.
        
        Args:
            time_series: List of (datetime, value) tuples
            forecast_periods: Number of periods to forecast
            confidence_level: Confidence level for anomaly detection
            frequency: Time series frequency ('D' for daily, 'W' for weekly, etc.)
            
        Returns:
            Dictionary containing anomaly predictions
        """
        if len(time_series) < 10:
            return {"error": "Need at least 10 data points for anomaly prediction"}
        
        # Get forecast
        forecast_result = PredictiveAnalyzer.forecast_time_series(
            time_series,
            forecast_periods=forecast_periods,
            method="auto",
            frequency=frequency
        )
        
        if "error" in forecast_result:
            return forecast_result
        
        # Calculate prediction intervals if not already present
        if "forecast" in forecast_result and "lower_bound" not in forecast_result["forecast"][0]:
            # Convert to DataFrame
            df = pd.DataFrame(time_series, columns=["ds", "y"])
            df["ds"] = pd.to_datetime(df["ds"])
            
            # Calculate standard deviation of residuals
            if SKLEARN_AVAILABLE and len(df) > 10:
                # Use last 20% as validation
                train_size = int(len(df) * 0.8)
                train_df = df.iloc[:train_size]
                test_df = df.iloc[train_size:]
                
                # Simple linear model for residuals
                train_df["days_since_start"] = (train_df["ds"] - train_df["ds"].min()).dt.days
                test_df["days_since_start"] = (test_df["ds"] - train_df["ds"].min()).dt.days
                
                X_train = train_df[["days_since_start"]].values
                y_train = train_df["y"].values
                X_test = test_df[["days_since_start"]].values
                y_test = test_df["y"].values
                
                model = LinearRegression()
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                residuals = y_test - y_pred
                std_residuals = np.std(residuals)
                
                # Z-score for confidence level
                if SCIPY_AVAILABLE:
                    z_score = stats.norm.ppf((1 + confidence_level) / 2)
                else:
                    # Approximate z-scores for common confidence levels
                    if confidence_level >= 0.99:
                        z_score = 2.576  # 99% confidence
                    elif confidence_level >= 0.95:
                        z_score = 1.96   # 95% confidence
                    elif confidence_level >= 0.90:
                        z_score = 1.645  # 90% confidence
                    else:
                        z_score = 1.0    # Default fallback
                
                # Add prediction intervals
                for i in range(len(forecast_result["forecast"])):
                    forecast_result["forecast"][i]["lower_bound"] = forecast_result["forecast"][i]["value"] - z_score * std_residuals
                    forecast_result["forecast"][i]["upper_bound"] = forecast_result["forecast"][i]["value"] + z_score * std_residuals
            else:
                # Simple approach: use historical standard deviation
                std_dev = np.std([v for _, v in time_series])
                z_score = 1.96  # Approximately 95% confidence
                
                for i in range(len(forecast_result["forecast"])):
                    forecast_result["forecast"][i]["lower_bound"] = forecast_result["forecast"][i]["value"] - z_score * std_dev
                    forecast_result["forecast"][i]["upper_bound"] = forecast_result["forecast"][i]["value"] + z_score * std_dev
        
        # Identify potential anomalies
        anomalies = []
        
        # Historical anomalies
        df = pd.DataFrame(time_series, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])
        
        if SKLEARN_AVAILABLE and len(df) >= 10:
            # Use IsolationForest for historical anomalies
            X = df["y"].values.reshape(-1, 1)
            model = IsolationForest(contamination=0.05, random_state=42)
            df["anomaly"] = model.fit_predict(X)
            
            historical_anomalies = df[df["anomaly"] == -1]
            
            for _, row in historical_anomalies.iterrows():
                anomalies.append({
                    "date": row["ds"].strftime("%Y-%m-%d"),
                    "value": float(row["y"]),
                    "type": "historical"
                })
        
        # Predicted anomalies
        for forecast in forecast_result["forecast"]:
            # Check if the forecast is outside historical range
            min_value = min(v for _, v in time_series)
            max_value = max(v for _, v in time_series)
            
            if forecast["value"] < min_value * 0.5 or forecast["value"] > max_value * 1.5:
                anomalies.append({
                    "date": forecast["date"],
                    "value": forecast["value"],
                    "type": "predicted",
                    "confidence": confidence_level
                })
        
        forecast_result["anomalies"] = anomalies
        forecast_result["confidence_level"] = confidence_level
        
        return forecast_result