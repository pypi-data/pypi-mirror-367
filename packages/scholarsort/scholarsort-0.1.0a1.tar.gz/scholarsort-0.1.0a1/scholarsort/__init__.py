"""
ScholarSort: A Python library for scholarly research with impact factor analysis

This library provides tools for:
- Searching scholarly publications
- Retrieving author information
- Fetching journal impact factors
- Analyzing citation metrics
- Advanced research analytics

Author: ScholarSort Team
Year: 2025
"""

__version__ = "0.1.0a1"

from .scholarly import ScholarlySearch
from .impact_factor import ImpactFactorAnalyzer
from .author import AuthorAnalyzer
from .journal import JournalAnalyzer

__all__ = [
    "ScholarlySearch",
    "ImpactFactorAnalyzer", 
    "AuthorAnalyzer",
    "JournalAnalyzer",
    "__version__"
]

# Package metadata
__author__ = "ScholarSort Team"
__email__ = "team@scholarsort.org"
__license__ = "MIT"
__copyright__ = "Copyright 2025, ScholarSort Team"
