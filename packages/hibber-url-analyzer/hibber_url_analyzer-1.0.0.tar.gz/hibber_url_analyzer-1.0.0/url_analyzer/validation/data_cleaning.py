"""
Data Cleaning Module

This module provides data cleaning and normalization capabilities for URL data,
ensuring that data is consistent, standardized, and ready for analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
import numpy as np
from datetime import datetime
import unicodedata
import urllib.parse

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaner for URL data.
    
    This class provides methods for cleaning and normalizing URL data,
    ensuring that data is consistent, standardized, and ready for analysis.
    """
    
    @staticmethod
    def clean_urls(df: pd.DataFrame, url_column: str = "url") -> pd.DataFrame:
        """
        Clean and normalize URLs in a DataFrame.
        
        Args:
            df: DataFrame containing URLs
            url_column: Name of the column containing URLs
            
        Returns:
            DataFrame with cleaned URLs
        """
        if url_column not in df.columns:
            logger.warning(f"URL column '{url_column}' not found in DataFrame")
            return df
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_cleaned = df.copy()
        
        # Apply URL cleaning to the specified column
        df_cleaned[url_column] = df_cleaned[url_column].apply(
            lambda x: DataCleaner._clean_url(x) if pd.notna(x) else x
        )
        
        return df_cleaned
    
    @staticmethod
    def _clean_url(url: str) -> str:
        """
        Clean and normalize a single URL.
        
        Args:
            url: URL to clean
            
        Returns:
            Cleaned URL
        """
        if not url:
            return url
        
        # Convert to string if not already
        url = str(url)
        
        # Trim whitespace
        url = url.strip()
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            # Parse the URL
            parsed = urllib.parse.urlparse(url)
            
            # Normalize the domain (lowercase)
            netloc = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            # Normalize the path (remove trailing slash)
            path = parsed.path
            if path == '/':
                path = ''
            
            # Reconstruct the URL
            cleaned_url = urllib.parse.urlunparse((
                parsed.scheme,
                netloc,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return cleaned_url
        except Exception as e:
            logger.warning(f"Error cleaning URL '{url}': {str(e)}")
            return url
    
    @staticmethod
    def normalize_text_columns(df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """
        Normalize text columns in a DataFrame.
        
        Args:
            df: DataFrame containing text columns
            text_columns: List of column names containing text
            
        Returns:
            DataFrame with normalized text columns
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_normalized = df.copy()
        
        for col in text_columns:
            if col in df.columns:
                df_normalized[col] = df_normalized[col].apply(
                    lambda x: DataCleaner._normalize_text(x) if pd.notna(x) else x
                )
        
        return df_normalized
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize a text string.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return text
        
        # Convert to string if not already
        text = str(text)
        
        # Trim whitespace
        text = text.strip()
        
        # Convert to lowercase
        text = text.lower()
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def fill_missing_values(
        df: pd.DataFrame,
        fill_strategy: Dict[str, Union[str, Dict[str, Any]]]
    ) -> pd.DataFrame:
        """
        Fill missing values in a DataFrame.
        
        Args:
            df: DataFrame containing missing values
            fill_strategy: Dictionary mapping column names to fill strategies
            
        Returns:
            DataFrame with filled missing values
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_filled = df.copy()
        
        for col, strategy in fill_strategy.items():
            if col not in df.columns:
                continue
            
            if isinstance(strategy, str):
                # Simple fill strategy
                if strategy == "mean":
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df_filled[col] = df_filled[col].fillna(df[col].mean())
                elif strategy == "median":
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df_filled[col] = df_filled[col].fillna(df[col].median())
                elif strategy == "mode":
                    df_filled[col] = df_filled[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else None)
                elif strategy == "zero":
                    df_filled[col] = df_filled[col].fillna(0)
                elif strategy == "empty_string":
                    df_filled[col] = df_filled[col].fillna("")
                elif strategy == "none":
                    pass  # Do nothing, leave as NaN
                else:
                    # Use the strategy as a constant value
                    df_filled[col] = df_filled[col].fillna(strategy)
            elif isinstance(strategy, dict):
                # Advanced fill strategy
                method = strategy.get("method")
                
                if method == "forward_fill":
                    df_filled[col] = df_filled[col].ffill()
                elif method == "backward_fill":
                    df_filled[col] = df_filled[col].bfill()
                elif method == "interpolate":
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df_filled[col] = df_filled[col].interpolate(
                            method=strategy.get("interpolate_method", "linear")
                        )
                elif method == "conditional":
                    # Fill based on conditions in other columns
                    conditions = strategy.get("conditions", [])
                    for condition in conditions:
                        condition_col = condition.get("column")
                        condition_value = condition.get("value")
                        fill_value = condition.get("fill_value")
                        
                        if condition_col and condition_value is not None and fill_value is not None:
                            mask = (df_filled[condition_col] == condition_value) & df_filled[col].isna()
                            df_filled.loc[mask, col] = fill_value
                elif method == "custom":
                    # Apply a custom function
                    custom_fn = strategy.get("function")
                    if custom_fn and callable(custom_fn):
                        df_filled[col] = df_filled[col].apply(
                            lambda x: custom_fn(x) if pd.isna(x) else x
                        )
        
        return df_filled
    
    @staticmethod
    def remove_outliers(
        df: pd.DataFrame,
        numeric_columns: List[str],
        method: str = "zscore",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Remove outliers from numeric columns in a DataFrame.
        
        Args:
            df: DataFrame containing outliers
            numeric_columns: List of numeric column names
            method: Method for detecting outliers (zscore, iqr)
            threshold: Threshold for outlier detection
            
        Returns:
            DataFrame with outliers removed
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_cleaned = df.copy()
        
        # Filter to only include columns that exist and are numeric
        valid_columns = [col for col in numeric_columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if not valid_columns:
            return df_cleaned
        
        # Create a mask for rows to keep (not outliers)
        keep_mask = pd.Series(True, index=df.index)
        
        for col in valid_columns:
            if method.lower() == "zscore":
                # Z-score method
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                col_mask = z_scores <= threshold
                keep_mask = keep_mask & col_mask
            elif method.lower() == "iqr":
                # IQR method
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                col_mask = (df[col] >= lower_bound) & (df[col] <= upper_bound)
                keep_mask = keep_mask & col_mask
        
        # Apply the mask to keep non-outlier rows
        df_cleaned = df_cleaned[keep_mask]
        
        # Log the number of outliers removed
        outliers_removed = len(df) - len(df_cleaned)
        if outliers_removed > 0:
            logger.info(f"Removed {outliers_removed} outliers ({outliers_removed / len(df) * 100:.2f}% of data)")
        
        return df_cleaned
    
    @staticmethod
    def standardize_categorical_values(
        df: pd.DataFrame,
        mappings: Dict[str, Dict[str, str]]
    ) -> pd.DataFrame:
        """
        Standardize categorical values in a DataFrame.
        
        Args:
            df: DataFrame containing categorical columns
            mappings: Dictionary mapping column names to value mappings
            
        Returns:
            DataFrame with standardized categorical values
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_standardized = df.copy()
        
        for col, mapping in mappings.items():
            if col in df.columns:
                # Apply mapping to standardize values
                df_standardized[col] = df_standardized[col].map(mapping).fillna(df_standardized[col])
        
        return df_standardized
    
    @staticmethod
    def extract_url_components(
        df: pd.DataFrame,
        url_column: str = "url",
        extract_domain: bool = True,
        extract_path: bool = True,
        extract_query: bool = True,
        extract_scheme: bool = True
    ) -> pd.DataFrame:
        """
        Extract components from URLs in a DataFrame.
        
        Args:
            df: DataFrame containing URLs
            url_column: Name of the column containing URLs
            extract_domain: Whether to extract the domain
            extract_path: Whether to extract the path
            extract_query: Whether to extract the query
            extract_scheme: Whether to extract the scheme
            
        Returns:
            DataFrame with extracted URL components
        """
        if url_column not in df.columns:
            logger.warning(f"URL column '{url_column}' not found in DataFrame")
            return df
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_extracted = df.copy()
        
        # Define a function to extract URL components
        def extract_components(url):
            if pd.isna(url):
                return {
                    "domain": None,
                    "path": None,
                    "query": None,
                    "scheme": None
                }
            
            try:
                parsed = urllib.parse.urlparse(str(url))
                return {
                    "domain": parsed.netloc,
                    "path": parsed.path,
                    "query": parsed.query,
                    "scheme": parsed.scheme
                }
            except Exception as e:
                logger.warning(f"Error parsing URL '{url}': {str(e)}")
                return {
                    "domain": None,
                    "path": None,
                    "query": None,
                    "scheme": None
                }
        
        # Apply the function to extract components
        components = df_extracted[url_column].apply(extract_components)
        
        # Add extracted components as new columns
        if extract_domain:
            df_extracted["domain"] = components.apply(lambda x: x["domain"])
        
        if extract_path:
            df_extracted["path"] = components.apply(lambda x: x["path"])
        
        if extract_query:
            df_extracted["query"] = components.apply(lambda x: x["query"])
        
        if extract_scheme:
            df_extracted["scheme"] = components.apply(lambda x: x["scheme"])
        
        return df_extracted
    
    @staticmethod
    def normalize_dataframe(df: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Apply a series of normalization operations to a DataFrame.
        
        Args:
            df: DataFrame to normalize
            config: Configuration for normalization operations
            
        Returns:
            Normalized DataFrame
        """
        if config is None:
            config = {}
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_normalized = df.copy()
        
        # Clean URLs
        url_column = config.get("url_column", "url")
        if url_column in df.columns:
            df_normalized = DataCleaner.clean_urls(df_normalized, url_column=url_column)
        
        # Normalize text columns
        text_columns = config.get("text_columns", [])
        if text_columns:
            df_normalized = DataCleaner.normalize_text_columns(df_normalized, text_columns)
        
        # Fill missing values
        fill_strategy = config.get("fill_strategy")
        if fill_strategy:
            df_normalized = DataCleaner.fill_missing_values(df_normalized, fill_strategy)
        
        # Remove outliers
        outlier_config = config.get("outliers")
        if outlier_config:
            numeric_columns = outlier_config.get("columns", [])
            method = outlier_config.get("method", "zscore")
            threshold = outlier_config.get("threshold", 3.0)
            df_normalized = DataCleaner.remove_outliers(
                df_normalized, numeric_columns, method=method, threshold=threshold
            )
        
        # Standardize categorical values
        categorical_mappings = config.get("categorical_mappings")
        if categorical_mappings:
            df_normalized = DataCleaner.standardize_categorical_values(df_normalized, categorical_mappings)
        
        # Extract URL components
        extract_components = config.get("extract_url_components", False)
        if extract_components and url_column in df.columns:
            extract_config = config.get("extract_url_config", {})
            df_normalized = DataCleaner.extract_url_components(
                df_normalized,
                url_column=url_column,
                extract_domain=extract_config.get("domain", True),
                extract_path=extract_config.get("path", True),
                extract_query=extract_config.get("query", True),
                extract_scheme=extract_config.get("scheme", True)
            )
        
        return df_normalized


# Common data cleaning configuration for URL data
URL_DATA_CLEANING_CONFIG = {
    "url_column": "url",
    "text_columns": ["title", "description", "content"],
    "fill_strategy": {
        "status_code": 0,
        "fetch_time": "median",
        "analysis_time": "median",
        "content_type": "empty_string",
        "category": "Other"
    },
    "outliers": {
        "columns": ["fetch_time", "analysis_time"],
        "method": "zscore",
        "threshold": 3.0
    },
    "categorical_mappings": {
        "category": {
            "social": "Social",
            "social media": "Social",
            "news": "News",
            "news site": "News",
            "shopping": "Shopping",
            "e-commerce": "Shopping",
            "tech": "Technology",
            "technology": "Technology",
            "entertainment": "Entertainment",
            "business": "Business",
            "education": "Education",
            "educational": "Education"
        }
    },
    "extract_url_components": True,
    "extract_url_config": {
        "domain": True,
        "path": True,
        "query": True,
        "scheme": True
    }
}