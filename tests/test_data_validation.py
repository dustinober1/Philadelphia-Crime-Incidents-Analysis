"""Tests for data validation using Pydantic models.

This module tests the data validation functionality including:
- CrimeIncidentValidator with valid/invalid data
- validate_crime_data() with sampling and strict mode
- validate_coordinates() for Philadelphia bounds filtering
- Coordinate bounds constants
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest
from pydantic import ValidationError

from analysis.data.validation import (
    PHILLY_LAT_MAX,
    PHILLY_LAT_MIN,
    PHILLY_LON_MAX,
    PHILLY_LON_MIN,
    CrimeIncidentValidator,
    validate_coordinates,
    validate_crime_data,
)


class TestCoordinateBoundsConstants:
    """Tests for Philadelphia coordinate bounds constants."""

    def test_philly_lon_min(self):
        """PHILLY_LON_MIN is -75.3."""
        assert PHILLY_LON_MIN == -75.3

    def test_philly_lon_max(self):
        """PHILLY_LON_MAX is -74.95."""
        assert PHILLY_LON_MAX == -74.95

    def test_philly_lat_min(self):
        """PHILLY_LAT_MIN is 39.85."""
        assert PHILLY_LAT_MIN == 39.85

    def test_philly_lat_max(self):
        """PHILLY_LAT_MAX is 40.15."""
        assert PHILLY_LAT_MAX == 40.15


class TestCrimeIncidentValidatorValidData:
    """Tests for CrimeIncidentValidator with valid data."""

    def test_valid_incident_with_all_fields(self):
        """Valid incident with all required fields."""
        validator = CrimeIncidentValidator(
            incident_id="12345",
            dispatch_date="2020-01-01T12:00:00",
            ucr_general=600,
            text_general_code="Theft",
            point_x=-75.16,
            point_y=39.95,
            dc_key=1,
            psa="A",
        )
        assert validator.incident_id == "12345"
        assert validator.ucr_general == 600

    def test_valid_incident_with_required_fields_only(self):
        """Valid incident with only required fields."""
        validator = CrimeIncidentValidator(
            dispatch_date="2020-01-01T12:00:00",
            ucr_general=100,
        )
        assert validator.ucr_general == 100

    def test_valid_ucr_code_in_expanded_format(self):
        """Valid UCR codes in expanded format (100-9999)."""
        valid_codes = [100, 600, 999, 1500, 2500, 7999]
        for code in valid_codes:
            validator = CrimeIncidentValidator(
                dispatch_date="2020-01-01T12:00:00", ucr_general=code
            )
            assert validator.ucr_general == code

    def test_valid_psa_as_letter_code(self):
        """Valid PSA as letter code."""
        for psa in ["A", "E", "D", "B", "C"]:
            validator = CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", psa=psa)
            assert validator.psa == psa

    def test_valid_psa_as_string_number(self):
        """Valid PSA as string number."""
        validator = CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", psa="1")
        assert validator.psa == "1"

    def test_valid_coordinates_within_philly_bounds(self):
        """Valid coordinates within Philadelphia bounds."""
        # Center City Philadelphia
        validator = CrimeIncidentValidator(
            dispatch_date="2020-01-01T12:00:00",
            point_x=-75.16,  # Within -75.3 to -74.95
            point_y=39.95,  # Within 39.85 to 40.15
        )
        assert validator.point_x == -75.16
        assert validator.point_y == 39.95

    def test_valid_datetime_string(self):
        """Valid datetime string."""
        validator = CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", ucr_general=100)
        assert isinstance(validator.dispatch_date, datetime)

    def test_none_values_for_optional_fields(self):
        """None values are accepted for optional fields."""
        validator = CrimeIncidentValidator(
            dispatch_date="2020-01-01T12:00:00",
            ucr_general=None,
            point_x=None,
            point_y=None,
            dc_key=None,
            psa=None,
        )
        assert validator.ucr_general is None
        assert validator.point_x is None
        assert validator.point_y is None

    def test_boundary_case_minimum_coordinates(self):
        """Boundary case: minimum valid coordinates."""
        validator = CrimeIncidentValidator(
            dispatch_date="2020-01-01T12:00:00",
            point_x=PHILLY_LON_MIN,
            point_y=PHILLY_LAT_MIN,
        )
        assert validator.point_x == PHILLY_LON_MIN
        assert validator.point_y == PHILLY_LAT_MIN

    def test_boundary_case_maximum_coordinates(self):
        """Boundary case: maximum valid coordinates."""
        validator = CrimeIncidentValidator(
            dispatch_date="2020-01-01T12:00:00",
            point_x=PHILLY_LON_MAX,
            point_y=PHILLY_LAT_MAX,
        )
        assert validator.point_x == PHILLY_LON_MAX
        assert validator.point_y == PHILLY_LAT_MAX


class TestCrimeIncidentValidatorInvalidData:
    """Tests for CrimeIncidentValidator with invalid data."""

    def test_invalid_ucr_code_below_minimum(self):
        """UCR code below 100 raises ValidationError."""
        with pytest.raises(ValidationError, match="greater than or equal to 100"):
            CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", ucr_general=99)

    def test_invalid_ucr_code_above_maximum(self):
        """UCR code above 9999 raises ValidationError."""
        with pytest.raises(ValidationError, match="less than or equal to 9999"):
            CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", ucr_general=10000)

    def test_invalid_longitude_below_minimum(self):
        """Longitude below -75.3 raises ValidationError."""
        with pytest.raises(ValidationError):
            CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", point_x=-75.31)

    def test_invalid_longitude_above_maximum(self):
        """Longitude above -74.95 raises ValidationError."""
        with pytest.raises(ValidationError):
            CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", point_x=-74.94)

    def test_invalid_latitude_below_minimum(self):
        """Latitude below 39.85 raises ValidationError."""
        with pytest.raises(ValidationError):
            CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", point_y=39.84)

    def test_invalid_latitude_above_maximum(self):
        """Latitude above 40.15 raises ValidationError."""
        with pytest.raises(ValidationError):
            CrimeIncidentValidator(dispatch_date="2020-01-01T12:00:00", point_y=40.16)

    def test_invalid_datetime_string(self):
        """Invalid datetime string raises ValidationError."""
        with pytest.raises(ValidationError):
            CrimeIncidentValidator(dispatch_date="invalid-date", ucr_general=100)

    def test_missing_required_field_dispatch_date(self):
        """Missing required dispatch_date raises ValidationError."""
        with pytest.raises(ValidationError):
            CrimeIncidentValidator(ucr_general=100)


class TestValidateCoordinates:
    """Tests for validate_coordinates function."""

    def test_valid_philly_coordinates_pass(self):
        """Valid Philadelphia coordinates pass validation."""
        df = pd.DataFrame(
            {
                "point_x": [-75.16, -75.20, -75.10],
                "point_y": [39.95, 40.00, 39.90],
            }
        )
        result = validate_coordinates(df)
        assert len(result) == 3

    def test_invalid_coordinates_filtered_out(self):
        """Invalid coordinates outside Philly bounds are filtered out."""
        df = pd.DataFrame(
            {
                "point_x": [-75.16, -100.0, -75.10],  # -100.0 is invalid
                "point_y": [39.95, 40.00, 50.0],  # 50.0 is invalid
            }
        )
        result = validate_coordinates(df)
        assert len(result) == 1  # Only first row is valid

    def test_none_coordinates_filtered_out(self):
        """None/NaN coordinates are filtered out."""
        df = pd.DataFrame(
            {
                "point_x": [-75.16, None, -75.10],
                "point_y": [39.95, 40.00, None],
            }
        )
        result = validate_coordinates(df)
        assert len(result) == 1  # Only first row is valid

    def test_boundary_case_edge_coordinates(self):
        """Boundary case: coordinates at edge of Philly bounds."""
        df = pd.DataFrame(
            {
                "point_x": [PHILLY_LON_MIN, PHILLY_LON_MAX, -75.16],
                "point_y": [PHILLY_LAT_MIN, PHILLY_LAT_MAX, 39.95],
            }
        )
        result = validate_coordinates(df)
        assert len(result) == 3  # All boundary coordinates are valid

    def test_boundary_case_just_outside_bounds(self):
        """Boundary case: coordinates just outside Philly bounds."""
        df = pd.DataFrame(
            {
                "point_x": [PHILLY_LON_MIN - 0.01, PHILLY_LON_MAX + 0.01],
                "point_y": [PHILLY_LAT_MIN - 0.01, PHILLY_LAT_MAX + 0.01],
            }
        )
        result = validate_coordinates(df)
        assert len(result) == 0  # All coordinates are outside bounds

    def test_custom_column_names(self):
        """Custom column names for longitude and latitude."""
        df = pd.DataFrame(
            {
                "custom_lon": [-75.16],
                "custom_lat": [39.95],
            }
        )
        result = validate_coordinates(df, x_col="custom_lon", y_col="custom_lat")
        assert len(result) == 1

    def test_missing_x_column_raises_value_error(self):
        """Missing x_col raises ValueError."""
        df = pd.DataFrame({"point_y": [39.95]})
        with pytest.raises(ValueError, match="Column 'point_x' not found"):
            validate_coordinates(df)

    def test_missing_y_column_raises_value_error(self):
        """Missing y_col raises ValueError."""
        df = pd.DataFrame({"point_x": [-75.16]})
        with pytest.raises(ValueError, match="Column 'point_y' not found"):
            validate_coordinates(df)

    def test_custom_bounds(self):
        """Custom coordinate bounds."""
        df = pd.DataFrame(
            {
                "point_x": [-75.16, -70.0],
                "point_y": [39.95, 40.0],
            }
        )
        # Use custom bounds that include both coordinates
        result = validate_coordinates(df, lon_bounds=(-80.0, -70.0), lat_bounds=(39.0, 41.0))
        assert len(result) == 2


class TestValidateCrimeData:
    """Tests for validate_crime_data function."""

    @pytest.fixture
    def valid_sample_df(self):
        """Create a valid sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "incident_id": ["1", "2", "3", "4", "5"],
                "dispatch_date": pd.to_datetime(
                    ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
                ),
                "ucr_general": [100, 600, 300, 700, 200],
                "text_general_code": ["Homicide", "Theft", "Robbery", "Vehicle Theft", "Rape"],
                "point_x": [-75.16, -75.20, -75.10, -75.05, -75.15],
                "point_y": [39.95, 40.00, 39.90, 40.05, 39.92],
                "dc_key": [1, 2, 3, 4, 5],
                "psa": ["A", "B", "C", "D", "E"],
            }
        )

    @pytest.fixture
    def invalid_sample_df(self):
        """Create a DataFrame with some invalid rows."""
        return pd.DataFrame(
            {
                "incident_id": ["1", "2", "3"],
                "dispatch_date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
                "ucr_general": [100, 50, 300],  # 50 is invalid (< 100)
                "text_general_code": ["Homicide", "Invalid", "Robbery"],
                "point_x": [-75.16, -75.20, -100.0],  # -100.0 is invalid longitude
                "point_y": [39.95, 40.00, 50.0],  # 50.0 is invalid latitude
            }
        )

    def test_valid_sample_dataframe_passes(self, valid_sample_df):
        """Valid sample DataFrame passes validation."""
        result = validate_crime_data(valid_sample_df)
        assert result is valid_sample_df  # Returns same DataFrame

    def test_strict_mode_validates_all_rows(self, valid_sample_df):
        """Strict mode validates all rows."""
        result = validate_crime_data(valid_sample_df, strict=True)
        assert result is valid_sample_df

    def test_invalid_dataframe_raises_value_error(self, invalid_sample_df):
        """DataFrame with invalid rows raises ValueError."""
        with pytest.raises(ValueError, match="Data validation failed"):
            validate_crime_data(invalid_sample_df)

    def test_error_details_in_error_message(self, invalid_sample_df):
        """Error message includes details about validation failures."""
        with pytest.raises(ValueError) as exc_info:
            validate_crime_data(invalid_sample_df)
        error_message = str(exc_info.value)
        assert "Data validation failed" in error_message
        assert "errors" in error_message

    def test_empty_dataframe_raises_value_error(self):
        """Empty DataFrame raises ValueError."""
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="DataFrame is empty"):
            validate_crime_data(df)

    def test_sample_size_parameter_limits_validation(self, valid_sample_df):
        """sample_size parameter limits number of rows validated."""
        # Should only validate first 2 rows (default sample_size=1000)
        result = validate_crime_data(valid_sample_df, sample_size=2)
        assert result is valid_sample_df

    def test_returns_validated_dataframe(self, valid_sample_df):
        """Returns the validated DataFrame."""
        result = validate_crime_data(valid_sample_df)
        pd.testing.assert_frame_equal(result, valid_sample_df)

    @pytest.mark.slow
    def test_strict_mode_with_large_dataset(self):
        """Strict mode with larger dataset (slow test)."""
        df = pd.DataFrame(
            {
                "dispatch_date": pd.date_range("2020-01-01", periods=100),
                "ucr_general": [100] * 100,
                "point_x": [-75.16] * 100,
                "point_y": [39.95] * 100,
            }
        )
        result = validate_crime_data(df, strict=True)
        assert len(result) == 100
