#!/usr/bin/env python3
"""
Setup script for Zoom Deep Clean Enhanced
VM-Aware & System-Wide cleanup utility

Created by: PHLthy215
Enhanced Version: 2.4.2
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Enhanced Zoom Deep Clean - VM-Aware & System-Wide cleanup utility"


# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


setup(
    name="zoom-deep-clean-enhanced",
    version="2.4.2",
    author="PHLthy215",
    author_email="PHLthy215@example.com",
    description="Enhanced VM-Aware & System-Wide Zoom cleanup utility for macOS",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/PHLthy215/zoom-deep-clean-enhanced",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ]
    },
    entry_points={
        "console_scripts": [
            "zoom-deep-clean-enhanced=zoom_deep_clean.cli_enhanced:main",
            "zdce=zoom_deep_clean.cli_enhanced:main",  # Short alias
            "zoom-deep-clean-gui=zoom_deep_clean.gui_app:main",  # GUI launcher
        ],
    },
    include_package_data=True,
    package_data={
        "zoom_deep_clean": [
            "*.md",
            "*.txt",
            "*.json",
        ],
    },
    keywords=[
        "zoom",
        "cleanup",
        "privacy",
        "macos",
        "vm",
        "virtual-machine",
        "system-administration",
        "security",
        "fingerprint-removal",
        "pypi-ready",
    ],
    project_urls={
        "Bug Reports": "https://github.com/PHLthy215/zoom-deep-clean-enhanced/issues",
        "Source": "https://github.com/PHLthy215/zoom-deep-clean-enhanced",
        "Documentation": "https://github.com/PHLthy215/zoom-deep-clean-enhanced/blob/main/README.md",
    },
)
