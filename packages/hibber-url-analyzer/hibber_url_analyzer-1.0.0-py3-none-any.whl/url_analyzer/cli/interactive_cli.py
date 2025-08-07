"""
Interactive CLI Module

This module provides an interactive command-line interface for the URL Analyzer application,
with a rich terminal UI and guided workflows.
"""

import os
import sys
import webbrowser
from typing import Dict, List, Any, Optional, Union, Tuple

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.columns import Columns
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.formatted_text import HTML
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import from other modules
from url_analyzer.utils.logging import get_logger
from url_analyzer.config.manager import load_config, save_config, compile_patterns
from url_analyzer.core.classification import classify_url, get_base_domain
from url_analyzer.core.analysis import fetch_url_data, load_cache, save_cache, LIVE_SCAN_CACHE
from url_analyzer.data.processing import process_file, process_files, print_summary
from url_analyzer.data.export import export_data
from url_analyzer.reporting.html_report import list_available_templates, get_template_path
from url_analyzer.reporting.generators import ReportGenerator, ReportGeneratorFactory
from url_analyzer.utils.observers import RichProgressObserver, ProgressTracker

# Create logger
logger = get_logger(__name__)

# Create console for rich output
console = Console() if RICH_AVAILABLE else None


def check_dependencies() -> bool:
    """
    Check if the required dependencies for interactive mode are available.
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    if not RICH_AVAILABLE:
        print("Error: The 'rich' and 'prompt_toolkit' packages are required for interactive mode.")
        print("Please install them with: pip install rich prompt_toolkit")
        return False
    return True


def display_welcome_screen() -> None:
    """
    Display a welcome screen with information about the interactive mode.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Welcome to URL Analyzer Interactive Mode[/bold blue]\n\n"
        "This interactive interface allows you to analyze URLs, generate reports, "
        "and configure the application with a user-friendly interface.\n\n"
        "Use the arrow keys to navigate, Enter to select, and Ctrl+C to exit at any time.",
        title="URL Analyzer",
        subtitle="Interactive Mode",
        border_style="blue"
    ))
    console.print()


def display_main_menu() -> str:
    """
    Display the main menu and get the user's selection.
    
    Returns:
        str: The selected option
    """
    options = [
        "Analyze URLs",
        "Generate Reports",
        "Export Data",
        "Explore Data",
        "Configure Application",
        "View Templates",
        "Exit"
    ]
    
    console.print("[bold]Main Menu[/bold]")
    console.print()
    
    for i, option in enumerate(options, 1):
        console.print(f"  {i}. {option}")
    
    console.print()
    choice = Prompt.ask(
        "Select an option",
        choices=[str(i) for i in range(1, len(options) + 1)],
        default="1"
    )
    
    return options[int(choice) - 1]


