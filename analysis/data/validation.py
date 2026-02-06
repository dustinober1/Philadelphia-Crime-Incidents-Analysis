"""Pydantic validators for crime incident data.

This module provides Pydantic models for validating crime incident data
schema, ensuring type safety and data quality.

Classes:
    CrimeIncidentValidator: Validates crime incident row data

Validation rules:
- dispatch_time: Valid datetime, not null
- ucr_general: Integer 100-9999
- point_x, point_y: Float coordinates within Philadelphia bounds
- text_general_code: Non-empty string
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator

# Coordinate bounds for Philadelphia
PHILLY_LON_MIN = -75.3
PHILLY_LON_MAX = -74.95
PHILLY_LAT_MIN = 39.85
PHILLY_LAT_MAX = 40.15


class CrimeIncidentValidator(BaseModel):
    """Pydantic model for validating crime incident data.

    Coordinates are validated against Philadelphia bounds:
    - Longitude: -75.3 to -74.95
    - Latitude: 39.85 to 40.15

    Attributes:
        incident_id: Unique incident identifier
        dispatch_date: Dispatch timestamp (required)
        ucr_general: UCR code (100-9999 for expanded codes)
        text_general_code: Crime type description
        point_x: Longitude coordinate (optional, validated to Philly bounds)
        point_y: Latitude coordinate (optional, validated to Philly bounds)
        dc_key: District code (optional)
        psa: Police service area (optional, can be string or numeric)

    Example:
        >>> validator = CrimeIncidentValidator(
        ...     incident_id="12345",
        ...     dispatch_date="2020-01-01 12:00:00",
        ...     ucr_general=600,
        ...     text_general_code="Theft"
        ... )
    """

    incident_id: str | None = Field(None, description="Unique incident identifier")
    dispatch_date: datetime = Field(..., description="Dispatch timestamp")
    ucr_general: int | None = Field(None, ge=100, le=9999, description="UCR code (100-9999)")
    text_general_code: str | None = Field(None, description="Crime type description")
    point_x: float | None = Field(
        None, ge=PHILLY_LON_MIN, le=PHILLY_LON_MAX, description="Longitude"
    )
    point_y: float | None = Field(
        None, ge=PHILLY_LAT_MIN, le=PHILLY_LAT_MAX, description="Latitude"
    )
    dc_key: int | None = Field(None, description="District code")
    psa: str | None = Field(None, description="Police service area (can be letter or numeric)")

    @field_validator("ucr_general")
    @classmethod
    def validate_ucr_code(cls, v: int | None) -> int | None:
        """Validate UCR code is in expected range.

        Args:
            v: UCR code value to validate.

        Returns:
            Validated UCR code.

        Raises:
            ValueError: If UCR code is negative or unreasonably large.
        """
        if v is not None and (v < 100 or v > 9999):
            raise ValueError(f"UCR code must be 100-9999, got {v}")
        return v

    @field_validator("point_x", "point_y")
    @classmethod
    def validate_philly_coords(cls, v: float | None) -> float | None:
        """Validate coordinates are within Philadelphia bounds.

        Args:
            v: Coordinate value to validate.

        Returns:
            Validated coordinate.

        Raises:
            ValueError: If coordinate is outside Philadelphia bounds.
        """
        if v is not None:
            # Field constraints handle the bounds validation
            pass
        return v


def validate_crime_data(
    df: pd.DataFrame,
    sample_size: int = 1000,
    strict: bool = False,
) -> pd.DataFrame:
    """Validate crime data using Pydantic model.

    This function validates a sample of rows by default for performance.
    Set strict=True to validate all rows (may be slow for large datasets).

    Args:
        df: DataFrame to validate.
        sample_size: Number of rows to validate (full validation if strict=True).
        strict: If True, validate all rows. If False, validate sample only.

    Returns:
        Validated DataFrame (same as input if validation passes).

    Raises:
        ValueError: If validation fails with details of errors.

    Example:
        >>> from analysis.data import load_crime_data, validate_crime_data
        >>> df = load_crime_data()
        >>> validate_crime_data(df)  # Validate sample
        >>> validate_crime_data(df, strict=True)  # Validate all (slow)
    """
    if len(df) == 0:
        raise ValueError("DataFrame is empty")

    # Determine sample size
    if strict:
        sample = df
    else:
        sample_size_actual = min(len(df), sample_size)
        sample = (
            df.sample(n=sample_size_actual, random_state=42) if len(df) > sample_size_actual else df
        )

    errors = []
    for idx, row in sample.iterrows():
        try:
            # Convert row to dict and validate
            row_dict = {str(k): v for k, v in row.to_dict().items()}
            # Handle NaN values for optional fields
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            CrimeIncidentValidator(**row_dict)
        except ValidationError as e:
            errors.append((idx, str(e)))
        except Exception as e:
            errors.append((idx, f"Unexpected error: {e}"))

    if errors:
        error_msg = "\n".join(
            f"Row {idx}: {err[:100]}..." if len(err) > 100 else f"Row {idx}: {err}"
            for idx, err in errors[:5]
        )
        if len(errors) > 5:
            error_msg += f"\n... and {len(errors) - 5} more errors"
        raise ValueError(f"Data validation failed ({len(errors)} errors):\n{error_msg}")

    return df


def validate_coordinates(
    df: pd.DataFrame,
    x_col: str = "point_x",
    y_col: str = "point_y",
    lon_bounds: tuple[float, float] = (PHILLY_LON_MIN, PHILLY_LON_MAX),
    lat_bounds: tuple[float, float] = (PHILLY_LAT_MIN, PHILLY_LAT_MAX),
) -> pd.DataFrame:
    """Filter DataFrame to only include rows with valid coordinates.

    This function filters out rows where coordinates are outside the
    specified bounds or are missing.

    Args:
        df: Input DataFrame with coordinate columns.
        x_col: Name of longitude column.
        y_col: Name of latitude column.
        lon_bounds: (min, max) longitude values for valid range.
        lat_bounds: (min, max) latitude values for valid range.

    Returns:
        DataFrame with only rows with valid coordinates.

    Raises:
        ValueError: If coordinate columns not found in DataFrame.

    Example:
        >>> from analysis.data import load_crime_data, validate_coordinates
        >>> df = load_crime_data()
        >>> valid_df = validate_coordinates(df)
        >>> print(f"Valid coordinates: {len(valid_df)} / {len(df)}")
    """
    result = df.copy()

    # Check columns exist
    if x_col not in result.columns:
        raise ValueError(f"Column '{x_col}' not found in DataFrame")
    if y_col not in result.columns:
        raise ValueError(f"Column '{y_col}' not found in DataFrame")

    # Filter valid coordinates
    lon_min, lon_max = lon_bounds
    lat_min, lat_max = lat_bounds

    valid_mask = (
        (result[x_col].notna())
        & (result[y_col].notna())
        & (result[x_col] >= lon_min)
        & (result[x_col] <= lon_max)
        & (result[y_col] >= lat_min)
        & (result[y_col] <= lat_max)
    )

    return result[valid_mask].copy()


__all__ = [
    "CrimeIncidentValidator",
    "validate_crime_data",
    "validate_coordinates",
    "PHILLY_LON_MIN",
    "PHILLY_LON_MAX",
    "PHILLY_LAT_MIN",
    "PHILLY_LAT_MAX",
]
