#!/usr/bin/env python3
"""
Setup script for AI-shell - AI-Powered Interactive Shell
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        # Fallback to basic requirements
        return [
            "requests>=2.31.0",
            "rich>=13.0.0", 
            "python-dotenv>=1.0.0",
        ]

setup(
    name="ai-shell-cli",
    version="0.1.0",
    author="AI-shell Team",
    author_email="contact@ai-shell.dev",
    description="AI-Powered Interactive Shell - Convert natural language to shell commands",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ai-shell/ai-shell",
    project_urls={
        "Bug Reports": "https://github.com/ai-shell/ai-shell/issues",
        "Source": "https://github.com/ai-shell/ai-shell",
        "Documentation": "https://github.com/ai-shell/ai-shell#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Shells",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-shell-cli=ai_shell.main:main",
            "ai-shell-demo=ai_shell.demo_mode:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_shell": ["*.txt", "*.md", "*.sh"],
    },
    keywords="shell, ai, cli, terminal, automation, command-line",
    license="MIT",
    zip_safe=False,
) 