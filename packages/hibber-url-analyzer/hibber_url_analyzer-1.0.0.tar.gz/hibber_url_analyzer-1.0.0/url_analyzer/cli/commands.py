"""
Command-Line Interface Module

This module provides the command-line interface for the URL Analyzer application,
with support for subcommands, rich help text, and advanced options.
"""

import os
import sys
import argparse
import glob
import webbrowser
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple

# Rich imports for enhanced CLI experience
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich import print as rich_print

# Import from other modules
from url_analyzer.utils.logging import get_logger, setup_logging
from url_analyzer.utils.errors import ValidationError
from url_analyzer.config_manager import load_config, save_config, compile_patterns
from url_analyzer.core.classification import classify_url, get_base_domain
# Temporarily commented out - these functions need to be located in refactored codebase
# from url_analyzer.core.analysis import fetch_url_data, load_cache, save_cache, LIVE_SCAN_CACHE
from url_analyzer.data.processing import process_file, process_files, print_summary
from url_analyzer.data.export import export_data
from url_analyzer.reporting.html_report import (
    list_available_templates, get_template_path
)
from url_analyzer.reporting.generators import (
    ReportGenerator, ReportGeneratorFactory
)
from url_analyzer.cli.dependency_commands import (
    add_dependency_commands, handle_dependency_command
)
from url_analyzer.cli.automation_cli import (
    add_automation_commands, handle_automation_command
)

# Create logger and rich console
logger = get_logger(__name__)
console = Console()


def create_main_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser with global options.
    
    Returns:
        Main argument parser
    """
    parser = argparse.ArgumentParser(
        description="""URL Analyzer - A comprehensive tool for analyzing and categorizing URLs

URL Analyzer is a powerful tool for processing, analyzing, and visualizing URL data.
It can classify URLs based on patterns, fetch content from live URLs, generate
interactive reports, and export data in various formats.

Key Features:
- URL classification based on configurable patterns
- Live URL scanning and content summarization
- Interactive HTML reports with visualizations
- Data export in multiple formats (CSV, JSON, Excel)
- Batch processing for large datasets
- Memory-efficient processing for large files
- Interactive mode with rich terminal UI
- Extensible plugin architecture
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Command Overview:
  analyze      - Process URLs from files and generate reports
  report       - Create reports from previously analyzed data
  export       - Export data to different formats
  configure    - Manage application configuration
  templates    - List and manage report templates
  interactive  - Launch interactive mode with rich terminal UI
  dependencies - Check and manage dependencies

Examples:
  # Launch interactive mode (recommended for new users)
  python -m url_analyzer interactive

  # Analyze a single file
  python -m url_analyzer analyze --path "path/to/file.csv"
  
  # Analyze a file with live scanning and summarization
  python -m url_analyzer analyze --path "path/to/file.csv" --live-scan --summarize
  
  # Analyze all CSV files in a directory and generate an aggregated report
  python -m url_analyzer analyze --path "path/to/directory" --aggregate
  
  # Configure the application
  python -m url_analyzer configure
  
  # Export data to different formats
  python -m url_analyzer export --path "path/to/file.csv" --format json
  
  # Generate a report from a previously analyzed file
  python -m url_analyzer report --path "path/to/file.csv" --template security_focus
  
  # List available report templates
  python -m url_analyzer templates --details

For detailed help on a specific command, use:
  python -m url_analyzer <command> --help
"""
    )
    
    # Add global options
    parser.add_argument('--verbose', '-v', action='count', default=0,
                       help="Increase verbosity (can be used multiple times)")
    parser.add_argument('--quiet', '-q', action='store_true',
                       help="Suppress non-error output")
    parser.add_argument('--log-file', help="Path to log file")
    
    return parser


def add_interactive_command(subparsers) -> None:
    """Add the interactive command parser."""
    interactive_parser = subparsers.add_parser('interactive', 
                                             help='Launch interactive mode with rich terminal UI')
    interactive_parser.add_argument('--no-color', action='store_true',
                                  help="Disable colored output")


def add_analyze_command(subparsers) -> None:
    """Add the analyze command parser with all its options."""
    analyze_parser = subparsers.add_parser('analyze', 
                                         help='Analyze URLs in a file or directory',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description="""
Analyze URLs in a file or directory and generate reports.

This command processes URLs from input files, classifies them based on patterns,
and generates HTML reports with visualizations. It supports various options for
customizing the analysis process and output.

Examples:
  # Basic analysis of a single file
  python -m url_analyzer analyze --path "path/to/file.csv"
  
  # Analyze with live scanning and content summarization
  python -m url_analyzer analyze --path "path/to/file.csv" --live-scan --summarize
  
  # Process all files in a directory with aggregated report
  python -m url_analyzer analyze --path "path/to/directory" --aggregate
  
  # Use a custom template and export to JSON
  python -m url_analyzer analyze --path "path/to/file.csv" --template "security_focus" --export-format json
