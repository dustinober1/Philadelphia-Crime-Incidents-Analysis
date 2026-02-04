"""Data layer module for loading, validation, and preprocessing.

This module provides a complete data layer for crime incident analysis:
- Loading: load_crime_data, load_boundaries, load_external_data
- Validation: validate_crime_data, validate_coordinates, CrimeIncidentValidator
- Preprocessing: filter_by_date_range, aggregate_by_period, add_temporal_features
- Caching: clear_cache

Example:
    >>> from analysis.data import load_crime_data, validate_crime_data, filter_by_date_range
    >>> df = load_crime_data()
    >>> validate_crime_data(df)
    >>> df_2020 = filter_by_date_range(df, "2020-01-01", "2020-12-31")
"""

# Exports from loading.py
from analysis.data.loading import load_crime_data, load_boundaries, load_external_data

# Exports from cache.py
from analysis.data.cache import memory, clear_cache

# Exports from validation.py
from analysis.data.validation import (
    CrimeIncidentValidator,
    validate_crime_data,
    validate_coordinates,
    PHILLY_LON_MIN,
    PHILLY_LON_MAX,
    PHILLY_LAT_MIN,
    PHILLY_LAT_MAX,
)

# Exports from preprocessing.py
from analysis.data.preprocessing import (
    filter_by_date_range,
    aggregate_by_period,
    add_temporal_features,
)

__all__ = [
    "load_crime_data",
    "load_boundaries",
    "load_external_data",
    "memory",
    "clear_cache",
    "CrimeIncidentValidator",
    "validate_crime_data",
    "validate_coordinates",
    "filter_by_date_range",
    "aggregate_by_period",
    "add_temporal_features",
    "PHILLY_LON_MIN",
    "PHILLY_LON_MAX",
    "PHILLY_LAT_MIN",
    "PHILLY_LAT_MAX",
]
