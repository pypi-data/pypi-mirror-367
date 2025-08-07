"""
Data Anonymization Module

This module provides data anonymization capabilities for URL data,
ensuring that sensitive information is properly anonymized or pseudonymized.
"""

import re
import logging
import hashlib
import uuid
import random
import string
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataAnonymizer:
    """
    Data anonymizer for URL data.
    
    This class provides methods for anonymizing sensitive data,
    ensuring that personally identifiable information (PII) is
    properly anonymized or pseudonymized.
    """
    
    @staticmethod
    def anonymize_column(
        df: pd.DataFrame,
        column: str,
        method: str = "hash",
        salt: Optional[str] = None,
        preserve_format: bool = False
    ) -> pd.DataFrame:
        """
        Anonymize a column in a DataFrame.
        
        Args:
            df: DataFrame containing the column to anonymize
            column: Name of the column to anonymize
            method: Anonymization method (hash, mask, random, token)
            salt: Optional salt for hashing
            preserve_format: Whether to preserve the format of the original value
            
        Returns:
            DataFrame with anonymized column
        """
        if column not in df.columns:
            logger.warning(f"Column '{column}' not found in DataFrame")
            return df
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_anonymized = df.copy()
        
        # Generate a random salt if not provided
        if salt is None and method == "hash":
            salt = uuid.uuid4().hex
        
        # Apply anonymization method
        if method == "hash":
            df_anonymized[column] = df_anonymized[column].apply(
                lambda x: DataAnonymizer._hash_value(x, salt, preserve_format) if pd.notna(x) else x
            )
        elif method == "mask":
            df_anonymized[column] = df_anonymized[column].apply(
                lambda x: DataAnonymizer._mask_value(x, preserve_format) if pd.notna(x) else x
            )
        elif method == "random":
            df_anonymized[column] = df_anonymized[column].apply(
                lambda x: DataAnonymizer._random_value(x, preserve_format) if pd.notna(x) else x
            )
        elif method == "token":
            # Create a mapping of original values to tokens
            unique_values = df[column].dropna().unique()
            token_mapping = {
                value: f"TOKEN_{i}" for i, value in enumerate(unique_values)
            }
            
            # Apply the mapping
            df_anonymized[column] = df_anonymized[column].map(token_mapping).fillna(df_anonymized[column])
        else:
            logger.warning(f"Unsupported anonymization method: {method}")
        
        return df_anonymized
    
    @staticmethod
    def _hash_value(value: Any, salt: str, preserve_format: bool) -> str:
        """
        Hash a value using SHA-256.
        
        Args:
            value: Value to hash
            salt: Salt for hashing
            preserve_format: Whether to preserve the format of the original value
            
        Returns:
            Hashed value
        """
        # Convert value to string
        value_str = str(value)
        
        # Create a hash
        hasher = hashlib.sha256()
        hasher.update((value_str + salt).encode('utf-8'))
        hashed = hasher.hexdigest()
        
        if preserve_format:
            # Preserve the format of the original value
            if re.match(r'^[0-9]+$', value_str):
                # Numeric value
                return hashed[:len(value_str)].replace(r'[a-f]', lambda m: str(int(m.group(0), 16) % 10))
            elif re.match(r'^[A-Za-z]+$', value_str):
                # Alphabetic value
                if value_str.isupper():
                    return hashed[:len(value_str)].upper()
                elif value_str.islower():
                    return hashed[:len(value_str)].lower()
                else:
                    return hashed[:len(value_str)]
            elif '@' in value_str and '.' in value_str.split('@')[1]:
                # Email address
                username, domain = value_str.split('@', 1)
                hashed_username = hashed[:len(username)]
                return f"{hashed_username}@{domain}"
            else:
                # Other format
                return hashed[:len(value_str)]
        else:
            # Return the full hash
            return hashed
    
    @staticmethod
    def _mask_value(value: Any, preserve_format: bool) -> str:
        """
        Mask a value by replacing characters with asterisks.
        
        Args:
            value: Value to mask
            preserve_format: Whether to preserve the format of the original value
            
        Returns:
            Masked value
        """
        # Convert value to string
        value_str = str(value)
        
        if preserve_format:
            # Preserve the format of the original value
            if re.match(r'^[0-9]+$', value_str):
                # Numeric value
                return '*' * len(value_str)
            elif '@' in value_str and '.' in value_str.split('@')[1]:
                # Email address
                username, domain = value_str.split('@', 1)
                masked_username = '*' * len(username)
                return f"{masked_username}@{domain}"
            elif re.match(r'^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$', value_str):
                # Credit card number
                return f"****-****-****-{value_str[-4:]}"
            elif re.match(r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$', value_str):
                # Social Security Number
                return f"***-**-{value_str[-4:]}"
            elif re.match(r'^[0-9]{10}$', value_str):
                # Phone number
                return f"***-***-{value_str[-4:]}"
            else:
                # Other format
                if len(value_str) <= 4:
                    return '*' * len(value_str)
                else:
                    return value_str[:2] + '*' * (len(value_str) - 4) + value_str[-2:]
        else:
            # Mask the entire value
            return '*' * len(value_str)
    
    @staticmethod
    def _random_value(value: Any, preserve_format: bool) -> str:
        """
        Replace a value with a random value of similar format.
        
        Args:
            value: Value to replace
            preserve_format: Whether to preserve the format of the original value
            
        Returns:
            Random value
        """
        # Convert value to string
        value_str = str(value)
        
        if preserve_format:
            # Preserve the format of the original value
            if re.match(r'^[0-9]+$', value_str):
                # Numeric value
                return ''.join(random.choices(string.digits, k=len(value_str)))
            elif re.match(r'^[A-Za-z]+$', value_str):
                # Alphabetic value
                if value_str.isupper():
                    return ''.join(random.choices(string.ascii_uppercase, k=len(value_str)))
                elif value_str.islower():
                    return ''.join(random.choices(string.ascii_lowercase, k=len(value_str)))
                else:
                    return ''.join(random.choices(string.ascii_letters, k=len(value_str)))
            elif '@' in value_str and '.' in value_str.split('@')[1]:
                # Email address
                username, domain = value_str.split('@', 1)
                random_username = ''.join(random.choices(string.ascii_lowercase, k=len(username)))
                return f"{random_username}@{domain}"
            else:
                # Other format
                return ''.join(random.choices(string.ascii_letters + string.digits, k=len(value_str)))
        else:
            # Generate a completely random value
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    @staticmethod
    def anonymize_urls(
        df: pd.DataFrame,
        url_column: str = "url",
        method: str = "domain",
        preserve_query_params: bool = False
    ) -> pd.DataFrame:
        """
        Anonymize URLs in a DataFrame.
        
        Args:
            df: DataFrame containing URLs
            url_column: Name of the column containing URLs
            method: Anonymization method (domain, path, full)
            preserve_query_params: Whether to preserve query parameters
            
        Returns:
            DataFrame with anonymized URLs
        """
        if url_column not in df.columns:
            logger.warning(f"URL column '{url_column}' not found in DataFrame")
            return df
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_anonymized = df.copy()
        
        # Apply URL anonymization
        df_anonymized[url_column] = df_anonymized[url_column].apply(
            lambda x: DataAnonymizer._anonymize_url(x, method, preserve_query_params) if pd.notna(x) else x
        )
        
        return df_anonymized
    
    @staticmethod
    def _anonymize_url(url: str, method: str, preserve_query_params: bool) -> str:
        """
        Anonymize a single URL.
        
        Args:
            url: URL to anonymize
            method: Anonymization method (domain, path, full)
            preserve_query_params: Whether to preserve query parameters
            
        Returns:
            Anonymized URL
        """
        import urllib.parse
        
        try:
            # Parse the URL
            parsed = urllib.parse.urlparse(url)
            
            if method == "domain":
                # Anonymize only the domain
                netloc_parts = parsed.netloc.split('.')
                if len(netloc_parts) > 2:
                    # Subdomain present
                    tld = netloc_parts[-1]
                    sld = netloc_parts[-2]
                    anonymized_netloc = f"anon-{hashlib.md5(parsed.netloc.encode()).hexdigest()[:8]}.{sld}.{tld}"
                else:
                    # No subdomain
                    anonymized_netloc = f"anon-{hashlib.md5(parsed.netloc.encode()).hexdigest()[:8]}.com"
                
                # Reconstruct the URL
                anonymized_url = urllib.parse.urlunparse((
                    parsed.scheme,
                    anonymized_netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query if preserve_query_params else '',
                    parsed.fragment
                ))
                
            elif method == "path":
                # Anonymize domain and path
                netloc_parts = parsed.netloc.split('.')
                if len(netloc_parts) > 2:
                    # Subdomain present
                    tld = netloc_parts[-1]
                    sld = netloc_parts[-2]
                    anonymized_netloc = f"anon-{hashlib.md5(parsed.netloc.encode()).hexdigest()[:8]}.{sld}.{tld}"
                else:
                    # No subdomain
                    anonymized_netloc = f"anon-{hashlib.md5(parsed.netloc.encode()).hexdigest()[:8]}.com"
                
                # Anonymize path
                path_parts = parsed.path.split('/')
                anonymized_path = '/'.join([
                    f"anon-{hashlib.md5(part.encode()).hexdigest()[:8]}" if part else ''
                    for part in path_parts
                ])
                
                # Reconstruct the URL
                anonymized_url = urllib.parse.urlunparse((
                    parsed.scheme,
                    anonymized_netloc,
                    anonymized_path,
                    parsed.params,
                    parsed.query if preserve_query_params else '',
                    parsed.fragment
                ))
                
            elif method == "full":
                # Fully anonymize the URL
                anonymized_url = f"https://anon-{hashlib.md5(url.encode()).hexdigest()[:16]}.com"
                
            else:
                logger.warning(f"Unsupported URL anonymization method: {method}")
                anonymized_url = url
                
            return anonymized_url
            
        except Exception as e:
            logger.warning(f"Error anonymizing URL '{url}': {str(e)}")
            return url
    
    @staticmethod
    def detect_pii(df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect personally identifiable information (PII) in a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to lists of PII detections
        """
        pii_detections = {}
        
        # Define PII patterns
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            "date_of_birth": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        # Check each column for PII
        for col in df.columns:
            # Skip non-string columns
            if not pd.api.types.is_string_dtype(df[col]):
                continue
            
            # Check for PII patterns
            col_detections = []
            
            for pii_type, pattern in pii_patterns.items():
                # Count matches
                matches = df[col].str.contains(pattern, regex=True, na=False)
                match_count = matches.sum()
                
                if match_count > 0:
                    # Get sample matches
                    sample_matches = df.loc[matches, col].head(5).tolist()
                    
                    col_detections.append({
                        "pii_type": pii_type,
                        "match_count": int(match_count),
                        "match_percentage": float(match_count / len(df) * 100),
                        "sample_matches": sample_matches
                    })
            
            if col_detections:
                pii_detections[col] = col_detections
        
        return pii_detections
    
    @staticmethod
    def anonymize_dataframe(
        df: pd.DataFrame,
        config: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        Apply a series of anonymization operations to a DataFrame.
        
        Args:
            df: DataFrame to anonymize
            config: Configuration for anonymization operations
            
        Returns:
            Anonymized DataFrame
        """
        if config is None:
            config = {}
        
        # Create a copy of the DataFrame to avoid modifying the original
        df_anonymized = df.copy()
        
        # Anonymize columns
        column_config = config.get("columns", {})
        for col, col_config in column_config.items():
            if col in df.columns:
                method = col_config.get("method", "hash")
                salt = col_config.get("salt")
                preserve_format = col_config.get("preserve_format", False)
                
                df_anonymized = DataAnonymizer.anonymize_column(
                    df_anonymized, col, method=method, salt=salt, preserve_format=preserve_format
                )
        
        # Anonymize URLs
        url_config = config.get("urls", {})
        if url_config:
            url_column = url_config.get("column", "url")
            method = url_config.get("method", "domain")
            preserve_query_params = url_config.get("preserve_query_params", False)
            
            if url_column in df.columns:
                df_anonymized = DataAnonymizer.anonymize_urls(
                    df_anonymized, url_column=url_column, method=method, preserve_query_params=preserve_query_params
                )
        
        # Detect and anonymize PII
        auto_detect_pii = config.get("auto_detect_pii", False)
        if auto_detect_pii:
            pii_detections = DataAnonymizer.detect_pii(df_anonymized)
            
            for col, detections in pii_detections.items():
                if detections:
                    # Anonymize column with detected PII
                    df_anonymized = DataAnonymizer.anonymize_column(
                        df_anonymized, col, method="mask", preserve_format=True
                    )
        
        return df_anonymized


# Common anonymization configuration for URL data
URL_ANONYMIZATION_CONFIG = {
    "columns": {
        "user_id": {
            "method": "hash",
            "preserve_format": False
        },
        "ip_address": {
            "method": "mask",
            "preserve_format": True
        },
        "email": {
            "method": "mask",
            "preserve_format": True
        },
        "username": {
            "method": "token",
            "preserve_format": False
        }
    },
    "urls": {
        "column": "url",
        "method": "domain",
        "preserve_query_params": False
    },
    "auto_detect_pii": True
}