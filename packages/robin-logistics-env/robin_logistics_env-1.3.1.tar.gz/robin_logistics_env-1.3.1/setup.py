"""
Robin Hackathon 2025: Logistics Operations Environment
A multi-depot vehicle routing problem (MDVRP) simulation environment for hackathon contestants.
"""

from setuptools import setup, find_packages
import os

# Read README for PyPI long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="robin-logistics-env",
    version="1.3.1",
    author="Robin Hackathon Team",
    author_email="hackathon@robin.com",
    description="Multi-depot vehicle routing problem simulation environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robin/hackathon-2025",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
    ],
    keywords="vehicle routing problem, optimization, logistics, hackathon, MDVRP, simulation",
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "networkx>=2.6.0",
        "streamlit>=1.28.0",
        "folium>=0.14.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "dashboard": [
            "dill>=0.3.0",
        ],
    },
    include_package_data=True,
    package_data={
        "robin_logistics": ["data/*.csv"],
    },
    entry_points={
        "console_scripts": [
            "robin-logistics=robin_logistics.cli:main",
        ],
    },
)