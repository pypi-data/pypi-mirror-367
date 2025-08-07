"""
Type Validation Example

This example demonstrates the use of custom type definitions and runtime type validation
in the URL Analyzer project. It shows how to use the custom types defined in
url_analyzer.utils.types and the validate_types decorator for runtime type validation.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import custom types and validation
from url_analyzer.utils.types import (
    ConfigDict, UrlCategory, UrlData, StatDict, 
    StrDict, StrList, PluginRegistry
)
from url_analyzer.utils.validation import validate_types, validate_type, ValidationError

# Example configuration
example_config: ConfigDict = {
    "sensitive_patterns": ["facebook\\.com", "twitter\\.com"],
    "ugc_patterns": ["/user/", "/profile/"],
    "junk_subcategories": {
        "Advertising": ["adservice", "doubleclick\\.net"],
        "Analytics": ["analytics", "tracking"]
    },
    "scan_settings": {
        "max_workers": 20,
        "timeout": 7
    }
}

# Example function with custom type annotations and runtime validation
@validate_types
def classify_url_example(url: str, config: ConfigDict) -> UrlCategory:
    """
    Example function that classifies a URL using custom type annotations.
    
    Args:
        url: URL to classify
        config: Configuration dictionary
        
    Returns:
        Tuple of (category, is_sensitive)
    """
    # Simple classification logic for demonstration
    if any(pattern in url for pattern in config["sensitive_patterns"]):
        return ("Sensitive", True)
    
    for category, patterns in config["junk_subcategories"].items():
        if any(pattern in url for pattern in patterns):
            return (category, False)
    
    return ("Unknown", False)

@validate_types
def process_urls(urls: StrList, config: ConfigDict) -> Dict[str, UrlCategory]:
    """
    Process multiple URLs and return their classifications.
    
    Args:
        urls: List of URLs to process
        config: Configuration dictionary
        
    Returns:
        Dictionary mapping URLs to their classifications
    """
    results: Dict[str, UrlCategory] = {}
    
    for url in urls:
        results[url] = classify_url_example(url, config)
    
    return results

@validate_types
def generate_stats(results: Dict[str, UrlCategory]) -> StatDict:
    """
    Generate statistics from classification results.
    
    Args:
        results: Dictionary of classification results
        
    Returns:
        Statistics dictionary
    """
    stats: StatDict = {
        "total_urls": len(results),
        "category_counts": {},
        "sensitive_count": 0
    }
    
    for url, (category, is_sensitive) in results.items():
        if category not in stats["category_counts"]:
            stats["category_counts"][category] = 0
        
        stats["category_counts"][category] += 1
        
        if is_sensitive:
            stats["sensitive_count"] += 1
    
    return stats

def main():
    """Main function to demonstrate type validation."""
    print("URL Analyzer Type Validation Example")
    print("====================================")
    
    # Example URLs
    urls = [
        "https://www.facebook.com/user/123",
        "https://www.example.com/about",
        "https://analytics.google.com",
        "https://adservice.example.com"
    ]
    
    print(f"\nProcessing {len(urls)} URLs...")
    
    try:
        # Process URLs
        results = process_urls(urls, example_config)
        
        # Print results
        print("\nClassification Results:")
        for url, (category, is_sensitive) in results.items():
            print(f"  {url}: {category} (Sensitive: {is_sensitive})")
        
        # Generate and print statistics
        stats = generate_stats(results)
        print("\nStatistics:")
        print(f"  Total URLs: {stats['total_urls']}")
        print(f"  Sensitive URLs: {stats['sensitive_count']}")
        print("  Category Counts:")
        for category, count in stats["category_counts"].items():
            print(f"    {category}: {count}")
        
        # Demonstrate validation error
        print("\nDemonstrating validation error:")
        try:
            # This should raise a ValidationError because 123 is not a ConfigDict
            classify_url_example("https://example.com", 123)
        except ValidationError as e:
            print(f"  Caught expected ValidationError: {e}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()