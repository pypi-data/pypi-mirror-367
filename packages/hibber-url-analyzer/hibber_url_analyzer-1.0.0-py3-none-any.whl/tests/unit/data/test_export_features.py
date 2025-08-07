"""
Test script for the new export features.

This script tests the new export formats, advanced filtering, scheduling,
and export profiles functionality.
"""

import os
import pandas as pd
import datetime
import time
from typing import Dict, Any

from url_analyzer.data.export import (
    export_data, 
    export_filtered_data
)
from url_analyzer.data.scheduler import (
    get_scheduler,
    schedule_export
)
from url_analyzer.data.profiles import (
    export_with_profile,
    schedule_with_profile,
    list_profiles
)

# Create test directory
TEST_DIR = "test_exports"
os.makedirs(TEST_DIR, exist_ok=True)

# Create a sample DataFrame for testing
def create_test_data() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    data = {
        "Domain_name": [
            "example.com", 
            "google.com", 
            "facebook.com", 
            "twitter.com",
            "ads.doubleclick.net",
            "analytics.google.com",
            "github.com",
            "stackoverflow.com",
            "youtube.com",
            "netflix.com"
        ],
        "Category": [
            "Business", 
            "Search", 
            "Social", 
            "Social",
            "Junk",
            "Junk",
            "Development",
            "Development",
            "Entertainment",
            "Entertainment"
        ],
        "Subcategory": [
            "Website", 
            "Engine", 
            "Network", 
            "Network",
            "Advertising",
            "Analytics",
            "Repository",
            "Q&A",
            "Video",
            "Streaming"
        ],
        "Access_time": [
            "2025-08-01 10:00:00",
            "2025-08-01 10:15:00",
            "2025-08-01 10:30:00",
            "2025-08-01 10:45:00",
            "2025-08-01 11:00:00",
            "2025-08-01 11:15:00",
            "2025-08-01 11:30:00",
            "2025-08-01 11:45:00",
            "2025-08-01 12:00:00",
            "2025-08-01 12:15:00"
        ],
        "Client_Name": [
            "User1",
            "User1",
            "User2",
            "User2",
            "User1",
            "User2",
            "User3",
            "User3",
            "User1",
            "User2"
        ],
        "MAC_address": [
            "00:11:22:33:44:55",
            "00:11:22:33:44:55",
            "66:77:88:99:AA:BB",
            "66:77:88:99:AA:BB",
            "00:11:22:33:44:55",
            "66:77:88:99:AA:BB",
            "CC:DD:EE:FF:00:11",
            "CC:DD:EE:FF:00:11",
            "00:11:22:33:44:55",
            "66:77:88:99:AA:BB"
        ],
        "Is_Sensitive": [
            False,
            False,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Convert Access_time to datetime
    df["Access_time"] = pd.to_datetime(df["Access_time"])
    
    return df

def test_export_formats():
    """Test the new export formats."""
    print("\n=== Testing Export Formats ===")
    
    df = create_test_data()
    
    # Test XML export
    xml_path = export_data(df, os.path.join(TEST_DIR, "test_export.xml"), "xml")
    print(f"XML export: {xml_path}")
    
    # Test HTML export
    html_path = export_data(df, os.path.join(TEST_DIR, "test_export.html"), "html", "Test HTML Export")
    print(f"HTML export: {html_path}")
    
    # Test Markdown export
    md_path = export_data(df, os.path.join(TEST_DIR, "test_export.md"), "markdown", "Test Markdown Export")
    print(f"Markdown export: {md_path}")
    
    # Verify files exist
    for path in [xml_path, html_path, md_path]:
        if os.path.exists(path):
            print(f"✓ File exists: {path}")
        else:
            print(f"✗ File does not exist: {path}")

def test_advanced_filtering():
    """Test the advanced filtering options."""
    print("\n=== Testing Advanced Filtering ===")
    
    df = create_test_data()
    
    # Test exact match filtering
    filters_exact = {"Category": "Social"}
    exact_path = export_filtered_data(
        df, 
        os.path.join(TEST_DIR, "test_filter_exact.csv"),
        "csv",
        filters_exact,
        "exact"
    )
    print(f"Exact match filtering: {exact_path}")
    
    # Test contains filtering
    filters_contains = {"Domain_name": "google"}
    contains_path = export_filtered_data(
        df, 
        os.path.join(TEST_DIR, "test_filter_contains.csv"),
        "csv",
        filters_contains,
        "contains"
    )
    print(f"Contains filtering: {contains_path}")
    
    # Test regex filtering
    filters_regex = {"Domain_name": r".*\.com$"}
    regex_path = export_filtered_data(
        df, 
        os.path.join(TEST_DIR, "test_filter_regex.csv"),
        "csv",
        filters_regex,
        "regex"
    )
    print(f"Regex filtering: {regex_path}")
    
    # Test range filtering
    start_time = pd.to_datetime("2025-08-01 10:30:00")
    end_time = pd.to_datetime("2025-08-01 11:30:00")
    filters_range = {"Access_time": (start_time, end_time)}
    range_path = export_filtered_data(
        df, 
        os.path.join(TEST_DIR, "test_filter_range.csv"),
        "csv",
        filters_range,
        "range"
    )
    print(f"Range filtering: {range_path}")
    
    # Verify files exist
    for path in [exact_path, contains_path, regex_path, range_path]:
        if os.path.exists(path):
            print(f"✓ File exists: {path}")
        else:
            print(f"✗ File does not exist: {path}")

def test_scheduling():
    """Test the scheduling functionality."""
    print("\n=== Testing Scheduling ===")
    
    df = create_test_data()
    
    # Get scheduler
    scheduler = get_scheduler()
    
    # Schedule an export to run after 5 seconds
    task_id = schedule_export(
        df,
        os.path.join(TEST_DIR, "scheduled_export_{timestamp}.csv"),
        "csv",
        5,  # 5 seconds interval
        None,  # No filters
        "exact",
        "Scheduled Export Test"
    )
    
    print(f"Scheduled export task: {task_id}")
    
    # Wait for the export to run
    print("Waiting for scheduled export to run (5 seconds)...")
    time.sleep(7)
    
    # Get task info
    task_info = scheduler.get_task(task_id)
    print(f"Task info: {task_info}")
    
    # Check if the export was successful
    if task_info and task_info.get("last_status") == "success":
        print("✓ Scheduled export completed successfully")
    else:
        print("✗ Scheduled export failed or did not run")
    
    # Stop the scheduler
    scheduler.stop()

def test_export_profiles():
    """Test the export profiles functionality."""
    print("\n=== Testing Export Profiles ===")
    
    df = create_test_data()
    
    # List available profiles
    profiles = list_profiles()
    print("Available profiles:")
    for name, description in profiles.items():
        print(f"- {name}: {description}")
    
    # Test exporting with profiles
    profile_names = ["security_audit", "executive_summary", "detailed_analysis"]
    
    for name in profile_names:
        path = export_with_profile(name, df)
        print(f"Exported with profile '{name}': {path}")
        
        if os.path.exists(path):
            print(f"✓ File exists: {path}")
        else:
            print(f"✗ File does not exist: {path}")
    
    # Test scheduling with a profile
    task_id = schedule_with_profile(
        "junk_traffic",
        df,
        5,  # 5 seconds interval
    )
    
    print(f"Scheduled export with profile 'junk_traffic': {task_id}")
    
    # Wait for the export to run
    print("Waiting for scheduled export to run (5 seconds)...")
    time.sleep(7)
    
    # Get scheduler
    scheduler = get_scheduler()
    
    # Get task info
    task_info = scheduler.get_task(task_id)
    print(f"Task info: {task_info}")
    
    # Check if the export was successful
    if task_info and task_info.get("last_status") == "success":
        print("✓ Scheduled export with profile completed successfully")
    else:
        print("✗ Scheduled export with profile failed or did not run")
    
    # Stop the scheduler
    scheduler.stop()

def main():
    """Run all tests."""
    print("=== Testing New Export Features ===")
    
    # Test export formats
    test_export_formats()
    
    # Test advanced filtering
    test_advanced_filtering()
    
    # Test scheduling
    test_scheduling()
    
    # Test export profiles
    test_export_profiles()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()