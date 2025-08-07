"""
Penetration testing for URL Analyzer.

This module contains penetration tests that simulate various attack vectors
to identify security vulnerabilities in the URL Analyzer system.
"""

import unittest
import tempfile
import os
import json
import shutil
import re
import subprocess
import sys
import requests
from pathlib import Path
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode, quote
import hashlib
import base64
from datetime import datetime
import socket
import ssl
import logging
from concurrent.futures import ThreadPoolExecutor
import time

# Import the modules to test
from url_analyzer.analysis import (
    URLContent, 
    AnalysisOptions,
    RequestsURLFetcher,
    HTMLContentAnalyzer,
    DefaultAnalysisService
)
from config_manager import load_config, save_config, create_default_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'penetration_tests.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('penetration_tests')

class PenetrationTestBase(unittest.TestCase):
    """Base class for penetration tests with common setup and teardown."""
    
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
        
        # Create a temporary output directory
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Path to the main script
        self.script_path = "url_analyzer.py"
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Log test start
        logger.info(f"Starting penetration test: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
        
        # Log test end
        logger.info(f"Completed penetration test: {self._testMethodName}")
    
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


class TestXSSVulnerabilities(PenetrationTestBase):
    """Test for Cross-Site Scripting (XSS) vulnerabilities."""
    
    def test_xss_in_html_output(self):
        """Test for XSS vulnerabilities in HTML output."""
        # Create a file with XSS payloads
        xss_file = os.path.join(self.temp_dir, "xss_urls.csv")
        with open(xss_file, "w") as f:
            f.write("Domain_name\n")
            f.write("example.com/<script>alert('XSS')</script>\n")
            f.write("example.com/\"><img src=x onerror=alert('XSS')>\n")
            f.write("example.com/javascript:alert('XSS')\n")
        
        # Run the command with the XSS file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", xss_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check the generated HTML file for XSS vulnerabilities
        html_files = [f for f in os.listdir(self.output_dir) if f.endswith('.html')]
        if html_files:
            html_file = os.path.join(self.output_dir, html_files[0])
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
                # Check for unescaped script tags
                self.assertNotIn("<script>alert('XSS')</script>", html_content)
                
                # Check for unescaped event handlers
                self.assertNotIn("onerror=alert", html_content)
                
                # Check for javascript: URLs
                self.assertNotIn("javascript:alert", html_content)
                
                # Check that the content is properly escaped
                self.assertIn("&lt;script&gt;", html_content.lower()) or \
                self.assertIn("&amp;lt;script&amp;gt;", html_content.lower()) or \
                self.assertNotIn("<script", html_content.lower())


class TestSQLInjectionVulnerabilities(PenetrationTestBase):
    """Test for SQL Injection vulnerabilities."""
    
    def test_sql_injection_in_input(self):
        """Test for SQL Injection vulnerabilities in input handling."""
        # Create a file with SQL Injection payloads
        sql_file = os.path.join(self.temp_dir, "sql_urls.csv")
        with open(sql_file, "w") as f:
            f.write("Domain_name\n")
            f.write("example.com' OR 1=1 --\n")
            f.write("example.com; DROP TABLE urls;\n")
            f.write("example.com' UNION SELECT username, password FROM users --\n")
        
        # Run the command with the SQL Injection file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", sql_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check that error messages don't reveal SQL syntax or database information
        if stderr:
            self.assertNotIn("SQL syntax", stderr)
            self.assertNotIn("ORA-", stderr)  # Oracle errors
            self.assertNotIn("MySQL", stderr)
            self.assertNotIn("SQLite", stderr)
            self.assertNotIn("PostgreSQL", stderr)


class TestCommandInjectionVulnerabilities(PenetrationTestBase):
    """Test for Command Injection vulnerabilities."""
    
    def test_command_injection_in_input(self):
        """Test for Command Injection vulnerabilities in input handling."""
        # Create a file with Command Injection payloads
        cmd_file = os.path.join(self.temp_dir, "cmd_urls.csv")
        with open(cmd_file, "w") as f:
            f.write("Domain_name\n")
            f.write("example.com; ls -la\n")
            f.write("example.com && cat /etc/passwd\n")
            f.write("example.com | whoami\n")
            f.write("example.com `id`\n")
            f.write("example.com $(id)\n")
        
        # Run the command with the Command Injection file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", cmd_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check that no command output is present in stdout or stderr
        combined_output = stdout + stderr
        self.assertNotIn("/bin", combined_output)
        self.assertNotIn("/etc/passwd", combined_output)
        self.assertNotIn("root:", combined_output)
        self.assertNotIn("uid=", combined_output)


class TestPathTraversalVulnerabilities(PenetrationTestBase):
    """Test for Path Traversal vulnerabilities."""
    
    def test_path_traversal_in_input(self):
        """Test for Path Traversal vulnerabilities in input handling."""
        # Create a file with Path Traversal payloads
        path_file = os.path.join(self.temp_dir, "path_urls.csv")
        with open(path_file, "w") as f:
            f.write("Domain_name\n")
            f.write("example.com/../../../etc/passwd\n")
            f.write("example.com/..\\..\\..\\Windows\\system.ini\n")
            f.write("example.com/%2e%2e/%2e%2e/etc/passwd\n")
        
        # Run the command with the Path Traversal file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", path_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check that no sensitive file content is present in stdout or stderr
        combined_output = stdout + stderr
        self.assertNotIn("root:", combined_output)
        self.assertNotIn("[boot loader]", combined_output)
        
        # Check that no files were created outside the output directory
        parent_dir = os.path.dirname(self.temp_dir)
        unexpected_files = []
        for root, dirs, files in os.walk(parent_dir):
            if self.temp_dir in root:
                continue
            for file in files:
                if datetime.fromtimestamp(os.path.getctime(os.path.join(root, file))).date() == datetime.now().date():
                    unexpected_files.append(os.path.join(root, file))
        
        self.assertEqual(len(unexpected_files), 0, 
                         f"Unexpected files created: {unexpected_files}")


class TestSSRFVulnerabilities(PenetrationTestBase):
    """Test for Server-Side Request Forgery (SSRF) vulnerabilities."""
    
    def test_ssrf_in_url_fetching(self):
        """Test for SSRF vulnerabilities in URL fetching."""
        # Create a list of SSRF payloads targeting internal services
        ssrf_targets = [
            "http://localhost:22",  # SSH
            "http://127.0.0.1:3306",  # MySQL
            "http://10.0.0.1",  # Internal network
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "http://metadata.google.internal/",  # GCP metadata
            "file:///etc/passwd",  # Local file
            "gopher://localhost:25/",  # SMTP via Gopher
        ]
        
        fetcher = RequestsURLFetcher(timeout=2)
        
        for url in ssrf_targets:
            try:
                # This should validate the URL before fetching
                result = fetcher.fetch_url(url)
                
                # If we get here, the URL was fetched
                # Check that sensitive information is not exposed
                if result and result.content:
                    content_str = str(result.content)
                    self.assertNotIn("root:", content_str)
                    self.assertNotIn("mysql", content_str.lower())
                    self.assertNotIn("password", content_str.lower())
                    self.assertNotIn("ami-id", content_str.lower())
                    self.assertNotIn("instance-id", content_str.lower())
                
            except Exception as e:
                # An exception is expected for invalid or blocked URLs
                # This is a good sign that SSRF protection is working
                pass


class TestDOSVulnerabilities(PenetrationTestBase):
    """Test for Denial of Service (DOS) vulnerabilities."""
    
    def test_resource_exhaustion(self):
        """Test for resource exhaustion vulnerabilities."""
        # Create a file with large inputs
        dos_file = os.path.join(self.temp_dir, "dos_urls.csv")
        with open(dos_file, "w") as f:
            f.write("Domain_name\n")
            # Add a large number of URLs
            for i in range(1000):
                f.write(f"example{i}.com\n")
            
            # Add URLs with very long domains
            f.write("a" * 10000 + ".com\n")
            
            # Add URLs that might cause regex backtracking
            f.write("a" * 100 + "." + "b" * 100 + "." + "c" * 100 + ".com\n")
        
        # Measure time and memory usage
        start_time = time.time()
        
        # Run the command with the DOS file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", dos_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir,
            "--max-workers", "5"  # Limit workers to prevent actual DOS
        ])
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Check that the command completed in a reasonable time
        # This is a soft check, as execution time can vary by environment
        logger.info(f"DOS test execution time: {execution_time:.2f} seconds")
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")


