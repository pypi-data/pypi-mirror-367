#!/usr/bin/env python
"""
Build Distribution Script for URL Analyzer.

This script builds source and binary distributions for URL Analyzer.
It supports building wheels for different platforms and architectures.

Usage:
    python build_dist.py [--clean] [--source] [--wheel] [--all]

Options:
    --clean     Clean build directories before building
    --source    Build source distribution only
    --wheel     Build wheel distribution only
    --all       Build all distributions (default)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs() -> None:
    """
    Clean build directories.
    """
    print("Cleaning build directories...")
    
    # Directories to clean
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for dir_pattern in dirs_to_clean:
        for path in Path('.').glob(dir_pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)


def build_source_dist() -> bool:
    """
    Build source distribution.
    
    Returns:
        True if successful, False otherwise
    """
    print("Building source distribution...")
    try:
        subprocess.check_call([sys.executable, '-m', 'build', '--sdist'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building source distribution: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def build_wheel_dist() -> bool:
    """
    Build wheel distribution.
    
    Returns:
        True if successful, False otherwise
    """
    print("Building wheel distribution...")
    try:
        subprocess.check_call([sys.executable, '-m', 'build', '--wheel'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building wheel distribution: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def check_build_dependencies() -> bool:
    """
    Check if build dependencies are installed.
    
    Returns:
        True if all dependencies are installed, False otherwise
    """
    required_packages = ['build', 'wheel', 'setuptools', 'twine']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing build dependencies:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall missing dependencies with:")
        print(f"  {sys.executable} -m pip install {' '.join(missing_packages)}")
        return False
    
    return True


def print_distribution_info() -> None:
    """
    Print information about the built distributions.
    """
    print("\nDistribution files:")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  No distribution files found.")
        return
    
    for file_path in dist_dir.glob('*'):
        file_size = file_path.stat().st_size / 1024  # Size in KB
        print(f"  {file_path.name} ({file_size:.1f} KB)")
    
    print("\nTo upload to PyPI:")
    print("  python -m twine upload dist/*")
    
    print("\nTo install from the built distribution:")
    print("  pip install dist/*.whl")


def main():
    """Main function to run the build script."""
    parser = argparse.ArgumentParser(description='URL Analyzer Build Script')
    parser.add_argument('--clean', action='store_true',
                        help='Clean build directories before building')
    parser.add_argument('--source', action='store_true',
                        help='Build source distribution only')
    parser.add_argument('--wheel', action='store_true',
                        help='Build wheel distribution only')
    parser.add_argument('--all', action='store_true',
                        help='Build all distributions (default)')
    
    args = parser.parse_args()
    
    # Default to --all if no specific build option is provided
    if not (args.source or args.wheel or args.all):
        args.all = True
    
    # Check build dependencies
    if not check_build_dependencies():
        sys.exit(1)
    
    # Clean build directories if requested
    if args.clean:
        clean_build_dirs()
    
    # Build distributions
    success = True
    
    if args.source or args.all:
        if not build_source_dist():
            success = False
    
    if args.wheel or args.all:
        if not build_wheel_dist():
            success = False
    
    # Print distribution information
    if success:
        print("\nBuild completed successfully!")
        print_distribution_info()
    else:
        print("\nBuild failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()