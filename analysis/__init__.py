"""
Philadelphia Crime Incidents - Exploratory Data Analysis Package

This package contains analysis scripts for the Philadelphia crime incidents dataset,
spanning from 2006 to 2026 with over 3.4 million records.
"""

__version__ = "1.0.0"

# Import key functions from submodules for easy access
from .weighted_severity_analysis import (
    analyze_weighted_severity,
    generate_severity_report,
    create_severity_choropleth,
    calculate_weighted_severity_scores
)
