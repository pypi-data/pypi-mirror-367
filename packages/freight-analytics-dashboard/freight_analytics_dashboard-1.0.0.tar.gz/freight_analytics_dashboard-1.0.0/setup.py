#!/usr/bin/env python3
"""Setup configuration for US Freight Analytics Dashboard package."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="freight-analytics-dashboard",
    version="1.0.0",
    author="Megh KC",
    author_email="kc.megh2048@gmail.com",
    description="Advanced US Freight Analytics Dashboard with Interactive Visualizations",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/meghkc/DashBoard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
        "deploy": [
            "gunicorn>=20.0",
            "docker>=5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "freight-dashboard=freight_analytics.cli:main",
            "freight-analytics=freight_analytics.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "freight_analytics": [
            "data/*.csv",
            "data/*.json",
        ],
    },
    zip_safe=False,
    keywords="freight analytics dashboard visualization streamlit logistics transportation",
    project_urls={
        "Bug Reports": "https://github.com/meghkc/DashBoard/issues",
        "Source": "https://github.com/meghkc/DashBoard",
        "Documentation": "https://github.com/meghkc/DashBoard/blob/main/README.md",
        "Live Demo": "https://meghkc-dashboard-freight-analysis.streamlit.app/",
    },
)