""")
    
    # Input options
    input_group = analyze_parser.add_argument_group('Input Options')
    input_group.add_argument('--path', required=True,
                           help="Path to a single file or a directory for batch processing")
    input_group.add_argument('--filter', 
                           help="Filter expression for input data (e.g., 'Domain_name=example.com')")
    input_group.add_argument('--include-pattern', 
                           help="Only process files matching this pattern (e.g., '*.csv')")
    input_group.add_argument('--exclude-pattern',
                           help="Skip files matching this pattern (e.g., 'temp_*')")
    
    # Analysis options
    analysis_group = analyze_parser.add_argument_group('Analysis Options')
    analysis_group.add_argument('--live-scan', action='store_true',
                              help="Enable live URL scanning")
    analysis_group.add_argument('--summarize', action='store_true',
                              help="Enable AI content summarization (requires --live-scan)")
    analysis_group.add_argument('--timeout', type=int, default=7,
                              help="Timeout for URL requests in seconds (default: 7)")
    analysis_group.add_argument('--retry', type=int, default=2,
                              help="Number of retry attempts for failed requests (default: 2)")
    analysis_group.add_argument('--user-agent',
                              help="Custom User-Agent string for HTTP requests")
    analysis_group.add_argument('--follow-redirects', action='store_true',
                              help="Follow URL redirects during live scanning")
    analysis_group.add_argument('--max-redirects', type=int, default=5,
                              help="Maximum number of redirects to follow (default: 5)")
    
    # Output options
    output_group = analyze_parser.add_argument_group('Output Options')
    output_group.add_argument('--aggregate', action='store_true',
                            help="Generate a single aggregated report for a directory")
    output_group.add_argument('--output', '-o',
                            help="Output directory for reports (default: same as input)")
    output_group.add_argument('--template',
                            help="Template to use for report generation")
    output_group.add_argument('--no-open', action='store_true',
                            help="Don't open the report in a browser after generation")
    output_group.add_argument('--export-format',
                            choices=['csv', 'json', 'excel'],
                            help="Export analyzed data to the specified format")
    output_group.add_argument('--report-title',
                            help="Custom title for the generated report")
    output_group.add_argument('--include-summary', action='store_true', default=True,
                            help="Include summary statistics in the report (default: True)")
    output_group.add_argument('--no-summary', action='store_false', dest='include_summary',
                            help="Exclude summary statistics from the report")
    
    # Batch processing options
    batch_group = analyze_parser.add_argument_group('Batch Processing Options')
    batch_group.add_argument('--job-id',
                           help="Unique identifier for the batch job (default: timestamp)")
    batch_group.add_argument('--max-workers', type=int,
                           help="Maximum number of worker threads for parallel processing")
    batch_group.add_argument('--checkpoint-interval', type=int, default=5,
                           help="Interval for saving checkpoints in minutes (default: 5)")
    batch_group.add_argument('--resume', action='store_true',
                           help="Resume processing from the last checkpoint")
    batch_group.add_argument('--skip-errors', action='store_true',
                           help="Continue processing even if some files have errors")
    
    # Memory optimization options
    memory_group = analyze_parser.add_argument_group('Memory Optimization Options')
    memory_group.add_argument('--chunked', action='store_true',
                            help="Enable chunked processing for large files")
    memory_group.add_argument('--no-chunked', action='store_false', dest='chunked',
                            help="Disable chunked processing (load entire file)")
    memory_group.add_argument('--chunk-size', type=int, default=10000,
                            help="Number of rows to process in each chunk (default: 10000)")
    memory_group.add_argument('--low-memory', action='store_true',
                            help="Optimize for low memory usage (slower but uses less RAM)")
    memory_group.add_argument('--cache-dir',
                            help="Directory for caching results (default: system temp directory)")


def add_configure_command(subparsers) -> None:
    """Add the configure command parser with all its options."""
    configure_parser = subparsers.add_parser('configure', 
                                           help='Configure the application',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description="""
Configure the URL Analyzer application.

This command provides an interface for managing the application's configuration,
including URL classification patterns, API settings, and scan settings. It supports
both interactive configuration and command-line options.

Examples:
  # Enter interactive configuration mode
  python -m url_analyzer configure
  
  # Reset configuration to defaults
  python -m url_analyzer configure --reset
  
  # Use a specific configuration file
  python -m url_analyzer configure --config-file "path/to/config.json"
  
  # Set a specific configuration value
  python -m url_analyzer configure --set "scan_settings.max_workers=30"
