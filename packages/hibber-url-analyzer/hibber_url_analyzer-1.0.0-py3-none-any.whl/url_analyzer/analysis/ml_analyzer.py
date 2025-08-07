"""
Machine Learning Analyzer for URL Analysis.

This module provides machine learning capabilities for URL analysis, including
pattern recognition, clustering, and classification of URLs based on various features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
import json
from collections import Counter
import math
import logging
import os

# Optional imports with fallbacks
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.decomposition import PCA
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, silhouette_score
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from url_analyzer.analysis.interfaces import ContentAnalyzer
from url_analyzer.analysis.domain import URLContent, AnalysisResult, AnalysisOptions
from url_analyzer.analysis.statistical import StatisticalAnalyzer

logger = logging.getLogger(__name__)

class MLAnalyzer:
    """
    Machine Learning Analyzer for URL data.
    
    This class provides machine learning capabilities for analyzing URL data,
    including pattern recognition, clustering, and classification.
    """
    
    @staticmethod
    def extract_features_from_urls(urls: List[str]) -> pd.DataFrame:
        """
        Extract features from URLs for machine learning analysis.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            DataFrame containing extracted features
        """
        features = []
        
        for url in urls:
            # Basic features
            url_length = len(url)
            domain_part = url.split('/')[0] if '/' in url else url
            domain_length = len(domain_part)
            path_length = url_length - domain_length - 1 if '/' in url else 0
            
            # Count special characters
            num_dots = url.count('.')
            num_hyphens = url.count('-')
            num_underscores = url.count('_')
            num_slashes = url.count('/')
            num_equals = url.count('=')
            num_question_marks = url.count('?')
            num_ampersands = url.count('&')
            num_digits = sum(c.isdigit() for c in url)
            
            # TLD features
            tld = domain_part.split('.')[-1] if '.' in domain_part else ''
            tld_length = len(tld)
            
            # Create feature dictionary
            feature_dict = {
                'url_length': url_length,
                'domain_length': domain_length,
                'path_length': path_length,
                'num_dots': num_dots,
                'num_hyphens': num_hyphens,
                'num_underscores': num_underscores,
                'num_slashes': num_slashes,
                'num_equals': num_equals,
                'num_question_marks': num_question_marks,
                'num_ampersands': num_ampersands,
                'num_digits': num_digits,
                'tld_length': tld_length,
                'has_https': url.startswith('https'),
                'has_www': 'www.' in url,
                'digit_ratio': num_digits / url_length if url_length > 0 else 0,
                'special_char_ratio': (num_dots + num_hyphens + num_underscores + 
                                      num_slashes + num_equals + num_question_marks + 
                                      num_ampersands) / url_length if url_length > 0 else 0
            }
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    @staticmethod
    def cluster_urls(urls: List[str], n_clusters: int = 5, method: str = "kmeans") -> Dict[str, Any]:
        """
        Cluster URLs based on their features.
        
        Args:
            urls: List of URLs to cluster
            n_clusters: Number of clusters to create (for KMeans)
            method: Clustering method to use ('kmeans' or 'dbscan')
            
        Returns:
            Dictionary containing clustering results
        """
        if len(urls) < 2:
            return {"error": "Need at least 2 URLs for clustering"}
        
        # Extract features
        features_df = MLAnalyzer.extract_features_from_urls(urls)
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features_df)
        
        # Apply dimensionality reduction for visualization
        pca = PCA(n_components=2)
        reduced_features = pca.fit_transform(scaled_features)
        
        # Perform clustering
        labels = None
        if method.lower() == "kmeans":
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(scaled_features)
            centers = kmeans.cluster_centers_
            centers_2d = pca.transform(centers)
            silhouette = silhouette_score(scaled_features, labels) if len(set(labels)) > 1 else 0
            
            # Transform centers back to original feature space
            centers_original = scaler.inverse_transform(centers)
            centers_df = pd.DataFrame(centers_original, columns=features_df.columns)
            
            result = {
                "method": "kmeans",
                "n_clusters": n_clusters,
                "labels": labels.tolist(),
                "centers_2d": centers_2d.tolist(),
                "centers": centers_df.to_dict(orient="records"),
                "silhouette_score": silhouette,
                "reduced_features": reduced_features.tolist()
            }
            
        elif method.lower() == "dbscan":
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            labels = dbscan.fit_predict(scaled_features)
            n_clusters_found = len(set(labels)) - (1 if -1 in labels else 0)
            silhouette = silhouette_score(scaled_features, labels) if n_clusters_found > 1 and len(set(labels)) > 1 else 0
            
            result = {
                "method": "dbscan",
                "n_clusters_found": n_clusters_found,
                "labels": labels.tolist(),
                "silhouette_score": silhouette,
                "reduced_features": reduced_features.tolist(),
                "noise_points": (labels == -1).sum()
            }
        else:
            return {"error": f"Unsupported clustering method: {method}"}
        
        # Add cluster assignments to URLs
        url_clusters = []
        for i, url in enumerate(urls):
            url_clusters.append({
                "url": url,
                "cluster": int(labels[i])
            })
        
        result["url_clusters"] = url_clusters
        
        return result
    
    @staticmethod
    def train_url_classifier(urls: List[str], labels: List[str], model_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Train a classifier to categorize URLs based on their features.
        
        Args:
            urls: List of URLs to use for training
            labels: List of labels corresponding to the URLs
            model_path: Optional path to save the trained model
            
        Returns:
            Dictionary containing training results
        """
        if len(urls) != len(labels):
            return {"error": "Number of URLs and labels must match"}
        
        if len(urls) < 10:
            return {"error": "Need at least 10 URLs for training"}
        
        # Extract features
        features_df = MLAnalyzer.extract_features_from_urls(urls)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_df, labels, test_size=0.2, random_state=42, stratify=labels if len(set(labels)) > 1 else None
        )
        
        # Create and train classifier
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        # Evaluate
        y_pred = clf.predict(X_test)
        accuracy = clf.score(X_test, y_test)
        
        # Feature importance
        feature_importance = sorted(
            zip(features_df.columns, clf.feature_importances_),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Save model if path provided
        if model_path:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(clf, model_path)
        
        return {
            "accuracy": accuracy,
            "feature_importance": feature_importance,
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "model_saved": model_path is not None,
            "model_path": model_path
        }
    
    @staticmethod
    def classify_urls(urls: List[str], model_path: str) -> Dict[str, Any]:
        """
        Classify URLs using a pre-trained model.
        
        Args:
            urls: List of URLs to classify
            model_path: Path to the trained model
            
        Returns:
            Dictionary containing classification results
        """
        if not os.path.exists(model_path):
            return {"error": f"Model not found at {model_path}"}
        
        # Load model
        clf = joblib.load(model_path)
        
        # Extract features
        features_df = MLAnalyzer.extract_features_from_urls(urls)
        
        # Predict
        predictions = clf.predict(features_df)
        probabilities = clf.predict_proba(features_df)
        
        # Format results
        results = []
        for i, url in enumerate(urls):
            result = {
                "url": url,
                "predicted_class": predictions[i],
                "confidence": max(probabilities[i])
            }
            results.append(result)
        
        return {
            "classifications": results,
            "class_distribution": Counter(predictions).most_common()
        }
    
    @staticmethod
    def detect_url_patterns(urls: List[str]) -> Dict[str, Any]:
        """
        Detect patterns in URLs using machine learning techniques.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            Dictionary containing pattern detection results
        """
        # Extract features
        features_df = MLAnalyzer.extract_features_from_urls(urls)
        
        # Apply PCA for dimensionality reduction
        pca = PCA(n_components=min(5, len(features_df.columns)))
        pca_result = pca.fit_transform(StandardScaler().fit_transform(features_df))
        
        # Detect outliers
        outlier_detector = IsolationForest(contamination=0.1, random_state=42)
        outliers = outlier_detector.fit_predict(features_df)
        outlier_indices = [i for i, x in enumerate(outliers) if x == -1]
        
        # Cluster URLs
        clustering_result = MLAnalyzer.cluster_urls(urls, n_clusters=min(5, len(urls)))
        
        # Analyze TF-IDF patterns in URLs
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 5))
        tfidf_matrix = vectorizer.fit_transform(urls)
        
        # Get top features for each URL
        feature_names = vectorizer.get_feature_names_out()
        top_features = []
        
        for i, url in enumerate(urls):
            url_features = tfidf_matrix[i].toarray()[0]
            top_indices = url_features.argsort()[-5:][::-1]
            top_url_features = [(feature_names[idx], url_features[idx]) for idx in top_indices]
            top_features.append({
                "url": url,
                "top_features": top_url_features
            })
        
        return {
            "pca_components": pca.components_.tolist(),
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "outlier_urls": [urls[i] for i in outlier_indices],
            "clustering": clustering_result,
            "url_features": top_features
        }


