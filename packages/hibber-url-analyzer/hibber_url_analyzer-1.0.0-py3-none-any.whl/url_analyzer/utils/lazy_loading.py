"""
Lazy Loading Module

This module provides lazy loading functionality for resource-intensive components
in the URL Analyzer. Lazy loading defers the initialization of objects until they
are actually needed, reducing memory usage during startup and improving performance.
"""

import importlib
import functools
import threading
import time
from typing import Dict, Any, Optional, Callable, Type, TypeVar, Generic, Union, List, Tuple

# Import logging
from url_analyzer.utils.logging import get_logger

# Create logger
logger = get_logger(__name__)

# Type variable for generic types
T = TypeVar('T')


class LazyObject(Generic[T]):
    """
    A proxy that lazily initializes an object when it's first accessed.
    
    This class is useful for deferring the initialization of resource-intensive
    objects until they are actually needed.
    """
    
    def __init__(self, factory: Callable[[], T]):
        """
        Initialize the lazy object.
        
        Args:
            factory: Function that creates the actual object when needed
        """
        self._factory = factory
        self._object = None
        self._lock = threading.RLock()
        self._initialized = False
    
    def _initialize(self) -> None:
        """Initialize the object if it hasn't been initialized yet."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    start_time = time.time()
                    self._object = self._factory()
                    elapsed_time = time.time() - start_time
                    logger.debug(f"Lazy initialized object in {elapsed_time:.3f}s: {type(self._object).__name__}")
                    self._initialized = True
    
    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the underlying object.
        
        Args:
            name: Name of the attribute to get
            
        Returns:
            Attribute value
        """
        self._initialize()
        return getattr(self._object, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Call the underlying object.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of calling the underlying object
        """
        self._initialize()
        return self._object(*args, **kwargs)
    
    def get_object(self) -> T:
        """
        Get the underlying object, initializing it if necessary.
        
        Returns:
            Underlying object
        """
        self._initialize()
        return self._object
    
    def is_initialized(self) -> bool:
        """
        Check if the object has been initialized.
        
        Returns:
            True if the object has been initialized, False otherwise
        """
        return self._initialized


class LazyModule:
    """
    A proxy that lazily imports a module when it's first accessed.
    
    This class is useful for deferring the import of modules until they are
    actually needed, reducing memory usage during startup.
    """
    
    def __init__(self, module_name: str):
        """
        Initialize the lazy module.
        
        Args:
            module_name: Name of the module to import lazily
        """
        self._module_name = module_name
        self._module = None
        self._lock = threading.RLock()
        self._initialized = False
    
    def _initialize(self) -> None:
        """Import the module if it hasn't been imported yet."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    start_time = time.time()
                    self._module = importlib.import_module(self._module_name)
                    elapsed_time = time.time() - start_time
                    logger.debug(f"Lazy imported module in {elapsed_time:.3f}s: {self._module_name}")
                    self._initialized = True
    
    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the underlying module.
        
        Args:
            name: Name of the attribute to get
            
        Returns:
            Attribute value
        """
        self._initialize()
        return getattr(self._module, name)
    
    def get_module(self) -> Any:
        """
        Get the underlying module, importing it if necessary.
        
        Returns:
            Underlying module
        """
        self._initialize()
        return self._module
    
    def is_initialized(self) -> bool:
        """
        Check if the module has been imported.
        
        Returns:
            True if the module has been imported, False otherwise
        """
        return self._initialized


class LazyClass(Generic[T]):
    """
    A proxy that lazily initializes a class when it's first accessed.
    
    This class is useful for deferring the initialization of resource-intensive
    classes until they are actually needed.
    """
    
    def __init__(self, module_name: str, class_name: str):
        """
        Initialize the lazy class.
        
        Args:
            module_name: Name of the module containing the class
            class_name: Name of the class to initialize lazily
        """
        self._module_name = module_name
        self._class_name = class_name
        self._class = None
        self._lock = threading.RLock()
        self._initialized = False
    
    def _initialize(self) -> None:
        """Initialize the class if it hasn't been initialized yet."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    start_time = time.time()
                    module = importlib.import_module(self._module_name)
                    self._class = getattr(module, self._class_name)
                    elapsed_time = time.time() - start_time
                    logger.debug(f"Lazy initialized class in {elapsed_time:.3f}s: {self._module_name}.{self._class_name}")
                    self._initialized = True
    
    def __call__(self, *args, **kwargs) -> T:
        """
        Create an instance of the class.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Instance of the class
        """
        self._initialize()
        return self._class(*args, **kwargs)
    
    def get_class(self) -> Type[T]:
        """
        Get the underlying class, initializing it if necessary.
        
        Returns:
            Underlying class
        """
        self._initialize()
        return self._class
    
    def is_initialized(self) -> bool:
        """
        Check if the class has been initialized.
        
        Returns:
            True if the class has been initialized, False otherwise
        """
        return self._initialized


# Registry of lazy-loaded components
_lazy_components: Dict[str, Union[LazyObject, LazyModule, LazyClass]] = {}
_registry_lock = threading.RLock()


def lazy_import(module_name: str) -> LazyModule:
    """
    Lazily import a module.
    
    Args:
        module_name: Name of the module to import lazily
        
    Returns:
        LazyModule proxy
    """
    with _registry_lock:
        key = f"module:{module_name}"
        if key not in _lazy_components:
            _lazy_components[key] = LazyModule(module_name)
        return _lazy_components[key]  # type: ignore


def lazy_class(module_name: str, class_name: str) -> LazyClass:
    """
    Lazily initialize a class.
    
    Args:
        module_name: Name of the module containing the class
        class_name: Name of the class to initialize lazily
        
    Returns:
        LazyClass proxy
    """
    with _registry_lock:
        key = f"class:{module_name}.{class_name}"
        if key not in _lazy_components:
            _lazy_components[key] = LazyClass(module_name, class_name)
        return _lazy_components[key]  # type: ignore


def lazy_object(factory: Callable[[], T]) -> LazyObject[T]:
    """
    Lazily initialize an object.
    
    Args:
        factory: Function that creates the object when needed
        
    Returns:
        LazyObject proxy
    """
    return LazyObject(factory)


def lazy_function(module_name: str, function_name: str) -> Callable:
    """
    Lazily import a function.
    
    Args:
        module_name: Name of the module containing the function
        function_name: Name of the function to import lazily
        
    Returns:
        Function that lazily imports and calls the actual function
    """
    lazy_mod = lazy_import(module_name)
    
    @functools.wraps(getattr(lazy_mod.get_module(), function_name) if lazy_mod.is_initialized() else lambda *a, **kw: None)
    def wrapper(*args, **kwargs):
        func = getattr(lazy_mod, function_name)
        return func(*args, **kwargs)
    
    return wrapper


# Decorator for lazy initialization
def lazy_init(func):
    """
    Decorator for lazy initialization of a function.
    
    This decorator defers the execution of the decorated function until
    the returned object is actually accessed.
    
    Args:
        func: Function to decorate
        
    Returns:
        LazyObject proxy
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return LazyObject(lambda: func(*args, **kwargs))
    
    return wrapper


# Decorator for lazy loading of resource-intensive components
def lazy_component(component_name: str = None):
    """
    Decorator for lazy loading of resource-intensive components.
    
    This decorator registers a factory function for a component that will be
    lazily initialized when it's first accessed.
    
    Args:
        component_name: Name of the component (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(factory):
        nonlocal component_name
        if component_name is None:
            component_name = factory.__name__
        
        with _registry_lock:
            key = f"component:{component_name}"
            if key not in _lazy_components:
                _lazy_components[key] = LazyObject(factory)
        
        @functools.wraps(factory)
        def wrapper(*args, **kwargs):
            with _registry_lock:
                lazy_obj = _lazy_components[key]
                if not lazy_obj.is_initialized():
                    # If arguments are provided, we need to create a new instance
                    if args or kwargs:
                        return factory(*args, **kwargs)
                return lazy_obj.get_object()
        
        return wrapper
    
    return decorator


def get_lazy_component(component_name: str) -> Any:
    """
    Get a lazily loaded component by name.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Component instance
        
    Raises:
        KeyError: If the component is not registered
    """
    with _registry_lock:
        key = f"component:{component_name}"
        if key not in _lazy_components:
            raise KeyError(f"Lazy component not found: {component_name}")
        return _lazy_components[key].get_object()


def is_component_initialized(component_name: str) -> bool:
    """
    Check if a lazily loaded component has been initialized.
    
    Args:
        component_name: Name of the component
        
    Returns:
        True if the component has been initialized, False otherwise
        
    Raises:
        KeyError: If the component is not registered
    """
    with _registry_lock:
        key = f"component:{component_name}"
        if key not in _lazy_components:
            raise KeyError(f"Lazy component not found: {component_name}")
        return _lazy_components[key].is_initialized()


def get_initialized_components() -> List[str]:
    """
    Get a list of initialized component names.
    
    Returns:
        List of initialized component names
    """
    with _registry_lock:
        return [
            key.split(':', 1)[1]
            for key, component in _lazy_components.items()
            if key.startswith('component:') and component.is_initialized()
        ]


def get_component_stats() -> Dict[str, Any]:
    """
    Get statistics about lazy-loaded components.
    
    Returns:
        Dictionary with component statistics
    """
    with _registry_lock:
        total_components = len([k for k in _lazy_components if k.startswith('component:')])
        initialized_components = len([
            k for k, c in _lazy_components.items()
            if k.startswith('component:') and c.is_initialized()
        ])
        
        total_modules = len([k for k in _lazy_components if k.startswith('module:')])
        initialized_modules = len([
            k for k, c in _lazy_components.items()
            if k.startswith('module:') and c.is_initialized()
        ])
        
        total_classes = len([k for k in _lazy_components if k.startswith('class:')])
        initialized_classes = len([
            k for k, c in _lazy_components.items()
            if k.startswith('class:') and c.is_initialized()
        ])
        
        return {
            "total_components": total_components,
            "initialized_components": initialized_components,
            "total_modules": total_modules,
            "initialized_modules": initialized_modules,
            "total_classes": total_classes,
            "initialized_classes": initialized_classes,
            "total_lazy_objects": total_components + total_modules + total_classes,
            "total_initialized": initialized_components + initialized_modules + initialized_classes
        }


# Common resource-intensive components that should be lazily loaded
pandas = lazy_import('pandas')
numpy = lazy_import('numpy')
plotly = lazy_import('plotly.graph_objects')
beautifulsoup = lazy_import('bs4')
requests = lazy_import('requests')
tldextract = lazy_import('tldextract')
geoip2 = lazy_import('geoip2.database')
pycountry = lazy_import('pycountry')
weasyprint = lazy_import('weasyprint')
openpyxl = lazy_import('openpyxl')
rich = lazy_import('rich')
prompt_toolkit = lazy_import('prompt_toolkit')


# Lazy initialization of resource-intensive components
@lazy_component('tld_extractor')
def create_tld_extractor():
    """
    Create a TLD extractor instance.
    
    Returns:
        TLD extractor instance
    """
    import tldextract
    return tldextract.TLDExtract(cache_file='.tld_cache')


@lazy_component('geoip_reader')
def create_geoip_reader():
    """
    Create a GeoIP reader instance.
    
    Returns:
        GeoIP reader instance
    """
    import geoip2.database
    import os
    
    # Check if GeoIP database exists
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'GeoLite2-City.mmdb')
    if not os.path.exists(db_path):
        logger.warning(f"GeoIP database not found: {db_path}")
        return None
    
    try:
        return geoip2.database.Reader(db_path)
    except Exception as e:
        logger.error(f"Error creating GeoIP reader: {e}")
        return None


@lazy_component('html_parser')
def create_html_parser():
    """
    Create an HTML parser instance.
    
    Returns:
        HTML parser instance
    """
    from bs4 import BeautifulSoup
    
    # Create a dummy parser that will be replaced with the actual parser when needed
    class LazyBeautifulSoup:
        def __call__(self, markup, features='html.parser'):
            return BeautifulSoup(markup, features)
    
    return LazyBeautifulSoup()


# Initialize lazy components registry
logger.debug("Initialized lazy loading module")