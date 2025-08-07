#!/usr/bin/env python3
"""
Pre-commit setup script for URL Analyzer project.

This script helps developers set up pre-commit hooks for the project.
It installs pre-commit, installs the hooks, and provides helpful information.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def run_command(command: list, description: str) -> bool:
    """
    Run a command and return whether it was successful.
    
    Args:
        command: Command to run as a list
        description: Description of what the command does
        
    Returns:
        True if command was successful, False otherwise
    """
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(command)}")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} failed: Command not found")
        return False

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ is required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor} is compatible")
    return True

def check_git_repository() -> bool:
    """Check if we're in a git repository."""
    if not Path('.git').exists():
        print("❌ This script must be run from the root of a git repository")
        return False
    print("✅ Git repository detected")
    return True

def install_precommit() -> bool:
    """Install pre-commit using pip."""
    # Check if pre-commit is already installed
    if shutil.which('pre-commit'):
        print("✅ pre-commit is already installed")
        return True
    
    # Try to install pre-commit
    return run_command(
        [sys.executable, '-m', 'pip', 'install', 'pre-commit'],
        "Installing pre-commit"
    )

def install_precommit_hooks() -> bool:
    """Install the pre-commit hooks."""
    return run_command(
        ['pre-commit', 'install'],
        "Installing pre-commit hooks"
    )

def install_commit_msg_hook() -> bool:
    """Install the commit message hook."""
    return run_command(
        ['pre-commit', 'install', '--hook-type', 'commit-msg'],
        "Installing commit message hook"
    )

def run_precommit_on_all_files() -> bool:
    """Run pre-commit on all files to check everything is working."""
    print("🔄 Running pre-commit on all files (this may take a while)...")
    try:
        result = subprocess.run(
            ['pre-commit', 'run', '--all-files'],
            check=False,  # Don't fail if pre-commit finds issues
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ All pre-commit checks passed!")
            return True
        else:
            print("⚠️ Pre-commit found some issues that need to be fixed:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            print("\n💡 Don't worry! These issues can be fixed automatically on your next commit.")
            return True  # This is expected for the first run
            
    except FileNotFoundError:
        print("❌ pre-commit command not found")
        return False

def create_precommit_config_if_missing() -> bool:
    """Create .pre-commit-config.yaml if it doesn't exist."""
    config_path = Path('.pre-commit-config.yaml')
    if config_path.exists():
        print("✅ .pre-commit-config.yaml already exists")
        return True
    
    print("❌ .pre-commit-config.yaml not found")
    print("   Please ensure the .pre-commit-config.yaml file exists in the project root")
    return False

def setup_development_dependencies() -> bool:
    """Install development dependencies that are used by pre-commit hooks."""
    dev_packages = [
        'black',
        'isort', 
        'flake8',
        'mypy',
        'bandit',
        'safety'
    ]
    
    print("🔄 Installing development dependencies...")
    for package in dev_packages:
        success = run_command(
            [sys.executable, '-m', 'pip', 'install', package],
            f"Installing {package}"
        )
        if not success:
            print(f"⚠️ Failed to install {package}, but continuing...")
    
    return True

def print_usage_instructions():
    """Print instructions for using pre-commit."""
    print("\n" + "="*60)
    print("🎉 Pre-commit setup completed successfully!")
    print("="*60)
    print("\n📋 What happens now:")
    print("   • Pre-commit hooks will run automatically on every commit")
    print("   • Code will be automatically formatted and checked")
    print("   • Commits will be blocked if there are serious issues")
    print("\n🔧 Useful commands:")
    print("   • Run hooks manually:     pre-commit run --all-files")
    print("   • Update hook versions:   pre-commit autoupdate")
    print("   • Skip hooks (emergency): git commit --no-verify")
    print("   • Check specific files:   pre-commit run --files file1.py file2.py")
    print("\n💡 Tips:")
    print("   • Hooks will fix many issues automatically (formatting, imports)")
    print("   • Review changes before committing to understand what was fixed")
    print("   • If a hook fails, fix the issue and commit again")
    print("   • Use 'git add .' after hooks make changes, then commit again")
    print("\n📚 More info: https://pre-commit.com/")

def main():
    """Main setup function."""
    print("URL Analyzer - Pre-commit Setup")
    print("="*40)
    
    # Check prerequisites
    if not check_python_version():
        return 1
        
    if not check_git_repository():
        return 1
        
    if not create_precommit_config_if_missing():
        return 1
    
    # Install pre-commit
    if not install_precommit():
        return 1
    
    # Install development dependencies
    setup_development_dependencies()
    
    # Install hooks
    if not install_precommit_hooks():
        return 1
        
    if not install_commit_msg_hook():
        print("⚠️ Commit message hook installation failed, but continuing...")
    
    # Test the setup
    if not run_precommit_on_all_files():
        print("⚠️ Initial pre-commit run had issues, but setup is complete")
    
    # Print usage instructions
    print_usage_instructions()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())