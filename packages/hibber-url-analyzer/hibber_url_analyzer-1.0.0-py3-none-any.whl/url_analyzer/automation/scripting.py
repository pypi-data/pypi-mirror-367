"""
Scripting Module

This module provides scripting interfaces for the URL Analyzer, allowing users to
create and run scripts for automating URL analysis tasks. It includes a script runner,
script templates, and utilities for managing scripts.
"""

import os
import sys
import json
import importlib.util
import inspect
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict

from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.errors import ScriptingError, AutomationError

# Create logger
logger = get_logger(__name__)

# Default path for storing scripts
DEFAULT_SCRIPTS_DIR = os.path.join(os.path.expanduser("~"), ".url_analyzer", "scripts")


@dataclass
class ScriptInfo:
    """
    Information about a script.
    
    Attributes:
        name: Name of the script
        path: Path to the script file
        description: Description of the script
        author: Author of the script
        version: Version of the script
        tags: Tags for categorizing the script
        parameters: Parameters that the script accepts
        created_at: Timestamp when the script was created
        updated_at: Timestamp when the script was last updated
    """
    name: str
    path: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the script info to a dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScriptInfo':
        """Create script info from a dictionary."""
        return cls(**data)
    
    @classmethod
    def from_script(cls, script_path: str) -> 'ScriptInfo':
        """
        Extract script information from a script file.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            ScriptInfo object with information extracted from the script
            
        Raises:
            ScriptingError: If the script cannot be loaded or is invalid
        """
        try:
            # Get the script name from the filename
            script_name = os.path.splitext(os.path.basename(script_path))[0]
            
            # Load the script module
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec is None or spec.loader is None:
                raise ScriptingError(f"Could not load script: {script_path}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract script information
            description = getattr(module, "__doc__", "").strip() or None
            author = getattr(module, "__author__", None)
            version = getattr(module, "__version__", "1.0.0")
            tags = getattr(module, "__tags__", [])
            
            # Extract parameters from the main function
            parameters = {}
            if hasattr(module, "main") and callable(module.main):
                sig = inspect.signature(module.main)
                for param_name, param in sig.parameters.items():
                    if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY):
                        param_info = {
                            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                            "default": None if param.default == inspect.Parameter.empty else param.default,
                            "required": param.default == inspect.Parameter.empty
                        }
                        parameters[param_name] = param_info
            
            # Get file timestamps
            stat = os.stat(script_path)
            created_at = stat.st_ctime
            updated_at = stat.st_mtime
            
            return cls(
                name=script_name,
                path=script_path,
                description=description,
                author=author,
                version=version,
                tags=tags,
                parameters=parameters,
                created_at=created_at,
                updated_at=updated_at
            )
        except Exception as e:
            raise ScriptingError(f"Error loading script {script_path}: {e}")