""")
    
    # Basic options
    basic_group = configure_parser.add_argument_group('Basic Options')
    basic_group.add_argument('--reset', action='store_true',
                           help="Reset configuration to defaults")
    basic_group.add_argument('--config-file',
                           help="Path to configuration file")
    basic_group.add_argument('--show', action='store_true',
                           help="Show current configuration")
    basic_group.add_argument('--export',
                           help="Export configuration to a file")
    basic_group.add_argument('--import',
                           dest='import_file',
                           help="Import configuration from a file")
    
    # Configuration options
    config_group = configure_parser.add_argument_group('Configuration Options')
    config_group.add_argument('--set',
                            help="Set a configuration value (format: key=value)")
    config_group.add_argument('--get',
                            help="Get a configuration value (format: key)")
    config_group.add_argument('--add-pattern',
                            help="Add a pattern to a category (format: category:pattern)")
    config_group.add_argument('--remove-pattern',
                            help="Remove a pattern from a category (format: category:pattern)")
    config_group.add_argument('--list-patterns',
                            choices=['sensitive', 'ugc', 'junk', 'all'],
                            help="List patterns for a specific category")
    
    # API settings
    api_group = configure_parser.add_argument_group('API Settings')
    api_group.add_argument('--set-api-url',
                         help="Set the API URL for content summarization")
    api_group.add_argument('--set-api-key',
                         help="Set the API key for content summarization (use credential manager for better security)")
    api_group.add_argument('--test-api', action='store_true',
                         help="Test the API connection")
    
    # Scan settings
    scan_group = configure_parser.add_argument_group('Scan Settings')
    scan_group.add_argument('--set-max-workers', type=int,
                          help="Set the maximum number of worker threads for parallel processing")
    scan_group.add_argument('--set-timeout', type=int,
                          help="Set the timeout for URL requests in seconds")
    scan_group.add_argument('--set-cache-file',
                          help="Set the cache file path for scan results")
    scan_group.add_argument('--clear-cache', action='store_true',
                          help="Clear the scan cache")
    
    # Advanced options
    advanced_group = configure_parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--validate', action='store_true',
                              help="Validate the configuration file")
    advanced_group.add_argument('--backup', action='store_true',
                              help="Create a backup of the current configuration")
    advanced_group.add_argument('--restore',
                              help="Restore configuration from a backup file")
    advanced_group.add_argument('--no-interactive', action='store_true',
                              help="Disable interactive mode for configuration")


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser with subcommands.
    
    Returns:
        Configured argument parser
    """
    # Create the main parser
    parser = create_main_parser()
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add dependency commands
    add_dependency_commands(subparsers)
    
    # Add automation commands
    add_automation_commands(subparsers)
    
    # Add individual command parsers
    add_interactive_command(subparsers)
    add_analyze_command(subparsers)
    add_configure_command(subparsers)
    
    # Export command
    export_parser = subparsers.add_parser('export', 
                                        help='Export data to different formats',
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description="""
Export analyzed data to different formats.

This command exports data from analyzed files to various formats for further
processing or integration with other tools. It supports filtering to export
only specific subsets of the data.

Examples:
  # Export to CSV format
  python -m url_analyzer export --path "path/to/file.csv" --format csv
  
  # Export to JSON with a filter
  python -m url_analyzer export --path "path/to/file.csv" --format json --filter "URL_Category=Advertising"
  
  # Export to Excel with a custom output path
  python -m url_analyzer export --path "path/to/file.csv" --format excel --output "path/to/output.xlsx"
""")
    
    # Input options
    input_group = export_parser.add_argument_group('Input Options')
    input_group.add_argument('--path', required=True,
                           help="Path to the file to export")
    input_group.add_argument('--filter',
                           help="Filter expression (e.g., 'URL_Category=Advertising')")
    input_group.add_argument('--columns',
                           help="Comma-separated list of columns to include (default: all columns)")
    input_group.add_argument('--sort-by',
                           help="Column to sort by (default: no sorting)")
    input_group.add_argument('--sort-order', choices=['asc', 'desc'], default='asc',
                           help="Sort order: ascending (asc) or descending (desc) (default: asc)")
    
    # Export options
    export_group = export_parser.add_argument_group('Export Options')
    export_group.add_argument('--format', required=True,
                            choices=['csv', 'json', 'excel'],
                            help="Export format")
    export_group.add_argument('--output', '-o',
                            help="Output file path (default: input file with new extension)")
    export_group.add_argument('--encoding', default='utf-8',
                            help="Character encoding for output file (default: utf-8)")
    export_group.add_argument('--compression', choices=['none', 'gzip', 'zip'],
                            default='none',
                            help="Compression format for output file (default: none)")
    
    # Format-specific options
    csv_group = export_parser.add_argument_group('CSV Options')
    csv_group.add_argument('--delimiter', default=',',
                         help="Delimiter for CSV output (default: ',')")
    csv_group.add_argument('--quotechar', default='"',
                         help="Quote character for CSV output (default: '\"')")
    csv_group.add_argument('--no-header', action='store_true',
                         help="Exclude header row from CSV output")
    
    excel_group = export_parser.add_argument_group('Excel Options')
    excel_group.add_argument('--sheet-name', default='Data',
                           help="Sheet name for Excel output (default: 'Data')")
    excel_group.add_argument('--include-stats', action='store_true',
                           help="Include statistics in a separate sheet")
    excel_group.add_argument('--freeze-panes', action='store_true',
                           help="Freeze the first row and column")
    
    json_group = export_parser.add_argument_group('JSON Options')
    json_group.add_argument('--indent', type=int, default=2,
                          help="Indentation level for JSON output (default: 2)")
    json_group.add_argument('--orient', choices=['records', 'columns', 'index', 'split', 'table'],
                          default='records',
                          help="JSON orientation format (default: records)")
    json_group.add_argument('--date-format',
                          help="Format string for date values in JSON output")
    
    # Report command
    report_parser = subparsers.add_parser('report', 
                                        help='Generate reports from analyzed data',
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description="""
Generate reports from analyzed data.

This command creates HTML reports with visualizations and statistics from
previously analyzed data files. It supports various templates and customization
options to tailor the reports to different needs.

Examples:
  # Generate a report with the default template
  python -m url_analyzer report --path "path/to/file.csv"
  
  # Use a specific template
  python -m url_analyzer report --path "path/to/file.csv" --template "security_focus"
  
  # Specify a custom output path and don't open in browser
  python -m url_analyzer report --path "path/to/file.csv" --output "path/to/report.html" --no-open
""")
    
    # Input options
    input_group = report_parser.add_argument_group('Input Options')
    input_group.add_argument('--path', required=True,
                           help="Path to the analyzed file")
    input_group.add_argument('--filter',
                           help="Filter expression to include only specific data (e.g., 'URL_Category=Advertising')")
    input_group.add_argument('--exclude',
                           help="Filter expression to exclude specific data (e.g., 'Is_Sensitive=True')")
    input_group.add_argument('--limit', type=int,
                           help="Maximum number of rows to include in the report")
    
    # Report options
    report_group = report_parser.add_argument_group('Report Options')
    report_group.add_argument('--template',
                            help="Template to use for report generation")
    report_group.add_argument('--output', '-o',
                            help="Output file path (default: input file with .html extension)")
    report_group.add_argument('--title',
                            help="Custom title for the report")
    report_group.add_argument('--description',
                            help="Custom description for the report")
    report_group.add_argument('--logo',
                            help="Path to a logo image to include in the report")
    report_group.add_argument('--no-open', action='store_true',
                            help="Don't open the report in a browser after generation")
    
    # Visualization options
    viz_group = report_parser.add_argument_group('Visualization Options')
    viz_group.add_argument('--chart-theme', choices=['light', 'dark', 'colorblind'],
                         default='light',
                         help="Color theme for charts (default: light)")
    viz_group.add_argument('--max-chart-items', type=int, default=10,
                         help="Maximum number of items to show in charts (default: 10)")
    viz_group.add_argument('--include-sankey', action='store_true', default=True,
                         help="Include Sankey diagram in the report (default: True)")
    viz_group.add_argument('--no-sankey', action='store_false', dest='include_sankey',
                         help="Exclude Sankey diagram from the report")
    viz_group.add_argument('--include-pie-charts', action='store_true', default=True,
                         help="Include pie charts in the report (default: True)")
    viz_group.add_argument('--no-pie-charts', action='store_false', dest='include_pie_charts',
                         help="Exclude pie charts from the report")
    viz_group.add_argument('--include-bar-charts', action='store_true', default=True,
                         help="Include bar charts in the report (default: True)")
    viz_group.add_argument('--no-bar-charts', action='store_false', dest='include_bar_charts',
                         help="Exclude bar charts from the report")
    
    # Advanced options
    advanced_group = report_parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--custom-css',
                              help="Path to a custom CSS file to include in the report")
    advanced_group.add_argument('--custom-js',
                              help="Path to a custom JavaScript file to include in the report")
    advanced_group.add_argument('--template-vars',
                              help="JSON string of additional template variables")
    advanced_group.add_argument('--minify', action='store_true',
                              help="Minify HTML, CSS, and JavaScript in the report")
    advanced_group.add_argument('--include-raw-data', action='store_true',
                              help="Include raw data in the report for client-side filtering")
    
    # Templates command
    templates_parser = subparsers.add_parser('templates', 
                                           help='List and manage report templates',
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           description="""
List and manage report templates.

This command provides tools for working with report templates, including listing
available templates, showing template details, creating new templates, and
managing custom templates.

Examples:
  # List available templates
  python -m url_analyzer templates
  
  # Show detailed information about templates
  python -m url_analyzer templates --details
  
  # Create a new template based on an existing one
  python -m url_analyzer templates --create "my_template" --base "security_focus"
  
  # Preview a template with sample data
  python -m url_analyzer templates --preview "security_focus"
""")
    
    # Listing options
    list_group = templates_parser.add_argument_group('Listing Options')
    list_group.add_argument('--details', action='store_true',
                          help="Show detailed information about each template")
    list_group.add_argument('--filter',
                          help="Filter templates by name or description")
    list_group.add_argument('--sort-by', choices=['name', 'type', 'date'],
                          default='name',
                          help="Sort templates by field (default: name)")
    list_group.add_argument('--reverse', action='store_true',
                          help="Reverse the sort order")
    
    # Template management
    manage_group = templates_parser.add_argument_group('Template Management')
    manage_group.add_argument('--create',
                            help="Create a new template with the specified name")
    manage_group.add_argument('--base',
                            help="Base template to use when creating a new template")
    manage_group.add_argument('--edit',
                            help="Edit an existing template")
    manage_group.add_argument('--delete',
                            help="Delete a custom template")
    manage_group.add_argument('--export',
                            help="Export a template to a file")
    manage_group.add_argument('--import',
                            dest='import_template',
                            help="Import a template from a file")
    
    # Preview options
    preview_group = templates_parser.add_argument_group('Preview Options')
    preview_group.add_argument('--preview',
                             help="Preview a template with sample data")
    preview_group.add_argument('--sample-data',
                             help="Path to sample data file for preview (default: built-in sample)")
    preview_group.add_argument('--no-open', action='store_true',
                             help="Don't open the preview in a browser")
    
    # Advanced options
    advanced_group = templates_parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--template-dir',
                              help="Custom directory for templates")
    advanced_group.add_argument('--validate', action='store_true',
                              help="Validate all templates")
    advanced_group.add_argument('--repair', action='store_true',
                              help="Attempt to repair invalid templates")
    advanced_group.add_argument('--reset-defaults', action='store_true',
                              help="Reset built-in templates to defaults")
    
    return parser


