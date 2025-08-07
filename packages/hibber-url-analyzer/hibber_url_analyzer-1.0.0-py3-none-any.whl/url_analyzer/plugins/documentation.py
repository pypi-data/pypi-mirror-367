"""
Plugin Documentation Generator Module

This module provides functionality for generating documentation for plugins
in the URL Analyzer system. It extracts information from plugin metadata,
docstrings, and source code to create comprehensive documentation.
"""

import os
import inspect
import re
import json
import logging
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from pathlib import Path
import datetime

from url_analyzer.plugins.domain import Plugin, PluginMetadata, PluginType, PluginStatus, PluginDependency
from url_analyzer.plugins.registry import PluginRegistry
from url_analyzer.utils.logging import get_logger

# Try to import optional dependencies
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

try:
    import docstring_parser
    DOCSTRING_PARSER_AVAILABLE = True
except ImportError:
    DOCSTRING_PARSER_AVAILABLE = False

# Create logger
logger = get_logger(__name__)

# Constants
DOCS_DIR = "plugin_docs"
TEMPLATES_DIR = "doc_templates"


class DocstringParser:
    """
    Parser for Python docstrings.
    
    This class extracts information from docstrings, including descriptions,
    parameters, return values, and exceptions.
    """
    
    @staticmethod
    def parse(docstring: str) -> Dict[str, Any]:
        """
        Parse a docstring and extract its components.
        
        Args:
            docstring: The docstring to parse
            
        Returns:
            Dictionary containing the parsed docstring components
        """
        if DOCSTRING_PARSER_AVAILABLE:
            try:
                parsed = docstring_parser.parse(docstring)
                
                result = {
                    'short_description': parsed.short_description,
                    'long_description': parsed.long_description,
                    'params': [],
                    'returns': None,
                    'raises': []
                }
                
                # Extract parameters
                for param in parsed.params:
                    result['params'].append({
                        'name': param.arg_name,
                        'type': param.type_name,
                        'description': param.description,
                        'default': param.default,
                        'is_optional': param.is_optional
                    })
                
                # Extract return value
                if parsed.returns:
                    result['returns'] = {
                        'type': parsed.returns.type_name,
                        'description': parsed.returns.description
                    }
                
                # Extract exceptions
                for exception in parsed.raises:
                    result['raises'].append({
                        'type': exception.type_name,
                        'description': exception.description
                    })
                
                return result
            except Exception as e:
                logger.warning(f"Error parsing docstring with docstring_parser: {e}")
        
        # Fallback to simple parsing
        return DocstringParser._simple_parse(docstring)
    
    @staticmethod
    def _simple_parse(docstring: str) -> Dict[str, Any]:
        """
        Simple docstring parser for when docstring_parser is not available.
        
        Args:
            docstring: The docstring to parse
            
        Returns:
            Dictionary containing the parsed docstring components
        """
        if not docstring:
            return {
                'short_description': '',
                'long_description': '',
                'params': [],
                'returns': None,
                'raises': []
            }
        
        # Clean up the docstring
        lines = [line.strip() for line in docstring.strip().split('\n')]
        
        # Extract short and long descriptions
        short_description = lines[0] if lines else ''
        
        long_description_lines = []
        params = []
        returns = None
        raises = []
        
        # Parse the rest of the docstring
        current_section = 'long_description'
        current_item = None
        
        for line in lines[1:]:
            if not line:
                continue
            
            # Check for section headers
            if line.startswith('Args:') or line.startswith('Parameters:'):
                current_section = 'params'
                continue
            elif line.startswith('Returns:'):
                current_section = 'returns'
                returns = {'type': '', 'description': ''}
                continue
            elif line.startswith('Raises:') or line.startswith('Exceptions:'):
                current_section = 'raises'
                continue
            
            # Process the line based on the current section
            if current_section == 'long_description':
                long_description_lines.append(line)
            elif current_section == 'params':
                # Check if this is a new parameter
                param_match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(\([^)]*\))?\s*:\s*(.*)$', line)
                if param_match:
                    name = param_match.group(1)
                    type_name = param_match.group(2)[1:-1] if param_match.group(2) else ''
                    description = param_match.group(3)
                    
                    current_item = {
                        'name': name,
                        'type': type_name,
                        'description': description,
                        'default': '',
                        'is_optional': False
                    }
                    params.append(current_item)
                elif current_item:
                    # Continue the description of the current parameter
                    current_item['description'] += ' ' + line.strip()
            elif current_section == 'returns':
                if returns:
                    # Check if this line contains a type
                    type_match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*|\([^)]*\))\s*:\s*(.*)$', line)
                    if type_match and not returns['type']:
                        returns['type'] = type_match.group(1)
                        returns['description'] = type_match.group(2)
                    else:
                        # Continue the description
                        returns['description'] += ' ' + line.strip()
            elif current_section == 'raises':
                # Check if this is a new exception
                exception_match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$', line)
                if exception_match:
                    type_name = exception_match.group(1)
                    description = exception_match.group(2)
                    
                    current_item = {
                        'type': type_name,
                        'description': description
                    }
                    raises.append(current_item)
                elif current_item:
                    # Continue the description of the current exception
                    current_item['description'] += ' ' + line.strip()
        
        return {
            'short_description': short_description,
            'long_description': '\n'.join(long_description_lines),
            'params': params,
            'returns': returns,
            'raises': raises
        }


