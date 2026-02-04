"""Data layer module for loading, validation, and preprocessing.

This module provides a complete data layer for crime incident analysis:
- Loading: load_crime_data, load_boundaries, load_external_data
- Validation: validate_crime_data, validate_coordinates
- Preprocessing: filter_by_date_range, aggregate_by_period
- Caching: clear_cache

Example:
    >>> from analysis.data import load_crime_data, validate_crime_data
    >>> df = load_crime_data()
    >>> validate_crime_data(df)
"""

# Exports from loading.py
from analysis.data.loading import load_crime_data, load_boundaries, load_external_data

# Exports from cache.py
from analysis.data.cache import memory, clear_cache

__all__ = [
    "load_crime_data",
    "load_boundaries",
    "load_external_data",
    "memory",
    "clear_cache",
]
