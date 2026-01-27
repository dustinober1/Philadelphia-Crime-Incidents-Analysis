"""
Geospatial analysis module for crime incident data.

Provides geographic analysis capabilities including mapping, hotspot identification,
and spatial distribution analysis through the GeoAnalyzer class and utility functions.
"""

from src.geospatial.analyzer import GeoAnalyzer
from src.geospatial.utils import (
    validate_coordinates,
    get_marker_color,
    get_phl_center_coordinates,
    prepare_coordinate_data,
)

__all__ = [
    "GeoAnalyzer",
    "validate_coordinates",
    "get_marker_color",
    "get_phl_center_coordinates",
    "prepare_coordinate_data",
]
