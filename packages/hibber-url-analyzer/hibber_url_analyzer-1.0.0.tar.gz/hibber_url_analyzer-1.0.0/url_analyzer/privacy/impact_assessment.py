"""
Privacy Impact Assessment Module

This module provides functionality for conducting privacy impact assessments,
supporting compliance with data privacy regulations and best practices.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PrivacyImpactAssessment:
    """
    Privacy Impact Assessment (PIA) for data processing activities.
    
    This class represents a privacy impact assessment, which evaluates the
    privacy risks associated with data processing activities.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        data_types: Optional[List[str]] = None,
        processing_purposes: Optional[List[str]] = None,
        data_subjects: Optional[List[str]] = None,
        assessment_date: Optional[datetime] = None
    ):
        """
        Initialize a privacy impact assessment.
        
        Args:
            name: Name of the assessment
            description: Description of the assessment
            data_types: Types of data being processed
            processing_purposes: Purposes for processing the data
            data_subjects: Categories of data subjects
            assessment_date: Date of the assessment
        """
        self.name = name
        self.description = description
        self.data_types = data_types or []
        self.processing_purposes = processing_purposes or []
        self.data_subjects = data_subjects or []
        self.assessment_date = assessment_date or datetime.now()
        self.risks: List[Dict[str, Any]] = []
        self.mitigations: List[Dict[str, Any]] = []
        self.recommendations: List[Dict[str, Any]] = []
        self.assessment_id = f"PIA-{self.assessment_date.strftime('%Y%m%d%H%M%S')}-{name.replace(' ', '-')}"
    
    def add_risk(
        self,
        name: str,
        description: str,
        severity: str,
        likelihood: str,
        impact: str,
        affected_data_types: Optional[List[str]] = None,
        affected_data_subjects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a privacy risk to the assessment.
        
        Args:
            name: Name of the risk
            description: Description of the risk
            severity: Severity of the risk (low, medium, high, critical)
            likelihood: Likelihood of the risk occurring (low, medium, high)
            impact: Impact if the risk occurs (low, medium, high, critical)
            affected_data_types: Types of data affected by the risk
            affected_data_subjects: Categories of data subjects affected by the risk
            
        Returns:
            Dictionary containing the risk information
        """
        # Create risk
        risk = {
            "risk_id": f"{self.assessment_id}-RISK-{len(self.risks) + 1}",
            "name": name,
            "description": description,
            "severity": severity,
            "likelihood": likelihood,
            "impact": impact,
            "affected_data_types": affected_data_types or [],
            "affected_data_subjects": affected_data_subjects or [],
            "added_date": datetime.now().isoformat()
        }
        
        # Add risk to risks list
        self.risks.append(risk)
        
        return risk
    
    def add_mitigation(
        self,
        name: str,
        description: str,
        risk_ids: Optional[List[str]] = None,
        implementation_status: str = "planned",
        implementation_date: Optional[datetime] = None,
        responsible_party: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a mitigation measure to the assessment.
        
        Args:
            name: Name of the mitigation
            description: Description of the mitigation
            risk_ids: IDs of risks this mitigation addresses
            implementation_status: Status of implementation (planned, in progress, implemented)
            implementation_date: Date of implementation
            responsible_party: Party responsible for implementing the mitigation
            
        Returns:
            Dictionary containing the mitigation information
        """
        # Create mitigation
        mitigation = {
            "mitigation_id": f"{self.assessment_id}-MIT-{len(self.mitigations) + 1}",
            "name": name,
            "description": description,
            "risk_ids": risk_ids or [],
            "implementation_status": implementation_status,
            "added_date": datetime.now().isoformat()
        }
        
        # Add implementation date if provided
        if implementation_date:
            mitigation["implementation_date"] = implementation_date.isoformat()
        
        # Add responsible party if provided
        if responsible_party:
            mitigation["responsible_party"] = responsible_party
        
        # Add mitigation to mitigations list
        self.mitigations.append(mitigation)
        
        return mitigation
    
    def add_recommendation(
        self,
        name: str,
        description: str,
        priority: str = "medium",
        risk_ids: Optional[List[str]] = None,
        implementation_status: str = "pending",
        responsible_party: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a recommendation to the assessment.
        
        Args:
            name: Name of the recommendation
            description: Description of the recommendation
            priority: Priority of the recommendation (low, medium, high, critical)
            risk_ids: IDs of risks this recommendation addresses
            implementation_status: Status of implementation (pending, in progress, implemented)
            responsible_party: Party responsible for implementing the recommendation
            
        Returns:
            Dictionary containing the recommendation information
        """
        # Create recommendation
        recommendation = {
            "recommendation_id": f"{self.assessment_id}-REC-{len(self.recommendations) + 1}",
            "name": name,
            "description": description,
            "priority": priority,
            "risk_ids": risk_ids or [],
            "implementation_status": implementation_status,
            "added_date": datetime.now().isoformat()
        }
        
        # Add responsible party if provided
        if responsible_party:
            recommendation["responsible_party"] = responsible_party
        
        # Add recommendation to recommendations list
        self.recommendations.append(recommendation)
        
        return recommendation
    
    def calculate_risk_score(self) -> Dict[str, Any]:
        """
        Calculate the overall risk score for the assessment.
        
        Returns:
            Dictionary containing risk score information
        """
        if not self.risks:
            return {
                "overall_score": 0,
                "risk_level": "none",
                "risk_count": 0,
                "risk_distribution": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
            }
        
        # Map severity and likelihood to numeric values
        severity_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        
        likelihood_map = {
            "low": 1,
            "medium": 2,
            "high": 3
        }
        
        # Calculate risk scores and distribution
        risk_scores = []
        risk_distribution = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for risk in self.risks:
            # Get severity and likelihood values
            severity = severity_map.get(risk["severity"].lower(), 1)
            likelihood = likelihood_map.get(risk["likelihood"].lower(), 1)
            
            # Calculate risk score
            risk_score = severity * likelihood
            risk_scores.append(risk_score)
            
            # Update risk distribution
            risk_distribution[risk["severity"].lower()] += 1
        
        # Calculate overall risk score
        overall_score = sum(risk_scores) / len(risk_scores)
        
        # Determine risk level
        if overall_score >= 9:
            risk_level = "critical"
        elif overall_score >= 6:
            risk_level = "high"
        elif overall_score >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "overall_score": overall_score,
            "risk_level": risk_level,
            "risk_count": len(self.risks),
            "risk_distribution": risk_distribution
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the assessment to a dictionary.
        
        Returns:
            Dictionary representation of the assessment
        """
        return {
            "assessment_id": self.assessment_id,
            "name": self.name,
            "description": self.description,
            "data_types": self.data_types,
            "processing_purposes": self.processing_purposes,
            "data_subjects": self.data_subjects,
            "assessment_date": self.assessment_date.isoformat(),
            "risks": self.risks,
            "mitigations": self.mitigations,
            "recommendations": self.recommendations,
            "risk_score": self.calculate_risk_score()
        }
    
    @classmethod
    def from_dict(cls, assessment_dict: Dict[str, Any]) -> 'PrivacyImpactAssessment':
        """
        Create an assessment from a dictionary.
        
        Args:
            assessment_dict: Dictionary representation of the assessment
            
        Returns:
            PrivacyImpactAssessment object
        """
        # Create assessment
        assessment = cls(
            name=assessment_dict["name"],
            description=assessment_dict.get("description", ""),
            data_types=assessment_dict.get("data_types", []),
            processing_purposes=assessment_dict.get("processing_purposes", []),
            data_subjects=assessment_dict.get("data_subjects", []),
            assessment_date=datetime.fromisoformat(assessment_dict["assessment_date"])
        )
        
        # Set assessment ID
        assessment.assessment_id = assessment_dict["assessment_id"]
        
        # Add risks
        assessment.risks = assessment_dict.get("risks", [])
        
        # Add mitigations
        assessment.mitigations = assessment_dict.get("mitigations", [])
        
        # Add recommendations
        assessment.recommendations = assessment_dict.get("recommendations", [])
        
        return assessment


class PrivacyImpactAssessmentManager:
    """
    Manager for privacy impact assessments.
    
    This class provides methods for managing multiple privacy impact assessments,
    including creating, loading, saving, and analyzing assessments.
    """
    
    def __init__(self, assessments_dir: Optional[str] = None):
        """
        Initialize the privacy impact assessment manager.
        
        Args:
            assessments_dir: Directory to store assessments
        """
        self.assessments_dir = assessments_dir
        self.assessments: Dict[str, PrivacyImpactAssessment] = {}
        
        # Load existing assessments if directory is provided
        if assessments_dir and os.path.exists(assessments_dir):
            self.load_assessments()
    
    def create_assessment(
        self,
        name: str,
        description: str = "",
        data_types: Optional[List[str]] = None,
        processing_purposes: Optional[List[str]] = None,
        data_subjects: Optional[List[str]] = None,
        assessment_date: Optional[datetime] = None
    ) -> PrivacyImpactAssessment:
        """
        Create a new privacy impact assessment.
        
        Args:
            name: Name of the assessment
            description: Description of the assessment
            data_types: Types of data being processed
            processing_purposes: Purposes for processing the data
            data_subjects: Categories of data subjects
            assessment_date: Date of the assessment
            
        Returns:
            PrivacyImpactAssessment object
        """
        # Create assessment
        assessment = PrivacyImpactAssessment(
            name=name,
            description=description,
            data_types=data_types,
            processing_purposes=processing_purposes,
            data_subjects=data_subjects,
            assessment_date=assessment_date
        )
        
        # Add assessment to assessments dictionary
        self.assessments[assessment.assessment_id] = assessment
        
        # Save assessment if directory is provided
        if self.assessments_dir:
            self.save_assessment(assessment)
        
        return assessment
    
    def get_assessment(self, assessment_id: str) -> Optional[PrivacyImpactAssessment]:
        """
        Get an assessment by ID.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            PrivacyImpactAssessment object or None if not found
        """
        return self.assessments.get(assessment_id)
    
    def list_assessments(self) -> List[Dict[str, Any]]:
        """
        List all assessments.
        
        Returns:
            List of assessment summaries
        """
        return [
            {
                "assessment_id": assessment.assessment_id,
                "name": assessment.name,
                "description": assessment.description,
                "assessment_date": assessment.assessment_date.isoformat(),
                "risk_score": assessment.calculate_risk_score()
            }
            for assessment in self.assessments.values()
        ]
    
    def save_assessment(self, assessment: PrivacyImpactAssessment) -> bool:
        """
        Save an assessment to a file.
        
        Args:
            assessment: Assessment to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.assessments_dir:
            logger.warning("No assessments directory specified, cannot save assessment")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.assessments_dir, exist_ok=True)
            
            # Create file path
            file_path = os.path.join(self.assessments_dir, f"{assessment.assessment_id}.json")
            
            # Save assessment
            with open(file_path, "w") as f:
                json.dump(assessment.to_dict(), f, indent=2)
            
            logger.info(f"Saved assessment to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving assessment: {str(e)}")
            return False
    
    def load_assessment(self, file_path: str) -> Optional[PrivacyImpactAssessment]:
        """
        Load an assessment from a file.
        
        Args:
            file_path: Path to the assessment file
            
        Returns:
            PrivacyImpactAssessment object or None if loading fails
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Assessment file not found: {file_path}")
                return None
            
            # Load assessment
            with open(file_path, "r") as f:
                assessment_dict = json.load(f)
            
            # Create assessment
            assessment = PrivacyImpactAssessment.from_dict(assessment_dict)
            
            # Add assessment to assessments dictionary
            self.assessments[assessment.assessment_id] = assessment
            
            logger.info(f"Loaded assessment from {file_path}")
            return assessment
        except Exception as e:
            logger.error(f"Error loading assessment: {str(e)}")
            return None
    
    def load_assessments(self) -> int:
        """
        Load all assessments from the assessments directory.
        
        Returns:
            Number of assessments loaded
        """
        if not self.assessments_dir or not os.path.exists(self.assessments_dir):
            logger.warning(f"Assessments directory not found: {self.assessments_dir}")
            return 0
        
        # Clear existing assessments
        self.assessments = {}
        
        # Load assessments
        count = 0
        for file_name in os.listdir(self.assessments_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.assessments_dir, file_name)
                assessment = self.load_assessment(file_path)
                if assessment:
                    count += 1
        
        logger.info(f"Loaded {count} assessments from {self.assessments_dir}")
        return count
    
    def delete_assessment(self, assessment_id: str) -> bool:
        """
        Delete an assessment.
        
        Args:
            assessment_id: ID of the assessment to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Check if assessment exists
        if assessment_id not in self.assessments:
            logger.error(f"Assessment not found: {assessment_id}")
            return False
        
        # Remove assessment from assessments dictionary
        assessment = self.assessments.pop(assessment_id)
        
        # Delete assessment file if directory is provided
        if self.assessments_dir:
            file_path = os.path.join(self.assessments_dir, f"{assessment_id}.json")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted assessment file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting assessment file: {str(e)}")
                    return False
        
        return True
    
    def generate_assessment_report(
        self,
        assessment_id: str,
        output_path: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a report for an assessment.
        
        Args:
            assessment_id: ID of the assessment
            output_path: Path to save the report
            include_details: Whether to include detailed information
            
        Returns:
            Dictionary containing report generation results
        """
        # Check if assessment exists
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return {
                "success": False,
                "error": f"Assessment not found: {assessment_id}"
            }
        
        # Create report data
        report_data = {
            "report_id": f"PIA-REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_date": datetime.now().isoformat(),
            "assessment_id": assessment_id,
            "assessment_name": assessment.name,
            "assessment_date": assessment.assessment_date.isoformat(),
            "risk_score": assessment.calculate_risk_score()
        }
        
        # Add detailed information if requested
        if include_details:
            report_data["assessment"] = assessment.to_dict()
        else:
            # Add summary information
            report_data["summary"] = {
                "description": assessment.description,
                "data_types": assessment.data_types,
                "processing_purposes": assessment.processing_purposes,
                "data_subjects": assessment.data_subjects,
                "risk_count": len(assessment.risks),
                "mitigation_count": len(assessment.mitigations),
                "recommendation_count": len(assessment.recommendations)
            }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write report to file
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        return {
            "success": True,
            "report_id": report_data["report_id"],
            "output_path": output_path
        }
    
    def analyze_url_data(
        self,
        df: pd.DataFrame,
        assessment_id: str,
        url_column: str = "url",
        sensitive_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze URL data for privacy risks.
        
        Args:
            df: DataFrame containing URL data
            assessment_id: ID of the assessment to update
            url_column: Name of the column containing URLs
            sensitive_patterns: Patterns to identify sensitive URLs
            
        Returns:
            Dictionary containing analysis results
        """
        # Check if assessment exists
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return {
                "success": False,
                "error": f"Assessment not found: {assessment_id}"
            }
        
        # Check if URL column exists
        if url_column not in df.columns:
            return {
                "success": False,
                "error": f"URL column not found: {url_column}"
            }
        
        # Use default sensitive patterns if none provided
        if not sensitive_patterns:
            sensitive_patterns = [
                "login", "signin", "account", "profile", "password",
                "payment", "checkout", "billing", "address", "personal",
                "health", "medical", "finance", "bank", "credit",
                "social", "security", "private", "confidential"
            ]
        
        # Count URLs
        url_count = len(df)
        
        # Count unique domains
        domains = df[url_column].str.extract(r"https?://([^/]+)")[0].dropna().unique()
        domain_count = len(domains)
        
        # Count sensitive URLs
        sensitive_count = 0
        for pattern in sensitive_patterns:
            sensitive_count += df[url_column].str.contains(pattern, case=False).sum()
        
        # Calculate sensitive URL percentage
        sensitive_percentage = (sensitive_count / url_count) * 100 if url_count > 0 else 0
        
        # Create analysis results
        analysis_results = {
            "success": True,
            "url_count": url_count,
            "domain_count": domain_count,
            "sensitive_count": sensitive_count,
            "sensitive_percentage": sensitive_percentage
        }
        
        # Add risks based on analysis
        if sensitive_percentage > 20:
            assessment.add_risk(
                name="High percentage of sensitive URLs",
                description=f"The dataset contains a high percentage ({sensitive_percentage:.1f}%) of URLs that may contain sensitive information.",
                severity="high",
                likelihood="high",
                impact="high",
                affected_data_types=["URLs", "Personal Data"]
            )
            
            assessment.add_recommendation(
                name="Implement URL anonymization",
                description="Implement URL anonymization for sensitive URLs to protect user privacy.",
                priority="high",
                implementation_status="pending"
            )
        
        if domain_count > 100:
            assessment.add_risk(
                name="Large number of domains",
                description=f"The dataset contains a large number of domains ({domain_count}), increasing the risk of data sharing with multiple third parties.",
                severity="medium",
                likelihood="medium",
                impact="medium",
                affected_data_types=["URLs", "Browsing History"]
            )
            
            assessment.add_recommendation(
                name="Implement domain categorization",
                description="Implement domain categorization to identify and manage third-party data sharing.",
                priority="medium",
                implementation_status="pending"
            )
        
        # Save assessment
        self.save_assessment(assessment)
        
        return analysis_results