"""
Command-Line Interface for Log Monitoring

This module provides a command-line interface for monitoring log files,
generating alerts, and analyzing log data.
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.log_monitor import (
    LogMonitor, AlertNotifier, create_default_monitor, setup_console_monitoring
)

# Create logger
logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="URL Analyzer Log Monitor - Monitor and analyze log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor the default log file with console alerts
  python -m url_analyzer.cli.log_monitor_cli monitor
  
  # Monitor a specific log file
  python -m url_analyzer.cli.log_monitor_cli monitor --log-file "path/to/log/file.log"
  
  # Analyze a log file and generate a report
  python -m url_analyzer.cli.log_monitor_cli analyze --log-file "path/to/log/file.log"
  
  # Generate a visualization of log data
  python -m url_analyzer.cli.log_monitor_cli visualize --log-file "path/to/log/file.log"
"""
    )
    
    # Add global options
    parser.add_argument('--verbose', '-v', action='count', default=0,
                       help="Increase verbosity (can be used multiple times)")
    parser.add_argument('--quiet', '-q', action='store_true',
                       help="Suppress non-error output")
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor a log file in real-time')
    monitor_parser.add_argument('--log-file', default="logs/url_analyzer.log",
                              help="Path to the log file to monitor (default: logs/url_analyzer.log)")
    monitor_parser.add_argument('--error-threshold', type=int, default=5,
                              help="Number of errors per minute to trigger an alert (default: 5)")
    monitor_parser.add_argument('--performance-threshold', type=float, default=2.0,
                              help="Performance multiplier to trigger an alert (default: 2.0)")
    monitor_parser.add_argument('--check-interval', type=float, default=1.0,
                              help="Interval in seconds between log checks (default: 1.0)")
    monitor_parser.add_argument('--stats-interval', type=int, default=60,
                              help="Interval in seconds between stats reports (default: 60)")
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a log file and generate a report')
    analyze_parser.add_argument('--log-file', required=True,
                              help="Path to the log file to analyze")
    analyze_parser.add_argument('--output', '-o',
                              help="Path to the output report file (default: log_analysis_YYYYMMDD.md)")
    analyze_parser.add_argument('--format', choices=['text', 'markdown', 'html'], default='markdown',
                              help="Output format (default: markdown)")
    
    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Generate visualizations of log data')
    visualize_parser.add_argument('--log-file', required=True,
                                help="Path to the log file to visualize")
    visualize_parser.add_argument('--output', '-o',
                                help="Path to the output image file (default: log_visualization_YYYYMMDD.png)")
    
    return parser