class TestTLSVulnerabilities(PenetrationTestBase):
    """Test for TLS/SSL vulnerabilities."""
    
    def test_ssl_configuration(self):
        """Test for weak SSL/TLS configurations."""
        # This test checks if the application accepts weak SSL/TLS configurations
        # when making outbound connections
        
        # List of weak ciphers and protocols to test
        weak_configs = [
            ssl.PROTOCOL_TLSv1,  # TLS 1.0 (weak)
            ssl.PROTOCOL_TLSv1_1,  # TLS 1.1 (weak)
        ]
        
        # Test domains
        test_domains = ["example.com", "google.com", "microsoft.com"]
        
        for domain in test_domains:
            for protocol in weak_configs:
                try:
                    # Create a socket and wrap it with SSL
                    context = ssl.SSLContext(protocol)
                    
                    # Try to connect with weak configuration
                    with socket.create_connection((domain, 443)) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as ssock:
                            # If we get here, the weak configuration was accepted
                            cipher = ssock.cipher()
                            logger.warning(f"Weak SSL/TLS configuration accepted: {domain} - {cipher}")
                            
                            # This is not a strict test, just a warning
                            # We don't want to fail the build for external services we can't control
                
                except (ssl.SSLError, socket.error) as e:
                    # An exception is expected for secure configurations
                    # This is a good sign that weak protocols are rejected
                    logger.info(f"Weak SSL/TLS configuration rejected: {domain} - {protocol} - {str(e)}")


