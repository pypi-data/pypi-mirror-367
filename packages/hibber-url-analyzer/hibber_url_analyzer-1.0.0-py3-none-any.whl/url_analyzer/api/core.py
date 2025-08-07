"""
Core API implementation for URL Analyzer.

This module provides the main API implementation for programmatic access
to URL Analyzer functionality. It serves as the entry point for external
applications to integrate with URL Analyzer.
"""

import concurrent.futures
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from urllib.parse import urlparse, parse_qs

from url_analyzer.api.models import (
    AnalysisRequest, AnalysisResult, BatchAnalysisResult, 
    APIResponse, URLMetadata, ContentAnalysis, APIVersion
)
from url_analyzer.application.use_cases import (
    ClassifyURLUseCase, AnalyzeURLContentUseCase, BatchAnalyzeURLsUseCase
)
from url_analyzer.utils.errors import URLAnalyzerError, APIError, APIAuthenticationError, APIRateLimitError
from url_analyzer.config.manager import (
    load_config, get_max_workers, get_request_timeout
)
from url_analyzer.domain.entities import URLAnalysisResult
from url_analyzer.api.infrastructure import (
    URLRepositoryImpl, URLClassificationServiceImpl, URLContentAnalysisServiceImpl,
    CacheServiceImpl, LoggingServiceImpl
)
from url_analyzer.api.security import (
    APIKeyManager, RateLimiter, RequestValidator, AuditLogger, CORSHandler,
    require_api_key, rate_limit, validate_request, audit_log_request
)

# Configure logger
logger = logging.getLogger(__name__)


