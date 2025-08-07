#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geneinfo",
    version="0.1.0",
    author="Chunjie Liu",
    author_email="",
    description="Get comprehensive gene information based on gene symbol or Ensembl ID",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chunjie-sam-liu/geneinfo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "geneinfo=geneinfo.cli:main",
        ],
    },
)