class PluginDocumentationGenerator:
    """
    Generator for plugin documentation.
    
    This class generates documentation for plugins in various formats,
    including HTML, Markdown, and JSON.
    """
    
    def __init__(self, registry: PluginRegistry):
        """
        Initialize the plugin documentation generator.
        
        Args:
            registry: Plugin registry to use for accessing plugins
        """
        self._registry = registry
        self._docs_dir = os.path.join(os.path.dirname(__file__), DOCS_DIR)
        self._templates_dir = os.path.join(os.path.dirname(__file__), TEMPLATES_DIR)
        
        # Create docs directory if it doesn't exist
        os.makedirs(self._docs_dir, exist_ok=True)
        
        # Create templates directory if it doesn't exist
        os.makedirs(self._templates_dir, exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_default_templates()
        
        logger.info(f"Plugin documentation generator initialized")
    
    def _create_default_templates(self) -> None:
        """
        Create default documentation templates if they don't exist.
        """
        # HTML template
        html_template_path = os.path.join(self._templates_dir, 'plugin_doc.html')
        if not os.path.exists(html_template_path):
            with open(html_template_path, 'w') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ plugin.metadata.name }} - Plugin Documentation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #0066cc;
        }
        .metadata {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metadata-item {
            margin-bottom: 5px;
        }
        .metadata-label {
            font-weight: bold;
        }
        .method {
            border-bottom: 1px solid #ddd;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }
        .method-signature {
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            margin-bottom: 10px;
        }
        .param-name {
            font-weight: bold;
        }
        .param-type {
            color: #0066cc;
        }
        .return-type {
            color: #0066cc;
        }
        .exception-type {
            color: #cc0000;
        }
        .tag {
            display: inline-block;
            background-color: #e0e0e0;
            padding: 2px 8px;
            border-radius: 3px;
            margin-right: 5px;
            font-size: 0.9em;
        }
        .dependency {
            margin-bottom: 5px;
        }
        .optional {
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>{{ plugin.metadata.name }} - Plugin Documentation</h1>
    
    <div class="metadata">
        <div class="metadata-item">
            <span class="metadata-label">Version:</span> {{ plugin.metadata.version }}
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Author:</span> {{ plugin.metadata.author }}
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Type:</span> {{ plugin.metadata.plugin_type.name }}
        </div>
        {% if plugin.metadata.homepage %}
        <div class="metadata-item">
            <span class="metadata-label">Homepage:</span> <a href="{{ plugin.metadata.homepage }}">{{ plugin.metadata.homepage }}</a>
        </div>
        {% endif %}
        {% if plugin.metadata.license %}
        <div class="metadata-item">
            <span class="metadata-label">License:</span> {{ plugin.metadata.license }}
        </div>
        {% endif %}
        {% if plugin.metadata.min_app_version or plugin.metadata.max_app_version %}
        <div class="metadata-item">
            <span class="metadata-label">Compatibility:</span>
            {% if plugin.metadata.min_app_version %}
            ≥ {{ plugin.metadata.min_app_version }}
            {% endif %}
            {% if plugin.metadata.min_app_version and plugin.metadata.max_app_version %}
            and
            {% endif %}
            {% if plugin.metadata.max_app_version %}
            ≤ {{ plugin.metadata.max_app_version }}
            {% endif %}
        </div>
        {% endif %}
        {% if plugin.metadata.tags %}
        <div class="metadata-item">
            <span class="metadata-label">Tags:</span>
            {% for tag in plugin.metadata.tags %}
            <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    
    <h2>Description</h2>
    <p>{{ plugin.metadata.description }}</p>
    
    {% if plugin.metadata.dependencies %}
    <h2>Dependencies</h2>
    <ul>
        {% for dependency in plugin.metadata.dependencies %}
        <li class="dependency">
            <span class="metadata-label">{{ dependency.name }}</span>
            {{ dependency.version_constraint }}
            {% if dependency.optional %}
            <span class="optional">(optional)</span>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
    {% endif %}
    
    <h2>Methods</h2>
    {% for method in methods %}
    <div class="method">
        <h3>{{ method.name }}</h3>
        <div class="method-signature">{{ method.signature }}</div>
        
        {% if method.docstring.short_description %}
        <p>{{ method.docstring.short_description }}</p>
        {% endif %}
        
        {% if method.docstring.long_description %}
        <p>{{ method.docstring.long_description }}</p>
        {% endif %}
        
        {% if method.docstring.params %}
        <h4>Parameters</h4>
        <ul>
            {% for param in method.docstring.params %}
            <li>
                <span class="param-name">{{ param.name }}</span>
                {% if param.type %}
                <span class="param-type">({{ param.type }})</span>
                {% endif %}
                {% if param.is_optional %}
                <span class="optional">(optional)</span>
                {% endif %}
                {% if param.description %}
                : {{ param.description }}
                {% endif %}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {% if method.docstring.returns %}
        <h4>Returns</h4>
        <p>
            {% if method.docstring.returns.type %}
            <span class="return-type">{{ method.docstring.returns.type }}</span>:
            {% endif %}
            {{ method.docstring.returns.description }}
        </p>
        {% endif %}
        
        {% if method.docstring.raises %}
        <h4>Raises</h4>
        <ul>
            {% for exception in method.docstring.raises %}
            <li>
                <span class="exception-type">{{ exception.type }}</span>
                {% if exception.description %}
                : {{ exception.description }}
                {% endif %}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    {% endfor %}
    
    <footer>
        <p>Generated on {{ generation_date }} by URL Analyzer Plugin Documentation Generator</p>
    </footer>
</body>
</html>""")
            logger.info(f"Created default HTML template at {html_template_path}")
        
        # Markdown template
        md_template_path = os.path.join(self._templates_dir, 'plugin_doc.md')
        if not os.path.exists(md_template_path):
            with open(md_template_path, 'w') as f:
                f.write("""# {{ plugin.metadata.name }} - Plugin Documentation

## Metadata

- **Version:** {{ plugin.metadata.version }}
- **Author:** {{ plugin.metadata.author }}
- **Type:** {{ plugin.metadata.plugin_type.name }}
{% if plugin.metadata.homepage %}
- **Homepage:** [{{ plugin.metadata.homepage }}]({{ plugin.metadata.homepage }})
{% endif %}
{% if plugin.metadata.license %}
- **License:** {{ plugin.metadata.license }}
{% endif %}
{% if plugin.metadata.min_app_version or plugin.metadata.max_app_version %}
- **Compatibility:** 
  {% if plugin.metadata.min_app_version %}≥ {{ plugin.metadata.min_app_version }}{% endif %}
  {% if plugin.metadata.min_app_version and plugin.metadata.max_app_version %}and{% endif %}
  {% if plugin.metadata.max_app_version %}≤ {{ plugin.metadata.max_app_version }}{% endif %}
{% endif %}
{% if plugin.metadata.tags %}
- **Tags:** {% for tag in plugin.metadata.tags %}{{ tag }}{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}

## Description

{{ plugin.metadata.description }}

{% if plugin.metadata.dependencies %}
## Dependencies

{% for dependency in plugin.metadata.dependencies %}
- **{{ dependency.name }}** {{ dependency.version_constraint }}{% if dependency.optional %} (optional){% endif %}
{% endfor %}
{% endif %}

## Methods

{% for method in methods %}
### {{ method.name }}

```python
{{ method.signature }}
```

{% if method.docstring.short_description %}
{{ method.docstring.short_description }}
{% endif %}

{% if method.docstring.long_description %}
{{ method.docstring.long_description }}
{% endif %}

{% if method.docstring.params %}
#### Parameters

{% for param in method.docstring.params %}
- **{{ param.name }}**{% if param.type %} ({{ param.type }}){% endif %}{% if param.is_optional %} (optional){% endif %}{% if param.description %}: {{ param.description }}{% endif %}
{% endfor %}
{% endif %}

{% if method.docstring.returns %}
#### Returns

{% if method.docstring.returns.type %}**{{ method.docstring.returns.type }}**: {% endif %}{{ method.docstring.returns.description }}
{% endif %}

{% if method.docstring.raises %}
#### Raises

{% for exception in method.docstring.raises %}
- **{{ exception.type }}**{% if exception.description %}: {{ exception.description }}{% endif %}
{% endfor %}
{% endif %}

{% endfor %}

---

*Generated on {{ generation_date }} by URL Analyzer Plugin Documentation Generator*""")
            logger.info(f"Created default Markdown template at {md_template_path}")
    
    def generate_documentation(self, plugin_name: str, format: str = 'html') -> Optional[str]:
        """
        Generate documentation for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            format: Documentation format ('html', 'markdown', or 'json')
            
        Returns:
            Path to the generated documentation file or None if generation failed
        """
        # Get the plugin
        plugin = self._registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            return None
        
        # Extract plugin information
        plugin_info = self._extract_plugin_info(plugin)
        
        # Generate documentation in the requested format
        if format.lower() == 'html':
            return self._generate_html_doc(plugin_info)
        elif format.lower() in ('markdown', 'md'):
            return self._generate_markdown_doc(plugin_info)
        elif format.lower() == 'json':
            return self._generate_json_doc(plugin_info)
        else:
            logger.error(f"Unsupported documentation format: {format}")
            return None
    
    def _extract_plugin_info(self, plugin: Any) -> Dict[str, Any]:
        """
        Extract information from a plugin for documentation.
        
        Args:
            plugin: Plugin instance
            
        Returns:
            Dictionary containing plugin information
        """
        # Get plugin metadata
        metadata = {
            'name': plugin.get_name(),
            'version': plugin.get_version(),
            'description': plugin.get_description(),
            'author': plugin.get_author()
        }
        
        # Extract methods
        methods = []
        
        # Get the plugin class
        plugin_class = plugin.__class__
        
        # Get all methods
        for name, method in inspect.getmembers(plugin_class, predicate=inspect.isfunction):
            # Skip private methods
            if name.startswith('_'):
                continue
            
            # Get the method signature
            try:
                signature = str(inspect.signature(method))
                full_signature = f"{name}{signature}"
            except ValueError:
                full_signature = f"{name}(...)"
            
            # Get the method docstring
            docstring = inspect.getdoc(method) or ""
            parsed_docstring = DocstringParser.parse(docstring)
            
            # Add the method info
            methods.append({
                'name': name,
                'signature': full_signature,
                'docstring': parsed_docstring
            })
        
        # Sort methods by name
        methods.sort(key=lambda m: m['name'])
        
        # Create the plugin info dictionary
        plugin_info = {
            'plugin': {
                'metadata': metadata
            },
            'methods': methods,
            'generation_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return plugin_info
    
    def _generate_html_doc(self, plugin_info: Dict[str, Any]) -> Optional[str]:
        """
        Generate HTML documentation for a plugin.
        
        Args:
            plugin_info: Dictionary containing plugin information
            
        Returns:
            Path to the generated HTML file or None if generation failed
        """
        if not JINJA2_AVAILABLE:
            logger.error("Jinja2 is required for HTML documentation generation")
            return None
        
        try:
            # Set up Jinja2 environment
            env = Environment(loader=FileSystemLoader(self._templates_dir))
            template = env.get_template('plugin_doc.html')
            
            # Render the template
            html = template.render(**plugin_info)
            
            # Save the HTML file
            plugin_name = plugin_info['plugin']['metadata']['name']
            output_path = os.path.join(self._docs_dir, f"{plugin_name}.html")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Generated HTML documentation for plugin {plugin_name} at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating HTML documentation: {e}")
            return None
    
    def _generate_markdown_doc(self, plugin_info: Dict[str, Any]) -> Optional[str]:
        """
        Generate Markdown documentation for a plugin.
        
        Args:
            plugin_info: Dictionary containing plugin information
            
        Returns:
            Path to the generated Markdown file or None if generation failed
        """
        if not JINJA2_AVAILABLE:
            logger.error("Jinja2 is required for Markdown documentation generation")
            return None
        
        try:
            # Set up Jinja2 environment
            env = Environment(loader=FileSystemLoader(self._templates_dir))
            template = env.get_template('plugin_doc.md')
            
            # Render the template
            md = template.render(**plugin_info)
            
            # Save the Markdown file
            plugin_name = plugin_info['plugin']['metadata']['name']
            output_path = os.path.join(self._docs_dir, f"{plugin_name}.md")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)
            
            logger.info(f"Generated Markdown documentation for plugin {plugin_name} at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating Markdown documentation: {e}")
            return None
    
    def _generate_json_doc(self, plugin_info: Dict[str, Any]) -> Optional[str]:
        """
        Generate JSON documentation for a plugin.
        
        Args:
            plugin_info: Dictionary containing plugin information
            
        Returns:
            Path to the generated JSON file or None if generation failed
        """
        try:
            # Save the JSON file
            plugin_name = plugin_info['plugin']['metadata']['name']
            output_path = os.path.join(self._docs_dir, f"{plugin_name}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(plugin_info, f, indent=4)
            
            logger.info(f"Generated JSON documentation for plugin {plugin_name} at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating JSON documentation: {e}")
            return None
    
    def generate_all_documentation(self, format: str = 'html') -> List[str]:
        """
        Generate documentation for all plugins.
        
        Args:
            format: Documentation format ('html', 'markdown', or 'json')
            
        Returns:
            List of paths to the generated documentation files
        """
        # Get all plugins
        plugins = self._registry.get_all_plugins()
        
        # Generate documentation for each plugin
        doc_paths = []
        for plugin in plugins:
            doc_path = self.generate_documentation(plugin.get_name(), format)
            if doc_path:
                doc_paths.append(doc_path)
        
        return doc_paths
    
    def generate_index(self, format: str = 'html') -> Optional[str]:
        """
        Generate an index of all plugin documentation.
        
        Args:
            format: Documentation format ('html', 'markdown', or 'json')
            
        Returns:
            Path to the generated index file or None if generation failed
        """
        # Get all plugins
        plugins = self._registry.get_all_plugins()
        
        # Extract basic information for each plugin
        plugin_list = []
        for plugin in plugins:
            plugin_list.append({
                'name': plugin.get_name(),
                'version': plugin.get_version(),
                'description': plugin.get_description(),
                'author': plugin.get_author(),
                'doc_path': f"{plugin.get_name()}.{format.lower()}"
            })
        
        # Sort plugins by name
        plugin_list.sort(key=lambda p: p['name'])
        
        # Generate the index in the requested format
        if format.lower() == 'html':
            return self._generate_html_index(plugin_list)
        elif format.lower() in ('markdown', 'md'):
            return self._generate_markdown_index(plugin_list)
        elif format.lower() == 'json':
            return self._generate_json_index(plugin_list)
        else:
            logger.error(f"Unsupported documentation format: {format}")
            return None
    
    def _generate_html_index(self, plugin_list: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate an HTML index of all plugin documentation.
        
        Args:
            plugin_list: List of dictionaries containing plugin information
            
        Returns:
            Path to the generated HTML index file or None if generation failed
        """
        try:
            # Create the HTML index
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Analyzer Plugin Documentation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 {
            color: #0066cc;
        }
        .plugin {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .plugin-name {
            margin-top: 0;
            margin-bottom: 5px;
        }
        .plugin-meta {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .plugin-description {
            margin-bottom: 10px;
        }
        .plugin-link {
            display: inline-block;
            background-color: #0066cc;
            color: white;
            padding: 5px 10px;
            text-decoration: none;
            border-radius: 3px;
        }
        .plugin-link:hover {
            background-color: #0052a3;
        }
    </style>
</head>
<body>
    <h1>URL Analyzer Plugin Documentation</h1>
    
    <p>This page lists all available plugins for the URL Analyzer system.</p>
    
    <h2>Plugins</h2>
"""
            
            # Add each plugin to the index
            for plugin in plugin_list:
                html += f"""    <div class="plugin">
        <h3 class="plugin-name">{plugin['name']}</h3>
        <div class="plugin-meta">Version {plugin['version']} | Author: {plugin['author']}</div>
        <div class="plugin-description">{plugin['description']}</div>
        <a href="{plugin['doc_path']}" class="plugin-link">View Documentation</a>
    </div>
"""
            
            # Add the footer
            html += f"""    <footer>
        <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by URL Analyzer Plugin Documentation Generator</p>
    </footer>
</body>
</html>"""
            
            # Save the HTML index
            output_path = os.path.join(self._docs_dir, "index.html")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Generated HTML index at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating HTML index: {e}")
            return None
    
    def _generate_markdown_index(self, plugin_list: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a Markdown index of all plugin documentation.
        
        Args:
            plugin_list: List of dictionaries containing plugin information
            
        Returns:
            Path to the generated Markdown index file or None if generation failed
        """
        try:
            # Create the Markdown index
            md = """# URL Analyzer Plugin Documentation

This page lists all available plugins for the URL Analyzer system.

## Plugins

"""
            
            # Add each plugin to the index
            for plugin in plugin_list:
                md += f"""### {plugin['name']}

- **Version:** {plugin['version']}
- **Author:** {plugin['author']}

{plugin['description']}

[View Documentation]({plugin['doc_path']})

"""
            
            # Add the footer
            md += f"""---

*Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by URL Analyzer Plugin Documentation Generator*"""
            
            # Save the Markdown index
            output_path = os.path.join(self._docs_dir, "index.md")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)
            
            logger.info(f"Generated Markdown index at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating Markdown index: {e}")
            return None
    
    def _generate_json_index(self, plugin_list: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a JSON index of all plugin documentation.
        
        Args:
            plugin_list: List of dictionaries containing plugin information
            
        Returns:
            Path to the generated JSON index file or None if generation failed
        """
        try:
            # Create the JSON index
            index = {
                'plugins': plugin_list,
                'generation_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save the JSON index
            output_path = os.path.join(self._docs_dir, "index.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=4)
            
            logger.info(f"Generated JSON index at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating JSON index: {e}")
            return None


def generate_plugin_documentation(registry: PluginRegistry, plugin_name: Optional[str] = None, format: str = 'html') -> List[str]:
    """
    Generate documentation for plugins.
    
    Args:
        registry: Plugin registry
        plugin_name: Name of the plugin to document (None for all plugins)
        format: Documentation format ('html', 'markdown', or 'json')
        
    Returns:
        List of paths to the generated documentation files
    """
    # Create the documentation generator
    generator = PluginDocumentationGenerator(registry)
    
    # Generate documentation
    if plugin_name:
        # Generate documentation for a specific plugin
        doc_path = generator.generate_documentation(plugin_name, format)
        return [doc_path] if doc_path else []
    else:
        # Generate documentation for all plugins
        doc_paths = generator.generate_all_documentation(format)
        
        # Generate the index
        index_path = generator.generate_index(format)
        if index_path:
            doc_paths.append(index_path)
        
        return doc_paths