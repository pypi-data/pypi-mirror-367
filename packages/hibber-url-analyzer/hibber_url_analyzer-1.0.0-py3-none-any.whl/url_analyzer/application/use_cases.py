"""
Application Layer Use Cases

This module defines use cases for the URL Analyzer application.
Use cases represent the application-specific business rules and orchestrate
the flow of data to and from the domain layer.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set

from url_analyzer.domain.entities import URL, URLAnalysisResult, BatchAnalysisResult
from url_analyzer.domain.value_objects import URLClassificationRule, DomainName
from url_analyzer.application.interfaces import (
    URLRepository, URLClassificationService, URLContentAnalysisService,
    ReportingService, CacheService, FileStorageService, LoggingService
)


class ClassifyURLUseCase:
    """
    Use case for classifying a URL.
    
    This use case orchestrates the classification of a URL, including
    creating a domain entity, classifying it, and storing the result.
    """
    
    def __init__(
        self,
        url_repository: URLRepository,
        classification_service: URLClassificationService,
        cache_service: CacheService,
        logging_service: LoggingService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            url_repository: Repository for storing URL entities
            classification_service: Service for classifying URLs
            cache_service: Service for caching results
            logging_service: Service for logging
        """
        self.url_repository = url_repository
        self.classification_service = classification_service
        self.cache_service = cache_service
        self.logging_service = logging_service
    
    def execute(self, url_string: str) -> URLAnalysisResult:
        """
        Execute the use case.
        
        Args:
            url_string: The URL to classify
            
        Returns:
            The analysis result
        """
        self.logging_service.info(f"Classifying URL: {url_string}")
        
        # Check cache first
        cached_result = self.cache_service.get(url_string)
        if cached_result:
            self.logging_service.debug(f"Using cached result for URL: {url_string}")
            # Convert cached result to domain entity
            url = URL(
                url=url_string,
                base_domain=cached_result.get('base_domain'),
                category=cached_result.get('category', 'UNKNOWN'),
                sensitivity_level=cached_result.get('sensitivity_level', 'LOW'),
                is_malicious=cached_result.get('is_malicious', False),
                metadata=cached_result.get('metadata', {}),
                last_analyzed=datetime.fromisoformat(cached_result.get('last_analyzed', datetime.now().isoformat()))
            )
            result = URLAnalysisResult(
                url=url,
                classification_successful=True,
                content_analysis_successful=False
            )
            return result
        
        # Get existing URL entity or create a new one
        url_entity = self.url_repository.get_by_url(url_string)
        if not url_entity:
            try:
                # Extract base domain
                domain_name = DomainName.from_url(url_string)
                base_domain = domain_name.value
            except ValueError:
                base_domain = None
                
            url_entity = URL(url=url_string, base_domain=base_domain)
        
        # Create analysis result
        result = URLAnalysisResult(url=url_entity)
        
        try:
            # Classify the URL
            category, is_sensitive = self.classification_service.classify(url_string)
            
            # Update the URL entity
            url_entity.update_category(category)
            url_entity.is_malicious = category.lower() == 'malicious'
            
            # Mark classification as complete
            result.mark_classification_complete()
            
            # Save the URL entity
            self.url_repository.save(url_entity)
            
            # Cache the result
            self.cache_service.set(url_string, {
                'base_domain': url_entity.base_domain,
                'category': category,
                'sensitivity_level': 'HIGH' if is_sensitive else 'LOW',
                'is_malicious': url_entity.is_malicious,
                'metadata': url_entity.metadata,
                'last_analyzed': url_entity.last_analyzed.isoformat() if url_entity.last_analyzed else datetime.now().isoformat()
            })
            
            self.logging_service.info(f"URL classified successfully: {url_string} -> {category}")
        except Exception as e:
            error_message = f"Error classifying URL {url_string}: {str(e)}"
            self.logging_service.error(error_message)
            result.add_error(error_message)
        
        return result


