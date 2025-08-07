"""
Robin Logistics Environment - Multi-Depot Vehicle Routing Optimization
A comprehensive logistics optimization environment for developing and testing 
vehicle routing algorithms with real-world constraints and interactive visualization.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="robin-logistics-env",
    version="2.0.0",
    author="Robin Logistics Team",
    author_email="info@robin-logistics.com",
    description="Comprehensive logistics optimization environment with interactive dashboard and performance analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robin-logistics/optimization-environment",
    project_urls={
        "Bug Tracker": "https://github.com/robin-logistics/optimization-environment/issues",
        "Documentation": "https://robin-logistics.readthedocs.io/",
        "Source Code": "https://github.com/robin-logistics/optimization-environment",
        "Changelog": "https://github.com/robin-logistics/optimization-environment/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
    ],
    keywords="logistics, optimization, vehicle-routing, supply-chain, algorithms, hackathon, vrp, mdvrp",
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "networkx>=2.6.0",
        "streamlit>=1.28.0",
        "folium>=0.14.0",
        "dill>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "examples": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "jupyter>=1.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    include_package_data=True,
    package_data={
        "robin_logistics": ["data/*.csv", "templates/*.html"],
    },
    entry_points={
        "console_scripts": [
            "robin-logistics=robin_logistics.cli:main",
        ],
    },
    zip_safe=False,
    platforms=["any"],
)