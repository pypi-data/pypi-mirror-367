"""
Topic Modeling and Text Analysis Module

This module provides advanced text analysis capabilities for URL content,
including topic modeling, entity recognition, sentiment analysis, and
text classification using machine learning techniques.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
import re
import json
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.decomposition import NMF, LatentDirichletAllocation
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import normalize
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
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

try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        # Try to load a spaCy model
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # If model not found, set flag to False
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class TopicModeler:
    """
    Provides topic modeling capabilities for text data.
    
    This class contains methods for extracting topics from text data
    using various algorithms such as NMF, LDA, and BERTopic.
    """
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Preprocess text for topic modeling.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not NLTK_AVAILABLE:
            # Basic preprocessing without NLTK
            text = text.lower()
            text = re.sub(r'[^\w\s]', '', text)
            return text
        
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        # Lemmatize
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        # Join tokens back into text
        return ' '.join(tokens)
    
    @staticmethod
    def extract_topics_nmf(
        texts: List[str],
        n_topics: int = 5,
        n_top_words: int = 10
    ) -> Dict[str, Any]:
        """
        Extract topics using Non-negative Matrix Factorization (NMF).
        
        Args:
            texts: List of text documents
            n_topics: Number of topics to extract
            n_top_words: Number of top words per topic
            
        Returns:
            Dictionary containing topic modeling results
        """
        if not SKLEARN_AVAILABLE:
            return {
                "error": "scikit-learn is required for NMF topic modeling",
                "topics": []
            }
        
        if not texts:
            return {
                "topics": [],
                "document_topics": []
            }
        
        # Preprocess texts
        preprocessed_texts = [TopicModeler.preprocess_text(text) for text in texts]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.9,
            stop_words='english'
        )
        
        # Create document-term matrix
        try:
            dtm = vectorizer.fit_transform(preprocessed_texts)
        except ValueError as e:
            return {
                "error": f"Error creating document-term matrix: {str(e)}",
                "topics": []
            }
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Apply NMF
        nmf = NMF(n_components=n_topics, random_state=42)
        nmf_result = nmf.fit_transform(dtm)
        
        # Extract topics
        topics = []
        for topic_idx, topic in enumerate(nmf.components_):
            top_indices = topic.argsort()[:-n_top_words-1:-1]
            top_words = [feature_names[i] for i in top_indices]
            topics.append({
                "id": topic_idx,
                "words": top_words,
                "weight": float(np.sum(topic))
            })
        
        # Assign topics to documents
        document_topics = []
        for i, doc_topic_weights in enumerate(nmf_result):
            dominant_topic = int(np.argmax(doc_topic_weights))
            document_topics.append({
                "document_index": i,
                "dominant_topic": dominant_topic,
                "topic_distribution": doc_topic_weights.tolist()
            })
        
        return {
            "topics": topics,
            "document_topics": document_topics,
            "method": "nmf"
        }
    
    @staticmethod
    def extract_topics_lda(
        texts: List[str],
        n_topics: int = 5,
        n_top_words: int = 10
    ) -> Dict[str, Any]:
        """
        Extract topics using Latent Dirichlet Allocation (LDA).
        
        Args:
            texts: List of text documents
            n_topics: Number of topics to extract
            n_top_words: Number of top words per topic
            
        Returns:
            Dictionary containing topic modeling results
        """
        if not SKLEARN_AVAILABLE:
            return {
                "error": "scikit-learn is required for LDA topic modeling",
                "topics": []
            }
        
        if not texts:
            return {
                "topics": [],
                "document_topics": []
            }
        
        # Preprocess texts
        preprocessed_texts = [TopicModeler.preprocess_text(text) for text in texts]
        
        # Create Count vectorizer
        vectorizer = CountVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.9,
            stop_words='english'
        )
        
        # Create document-term matrix
        try:
            dtm = vectorizer.fit_transform(preprocessed_texts)
        except ValueError as e:
            return {
                "error": f"Error creating document-term matrix: {str(e)}",
                "topics": []
            }
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Apply LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=10
        )
        lda_result = lda.fit_transform(dtm)
        
        # Extract topics
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_indices = topic.argsort()[:-n_top_words-1:-1]
            top_words = [feature_names[i] for i in top_indices]
            topics.append({
                "id": topic_idx,
                "words": top_words,
                "weight": float(np.sum(topic))
            })
        
        # Assign topics to documents
        document_topics = []
        for i, doc_topic_weights in enumerate(lda_result):
            dominant_topic = int(np.argmax(doc_topic_weights))
            document_topics.append({
                "document_index": i,
                "dominant_topic": dominant_topic,
                "topic_distribution": doc_topic_weights.tolist()
            })
        
        return {
            "topics": topics,
            "document_topics": document_topics,
            "method": "lda"
        }
    
    @staticmethod
    def extract_topics_bertopic(
        texts: List[str],
        n_topics: int = 5
    ) -> Dict[str, Any]:
        """
        Extract topics using BERTopic (if available).
        
        Args:
            texts: List of text documents
            n_topics: Number of topics to extract
            
        Returns:
            Dictionary containing topic modeling results
        """
        try:
            from bertopic import BERTopic
            
            if not texts:
                return {
                    "topics": [],
                    "document_topics": []
                }
            
            # Create BERTopic model
            topic_model = BERTopic(nr_topics=n_topics)
            
            # Fit model and transform documents
            topics, probs = topic_model.fit_transform(texts)
            
            # Get topic information
            topic_info = topic_model.get_topic_info()
            
            # Extract topics
            topic_list = []
            for topic_id in range(min(n_topics, len(topic_info))):
                if topic_id != -1:  # Skip outlier topic
                    topic_words = topic_model.get_topic(topic_id)
                    topic_list.append({
                        "id": topic_id,
                        "words": [word for word, _ in topic_words],
                        "weights": [float(weight) for _, weight in topic_words]
                    })
            
            # Assign topics to documents
            document_topics = []
            for i, (topic, prob) in enumerate(zip(topics, probs)):
                document_topics.append({
                    "document_index": i,
                    "dominant_topic": int(topic),
                    "probability": float(prob.max()) if prob.size > 0 else 0.0
                })
            
            return {
                "topics": topic_list,
                "document_topics": document_topics,
                "method": "bertopic"
            }
        except ImportError:
            # Fall back to NMF if BERTopic is not available
            logger.warning("BERTopic not available, falling back to NMF")
            return TopicModeler.extract_topics_nmf(texts, n_topics)
    
    @staticmethod
    def cluster_texts(
        texts: List[str],
        n_clusters: int = 5
    ) -> Dict[str, Any]:
        """
        Cluster texts based on their content.
        
        Args:
            texts: List of text documents
            n_clusters: Number of clusters
            
        Returns:
            Dictionary containing clustering results
        """
        if not SKLEARN_AVAILABLE:
            return {
                "error": "scikit-learn is required for text clustering",
                "clusters": []
            }
        
        if not texts:
            return {
                "clusters": [],
                "document_clusters": []
            }
        
        # Preprocess texts
        preprocessed_texts = [TopicModeler.preprocess_text(text) for text in texts]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.9,
            stop_words='english'
        )
        
        # Create document-term matrix
        try:
            dtm = vectorizer.fit_transform(preprocessed_texts)
        except ValueError as e:
            return {
                "error": f"Error creating document-term matrix: {str(e)}",
                "clusters": []
            }
        
        # Normalize the DTM
        dtm_normalized = normalize(dtm)
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(dtm_normalized)
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Extract cluster centroids
        cluster_info = []
        for i, centroid in enumerate(kmeans.cluster_centers_):
            top_indices = centroid.argsort()[:-11:-1]
            top_terms = [feature_names[idx] for idx in top_indices]
            cluster_info.append({
                "id": i,
                "top_terms": top_terms,
                "size": int(np.sum(clusters == i))
            })
        
        # Assign clusters to documents
        document_clusters = []
        for i, cluster in enumerate(clusters):
            document_clusters.append({
                "document_index": i,
                "cluster": int(cluster)
            })
        
        return {
            "clusters": cluster_info,
            "document_clusters": document_clusters,
            "method": "kmeans"
        }


class EntityRecognizer:
    """
    Provides entity recognition capabilities for text data.
    
    This class contains methods for extracting named entities from text
    using various NLP libraries such as spaCy and NLTK.
    """
    
    @staticmethod
    def extract_entities_spacy(text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        if not SPACY_AVAILABLE:
            return {
                "error": "spaCy is required for entity extraction",
                "entities": {}
            }
        
        # Process text with spaCy
        doc = nlp(text)
        
        # Extract entities
        entities = {}
        for ent in doc.ents:
            entity_type = ent.label_
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append(ent.text)
        
        return {
            "entities": entities,
            "method": "spacy"
        }
    
    @staticmethod
    def extract_entities_transformers(text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities using Hugging Face Transformers.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary containing entity extraction results
        """
        if not TRANSFORMERS_AVAILABLE:
            return {
                "error": "transformers is required for entity extraction",
                "entities": []
            }
        
        try:
            # Create NER pipeline
            ner_pipeline = pipeline("ner")
            
            # Extract entities
            entities = ner_pipeline(text)
            
            # Group entities by type
            entities_by_type = {}
            for entity in entities:
                entity_type = entity["entity"]
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append({
                    "word": entity["word"],
                    "score": float(entity["score"]),
                    "start": entity["start"],
                    "end": entity["end"]
                })
            
            return {
                "entities": entities_by_type,
                "method": "transformers"
            }
        except Exception as e:
            return {
                "error": f"Error extracting entities: {str(e)}",
                "entities": []
            }
    
    @staticmethod
    def extract_entities_nltk(text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using NLTK.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        if not NLTK_AVAILABLE:
            return {
                "error": "NLTK is required for entity extraction",
                "entities": {}
            }
        
        try:
            # Download required NLTK data if not already present
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            try:
                nltk.data.find('maxent_ne_chunker')
            except LookupError:
                nltk.download('maxent_ne_chunker', quiet=True)
            try:
                nltk.data.find('words')
            except LookupError:
                nltk.download('words', quiet=True)
            
            # Tokenize and tag text
            tokens = word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            
            # Extract named entities
            named_entities = nltk.ne_chunk(pos_tags)
            
            # Process named entities
            entities = {}
            for chunk in named_entities:
                if hasattr(chunk, 'label'):
                    entity_type = chunk.label()
                    entity_text = ' '.join(c[0] for c in chunk)
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].append(entity_text)
            
            return {
                "entities": entities,
                "method": "nltk"
            }
        except Exception as e:
            return {
                "error": f"Error extracting entities: {str(e)}",
                "entities": {}
            }