def analyze_urls_workflow() -> None:
    """
    Interactive workflow for analyzing URLs.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Analyze URLs[/bold blue]\n\n"
        "This workflow will guide you through analyzing URLs from a file or directory.",
        title="URL Analyzer",
        subtitle="Analyze URLs",
        border_style="blue"
    ))
    console.print()
    
    # Get input path
    path = Prompt.ask("Enter the path to a file or directory")
    
    # Validate path
    if not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] Path '{path}' does not exist.")
        input("Press Enter to continue...")
        return
    
    # Get analysis options
    live_scan = Confirm.ask("Enable live URL scanning?", default=False)
    summarize = False
    if live_scan:
        summarize = Confirm.ask("Enable AI content summarization?", default=False)
    
    aggregate = False
    if os.path.isdir(path):
        aggregate = Confirm.ask("Generate a single aggregated report?", default=True)
    
    # Get output options
    output = Prompt.ask("Enter output directory (leave empty for same as input)", default="")
    
    # Get template options
    templates = list_available_templates()
    template_names = ["default"] + [t["name"] for t in templates]
    template = Prompt.ask(
        "Select a template for the report",
        choices=template_names,
        default="default"
    )
    
    # Get export options
    export_format = Prompt.ask(
        "Export analyzed data to format",
        choices=["none", "csv", "json", "excel"],
        default="none"
    )
    
    # Confirm settings
    console.print("\n[bold]Analysis Settings:[/bold]")
    console.print(f"  Path: {path}")
    console.print(f"  Live Scan: {'Yes' if live_scan else 'No'}")
    if live_scan:
        console.print(f"  Summarize: {'Yes' if summarize else 'No'}")
    if os.path.isdir(path):
        console.print(f"  Aggregate: {'Yes' if aggregate else 'No'}")
    console.print(f"  Output: {output or 'Same as input'}")
    console.print(f"  Template: {template}")
    console.print(f"  Export Format: {export_format if export_format != 'none' else 'None'}")
    
    if not Confirm.ask("\nProceed with analysis?", default=True):
        console.print("Analysis cancelled.")
        input("Press Enter to continue...")
        return
    
    # Prepare command-line arguments
    import argparse
    args = argparse.Namespace()
    args.path = path
    args.live_scan = live_scan
    args.summarize = summarize
    args.aggregate = aggregate
    args.output = output
    args.template = None if template == "default" else template
    args.export_format = None if export_format == "none" else export_format
    args.no_open = False
    args.chunked = True
    args.chunk_size = 10000
    args.verbose = 1
    args.quiet = False
    args.log_file = None
    
    # Run analysis
    console.print("\n[bold]Running Analysis...[/bold]")
    
    # Create a Rich progress instance
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        # Create a RichProgressObserver with the progress instance
        rich_observer = RichProgressObserver(progress)
        
        # Start the progress tracking
        rich_observer.start(100, "[green]Analyzing...")
        
        try:
            # Import the analyze command handler
            from url_analyzer.cli.commands import handle_analyze_command
            
            # Create a custom analyze handler that updates progress
            def analyze_with_progress(args):
                # Monkey patch the handle_analyze_command to track progress
                original_process_batch = None
                
                try:
                    # Import the batch processing module
                    from url_analyzer.data.batch import process_batch
                    
                    # Store the original function
                    original_process_batch = process_batch
                    
                    # Define a wrapper function that updates progress
                    def process_batch_with_progress(path, compiled_patterns, args, **kwargs):
                        # Create a progress tracker
                        tracker = ProgressTracker()
                        tracker.attach(rich_observer)
                        
                        # Add the tracker to kwargs
                        kwargs['progress_tracker'] = tracker
                        
                        # Call the original function
                        return original_process_batch(path, compiled_patterns, args, **kwargs)
                    
                    # Replace the original function with our wrapper
                    import url_analyzer.data.batch
                    url_analyzer.data.batch.process_batch = process_batch_with_progress
                    
                    # Run the analysis
                    result = handle_analyze_command(args)
                    
                    return result
                finally:
                    # Restore the original function
                    if original_process_batch:
                        import url_analyzer.data.batch
                        url_analyzer.data.batch.process_batch = original_process_batch
            
            # Run the analysis with progress tracking
            result = analyze_with_progress(args)
            
            # Complete the progress
            rich_observer.finish()
            
            if result == 0:
                console.print("[bold green]Analysis completed successfully![/bold green]")
            else:
                console.print("[bold red]Analysis failed.[/bold red]")
        except Exception as e:
            # Complete the progress in case of error
            rich_observer.finish()
            console.print(f"[bold red]Error:[/bold red] {e}")
            logger.exception(f"Error in analyze_urls_workflow: {e}")
    
    input("\nPress Enter to continue...")


def generate_reports_workflow() -> None:
    """
    Interactive workflow for generating reports.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Generate Reports[/bold blue]\n\n"
        "This workflow will guide you through generating reports from analyzed data.",
        title="URL Analyzer",
        subtitle="Generate Reports",
        border_style="blue"
    ))
    console.print()
    
    # Get input path
    path = Prompt.ask("Enter the path to an analyzed file")
    
    # Validate path
    if not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] Path '{path}' does not exist.")
        input("Press Enter to continue...")
        return
    
    # Get template options
    templates = list_available_templates()
    template_names = ["default"] + [t["name"] for t in templates]
    template = Prompt.ask(
        "Select a template for the report",
        choices=template_names,
        default="default"
    )
    
    # Get output options
    output = Prompt.ask("Enter output file path (leave empty for default)", default="")
    
    # Confirm settings
    console.print("\n[bold]Report Settings:[/bold]")
    console.print(f"  Input File: {path}")
    console.print(f"  Template: {template}")
    console.print(f"  Output: {output or 'Default'}")
    
    if not Confirm.ask("\nProceed with report generation?", default=True):
        console.print("Report generation cancelled.")
        input("Press Enter to continue...")
        return
    
    # Prepare command-line arguments
    import argparse
    args = argparse.Namespace()
    args.path = path
    args.template = None if template == "default" else template
    args.output = output
    args.no_open = False
    args.verbose = 1
    args.quiet = False
    args.log_file = None
    
    # Run report generation
    console.print("\n[bold]Generating Report...[/bold]")
    
    # Create a Rich progress instance
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        # Create a RichProgressObserver with the progress instance
        rich_observer = RichProgressObserver(progress)
        
        # Start the progress tracking
        rich_observer.start(100, "[green]Generating Report...")
        
        try:
            # Import the report command handler
            from url_analyzer.cli.commands import handle_report_command
            
            # Create a custom report handler that updates progress
            def generate_report_with_progress(args):
                # Monkey patch the report generation to track progress
                original_generate_report = None
                
                try:
                    # Import the report generator
                    from url_analyzer.reporting.generators import ReportGenerator
                    
                    # Store the original generate_report method
                    original_generate_report = ReportGenerator.generate_report
                    
                    # Define a wrapper method that updates progress
                    def generate_report_with_tracking(self, data, output_path, stats=None):
                        # Update progress to 10%
                        rich_observer.update(0.1, "Preparing data...")
                        
                        # Update progress to 30%
                        rich_observer.update(0.3, "Generating visualizations...")
                        
                        # Call the original method
                        result = original_generate_report(self, data, output_path, stats)
                        
                        # Update progress to 90%
                        rich_observer.update(0.9, "Finalizing report...")
                        
                        return result
                    
                    # Replace the original method with our wrapper
                    ReportGenerator.generate_report = generate_report_with_tracking
                    
                    # Run the report generation
                    result = handle_report_command(args)
                    
                    return result
                finally:
                    # Restore the original method
                    if original_generate_report:
                        ReportGenerator.generate_report = original_generate_report
            
            # Run the report generation with progress tracking
            result = generate_report_with_progress(args)
            
            # Complete the progress
            rich_observer.update(1.0, "Report completed")
            rich_observer.finish()
            
            if result == 0:
                console.print("[bold green]Report generated successfully![/bold green]")
            else:
                console.print("[bold red]Report generation failed.[/bold red]")
        except Exception as e:
            # Complete the progress in case of error
            rich_observer.finish()
            console.print(f"[bold red]Error:[/bold red] {e}")
            logger.exception(f"Error in generate_reports_workflow: {e}")
    
    input("\nPress Enter to continue...")


