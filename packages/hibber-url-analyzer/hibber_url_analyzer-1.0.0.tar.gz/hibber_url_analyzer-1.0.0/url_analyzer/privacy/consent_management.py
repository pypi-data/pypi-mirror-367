"""
Consent Management Module

This module provides functionality for managing user consent for data processing,
supporting compliance with data privacy regulations such as GDPR and CCPA.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConsentManager:
    """
    Consent manager for handling user consent preferences.
    
    This class provides methods for recording, validating, and enforcing user consent
    for various data processing operations.
    """
    
    def __init__(self, consent_store_path: Optional[str] = None):
        """
        Initialize the consent manager.
        
        Args:
            consent_store_path: Path to the consent store file
        """
        self.consent_store_path = consent_store_path
        self.consent_records: Dict[str, Dict[str, Any]] = {}
        
        # Load existing consent records if available
        if consent_store_path and os.path.exists(consent_store_path):
            try:
                with open(consent_store_path, 'r') as f:
                    self.consent_records = json.load(f)
                logger.info(f"Loaded {len(self.consent_records)} consent records from {consent_store_path}")
            except Exception as e:
                logger.error(f"Error loading consent records: {str(e)}")
    
    def save_consent_store(self) -> bool:
        """
        Save the consent records to the consent store file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.consent_store_path:
            logger.warning("No consent store path specified, cannot save consent records")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.consent_store_path), exist_ok=True)
            
            # Save consent records
            with open(self.consent_store_path, 'w') as f:
                json.dump(self.consent_records, f, indent=2)
            
            logger.info(f"Saved {len(self.consent_records)} consent records to {self.consent_store_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving consent records: {str(e)}")
            return False
    
    def record_consent(
        self,
        user_id: str,
        purpose: str,
        consented: bool,
        timestamp: Optional[datetime] = None,
        expiration: Optional[datetime] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a user's consent for a specific purpose.
        
        Args:
            user_id: Identifier for the user
            purpose: Purpose for which consent is being recorded
            consented: Whether the user consented
            timestamp: When the consent was recorded (defaults to now)
            expiration: When the consent expires (optional)
            additional_data: Additional data related to the consent
            
        Returns:
            Dictionary containing the consent record
        """
        # Use current time if no timestamp provided
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create consent record
        consent_record = {
            "user_id": user_id,
            "purpose": purpose,
            "consented": consented,
            "timestamp": timestamp.isoformat(),
            "consent_id": f"{user_id}-{purpose}-{timestamp.strftime('%Y%m%d%H%M%S')}",
        }
        
        # Add expiration if provided
        if expiration:
            consent_record["expiration"] = expiration.isoformat()
        
        # Add additional data if provided
        if additional_data:
            consent_record["additional_data"] = additional_data
        
        # Store the consent record
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
        
        self.consent_records[user_id][purpose] = consent_record
        
        # Save the updated consent store
        self.save_consent_store()
        
        return consent_record
    
    def check_consent(
        self,
        user_id: str,
        purpose: str,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Check if a user has consented to a specific purpose.
        
        Args:
            user_id: Identifier for the user
            purpose: Purpose to check consent for
            current_time: Current time for checking expiration (defaults to now)
            
        Returns:
            Dictionary containing consent status and details
        """
        # Use current time if not provided
        if current_time is None:
            current_time = datetime.now()
        
        # Check if user exists in consent records
        if user_id not in self.consent_records:
            return {
                "consented": False,
                "reason": "No consent records found for user",
                "user_id": user_id,
                "purpose": purpose
            }
        
        # Check if purpose exists in user's consent records
        if purpose not in self.consent_records[user_id]:
            return {
                "consented": False,
                "reason": "No consent record found for purpose",
                "user_id": user_id,
                "purpose": purpose
            }
        
        # Get the consent record
        consent_record = self.consent_records[user_id][purpose]
        
        # Check if consent has expired
        if "expiration" in consent_record:
            expiration = datetime.fromisoformat(consent_record["expiration"])
            if current_time > expiration:
                return {
                    "consented": False,
                    "reason": "Consent has expired",
                    "user_id": user_id,
                    "purpose": purpose,
                    "expiration": consent_record["expiration"],
                    "current_time": current_time.isoformat()
                }
        
        # Return consent status
        return {
            "consented": consent_record["consented"],
            "user_id": user_id,
            "purpose": purpose,
            "timestamp": consent_record["timestamp"],
            "consent_id": consent_record["consent_id"],
            "expiration": consent_record.get("expiration")
        }
    
    def withdraw_consent(
        self,
        user_id: str,
        purpose: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Withdraw a user's consent for a specific purpose.
        
        Args:
            user_id: Identifier for the user
            purpose: Purpose to withdraw consent for
            timestamp: When the consent was withdrawn (defaults to now)
            
        Returns:
            Dictionary containing the updated consent record
        """
        # Record consent as False
        return self.record_consent(
            user_id=user_id,
            purpose=purpose,
            consented=False,
            timestamp=timestamp
        )
    
    def get_user_consents(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all consent records for a user.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            Dictionary containing all consent records for the user
        """
        if user_id not in self.consent_records:
            return {}
        
        return self.consent_records[user_id]
    
    def filter_data_by_consent(
        self,
        df: pd.DataFrame,
        user_id_column: str,
        purpose: str,
        current_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Filter a DataFrame to include only data for users who have consented.
        
        Args:
            df: DataFrame to filter
            user_id_column: Name of the column containing user IDs
            purpose: Purpose to check consent for
            current_time: Current time for checking expiration (defaults to now)
            
        Returns:
            Filtered DataFrame
        """
        # Use current time if not provided
        if current_time is None:
            current_time = datetime.now()
        
        # Get unique user IDs
        user_ids = df[user_id_column].unique()
        
        # Check consent for each user
        consented_users = []
        for user_id in user_ids:
            # Skip null/NaN user IDs
            if pd.isna(user_id):
                continue
            
            # Check consent
            consent_status = self.check_consent(str(user_id), purpose, current_time)
            if consent_status.get("consented", False):
                consented_users.append(user_id)
        
        # Filter DataFrame to include only consented users
        return df[df[user_id_column].isin(consented_users)]
    
    def generate_consent_report(
        self,
        output_path: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a report of all consent records.
        
        Args:
            output_path: Path to save the report
            include_details: Whether to include detailed consent records
            
        Returns:
            Dictionary containing report generation results
        """
        # Create report data
        report_data = {
            "report_id": f"CONSENT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_date": datetime.now().isoformat(),
            "user_count": len(self.consent_records),
            "consent_count": sum(len(purposes) for purposes in self.consent_records.values())
        }
        
        # Calculate consent statistics
        purposes = {}
        for user_id, user_consents in self.consent_records.items():
            for purpose, consent_record in user_consents.items():
                if purpose not in purposes:
                    purposes[purpose] = {
                        "total": 0,
                        "consented": 0,
                        "not_consented": 0,
                        "expired": 0
                    }
                
                purposes[purpose]["total"] += 1
                
                # Check if consent has expired
                expired = False
                if "expiration" in consent_record:
                    expiration = datetime.fromisoformat(consent_record["expiration"])
                    if datetime.now() > expiration:
                        expired = True
                        purposes[purpose]["expired"] += 1
                
                # Count consented/not consented
                if consent_record["consented"] and not expired:
                    purposes[purpose]["consented"] += 1
                else:
                    purposes[purpose]["not_consented"] += 1
        
        # Add purpose statistics to report
        report_data["purposes"] = purposes
        
        # Add detailed consent records if requested
        if include_details:
            report_data["consent_records"] = self.consent_records
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write report to file
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        return {
            "success": True,
            "report_id": report_data["report_id"],
            "output_path": output_path
        }