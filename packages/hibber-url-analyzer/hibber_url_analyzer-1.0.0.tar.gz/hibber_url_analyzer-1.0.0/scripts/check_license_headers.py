#!/usr/bin/env python3
"""
License header checker for URL Analyzer project.

This script checks that all Python files have proper license headers.
It's used as part of the pre-commit hooks to ensure consistency.
"""

import sys
import os
import argparse
from typing import List, Optional

# Expected license header template
LICENSE_HEADER_TEMPLATE = '''"""
URL Analyzer - A comprehensive tool for analyzing and categorizing URLs

Copyright (c) 2025 URL Analyzer Project
Licensed under the MIT License - see LICENSE file for details.

This file is part of the URL Analyzer project.
"""'''

# Alternative shorter header for scripts
SHORT_LICENSE_HEADER = '''# URL Analyzer - Licensed under MIT License'''

def check_license_header(file_path: str) -> bool:
    """
    Check if a Python file has a proper license header.
    
    Args:
        file_path: Path to the Python file to check
        
    Returns:
        True if the file has a proper license header, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip empty files
        if not content.strip():
            return True
            
        # Skip files that are clearly test files or generated files
        if any(pattern in file_path.lower() for pattern in [
            'test_', '__pycache__', '.pyc', 'migrations/', 'venv/', '.venv/'
        ]):
            return True
            
        # Check for shebang line first
        lines = content.split('\n')
        start_idx = 0
        
        # Skip shebang if present
        if lines and lines[0].startswith('#!'):
            start_idx = 1
            
        # Skip encoding declaration if present
        if len(lines) > start_idx and 'coding:' in lines[start_idx]:
            start_idx += 1
            
        # Look for license header in the first few lines
        header_content = '\n'.join(lines[start_idx:start_idx + 10])
        
        # Check for full license header or short header
        has_full_header = (
            'URL Analyzer' in header_content and 
            ('Licensed under' in header_content or 'MIT License' in header_content)
        )
        
        has_short_header = SHORT_LICENSE_HEADER.strip() in content
        
        return has_full_header or has_short_header
        
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

def add_license_header(file_path: str, use_short_header: bool = False) -> bool:
    """
    Add a license header to a Python file.
    
    Args:
        file_path: Path to the Python file
        use_short_header: Whether to use the short header format
        
    Returns:
        True if header was added successfully, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        insert_idx = 0
        
        # Skip shebang if present
        if lines and lines[0].startswith('#!'):
            insert_idx = 1
            
        # Skip encoding declaration if present
        if len(lines) > insert_idx and 'coding:' in lines[insert_idx]:
            insert_idx += 1
            
        # Choose header based on file type
        if use_short_header or file_path.endswith(('setup.py', 'conftest.py')):
            header = SHORT_LICENSE_HEADER + '\n\n'
        else:
            header = LICENSE_HEADER_TEMPLATE + '\n\n'
            
        # Insert header
        lines.insert(insert_idx, header)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            
        return True
        
    except Exception as e:
        print(f"Error adding header to {file_path}: {e}")
        return False

def main():
    """Main function for the license header checker."""
    parser = argparse.ArgumentParser(
        description='Check and optionally add license headers to Python files'
    )
    parser.add_argument(
        'files', 
        nargs='*', 
        help='Python files to check'
    )
    parser.add_argument(
        '--add-header', 
        action='store_true',
        help='Add license header to files that are missing it'
    )
    parser.add_argument(
        '--short-header', 
        action='store_true',
        help='Use short header format for scripts'
    )
    parser.add_argument(
        '--check-all', 
        action='store_true',
        help='Check all Python files in the project'
    )
    
    args = parser.parse_args()
    
    # Determine which files to check
    files_to_check = []
    
    if args.check_all:
        # Find all Python files in the project
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                '__pycache__', 'venv', '.venv', 'node_modules', 'build', 'dist'
            ]]
            
            for file in files:
                if file.endswith('.py'):
                    files_to_check.append(os.path.join(root, file))
    else:
        files_to_check = args.files
    
    if not files_to_check:
        print("No files to check. Use --check-all or specify files.")
        return 0
    
    # Check files
    missing_headers = []
    total_files = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
            
        if not file_path.endswith('.py'):
            continue
            
        total_files += 1
        
        if not check_license_header(file_path):
            missing_headers.append(file_path)
            
            if args.add_header:
                print(f"Adding license header to: {file_path}")
                add_license_header(file_path, args.short_header)
            else:
                print(f"Missing license header: {file_path}")
    
    # Report results
    if missing_headers and not args.add_header:
        print(f"\n❌ {len(missing_headers)} out of {total_files} files are missing license headers.")
        print("\nFiles missing headers:")
        for file_path in missing_headers:
            print(f"  - {file_path}")
        print(f"\nRun with --add-header to automatically add headers.")
        return 1
    elif missing_headers and args.add_header:
        print(f"\n✅ Added license headers to {len(missing_headers)} files.")
        return 0
    else:
        print(f"\n✅ All {total_files} Python files have proper license headers.")
        return 0

if __name__ == '__main__':
    sys.exit(main())