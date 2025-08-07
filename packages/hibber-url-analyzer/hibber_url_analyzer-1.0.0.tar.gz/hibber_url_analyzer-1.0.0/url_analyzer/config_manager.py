"""
Configuration Manager for URL Analyzer

This module handles loading, validating, and accessing configuration settings
for the URL Analyzer application. It supports:
- Loading configuration from JSON files
- Environment variable overrides for sensitive settings
- Configuration validation
- Default configuration generation
"""

import os
import json
import re
from typing import Dict, Any, Optional, List, Union

from url_analyzer.utils.errors import (
    URLAnalyzerError, ConfigurationError, ValidationError,
    InvalidConfigurationError, MissingConfigurationError
)
from url_analyzer.utils.validation import (
    validate_string, validate_file_path, validate_json,
    validate_dict, validate_params, validate_file_param,
    validate_list, validate_integer, validate_float
)
from url_analyzer.utils.sanitization import sanitize_path, sanitize_json_string

# Rich imports for interactive configuration management
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
    from rich.table import Table
    from rich import print as rich_print
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@validate_params
def get_env_var(name: str, default: Any = None) -> Any:
    """
    Get an environment variable with a default fallback.
    
    Args:
        name: Name of the environment variable
        default: Default value if environment variable is not set
        
    Returns:
        The value of the environment variable or the default
    """
    # Validate the name parameter
    try:
        name = validate_string(name, allow_empty=False, 
                              error_message="Environment variable name cannot be empty")
    except ValidationError as e:
        raise ConfigurationError(f"Invalid environment variable name: {str(e)}")
    
    return os.environ.get(name, default)


@validate_file_param(param_name='config_path', must_exist=False)
def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from a JSON file or create a default one if it doesn't exist.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration settings
        
    Raises:
        ConfigurationError: If there's an error loading or parsing the configuration
    """
    if not os.path.exists(config_path):
        print(f"👋 `{config_path}` not found. Creating a default one.")
        config_data = create_default_config()
        save_config(config_data, config_path)
        return config_data

    try:
        # Sanitize the path to prevent path traversal attacks
        safe_path = sanitize_path(config_path)
        
        with open(safe_path, 'r') as f:
            config_content = f.read()
            
        # Sanitize and validate the JSON content
        sanitized_content = sanitize_json_string(config_content)
        config_data = validate_json(sanitized_content)
        
        # Validate the loaded configuration
        validate_config(config_data)
        return config_data
    except json.JSONDecodeError as e:
        raise InvalidConfigurationError(f"Error parsing {config_path}: {e}")
    except ValidationError as e:
        raise InvalidConfigurationError(f"Invalid configuration in {config_path}: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading configuration: {e}")


@validate_file_param(param_name='config_path', must_exist=False)
def save_config(config_data: Dict[str, Any], config_path: str = 'config.json') -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config_data: Configuration dictionary to save
        config_path: Path where to save the configuration
        
    Raises:
        ConfigurationError: If there's an error saving the configuration
    """
    try:
        # Validate the configuration data
        validate_config(config_data)
        
        # Sanitize the path to prevent path traversal attacks
        safe_path = sanitize_path(config_path)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(safe_path)), exist_ok=True)
        
        with open(safe_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"✅ Configuration saved to {config_path}")
    except ValidationError as e:
        raise InvalidConfigurationError(f"Invalid configuration data: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error saving configuration to {config_path}: {e}")


