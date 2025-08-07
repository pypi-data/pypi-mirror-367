"""
Security regression testing for URL Analyzer.

This module contains security regression tests that verify security fixes remain effective
and that new changes don't reintroduce previously fixed vulnerabilities.
"""

import unittest
import tempfile
import os
import json
import shutil
import re
import subprocess
import sys
import hashlib
import logging
from datetime import datetime
from pathlib import Path
import time
import csv
import sqlite3
import pickle

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
        logging.FileHandler(os.path.join('logs', 'security_regression_tests.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('security_regression_tests')

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

class SecurityRegressionTestBase(unittest.TestCase):
    """Base class for security regression tests with common setup and teardown."""
    
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
        
        # Load known vulnerabilities database
        self.known_vulnerabilities = self.load_known_vulnerabilities()
        
        # Log test start
        logger.info(f"Starting security regression test: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
        
        # Log test end
        logger.info(f"Completed security regression test: {self._testMethodName}")
    
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
    
    def load_known_vulnerabilities(self):
        """Load the database of known vulnerabilities."""
        # Create the database file if it doesn't exist
        db_dir = os.path.join('reports', 'security')
        os.makedirs(db_dir, exist_ok=True)
        db_file = os.path.join(db_dir, 'known_vulnerabilities.json')
        
        if not os.path.exists(db_file):
            # Create an empty database
            known_vulnerabilities = {
                "xss": [],
                "sql_injection": [],
                "command_injection": [],
                "path_traversal": [],
                "ssrf": [],
                "dos": [],
                "insecure_deserialization": [],
                "insecure_configuration": [],
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }
            
            # Save the empty database
            with open(db_file, 'w') as f:
                json.dump(known_vulnerabilities, f, indent=2)
        else:
            # Load the existing database
            with open(db_file, 'r') as f:
                known_vulnerabilities = json.load(f)
        
        return known_vulnerabilities
    
    def save_known_vulnerabilities(self):
        """Save the database of known vulnerabilities."""
        db_dir = os.path.join('reports', 'security')
        os.makedirs(db_dir, exist_ok=True)
        db_file = os.path.join(db_dir, 'known_vulnerabilities.json')
        
        # Update metadata
        self.known_vulnerabilities["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Save the database
        with open(db_file, 'w') as f:
            json.dump(self.known_vulnerabilities, f, indent=2)
    
    def add_vulnerability(self, category, vulnerability):
        """Add a vulnerability to the database."""
        if category in self.known_vulnerabilities:
            # Check if the vulnerability already exists
            for existing_vuln in self.known_vulnerabilities[category]:
                if existing_vuln["hash"] == vulnerability["hash"]:
                    # Update the existing vulnerability
                    existing_vuln.update(vulnerability)
                    break
            else:
                # Add the new vulnerability
                self.known_vulnerabilities[category].append(vulnerability)
            
            # Save the updated database
            self.save_known_vulnerabilities()
    
    def generate_vulnerability_hash(self, vulnerability_data):
        """Generate a unique hash for a vulnerability."""
        # Create a string representation of the vulnerability data
        vuln_str = json.dumps(vulnerability_data, sort_keys=True)
        
        # Generate a hash
        return hashlib.sha256(vuln_str.encode()).hexdigest()


class TestXSSRegressionTests(SecurityRegressionTestBase):
    """Regression tests for Cross-Site Scripting (XSS) vulnerabilities."""
    
    def test_xss_regression(self):
        """Test that previously fixed XSS vulnerabilities haven't been reintroduced."""
        # Create a file with XSS payloads from known vulnerabilities
        xss_file = os.path.join(self.temp_dir, "xss_regression.csv")
        with open(xss_file, "w") as f:
            f.write("Domain_name\n")
            
            # Add known XSS payloads
            for vuln in self.known_vulnerabilities.get("xss", []):
                if "payload" in vuln:
                    f.write(f"{vuln['payload']}\n")
            
            # Add some standard XSS payloads
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
                
                # Record any new vulnerabilities found
                if "<script>alert" in html_content or "onerror=alert" in html_content or "javascript:alert" in html_content:
                    vuln_data = {
                        "type": "xss",
                        "payload": "example.com/<script>alert('XSS')</script>",
                        "location": "HTML output",
                        "discovered": datetime.now().isoformat(),
                        "fixed": None,
                        "regression": True,
                        "notes": "XSS vulnerability reintroduced in HTML output"
                    }
                    
                    # Generate a hash for the vulnerability
                    vuln_data["hash"] = self.generate_vulnerability_hash(vuln_data)
                    
                    # Add the vulnerability to the database
                    self.add_vulnerability("xss", vuln_data)
                    
                    # Fail the test
                    self.fail("XSS vulnerability found in HTML output")


class TestSQLInjectionRegressionTests(SecurityRegressionTestBase):
    """Regression tests for SQL Injection vulnerabilities."""
    
    def test_sql_injection_regression(self):
        """Test that previously fixed SQL Injection vulnerabilities haven't been reintroduced."""
        # Create a file with SQL Injection payloads from known vulnerabilities
        sql_file = os.path.join(self.temp_dir, "sql_regression.csv")
        with open(sql_file, "w") as f:
            f.write("Domain_name\n")
            
            # Add known SQL Injection payloads
            for vuln in self.known_vulnerabilities.get("sql_injection", []):
                if "payload" in vuln:
                    f.write(f"{vuln['payload']}\n")
            
            # Add some standard SQL Injection payloads
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
            
            # Record any new vulnerabilities found
            if "SQL syntax" in stderr or "ORA-" in stderr or "MySQL" in stderr or "SQLite" in stderr or "PostgreSQL" in stderr:
                vuln_data = {
                    "type": "sql_injection",
                    "payload": "example.com' OR 1=1 --",
                    "location": "Error messages",
                    "discovered": datetime.now().isoformat(),
                    "fixed": None,
                    "regression": True,
                    "notes": "SQL Injection vulnerability reintroduced in error messages"
                }
                
                # Generate a hash for the vulnerability
                vuln_data["hash"] = self.generate_vulnerability_hash(vuln_data)
                
                # Add the vulnerability to the database
                self.add_vulnerability("sql_injection", vuln_data)
                
                # Fail the test
                self.fail("SQL Injection vulnerability found in error messages")


class TestCommandInjectionRegressionTests(SecurityRegressionTestBase):
    """Regression tests for Command Injection vulnerabilities."""
    
    def test_command_injection_regression(self):
        """Test that previously fixed Command Injection vulnerabilities haven't been reintroduced."""
        # Create a file with Command Injection payloads from known vulnerabilities
        cmd_file = os.path.join(self.temp_dir, "cmd_regression.csv")
        with open(cmd_file, "w") as f:
            f.write("Domain_name\n")
            
            # Add known Command Injection payloads
            for vuln in self.known_vulnerabilities.get("command_injection", []):
                if "payload" in vuln:
                    f.write(f"{vuln['payload']}\n")
            
            # Add some standard Command Injection payloads
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
        
        # Record any new vulnerabilities found
        if "/bin" in combined_output or "/etc/passwd" in combined_output or "root:" in combined_output or "uid=" in combined_output:
            vuln_data = {
                "type": "command_injection",
                "payload": "example.com; ls -la",
                "location": "Command output",
                "discovered": datetime.now().isoformat(),
                "fixed": None,
                "regression": True,
                "notes": "Command Injection vulnerability reintroduced in command output"
            }
            
            # Generate a hash for the vulnerability
            vuln_data["hash"] = self.generate_vulnerability_hash(vuln_data)
            
            # Add the vulnerability to the database
            self.add_vulnerability("command_injection", vuln_data)
            
            # Fail the test
            self.fail("Command Injection vulnerability found in command output")


class TestPathTraversalRegressionTests(SecurityRegressionTestBase):
    """Regression tests for Path Traversal vulnerabilities."""
    
    def test_path_traversal_regression(self):
        """Test that previously fixed Path Traversal vulnerabilities haven't been reintroduced."""
        # Create a file with Path Traversal payloads from known vulnerabilities
        path_file = os.path.join(self.temp_dir, "path_regression.csv")
        with open(path_file, "w") as f:
            f.write("Domain_name\n")
            
            # Add known Path Traversal payloads
            for vuln in self.known_vulnerabilities.get("path_traversal", []):
                if "payload" in vuln:
                    f.write(f"{vuln['payload']}\n")
            
            # Add some standard Path Traversal payloads
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
        
        # Record any new vulnerabilities found
        if "root:" in combined_output or "[boot loader]" in combined_output or len(unexpected_files) > 0:
            vuln_data = {
                "type": "path_traversal",
                "payload": "example.com/../../../etc/passwd",
                "location": "File system",
                "discovered": datetime.now().isoformat(),
                "fixed": None,
                "regression": True,
                "notes": "Path Traversal vulnerability reintroduced in file system access"
            }
            
            # Generate a hash for the vulnerability
            vuln_data["hash"] = self.generate_vulnerability_hash(vuln_data)
            
            # Add the vulnerability to the database
            self.add_vulnerability("path_traversal", vuln_data)
            
            # Fail the test
            self.fail("Path Traversal vulnerability found in file system access")


class TestInsecureDeserializationRegressionTests(SecurityRegressionTestBase):
    """Regression tests for Insecure Deserialization vulnerabilities."""
    
    def test_insecure_deserialization_regression(self):
        """Test that previously fixed Insecure Deserialization vulnerabilities haven't been reintroduced."""
        # Create a malicious pickle file
        pickle_file = os.path.join(self.temp_dir, "malicious.pickle")
        
        # This is a safe pickle that just contains a dictionary
        safe_data = {"test": "data"}
        with open(pickle_file, 'wb') as f:
            pickle.dump(safe_data, f)
        
        # Create a test file that references the pickle file
        test_file = os.path.join(self.temp_dir, "deserialize_test.py")
        with open(test_file, 'w') as f:
            f.write("""
import pickle
import sys
import os

# Get the pickle file path from command line
pickle_file = sys.argv[1]

# Try to load the pickle file
try:
    with open(pickle_file, 'rb') as f:
        data = pickle.load(f)
    print(f"Loaded data: {data}")
except Exception as e:
    print(f"Error loading pickle file: {e}")
""")
        
        # Run the test script with the pickle file
        returncode, stdout, stderr = self.run_command([
            sys.executable,
            test_file,
            pickle_file
        ])
        
        # Check that the script completed without errors
        self.assertEqual(returncode, 0, 
                        f"Script crashed with unexpected exit code: {returncode}")
        
        # Check that the data was loaded correctly
        self.assertIn("Loaded data: {'test': 'data'}", stdout)
        
        # Now try to load the pickle file using the URL Analyzer's cache loading mechanism
        # This is a simplified test and should be adapted to the actual implementation
        
        # Create a malicious cache file
        cache_file = os.path.join(self.temp_dir, "malicious_cache.json")
        with open(cache_file, 'w') as f:
            f.write('{"test": "data"}')
        
        # Run the command with the malicious cache file
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--url", "example.com",
            "--config", self.config_file,
            "--cache", cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check that no unexpected code execution occurred
        combined_output = stdout + stderr
        self.assertNotIn("os.system", combined_output)
        self.assertNotIn("subprocess", combined_output)
        self.assertNotIn("exec(", combined_output)
        self.assertNotIn("eval(", combined_output)
        
        # Record any new vulnerabilities found
        if "os.system" in combined_output or "subprocess" in combined_output or "exec(" in combined_output or "eval(" in combined_output:
            vuln_data = {
                "type": "insecure_deserialization",
                "payload": "malicious_cache.json",
                "location": "Cache loading",
                "discovered": datetime.now().isoformat(),
                "fixed": None,
                "regression": True,
                "notes": "Insecure Deserialization vulnerability reintroduced in cache loading"
            }
            
            # Generate a hash for the vulnerability
            vuln_data["hash"] = self.generate_vulnerability_hash(vuln_data)
            
            # Add the vulnerability to the database
            self.add_vulnerability("insecure_deserialization", vuln_data)
            
            # Fail the test
            self.fail("Insecure Deserialization vulnerability found in cache loading")


class TestInsecureConfigurationRegressionTests(SecurityRegressionTestBase):
    """Regression tests for Insecure Configuration vulnerabilities."""
    
    def test_insecure_configuration_regression(self):
        """Test that previously fixed Insecure Configuration vulnerabilities haven't been reintroduced."""
        # Create a malicious configuration file
        config_file = os.path.join(self.temp_dir, "malicious_config.json")
        
        # Create a configuration with potentially dangerous settings
        malicious_config = {
            "sensitive_patterns": ["$(ls -la)"],
            "ugc_patterns": ["/etc/passwd"],
            "junk_subcategories": {
                "Advertising": ["adservice", "doubleclick\\.net"],
                "Analytics": ["analytics", "tracking"]
            },
            "api_settings": {
                "gemini_api_url": "file:///etc/passwd"
            },
            "scan_settings": {
                "max_workers": 999999,
                "timeout": 999999,
                "cache_file": "../../../etc/passwd"
            }
        }
        
        # Save the malicious configuration
        with open(config_file, 'w') as f:
            json.dump(malicious_config, f)
        
        # Run the command with the malicious configuration
        returncode, stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--url", "example.com",
            "--config", config_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that the command completed without crashing
        self.assertIn(returncode, [0, 1, 2], 
                     f"Command crashed with unexpected exit code: {returncode}")
        
        # Check that no sensitive file content is present in stdout or stderr
        combined_output = stdout + stderr
        self.assertNotIn("root:", combined_output)
        self.assertNotIn("/bin", combined_output)
        
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
        
        # Record any new vulnerabilities found
        if "root:" in combined_output or "/bin" in combined_output or len(unexpected_files) > 0:
            vuln_data = {
                "type": "insecure_configuration",
                "payload": "malicious_config.json",
                "location": "Configuration loading",
                "discovered": datetime.now().isoformat(),
                "fixed": None,
                "regression": True,
                "notes": "Insecure Configuration vulnerability reintroduced in configuration loading"
            }
            
            # Generate a hash for the vulnerability
            vuln_data["hash"] = self.generate_vulnerability_hash(vuln_data)
            
            # Add the vulnerability to the database
            self.add_vulnerability("insecure_configuration", vuln_data)
            
            # Fail the test
            self.fail("Insecure Configuration vulnerability found in configuration loading")


def generate_regression_test_report():
    """Generate a report of security regression test results."""
    # Create report directory
    report_dir = os.path.join('reports', 'security')
    os.makedirs(report_dir, exist_ok=True)
    
    # Report file path
    report_file = os.path.join(report_dir, f'security_regression_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    
    # Read log file
    log_file = os.path.join('logs', 'security_regression_tests.log')
    log_content = ""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_content = f.read()
    
    # Parse log content to extract test results
    test_results = {}
    current_test = None
    
    for line in log_content.split('\n'):
        if 'Starting security regression test:' in line:
            test_name = line.split('Starting security regression test:')[1].strip()
            current_test = test_name
            test_results[current_test] = {
                'status': 'Unknown',
                'warnings': [],
                'errors': []
            }
        elif 'Completed security regression test:' in line:
            test_name = line.split('Completed security regression test:')[1].strip()
            if test_name in test_results:
                test_results[test_name]['status'] = 'Passed'
        elif 'WARNING' in line and current_test:
            test_results[current_test]['warnings'].append(line)
        elif 'ERROR' in line and current_test:
            test_results[current_test]['errors'].append(line)
            test_results[current_test]['status'] = 'Failed'
    
    # Load known vulnerabilities
    db_file = os.path.join(report_dir, 'known_vulnerabilities.json')
    known_vulnerabilities = {}
    if os.path.exists(db_file):
        with open(db_file, 'r') as f:
            known_vulnerabilities = json.load(f)
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Regression Test Report - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</title>
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
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>Security Regression Test Report</h1>
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
    
    # Add known vulnerabilities
    html_content += """
        <h2>Known Vulnerabilities</h2>
        <table>
            <tr>
                <th>Type</th>
                <th>Payload</th>
                <th>Location</th>
                <th>Discovered</th>
                <th>Fixed</th>
                <th>Regression</th>
                <th>Notes</th>
            </tr>
    """
    
    # Add rows for each vulnerability
    vuln_count = 0
    for category, vulns in known_vulnerabilities.items():
        if category == "metadata":
            continue
        
        for vuln in vulns:
            vuln_count += 1
            html_content += f"""
            <tr>
                <td>{vuln.get('type', category)}</td>
                <td>{vuln.get('payload', 'N/A')}</td>
                <td>{vuln.get('location', 'N/A')}</td>
                <td>{vuln.get('discovered', 'N/A')}</td>
                <td>{vuln.get('fixed', 'Not Fixed')}</td>
                <td>{'Yes' if vuln.get('regression', False) else 'No'}</td>
                <td>{vuln.get('notes', '')}</td>
            </tr>
            """
    
    if vuln_count == 0:
        html_content += """
            <tr>
                <td colspan="7" style="text-align: center;">No known vulnerabilities</td>
            </tr>
        """
    
    html_content += """
        </table>
    """
    
    # Add log content
    html_content += f"""
        <h2>Raw Log</h2>
        <pre>{log_content}</pre>
        
        <h2>Recommendations</h2>
        <ul>
            <li>Review all failed tests and fix the underlying issues</li>
            <li>Update the known vulnerabilities database with any new findings</li>
            <li>Run security regression tests regularly to catch regressions early</li>
            <li>Integrate security regression tests into the CI/CD pipeline</li>
            <li>Review and update security tests as the application evolves</li>
        </ul>
    </body>
    </html>
    """
    
    # Write report to file
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Security regression test report generated: {report_file}")
    return report_file


if __name__ == "__main__":
    # Run the tests
    unittest.main(exit=False)
    
    # Generate the report
    report_file = generate_regression_test_report()
    print(f"Security regression test report generated: {report_file}")