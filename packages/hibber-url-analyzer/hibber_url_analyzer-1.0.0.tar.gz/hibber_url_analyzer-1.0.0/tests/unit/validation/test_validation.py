"""
Test script for validation utilities.

This script tests the validation utilities to ensure they work correctly.
"""

import os
import sys
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import validation utilities
try:
    from url_analyzer.utils.cli_validation import (
        validate_input_path, validate_output_path, validate_file_format,
        validate_filter_expression, validate_template_name, validate_args
    )
    from url_analyzer.utils.validation import (
        validate_string, validate_integer, validate_float, validate_boolean,
        validate_list, validate_dict, validate_enum, validate_url, validate_email
    )
    from url_analyzer.utils.errors import ValidationError
    
    print("✅ Successfully imported validation utilities")
except ImportError as e:
    print(f"❌ Error importing validation utilities: {e}")
    sys.exit(1)

def test_string_validation():
    """Test string validation with various scenarios including length constraints and patterns."""
    print("\n--- Testing String Validation ---")
    
    # Test valid strings
    try:
        result = validate_string("hello", min_length=1, max_length=10)
        print(f"✅ Valid string: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid string: {e}")
    
    # Test empty string
    try:
        result = validate_string("", allow_empty=False)
        print(f"❌ Empty string validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Empty string validation failed as expected: {e}")
    
    # Test string too long
    try:
        result = validate_string("hello world", max_length=5)
        print(f"❌ String too long validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ String too long validation failed as expected: {e}")
    
    # Test string pattern
    try:
        result = validate_string("abc123", pattern=r"^[a-z0-9]+$")
        print(f"✅ String pattern validation passed: {result}")
    except ValidationError as e:
        print(f"❌ Error validating string pattern: {e}")
    
    # Test invalid string pattern
    try:
        result = validate_string("abc-123", pattern=r"^[a-z0-9]+$")
        print(f"❌ Invalid string pattern validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid string pattern validation failed as expected: {e}")

def test_numeric_validation():
    """Test numeric validation."""
    print("\n--- Testing Numeric Validation ---")
    
    # Test valid integer
    try:
        result = validate_integer(42, min_value=0, max_value=100)
        print(f"✅ Valid integer: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid integer: {e}")
    
    # Test invalid integer
    try:
        result = validate_integer("not an integer")
        print(f"❌ Invalid integer validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid integer validation failed as expected: {e}")
    
    # Test integer out of range
    try:
        result = validate_integer(200, max_value=100)
        print(f"❌ Integer out of range validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Integer out of range validation failed as expected: {e}")
    
    # Test valid float
    try:
        result = validate_float(3.14, min_value=0.0, max_value=10.0)
        print(f"✅ Valid float: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid float: {e}")
    
    # Test invalid float
    try:
        result = validate_float("not a float")
        print(f"❌ Invalid float validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid float validation failed as expected: {e}")

def test_collection_validation():
    """Test collection validation."""
    print("\n--- Testing Collection Validation ---")
    
    # Test valid list
    try:
        result = validate_list([1, 2, 3], min_length=1, max_length=10)
        print(f"✅ Valid list: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid list: {e}")
    
    # Test empty list
    try:
        result = validate_list([], min_length=1)
        print(f"❌ Empty list validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Empty list validation failed as expected: {e}")
    
    # Test valid dict
    try:
        result = validate_dict({"key": "value"})
        print(f"✅ Valid dict: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid dict: {e}")
    
    # Test invalid dict
    try:
        result = validate_dict("not a dict")
        print(f"❌ Invalid dict validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid dict validation failed as expected: {e}")
    
    # Test enum validation
    try:
        result = validate_enum("apple", ["apple", "banana", "orange"])
        print(f"✅ Valid enum: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid enum: {e}")
    
    # Test invalid enum
    try:
        result = validate_enum("grape", ["apple", "banana", "orange"])
        print(f"❌ Invalid enum validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid enum validation failed as expected: {e}")

def test_url_validation():
    """Test URL validation."""
    print("\n--- Testing URL Validation ---")
    
    # Test valid URL
    try:
        result = validate_url("https://example.com")
        print(f"✅ Valid URL: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid URL: {e}")
    
    # Test invalid URL
    try:
        result = validate_url("not a url")
        print(f"❌ Invalid URL validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid URL validation failed as expected: {e}")
    
    # Test valid email
    try:
        result = validate_email("user@example.com")
        print(f"✅ Valid email: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid email: {e}")
    
    # Test invalid email
    try:
        result = validate_email("not an email")
        print(f"❌ Invalid email validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid email validation failed as expected: {e}")

def test_cli_validation():
    """Test CLI validation."""
    print("\n--- Testing CLI Validation ---")
    
    # Test filter expression validation
    try:
        result = validate_filter_expression("column=value")
        print(f"✅ Valid filter expression: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid filter expression: {e}")
    
    # Test invalid filter expression
    try:
        result = validate_filter_expression("invalid filter")
        print(f"❌ Invalid filter expression validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid filter expression validation failed as expected: {e}")
    
    # Test template name validation
    try:
        result = validate_template_name("template_name")
        print(f"✅ Valid template name: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid template name: {e}")
    
    # Test file format validation
    try:
        result = validate_file_format("test.csv", ["csv", "xlsx", "xls"])
        print(f"✅ Valid file format: {result}")
    except ValidationError as e:
        print(f"❌ Error validating valid file format: {e}")
    
    # Test invalid file format
    try:
        result = validate_file_format("test.pdf", ["csv", "xlsx", "xls"])
        print(f"❌ Invalid file format validation should have failed but returned: {result}")
    except ValidationError as e:
        print(f"✅ Invalid file format validation failed as expected: {e}")

def main():
    """Main function."""
    print("=== Testing Validation Utilities ===\n")
    
    # Run tests
    test_string_validation()
    test_numeric_validation()
    test_collection_validation()
    test_url_validation()
    test_cli_validation()
    
    print("\n=== Validation Tests Completed ===")

if __name__ == "__main__":
    main()