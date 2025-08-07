"""
HTML Report Generation Module

This module provides functionality for generating HTML reports based on
URL analysis results, including charts, tables, and interactive elements.
"""

import os
import json
import time
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Optional imports for advanced features
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.io import to_html
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Optional imports for geolocation
try:
    import socket
    import geoip2.database
    import pycountry
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False

# Template information
TEMPLATE_INFO = {
    "default.html": {
        "name": "Default",
        "description": "Comprehensive template with all report sections and visualizations"
    },
    "minimal.html": {
        "name": "Minimal",
        "description": "Simplified template with a clean, streamlined design"
    },
    "data_analytics.html": {
        "name": "Data Analytics",
        "description": "Data-focused template with additional metrics and insights"
    },
    "security_focus.html": {
        "name": "Security Focus",
        "description": "Security-oriented template with security metrics and recommendations"
    },
    "executive_summary.html": {
        "name": "Executive Summary",
        "description": "High-level overview for executives with key metrics and insights"
    },
    "print_friendly.html": {
        "name": "Print Friendly",
        "description": "Optimized for printing with simplified layout and print-specific styling"
    }
}


def list_available_templates() -> List[Dict[str, str]]:
    """
    Lists all available report templates.
    
    Returns:
        List of dictionaries containing template information (filename, name, description)
    """
    templates = []
    
    # Get the templates directory
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    # Check if the directory exists
    if not os.path.isdir(template_dir):
        return templates
    
    # List all HTML files in the templates directory
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            template_info = {
                "filename": filename,
                "name": TEMPLATE_INFO.get(filename, {}).get("name", filename),
                "description": TEMPLATE_INFO.get(filename, {}).get("description", "Custom template")
            }
            templates.append(template_info)
    
    # Sort templates by name
    templates.sort(key=lambda x: x["name"])
    
    return templates


def get_template_path(template_name: str) -> str:
    """
    Gets the full path to a template file.
    
    Args:
        template_name: Name of the template file
        
    Returns:
        Full path to the template file
        
    Raises:
        ValidationError: If the template name is not a valid string
        PathValidationError: If the template directory does not exist
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_string, validate_directory_path
    from url_analyzer.utils.errors import ValidationError, PathValidationError
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    try:
        # Validate template name
        template_name = validate_string(
            template_name, 
            allow_empty=False, 
            error_message="Template name cannot be empty"
        )
        
        # Get the templates directory
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        
        # Validate that the templates directory exists
        try:
            validate_directory_path(
                template_dir, 
                must_exist=True, 
                error_message=f"Templates directory not found: {template_dir}"
            )
        except ValidationError as e:
            logger.error(str(e))
            # Create the directory if it doesn't exist
            os.makedirs(template_dir, exist_ok=True)
            logger.info(f"Created templates directory: {template_dir}")
        
        # If template_name doesn't have .html extension, add it
        if not template_name.endswith('.html'):
            template_name += '.html'
            logger.debug(f"Added .html extension to template name: {template_name}")
        
        # Check if the template exists
        template_path = os.path.join(template_dir, template_name)
        if not os.path.isfile(template_path):
            logger.warning(f"Template not found: {template_path}")
            
            # If not found, try to find a template with a similar name
            available_templates = list_available_templates()
            for template in available_templates:
                if template_name.lower() in template["filename"].lower():
                    similar_path = os.path.join(template_dir, template["filename"])
                    logger.info(f"Found similar template: {similar_path}")
                    return similar_path
            
            # If still not found, return the default template
            default_path = os.path.join(template_dir, "default.html")
            logger.info(f"Using default template: {default_path}")
            
            # Check if the default template exists, create it if not
            if not os.path.isfile(default_path):
                logger.warning(f"Default template not found: {default_path}")
                # Create a basic default template
                with open(default_path, 'w') as f:
                    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>URL Analysis Report</h1>
    <div id="content">
        <!-- Content will be inserted here -->
    </div>
</body>
</html>""")
                    logger.info(f"Created default template: {default_path}")
            
            return default_path
        
        logger.debug(f"Using template: {template_path}")
        return template_path
        
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Template validation error: {str(e)}")
        raise


def generate_time_analysis_charts(df: pd.DataFrame) -> str:
    """
    Generates HTML for time-based charts using Plotly.
    
    Args:
        df: DataFrame containing URL data with Access_time column
        
    Returns:
        HTML string containing time-based charts
    """
    if not PLOTLY_AVAILABLE:
        return "<div class='alert alert-warning'>Plotly not installed. Time analysis charts not available.</div>"
    
    if 'Access_time' not in df.columns:
        return "<div class='alert alert-warning'>Access_time column not found. Time analysis charts not available.</div>"
    
    # Convert Access_time to datetime if it's not already
    df['Access_time'] = pd.to_datetime(df['Access_time'])

    # Create heatmap of activity by day and hour
    heatmap_data = df.groupby([df['Access_time'].dt.day_name(), df['Access_time'].dt.hour]).size().unstack(fill_value=0)
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(days_of_week)
    
    heatmap_fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values, 
            x=heatmap_data.columns, 
            y=heatmap_data.index, 
            colorscale='Viridis'
        )
    )
    
    heatmap_fig.update_layout(
        title='Activity Heatmap', 
        yaxis_title='Day of Week', 
        xaxis_title='Hour of Day',
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        width=None  # Allow width to be determined by container
    )

    # Create trend chart of daily activity
    trend_data = df.set_index('Access_time').resample('D').size()
    
    trend_fig = go.Figure([
        go.Scatter(
            x=trend_data.index, 
            y=trend_data.values, 
            mode='lines+markers'
        )
    ])
    
    trend_fig.update_layout(
        title='Daily URL Access Trend', 
        yaxis_title='URL Count', 
        xaxis_title='Date',
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        width=None  # Allow width to be determined by container
    )

    # Combine charts into a single HTML string
    return to_html(heatmap_fig, full_html=False, include_plotlyjs='cdn') + \
           to_html(trend_fig, full_html=False, include_plotlyjs=False, config={'responsive': True})


def generate_sankey_diagram(df: pd.DataFrame) -> str:
    """
    Generates HTML for a Sankey diagram showing traffic flow.
    
    Args:
        df: DataFrame containing URL data
        
    Returns:
        HTML string containing Sankey diagram
    """
    if not PLOTLY_AVAILABLE:
        return "<div class='alert alert-warning'>Plotly not installed. Traffic flow diagram not available.</div>"
    
    if not all(col in df.columns for col in ['Client_Name', 'URL_Category', 'Base_Domain']):
        return "<div class='alert alert-warning'>Required columns missing. Traffic flow diagram not available.</div>"

    # Use a sample for performance with large datasets
    df_sample = df.sample(n=min(len(df), 1000))
    
    # Get unique nodes (clients, categories, domains)
    all_nodes = pd.concat([
        df_sample['Client_Name'], 
        df_sample['URL_Category'], 
        df_sample['Base_Domain']
    ]).unique().tolist()

    source = []
    target = []
    value = []

    # Flow from Client to Category
    client_cat = df_sample.groupby(['Client_Name', 'URL_Category']).size().reset_index(name='count')
    for _, row in client_cat.iterrows():
        source.append(all_nodes.index(row['Client_Name']))
        target.append(all_nodes.index(row['URL_Category']))
        value.append(row['count'])

    # Flow from Category to Domain
    cat_domain = df_sample.groupby(['URL_Category', 'Base_Domain']).size().reset_index(name='count')
    for _, row in cat_domain.iterrows():
        source.append(all_nodes.index(row['URL_Category']))
        target.append(all_nodes.index(row['Base_Domain']))
        value.append(row['count'])

    # Create Sankey diagram
    sankey_fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, 
            thickness=20, 
            line=dict(color="black", width=0.5), 
            label=all_nodes
        ),
        link=dict(
            source=source, 
            target=target, 
            value=value
        )
    )])
    
    sankey_fig.update_layout(
        title_text="Traffic Flow: Client → Category → Domain", 
        font_size=10,
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=500,
        width=None  # Allow width to be determined by container
    )
    
    return to_html(sankey_fig, full_html=False, include_plotlyjs=False, config={'responsive': True})


