"""
Test Plugin Architecture

This module contains tests for the enhanced plugin architecture, including the
marketplace, configuration UI, documentation generation, and plugin manager.
"""

import unittest
import os
import tempfile
import shutil
import json
from typing import Dict, Any, List, Optional

from url_analyzer.plugins.domain import Plugin, PluginMetadata, PluginType, PluginStatus, PluginDependency
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.plugins.marketplace import PluginMarketplace, PluginPackage
from url_analyzer.plugins.config_ui import PluginConfigManager
from url_analyzer.plugins.documentation import DocstringParser, PluginDocumentationGenerator
from url_analyzer.plugins.manager import PluginManager, get_plugin_manager
from url_analyzer.plugins.interface import Plugin as PluginInterface


class MockPlugin(PluginInterface):
    """Mock plugin for testing."""
    
    def __init__(self, name: str, version: str, description: str, author: str):
        """
        Initialize the mock plugin.
        
        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description
            author: Plugin author
        """
        self._name = name
        self._version = version
        self._description = description
        self._author = author
        self._initialized = False
    
    def get_name(self) -> str:
        """
        Returns the name of the plugin.
        
        Returns:
            String name of the plugin
        """
        return self._name
    
    def get_version(self) -> str:
        """
        Returns the version of the plugin.
        
        Returns:
            String version of the plugin (e.g., "1.0.0")
        """
        return self._version
    
    def get_description(self) -> str:
        """
        Returns a description of the plugin.
        
        Returns:
            String description of the plugin
        """
        return self._description
    
    def get_author(self) -> str:
        """
        Returns the author of the plugin.
        
        Returns:
            String author of the plugin
        """
        return self._author
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initializes the plugin with the given configuration.
        
        Args:
            config: Dictionary containing configuration values
            
        Returns:
            Boolean indicating whether initialization was successful
        """
        self._initialized = True
        return True
    
    def shutdown(self) -> bool:
        """
        Performs cleanup when the plugin is being unloaded.
        
        Returns:
            Boolean indicating whether shutdown was successful
        """
        self._initialized = False
        return True


class TestPluginRegistry(unittest.TestCase):
    """Tests for the PluginRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()
        self.plugin1 = MockPlugin("test-plugin-1", "1.0.0", "Test Plugin 1", "Test Author")
        self.plugin2 = MockPlugin("test-plugin-2", "2.0.0", "Test Plugin 2", "Test Author")
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        # Register a plugin
        result = self.registry.register_plugin(self.plugin1)
        self.assertTrue(result)
        
        # Check that the plugin is in the registry
        plugins = self.registry.get_all_plugins()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0].get_name(), "test-plugin-1")
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        # Register a plugin
        self.registry.register_plugin(self.plugin1)
        
        # Unregister the plugin
        result = self.registry.unregister_plugin(self.plugin1.get_name())
        self.assertTrue(result)
        
        # Check that the plugin is no longer in the registry
        plugins = self.registry.get_all_plugins()
        self.assertEqual(len(plugins), 0)
    
    def test_get_plugin(self):
        """Test getting a plugin by name."""
        # Register a plugin
        self.registry.register_plugin(self.plugin1)
        
        # Get the plugin
        plugin = self.registry.get_plugin(self.plugin1.get_name())
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.get_name(), "test-plugin-1")
    
    def test_initialize_plugin(self):
        """Test initializing a plugin."""
        # Register a plugin
        self.registry.register_plugin(self.plugin1)
        
        # Initialize the plugin
        result = self.registry.initialize_plugin(self.plugin1.get_name(), {})
        self.assertTrue(result)
        
        # Check that the plugin is initialized
        self.assertTrue(self.plugin1._initialized)


