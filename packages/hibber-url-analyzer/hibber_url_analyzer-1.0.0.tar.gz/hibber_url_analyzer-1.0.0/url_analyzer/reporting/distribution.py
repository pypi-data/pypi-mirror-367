"""
Report Distribution Module

This module provides functionality for distributing reports through various channels,
such as email, file sharing, and API integrations.
"""

import logging
import os
import json
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Set
import uuid

from url_analyzer.reporting.domain import Report, ReportFormat

logger = logging.getLogger(__name__)


class DistributionChannel:
    """
    Base class for report distribution channels.
    
    This class defines the interface for distributing reports through
    various channels.
    """
    
    def distribute(self, report: Report, recipients: List[str], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Distribute a report to recipients.
        
        Args:
            report: Report to distribute
            recipients: List of recipient identifiers (e.g., email addresses)
            options: Optional distribution options
            
        Returns:
            Dictionary containing distribution results
        """
        raise NotImplementedError("Subclasses must implement distribute()")
    
    def get_name(self) -> str:
        """
        Get the name of the distribution channel.
        
        Returns:
            Name of the distribution channel
        """
        raise NotImplementedError("Subclasses must implement get_name()")


class EmailDistributionChannel(DistributionChannel):
    """
    Distribution channel for sending reports via email.
    """
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        sender_email: str,
        use_tls: bool = True
    ):
        """
        Initialize the email distribution channel.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            sender_email: Email address to send from
            use_tls: Whether to use TLS for SMTP connection
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email
        self.use_tls = use_tls
    
    def distribute(
        self,
        report: Report,
        recipients: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute a report via email.
        
        Args:
            report: Report to distribute
            recipients: List of email addresses
            options: Optional distribution options
                - subject: Email subject
                - body: Email body
                - include_attachment: Whether to include the report as an attachment
                - attachment_name: Name for the attachment file
            
        Returns:
            Dictionary containing distribution results
        """
        options = options or {}
        
        # Get email options
        subject = options.get("subject", f"URL Analyzer Report: {report.name}")
        body = options.get("body", f"Please find attached the URL Analyzer report: {report.name}")
        include_attachment = options.get("include_attachment", True)
        attachment_name = options.get("attachment_name", f"{report.name}.html")
        
        # Check if report file exists
        if not report.file_exists:
            return {
                "success": False,
                "error": "Report file does not exist",
                "report_id": report.report_id,
                "channel": self.get_name()
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            
            # Add body
            msg.attach(MIMEText(body, "plain"))
            
            # Add attachment if requested
            if include_attachment:
                with open(report.output_path, "rb") as f:
                    attachment = MIMEApplication(f.read(), _subtype=self._get_mime_subtype(report.format))
                    attachment.add_header("Content-Disposition", f"attachment; filename={attachment_name}")
                    msg.attach(attachment)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                # Login if credentials provided
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                # Send email
                server.send_message(msg)
            
            return {
                "success": True,
                "recipients": recipients,
                "report_id": report.report_id,
                "channel": self.get_name(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "report_id": report.report_id,
                "channel": self.get_name()
            }
    
    def get_name(self) -> str:
        """
        Get the name of the distribution channel.
        
        Returns:
            Name of the distribution channel
        """
        return "Email"
    
    def _get_mime_subtype(self, format: ReportFormat) -> str:
        """
        Get the MIME subtype for a report format.
        
        Args:
            format: Report format
            
        Returns:
            MIME subtype
        """
        if format == ReportFormat.HTML:
            return "html"
        elif format == ReportFormat.CSV:
            return "csv"
        elif format == ReportFormat.JSON:
            return "json"
        elif format == ReportFormat.PDF:
            return "pdf"
        elif format == ReportFormat.EXCEL:
            return "vnd.ms-excel"
        else:
            return "octet-stream"


class FileShareDistributionChannel(DistributionChannel):
    """
    Distribution channel for copying reports to a file share.
    """
    
    def __init__(
        self,
        base_directory: str,
        create_subdirectories: bool = True
    ):
        """
        Initialize the file share distribution channel.
        
        Args:
            base_directory: Base directory for the file share
            create_subdirectories: Whether to create subdirectories for recipients
        """
        self.base_directory = base_directory
        self.create_subdirectories = create_subdirectories
        
        # Create base directory if it doesn't exist
        if not os.path.exists(base_directory):
            os.makedirs(base_directory, exist_ok=True)
    
    def distribute(
        self,
        report: Report,
        recipients: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute a report to a file share.
        
        Args:
            report: Report to distribute
            recipients: List of recipient directories or identifiers
            options: Optional distribution options
                - filename: Name for the distributed file
                - overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary containing distribution results
        """
        options = options or {}
        
        # Get distribution options
        filename = options.get("filename", os.path.basename(report.output_path))
        overwrite = options.get("overwrite", True)
        
        # Check if report file exists
        if not report.file_exists:
            return {
                "success": False,
                "error": "Report file does not exist",
                "report_id": report.report_id,
                "channel": self.get_name()
            }
        
        # Distribute to each recipient
        results = []
        for recipient in recipients:
            try:
                # Create recipient directory if needed
                if self.create_subdirectories:
                    recipient_dir = os.path.join(self.base_directory, recipient)
                    os.makedirs(recipient_dir, exist_ok=True)
                else:
                    recipient_dir = self.base_directory
                
                # Create destination path
                dest_path = os.path.join(recipient_dir, filename)
                
                # Check if file exists and overwrite is disabled
                if os.path.exists(dest_path) and not overwrite:
                    results.append({
                        "success": False,
                        "error": "File already exists and overwrite is disabled",
                        "recipient": recipient,
                        "path": dest_path
                    })
                    continue
                
                # Copy file
                import shutil
                shutil.copy2(report.output_path, dest_path)
                
                results.append({
                    "success": True,
                    "recipient": recipient,
                    "path": dest_path
                })
                
            except Exception as e:
                logger.error(f"Error distributing to {recipient}: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "recipient": recipient
                })
        
        return {
            "success": all(result["success"] for result in results),
            "results": results,
            "report_id": report.report_id,
            "channel": self.get_name(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_name(self) -> str:
        """
        Get the name of the distribution channel.
        
        Returns:
            Name of the distribution channel
        """
        return "File Share"


class WebhookDistributionChannel(DistributionChannel):
    """
    Distribution channel for sending reports via webhooks.
    """
    
    def __init__(
        self,
        default_webhook_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ):
        """
        Initialize the webhook distribution channel.
        
        Args:
            default_webhook_url: Default webhook URL
            headers: Default headers to include in webhook requests
            timeout: Timeout for webhook requests in seconds
        """
        self.default_webhook_url = default_webhook_url
        self.headers = headers or {}
        self.timeout = timeout
    
    def distribute(
        self,
        report: Report,
        recipients: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute a report via webhooks.
        
        Args:
            report: Report to distribute
            recipients: List of webhook URLs
            options: Optional distribution options
                - include_file: Whether to include the report file in the request
                - additional_data: Additional data to include in the webhook payload
                - method: HTTP method to use (POST, PUT)
                - headers: Additional headers to include in the request
            
        Returns:
            Dictionary containing distribution results
        """
        options = options or {}
        
        # Get webhook options
        include_file = options.get("include_file", True)
        additional_data = options.get("additional_data", {})
        method = options.get("method", "POST")
        headers = {**self.headers, **(options.get("headers", {}))}
        
        # Check if report file exists
        if include_file and not report.file_exists:
            return {
                "success": False,
                "error": "Report file does not exist",
                "report_id": report.report_id,
                "channel": self.get_name()
            }
        
        # Use default webhook URL if no recipients provided
        if not recipients and self.default_webhook_url:
            recipients = [self.default_webhook_url]
        
        # Distribute to each recipient
        results = []
        for webhook_url in recipients:
            try:
                # Create payload
                payload = {
                    "report_id": report.report_id,
                    "report_name": report.name,
                    "report_type": report.template.type.name,
                    "report_format": report.template.format.name,
                    "timestamp": datetime.now().isoformat(),
                    **additional_data
                }
                
                # Send webhook request
                if include_file:
                    # Send with file
                    with open(report.output_path, "rb") as f:
                        files = {"file": (os.path.basename(report.output_path), f)}
                        response = requests.request(
                            method,
                            webhook_url,
                            data=payload,
                            files=files,
                            headers=headers,
                            timeout=self.timeout
                        )
                else:
                    # Send without file
                    response = requests.request(
                        method,
                        webhook_url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout
                    )
                
                # Check response
                response.raise_for_status()
                
                results.append({
                    "success": True,
                    "webhook_url": webhook_url,
                    "status_code": response.status_code
                })
                
            except Exception as e:
                logger.error(f"Error sending webhook to {webhook_url}: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "webhook_url": webhook_url
                })
        
        return {
            "success": all(result["success"] for result in results),
            "results": results,
            "report_id": report.report_id,
            "channel": self.get_name(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_name(self) -> str:
        """
        Get the name of the distribution channel.
        
        Returns:
            Name of the distribution channel
        """
        return "Webhook"


class ReportDistributionManager:
    """
    Manages report distribution through various channels.
    
    This class provides functionality for distributing reports through
    multiple channels and managing distribution configurations.
    """
    
    def __init__(self):
        """
        Initialize the report distribution manager.
        """
        self.channels: Dict[str, DistributionChannel] = {}
        self.distribution_history: List[Dict[str, Any]] = []
    
    def register_channel(self, channel: DistributionChannel) -> None:
        """
        Register a distribution channel.
        
        Args:
            channel: Distribution channel to register
        """
        self.channels[channel.get_name()] = channel
    
    def get_channel(self, channel_name: str) -> Optional[DistributionChannel]:
        """
        Get a distribution channel by name.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Distribution channel or None if not found
        """
        return self.channels.get(channel_name)
    
    def list_channels(self) -> List[str]:
        """
        List all registered distribution channels.
        
        Returns:
            List of channel names
        """
        return list(self.channels.keys())
    
    def distribute_report(
        self,
        report: Report,
        channel_name: str,
        recipients: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute a report through a specific channel.
        
        Args:
            report: Report to distribute
            channel_name: Name of the distribution channel
            recipients: List of recipients
            options: Optional distribution options
            
        Returns:
            Dictionary containing distribution results
        """
        # Get the channel
        channel = self.get_channel(channel_name)
        if not channel:
            result = {
                "success": False,
                "error": f"Distribution channel not found: {channel_name}",
                "report_id": report.report_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Distribute the report
            result = channel.distribute(report, recipients, options)
        
        # Add to distribution history
        distribution_record = {
            "distribution_id": str(uuid.uuid4()),
            "report_id": report.report_id,
            "channel": channel_name,
            "recipients": recipients,
            "options": options,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.distribution_history.append(distribution_record)
        
        return result
    
    def distribute_report_to_multiple_channels(
        self,
        report: Report,
        distribution_config: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Distribute a report through multiple channels.
        
        Args:
            report: Report to distribute
            distribution_config: List of distribution configurations
                Each configuration should have:
                - channel: Name of the distribution channel
                - recipients: List of recipients
                - options: Optional distribution options
            
        Returns:
            Dictionary containing distribution results for all channels
        """
        results = []
        
        for config in distribution_config:
            channel_name = config.get("channel")
            recipients = config.get("recipients", [])
            options = config.get("options")
            
            if not channel_name:
                results.append({
                    "success": False,
                    "error": "Channel name not specified",
                    "config": config
                })
                continue
            
            result = self.distribute_report(report, channel_name, recipients, options)
            results.append(result)
        
        return {
            "success": all(result.get("success", False) for result in results),
            "results": results,
            "report_id": report.report_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_distribution_history(
        self,
        report_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get distribution history with optional filtering.
        
        Args:
            report_id: Filter by report ID
            channel_name: Filter by channel name
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of distribution records
        """
        filtered_history = self.distribution_history
        
        # Filter by report ID
        if report_id:
            filtered_history = [
                record for record in filtered_history
                if record["report_id"] == report_id
            ]
        
        # Filter by channel name
        if channel_name:
            filtered_history = [
                record for record in filtered_history
                if record["channel"] == channel_name
            ]
        
        # Filter by start date
        if start_date:
            filtered_history = [
                record for record in filtered_history
                if datetime.fromisoformat(record["timestamp"]) >= start_date
            ]
        
        # Filter by end date
        if end_date:
            filtered_history = [
                record for record in filtered_history
                if datetime.fromisoformat(record["timestamp"]) <= end_date
            ]
        
        return filtered_history
    
    def save_distribution_history(self, file_path: str) -> bool:
        """
        Save distribution history to a file.
        
        Args:
            file_path: Path to save the history
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save history
            with open(file_path, "w") as f:
                json.dump(self.distribution_history, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving distribution history: {str(e)}")
            return False
    
    def load_distribution_history(self, file_path: str) -> bool:
        """
        Load distribution history from a file.
        
        Args:
            file_path: Path to load the history from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Distribution history file not found: {file_path}")
                return False
            
            # Load history
            with open(file_path, "r") as f:
                self.distribution_history = json.load(f)
            
            return True
        except Exception as e:
            logger.error(f"Error loading distribution history: {str(e)}")
            return False