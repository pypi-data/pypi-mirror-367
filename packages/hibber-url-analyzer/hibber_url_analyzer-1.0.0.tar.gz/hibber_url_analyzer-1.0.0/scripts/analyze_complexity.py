#!/usr/bin/env python
"""
Code Complexity Analysis Script for URL Analyzer.

This script analyzes the codebase for complexity metrics using radon and generates
a report with complexity scores, maintainability index, and technical debt indicators.
It can be used as part of the CI/CD pipeline or run manually to track code quality.
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import radon.complexity as radon_cc
    import radon.metrics as radon_metrics
    import radon.raw as radon_raw
    from radon.cli import Config
    from radon.cli.harvest import CCHarvester, RawHarvester, MIHarvester
except ImportError:
    print("Error: radon package is required. Install it with 'pip install radon'.")
    sys.exit(1)

# Default configuration
DEFAULT_CONFIG = {
    "exclude": [
        "tests/*",
        "test_*.py",
        "*/migrations/*",
        "setup.py",
        "docs/*",
        "scripts/*",
        "examples/*",
        "*.md",
        "*.json",
        "*.yml",
        "*.yaml",
        "*.ini",
        "*.toml",
    ],
    "include": ["*.py"],
    "min_threshold": "B",  # Minimum complexity rank to report (A, B, C, D, E, F)
    "max_threshold": "C",  # Maximum acceptable complexity rank (above this is considered technical debt)
    "output_file": "complexity_report.json",
    "history_file": "complexity_history.json",
    "max_history": 10,  # Number of historical reports to keep
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze code complexity metrics")
    parser.add_argument(
        "--path",
        type=str,
        default="url_analyzer",
        help="Path to the directory to analyze (default: url_analyzer)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: use built-in config)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output file (default: complexity_report.json)",
    )
    parser.add_argument(
        "--history",
        type=str,
        default=None,
        help="Path to history file (default: complexity_history.json)",
    )
    parser.add_argument(
        "--threshold",
        type=str,
        default=None,
        choices=["A", "B", "C", "D", "E", "F"],
        help="Maximum acceptable complexity rank (default: C)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed output"
    )
    parser.add_argument(
        "--ci-mode", action="store_true", help="Run in CI mode (exit with error if thresholds exceeded)"
    )
    return parser.parse_args()


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or use default."""
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    return config


