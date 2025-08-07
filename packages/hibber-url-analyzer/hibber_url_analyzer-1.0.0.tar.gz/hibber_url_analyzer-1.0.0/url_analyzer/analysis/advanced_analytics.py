"""
Advanced Analytics Module for URL Analyzer

This module provides advanced data analysis capabilities for URL data, including:
- Statistical analysis tools
- Trend detection
- Anomaly detection
- Custom analytics
- Machine learning integration
- Predictive analytics

It builds upon the existing analysis modules and adds new capabilities.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from datetime import datetime, timedelta
import json
from collections import Counter
import math
import logging
import os
import re

# Optional imports with fallbacks
try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    # Download required NLTK data if not already present
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
except ImportError:
    NLTK_AVAILABLE = False

from url_analyzer.analysis.interfaces import ContentAnalyzer
from url_analyzer.analysis.domain import URLContent, AnalysisResult, AnalysisOptions
from url_analyzer.analysis.statistical import StatisticalAnalyzer
from url_analyzer.analysis.trends import TrendAnalyzer
from url_analyzer.analysis.anomalies import AnomalyDetector
from url_analyzer.analysis.ml_analyzer import MLAnalyzer
from url_analyzer.analysis.predictive import PredictiveAnalyzer
from url_analyzer.analysis.custom_analytics import CustomAnalyzer, CustomMetric

logger = logging.getLogger(__name__)


class AdvancedAnalytics:
    """
    Advanced analytics class that combines multiple analysis techniques
    and provides additional advanced capabilities.
    """

    def __init__(self):
        """Initialize the AdvancedAnalytics class."""
        self.statistical_analyzer = StatisticalAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.ml_analyzer = MLAnalyzer()
        self.predictive_analyzer = PredictiveAnalyzer()
        self.custom_analyzer = CustomAnalyzer()
        
        # Register default custom metrics
        self._register_default_metrics()

    def _register_default_metrics(self):
        """Register default custom metrics for analysis."""
        # Topic diversity metric
        self.custom_analyzer.register_metric(
            CustomMetric(
                name="topic_diversity",
                calculation_fn=self._calculate_topic_diversity,
                description="Measures the diversity of topics in URL content",
                parameters={"min_topics": 3, "max_topics": 10}
            )
        )
        
        # Content complexity metric
        self.custom_analyzer.register_metric(
            CustomMetric(
                name="content_complexity",
                calculation_fn=self._calculate_content_complexity,
                description="Measures the complexity of URL content",
                parameters={}
            )
        )
        
        # URL relationship strength metric
        self.custom_analyzer.register_metric(
            CustomMetric(
                name="url_relationship_strength",
                calculation_fn=self._calculate_url_relationship_strength,
                description="Measures the strength of relationships between URLs",
                parameters={"threshold": 0.5}
            )
        )

    def _calculate_topic_diversity(self, data: Any, **kwargs) -> float:
        """
        Calculate the diversity of topics in URL content.
        
        Args:
            data: URL content data
            **kwargs: Additional parameters (min_topics, max_topics)
            
        Returns:
            float: Topic diversity score (0-1)
        """
        # Extract parameters from kwargs
        min_topics = kwargs.get('min_topics', 3)
        max_topics = kwargs.get('max_topics', 10)
        if not SKLEARN_AVAILABLE or not isinstance(data, str):
            return 0.0
            
        try:
            # Extract text features
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X = vectorizer.fit_transform([data])
            
            # Determine optimal number of topics
            optimal_k = min(max(3, X.shape[1] // 10), 10)
            
            # Cluster into topics
            kmeans = KMeans(n_clusters=optimal_k, random_state=42)
            kmeans.fit(X)
            
            # Calculate diversity based on cluster sizes
            cluster_sizes = np.bincount(kmeans.labels_)
            normalized_sizes = cluster_sizes / np.sum(cluster_sizes)
            
            # Calculate entropy as a measure of diversity
            entropy = -np.sum(normalized_sizes * np.log2(normalized_sizes + 1e-10))
            max_entropy = np.log2(optimal_k)
            
            # Normalize to 0-1 range
            diversity_score = entropy / max_entropy if max_entropy > 0 else 0
            
            return diversity_score
        except Exception as e:
            logger.warning(f"Error calculating topic diversity: {e}")
            return 0.0

    def _calculate_content_complexity(self, data: Any) -> float:
        """
        Calculate the complexity of URL content based on various metrics.
        
        Args:
            data: URL content data
            
        Returns:
            float: Content complexity score (0-1)
        """
        if not isinstance(data, str):
            return 0.0
            
        try:
            # Calculate various complexity metrics
            metrics = []
            
            # 1. Vocabulary richness
            if NLTK_AVAILABLE:
                tokens = word_tokenize(data.lower())
                stop_words = set(stopwords.words('english'))
                filtered_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]
                
                if filtered_tokens:
                    unique_words = len(set(filtered_tokens))
                    total_words = len(filtered_tokens)
                    vocab_richness = unique_words / total_words if total_words > 0 else 0
                    metrics.append(vocab_richness)
            
            # 2. Sentence complexity
            sentences = re.split(r'[.!?]+', data)
            sentence_lengths = [len(re.findall(r'\w+', s)) for s in sentences if s.strip()]
            if sentence_lengths:
                avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
                # Normalize to 0-1 range (assuming 30 words is max complexity)
                sentence_complexity = min(avg_sentence_length / 30, 1.0)
                metrics.append(sentence_complexity)
            
            # 3. Structural complexity
            structural_elements = len(re.findall(r'<[^>]+>', data))
            # Normalize to 0-1 range (assuming 100 elements is max complexity)
            structural_complexity = min(structural_elements / 100, 1.0)
            metrics.append(structural_complexity)
            
            # Combine metrics
            if metrics:
                return sum(metrics) / len(metrics)
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating content complexity: {e}")
            return 0.0

    def _calculate_url_relationship_strength(self, data: Any, **kwargs) -> Dict[str, float]:
        """
        Calculate the strength of relationships between URLs.
        
        Args:
            data: List of URLs or URL data
            **kwargs: Additional parameters (threshold)
            
        Returns:
            Dict[str, float]: Dictionary of URL pairs and their relationship strengths
        """
        # Extract parameters from kwargs
        threshold = kwargs.get('threshold', 0.3)
        if not NETWORKX_AVAILABLE or not isinstance(data, list):
            return {}
            
        try:
            # Create a graph of URL relationships
            G = nx.Graph()
            
            # Extract URLs from data
            urls = []
            if all(isinstance(item, str) for item in data):
                urls = data
            elif all(isinstance(item, dict) for item in data):
                urls = [item.get('url') for item in data if item.get('url')]
            
            if not urls:
                return {}
                
            # Add nodes for each URL
            for url in urls:
                G.add_node(url)
            
            # Add edges based on domain similarity
            for i, url1 in enumerate(urls):
                domain1 = re.search(r'://([^/]+)', url1)
                if not domain1:
                    continue
                domain1 = domain1.group(1)
                
                for j in range(i+1, len(urls)):
                    url2 = urls[j]
                    domain2 = re.search(r'://([^/]+)', url2)
                    if not domain2:
                        continue
                    domain2 = domain2.group(1)
                    
                    # Calculate similarity
                    similarity = self._calculate_domain_similarity(domain1, domain2)
                    if similarity > threshold:  # Threshold for adding an edge
                        G.add_edge(url1, url2, weight=similarity)
            
            # Calculate relationship strengths
            relationship_strengths = {}
            for u, v, data in G.edges(data=True):
                relationship_strengths[f"{u}|{v}"] = data.get('weight', 0.0)
                
            return relationship_strengths
        except Exception as e:
            logger.warning(f"Error calculating URL relationship strength: {e}")
            return {}

    def _calculate_domain_similarity(self, domain1: str, domain2: str) -> float:
        """
        Calculate similarity between two domains.
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            float: Similarity score (0-1)
        """
        # Simple similarity based on common parts
        parts1 = domain1.split('.')
        parts2 = domain2.split('.')
        
        # Compare TLDs
        if parts1[-1] != parts2[-1]:
            return 0.1  # Different TLDs have low similarity
            
        # Compare main domain
        if len(parts1) > 1 and len(parts2) > 1 and parts1[-2] == parts2[-2]:
            return 0.8  # Same main domain has high similarity
            
        # Calculate Jaccard similarity for subdomains
        if len(parts1) > 2 and len(parts2) > 2:
            set1 = set(parts1[:-2])
            set2 = set(parts2[:-2])
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            if union > 0:
                return 0.5 * (intersection / union)
                
        return 0.2  # Default similarity

    def analyze_url_clusters(self, urls: List[str], n_clusters: int = 5) -> Dict[str, Any]:
        """
        Analyze URL clusters to identify patterns and relationships.
        
        Args:
            urls: List of URLs to analyze
            n_clusters: Number of clusters to create
            
        Returns:
            Dict[str, Any]: Cluster analysis results
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn is not available. URL clustering analysis requires scikit-learn.")
            return {"error": "scikit-learn is required for URL clustering analysis"}
            
        try:
            # Extract features from URLs
            features = self.ml_analyzer.extract_features_from_urls(urls)
            
            # Standardize features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)
            
            # Reduce dimensionality for visualization
            pca = PCA(n_components=min(5, scaled_features.shape[1]))
            pca_features = pca.fit_transform(scaled_features)
            
            # Cluster URLs
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_features)
            
            # Calculate cluster statistics
            cluster_stats = {}
            for i in range(n_clusters):
                cluster_urls = [urls[j] for j in range(len(urls)) if clusters[j] == i]
                cluster_stats[f"cluster_{i}"] = {
                    "size": len(cluster_urls),
                    "percentage": len(cluster_urls) / len(urls) * 100,
                    "sample_urls": cluster_urls[:5],
                    "center": kmeans.cluster_centers_[i].tolist()
                }
            
            # Calculate silhouette score
            if len(set(clusters)) > 1 and len(clusters) > n_clusters and SKLEARN_AVAILABLE:
                try:
                    from sklearn.metrics import silhouette_score
                    silhouette = silhouette_score(scaled_features, clusters)
                except ImportError:
                    silhouette = 0
            else:
                silhouette = 0
                
            return {
                "n_clusters": n_clusters,
                "silhouette_score": silhouette,
                "cluster_stats": cluster_stats,
                "pca_features": pca_features.tolist(),
                "clusters": clusters.tolist(),
                "explained_variance": pca.explained_variance_ratio_.tolist()
            }
        except Exception as e:
            logger.error(f"Error in URL cluster analysis: {e}")
            return {"error": str(e)}

    def perform_topic_modeling(self, texts: List[str], n_topics: int = 5) -> Dict[str, Any]:
        """
        Perform topic modeling on a collection of texts.
        
        Args:
            texts: List of text content to analyze
            n_topics: Number of topics to extract
            
        Returns:
            Dict[str, Any]: Topic modeling results
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn is not available. Topic modeling requires scikit-learn.")
            return {"error": "scikit-learn is required for topic modeling"}
            
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                min_df=2,
                max_df=0.9
            )
            X = vectorizer.fit_transform(texts)
            
            # Perform topic modeling using NMF
            if SKLEARN_AVAILABLE:
                try:
                    from sklearn.decomposition import NMF
                    nmf = NMF(n_components=n_topics, random_state=42)
                    topic_distributions = nmf.fit_transform(X)
                except ImportError:
                    logger.error("NMF not available for topic modeling")
                    return {"error": "NMF not available for topic modeling"}
            else:
                return {"error": "scikit-learn is required for topic modeling"}
            
            # Get feature names
            feature_names = vectorizer.get_feature_names_out()
            
            # Extract top words for each topic
            topics = []
            for topic_idx, topic in enumerate(nmf.components_):
                top_words_idx = topic.argsort()[:-11:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append({
                    "id": topic_idx,
                    "top_words": top_words,
                    "weight": float(np.sum(topic))
                })
            
            # Assign dominant topics to texts
            dominant_topics = []
            for i, dist in enumerate(topic_distributions):
                dominant_topic = int(np.argmax(dist))
                dominant_topics.append({
                    "text_index": i,
                    "dominant_topic": dominant_topic,
                    "topic_distribution": dist.tolist()
                })
                
            return {
                "n_topics": n_topics,
                "topics": topics,
                "document_topics": dominant_topics,
                "topic_term_matrix": nmf.components_.tolist()
            }
        except Exception as e:
            logger.error(f"Error in topic modeling: {e}")
            return {"error": str(e)}

    def analyze_url_network(self, urls: List[str], link_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze the network of relationships between URLs.
        
        Args:
            urls: List of URLs to analyze
            link_data: Optional list of link data (source, target, weight)
            
        Returns:
            Dict[str, Any]: Network analysis results
        """
        if not NETWORKX_AVAILABLE:
            logger.warning("networkx is not available. Network analysis requires networkx.")
            return {"error": "networkx is required for URL network analysis"}
            
        try:
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes for each URL
            for url in urls:
                G.add_node(url)
            
            # Add edges from link data if provided
            if link_data:
                for link in link_data:
                    source = link.get('source')
                    target = link.get('target')
                    weight = link.get('weight', 1.0)
                    
                    if source in urls and target in urls:
                        G.add_edge(source, target, weight=weight)
            
            # Calculate network metrics
            metrics = {
                "node_count": G.number_of_nodes(),
                "edge_count": G.number_of_edges(),
                "density": nx.density(G),
                "is_connected": nx.is_weakly_connected(G),
                "average_clustering": nx.average_clustering(G),
                "average_shortest_path_length": 0,
                "diameter": 0
            }
            
            # Calculate path metrics if the graph is connected
            if nx.is_weakly_connected(G) and G.number_of_nodes() > 1:
                try:
                    metrics["average_shortest_path_length"] = nx.average_shortest_path_length(G)
                    metrics["diameter"] = nx.diameter(G)
                except nx.NetworkXError:
                    # Handle disconnected graphs
                    pass
            
            # Calculate centrality measures
            centrality = {
                "degree": dict(nx.degree_centrality(G)),
                "betweenness": dict(nx.betweenness_centrality(G)),
                "closeness": dict(nx.closeness_centrality(G)),
                "pagerank": dict(nx.pagerank(G))
            }
            
            # Identify communities
            communities = []
            if G.number_of_nodes() > 2 and NETWORKX_AVAILABLE:
                try:
                    # Only attempt if networkx is available
                    if hasattr(nx, 'algorithms') and hasattr(nx.algorithms, 'community'):
                        communities_generator = nx.algorithms.community.girvan_newman(G)
                        top_level_communities = next(communities_generator)
                        communities = [list(c) for c in top_level_communities]
                    else:
                        logger.warning("Community detection not available in this version of networkx")
                except Exception as e:
                    logger.warning(f"Error detecting communities: {e}")
            
            return {
                "metrics": metrics,
                "centrality": centrality,
                "communities": communities,
                "nodes": list(G.nodes()),
                "edges": [{"source": u, "target": v, "weight": d.get("weight", 1.0)} 
                          for u, v, d in G.edges(data=True)]
            }
        except Exception as e:
            logger.error(f"Error in URL network analysis: {e}")
            return {"error": str(e)}

    def comprehensive_analysis(self, url_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of URL data combining multiple analysis techniques.
        
        Args:
            url_data: List of URL data dictionaries
            
        Returns:
            Dict[str, Any]: Comprehensive analysis results
        """
        results = {}
        
        try:
            # Extract URLs and texts
            urls = [item.get('url') for item in url_data if item.get('url')]
            texts = [item.get('content', '') for item in url_data if item.get('content')]
            
            # 1. Statistical analysis
            if urls:
                url_patterns = self.statistical_analyzer.analyze_url_patterns(urls)
                results["statistical_analysis"] = url_patterns
            
            # 2. Trend analysis
            if len(url_data) > 5 and all('timestamp' in item for item in url_data):
                try:
                    domain_trends = self.trend_analyzer.analyze_domain_trends(url_data)
                    category_trends = self.trend_analyzer.analyze_category_trends(url_data)
                    results["trend_analysis"] = {
                        "domain_trends": domain_trends,
                        "category_trends": category_trends
                    }
                except Exception as e:
                    logger.warning(f"Error in trend analysis: {e}")
            
            # 3. Anomaly detection
            if len(url_data) > 10:
                try:
                    volume_anomalies = self.anomaly_detector.detect_url_volume_anomalies(url_data)
                    domain_anomalies = self.anomaly_detector.detect_domain_anomalies(url_data)
                    results["anomaly_detection"] = {
                        "volume_anomalies": volume_anomalies,
                        "domain_anomalies": domain_anomalies
                    }
                except Exception as e:
                    logger.warning(f"Error in anomaly detection: {e}")
            
            # 4. URL clustering
            if len(urls) > 5:
                try:
                    cluster_analysis = self.analyze_url_clusters(urls, n_clusters=min(5, len(urls) // 2))
                    results["cluster_analysis"] = cluster_analysis
                except Exception as e:
                    logger.warning(f"Error in cluster analysis: {e}")
            
            # 5. Topic modeling
            if len(texts) > 5 and any(text for text in texts):
                try:
                    topic_analysis = self.perform_topic_modeling(
                        [text for text in texts if text], 
                        n_topics=min(5, len(texts) // 2)
                    )
                    results["topic_analysis"] = topic_analysis
                except Exception as e:
                    logger.warning(f"Error in topic analysis: {e}")
            
            # 6. Network analysis
            if len(urls) > 3:
                try:
                    # Create simple link data based on domain similarity
                    link_data = []
                    for i, url1 in enumerate(urls):
                        for j, url2 in enumerate(urls):
                            if i != j:
                                domain1 = re.search(r'://([^/]+)', url1)
                                domain2 = re.search(r'://([^/]+)', url2)
                                if domain1 and domain2:
                                    similarity = self._calculate_domain_similarity(
                                        domain1.group(1), domain2.group(1)
                                    )
                                    if similarity > 0.5:
                                        link_data.append({
                                            "source": url1,
                                            "target": url2,
                                            "weight": similarity
                                        })
                    
                    network_analysis = self.analyze_url_network(urls, link_data)
                    results["network_analysis"] = network_analysis
                except Exception as e:
                    logger.warning(f"Error in network analysis: {e}")
            
            # 7. Custom metrics
            try:
                custom_metrics = self.custom_analyzer.analyze_url_data(url_data)
                results["custom_metrics"] = custom_metrics
            except Exception as e:
                logger.warning(f"Error in custom metrics analysis: {e}")
            
            # 8. Predictive analysis
            if len(url_data) > 10 and all('timestamp' in item for item in url_data):
                try:
                    url_growth = self.predictive_analyzer.predict_url_growth(
                        url_data, forecast_periods=7
                    )
                    category_shifts = self.predictive_analyzer.predict_category_shifts(
                        url_data, forecast_periods=7
                    )
                    results["predictive_analysis"] = {
                        "url_growth": url_growth,
                        "category_shifts": category_shifts
                    }
                except Exception as e:
                    logger.warning(f"Error in predictive analysis: {e}")
            
            return results
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}


class AdvancedContentAnalyzer(ContentAnalyzer):
    """
    Advanced content analyzer that combines multiple analysis techniques
    and provides comprehensive content analysis.
    """
    
    def __init__(self, name: str = "Advanced Content Analyzer"):
        """
        Initialize the AdvancedContentAnalyzer.
        
        Args:
            name: Name of the analyzer
        """
        self.name = name
        self.advanced_analytics = AdvancedAnalytics()
        
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> AnalysisResult:
        """
        Analyze URL content using advanced analytics techniques.
        
        Args:
            content: URL content to analyze
            options: Analysis options
            
        Returns:
            AnalysisResult: Analysis results
        """
        # Create a mock FetchResult since we're working with already fetched content
        from url_analyzer.analysis.domain import FetchResult
        fetch_result = FetchResult(
            url=content.url,
            success=content.status_code >= 200 and content.status_code < 300,
            status_code=content.status_code,
            content=content,
            error_message=None,
            fetch_time=content.fetch_time
        )
        
        # Create the analysis result
        result = AnalysisResult(
            url=content.url,
            fetch_result=fetch_result,
            metadata={"analyzer": self.name}
        )
        
        try:
            # Extract content data
            url = content.url
            content_text = content.content
            content_type = content.content_type
            headers = content.headers
            
            # Create URL data dictionary
            url_data = {
                "url": url,
                "content": content_text,
                "html": content_text if content_type.lower().startswith('text/html') else "",
                "timestamp": datetime.now(),
                "metadata": headers
            }
            
            # Perform comprehensive analysis
            analysis_results = self.advanced_analytics.comprehensive_analysis([url_data])
            
            # Add results to the analysis result's metadata
            result.metadata["comprehensive_analysis"] = analysis_results
            
            # Add specific analyses based on options
            # Check if extract_keywords is enabled (as a proxy for topic modeling)
            if options.extract_keywords and content_text:
                topic_results = self.advanced_analytics.perform_topic_modeling([content_text])
                result.metadata["topic_modeling"] = topic_results
                
            # Always calculate custom metrics
            custom_metrics = self.advanced_analytics.custom_analyzer.analyze_urls([url])
            result.metadata["custom_metrics"] = custom_metrics
                
            # Add content complexity analysis
            if content_text:
                complexity = self.advanced_analytics._calculate_content_complexity(content_text)
                result.metadata["content_complexity"] = complexity
                
            # Add topic diversity analysis
            if content_text:
                diversity = self.advanced_analytics._calculate_topic_diversity(content_text)
                result.metadata["topic_diversity"] = diversity
                
            return result
        except Exception as e:
            logger.error(f"Error in advanced content analysis: {e}")
            result.metadata["error"] = str(e)
            return result
            
    def get_name(self) -> str:
        """
        Get the name of the analyzer.
        
        Returns:
            str: Analyzer name
        """
        return self.name
        
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set[str]: Set of supported content types
        """
        return {"text/html", "text/plain", "application/json"}