def configure_logging(args: argparse.Namespace) -> None:
    """
    Configure logging based on command-line arguments.
    
    Args:
        args: Command-line arguments
    """
    # Determine log level based on verbosity
    if args.quiet:
        log_level = "ERROR"
    elif args.verbose == 0:
        log_level = "INFO"
    elif args.verbose == 1:
        log_level = "DEBUG"
    else:
        log_level = "DEBUG"  # More detailed debug for verbosity > 1
    
    # Configure logging
    setup_logging(
        log_level=log_level,
        log_file=args.log_file,
        console=not args.quiet
    )
    
    logger.debug(f"Logging configured with level: {log_level}")


def handle_analyze_command(args: argparse.Namespace) -> int:
    """
    Handle the 'analyze' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Analyzing URLs in {args.path}")
    
    try:
        # Validate command-line arguments
        from url_analyzer.utils.cli_validation import (
            validate_input_path, validate_output_path, validate_output_directory,
            validate_template_name, validate_args
        )
        
        # Create a dictionary of validation functions for each argument
        validations = {
            'path': lambda p: validate_input_path(p, must_exist=True),
            'template': validate_template_name,
            'output': lambda p: validate_output_directory(p) if os.path.isdir(p) or p.endswith('/') or p.endswith('\\') 
                               else validate_output_path(p)
        }
        
        # Validate the arguments
        validated_args = validate_args(args, validations)
        
        # Load configuration
        config_data = load_config()
        compiled_patterns = compile_patterns(config_data)
        
        # Load cache - temporarily commented out during refactoring
        # global LIVE_SCAN_CACHE
        # LIVE_SCAN_CACHE = load_cache(config_data)
        
        # Process batch
        from url_analyzer.data.batch import process_batch
        
        # Add batch processing options
        job_id = getattr(validated_args, 'job_id', None)
        max_workers = getattr(validated_args, 'max_workers', None)
        checkpoint_interval = getattr(validated_args, 'checkpoint_interval', 5)
        
        # Process the batch
        valid_dfs, report_path = process_batch(
            validated_args.path,
            compiled_patterns,
            validated_args,
            job_id=job_id,
            max_workers=max_workers,
            checkpoint_interval=checkpoint_interval
        )
        
        if not valid_dfs:
            logger.error("No valid data to process.")
            return 1
        
        # Concatenate DataFrames if needed
        final_df = pd.concat(valid_dfs, ignore_index=True)
        
        # Determine output path
        if validated_args.output:
            if not os.path.isdir(validated_args.output):
                # If output is a file path, use it directly
                report_path = validated_args.output
            else:
                # If output is a directory, construct the report path
                output_dir = validated_args.output
                base_name = os.path.splitext(os.path.basename(report_path))[0]
                report_path = os.path.join(output_dir, f"{base_name}.html")
        
        # Validate the final report path
        report_path = validate_output_path(report_path)
        
        # Calculate stats for the report
        stats = print_summary(final_df)
        
        # Generate report
        logger.info("Generating report...")
        if validated_args.template:
            # Create a report generator with the specified template
            report_generator = ReportGeneratorFactory.create_generator('html', validated_args.template)
        else:
            # Create a default HTML report generator
            report_generator = ReportGeneratorFactory.create_generator('html')
        
        # Generate the report
        report_path = report_generator.generate_report(final_df, report_path, stats)
        
        logger.info(f"HTML report saved to: {report_path}")
        
        # Export data if requested
        if validated_args.export_format:
            export_path = os.path.splitext(report_path)[0] + f".{validated_args.export_format}"
            export_path = validate_output_path(export_path)
            export_data(final_df, export_path, validated_args.export_format)
            logger.info(f"Data exported to: {export_path}")
        
        # Open report in browser
        if not validated_args.no_open:
            webbrowser.open(f"file://{os.path.realpath(report_path)}")
        
        # Show success message with rich formatting
        console.print(Panel(
            f"[green]Analysis completed successfully![/green]\n\n"
            f"📊 Report saved to: [cyan]{report_path}[/cyan]\n"
            f"🌐 Report opened in browser: [yellow]{'Yes' if not validated_args.no_open else 'No'}[/yellow]",
            title="✅ Analysis Complete",
            border_style="green"
        ))
        
        return 0
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        console.print(Panel(
            f"[red]Validation Error[/red]\n\n{str(e)}\n\n"
            f"[yellow]💡 Tip:[/yellow] Check your input file path and format requirements.",
            title="❌ Input Validation Failed",
            border_style="red"
        ))
        return 1
    except Exception as e:
        logger.exception(f"Error analyzing URLs: {e}")
        console.print(Panel(
            f"[red]Unexpected Error[/red]\n\n{str(e)}\n\n"
            f"[yellow]💡 Tip:[/yellow] Check the logs for more details or try running with --verbose flag.",
            title="❌ Analysis Failed",
            border_style="red"
        ))
        return 1


def handle_configure_command(args: argparse.Namespace) -> int:
    """
    Handle the 'configure' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info("Entering configuration mode")
    
    try:
        # Validate command-line arguments
        from url_analyzer.utils.cli_validation import (
            validate_output_path, validate_args
        )
        
        # Create a dictionary of validation functions for each argument
        validations = {
            'config_file': lambda p: validate_output_path(p, create_dirs=False) if p else 'config.json'
        }
        
        # Validate the arguments
        validated_args = validate_args(args, validations)
        
        # Load configuration
        config_path = validated_args.config_file or 'config.json'
        
        if validated_args.reset:
            logger.info("Resetting configuration to defaults")
            from url_analyzer.config_manager import create_default_config
            config_data = create_default_config()
            save_config(config_data, config_path)
            logger.info(f"Configuration reset to defaults and saved to {config_path}")
            console.print(Panel(
                f"[green]Configuration reset successfully![/green]\n\n"
                f"📁 Config file: [cyan]{config_path}[/cyan]\n"
                f"🔄 All settings restored to default values",
                title="✅ Configuration Reset",
                border_style="green"
            ))
            return 0
        
        # Interactive configuration mode
        from url_analyzer.config_manager import manage_configuration
        # Set the config path in the environment variable
        import os
        os.environ['URL_ANALYZER_CONFIG_PATH'] = config_path
        manage_configuration()
        
        return 0
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        console.print(Panel(
            f"[red]Configuration Validation Error[/red]\n\n{str(e)}",
            title="❌ Configuration Failed",
            border_style="red"
        ))
        return 1
    except Exception as e:
        logger.exception(f"Error configuring application: {e}")
        console.print(Panel(
            f"[red]Configuration Error[/red]\n\n{str(e)}\n\n"
            f"[yellow]💡 Tip:[/yellow] Check file permissions and configuration format.",
            title="❌ Configuration Failed",
            border_style="red"
        ))
        return 1


