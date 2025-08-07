"""
Plugins Domain Models

This module defines the domain models and value objects for the Plugins domain.
These models represent the core concepts in plugin management and encapsulate domain logic.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Union, Callable
import os
import importlib.util
import sys
import re
from datetime import datetime

# Try to import semver for semantic versioning, but provide a fallback if not available
try:
    import semver
    SEMVER_AVAILABLE = True
except ImportError:
    SEMVER_AVAILABLE = False


class PluginType(Enum):
    """Enumeration of plugin types."""
    
    URL_CLASSIFIER = auto()
    URL_PROCESSOR = auto()
    DATA_SOURCE = auto()
    DATA_SINK = auto()
    REPORT_GENERATOR = auto()
    CHART_GENERATOR = auto()
    CUSTOM = auto()


class PluginStatus(Enum):
    """Enumeration of plugin statuses."""
    
    ACTIVE = auto()
    INACTIVE = auto()
    ERROR = auto()
    INCOMPATIBLE = auto()
    PENDING = auto()


@dataclass(frozen=True)
class PluginDependency:
    """Value object representing a plugin dependency."""
    
    name: str
    version_constraint: str
    optional: bool = False
    
    def is_satisfied_by(self, version: str) -> bool:
        """
        Check if this dependency is satisfied by the given version.
        
        Args:
            version: Version to check against
            
        Returns:
            True if the version satisfies the constraint, False otherwise
        """
        if SEMVER_AVAILABLE:
            try:
                # Use semver for semantic versioning if available
                # Parse the version constraint
                if self.version_constraint.startswith('>='):
                    min_version = self.version_constraint[2:]
                    return semver.compare(version, min_version) >= 0
                elif self.version_constraint.startswith('>'):
                    min_version = self.version_constraint[1:]
                    return semver.compare(version, min_version) > 0
                elif self.version_constraint.startswith('<='):
                    max_version = self.version_constraint[2:]
                    return semver.compare(version, max_version) <= 0
                elif self.version_constraint.startswith('<'):
                    max_version = self.version_constraint[1:]
                    return semver.compare(version, max_version) < 0
                elif self.version_constraint.startswith('=='):
                    exact_version = self.version_constraint[2:]
                    return semver.compare(version, exact_version) == 0
                elif self.version_constraint.startswith('!='):
                    not_version = self.version_constraint[2:]
                    return semver.compare(version, not_version) != 0
                elif self.version_constraint.startswith('~'):
                    # Compatible release (patch level changes allowed)
                    compatible_version = self.version_constraint[1:]
                    return semver.match(version, f"~{compatible_version}")
                elif self.version_constraint.startswith('^'):
                    # Compatible release (minor level changes allowed)
                    compatible_version = self.version_constraint[1:]
                    return semver.match(version, f"^{compatible_version}")
                else:
                    # Exact version match
                    return semver.compare(version, self.version_constraint) == 0
            except Exception:
                # If there's any error in version comparison, assume not satisfied
                return False
        else:
            # Fallback implementation for simple version comparison
            try:
                # Simple version comparison using regex
                # This is a basic implementation that doesn't fully support semantic versioning
                def parse_version(v):
                    # Extract major, minor, patch versions
                    match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?', v)
                    if not match:
                        return (0, 0, 0)
                    
                    major = int(match.group(1) or 0)
                    minor = int(match.group(2) or 0)
                    patch = int(match.group(3) or 0)
                    
                    return (major, minor, patch)
                
                def compare_versions(v1, v2):
                    # Compare two version strings
                    # Returns -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
                    v1_parts = parse_version(v1)
                    v2_parts = parse_version(v2)
                    
                    for i in range(3):
                        if v1_parts[i] < v2_parts[i]:
                            return -1
                        elif v1_parts[i] > v2_parts[i]:
                            return 1
                    
                    return 0
                
                # Parse the version constraint
                if self.version_constraint.startswith('>='):
                    min_version = self.version_constraint[2:]
                    return compare_versions(version, min_version) >= 0
                elif self.version_constraint.startswith('>'):
                    min_version = self.version_constraint[1:]
                    return compare_versions(version, min_version) > 0
                elif self.version_constraint.startswith('<='):
                    max_version = self.version_constraint[2:]
                    return compare_versions(version, max_version) <= 0
                elif self.version_constraint.startswith('<'):
                    max_version = self.version_constraint[1:]
                    return compare_versions(version, max_version) < 0
                elif self.version_constraint.startswith('=='):
                    exact_version = self.version_constraint[2:]
                    return compare_versions(version, exact_version) == 0
                elif self.version_constraint.startswith('!='):
                    not_version = self.version_constraint[2:]
                    return compare_versions(version, not_version) != 0
                elif self.version_constraint.startswith('~') or self.version_constraint.startswith('^'):
                    # For ~ and ^ constraints, we'll do a simple implementation
                    # that just checks if the version is greater than or equal to the base version
                    base_version = self.version_constraint[1:]
                    return compare_versions(version, base_version) >= 0
                else:
                    # Exact version match
                    return compare_versions(version, self.version_constraint) == 0
            except Exception:
                # If there's any error in version comparison, assume not satisfied
                return False


@dataclass(frozen=True)
class PluginMetadata:
    """Value object representing plugin metadata."""
    
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[PluginDependency] = field(default_factory=list)
    homepage: Optional[str] = None
    license: Optional[str] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def id(self) -> str:
        """
        Get the plugin ID.
        
        Returns:
            Plugin ID (name-version)
        """
        return f"{self.name}-{self.version}"
    
    def is_compatible_with_app_version(self, app_version: str) -> bool:
        """
        Check if this plugin is compatible with the given application version.
        
        Args:
            app_version: Application version to check against
            
        Returns:
            True if the plugin is compatible, False otherwise
        """
        try:
            # Check minimum version constraint
            if self.min_app_version and semver.compare(app_version, self.min_app_version) < 0:
                return False
            
            # Check maximum version constraint
            if self.max_app_version and semver.compare(app_version, self.max_app_version) > 0:
                return False
            
            return True
        except Exception:
            # If there's any error in version comparison, assume not compatible
            return False
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if this plugin has the given tag.
        
        Args:
            tag: Tag to check for
            
        Returns:
            True if the plugin has the tag, False otherwise
        """
        return tag in self.tags