def create_default_config() -> Dict[str, Any]:
    """
    Create a default configuration.
    
    Returns:
        Dictionary containing default configuration settings
    """
    return {
        "sensitive_patterns": [
            "facebook\\.com", "twitter\\.com", "instagram\\.com", "tiktok\\.com",
            "reddit\\.com", "linkedin\\.com", "pinterest\\.com", "snapchat\\.com",
            "onlyfans\\.com", "pornhub\\.com", "xvideos\\.com", "xnxx\\.com",
            "growlrapp\\.com", "badoo\\.com", "hornetapp\\.com", "gaydar\\.net",
            "jackd\\.mobi", "scruff\\.com", "benderapp\\.com"
        ],
        "ugc_patterns": [
            "/user/", "/profile/", "/author/", "/member/", "/u/", "/@[\\w-]+",
            "/forum/", "/thread/", "/topic/", "/discussion/", "/post/",
            "/q/", "/question/", "#comment-", "\\?commentid=", "/review/", "/ratings/"
        ],
        "junk_subcategories": {
            "Advertising": ["adservice", "doubleclick\\.net", "googleadservices\\.com"],
            "Analytics": ["analytics", "metrics", "tracking", "google-analytics\\.com"],
            "CDN": ["cdn", "fbcdn\\.net", "tiktokcdn", "akamaihd\\.net"],
            "Corporate": [
                "/about", "/contact", "/services", "/privacy", "/terms",
                "/promo/", "/offer/", "/login/", "/signup/", "/blog",
                "api[0-9]*-"
            ]
        },
        "api_settings": {
            "gemini_api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
        },
        "scan_settings": {
            "max_workers": 20,
            "timeout": 7,
            "cache_file": "scan_cache.json"
        }
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if the configuration is valid
        
    Raises:
        InvalidConfigurationError: If configuration structure is invalid
        MissingConfigurationError: If required configuration keys are missing
    """
    try:
        # Validate that config is a dictionary
        validate_dict(config, error_message="Configuration must be a dictionary")
        
        # Define required keys
        required_keys = ["sensitive_patterns", "ugc_patterns", "junk_subcategories"]
        
        # Validate required keys are present
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise MissingConfigurationError(
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )
        
        # Validate sensitive_patterns is a list of strings
        validate_list(
            config.get("sensitive_patterns", []),
            item_validator=lambda x: validate_string(x),
            error_message="sensitive_patterns must be a list of strings"
        )
        
        # Validate ugc_patterns is a list of strings
        validate_list(
            config.get("ugc_patterns", []),
            item_validator=lambda x: validate_string(x),
            error_message="ugc_patterns must be a list of strings"
        )
        
        # Validate junk_subcategories is a dictionary with string keys and list values
        junk_subcategories = config.get("junk_subcategories", {})
        validate_dict(
            junk_subcategories,
            key_validator=lambda x: validate_string(x),
            error_message="junk_subcategories must be a dictionary with string keys"
        )
        
        # Validate each category's patterns is a list of strings
        for category, patterns in junk_subcategories.items():
            validate_list(
                patterns,
                item_validator=lambda x: validate_string(x),
                error_message=f"Patterns for category '{category}' must be a list of strings"
            )
        
        # Ensure api_settings and scan_settings exist with defaults if not present
        if "api_settings" not in config:
            config["api_settings"] = create_default_config()["api_settings"]
        else:
            # Validate api_settings is a dictionary
            validate_dict(
                config["api_settings"],
                error_message="api_settings must be a dictionary"
            )
        
        if "scan_settings" not in config:
            config["scan_settings"] = create_default_config()["scan_settings"]
        else:
            # Validate scan_settings is a dictionary
            validate_dict(
                config["scan_settings"],
                error_message="scan_settings must be a dictionary"
            )
            
            # Validate max_workers is a positive integer
            if "max_workers" in config["scan_settings"]:
                validate_integer(
                    config["scan_settings"]["max_workers"],
                    min_value=1,
                    error_message="max_workers must be a positive integer"
                )
            
            # Validate timeout is a positive integer or float
            if "timeout" in config["scan_settings"]:
                validate_float(
                    config["scan_settings"]["timeout"],
                    min_value=0.1,
                    error_message="timeout must be a positive number"
                )
            
            # Validate cache_file is a string
            if "cache_file" in config["scan_settings"]:
                validate_string(
                    config["scan_settings"]["cache_file"],
                    error_message="cache_file must be a string"
                )
        
        return True
        
    except ValidationError as e:
        # Convert ValidationError to InvalidConfigurationError
        raise InvalidConfigurationError(str(e))


@validate_params
def get_api_key() -> Optional[str]:
    """
    Get the Gemini API key from environment variable with fallback to default.
    
    Returns:
        API key string or None if not set
    """
    api_key = get_env_var('GEMINI_API_KEY')
    
    if not api_key:
        print("\n⚠️ Warning: GEMINI_API_KEY environment variable not set.")
        print("    For security, set your own key as an environment variable:")
        print("    - Set GEMINI_API_KEY environment variable")
        print("    - Or create a .env file with GEMINI_API_KEY=your_api_key\n")
        return None
    
    # Validate the API key
    try:
        # API keys are typically strings with specific formats
        # Here we just validate that it's a non-empty string
        return validate_string(api_key, min_length=1, 
                              error_message="API key cannot be empty")
    except ValidationError as e:
        print(f"\n⚠️ Warning: Invalid API key: {e}")
        return None


@validate_params
def get_api_url(config: Dict[str, Any]) -> str:
    """
    Get the Gemini API URL from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        API URL string
        
    Raises:
        InvalidConfigurationError: If the API URL is invalid
    """
    try:
        # Validate the config parameter
        validate_dict(config, error_message="Configuration must be a dictionary")
        
        # Get the API URL from the configuration
        api_settings = config.get("api_settings", {})
        validate_dict(api_settings, error_message="api_settings must be a dictionary")
        
        api_url = api_settings.get("gemini_api_url")
        api_key = get_api_key()
        
        # If API URL is provided, validate it
        if api_url:
            # Validate and sanitize the URL
            from url_analyzer.utils.sanitization import sanitize_url
            try:
                api_url = sanitize_url(api_url, allowed_schemes=['https'])
            except ValidationError:
                # If URL validation fails, use the default URL
                default_url = create_default_config()["api_settings"]["gemini_api_url"]
                print(f"\n⚠️ Warning: Invalid API URL: {api_url}. Using default URL.")
                api_url = default_url
        else:
            # Fallback to default
            default_url = create_default_config()["api_settings"]["gemini_api_url"]
            api_url = default_url
        
        # Append API key if available
        if api_key:
            return f"{api_url}?key={api_key}"
        
        return api_url
        
    except ValidationError as e:
        # Convert ValidationError to InvalidConfigurationError
        raise InvalidConfigurationError(f"Invalid API URL configuration: {str(e)}")


@validate_params
def compile_patterns(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compile regex patterns from the configuration for performance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of compiled patterns
        
    Raises:
        InvalidConfigurationError: If the configuration is invalid
    """
    try:
        # Validate the config parameter
        validate_dict(config, error_message="Configuration must be a dictionary")
        
        # Validate required keys are present
        required_keys = ["sensitive_patterns", "ugc_patterns", "junk_subcategories"]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise MissingConfigurationError(
                f"Missing required configuration keys for pattern compilation: {', '.join(missing_keys)}"
            )
        
        # Validate sensitive_patterns is a list of strings
        validate_list(
            config.get("sensitive_patterns", []),
            item_validator=lambda x: validate_string(x),
            error_message="sensitive_patterns must be a list of strings"
        )
        
        # Validate ugc_patterns is a list of strings
        validate_list(
            config.get("ugc_patterns", []),
            item_validator=lambda x: validate_string(x),
            error_message="ugc_patterns must be a list of strings"
        )
        
        # Validate junk_subcategories is a dictionary with string keys and list values
        junk_subcategories = config.get("junk_subcategories", {})
        validate_dict(
            junk_subcategories,
            key_validator=lambda x: validate_string(x),
            error_message="junk_subcategories must be a dictionary with string keys"
        )
        
        # Compile the patterns
        return {
            'sensitive': re.compile('|'.join(config['sensitive_patterns']), re.IGNORECASE),
            'ugc': re.compile('|'.join(config['ugc_patterns']), re.IGNORECASE),
            'junk': {
                cat: re.compile('|'.join(cat_patterns), re.IGNORECASE)
                for cat, cat_patterns in config['junk_subcategories'].items()
            }
        }
    except ValidationError as e:
        # Convert ValidationError to InvalidConfigurationError
        raise InvalidConfigurationError(f"Invalid configuration for pattern compilation: {str(e)}")


def get_cache_file_path(config: Dict[str, Any]) -> str:
    """
    Get the cache file path from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Cache file path string
    """
    return config.get("scan_settings", {}).get("cache_file", "scan_cache.json")


def get_max_workers(config: Dict[str, Any]) -> int:
    """
    Get the maximum number of worker threads from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Maximum number of worker threads
    """
    return config.get("scan_settings", {}).get("max_workers", 20)


def get_request_timeout(config: Dict[str, Any]) -> float:
    """
    Get the request timeout from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Request timeout in seconds
    """
    return config.get("scan_settings", {}).get("timeout", 7)


def manage_configuration():
    """
    Interactive configuration management with real-time validation feedback.
    
    Provides a user-friendly interface for modifying configuration settings
    with immediate validation and feedback.
    """
    if not RICH_AVAILABLE:
        print("Error: Rich library is required for interactive configuration management.")
        print("Please install it with: pip install rich")
        return
        
    try:
        console = Console()
        
        # Load current configuration
        config_path = get_env_var('URL_ANALYZER_CONFIG_PATH', 'config.json')
        
        try:
            config = load_config(config_path)
            console.print(Panel(
                f"✅ Loaded configuration from: [cyan]{config_path}[/cyan]",
                title="Configuration Manager",
                border_style="green"
            ))
        except Exception as e:
            console.print(Panel(
                f"⚠️ Could not load configuration: {str(e)}\n"
                f"Creating new configuration...",
                title="Configuration Manager",
                border_style="yellow"
            ))
            config = create_default_config()
        
        while True:
            # Display current configuration
            console.print("\n" + "="*60)
            console.print("[bold blue]Current Configuration[/bold blue]")
            console.print("="*60)
            
            # Create a table to display configuration
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Setting", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")
            table.add_column("Description", style="dim")
            
            # Add configuration rows
            table.add_row(
                "Sensitive Patterns", 
                f"{len(config.get('sensitive_patterns', []))} patterns",
                "Patterns for sensitive URL detection"
            )
            table.add_row(
                "UGC Patterns", 
                f"{len(config.get('ugc_patterns', []))} patterns",
                "User-generated content patterns"
            )
            table.add_row(
                "Junk Categories", 
                f"{len(config.get('junk_subcategories', {}))} categories",
                "Junk URL classification categories"
            )
            table.add_row(
                "Max Workers", 
                str(config.get('scan_settings', {}).get('max_workers', 20)),
                "Maximum concurrent workers"
            )
            table.add_row(
                "Timeout", 
                f"{config.get('scan_settings', {}).get('timeout', 7)}s",
                "Request timeout in seconds"
            )
            table.add_row(
                "Cache File", 
                config.get('scan_settings', {}).get('cache_file', 'scan_cache.json'),
                "Cache file location"
            )
            
            console.print(table)
            
            # Menu options
            console.print("\n[bold yellow]Configuration Options:[/bold yellow]")
            console.print("1. Edit sensitive patterns")
            console.print("2. Edit UGC patterns") 
            console.print("3. Edit junk categories")
            console.print("4. Edit scan settings")
            console.print("5. Validate current configuration")
            console.print("6. Save configuration")
            console.print("7. Reset to defaults")
            console.print("8. Exit")
            
            choice = Prompt.ask(
                "\n[bold cyan]Select an option[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                default="8"
            )
            
            if choice == "1":
                _edit_patterns(console, config, "sensitive_patterns", "Sensitive Patterns")
            elif choice == "2":
                _edit_patterns(console, config, "ugc_patterns", "UGC Patterns")
            elif choice == "3":
                _edit_junk_categories(console, config)
            elif choice == "4":
                _edit_scan_settings(console, config)
            elif choice == "5":
                _validate_configuration(console, config)
            elif choice == "6":
                _save_configuration(console, config, config_path)
            elif choice == "7":
                if Confirm.ask("\n[yellow]Reset all settings to defaults?[/yellow]"):
                    config = create_default_config()
                    console.print(Panel(
                        "✅ Configuration reset to defaults",
                        title="Reset Complete",
                        border_style="green"
                    ))
            elif choice == "8":
                if Confirm.ask("\n[yellow]Exit without saving changes?[/yellow]"):
                    break
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration management cancelled.[/yellow]")
    except Exception as e:
        console.print(Panel(
            f"[red]Error in configuration management:[/red]\n{str(e)}",
            title="❌ Error",
            border_style="red"
        ))