def generate_network_graph(df: pd.DataFrame, max_domains: int = 50) -> str:
    """
    Generates HTML for a network graph of domain relationships.
    
    This function creates an interactive network graph showing how domains are related
    to each other based on common clients or categories.
    
    Args:
        df: DataFrame containing URL data with Base_Domain, Client_Name, and URL_Category columns
        max_domains: Maximum number of domains to include in the graph
        
    Returns:
        HTML string containing network graph
    """
    if not PLOTLY_AVAILABLE:
        return "<div class='alert alert-warning'>Plotly not installed. Network graph not available.</div>"
    
    if not all(col in df.columns for col in ['Base_Domain', 'URL_Category']):
        return "<div class='alert alert-warning'>Required columns missing. Network graph not available.</div>"
    
    try:
        # Get the most frequent domains
        top_domains = df['Base_Domain'].value_counts().head(max_domains).index.tolist()
        
        # Filter the DataFrame to include only the top domains
        df_filtered = df[df['Base_Domain'].isin(top_domains)]
        
        # Create edges between domains that share the same category
        edges = []
        edge_weights = {}
        
        # Group domains by category
        category_domains = {}
        for _, row in df_filtered.iterrows():
            category = row['URL_Category']
            domain = row['Base_Domain']
            
            if category not in category_domains:
                category_domains[category] = set()
            
            category_domains[category].add(domain)
        
        # Create edges between domains in the same category
        for category, domains in category_domains.items():
            domains_list = list(domains)
            for i in range(len(domains_list)):
                for j in range(i + 1, len(domains_list)):
                    domain1 = domains_list[i]
                    domain2 = domains_list[j]
                    
                    # Create a unique edge identifier
                    edge_id = tuple(sorted([domain1, domain2]))
                    
                    if edge_id in edge_weights:
                        edge_weights[edge_id] += 1
                    else:
                        edge_weights[edge_id] = 1
                        edges.append((domain1, domain2))
        
        # Create nodes for each domain
        nodes = top_domains
        
        # Calculate node sizes based on frequency
        domain_counts = df['Base_Domain'].value_counts()
        node_sizes = [domain_counts.get(domain, 0) * 0.5 for domain in nodes]
        
        # Create node colors based on category
        domain_categories = {}
        for _, row in df_filtered.iterrows():
            domain_categories[row['Base_Domain']] = row['URL_Category']
        
        # Get unique categories and assign colors
        unique_categories = list(set(domain_categories.values()))
        color_map = {category: f'rgb({hash(category) % 256}, {(hash(category) >> 8) % 256}, {(hash(category) >> 16) % 256})' 
                     for category in unique_categories}
        
        node_colors = [color_map.get(domain_categories.get(domain, 'Unknown'), 'rgb(200, 200, 200)') for domain in nodes]
        
        # Create edge weights
        edge_weights_list = [edge_weights[tuple(sorted([edges[i][0], edges[i][1]]))] for i in range(len(edges))]
        
        # Create the network graph
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                color=node_colors,
                size=node_sizes,
                colorbar=dict(
                    thickness=15,
                    title='Domain Category',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)
            )
        )
        
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create a simple force-directed layout
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components
        
        # Create adjacency matrix
        n = len(nodes)
        adjacency = np.zeros((n, n))
        
        for i, (node1, node2) in enumerate(edges):
            idx1 = nodes.index(node1)
            idx2 = nodes.index(node2)
            weight = edge_weights_list[i]
            adjacency[idx1, idx2] = weight
            adjacency[idx2, idx1] = weight
        
        # Use a simple force-directed layout algorithm
        pos = np.random.rand(n, 2)
        
        # Run a few iterations of force-directed layout
        k = 1.0  # optimal distance between nodes
        iterations = 50
        
        for _ in range(iterations):
            # Calculate repulsive forces
            for i in range(n):
                for j in range(n):
                    if i != j:
                        dx = pos[i, 0] - pos[j, 0]
                        dy = pos[i, 1] - pos[j, 1]
                        distance = max(0.01, np.sqrt(dx*dx + dy*dy))
                        repulsive_force = k*k / distance
                        pos[i, 0] += dx / distance * repulsive_force
                        pos[i, 1] += dy / distance * repulsive_force
            
            # Calculate attractive forces
            for i, j in zip(*np.where(adjacency > 0)):
                if i < j:  # Only process each edge once
                    dx = pos[i, 0] - pos[j, 0]
                    dy = pos[i, 1] - pos[j, 1]
                    distance = max(0.01, np.sqrt(dx*dx + dy*dy))
                    attractive_force = distance*distance / k
                    weight = adjacency[i, j]
                    pos[i, 0] -= dx / distance * attractive_force * weight
                    pos[i, 1] -= dy / distance * attractive_force * weight
                    pos[j, 0] += dx / distance * attractive_force * weight
                    pos[j, 1] += dy / distance * attractive_force * weight
        
        # Scale positions to fit in a reasonable range
        pos = (pos - pos.min(axis=0)) / (pos.max(axis=0) - pos.min(axis=0)) * 2 - 1
        
        # Add edges to the graph
        for i, (node1, node2) in enumerate(edges):
            idx1 = nodes.index(node1)
            idx2 = nodes.index(node2)
            x0, y0 = pos[idx1]
            x1, y1 = pos[idx2]
            
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)
        
        # Add nodes to the graph
        for i, node in enumerate(nodes):
            x, y = pos[i]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            
            # Add node information for hover text
            count = domain_counts.get(node, 0)
            category = domain_categories.get(node, 'Unknown')
            node_trace['text'] += (f"Domain: {node}<br>Count: {count}<br>Category: {category}",)
        
        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Domain Relationship Network',
                            titlefont=dict(size=16),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=600,
                            width=None,  # Allow width to be determined by container
                            annotations=[
                                dict(
                                    text="Network of domain relationships based on shared categories",
                                    showarrow=False,
                                    xref="paper", yref="paper",
                                    x=0.005, y=-0.002
                                )
                            ]
                        ))
        
        return to_html(fig, full_html=False, include_plotlyjs=False, config={'responsive': True})
    
    except Exception as e:
        # Log the error
        from url_analyzer.utils.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error generating network graph: {e}")
        
        return f"<div class='alert alert-danger'>Error generating network graph: {e}</div>"


