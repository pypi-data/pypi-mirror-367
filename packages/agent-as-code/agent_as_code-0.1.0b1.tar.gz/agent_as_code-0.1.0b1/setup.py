#!/usr/bin/env python3
"""
Setup script for Agent as Code (AaC) framework
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Agent as Code (AaC) - Declarative AI agent configuration framework"

setup(
    name="agent-as-code",
    version="0.1.0b1",
    description="Declarative configuration system for AI agents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Partha Sarathi Kundu",
    author_email="inboxpartha@outlook.com",
    url="https://agent-as-code.myagentregistry.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'agent_as_code': [
            'proto/*.proto',
            'templates/*/*',
            'config/*.json',
        ],
    },
    install_requires=[
        "grpcio>=1.59.0",
        "grpcio-tools>=1.59.0",
        "requests>=2.31.0",
        "numpy>=1.21.0",
        "openai>=0.28.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agent=agent_as_code.cli.agent_cli:main",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    keywords="ai, agent, configuration, declarative, docker-like",
    project_urls={
        "Documentation": "https://agent-as-code.myagentregistry.com/docs",
        "Registry": "https://www.myagentregistry.com",
        "Developed_By": "https://github.com/pxkundu",
    },
) 