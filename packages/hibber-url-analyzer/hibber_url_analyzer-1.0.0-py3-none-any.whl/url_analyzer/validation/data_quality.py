"""
Data Quality Module

This module provides data quality checking capabilities for URL data,
ensuring that data meets quality standards and identifying potential issues.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """
    Data quality checker for URL data.
    
    This class provides methods for checking data quality,
    identifying issues, and generating quality reports.
    """
    
    @staticmethod
    def check_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for missing values in a DataFrame.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary containing missing value statistics
        """
        # Calculate missing value counts and percentages
        missing_counts = df.isna().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Create a summary of columns with missing values
        columns_with_missing = []
        for col in df.columns:
            if missing_counts[col] > 0:
                columns_with_missing.append({
                    "column": col,
                    "missing_count": int(missing_counts[col]),
                    "missing_percentage": float(missing_percentages[col])
                })
        
        # Calculate overall statistics
        total_cells = df.size
        total_missing = missing_counts.sum()
        overall_missing_percentage = (total_missing / total_cells) * 100
        
        return {
            "columns_with_missing": columns_with_missing,
            "total_cells": int(total_cells),
            "total_missing": int(total_missing),
            "overall_missing_percentage": float(overall_missing_percentage)
        }
    
    @staticmethod
    def check_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check for duplicate rows in a DataFrame.
        
        Args:
            df: DataFrame to check
            subset: Optional list of columns to consider for duplicates
            
        Returns:
            Dictionary containing duplicate statistics
        """
        # Find duplicates
        if subset:
            duplicates = df.duplicated(subset=subset, keep='first')
        else:
            duplicates = df.duplicated(keep='first')
        
        duplicate_count = duplicates.sum()
        duplicate_percentage = (duplicate_count / len(df)) * 100
        
        # Get indices of duplicate rows
        duplicate_indices = df[duplicates].index.tolist()
        
        # Get sample of duplicate rows (up to 10)
        duplicate_samples = df.loc[duplicate_indices[:10]].to_dict('records') if duplicate_indices else []
        
        return {
            "duplicate_count": int(duplicate_count),
            "duplicate_percentage": float(duplicate_percentage),
            "duplicate_indices": duplicate_indices,
            "duplicate_samples": duplicate_samples
        }
    
    @staticmethod
    def check_value_ranges(
        df: pd.DataFrame,
        numeric_ranges: Optional[Dict[str, Tuple[float, float]]] = None,
        categorical_values: Optional[Dict[str, List[Any]]] = None
    ) -> Dict[str, Any]:
        """
        Check if values in columns are within expected ranges.
        
        Args:
            df: DataFrame to check
            numeric_ranges: Dictionary mapping column names to (min, max) ranges
            categorical_values: Dictionary mapping column names to lists of valid values
            
        Returns:
            Dictionary containing value range check results
        """
        results = {
            "numeric_columns": [],
            "categorical_columns": []
        }
        
        # Check numeric ranges
        if numeric_ranges:
            for col, (min_val, max_val) in numeric_ranges.items():
                if col in df.columns:
                    # Skip non-numeric columns
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        continue
                    
                    # Count values outside range
                    below_min = (df[col] < min_val).sum()
                    above_max = (df[col] > max_val).sum()
                    within_range = ((df[col] >= min_val) & (df[col] <= max_val)).sum()
                    
                    # Calculate percentages
                    total_non_null = df[col].count()
                    below_min_pct = (below_min / total_non_null) * 100 if total_non_null > 0 else 0
                    above_max_pct = (above_max / total_non_null) * 100 if total_non_null > 0 else 0
                    within_range_pct = (within_range / total_non_null) * 100 if total_non_null > 0 else 0
                    
                    results["numeric_columns"].append({
                        "column": col,
                        "min_value": float(min_val),
                        "max_value": float(max_val),
                        "below_min_count": int(below_min),
                        "below_min_percentage": float(below_min_pct),
                        "above_max_count": int(above_max),
                        "above_max_percentage": float(above_max_pct),
                        "within_range_count": int(within_range),
                        "within_range_percentage": float(within_range_pct)
                    })
        
        # Check categorical values
        if categorical_values:
            for col, valid_values in categorical_values.items():
                if col in df.columns:
                    # Count invalid values
                    invalid_mask = ~df[col].isin(valid_values)
                    invalid_count = invalid_mask.sum()
                    valid_count = (~invalid_mask).sum()
                    
                    # Calculate percentages
                    total_non_null = df[col].count()
                    invalid_pct = (invalid_count / total_non_null) * 100 if total_non_null > 0 else 0
                    valid_pct = (valid_count / total_non_null) * 100 if total_non_null > 0 else 0
                    
                    # Get sample of invalid values
                    invalid_values = df.loc[invalid_mask, col].unique().tolist()
                    invalid_samples = invalid_values[:10] if len(invalid_values) > 10 else invalid_values
                    
                    results["categorical_columns"].append({
                        "column": col,
                        "valid_values": valid_values,
                        "invalid_count": int(invalid_count),
                        "invalid_percentage": float(invalid_pct),
                        "valid_count": int(valid_count),
                        "valid_percentage": float(valid_pct),
                        "invalid_samples": invalid_samples
                    })
        
        return results
    
    @staticmethod
    def check_data_consistency(df: pd.DataFrame, consistency_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check data consistency based on custom rules.
        
        Args:
            df: DataFrame to check
            consistency_rules: List of consistency rule dictionaries
            
        Returns:
            Dictionary containing consistency check results
        """
        results = []
        
        for rule in consistency_rules:
            rule_type = rule.get("type")
            columns = rule.get("columns", [])
            
            if not all(col in df.columns for col in columns):
                # Skip rules with missing columns
                continue
            
            if rule_type == "comparison":
                # Compare values between two columns
                col1, col2 = columns
                operator = rule.get("operator", "==")
                
                if operator == "==":
                    inconsistent = df[col1] != df[col2]
                elif operator == "!=":
                    inconsistent = df[col1] == df[col2]
                elif operator == ">":
                    inconsistent = df[col1] <= df[col2]
                elif operator == ">=":
                    inconsistent = df[col1] < df[col2]
                elif operator == "<":
                    inconsistent = df[col1] >= df[col2]
                elif operator == "<=":
                    inconsistent = df[col1] > df[col2]
                else:
                    # Skip unsupported operators
                    continue
                
                inconsistent_count = inconsistent.sum()
                inconsistent_percentage = (inconsistent_count / len(df)) * 100
                
                results.append({
                    "rule_type": "comparison",
                    "columns": columns,
                    "operator": operator,
                    "inconsistent_count": int(inconsistent_count),
                    "inconsistent_percentage": float(inconsistent_percentage),
                    "description": rule.get("description", f"Check if {col1} {operator} {col2}")
                })
                
            elif rule_type == "dependency":
                # Check if values in one column depend on values in another
                col1, col2 = columns
                condition_col = rule.get("condition_column", col1)
                condition_value = rule.get("condition_value")
                expected_value = rule.get("expected_value")
                
                if condition_value is not None and expected_value is not None:
                    # Check if col2 has expected value when col1 has condition value
                    inconsistent = (df[condition_col] == condition_value) & (df[col2] != expected_value)
                    inconsistent_count = inconsistent.sum()
                    inconsistent_percentage = (inconsistent_count / len(df[df[condition_col] == condition_value])) * 100 if len(df[df[condition_col] == condition_value]) > 0 else 0
                    
                    results.append({
                        "rule_type": "dependency",
                        "condition_column": condition_col,
                        "condition_value": condition_value,
                        "dependent_column": col2,
                        "expected_value": expected_value,
                        "inconsistent_count": int(inconsistent_count),
                        "inconsistent_percentage": float(inconsistent_percentage),
                        "description": rule.get("description", f"Check if {col2} = {expected_value} when {condition_col} = {condition_value}")
                    })
                
            elif rule_type == "custom":
                # Apply custom validation function
                validation_fn = rule.get("validation_function")
                if validation_fn and callable(validation_fn):
                    try:
                        # Apply validation function to get mask of inconsistent rows
                        inconsistent = validation_fn(df)
                        inconsistent_count = inconsistent.sum()
                        inconsistent_percentage = (inconsistent_count / len(df)) * 100
                        
                        results.append({
                            "rule_type": "custom",
                            "columns": columns,
                            "inconsistent_count": int(inconsistent_count),
                            "inconsistent_percentage": float(inconsistent_percentage),
                            "description": rule.get("description", "Custom validation rule")
                        })
                    except Exception as e:
                        logger.error(f"Error applying custom validation function: {str(e)}")
        
        return {
            "consistency_checks": results
        }
    
    @staticmethod
    def check_url_validity(df: pd.DataFrame, url_column: str = "url") -> Dict[str, Any]:
        """
        Check the validity of URLs in a DataFrame.
        
        Args:
            df: DataFrame to check
            url_column: Name of the column containing URLs
            
        Returns:
            Dictionary containing URL validity check results
        """
        if url_column not in df.columns:
            return {
                "error": f"URL column '{url_column}' not found in DataFrame"
            }
        
        # Basic URL regex pattern
        url_pattern = re.compile(
            r'^(https?://)?'  # http:// or https:// (optional)
            r'([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?'  # domain
            r'(/.*)?$'  # path (optional)
        )
        
        # Check each URL
        valid_mask = df[url_column].apply(lambda x: bool(url_pattern.match(str(x))) if pd.notna(x) else False)
        invalid_mask = ~valid_mask & df[url_column].notna()
        
        valid_count = valid_mask.sum()
        invalid_count = invalid_mask.sum()
        missing_count = df[url_column].isna().sum()
        
        total_urls = len(df)
        valid_percentage = (valid_count / total_urls) * 100
        invalid_percentage = (invalid_count / total_urls) * 100
        missing_percentage = (missing_count / total_urls) * 100
        
        # Get sample of invalid URLs
        invalid_urls = df.loc[invalid_mask, url_column].head(10).tolist()
        
        # Check for common URL issues
        issues = []
        
        # Check for URLs without scheme
        no_scheme_mask = df[url_column].apply(
            lambda x: not str(x).startswith(('http://', 'https://')) if pd.notna(x) else False
        )
        no_scheme_count = no_scheme_mask.sum()
        if no_scheme_count > 0:
            issues.append({
                "issue_type": "missing_scheme",
                "count": int(no_scheme_count),
                "percentage": float((no_scheme_count / total_urls) * 100),
                "description": "URLs missing http:// or https:// scheme"
            })
        
        # Check for URLs with unusual TLDs
        common_tlds = {'.com', '.org', '.net', '.edu', '.gov', '.io', '.co', '.info', '.biz'}
        unusual_tld_mask = df[url_column].apply(
            lambda x: not any(str(x).endswith(tld) for tld in common_tlds) if pd.notna(x) else False
        )
        unusual_tld_count = unusual_tld_mask.sum()
        if unusual_tld_count > 0:
            issues.append({
                "issue_type": "unusual_tld",
                "count": int(unusual_tld_count),
                "percentage": float((unusual_tld_count / total_urls) * 100),
                "description": "URLs with unusual top-level domains"
            })
        
        return {
            "valid_count": int(valid_count),
            "valid_percentage": float(valid_percentage),
            "invalid_count": int(invalid_count),
            "invalid_percentage": float(invalid_percentage),
            "missing_count": int(missing_count),
            "missing_percentage": float(missing_percentage),
            "invalid_samples": invalid_urls,
            "issues": issues
        }
    
    @staticmethod
    def generate_data_quality_report(df: pd.DataFrame, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive data quality report for a DataFrame.
        
        Args:
            df: DataFrame to analyze
            config: Configuration for quality checks
            
        Returns:
            Dictionary containing data quality report
        """
        if config is None:
            config = {}
        
        # Initialize report
        report = {
            "timestamp": datetime.now().isoformat(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist()
        }
        
        # Check missing values
        report["missing_values"] = DataQualityChecker.check_missing_values(df)
        
        # Check duplicates
        duplicate_subset = config.get("duplicate_subset")
        report["duplicates"] = DataQualityChecker.check_duplicates(df, subset=duplicate_subset)
        
        # Check value ranges
        numeric_ranges = config.get("numeric_ranges")
        categorical_values = config.get("categorical_values")
        if numeric_ranges or categorical_values:
            report["value_ranges"] = DataQualityChecker.check_value_ranges(
                df, numeric_ranges=numeric_ranges, categorical_values=categorical_values
            )
        
        # Check data consistency
        consistency_rules = config.get("consistency_rules")
        if consistency_rules:
            report["consistency"] = DataQualityChecker.check_data_consistency(df, consistency_rules)
        
        # Check URL validity
        url_column = config.get("url_column", "url")
        if url_column in df.columns:
            report["url_validity"] = DataQualityChecker.check_url_validity(df, url_column=url_column)
        
        # Calculate overall quality score
        quality_score = DataQualityChecker._calculate_quality_score(report)
        report["quality_score"] = quality_score
        
        return report
    
    @staticmethod
    def _calculate_quality_score(report: Dict[str, Any]) -> float:
        """
        Calculate an overall data quality score based on the quality report.
        
        Args:
            report: Data quality report
            
        Returns:
            Quality score between 0 and 100
        """
        score = 100.0
        deductions = []
        
        # Deduct for missing values
        if "missing_values" in report:
            missing_pct = report["missing_values"].get("overall_missing_percentage", 0)
            deduction = missing_pct * 0.5  # Deduct 0.5 points for each percent of missing values
            deductions.append(("missing_values", deduction))
        
        # Deduct for duplicates
        if "duplicates" in report:
            duplicate_pct = report["duplicates"].get("duplicate_percentage", 0)
            deduction = duplicate_pct * 0.5  # Deduct 0.5 points for each percent of duplicates
            deductions.append(("duplicates", deduction))
        
        # Deduct for value range issues
        if "value_ranges" in report:
            # Deduct for numeric range issues
            numeric_deduction = 0
            for col_info in report["value_ranges"].get("numeric_columns", []):
                outside_range_pct = col_info.get("below_min_percentage", 0) + col_info.get("above_max_percentage", 0)
                numeric_deduction += outside_range_pct * 0.2  # Deduct 0.2 points for each percent outside range
            
            # Deduct for categorical value issues
            categorical_deduction = 0
            for col_info in report["value_ranges"].get("categorical_columns", []):
                invalid_pct = col_info.get("invalid_percentage", 0)
                categorical_deduction += invalid_pct * 0.2  # Deduct 0.2 points for each percent of invalid values
            
            deductions.append(("value_ranges_numeric", numeric_deduction))
            deductions.append(("value_ranges_categorical", categorical_deduction))
        
        # Deduct for consistency issues
        if "consistency" in report and "consistency_checks" in report["consistency"]:
            consistency_deduction = 0
            for check in report["consistency"]["consistency_checks"]:
                inconsistent_pct = check.get("inconsistent_percentage", 0)
                consistency_deduction += inconsistent_pct * 0.3  # Deduct 0.3 points for each percent of inconsistencies
            
            deductions.append(("consistency", consistency_deduction))
        
        # Deduct for URL validity issues
        if "url_validity" in report:
            invalid_pct = report["url_validity"].get("invalid_percentage", 0)
            deduction = invalid_pct * 0.4  # Deduct 0.4 points for each percent of invalid URLs
            deductions.append(("url_validity", deduction))
        
        # Apply deductions
        for _, deduction in deductions:
            score -= deduction
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))


# Common data quality configurations for URL data
URL_DATA_QUALITY_CONFIG = {
    "duplicate_subset": ["url"],
    "numeric_ranges": {
        "status_code": (100, 599),
        "fetch_time": (0, 60),
        "analysis_time": (0, 60)
    },
    "categorical_values": {
        "category": ["Social", "News", "Shopping", "Technology", "Entertainment", "Business", "Education", "Other"],
        "is_sensitive": [True, False],
        "is_malicious": [True, False]
    },
    "consistency_rules": [
        {
            "type": "dependency",
            "columns": ["status_code", "content_type"],
            "condition_column": "status_code",
            "condition_value": 200,
            "expected_value": None,  # None means any non-null value
            "description": "Content type should be present for successful requests (status code 200)"
        },
        {
            "type": "comparison",
            "columns": ["fetch_time", "analysis_time"],
            "operator": "<=",
            "description": "Fetch time should be less than or equal to analysis time"
        }
    ],
    "url_column": "url"
}