# URL Analyzer

A powerful tool for analyzing, categorizing, and reporting on URLs from browsing history or other sources.

![URL Analyzer](https://img.shields.io/badge/URL-Analyzer-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

URL Analyzer helps you understand web browsing patterns, identify potentially sensitive websites, and generate comprehensive reports with visualizations. It provides powerful classification, analysis, and reporting capabilities for URL data.

### Key Features

- **URL Classification**: Automatically categorize URLs using pattern matching and custom rules
- **Batch Processing**: Process multiple files with parallel execution for efficiency
- **Live Scanning**: Fetch additional information about uncategorized URLs
- **Content Summarization**: Generate AI-powered summaries of web page content
- **Interactive Reports**: Create rich HTML reports with charts, tables, and visualizations
- **Multiple Report Templates**: Choose from various templates for different use cases
- **Data Export**: Export analyzed data to CSV, JSON, or Excel formats
- **Customizable Rules**: Define custom classification rules for your specific needs
- **Memory Optimization**: Process large files efficiently with chunked processing

## Installation

### Requirements

- Python 3.8 or higher
- Required dependencies (installed automatically)

### Installation Steps

#### From PyPI (Recommended)

Install the latest stable version from PyPI:

```bash
pip install hibber-url-analyzer
```

#### Optional Dependencies

For additional features, install optional dependencies:

```bash
# For all features
pip install hibber-url-analyzer[all]

# For specific features
pip install hibber-url-analyzer[url_fetching,html_parsing,visualization]
```

Available optional dependency groups:
- `url_fetching`: For fetching URL content
- `html_parsing`: For parsing HTML content
- `domain_extraction`: For advanced domain analysis
- `visualization`: For enhanced charts and graphs
- `geolocation`: For IP geolocation features
- `pdf_export`: For PDF report generation
- `progress`: For progress bars
- `excel`: For Excel file support
- `terminal_ui`: For rich terminal interface
- `system`: For system monitoring
- `ml_analysis`: For machine learning analysis features
- `dev`: For development tools

#### From Source

For development or latest features:

```bash
git clone https://github.com/yourusername/url-analyzer.git
cd url-analyzer
pip install -e .
```

#### Environment Variables (Optional)

Set up environment variables for enhanced features:

- `GEMINI_API_KEY`: For content summarization features
- `URL_ANALYZER_CONFIG_PATH`: Custom path to configuration file
- `URL_ANALYZER_CACHE_PATH`: Custom path to cache file

## Quick Start

### Analyzing a Single File

To analyze a CSV or Excel file containing URLs:

```
python -m url_analyzer analyze --path "path/to/file.csv"
```

This will:
1. Process the file and classify URLs
2. Generate an HTML report
3. Open the report in your default web browser

### Required File Format

Your input file should be a CSV or Excel file with at least one column named `Domain_name` containing the URLs to analyze. Additional columns that enhance the analysis include:

- `Client_Name`: Name of the device or user
- `MAC_address`: MAC address of the device
- `Access_time`: Timestamp of when the URL was accessed

### Basic Command Options

The basic command can be enhanced with various options:

- `--live-scan`: Fetch additional information about uncategorized URLs
- `--summarize`: Generate AI-powered summaries of web page content (requires `--live-scan`)
- `--aggregate`: Generate a single report for multiple files
- `--output PATH`: Specify output directory for reports
- `--no-open`: Don't automatically open the report in browser

Example with options:
```
python -m url_analyzer analyze --path "path/to/file.csv" --live-scan --summarize --output "reports"
```

## Advanced Features

### Batch Processing

To process multiple files at once:

```
python -m url_analyzer analyze --path "path/to/directory" --aggregate
```

This will process all CSV and Excel files in the directory and generate a single aggregated report.

Batch processing options:
- `--job-id ID`: Assign a unique identifier to the batch job
- `--max-workers N`: Set maximum number of parallel workers (default: 20)
- `--checkpoint-interval N`: Minutes between saving checkpoints (default: 5)

### Report Templates

URL Analyzer provides several built-in report templates for different use cases:

```
python -m url_analyzer templates
```

This will list all available templates with descriptions.

To use a specific template:

```
python -m url_analyzer analyze --path "path/to/file.csv" --template "template_name"
```

#### Available Templates

- **Default**: Comprehensive template with all report sections and visualizations
- **Minimal**: Simplified template with a clean, streamlined design
- **Data Analytics**: Data-focused template with additional metrics and insights
- **Security Focus**: Security-oriented template with security metrics and recommendations
- **Executive Summary**: High-level overview for executives with key metrics and insights
- **Print Friendly**: Optimized for printing with simplified layout and print-specific styling

### Exporting Data

Export analyzed data to different formats:

```
python -m url_analyzer export --path "path/to/file.csv" --format json
```

Supported formats: `csv`, `json`, `excel`

### Configuration

Configure the application settings:

```
python -m url_analyzer configure
```

This opens an interactive configuration interface where you can:
- View current settings
- Add or modify URL classification patterns
- Configure API settings
- Set scan parameters

## Understanding the Report

The HTML report provides a comprehensive view of your URL data:

### Dashboard Section
- Doughnut chart showing URL categories
- Statistics including total URLs, sensitive URLs, etc.

### Domain & Time Insights
- Top 10 visited domains chart
- Traffic flow analysis (Sankey diagram)
- Activity heatmap by day and hour
- Daily URL access trend

### Detailed URL Data
- Interactive table with all URLs
- Filtering by client name or MAC address
- Export options (CSV, JSON)
- Dark/light theme toggle

## URL Classification

URLs are classified into several categories:

- **Sensitive**: URLs matching patterns for social media, adult content, etc.
- **User-Generated**: URLs containing user content patterns like profiles, forums, etc.
- **Advertising**: Ad-related domains and services
- **Analytics**: Tracking and analytics services
- **CDN**: Content delivery networks
- **Corporate**: Business and corporate sites
- **Uncategorized**: URLs that don't match any defined patterns

## Custom URL Classification Rules

You can define custom classification rules in the configuration file (`config.json`):

```json
{
  "custom_rules": [
    {
      "pattern": "news\\.google\\.com",
      "category": "News",
      "priority": 120,
      "is_sensitive": false,
      "description": "Google News"
    }
  ]
}
```

For more information on custom rules, see the [Custom Rules Documentation](docs/custom_rules.md).

## Troubleshooting

### Common Issues

1. **Missing dependencies**:
   - Ensure you've installed all required dependencies with `pip install -r requirements.txt`
   - For advanced features, make sure optional dependencies are installed

2. **File format issues**:
   - Verify your input file has a `Domain_name` column
   - Check for encoding issues in CSV files

3. **Performance with large files**:
   - Use the `--max-workers` option to adjust parallel processing
   - Consider splitting very large files into smaller chunks

4. **API key issues**:
   - Set the `GEMINI_API_KEY` environment variable for summarization features

### Getting Help

If you encounter issues not covered here:
1. Check the logs for detailed error messages
2. Consult the [documentation](docs/)
3. Submit an issue on the project repository

## Command Reference

### Main Commands

- `analyze`: Process files and generate reports
- `configure`: Manage application configuration
- `export`: Export data to different formats
- `report`: Generate reports from previously analyzed data
- `templates`: List available report templates

### Global Options

- `--verbose`, `-v`: Increase output verbosity
- `--quiet`, `-q`: Suppress non-error output
- `--log-file PATH`: Specify log file path

For a complete list of commands and options, run:
```
python -m url_analyzer --help
```

## Documentation

- [User Instructions](docs/user_instructions.md): Detailed user guide
- [Custom Rules](docs/custom_rules.md): Guide to creating custom classification rules
- [Batch Processing](docs/batch_processing.md): Advanced batch processing options
- [Configuration Guide](docs/configuration.md): Detailed configuration options

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped improve this project
- Special thanks to the open-source libraries that made this project possible