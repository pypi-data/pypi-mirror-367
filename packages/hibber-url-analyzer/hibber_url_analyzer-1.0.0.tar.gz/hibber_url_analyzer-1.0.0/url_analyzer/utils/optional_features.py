"""
Optional features for URL Analyzer.

This module demonstrates how to implement graceful degradation
when optional dependencies are missing.
"""

import logging
from typing import Dict, List, Optional, Union, Any
import urllib.parse

# Configure logging
logger = logging.getLogger(__name__)

# Import feature flags
from url_analyzer.utils.feature_flags import is_feature_available, with_feature

# Try to import optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.debug("requests package not found, URL fetching will use urllib")

try:
    import tldextract
    HAS_TLDEXTRACT = True
except ImportError:
    HAS_TLDEXTRACT = False
    logger.debug("tldextract package not found, domain extraction will use basic parsing")

try:
    from bs4 import BeautifulSoup
    import lxml
    HAS_HTML_PARSING = True
except ImportError:
    HAS_HTML_PARSING = False
    logger.debug("beautifulsoup4 or lxml not found, HTML parsing will be limited")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logger.debug("plotly not found, advanced visualizations will be unavailable")


def extract_domain_info(url: str) -> Dict[str, str]:
    """
    Extract domain information from a URL.
    
    This function demonstrates graceful degradation when tldextract is not available.
    
    Args:
        url: The URL to analyze
        
    Returns:
        Dictionary with domain information
    """
    # Use feature flag to check if domain_extraction is available
    if is_feature_available("domain_extraction"):
        # Use tldextract for better domain parsing
        extracted = tldextract.extract(url)
        return {
            "subdomain": extracted.subdomain,
            "domain": extracted.domain,
            "suffix": extracted.suffix,
            "registered_domain": extracted.registered_domain,
            "fqdn": extracted.fqdn
        }
    else:
        # Fallback implementation using urllib
        logger.warning("Using basic domain extraction (tldextract not available)")
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.netloc
        
        # Basic parsing - not as accurate as tldextract
        parts = hostname.split('.')
        
        if len(parts) >= 3:
            subdomain = '.'.join(parts[:-2])
            domain = parts[-2]
            suffix = parts[-1]
        elif len(parts) == 2:
            subdomain = ""
            domain = parts[0]
            suffix = parts[1]
        else:
            subdomain = ""
            domain = hostname
            suffix = ""
            
        return {
            "subdomain": subdomain,
            "domain": domain,
            "suffix": suffix,
            "registered_domain": f"{domain}.{suffix}" if suffix else domain,
            "fqdn": hostname
        }


@with_feature("url_fetching", fallback_result={"error": "URL fetching not available"})
def fetch_url_content(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch content from a URL.
    
    This function uses the @with_feature decorator to check if the feature is available.
    
    Args:
        url: The URL to fetch
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with response data
    """
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "status_code": response.status_code,
            "content": response.text,
            "headers": dict(response.headers),
            "url": response.url
        }
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return {
            "error": str(e),
            "url": url
        }


def parse_html_content(html_content: str) -> Dict[str, Any]:
    """
    Parse HTML content and extract useful information.
    
    This function demonstrates checking for dependencies directly.
    
    Args:
        html_content: HTML content to parse
        
    Returns:
        Dictionary with extracted information
    """
    if not HAS_HTML_PARSING:
        logger.warning("HTML parsing is limited (beautifulsoup4 or lxml not available)")
        # Basic fallback implementation
        result = {}
        
        # Extract title with basic parsing
        title_start = html_content.find("<title>")
        title_end = html_content.find("</title>")
        if title_start != -1 and title_end != -1:
            result["title"] = html_content[title_start + 7:title_end].strip()
        else:
            result["title"] = ""
            
        # Count links with basic parsing
        result["link_count"] = html_content.count("<a ")
        
        # Count images with basic parsing
        result["image_count"] = html_content.count("<img ")
        
        return result
    else:
        # Use BeautifulSoup for better HTML parsing
        soup = BeautifulSoup(html_content, "lxml")
        
        # Extract metadata
        meta_tags = {}
        for tag in soup.find_all("meta"):
            if tag.get("name"):
                meta_tags[tag.get("name")] = tag.get("content", "")
            elif tag.get("property"):
                meta_tags[tag.get("property")] = tag.get("content", "")
        
        # Extract links
        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                links.append({
                    "href": href,
                    "text": link.get_text().strip()
                })
        
        # Extract images
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                images.append({
                    "src": src,
                    "alt": img.get("alt", "")
                })
        
        return {
            "title": soup.title.get_text() if soup.title else "",
            "meta_tags": meta_tags,
            "links": links,
            "link_count": len(links),
            "images": images,
            "image_count": len(images),
            "headings": {
                f"h{i}": len(soup.find_all(f"h{i}"))
                for i in range(1, 7)
            }
        }


def create_domain_visualization(domain_data: List[Dict[str, Any]]) -> Optional[str]:
    """
    Create a visualization of domain data.
    
    This function demonstrates checking feature availability and returning None when not available.
    
    Args:
        domain_data: List of dictionaries with domain information
        
    Returns:
        HTML string with visualization or None if plotly is not available
    """
    if not is_feature_available("advanced_visualization"):
        logger.warning("Advanced visualization not available (plotly not installed)")
        return None
    
    # Count domains
    domain_counts = {}
    for item in domain_data:
        domain = item.get("registered_domain", "")
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Sort by count
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    domains = [item[0] for item in sorted_domains[:20]]  # Top 20
    counts = [item[1] for item in sorted_domains[:20]]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(x=domains, y=counts)
    ])
    
    fig.update_layout(
        title="Top Domains",
        xaxis_title="Domain",
        yaxis_title="Count",
        template="plotly_white"
    )
    
    return fig.to_html(include_plotlyjs="cdn")


def analyze_url(url: str) -> Dict[str, Any]:
    """
    Analyze a URL using available features.
    
    This function demonstrates combining multiple optional features.
    
    Args:
        url: URL to analyze
        
    Returns:
        Dictionary with analysis results
    """
    result = {
        "url": url,
        "domain_info": extract_domain_info(url),
        "features_available": {
            "url_fetching": is_feature_available("url_fetching"),
            "html_parsing": is_feature_available("html_parsing"),
            "domain_extraction": is_feature_available("domain_extraction"),
            "advanced_visualization": is_feature_available("advanced_visualization")
        }
    }
    
    # Fetch content if available
    if is_feature_available("url_fetching"):
        content_result = fetch_url_content(url)
        result["fetch_result"] = content_result
        
        # Parse HTML if content was fetched successfully and parsing is available
        if "content" in content_result and is_feature_available("html_parsing"):
            result["html_analysis"] = parse_html_content(content_result["content"])
    
    return result


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test URL analysis
    test_url = "https://www.example.com"
    result = analyze_url(test_url)
    
    print(f"\nAnalysis of {test_url}:")
    print(f"Domain info: {result['domain_info']}")
    print(f"Features available: {result['features_available']}")
    
    if "fetch_result" in result:
        if "error" in result["fetch_result"]:
            print(f"Error fetching URL: {result['fetch_result']['error']}")
        else:
            print(f"Fetch successful: Status {result['fetch_result']['status_code']}")
            
            if "html_analysis" in result:
                print(f"Title: {result['html_analysis'].get('title', '')}")
                print(f"Links: {result['html_analysis'].get('link_count', 0)}")
                print(f"Images: {result['html_analysis'].get('image_count', 0)}")
    else:
        print("URL fetching not available")