def generate_geo_map(df: pd.DataFrame, max_domains: int = 100) -> str:
    """
    Generates HTML for a geographical map of domain locations.
    
    Args:
        df: DataFrame containing URL data with Base_Domain column
        max_domains: Maximum number of domains to include in the map
        
    Returns:
        HTML string containing geographical map
    """
    if not PLOTLY_AVAILABLE:
        return "<div class='alert alert-warning'>Plotly not installed. Geographical map not available.</div>"
    
    if not GEOIP_AVAILABLE:
        return "<div class='alert alert-warning'>GeoIP libraries not installed. Geographical map not available.</div>"
    
    if 'Base_Domain' not in df.columns:
        return "<div class='alert alert-warning'>Base_Domain column not found. Geographical map not available.</div>"
    
    # Get the most frequent domains
    top_domains = df['Base_Domain'].value_counts().head(max_domains).index.tolist()
    
    # Path to the GeoIP database
    # Note: This assumes the GeoLite2 database is in a 'data' directory
    # Users need to download this from MaxMind: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
    geoip_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'data', 'GeoLite2-City.mmdb')
    
    # Check if the database exists
    if not os.path.exists(geoip_db_path):
        return "<div class='alert alert-warning'>GeoIP database not found. Geographical map not available.</div>"
    
    try:
        # Open the GeoIP database
        with geoip2.database.Reader(geoip_db_path) as reader:
            # Create lists to store location data
            domains = []
            latitudes = []
            longitudes = []
            countries = []
            cities = []
            counts = []
            
            # Get domain counts
            domain_counts = df['Base_Domain'].value_counts()
            
            # Resolve domains to locations
            for domain in top_domains:
                try:
                    # Resolve domain to IP address
                    ip = socket.gethostbyname(domain)
                    
                    # Look up location
                    response = reader.city(ip)
                    
                    # Get country name
                    country_code = response.country.iso_code
                    country_name = pycountry.countries.get(alpha_2=country_code).name if country_code else "Unknown"
                    
                    # Add to lists
                    domains.append(domain)
                    latitudes.append(response.location.latitude)
                    longitudes.append(response.location.longitude)
                    countries.append(country_name)
                    cities.append(response.city.name or "Unknown")
                    counts.append(int(domain_counts.get(domain, 0)))
                except (socket.gaierror, geoip2.errors.AddressNotFoundError):
                    # Skip domains that can't be resolved or located
                    continue
            
            # Check if we have any data
            if not domains:
                return "<div class='alert alert-warning'>No domains could be geolocated. Geographical map not available.</div>"
            
            # Create a DataFrame with the location data
            geo_df = pd.DataFrame({
                'domain': domains,
                'latitude': latitudes,
                'longitude': longitudes,
                'country': countries,
                'city': cities,
                'count': counts
            })
            
            # Create the map
            geo_fig = px.scatter_geo(
                geo_df,
                lat='latitude',
                lon='longitude',
                color='country',
                size='count',
                hover_name='domain',
                hover_data={
                    'domain': True,
                    'country': True,
                    'city': True,
                    'count': True,
                    'latitude': False,
                    'longitude': False
                },
                projection='natural earth',
                title='Domain Locations'
            )
            
            geo_fig.update_layout(
                autosize=True,
                margin=dict(l=0, r=0, t=40, b=0),
                height=500,
                width=None  # Allow width to be determined by container
            )
            
            return to_html(geo_fig, full_html=False, include_plotlyjs=False, config={'responsive': True})
    
    except Exception as e:
        # Log the error
        from url_analyzer.utils.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error generating geographical map: {e}")
        
        return f"<div class='alert alert-danger'>Error generating geographical map: {e}</div>"


def _create_filter_html(df: pd.DataFrame) -> str:
    """
    Creates HTML for client and MAC address filters.
    
    This is an internal function used by generate_html_report.
    
    Args:
        df: DataFrame containing URL data
        
    Returns:
        HTML string for filters
    """
    filter_html_parts = []
    for col_name in ['Client_Name', 'MAC_address']:
        if col_name in df.columns:
            options = df[col_name].dropna().unique().tolist()
            options_html = "".join([
                f'<option value="{str(opt).replace('"', "&quot;")}">{str(opt)}</option>' 
                for opt in options
            ])
            filter_html_parts.append(
                f"<div class='filter-box'><label for='{col_name}_filter'>{col_name.replace('_', ' ')}:</label>"
                f"<select id='{col_name}_filter' class='datatable-filter'>"
                f"<option value=''>All</option>{options_html}</select></div>"
            )
    return "".join(filter_html_parts)


def _prepare_chart_data(stats: Dict[str, Any]) -> Tuple[str, str]:
    """
    Prepares chart data from statistics.
    
    This is an internal function used by generate_html_report.
    
    Args:
        stats: Dictionary of statistics for the report
        
    Returns:
        Tuple of (chart_labels_json, chart_data_json)
    """
    chart_labels = json.dumps(list(stats['category_counts'].keys()))
    chart_data = json.dumps([int(v) for v in stats['category_counts'].values()])
    return chart_labels, chart_data


def _calculate_top_domains(df: pd.DataFrame) -> str:
    """
    Calculates top domains for each client for interactive chart.
    
    This is an internal function used by generate_html_report.
    
    Args:
        df: DataFrame containing URL data
        
    Returns:
        JSON string of top domains by client
    """
    top_n_by_client = {}
    
    # Add an 'All' entry for when no client is selected
    top_n_all = df['Base_Domain'].value_counts().nlargest(10).sort_values()
    top_n_by_client['All'] = {'labels': top_n_all.index.tolist(), 'data': top_n_all.tolist()}
    
    if 'Client_Name' in df.columns:
        for client in df['Client_Name'].unique():
            top_n = df[df['Client_Name'] == client]['Base_Domain'].value_counts().nlargest(10).sort_values()
            top_n_by_client[client] = {'labels': top_n.index.tolist(), 'data': top_n.tolist()}
    
    return json.dumps(top_n_by_client)


def _generate_stat_boxes(stats: Dict[str, Any]) -> str:
    """
    Generates HTML for stat boxes.
    
    This is an internal function used by generate_html_report.
    
    Args:
        stats: Dictionary of statistics for the report
        
    Returns:
        HTML string for stat boxes
    """
    stat_boxes = []
    for cat, count in stats.items():
        if cat == 'category_counts':
            # Skip the raw category_counts dictionary as it's displayed in the chart
            continue
        stat_boxes.append(f"<div class='stat-box card'><h3>{cat}</h3><p>{count}</p></div>")
    
    # Add individual category count boxes
    if 'category_counts' in stats:
        for category, count in stats['category_counts'].items():
            stat_boxes.append(f"<div class='stat-box card'><h3>{category}</h3><p>{count}</p></div>")
    
    return "".join(stat_boxes)


def _generate_column_defs(df: pd.DataFrame) -> str:
    """
    Generates column definitions for DataTables.
    
    This is an internal function used by generate_html_report.
    
    Args:
        df: DataFrame containing URL data
        
    Returns:
        JavaScript string for column definitions
    """
    return f"[{', '.join([f'{{\"name\": \"{col_name}\", \"targets\": {df.columns.get_loc(col_name)}}}' for col_name in ['Client_Name', 'MAC_address'] if col_name in df.columns])}]"


