"""Crime classification utilities.

This module provides functions for classifying crimes into categories
(Violent, Property, Other) based on UCR general codes.
"""

from __future__ import annotations

import pandas as pd

# UCR hundred-bands: 1=Homicide, 2=Rape, 3=Robbery, 4=Agg Assault,
# 5=Burglary, 6=Theft, 7=Vehicle Theft
CRIME_CATEGORY_MAP: dict[str, set[int]] = {
    "Violent": {1, 2, 3, 4},  # Homicide, Rape, Robbery, Aggravated Assault
    "Property": {5, 6, 7},  # Burglary, Theft, Vehicle Theft
}


def classify_crime_category(df: pd.DataFrame) -> pd.DataFrame:
    """Classify crimes into Violent, Property, or Other.

    This function adds a ``crime_category`` column to the DataFrame based
    on the UCR general code hundred-bands. Classification follows the FBI
    UCR hierarchy where violent crimes include Homicide, Rape, Robbery,
    and Aggravated Assault, while property crimes include Burglary, Theft,
    and Vehicle Theft.

    Args:
        df: Dataset containing a ``ucr_general`` column with UCR general codes.

    Returns:
        DataFrame with a ``crime_category`` column added. Values are
        ``"Violent"``, ``"Property"``, or ``"Other"``.

    Raises:
        ValueError: If ``ucr_general`` column is not found in the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"ucr_general": [100, 200, 500, 600, 999]})
        >>> result = classify_crime_category(df)
        >>> result["crime_category"].tolist()
        ['Violent', 'Violent', 'Property', 'Property', 'Other']
    """
    if "ucr_general" not in df.columns:
        raise ValueError("Expected 'ucr_general' column for classification")

    df = df.copy()
    ucr_series = pd.to_numeric(df["ucr_general"], errors="coerce")
    ucr_group = (ucr_series // 100).astype("Int64")

    df["crime_category"] = "Other"
    for category, groups in CRIME_CATEGORY_MAP.items():
        df.loc[ucr_group.isin(groups), "crime_category"] = category

    return df