@dataclass
class Plugin:
    """Entity representing a plugin."""
    
    metadata: PluginMetadata
    module_path: str
    status: PluginStatus = PluginStatus.INACTIVE
    error_message: Optional[str] = None
    instance: Optional[Any] = None
    loaded_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, metadata: PluginMetadata, module_path: str) -> 'Plugin':
        """
        Create a new plugin.
        
        Args:
            metadata: Plugin metadata
            module_path: Path to the plugin module
            
        Returns:
            Plugin instance
        """
        return cls(
            metadata=metadata,
            module_path=module_path,
            status=PluginStatus.INACTIVE
        )
    
    def activate(self) -> bool:
        """
        Activate the plugin.
        
        Returns:
            True if successful, False otherwise
        """
        if self.status == PluginStatus.ACTIVE:
            return True
        
        if self.status == PluginStatus.INCOMPATIBLE:
            self.error_message = "Plugin is incompatible with the current application version"
            return False
        
        try:
            # Load the plugin module
            if not self.instance:
                self._load_module()
            
            # Mark as active
            self.status = PluginStatus.ACTIVE
            self.loaded_at = datetime.now()
            self.error_message = None
            
            return True
            
        except Exception as e:
            # Mark as error
            self.status = PluginStatus.ERROR
            self.error_message = str(e)
            
            return False
    
    def deactivate(self) -> bool:
        """
        Deactivate the plugin.
        
        Returns:
            True if successful, False otherwise
        """
        if self.status != PluginStatus.ACTIVE:
            return True
        
        try:
            # Mark as inactive
            self.status = PluginStatus.INACTIVE
            
            return True
            
        except Exception as e:
            # Mark as error
            self.status = PluginStatus.ERROR
            self.error_message = str(e)
            
            return False
    
    def _load_module(self) -> None:
        """
        Load the plugin module.
        
        Raises:
            ImportError: If the module cannot be loaded
            AttributeError: If the module does not have the required attributes
        """
        # Check if the module file exists
        if not os.path.exists(self.module_path):
            raise ImportError(f"Plugin module file not found: {self.module_path}")
        
        # Load the module
        module_name = os.path.splitext(os.path.basename(self.module_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, self.module_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load plugin module: {self.module_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Check if the module has the required attributes
        if not hasattr(module, 'create_plugin'):
            raise AttributeError(f"Plugin module does not have a create_plugin function: {self.module_path}")
        
        # Create the plugin instance
        self.instance = module.create_plugin()
    
    @property
    def is_active(self) -> bool:
        """
        Check if the plugin is active.
        
        Returns:
            True if the plugin is active, False otherwise
        """
        return self.status == PluginStatus.ACTIVE
    
    @property
    def has_error(self) -> bool:
        """
        Check if the plugin has an error.
        
        Returns:
            True if the plugin has an error, False otherwise
        """
        return self.status == PluginStatus.ERROR
    
    @property
    def is_compatible(self) -> bool:
        """
        Check if the plugin is compatible.
        
        Returns:
            True if the plugin is compatible, False otherwise
        """
        return self.status != PluginStatus.INCOMPATIBLE


@dataclass
class PluginEvent:
    """Value object representing a plugin event."""
    
    plugin: Plugin
    event_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_activation_event(cls, plugin: Plugin) -> 'PluginEvent':
        """
        Create a plugin activation event.
        
        Args:
            plugin: Plugin that was activated
            
        Returns:
            PluginEvent instance
        """
        return cls(
            plugin=plugin,
            event_type="activation"
        )
    
    @classmethod
    def create_deactivation_event(cls, plugin: Plugin) -> 'PluginEvent':
        """
        Create a plugin deactivation event.
        
        Args:
            plugin: Plugin that was deactivated
            
        Returns:
            PluginEvent instance
        """
        return cls(
            plugin=plugin,
            event_type="deactivation"
        )
    
    @classmethod
    def create_error_event(cls, plugin: Plugin, error_message: str) -> 'PluginEvent':
        """
        Create a plugin error event.
        
        Args:
            plugin: Plugin that had an error
            error_message: Error message
            
        Returns:
            PluginEvent instance
        """
        return cls(
            plugin=plugin,
            event_type="error",
            details={"error_message": error_message}
        )
    
    @property
    def is_activation(self) -> bool:
        """
        Check if this is an activation event.
        
        Returns:
            True if this is an activation event, False otherwise
        """
        return self.event_type == "activation"
    
    @property
    def is_deactivation(self) -> bool:
        """
        Check if this is a deactivation event.
        
        Returns:
            True if this is a deactivation event, False otherwise
        """
        return self.event_type == "deactivation"
    
    @property
    def is_error(self) -> bool:
        """
        Check if this is an error event.
        
        Returns:
            True if this is an error event, False otherwise
        """
        return self.event_type == "error"