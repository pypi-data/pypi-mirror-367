"""
Schema Validation Module

This module provides schema validation capabilities for URL data,
ensuring that data conforms to expected formats and structures.
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

try:
    import pydantic
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class SchemaValidator:
    """
    Schema validator for URL data.
    
    This class provides methods for validating data against schemas,
    ensuring that data conforms to expected formats and structures.
    """
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema package not available. Schema validation will be limited.")
            return SchemaValidator._basic_schema_validation(data, schema)
        
        try:
            validate(instance=data, schema=schema)
            return True, []
        except ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected error during schema validation: {str(e)}"]
    
    @staticmethod
    def _basic_schema_validation(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Basic schema validation without jsonschema.
        
        Args:
            data: Data to validate
            schema: Schema to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required properties
        if "required" in schema:
            for prop in schema["required"]:
                if prop not in data:
                    errors.append(f"Required property '{prop}' is missing")
        
        # Check property types
        if "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                if prop in data:
                    # Check type
                    if "type" in prop_schema:
                        expected_type = prop_schema["type"]
                        if expected_type == "string" and not isinstance(data[prop], str):
                            errors.append(f"Property '{prop}' should be a string")
                        elif expected_type == "number" and not isinstance(data[prop], (int, float)):
                            errors.append(f"Property '{prop}' should be a number")
                        elif expected_type == "integer" and not isinstance(data[prop], int):
                            errors.append(f"Property '{prop}' should be an integer")
                        elif expected_type == "boolean" and not isinstance(data[prop], bool):
                            errors.append(f"Property '{prop}' should be a boolean")
                        elif expected_type == "array" and not isinstance(data[prop], list):
                            errors.append(f"Property '{prop}' should be an array")
                        elif expected_type == "object" and not isinstance(data[prop], dict):
                            errors.append(f"Property '{prop}' should be an object")
                    
                    # Check enum
                    if "enum" in prop_schema and data[prop] not in prop_schema["enum"]:
                        errors.append(f"Property '{prop}' should be one of {prop_schema['enum']}")
                    
                    # Check pattern
                    if "pattern" in prop_schema and isinstance(data[prop], str):
                        pattern = re.compile(prop_schema["pattern"])
                        if not pattern.match(data[prop]):
                            errors.append(f"Property '{prop}' does not match pattern '{prop_schema['pattern']}'")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_dataframe_schema(
        df: pd.DataFrame,
        column_types: Dict[str, str],
        required_columns: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a pandas DataFrame against a schema.
        
        Args:
            df: DataFrame to validate
            column_types: Dictionary mapping column names to expected types
            required_columns: List of required columns
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required columns
        if required_columns:
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"Required column '{col}' is missing")
        
        # Check column types
        for col, expected_type in column_types.items():
            if col in df.columns:
                # Get actual type
                actual_type = df[col].dtype
                
                # Check type compatibility
                if expected_type == "string" or expected_type == "str":
                    if not pd.api.types.is_string_dtype(actual_type):
                        errors.append(f"Column '{col}' should be of type string, but is {actual_type}")
                elif expected_type == "integer" or expected_type == "int":
                    if not pd.api.types.is_integer_dtype(actual_type):
                        errors.append(f"Column '{col}' should be of type integer, but is {actual_type}")
                elif expected_type == "float" or expected_type == "number":
                    if not pd.api.types.is_float_dtype(actual_type) and not pd.api.types.is_integer_dtype(actual_type):
                        errors.append(f"Column '{col}' should be of type number, but is {actual_type}")
                elif expected_type == "boolean" or expected_type == "bool":
                    if not pd.api.types.is_bool_dtype(actual_type):
                        errors.append(f"Column '{col}' should be of type boolean, but is {actual_type}")
                elif expected_type == "datetime":
                    if not pd.api.types.is_datetime64_dtype(actual_type):
                        errors.append(f"Column '{col}' should be of type datetime, but is {actual_type}")
                elif expected_type == "category":
                    if not pd.api.types.is_categorical_dtype(actual_type):
                        errors.append(f"Column '{col}' should be of type category, but is {actual_type}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_with_pydantic(data: Dict[str, Any], model_class: Any) -> Tuple[bool, List[str]]:
        """
        Validate data using a Pydantic model.
        
        Args:
            data: Data to validate
            model_class: Pydantic model class to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not PYDANTIC_AVAILABLE:
            logger.warning("pydantic package not available. Validation will be limited.")
            return False, ["pydantic package not available"]
        
        try:
            model_class(**data)
            return True, []
        except pydantic.ValidationError as e:
            errors = []
            for error in e.errors():
                loc = ".".join(str(l) for l in error["loc"])
                errors.append(f"{loc}: {error['msg']}")
            return False, errors
        except Exception as e:
            return False, [f"Unexpected error during validation: {str(e)}"]