def export_data_workflow() -> None:
    """
    Interactive workflow for exporting data.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Export Data[/bold blue]\n\n"
        "This workflow will guide you through exporting data to different formats.",
        title="URL Analyzer",
        subtitle="Export Data",
        border_style="blue"
    ))
    console.print()
    
    # Get input path
    path = Prompt.ask("Enter the path to the file to export")
    
    # Validate path
    if not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] Path '{path}' does not exist.")
        input("Press Enter to continue...")
        return
    
    # Get export format
    export_format = Prompt.ask(
        "Select export format",
        choices=["csv", "json", "excel"],
        default="csv"
    )
    
    # Get output options
    output = Prompt.ask("Enter output file path (leave empty for default)", default="")
    
    # Get filter options
    use_filter = Confirm.ask("Apply a filter to the data?", default=False)
    filter_expr = ""
    if use_filter:
        console.print("\n[bold]Available Filter Format:[/bold]")
        console.print("  column=value (e.g., URL_Category=Advertising)")
        filter_expr = Prompt.ask("Enter filter expression")
    
    # Confirm settings
    console.print("\n[bold]Export Settings:[/bold]")
    console.print(f"  Input File: {path}")
    console.print(f"  Export Format: {export_format}")
    console.print(f"  Output: {output or 'Default'}")
    if use_filter:
        console.print(f"  Filter: {filter_expr}")
    
    if not Confirm.ask("\nProceed with export?", default=True):
        console.print("Export cancelled.")
        input("Press Enter to continue...")
        return
    
    # Prepare command-line arguments
    import argparse
    args = argparse.Namespace()
    args.path = path
    args.format = export_format
    args.output = output
    args.filter = filter_expr if use_filter else None
    args.verbose = 1
    args.quiet = False
    args.log_file = None
    
    # Run export
    console.print("\n[bold]Exporting Data...[/bold]")
    
    # Create a Rich progress instance
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        # Create a RichProgressObserver with the progress instance
        rich_observer = RichProgressObserver(progress)
        
        # Start the progress tracking
        rich_observer.start(100, "[green]Exporting Data...")
        
        try:
            # Import the export command handler
            from url_analyzer.cli.commands import handle_export_command
            
            # Create a custom export handler that updates progress
            def export_with_progress(args):
                # Monkey patch the export_data function to track progress
                original_export_data = None
                
                try:
                    # Import the export module
                    from url_analyzer.data.export import export_data
                    
                    # Store the original function
                    original_export_data = export_data
                    
                    # Define a wrapper function that updates progress
                    def export_data_with_tracking(df, output_path, format, **kwargs):
                        # Update progress to 20%
                        rich_observer.update(0.2, "Preparing data...")
                        
                        # Get the number of rows
                        num_rows = len(df)
                        
                        # Update progress based on format
                        if format == 'csv':
                            rich_observer.update(0.4, f"Exporting {num_rows} rows to CSV...")
                        elif format == 'json':
                            rich_observer.update(0.4, f"Exporting {num_rows} rows to JSON...")
                        elif format == 'excel':
                            rich_observer.update(0.4, f"Exporting {num_rows} rows to Excel...")
                        else:
                            rich_observer.update(0.4, f"Exporting {num_rows} rows...")
                        
                        # Call the original function
                        result = original_export_data(df, output_path, format, **kwargs)
                        
                        # Update progress to 90%
                        rich_observer.update(0.9, "Finalizing export...")
                        
                        return result
                    
                    # Replace the original function with our wrapper
                    import url_analyzer.data.export
                    url_analyzer.data.export.export_data = export_data_with_tracking
                    
                    # Run the export
                    result = handle_export_command(args)
                    
                    return result
                finally:
                    # Restore the original function
                    if original_export_data:
                        import url_analyzer.data.export
                        url_analyzer.data.export.export_data = original_export_data
            
            # Run the export with progress tracking
            result = export_with_progress(args)
            
            # Complete the progress
            rich_observer.update(1.0, "Export completed")
            rich_observer.finish()
            
            if result == 0:
                console.print("[bold green]Data exported successfully![/bold green]")
            else:
                console.print("[bold red]Export failed.[/bold red]")
        except Exception as e:
            # Complete the progress in case of error
            rich_observer.finish()
            console.print(f"[bold red]Error:[/bold red] {e}")
            logger.exception(f"Error in export_data_workflow: {e}")
    
    input("\nPress Enter to continue...")


def configure_application_workflow() -> None:
    """
    Interactive workflow for configuring the application.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Configure Application[/bold blue]\n\n"
        "This workflow will guide you through configuring the application settings.",
        title="URL Analyzer",
        subtitle="Configure Application",
        border_style="blue"
    ))
    console.print()
    
    # Get configuration options
    reset = Confirm.ask("Reset configuration to defaults?", default=False)
    
    config_file = Prompt.ask(
        "Enter path to configuration file (leave empty for default)",
        default="config.json"
    )
    
    # Confirm settings
    console.print("\n[bold]Configuration Settings:[/bold]")
    console.print(f"  Reset to Defaults: {'Yes' if reset else 'No'}")
    console.print(f"  Configuration File: {config_file}")
    
    if not Confirm.ask("\nProceed with configuration?", default=True):
        console.print("Configuration cancelled.")
        input("Press Enter to continue...")
        return
    
    # Prepare command-line arguments
    import argparse
    args = argparse.Namespace()
    args.reset = reset
    args.config_file = config_file
    args.verbose = 1
    args.quiet = False
    args.log_file = None
    
    # Run configuration
    console.print("\n[bold]Configuring Application...[/bold]")
    
    try:
        # Import the configure command handler
        from url_analyzer.cli.commands import handle_configure_command
        
        # Run the configuration
        result = handle_configure_command(args)
        
        if result == 0:
            console.print("[bold green]Configuration completed successfully![/bold green]")
        else:
            console.print("[bold red]Configuration failed.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    
    input("\nPress Enter to continue...")


def view_templates_workflow() -> None:
    """
    Interactive workflow for viewing available templates.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]View Templates[/bold blue]\n\n"
        "This workflow will show you the available report templates.",
        title="URL Analyzer",
        subtitle="View Templates",
        border_style="blue"
    ))
    console.print()
    
    # Get template options
    details = Confirm.ask("Show detailed information about each template?", default=True)
    
    # Prepare command-line arguments
    import argparse
    args = argparse.Namespace()
    args.details = details
    args.verbose = 1
    args.quiet = False
    args.log_file = None
    
    # Run templates command
    console.print("\n[bold]Available Templates:[/bold]")
    
    try:
        # List available templates
        templates = list_available_templates()
        
        if not templates:
            console.print("No templates found.")
        else:
            # Create a table for templates
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Name")
            table.add_column("Description")
            if details:
                table.add_column("Filename")
            
            for template in templates:
                if details:
                    table.add_row(
                        template["name"],
                        template["description"],
                        template["filename"]
                    )
                else:
                    table.add_row(
                        template["name"],
                        template["description"]
                    )
            
            console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    
    input("\nPress Enter to continue...")


def explore_data_workflow() -> None:
    """
    Interactive workflow for exploring analyzed data.
    
    This workflow allows users to interactively explore analyzed data,
    including viewing statistics, filtering data, and examining specific URLs.
    """
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Explore Data[/bold blue]\n\n"
        "This workflow will guide you through exploring analyzed data interactively.",
        title="URL Analyzer",
        subtitle="Explore Data",
        border_style="blue"
    ))
    console.print()
    
    # Get input path
    path = Prompt.ask("Enter the path to an analyzed file")
    
    # Validate path
    if not os.path.exists(path):
        from url_analyzer.utils.error_handler import display_error, ErrorCategory
        display_error(
            f"Path '{path}' does not exist",
            category=ErrorCategory.FILE,
            suggestions=[
                f"Check if the file exists at the specified location",
                f"Use an absolute path instead of a relative path",
                f"Make sure you have permission to access the file"
            ]
        )
        input("\nPress Enter to continue...")
        return
    
    try:
        # Load the data
        console.print("\n[bold]Loading data...[/bold]")
        
        # Get file size for progress context
        file_size = os.path.getsize(path)
        
        # Create a Rich progress instance with enhanced columns
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("{task.fields[context]}"),
            console=console
        ) as progress:
            # Create a task for loading data
            task = progress.add_task(
                "[green]Loading data...", 
                total=100, 
                context=f"File: {os.path.basename(path)} ({file_size / (1024*1024):.2f} MB)"
            )
            
            # Update progress
            progress.update(task, completed=10)
            
            # Load the data
            if path.lower().endswith('.csv'):
                df = pd.read_csv(path, on_bad_lines='skip')
            elif path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(path)
            else:
                from url_analyzer.utils.error_handler import display_error, ErrorCategory
                display_error(
                    f"Unsupported file format: {path}",
                    category=ErrorCategory.FILE,
                    suggestions=[
                        "Use a CSV or Excel file (.csv, .xlsx, .xls)",
                        "Convert your file to a supported format"
                    ]
                )
                input("\nPress Enter to continue...")
                return
            
            # Update progress with data dimensions
            progress.update(
                task, 
                completed=100, 
                context=f"Loaded {len(df):,} rows × {len(df.columns)} columns"
            )
        
        # Check if the data is empty
        if df.empty:
            from url_analyzer.utils.error_handler import display_error, ErrorCategory
            display_error(
                "The file contains no data",
                category=ErrorCategory.DATA,
                suggestions=[
                    "Check if the file is properly formatted",
                    "Make sure the file contains valid data",
                    "Try using a different file"
                ]
            )
            input("\nPress Enter to continue...")
            return
        
        # Show data summary
        console.print("\n[bold]Data Summary:[/bold]")
        
        # Create a table for basic statistics
        table = Table(show_header=True, header_style="bold blue", border_style="blue")
        table.add_column("Statistic", style="bold")
        table.add_column("Value")
        
        # Add basic statistics
        table.add_row("Number of URLs", f"[bold green]{len(df):,}[/bold green]")
        table.add_row("Number of Columns", f"[bold green]{len(df.columns)}[/bold green]")
        table.add_row("File Size", f"[bold green]{file_size / (1024*1024):.2f} MB[/bold green]")
        
        # Check if URL_Category column exists
        if 'URL_Category' in df.columns:
            # Count categories
            categories = df['URL_Category'].value_counts()
            table.add_row("Number of Categories", f"[bold green]{len(categories):,}[/bold green]")
            
            # Add top categories
            top_categories = categories.head(5)
            category_str = ", ".join([f"{cat} ([bold green]{count:,}[/bold green])" for cat, count in top_categories.items()])
            table.add_row("Top Categories", category_str)
        
        # Check if Is_Sensitive column exists
        if 'Is_Sensitive' in df.columns:
            # Count sensitive URLs
            sensitive_count = df['Is_Sensitive'].sum() if df['Is_Sensitive'].dtype == bool else 0
            table.add_row("Sensitive URLs", f"[bold red]{sensitive_count:,}[/bold red]")
        
        # Check if Base_Domain column exists
        if 'Base_Domain' in df.columns:
            # Count unique domains
            unique_domains = df['Base_Domain'].nunique()
            table.add_row("Unique Domains", f"[bold green]{unique_domains:,}[/bold green]")
            
            # Add top domains
            top_domains = df['Base_Domain'].value_counts().head(5)
            domain_str = ", ".join([f"{dom} ([bold green]{count:,}[/bold green])" for dom, count in top_domains.items()])
            table.add_row("Top Domains", domain_str)
        
        # Print the table
        console.print(table)
        
        # Interactive exploration loop
        while True:
            console.print("\n[bold]Exploration Options:[/bold]")
            options = [
                "View Data Sample",
                "Interactive Filtering",
                "Search URLs",
                "View URL Details",
                "View Category Distribution",
                "View Domain Distribution",
                "Basic Visualizations",
                "Return to Main Menu"
            ]
            
            # Create a grid for options
            from rich.columns import Columns
            from rich.panel import Panel
            
            # Create panels for each option with icons
            panels = []
            icons = ["🔍", "🔎", "🔗", "📋", "📊", "🌐", "📈", "🔙"]
            
            for i, (option, icon) in enumerate(zip(options, icons), 1):
                panels.append(
                    Panel(
                        f"[bold]{i}.[/bold] {option}",
                        border_style="blue",
                        padding=(1, 2),
                        title=icon
                    )
                )
            
            # Display options in a grid
            console.print(Columns(panels, equal=True, expand=True))
            
            console.print()
            choice = Prompt.ask(
                "Select an option",
                choices=[str(i) for i in range(1, len(options) + 1)],
                default="1"
            )
            
            if choice == "1":  # View Data Sample
                # Ask for sample size
                sample_size = int(Prompt.ask("Enter sample size", default="10"))
                
                # Get a sample of the data
                sample = df.sample(min(sample_size, len(df)))
                
                # Create a table for the sample
                table = Table(show_header=True, header_style="bold blue")
                
                # Add columns
                for col in sample.columns:
                    table.add_column(col)
                
                # Add rows
                for _, row in sample.iterrows():
                    table.add_row(*[str(val) for val in row])
                
                # Print the table
                console.print("\n[bold]Data Sample:[/bold]")
                console.print(table)
            
            elif choice == "2":  # Interactive Filtering
                console.print("\n[bold blue]Interactive Filtering[/bold blue]")
                console.print("This feature allows you to apply multiple filters to your data interactively.")
                
                # Start with the full dataset
                filtered_df = df.copy()
                active_filters = []
                
                # Interactive filtering loop
                while True:
                    # Show current filter status
                    if active_filters:
                        console.print("\n[bold]Active Filters:[/bold]")
                        filter_table = Table(show_header=True, header_style="bold blue", border_style="blue")
                        filter_table.add_column("Column", style="bold")
                        filter_table.add_column("Condition")
                        filter_table.add_column("Value")
                        
                        for f in active_filters:
                            filter_table.add_row(f["column"], f["condition"], str(f["value"]))
                        
                        console.print(filter_table)
                        console.print(f"[bold green]{len(filtered_df):,}[/bold green] rows match all filters.")
                    
                    # Show filtering options
                    console.print("\n[bold]Filtering Options:[/bold]")
                    filter_options = [
                        "Add Filter",
                        "Remove Filter",
                        "Clear All Filters",
                        "View Results",
                        "Export Filtered Data",
                        "Return to Exploration Menu"
                    ]
                    
                    for i, option in enumerate(filter_options, 1):
                        console.print(f"  {i}. {option}")
                    
                    filter_choice = Prompt.ask(
                        "Select an option",
                        choices=[str(i) for i in range(1, len(filter_options) + 1)],
                        default="1"
                    )
                    
                    if filter_choice == "1":  # Add Filter
                        # Get available columns
                        columns = df.columns.tolist()
                        
                        # Ask for column to filter on
                        column = Prompt.ask(
                            "Select column to filter on",
                            choices=columns,
                            default=columns[0]
                        )
                        
                        # Determine column type
                        col_type = df[column].dtype
                        is_numeric = pd.api.types.is_numeric_dtype(col_type)
                        is_bool = pd.api.types.is_bool_dtype(col_type)
                        
                        # Show appropriate conditions based on column type
                        if is_numeric:
                            conditions = ["equals", "not equals", "greater than", "less than", "between", "contains"]
                        elif is_bool:
                            conditions = ["is True", "is False"]
                        else:
                            conditions = ["equals", "not equals", "contains", "starts with", "ends with"]
                        
                        # Ask for condition
                        condition = Prompt.ask(
                            f"Select condition for {column}",
                            choices=conditions,
                            default=conditions[0]
                        )
                        
                        # Get filter value based on condition
                        if condition == "between":
                            min_val = Prompt.ask(f"Enter minimum value for {column}")
                            max_val = Prompt.ask(f"Enter maximum value for {column}")
                            value = (float(min_val), float(max_val))
                        elif condition in ["is True", "is False"]:
                            value = condition == "is True"
                        else:
                            # Get unique values for the column (for non-numeric columns)
                            if not is_numeric and not is_bool:
                                unique_values = df[column].unique().tolist()
                                unique_values = [str(val) for val in unique_values[:20]]
                                default_val = unique_values[0] if unique_values else ""
                            else:
                                default_val = str(df[column].median()) if is_numeric else ""
                            
                            value = Prompt.ask(
                                f"Enter value for {column}",
                                default=default_val
                            )
                            
                            # Convert to appropriate type for numeric columns
                            if is_numeric and condition != "contains":
                                try:
                                    value = float(value)
                                except ValueError:
                                    console.print("[bold red]Error:[/bold red] Invalid numeric value. Filter not applied.")
                                    continue
                        
                        # Apply the filter
                        try:
                            if condition == "equals":
                                filtered_df = filtered_df[filtered_df[column] == value]
                            elif condition == "not equals":
                                filtered_df = filtered_df[filtered_df[column] != value]
                            elif condition == "greater than":
                                filtered_df = filtered_df[filtered_df[column] > value]
                            elif condition == "less than":
                                filtered_df = filtered_df[filtered_df[column] < value]
                            elif condition == "between":
                                filtered_df = filtered_df[(filtered_df[column] >= value[0]) & (filtered_df[column] <= value[1])]
                            elif condition == "contains":
                                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False)]
                            elif condition == "starts with":
                                filtered_df = filtered_df[filtered_df[column].astype(str).str.startswith(value, na=False)]
                            elif condition == "ends with":
                                filtered_df = filtered_df[filtered_df[column].astype(str).str.endswith(value, na=False)]
                            elif condition == "is True":
                                filtered_df = filtered_df[filtered_df[column] == True]
                            elif condition == "is False":
                                filtered_df = filtered_df[filtered_df[column] == False]
                            
                            # Add to active filters
                            active_filters.append({
                                "column": column,
                                "condition": condition,
                                "value": value
                            })
                            
                            console.print(f"[bold green]Filter applied.[/bold green] {len(filtered_df):,} rows match all filters.")
                        except Exception as e:
                            from url_analyzer.utils.error_handler import display_error, ErrorCategory
                            display_error(
                                "Failed to apply filter",
                                exception=e,
                                category=ErrorCategory.DATA,
                                suggestions=[
                                    "Check if the value is valid for the selected column",
                                    "Try a different condition or column"
                                ]
                            )
                    
                    elif filter_choice == "2":  # Remove Filter
                        if not active_filters:
                            console.print("[italic]No active filters to remove.[/italic]")
                            continue
                        
                        # List active filters
                        console.print("\n[bold]Select filter to remove:[/bold]")
                        for i, f in enumerate(active_filters, 1):
                            console.print(f"  {i}. {f['column']} {f['condition']} {f['value']}")
                        
                        # Ask which filter to remove
                        remove_idx = int(Prompt.ask(
                            "Enter filter number to remove",
                            choices=[str(i) for i in range(1, len(active_filters) + 1)],
                            default="1"
                        ))
                        
                        # Remove the filter
                        active_filters.pop(remove_idx - 1)
                        
                        # Reapply all remaining filters
                        filtered_df = df.copy()
                        for f in active_filters:
                            column = f["column"]
                            condition = f["condition"]
                            value = f["value"]
                            
                            if condition == "equals":
                                filtered_df = filtered_df[filtered_df[column] == value]
                            elif condition == "not equals":
                                filtered_df = filtered_df[filtered_df[column] != value]
                            elif condition == "greater than":
                                filtered_df = filtered_df[filtered_df[column] > value]
                            elif condition == "less than":
                                filtered_df = filtered_df[filtered_df[column] < value]
                            elif condition == "between":
                                filtered_df = filtered_df[(filtered_df[column] >= value[0]) & (filtered_df[column] <= value[1])]
                            elif condition == "contains":
                                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False)]
                            elif condition == "starts with":
                                filtered_df = filtered_df[filtered_df[column].astype(str).str.startswith(value, na=False)]
                            elif condition == "ends with":
                                filtered_df = filtered_df[filtered_df[column].astype(str).str.endswith(value, na=False)]
                            elif condition == "is True":
                                filtered_df = filtered_df[filtered_df[column] == True]
                            elif condition == "is False":
                                filtered_df = filtered_df[filtered_df[column] == False]
                        
                        console.print(f"[bold green]Filter removed.[/bold green] {len(filtered_df):,} rows match all filters.")
                    
                    elif filter_choice == "3":  # Clear All Filters
                        active_filters = []
                        filtered_df = df.copy()
                        console.print("[bold green]All filters cleared.[/bold green]")
                    
                    elif filter_choice == "4":  # View Results
                        if filtered_df.empty:
                            console.print("[italic]No data matches the current filters.[/italic]")
                            continue
                        
                        # Show results
                        console.print(f"\n[bold]Filtered Data ({len(filtered_df):,} rows):[/bold]")
                        
                        # Create a table for the filtered data
                        table = Table(show_header=True, header_style="bold blue", border_style="blue")
                        
                        # Add columns
                        for col in filtered_df.columns:
                            table.add_column(col)
                        
                        # Add rows (limit to 15)
                        for _, row in filtered_df.head(15).iterrows():
                            table.add_row(*[str(val) for val in row])
                        
                        # Print the table
                        console.print(table)
                        
                        if len(filtered_df) > 15:
                            console.print(f"[italic]Showing 15 of {len(filtered_df):,} matching rows.[/italic]")
                    
                    elif filter_choice == "5":  # Export Filtered Data
                        if filtered_df.empty:
                            console.print("[italic]No data to export.[/italic]")
                            continue
                        
                        # Ask for export path
                        export_path = Prompt.ask(
                            "Enter path for export file",
                            default="filtered_data.csv"
                        )
                        
                        # Export the data
                        try:
                            filtered_df.to_csv(export_path, index=False)
                            console.print(f"[bold green]Data exported to {export_path}[/bold green]")
                        except Exception as e:
                            from url_analyzer.utils.error_handler import display_error, ErrorCategory
                            display_error(
                                f"Failed to export data to {export_path}",
                                exception=e,
                                category=ErrorCategory.FILE,
                                suggestions=[
                                    "Check if you have write permission to the directory",
                                    "Make sure the path is valid",
                                    "Try a different location"
                                ]
                            )
                    
                    elif filter_choice == "6":  # Return to Exploration Menu
                        break
            
            elif choice == "3":  # Search URLs
                # Ask for search term
                search_term = Prompt.ask("Enter search term for URLs")
                
                # Search in URL column
                url_col = next((col for col in df.columns if col.lower() in ['url', 'domain_name']), df.columns[0])
                
                # Filter the data
                filtered_df = df[df[url_col].astype(str).str.contains(search_term, case=False)]
                
                # Show results
                console.print(f"\n[bold]Search Results ({len(filtered_df)} rows):[/bold]")
                
                if filtered_df.empty:
                    console.print("[italic]No matching URLs found.[/italic]")
                else:
                    # Create a table for the search results
                    table = Table(show_header=True, header_style="bold blue")
                    
                    # Add columns
                    for col in filtered_df.columns:
                        table.add_column(col)
                    
                    # Add rows (limit to 10)
                    for _, row in filtered_df.head(10).iterrows():
                        table.add_row(*[str(val) for val in row])
                    
                    # Print the table
                    console.print(table)
                    
                    if len(filtered_df) > 10:
                        console.print(f"[italic]Showing 10 of {len(filtered_df)} matching rows.[/italic]")
            
            elif choice == "4":  # View URL Details
                # Ask for URL index
                url_index = int(Prompt.ask("Enter row index of URL to view", default="0"))
                
                # Check if index is valid
                if url_index < 0 or url_index >= len(df):
                    console.print(f"[bold red]Error:[/bold red] Invalid index. Must be between 0 and {len(df) - 1}.")
                    continue
                
                # Get the URL data
                url_data = df.iloc[url_index]
                
                # Create a panel for the URL details
                url_col = next((col for col in df.columns if col.lower() in ['url', 'domain_name']), df.columns[0])
                url = url_data[url_col]
                
                # Create content for the panel
                content = ""
                for col, val in url_data.items():
                    content += f"[bold]{col}:[/bold] {val}\n"
                
                # Create the panel
                panel = Panel(
                    content,
                    title=f"URL Details: {url}",
                    border_style="blue"
                )
                
                # Print the panel
                console.print(panel)
            
            elif choice == "5":  # View Category Distribution
                # Check if URL_Category column exists
                if 'URL_Category' not in df.columns:
                    console.print("[bold red]Error:[/bold red] URL_Category column not found in the data.")
                    continue
                
                # Count categories
                categories = df['URL_Category'].value_counts()
                
                # Create a table for the category distribution
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Category")
                table.add_column("Count")
                table.add_column("Percentage")
                
                # Add rows
                for cat, count in categories.items():
                    percentage = count / len(df) * 100
                    table.add_row(str(cat), str(count), f"{percentage:.1f}%")
                
                # Print the table
                console.print("\n[bold]Category Distribution:[/bold]")
                console.print(table)
            
            elif choice == "6":  # View Domain Distribution
                # Check if Base_Domain column exists
                if 'Base_Domain' not in df.columns:
                    console.print("[bold red]Error:[/bold red] Base_Domain column not found in the data.")
                    continue
                
                # Count domains
                domains = df['Base_Domain'].value_counts().head(20)
                
                # Create a table for the domain distribution
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Domain")
                table.add_column("Count")
                table.add_column("Percentage")
                
                # Add rows
                for dom, count in domains.items():
                    percentage = count / len(df) * 100
                    table.add_row(str(dom), str(count), f"{percentage:.1f}%")
                
                # Print the table
                console.print("\n[bold]Domain Distribution (Top 20):[/bold]")
                console.print(table)
            
            elif choice == "7":  # Basic Visualizations
                console.print("\n[bold blue]Basic Visualizations[/bold blue]")
                console.print("This feature provides simple visualizations of your data in the terminal.")
                
                # Check if we have data to visualize
                if df.empty:
                    console.print("[italic]No data to visualize.[/italic]")
                    continue
                
                # Show visualization options
                console.print("\n[bold]Visualization Options:[/bold]")
                viz_options = [
                    "Category Distribution Bar Chart",
                    "Domain Distribution Bar Chart",
                    "Sensitivity Pie Chart",
                    "URL Length Histogram",
                    "Return to Exploration Menu"
                ]
                
                for i, option in enumerate(viz_options, 1):
                    console.print(f"  {i}. {option}")
                
                viz_choice = Prompt.ask(
                    "Select a visualization",
                    choices=[str(i) for i in range(1, len(viz_options) + 1)],
                    default="1"
                )
                
                if viz_choice == "1":  # Category Distribution Bar Chart
                    # Check if URL_Category column exists
                    if 'URL_Category' not in df.columns:
                        console.print("[bold red]Error:[/bold red] URL_Category column not found in the data.")
                        continue
                    
                    # Count categories
                    categories = df['URL_Category'].value_counts().head(15)
                    
                    # Create a simple bar chart
                    console.print("\n[bold]Category Distribution:[/bold]")
                    
                    # Get the maximum count for scaling
                    max_count = categories.max()
                    max_label_len = max([len(str(cat)) for cat in categories.index])
                    
                    # Create the chart
                    for cat, count in categories.items():
                        # Calculate bar length (max 40 characters)
                        bar_len = int((count / max_count) * 40)
                        
                        # Format the label with padding
                        label = str(cat).ljust(max_label_len)
                        
                        # Choose color based on count
                        if count > max_count * 0.75:
                            color = "green"
                        elif count > max_count * 0.5:
                            color = "yellow"
                        elif count > max_count * 0.25:
                            color = "blue"
                        else:
                            color = "red"
                        
                        # Print the bar
                        console.print(
                            f"{label} | "
                            f"[bold {color}]{'█' * bar_len}[/bold {color}] "
                            f"{count:,} ({count/len(df)*100:.1f}%)"
                        )
                
                elif viz_choice == "2":  # Domain Distribution Bar Chart
                    # Check if Base_Domain column exists
                    if 'Base_Domain' not in df.columns:
                        console.print("[bold red]Error:[/bold red] Base_Domain column not found in the data.")
                        continue
                    
                    # Count domains
                    domains = df['Base_Domain'].value_counts().head(15)
                    
                    # Create a simple bar chart
                    console.print("\n[bold]Domain Distribution:[/bold]")
                    
                    # Get the maximum count for scaling
                    max_count = domains.max()
                    max_label_len = max([len(str(dom)) for dom in domains.index])
                    
                    # Create the chart
                    for dom, count in domains.items():
                        # Calculate bar length (max 40 characters)
                        bar_len = int((count / max_count) * 40)
                        
                        # Format the label with padding
                        label = str(dom).ljust(max_label_len)
                        
                        # Choose color based on count
                        if count > max_count * 0.75:
                            color = "green"
                        elif count > max_count * 0.5:
                            color = "yellow"
                        elif count > max_count * 0.25:
                            color = "blue"
                        else:
                            color = "red"
                        
                        # Print the bar
                        console.print(
                            f"{label} | "
                            f"[bold {color}]{'█' * bar_len}[/bold {color}] "
                            f"{count:,} ({count/len(df)*100:.1f}%)"
                        )
                
                elif viz_choice == "3":  # Sensitivity Pie Chart
                    # Check if Is_Sensitive column exists
                    if 'Is_Sensitive' not in df.columns:
                        console.print("[bold red]Error:[/bold red] Is_Sensitive column not found in the data.")
                        continue
                    
                    # Count sensitive and non-sensitive URLs
                    sensitive_count = df['Is_Sensitive'].sum() if df['Is_Sensitive'].dtype == bool else 0
                    non_sensitive_count = len(df) - sensitive_count
                    
                    # Calculate percentages
                    sensitive_pct = sensitive_count / len(df) * 100
                    non_sensitive_pct = non_sensitive_count / len(df) * 100
                    
                    # Create a simple pie chart
                    console.print("\n[bold]Sensitivity Distribution:[/bold]")
                    
                    # Create a visual representation
                    total_chars = 50
                    sensitive_chars = int(sensitive_pct / 100 * total_chars)
                    non_sensitive_chars = total_chars - sensitive_chars
                    
                    # Print the chart
                    console.print(
                        f"[bold red]{'█' * sensitive_chars}[/bold red]"
                        f"[bold green]{'█' * non_sensitive_chars}[/bold green]"
                    )
                    console.print(
                        f"[bold red]Sensitive:[/bold red] {sensitive_count:,} ({sensitive_pct:.1f}%)"
                    )
                    console.print(
                        f"[bold green]Non-Sensitive:[/bold green] {non_sensitive_count:,} ({non_sensitive_pct:.1f}%)"
                    )
                
                elif viz_choice == "4":  # URL Length Histogram
                    # Check if we have a URL column
                    url_col = next((col for col in df.columns if col.lower() in ['url', 'domain_name']), None)
                    if not url_col:
                        console.print("[bold red]Error:[/bold red] URL column not found in the data.")
                        continue
                    
                    # Calculate URL lengths
                    df['url_length'] = df[url_col].astype(str).str.len()
                    
                    # Create bins for the histogram
                    bins = [0, 20, 40, 60, 80, 100, 150, 200, 500, 1000, float('inf')]
                    labels = ['0-20', '21-40', '41-60', '61-80', '81-100', '101-150', '151-200', '201-500', '501-1000', '1000+']
                    
                    # Count URLs in each bin
                    hist_data = pd.cut(df['url_length'], bins=bins, labels=labels).value_counts().sort_index()
                    
                    # Create a simple histogram
                    console.print("\n[bold]URL Length Distribution:[/bold]")
                    
                    # Get the maximum count for scaling
                    max_count = hist_data.max()
                    
                    # Create the chart
                    for length_range, count in hist_data.items():
                        # Calculate bar length (max 40 characters)
                        bar_len = int((count / max_count) * 40)
                        
                        # Choose color based on URL length
                        if 'short' in str(length_range).lower() or '0-' in str(length_range):
                            color = "green"
                        elif 'long' in str(length_range).lower() or '1000+' in str(length_range):
                            color = "red"
                        else:
                            color = "blue"
                        
                        # Print the bar
                        console.print(
                            f"{str(length_range).ljust(10)} | "
                            f"[bold {color}]{'█' * bar_len}[/bold {color}] "
                            f"{count:,} ({count/len(df)*100:.1f}%)"
                        )
                
                elif viz_choice == "5":  # Return to Exploration Menu
                    continue
            
            elif choice == "8":  # Return to Main Menu
                break
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception(f"Error in explore_data_workflow: {e}")
    
    input("\nPress Enter to continue...")


def run_interactive_mode() -> int:
    """
    Run the interactive mode.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Check if required dependencies are available
    if not check_dependencies():
        return 1
    
    try:
        # Display welcome screen
        display_welcome_screen()
        
        while True:
            # Display main menu and get selection
            selection = display_main_menu()
            
            if selection == "Analyze URLs":
                analyze_urls_workflow()
            elif selection == "Generate Reports":
                generate_reports_workflow()
            elif selection == "Export Data":
                export_data_workflow()
            elif selection == "Explore Data":
                explore_data_workflow()
            elif selection == "Configure Application":
                configure_application_workflow()
            elif selection == "View Templates":
                view_templates_workflow()
            elif selection == "Exit":
                console.print("[bold blue]Thank you for using URL Analyzer![/bold blue]")
                return 0
    except KeyboardInterrupt:
        console.print("\n[bold blue]Exiting URL Analyzer Interactive Mode...[/bold blue]")
        return 0
    except Exception as e:
        logger.exception(f"Error in interactive mode: {e}")
        if console:
            console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            print(f"Error: {e}")
        return 1


def main() -> int:
    """
    Main entry point for the interactive CLI.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    return run_interactive_mode()


if __name__ == "__main__":
    sys.exit(main())