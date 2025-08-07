"""
Lazy Import Utilities

This module provides utilities for lazy loading of heavy dependencies
to improve startup time and reduce memory usage.
"""

import importlib
import logging
from typing import Any, Dict, Optional, Callable, Union
from functools import wraps

logger = logging.getLogger(__name__)

# Cache for lazy-loaded modules
_lazy_cache: Dict[str, Any] = {}

# Heavy dependencies that should be lazy-loaded
HEAVY_DEPENDENCIES = {
    'plotly': ['plotly.graph_objects', 'plotly.express', 'plotly.offline'],
    'weasyprint': ['weasyprint'],
    'beautifulsoup4': ['bs4'],
    'geoip2': ['geoip2.database'],
    'rich': ['rich.console', 'rich.table', 'rich.panel'],
    'prompt_toolkit': ['prompt_toolkit'],
    'psutil': ['psutil'],
    'tqdm': ['tqdm']
}


class LazyImport:
    """
    A lazy import wrapper that defers module loading until first access.
    """
    
    def __init__(self, module_name: str, fallback: Optional[Any] = None):
        """
        Initialize lazy import.
        
        Args:
            module_name: Name of the module to import lazily
            fallback: Fallback value if import fails
        """
        self._module_name = module_name
        self._module = None
        self._fallback = fallback
        self._import_attempted = False
    
    def _import_module(self) -> Any:
        """Import the module if not already imported."""
        if not self._import_attempted:
            self._import_attempted = True
            try:
                self._module = importlib.import_module(self._module_name)
                logger.debug(f"Lazy loaded module: {self._module_name}")
            except ImportError as e:
                logger.warning(f"Failed to lazy load {self._module_name}: {e}")
                self._module = self._fallback
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from the lazily imported module."""
        module = self._import_module()
        if module is None:
            raise AttributeError(f"Module {self._module_name} not available and no fallback provided")
        return getattr(module, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """Make the lazy import callable if the module is callable."""
        module = self._import_module()
        if module is None:
            raise RuntimeError(f"Module {self._module_name} not available and no fallback provided")
        return module(*args, **kwargs)
    
    @property
    def is_available(self) -> bool:
        """Check if the module is available."""
        module = self._import_module()
        return module is not None and module is not self._fallback


def lazy_import(module_name: str, fallback: Optional[Any] = None) -> LazyImport:
    """
    Create a lazy import for a module.
    
    Args:
        module_name: Name of the module to import lazily
        fallback: Fallback value if import fails
        
    Returns:
        LazyImport instance
    """
    if module_name in _lazy_cache:
        return _lazy_cache[module_name]
    
    lazy_module = LazyImport(module_name, fallback)
    _lazy_cache[module_name] = lazy_module
    return lazy_module


def requires_dependency(dependency: str, 
                       feature_name: Optional[str] = None,
                       fallback_return: Any = None) -> Callable:
    """
    Decorator that checks if a dependency is available before executing a function.
    
    Args:
        dependency: Name of the required dependency
        feature_name: Human-readable name of the feature (for error messages)
        fallback_return: Value to return if dependency is not available
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            lazy_module = lazy_import(dependency)
            if not lazy_module.is_available:
                feature = feature_name or dependency
                logger.warning(f"Feature '{feature}' not available: {dependency} not installed")
                if fallback_return is not None:
                    return fallback_return
                raise ImportError(f"Required dependency '{dependency}' not available for feature '{feature}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_lazy_module(module_name: str, fallback: Optional[Any] = None) -> LazyImport:
    """
    Get a lazy-loaded module with optional fallback.
    
    Args:
        module_name: Name of the module to load lazily
        fallback: Fallback value if module is not available
        
    Returns:
        LazyImport instance
    """
    return lazy_import(module_name, fallback)


# Pre-configured lazy imports for common heavy dependencies
plotly = lazy_import('plotly.graph_objects')
plotly_express = lazy_import('plotly.express')
weasyprint = lazy_import('weasyprint')
beautifulsoup = lazy_import('bs4', fallback=None)
geoip2 = lazy_import('geoip2.database')
rich_console = lazy_import('rich.console')
rich_table = lazy_import('rich.table')
rich_panel = lazy_import('rich.panel')
prompt_toolkit = lazy_import('prompt_toolkit')
psutil = lazy_import('psutil')
tqdm = lazy_import('tqdm')


def check_lazy_dependencies() -> Dict[str, bool]:
    """
    Check availability of all lazy-loaded dependencies.
    
    Returns:
        Dictionary mapping dependency names to availability status
    """
    results = {}
    
    # Check pre-configured lazy imports
    lazy_modules = {
        'plotly': plotly,
        'plotly_express': plotly_express,
        'weasyprint': weasyprint,
        'beautifulsoup4': beautifulsoup,
        'geoip2': geoip2,
        'rich': rich_console,
        'prompt_toolkit': prompt_toolkit,
        'psutil': psutil,
        'tqdm': tqdm
    }
    
    for name, lazy_module in lazy_modules.items():
        results[name] = lazy_module.is_available
    
    return results


def clear_lazy_cache() -> None:
    """Clear the lazy import cache."""
    global _lazy_cache
    _lazy_cache.clear()
    logger.debug("Cleared lazy import cache")


# Example usage functions
def create_plot_with_fallback(data, title="Plot"):
    """
    Create a plot using plotly with graceful fallback.
    
    Args:
        data: Data to plot
        title: Plot title
        
    Returns:
        Plot object or None if plotly not available
    """
    if not plotly.is_available:
        logger.warning("Plotly not available, cannot create plot")
        return None
    
    try:
        fig = plotly.Figure()
        fig.add_trace(plotly.Scatter(y=data, mode='lines', name=title))
        fig.update_layout(title=title)
        return fig
    except Exception as e:
        logger.error(f"Error creating plot: {e}")
        return None


def show_progress_with_fallback(iterable, description="Processing"):
    """
    Show progress bar with tqdm fallback.
    
    Args:
        iterable: Iterable to wrap
        description: Progress description
        
    Returns:
        Progress-wrapped iterable or original iterable if tqdm not available
    """
    if tqdm.is_available:
        return tqdm(iterable, desc=description)
    else:
        logger.info(f"{description}...")
        return iterable