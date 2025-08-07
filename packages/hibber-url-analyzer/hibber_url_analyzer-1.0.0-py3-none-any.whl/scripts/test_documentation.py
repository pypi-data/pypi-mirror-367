#!/usr/bin/env python3
"""
Documentation Testing Script for URL Analyzer

This script validates the documentation files in the URL Analyzer project.
It checks for broken links, code example validity, and consistency across documentation.
"""

import os
import re
import sys
import json
import argparse
import logging
import markdown
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('doc_tester')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DOCS_DIR = PROJECT_ROOT / 'docs'
URL_ANALYZER_DIR = PROJECT_ROOT / 'url_analyzer'


class DocumentationTester:
    """Tests documentation files for various issues."""

    def __init__(self, docs_dir: Path = DOCS_DIR, verbose: bool = False):
        """Initialize the documentation tester.

        Args:
            docs_dir: Path to the documentation directory
            verbose: Whether to print verbose output
        """
        self.docs_dir = docs_dir
        self.verbose = verbose
        self.md_files = list(docs_dir.glob('**/*.md'))
        self.errors = []
        self.warnings = []
        
        # Load module information
        self.modules = self._get_modules()
        
        # Track links between documents
        self.internal_links = {}
        self.external_links = set()
        
        logger.info(f"Found {len(self.md_files)} markdown files in {docs_dir}")

    def _get_modules(self) -> Dict[str, Path]:
        """Get all Python modules in the project.

        Returns:
            Dictionary mapping module names to file paths
        """
        modules = {}
        for py_file in URL_ANALYZER_DIR.glob('**/*.py'):
            if py_file.name == '__init__.py':
                module_name = str(py_file.parent.relative_to(PROJECT_ROOT)).replace('\\', '.')
            else:
                module_name = str(py_file.relative_to(PROJECT_ROOT)).replace('\\', '.').replace('.py', '')
            modules[module_name] = py_file
        
        logger.debug(f"Found {len(modules)} Python modules")
        return modules

    def run_all_tests(self) -> bool:
        """Run all documentation tests.

        Returns:
            True if all tests pass, False otherwise
        """
        logger.info("Starting documentation tests")
        
        # Run tests
        self.check_broken_internal_links()
        self.check_code_examples()
        self.check_api_documentation()
        self.check_documentation_coverage()
        self.check_markdown_syntax()
        self.check_image_references()
        self.check_consistency()
        
        # Report results
        if self.errors:
            logger.error(f"Found {len(self.errors)} errors in documentation")
            for error in self.errors:
                logger.error(f"ERROR: {error}")
                
        if self.warnings:
            logger.warning(f"Found {len(self.warnings)} warnings in documentation")
            for warning in self.warnings:
                logger.warning(f"WARNING: {warning}")
                
        return len(self.errors) == 0

    def check_broken_internal_links(self) -> None:
        """Check for broken internal links between documentation files."""
        logger.info("Checking for broken internal links")
        
        # First pass: collect all internal links and document IDs
        document_ids = {}  # Maps document names to their paths
        for md_file in self.md_files:
            document_ids[md_file.name] = md_file
            document_ids[md_file.stem] = md_file  # Also map without .md extension
            
            # Add any anchor IDs in the document
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all heading anchors
            headings = re.findall(r'^(#{1,6})\s+(.+?)$', content, re.MULTILINE)
            for level, heading in headings:
                anchor = heading.lower().replace(' ', '-').replace('.', '').replace('(', '').replace(')', '')
                anchor = re.sub(r'[^a-z0-9-]', '', anchor)
                document_ids[f"{md_file.stem}#{anchor}"] = md_file
        
        # Second pass: check all links
        for md_file in self.md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all Markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_target in links:
                # Skip external links and absolute paths
                if link_target.startswith(('http://', 'https://', '/')):
                    self.external_links.add(link_target)
                    continue
                
                # Handle relative links
                if '#' in link_target:
                    doc_part, anchor_part = link_target.split('#', 1)
                    if not doc_part:  # Link to anchor in current document
                        doc_part = md_file.stem
                    else:
                        if doc_part.endswith('.md'):
                            doc_part = doc_part[:-3]
                    
                    link_id = f"{doc_part}#{anchor_part}"
                else:
                    link_id = link_target
                    if link_target.endswith('.md'):
                        link_id = link_target[:-3]
                
                # Check if the link target exists
                if link_id not in document_ids:
                    self.errors.append(f"Broken internal link in {md_file.name}: [{link_text}]({link_target})")
                else:
                    # Track the link for later analysis
                    source = md_file.stem
                    target = document_ids[link_id].stem
                    
                    if source not in self.internal_links:
                        self.internal_links[source] = set()
                    self.internal_links[source].add(target)

    def check_code_examples(self) -> None:
        """Check code examples for syntax errors and consistency."""
        logger.info("Checking code examples")
        
        for md_file in self.md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all code blocks
            code_blocks = re.findall(r'```(\w+)\n(.*?)```', content, re.DOTALL)
            
            for lang, code in code_blocks:
                if lang == 'python':
                    # Check Python syntax
                    try:
                        compile(code, md_file.name, 'exec')
                    except SyntaxError as e:
                        self.errors.append(f"Python syntax error in {md_file.name}: {e}")
                
                elif lang in ('bash', 'sh'):
                    # Check for common shell syntax issues
                    if re.search(r'[^\\]&&', code):
                        self.warnings.append(f"Shell code in {md_file.name} uses '&&' which may not be portable")
                
                elif lang == 'json':
                    # Check JSON syntax
                    try:
                        json.loads(code)
                    except json.JSONDecodeError as e:
                        self.errors.append(f"JSON syntax error in {md_file.name}: {e}")

    def check_api_documentation(self) -> None:
        """Check API documentation for completeness and accuracy."""
        logger.info("Checking API documentation")
        
        api_doc_file = self.docs_dir / 'api_usage.md'
        if not api_doc_file.exists():
            self.warnings.append("API documentation file (api_usage.md) not found")
            return
        
        with open(api_doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for API reference section
        if '## API Reference' not in content:
            self.warnings.append("API documentation missing 'API Reference' section")
        
        # Extract documented classes and methods
        documented_items = set()
        class_matches = re.findall(r'### (\w+)', content)
        for class_name in class_matches:
            documented_items.add(class_name)
            
        method_matches = re.findall(r'- `([^`]+)\(', content)
        for method_name in method_matches:
            documented_items.add(method_name.split('(')[0])
        
        # Check if main API classes are documented
        expected_classes = ['URLAnalyzerAPI', 'APIResponse', 'AnalysisResult', 'BatchAnalysisResult']
        for cls in expected_classes:
            if cls not in documented_items:
                self.warnings.append(f"API class '{cls}' not documented in api_usage.md")

    def check_documentation_coverage(self) -> None:
        """Check documentation coverage of the codebase."""
        logger.info("Checking documentation coverage")
        
        # Get all Python modules and classes
        module_classes = {}
        for module_name, module_path in self.modules.items():
            if not module_path.exists():
                continue
                
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract classes
            class_matches = re.findall(r'class\s+(\w+)', content)
            module_classes[module_name] = class_matches
        
        # Check if modules and classes are mentioned in documentation
        for module_name, classes in module_classes.items():
            module_mentioned = False
            
            for md_file in self.md_files:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if module_name in content:
                    module_mentioned = True
                    break
            
            if not module_mentioned and not module_name.startswith('_'):
                self.warnings.append(f"Module '{module_name}' not mentioned in documentation")
            
            # Check for important classes
            for class_name in classes:
                if class_name.startswith('_'):
                    continue  # Skip private classes
                    
                class_mentioned = False
                for md_file in self.md_files:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if class_name in content:
                        class_mentioned = True
                        break
                
                if not class_mentioned and class_name.endswith(('API', 'Manager', 'Service', 'Factory')):
                    self.warnings.append(f"Important class '{class_name}' not mentioned in documentation")

    def check_markdown_syntax(self) -> None:
        """Check Markdown syntax for common issues."""
        logger.info("Checking Markdown syntax")
        
        for md_file in self.md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common Markdown syntax issues
            
            # 1. Headings should have a space after #
            if re.search(r'^#+[^ \n]', content, re.MULTILINE):
                self.errors.append(f"Heading without space after # in {md_file.name}")
            
            # 2. Check for broken tables
            table_rows = re.findall(r'\|(.+)\|', content)
            if table_rows:
                # Check if there's a header separator row
                has_separator = bool(re.search(r'\|[-:| ]+\|', content))
                if not has_separator:
                    self.errors.append(f"Table missing header separator in {md_file.name}")
            
            # 3. Check for consistent list markers
            list_markers = re.findall(r'^\s*([-*+])\s', content, re.MULTILINE)
            if list_markers and len(set(list_markers)) > 1:
                self.warnings.append(f"Inconsistent list markers in {md_file.name}")
            
            # 4. Check for HTML that could be Markdown
            if re.search(r'<(b|i|strong|em)>', content):
                self.warnings.append(f"HTML formatting used instead of Markdown in {md_file.name}")

    def check_image_references(self) -> None:
        """Check image references for broken links."""
        logger.info("Checking image references")
        
        for md_file in self.md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all image references
            images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
            
            for alt_text, image_path in images:
                # Skip external images
                if image_path.startswith(('http://', 'https://')):
                    continue
                
                # Check if the image file exists
                if image_path.startswith('/'):
                    # Absolute path within the project
                    full_path = PROJECT_ROOT / image_path.lstrip('/')
                else:
                    # Relative path
                    full_path = md_file.parent / image_path
                
                if not full_path.exists():
                    self.errors.append(f"Broken image reference in {md_file.name}: ![{alt_text}]({image_path})")
                
                # Check if alt text is provided
                if not alt_text:
                    self.warnings.append(f"Image missing alt text in {md_file.name}: ![{alt_text}]({image_path})")

    def check_consistency(self) -> None:
        """Check for consistency across documentation files."""
        logger.info("Checking documentation consistency")
        
        # Check for consistent terminology
        terminology = {}
        
        for md_file in self.md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for inconsistent capitalization of key terms
            for term in ['url analyzer', 'URL analyzer', 'Url Analyzer', 'URL Analyzer']:
                count = len(re.findall(r'\b' + re.escape(term) + r'\b', content))
                if term not in terminology:
                    terminology[term] = 0
                terminology[term] += count
        
        # Check if multiple variants are used
        used_terms = [term for term, count in terminology.items() if count > 0]
        if len(used_terms) > 1:
            self.warnings.append(f"Inconsistent capitalization of product name: {', '.join(used_terms)}")
        
        # Check for consistent headings across similar documents
        api_docs = [f for f in self.md_files if 'api' in f.stem.lower()]
        if len(api_docs) > 1:
            # Extract headings from each API doc
            api_headings = {}
            for doc in api_docs:
                with open(doc, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                headings = re.findall(r'^(#{2,3})\s+(.+?)$', content, re.MULTILINE)
                api_headings[doc.name] = [h[1] for h in headings]
            
            # Check for common headings that should be in all API docs
            common_headings = ['Installation', 'Usage', 'Examples', 'Reference']
            for heading in common_headings:
                docs_with_heading = [doc for doc, headings in api_headings.items() 
                                    if any(heading.lower() in h.lower() for h in headings)]
                
                if docs_with_heading and len(docs_with_heading) < len(api_docs):
                    missing_docs = set(api_headings.keys()) - set(docs_with_heading)
                    self.warnings.append(f"Heading '{heading}' missing in some API docs: {', '.join(missing_docs)}")

    def generate_report(self, output_file: Optional[str] = None) -> None:
        """Generate a report of the documentation tests.

        Args:
            output_file: Path to the output file, or None to print to stdout
        """
        # Create report content
        report = [
            "# URL Analyzer Documentation Test Report",
            "",
            f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- **Documentation files**: {len(self.md_files)}",
            f"- **Errors**: {len(self.errors)}",
            f"- **Warnings**: {len(self.warnings)}",
            f"- **Status**: {'PASS' if not self.errors else 'FAIL'}",
            "",
        ]
        
        if self.errors:
            report.extend([
                "## Errors",
                "",
            ])
            for error in self.errors:
                report.append(f"- {error}")
            report.append("")
        
        if self.warnings:
            report.extend([
                "## Warnings",
                "",
            ])
            for warning in self.warnings:
                report.append(f"- {warning}")
            report.append("")
        
        # Add documentation coverage section
        report.extend([
            "## Documentation Coverage",
            "",
            "### Internal Links",
            "",
        ])
        
        # Create a simple graph of internal links
        if self.internal_links:
            report.append("```")
            for source, targets in sorted(self.internal_links.items()):
                report.append(f"{source} -> {', '.join(sorted(targets))}")
            report.append("```")
        else:
            report.append("No internal links found.")
        
        report.append("")
        
        # Output the report
        report_content = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report written to {output_file}")
        else:
            print(report_content)


def main():
    """Main entry point for the documentation testing script."""
    parser = argparse.ArgumentParser(description='Test URL Analyzer documentation')
    parser.add_argument('--docs-dir', type=str, default=str(DOCS_DIR),
                        help='Path to the documentation directory')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--report', '-r', type=str,
                        help='Generate a report file')
    
    args = parser.parse_args()
    
    tester = DocumentationTester(Path(args.docs_dir), args.verbose)
    success = tester.run_all_tests()
    
    if args.report:
        tester.generate_report(args.report)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    import datetime  # Import here to avoid unused import in module scope
    main()