"""
Social Media URL Classifier Plugin

This plugin provides a custom URL classifier for social media URLs.
It demonstrates how to create a custom URL classifier plugin for the URL Analyzer.
"""

import re
from typing import Dict, Any, Tuple, Optional

from url_analyzer.plugins.interface import URLClassifierPlugin
from url_analyzer.core.strategies import ClassificationStrategy


class SocialMediaClassificationStrategy(ClassificationStrategy):
    """
    Custom classification strategy for social media URLs.
    
    This strategy classifies URLs based on social media patterns.
    """
    
    def __init__(self):
        """
        Initialize the social media classification strategy.
        """
        # Compile regex patterns for social media platforms
        self.social_media_patterns = {
            'Facebook': re.compile(r'facebook\.com|fb\.com|fbcdn\.net', re.IGNORECASE),
            'Twitter': re.compile(r'twitter\.com|t\.co|x\.com', re.IGNORECASE),
            'Instagram': re.compile(r'instagram\.com|instagr\.am', re.IGNORECASE),
            'LinkedIn': re.compile(r'linkedin\.com|lnkd\.in', re.IGNORECASE),
            'YouTube': re.compile(r'youtube\.com|youtu\.be', re.IGNORECASE),
            'TikTok': re.compile(r'tiktok\.com|tiktokcdn\.com', re.IGNORECASE),
            'Pinterest': re.compile(r'pinterest\.com|pin\.it', re.IGNORECASE),
            'Reddit': re.compile(r'reddit\.com|redd\.it', re.IGNORECASE),
            'Snapchat': re.compile(r'snapchat\.com|snap\.com', re.IGNORECASE),
            'WhatsApp': re.compile(r'whatsapp\.com|wa\.me', re.IGNORECASE),
        }
        
        # Compile regex pattern for sensitive content
        self.sensitive_pattern = re.compile(
            r'nsfw|adult|xxx|porn|sex|gambling|betting|casino|drugs|alcohol',
            re.IGNORECASE
        )
    
    def classify_url(self, url: str) -> Tuple[str, bool]:
        """
        Classify a URL using social media patterns.
        
        Args:
            url: URL to classify
            
        Returns:
            Tuple of (category, is_sensitive)
        """
        if not isinstance(url, str) or not url.strip():
            return 'Empty or Invalid', False
        
        url_lower = url.lower().strip()
        is_sensitive = bool(self.sensitive_pattern.search(url_lower))
        
        # Check if the URL matches any social media platform
        for platform, pattern in self.social_media_patterns.items():
            if pattern.search(url_lower):
                return f'Social Media - {platform}', is_sensitive
        
        # If no match, return 'Other'
        return 'Other', is_sensitive
    
    def get_name(self) -> str:
        """
        Get the name of this strategy.
        
        Returns:
            Strategy name
        """
        return "Social Media Classification"


class SocialMediaClassifierPlugin(URLClassifierPlugin):
    """
    URL classifier plugin for social media URLs.
    
    This plugin provides a custom URL classifier that categorizes URLs
    based on social media platforms.
    """
    
    def __init__(self):
        """
        Initialize the social media classifier plugin.
        """
        self._strategy = None
        self._initialized = False
    
    def get_name(self) -> str:
        """
        Returns the name of the plugin.
        
        Returns:
            String name of the plugin
        """
        return "Social Media Classifier"
    
    def get_version(self) -> str:
        """
        Returns the version of the plugin.
        
        Returns:
            String version of the plugin
        """
        return "1.0.0"
    
    def get_description(self) -> str:
        """
        Returns a description of the plugin.
        
        Returns:
            String description of the plugin
        """
        return "Classifies URLs based on social media platforms"
    
    def get_author(self) -> str:
        """
        Returns the author of the plugin.
        
        Returns:
            String author of the plugin
        """
        return "URL Analyzer Team"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initializes the plugin with the given configuration.
        
        Args:
            config: Dictionary containing configuration values
            
        Returns:
            Boolean indicating whether initialization was successful
        """
        try:
            self._strategy = SocialMediaClassificationStrategy()
            self._initialized = True
            return True
        except Exception as e:
            print(f"Error initializing Social Media Classifier plugin: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Performs cleanup when the plugin is being unloaded.
        
        Returns:
            Boolean indicating whether shutdown was successful
        """
        self._strategy = None
        self._initialized = False
        return True
    
    def get_strategy(self) -> Optional[ClassificationStrategy]:
        """
        Returns the classification strategy implemented by this plugin.
        
        Returns:
            ClassificationStrategy instance or None if not initialized
        """
        return self._strategy if self._initialized else None
    
    def classify_url(self, url: str) -> Tuple[str, bool]:
        """
        Classifies a URL using the plugin's strategy.
        
        Args:
            url: URL to classify
            
        Returns:
            Tuple of (category, is_sensitive)
        """
        if not self._initialized or self._strategy is None:
            return 'Not Initialized', False
        
        return self._strategy.classify_url(url)