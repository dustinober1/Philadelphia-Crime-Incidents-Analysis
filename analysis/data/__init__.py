"""Data layer for crime incident analysis.

This package provides data loading, validation, and preprocessing utilities
for crime incident data, with caching and Pydantic validation.

Modules:
    loading: Data loading with joblib caching
    validation: Pydantic validators for crime incident data
    preprocessing: Filtering, aggregation, and data preparation

Example:
    >>> from analysis.data.loading import load_crime_data
    >>> df = load_crime_data(clean=True)
    >>> from analysis.data.preprocessing import filter_by_date_range
    >>> df = filter_by_date_range(df, start="2020-01-01", end="2023-12-31")
"""

# Exports from loading.py
# Exports from cache.py
from analysis.data.cache import clear_cache, memory
from analysis.data.loading import load_boundaries, load_crime_data, load_external_data

# Exports from preprocessing.py
from analysis.data.preprocessing import (
    add_temporal_features,
    aggregate_by_period,
    filter_by_date_range,
)

# Exports from validation.py
from analysis.data.validation import (
    PHILLY_LAT_MAX,
    PHILLY_LAT_MIN,
    PHILLY_LON_MAX,
    PHILLY_LON_MIN,
    CrimeIncidentValidator,
    validate_coordinates,
    validate_crime_data,
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