def analyze_complexity(path: str, config: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """Analyze code complexity using radon."""
    # Create radon config
    radon_config = Config(
        exclude=config["exclude"],
        ignore=None,
        order=True,
        no_assert=False,
        show_closures=False,
        min=config["min_threshold"],
        max=config["max_threshold"],
        show_complexity=True,
        average=True,
        total_average=True,
        show_mi=True,
        multi=True,
    )
    
    # Get file paths
    file_paths = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Check if file should be excluded
                exclude_file = False
                for pattern in config["exclude"]:
                    if pattern.startswith("*"):
                        if file.endswith(pattern[1:]):
                            exclude_file = True
                            break
                    elif pattern.endswith("*"):
                        if file_path.startswith(os.path.join(os.getcwd(), pattern[:-1])):
                            exclude_file = True
                            break
                    elif pattern in file_path:
                        exclude_file = True
                        break
                
                if not exclude_file:
                    file_paths.append(file_path)
    
    if verbose:
        print(f"Analyzing {len(file_paths)} Python files...")
    
    # Analyze cyclomatic complexity
    cc_harvester = CCHarvester(file_paths, radon_config)
    cc_results = cc_harvester.results
    
    # Analyze raw metrics
    raw_harvester = RawHarvester(file_paths, radon_config)
    raw_results = raw_harvester.results
    
    # Analyze maintainability index
    mi_harvester = MIHarvester(file_paths, radon_config)
    mi_results = mi_harvester.results
    
    # Process results
    complexity_data = {}
    total_complexity = 0
    file_count = 0
    complexity_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    
    for file_path, blocks in cc_results:
        rel_path = os.path.relpath(file_path)
        complexity_data[rel_path] = {
            "functions": [],
            "complexity": 0,
            "maintainability": 0,
            "loc": 0,
            "lloc": 0,
            "comments": 0,
        }
        
        # Add function complexity
        file_complexity = 0
        for block in blocks:
            rank = block.letter_rank()
            complexity_counts[rank] += 1
            
            function_data = {
                "name": block.name,
                "line": block.lineno,
                "complexity": block.complexity,
                "rank": rank,
            }
            complexity_data[rel_path]["functions"].append(function_data)
            file_complexity += block.complexity
        
        complexity_data[rel_path]["complexity"] = file_complexity
        total_complexity += file_complexity
        file_count += 1
        
        # Add raw metrics
        for raw_path, raw_data in raw_results:
            if raw_path == file_path:
                complexity_data[rel_path]["loc"] = raw_data.loc
                complexity_data[rel_path]["lloc"] = raw_data.lloc
                complexity_data[rel_path]["comments"] = raw_data.comments
        
        # Add maintainability index
        for mi_path, mi_data in mi_results:
            if mi_path == file_path:
                complexity_data[rel_path]["maintainability"] = mi_data
    
    # Calculate summary
    avg_complexity = total_complexity / file_count if file_count > 0 else 0
    technical_debt_count = sum(complexity_counts[rank] for rank in ["D", "E", "F"])
    technical_debt_percentage = (technical_debt_count / sum(complexity_counts.values())) * 100 if sum(complexity_counts.values()) > 0 else 0
    
    summary = {
        "total_files": file_count,
        "total_functions": sum(complexity_counts.values()),
        "average_complexity": avg_complexity,
        "complexity_distribution": complexity_counts,
        "technical_debt_count": technical_debt_count,
        "technical_debt_percentage": technical_debt_percentage,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    
    return {
        "summary": summary,
        "files": complexity_data,
    }


def update_history(report: Dict[str, Any], history_file: str, max_history: int) -> None:
    """Update the history file with the new report."""
    history = []
    
    # Load existing history if available
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception as e:
            print(f"Error loading history file: {e}")
    
    # Add new report summary
    history.append(report["summary"])
    
    # Keep only the most recent reports
    if len(history) > max_history:
        history = history[-max_history:]
    
    # Save updated history
    try:
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history file: {e}")


def print_report(report: Dict[str, Any], verbose: bool = False) -> None:
    """Print the complexity report to the console."""
    summary = report["summary"]
    
    print("\n=== Code Complexity Report ===")
    print(f"Total files analyzed: {summary['total_files']}")
    print(f"Total functions/methods: {summary['total_functions']}")
    print(f"Average cyclomatic complexity: {summary['average_complexity']:.2f}")
    print("\nComplexity distribution:")
    for rank, count in summary['complexity_distribution'].items():
        print(f"  {rank}: {count}")
    
    print(f"\nTechnical debt: {summary['technical_debt_count']} functions ({summary['technical_debt_percentage']:.2f}%)")
    
    if verbose:
        print("\nTop 10 most complex functions:")
        all_functions = []
        for file_path, file_data in report["files"].items():
            for func in file_data["functions"]:
                all_functions.append((file_path, func))
        
        # Sort by complexity (descending)
        all_functions.sort(key=lambda x: x[1]["complexity"], reverse=True)
        
        for i, (file_path, func) in enumerate(all_functions[:10]):
            print(f"  {i+1}. {func['name']} ({file_path}:{func['line']}) - Complexity: {func['complexity']} (Rank {func['rank']})")


def check_thresholds(report: Dict[str, Any], max_threshold: str) -> Tuple[bool, List[str]]:
    """Check if the code meets the complexity thresholds."""
    threshold_ranks = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}
    max_threshold_value = threshold_ranks[max_threshold]
    
    violations = []
    for file_path, file_data in report["files"].items():
        for func in file_data["functions"]:
            if threshold_ranks[func["rank"]] > max_threshold_value:
                violations.append(
                    f"{func['name']} ({file_path}:{func['line']}) - Complexity: {func['complexity']} (Rank {func['rank']})"
                )
    
    return len(violations) == 0, violations


def main() -> int:
    """Main function."""
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.output:
        config["output_file"] = args.output
    if args.history:
        config["history_file"] = args.history
    if args.threshold:
        config["max_threshold"] = args.threshold
    
    # Analyze code complexity
    report = analyze_complexity(args.path, config, args.verbose)
    
    # Print report
    print_report(report, args.verbose)
    
    # Save report
    try:
        with open(config["output_file"], "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {config['output_file']}")
    except Exception as e:
        print(f"Error saving report: {e}")
    
    # Update history
    update_history(report, config["history_file"], config["max_history"])
    print(f"History updated in {config['history_file']}")
    
    # Check thresholds
    passed, violations = check_thresholds(report, config["max_threshold"])
    
    if not passed:
        print(f"\nWARNING: {len(violations)} functions exceed the maximum complexity threshold ({config['max_threshold']})")
        if args.verbose:
            print("\nViolations:")
            for violation in violations[:10]:  # Show only the first 10 violations
                print(f"  - {violation}")
            if len(violations) > 10:
                print(f"  ... and {len(violations) - 10} more")
        
        if args.ci_mode:
            print("\nCI check failed: Complexity thresholds exceeded")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())