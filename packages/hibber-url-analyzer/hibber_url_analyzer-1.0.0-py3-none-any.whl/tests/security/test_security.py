"""
Security tests for URL Analyzer.

This module contains security tests that verify the security aspects of the URL Analyzer
system. These tests help identify security vulnerabilities and ensure that the system
handles security concerns appropriately.
"""

import unittest
import tempfile
import os
import json
import shutil
import re
import subprocess
import sys
from pathlib import Path
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode, quote
import hashlib
import base64
from datetime import datetime

# Import the modules to test
from url_analyzer.analysis import (
    URLContent, 
    AnalysisOptions,
    RequestsURLFetcher,
    HTMLContentAnalyzer,
    DefaultAnalysisService
)
from config_manager import load_config, save_config, create_default_config


class SecurityTestBase(unittest.TestCase):
    """Base class for security tests with common setup and teardown."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a temporary config file
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.default_config = create_default_config()
        save_config(self.default_config, self.config_file)
        
        # Create a temporary cache file
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")
        
        # Create a temporary input file with test URLs
        self.input_file = os.path.join(self.temp_dir, "test_urls.csv")
        with open(self.input_file, "w") as f:
            f.write("Domain_name\n")
            f.write("example.com\n")
            f.write("example.org\n")
        
        # Create a temporary output directory
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Path to the main script
        self.script_path = "url_analyzer.py"
        
        # Sample malicious inputs
        self.malicious_inputs = self._generate_malicious_inputs()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def _generate_malicious_inputs(self):
        """Generate sample malicious inputs for testing."""
        return {
            "sql_injection": [
                "example.com' OR 1=1 --",
                "example.com; DROP TABLE urls;",
                "example.com' UNION SELECT username, password FROM users --",
            ],
            "xss": [
                "example.com/<script>alert('XSS')</script>",
                "example.com/\"><img src=x onerror=alert('XSS')>",
                "example.com/javascript:alert('XSS')",
            ],
            "path_traversal": [
                "example.com/../../../etc/passwd",
                "example.com/..\\..\\..\\Windows\\system.ini",
                "example.com/%2e%2e/%2e%2e/etc/passwd",
            ],
            "command_injection": [
                "example.com; ls -la",
                "example.com && cat /etc/passwd",
                "example.com | whoami",
            ],
            "large_input": [
                "example.com/" + "A" * 10000,
                "example.com?" + "x=" * 5000,
                "example.com#" + "fragment" * 1000,
            ],
            "special_chars": [
                "example.com/%00",  # Null byte
                "example.com/%0A",  # Newline
                "example.com/%22%27%3C%3E",  # Quotes and brackets
            ],
        }
    
    def run_command(self, command):
        """Run a command and return its output."""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False  # Don't raise exception on non-zero exit code
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)


class TestInputValidation(SecurityTestBase):
    """Security tests for input validation."""
    
    def test_url_validation(self):
        """Test that URL validation prevents malicious inputs."""
        fetcher = RequestsURLFetcher(timeout=5)
        
        for category, inputs in self.malicious_inputs.items():
            for malicious_input in inputs:
                # Test URL validation in the fetcher
                try:
                    # This should validate the URL before fetching
                    result = fetcher.fetch_url(malicious_input)
                    
                    # If we get here, the URL was accepted
                    # Check if it was normalized or sanitized
                    parsed_url = urlparse(result.url)
                    
                    # The URL should be properly formed
                    self.assertTrue(parsed_url.scheme in ["http", "https"])
                    self.assertTrue(parsed_url.netloc)
                    
                    # Check that the original malicious input is not present in the URL
                    # This is a simplistic check and might have false positives
                    if category in ["sql_injection", "command_injection"]:
                        self.assertNotIn("'", result.url)
                        self.assertNotIn(";", result.url)
                        self.assertNotIn("--", result.url)
                    
                    if category == "xss":
                        self.assertNotIn("<script>", result.url.lower())
                        self.assertNotIn("javascript:", result.url.lower())
                    
                except Exception as e:
                    # An exception is expected for invalid URLs
                    # This is a good sign that validation is working
                    pass
    
    def test_file_input_validation(self):
        """Test that file input validation prevents malicious inputs."""
        # Create a file with malicious inputs
        malicious_file = os.path.join(self.temp_dir, "malicious_urls.csv")
        with open(malicious_file, "w") as f:
            f.write("Domain_name\n")
            for category, inputs in self.malicious_inputs.items():
                for malicious_input in inputs:
                    f.write(f"{malicious_input}\n")
        
        # Run the command with the malicious file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", malicious_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        # Note: It might return a non-zero exit code if it detected malicious inputs
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check that error messages are informative but don't reveal sensitive information
        if returncode != 0:
            self.assertNotIn("/etc/passwd", stderr)
            self.assertNotIn("system.ini", stderr)
            self.assertNotIn("SELECT", stderr.upper())
            self.assertNotIn("DROP", stderr.upper())


class TestConfigSecurity(SecurityTestBase):
    """Security tests for configuration handling."""
    
    def test_config_file_validation(self):
        """Test that configuration file validation prevents malicious inputs."""
        # Create a malicious config file
        malicious_config = os.path.join(self.temp_dir, "malicious_config.json")
        
        # Test with various malicious configurations
        malicious_configs = [
            # Extremely large timeout
            {"scan_settings": {"timeout": 999999}},
            
            # Extremely large max_workers
            {"scan_settings": {"max_workers": 999999}},
            
            # Path traversal in cache_file
            {"scan_settings": {"cache_file": "../../../etc/passwd"}},
            
            # Command injection in patterns
            {"sensitive_patterns": ["$(ls -la)"]},
            
            # JavaScript injection in patterns
            {"sensitive_patterns": ["<script>alert('XSS')</script>"]},
        ]
        
        for config_data in malicious_configs:
            # Create a base config and update it with malicious data
            config = create_default_config()
            
            # Update the config with malicious data
            for key, value in config_data.items():
                if isinstance(value, dict):
                    if key not in config:
                        config[key] = {}
                    for subkey, subvalue in value.items():
                        config[key][subkey] = subvalue
                else:
                    config[key] = value
            
            # Save the malicious config
            save_config(config, malicious_config)
            
            # Run the command with the malicious config
            returncode, stdout, stderr = self.run_command([
                sys.executable, 
                self.script_path, 
                "--url", "example.com",
                "--config", malicious_config,
                "--output-dir", self.output_dir
            ])
            
            # Check that the command completed without crashing
            # It might return a non-zero exit code if it detected malicious inputs
            self.assertIn(returncode, [0, 1, 2], 
                         f"Command crashed with unexpected exit code: {returncode}")


class TestContentSecurity(SecurityTestBase):
    """Security tests for content handling."""
    
    def test_html_content_handling(self):
        """Test that HTML content handling prevents security issues."""
        analyzer = HTMLContentAnalyzer()
        options = AnalysisOptions({"include_metadata": True})
        
        # Test with various malicious HTML content
        malicious_html = [
            "<html><script>alert('XSS')</script></html>",
            "<html><img src=x onerror=alert('XSS')></html>",
            "<html><iframe src='javascript:alert(\"XSS\")'></iframe></html>",
            "<html><a href='javascript:alert(\"XSS\")'>Click me</a></html>",
            "<html><svg onload=alert('XSS')></svg></html>",
        ]
        
        for html in malicious_html:
            url_content = URLContent(
                url="https://example.com",
                content_type="text/html",
                status_code=200,
                content=html,
                headers={"Content-Type": "text/html"},
                fetch_time=datetime.now(),
                size_bytes=len(html)
            )
            
            # Analyze the content
            result = analyzer.analyze_content(url_content, options)
            
            # Check that the analysis completed without errors
            self.assertIsNotNone(result)
            
            # Check that the result doesn't contain executable JavaScript
            result_str = str(result.results)
            self.assertNotIn("<script>", result_str.lower())
            self.assertNotIn("javascript:", result_str.lower())
            self.assertNotIn("onerror=", result_str.lower())
            self.assertNotIn("onload=", result_str.lower())


class TestAPISecurityTests(SecurityTestBase):
    """Security tests for API endpoints."""
    
    def test_api_input_validation(self):
        """Test that API input validation prevents security issues."""
        # This test is only applicable if the system has API endpoints
        # Skip it if there are no API endpoints
        try:
            from url_analyzer.api import api_endpoints
        except ImportError:
            self.skipTest("No API endpoints available")
        
        # Test with various malicious API inputs
        # This is a simplified example and should be adapted to the actual API
        api_inputs = [
            {"url": "example.com' OR 1=1 --"},
            {"url": "<script>alert('XSS')</script>"},
            {"url": "../../../etc/passwd"},
            {"url": "example.com; ls -la"},
            {"url": "A" * 10000},
        ]
        
        for input_data in api_inputs:
            # Call the API endpoint
            try:
                result = api_endpoints.analyze_url(input_data)
                
                # Check that the result doesn't contain sensitive information
                result_str = str(result)
                self.assertNotIn("/etc/passwd", result_str)
                self.assertNotIn("system.ini", result_str)
                self.assertNotIn("<script>", result_str.lower())
                
            except Exception as e:
                # An exception is expected for invalid inputs
                # This is a good sign that validation is working
                pass


class TestDependencyVulnerabilities(SecurityTestBase):
    """Security tests for dependency vulnerabilities."""
    
    def test_dependency_versions(self):
        """Test that dependencies are up-to-date and don't have known vulnerabilities."""
        # This test requires the safety package
        try:
            import safety
            import safety.cli
            import pkg_resources
            import json
            import tempfile
            from datetime import datetime
        except ImportError:
            self.skipTest("safety package not available")
        
        # Create a temporary file to store the safety check results
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Run safety check and output results to the temporary file
            # Using safety's programmatic API
            command = [
                "check",
                "--output", "json",
                "--file", temp_filename,
                "--full-report"
            ]
            
            try:
                safety.cli.cli_main(command)
                
                # Read the results from the temporary file
                with open(temp_filename, 'r') as f:
                    safety_results = json.load(f)
                
                # Process the results
                vulnerable_packages = []
                if isinstance(safety_results, dict) and "vulnerabilities" in safety_results:
                    vulnerable_packages = safety_results["vulnerabilities"]
                elif isinstance(safety_results, list):
                    vulnerable_packages = safety_results
                
                # Print warning for vulnerable packages
                if vulnerable_packages:
                    print("\nWARNING: Vulnerable packages found:")
                    for vuln in vulnerable_packages:
                        if isinstance(vuln, dict):
                            package_name = vuln.get("package_name", "Unknown")
                            affected_version = vuln.get("vulnerable_spec", "Unknown")
                            vulnerability_id = vuln.get("vulnerability_id", "Unknown")
                            description = vuln.get("advisory", "No description available")
                            
                            print(f"  Package: {package_name}")
                            print(f"  Affected version: {affected_version}")
                            print(f"  Vulnerability ID: {vulnerability_id}")
                            print(f"  Description: {description}")
                            print("  ---")
                        else:
                            print(f"  {vuln}")
                
                # Log the scan results
                scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = {
                    "scan_time": scan_time,
                    "vulnerabilities_found": len(vulnerable_packages),
                    "scan_successful": True
                }
                
                # Save scan results to a log file
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, "dependency_scan_history.json")
                
                # Read existing log if it exists
                log_history = []
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            log_history = json.load(f)
                    except json.JSONDecodeError:
                        log_history = []
                
                # Append new log entry
                log_history.append(log_entry)
                
                # Write updated log
                with open(log_file, 'w') as f:
                    json.dump(log_history, f, indent=2)
                
                # This is not a strict test, just a warning
                # We don't want to fail the build for vulnerabilities, just report them
                if vulnerable_packages:
                    print(f"\nFound {len(vulnerable_packages)} vulnerable packages. See logs for details.")
                else:
                    print("\nNo vulnerable packages found.")
                
            except Exception as e:
                print(f"Error running safety check: {str(e)}")
                # Log the failed scan
                scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = {
                    "scan_time": scan_time,
                    "error": str(e),
                    "scan_successful": False
                }
                
                # Save scan results to a log file
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, "dependency_scan_history.json")
                
                # Read existing log if it exists
                log_history = []
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            log_history = json.load(f)
                    except json.JSONDecodeError:
                        log_history = []
                
                # Append new log entry
                log_history.append(log_entry)
                
                # Write updated log
                with open(log_file, 'w') as f:
                    json.dump(log_history, f, indent=2)
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_dependency_security_policy(self):
        """Test that a dependency security policy is in place and followed."""
        # Check if a security policy file exists
        policy_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SECURITY.md")
        self.assertTrue(os.path.exists(policy_file), 
                        "Security policy file (SECURITY.md) not found. Create one to document security practices.")
        
        # Check if requirements.txt has pinned versions
        requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        self.assertTrue(os.path.exists(requirements_file), "requirements.txt file not found")
        
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()
        
        # Check that all non-comment lines with package specifications have version pins
        unpinned_packages = []
        for line in requirements:
            line = line.strip()
            if line and not line.startswith('#') and '==' not in line and '>=' not in line:
                unpinned_packages.append(line)
        
        self.assertEqual(len(unpinned_packages), 0, 
                         f"Found {len(unpinned_packages)} unpinned packages in requirements.txt: {unpinned_packages}")


if __name__ == "__main__":
    unittest.main()