def _generate_html_content(
    df: pd.DataFrame, 
    filter_html: str, 
    stat_boxes_html: str, 
    time_charts_html: str, 
    sankey_html: str, 
    geo_map_html: str,
    top_n_by_client_json: str, 
    chart_labels: str, 
    chart_data: str, 
    column_defs_js: str
) -> str:
    """
    Generates the HTML content for the report.
    
    This is an internal function used by generate_html_report.
    
    Args:
        df: DataFrame containing URL data
        filter_html: HTML string for filters
        stat_boxes_html: HTML string for stat boxes
        time_charts_html: HTML string for time charts
        sankey_html: HTML string for Sankey diagram
        top_n_by_client_json: JSON string of top domains by client
        chart_labels: JSON string of chart labels
        chart_data: JSON string of chart data
        column_defs_js: JavaScript string for column definitions
        
    Returns:
        Complete HTML content as a string
    """
    # Import sanitization utilities
    from url_analyzer.utils.sanitization import sanitize_html, sanitize_json_string
    
    # Sanitize JSON data to prevent XSS attacks
    safe_top_n_by_client_json = sanitize_json_string(top_n_by_client_json)
    safe_chart_labels = sanitize_json_string(chart_labels)
    safe_chart_data = sanitize_json_string(chart_data)
    
    # Generate CSRF token for protection
    csrf_token = os.urandom(16).hex()
    
    # TODO: Replace this with Jinja2 template rendering in the future
    # For now, we're keeping the HTML generation inline for compatibility
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>URL Analysis Report</title>
        <!-- Security headers -->
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.datatables.net https://cdn.plot.ly; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.datatables.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;">
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
        <meta http-equiv="X-XSS-Protection" content="1; mode=block">
        <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            :root {{ --bg-color: #f7f9fc; --card-bg: #ffffff; --text-color: #333; --heading-color: #1e3a5f; --border-color: #e0e6ed; --shadow-color: rgba(0, 0, 0, 0.08); --primary-color: #4a90e2; --table-header-bg: #f1f5f9; }}
            [data-theme="dark"] {{ --bg-color: #121212; --card-bg: #1e1e1e; --text-color: #e0e0e0; --heading-color: #bb86fc; --border-color: #333; --shadow-color: rgba(0, 0, 0, 0.2); --primary-color: #bb86fc; --table-header-bg: #2c2c2c; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background-color: var(--bg-color); color: var(--text-color); }}
            .container {{ padding: 2rem; max-width: 1800px; margin: auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }}
            h1, h2 {{ color: var(--heading-color); }}
            h1 {{ font-size: 2.5rem; }}
            h2 {{ font-size: 1.75rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.75rem; margin-top: 2.5rem; margin-bottom: 1.5rem; }}
            .card {{ background-color: var(--card-bg); padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 12px var(--shadow-color); }}
            .grid-container {{ display: grid; gap: 2rem; }}
            .dashboard {{ grid-template-columns: 1fr 1.5fr; }}
            .insights {{ grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1.5rem; }}
            .stat-box h3 {{ margin: 0 0 0.5rem; font-size: 1rem; opacity: 0.8; }}
            .stat-box p {{ margin: 0; font-size: 2.5rem; font-weight: 700; color: var(--primary-color); }}
            .export-buttons button, .theme-switch-wrapper {{  align-self: center; }}
            .traffic-flow-section {{ margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); }}
            .traffic-flow-section h3 {{ margin-top: 0; margin-bottom: 1rem; font-size: 1.25rem; color: var(--heading-color); }}
            .traffic-flow-section .plotly {{ width: 100% !important; max-width: 100%; }}
            .traffic-flow-section .js-plotly-plot {{ width: 100% !important; }}
            .geo-map-container {{ margin-bottom: 2rem; }}
            .geo-map-container h3 {{ margin-top: 0; margin-bottom: 0.5rem; font-size: 1.25rem; color: var(--heading-color); }}
            .geo-map-container .map-description {{ margin-top: 0; margin-bottom: 1rem; color: var(--text-color); opacity: 0.8; }}
            .geo-map-container .plotly {{ width: 100% !important; max-width: 100%; }}
            .geo-map-container .js-plotly-plot {{ width: 100% !important; }}
            .theme-switch {{ display: inline-block; height: 34px; position: relative; width: 60px; }} .theme-switch input {{ display:none; }} .slider {{ background-color: #ccc; bottom: 0; cursor: pointer; left: 0; position: absolute; right: 0; top: 0; transition: .4s; }} .slider:before {{ background-color: #fff; bottom: 4px; content: ""; height: 26px; left: 4px; position: absolute; transition: .4s; width: 26px; }} input:checked + .slider {{ background-color: var(--primary-color); }} input:checked + .slider:before {{ transform: translateX(26px); }} .slider.round {{ border-radius: 34px; }} .slider.round:before {{ border-radius: 50%; }}
        </style>
    </head>
    <body>
        <script> (function() {{ const theme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); document.documentElement.setAttribute('data-theme', theme); }})(); </script>
        <div class="container">
            <div class="header"><h1>URL Analysis Report</h1><div class="theme-switch-wrapper"><label class="theme-switch" for="checkbox"><input type="checkbox" id="checkbox" /><div class="slider round"></div></label></div></div>
            <div class="grid-container dashboard">
                <div class="chart-container card"><canvas id="categoryChart"></canvas></div>
                <div class="stats-grid">{stat_boxes_html}</div>
            </div>
            <h2>Domain & Time Insights</h2>
            <div class="grid-container insights">
                <div class="card" id="topDomainsContainer">
                    <canvas id="topDomainsChart"></canvas>
                    <div class="traffic-flow-section">
                        <h3>Traffic Flow Analysis</h3>
                        {sankey_html}
                    </div>
                </div>
                <div class="card">{time_charts_html}</div>
            </div>
            
            <h2>Geographical Insights</h2>
            <div class="card geo-map-container">
                <h3>Domain Locations Map</h3>
                <p class="map-description">This map shows the geographical locations of the most frequently accessed domains.</p>
                {geo_map_html}
            </div>
            <h2>Detailed URL Data</h2>
            <div class="card">
                <div class="filters-container">
                    <div class="export-buttons">
                        <button id="exportCsv">Export CSV</button>
                        <button id="exportJson">Export JSON</button>
                    </div>
                    <!-- CSRF token for protection against CSRF attacks -->
                    <input type="hidden" name="csrf_token" value="{csrf_token}">
                    {filter_html}
                </div>
                {df.to_html(table_id='urlTable', index=False, classes='display compact', escape=True)}
            </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script><script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
        <script>
            const topNByClientData = {safe_top_n_by_client_json};
            const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
            if (localStorage.getItem('theme') === 'dark') toggleSwitch.checked = true;
            toggleSwitch.addEventListener('change', e => {{ const theme = e.target.checked ? 'dark' : 'light'; document.documentElement.setAttribute('data-theme', theme); localStorage.setItem('theme', theme); }});

            const topDomainsChart = new Chart(document.getElementById('topDomainsChart'), {{ type: 'bar', options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }}, title: {{ display: true, text: 'Top 10 Visited Domains (All Clients)' }} }} }} }});

            function updateTopDomainsChart(clientName) {{
                const chartData = topNByClientData[clientName] || topNByClientData['All'];
                topDomainsChart.data.labels = chartData.labels;
                topDomainsChart.data.datasets = [{{ label: 'Visits', data: chartData.data, backgroundColor: '#50e3c2' }}];
                topDomainsChart.options.plugins.title.text = `Top 10 Visited Domains (` + (clientName || 'All Clients') + `)`;
                topDomainsChart.update();
            }}

            $(document).ready(function() {{
                var table = $('#urlTable').DataTable({{ "pageLength": 25, "columnDefs": {column_defs_js} }});

                $('#Client_Name_filter').on('change', function() {{
                    var clientName = $(this).val();
                    var searchVal = clientName ? '^' + $.fn.dataTable.util.escapeRegex(clientName) + '$' : '';
                    table.column('Client_Name:name').search(searchVal, true, false).draw();
                    updateTopDomainsChart(clientName);
                }});
                $('#MAC_address_filter').on('change', function() {{ table.column('MAC_address:name').search($(this).val() ? '^' + $.fn.dataTable.util.escapeRegex($(this).val()) + '$' : '', true, false).draw(); }});

                function exportData(format) {{
                    const data = table.rows({{ search: 'applied' }}).data().toArray();
                    const headers = table.columns().header().toArray().map(h => h.innerText);
                    let content = format === 'csv' ? [headers.join(','), ...data.map(row => row.map(val => `"${{String(val).replace(/"/g, '""')}}"`).join(','))].join('\\n') : JSON.stringify(data.map(row => Object.fromEntries(headers.map((h, i) => [h, row[i]]))), null, 2);
                    const blob = new Blob([content], {{ type: `text/${{format}};charset=utf-8;` }});
                    const link = document.createElement("a");
                    link.href = URL.createObjectURL(blob);
                    link.download = `report_export.${{format}}`;
                    link.click();
                }}
                $('#exportCsv').on('click', () => exportData('csv'));
                $('#exportJson').on('click', () => exportData('json'));

                updateTopDomainsChart(null); // Initial chart load
            }});

            new Chart(document.getElementById('categoryChart'), {{ type: 'doughnut', data: {{ labels: {safe_chart_labels}, datasets: [{{ data: {safe_chart_data}, backgroundColor: ['#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#9013fe', '#7ed321', '#417505'], borderWidth: 2 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }} }});
        </script>
    </body></html>
    """


def write_html_to_file(html: str, output_path: str) -> str:
    """
    Writes HTML content to a file.
    
    Args:
        html: HTML content to write
        output_path: Path where to save the HTML file
        
    Returns:
        Path to the generated HTML file
        
    Raises:
        ValidationError: If the HTML content or output path is not valid
        IOError: If there's an error writing to the file
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_string
    from url_analyzer.utils.sanitization import sanitize_path
    from url_analyzer.utils.errors import ValidationError
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    try:
        # Validate HTML content
        html = validate_string(
            html, 
            allow_empty=False, 
            error_message="HTML content cannot be empty"
        )
        
        # Validate output path
        output_path = validate_string(
            output_path, 
            allow_empty=False, 
            error_message="Output path cannot be empty"
        )
        
        # Sanitize the output path to prevent path traversal attacks
        safe_path = sanitize_path(output_path)
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(os.path.abspath(safe_path))
        if not os.path.exists(output_dir):
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        # Log the file write operation
        logger.info(f"Writing HTML report to: {safe_path}")
        
        # Write the HTML to file
        try:
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Successfully wrote HTML report to: {safe_path}")
            return safe_path
            
        except IOError as e:
            error_msg = f"Error writing HTML to file {safe_path}: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg)
            
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Validation error: {str(e)}")
        raise


def write_streaming_html_to_file(html_generator, output_path: str, chunk_size: int = 8192) -> str:
    """
    Writes HTML content to a file using streaming to reduce memory usage.
    
    Args:
        html_generator: Generator that yields HTML content chunks
        output_path: Path where to save the HTML file
        chunk_size: Size of chunks to write at once
        
    Returns:
        Path to the generated HTML file
        
    Raises:
        ValidationError: If the output path is not valid
        IOError: If there's an error writing to the file
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_string
    from url_analyzer.utils.sanitization import sanitize_path
    from url_analyzer.utils.errors import ValidationError
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    try:
        # Validate output path
        output_path = validate_string(
            output_path, 
            allow_empty=False, 
            error_message="Output path cannot be empty"
        )
        
        # Sanitize the output path to prevent path traversal attacks
        safe_path = sanitize_path(output_path)
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(os.path.abspath(safe_path))
        if not os.path.exists(output_dir):
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        # Log the file write operation
        logger.info(f"Writing streaming HTML report to: {safe_path}")
        
        # Write the HTML to file in chunks
        try:
            with open(safe_path, 'w', encoding='utf-8') as f:
                bytes_written = 0
                for chunk in html_generator:
                    if chunk:
                        f.write(chunk)
                        bytes_written += len(chunk)
                        
                        # Log progress for large files
                        if bytes_written % (chunk_size * 100) == 0:
                            logger.debug(f"Wrote {bytes_written} bytes to {safe_path}")
            
            logger.info(f"Successfully wrote streaming HTML report to: {safe_path} ({bytes_written} bytes)")
            return safe_path
            
        except IOError as e:
            error_msg = f"Error writing HTML to file {safe_path}: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg)
            
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Validation error: {str(e)}")
        raise


def generate_html_report(df: pd.DataFrame, output_path: str, stats: Dict[str, Any]) -> str:
    """
    Generates a self-contained, interactive HTML report.
    
    This function creates a comprehensive HTML report from URL analysis data,
    including charts, tables, and interactive elements. The report is self-contained
    with all necessary CSS, JavaScript, and data embedded in a single HTML file.
    
    Args:
        df: DataFrame containing URL data with columns like 'Domain_name', 'Category',
            'Is_Sensitive', etc.
        output_path: Path where to save the HTML report (e.g., 'reports/analysis.html')
        stats: Dictionary of statistics for the report, including keys like
               'category_counts', 'total_urls', 'sensitive_count', etc.
        
    Returns:
        Path to the generated HTML report
        
    Raises:
        ValidationError: If any input parameters are invalid
        TypeError: If df is not a pandas DataFrame
        IOError: If there's an error writing to the output file
        
    Examples:
        Basic usage with a DataFrame and statistics:
            ```python
            import pandas as pd
            from url_analyzer.reporting.html_report import generate_html_report
            
            # Create or load a DataFrame with URL analysis results
            df = pd.DataFrame({
                'Domain_name': ['example.com', 'google.com', 'facebook.com'],
                'Category': ['Business', 'Search', 'Social Media'],
                'Is_Sensitive': [False, False, True],
                'Base_Domain': ['example.com', 'google.com', 'facebook.com'],
                'URL': ['https://example.com', 'https://google.com', 'https://facebook.com/profile']
            })
            
            # Create statistics dictionary
            stats = {
                'total_urls': len(df),
                'sensitive_count': df['Is_Sensitive'].sum(),
                'category_counts': df['Category'].value_counts().to_dict(),
                'domain_counts': df['Base_Domain'].value_counts().to_dict()
            }
            
            # Generate the report
            report_path = generate_html_report(df, 'reports/url_analysis.html', stats)
            print(f"Report generated at: {report_path}")
            ```
            
        Using with processed data from the URL analyzer:
            ```python
            from url_analyzer.data.processing import process_file
            from url_analyzer.reporting.html_report import generate_html_report
            
            # Process a CSV file with URLs
            df, stats = process_file('data/urls.csv')
            
            # Generate the report
            report_path = generate_html_report(df, 'reports/analysis_report.html', stats)
            ```
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_string, validate_dict, validate_type
    from url_analyzer.utils.errors import ValidationError
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    try:
        # Validate input parameters
        logger.debug("Validating input parameters for HTML report generation")
        
        # Validate DataFrame
        validate_type(df, pd.DataFrame, error_message="df must be a pandas DataFrame")
        
        if df.empty:
            logger.warning("DataFrame is empty, report may not contain useful information")
        
        # Validate output path
        output_path = validate_string(
            output_path, 
            allow_empty=False, 
            error_message="Output path cannot be empty"
        )
        
        # Validate stats dictionary
        validate_dict(
            stats, 
            error_message="Stats must be a dictionary"
        )
        
        # Check if required stats are present
        if 'category_counts' not in stats:
            logger.warning("'category_counts' not found in stats dictionary, chart may not display correctly")
        
        logger.info(f"Generating HTML report for {len(df)} rows to {output_path}")
        
        # Create filter HTML for client and MAC address filters
        filter_html = _create_filter_html(df)
        
        # Prepare chart data
        chart_labels, chart_data = _prepare_chart_data(stats)
        
        # Pre-calculate Top N data for each client for interactive chart
        top_n_by_client_json = _calculate_top_domains(df)
        
        # Generate time charts, Sankey diagram, and geographical map
        time_charts_html = generate_time_analysis_charts(df)
        sankey_html = generate_sankey_diagram(df)
        geo_map_html = generate_geo_map(df)
        
        # Generate stat boxes
        stat_boxes_html = _generate_stat_boxes(stats)
        
        # Generate column definitions for DataTables
        column_defs_js = _generate_column_defs(df)
        
        # Generate HTML content
        logger.debug("Generating HTML content")
        html = _generate_html_content(
            df, 
            filter_html, 
            stat_boxes_html, 
            time_charts_html, 
            sankey_html, 
            geo_map_html,
            top_n_by_client_json, 
            chart_labels, 
            chart_data, 
            column_defs_js
        )
        
        # Write HTML to file
        logger.debug(f"Writing HTML report to {output_path}")
        result_path = write_html_to_file(html, output_path)
        
        logger.info(f"Successfully generated HTML report at {result_path}")
        return result_path
        
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Validation error generating HTML report: {str(e)}")
        raise
    except Exception as e:
        # Log and re-raise other exceptions
        error_msg = f"Error generating HTML report: {str(e)}"
        logger.error(error_msg)
        raise


def generate_streaming_report(df: pd.DataFrame, output_path: str, stats: Dict[str, Any],
                              template_name: str = 'default.html', chunk_size: int = 8192,
                              page_size: int = 100, enable_lazy_loading: bool = True,
                              enable_pagination: bool = True) -> str:
    """
    Generates an HTML report using streaming templates and writes it to a file in chunks.
    This approach is more memory-efficient for large datasets.
    
    Args:
        df: DataFrame containing URL data
        output_path: Path where to save the HTML report
        stats: Dictionary of statistics for the report
        template_name: Name of the template to use
        chunk_size: Size of chunks to write at once
        page_size: Number of rows per page in the data table
        enable_lazy_loading: Whether to enable lazy loading for charts and visualizations
        enable_pagination: Whether to enable pagination for large tables
        
    Returns:
        Path to the generated HTML report
        
    Raises:
        ValidationError: If any input parameters are invalid
        IOError: If there's an error writing to the output file
    """
    # Import validation and sanitization utilities
    from url_analyzer.utils.validation import validate_string, validate_dict, validate_type
    from url_analyzer.utils.sanitization import sanitize_html, sanitize_json_string, sanitize_input
    from url_analyzer.utils.errors import ValidationError
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    try:
        # Validate input parameters
        logger.debug("Validating input parameters for streaming HTML report generation")
        
        # Validate DataFrame
        validate_type(df, pd.DataFrame, error_message="df must be a pandas DataFrame")
        
        if df.empty:
            logger.warning("DataFrame is empty, report may not contain useful information")
        
        # Validate output path
        output_path = validate_string(
            output_path, 
            allow_empty=False, 
            error_message="Output path cannot be empty"
        )
        
        # Validate stats dictionary
        validate_dict(
            stats, 
            error_message="Stats must be a dictionary"
        )
        
        # Validate template name
        template_name = validate_string(
            template_name, 
            allow_empty=False, 
            error_message="Template name cannot be empty"
        )
        
        # Get the template path
        template_path = get_template_path(template_name)
        template_filename = os.path.basename(template_path)
        
        # Log optimization settings
        optimization_info = []
        if enable_streaming := True:
            optimization_info.append("streaming rendering")
        if enable_lazy_loading:
            optimization_info.append("lazy loading")
        if enable_pagination:
            optimization_info.append("pagination")
        
        optimization_str = ", ".join(optimization_info)
        logger.info(f"Generating optimized HTML report with {optimization_str} using template '{template_name}' for {len(df)} rows to {output_path}")
        
        # Determine if we should use pagination based on dataset size
        # For very small datasets, pagination might not be necessary
        actual_pagination = enable_pagination and len(df) > page_size
        
        # Determine if we should use lazy loading based on dataset size and complexity
        # For simple reports, lazy loading might not provide significant benefits
        actual_lazy_loading = enable_lazy_loading and (len(df) > 1000 or 'category_counts' in stats and len(stats['category_counts']) > 10)
        
        if actual_pagination != enable_pagination:
            logger.debug(f"Pagination automatically {'enabled' if actual_pagination else 'disabled'} based on dataset size ({len(df)} rows)")
        
        if actual_lazy_loading != enable_lazy_loading:
            logger.debug(f"Lazy loading automatically {'enabled' if actual_lazy_loading else 'disabled'} based on dataset complexity")
        
        # Set up Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(os.path.dirname(template_path)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Try to load the template
        try:
            template = env.get_template(template_filename)
        except Exception as e:
            logger.warning(f"Error loading template {template_filename}: {e}")
            logger.info("Falling back to built-in HTML generation.")
            return generate_html_report(df, output_path, stats)
        
        # Prepare template context with optimizations
        context = prepare_template_context(
            df=df, 
            stats=stats, 
            enable_pagination=actual_pagination, 
            page_size=page_size,
            enable_lazy_loading=actual_lazy_loading
        )
        
        # Add optimization flags to the context
        context['optimized'] = True
        context['streaming_enabled'] = enable_streaming
        context['lazy_loading_enabled'] = actual_lazy_loading
        context['pagination_enabled'] = actual_pagination
        
        # Create a generator that yields template chunks
        def template_generator():
            # Yield the template in chunks
            for chunk in template.generate(context):
                yield chunk
        
        # Measure generation time
        start_time = time.time()
        
        # Write the streaming HTML to file
        result_path = write_streaming_html_to_file(template_generator(), output_path, chunk_size)
        
        # Log performance metrics
        end_time = time.time()
        generation_time = end_time - start_time
        logger.info(f"Generated optimized HTML report in {generation_time:.2f} seconds")
        
        # Log memory usage if psutil is available
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            logger.info(f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")
        except ImportError:
            pass
        
        return result_path
        
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Validation error generating streaming HTML report: {str(e)}")
        raise
    except Exception as e:
        # Log and re-raise other exceptions
        error_msg = f"Error generating streaming HTML report: {str(e)}"
        logger.error(error_msg)
        raise


def prepare_template_context(df: pd.DataFrame, stats: Dict[str, Any], enable_pagination: bool = False, 
                        page_size: int = 100, enable_lazy_loading: bool = False) -> Dict[str, Any]:
    """
    Prepares the context dictionary for the Jinja2 template.
    
    Args:
        df: DataFrame containing URL data
        stats: Dictionary of statistics for the report
        enable_pagination: Whether to enable pagination for large tables
        page_size: Number of rows per page in the data table
        enable_lazy_loading: Whether to enable lazy loading for charts and visualizations
        
    Returns:
        Context dictionary for the template
    """
    from url_analyzer.utils.sanitization import sanitize_html, sanitize_json_string
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    # Create filter HTML for client and MAC address filters
    filter_html_parts = []
    for col_name in ['Client_Name', 'MAC_address']:
        if col_name in df.columns:
            options = df[col_name].dropna().unique().tolist()
            options_html = "".join([
                f'<option value="{sanitize_html(str(opt))}">{sanitize_html(str(opt))}</option>' 
                for opt in options
            ])
            # Sanitize column name
            safe_col_name = sanitize_html(col_name)
            filter_html_parts.append(f"""
            <div class="filter-group">
                <label for="{safe_col_name}_filter">{safe_col_name}:</label>
                <select id="{safe_col_name}_filter" class="filter-select" data-column="{safe_col_name}">
                    <option value="">All</option>
                    {options_html}
                </select>
            </div>
            """)
    filter_html = "".join(filter_html_parts)
    
    # Generate time charts and Sankey diagram
    # If lazy loading is enabled, we'll defer these expensive operations
    if enable_lazy_loading:
        # Create placeholders for lazy-loaded content
        time_charts_html = """
        <div id="timeChartsContainer" class="loading-container">
            <div class="loading-spinner"></div>
            <script>
                // This script will be executed when the element is visible
                document.addEventListener('DOMContentLoaded', function() {
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                // Load the time charts when visible
                                fetch('/api/time-charts?report_id={{ report_id }}')
                                    .then(response => response.text())
                                    .then(html => {
                                        document.getElementById('timeChartsContainer').innerHTML = html;
                                    })
                                    .catch(error => {
                                        console.error('Error loading time charts:', error);
                                        document.getElementById('timeChartsContainer').innerHTML = 
                                            '<div class="error">Error loading time charts</div>';
                                    });
                                observer.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.1 });
                    
                    observer.observe(document.getElementById('timeChartsContainer'));
                });
            </script>
        </div>
        """
        
        sankey_html = """
        <div id="sankeyContainer" class="loading-container">
            <div class="loading-spinner"></div>
            <script>
                // This script will be executed when the element is visible
                document.addEventListener('DOMContentLoaded', function() {
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                // Load the Sankey diagram when visible
                                fetch('/api/sankey?report_id={{ report_id }}')
                                    .then(response => response.text())
                                    .then(html => {
                                        document.getElementById('sankeyContainer').innerHTML = html;
                                    })
                                    .catch(error => {
                                        console.error('Error loading Sankey diagram:', error);
                                        document.getElementById('sankeyContainer').innerHTML = 
                                            '<div class="error">Error loading Sankey diagram</div>';
                                    });
                                observer.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.1 });
                    
                    observer.observe(document.getElementById('sankeyContainer'));
                });
            </script>
        </div>
        """
    else:
        # Generate the content immediately
        time_charts_html = generate_time_analysis_charts(df)
        sankey_html = generate_sankey_diagram(df)
    
    # Generate stat boxes
    stats_boxes = []
    for cat, count in stats.items():
        if cat == 'category_counts':
            # Skip the raw category_counts dictionary as it's displayed in the chart
            continue
        # Sanitize category name and count
        safe_cat = sanitize_html(str(cat))
        safe_count = sanitize_html(str(count))
        stats_boxes.append(f"<div class='stat-box'><h3>{safe_cat}</h3><p>{safe_count}</p></div>")
    
    # Add individual category count boxes
    if 'category_counts' in stats:
        for category, count in stats['category_counts'].items():
            # Sanitize category name and count
            safe_category = sanitize_html(str(category))
            safe_count = sanitize_html(str(count))
            stats_boxes.append(f"<div class='stat-box'><h3>{safe_category}</h3><p>{safe_count}</p></div>")
    
    stats_boxes_html = "".join(stats_boxes)
    
    # Prepare chart data
    chart_labels, chart_data = _prepare_chart_data(stats)
    
    # Pre-calculate Top N data for each client for interactive chart
    top_n_by_client_json = _calculate_top_domains(df)
    
    # Generate column definitions for DataTables
    column_defs_js = _generate_column_defs(df)
    
    # Prepare pagination settings
    pagination_settings = {
        'enabled': enable_pagination,
        'page_size': page_size,
        'total_rows': len(df),
        'total_pages': (len(df) + page_size - 1) // page_size if df is not None and not df.empty else 1
    }
    
    # Convert DataFrame to HTML table with pagination if enabled
    if enable_pagination:
        # Only include the first page in the initial HTML
        table_html = df.head(page_size).to_html(table_id='urlTable', index=False, classes='display compact', escape=True)
        
        # Prepare data for AJAX loading
        # We'll create a JSON representation of the DataFrame for client-side pagination
        # For very large DataFrames, this should be replaced with server-side pagination
        if len(df) <= 10000:  # Only do this for reasonably sized DataFrames
            try:
                import json
                # Convert DataFrame to dict of records
                data_json = sanitize_json_string(json.dumps(df.to_dict(orient='records')))
                logger.debug(f"Prepared JSON data for client-side pagination ({len(data_json)} bytes)")
            except Exception as e:
                logger.warning(f"Error preparing JSON data for pagination: {e}")
                data_json = "[]"
        else:
            logger.warning(f"DataFrame too large for client-side pagination ({len(df)} rows). Consider server-side pagination.")
            data_json = "[]"
    else:
        # Include the entire table in the HTML
        table_html = df.to_html(table_id='urlTable', index=False, classes='display compact', escape=True)
        data_json = "[]"
    
    # Generate additional JavaScript for DataTables with pagination
    if enable_pagination:
        datatable_js = """
        $(document).ready(function() {
            // Initialize DataTable with pagination
            const dataTable = $('#urlTable').DataTable({
                paging: true,
                pageLength: """ + str(page_size) + """,
                lengthMenu: [10, 25, 50, 100, 250, 500],
                searching: true,
                ordering: true,
                info: true,
                responsive: true,
                deferRender: true,
                scroller: true,
                scrollY: '50vh',
                scrollCollapse: true
            });
            
            // Add custom search functionality
            $('.filter-select').on('change', function() {
                const column = $(this).data('column');
                const value = $(this).val();
                
                dataTable.column(column + ':name').search(value).draw();
            });
        });
        """
    else:
        datatable_js = """
        $(document).ready(function() {
            // Initialize DataTable without pagination
            $('#urlTable').DataTable({
                paging: true,
                searching: true,
                ordering: true
            });
        });
        """
    
    # Generate additional JavaScript for lazy loading charts
    if enable_lazy_loading:
        charts_js = """
        // Lazy loading for charts
        document.addEventListener('DOMContentLoaded', function() {
            // Use Intersection Observer to detect when elements are visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const target = entry.target;
                        
                        // Load the appropriate chart based on the target ID
                        if (target.id === 'categoryChart') {
                            loadCategoryChart();
                        } else if (target.id === 'topDomainsChart') {
                            loadTopDomainsChart();
                        }
                        
                        // Stop observing once loaded
                        observer.unobserve(target);
                    }
                });
            }, { threshold: 0.1 });
            
            // Observe chart containers
            const chartElements = document.querySelectorAll('.chart-container canvas');
            chartElements.forEach(element => {
                observer.observe(element);
            });
            
            // Function to load category chart
            function loadCategoryChart() {
                const ctx = document.getElementById('categoryChart').getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: """ + chart_labels + """,
                        datasets: [{
                            data: """ + chart_data + """,
                            backgroundColor: ['#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#9013fe', '#7ed321', '#417505'],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right'
                            }
                        }
                    }
                });
            }
            
            // Function to load top domains chart
            function loadTopDomainsChart() {
                // Implementation of top domains chart
                // This would be populated with actual data
            }
        });
        """
    else:
        charts_js = """
        // Initialize charts immediately
        document.addEventListener('DOMContentLoaded', function() {
            // Category chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            new Chart(categoryCtx, {
                type: 'doughnut',
                data: {
                    labels: """ + chart_labels + """,
                    datasets: [{
                        data: """ + chart_data + """,
                        backgroundColor: ['#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#9013fe', '#7ed321', '#417505'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
            
            // Top domains chart would be initialized here
        });
        """
    
    # Add CSS for loading indicators if lazy loading is enabled
    if enable_lazy_loading:
        additional_css = """
        /* Loading indicator styles */
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid var(--border-color);
            border-top: 5px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        """
    else:
        additional_css = ""
    
    # Create context dictionary
    context = {
        'df': df,
        'stats': stats,
        'filter_html': filter_html,
        'stats_boxes_html': stats_boxes_html,
        'time_charts_html': time_charts_html,
        'sankey_html': sankey_html,
        'top_n_by_client_json': sanitize_json_string(top_n_by_client_json),
        'chart_labels': sanitize_json_string(chart_labels),
        'chart_data': sanitize_json_string(chart_data),
        'column_defs_js': column_defs_js,
        'table_html': table_html,
        'data_json': data_json,
        'pagination': pagination_settings,
        'csrf_token': os.urandom(16).hex(),
        'enable_lazy_loading': enable_lazy_loading,
        'datatable_js': datatable_js,
        'charts_js': charts_js,
        'additional_css': additional_css,
        'report_id': f"report_{int(time.time())}"  # Generate a unique report ID for API calls
    }
    
    return context


def generate_report_from_template(df: pd.DataFrame, output_path: str, stats: Dict[str, Any], 
                                 template_name: str = 'default.html') -> str:
    """
    Generates an HTML report using a Jinja2 template.
    
    Args:
        df: DataFrame containing URL data
        output_path: Path where to save the HTML report
        stats: Dictionary of statistics for the report
        template_name: Name of the template to use
        
    Returns:
        Path to the generated HTML report
        
    Raises:
        ValidationError: If any input parameters are invalid
        IOError: If there's an error writing to the output file
    """
    # Import validation and sanitization utilities
    from url_analyzer.utils.validation import validate_string, validate_dict, validate_type
    from url_analyzer.utils.sanitization import sanitize_html, sanitize_json_string, sanitize_input
    from url_analyzer.utils.errors import ValidationError
    from url_analyzer.utils.logging import get_logger
    
    # Create logger
    logger = get_logger(__name__)
    
    try:
        # Validate input parameters
        logger.debug("Validating input parameters for template-based HTML report generation")
        
        # Validate DataFrame
        validate_type(df, pd.DataFrame, error_message="df must be a pandas DataFrame")
        
        if df.empty:
            logger.warning("DataFrame is empty, report may not contain useful information")
        
        # Validate output path
        output_path = validate_string(
            output_path, 
            allow_empty=False, 
            error_message="Output path cannot be empty"
        )
        
        # Validate stats dictionary
        validate_dict(
            stats, 
            error_message="Stats must be a dictionary"
        )
        
        # Validate template name
        template_name = validate_string(
            template_name, 
            allow_empty=False, 
            error_message="Template name cannot be empty"
        )
        
        # Get the templates directory
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        
        # Get the template path
        template_path = get_template_path(template_name)
        template_filename = os.path.basename(template_path)
        
        logger.info(f"Generating HTML report using template '{template_name}' for {len(df)} rows to {output_path}")
        
        # Set up Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(os.path.dirname(template_path)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Try to load the template
        try:
            template = env.get_template(template_filename)
        except Exception as e:
            logger.warning(f"Error loading template {template_filename}: {e}")
            logger.info("Falling back to built-in HTML generation.")
            return generate_html_report(df, output_path, stats)
        
        # Calculate stats for the template
        stats_boxes = []
        for cat, count in stats.items():
            if cat == 'category_counts':
                # Skip the raw category_counts dictionary as it's displayed in the chart
                continue
            # Sanitize category name and count
            safe_cat = sanitize_html(str(cat))
            safe_count = sanitize_html(str(count))
            stats_boxes.append(f"<div class='stat-box'><h3>{safe_cat}</h3><p>{safe_count}</p></div>")
        
        # Add individual category count boxes
        if 'category_counts' in stats:
            for category, count in stats['category_counts'].items():
                # Sanitize category name and count
                safe_category = sanitize_html(str(category))
                safe_count = sanitize_html(str(count))
                stats_boxes.append(f"<div class='stat-box'><h3>{safe_category}</h3><p>{safe_count}</p></div>")
        
        stats_boxes_html = "".join(stats_boxes)
        
        # Create filter HTML for client and MAC address filters
        filter_html_parts = []
        for col_name in ['Client_Name', 'MAC_address']:
            if col_name in df.columns:
                options = df[col_name].dropna().unique().tolist()
                options_html = "".join([
                    f'<option value="{sanitize_html(str(opt))}">{sanitize_html(str(opt))}</option>' 
                    for opt in options
                ])
                # Sanitize column name
                safe_col_name = sanitize_html(col_name)
                safe_col_display = sanitize_html(col_name.replace('_', ' '))
                filter_html_parts.append(
                    f"<div class='filter-box'><label for='{safe_col_name}_filter'>{safe_col_display}:</label>"
                    f"<select id='{safe_col_name}_filter' class='datatable-filter'>"
                    f"<option value=''>All</option>{options_html}</select></div>"
                )
        filters_html = "".join(filter_html_parts)
        
        # Prepare chart data
        # Ensure category_counts exists
        if 'category_counts' not in stats:
            logger.warning("'category_counts' not found in stats dictionary, chart may not display correctly")
            stats['category_counts'] = {}
            
        # Convert to JSON and sanitize
        chart_labels_raw = json.dumps(list(stats['category_counts'].keys()))
        chart_data_raw = json.dumps([int(v) for v in stats['category_counts'].values()])
        
        chart_labels = sanitize_json_string(chart_labels_raw)
        chart_data = sanitize_json_string(chart_data_raw)
        
        # Pre-calculate Top N data for each client for interactive chart
        top_n_by_client = {}
        
        # Add an 'All' entry for when no client is selected
        if 'Base_Domain' in df.columns:
            top_n_all = df['Base_Domain'].value_counts().nlargest(10).sort_values()
            top_n_by_client['All'] = {'labels': top_n_all.index.tolist(), 'data': top_n_all.tolist()}
        else:
            # Provide default values if Base_Domain column doesn't exist
            logger.warning("'Base_Domain' column not found in DataFrame, top domains chart will be empty")
            top_n_by_client['All'] = {'labels': [], 'data': []}
        
        if 'Client_Name' in df.columns and 'Base_Domain' in df.columns:
            for client in df['Client_Name'].unique():
                top_n = df[df['Client_Name'] == client]['Base_Domain'].value_counts().nlargest(10).sort_values()
                top_n_by_client[client] = {'labels': top_n.index.tolist(), 'data': top_n.tolist()}
        
        # Convert to JSON and sanitize
        top_n_by_client_json_raw = json.dumps(top_n_by_client)
        top_n_by_client_json = sanitize_json_string(top_n_by_client_json_raw)
        
        # Generate column definitions for DataTables
        column_defs = []
        for col_name in ['Client_Name', 'MAC_address']:
            if col_name in df.columns:
                # Sanitize column name
                safe_col_name = sanitize_html(col_name)
                column_defs.append(f'{{"name": "{safe_col_name}", "targets": {df.columns.get_loc(col_name)}}}')
        
        column_defs_js = f"[{', '.join(column_defs)}]"
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Validation error generating template-based HTML report: {str(e)}")
        raise
    except Exception as e:
        # Log and re-raise other exceptions
        error_msg = f"Error generating template-based HTML report: {str(e)}"
        logger.error(error_msg)
        raise
    
    # JavaScript for charts
    charts_js = f"""
        // Initialize category chart
        new Chart(document.getElementById('categoryChart'), {{
            type: 'doughnut',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    data: {chart_data},
                    backgroundColor: ['#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#9013fe', '#7ed321', '#417505'],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});
        
        // Initialize top domains chart
        const topDomainsChart = new Chart(document.getElementById('topDomainsChart'), {{
            type: 'bar',
            options: {{
                indexAxis: 'y',
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    title: {{
                        display: true,
                        text: 'Top 10 Visited Domains (All Clients)'
                    }}
                }}
            }}
        }});
        
        function updateTopDomainsChart(clientName) {{
            const chartData = topNByClientData[clientName] || topNByClientData['All'];
            topDomainsChart.data.labels = chartData.labels;
            topDomainsChart.data.datasets = [{{
                label: 'Visits',
                data: chartData.data,
                backgroundColor: '#50e3c2'
            }}];
            topDomainsChart.options.plugins.title.text = `Top 10 Visited Domains (` + (clientName || 'All Clients') + `)`;
            topDomainsChart.update();
        }}
        
        // Initial chart load
        updateTopDomainsChart(null);
    """
    
    # JavaScript for DataTables
    datatable_js = f"""
        var table = $('#urlTable').DataTable({{
            "pageLength": 25,
            "columnDefs": {column_defs_js}
        }});
        
        $('#Client_Name_filter').on('change', function() {{
            var clientName = $(this).val();
            var searchVal = clientName ? '^' + $.fn.dataTable.util.escapeRegex(clientName) + '$' : '';
            table.column('Client_Name:name').search(searchVal, true, false).draw();
            updateTopDomainsChart(clientName);
        }});
        
        $('#MAC_address_filter').on('change', function() {{
            table.column('MAC_address:name').search($(this).val() ? '^' + $.fn.dataTable.util.escapeRegex($(this).val()) + '$' : '', true, false).draw();
        }});
        
        function exportData(format) {{
            // Get CSRF token
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            
            // Include CSRF token in the export data
            const data = table.rows({{ search: 'applied' }}).data().toArray();
            const headers = table.columns().header().toArray().map(h => h.innerText);
            
            // Add metadata including CSRF token for security
            const metadata = {{
                exportDate: new Date().toISOString(),
                csrfToken: csrfToken,
                exportFormat: format
            }};
            
            // Create content with proper escaping
            let content;
            if (format === 'csv') {{
                content = [headers.join(','), ...data.map(row => row.map(val => `"${{String(val).replace(/"/g, '""')}}"`).join(','))].join('\\n');
            }} else {{
                // For JSON, include metadata
                const jsonData = {{
                    metadata: metadata,
                    data: data.map(row => Object.fromEntries(headers.map((h, i) => [h, row[i]])))
                }};
                content = JSON.stringify(jsonData, null, 2);
            }}
            
            // Create and download the file
            const blob = new Blob([content], {{ type: `text/${{format}};charset=utf-8;` }});
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `report_export.${{format}}`;
            link.click();
        }}
        
        $('#exportCsv').on('click', () => exportData('csv'));
        $('#exportJson').on('click', () => exportData('json'));
    """
    
    # JavaScript for chart data
    chart_data_js = f"""
        const chartLabels = {chart_labels};
        const chartData = {chart_data};
        const topNByClientData = {top_n_by_client_json};
        const columnDefs = {column_defs_js};
    """
    
    # Get available templates for template switching
    available_templates = list_available_templates()
    
    # Generate CSRF token for protection
    csrf_token = os.urandom(16).hex()  # Generate a random token
    
    # Prepare data for the template with security enhancements
    template_data = {
        'df': df,
        'stats': stats,
        'time_charts_html': generate_time_analysis_charts(df),
        'sankey_html': generate_sankey_diagram(df),
        'table_html': df.to_html(table_id='urlTable', index=False, classes='display compact', escape=True),
        'stats_boxes_html': stats_boxes_html,
        'filters_html': filters_html,
        'chart_data_js': chart_data_js,
        'charts_js': charts_js,
        'datatable_js': datatable_js,
        'report_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'available_templates': available_templates,
        'current_template': template_filename,
        'report_path': output_path,
        'csrf_token': csrf_token,  # Add CSRF token to template data
        'security_headers': {
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.datatables.net https://cdn.plot.ly; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.datatables.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
    }
    
    # Render the template
    html = template.render(**template_data)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Write the HTML to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path