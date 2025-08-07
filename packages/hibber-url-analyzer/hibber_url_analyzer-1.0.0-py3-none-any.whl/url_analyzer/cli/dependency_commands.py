"""
Dependency Commands Module

This module provides command-line interface commands for checking and managing dependencies.
"""

import argparse
import sys
from typing import List, Optional, Dict, Any

from url_analyzer.utils.dependency_checker import (
    check_all_dependencies,
    print_dependency_status,
    get_dependency_report,
    is_feature_available,
    get_missing_dependencies_for_feature,
    FEATURE_DEPENDENCIES,
    DEPENDENCY_GROUPS
)
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


def add_dependency_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    Add dependency-related commands to the argument parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    # Add dependency command
    dependency_parser = subparsers.add_parser(
        'dependencies',
        help='Check and manage dependencies'
    )
    
    # Add dependency subcommands
    dependency_subparsers = dependency_parser.add_subparsers(
        dest='dependency_command',
        help='Dependency command'
    )
    
    # Add check command
    check_parser = dependency_subparsers.add_parser(
        'check',
        help='Check dependency status'
    )
    check_parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Add feature command
    feature_parser = dependency_subparsers.add_parser(
        'feature',
        help='Check if a feature is available'
    )
    feature_parser.add_argument(
        'feature',
        help='Feature to check'
    )
    
    # Add list command
    list_parser = dependency_subparsers.add_parser(
        'list',
        help='List available features and their dependencies'
    )
    list_parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Add install command
    install_parser = dependency_subparsers.add_parser(
        'install',
        help='Generate pip install command for missing dependencies'
    )
    install_parser.add_argument(
        'feature',
        nargs='?',
        help='Feature to install dependencies for (if not specified, all dependencies will be included)'
    )
    install_parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the pip install command'
    )


def handle_dependency_command(args: argparse.Namespace) -> None:
    """
    Handle dependency-related commands.
    
    Args:
        args: Command-line arguments
    """
    if not hasattr(args, 'dependency_command') or args.dependency_command is None:
        print("Error: No dependency command specified.")
        print("Run 'url_analyzer dependencies --help' for usage information.")
        return
    
    if args.dependency_command == 'check':
        handle_check_command(args)
    elif args.dependency_command == 'feature':
        handle_feature_command(args)
    elif args.dependency_command == 'list':
        handle_list_command(args)
    elif args.dependency_command == 'install':
        handle_install_command(args)
    else:
        print(f"Error: Unknown dependency command: {args.dependency_command}")


def handle_check_command(args: argparse.Namespace) -> None:
    """
    Handle the 'check' command.
    
    Args:
        args: Command-line arguments
    """
    if args.format == 'text':
        print_dependency_status()
    elif args.format == 'json':
        import json
        report = get_dependency_report()
        print(json.dumps(report, indent=2))


def handle_feature_command(args: argparse.Namespace) -> None:
    """
    Handle the 'feature' command.
    
    Args:
        args: Command-line arguments
    """
    feature = args.feature
    
    if feature not in FEATURE_DEPENDENCIES:
        print(f"Error: Unknown feature: {feature}")
        print(f"Available features: {', '.join(FEATURE_DEPENDENCIES.keys())}")
        return
    
    available = is_feature_available(feature)
    
    if available:
        print(f"Feature '{feature}' is available.")
    else:
        missing_deps = get_missing_dependencies_for_feature(feature)
        print(f"Feature '{feature}' is not available.")
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print(f"Install them with: pip install {' '.join(missing_deps)}")


def handle_list_command(args: argparse.Namespace) -> None:
    """
    Handle the 'list' command.
    
    Args:
        args: Command-line arguments
    """
    if args.format == 'text':
        print("\nAvailable Features and Dependencies:")
        print("----------------------------------")
        
        for feature, dep_groups in FEATURE_DEPENDENCIES.items():
            available = is_feature_available(feature)
            status = "✓ Available" if available else "✗ Missing dependencies"
            
            print(f"\n{feature.replace('_', ' ').title()} ({status}):")
            
            # List dependency groups
            for group in dep_groups:
                if group in DEPENDENCY_GROUPS:
                    deps = DEPENDENCY_GROUPS[group]
                    print(f"  - {group.replace('_', ' ').title()}:")
                    
                    for dep in deps:
                        dep_available = dep in get_dependency_report()["dependencies"].get(group, {})
                        dep_status = "✓ Available" if dep_available else "✗ Missing"
                        print(f"    - {dep}: {dep_status}")
        
        print()
    elif args.format == 'json':
        import json
        
        feature_info = {}
        for feature, dep_groups in FEATURE_DEPENDENCIES.items():
            deps_by_group = {}
            for group in dep_groups:
                if group in DEPENDENCY_GROUPS:
                    deps_by_group[group] = DEPENDENCY_GROUPS[group]
            
            feature_info[feature] = {
                "available": is_feature_available(feature),
                "dependency_groups": deps_by_group,
                "missing_dependencies": get_missing_dependencies_for_feature(feature)
            }
        
        print(json.dumps(feature_info, indent=2))


def handle_install_command(args: argparse.Namespace) -> None:
    """
    Handle the 'install' command.
    
    Args:
        args: Command-line arguments
    """
    feature = args.feature
    
    if feature is not None and feature not in FEATURE_DEPENDENCIES:
        print(f"Error: Unknown feature: {feature}")
        print(f"Available features: {', '.join(FEATURE_DEPENDENCIES.keys())}")
        return
    
    # Get missing dependencies
    missing_deps = []
    if feature is not None:
        missing_deps = get_missing_dependencies_for_feature(feature)
    else:
        # Get all missing dependencies
        for feature in FEATURE_DEPENDENCIES:
            missing_deps.extend(get_missing_dependencies_for_feature(feature))
        
        # Remove duplicates
        missing_deps = list(set(missing_deps))
    
    if not missing_deps:
        if feature is not None:
            print(f"All dependencies for feature '{feature}' are already installed.")
        else:
            print("All dependencies are already installed.")
        return
    
    # Generate pip install command
    pip_command = f"pip install {' '.join(missing_deps)}"
    
    if args.execute:
        import subprocess
        
        print(f"Executing: {pip_command}")
        try:
            subprocess.check_call(pip_command.split())
            print("Dependencies installed successfully.")
            
            # Re-check dependencies
            check_all_dependencies()
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
    else:
        print("To install missing dependencies, run:")
        print(f"  {pip_command}")
        
        if feature is not None:
            print(f"\nOr run: url_analyzer dependencies install {feature} --execute")
        else:
            print("\nOr run: url_analyzer dependencies install --execute")


def main() -> None:
    """
    Main function for running the dependency commands directly.
    """
    parser = argparse.ArgumentParser(description='URL Analyzer Dependency Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    add_dependency_commands(subparsers)
    
    args = parser.parse_args()
    
    if args.command == 'dependencies':
        handle_dependency_command(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()