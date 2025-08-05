#!/usr/bin/env python3
"""
Setup script for artifacts-mcp-server
"""

from setuptools import setup, find_packages

setup(
    name="artifacts-mcp-server",
    version="0.1.0",
    description="Zero-config MCP Server for AI code artifacts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/artifacts-mcp-server",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.5.0",
        "agentsphere>=1.0.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "artifacts-mcp-server=artifacts_mcp_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)