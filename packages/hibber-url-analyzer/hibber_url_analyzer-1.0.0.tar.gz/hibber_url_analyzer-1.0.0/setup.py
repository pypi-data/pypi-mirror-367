#!/usr/bin/env python
"""
Setup script for URL Analyzer.

This file is provided for backward compatibility with tools that don't support pyproject.toml.
For modern Python packaging, use pyproject.toml instead.
"""

# import os
from setuptools import setup, find_packages

# # Read the long description from README.md
# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

# Define package metadata
setup(
    name="hibber-url-analyzer",
    version="1.0.0",
    description="A tool for analyzing, categorizing, and reporting on URLs from browsing history or other sources",
    long_description="long_description",
    long_description_content_type="text/markdown",
    author="URL Analyzer Team",
    author_email="contact@url-analyzer.dev",
    url="https://github.com/url-analyzer/url-analyzer",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "url_analyzer": [
            "templates/*.html", 
            "templates/*.css", 
            "templates/*.js",
            "reporting/templates/*.html",
            "web/templates/*/*.html",
            "static/css/*.css",
            "static/pdf/*"
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "jinja2>=3.1.6",
        "flask>=2.3.0",
        "flask-wtf>=1.2.0",
        "flask-babel>=3.1.0",
        "werkzeug>=2.3.0",
        "email-validator>=2.0.0",
        "itsdangerous>=2.1.0",
        "networkx>=2.6.0",
    ],
    extras_require={
        "url_fetching": ["requests>=2.32.4"],
        "html_parsing": ["beautifulsoup4>=4.9.0", "lxml>=4.6.0"],
        "domain_extraction": ["tldextract>=3.1.0"],
        "visualization": ["plotly>=5.3.0"],
        "geolocation": ["geoip2>=4.6.0", "pycountry>=22.3.5"],
        "pdf_export": ["weasyprint>=57.1"],
        "progress": ["tqdm>=4.60.0"],
        "excel": ["openpyxl>=3.0.0"],
        "terminal_ui": ["rich>=13.3.0", "prompt_toolkit>=3.0.30"],
        "system": ["psutil>=5.9.0"],
        "ml_analysis": ["scipy>=1.8.0", "scikit-learn>=1.0.0", "nltk>=3.7.0"],
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "hypothesis>=6.82.0",
            "mutmut>=2.4.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "radon>=6.0.0",
            "pylint>=2.17.0",
            "bandit>=1.7.5",
            "safety>=2.3.5",
        ],
        "all": [
            "requests>=2.32.4",
            "beautifulsoup4>=4.9.0",
            "lxml>=4.6.0",
            "tldextract>=3.1.0",
            "plotly>=5.3.0",
            "geoip2>=4.6.0",
            "pycountry>=22.3.5",
            "weasyprint>=57.1",
            "tqdm>=4.60.0",
            "openpyxl>=3.0.0",
            "rich>=13.3.0",
            "prompt_toolkit>=3.0.30",
            "psutil>=5.9.0",
            "scipy>=1.8.0",
            "scikit-learn>=1.0.0",
            "nltk>=3.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "url-analyzer=url_analyzer.cli.commands:main",
            "url-analyzer-check-dependencies=url_analyzer.cli.dependency_commands:main",
            "url-analyzer-check-features=url_analyzer.cli.dependency_commands:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
    ],
    keywords="url, analysis, web, browsing, history, categorization, reporting",
    project_urls={
        "Homepage": "https://github.com/Hibber/url-analyzer",
        "Bug Tracker": "https://github.com/Hibber/url-analyzer/issues",
        "Documentation": "https://github.com/Hibber/url-analyzer/blob/main/docs",
        "Source Code": "https://github.com/Hibber/url-analyzer",
        "Repository": "https://github.com/Hibber/url-analyzer.git",
    },
)