#!/usr/bin/env python3
"""
Setup script for detect-repo-language package.

This script configures the package for installation via setuptools.
It allows building wheels and source distributions.
"""

from setuptools import setup
from pathlib import Path
import os
import glob

# Read the README for the long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

# Gather all language JSON files and documentation
languages_dir = Path(__file__).parent / "languages"
language_files = []
if languages_dir.exists():
    for json_file in languages_dir.glob("*.json"):
        language_files.append(str(json_file.relative_to(Path(__file__).parent)))
    # Add language documentation
    readme_file = languages_dir / "README.md"
    if readme_file.exists():
        language_files.append(str(readme_file.relative_to(Path(__file__).parent)))

setup(
    name="detect-repo-language",
    version="1.0.0",
    author="Alexandra",
    description="Detect the primary programming language of a repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lang-detect",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/lang-detect/issues",
        "Documentation": "https://github.com/yourusername/lang-detect#readme",
        "Source Code": "https://github.com/yourusername/lang-detect",
    },
    license="MIT",
    python_requires=">=3.7",
    py_modules=["detect_repo_language"],
    entry_points={
        "console_scripts": [
            "detect-repo-language=detect_repo_language:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="language detection repository analysis starship",
)
