#!/usr/bin/env python
"""
Dependency Update Script for URL Analyzer

This script implements a strategy for updating dependencies in a controlled manner.
It can check for updates, test compatibility, and update dependencies safely.

Usage:
    python update_dependencies.py [--check] [--update [PACKAGE]] [--test]

Options:
    --check              Check for available updates
    --update [PACKAGE]   Update all dependencies or a specific package
    --test               Run tests after updating to verify compatibility
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the parent directory to the path so we can import url_analyzer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from url_analyzer.utils.dependency_manager import (
    CORE_DEPENDENCIES,
    OPTIONAL_DEPENDENCIES,
    check_version,
    is_package_installed
)


def get_latest_version(package_name: str) -> Optional[str]:
    """
    Get the latest version of a package from PyPI.
    
    Args:
        package_name: Name of the package
        
    Returns:
        Latest version string or None if package not found
    """
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'index', 'versions', package_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output to find the latest version
        output = result.stdout
        if "Available versions:" in output:
            versions_line = output.split("Available versions:")[1].strip().split("\n")[0]
            latest_version = versions_line.split(",")[0].strip()
            return latest_version
        return None
    except subprocess.CalledProcessError:
        return None


def check_for_updates() -> Dict[str, Dict[str, str]]:
    """
    Check for available updates for all dependencies.
    
    Returns:
        Dictionary with update information
    """
    updates = {
        'core': {},
        'optional': {}
    }
    
    # Check core dependencies
    print("Checking core dependencies for updates...")
    for package, min_version in CORE_DEPENDENCIES.items():
        if is_package_installed(package):
            _, current_version = check_version(package, min_version)
            latest_version = get_latest_version(package)
            
            if latest_version and current_version != latest_version:
                updates['core'][package] = {
                    'current': current_version,
                    'latest': latest_version
                }
                print(f"  {package}: {current_version} -> {latest_version}")
            else:
                print(f"  {package}: {current_version} (up to date)")
    
    # Check optional dependencies
    print("\nChecking optional dependencies for updates...")
    for feature, dependencies in OPTIONAL_DEPENDENCIES.items():
        print(f"  {feature}:")
        for package, min_version in dependencies.items():
            if is_package_installed(package):
                _, current_version = check_version(package, min_version)
                latest_version = get_latest_version(package)
                
                if latest_version and current_version != latest_version:
                    if 'optional' not in updates:
                        updates['optional'] = {}
                    updates['optional'][package] = {
                        'current': current_version,
                        'latest': latest_version,
                        'feature': feature
                    }
                    print(f"    {package}: {current_version} -> {latest_version}")
                else:
                    print(f"    {package}: {current_version} (up to date)")
    
    return updates


def update_package(package_name: str, target_version: Optional[str] = None) -> bool:
    """
    Update a package to the latest version or a specific version.
    
    Args:
        package_name: Name of the package to update
        target_version: Specific version to install, or None for latest
        
    Returns:
        True if update was successful, False otherwise
    """
    try:
        if target_version:
            print(f"Updating {package_name} to version {target_version}...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', f"{package_name}=={target_version}"],
                check=True
            )
        else:
            print(f"Updating {package_name} to latest version...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', package_name],
                check=True
            )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating {package_name}: {e}")
        return False


def run_tests() -> bool:
    """
    Run the test suite to verify compatibility after updates.
    
    Returns:
        True if all tests pass, False otherwise
    """
    print("Running tests to verify compatibility...")
    try:
        # Run unittest discover to find and run all tests
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("All tests passed!")
            return True
        else:
            print("Some tests failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def save_update_history(updates: Dict[str, Dict[str, str]], success: bool) -> None:
    """
    Save update history to a JSON file.
    
    Args:
        updates: Dictionary with update information
        success: Whether the update was successful
    """
    history_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'logs',
        'dependency_updates.json'
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.dirname(history_file)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Load existing history or create new
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {'updates': []}
    else:
        history = {'updates': []}
    
    # Add new update record
    update_record = {
        'timestamp': datetime.now().isoformat(),
        'updates': updates,
        'success': success
    }
    
    history['updates'].append(update_record)
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)


def create_backup() -> str:
    """
    Create a backup of the current requirements.
    
    Returns:
        Path to the backup file
    """
    requirements_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'requirements.txt'
    )
    
    backup_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'backups'
    )
    
    # Create backups directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'requirements_{timestamp}.txt')
    
    # Copy requirements file
    with open(requirements_path, 'r') as src, open(backup_path, 'w') as dst:
        dst.write(src.read())
    
    print(f"Created backup at {backup_path}")
    return backup_path


def main():
    """Main function to run the dependency updater."""
    parser = argparse.ArgumentParser(description='URL Analyzer Dependency Updater')
    parser.add_argument('--check', action='store_true',
                        help='Check for available updates')
    parser.add_argument('--update', nargs='?', const='all', metavar='PACKAGE',
                        help='Update all dependencies or a specific package')
    parser.add_argument('--test', action='store_true',
                        help='Run tests after updating to verify compatibility')
    
    args = parser.parse_args()
    
    # Default to --check if no arguments provided
    if not (args.check or args.update or args.test):
        args.check = True
    
    # Check for updates
    if args.check:
        updates = check_for_updates()
        
        # Print summary
        core_updates = updates.get('core', {})
        optional_updates = updates.get('optional', {})
        
        print("\nUpdate Summary:")
        print(f"  Core dependencies: {len(core_updates)} updates available")
        print(f"  Optional dependencies: {len(optional_updates)} updates available")
        
        if not core_updates and not optional_updates:
            print("\nAll dependencies are up to date!")
    
    # Update dependencies
    if args.update:
        # Create backup before updating
        backup_path = create_backup()
        
        updates = {}
        success = True
        
        if args.update == 'all':
            # Check for available updates
            available_updates = check_for_updates()
            updates = available_updates
            
            # Update core dependencies
            print("\nUpdating core dependencies...")
            for package in available_updates.get('core', {}):
                if not update_package(package):
                    success = False
            
            # Update optional dependencies
            print("\nUpdating optional dependencies...")
            for package in available_updates.get('optional', {}):
                if not update_package(package):
                    success = False
        else:
            # Update specific package
            package = args.update
            current_version = None
            
            # Check if package is installed
            if is_package_installed(package):
                # Get current version
                for pkg, min_version in CORE_DEPENDENCIES.items():
                    if pkg == package:
                        _, current_version = check_version(package, min_version)
                        break
                
                if not current_version:
                    for feature, dependencies in OPTIONAL_DEPENDENCIES.items():
                        for pkg, min_version in dependencies.items():
                            if pkg == package:
                                _, current_version = check_version(package, min_version)
                                break
                        if current_version:
                            break
            
            # Update the package
            latest_version = get_latest_version(package)
            if latest_version:
                if update_package(package):
                    updates[package] = {
                        'current': current_version,
                        'latest': latest_version
                    }
                else:
                    success = False
            else:
                print(f"Package {package} not found on PyPI")
                success = False
        
        # Run tests if requested
        if args.test and success:
            test_success = run_tests()
            if not test_success:
                print(f"\nTests failed after updating. You may want to restore from backup: {backup_path}")
                success = False
        
        # Save update history
        save_update_history(updates, success)
        
        if success:
            print("\nAll dependencies updated successfully!")
        else:
            print("\nSome updates failed. Check the logs for details.")
    
    # Run tests without updating
    if args.test and not args.update:
        run_tests()


if __name__ == "__main__":
    main()