def handle_export_command(args: argparse.Namespace) -> int:
    """
    Handle the 'export' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Exporting data from {args.path} to {args.format} format")
    
    try:
        # Validate command-line arguments
        from url_analyzer.utils.cli_validation import (
            validate_input_path, validate_output_path, validate_file_format,
            validate_filter_expression, validate_args
        )
        from url_analyzer.utils.validation import validate_enum
        
        # Create a dictionary of validation functions for each argument
        validations = {
            'path': lambda p: validate_input_path(p, must_exist=True),
            'format': lambda f: validate_enum(f, ['csv', 'json', 'excel'], 
                                             error_message=f"Unsupported export format: {f}"),
            'output': validate_output_path,
            'filter': validate_filter_expression
        }
        
        # Validate the arguments
        validated_args = validate_args(args, validations)
        
        # Validate file format
        validate_file_format(validated_args.path, ['csv', 'xlsx', 'xls'])
        
        # Read the input file
        if validated_args.path.lower().endswith('.csv'):
            df = pd.read_csv(validated_args.path, on_bad_lines='skip')
        elif validated_args.path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(validated_args.path)
        else:
            # This should not happen due to the validation above
            logger.error(f"Unsupported file format: {validated_args.path}")
            return 1
        
        # Determine output path
        if validated_args.output:
            output_path = validated_args.output
        else:
            output_path = os.path.splitext(validated_args.path)[0] + f".{validated_args.format}"
            # Validate the output path
            output_path = validate_output_path(output_path)
        
        # Apply filter if specified
        if validated_args.filter:
            try:
                # Use the validated and parsed filter
                filter_dict = validated_args.filter
                column = filter_dict['column']
                value = filter_dict['value']
                
                # Check if the column exists in the DataFrame
                if column not in df.columns:
                    error_msg = f"Column '{column}' not found in the data"
                    logger.error(error_msg)
                    console.print(Panel(
                        f"[red]Filter Error[/red]\n\n{error_msg}\n\n"
                        f"[yellow]Available columns:[/yellow] {', '.join(df.columns.tolist())}",
                        title="❌ Column Not Found",
                        border_style="red"
                    ))
                    return 1
                
                # Apply the filter
                df = df[df[column] == value]
                logger.info(f"Applied filter: {column}={value}")
                
                # Check if the filtered DataFrame is empty
                if df.empty:
                    logger.warning(f"No data matches the filter: {column}={value}")
                    console.print(Panel(
                        f"[yellow]No data matches the specified filter[/yellow]\n\n"
                        f"Filter: [cyan]{column}={value}[/cyan]\n\n"
                        f"[dim]The export will continue with an empty dataset.[/dim]",
                        title="⚠️ Empty Filter Result",
                        border_style="yellow"
                    ))
            except Exception as e:
                logger.error(f"Error applying filter: {e}")
                console.print(Panel(
                    f"[red]Filter Processing Error[/red]\n\n{str(e)}\n\n"
                    f"[yellow]💡 Tip:[/yellow] Check your filter syntax and column names.",
                    title="❌ Filter Failed",
                    border_style="red"
                ))
                return 1
        
        # Export data with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Exporting to {validated_args.format.upper()}...", total=100)
            progress.update(task, advance=50)
            export_data(df, output_path, validated_args.format)
            progress.update(task, advance=50)
        
        logger.info(f"Data exported to: {output_path}")
        console.print(Panel(
            f"[green]Export completed successfully![/green]\n\n"
            f"📁 Output file: [cyan]{output_path}[/cyan]\n"
            f"📊 Format: [yellow]{validated_args.format.upper()}[/yellow]\n"
            f"📈 Records exported: [magenta]{len(df):,}[/magenta]",
            title="✅ Export Complete",
            border_style="green"
        ))
        
        return 0
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        console.print(Panel(
            f"[red]Export Validation Error[/red]\n\n{str(e)}",
            title="❌ Export Failed",
            border_style="red"
        ))
        return 1
    except Exception as e:
        logger.exception(f"Error exporting data: {e}")
        console.print(Panel(
            f"[red]Export Error[/red]\n\n{str(e)}\n\n"
            f"[yellow]💡 Tip:[/yellow] Check file permissions and disk space.",
            title="❌ Export Failed",
            border_style="red"
        ))
        return 1


def handle_report_command(args: argparse.Namespace) -> int:
    """
    Handle the 'report' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Generating report from {args.path}")
    
    try:
        # Validate command-line arguments
        from url_analyzer.utils.cli_validation import (
            validate_input_path, validate_output_path, validate_file_format,
            validate_template_name, validate_args
        )
        
        # Create a dictionary of validation functions for each argument
        validations = {
            'path': lambda p: validate_input_path(p, must_exist=True),
            'template': validate_template_name,
            'output': validate_output_path
        }
        
        # Validate the arguments
        validated_args = validate_args(args, validations)
        
        # Validate file format
        validate_file_format(validated_args.path, ['csv', 'xlsx', 'xls'])
        
        # Read the input file
        if validated_args.path.lower().endswith('.csv'):
            df = pd.read_csv(validated_args.path, on_bad_lines='skip')
        elif validated_args.path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(validated_args.path)
        else:
            # This should not happen due to the validation above
            logger.error(f"Unsupported file format: {validated_args.path}")
            return 1
        
        # Determine output path
        if validated_args.output:
            output_path = validated_args.output
        else:
            output_path = os.path.splitext(validated_args.path)[0] + ".html"
            # Validate the output path
            output_path = validate_output_path(output_path)
        
        # Calculate stats for the report
        stats = print_summary(df)
        
        # Generate report
        if validated_args.template:
            # Create a report generator with the specified template
            report_generator = ReportGeneratorFactory.create_generator('html', validated_args.template)
        else:
            # Create a default HTML report generator
            report_generator = ReportGeneratorFactory.create_generator('html')
        
        # Generate the report
        report_path = report_generator.generate_report(df, output_path, stats)
        
        logger.info(f"HTML report saved to: {report_path}")
        print(f"✅ HTML report saved to: {report_path}")
        
        # Open report in browser
        if not validated_args.no_open:
            webbrowser.open(f"file://{os.path.realpath(report_path)}")
        
        return 0
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ {e}")
        return 1
    except Exception as e:
        logger.exception(f"Error generating report: {e}")
        print(f"❌ Error generating report: {e}")
        return 1


