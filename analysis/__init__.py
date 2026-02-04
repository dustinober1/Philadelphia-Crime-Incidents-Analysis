"""Crime incidents analysis package.

This package provides utilities for:
- Data loading and validation (analysis.utils)
- Crime classification and temporal features (analysis.utils.classification, analysis.utils.temporal)
- Spatial analysis and joins (analysis.utils.spatial)
- Visualization (analysis.visualization)
- ML models (analysis.models)

Example:
    >>> from analysis import classify_crime_category, extract_temporal_features
    >>> from analysis.utils.spatial import clean_coordinates, df_to_geodataframe
    >>> from analysis.data import load_crime_data  # TODO: Phase 5
"""

from __future__ import annotations

from typing import Any

__version__ = "1.1.0"

# Export configuration constants
from analysis.config import COLORS, CRIME_DATA_PATH, REPORTS_DIR

# Export key utilities
from analysis.utils import (
    CRIME_CATEGORY_MAP,
    classify_crime_category,
    extract_temporal_features,
    load_data,
)

# Export spatial utilities (optional, requires geopandas)
try:
    from analysis.utils.spatial import (
        calculate_severity_score,
        clean_coordinates,
        df_to_geodataframe,
    )
except ImportError:
    # geopandas not available - define stubs
    def _missing_geopandas(*args: Any, **kwargs: Any) -> Any:
        raise ImportError(
            "geopandas is required for spatial functions. "
            "Install it with: conda install -c conda-forge geopandas"
        )

    # Reassign with explicit type annotations
    calculate_severity_score = _missing_geopandas
    clean_coordinates = _missing_geopandas
    df_to_geodataframe = _missing_geopandas

__all__ = [
    # Version
    "__version__",
    # Configuration
    "COLORS",
    "CRIME_DATA_PATH",
    "REPORTS_DIR",
    # Classification
    "classify_crime_category",
    "CRIME_CATEGORY_MAP",
    # Temporal
    "extract_temporal_features",
    # Data loading (backward compatibility)
    "load_data",
    # Spatial
    "clean_coordinates",
    "df_to_geodataframe",
    "calculate_severity_score",
]
