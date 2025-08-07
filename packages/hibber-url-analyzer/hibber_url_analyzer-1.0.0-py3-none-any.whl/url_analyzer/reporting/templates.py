"""
Report Templates Module

This module provides functionality for managing report templates,
including creating, customizing, and applying templates to reports.
"""

import logging
import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Set
import uuid

from url_analyzer.reporting.domain import ReportTemplate, ReportFormat, ReportType
from url_analyzer.reporting.interfaces import TemplateRepository

logger = logging.getLogger(__name__)


class ReportTemplateManager:
    """
    Manages report templates.
    
    This class provides functionality for creating, customizing, and
    applying templates to reports.
    """
    
    def __init__(
        self,
        template_repository: TemplateRepository,
        template_dir: Optional[str] = None
    ):
        """
        Initialize the report template manager.
        
        Args:
            template_repository: Repository for storing templates
            template_dir: Directory containing template files
        """
        self.template_repository = template_repository
        self.template_dir = template_dir
        
        # Create template directory if it doesn't exist
        if template_dir and not os.path.exists(template_dir):
            os.makedirs(template_dir, exist_ok=True)
    
    def create_template(
        self,
        name: str,
        format: ReportFormat,
        type: ReportType,
        content: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReportTemplate:
        """
        Create a new report template.
        
        Args:
            name: Name of the template
            format: Format of the template (HTML, CSV, etc.)
            type: Type of the template (summary, detailed, etc.)
            content: Content of the template
            description: Description of the template
            metadata: Additional metadata for the template
            
        Returns:
            ReportTemplate object
        """
        # Generate a unique ID for the template
        template_id = f"template-{uuid.uuid4()}"
        
        # Create template file path
        if self.template_dir:
            file_name = f"{template_id}.{format.name.lower()}"
            template_path = os.path.join(self.template_dir, file_name)
            
            # Write template content to file
            with open(template_path, "w") as f:
                f.write(content)
        else:
            template_path = None
        
        # Create template object
        template = ReportTemplate(
            template_id=template_id,
            name=name,
            description=description,
            format=format,
            template_path=template_path,
            type=type,
            options=metadata or {}
        )
        
        # Add template to repository
        self.template_repository.add_template(template)
        
        return template
    
    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ReportTemplate]:
        """
        Update an existing template.
        
        Args:
            template_id: ID of the template to update
            name: New name for the template
            description: New description for the template
            content: New content for the template
            metadata: New metadata for the template
            
        Returns:
            Updated ReportTemplate object or None if not found
        """
        # Get the template
        template = self.template_repository.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        # Create updated template properties
        updated_name = name if name is not None else template.name
        updated_description = description if description is not None else template.description
        
        # Update content if provided
        if content is not None and template.path:
            with open(template.path, "w") as f:
                f.write(content)
        
        # Create updated metadata
        updated_metadata = template.metadata.copy()
        if metadata is not None:
            updated_metadata.update(metadata)
        
        # Create a new template object with updated values
        updated_template = ReportTemplate(
            template_id=template.template_id,
            name=updated_name,
            description=updated_description,
            format=template.format,
            template_path=template.template_path,
            type=template.type,
            options=updated_metadata
        )
        
        # Update template in repository
        self.template_repository.add_template(updated_template)
        
        return updated_template
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            True if the template was deleted, False otherwise
        """
        # Get the template
        template = self.template_repository.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return False
        
        # Delete template file if it exists
        if template.path and os.path.exists(template.path):
            try:
                os.remove(template.path)
            except Exception as e:
                logger.error(f"Error deleting template file: {str(e)}")
        
        # Remove template from repository
        self.template_repository.remove_template(template_id)
        
        return True
    
    def get_template_content(self, template_id: str) -> Optional[str]:
        """
        Get the content of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Template content or None if not found
        """
        # Get the template
        template = self.template_repository.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        # Check if template has a path
        if not template.path:
            logger.error(f"Template has no path: {template_id}")
            return None
        
        # Check if template file exists
        if not os.path.exists(template.path):
            logger.error(f"Template file not found: {template.path}")
            return None
        
        # Read template content
        try:
            with open(template.path, "r") as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading template file: {str(e)}")
            return None
    
    def clone_template(
        self,
        template_id: str,
        new_name: str,
        new_description: Optional[str] = None
    ) -> Optional[ReportTemplate]:
        """
        Clone an existing template.
        
        Args:
            template_id: ID of the template to clone
            new_name: Name for the cloned template
            new_description: Description for the cloned template
            
        Returns:
            Cloned ReportTemplate object or None if not found
        """
        # Get the template
        template = self.template_repository.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        # Get template content
        content = self.get_template_content(template_id)
        if content is None:
            logger.error(f"Could not get template content: {template_id}")
            return None
        
        # Create new template
        return self.create_template(
            name=new_name,
            format=template.format,
            type=template.type,
            content=content,
            description=new_description or f"Clone of {template.name}",
            metadata=template.metadata.copy()
        )
    
    def import_template(
        self,
        file_path: str,
        name: str,
        format: ReportFormat,
        type: ReportType,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ReportTemplate]:
        """
        Import a template from a file.
        
        Args:
            file_path: Path to the template file
            name: Name for the template
            format: Format of the template
            type: Type of the template
            description: Description for the template
            metadata: Metadata for the template
            
        Returns:
            Imported ReportTemplate object or None if import failed
        """
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Template file not found: {file_path}")
            return None
        
        # Read template content
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading template file: {str(e)}")
            return None
        
        # Create new template
        return self.create_template(
            name=name,
            format=format,
            type=type,
            content=content,
            description=description,
            metadata=metadata
        )
    
    def export_template(
        self,
        template_id: str,
        output_path: str
    ) -> bool:
        """
        Export a template to a file.
        
        Args:
            template_id: ID of the template to export
            output_path: Path to save the template
            
        Returns:
            True if the template was exported, False otherwise
        """
        # Get the template
        template = self.template_repository.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return False
        
        # Check if template has a path
        if not template.path:
            logger.error(f"Template has no path: {template_id}")
            return False
        
        # Check if template file exists
        if not os.path.exists(template.path):
            logger.error(f"Template file not found: {template.path}")
            return False
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Copy template file
        try:
            shutil.copy2(template.path, output_path)
            return True
        except Exception as e:
            logger.error(f"Error exporting template: {str(e)}")
            return False
    
    def get_template_variables(self, template_id: str) -> Optional[List[str]]:
        """
        Get the variables used in a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            List of variable names or None if not found
        """
        # Get template content
        content = self.get_template_content(template_id)
        if content is None:
            return None
        
        # Get template format
        template = self.template_repository.get_template(template_id)
        if not template:
            return None
        
        # Extract variables based on template format
        if template.format == ReportFormat.HTML:
            return self._extract_html_variables(content)
        elif template.format == ReportFormat.JSON:
            return self._extract_json_variables(content)
        else:
            logger.warning(f"Variable extraction not supported for format: {template.format}")
            return []
    
    def _extract_html_variables(self, content: str) -> List[str]:
        """
        Extract variables from an HTML template.
        
        Args:
            content: Template content
            
        Returns:
            List of variable names
        """
        import re
        
        # Look for {{ variable }} pattern (Jinja2 style)
        pattern = r"{{\s*([a-zA-Z0-9_\.]+)\s*}}"
        matches = re.findall(pattern, content)
        
        # Remove duplicates and sort
        variables = sorted(set(matches))
        
        return variables
    
    def _extract_json_variables(self, content: str) -> List[str]:
        """
        Extract variables from a JSON template.
        
        Args:
            content: Template content
            
        Returns:
            List of variable names
        """
        import re
        
        # Look for "${variable}" pattern
        pattern = r'\$\{([a-zA-Z0-9_\.]+)\}'
        matches = re.findall(pattern, content)
        
        # Remove duplicates and sort
        variables = sorted(set(matches))
        
        return variables


class TemplateVersionManager:
    """
    Manages versions of report templates.
    
    This class provides functionality for versioning templates,
    including creating new versions, reverting to previous versions,
    and comparing versions.
    """
    
    def __init__(
        self,
        template_manager: ReportTemplateManager,
        version_dir: Optional[str] = None
    ):
        """
        Initialize the template version manager.
        
        Args:
            template_manager: Manager for templates
            version_dir: Directory for storing version files
        """
        self.template_manager = template_manager
        self.version_dir = version_dir
        
        # Create version directory if it doesn't exist
        if version_dir and not os.path.exists(version_dir):
            os.makedirs(version_dir, exist_ok=True)
    
    def create_version(
        self,
        template_id: str,
        version_name: str,
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new version of a template.
        
        Args:
            template_id: ID of the template
            version_name: Name for the version
            description: Description for the version
            
        Returns:
            Version information or None if creation failed
        """
        # Get the template
        template = self.template_manager.template_repository.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        # Get template content
        content = self.template_manager.get_template_content(template_id)
        if content is None:
            logger.error(f"Could not get template content: {template_id}")
            return None
        
        # Create version ID
        version_id = f"v-{uuid.uuid4()}"
        
        # Create version file
        if self.version_dir:
            version_file = os.path.join(self.version_dir, f"{version_id}.json")
            
            # Create version data
            version_data = {
                "id": version_id,
                "template_id": template_id,
                "name": version_name,
                "description": description,
                "content": content,
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "template_name": template.name,
                    "template_format": template.format.name,
                    "template_type": template.type.name
                }
            }
            
            # Write version data to file
            try:
                with open(version_file, "w") as f:
                    json.dump(version_data, f, indent=2)
            except Exception as e:
                logger.error(f"Error writing version file: {str(e)}")
                return None
            
            return version_data
        else:
            logger.error("No version directory specified")
            return None
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of a template.
        
        Args:
            version_id: ID of the version
            
        Returns:
            Version information or None if not found
        """
        if not self.version_dir:
            logger.error("No version directory specified")
            return None
        
        # Create version file path
        version_file = os.path.join(self.version_dir, f"{version_id}.json")
        
        # Check if version file exists
        if not os.path.exists(version_file):
            logger.error(f"Version file not found: {version_file}")
            return None
        
        # Read version data
        try:
            with open(version_file, "r") as f:
                version_data = json.load(f)
            return version_data
        except Exception as e:
            logger.error(f"Error reading version file: {str(e)}")
            return None
    
    def get_versions(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            List of version information
        """
        if not self.version_dir:
            logger.error("No version directory specified")
            return []
        
        versions = []
        
        # Iterate through version files
        for file_name in os.listdir(self.version_dir):
            if not file_name.endswith(".json"):
                continue
            
            # Read version data
            try:
                with open(os.path.join(self.version_dir, file_name), "r") as f:
                    version_data = json.load(f)
                
                # Check if version is for the specified template
                if version_data.get("template_id") == template_id:
                    versions.append(version_data)
            except Exception as e:
                logger.error(f"Error reading version file {file_name}: {str(e)}")
        
        # Sort versions by creation date
        versions.sort(key=lambda v: v.get("created_at", ""), reverse=True)
        
        return versions
    
    def revert_to_version(self, version_id: str) -> Optional[ReportTemplate]:
        """
        Revert a template to a specific version.
        
        Args:
            version_id: ID of the version
            
        Returns:
            Updated ReportTemplate object or None if reversion failed
        """
        # Get version data
        version_data = self.get_version(version_id)
        if not version_data:
            return None
        
        # Get template ID
        template_id = version_data.get("template_id")
        if not template_id:
            logger.error(f"Version has no template ID: {version_id}")
            return None
        
        # Get template content
        content = version_data.get("content")
        if not content:
            logger.error(f"Version has no content: {version_id}")
            return None
        
        # Update template with version content
        return self.template_manager.update_template(
            template_id=template_id,
            content=content,
            metadata={
                "reverted_from_version": version_id,
                "reverted_at": datetime.now().isoformat()
            }
        )
    
    def compare_versions(
        self,
        version_id1: str,
        version_id2: str
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two versions of a template.
        
        Args:
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Comparison results or None if comparison failed
        """
        # Get version data
        version1 = self.get_version(version_id1)
        version2 = self.get_version(version_id2)
        
        if not version1 or not version2:
            return None
        
        # Check if versions are for the same template
        if version1.get("template_id") != version2.get("template_id"):
            logger.error("Cannot compare versions of different templates")
            return None
        
        # Get content
        content1 = version1.get("content", "")
        content2 = version2.get("content", "")
        
        # Calculate diff
        import difflib
        diff = difflib.unified_diff(
            content1.splitlines(),
            content2.splitlines(),
            fromfile=version1.get("name", version_id1),
            tofile=version2.get("name", version_id2),
            lineterm=""
        )
        
        # Create comparison results
        return {
            "template_id": version1.get("template_id"),
            "version1": {
                "id": version_id1,
                "name": version1.get("name"),
                "created_at": version1.get("created_at")
            },
            "version2": {
                "id": version_id2,
                "name": version2.get("name"),
                "created_at": version2.get("created_at")
            },
            "diff": list(diff)
        }