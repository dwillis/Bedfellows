"""Setup script for Bedfellows FEC campaign finance analysis tool."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="bedfellows",
    version="2.0.0",
    description="Federal Election Commission (FEC) campaign finance relationship analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bedfellows Contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "peewee>=3.17.0,<4.0.0",
        "pandas>=2.0.0,<3.0.0",
        "numpy>=1.24.0,<2.0.0",
        "scipy>=1.10.0,<2.0.0",
        "requests>=2.31.0,<3.0.0",
        "click>=8.1.0,<9.0.0",
        "tqdm>=4.65.0,<5.0.0",
        "rich>=13.0.0,<14.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "pyyaml>=6.0,<7.0",
        "datasette>=0.64.0,<1.0.0",
        "python-dateutil>=2.8.0,<3.0.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "mysql": ["mysqlclient>=2.2.0,<3.0.0"],
        "postgresql": ["psycopg2-binary>=2.9.0,<3.0.0"],
        "dev": [
            "pytest>=7.4.0,<8.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "black>=23.0.0,<24.0.0",
            "ruff>=0.1.0,<1.0.0",
            "mypy>=1.5.0,<2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bedfellows=bedfellows.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="fec campaign-finance politics data-analysis",
    project_urls={
        "Source": "https://github.com/dwillis/Bedfellows",
        "Bug Reports": "https://github.com/dwillis/Bedfellows/issues",
    },
)
