"""
Main entry point for the URL Analyzer package.

This module allows the package to be run as a module with `python -m url_analyzer`.
"""

import sys
from url_analyzer.cli.commands import main

if __name__ == "__main__":
    sys.exit(main())