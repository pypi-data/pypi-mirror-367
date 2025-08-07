"""
Type Definitions Module

This module provides custom type definitions for complex data structures
used throughout the URL Analyzer codebase. These type definitions improve
type checking and documentation.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Pattern, Callable, TypeVar, NewType

# Basic type aliases
StrDict = Dict[str, str]
AnyDict = Dict[str, Any]
StrList = List[str]
StrOrNone = Optional[str]
IntOrNone = Optional[int]
BoolOrNone = Optional[bool]

# Complex type aliases
ConfigDict = Dict[str, Any]
PatternDict = Dict[str, Pattern]
CategoryPatterns = Dict[str, List[Pattern]]
UrlCategory = Tuple[str, bool]  # (category, is_sensitive)
UrlData = Dict[str, Any]  # Data extracted from a URL
StatDict = Dict[str, Any]  # Statistics dictionary

# Function types
UrlClassifierFunc = Callable[[str], UrlCategory]
UrlProcessorFunc = Callable[[str], UrlData]
ValidationFunc = Callable[[Any], Any]
ProgressCallback = Callable[[int, int, Optional[str]], None]

# NewTypes for stronger typing
RuleId = NewType('RuleId', str)
PluginId = NewType('PluginId', str)
TemplateId = NewType('TemplateId', str)

# Generic types
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Type aliases for plugin system
PluginRegistry = Dict[str, Any]
PluginConfig = Dict[str, Any]
PluginResult = Dict[str, Any]

# Type aliases for reporting
ReportData = Dict[str, Any]
ChartData = Dict[str, Any]
TemplateContext = Dict[str, Any]

# Type aliases for caching
CacheKey = Union[str, Tuple[Any, ...]]
CacheValue = Any
CacheDict = Dict[CacheKey, CacheValue]

# Type aliases for concurrency
WorkItem = Any
WorkResult = Any
WorkQueue = List[WorkItem]
ResultCallback = Callable[[WorkResult], None]