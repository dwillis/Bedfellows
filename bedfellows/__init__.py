"""
Bedfellows - FEC Campaign Finance Relationship Analysis Tool

A modern Python 3 tool for analyzing relationships between PAC donors and recipients
using Federal Election Commission data.
"""

__version__ = "2.0.0"
__author__ = "Bedfellows Contributors"

from bedfellows.config import Config
from bedfellows.database import DatabaseManager

__all__ = ["Config", "DatabaseManager", "__version__"]
