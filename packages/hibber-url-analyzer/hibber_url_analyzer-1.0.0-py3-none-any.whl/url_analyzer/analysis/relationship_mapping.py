"""
Relationship Mapping Module for URL Analyzer.

This module provides functionality for mapping relationships between URLs, domains,
and content. It helps identify connections and patterns in browsing behavior and
content relationships.
"""

import logging
from typing import Dict, List, Tuple, Set, Any, Optional, Union
import re
from collections import defaultdict
import math
from datetime import datetime
from urllib.parse import urlparse

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    import community as community_louvain
    COMMUNITY_DETECTION_AVAILABLE = True
except ImportError:
    COMMUNITY_DETECTION_AVAILABLE = False

from url_analyzer.analysis.domain import URLContent, AnalysisOptions, AnalysisResult

logger = logging.getLogger(__name__)


class RelationshipMapper:
    """
    Class for mapping relationships between URLs, domains, and content.
    
    This class provides methods to analyze and visualize relationships between
    different URLs, domains, and their content. It can identify patterns in
    browsing behavior, content similarity, and domain relationships.
    """
    
    def __init__(self):
        """Initialize the RelationshipMapper."""
        self.url_graph = None
        self.domain_graph = None
        if NETWORKX_AVAILABLE:
            self.url_graph = nx.DiGraph()
            self.domain_graph = nx.Graph()
        else:
            logger.warning("NetworkX not available. Graph-based relationship mapping will be limited.")
    
    def map_url_relationships(self, url_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Map relationships between URLs based on various factors.
        
        Args:
            url_data: List of dictionaries containing URL data
                Each dictionary should have at least 'url' and optionally
                'content', 'domain', 'timestamp', etc.
        
        Returns:
            Dictionary containing relationship mapping results
        """
        if not NETWORKX_AVAILABLE:
            return {
                "error": "NetworkX library is required for relationship mapping",
                "relationships_found": 0
            }
        
        # Reset graphs
        self.url_graph = nx.DiGraph()
        self.domain_graph = nx.Graph()
        
        # Extract domains and add nodes
        domains = set()
        for item in url_data:
            url = item.get('url', '')
            if not url:
                continue
                
            # Add URL node
            self.url_graph.add_node(url, 
                                   timestamp=item.get('timestamp', datetime.now()),
                                   category=item.get('category', ''),
                                   content_length=len(item.get('content', '')))
            
            # Extract domain
            domain = self._extract_domain(url)
            domains.add(domain)
            
            # Add domain node if not exists
            if not self.domain_graph.has_node(domain):
                self.domain_graph.add_node(domain, url_count=0)
            
            # Increment URL count for this domain
            self.domain_graph.nodes[domain]['url_count'] += 1
        
        # Map relationships between URLs
        self._map_sequential_relationships(url_data)
        self._map_content_relationships(url_data)
        self._map_domain_relationships(domains)
        
        # Calculate metrics
        url_metrics = self._calculate_url_graph_metrics()
        domain_metrics = self._calculate_domain_graph_metrics()
        
        # Detect communities if available
        communities = self._detect_communities()
        
        return {
            "url_relationships": {
                "node_count": self.url_graph.number_of_nodes(),
                "edge_count": self.url_graph.number_of_edges(),
                "metrics": url_metrics,
                "top_central_urls": self._get_top_central_nodes(self.url_graph, 5)
            },
            "domain_relationships": {
                "node_count": self.domain_graph.number_of_nodes(),
                "edge_count": self.domain_graph.number_of_edges(),
                "metrics": domain_metrics,
                "top_domains": self._get_top_central_nodes(self.domain_graph, 5)
            },
            "communities": communities,
            "relationships_found": self.url_graph.number_of_edges() + self.domain_graph.number_of_edges()
        }
    
    def _map_sequential_relationships(self, url_data: List[Dict[str, Any]]) -> None:
        """
        Map relationships between URLs based on sequential access patterns.
        
        Args:
            url_data: List of dictionaries containing URL data
        """
        # Sort by timestamp if available
        sorted_data = sorted(url_data, 
                            key=lambda x: x.get('timestamp', datetime.now()), 
                            reverse=False)
        
        # Connect sequential URLs
        for i in range(len(sorted_data) - 1):
            current_url = sorted_data[i].get('url', '')
            next_url = sorted_data[i + 1].get('url', '')
            
            if current_url and next_url:
                # Add directed edge from current to next
                if self.url_graph.has_edge(current_url, next_url):
                    # Increment weight if edge exists
                    self.url_graph[current_url][next_url]['weight'] += 1
                else:
                    # Create new edge with weight 1
                    self.url_graph.add_edge(current_url, next_url, 
                                           weight=1, 
                                           type='sequential')
    
    def _map_content_relationships(self, url_data: List[Dict[str, Any]]) -> None:
        """
        Map relationships between URLs based on content similarity.
        
        Args:
            url_data: List of dictionaries containing URL data
        """
        # Create a list of URLs with content
        urls_with_content = [(item.get('url', ''), item.get('content', '')) 
                            for item in url_data if item.get('content')]
        
        # Calculate content similarity between pairs
        for i in range(len(urls_with_content)):
            url1, content1 = urls_with_content[i]
            
            for j in range(i + 1, len(urls_with_content)):
                url2, content2 = urls_with_content[j]
                
                # Calculate similarity
                similarity = self._calculate_content_similarity(content1, content2)
                
                # Add edge if similarity is above threshold
                if similarity > 0.3:  # Threshold for meaningful similarity
                    self.url_graph.add_edge(url1, url2, 
                                           weight=similarity, 
                                           type='content_similarity')
                    self.url_graph.add_edge(url2, url1, 
                                           weight=similarity, 
                                           type='content_similarity')
    
    def _map_domain_relationships(self, domains: Set[str]) -> None:
        """
        Map relationships between domains.
        
        Args:
            domains: Set of domain names
        """
        # Connect domains based on URL relationships
        for url1, url2, data in self.url_graph.edges(data=True):
            domain1 = self._extract_domain(url1)
            domain2 = self._extract_domain(url2)
            
            if domain1 != domain2:
                # Add or update edge between domains
                if self.domain_graph.has_edge(domain1, domain2):
                    self.domain_graph[domain1][domain2]['weight'] += data.get('weight', 1)
                    self.domain_graph[domain1][domain2]['url_pairs'].append((url1, url2))
                else:
                    self.domain_graph.add_edge(domain1, domain2, 
                                              weight=data.get('weight', 1),
                                              url_pairs=[(url1, url2)])
        
        # Connect domains based on name similarity
        domain_list = list(domains)
        for i in range(len(domain_list)):
            for j in range(i + 1, len(domain_list)):
                domain1 = domain_list[i]
                domain2 = domain_list[j]
                
                # Calculate domain similarity
                similarity = self._calculate_domain_similarity(domain1, domain2)
                
                # Add edge if similarity is above threshold
                if similarity > 0.7:  # High threshold for domain similarity
                    if self.domain_graph.has_edge(domain1, domain2):
                        # Update existing edge
                        self.domain_graph[domain1][domain2]['name_similarity'] = similarity
                    else:
                        # Create new edge
                        self.domain_graph.add_edge(domain1, domain2, 
                                                  weight=1,
                                                  name_similarity=similarity,
                                                  url_pairs=[])
    
    def _calculate_url_graph_metrics(self) -> Dict[str, float]:
        """
        Calculate metrics for the URL graph.
        
        Returns:
            Dictionary of graph metrics
        """
        metrics = {}
        
        try:
            # Basic metrics
            metrics['density'] = nx.density(self.url_graph)
            
            # Degree metrics
            in_degrees = [d for n, d in self.url_graph.in_degree()]
            out_degrees = [d for n, d in self.url_graph.out_degree()]
            
            if in_degrees:
                metrics['avg_in_degree'] = sum(in_degrees) / len(in_degrees)
                metrics['max_in_degree'] = max(in_degrees)
            
            if out_degrees:
                metrics['avg_out_degree'] = sum(out_degrees) / len(out_degrees)
                metrics['max_out_degree'] = max(out_degrees)
            
            # Connectivity metrics
            if nx.is_strongly_connected(self.url_graph):
                metrics['strongly_connected'] = True
            else:
                metrics['strongly_connected'] = False
                metrics['strongly_connected_components'] = nx.number_strongly_connected_components(self.url_graph)
            
            # Try to calculate more advanced metrics
            try:
                # Centrality metrics (can be computationally expensive for large graphs)
                if self.url_graph.number_of_nodes() < 1000:
                    betweenness = nx.betweenness_centrality(self.url_graph)
                    metrics['max_betweenness'] = max(betweenness.values()) if betweenness else 0
                    
                    pagerank = nx.pagerank(self.url_graph)
                    metrics['max_pagerank'] = max(pagerank.values()) if pagerank else 0
            except Exception as e:
                logger.warning(f"Error calculating advanced URL graph metrics: {e}")
                
        except Exception as e:
            logger.error(f"Error calculating URL graph metrics: {e}")
            metrics['error'] = str(e)
            
        return metrics
    
    def _calculate_domain_graph_metrics(self) -> Dict[str, float]:
        """
        Calculate metrics for the domain graph.
        
        Returns:
            Dictionary of graph metrics
        """
        metrics = {}
        
        try:
            # Basic metrics
            metrics['density'] = nx.density(self.domain_graph)
            
            # Degree metrics
            degrees = [d for n, d in self.domain_graph.degree()]
            
            if degrees:
                metrics['avg_degree'] = sum(degrees) / len(degrees)
                metrics['max_degree'] = max(degrees)
            
            # Connectivity metrics
            if nx.is_connected(self.domain_graph):
                metrics['connected'] = True
            else:
                metrics['connected'] = False
                metrics['connected_components'] = nx.number_connected_components(self.domain_graph)
            
            # Try to calculate more advanced metrics
            try:
                # Centrality metrics
                if self.domain_graph.number_of_nodes() < 1000:
                    betweenness = nx.betweenness_centrality(self.domain_graph)
                    metrics['max_betweenness'] = max(betweenness.values()) if betweenness else 0
                    
                    eigenvector = nx.eigenvector_centrality(self.domain_graph, max_iter=1000)
                    metrics['max_eigenvector'] = max(eigenvector.values()) if eigenvector else 0
            except Exception as e:
                logger.warning(f"Error calculating advanced domain graph metrics: {e}")
                
        except Exception as e:
            logger.error(f"Error calculating domain graph metrics: {e}")
            metrics['error'] = str(e)
            
        return metrics
    
    def _detect_communities(self) -> Dict[str, Any]:
        """
        Detect communities in the domain graph.
        
        Returns:
            Dictionary containing community detection results
        """
        results = {
            "available": False,
            "method": None,
            "count": 0
        }
        
        if not COMMUNITY_DETECTION_AVAILABLE:
            results["error"] = "Community detection requires the 'community' package"
            return results
        
        try:
            # Convert to undirected graph for community detection
            if isinstance(self.url_graph, nx.DiGraph):
                undirected = self.url_graph.to_undirected()
            else:
                undirected = self.url_graph
            
            # Detect communities using Louvain method
            partition = community_louvain.best_partition(undirected)
            
            # Count communities
            communities = defaultdict(list)
            for node, community_id in partition.items():
                communities[community_id].append(node)
            
            results["available"] = True
            results["method"] = "louvain"
            results["count"] = len(communities)
            results["sizes"] = [len(nodes) for nodes in communities.values()]
            
            # Include top communities
            top_communities = sorted(communities.items(), 
                                    key=lambda x: len(x[1]), 
                                    reverse=True)[:3]
            
            results["top_communities"] = [
                {"id": comm_id, "size": len(nodes), "sample_nodes": nodes[:5]}
                for comm_id, nodes in top_communities
            ]
            
        except Exception as e:
            logger.error(f"Error in community detection: {e}")
            results["error"] = str(e)
            
        return results
    
    def _get_top_central_nodes(self, graph: Union["nx.Graph", "nx.DiGraph"], n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top central nodes in a graph.
        
        Args:
            graph: NetworkX graph
            n: Number of top nodes to return
            
        Returns:
            List of dictionaries containing node information
        """
        try:
            # Calculate degree centrality
            if isinstance(graph, nx.DiGraph):
                centrality = nx.in_degree_centrality(graph)
            else:
                centrality = nx.degree_centrality(graph)
            
            # Sort nodes by centrality
            sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            
            # Return top n nodes
            return [
                {
                    "node": node,
                    "centrality": round(score, 4),
                    "attributes": dict(graph.nodes[node])
                }
                for node, score in sorted_nodes[:n]
            ]
            
        except Exception as e:
            logger.error(f"Error getting top central nodes: {e}")
            return []
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate similarity between two content strings.
        
        Args:
            content1: First content string
            content2: Second content string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not content1 or not content2:
            return 0.0
        
        # Convert to lowercase and split into words
        words1 = set(re.findall(r'\w+', content1.lower()))
        words2 = set(re.findall(r'\w+', content2.lower()))
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
            
        return intersection / union
    
    def _calculate_domain_similarity(self, domain1: str, domain2: str) -> float:
        """
        Calculate similarity between two domain names.
        
        Args:
            domain1: First domain name
            domain2: Second domain name
            
        Returns:
            Similarity score between 0 and 1
        """
        if not domain1 or not domain2:
            return 0.0
        
        # Extract main domain parts
        parts1 = domain1.split('.')
        parts2 = domain2.split('.')
        
        # Check for exact TLD match
        if len(parts1) > 1 and len(parts2) > 1:
            if parts1[-1] == parts2[-1]:  # Same TLD
                # Check for same domain name
                if parts1[-2] == parts2[-2]:
                    return 1.0
                
                # Calculate similarity of domain names
                name1 = parts1[-2]
                name2 = parts2[-2]
                
                # Levenshtein distance (simplified)
                distance = self._levenshtein_distance(name1, name2)
                max_len = max(len(name1), len(name2))
                
                if max_len == 0:
                    return 0.0
                    
                return 1.0 - (distance / max_len)
        
        # Default similarity for different TLDs
        return 0.1
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Levenshtein distance
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            # Return original URL if parsing fails
            return url


class RelationshipAnalyzer:
    """
    Analyzer for URL relationships.
    
    This class provides methods to analyze relationships between URLs,
    domains, and content.
    """
    
    def __init__(self):
        """Initialize the RelationshipAnalyzer."""
        self.mapper = RelationshipMapper()
    
    def get_name(self) -> str:
        """
        Get the name of the analyzer.
        
        Returns:
            Analyzer name
        """
        return "Relationship Analyzer"
    
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types
        """
        return {"text/html", "text/plain", "application/json"}
    
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> AnalysisResult:
        """
        Analyze URL content for relationships.
        
        Args:
            content: URL content to analyze
            options: Analysis options
            
        Returns:
            Analysis result
        """
        results = {}
        
        # Check if we have enough data for relationship mapping
        if not hasattr(options, 'url_data') or not options.url_data:
            results["error"] = "Relationship mapping requires url_data in options"
            return AnalysisResult(
                analyzer_name=self.get_name(),
                results=results
            )
        
        # Map relationships
        relationship_results = self.mapper.map_url_relationships(options.url_data)
        results.update(relationship_results)
        
        return AnalysisResult(
            analyzer_name=self.get_name(),
            results=results
        )


def analyze_url_relationships(url_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze relationships between URLs.
    
    Args:
        url_data: List of dictionaries containing URL data
            Each dictionary should have at least 'url' and optionally
            'content', 'domain', 'timestamp', etc.
    
    Returns:
        Dictionary containing relationship analysis results
    """
    mapper = RelationshipMapper()
    return mapper.map_url_relationships(url_data)