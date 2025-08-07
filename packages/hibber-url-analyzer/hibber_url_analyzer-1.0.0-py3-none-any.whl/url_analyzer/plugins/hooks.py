"""
Hooks Module for URL Analyzer

This module provides a hook system for extending URL Analyzer functionality
at various points in the processing pipeline. Hooks allow custom code to be
executed at specific points without modifying the core codebase.
"""

import inspect
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from enum import Enum, auto
import logging

from url_analyzer.utils.logging import get_logger

logger = get_logger(__name__)

class HookType(Enum):
    """Enum defining the types of hooks available in the system."""
    PRE_PROCESSING = auto()  # Before URL processing begins
    POST_PROCESSING = auto()  # After URL processing completes
    PRE_CLASSIFICATION = auto()  # Before URL classification
    POST_CLASSIFICATION = auto()  # After URL classification
    PRE_REPORT = auto()  # Before report generation
    POST_REPORT = auto()  # After report generation
    PRE_EXPORT = auto()  # Before data export
    POST_EXPORT = auto()  # After data export
    PRE_ANALYSIS = auto()  # Before data analysis
    POST_ANALYSIS = auto()  # After data analysis
    CUSTOM = auto()  # For custom hook points


class HookPriority(Enum):
    """Enum defining the priority levels for hook execution."""
    HIGHEST = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    LOWEST = 0


class HookManager:
    """
    Manager for registering and executing hooks.
    
    This class provides methods for registering hook functions and executing
    them at specific points in the processing pipeline.
    """
    
    def __init__(self):
        """Initialize the hook manager."""
        self._hooks: Dict[HookType, List[Tuple[Callable, HookPriority, str]]] = {
            hook_type: [] for hook_type in HookType
        }
        self._custom_hooks: Dict[str, List[Tuple[Callable, HookPriority, str]]] = {}
        logger.debug("HookManager initialized")
    
    def register_hook(self, 
                     hook_type: Union[HookType, str], 
                     callback: Callable, 
                     priority: HookPriority = HookPriority.NORMAL,
                     name: Optional[str] = None) -> bool:
        """
        Register a hook function to be called at a specific point.
        
        Args:
            hook_type: The type of hook or custom hook name
            callback: The function to call
            priority: Priority level for execution order
            name: Optional name for the hook (defaults to function name)
            
        Returns:
            Boolean indicating whether registration was successful
        """
        if name is None:
            name = callback.__name__
            
        if isinstance(hook_type, HookType):
            if hook_type == HookType.CUSTOM:
                logger.error("Cannot register to generic CUSTOM hook type. Use a string name instead.")
                return False
                
            self._hooks[hook_type].append((callback, priority, name))
            self._hooks[hook_type].sort(key=lambda x: x[1].value, reverse=True)
            logger.debug(f"Registered hook '{name}' for {hook_type.name} with priority {priority.name}")
        else:
            # This is a custom hook identified by string name
            if hook_type not in self._custom_hooks:
                self._custom_hooks[hook_type] = []
            
            self._custom_hooks[hook_type].append((callback, priority, name))
            self._custom_hooks[hook_type].sort(key=lambda x: x[1].value, reverse=True)
            logger.debug(f"Registered custom hook '{name}' for '{hook_type}' with priority {priority.name}")
            
        return True
    
    def unregister_hook(self, hook_type: Union[HookType, str], name: str) -> bool:
        """
        Unregister a hook function.
        
        Args:
            hook_type: The type of hook or custom hook name
            name: The name of the hook to unregister
            
        Returns:
            Boolean indicating whether unregistration was successful
        """
        if isinstance(hook_type, HookType):
            for i, (_, _, hook_name) in enumerate(self._hooks[hook_type]):
                if hook_name == name:
                    self._hooks[hook_type].pop(i)
                    logger.debug(f"Unregistered hook '{name}' from {hook_type.name}")
                    return True
        else:
            # This is a custom hook identified by string name
            if hook_type in self._custom_hooks:
                for i, (_, _, hook_name) in enumerate(self._custom_hooks[hook_type]):
                    if hook_name == name:
                        self._custom_hooks[hook_type].pop(i)
                        logger.debug(f"Unregistered custom hook '{name}' from '{hook_type}'")
                        return True
        
        logger.warning(f"Hook '{name}' not found for {hook_type}")
        return False
    
    def execute_hooks(self, 
                     hook_type: Union[HookType, str], 
                     context: Dict[str, Any],
                     stop_on_error: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute all hooks of a specific type.
        
        Args:
            hook_type: The type of hook or custom hook name
            context: Dictionary containing context data for the hooks
            stop_on_error: Whether to stop execution if a hook raises an exception
            
        Returns:
            Tuple of (success, updated_context)
        """
        hooks_to_execute = []
        
        if isinstance(hook_type, HookType):
            hooks_to_execute = self._hooks[hook_type]
            logger.debug(f"Executing {len(hooks_to_execute)} hooks for {hook_type.name}")
        else:
            # This is a custom hook identified by string name
            if hook_type in self._custom_hooks:
                hooks_to_execute = self._custom_hooks[hook_type]
                logger.debug(f"Executing {len(hooks_to_execute)} custom hooks for '{hook_type}'")
            else:
                logger.debug(f"No hooks registered for custom hook '{hook_type}'")
        
        success = True
        for callback, priority, name in hooks_to_execute:
            try:
                # Get the signature of the callback to determine if it expects a return value
                sig = inspect.signature(callback)
                
                if len(sig.parameters) > 0:
                    # Pass the context to the callback
                    result = callback(context)
                    
                    # If the callback returns a dictionary, update the context
                    if isinstance(result, dict):
                        context.update(result)
                else:
                    # Just call the callback without arguments
                    callback()
                    
                logger.debug(f"Successfully executed hook '{name}'")
            except Exception as e:
                logger.error(f"Error executing hook '{name}': {str(e)}")
                success = False
                if stop_on_error:
                    break
        
        return success, context
    
    def get_registered_hooks(self, hook_type: Optional[Union[HookType, str]] = None) -> Dict[str, List[str]]:
        """
        Get information about registered hooks.
        
        Args:
            hook_type: Optional type to filter by
            
        Returns:
            Dictionary mapping hook types to lists of hook names
        """
        result = {}
        
        if hook_type is None:
            # Return all hooks
            for ht in HookType:
                if ht != HookType.CUSTOM:
                    result[ht.name] = [name for _, _, name in self._hooks[ht]]
            
            # Add custom hooks
            for custom_name, hooks in self._custom_hooks.items():
                result[f"CUSTOM:{custom_name}"] = [name for _, _, name in hooks]
        elif isinstance(hook_type, HookType):
            # Return hooks for a specific type
            result[hook_type.name] = [name for _, _, name in self._hooks[hook_type]]
        else:
            # Return hooks for a specific custom type
            if hook_type in self._custom_hooks:
                result[f"CUSTOM:{hook_type}"] = [name for _, _, name in self._custom_hooks[hook_type]]
            else:
                result[f"CUSTOM:{hook_type}"] = []
        
        return result


# Create a global hook manager instance
hook_manager = HookManager()