class TestPluginMarketplace(unittest.TestCase):
    """Tests for the PluginMarketplace class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()
        self.marketplace = PluginMarketplace(self.registry)
        
        # Create a mock plugin package
        self.plugin_metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test Plugin",
            author="Test Author",
            plugin_type=PluginType.URL_CLASSIFIER,
            dependencies=[],
            homepage=None,
            license=None,
            min_app_version=None,
            max_app_version=None,
            tags=[]
        )
        
        self.plugin_package = PluginPackage(
            metadata=self.plugin_metadata,
            package_url="https://example.com/test-plugin-1.0.0.zip",
            download_count=100,
            rating=4.5,
            description_long="Long description of the test plugin.",
            screenshots=[],
            documentation_url=None,
            changelog=None
        )
    
    def test_version_comparison(self):
        """Test version comparison."""
        # Test with semver
        self.assertEqual(self.marketplace._compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(self.marketplace._compare_versions("1.0.0", "1.0.1"), -1)
        self.assertEqual(self.marketplace._compare_versions("1.0.1", "1.0.0"), 1)
        self.assertEqual(self.marketplace._compare_versions("1.0.0", "1.1.0"), -1)
        self.assertEqual(self.marketplace._compare_versions("1.1.0", "1.0.0"), 1)
        self.assertEqual(self.marketplace._compare_versions("1.0.0", "2.0.0"), -1)
        self.assertEqual(self.marketplace._compare_versions("2.0.0", "1.0.0"), 1)
    
    def test_plugin_package_serialization(self):
        """Test serializing and deserializing a plugin package."""
        # Convert to dictionary
        package_dict = self.plugin_package.to_dict()
        
        # Convert back to PluginPackage
        package = PluginPackage.from_dict(package_dict)
        
        # Check that the package is the same
        self.assertEqual(package.metadata.name, self.plugin_package.metadata.name)
        self.assertEqual(package.metadata.version, self.plugin_package.metadata.version)
        self.assertEqual(package.metadata.description, self.plugin_package.metadata.description)
        self.assertEqual(package.metadata.author, self.plugin_package.metadata.author)
        self.assertEqual(package.package_url, self.plugin_package.package_url)
        self.assertEqual(package.download_count, self.plugin_package.download_count)
        self.assertEqual(package.rating, self.plugin_package.rating)
        self.assertEqual(package.description_long, self.plugin_package.description_long)


class TestPluginConfigManager(unittest.TestCase):
    """Tests for the PluginConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()
        self.plugin = MockPlugin("test-plugin", "1.0.0", "Test Plugin", "Test Author")
        self.registry.register_plugin(self.plugin)
        
        # Create a temporary directory for config files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a config manager with the temporary directory
        self.config_manager = PluginConfigManager(self.registry)
        self.config_manager._config_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_get_config(self):
        """Test getting a plugin configuration."""
        # Get the configuration
        config = self.config_manager.get_config(self.plugin.get_name())
        
        # Check that the configuration has the expected structure
        self.assertIn("enabled", config)
        self.assertIn("settings", config)
        self.assertTrue(config["enabled"])
        self.assertEqual(config["settings"], {})
    
    def test_save_config(self):
        """Test saving a plugin configuration."""
        # Create a configuration
        config = {
            "enabled": True,
            "settings": {
                "setting1": "value1",
                "setting2": 42
            }
        }
        
        # Save the configuration
        result = self.config_manager.save_config(self.plugin.get_name(), config)
        self.assertTrue(result)
        
        # Check that the configuration file exists
        config_path = os.path.join(self.temp_dir, f"{self.plugin.get_name()}.json")
        self.assertTrue(os.path.exists(config_path))
        
        # Load the configuration from the file
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        # Check that the loaded configuration matches the original
        self.assertEqual(loaded_config, config)
    
    def test_get_setting(self):
        """Test getting a setting from a plugin configuration."""
        # Create a configuration with settings
        config = {
            "enabled": True,
            "settings": {
                "setting1": "value1",
                "setting2": 42
            }
        }
        
        # Save the configuration
        self.config_manager.save_config(self.plugin.get_name(), config)
        
        # Get a setting
        value = self.config_manager.get_setting(self.plugin.get_name(), "setting1")
        self.assertEqual(value, "value1")
        
        # Get a non-existent setting
        value = self.config_manager.get_setting(self.plugin.get_name(), "non-existent", "default")
        self.assertEqual(value, "default")
    
    def test_set_setting(self):
        """Test setting a setting in a plugin configuration."""
        # Set a setting
        result = self.config_manager.set_setting(self.plugin.get_name(), "setting1", "value1")
        self.assertTrue(result)
        
        # Check that the setting was set
        value = self.config_manager.get_setting(self.plugin.get_name(), "setting1")
        self.assertEqual(value, "value1")
    
    def test_is_plugin_enabled(self):
        """Test checking if a plugin is enabled."""
        # By default, plugins are enabled
        enabled = self.config_manager.is_plugin_enabled(self.plugin.get_name())
        self.assertTrue(enabled)
        
        # Disable the plugin
        self.config_manager.set_plugin_enabled(self.plugin.get_name(), False)
        
        # Check that the plugin is disabled
        enabled = self.config_manager.is_plugin_enabled(self.plugin.get_name())
        self.assertFalse(enabled)


class TestDocstringParser(unittest.TestCase):
    """Tests for the DocstringParser class."""
    
    def test_parse_simple_docstring(self):
        """Test parsing a simple docstring."""
        docstring = """This is a short description.
        
        This is a longer description that spans
        multiple lines.
        
        Args:
            param1: Description of param1
            param2: Description of param2
            
        Returns:
            Description of return value
            
        Raises:
            ExceptionType: When and why this exception is raised
        """
        
        parsed = DocstringParser.parse(docstring)
        
        self.assertEqual(parsed["short_description"], "This is a short description.")
        self.assertIn("This is a longer description", parsed["long_description"])
        self.assertEqual(len(parsed["params"]), 2)
        self.assertEqual(parsed["params"][0]["name"], "param1")
        self.assertEqual(parsed["params"][1]["name"], "param2")
        self.assertIsNotNone(parsed["returns"])
        self.assertIn("Description of return value", parsed["returns"]["description"])
        self.assertEqual(len(parsed["raises"]), 1)
        self.assertEqual(parsed["raises"][0]["type"], "ExceptionType")


class TestPluginManager(unittest.TestCase):
    """Tests for the PluginManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for plugins
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a plugin manager with the temporary directory
        self.plugin_manager = PluginManager([self.temp_dir])
        
        # Create a mock plugin
        self.plugin = MockPlugin("test-plugin", "1.0.0", "Test Plugin", "Test Author")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_get_registry(self):
        """Test getting the plugin registry."""
        registry = self.plugin_manager.get_registry()
        self.assertIsInstance(registry, PluginRegistry)
    
    def test_get_marketplace(self):
        """Test getting the plugin marketplace."""
        marketplace = self.plugin_manager.get_marketplace()
        self.assertIsInstance(marketplace, PluginMarketplace)
    
    def test_singleton(self):
        """Test that get_plugin_manager returns a singleton instance."""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()
        self.assertIs(manager1, manager2)


if __name__ == "__main__":
    unittest.main()