class ScriptRunner:
    """
    Runs URL Analyzer scripts.
    
    This class provides functionality for running scripts that automate URL analysis
    tasks. It handles script loading, parameter validation, and execution.
    """
    
    def __init__(self, scripts_dir: str = DEFAULT_SCRIPTS_DIR):
        """
        Initialize the script runner.
        
        Args:
            scripts_dir: Directory containing scripts
        """
        self.scripts_dir = scripts_dir
        self._ensure_scripts_dir()
    
    def _ensure_scripts_dir(self) -> None:
        """Ensure the scripts directory exists."""
        os.makedirs(self.scripts_dir, exist_ok=True)
    
    def list_scripts(self) -> List[ScriptInfo]:
        """
        List all available scripts.
        
        Returns:
            List of ScriptInfo objects for all available scripts
        """
        scripts = []
        
        # Ensure the scripts directory exists
        self._ensure_scripts_dir()
        
        # Find all Python files in the scripts directory
        for filename in os.listdir(self.scripts_dir):
            if filename.endswith(".py"):
                script_path = os.path.join(self.scripts_dir, filename)
                try:
                    script_info = ScriptInfo.from_script(script_path)
                    scripts.append(script_info)
                except Exception as e:
                    logger.warning(f"Error loading script {script_path}: {e}")
        
        return scripts
    
    def get_script(self, script_name: str) -> Optional[ScriptInfo]:
        """
        Get information about a script.
        
        Args:
            script_name: Name of the script (without .py extension)
            
        Returns:
            ScriptInfo object for the script, or None if not found
        """
        script_path = os.path.join(self.scripts_dir, f"{script_name}.py")
        if not os.path.exists(script_path):
            return None
        
        try:
            return ScriptInfo.from_script(script_path)
        except Exception as e:
            logger.warning(f"Error loading script {script_path}: {e}")
            return None
    
    def run_script(self, script_name: str, args: Optional[List[str]] = None) -> Any:
        """
        Run a script.
        
        Args:
            script_name: Name of the script (without .py extension)
            args: Command-line arguments to pass to the script
            
        Returns:
            The return value from the script's main function
            
        Raises:
            ScriptingError: If the script cannot be run
        """
        script_path = os.path.join(self.scripts_dir, f"{script_name}.py")
        if not os.path.exists(script_path):
            raise ScriptingError(f"Script not found: {script_name}")
        
        try:
            # Load the script module
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec is None or spec.loader is None:
                raise ScriptingError(f"Could not load script: {script_path}")
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[script_name] = module
            spec.loader.exec_module(module)
            
            # Check if the script has a main function
            if not hasattr(module, "main") or not callable(module.main):
                raise ScriptingError(f"Script {script_name} does not have a main function")
            
            # Set up command-line arguments
            original_argv = sys.argv
            if args is not None:
                sys.argv = [script_path] + args
            
            try:
                # Run the script's main function
                return module.main()
            finally:
                # Restore original command-line arguments
                sys.argv = original_argv
        except Exception as e:
            if isinstance(e, ScriptingError):
                raise
            raise ScriptingError(f"Error running script {script_name}: {e}")
    
    def create_script(self, script_name: str, template: str = "basic") -> str:
        """
        Create a new script from a template.
        
        Args:
            script_name: Name of the new script (without .py extension)
            template: Name of the template to use
            
        Returns:
            Path to the created script
            
        Raises:
            ScriptingError: If the script cannot be created
        """
        script_path = os.path.join(self.scripts_dir, f"{script_name}.py")
        
        # Check if the script already exists
        if os.path.exists(script_path):
            raise ScriptingError(f"Script {script_name} already exists")
        
        # Ensure the scripts directory exists
        self._ensure_scripts_dir()
        
        # Get the template content
        template_content = self._get_template_content(template)
        
        # Write the script file
        try:
            with open(script_path, "w") as f:
                f.write(template_content)
            
            logger.info(f"Created script: {script_path}")
            return script_path
        except Exception as e:
            raise ScriptingError(f"Error creating script {script_name}: {e}")
    
    def _get_template_content(self, template: str) -> str:
        """
        Get the content of a script template.
        
        Args:
            template: Name of the template
            
        Returns:
            Content of the template
            
        Raises:
            ScriptingError: If the template is not found
        """
        templates = {
            "basic": """#!/usr/bin/env python
\"\"\"
Basic URL Analyzer Script

This script demonstrates the basic structure of a URL Analyzer script.
\"\"\"

__author__ = "Your Name"
__version__ = "1.0.0"
__tags__ = ["example", "basic"]

import sys
from typing import List, Optional

from url_analyzer.core.classification import classify_url
from url_analyzer.core.analysis import fetch_url_data
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


def main() -> int:
    \"\"\"
    Main entry point for the script.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    \"\"\"
    logger.info("Running basic URL Analyzer script")
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m url_analyzer.automation.run_script basic <url>")
        return 1
    
    url = sys.argv[1]
    logger.info(f"Analyzing URL: {url}")
    
    # Classify the URL
    category, is_sensitive = classify_url(url)
    print(f"URL: {url}")
    print(f"Category: {category}")
    print(f"Sensitive: {is_sensitive}")
    
    # Fetch URL data if requested
    if len(sys.argv) > 2 and sys.argv[2] == "--fetch":
        logger.info(f"Fetching URL data: {url}")
        status_code, data = fetch_url_data(url)
        print(f"Status Code: {status_code}")
        if status_code == 200:
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Description: {data.get('description', 'N/A')}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
""",
            "batch": """#!/usr/bin/env python
\"\"\"
Batch Processing Script

This script demonstrates how to process multiple URLs in batch mode.
\"\"\"

__author__ = "Your Name"
__version__ = "1.0.0"
__tags__ = ["example", "batch"]

import sys
import csv
from typing import List, Dict, Any, Optional

from url_analyzer.core.classification import classify_url
from url_analyzer.data.processing import process_file
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


def process_urls(urls: List[str], output_file: Optional[str] = None) -> List[Dict[str, Any]]:
    \"\"\"
    Process a list of URLs.
    
    Args:
        urls: List of URLs to process
        output_file: Optional path to output CSV file
        
    Returns:
        List of dictionaries with URL analysis results
    \"\"\"
    results = []
    
    for url in urls:
        logger.info(f"Processing URL: {url}")
        category, is_sensitive = classify_url(url)
        
        result = {
            "URL": url,
            "Category": category,
            "Sensitive": is_sensitive
        }
        
        results.append(result)
        print(f"URL: {url}, Category: {category}, Sensitive: {is_sensitive}")
    
    # Write results to CSV if output file is specified
    if output_file:
        with open(output_file, "w", newline="") as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        logger.info(f"Results written to {output_file}")
    
    return results


def main() -> int:
    \"\"\"
    Main entry point for the script.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    \"\"\"
    logger.info("Running batch processing script")
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m url_analyzer.automation.run_script batch <url_file> [output_file]")
        return 1
    
    url_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Read URLs from file
        with open(url_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
        
        logger.info(f"Processing {len(urls)} URLs from {url_file}")
        
        # Process the URLs
        results = process_urls(urls, output_file)
        
        logger.info(f"Processed {len(results)} URLs")
        return 0
    except Exception as e:
        logger.error(f"Error processing URLs: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
""",
            "report": """#!/usr/bin/env python
\"\"\"
Report Generation Script

This script demonstrates how to generate custom reports from URL analysis data.
\"\"\"

__author__ = "Your Name"
__version__ = "1.0.0"
__tags__ = ["example", "report"]

import sys
import os
import pandas as pd
from typing import Dict, Any, Optional

from url_analyzer.data.processing import process_file, print_summary
from url_analyzer.reporting.generators import ReportGeneratorFactory
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)


def generate_report(
    input_file: str,
    output_file: Optional[str] = None,
    template: str = "default",
    title: Optional[str] = None
) -> str:
    \"\"\"
    Generate a report from URL analysis data.
    
    Args:
        input_file: Path to input file (CSV or Excel)
        output_file: Path to output HTML file (default: input_file with .html extension)
        template: Report template to use
        title: Custom title for the report
        
    Returns:
        Path to the generated report
    \"\"\"
    logger.info(f"Generating report from {input_file} using template {template}")
    
    # Determine output file path
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + ".html"
    
    # Read the input file
    if input_file.lower().endswith(".csv"):
        df = pd.read_csv(input_file)
    elif input_file.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(input_file)
    else:
        raise ValueError(f"Unsupported file format: {input_file}")
    
    # Calculate statistics
    stats = print_summary(df)
    
    # Create report generator
    report_generator = ReportGeneratorFactory.create_generator("html", template)
    
    # Generate the report
    report_path = report_generator.generate_report(
        df,
        output_file,
        stats,
        title=title
    )
    
    logger.info(f"Report generated: {report_path}")
    return report_path


def main() -> int:
    \"\"\"
    Main entry point for the script.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    \"\"\"
    logger.info("Running report generation script")
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m url_analyzer.automation.run_script report <input_file> [output_file] [--template TEMPLATE] [--title TITLE]")
        return 1
    
    input_file = sys.argv[1]
    
    # Parse optional arguments
    output_file = None
    template = "default"
    title = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            if sys.argv[i] == "--template" and i + 1 < len(sys.argv):
                template = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--title" and i + 1 < len(sys.argv):
                title = sys.argv[i + 1]
                i += 2
            else:
                print(f"Unknown option: {sys.argv[i]}")
                i += 1
        else:
            output_file = sys.argv[i]
            i += 1
    
    try:
        # Generate the report
        report_path = generate_report(input_file, output_file, template, title)
        
        print(f"Report generated: {report_path}")
        
        # Open the report in a web browser
        if os.name == "nt":  # Windows
            os.system(f"start {report_path}")
        elif os.name == "posix":  # macOS or Linux
            if sys.platform == "darwin":  # macOS
                os.system(f"open {report_path}")
            else:  # Linux
                os.system(f"xdg-open {report_path}")
        
        return 0
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
"""
        }
        
        if template not in templates:
            raise ScriptingError(f"Template not found: {template}")
        
        return templates[template]


# Global script runner instance
_script_runner = None


def get_script_runner() -> ScriptRunner:
    """
    Get the global script runner instance.
    
    Returns:
        The global script runner instance
    """
    global _script_runner
    if _script_runner is None:
        _script_runner = ScriptRunner()
    return _script_runner


def run_script(script_name: str, args: Optional[List[str]] = None) -> Any:
    """
    Run a script.
    
    Args:
        script_name: Name of the script (without .py extension)
        args: Command-line arguments to pass to the script
        
    Returns:
        The return value from the script's main function
    """
    script_runner = get_script_runner()
    return script_runner.run_script(script_name, args)


def list_available_scripts() -> List[Dict[str, Any]]:
    """
    List all available scripts.
    
    Returns:
        List of dictionaries with script information
    """
    script_runner = get_script_runner()
    return [script.to_dict() for script in script_runner.list_scripts()]


def create_script_template(script_name: str, template: str = "basic") -> str:
    """
    Create a new script from a template.
    
    Args:
        script_name: Name of the new script (without .py extension)
        template: Name of the template to use
        
    Returns:
        Path to the created script
    """
    script_runner = get_script_runner()
    return script_runner.create_script(script_name, template)