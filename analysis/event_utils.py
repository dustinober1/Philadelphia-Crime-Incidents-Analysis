"""Event impact analysis utilities for Phase 3."""

from typing import Any

import pandas as pd


def identify_event_days(
    crime_df: pd.DataFrame,
    event_df: pd.DataFrame,
    date_col: str = "dispatch_date",
    buffer_days: int = 0,
) -> pd.DataFrame:
    """Tag crime records with event-day indicators.

    Parameters
    ----------
    crime_df : pd.DataFrame
        Crime incidents with date column
    event_df : pd.DataFrame
        Event calendar with 'date' and 'event_type' columns
    date_col : str
        Name of date column in crime_df
    buffer_days : int
        Include N days before/after events

    Returns
    -------
    pd.DataFrame
        Crime data with event indicator columns added
    """
    crime_df = crime_df.copy()
    crime_df[date_col] = pd.to_datetime(crime_df[date_col]).dt.normalize()

    # Create expanded event dates with buffer
    event_dates: set[pd.Timestamp] = set()
    for date in event_df["date"]:
        for offset in range(-buffer_days, buffer_days + 1):
            event_dates.add(date + pd.Timedelta(days=offset))

    crime_df["is_event_day"] = crime_df[date_col].isin(event_dates)

    # Add specific event type indicators
    for event_type in event_df["event_type"].unique():
        type_dates = set(event_df[event_df["event_type"] == event_type]["date"])
        expanded_dates: set[pd.Timestamp] = set()
        for date in type_dates:
            for offset in range(-buffer_days, buffer_days + 1):
                expanded_dates.add(date + pd.Timedelta(days=offset))
        crime_df[f"is_{event_type}_day"] = crime_df[date_col].isin(expanded_dates)

    return crime_df


def get_control_days(
    event_date: pd.Timestamp,
    all_dates: pd.DatetimeIndex,
    event_dates: set[pd.Timestamp],
    n_controls: int = 4,
) -> list[pd.Timestamp]:
    """Get control days for an event (same day-of-week, non-event days).

    Parameters
    ----------
    event_date : pd.Timestamp
        The event date
    all_dates : pd.DatetimeIndex
        All available dates in the crime data
    event_dates : set
        Set of all event dates to exclude
    n_controls : int
        Number of control days to find (before and after combined)

    Returns
    -------
    List[pd.Timestamp]
        Control day dates
    """
    controls: list[pd.Timestamp] = []
    all_dates_set = set(all_dates)

    # Look for same day-of-week in adjacent weeks
    for weeks in range(1, n_controls + 1):
        before = event_date - pd.Timedelta(weeks=weeks)
        after = event_date + pd.Timedelta(weeks=weeks)

        if before in all_dates_set and before not in event_dates:
            controls.append(before)
        if after in all_dates_set and after not in event_dates:
            controls.append(after)

        if len(controls) >= n_controls:
            break

    return controls[:n_controls]


def calculate_event_impact(
    crime_df: pd.DataFrame,
    event_df: pd.DataFrame,
    crime_category: str = None,
    date_col: str = "dispatch_date",
) -> dict[str, Any]:
    """Calculate difference-in-means for event vs control days.

    Parameters
    ----------
    crime_df : pd.DataFrame
        Crime incidents with date column
    event_df : pd.DataFrame
        Event calendar with 'date' column
    crime_category : str, optional
        Filter to specific crime category
    date_col : str
        Name of date column in crime_df

    Returns
    -------
    dict
        Dictionary with mean counts, difference, and statistical tests
    """
    from scipy import stats

    df = crime_df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()

    if crime_category:
        df = df[df["crime_category"] == crime_category]

    # Daily counts
    daily_counts = df.groupby(date_col).size()

    event_dates = set(event_df["date"])
    event_counts = daily_counts[daily_counts.index.isin(event_dates)]
    control_counts = daily_counts[~daily_counts.index.isin(event_dates)]

    event_mean = event_counts.mean()
    control_mean = control_counts.mean()
    diff = event_mean - control_mean

    # T-test for statistical significance
    t_result = stats.ttest_ind(event_counts, control_counts)

    return {
        "event_mean": event_mean,
        "control_mean": control_mean,
        "difference": diff,
        "pct_change": (diff / control_mean * 100) if control_mean > 0 else None,
        "p_value": t_result.pvalue,
        "n_event_days": len(event_counts),
        "n_control_days": len(control_counts),
        "significant": t_result.pvalue < 0.05,
    }


def calculate_event_impact_by_type(
    crime_df: pd.DataFrame, event_df: pd.DataFrame, date_col: str = "dispatch_date"
) -> pd.DataFrame:
    """Calculate event impact separately for each event type.

    Parameters
    ----------
    crime_df : pd.DataFrame
        Crime incidents with date column
    event_df : pd.DataFrame
        Event calendar with 'date' and 'event_type' columns
    date_col : str
        Name of date column in crime_df

    Returns
    -------
    pd.DataFrame
        Impact statistics by event type
    """
    results = []

    for event_type in event_df["event_type"].unique():
        type_events = event_df[event_df["event_type"] == event_type]
        impact = calculate_event_impact(crime_df, type_events, date_col=date_col)
        impact["event_type"] = event_type
        results.append(impact)

    return pd.DataFrame(results)


def generate_matched_controls(
    event_df: pd.DataFrame,
    crime_df: pd.DataFrame,
    date_col: str = "dispatch_date",
    n_controls: int = 4,
) -> pd.DataFrame:
    """Generate matched control days for each event.

    Uses same day-of-week matching from adjacent weeks.

    Parameters
    ----------
    event_df : pd.DataFrame
        Event calendar with 'date' column
    crime_df : pd.DataFrame
        Crime data to get available dates
    date_col : str
        Name of date column
    n_controls : int
        Number of control days per event

    Returns
    -------
    pd.DataFrame
        Control days with event_date they are matched to
    """
    df = crime_df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()
    all_dates = pd.DatetimeIndex(df[date_col].unique())
    event_dates = set(event_df["date"])

    controls = []
    for _, row in event_df.iterrows():
        event_date = row["date"]
        matched = get_control_days(event_date, all_dates, event_dates, n_controls)
        for control_date in matched:
            controls.append(
                {
                    "control_date": control_date,
                    "matched_event_date": event_date,
                    "event_type": row.get("event_type", "unknown"),
                    "event_name": row.get("event_name", "unknown"),
                }
            )

    return pd.DataFrame(controls)
