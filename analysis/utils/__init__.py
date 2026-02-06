"""Crime data utility functions.

This package provides modular utilities for crime data analysis, including
classification, temporal feature extraction, and spatial operations.

Modules:
    classification: Crime category classification and UCR code mapping
    temporal: Temporal feature extraction (year, month, day_of_week, etc.)
    spatial: Coordinate cleaning, spatial joins, severity scoring

Example:
    >>> from analysis.utils.classification import classify_crime_category
    >>> category = classify_crime_category(100)  # Homicide
    >>> from analysis.utils.temporal import extract_temporal_features
    >>> df = extract_temporal_features(df)

See CLAUDE.md for usage guidance and CLI workflow examples.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import pandas as pd

from analysis.utils.classification import CRIME_CATEGORY_MAP, classify_crime_category
from analysis.utils.temporal import extract_temporal_features

# Optional spatial imports (require geopandas)
try:
    from analysis.utils.spatial import (
        calculate_severity_score,
        clean_coordinates,
        df_to_geodataframe,
        get_coordinate_stats,
        load_boundaries,
        spatial_join_districts,
        spatial_join_tracts,
    )

    HAS_SPATIAL = True
except ImportError:
    # geopandas not available - spatial functions will not be available
    HAS_SPATIAL = False

    # Define stub functions that raise helpful errors
    def _missing_geopandas(*args: Any, **kwargs: Any) -> None:
        raise ImportError(
            "geopandas is required for spatial functions. "
            "Install it with: conda install -c conda-forge geopandas"
        )

    calculate_severity_score = _missing_geopandas  # type: ignore[assignment]
    clean_coordinates = _missing_geopandas  # type: ignore[assignment]
    df_to_geodataframe = _missing_geopandas
    get_coordinate_stats = _missing_geopandas  # type: ignore[assignment]
    load_boundaries = _missing_geopandas
    spatial_join_districts = _missing_geopandas  # type: ignore[assignment]
    spatial_join_tracts = _missing_geopandas  # type: ignore[assignment]

# Import load_data from parent utils.py for backward compatibility
# TODO: Migrate to analysis.data.load_crime_data in Phase 5
utils_path = Path(__file__).parent.parent / "utils.py"
if utils_path.exists():
    spec = spec_from_file_location("analysis._utils_legacy", utils_path)
    if spec is not None:
        utils_module = module_from_spec(spec)
        sys.modules["analysis._utils_legacy"] = utils_module
        if spec.loader:
            spec.loader.exec_module(utils_module)
        load_data: Callable[..., pd.DataFrame] = utils_module.load_data
    else:

        def load_data(*args: Any, **kwargs: Any) -> pd.DataFrame:
            raise ImportError("load_data has been migrated to analysis.data.load_crime_data")

else:

    def load_data(*args: Any, **kwargs: Any) -> pd.DataFrame:
        raise ImportError("load_data has been migrated to analysis.data.load_crime_data")


__all__ = [
    "classify_crime_category",
    "CRIME_CATEGORY_MAP",
    "extract_temporal_features",
    "load_data",
    "clean_coordinates",
    "df_to_geodataframe",
    "spatial_join_districts",
    "spatial_join_tracts",
    "load_boundaries",
    "calculate_severity_score",
    "get_coordinate_stats",
]