class MLContentAnalyzer(ContentAnalyzer):
    """
    Machine Learning Content Analyzer for URL content.
    
    This class implements the ContentAnalyzer interface to provide
    machine learning analysis of URL content.
    """
    
    def __init__(self, name: str = "ML Content Analyzer"):
        """
        Initialize the ML Content Analyzer.
        
        Args:
            name: Name of the analyzer
        """
        self.name = name
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.statistical_analyzer = StatisticalAnalyzer()
    
    def analyze_content(self, content: URLContent, options: AnalysisOptions) -> AnalysisResult:
        """
        Analyze URL content using machine learning techniques.
        
        Args:
            content: URL content to analyze
            options: Analysis options
            
        Returns:
            Analysis result
        """
        if not content.is_success():
            return AnalysisResult(
                url=content.url,
                success=False,
                error="Content fetch was not successful",
                metadata={}
            )
        
        metadata = {}
        metadata["analyzer"] = self.name
        
        try:
            # Extract text content
            text_content = ""
            if content.is_html():
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content.content, 'html.parser')
                    text_content = soup.get_text()
                except ImportError:
                    # Fall back to simple regex if BeautifulSoup is not available
                    import re
                    text_content = re.sub(r'<[^>]+>', ' ', content.content)
            elif content.is_json():
                # Convert JSON to string representation
                try:
                    json_data = json.loads(content.content)
                    text_content = json.dumps(json_data)
                except json.JSONDecodeError:
                    text_content = content.content
            else:
                text_content = content.content
            
            if not text_content:
                metadata["error"] = "No text content available for analysis"
                return AnalysisResult(
                    url=content.url,
                    success=False,
                    metadata=metadata
                )
            
            # Text statistics
            word_count = len(text_content.split())
            metadata["word_count"] = word_count
            
            if word_count > 0 and SKLEARN_AVAILABLE:
                # Perform TF-IDF analysis
                tfidf_matrix = self.vectorizer.fit_transform([text_content])
                feature_names = self.vectorizer.get_feature_names_out()
                
                # Get top terms
                dense = tfidf_matrix.todense()
                top_indices = dense.argsort().tolist()[0][-10:]
                top_terms = [(feature_names[i], float(dense[0, i])) for i in top_indices]
                
                metadata["top_terms"] = top_terms
                
                # Content complexity metrics
                avg_word_length = sum(len(word) for word in text_content.split()) / word_count
                metadata["avg_word_length"] = avg_word_length
                
                # Sentiment analysis (simplified)
                positive_words = ["good", "great", "excellent", "best", "positive", "nice", "love", "perfect"]
                negative_words = ["bad", "worst", "terrible", "poor", "negative", "hate", "awful", "horrible"]
                
                words = text_content.lower().split()
                positive_count = sum(1 for word in words if word in positive_words)
                negative_count = sum(1 for word in words if word in negative_words)
                
                sentiment_score = (positive_count - negative_count) / word_count if word_count > 0 else 0
                metadata["sentiment_score"] = sentiment_score
                
                # Topic modeling (simplified)
                topics = []
                tech_words = ["software", "technology", "computer", "digital", "data", "code", "programming"]
                finance_words = ["money", "finance", "bank", "investment", "stock", "market", "economic"]
                health_words = ["health", "medical", "doctor", "patient", "hospital", "treatment", "medicine"]
                
                tech_score = sum(1 for word in words if word in tech_words) / word_count
                finance_score = sum(1 for word in words if word in finance_words) / word_count
                health_score = sum(1 for word in words if word in health_words) / word_count
                
                if tech_score > 0.01:
                    topics.append(("technology", tech_score))
                if finance_score > 0.01:
                    topics.append(("finance", finance_score))
                if health_score > 0.01:
                    topics.append(("health", health_score))
                
                metadata["topics"] = topics
                
                # Content classification (simplified)
                if tech_score > finance_score and tech_score > health_score:
                    metadata["content_category"] = "technology"
                elif finance_score > tech_score and finance_score > health_score:
                    metadata["content_category"] = "finance"
                elif health_score > tech_score and health_score > finance_score:
                    metadata["content_category"] = "health"
                else:
                    metadata["content_category"] = "general"
            
            return AnalysisResult(
                url=content.url,
                success=True,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error in ML content analysis: {str(e)}")
            metadata["error"] = str(e)
            return AnalysisResult(
                url=content.url,
                success=False,
                metadata=metadata
            )
    
    def get_name(self) -> str:
        """
        Get the name of the analyzer.
        
        Returns:
            Analyzer name
        """
        return self.name
    
    def get_supported_content_types(self) -> Set[str]:
        """
        Get the content types supported by this analyzer.
        
        Returns:
            Set of supported content types
        """
        return {"text/html", "application/json", "text/plain"}