class AnalyzeURLContentUseCase:
    """
    Use case for analyzing URL content.
    
    This use case orchestrates the analysis of URL content, including
    fetching the content, analyzing it, and storing the result.
    """
    
    def __init__(
        self,
        url_repository: URLRepository,
        content_analysis_service: URLContentAnalysisService,
        cache_service: CacheService,
        logging_service: LoggingService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            url_repository: Repository for storing URL entities
            content_analysis_service: Service for analyzing URL content
            cache_service: Service for caching results
            logging_service: Service for logging
        """
        self.url_repository = url_repository
        self.content_analysis_service = content_analysis_service
        self.cache_service = cache_service
        self.logging_service = logging_service
    
    def execute(self, url_string: str) -> URLAnalysisResult:
        """
        Execute the use case.
        
        Args:
            url_string: The URL to analyze
            
        Returns:
            The analysis result
        """
        self.logging_service.info(f"Analyzing content for URL: {url_string}")
        
        # Get existing URL entity or create a new one
        url_entity = self.url_repository.get_by_url(url_string)
        if not url_entity:
            try:
                # Extract base domain
                domain_name = DomainName.from_url(url_string)
                base_domain = domain_name.value
            except ValueError:
                base_domain = None
                
            url_entity = URL(url=url_string, base_domain=base_domain)
        
        # Create analysis result
        result = URLAnalysisResult(url=url_entity)
        
        try:
            # Analyze the URL content
            content_metadata = self.content_analysis_service.analyze_content(url_string)
            
            # Update the URL entity with metadata
            for key, value in content_metadata.items():
                url_entity.add_metadata(key, value)
            
            # Add content metadata to the result
            for key, value in content_metadata.items():
                result.add_content_metadata(key, value)
            
            # Mark content analysis as complete
            result.mark_content_analysis_complete()
            
            # Save the URL entity
            self.url_repository.save(url_entity)
            
            self.logging_service.info(f"URL content analyzed successfully: {url_string}")
        except Exception as e:
            error_message = f"Error analyzing URL content {url_string}: {str(e)}"
            self.logging_service.error(error_message)
            result.add_error(error_message)
        
        return result


class BatchAnalyzeURLsUseCase:
    """
    Use case for batch analyzing URLs.
    
    This use case orchestrates the batch analysis of URLs, including
    classification, content analysis, and generating a batch result.
    """
    
    def __init__(
        self,
        classify_url_use_case: ClassifyURLUseCase,
        analyze_url_content_use_case: AnalyzeURLContentUseCase,
        logging_service: LoggingService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            classify_url_use_case: Use case for classifying URLs
            analyze_url_content_use_case: Use case for analyzing URL content
            logging_service: Service for logging
        """
        self.classify_url_use_case = classify_url_use_case
        self.analyze_url_content_use_case = analyze_url_content_use_case
        self.logging_service = logging_service
    
    def execute(self, urls: List[str], analyze_content: bool = False) -> BatchAnalysisResult:
        """
        Execute the use case.
        
        Args:
            urls: The URLs to analyze
            analyze_content: Whether to analyze URL content
            
        Returns:
            The batch analysis result
        """
        self.logging_service.info(f"Batch analyzing {len(urls)} URLs")
        
        # Create batch result
        batch_result = BatchAnalysisResult(
            total_urls=len(urls),
            successful_analyses=0,
            failed_analyses=0
        )
        
        # Process each URL
        for url in urls:
            try:
                # Classify the URL
                classification_result = self.classify_url_use_case.execute(url)
                
                # Analyze content if requested
                if analyze_content and not classification_result.has_errors():
                    content_result = self.analyze_url_content_use_case.execute(url)
                    
                    # Merge results
                    classification_result.content_analysis_successful = content_result.content_analysis_successful
                    classification_result.content_metadata = content_result.content_metadata
                    
                    # Merge errors
                    for error in content_result.error_messages:
                        classification_result.add_error(error)
                
                # Add result to batch
                batch_result.add_result(classification_result)
                
                # Update success/failure counts
                if classification_result.has_errors():
                    batch_result.failed_analyses += 1
                else:
                    batch_result.successful_analyses += 1
                
            except Exception as e:
                error_message = f"Error processing URL {url}: {str(e)}"
                self.logging_service.error(error_message)
                batch_result.failed_analyses += 1
        
        # Mark batch analysis as complete
        batch_result.complete_analysis()
        
        self.logging_service.info(
            f"Batch analysis completed: {batch_result.successful_analyses} successful, "
            f"{batch_result.failed_analyses} failed, "
            f"took {batch_result.get_processing_time():.2f} seconds"
        )
        
        return batch_result


class GenerateReportUseCase:
    """
    Use case for generating a report.
    
    This use case orchestrates the generation of a report from batch analysis results.
    """
    
    def __init__(
        self,
        reporting_service: ReportingService,
        file_storage_service: FileStorageService,
        logging_service: LoggingService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            reporting_service: Service for generating reports
            file_storage_service: Service for storing files
            logging_service: Service for logging
        """
        self.reporting_service = reporting_service
        self.file_storage_service = file_storage_service
        self.logging_service = logging_service
    
    def execute(
        self,
        batch_result: BatchAnalysisResult,
        output_path: str,
        format: str = 'html'
    ) -> str:
        """
        Execute the use case.
        
        Args:
            batch_result: The batch analysis result to include in the report
            output_path: The path to write the report to
            format: The report format (html, csv, json, pdf)
            
        Returns:
            The path to the generated report
        """
        self.logging_service.info(f"Generating {format} report at {output_path}")
        
        try:
            # Generate the report based on the requested format
            if format.lower() == 'html':
                report_path = self.reporting_service.generate_html_report(batch_result, output_path)
            elif format.lower() == 'csv':
                report_path = self.reporting_service.generate_csv_report(batch_result, output_path)
            elif format.lower() == 'json':
                report_path = self.reporting_service.generate_json_report(batch_result, output_path)
            elif format.lower() == 'pdf':
                report_path = self.reporting_service.generate_pdf_report(batch_result, output_path)
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            self.logging_service.info(f"Report generated successfully at {report_path}")
            return report_path
        except Exception as e:
            error_message = f"Error generating report: {str(e)}"
            self.logging_service.error(error_message)
            raise RuntimeError(error_message) from e


class AddClassificationRuleUseCase:
    """
    Use case for adding a classification rule.
    
    This use case orchestrates the addition of a classification rule.
    """
    
    def __init__(
        self,
        classification_service: URLClassificationService,
        logging_service: LoggingService
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            classification_service: Service for classifying URLs
            logging_service: Service for logging
        """
        self.classification_service = classification_service
        self.logging_service = logging_service
    
    def execute(self, rule: URLClassificationRule) -> None:
        """
        Execute the use case.
        
        Args:
            rule: The classification rule to add
        """
        self.logging_service.info(f"Adding classification rule: {rule.name}")
        
        try:
            # Add the rule
            self.classification_service.add_rule(rule)
            
            self.logging_service.info(f"Classification rule added successfully: {rule.name}")
        except Exception as e:
            error_message = f"Error adding classification rule {rule.name}: {str(e)}"
            self.logging_service.error(error_message)
            raise RuntimeError(error_message) from e