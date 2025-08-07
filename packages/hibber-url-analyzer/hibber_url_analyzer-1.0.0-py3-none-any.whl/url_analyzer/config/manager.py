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
from abc import ABC, abstractmethod
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


# Strategy Pattern for Configuration Sources
class ConfigurationSource(ABC):
    """
    Abstract base class for configuration sources.
    Implements Strategy pattern for different configuration loading strategies.
    """
    
    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the source.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the configuration source is available.
        
        Returns:
            True if source is available, False otherwise
        """
        pass


class FileConfigurationSource(ConfigurationSource):
    """
    Configuration source that loads from a JSON file.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize file configuration source.
        
        Args:
            file_path: Path to the configuration file
        """
        self.file_path = file_path
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise MissingConfigurationError(f"Configuration file not found: {self.file_path}")
        except json.JSONDecodeError as e:
            raise InvalidConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration file: {e}")
    
    def is_available(self) -> bool:
        """
        Check if configuration file exists and is readable.
        
        Returns:
            True if file is available, False otherwise
        """
        return os.path.isfile(self.file_path) and os.access(self.file_path, os.R_OK)


class EnvironmentConfigurationSource(ConfigurationSource):
    """
    Configuration source that loads from environment variables.
    """
    
    def __init__(self, env_prefix: str = "URL_ANALYZER_"):
        """
        Initialize environment configuration source.
        
        Args:
            env_prefix: Prefix for environment variables
        """
        self.env_prefix = env_prefix
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Returns:
            Configuration dictionary
        """
        config = {}
        
        # Load common configuration from environment
        if os.getenv(f"{self.env_prefix}CONFIG_PATH"):
            config["config_path"] = os.getenv(f"{self.env_prefix}CONFIG_PATH")
        
        if os.getenv(f"{self.env_prefix}CACHE_PATH"):
            config.setdefault("scan_settings", {})["cache_file"] = os.getenv(f"{self.env_prefix}CACHE_PATH")
        
        if os.getenv(f"{self.env_prefix}MAX_WORKERS"):
            try:
                config.setdefault("scan_settings", {})["max_workers"] = int(os.getenv(f"{self.env_prefix}MAX_WORKERS"))
            except ValueError:
                pass
        
        if os.getenv(f"{self.env_prefix}TIMEOUT"):
            try:
                config.setdefault("scan_settings", {})["timeout"] = float(os.getenv(f"{self.env_prefix}TIMEOUT"))
            except ValueError:
                pass
        
        if os.getenv("GEMINI_API_KEY"):
            config.setdefault("api_settings", {})["gemini_api_key"] = os.getenv("GEMINI_API_KEY")
        
        return config
    
    def is_available(self) -> bool:
        """
        Check if any relevant environment variables are set.
        
        Returns:
            True if environment variables are available, False otherwise
        """
        env_vars = [
            f"{self.env_prefix}CONFIG_PATH",
            f"{self.env_prefix}CACHE_PATH",
            f"{self.env_prefix}MAX_WORKERS",
            f"{self.env_prefix}TIMEOUT",
            "GEMINI_API_KEY"
        ]
        return any(os.getenv(var) for var in env_vars)


class DefaultConfigurationSource(ConfigurationSource):
    """
    Configuration source that provides default values.
    """
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return create_default_config()
    
    def is_available(self) -> bool:
        """
        Default configuration is always available.
        
        Returns:
            Always True
        """
        return True


