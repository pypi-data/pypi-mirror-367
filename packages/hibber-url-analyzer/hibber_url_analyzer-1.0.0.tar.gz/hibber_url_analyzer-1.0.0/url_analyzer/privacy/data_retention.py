"""
Data Retention Module

This module provides data retention policy capabilities for URL data,
ensuring that data is retained only for the necessary period and
properly deleted or archived when no longer needed.
"""

import logging
import os
import json
import shutil
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RetentionPolicy:
    """
    Represents a data retention policy.
    
    This class defines a retention policy for data, including
    retention period, action to take when data expires, and
    any conditions for retention.
    """
    
    def __init__(
        self,
        name: str,
        retention_period: timedelta,
        action: str = "delete",
        conditions: Optional[Dict[str, Any]] = None,
        description: str = ""
    ):
        """
        Initialize a retention policy.
        
        Args:
            name: Name of the policy
            retention_period: Period for which data should be retained
            action: Action to take when data expires (delete, archive, anonymize)
            conditions: Optional conditions for applying the policy
            description: Description of the policy
        """
        self.name = name
        self.retention_period = retention_period
        self.action = action
        self.conditions = conditions or {}
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the policy to a dictionary.
        
        Returns:
            Dictionary representation of the policy
        """
        return {
            "name": self.name,
            "retention_period_days": self.retention_period.days,
            "action": self.action,
            "conditions": self.conditions,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, policy_dict: Dict[str, Any]) -> 'RetentionPolicy':
        """
        Create a policy from a dictionary.
        
        Args:
            policy_dict: Dictionary representation of the policy
            
        Returns:
            RetentionPolicy object
        """
        return cls(
            name=policy_dict["name"],
            retention_period=timedelta(days=policy_dict["retention_period_days"]),
            action=policy_dict["action"],
            conditions=policy_dict.get("conditions", {}),
            description=policy_dict.get("description", "")
        )
    
    def applies_to(self, data: pd.DataFrame) -> pd.Series:
        """
        Check if the policy applies to each row in the data.
        
        Args:
            data: DataFrame to check
            
        Returns:
            Boolean Series indicating which rows the policy applies to
        """
        if not self.conditions:
            # If no conditions, policy applies to all rows
            return pd.Series(True, index=data.index)
        
        # Start with all rows
        mask = pd.Series(True, index=data.index)
        
        # Apply each condition
        for column, condition in self.conditions.items():
            if column not in data.columns:
                continue
            
            if isinstance(condition, dict):
                # Complex condition
                operator = condition.get("operator", "==")
                value = condition.get("value")
                
                if operator == "==":
                    mask = mask & (data[column] == value)
                elif operator == "!=":
                    mask = mask & (data[column] != value)
                elif operator == ">":
                    mask = mask & (data[column] > value)
                elif operator == ">=":
                    mask = mask & (data[column] >= value)
                elif operator == "<":
                    mask = mask & (data[column] < value)
                elif operator == "<=":
                    mask = mask & (data[column] <= value)
                elif operator == "in":
                    mask = mask & data[column].isin(value)
                elif operator == "not in":
                    mask = mask & ~data[column].isin(value)
                elif operator == "contains":
                    mask = mask & data[column].str.contains(value, na=False)
                elif operator == "not contains":
                    mask = mask & ~data[column].str.contains(value, na=False)
            else:
                # Simple equality condition
                mask = mask & (data[column] == condition)
        
        return mask


class DataRetentionManager:
    """
    Data retention manager for URL data.
    
    This class provides methods for managing data retention policies,
    applying them to data, and executing retention actions.
    """
    
    def __init__(self, policies: Optional[List[RetentionPolicy]] = None):
        """
        Initialize the data retention manager.
        
        Args:
            policies: Optional list of retention policies
        """
        self.policies = policies or []
    
    def add_policy(self, policy: RetentionPolicy) -> None:
        """
        Add a retention policy.
        
        Args:
            policy: Retention policy to add
        """
        self.policies.append(policy)
    
    def remove_policy(self, policy_name: str) -> bool:
        """
        Remove a retention policy by name.
        
        Args:
            policy_name: Name of the policy to remove
            
        Returns:
            True if the policy was removed, False otherwise
        """
        for i, policy in enumerate(self.policies):
            if policy.name == policy_name:
                del self.policies[i]
                return True
        return False
    
    def get_policy(self, policy_name: str) -> Optional[RetentionPolicy]:
        """
        Get a retention policy by name.
        
        Args:
            policy_name: Name of the policy to get
            
        Returns:
            RetentionPolicy if found, None otherwise
        """
        for policy in self.policies:
            if policy.name == policy_name:
                return policy
        return None
    
    def list_policies(self) -> List[Dict[str, Any]]:
        """
        List all retention policies.
        
        Returns:
            List of dictionaries containing policy information
        """
        return [policy.to_dict() for policy in self.policies]
    
    def save_policies(self, file_path: str) -> bool:
        """
        Save retention policies to a file.
        
        Args:
            file_path: Path to save the policies
            
        Returns:
            True if successful, False otherwise
        """
        try:
            policies_dict = [policy.to_dict() for policy in self.policies]
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(policies_dict, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving retention policies: {str(e)}")
            return False
    
    def load_policies(self, file_path: str) -> bool:
        """
        Load retention policies from a file.
        
        Args:
            file_path: Path to load the policies from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                policies_dict = json.load(f)
            
            self.policies = [RetentionPolicy.from_dict(policy_dict) for policy_dict in policies_dict]
            
            return True
        except Exception as e:
            logger.error(f"Error loading retention policies: {str(e)}")
            return False
    
    def apply_policies(
        self,
        df: pd.DataFrame,
        timestamp_column: str,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Apply retention policies to a DataFrame.
        
        Args:
            df: DataFrame to apply policies to
            timestamp_column: Name of the column containing timestamps
            current_time: Current time (defaults to now)
            
        Returns:
            Dictionary containing the results of applying policies
        """
        if timestamp_column not in df.columns:
            return {
                "error": f"Timestamp column '{timestamp_column}' not found in DataFrame",
                "rows_to_delete": [],
                "rows_to_archive": [],
                "rows_to_anonymize": []
            }
        
        # Set current time if not provided
        if current_time is None:
            current_time = datetime.now()
        
        # Ensure timestamp column is datetime
        if not pd.api.types.is_datetime64_dtype(df[timestamp_column]):
            try:
                df[timestamp_column] = pd.to_datetime(df[timestamp_column])
            except Exception as e:
                return {
                    "error": f"Error converting timestamp column to datetime: {str(e)}",
                    "rows_to_delete": [],
                    "rows_to_archive": [],
                    "rows_to_anonymize": []
                }
        
        # Initialize results
        rows_to_delete = []
        rows_to_archive = []
        rows_to_anonymize = []
        
        # Apply each policy
        for policy in self.policies:
            # Check which rows the policy applies to
            policy_mask = policy.applies_to(df)
            
            # Check which rows have expired based on the policy
            expired_mask = (current_time - df[timestamp_column]) > policy.retention_period
            
            # Combine masks to get rows that both match the policy and have expired
            expired_policy_mask = policy_mask & expired_mask
            
            # Get indices of expired rows
            expired_indices = df[expired_policy_mask].index.tolist()
            
            # Add to appropriate action list
            if policy.action == "delete":
                rows_to_delete.extend(expired_indices)
            elif policy.action == "archive":
                rows_to_archive.extend(expired_indices)
            elif policy.action == "anonymize":
                rows_to_anonymize.extend(expired_indices)
        
        # Remove duplicates and sort
        rows_to_delete = sorted(set(rows_to_delete))
        rows_to_archive = sorted(set(rows_to_archive) - set(rows_to_delete))  # Don't archive rows that will be deleted
        rows_to_anonymize = sorted(set(rows_to_anonymize) - set(rows_to_delete) - set(rows_to_archive))  # Don't anonymize rows that will be deleted or archived
        
        return {
            "rows_to_delete": rows_to_delete,
            "rows_to_archive": rows_to_archive,
            "rows_to_anonymize": rows_to_anonymize,
            "total_rows": len(df),
            "delete_count": len(rows_to_delete),
            "archive_count": len(rows_to_archive),
            "anonymize_count": len(rows_to_anonymize)
        }
    
    def execute_retention(
        self,
        df: pd.DataFrame,
        timestamp_column: str,
        current_time: Optional[datetime] = None,
        archive_path: Optional[str] = None,
        anonymizer: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Execute retention policies on a DataFrame.
        
        Args:
            df: DataFrame to apply policies to
            timestamp_column: Name of the column containing timestamps
            current_time: Current time (defaults to now)
            archive_path: Path to archive data (required for archive action)
            anonymizer: Function to anonymize data (required for anonymize action)
            
        Returns:
            Tuple of (updated DataFrame, results dictionary)
        """
        # Apply policies to get affected rows
        results = self.apply_policies(df, timestamp_column, current_time)
        
        if "error" in results:
            return df, results
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_updated = df.copy()
        
        # Archive rows if needed
        if results["rows_to_archive"] and archive_path:
            # Create archive directory if it doesn't exist
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            
            # Get rows to archive
            rows_to_archive = df.loc[results["rows_to_archive"]]
            
            # Save to archive
            try:
                if archive_path.endswith('.csv'):
                    # Check if archive file exists
                    if os.path.exists(archive_path):
                        # Append to existing file
                        rows_to_archive.to_csv(archive_path, mode='a', header=False, index=False)
                    else:
                        # Create new file
                        rows_to_archive.to_csv(archive_path, index=False)
                elif archive_path.endswith('.json'):
                    # Check if archive file exists
                    if os.path.exists(archive_path):
                        # Load existing data
                        with open(archive_path, 'r') as f:
                            existing_data = json.load(f)
                        
                        # Append new data
                        new_data = rows_to_archive.to_dict(orient='records')
                        existing_data.extend(new_data)
                        
                        # Save updated data
                        with open(archive_path, 'w') as f:
                            json.dump(existing_data, f, indent=2)
                    else:
                        # Create new file
                        rows_to_archive.to_json(archive_path, orient='records', indent=2)
                else:
                    # Unsupported format
                    logger.warning(f"Unsupported archive format: {archive_path}")
                    results["archive_error"] = f"Unsupported archive format: {archive_path}"
            except Exception as e:
                logger.error(f"Error archiving data: {str(e)}")
                results["archive_error"] = str(e)
        
        # Anonymize rows if needed
        if results["rows_to_anonymize"] and anonymizer:
            try:
                # Get rows to anonymize
                rows_to_anonymize = df_updated.loc[results["rows_to_anonymize"]]
                
                # Anonymize rows
                anonymized_rows = anonymizer(rows_to_anonymize)
                
                # Update DataFrame with anonymized rows
                df_updated.loc[results["rows_to_anonymize"]] = anonymized_rows
            except Exception as e:
                logger.error(f"Error anonymizing data: {str(e)}")
                results["anonymize_error"] = str(e)
        
        # Delete rows
        if results["rows_to_delete"]:
            df_updated = df_updated.drop(results["rows_to_delete"])
        
        return df_updated, results
    
    def apply_retention_to_file(
        self,
        file_path: str,
        timestamp_column: str,
        output_path: Optional[str] = None,
        archive_path: Optional[str] = None,
        anonymizer: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None
    ) -> Dict[str, Any]:
        """
        Apply retention policies to a data file.
        
        Args:
            file_path: Path to the data file
            timestamp_column: Name of the column containing timestamps
            output_path: Path to save the updated data (defaults to overwrite input)
            archive_path: Path to archive data (required for archive action)
            anonymizer: Function to anonymize data (required for anonymize action)
            
        Returns:
            Dictionary containing the results of applying policies
        """
        try:
            # Load data
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                return {"error": f"Unsupported file format: {file_path}"}
            
            # Execute retention
            df_updated, results = self.execute_retention(
                df, timestamp_column, archive_path=archive_path, anonymizer=anonymizer
            )
            
            # Save updated data
            output_path = output_path or file_path
            
            if output_path.endswith('.csv'):
                df_updated.to_csv(output_path, index=False)
            elif output_path.endswith('.json'):
                df_updated.to_json(output_path, orient='records', indent=2)
            else:
                results["save_error"] = f"Unsupported output format: {output_path}"
                return results
            
            # Add file information to results
            results["input_file"] = file_path
            results["output_file"] = output_path
            results["archive_file"] = archive_path
            
            return results
        except Exception as e:
            logger.error(f"Error applying retention to file: {str(e)}")
            return {"error": str(e)}


# Common retention policies for URL data
DEFAULT_URL_RETENTION_POLICIES = [
    RetentionPolicy(
        name="sensitive_data_policy",
        retention_period=timedelta(days=90),
        action="anonymize",
        conditions={"is_sensitive": True},
        description="Anonymize sensitive URLs after 90 days"
    ),
    RetentionPolicy(
        name="error_data_policy",
        retention_period=timedelta(days=30),
        action="delete",
        conditions={"status_code": {"operator": ">=", "value": 400}},
        description="Delete error URLs after 30 days"
    ),
    RetentionPolicy(
        name="standard_data_policy",
        retention_period=timedelta(days=365),
        action="archive",
        conditions={},
        description="Archive all URLs after 1 year"
    )
]