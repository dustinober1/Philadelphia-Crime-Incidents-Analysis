import pandas as pd
from typing import Dict


def validate_coordinates(
    df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude"
) -> bool:
    """
    Validate that coordinate values are within reasonable ranges.

    Args:
        df (pd.DataFrame): DataFrame to validate.
        lat_col (str): Name of latitude column. Defaults to 'latitude'.
        lon_col (str): Name of longitude column. Defaults to 'longitude'.

    Returns:
        bool: True if all coordinates are valid.

    Raises:
        ValueError: If coordinates are out of valid ranges.
    """
    # Check latitude range (-90 to 90)
    if lat_col in df.columns:
        invalid_lat = (df[lat_col] < -90) | (df[lat_col] > 90)
        if invalid_lat.any():
            raise ValueError(
                f"Invalid latitude values found. Valid range: -90 to 90. "
                f"Found: {df[invalid_lat][lat_col].min()} to {df[invalid_lat][lat_col].max()}"
            )

    # Check longitude range (-180 to 180)
    if lon_col in df.columns:
        invalid_lon = (df[lon_col] < -180) | (df[lon_col] > 180)
        if invalid_lon.any():
            raise ValueError(
                f"Invalid longitude values found. Valid range: -180 to 180. "
                f"Found: {df[invalid_lon][lon_col].min()} to {df[invalid_lon][lon_col].max()}"
            )

    return True


# Color mapping for different crime types
CRIME_TYPE_COLORS: Dict[str, str] = {
    "assault": "red",
    "theft": "orange",
    "robbery": "darkred",
    "burglary": "purple",
    "fraud": "pink",
    "drug": "brown",
    "homicide": "darkred",
    "shooting": "red",
    "carjacking": "orange",
    "rape": "darkpurple",
    "murder": "darkred",
}


def get_marker_color(crime_type: str) -> str:
    """
    Return color for different crime types for map visualization.

    Args:
        crime_type (str): The crime type to get color for.

    Returns:
        str: Color string for the crime type (folium color name).
    """
    if pd.isna(crime_type):
        return "gray"

    # Convert to lowercase for matching
    crime_lower = str(crime_type).lower()

    # Check direct match first
    if crime_lower in CRIME_TYPE_COLORS:
        return CRIME_TYPE_COLORS[crime_lower]

    # Check if crime type contains known keywords
    for crime_keyword, color in CRIME_TYPE_COLORS.items():
        if crime_keyword in crime_lower:
            return color

    # Default color for unknown crime types
    return "blue"


def get_phl_center_coordinates() -> list:
    """
    Return approximate center coordinates of Philadelphia.

    Returns:
        list: [latitude, longitude] for Philadelphia center.
    """
    return [39.9526, -75.1652]


def prepare_coordinate_data(
    df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude"
) -> pd.DataFrame:
    """
    Clean and prepare coordinate data for geospatial analysis.

    Removes rows with missing coordinates and validates coordinate ranges.

    Args:
        df (pd.DataFrame): DataFrame to prepare.
        lat_col (str): Name of latitude column. Defaults to 'latitude'.
        lon_col (str): Name of longitude column. Defaults to 'longitude'.

    Returns:
        pd.DataFrame: Cleaned DataFrame with valid coordinates.

    Raises:
        ValueError: If no valid coordinates found.
    """
    # Create a copy to avoid modifying original
    df_clean = df.copy()

    # Remove rows with missing coordinates
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=[lat_col, lon_col])

    if len(df_clean) == 0:
        raise ValueError(
            f"No valid coordinates found after removing missing values. "
            f"Removed {initial_count} rows."
        )

    # Validate coordinates
    validate_coordinates(df_clean, lat_col, lon_col)

    removed_count = initial_count - len(df_clean)
    if removed_count > 0:
        print(f"Removed {removed_count} rows with missing coordinates")

    return df_clean