# Builder Pattern for Complex Configuration Objects
class ConfigurationBuilder:
    """
    Builder pattern for creating complex configuration objects.
    Provides a fluent interface for building configurations step by step.
    """
    
    def __init__(self):
        """Initialize the configuration builder."""
        self._config = {}
    
    def with_sensitive_patterns(self, patterns: List[str]) -> 'ConfigurationBuilder':
        """
        Add sensitive patterns to the configuration.
        
        Args:
            patterns: List of sensitive URL patterns
            
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        self._config["sensitive_patterns"] = patterns
        return self
    
    def with_ugc_patterns(self, patterns: List[str]) -> 'ConfigurationBuilder':
        """
        Add UGC patterns to the configuration.
        
        Args:
            patterns: List of UGC URL patterns
            
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        self._config["ugc_patterns"] = patterns
        return self
    
    def with_junk_subcategories(self, subcategories: Dict[str, List[str]]) -> 'ConfigurationBuilder':
        """
        Add junk subcategories to the configuration.
        
        Args:
            subcategories: Dictionary of junk subcategories and their patterns
            
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        self._config["junk_subcategories"] = subcategories
        return self
    
    def with_api_settings(self, api_url: str, api_key: Optional[str] = None) -> 'ConfigurationBuilder':
        """
        Add API settings to the configuration.
        
        Args:
            api_url: API URL
            api_key: Optional API key
            
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        api_settings = {"gemini_api_url": api_url}
        if api_key:
            api_settings["gemini_api_key"] = api_key
        self._config["api_settings"] = api_settings
        return self
    
    def with_scan_settings(self, max_workers: int = 20, timeout: float = 7, 
                          cache_file: str = "scan_cache.json") -> 'ConfigurationBuilder':
        """
        Add scan settings to the configuration.
        
        Args:
            max_workers: Maximum number of worker threads
            timeout: Request timeout in seconds
            cache_file: Cache file path
            
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        self._config["scan_settings"] = {
            "max_workers": max_workers,
            "timeout": timeout,
            "cache_file": cache_file
        }
        return self
    
    def with_custom_setting(self, key: str, value: Any) -> 'ConfigurationBuilder':
        """
        Add a custom setting to the configuration.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        self._config[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build and return the final configuration dictionary.
        
        Returns:
            Complete configuration dictionary
            
        Raises:
            ValidationError: If the built configuration is invalid
        """
        # Validate the built configuration
        validate_config(self._config)
        return self._config.copy()
    
    def reset(self) -> 'ConfigurationBuilder':
        """
        Reset the builder to start fresh.
        
        Returns:
            ConfigurationBuilder instance for method chaining
        """
        self._config = {}
        return self


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


class ConfigManager:
    """
    Configuration manager class for centralized configuration handling.
    Implements Singleton pattern to ensure consistent configuration across the application.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, config_path: str = 'config.json'):
        """
        Implement Singleton pattern - only one instance per config path.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            ConfigManager instance
        """
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        if not self._initialized:
            self.config_path = config_path
            self._config = None
            self._compiled_patterns = None
            self._config_sources = []
            self._initialized = True
    
    @classmethod
    def get_instance(cls, config_path: str = 'config.json') -> 'ConfigManager':
        """
        Factory method to get ConfigManager instance.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            ConfigManager instance
        """
        return cls(config_path)
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (useful for testing).
        """
        cls._instance = None
        cls._initialized = False
    
    def add_configuration_source(self, source: ConfigurationSource) -> None:
        """
        Add a configuration source using Strategy pattern.
        
        Args:
            source: Configuration source to add
        """
        self._config_sources.append(source)
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration using Strategy pattern from multiple sources.
        Sources are processed in order: file, environment, defaults.
        
        Returns:
            Merged configuration dictionary
        """
        # Initialize default sources if none are configured
        if not self._config_sources:
            self._config_sources = [
                FileConfigurationSource(self.config_path),
                EnvironmentConfigurationSource(),
                DefaultConfigurationSource()
            ]
        
        # Start with empty configuration
        merged_config = {}
        
        # Load from each available source in order
        for source in self._config_sources:
            if source.is_available():
                try:
                    source_config = source.load_config()
                    merged_config = self._merge_configs(merged_config, source_config)
                except ConfigurationError as e:
                    # Log warning but continue with other sources
                    print(f"Warning: Failed to load from configuration source: {e}")
        
        # Validate the merged configuration
        validate_config(merged_config)
        
        self._config = merged_config
        return self._config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries recursively.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save(self, config_data: Dict[str, Any] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config_data: Configuration data to save (uses current config if None)
        """
        if config_data is None:
            config_data = self._config
        save_config(config_data, self.config_path)
        self._config = config_data
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        if self._config is None:
            self.load()
        return self._config
    
    def get_compiled_patterns(self) -> Dict[str, Any]:
        """
        Get compiled regex patterns.
        
        Returns:
            Dictionary of compiled patterns
        """
        if self._compiled_patterns is None:
            config = self.get_config()
            self._compiled_patterns = compile_patterns(config)
        return self._compiled_patterns
    
    def refresh(self) -> None:
        """
        Refresh configuration by reloading from file.
        """
        self._config = None
        self._compiled_patterns = None
        self.load()