class URLDataModel:
    """
    Provides Pydantic models for URL data validation.
    
    This class contains Pydantic model definitions for various URL data structures.
    """
    
    @staticmethod
    def get_url_model():
        """
        Get a Pydantic model for URL data.
        
        Returns:
            Pydantic model class for URL data
        """
        if not PYDANTIC_AVAILABLE:
            logger.warning("pydantic package not available. Model creation skipped.")
            return None
        
        class URLModel(BaseModel):
            url: str = Field(..., description="The URL string")
            domain: Optional[str] = Field(None, description="The domain part of the URL")
            path: Optional[str] = Field(None, description="The path part of the URL")
            query: Optional[str] = Field(None, description="The query part of the URL")
            fragment: Optional[str] = Field(None, description="The fragment part of the URL")
            scheme: Optional[str] = Field(None, description="The scheme part of the URL")
            is_valid: Optional[bool] = Field(None, description="Whether the URL is valid")
            
            @validator('url')
            def url_must_be_valid(cls, v):
                if not v:
                    raise ValueError('URL cannot be empty')
                # Basic URL validation
                if not re.match(r'^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(/.*)?$', v):
                    raise ValueError('URL format is invalid')
                return v
        
        return URLModel
    
    @staticmethod
    def get_url_analysis_model():
        """
        Get a Pydantic model for URL analysis results.
        
        Returns:
            Pydantic model class for URL analysis results
        """
        if not PYDANTIC_AVAILABLE:
            logger.warning("pydantic package not available. Model creation skipped.")
            return None
        
        class URLAnalysisModel(BaseModel):
            url: str = Field(..., description="The URL string")
            category: Optional[str] = Field(None, description="The category of the URL")
            is_sensitive: Optional[bool] = Field(None, description="Whether the URL is sensitive")
            is_malicious: Optional[bool] = Field(None, description="Whether the URL is malicious")
            content_type: Optional[str] = Field(None, description="The content type of the URL")
            status_code: Optional[int] = Field(None, description="The HTTP status code")
            fetch_time: Optional[float] = Field(None, description="The time taken to fetch the URL")
            analysis_time: Optional[float] = Field(None, description="The time taken to analyze the URL")
            
            @validator('category')
            def category_must_be_valid(cls, v):
                if v and v not in ["Social", "News", "Shopping", "Technology", "Entertainment", "Business", "Education", "Other"]:
                    raise ValueError('Invalid category')
                return v
            
            @validator('status_code')
            def status_code_must_be_valid(cls, v):
                if v and (v < 100 or v > 599):
                    raise ValueError('Invalid HTTP status code')
                return v
        
        return URLAnalysisModel


# JSON schemas for URL data
URL_SCHEMA = {
    "type": "object",
    "required": ["url"],
    "properties": {
        "url": {
            "type": "string",
            "pattern": "^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(/.*)?$"
        },
        "domain": {"type": "string"},
        "path": {"type": "string"},
        "query": {"type": "string"},
        "fragment": {"type": "string"},
        "scheme": {"type": "string"},
        "is_valid": {"type": "boolean"}
    }
}

URL_ANALYSIS_SCHEMA = {
    "type": "object",
    "required": ["url"],
    "properties": {
        "url": {"type": "string"},
        "category": {
            "type": "string",
            "enum": ["Social", "News", "Shopping", "Technology", "Entertainment", "Business", "Education", "Other"]
        },
        "is_sensitive": {"type": "boolean"},
        "is_malicious": {"type": "boolean"},
        "content_type": {"type": "string"},
        "status_code": {"type": "integer"},
        "fetch_time": {"type": "number"},
        "analysis_time": {"type": "number"}
    }
}

# DataFrame schemas for URL data
URL_DATAFRAME_SCHEMA = {
    "required_columns": ["url"],
    "column_types": {
        "url": "string",
        "domain": "string",
        "path": "string",
        "query": "string",
        "fragment": "string",
        "scheme": "string",
        "is_valid": "boolean"
    }
}

URL_ANALYSIS_DATAFRAME_SCHEMA = {
    "required_columns": ["url"],
    "column_types": {
        "url": "string",
        "category": "string",
        "is_sensitive": "boolean",
        "is_malicious": "boolean",
        "content_type": "string",
        "status_code": "integer",
        "fetch_time": "float",
        "analysis_time": "float"
    }
}