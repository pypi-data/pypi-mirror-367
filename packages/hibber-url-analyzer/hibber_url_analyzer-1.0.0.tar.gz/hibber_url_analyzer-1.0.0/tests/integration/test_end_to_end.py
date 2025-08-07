"""
End-to-End tests for URL Analyzer.

This module contains end-to-end tests that verify the entire URL Analyzer workflow
from command-line interface to report generation. These tests ensure that the
system works correctly as a whole in real-world scenarios.
"""

import unittest
import tempfile
import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
import time
import re
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


class EndToEndTestBase(unittest.TestCase):
    """Base class for end-to-end tests with common setup and teardown."""
    
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
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def run_command(self, command):
        """Run a command and return its output."""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise


class TestCommandLineInterface(EndToEndTestBase):
    """End-to-end tests for the command-line interface."""
    
    def test_help_command(self):
        """Test that the help command works."""
        stdout, stderr = self.run_command([sys.executable, self.script_path, "--help"])
        
        # Verify that help text is displayed
        self.assertIn("usage:", stdout.lower())
        self.assertIn("options:", stdout.lower())
    
    def test_version_command(self):
        """Test that the version command works."""
        stdout, stderr = self.run_command([sys.executable, self.script_path, "--version"])
        
        # Verify that version is displayed
        self.assertRegex(stdout, r"\d+\.\d+\.\d+")
    
    def test_analyze_single_url(self):
        """Test analyzing a single URL from the command line."""
        # Skip this test if we're not connected to the internet
        try:
            import socket
            socket.create_connection(("www.example.com", 80), timeout=1)
        except (socket.timeout, socket.error):
            self.skipTest("No internet connection available")
        
        stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--url", "example.com",
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Verify that analysis was performed
        self.assertIn("analyzing", stdout.lower())
        self.assertIn("completed", stdout.lower())
        
        # Check that output files were created
        html_files = list(Path(self.output_dir).glob("*.html"))
        self.assertGreaterEqual(len(html_files), 1)


class TestFileProcessing(EndToEndTestBase):
    """End-to-end tests for processing files."""
    
    def test_process_csv_file(self):
        """Test processing a CSV file with URLs."""
        # Skip this test if we're not connected to the internet
        try:
            import socket
            socket.create_connection(("www.example.com", 80), timeout=1)
        except (socket.timeout, socket.error):
            self.skipTest("No internet connection available")
        
        stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", self.input_file,
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Verify that analysis was performed
        self.assertIn("processing", stdout.lower())
        self.assertIn("completed", stdout.lower())
        
        # Check that output files were created
        html_files = list(Path(self.output_dir).glob("*.html"))
        self.assertGreaterEqual(len(html_files), 1)


class TestReportGeneration(EndToEndTestBase):
    """End-to-end tests for report generation."""
    
    def test_generate_html_report(self):
        """Test generating an HTML report."""
        # Skip this test if we're not connected to the internet
        try:
            import socket
            socket.create_connection(("www.example.com", 80), timeout=1)
        except (socket.timeout, socket.error):
            self.skipTest("No internet connection available")
        
        # First, analyze a URL
        self.run_command([
            sys.executable, 
            self.script_path, 
            "--url", "example.com",
            "--config", self.config_file,
            "--cache", self.cache_file,
            "--output-dir", self.output_dir
        ])
        
        # Check that HTML report was created
        html_files = list(Path(self.output_dir).glob("*.html"))
        self.assertGreaterEqual(len(html_files), 1)
        
        # Verify the content of the HTML report
        with open(html_files[0], "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Check for common HTML elements
        self.assertIn("<html", html_content.lower())
        self.assertIn("<body", html_content.lower())
        self.assertIn("example.com", html_content)


class TestCompleteWorkflow(EndToEndTestBase):
    """End-to-end tests for the complete URL Analyzer workflow."""
    
    def test_complete_workflow(self):
        """Test the complete URL Analyzer workflow."""
        # Skip this test if we're not connected to the internet
        try:
            import socket
            socket.create_connection(("www.example.com", 80), timeout=1)
        except (socket.timeout, socket.error):
            self.skipTest("No internet connection available")
        
        # 1. Create a custom configuration
        config = create_default_config()
        config["scan_settings"]["timeout"] = 10
        config["scan_settings"]["cache_file"] = self.cache_file
        save_config(config, self.config_file)
        
        # 2. Process a file with URLs
        stdout, stderr = self.run_command([
            sys.executable, 
            self.script_path, 
            "--file", self.input_file,
            "--config", self.config_file,
            "--output-dir", self.output_dir,
            "--verbose"
        ])
        
        # 3. Verify that analysis was performed
        self.assertIn("processing", stdout.lower())
        self.assertIn("completed", stdout.lower())
        
        # 4. Check that output files were created
        html_files = list(Path(self.output_dir).glob("*.html"))
        self.assertGreaterEqual(len(html_files), 1)
        
        # 5. Verify the content of the HTML report
        with open(html_files[0], "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Check for common HTML elements and content
        self.assertIn("<html", html_content.lower())
        self.assertIn("<body", html_content.lower())
        self.assertIn("example.com", html_content)
        
        # 6. Check that cache file was created
        self.assertTrue(os.path.exists(self.cache_file))
        
        # 7. Verify cache file content
        with open(self.cache_file, "r") as f:
            cache_data = json.load(f)
        
        self.assertIsInstance(cache_data, dict)
        self.assertGreaterEqual(len(cache_data), 1)


if __name__ == "__main__":
    unittest.main()