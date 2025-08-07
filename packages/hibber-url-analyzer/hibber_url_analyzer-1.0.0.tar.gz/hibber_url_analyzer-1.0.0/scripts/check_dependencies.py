#!/usr/bin/env python
"""
Dependency Checker Script for URL Analyzer

This script checks the status of all dependencies required by URL Analyzer
and provides a detailed report. It can also create a virtual environment
with all dependencies installed.

Usage:
    python check_dependencies.py [--create-venv PATH]

Options:
    --create-venv PATH    Create a virtual environment at the specified path
"""

import argparse
import os
import sys

# Add the parent directory to the path so we can import url_analyzer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from url_analyzer.utils.dependency_manager import (
    print_dependency_status,
    create_virtual_environment,
    check_dependencies_at_startup,
    generate_requirements_file
)


def main():
    """Main function to run the dependency checker."""
    parser = argparse.ArgumentParser(description='URL Analyzer Dependency Checker')
    parser.add_argument('--create-venv', metavar='PATH', type=str,
                        help='Create a virtual environment at the specified path')
    parser.add_argument('--generate-requirements', metavar='PATH', type=str,
                        help='Generate a requirements.txt file at the specified path')
    parser.add_argument('--check', action='store_true',
                        help='Check dependencies and exit with non-zero status if any core dependencies are missing')
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.check:
        if not check_dependencies_at_startup():
            print("ERROR: Missing core dependencies. Please install required dependencies.")
            sys.exit(1)
        print("All core dependencies satisfied.")
        sys.exit(0)
    
    # Create virtual environment if requested
    if args.create_venv:
        print(f"Creating virtual environment at {args.create_venv}...")
        if create_virtual_environment(args.create_venv):
            print(f"Virtual environment created successfully at {args.create_venv}")
        else:
            print(f"Failed to create virtual environment at {args.create_venv}")
            sys.exit(1)
    
    # Generate requirements file if requested
    if args.generate_requirements:
        print(f"Generating requirements file at {args.generate_requirements}...")
        generate_requirements_file(args.generate_requirements)
        print(f"Requirements file generated at {args.generate_requirements}")
    
    # If no specific action was requested, print dependency status
    if not (args.create_venv or args.generate_requirements or args.check):
        print_dependency_status()


if __name__ == "__main__":
    main()