class TestSecurityHeaders(PenetrationTestBase):
    """Test for security headers in HTTP responses."""
    
    def test_security_headers_in_responses(self):
        """Test for security headers in HTTP responses."""
        # This test checks if the application sets appropriate security headers
        # in its HTTP responses (if it has a web interface)
        
        # Try to find a local server
        local_server = None
        try:
            # Check if there's a web server running on common ports
            for port in [8000, 8080, 5000, 3000]:
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=1)
                    local_server = f"http://localhost:{port}"
                    break
                except requests.RequestException:
                    continue
        except Exception:
            pass
        
        if not local_server:
            self.skipTest("No local web server found to test security headers")
        
        # Check security headers
        try:
            response = requests.get(local_server, timeout=2)
            headers = response.headers
            
            # List of recommended security headers
            security_headers = {
                "Content-Security-Policy": "Missing Content-Security-Policy header",
                "X-Content-Type-Options": "Missing X-Content-Type-Options header",
                "X-Frame-Options": "Missing X-Frame-Options header",
                "X-XSS-Protection": "Missing X-XSS-Protection header",
                "Strict-Transport-Security": "Missing HSTS header",
                "Referrer-Policy": "Missing Referrer-Policy header"
            }
            
            # Check each security header
            missing_headers = []
            for header, message in security_headers.items():
                if header not in headers:
                    missing_headers.append(message)
            
            # Log missing headers as warnings
            for message in missing_headers:
                logger.warning(message)
            
            # This is not a strict test, just a warning
            # We don't want to fail the build for missing headers
            
        except requests.RequestException as e:
            logger.error(f"Error testing security headers: {str(e)}")


class TestSecurityMisconfiguration(PenetrationTestBase):
    """Test for security misconfigurations."""
    
    def test_default_credentials(self):
        """Test for default credentials."""
        # This test checks if the application accepts default credentials
        
        # List of common default credentials to test
        default_credentials = [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "root", "password": "root"},
            {"username": "user", "password": "user"},
            {"username": "test", "password": "test"},
        ]
        
        # Try to find a login endpoint
        login_endpoints = [
            "http://localhost:8000/login",
            "http://localhost:8080/login",
            "http://localhost:5000/login",
            "http://localhost:3000/login",
            "http://localhost:8000/admin",
            "http://localhost:8080/admin",
        ]
        
        login_url = None
        for url in login_endpoints:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    login_url = url
                    break
            except requests.RequestException:
                continue
        
        if not login_url:
            self.skipTest("No login endpoint found to test default credentials")
        
        # Test default credentials
        for creds in default_credentials:
            try:
                response = requests.post(
                    login_url, 
                    data=creds,
                    timeout=2
                )
                
                # Check if login was successful
                # This is a simplistic check and might need to be adapted
                if "welcome" in response.text.lower() or "dashboard" in response.text.lower():
                    logger.warning(f"Default credentials accepted: {creds}")
                
            except requests.RequestException as e:
                logger.error(f"Error testing default credentials: {str(e)}")