class SentimentAnalyzer:
    """
    Provides sentiment analysis capabilities for text data.
    
    This class contains methods for analyzing sentiment in text
    using various techniques and libraries.
    """
    
    @staticmethod
    def analyze_sentiment_basic(text: str) -> Dict[str, float]:
        """
        Perform basic sentiment analysis using lexicon-based approach.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment scores
        """
        if not NLTK_AVAILABLE:
            return {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "compound": 0.0,
                "method": "basic"
            }
        
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Simple sentiment lexicon
        positive_words = [
            "good", "great", "excellent", "best", "positive", "nice", "love", "perfect",
            "happy", "joy", "wonderful", "fantastic", "amazing", "awesome", "superb"
        ]
        negative_words = [
            "bad", "worst", "terrible", "poor", "negative", "hate", "awful", "horrible",
            "sad", "anger", "angry", "disappointing", "disappointed", "failure", "fail"
        ]
        
        # Count positive and negative words
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        total_count = len(tokens)
        
        # Calculate sentiment scores
        if total_count > 0:
            positive_score = positive_count / total_count
            negative_score = negative_count / total_count
            neutral_score = 1.0 - (positive_score + negative_score)
            compound_score = positive_score - negative_score
        else:
            positive_score = 0.0
            negative_score = 0.0
            neutral_score = 1.0
            compound_score = 0.0
        
        return {
            "positive": positive_score,
            "negative": negative_score,
            "neutral": neutral_score,
            "compound": compound_score,
            "method": "basic"
        }
    
    @staticmethod
    def analyze_sentiment_vader(text: str) -> Dict[str, float]:
        """
        Perform sentiment analysis using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment scores
        """
        if not NLTK_AVAILABLE:
            return {
                "error": "NLTK is required for VADER sentiment analysis",
                "method": "vader"
            }
        
        try:
            # Import VADER
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            
            # Create VADER analyzer
            vader = SentimentIntensityAnalyzer()
            
            # Analyze sentiment
            scores = vader.polarity_scores(text)
            
            return {
                "positive": scores["pos"],
                "negative": scores["neg"],
                "neutral": scores["neu"],
                "compound": scores["compound"],
                "method": "vader"
            }
        except Exception as e:
            # Fall back to basic sentiment analysis
            logger.warning(f"Error using VADER: {str(e)}. Falling back to basic sentiment analysis.")
            return SentimentAnalyzer.analyze_sentiment_basic(text)
    
    @staticmethod
    def analyze_sentiment_transformers(text: str) -> Dict[str, float]:
        """
        Perform sentiment analysis using Hugging Face Transformers.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment scores
        """
        if not TRANSFORMERS_AVAILABLE:
            return {
                "error": "transformers is required for transformer-based sentiment analysis",
                "method": "transformers"
            }
        
        try:
            # Create sentiment analysis pipeline
            sentiment_pipeline = pipeline("sentiment-analysis")
            
            # Analyze sentiment
            result = sentiment_pipeline(text)[0]
            
            # Extract label and score
            label = result["label"].lower()
            score = float(result["score"])
            
            # Convert to standard format
            if "positive" in label:
                return {
                    "positive": score,
                    "negative": 1.0 - score,
                    "neutral": 0.0,
                    "compound": score * 2 - 1,  # Scale to [-1, 1]
                    "method": "transformers"
                }
            elif "negative" in label:
                return {
                    "positive": 1.0 - score,
                    "negative": score,
                    "neutral": 0.0,
                    "compound": (1.0 - score) * 2 - 1,  # Scale to [-1, 1]
                    "method": "transformers"
                }
            else:
                return {
                    "positive": 0.0,
                    "negative": 0.0,
                    "neutral": score,
                    "compound": 0.0,
                    "method": "transformers"
                }
        except Exception as e:
            # Fall back to VADER or basic sentiment analysis
            logger.warning(f"Error using transformers: {str(e)}. Falling back to VADER.")
            return SentimentAnalyzer.analyze_sentiment_vader(text)