def handle_interactive_command(args: argparse.Namespace) -> int:
    """
    Handle the 'interactive' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info("Launching interactive mode")
    
    try:
        # Import the interactive CLI module
        from url_analyzer.cli.interactive_cli import run_interactive_mode
        
        # Set environment variable for colored output
        if args.no_color:
            os.environ['NO_COLOR'] = '1'
        
        # Run the interactive mode
        return run_interactive_mode()
    except ImportError as e:
        logger.error(f"Error importing interactive CLI module: {e}")
        print(f"❌ Error: The interactive mode requires additional dependencies.")
        print("   Please install them with: pip install rich prompt_toolkit")
        return 1
    except Exception as e:
        logger.exception(f"Error in interactive mode: {e}")
        print(f"❌ Error in interactive mode: {e}")
        return 1


def handle_templates_command(args: argparse.Namespace) -> int:
    """
    Handle the 'templates' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info("Listing available report templates")
    
    try:
        # Validate command-line arguments
        from url_analyzer.utils.cli_validation import validate_args
        
        # Create a dictionary of validation functions for each argument
        # No specific validation needed for the 'details' flag as it's a boolean
        validations = {}
        
        # Validate the arguments
        validated_args = validate_args(args, validations)
        
        # List available templates
        templates = list_available_templates()
        
        if not templates:
            print("No templates found.")
            return 0
        
        print(f"\nAvailable Report Templates ({len(templates)}):\n")
        
        # Calculate the maximum length of template names for alignment
        max_name_length = max(len(template["name"]) for template in templates)
        
        for template in templates:
            if validated_args.details:
                print(f"  {template['name']:{max_name_length}} - {template['filename']}")
                print(f"  {' ' * max_name_length}   {template['description']}")
                print()
            else:
                print(f"  {template['name']:{max_name_length}} - {template['description']}")
        
        print("\nTo use a template, specify it with the --template option:")
        print("  python -m url_analyzer analyze --path \"path/to/file.csv\" --template \"template_name\"")
        print("  python -m url_analyzer report --path \"path/to/file.csv\" --template \"template_name\"")
        
        return 0
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ {e}")
        return 1
    except Exception as e:
        logger.exception(f"Error listing templates: {e}")
        print(f"❌ Error listing templates: {e}")
        return 1


def main() -> int:
    """
    Main entry point for the command-line interface.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Create parser and parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(args)
    
    # Handle commands
    if args.command == 'analyze':
        return handle_analyze_command(args)
    elif args.command == 'configure':
        return handle_configure_command(args)
    elif args.command == 'export':
        return handle_export_command(args)
    elif args.command == 'report':
        return handle_report_command(args)
    elif args.command == 'templates':
        return handle_templates_command(args)
    elif args.command == 'interactive':
        return handle_interactive_command(args)
    elif args.command == 'dependencies':
        handle_dependency_command(args)
        return 0
    elif args.command == 'automation':
        return handle_automation_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())