"""
Plugin Configuration UI Module

This module provides a user interface for configuring plugins in the URL Analyzer.
It allows users to view and modify plugin settings through both a command-line
interface and a web-based interface.
"""

import os
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional, Tuple
import webbrowser
from pathlib import Path

from url_analyzer.plugins.domain import Plugin, PluginMetadata, PluginType, PluginStatus
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.utils.logging import get_logger

# Try to import optional dependencies
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.validation import Validator, ValidationError
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Create logger
logger = get_logger(__name__)

# Constants
CONFIG_DIR = "plugin_configs"
DEFAULT_CONFIG_TEMPLATE = {
    "enabled": True,
    "settings": {}
}


class PluginConfigManager:
    """
    Manager for plugin configurations.
    
    This class handles loading, saving, and validating plugin configurations.
    """
    
    def __init__(self, registry: PluginRegistry):
        """
        Initialize the plugin configuration manager.
        
        Args:
            registry: Plugin registry to use for accessing plugins
        """
        self._registry = registry
        self._config_dir = os.path.join(os.path.dirname(__file__), CONFIG_DIR)
        self._configs: Dict[str, Dict[str, Any]] = {}
        
        # Create config directory if it doesn't exist
        os.makedirs(self._config_dir, exist_ok=True)
        
        # Load configurations for all registered plugins
        self._load_all_configs()
        
        logger.info(f"Plugin configuration manager initialized with {len(self._configs)} configurations")
    
    def _load_all_configs(self) -> None:
        """
        Load configurations for all registered plugins.
        """
        for plugin_name in self._registry.list_plugins():
            self.get_config(plugin_name)
    
    def get_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a plugin.
        
        If the configuration doesn't exist, a default configuration is created.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin configuration dictionary
        """
        # Check if the configuration is already loaded
        if plugin_name in self._configs:
            return self._configs[plugin_name]
        
        # Get the plugin
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            logger.warning(f"Plugin not found: {plugin_name}")
            return DEFAULT_CONFIG_TEMPLATE.copy()
        
        # Try to load the configuration from file
        config_path = os.path.join(self._config_dir, f"{plugin_name}.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                logger.info(f"Loaded configuration for plugin: {plugin_name}")
                self._configs[plugin_name] = config
                return config
            except Exception as e:
                logger.error(f"Error loading configuration for plugin {plugin_name}: {e}")
        
        # Create a default configuration
        config = DEFAULT_CONFIG_TEMPLATE.copy()
        self._configs[plugin_name] = config
        
        # Save the default configuration
        self.save_config(plugin_name, config)
        
        return config
    
    def save_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Save the configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the in-memory configuration
            self._configs[plugin_name] = config
            
            # Save the configuration to file
            config_path = os.path.join(self._config_dir, f"{plugin_name}.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Saved configuration for plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration for plugin {plugin_name}: {e}")
            return False
    
    def reset_config(self, plugin_name: str) -> bool:
        """
        Reset the configuration for a plugin to default values.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a default configuration
            config = DEFAULT_CONFIG_TEMPLATE.copy()
            
            # Save the default configuration
            if self.save_config(plugin_name, config):
                logger.info(f"Reset configuration for plugin: {plugin_name}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error resetting configuration for plugin {plugin_name}: {e}")
            return False
    
    def get_setting(self, plugin_name: str, setting_name: str, default: Any = None) -> Any:
        """
        Get a setting value from a plugin configuration.
        
        Args:
            plugin_name: Name of the plugin
            setting_name: Name of the setting
            default: Default value to return if the setting doesn't exist
            
        Returns:
            Setting value or default if not found
        """
        config = self.get_config(plugin_name)
        return config.get("settings", {}).get(setting_name, default)
    
    def set_setting(self, plugin_name: str, setting_name: str, value: Any) -> bool:
        """
        Set a setting value in a plugin configuration.
        
        Args:
            plugin_name: Name of the plugin
            setting_name: Name of the setting
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = self.get_config(plugin_name)
            
            # Ensure the settings dictionary exists
            if "settings" not in config:
                config["settings"] = {}
            
            # Set the setting value
            config["settings"][setting_name] = value
            
            # Save the updated configuration
            return self.save_config(plugin_name, config)
        except Exception as e:
            logger.error(f"Error setting {setting_name} for plugin {plugin_name}: {e}")
            return False
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """
        Check if a plugin is enabled.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if the plugin is enabled, False otherwise
        """
        config = self.get_config(plugin_name)
        return config.get("enabled", True)
    
    def set_plugin_enabled(self, plugin_name: str, enabled: bool) -> bool:
        """
        Enable or disable a plugin.
        
        Args:
            plugin_name: Name of the plugin
            enabled: Whether the plugin should be enabled
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = self.get_config(plugin_name)
            
            # Set the enabled flag
            config["enabled"] = enabled
            
            # Save the updated configuration
            return self.save_config(plugin_name, config)
        except Exception as e:
            logger.error(f"Error {'enabling' if enabled else 'disabling'} plugin {plugin_name}: {e}")
            return False
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configurations for all plugins.
        
        Returns:
            Dictionary mapping plugin names to configurations
        """
        # Ensure all configurations are loaded
        for plugin_name in self._registry.list_plugins():
            self.get_config(plugin_name)
        
        return self._configs


class CommandLineConfigUI:
    """
    Command-line interface for configuring plugins.
    
    This class provides a text-based user interface for viewing and modifying
    plugin configurations.
    """
    
    def __init__(self, config_manager: PluginConfigManager, registry: PluginRegistry):
        """
        Initialize the command-line configuration UI.
        
        Args:
            config_manager: Plugin configuration manager
            registry: Plugin registry
        """
        self._config_manager = config_manager
        self._registry = registry
        self._console = Console() if RICH_AVAILABLE else None
    
    def run(self) -> None:
        """
        Run the command-line configuration UI.
        """
        while True:
            self._display_menu()
            choice = input("Enter your choice (q to quit): ")
            
            if choice.lower() == 'q':
                break
            
            try:
                choice_num = int(choice)
                self._handle_menu_choice(choice_num)
            except ValueError:
                print("Invalid choice. Please enter a number or 'q' to quit.")
    
    def _display_menu(self) -> None:
        """
        Display the main menu.
        """
        if RICH_AVAILABLE:
            self._display_rich_menu()
        else:
            self._display_simple_menu()
    
    def _display_simple_menu(self) -> None:
        """
        Display a simple text-based menu.
        """
        print("\nPlugin Configuration Menu")
        print("------------------------")
        print("1. List all plugins")
        print("2. Configure a plugin")
        print("3. Enable/disable a plugin")
        print("4. Reset a plugin configuration")
        print("5. Show plugin details")
        print("q. Quit")
    
    def _display_rich_menu(self) -> None:
        """
        Display a rich text-based menu using the rich library.
        """
        menu_text = Text()
        menu_text.append("Plugin Configuration Menu\n", style="bold cyan")
        menu_text.append("------------------------\n\n")
        menu_text.append("1. List all plugins\n")
        menu_text.append("2. Configure a plugin\n")
        menu_text.append("3. Enable/disable a plugin\n")
        menu_text.append("4. Reset a plugin configuration\n")
        menu_text.append("5. Show plugin details\n")
        menu_text.append("q. Quit\n")
        
        self._console.print(Panel(menu_text, title="URL Analyzer Plugin Configuration"))
    
    def _handle_menu_choice(self, choice: int) -> None:
        """
        Handle a menu choice.
        
        Args:
            choice: Menu choice number
        """
        if choice == 1:
            self._list_plugins()
        elif choice == 2:
            self._configure_plugin()
        elif choice == 3:
            self._toggle_plugin()
        elif choice == 4:
            self._reset_plugin()
        elif choice == 5:
            self._show_plugin_details()
        else:
            print("Invalid choice. Please try again.")
    
    def _list_plugins(self) -> None:
        """
        List all registered plugins.
        """
        plugins = self._registry.get_all_plugins()
        
        if not plugins:
            print("No plugins are registered.")
            return
        
        if RICH_AVAILABLE:
            table = Table(title="Registered Plugins")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Author", style="yellow")
            table.add_column("Enabled", style="magenta")
            
            for plugin in plugins:
                enabled = "Yes" if self._config_manager.is_plugin_enabled(plugin.get_name()) else "No"
                table.add_row(
                    plugin.get_name(),
                    plugin.get_version(),
                    plugin.get_author(),
                    enabled
                )
            
            self._console.print(table)
        else:
            print("\nRegistered Plugins:")
            print("-----------------")
            for plugin in plugins:
                enabled = "Yes" if self._config_manager.is_plugin_enabled(plugin.get_name()) else "No"
                print(f"- {plugin.get_name()} (v{plugin.get_version()}) by {plugin.get_author()} [Enabled: {enabled}]")
    
    def _configure_plugin(self) -> None:
        """
        Configure a plugin.
        """
        # Get the plugin name
        plugin_name = self._select_plugin("Configure plugin")
        if not plugin_name:
            return
        
        # Get the plugin configuration
        config = self._config_manager.get_config(plugin_name)
        settings = config.get("settings", {})
        
        # Display current settings
        if RICH_AVAILABLE:
            table = Table(title=f"Settings for {plugin_name}")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            
            for setting_name, setting_value in settings.items():
                table.add_row(setting_name, str(setting_value))
            
            self._console.print(table)
        else:
            print(f"\nSettings for {plugin_name}:")
            print("-" * (len(plugin_name) + 13))
            for setting_name, setting_value in settings.items():
                print(f"- {setting_name}: {setting_value}")
        
        # Prompt for setting to modify
        setting_name = input("\nEnter setting name to modify (or press Enter to cancel): ")
        if not setting_name:
            return
        
        # Prompt for new value
        current_value = settings.get(setting_name, "")
        new_value = input(f"Enter new value for {setting_name} [{current_value}]: ")
        if not new_value:
            new_value = current_value
        
        # Try to convert the value to the appropriate type
        try:
            # If the current value is a boolean, convert the new value to a boolean
            if isinstance(current_value, bool):
                new_value = new_value.lower() in ('true', 'yes', 'y', '1')
            # If the current value is an integer, convert the new value to an integer
            elif isinstance(current_value, int):
                new_value = int(new_value)
            # If the current value is a float, convert the new value to a float
            elif isinstance(current_value, float):
                new_value = float(new_value)
        except ValueError:
            print(f"Warning: Could not convert value to the same type as the current value. Using as string.")
        
        # Save the new value
        if self._config_manager.set_setting(plugin_name, setting_name, new_value):
            print(f"Setting {setting_name} updated successfully.")
        else:
            print(f"Error updating setting {setting_name}.")
    
    def _toggle_plugin(self) -> None:
        """
        Enable or disable a plugin.
        """
        # Get the plugin name
        plugin_name = self._select_plugin("Enable/disable plugin")
        if not plugin_name:
            return
        
        # Get the current enabled state
        enabled = self._config_manager.is_plugin_enabled(plugin_name)
        
        # Prompt for confirmation
        action = "disable" if enabled else "enable"
        confirm = input(f"Are you sure you want to {action} {plugin_name}? (y/n): ")
        if confirm.lower() not in ('y', 'yes'):
            return
        
        # Toggle the enabled state
        if self._config_manager.set_plugin_enabled(plugin_name, not enabled):
            print(f"Plugin {plugin_name} {'disabled' if enabled else 'enabled'} successfully.")
        else:
            print(f"Error {'disabling' if enabled else 'enabling'} plugin {plugin_name}.")
    
    def _reset_plugin(self) -> None:
        """
        Reset a plugin configuration to default values.
        """
        # Get the plugin name
        plugin_name = self._select_plugin("Reset plugin configuration")
        if not plugin_name:
            return
        
        # Prompt for confirmation
        confirm = input(f"Are you sure you want to reset the configuration for {plugin_name}? (y/n): ")
        if confirm.lower() not in ('y', 'yes'):
            return
        
        # Reset the configuration
        if self._config_manager.reset_config(plugin_name):
            print(f"Configuration for plugin {plugin_name} reset successfully.")
        else:
            print(f"Error resetting configuration for plugin {plugin_name}.")
    
    def _show_plugin_details(self) -> None:
        """
        Show detailed information about a plugin.
        """
        # Get the plugin name
        plugin_name = self._select_plugin("Show plugin details")
        if not plugin_name:
            return
        
        # Get the plugin
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            print(f"Plugin {plugin_name} not found.")
            return
        
        # Display plugin details
        if RICH_AVAILABLE:
            details = Text()
            details.append(f"Name: ", style="bold")
            details.append(f"{plugin.get_name()}\n")
            details.append(f"Version: ", style="bold")
            details.append(f"{plugin.get_version()}\n")
            details.append(f"Author: ", style="bold")
            details.append(f"{plugin.get_author()}\n")
            details.append(f"Description: ", style="bold")
            details.append(f"{plugin.get_description()}\n")
            details.append(f"Enabled: ", style="bold")
            details.append(f"{self._config_manager.is_plugin_enabled(plugin_name)}\n")
            
            self._console.print(Panel(details, title=f"Plugin Details: {plugin_name}"))
        else:
            print(f"\nPlugin Details: {plugin_name}")
            print("-" * (len(plugin_name) + 16))
            print(f"Name: {plugin.get_name()}")
            print(f"Version: {plugin.get_version()}")
            print(f"Author: {plugin.get_author()}")
            print(f"Description: {plugin.get_description()}")
            print(f"Enabled: {self._config_manager.is_plugin_enabled(plugin_name)}")
    
    def _select_plugin(self, prompt_text: str) -> Optional[str]:
        """
        Prompt the user to select a plugin.
        
        Args:
            prompt_text: Text to display in the prompt
            
        Returns:
            Selected plugin name or None if cancelled
        """
        # Get the list of plugin names
        plugin_names = self._registry.list_plugins()
        
        if not plugin_names:
            print("No plugins are registered.")
            return None
        
        # Display the list of plugins
        if RICH_AVAILABLE:
            table = Table(title="Available Plugins")
            table.add_column("Number", style="cyan")
            table.add_column("Name", style="green")
            
            for i, name in enumerate(plugin_names, 1):
                table.add_row(str(i), name)
            
            self._console.print(table)
        else:
            print("\nAvailable Plugins:")
            print("-----------------")
            for i, name in enumerate(plugin_names, 1):
                print(f"{i}. {name}")
        
        # Prompt for selection
        while True:
            try:
                choice = input(f"\n{prompt_text} (number or name, Enter to cancel): ")
                if not choice:
                    return None
                
                # Try to interpret the choice as a number
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(plugin_names):
                        return plugin_names[choice_num - 1]
                    else:
                        print(f"Invalid number. Please enter a number between 1 and {len(plugin_names)}.")
                except ValueError:
                    # If not a number, interpret as a plugin name
                    if choice in plugin_names:
                        return choice
                    else:
                        print(f"Plugin '{choice}' not found. Please enter a valid plugin name or number.")
            except KeyboardInterrupt:
                return None


class WebConfigUI:
    """
    Web-based interface for configuring plugins.
    
    This class provides a web-based user interface for viewing and modifying
    plugin configurations.
    """
    
    def __init__(self, config_manager: PluginConfigManager, registry: PluginRegistry, host: str = 'localhost', port: int = 5000):
        """
        Initialize the web-based configuration UI.
        
        Args:
            config_manager: Plugin configuration manager
            registry: Plugin registry
            host: Host to bind the web server to
            port: Port to bind the web server to
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for the web-based configuration UI")
        
        self._config_manager = config_manager
        self._registry = registry
        self._host = host
        self._port = port
        self._app = Flask(__name__)
        
        # Set up routes
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """
        Set up the Flask routes.
        """
        @self._app.route('/')
        def index():
            plugins = self._registry.get_all_plugins()
            return render_template('plugins/index.html', plugins=plugins, config_manager=self._config_manager)
        
        @self._app.route('/plugin/<name>')
        def plugin_details(name):
            plugin = self._registry.get_plugin(name)
            if not plugin:
                return redirect(url_for('index'))
            
            config = self._config_manager.get_config(name)
            return render_template('plugins/details.html', plugin=plugin, config=config)
        
        @self._app.route('/plugin/<name>/config', methods=['GET', 'POST'])
        def plugin_config(name):
            plugin = self._registry.get_plugin(name)
            if not plugin:
                return redirect(url_for('index'))
            
            if request.method == 'POST':
                # Update the configuration
                config = self._config_manager.get_config(name)
                
                # Update enabled state
                enabled = request.form.get('enabled') == 'on'
                config['enabled'] = enabled
                
                # Update settings
                for key, value in request.form.items():
                    if key.startswith('setting_'):
                        setting_name = key[8:]  # Remove 'setting_' prefix
                        
                        # Try to convert the value to the appropriate type
                        current_value = config.get('settings', {}).get(setting_name)
                        if current_value is not None:
                            try:
                                if isinstance(current_value, bool):
                                    value = value.lower() in ('true', 'yes', 'y', '1', 'on')
                                elif isinstance(current_value, int):
                                    value = int(value)
                                elif isinstance(current_value, float):
                                    value = float(value)
                            except ValueError:
                                pass
                        
                        # Ensure the settings dictionary exists
                        if 'settings' not in config:
                            config['settings'] = {}
                        
                        # Set the setting value
                        config['settings'][setting_name] = value
                
                # Save the updated configuration
                self._config_manager.save_config(name, config)
                
                return redirect(url_for('plugin_details', name=name))
            
            config = self._config_manager.get_config(name)
            return render_template('plugins/config.html', plugin=plugin, config=config)
        
        @self._app.route('/plugin/<name>/reset', methods=['POST'])
        def plugin_reset(name):
            plugin = self._registry.get_plugin(name)
            if not plugin:
                return redirect(url_for('index'))
            
            # Reset the configuration
            self._config_manager.reset_config(name)
            
            return redirect(url_for('plugin_details', name=name))
    
    def run(self, debug: bool = False, open_browser: bool = True) -> None:
        """
        Run the web-based configuration UI.
        
        Args:
            debug: Whether to run the server in debug mode
            open_browser: Whether to open a browser window automatically
        """
        if open_browser:
            webbrowser.open(f"http://{self._host}:{self._port}")
        
        self._app.run(host=self._host, port=self._port, debug=debug)


def create_config_ui(registry: PluginRegistry, ui_type: str = 'auto') -> Any:
    """
    Create a plugin configuration UI.
    
    Args:
        registry: Plugin registry
        ui_type: Type of UI to create ('cli', 'web', or 'auto')
        
    Returns:
        Configuration UI instance
    """
    # Create the configuration manager
    config_manager = PluginConfigManager(registry)
    
    # Determine the UI type
    if ui_type == 'auto':
        if FLASK_AVAILABLE:
            ui_type = 'web'
        else:
            ui_type = 'cli'
    
    # Create the UI
    if ui_type == 'web':
        if not FLASK_AVAILABLE:
            logger.warning("Flask is not available. Falling back to command-line UI.")
            return CommandLineConfigUI(config_manager, registry)
        
        return WebConfigUI(config_manager, registry)
    else:
        return CommandLineConfigUI(config_manager, registry)


def run_config_ui(registry: PluginRegistry, ui_type: str = 'auto') -> None:
    """
    Run a plugin configuration UI.
    
    Args:
        registry: Plugin registry
        ui_type: Type of UI to run ('cli', 'web', or 'auto')
    """
    ui = create_config_ui(registry, ui_type)
    ui.run()