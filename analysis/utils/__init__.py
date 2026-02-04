"""Analysis utilities module.

This module provides reusable utility functions for:
- Crime classification (analysis.utils.classification)
- Temporal feature extraction (analysis.utils.temporal)
- Spatial utilities (analysis.utils.spatial)
- Data loading (from analysis.utils.py for backward compatibility)

Example:
    >>> from analysis.utils import classify_crime_category, extract_temporal_features
    >>> from analysis.utils.spatial import clean_coordinates, df_to_geodataframe
"""

from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from analysis.utils.classification import CRIME_CATEGORY_MAP, classify_crime_category
from analysis.utils.temporal import extract_temporal_features

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
]
