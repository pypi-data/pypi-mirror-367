"""
Command-line interface for URL Analyzer.

This package contains modules for the command-line interface,
including argument parsing, subcommands, and interactive mode.
"""

from url_analyzer.cli.commands import main as main_cli
from url_analyzer.cli.log_monitor_cli import main as log_monitor_cli
from url_analyzer.cli.credential_cli import main as credential_cli

__all__ = ['main_cli', 'log_monitor_cli', 'credential_cli']