class URLAnalyzerAPI:
    """
    Main API class for URL Analyzer.
    
    This class provides methods for programmatic access to URL Analyzer
    functionality. It handles single and batch URL analysis, configuration
    management, and error handling.
    
    Args:
        config_path: Optional path to a custom configuration file
        max_workers: Maximum number of concurrent workers for batch processing
        timeout: Request timeout in seconds
    """
    
    def __init__(
        self, 
        config_path: Optional[str] = None,
        max_workers: Optional[int] = None,
        timeout: Optional[int] = None
    ):
        """Initialize the API with optional custom configuration."""
        self.config = load_config(config_path) if config_path else load_config()
        self.max_workers = max_workers or get_max_workers(self.config)
        self.timeout = timeout or get_request_timeout(self.config)
        self.version = APIVersion.V1
        
        # Initialize services
        self.logging_service = LoggingServiceImpl()
        self.url_repository = URLRepositoryImpl()
        self.classification_service = URLClassificationServiceImpl(self.config)
        self.content_analysis_service = URLContentAnalysisServiceImpl()
        self.cache_service = CacheServiceImpl()
        
        # Initialize security services
        self.api_key_manager = APIKeyManager(config_path)
        self.rate_limiter = RateLimiter(config_path)
        self.request_validator = RequestValidator(config_path)
        self.audit_logger = AuditLogger(config_path)
        self.cors_handler = CORSHandler(config_path)
        
        # Initialize use cases
        self.classify_url_use_case = ClassifyURLUseCase(
            url_repository=self.url_repository,
            classification_service=self.classification_service,
            cache_service=self.cache_service,
            logging_service=self.logging_service
        )
        
        self.analyze_content_use_case = AnalyzeURLContentUseCase(
            url_repository=self.url_repository,
            content_analysis_service=self.content_analysis_service,
            cache_service=self.cache_service,
            logging_service=self.logging_service
        )
        
        self.batch_analyze_use_case = BatchAnalyzeURLsUseCase(
            classify_url_use_case=self.classify_url_use_case,
            analyze_url_content_use_case=self.analyze_content_use_case,
            logging_service=self.logging_service
        )
        
        logger.debug(
            "Initialized URLAnalyzerAPI with max_workers=%d, timeout=%d",
            self.max_workers, self.timeout
        )
    
    @require_api_key
    @rate_limit
    @validate_request(
        required_params=["url"],
        optional_params=["include_content", "include_summary", "timeout", "custom_patterns"]
    )
    @audit_log_request(endpoint="/analyze_url", method="POST")
    def analyze_url(self, url: str, **kwargs) -> APIResponse:
        """
        Analyze a single URL.
        
        This method analyzes a single URL and returns the analysis result.
        
        Args:
            url: The URL to analyze
            **kwargs: Additional options for analysis
                api_key: API key for authentication
                client_ip: Client IP address for rate limiting
                include_content: Whether to fetch and analyze page content
                include_summary: Whether to generate a summary of the URL content
                timeout: Request timeout in seconds
                custom_patterns: Optional custom patterns to use for classification
        
        Returns:
            APIResponse containing the analysis result
        
        Raises:
            APIAuthenticationError: If the API key is invalid
            APIRateLimitError: If the rate limit is exceeded
            APIError: If the request is invalid
        """
        try:
            # Create a request with a single URL
            request = AnalysisRequest(
                urls=[url],
                include_content=kwargs.get('include_content', False),
                include_summary=kwargs.get('include_summary', False),
                timeout=kwargs.get('timeout', self.timeout),
                max_workers=1,  # Single URL, so only one worker needed
                custom_patterns=kwargs.get('custom_patterns')
            )
            
            # Perform the analysis
            start_time = time.time()
            result = self._analyze_single_url(url, request)
            execution_time = time.time() - start_time
            
            logger.info(
                "Analyzed URL %s in %.2f seconds (category: %s)",
                url, execution_time, result.category or "unknown"
            )
            
            # Get rate limit info if available
            rate_limit_info = kwargs.get('rate_limit_info', {})
            
            # Create response with rate limit headers
            response = APIResponse(
                success=result.success,
                data=result,
                version=self.version
            )
            
            # Add rate limit headers if available
            if rate_limit_info:
                response.headers = {
                    "X-RateLimit-Limit": str(rate_limit_info.get("limit", "")),
                    "X-RateLimit-Remaining": str(rate_limit_info.get("remaining", "")),
                    "X-RateLimit-Reset": str(rate_limit_info.get("reset", ""))
                }
            
            # Add CORS headers if origin is provided
            origin = kwargs.get('origin')
            if origin:
                cors_headers = self.cors_handler.get_cors_headers(origin)
                if response.headers:
                    response.headers.update(cors_headers)
                else:
                    response.headers = cors_headers
            
            return response
            
        except URLAnalyzerError as e:
            logger.error("Error analyzing URL %s: %s", url, str(e))
            return APIResponse(
                success=False,
                error=str(e),
                version=self.version
            )
        except Exception as e:
            logger.exception("Unexpected error analyzing URL %s", url)
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                version=self.version
            )
    
    @require_api_key
    @rate_limit
    @validate_request(
        required_params=["urls"],
        optional_params=["include_content", "include_summary", "timeout", "max_workers", "custom_patterns"],
        max_urls=100
    )
    @audit_log_request(endpoint="/analyze_urls", method="POST")
    def analyze_urls(self, urls: List[str], **kwargs) -> APIResponse:
        """
        Analyze multiple URLs in batch.
        
        This method analyzes multiple URLs in parallel and returns the batch result.
        
        Args:
            urls: List of URLs to analyze
            **kwargs: Additional options for analysis
                api_key: API key for authentication
                client_ip: Client IP address for rate limiting
                include_content: Whether to fetch and analyze page content
                include_summary: Whether to generate a summary of the URL content
                timeout: Request timeout in seconds
                max_workers: Maximum number of concurrent workers
                custom_patterns: Optional custom patterns to use for classification
        
        Returns:
            APIResponse containing the batch analysis result
            
        Raises:
            APIAuthenticationError: If the API key is invalid
            APIRateLimitError: If the rate limit is exceeded
            APIError: If the request is invalid
        """
        try:
            # Create a request with multiple URLs
            request = AnalysisRequest(
                urls=urls,
                include_content=kwargs.get('include_content', False),
                include_summary=kwargs.get('include_summary', False),
                timeout=kwargs.get('timeout', self.timeout),
                max_workers=kwargs.get('max_workers', self.max_workers),
                custom_patterns=kwargs.get('custom_patterns')
            )
            
            # Perform the batch analysis
            start_time = time.time()
            results = self._analyze_multiple_urls(urls, request)
            execution_time = time.time() - start_time
            
            # Count successful and failed analyses
            successful_urls = sum(1 for result in results if result.success)
            failed_urls = len(results) - successful_urls
            
            logger.info(
                "Analyzed %d URLs in %.2f seconds (successful: %d, failed: %d)",
                len(urls), execution_time, successful_urls, failed_urls
            )
            
            # Create the batch result
            batch_result = BatchAnalysisResult(
                results=results,
                total_urls=len(urls),
                successful_urls=successful_urls,
                failed_urls=failed_urls,
                execution_time=execution_time
            )
            
            # Get rate limit info if available
            rate_limit_info = kwargs.get('rate_limit_info', {})
            
            # Create response with rate limit headers
            response = APIResponse(
                success=True,
                data=batch_result,
                version=self.version
            )
            
            # Add rate limit headers if available
            if rate_limit_info:
                response.headers = {
                    "X-RateLimit-Limit": str(rate_limit_info.get("limit", "")),
                    "X-RateLimit-Remaining": str(rate_limit_info.get("remaining", "")),
                    "X-RateLimit-Reset": str(rate_limit_info.get("reset", ""))
                }
            
            # Add CORS headers if origin is provided
            origin = kwargs.get('origin')
            if origin:
                cors_headers = self.cors_handler.get_cors_headers(origin)
                if response.headers:
                    response.headers.update(cors_headers)
                else:
                    response.headers = cors_headers
            
            return response
            
        except URLAnalyzerError as e:
            logger.error("Error analyzing URLs: %s", str(e))
            return APIResponse(
                success=False,
                error=str(e),
                version=self.version
            )
        except Exception as e:
            logger.exception("Unexpected error analyzing URLs")
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                version=self.version
            )
    
    def _analyze_single_url(self, url: str, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze a single URL.
        
        This internal method performs the actual analysis of a single URL.
        
        Args:
            url: The URL to analyze
            request: The analysis request
        
        Returns:
            AnalysisResult containing the analysis result
        """
        try:
            # Extract metadata from the URL
            metadata = self._extract_url_metadata(url)
            
            # Use the classify URL use case
            if request.custom_patterns:
                # If custom patterns are provided, update the classification service
                self.classification_service.update_patterns(request.custom_patterns)
                
            # Execute the classify URL use case
            classification_result = self.classify_url_use_case.execute(url)
            
            # Initialize the result
            result = AnalysisResult(
                url=url,
                category=classification_result.category,
                is_sensitive=classification_result.is_sensitive,
                metadata=metadata,
                subcategory=classification_result.subcategory
            )
            
            # Fetch and analyze content if requested
            if request.include_content:
                # Execute the analyze content use case
                content_result = self.analyze_content_use_case.execute(url)
                
                # Extract content metadata
                content_metadata = content_result.content_metadata
                
                if content_metadata:
                    # Set status code if available
                    if 'status_code' in content_metadata:
                        result.status_code = content_metadata.get('status_code')
                    
                    # Create content analysis object
                    result.content = ContentAnalysis(
                        title=content_metadata.get('title'),
                        description=content_metadata.get('description'),
                        keywords=content_metadata.get('keywords', []),
                        text_length=content_metadata.get('text_length', 0),
                        links_count=content_metadata.get('links_count', 0),
                        images_count=content_metadata.get('images_count', 0),
                        summary=content_metadata.get('summary')
                    )
            
            return result
            
        except URLAnalyzerError as e:
            # Create a result with error information
            return AnalysisResult(
                url=url,
                error=str(e)
            )
        except Exception as e:
            # Create a result with error information
            return AnalysisResult(
                url=url,
                error=f"Unexpected error: {str(e)}"
            )
    
    def _analyze_multiple_urls(
        self, urls: List[str], request: AnalysisRequest
    ) -> List[AnalysisResult]:
        """
        Analyze multiple URLs in parallel.
        
        This internal method performs the actual analysis of multiple URLs.
        
        Args:
            urls: List of URLs to analyze
            request: The analysis request
        
        Returns:
            List of AnalysisResult containing the analysis results
        """
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=request.max_workers
        ) as executor:
            # Submit all URLs for analysis
            future_to_url = {
                executor.submit(self._analyze_single_url, url, request): url
                for url in urls
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Create a result with error information
                    results.append(AnalysisResult(
                        url=url,
                        error=f"Unexpected error: {str(e)}"
                    ))
        
        return results
    
    def _extract_url_metadata(self, url: str) -> URLMetadata:
        """
        Extract metadata from a URL.
        
        This internal method extracts metadata from a URL.
        
        Args:
            url: The URL to extract metadata from
        
        Returns:
            URLMetadata containing the extracted metadata
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Extract query parameters
            query_params = {}
            if parsed_url.query:
                query_dict = parse_qs(parsed_url.query)
                query_params = {k: v[0] if len(v) == 1 else v for k, v in query_dict.items()}
            
            # Create and return the metadata
            return URLMetadata(
                domain=parsed_url.netloc,
                path=parsed_url.path,
                query_params=query_params,
                fragment=parsed_url.fragment if parsed_url.fragment else None,
                protocol=parsed_url.scheme if parsed_url.scheme else "https",
                port=parsed_url.port
            )
        except Exception as e:
            logger.warning("Error extracting metadata from URL %s: %s", url, str(e))
            # Return basic metadata with just the URL as domain
            return URLMetadata(
                domain=url,
                path="/"
            )
    
    def get_version(self) -> APIVersion:
        """
        Get the API version.
        
        Returns:
            The current API version
        """
        return self.version
    
    def set_version(self, version: APIVersion) -> None:
        """
        Set the API version.
        
        Args:
            version: The API version to use
        """
        self.version = version
        logger.debug("Set API version to %s", str(version))
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            The current configuration dictionary
        """
        return self.config
        
    @require_api_key
    @audit_log_request(endpoint="/create_api_key", method="POST")
    def create_api_key(self, user_id: str, role: str = "basic", permissions: Optional[List[str]] = None, **kwargs) -> APIResponse:
        """
        Create a new API key.
        
        Args:
            user_id: Identifier for the user or application
            role: Role for the API key (basic, premium, unlimited)
            permissions: List of specific permissions for the API key
            **kwargs: Additional options
                api_key: Admin API key for authentication
                client_ip: Client IP address for audit logging
                
        Returns:
            APIResponse containing the newly created API key
            
        Raises:
            APIAuthenticationError: If the admin API key is invalid
            APIError: If the request is invalid
        """
        try:
            # Verify that the caller has admin permissions
            api_key_metadata = kwargs.get('api_key_metadata', {})
            if "admin" not in api_key_metadata.get("permissions", []):
                raise APIAuthenticationError("Admin permissions required to create API keys")
            
            # Create the API key
            new_api_key = self.api_key_manager.create_api_key(
                user_id=user_id,
                role=role,
                permissions=permissions
            )
            
            # Return the response
            return APIResponse(
                success=True,
                data={"api_key": new_api_key},
                version=self.version
            )
            
        except URLAnalyzerError as e:
            logger.error("Error creating API key for user %s: %s", user_id, str(e))
            return APIResponse(
                success=False,
                error=str(e),
                version=self.version
            )
        except Exception as e:
            logger.exception("Unexpected error creating API key for user %s", user_id)
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                version=self.version
            )
    
    @require_api_key
    @audit_log_request(endpoint="/revoke_api_key", method="POST")
    def revoke_api_key(self, api_key_to_revoke: str, **kwargs) -> APIResponse:
        """
        Revoke an API key.
        
        Args:
            api_key_to_revoke: The API key to revoke
            **kwargs: Additional options
                api_key: Admin API key for authentication
                client_ip: Client IP address for audit logging
                
        Returns:
            APIResponse indicating success or failure
            
        Raises:
            APIAuthenticationError: If the admin API key is invalid
            APIError: If the request is invalid
        """
        try:
            # Verify that the caller has admin permissions or is revoking their own key
            api_key_metadata = kwargs.get('api_key_metadata', {})
            caller_user_id = api_key_metadata.get("user_id")
            
            # Get metadata for the key to be revoked
            try:
                key_to_revoke_metadata = self.api_key_manager.validate_api_key(api_key_to_revoke)
                key_owner_id = key_to_revoke_metadata.get("user_id")
            except APIAuthenticationError:
                raise APIError("Invalid API key to revoke")
            
            # Check if caller has permission to revoke this key
            has_admin_permission = "admin" in api_key_metadata.get("permissions", [])
            is_own_key = caller_user_id == key_owner_id
            
            if not (has_admin_permission or is_own_key):
                raise APIAuthenticationError("Permission denied: Cannot revoke another user's API key")
            
            # Revoke the API key
            self.api_key_manager.revoke_api_key(api_key_to_revoke)
            
            # Return the response
            return APIResponse(
                success=True,
                data={"message": "API key revoked successfully"},
                version=self.version
            )
            
        except URLAnalyzerError as e:
            logger.error("Error revoking API key: %s", str(e))
            return APIResponse(
                success=False,
                error=str(e),
                version=self.version
            )
        except Exception as e:
            logger.exception("Unexpected error revoking API key")
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                version=self.version
            )
    
    @require_api_key
    @audit_log_request(endpoint="/validate_api_key", method="POST")
    def validate_api_key(self, api_key_to_validate: str, **kwargs) -> APIResponse:
        """
        Validate an API key and return its metadata.
        
        Args:
            api_key_to_validate: The API key to validate
            **kwargs: Additional options
                api_key: API key for authentication
                client_ip: Client IP address for audit logging
                
        Returns:
            APIResponse containing the API key metadata
            
        Raises:
            APIAuthenticationError: If the caller's API key is invalid
            APIError: If the request is invalid
        """
        try:
            # Validate the API key
            try:
                api_key_metadata = self.api_key_manager.validate_api_key(api_key_to_validate)
            except APIAuthenticationError:
                return APIResponse(
                    success=False,
                    data={"valid": False},
                    version=self.version
                )
            
            # Return the response with limited metadata for security
            return APIResponse(
                success=True,
                data={
                    "valid": True,
                    "user_id": api_key_metadata.get("user_id"),
                    "role": api_key_metadata.get("role"),
                    "created_at": api_key_metadata.get("created_at")
                },
                version=self.version
            )
            
        except URLAnalyzerError as e:
            logger.error("Error validating API key: %s", str(e))
            return APIResponse(
                success=False,
                error=str(e),
                version=self.version
            )
        except Exception as e:
            logger.exception("Unexpected error validating API key")
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                version=self.version
            )
    
    @require_api_key
    @audit_log_request(endpoint="/get_user_api_keys", method="GET")
    def get_user_api_keys(self, user_id: str, **kwargs) -> APIResponse:
        """
        Get all API keys for a user.
        
        Args:
            user_id: The user ID to get API keys for
            **kwargs: Additional options
                api_key: API key for authentication
                client_ip: Client IP address for audit logging
                
        Returns:
            APIResponse containing the list of API keys for the user
            
        Raises:
            APIAuthenticationError: If the API key is invalid
            APIError: If the request is invalid
        """
        try:
            # Verify that the caller has admin permissions or is requesting their own keys
            api_key_metadata = kwargs.get('api_key_metadata', {})
            caller_user_id = api_key_metadata.get("user_id")
            
            # Check if caller has permission to get keys for this user
            has_admin_permission = "admin" in api_key_metadata.get("permissions", [])
            is_own_keys = caller_user_id == user_id
            
            if not (has_admin_permission or is_own_keys):
                raise APIAuthenticationError("Permission denied: Cannot access another user's API keys")
            
            # Get the API keys
            api_keys = self.api_key_manager.get_user_api_keys(user_id)
            
            # Return the response
            return APIResponse(
                success=True,
                data={"api_keys": api_keys},
                version=self.version
            )
            
        except URLAnalyzerError as e:
            logger.error("Error getting API keys for user %s: %s", user_id, str(e))
            return APIResponse(
                success=False,
                error=str(e),
                version=self.version
            )
        except Exception as e:
            logger.exception("Unexpected error getting API keys for user %s", user_id)
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                version=self.version
            )