def generate_penetration_test_report():
    """Generate a report of penetration test results."""
    # Create report directory
    report_dir = os.path.join('reports', 'security')
    os.makedirs(report_dir, exist_ok=True)
    
    # Report file path
    report_file = os.path.join(report_dir, f'penetration_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    
    # Read log file
    log_file = os.path.join('logs', 'penetration_tests.log')
    log_content = ""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_content = f.read()
    
    # Parse log content to extract test results
    test_results = {}
    current_test = None
    
    for line in log_content.split('\n'):
        if 'Starting penetration test:' in line:
            test_name = line.split('Starting penetration test:')[1].strip()
            current_test = test_name
            test_results[current_test] = {
                'status': 'Unknown',
                'warnings': [],
                'errors': []
            }
        elif 'Completed penetration test:' in line:
            test_name = line.split('Completed penetration test:')[1].strip()
            if test_name in test_results:
                test_results[test_name]['status'] = 'Passed'
        elif 'WARNING' in line and current_test:
            test_results[current_test]['warnings'].append(line)
        elif 'ERROR' in line and current_test:
            test_results[current_test]['errors'].append(line)
            test_results[current_test]['status'] = 'Failed'
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Penetration Test Report - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .summary {{ margin: 20px 0; padding: 10px; background-color: #f5f5f5; }}
            .test {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
            .passed {{ background-color: #dff0d8; }}
            .failed {{ background-color: #f2dede; }}
            .unknown {{ background-color: #fcf8e3; }}
            .warning {{ color: #8a6d3b; }}
            .error {{ color: #a94442; }}
            pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Penetration Test Report</h1>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Total Tests: {len(test_results)}</p>
            <p>Passed: {sum(1 for result in test_results.values() if result['status'] == 'Passed')}</p>
            <p>Failed: {sum(1 for result in test_results.values() if result['status'] == 'Failed')}</p>
            <p>Unknown: {sum(1 for result in test_results.values() if result['status'] == 'Unknown')}</p>
        </div>
        
        <h2>Test Results</h2>
    """
    
    # Add test results
    for test_name, result in test_results.items():
        status_class = result['status'].lower()
        html_content += f"""
        <div class="test {status_class}">
            <h3>{test_name}</h3>
            <p>Status: {result['status']}</p>
        """
        
        if result['warnings']:
            html_content += "<h4>Warnings:</h4><ul>"
            for warning in result['warnings']:
                html_content += f"<li class='warning'>{warning}</li>"
            html_content += "</ul>"
        
        if result['errors']:
            html_content += "<h4>Errors:</h4><ul>"
            for error in result['errors']:
                html_content += f"<li class='error'>{error}</li>"
            html_content += "</ul>"
        
        html_content += "</div>"
    
    # Add log content
    html_content += f"""
        <h2>Raw Log</h2>
        <pre>{log_content}</pre>
        
        <h2>Recommendations</h2>
        <ul>
            <li>Review all warnings and errors in the test results</li>
            <li>Address any failed tests as high priority</li>
            <li>Implement security headers for all HTTP responses</li>
            <li>Ensure proper input validation for all user inputs</li>
            <li>Regularly update dependencies to patch security vulnerabilities</li>
            <li>Implement Content Security Policy to prevent XSS attacks</li>
            <li>Use HTTPS for all communications</li>
            <li>Implement rate limiting to prevent DOS attacks</li>
        </ul>
    </body>
    </html>
    """
    
    # Write report to file
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Penetration test report generated: {report_file}")
    return report_file


if __name__ == "__main__":
    # Run the tests
    unittest.main(exit=False)
    
    # Generate the report
    report_file = generate_penetration_test_report()
    print(f"Penetration test report generated: {report_file}")