def _edit_patterns(console, config: Dict[str, Any], pattern_key: str, pattern_name: str):
    """Edit pattern lists with real-time validation."""
    patterns = config.get(pattern_key, [])
    
    while True:
        console.print(f"\n[bold blue]{pattern_name}[/bold blue]")
        console.print("-" * len(pattern_name))
        
        for i, pattern in enumerate(patterns, 1):
            console.print(f"{i}. {pattern}")
        
        if not patterns:
            console.print("[dim]No patterns defined[/dim]")
        
        console.print(f"\n[yellow]Options:[/yellow]")
        console.print("1. Add pattern")
        console.print("2. Remove pattern")
        console.print("3. Edit pattern")
        console.print("4. Back to main menu")
        
        choice = Prompt.ask(
            "[cyan]Select option[/cyan]",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        
        if choice == "1":
            pattern = Prompt.ask("[cyan]Enter new pattern[/cyan]")
            if pattern:
                # Validate pattern in real-time
                try:
                    re.compile(pattern)
                    patterns.append(pattern)
                    config[pattern_key] = patterns
                    console.print(f"✅ Added pattern: [green]{pattern}[/green]")
                except re.error as e:
                    console.print(Panel(
                        f"[red]Invalid regex pattern:[/red]\n{str(e)}",
                        title="❌ Validation Error",
                        border_style="red"
                    ))
        elif choice == "2" and patterns:
            try:
                index = IntPrompt.ask(
                    f"[cyan]Enter pattern number to remove (1-{len(patterns)})[/cyan]",
                    default=1
                ) - 1
                if 0 <= index < len(patterns):
                    removed = patterns.pop(index)
                    config[pattern_key] = patterns
                    console.print(f"✅ Removed pattern: [red]{removed}[/red]")
                else:
                    console.print("[red]Invalid pattern number[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        elif choice == "3" and patterns:
            try:
                index = IntPrompt.ask(
                    f"[cyan]Enter pattern number to edit (1-{len(patterns)})[/cyan]",
                    default=1
                ) - 1
                if 0 <= index < len(patterns):
                    old_pattern = patterns[index]
                    new_pattern = Prompt.ask(
                        f"[cyan]Edit pattern[/cyan]",
                        default=old_pattern
                    )
                    if new_pattern:
                        # Validate pattern in real-time
                        try:
                            re.compile(new_pattern)
                            patterns[index] = new_pattern
                            config[pattern_key] = patterns
                            console.print(f"✅ Updated pattern: [green]{new_pattern}[/green]")
                        except re.error as e:
                            console.print(Panel(
                                f"[red]Invalid regex pattern:[/red]\n{str(e)}",
                                title="❌ Validation Error",
                                border_style="red"
                            ))
                else:
                    console.print("[red]Invalid pattern number[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        elif choice == "4":
            break


def _edit_junk_categories(console, config: Dict[str, Any]):
    """Edit junk categories with real-time validation."""
    junk_categories = config.get("junk_subcategories", {})
    
    while True:
        console.print(f"\n[bold blue]Junk Categories[/bold blue]")
        console.print("-" * 15)
        
        if junk_categories:
            for category, patterns in junk_categories.items():
                console.print(f"[cyan]{category}[/cyan]: {len(patterns)} patterns")
        else:
            console.print("[dim]No categories defined[/dim]")
        
        console.print(f"\n[yellow]Options:[/yellow]")
        console.print("1. Add category")
        console.print("2. Remove category")
        console.print("3. Edit category patterns")
        console.print("4. Back to main menu")
        
        choice = Prompt.ask(
            "[cyan]Select option[/cyan]",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        
        if choice == "1":
            category = Prompt.ask("[cyan]Enter category name[/cyan]")
            if category and category not in junk_categories:
                junk_categories[category] = []
                config["junk_subcategories"] = junk_categories
                console.print(f"✅ Added category: [green]{category}[/green]")
            elif category in junk_categories:
                console.print(f"[yellow]Category '{category}' already exists[/yellow]")
        elif choice == "2" and junk_categories:
            categories = list(junk_categories.keys())
            console.print("\nAvailable categories:")
            for i, cat in enumerate(categories, 1):
                console.print(f"{i}. {cat}")
            
            try:
                index = IntPrompt.ask(
                    f"[cyan]Enter category number to remove (1-{len(categories)})[/cyan]",
                    default=1
                ) - 1
                if 0 <= index < len(categories):
                    removed = categories[index]
                    del junk_categories[removed]
                    config["junk_subcategories"] = junk_categories
                    console.print(f"✅ Removed category: [red]{removed}[/red]")
                else:
                    console.print("[red]Invalid category number[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        elif choice == "3" and junk_categories:
            categories = list(junk_categories.keys())
            console.print("\nAvailable categories:")
            for i, cat in enumerate(categories, 1):
                console.print(f"{i}. {cat}")
            
            try:
                index = IntPrompt.ask(
                    f"[cyan]Enter category number to edit (1-{len(categories)})[/cyan]",
                    default=1
                ) - 1
                if 0 <= index < len(categories):
                    category = categories[index]
                    _edit_patterns(console, junk_categories, category, f"Patterns for {category}")
                    config["junk_subcategories"] = junk_categories
                else:
                    console.print("[red]Invalid category number[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        elif choice == "4":
            break


def _edit_scan_settings(console, config: Dict[str, Any]):
    """Edit scan settings with real-time validation."""
    scan_settings = config.get("scan_settings", {})
    
    while True:
        console.print(f"\n[bold blue]Scan Settings[/bold blue]")
        console.print("-" * 13)
        console.print(f"Max Workers: [cyan]{scan_settings.get('max_workers', 20)}[/cyan]")
        console.print(f"Timeout: [cyan]{scan_settings.get('timeout', 7)}s[/cyan]")
        console.print(f"Cache File: [cyan]{scan_settings.get('cache_file', 'scan_cache.json')}[/cyan]")
        
        console.print(f"\n[yellow]Options:[/yellow]")
        console.print("1. Edit max workers")
        console.print("2. Edit timeout")
        console.print("3. Edit cache file")
        console.print("4. Back to main menu")
        
        choice = Prompt.ask(
            "[cyan]Select option[/cyan]",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        
        if choice == "1":
            try:
                max_workers = IntPrompt.ask(
                    "[cyan]Enter max workers (1-100)[/cyan]",
                    default=scan_settings.get('max_workers', 20)
                )
                if 1 <= max_workers <= 100:
                    scan_settings['max_workers'] = max_workers
                    config['scan_settings'] = scan_settings
                    console.print(f"✅ Max workers set to: [green]{max_workers}[/green]")
                else:
                    console.print("[red]Max workers must be between 1 and 100[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        elif choice == "2":
            try:
                timeout = FloatPrompt.ask(
                    "[cyan]Enter timeout in seconds (0.1-60)[/cyan]",
                    default=scan_settings.get('timeout', 7.0)
                )
                if 0.1 <= timeout <= 60:
                    scan_settings['timeout'] = timeout
                    config['scan_settings'] = scan_settings
                    console.print(f"✅ Timeout set to: [green]{timeout}s[/green]")
                else:
                    console.print("[red]Timeout must be between 0.1 and 60 seconds[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        elif choice == "3":
            cache_file = Prompt.ask(
                "[cyan]Enter cache file path[/cyan]",
                default=scan_settings.get('cache_file', 'scan_cache.json')
            )
            if cache_file:
                scan_settings['cache_file'] = cache_file
                config['scan_settings'] = scan_settings
                console.print(f"✅ Cache file set to: [green]{cache_file}[/green]")
        elif choice == "4":
            break


def _validate_configuration(console, config: Dict[str, Any]):
    """Validate configuration and provide detailed feedback."""
    try:
        validate_config(config)
        console.print(Panel(
            "✅ Configuration is valid!\n\n"
            "All settings have been validated successfully.",
            title="✅ Validation Success",
            border_style="green"
        ))
    except Exception as e:
        console.print(Panel(
            f"[red]Configuration validation failed:[/red]\n\n{str(e)}\n\n"
            "[yellow]Please fix the issues above before saving.[/yellow]",
            title="❌ Validation Error",
            border_style="red"
        ))


def _save_configuration(console, config: Dict[str, Any], config_path: str):
    """Save configuration with validation."""
    try:
        # Validate before saving
        validate_config(config)
        save_config(config, config_path)
        console.print(Panel(
            f"✅ Configuration saved successfully!\n\n"
            f"📁 Location: [cyan]{config_path}[/cyan]",
            title="✅ Save Complete",
            border_style="green"
        ))
    except Exception as e:
        console.print(Panel(
            f"[red]Failed to save configuration:[/red]\n\n{str(e)}",
            title="❌ Save Error",
            border_style="red"
        ))