"""
Test script for URL Analyzer report templates.

This script tests all available report templates by generating reports
using sample data and verifying that they display correctly.
"""

import os
import sys
import pandas as pd
import tempfile
import webbrowser
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import URL Analyzer modules
from url_analyzer.reporting.html_report import (
    generate_report_from_template,
    list_available_templates
)

def create_sample_data() -> pd.DataFrame:
    """
    Create a sample DataFrame for testing.
    
    Returns:
        Sample DataFrame with URL data
    """
    data = {
        'Domain_name': [
            'https://www.example.com',
            'https://www.google.com',
            'https://www.facebook.com',
            'https://www.twitter.com',
            'https://www.github.com',
            'https://www.stackoverflow.com',
            'https://www.reddit.com',
            'https://www.wikipedia.org',
            'https://www.amazon.com',
            'https://www.netflix.com',
            'https://www.unknown-site.com',
            'https://api.example.com',
            'https://analytics.example.com',
            'https://ads.example.com',
            'https://cdn.example.com',
        ],
        'Client_Name': [
            'Client A', 'Client A', 'Client B', 'Client B', 'Client C',
            'Client C', 'Client A', 'Client B', 'Client C', 'Client A',
            'Client B', 'Client C', 'Client A', 'Client B', 'Client C'
        ],
        'MAC_address': [
            '00:11:22:33:44:55', '00:11:22:33:44:55', '66:77:88:99:AA:BB', 
            '66:77:88:99:AA:BB', 'CC:DD:EE:FF:00:11', 'CC:DD:EE:FF:00:11',
            '00:11:22:33:44:55', '66:77:88:99:AA:BB', 'CC:DD:EE:FF:00:11',
            '00:11:22:33:44:55', '66:77:88:99:AA:BB', 'CC:DD:EE:FF:00:11',
            '00:11:22:33:44:55', '66:77:88:99:AA:BB', 'CC:DD:EE:FF:00:11'
        ],
        'Access_time': [
            '2025-08-01 08:30:00', '2025-08-01 09:15:00', '2025-08-01 10:45:00',
            '2025-08-01 12:30:00', '2025-08-01 14:20:00', '2025-08-01 16:10:00',
            '2025-08-02 08:30:00', '2025-08-02 09:15:00', '2025-08-02 10:45:00',
            '2025-08-02 12:30:00', '2025-08-02 14:20:00', '2025-08-02 16:10:00',
            '2025-08-03 08:30:00', '2025-08-03 09:15:00', '2025-08-03 10:45:00'
        ],
        'URL_Category': [
            'Corporate', 'Search', 'Sensitive', 'Sensitive', 'Corporate',
            'Corporate', 'Social', 'Educational', 'Shopping', 'Entertainment',
            'Uncategorized', 'API', 'Analytics', 'Advertising', 'CDN'
        ],
        'Is_Sensitive': [
            False, False, True, True, False,
            False, False, False, False, False,
            False, False, False, False, False
        ],
        'Base_Domain': [
            'example.com', 'google.com', 'facebook.com', 'twitter.com', 'github.com',
            'stackoverflow.com', 'reddit.com', 'wikipedia.org', 'amazon.com', 'netflix.com',
            'unknown-site.com', 'example.com', 'example.com', 'example.com', 'example.com'
        ],
        'Notes': [
            '', '', '', '', '',
            '', '', '', '', '',
            'Uncategorized domain', 'API endpoint', 'Analytics service', 'Advertising service', 'Content delivery network'
        ]
    }
    
    return pd.DataFrame(data)

def calculate_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate statistics for the report.
    
    Args:
        df: DataFrame with URL data
        
    Returns:
        Dictionary of statistics
    """
    total_urls = len(df)
    total_sensitive = df['Is_Sensitive'].sum()
    category_counts = df['URL_Category'].value_counts().to_dict()
    
    stats = {
        'Total URLs': total_urls,
        'Sensitive URLs': total_sensitive,
        'Unique Domains': df['Base_Domain'].nunique(),
        'category_counts': category_counts
    }
    
    return stats

def test_templates(interactive: bool = False) -> None:
    """
    Test all available templates by generating reports.
    
    Args:
        interactive: Whether to open reports in browser and wait for user input
    """
    # Create sample data
    df = create_sample_data()
    
    # Calculate stats
    stats = calculate_stats(df)
    
    # Get available templates
    templates = list_available_templates()
    
    print(f"Testing {len(templates)} templates...")
    
    # Create a temporary directory for the reports
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate a report for each template
        for template in templates:
            template_name = template['filename']
            print(f"Testing template: {template['name']} ({template_name})")
            
            # Generate the report
            output_path = os.path.join(temp_dir, f"report_{template_name}")
            try:
                report_path = generate_report_from_template(df, output_path, stats, template_name)
                print(f"  ✓ Report generated: {report_path}")
                
                if interactive:
                    # Open the report in the default browser
                    print(f"  Opening report in browser...")
                    webbrowser.open(f"file://{os.path.realpath(report_path)}")
                    
                    # Wait for user confirmation
                    input("  Press Enter to continue to the next template...")
                
            except Exception as e:
                print(f"  ❌ Error generating report: {e}")
    
    print("Template testing completed.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test URL Analyzer report templates")
    parser.add_argument("--interactive", action="store_true", help="Open reports in browser and wait for user input")
    args = parser.parse_args()
    
    test_templates(interactive=args.interactive)