def handle_monitor_command(args: argparse.Namespace) -> int:
    """
    Handle the 'monitor' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Starting log monitor for {args.log_file}")
    
    try:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(args.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Set up console monitoring
        monitor, notifier = setup_console_monitoring(args.log_file)
        
        # Update monitor settings
        monitor.error_threshold = args.error_threshold
        monitor.performance_threshold = args.performance_threshold
        monitor.check_interval = args.check_interval
        monitor.stats_interval = args.stats_interval
        
        # Add stats callback
        def print_stats(stats):
            print("\n=== Log Statistics ===")
            print(f"Time window: {stats['window_seconds']:.1f} seconds")
            print(f"Error count: {stats['error_count']}")
            print(f"Warning count: {stats['warning_count']}")
            print(f"Info count: {stats['info_count']}")
            print(f"Error rate: {stats['error_rate_per_minute']:.2f} per minute")
            print(f"Warning rate: {stats['warning_rate_per_minute']:.2f} per minute")
            print(f"Performance stats: {len(stats['performance'])} operations")
            print("=====================\n")
        
        monitor.register_stats_callback(print_stats)
        
        # Print startup message
        print(f"Monitoring log file: {args.log_file}")
        print("Press Ctrl+C to stop...")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            monitor.stop()
            print("Monitor stopped.")
        
        return 0
    except Exception as e:
        logger.exception(f"Error monitoring log file: {e}")
        print(f"❌ Error monitoring log file: {e}")
        return 1


def handle_analyze_command(args: argparse.Namespace) -> int:
    """
    Handle the 'analyze' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Analyzing log file: {args.log_file}")
    
    try:
        # Check if file exists
        if not os.path.exists(args.log_file):
            logger.error(f"Log file not found: {args.log_file}")
            print(f"❌ Log file not found: {args.log_file}")
            return 1
        
        # Create analyzer
        from url_analyzer.utils.logging import LogAnalyzer
        analyzer = LogAnalyzer(args.log_file)
        
        # Parse the log file
        entries = analyzer.parse_file()
        print(f"Parsed {len(entries)} log entries")
        
        # Get statistics
        stats = analyzer.get_statistics()
        
        # Print summary statistics
        print("\n=== Log Statistics ===")
        print(f"Total entries: {stats.get('total_entries', 0)}")
        
        if 'level_counts' in stats:
            print("\nLog Levels:")
            for level, count in stats['level_counts'].items():
                print(f"  {level}: {count}")
        
        if 'source_counts' in stats:
            print("\nLog Sources:")
            for source, count in stats['source_counts'].items():
                print(f"  {source}: {count}")
        
        if 'time_range' in stats and stats['time_range']:
            print("\nTime Range:")
            print(f"  Start: {stats['time_range'].get('start')}")
            print(f"  End: {stats['time_range'].get('end')}")
            print(f"  Duration: {stats['time_range'].get('duration')}")
        
        # Generate report
        if args.output:
            output_file = args.output
        else:
            date_str = datetime.now().strftime("%Y%m%d")
            output_file = f"log_analysis_{date_str}.md"
        
        report_path = analyzer.generate_report(output_file)
        print(f"\n✅ Report generated: {report_path}")
        
        return 0
    except Exception as e:
        logger.exception(f"Error analyzing log file: {e}")
        print(f"❌ Error analyzing log file: {e}")
        return 1


def handle_visualize_command(args: argparse.Namespace) -> int:
    """
    Handle the 'visualize' command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger.info(f"Visualizing log file: {args.log_file}")
    
    try:
        # Check if file exists
        if not os.path.exists(args.log_file):
            logger.error(f"Log file not found: {args.log_file}")
            print(f"❌ Log file not found: {args.log_file}")
            return 1
        
        # Check if matplotlib is installed
        try:
            import matplotlib
        except ImportError:
            logger.error("Matplotlib is required for visualization")
            print("❌ Matplotlib is required for visualization. Install it with 'pip install matplotlib'")
            return 1
        
        # Create analyzer
        from url_analyzer.utils.logging import LogAnalyzer
        analyzer = LogAnalyzer(args.log_file)
        
        # Parse the log file
        entries = analyzer.parse_file()
        print(f"Parsed {len(entries)} log entries")
        
        # Determine output path
        if args.output:
            output_file = args.output
        else:
            date_str = datetime.now().strftime("%Y%m%d")
            output_file = f"log_visualization_{date_str}.png"
        
        # Generate visualization
        viz_path = analyzer.visualize(output_file)
        
        if viz_path:
            print(f"\n✅ Visualization generated: {viz_path}")
        else:
            print("\n❌ Failed to generate visualization")
            return 1
        
        return 0
    except Exception as e:
        logger.exception(f"Error visualizing log file: {e}")
        print(f"❌ Error visualizing log file: {e}")
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
    
    # Configure logging based on verbosity
    from url_analyzer.utils.logging import setup_logging
    
    if args.quiet:
        log_level = "ERROR"
    elif args.verbose == 0:
        log_level = "INFO"
    elif args.verbose == 1:
        log_level = "DEBUG"
    else:
        log_level = "DEBUG"  # More detailed debug for verbosity > 1
    
    setup_logging(log_level=log_level, console=not args.quiet)
    
    # Handle commands
    if args.command == 'monitor':
        return handle_monitor_command(args)
    elif args.command == 'analyze':
        return handle_analyze_command(args)
    elif args.command == 'visualize':
        return handle_visualize_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())