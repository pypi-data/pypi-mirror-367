#!/usr/bin/env python3
"""
DOCX Image Extractor MCP - Setup Script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="docx-image-extractor-mcp",
    version="1.2.1",
    author="DOCX Image Extractor Team",
    author_email="docx.extractor@gmail.com",
    description="A powerful DOC/DOCX image extractor with MCP protocol support for Claude Desktop integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/docx-image-extractor/docx-image-extractor-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pypinyin>=0.47.0",
        "mcp>=1.0.0",
        "python-docx>=0.8.11",
        "olefile>=0.46",
        "docx2txt>=0.8",
    ],
    entry_points={
        "console_scripts": [
            "docx-image-extractor-mcp=docx_image_extractor_mcp.main:cli_main",
            "docx-extract=docx_image_extractor_mcp.cli:main",
        ],
    },
    keywords="doc, docx, image, extractor, mcp, word, document, ole",
    project_urls={
        "Bug Reports": "https://github.com/docx-image-extractor/docx-image-extractor-mcp/issues",
        "Source": "https://github.com/docx-image-extractor/docx-image-extractor-mcp",
        "Documentation": "https://github.com/docx-image-extractor/docx-image-extractor-mcp/blob/main/README.md",
        "Changelog": "https://github.com/docx-image-extractor/docx-image-extractor-mcp/blob/main/CHANGELOG.md",
    },
)