"""
Advanced Predictive Analytics Module

This module provides advanced predictive analytics capabilities for URL data,
including time series forecasting, trend prediction, and predictive modeling
using sophisticated machine learning techniques.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split, TimeSeriesSplit
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import statsmodels.api as sm
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from pmdarima import auto_arima
    PMDARIMA_AVAILABLE = True
except ImportError:
    PMDARIMA_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, optimizers, callbacks
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class AdvancedTimeSeriesForecaster:
    """
    Advanced time series forecasting for URL data.
    
    This class provides sophisticated time series forecasting capabilities
    using various algorithms and techniques.
    """
    
    def __init__(self, method: str = "auto"):
        """
        Initialize the time series forecaster.
        
        Args:
            method: Forecasting method to use (auto, arima, prophet, lstm, etc.)
        """
        self.method = method
        self.model = None
        self.scaler = None
        self.config = {}
    
    def fit(
        self,
        time_series: List[Tuple[datetime, float]],
        exog_variables: Optional[pd.DataFrame] = None,
        seasonal_period: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fit the forecasting model to the time series data.
        
        Args:
            time_series: List of (timestamp, value) tuples
            exog_variables: Optional exogenous variables for the model
            seasonal_period: Optional seasonal period for the model
            
        Returns:
            Dictionary containing fitting results
        """
        if not time_series or len(time_series) < 5:
            return {"error": "Not enough data points for forecasting"}
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(time_series, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])
        
        # Sort by date
        df = df.sort_values("ds")
        
        # Determine best method if auto
        if self.method == "auto":
            if len(time_series) > 50 and TENSORFLOW_AVAILABLE:
                self.method = "lstm"
            elif PMDARIMA_AVAILABLE:
                self.method = "auto_arima"
            elif STATSMODELS_AVAILABLE:
                self.method = "sarimax"
            elif SKLEARN_AVAILABLE:
                self.method = "gbr"
            else:
                self.method = "naive"
        
        # Determine seasonal period if not provided
        if seasonal_period is None:
            # Try to infer from data frequency
            if len(df) > 2:
                # Calculate average time difference
                time_diff = (df["ds"].iloc[-1] - df["ds"].iloc[0]) / (len(df) - 1)
                
                if time_diff.total_seconds() < 3600:  # Less than an hour
                    seasonal_period = 24  # Hourly data, daily seasonality
                elif time_diff.total_seconds() < 86400:  # Less than a day
                    seasonal_period = 7  # Daily data, weekly seasonality
                elif time_diff.total_seconds() < 604800:  # Less than a week
                    seasonal_period = 52  # Weekly data, yearly seasonality
                elif time_diff.total_seconds() < 2592000:  # Less than a month
                    seasonal_period = 12  # Monthly data, yearly seasonality
                else:
                    seasonal_period = 4  # Quarterly data, yearly seasonality
            else:
                seasonal_period = 7  # Default to weekly seasonality
        
        # Store configuration
        self.config["seasonal_period"] = seasonal_period
        
        # Fit the appropriate model
        if self.method == "auto_arima" and PMDARIMA_AVAILABLE:
            # Use auto_arima to find the best ARIMA model
            y = df["y"].values
            
            # Create exogenous variables if provided
            X = None
            if exog_variables is not None:
                X = exog_variables.values
            
            # Fit auto_arima model
            self.model = auto_arima(
                y,
                X=X,
                seasonal=True,
                m=seasonal_period,
                suppress_warnings=True,
                error_action="ignore",
                stepwise=True
            )
            
            # Store model order
            self.config["order"] = self.model.order
            self.config["seasonal_order"] = self.model.seasonal_order
            
            return {
                "method": self.method,
                "aic": self.model.aic(),
                "order": self.model.order,
                "seasonal_order": self.model.seasonal_order
            }
            
        elif self.method == "sarimax" and STATSMODELS_AVAILABLE:
            # Use SARIMAX model
            y = df["y"].values
            
            # Create exogenous variables if provided
            exog = None
            if exog_variables is not None:
                exog = exog_variables.values
            
            # Try different orders and pick the best
            best_aic = float("inf")
            best_order = (1, 1, 1)
            best_seasonal_order = (1, 1, 1, seasonal_period)
            
            for p in range(3):
                for d in range(2):
                    for q in range(3):
                        for P in range(2):
                            for D in range(2):
                                for Q in range(2):
                                    try:
                                        model = SARIMAX(
                                            y,
                                            exog=exog,
                                            order=(p, d, q),
                                            seasonal_order=(P, D, Q, seasonal_period)
                                        )
                                        result = model.fit(disp=False)
                                        
                                        if result.aic < best_aic:
                                            best_aic = result.aic
                                            best_order = (p, d, q)
                                            best_seasonal_order = (P, D, Q, seasonal_period)
                                    except:
                                        continue
            
            # Fit the best model
            self.model = SARIMAX(
                y,
                exog=exog,
                order=best_order,
                seasonal_order=best_seasonal_order
            ).fit(disp=False)
            
            # Store model order
            self.config["order"] = best_order
            self.config["seasonal_order"] = best_seasonal_order
            
            return {
                "method": self.method,
                "aic": self.model.aic,
                "order": best_order,
                "seasonal_order": best_seasonal_order
            }
            
        elif self.method == "lstm" and TENSORFLOW_AVAILABLE:
            # Use LSTM model for time series forecasting
            # Prepare data for LSTM
            values = df["y"].values.reshape(-1, 1)
            
            # Scale the data
            self.scaler = StandardScaler()
            scaled_values = self.scaler.fit_transform(values)
            
            # Create sequences for LSTM
            def create_sequences(data, seq_length):
                xs, ys = [], []
                for i in range(len(data) - seq_length):
                    x = data[i:i+seq_length]
                    y = data[i+seq_length]
                    xs.append(x)
                    ys.append(y)
                return np.array(xs), np.array(ys)
            
            # Use 1/4 of the data length as sequence length, with a minimum of 3
            seq_length = max(3, len(scaled_values) // 4)
            X, y = create_sequences(scaled_values, seq_length)
            
            # Reshape for LSTM [samples, time steps, features]
            X = X.reshape(X.shape[0], X.shape[1], 1)
            
            # Build LSTM model
            model = models.Sequential([
                layers.LSTM(50, activation='relu', input_shape=(seq_length, 1)),
                layers.Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            
            # Split data for training and validation
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Early stopping to prevent overfitting
            early_stopping = callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            # Fit the model
            history = model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_val, y_val),
                callbacks=[early_stopping],
                verbose=0
            )
            
            self.model = model
            self.config["seq_length"] = seq_length
            
            return {
                "method": self.method,
                "loss": history.history['loss'][-1],
                "val_loss": history.history['val_loss'][-1],
                "seq_length": seq_length
            }
            
        elif self.method == "gbr" and SKLEARN_AVAILABLE:
            # Use Gradient Boosting Regressor
            # Create features from the time series
            df["dayofweek"] = df["ds"].dt.dayofweek
            df["month"] = df["ds"].dt.month
            df["year"] = df["ds"].dt.year
            df["dayofyear"] = df["ds"].dt.dayofyear
            df["dayofmonth"] = df["ds"].dt.day
            df["weekofyear"] = df["ds"].dt.isocalendar().week
            
            # Add lag features
            for lag in range(1, min(7, len(df) // 3)):
                df[f"lag_{lag}"] = df["y"].shift(lag)
            
            # Drop rows with NaN values
            df = df.dropna()
            
            if len(df) < 3:
                return {"error": "Not enough data points after creating lag features"}
            
            # Prepare features and target
            feature_columns = [col for col in df.columns if col not in ["ds", "y"]]
            X = df[feature_columns].values
            y = df["y"].values
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data for training and validation
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Fit Gradient Boosting Regressor
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate on validation set
            val_pred = model.predict(X_val)
            val_mse = mean_squared_error(y_val, val_pred)
            val_r2 = r2_score(y_val, val_pred)
            
            self.model = model
            self.config["feature_columns"] = feature_columns
            
            return {
                "method": self.method,
                "val_mse": val_mse,
                "val_r2": val_r2,
                "feature_importance": list(zip(feature_columns, model.feature_importances_))
            }
            
        else:
            # Fallback to naive forecasting
            self.method = "naive"
            self.model = df["y"].mean()
            
            return {
                "method": "naive",
                "mean_value": self.model
            }
    
    def predict(
        self,
        steps: int,
        exog_variables: Optional[pd.DataFrame] = None,
        confidence_interval: float = 0.95
    ) -> Dict[str, Any]:
        """
        Generate forecasts for future time steps.
        
        Args:
            steps: Number of steps to forecast
            exog_variables: Optional exogenous variables for the forecast
            confidence_interval: Confidence interval for prediction intervals
            
        Returns:
            Dictionary containing forecast results
        """
        if self.model is None:
            return {"error": "Model not fitted yet"}
        
        if steps <= 0:
            return {"error": "Steps must be positive"}
        
        if self.method == "auto_arima" or self.method == "sarimax":
            # Forecast with ARIMA/SARIMAX model
            exog = None
            if exog_variables is not None:
                exog = exog_variables.values
            
            # Generate forecast
            forecast = self.model.predict(n_periods=steps, X=exog)
            
            # Generate prediction intervals
            if hasattr(self.model, 'get_forecast'):
                forecast_obj = self.model.get_forecast(steps=steps, exog=exog)
                pred_int = forecast_obj.conf_int(alpha=1-confidence_interval)
                lower = pred_int.iloc[:, 0].values
                upper = pred_int.iloc[:, 1].values
            else:
                # Approximate prediction intervals
                residuals = self.model.resid
                std_resid = np.std(residuals)
                z_value = 1.96  # Approximate for 95% confidence
                lower = forecast - z_value * std_resid
                upper = forecast + z_value * std_resid
            
            return {
                "forecast": forecast.tolist(),
                "lower_bound": lower.tolist(),
                "upper_bound": upper.tolist(),
                "method": self.method
            }
            
        elif self.method == "lstm":
            # Forecast with LSTM model
            seq_length = self.config["seq_length"]
            
            # Get the last sequence from the data
            values = self.model.predict(np.zeros((1, seq_length, 1)))
            last_sequence = values[-seq_length:].reshape(1, seq_length, 1)
            
            # Generate forecasts iteratively
            forecasts = []
            for _ in range(steps):
                # Predict the next value
                next_value = self.model.predict(last_sequence)
                forecasts.append(float(next_value[0, 0]))
                
                # Update the sequence
                last_sequence = np.roll(last_sequence, -1, axis=1)
                last_sequence[0, -1, 0] = next_value[0, 0]
            
            # Inverse transform the forecasts
            forecasts = np.array(forecasts).reshape(-1, 1)
            forecasts = self.scaler.inverse_transform(forecasts).flatten()
            
            # Approximate prediction intervals
            std_dev = np.std(self.scaler.inverse_transform(self.model.predict(np.zeros((1, seq_length, 1)))) - 
                            self.scaler.inverse_transform(np.zeros((1, seq_length, 1))))
            z_value = 1.96  # Approximate for 95% confidence
            
            lower = forecasts - z_value * std_dev
            upper = forecasts + z_value * std_dev
            
            return {
                "forecast": forecasts.tolist(),
                "lower_bound": lower.tolist(),
                "upper_bound": upper.tolist(),
                "method": self.method
            }
            
        elif self.method == "gbr":
            # Forecast with Gradient Boosting Regressor
            feature_columns = self.config["feature_columns"]
            
            # Create a DataFrame for the forecast period
            last_date = pd.to_datetime(datetime.now())
            dates = [last_date + timedelta(days=i) for i in range(1, steps+1)]
            forecast_df = pd.DataFrame({"ds": dates})
            
            # Create time features
            forecast_df["dayofweek"] = forecast_df["ds"].dt.dayofweek
            forecast_df["month"] = forecast_df["ds"].dt.month
            forecast_df["year"] = forecast_df["ds"].dt.year
            forecast_df["dayofyear"] = forecast_df["ds"].dt.dayofyear
            forecast_df["dayofmonth"] = forecast_df["ds"].dt.day
            forecast_df["weekofyear"] = forecast_df["ds"].dt.isocalendar().week
            
            # Initialize lag features with the last known values
            # This is a simplification; in practice, you would use the actual last values
            for lag in range(1, 7):
                if f"lag_{lag}" in feature_columns:
                    forecast_df[f"lag_{lag}"] = 0
            
            # Add exogenous variables if provided
            if exog_variables is not None:
                for col in exog_variables.columns:
                    if col in feature_columns:
                        forecast_df[col] = exog_variables[col].values
            
            # Generate forecasts iteratively
            forecasts = []
            for i in range(steps):
                # Prepare features for the current step
                X = forecast_df.iloc[i:i+1][feature_columns].values
                X_scaled = self.scaler.transform(X)
                
                # Predict
                pred = self.model.predict(X_scaled)[0]
                forecasts.append(pred)
                
                # Update lag features for the next step
                for lag in range(6, 0, -1):
                    if i + 1 < steps and f"lag_{lag}" in feature_columns:
                        if lag == 1:
                            forecast_df.loc[i+1, f"lag_{lag}"] = pred
                        else:
                            prev_lag = f"lag_{lag-1}"
                            if prev_lag in feature_columns:
                                forecast_df.loc[i+1, f"lag_{lag}"] = forecast_df.loc[i, prev_lag]
            
            # Approximate prediction intervals
            std_dev = np.std(self.model.predict(self.scaler.transform(X)) - 
                            self.model.predict(self.scaler.transform(X)))
            z_value = 1.96  # Approximate for 95% confidence
            
            lower = np.array(forecasts) - z_value * std_dev
            upper = np.array(forecasts) + z_value * std_dev
            
            return {
                "forecast": forecasts,
                "lower_bound": lower.tolist(),
                "upper_bound": upper.tolist(),
                "method": self.method
            }
            
        else:
            # Naive forecasting
            forecast = [self.model] * steps
            
            # No prediction intervals for naive forecasting
            return {
                "forecast": forecast,
                "method": "naive"
            }
    
    def save(self, path: str) -> bool:
        """
        Save the forecasting model to disk.
        
        Args:
            path: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        if self.model is None:
            logger.error("No model to save")
            return False
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save model and configuration
            if self.method == "auto_arima" or self.method == "sarimax":
                # Save ARIMA/SARIMAX model
                import pickle
                with open(path, "wb") as f:
                    pickle.dump(self.model, f)
                
                # Save configuration
                with open(f"{path}_config.json", "w") as f:
                    json.dump({
                        "method": self.method,
                        "config": self.config
                    }, f)
                
                return True
                
            elif self.method == "lstm":
                # Save LSTM model
                self.model.save(path)
                
                # Save scaler and configuration
                import pickle
                with open(f"{path}_scaler.pkl", "wb") as f:
                    pickle.dump(self.scaler, f)
                
                with open(f"{path}_config.json", "w") as f:
                    json.dump({
                        "method": self.method,
                        "config": self.config
                    }, f)
                
                return True
                
            elif self.method == "gbr":
                # Save GBR model
                import pickle
                with open(path, "wb") as f:
                    pickle.dump(self.model, f)
                
                # Save scaler and configuration
                with open(f"{path}_scaler.pkl", "wb") as f:
                    pickle.dump(self.scaler, f)
                
                with open(f"{path}_config.json", "w") as f:
                    json.dump({
                        "method": self.method,
                        "config": self.config
                    }, f)
                
                return True
                
            else:
                # Save naive model
                with open(f"{path}_config.json", "w") as f:
                    json.dump({
                        "method": "naive",
                        "model": self.model
                    }, f)
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load(self, path: str) -> bool:
        """
        Load the forecasting model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load configuration
            with open(f"{path}_config.json", "r") as f:
                config_data = json.load(f)
            
            self.method = config_data["method"]
            
            if self.method == "naive":
                # Load naive model
                self.model = config_data["model"]
                return True
                
            elif self.method == "auto_arima" or self.method == "sarimax":
                # Load ARIMA/SARIMAX model
                import pickle
                with open(path, "rb") as f:
                    self.model = pickle.load(f)
                
                self.config = config_data["config"]
                return True
                
            elif self.method == "lstm":
                # Load LSTM model
                self.model = models.load_model(path)
                
                # Load scaler
                import pickle
                with open(f"{path}_scaler.pkl", "rb") as f:
                    self.scaler = pickle.load(f)
                
                self.config = config_data["config"]
                return True
                
            elif self.method == "gbr":
                # Load GBR model
                import pickle
                with open(path, "rb") as f:
                    self.model = pickle.load(f)
                
                # Load scaler
                with open(f"{path}_scaler.pkl", "rb") as f:
                    self.scaler = pickle.load(f)
                
                self.config = config_data["config"]
                return True
                
            else:
                logger.error(f"Unsupported method: {self.method}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False


class AdvancedPredictiveAnalyzer:
    """
    Advanced predictive analytics for URL data.
    
    This class provides comprehensive predictive analytics capabilities
    for URL data, combining multiple forecasting and prediction techniques.
    """
    
    def __init__(self):
        """Initialize the advanced predictive analyzer."""
        self.time_series_forecaster = AdvancedTimeSeriesForecaster()
    
    def predict_url_growth(
        self,
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        value_field: str = "count",
        group_by: Optional[str] = None,
        forecast_periods: int = 7,
        method: str = "auto"
    ) -> Dict[str, Any]:
        """
        Predict future growth of URL metrics with advanced models.
        
        Args:
            url_data: List of URL data dictionaries
            time_field: Field containing timestamp
            value_field: Field containing value to predict
            group_by: Field to group by (e.g., "domain", "category")
            forecast_periods: Number of periods to forecast
            method: Forecasting method to use
            
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
                time_series_df = group_df.groupby(pd.Grouper(key=time_field, freq="D"))[value_field].sum().reset_index()
                
                # Convert to list of tuples
                time_series = [(row[time_field], row[value_field]) for _, row in time_series_df.iterrows()]
                
                # Create forecaster with specified method
                forecaster = AdvancedTimeSeriesForecaster(method=method)
                
                # Fit the model
                fit_result = forecaster.fit(time_series)
                
                # Generate forecast
                forecast_result = forecaster.predict(steps=forecast_periods)
                
                results[group] = {
                    "fit_result": fit_result,
                    "forecast": forecast_result
                }
            
            return {
                "group_by": group_by,
                "forecasts": results
            }
        else:
            # Group by time only
            time_series_df = df.groupby(pd.Grouper(key=time_field, freq="D"))[value_field].sum().reset_index()
            
            # Convert to list of tuples
            time_series = [(row[time_field], row[value_field]) for _, row in time_series_df.iterrows()]
            
            # Create forecaster with specified method
            forecaster = AdvancedTimeSeriesForecaster(method=method)
            
            # Fit the model
            fit_result = forecaster.fit(time_series)
            
            # Generate forecast
            forecast_result = forecaster.predict(steps=forecast_periods)
            
            return {
                "fit_result": fit_result,
                "forecast": forecast_result
            }
    
    def predict_category_shifts(
        self,
        url_data: List[Dict[str, Any]],
        time_field: str = "timestamp",
        category_field: str = "category",
        forecast_periods: int = 7,
        method: str = "auto"
    ) -> Dict[str, Any]:
        """
        Predict shifts in URL category distribution over time with advanced models.
        
        Args:
            url_data: List of URL data dictionaries
            time_field: Field containing timestamp
            category_field: Field containing category
            forecast_periods: Number of periods to forecast
            method: Forecasting method to use
            
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
            time_series_df = category_df.groupby(pd.Grouper(key=time_field, freq="D")).size().reset_index(name="count")
            
            # Convert to list of tuples
            time_series = [(row[time_field], row["count"]) for _, row in time_series_df.iterrows()]
            
            category_series[category] = time_series
            
            # Create forecaster with specified method
            forecaster = AdvancedTimeSeriesForecaster(method=method)
            
            # Fit the model
            fit_result = forecaster.fit(time_series)
            
            # Generate forecast
            forecast_result = forecaster.predict(steps=forecast_periods)
            
            category_forecasts[category] = {
                "fit_result": fit_result,
                "forecast": forecast_result
            }
        
        # Calculate future proportions
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, forecast_periods+1)]
        future_proportions = []
        
        for i in range(forecast_periods):
            date_proportions = {"date": future_dates[i].strftime("%Y-%m-%d")}
            total = sum(category_forecasts[cat]["forecast"]["forecast"][i] for cat in top_categories)
            
            for category in top_categories:
                if total > 0:
                    proportion = category_forecasts[category]["forecast"]["forecast"][i] / total
                else:
                    proportion = 0
                date_proportions[category] = proportion
            
            future_proportions.append(date_proportions)
        
        return {
            "category_forecasts": category_forecasts,
            "future_proportions": future_proportions
        }
    
    def predict_anomalies(
        self,
        time_series: List[Tuple[datetime, float]],
        forecast_periods: int = 7,
        confidence_level: float = 0.95,
        method: str = "auto"
    ) -> Dict[str, Any]:
        """
        Predict future anomalies in a time series with advanced models.
        
        Args:
            time_series: List of (datetime, value) tuples
            forecast_periods: Number of periods to forecast
            confidence_level: Confidence level for anomaly detection
            method: Forecasting method to use
            
        Returns:
            Dictionary containing anomaly predictions
        """
        if len(time_series) < 10:
            return {"error": "Need at least 10 data points for anomaly prediction"}
        
        # Create forecaster with specified method
        forecaster = AdvancedTimeSeriesForecaster(method=method)
        
        # Fit the model
        fit_result = forecaster.fit(time_series)
        
        # Generate forecast with prediction intervals
        forecast_result = forecaster.predict(
            steps=forecast_periods,
            confidence_interval=confidence_level
        )
        
        # Identify potential anomalies
        anomalies = []
        
        if "lower_bound" in forecast_result and "upper_bound" in forecast_result:
            for i in range(forecast_periods):
                forecast = forecast_result["forecast"][i]
                lower_bound = forecast_result["lower_bound"][i]
                upper_bound = forecast_result["upper_bound"][i]
                
                # Calculate historical range
                values = [v for _, v in time_series]
                min_value = min(values)
                max_value = max(values)
                
                # Check if forecast is outside historical range
                if forecast < min_value * 0.5 or forecast > max_value * 1.5:
                    anomalies.append({
                        "period": i + 1,
                        "forecast": forecast,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "confidence": confidence_level,
                        "reason": "Outside historical range"
                    })
                
                # Check if forecast has a large prediction interval
                interval_width = upper_bound - lower_bound
                avg_value = sum(values) / len(values)
                if interval_width > avg_value * 0.5:
                    anomalies.append({
                        "period": i + 1,
                        "forecast": forecast,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "confidence": confidence_level,
                        "reason": "Large prediction interval"
                    })
        
        forecast_result["anomalies"] = anomalies
        forecast_result["fit_result"] = fit_result
        
        return forecast_result