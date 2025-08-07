#!/usr/bin/env python
"""
Installation script for URL Analyzer.

This script provides an easy way to install URL Analyzer with various feature sets.
It creates a virtual environment, installs the package, and provides instructions for activation.

Usage:
    python install.py [--features FEATURES] [--venv PATH] [--dev] [--all]

Options:
    --features FEATURES   Comma-separated list of features to install
                          (e.g., url_fetching,html_parsing,visualization)
    --venv PATH           Path to create virtual environment (default: .venv)
    --dev                 Install development dependencies
    --all                 Install all optional dependencies
"""

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


def create_virtual_environment(path: str) -> bool:
    """
    Create a virtual environment at the specified path.
    
    Args:
        path: Path where the virtual environment should be created
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Creating virtual environment at {path}...")
        venv.create(path, with_pip=True)
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False


def get_pip_path(venv_path: str) -> str:
    """
    Get the path to pip in the virtual environment.
    
    Args:
        venv_path: Path to the virtual environment
        
    Returns:
        Path to pip executable
    """
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:  # Unix/Linux/Mac
        return os.path.join(venv_path, 'bin', 'pip')


def get_python_path(venv_path: str) -> str:
    """
    Get the path to python in the virtual environment.
    
    Args:
        venv_path: Path to the virtual environment
        
    Returns:
        Path to python executable
    """
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    else:  # Unix/Linux/Mac
        return os.path.join(venv_path, 'bin', 'python')


def install_package(pip_path: str, features: list = None, dev: bool = False, all_features: bool = False) -> bool:
    """
    Install the URL Analyzer package with specified features.
    
    Args:
        pip_path: Path to pip executable
        features: List of features to install
        dev: Whether to install development dependencies
        all_features: Whether to install all optional dependencies
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Upgrade pip
        print("Upgrading pip...")
        subprocess.check_call([pip_path, 'install', '--upgrade', 'pip'])
        
        # Install the package
        print("Installing URL Analyzer...")
        install_args = [pip_path, 'install', '-e', '.']
        
        # Add features if specified
        if all_features:
            install_args.append('[all]')
        elif features:
            extras = ','.join(features)
            if dev:
                extras += ',dev'
            install_args.append(f'[{extras}]')
        elif dev:
            install_args.append('[dev]')
        
        subprocess.check_call(install_args)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing package: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def print_activation_instructions(venv_path: str) -> None:
    """
    Print instructions for activating the virtual environment.
    
    Args:
        venv_path: Path to the virtual environment
    """
    print("\nInstallation complete!")
    print("\nTo activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        print(f"    {venv_path}\\Scripts\\activate.bat")
    else:  # Unix/Linux/Mac
        print(f"    source {venv_path}/bin/activate")
    
    print("\nTo run URL Analyzer:")
    print("    url-analyzer --help")
    print("\nTo check dependencies:")
    print("    url-analyzer-check-dependencies")
    print("\nTo check features:")
    print("    url-analyzer-check-features")


def main():
    """Main function to run the installer."""
    parser = argparse.ArgumentParser(description='URL Analyzer Installer')
    parser.add_argument('--features', type=str,
                        help='Comma-separated list of features to install')
    parser.add_argument('--venv', type=str, default='.venv',
                        help='Path to create virtual environment')
    parser.add_argument('--dev', action='store_true',
                        help='Install development dependencies')
    parser.add_argument('--all', action='store_true',
                        help='Install all optional dependencies')
    
    args = parser.parse_args()
    
    # Parse features
    features = None
    if args.features:
        features = [f.strip() for f in args.features.split(',')]
    
    # Create virtual environment
    venv_path = args.venv
    if not create_virtual_environment(venv_path):
        sys.exit(1)
    
    # Get pip path
    pip_path = get_pip_path(venv_path)
    
    # Install package
    if not install_package(pip_path, features, args.dev, args.all):
        sys.exit(1)
    
    # Print activation instructions
    print_activation_instructions(venv_path)


if __name__ == "__main__":
    main()