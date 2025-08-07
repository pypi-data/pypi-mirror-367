"""
Data Export Module

This module provides data export capabilities for URL data,
supporting compliance with data privacy regulations such as GDPR and CCPA.
"""

import logging
import os
import json
import csv
import zipfile
import io
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataExporter:
    """
    Data exporter for URL data.
    
    This class provides methods for exporting data in various formats,
    supporting compliance with data privacy regulations.
    """
    
    @staticmethod
    def export_user_data(
        df: pd.DataFrame,
        user_identifier: str,
        user_id_column: str,
        output_path: str,
        format: str = "json",
        include_metadata: bool = True,
        anonymize_others: bool = True
    ) -> Dict[str, Any]:
        """
        Export data for a specific user.
        
        Args:
            df: DataFrame containing user data
            user_identifier: Identifier of the user to export data for
            user_id_column: Name of the column containing user identifiers
            output_path: Path to save the exported data
            format: Export format (json, csv, xml, html)
            include_metadata: Whether to include metadata in the export
            anonymize_others: Whether to anonymize data of other users
            
        Returns:
            Dictionary containing export results
        """
        if user_id_column not in df.columns:
            return {
                "success": False,
                "error": f"User ID column '{user_id_column}' not found in DataFrame"
            }
        
        # Filter data for the specified user
        user_data = df[df[user_id_column] == user_identifier]
        
        if len(user_data) == 0:
            return {
                "success": False,
                "error": f"No data found for user '{user_identifier}'"
            }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add metadata if requested
        if include_metadata:
            metadata = {
                "export_date": datetime.now().isoformat(),
                "user_identifier": user_identifier,
                "record_count": len(user_data),
                "columns": user_data.columns.tolist()
            }
        
        # Export data in the specified format
        try:
            if format.lower() == "json":
                # Export as JSON
                result = DataExporter._export_as_json(
                    user_data, output_path, metadata if include_metadata else None
                )
            elif format.lower() == "csv":
                # Export as CSV
                result = DataExporter._export_as_csv(
                    user_data, output_path, metadata if include_metadata else None
                )
            elif format.lower() == "xml":
                # Export as XML
                result = DataExporter._export_as_xml(
                    user_data, output_path, metadata if include_metadata else None
                )
            elif format.lower() == "html":
                # Export as HTML
                result = DataExporter._export_as_html(
                    user_data, output_path, metadata if include_metadata else None
                )
            elif format.lower() == "zip":
                # Export as ZIP containing multiple formats
                result = DataExporter._export_as_zip(
                    user_data, output_path, metadata if include_metadata else None
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {format}"
                }
            
            # Add export information to result
            result.update({
                "user_identifier": user_identifier,
                "record_count": len(user_data),
                "export_date": datetime.now().isoformat(),
                "format": format
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting user data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _export_as_json(
        df: pd.DataFrame,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data as JSON.
        
        Args:
            df: DataFrame to export
            output_path: Path to save the exported data
            metadata: Optional metadata to include
            
        Returns:
            Dictionary containing export results
        """
        # Convert DataFrame to records
        records = df.to_dict(orient="records")
        
        # Create export data
        export_data = {
            "data": records
        }
        
        # Add metadata if provided
        if metadata:
            export_data["metadata"] = metadata
        
        # Write to file
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        return {
            "success": True,
            "output_path": output_path,
            "format": "json"
        }
    
    @staticmethod
    def _export_as_csv(
        df: pd.DataFrame,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data as CSV.
        
        Args:
            df: DataFrame to export
            output_path: Path to save the exported data
            metadata: Optional metadata to include
            
        Returns:
            Dictionary containing export results
        """
        # Write DataFrame to CSV
        df.to_csv(output_path, index=False)
        
        # Write metadata to separate file if provided
        if metadata:
            metadata_path = output_path.replace(".csv", "_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "output_path": output_path,
            "format": "csv",
            "metadata_path": metadata_path if metadata else None
        }
    
    @staticmethod
    def _export_as_xml(
        df: pd.DataFrame,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data as XML.
        
        Args:
            df: DataFrame to export
            output_path: Path to save the exported data
            metadata: Optional metadata to include
            
        Returns:
            Dictionary containing export results
        """
        try:
            import dicttoxml
            from xml.dom.minidom import parseString
            
            # Convert DataFrame to records
            records = df.to_dict(orient="records")
            
            # Create export data
            export_data = {
                "data": {"record": records}
            }
            
            # Add metadata if provided
            if metadata:
                export_data["metadata"] = metadata
            
            # Convert to XML
            xml = dicttoxml.dicttoxml(export_data, custom_root="export", attr_type=False)
            
            # Pretty print XML
            dom = parseString(xml)
            pretty_xml = dom.toprettyxml()
            
            # Write to file
            with open(output_path, "w") as f:
                f.write(pretty_xml)
            
            return {
                "success": True,
                "output_path": output_path,
                "format": "xml"
            }
            
        except ImportError:
            # Fall back to JSON if dicttoxml is not available
            logger.warning("dicttoxml package not available. Falling back to JSON export.")
            json_path = output_path.replace(".xml", ".json")
            return DataExporter._export_as_json(df, json_path, metadata)
    
    @staticmethod
    def _export_as_html(
        df: pd.DataFrame,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data as HTML.
        
        Args:
            df: DataFrame to export
            output_path: Path to save the exported data
            metadata: Optional metadata to include
            
        Returns:
            Dictionary containing export results
        """
        # Create HTML content
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <meta charset=\"UTF-8\">",
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            "    <title>Data Export</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 20px; }",
            "        table { border-collapse: collapse; width: 100%; }",
            "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "        th { background-color: #f2f2f2; }",
            "        tr:nth-child(even) { background-color: #f9f9f9; }",
            "        .metadata { margin-bottom: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }",
            "    </style>",
            "</head>",
            "<body>"
        ]
        
        # Add metadata if provided
        if metadata:
            html_parts.append("    <div class=\"metadata\">")
            html_parts.append("        <h2>Metadata</h2>")
            html_parts.append("        <table>")
            html_parts.append("            <tr><th>Key</th><th>Value</th></tr>")
            
            for key, value in metadata.items():
                if isinstance(value, list):
                    value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)
                
                html_parts.append(f"            <tr><td>{key}</td><td>{value_str}</td></tr>")
            
            html_parts.append("        </table>")
            html_parts.append("    </div>")
        
        # Add data table
        html_parts.append("    <h2>Data</h2>")
        html_parts.append("    <table>")
        
        # Add table header
        html_parts.append("        <tr>")
        for col in df.columns:
            html_parts.append(f"            <th>{col}</th>")
        html_parts.append("        </tr>")
        
        # Add table rows
        for _, row in df.iterrows():
            html_parts.append("        <tr>")
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    value = ""
                html_parts.append(f"            <td>{value}</td>")
            html_parts.append("        </tr>")
        
        html_parts.append("    </table>")
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        # Write to file
        with open(output_path, "w") as f:
            f.write("\n".join(html_parts))
        
        return {
            "success": True,
            "output_path": output_path,
            "format": "html"
        }
    
    @staticmethod
    def _export_as_zip(
        df: pd.DataFrame,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data as ZIP containing multiple formats.
        
        Args:
            df: DataFrame to export
            output_path: Path to save the exported data
            metadata: Optional metadata to include
            
        Returns:
            Dictionary containing export results
        """
        # Create a ZIP file
        with zipfile.ZipFile(output_path, "w") as zip_file:
            # Export as JSON
            json_buffer = io.StringIO()
            records = df.to_dict(orient="records")
            export_data = {"data": records}
            if metadata:
                export_data["metadata"] = metadata
            json.dump(export_data, json_buffer, indent=2)
            zip_file.writestr("data.json", json_buffer.getvalue())
            
            # Export as CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            zip_file.writestr("data.csv", csv_buffer.getvalue())
            
            # Export metadata as separate JSON if provided
            if metadata:
                metadata_buffer = io.StringIO()
                json.dump(metadata, metadata_buffer, indent=2)
                zip_file.writestr("metadata.json", metadata_buffer.getvalue())
            
            # Export as HTML
            html_buffer = io.StringIO()
            html_export = DataExporter._export_as_html(df, "", metadata)
            with open(html_export["output_path"], "r") as f:
                html_content = f.read()
            zip_file.writestr("data.html", html_content)
            
            # Try to export as XML if dicttoxml is available
            try:
                import dicttoxml
                from xml.dom.minidom import parseString
                
                xml_buffer = io.StringIO()
                xml_export = DataExporter._export_as_xml(df, "", metadata)
                with open(xml_export["output_path"], "r") as f:
                    xml_content = f.read()
                zip_file.writestr("data.xml", xml_content)
            except ImportError:
                # Skip XML export if dicttoxml is not available
                pass
        
        return {
            "success": True,
            "output_path": output_path,
            "format": "zip",
            "included_formats": ["json", "csv", "html", "xml"] if "dicttoxml" in globals() else ["json", "csv", "html"]
        }
    
    @staticmethod
    def export_all_user_data(
        df: pd.DataFrame,
        user_id_column: str,
        output_dir: str,
        format: str = "json",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export data for all users.
        
        Args:
            df: DataFrame containing user data
            user_id_column: Name of the column containing user identifiers
            output_dir: Directory to save the exported data
            format: Export format (json, csv, xml, html)
            include_metadata: Whether to include metadata in the export
            
        Returns:
            Dictionary containing export results
        """
        if user_id_column not in df.columns:
            return {
                "success": False,
                "error": f"User ID column '{user_id_column}' not found in DataFrame"
            }
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get unique user IDs
        user_ids = df[user_id_column].unique()
        
        # Export data for each user
        results = {}
        for user_id in user_ids:
            # Skip null/NaN user IDs
            if pd.isna(user_id):
                continue
            
            # Create output path for this user
            user_output_path = os.path.join(output_dir, f"user_{user_id}.{format}")
            
            # Export user data
            user_result = DataExporter.export_user_data(
                df, user_id, user_id_column, user_output_path, format, include_metadata
            )
            
            # Store result
            results[str(user_id)] = user_result
        
        # Create summary
        summary = {
            "success": True,
            "user_count": len(results),
            "successful_exports": sum(1 for r in results.values() if r.get("success", False)),
            "failed_exports": sum(1 for r in results.values() if not r.get("success", False)),
            "output_dir": output_dir,
            "format": format,
            "export_date": datetime.now().isoformat()
        }
        
        # Save summary to file
        summary_path = os.path.join(output_dir, "export_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        # Add user results to summary
        summary["user_results"] = results
        
        return summary
    
    @staticmethod
    def create_data_subject_request(
        user_identifier: str,
        request_type: str,
        output_path: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a data subject request document.
        
        Args:
            user_identifier: Identifier of the user making the request
            request_type: Type of request (access, deletion, correction, etc.)
            output_path: Path to save the request document
            additional_info: Additional information for the request
            
        Returns:
            Dictionary containing request creation results
        """
        # Create request data
        request_data = {
            "request_id": f"DSR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_identifier}",
            "user_identifier": user_identifier,
            "request_type": request_type,
            "request_date": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Add additional information if provided
        if additional_info:
            request_data["additional_info"] = additional_info
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write request to file
        with open(output_path, "w") as f:
            json.dump(request_data, f, indent=2)
        
        return {
            "success": True,
            "request_id": request_data["request_id"],
            "output_path": output_path
        }
    
    @staticmethod
    def generate_privacy_report(
        df: pd.DataFrame,
        output_path: str,
        include_statistics: bool = True,
        include_sample_data: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a privacy report for the data.
        
        Args:
            df: DataFrame to analyze
            output_path: Path to save the report
            include_statistics: Whether to include statistics in the report
            include_sample_data: Whether to include sample data in the report
            
        Returns:
            Dictionary containing report generation results
        """
        # Create report data
        report_data = {
            "report_id": f"PRIVACY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_date": datetime.now().isoformat(),
            "record_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist()
        }
        
        # Add statistics if requested
        if include_statistics:
            # Calculate basic statistics
            statistics = {}
            
            # Count missing values
            missing_counts = df.isna().sum()
            missing_percentages = (missing_counts / len(df)) * 100
            
            statistics["missing_values"] = {
                col: {
                    "count": int(missing_counts[col]),
                    "percentage": float(missing_percentages[col])
                }
                for col in df.columns
            }
            
            # Count unique values
            unique_counts = df.nunique()
            unique_percentages = (unique_counts / len(df)) * 100
            
            statistics["unique_values"] = {
                col: {
                    "count": int(unique_counts[col]),
                    "percentage": float(unique_percentages[col])
                }
                for col in df.columns
            }
            
            # Add statistics to report
            report_data["statistics"] = statistics
        
        # Add sample data if requested
        if include_sample_data:
            # Sample a few rows (max 5)
            sample_size = min(5, len(df))
            sample = df.sample(sample_size).to_dict(orient="records")
            
            # Add sample to report
            report_data["sample_data"] = sample
        
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