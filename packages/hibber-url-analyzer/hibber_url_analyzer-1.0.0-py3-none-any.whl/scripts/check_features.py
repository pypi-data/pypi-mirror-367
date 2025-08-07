#!/usr/bin/env python
"""
Feature Checker Script for URL Analyzer

This script demonstrates the feature flags and optional features in URL Analyzer.
It shows how the application gracefully degrades when optional dependencies are missing.

Usage:
    python check_features.py [--analyze-url URL]

Options:
    --analyze-url URL    Analyze a specific URL
"""

import argparse
import logging
import os
import sys

# Add the parent directory to the path so we can import url_analyzer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import feature flags
from url_analyzer.utils.feature_flags import (
    print_feature_status,
    initialize_features,
    get_available_features,
    get_unavailable_features
)

# Import optional features
from url_analyzer.utils.optional_features import analyze_url


def main():
    """Main function to run the feature checker."""
    parser = argparse.ArgumentParser(description='URL Analyzer Feature Checker')
    parser.add_argument('--analyze-url', metavar='URL', type=str,
                        help='Analyze a specific URL')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Initialize features
    initialize_features()
    
    # Print feature status
    print_feature_status()
    
    # Print summary of available and unavailable features
    available = get_available_features()
    unavailable = get_unavailable_features()
    
    print("\nFeature Summary:")
    print(f"  Available features: {len([f for f, a in available.items() if a])}")
    print(f"  Unavailable features: {len(unavailable)}")
    
    # Analyze URL if provided
    if args.analyze_url:
        url = args.analyze_url
        print(f"\nAnalyzing URL: {url}")
        
        # Analyze URL with available features
        result = analyze_url(url)
        
        # Print domain information
        print("\nDomain Information:")
        for key, value in result["domain_info"].items():
            print(f"  {key}: {value}")
        
        # Print feature availability
        print("\nFeature Availability:")
        for feature, available in result["features_available"].items():
            status = "Available" if available else "Unavailable"
            print(f"  {feature}: {status}")
        
        # Print fetch result if available
        if "fetch_result" in result:
            print("\nFetch Result:")
            if "error" in result["fetch_result"]:
                print(f"  Error: {result['fetch_result']['error']}")
            else:
                print(f"  Status Code: {result['fetch_result'].get('status_code')}")
                print(f"  URL: {result['fetch_result'].get('url')}")
                print(f"  Headers: {len(result['fetch_result'].get('headers', {}))}")
                
                # Print HTML analysis if available
                if "html_analysis" in result:
                    print("\nHTML Analysis:")
                    print(f"  Title: {result['html_analysis'].get('title', '')}")
                    print(f"  Links: {result['html_analysis'].get('link_count', 0)}")
                    print(f"  Images: {result['html_analysis'].get('image_count', 0)}")
                    
                    if "headings" in result["html_analysis"]:
                        print("\n  Headings:")
                        for heading, count in result["html_analysis"]["headings"].items():
                            print(f"    {heading}: {count}")
        else:
            print("\nURL fetching is unavailable. Install 'requests' package to enable this feature.")
    
    # Provide instructions if no URL was provided
    else:
        print("\nTo analyze a URL, use the --analyze-url option:")
        print("  python check_features.py --analyze-url https://www.example.com")
        
        print("\nInstallation instructions for missing features:")
        for feature, missing_deps in unavailable.items():
            print(f"  To enable '{feature}', install: pip install {' '.join(missing_deps)}")


if __name__ == "__main__":
    main()