class TextClassifier:
    """
    Provides text classification capabilities.
    
    This class contains methods for classifying text into predefined
    categories using various machine learning techniques.
    """
    
    @staticmethod
    def classify_text_transformers(
        text: str,
        task: str = "text-classification"
    ) -> Dict[str, Any]:
        """
        Classify text using Hugging Face Transformers.
        
        Args:
            text: Text to classify
            task: Classification task (text-classification, zero-shot-classification)
            
        Returns:
            Dictionary containing classification results
        """
        if not TRANSFORMERS_AVAILABLE:
            return {
                "error": "transformers is required for text classification",
                "classifications": []
            }
        
        try:
            if task == "text-classification":
                # Create classification pipeline
                classifier = pipeline("text-classification")
                
                # Classify text
                result = classifier(text)
                
                return {
                    "classifications": [
                        {
                            "label": item["label"],
                            "score": float(item["score"])
                        }
                        for item in result
                    ],
                    "method": "transformers"
                }
            
            elif task == "zero-shot-classification":
                # Create zero-shot classification pipeline
                classifier = pipeline("zero-shot-classification")
                
                # Define candidate labels
                candidate_labels = [
                    "business", "technology", "politics", "sports",
                    "entertainment", "health", "science", "education"
                ]
                
                # Classify text
                result = classifier(text, candidate_labels)
                
                return {
                    "classifications": [
                        {
                            "label": label,
                            "score": float(score)
                        }
                        for label, score in zip(result["labels"], result["scores"])
                    ],
                    "method": "zero-shot"
                }
            
            else:
                return {
                    "error": f"Unsupported classification task: {task}",
                    "classifications": []
                }
        
        except Exception as e:
            return {
                "error": f"Error classifying text: {str(e)}",
                "classifications": []
            }
    
    @staticmethod
    def classify_text_sklearn(
        text: str,
        model_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify text using a pre-trained scikit-learn model.
        
        Args:
            text: Text to classify
            model_path: Path to the pre-trained model
            
        Returns:
            Dictionary containing classification results
        """
        if not SKLEARN_AVAILABLE:
            return {
                "error": "scikit-learn is required for text classification",
                "classifications": []
            }
        
        try:
            import joblib
            
            if model_path is None:
                return {
                    "error": "Model path not provided",
                    "classifications": []
                }
            
            # Load model and vectorizer
            model_data = joblib.load(model_path)
            model = model_data["model"]
            vectorizer = model_data["vectorizer"]
            classes = model_data["classes"]
            
            # Preprocess text
            preprocessed_text = TopicModeler.preprocess_text(text)
            
            # Vectorize text
            X = vectorizer.transform([preprocessed_text])
            
            # Predict probabilities
            probas = model.predict_proba(X)[0]
            
            # Create classification results
            classifications = [
                {
                    "label": str(classes[i]),
                    "score": float(proba)
                }
                for i, proba in enumerate(probas)
            ]
            
            # Sort by score in descending order
            classifications.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "classifications": classifications,
                "method": "sklearn"
            }
        
        except Exception as e:
            return {
                "error": f"Error classifying text: {str(e)}",
                "classifications": []
            }


def analyze_text_content(text: str) -> Dict[str, Any]:
    """
    Perform comprehensive text analysis on content.
    
    Args:
        text: Text content to analyze
        
    Returns:
        Dictionary containing comprehensive text analysis results
    """
    results = {}
    
    # Basic text statistics
    word_count = len(re.findall(r'\b\w+\b', text))
    sentence_count = len(re.split(r'[.!?]+', text))
    results["statistics"] = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "character_count": len(text),
        "average_word_length": sum(len(word) for word in re.findall(r'\b\w+\b', text)) / word_count if word_count > 0 else 0,
        "average_sentence_length": word_count / sentence_count if sentence_count > 0 else 0
    }
    
    # Sentiment analysis
    results["sentiment"] = SentimentAnalyzer.analyze_sentiment_vader(text)
    
    # Entity recognition
    if SPACY_AVAILABLE:
        results["entities"] = EntityRecognizer.extract_entities_spacy(text)
    elif NLTK_AVAILABLE:
        results["entities"] = EntityRecognizer.extract_entities_nltk(text)
    
    # Topic modeling
    if word_count > 20:
        results["topics"] = TopicModeler.extract_topics_nmf([text])
    
    # Text classification
    if TRANSFORMERS_AVAILABLE:
        results["classification"] = TextClassifier.classify_text_transformers(
            text, task="zero-shot-classification"
        )
    
    return results