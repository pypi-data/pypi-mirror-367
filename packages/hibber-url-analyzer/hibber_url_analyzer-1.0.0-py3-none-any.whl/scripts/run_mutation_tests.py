#!/usr/bin/env python
"""
Script to run mutation tests on the URL Analyzer codebase.

This script uses the mutmut library to perform mutation testing, which helps
identify weaknesses in the test suite by making small changes to the code and
checking if the tests catch these changes.

Usage:
    python scripts/run_mutation_tests.py [options]

Options:
    --target-file=FILE    Run mutation tests only on the specified file
    --show-results        Show detailed results after running
    --rerun-only          Rerun only previously failing mutations
    --help                Show this help message
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Ensure the script can be run from any directory
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run mutation tests on URL Analyzer")
    parser.add_argument("--target-file", help="Run mutation tests only on the specified file")
    parser.add_argument("--show-results", action="store_true", help="Show detailed results after running")
    parser.add_argument("--rerun-only", action="store_true", help="Rerun only previously failing mutations")
    return parser.parse_args()

def run_mutation_tests(target_file=None, rerun_only=False):
    """Run mutation tests using mutmut."""
    print("Running mutation tests...")
    
    # Base command
    cmd = ["python", "-m", "mutmut", "run", "--config-file", "mutmut_config.py"]
    
    # Add target file if specified
    if target_file:
        cmd.extend(["--paths", target_file])
    
    # Rerun only previously failing mutations if requested
    if rerun_only:
        cmd.append("--rerun-only")
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Mutation tests completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running mutation tests: {e}")
        return False

def show_mutation_results():
    """Show detailed mutation test results."""
    print("\nMutation test results:")
    
    # Run mutmut results command
    try:
        subprocess.run(["python", "-m", "mutmut", "results"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error showing results: {e}")
        return False
    
    # Try to load and analyze the results file
    try:
        with open(".mutmut-cache", "r") as f:
            results = json.load(f)
        
        total = len(results)
        killed = sum(1 for r in results.values() if r.get("status") == "killed")
        survived = sum(1 for r in results.values() if r.get("status") == "survived")
        timeout = sum(1 for r in results.values() if r.get("status") == "timeout")
        
        print(f"\nSummary:")
        print(f"  Total mutations: {total}")
        killed_pct = (killed/total*100) if total > 0 else 0
        survived_pct = (survived/total*100) if total > 0 else 0
        timeout_pct = (timeout/total*100) if total > 0 else 0
        print(f"  Killed: {killed} ({killed_pct:.1f}%)")
        print(f"  Survived: {survived} ({survived_pct:.1f}%)")
        print(f"  Timeout: {timeout} ({timeout_pct:.1f}%)")
        
        if survived > 0:
            print("\nSurvived mutations (tests didn't catch these):")
            for id, data in results.items():
                if data.get("status") == "survived":
                    print(f"  Mutation {id}: {data.get('file')}:{data.get('line')}")
        
        return True
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error analyzing results: {e}")
        return False

def main():
    """Main function."""
    args = parse_args()
    
    # Run the mutation tests
    success = run_mutation_tests(args.target_file, args.rerun_only)
    
    # Show results if requested or if tests were successful
    if args.show_results or success:
        show_mutation_results()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())