#!/usr/bin/env python
"""
Technical Debt Tracking Script for URL Analyzer.

This script identifies, tracks, and reports on technical debt in the codebase.
It uses various metrics and indicators to quantify technical debt and provides
actionable insights for debt reduction.
"""

import os
import sys
import json
import argparse
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

try:
    import radon.complexity as radon_cc
    from radon.cli import Config
    from radon.cli.harvest import CCHarvester, MIHarvester
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
    "complexity_threshold": "C",  # Complexity above this is considered debt
    "maintainability_threshold": 65,  # MI below this is considered debt
    "todo_patterns": [
        r"TODO",
        r"FIXME",
        r"HACK",
        r"XXX",
        r"BUG",
        r"REFACTOR",
        r"OPTIMIZE",
    ],
    "output_file": "technical_debt_report.json",
    "history_file": "technical_debt_history.json",
    "max_history": 10,  # Number of historical reports to keep
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Track technical debt in the codebase")
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
        help="Path to output file (default: technical_debt_report.json)",
    )
    parser.add_argument(
        "--history",
        type=str,
        default=None,
        help="Path to history file (default: technical_debt_history.json)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed output"
    )
    parser.add_argument(
        "--ci-mode", action="store_true", help="Run in CI mode (exit with error if debt exceeds threshold)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Maximum acceptable debt score (default: use built-in threshold)",
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


def find_files(path: str, config: Dict[str, Any], verbose: bool = False) -> List[str]:
    """Find Python files to analyze."""
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
        print(f"Found {len(file_paths)} Python files to analyze")
    
    return file_paths


def analyze_complexity(file_paths: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze code complexity using radon."""
    # Create radon config
    radon_config = Config(
        exclude=config["exclude"],
        ignore=None,
        order=True,
        no_assert=False,
        show_closures=False,
        min="A",  # Include all complexity ranks
        max="F",
        show_complexity=True,
        average=True,
        total_average=True,
        show_mi=True,
        multi=True,
    )
    
    # Analyze cyclomatic complexity
    cc_harvester = CCHarvester(file_paths, radon_config)
    cc_results = cc_harvester.results
    
    # Analyze maintainability index
    mi_harvester = MIHarvester(file_paths, radon_config)
    mi_results = mi_harvester.results
    
    # Process results
    complexity_data = {}
    threshold_ranks = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}
    complexity_threshold = threshold_ranks[config["complexity_threshold"]]
    
    for file_path, blocks in cc_results:
        rel_path = os.path.relpath(file_path)
        complexity_data[rel_path] = {
            "complex_functions": [],
            "maintainability": 0,
            "debt_score": 0,
        }
        
        # Find complex functions
        for block in blocks:
            rank = block.letter_rank()
            if threshold_ranks[rank] > complexity_threshold:
                function_data = {
                    "name": block.name,
                    "line": block.lineno,
                    "complexity": block.complexity,
                    "rank": rank,
                }
                complexity_data[rel_path]["complex_functions"].append(function_data)
        
        # Add maintainability index
        for mi_path, mi_data in mi_results:
            if mi_path == file_path:
                complexity_data[rel_path]["maintainability"] = mi_data
                # Calculate debt score based on maintainability
                if mi_data < config["maintainability_threshold"]:
                    # Lower MI means more debt
                    mi_debt = (config["maintainability_threshold"] - mi_data) / 10
                    complexity_data[rel_path]["debt_score"] += mi_debt
        
        # Add debt score based on complex functions
        if complexity_data[rel_path]["complex_functions"]:
            # More complex functions mean more debt
            func_debt = sum(
                threshold_ranks[func["rank"]] - complexity_threshold
                for func in complexity_data[rel_path]["complex_functions"]
            )
            complexity_data[rel_path]["debt_score"] += func_debt
    
    return complexity_data


def find_todos(file_paths: List[str], config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Find TODO comments and other debt indicators in the code."""
    todo_data = {}
    
    # Compile regex patterns
    patterns = [re.compile(pattern) for pattern in config["todo_patterns"]]
    
    for file_path in file_paths:
        rel_path = os.path.relpath(file_path)
        todos = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    for pattern in patterns:
                        match = pattern.search(line)
                        if match:
                            # Extract the comment
                            comment = line.strip()
                            # Remove leading comment characters
                            comment = re.sub(r"^\s*#\s*", "", comment)
                            comment = re.sub(r"^\s*\"\"\"\s*", "", comment)
                            comment = re.sub(r"^\s*'''\s*", "", comment)
                            
                            todos.append({
                                "line": i,
                                "text": comment,
                                "type": match.group(0),
                            })
                            break
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        
        if todos:
            todo_data[rel_path] = todos
    
    return todo_data


def analyze_duplication(file_paths: List[str], config: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """Analyze code duplication (simplified version)."""
    # This is a simplified approach to detect potential duplication
    # For a more comprehensive solution, consider using tools like PMD CPD
    
    duplication_data = {}
    function_hashes = {}
    
    for file_path in file_paths:
        rel_path = os.path.relpath(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Extract functions using a simple regex
                # This is a simplified approach and won't catch all functions
                function_pattern = re.compile(r"def\s+(\w+)\s*\(.*?\):\s*(?:\s*\"\"\".*?\"\"\"\s*)?", re.DOTALL)
                for match in function_pattern.finditer(content):
                    func_start = match.start()
                    # Find the end of the function (indentation returns to the same level)
                    lines = content[func_start:].split("\n")
                    func_end = func_start
                    indent = None
                    
                    for i, line in enumerate(lines):
                        if i == 0:
                            continue  # Skip the function definition line
                        
                        # Skip empty lines
                        if not line.strip():
                            func_end += len(line) + 1  # +1 for newline
                            continue
                        
                        # Determine the indentation of the function body
                        if indent is None:
                            indent = len(line) - len(line.lstrip())
                            func_end += len(line) + 1
                            continue
                        
                        # Check if we're back to the original indentation level
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent <= indent and line.strip():
                            break
                        
                        func_end += len(line) + 1
                    
                    # Extract the function body
                    func_body = content[func_start:func_end].strip()
                    
                    # Create a simple hash of the function body
                    # Ignore whitespace and comments for better comparison
                    clean_body = re.sub(r"\s+", "", func_body)
                    clean_body = re.sub(r"#.*$", "", clean_body, flags=re.MULTILINE)
                    func_hash = hash(clean_body)
                    
                    # Store the function information
                    func_name = match.group(1)
                    func_info = {
                        "name": func_name,
                        "file": rel_path,
                        "start_line": content[:func_start].count("\n") + 1,
                        "end_line": content[:func_end].count("\n") + 1,
                        "length": func_end - func_start,
                    }
                    
                    # Check for potential duplication
                    if func_hash in function_hashes:
                        # Only consider functions with substantial content
                        if len(clean_body) > 100:  # Arbitrary threshold
                            if rel_path not in duplication_data:
                                duplication_data[rel_path] = []
                            
                            duplication_data[rel_path].append({
                                "function": func_info,
                                "similar_to": function_hashes[func_hash],
                            })
                    else:
                        function_hashes[func_hash] = func_info
        
        except Exception as e:
            if verbose:
                print(f"Error analyzing duplication in {file_path}: {e}")
    
    return duplication_data


def calculate_debt_score(
    complexity_data: Dict[str, Any],
    todo_data: Dict[str, List[Dict[str, Any]]],
    duplication_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate overall technical debt score."""
    # Initialize debt metrics
    debt_metrics = {
        "complexity_debt": 0,
        "maintainability_debt": 0,
        "todo_debt": 0,
        "duplication_debt": 0,
        "total_debt": 0,
        "debt_by_file": {},
        "worst_files": [],
    }
    
    # Calculate complexity and maintainability debt
    for file_path, data in complexity_data.items():
        file_debt = data["debt_score"]
        debt_metrics["complexity_debt"] += len(data["complex_functions"])
        
        if data["maintainability"] < 65:  # Threshold for maintainability
            debt_metrics["maintainability_debt"] += 1
        
        debt_metrics["debt_by_file"][file_path] = {
            "debt_score": file_debt,
            "complex_functions": len(data["complex_functions"]),
            "maintainability": data["maintainability"],
            "todos": 0,
            "duplication": 0,
        }
    
    # Add TODO debt
    for file_path, todos in todo_data.items():
        todo_count = len(todos)
        debt_metrics["todo_debt"] += todo_count
        
        if file_path in debt_metrics["debt_by_file"]:
            debt_metrics["debt_by_file"][file_path]["todos"] = todo_count
            debt_metrics["debt_by_file"][file_path]["debt_score"] += todo_count * 0.5  # Weight for TODOs
        else:
            debt_metrics["debt_by_file"][file_path] = {
                "debt_score": todo_count * 0.5,
                "complex_functions": 0,
                "maintainability": 100,  # Default good maintainability
                "todos": todo_count,
                "duplication": 0,
            }
    
    # Add duplication debt
    for file_path, duplications in duplication_data.items():
        duplication_count = len(duplications)
        debt_metrics["duplication_debt"] += duplication_count
        
        if file_path in debt_metrics["debt_by_file"]:
            debt_metrics["debt_by_file"][file_path]["duplication"] = duplication_count
            debt_metrics["debt_by_file"][file_path]["debt_score"] += duplication_count * 2  # Weight for duplication
        else:
            debt_metrics["debt_by_file"][file_path] = {
                "debt_score": duplication_count * 2,
                "complex_functions": 0,
                "maintainability": 100,  # Default good maintainability
                "todos": 0,
                "duplication": duplication_count,
            }
    
    # Calculate total debt
    debt_metrics["total_debt"] = (
        debt_metrics["complexity_debt"] +
        debt_metrics["maintainability_debt"] * 2 +  # Weight maintainability higher
        debt_metrics["todo_debt"] * 0.5 +  # Weight TODOs lower
        debt_metrics["duplication_debt"] * 2  # Weight duplication higher
    )
    
    # Find worst files
    sorted_files = sorted(
        debt_metrics["debt_by_file"].items(),
        key=lambda x: x[1]["debt_score"],
        reverse=True,
    )
    debt_metrics["worst_files"] = [
        {"file": file_path, "debt_score": data["debt_score"]}
        for file_path, data in sorted_files[:10]  # Top 10 worst files
    ]
    
    return debt_metrics


def generate_report(
    complexity_data: Dict[str, Any],
    todo_data: Dict[str, List[Dict[str, Any]]],
    duplication_data: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a comprehensive technical debt report."""
    # Calculate debt metrics
    debt_metrics = calculate_debt_score(complexity_data, todo_data, duplication_data)
    
    # Create the report
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "total_debt_score": debt_metrics["total_debt"],
            "complexity_debt": debt_metrics["complexity_debt"],
            "maintainability_debt": debt_metrics["maintainability_debt"],
            "todo_debt": debt_metrics["todo_debt"],
            "duplication_debt": debt_metrics["duplication_debt"],
            "worst_files": debt_metrics["worst_files"],
        },
        "details": {
            "complex_functions": {},
            "low_maintainability_files": {},
            "todos": todo_data,
            "duplications": duplication_data,
        },
    }
    
    # Add complex functions details
    for file_path, data in complexity_data.items():
        if data["complex_functions"]:
            report["details"]["complex_functions"][file_path] = data["complex_functions"]
        
        if data["maintainability"] < config["maintainability_threshold"]:
            report["details"]["low_maintainability_files"][file_path] = data["maintainability"]
    
    return report


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
    history.append({
        "timestamp": report["timestamp"],
        "total_debt_score": report["summary"]["total_debt_score"],
        "complexity_debt": report["summary"]["complexity_debt"],
        "maintainability_debt": report["summary"]["maintainability_debt"],
        "todo_debt": report["summary"]["todo_debt"],
        "duplication_debt": report["summary"]["duplication_debt"],
    })
    
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
    """Print the technical debt report to the console."""
    summary = report["summary"]
    
    print("\n=== Technical Debt Report ===")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total Debt Score: {summary['total_debt_score']:.2f}")
    print(f"Complexity Debt: {summary['complexity_debt']} complex functions")
    print(f"Maintainability Debt: {summary['maintainability_debt']} files with low maintainability")
    print(f"TODO Debt: {summary['todo_debt']} TODO comments")
    print(f"Duplication Debt: {summary['duplication_debt']} potential duplications")
    
    print("\nWorst Files:")
    for i, file_data in enumerate(summary["worst_files"][:5]):  # Show top 5
        print(f"  {i+1}. {file_data['file']} - Debt Score: {file_data['debt_score']:.2f}")
    
    if verbose:
        print("\nComplex Functions:")
        for file_path, functions in report["details"]["complex_functions"].items():
            print(f"\n  {file_path}:")
            for func in functions[:3]:  # Show top 3 per file
                print(f"    - {func['name']} (line {func['line']}) - Complexity: {func['complexity']} (Rank {func['rank']})")
            if len(functions) > 3:
                print(f"    ... and {len(functions) - 3} more")
        
        print("\nLow Maintainability Files:")
        for file_path, mi in report["details"]["low_maintainability_files"].items():
            print(f"  - {file_path} - Maintainability Index: {mi:.2f}")
        
        print("\nTODO Comments:")
        todo_count = 0
        for file_path, todos in report["details"]["todos"].items():
            print(f"\n  {file_path}:")
            for todo in todos[:3]:  # Show top 3 per file
                print(f"    - Line {todo['line']}: {todo['text']}")
            if len(todos) > 3:
                print(f"    ... and {len(todos) - 3} more")
            todo_count += len(todos)
        
        print("\nPotential Duplications:")
        for file_path, duplications in report["details"]["duplications"].items():
            print(f"\n  {file_path}:")
            for dup in duplications[:3]:  # Show top 3 per file
                print(f"    - {dup['function']['name']} (lines {dup['function']['start_line']}-{dup['function']['end_line']})")
                print(f"      Similar to: {dup['similar_to']['name']} in {dup['similar_to']['file']}")
            if len(duplications) > 3:
                print(f"    ... and {len(duplications) - 3} more")


def generate_recommendations(report: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations for reducing technical debt."""
    recommendations = []
    
    # Recommendations based on complex functions
    if report["summary"]["complexity_debt"] > 0:
        recommendations.append(
            "Reduce function complexity by breaking down complex functions into smaller, more focused ones."
        )
        
        # Specific recommendations for the worst complex functions
        complex_files = list(report["details"]["complex_functions"].items())
        if complex_files:
            complex_files.sort(key=lambda x: max(f["complexity"] for f in x[1]), reverse=True)
            worst_file, worst_functions = complex_files[0]
            worst_function = max(worst_functions, key=lambda x: x["complexity"])
            recommendations.append(
                f"Start by refactoring {worst_function['name']} in {worst_file} (complexity: {worst_function['complexity']})."
            )
    
    # Recommendations based on maintainability
    if report["summary"]["maintainability_debt"] > 0:
        recommendations.append(
            "Improve code maintainability by adding better documentation, reducing nesting, and simplifying logic."
        )
        
        # Specific recommendations for the worst maintainability
        low_mi_files = list(report["details"]["low_maintainability_files"].items())
        if low_mi_files:
            low_mi_files.sort(key=lambda x: x[1])
            worst_mi_file, worst_mi = low_mi_files[0]
            recommendations.append(
                f"Focus on improving {worst_mi_file} (maintainability index: {worst_mi:.2f})."
            )
    
    # Recommendations based on TODOs
    if report["summary"]["todo_debt"] > 0:
        recommendations.append(
            "Address technical debt indicated by TODO, FIXME, and similar comments."
        )
        
        # Find the file with the most TODOs
        if report["details"]["todos"]:
            todo_files = [(file, len(todos)) for file, todos in report["details"]["todos"].items()]
            todo_files.sort(key=lambda x: x[1], reverse=True)
            worst_todo_file, todo_count = todo_files[0]
            recommendations.append(
                f"Start by addressing the {todo_count} TODOs in {worst_todo_file}."
            )
    
    # Recommendations based on duplication
    if report["summary"]["duplication_debt"] > 0:
        recommendations.append(
            "Reduce code duplication by extracting common functionality into shared methods or classes."
        )
        
        # Find the file with the most duplications
        if report["details"]["duplications"]:
            dup_files = [(file, len(dups)) for file, dups in report["details"]["duplications"].items()]
            dup_files.sort(key=lambda x: x[1], reverse=True)
            worst_dup_file, dup_count = dup_files[0]
            recommendations.append(
                f"Focus on reducing the {dup_count} potential duplications in {worst_dup_file}."
            )
    
    # General recommendations
    recommendations.append(
        "Regularly monitor technical debt and allocate time in each sprint to address it."
    )
    recommendations.append(
        "Consider implementing a 'boy scout rule': leave the code cleaner than you found it."
    )
    
    return recommendations


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
    
    # Find files to analyze
    file_paths = find_files(args.path, config, args.verbose)
    
    if not file_paths:
        print("No Python files found to analyze")
        return 1
    
    # Analyze code
    if args.verbose:
        print("Analyzing code complexity...")
    complexity_data = analyze_complexity(file_paths, config)
    
    if args.verbose:
        print("Finding TODO comments...")
    todo_data = find_todos(file_paths, config)
    
    if args.verbose:
        print("Analyzing code duplication...")
    duplication_data = analyze_duplication(file_paths, config, args.verbose)
    
    # Generate report
    if args.verbose:
        print("Generating technical debt report...")
    report = generate_report(complexity_data, todo_data, duplication_data, config)
    
    # Print report
    print_report(report, args.verbose)
    
    # Generate and print recommendations
    recommendations = generate_recommendations(report)
    print("\nRecommendations:")
    for i, recommendation in enumerate(recommendations, 1):
        print(f"{i}. {recommendation}")
    
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
    
    # Check threshold
    if args.threshold is not None and report["summary"]["total_debt_score"] > args.threshold:
        print(f"\nWARNING: Technical debt score ({report['summary']['total_debt_score']:.2f}) exceeds threshold ({args.threshold})")
        
        if args.ci_mode:
            print("\nCI check failed: Technical debt threshold exceeded")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())