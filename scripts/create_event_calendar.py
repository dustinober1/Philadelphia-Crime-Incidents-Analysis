"""Create event calendar for Phase 3 event impact analysis."""

from pathlib import Path

import pandas as pd


def generate_holidays(start_year: int, end_year: int) -> pd.DataFrame:
    """Generate federal holiday dates.

    Parameters
    ----------
    start_year : int
        Start year for calendar
    end_year : int
        End year for calendar (inclusive)

    Returns
    -------
    pd.DataFrame
        DataFrame with date, event_type, and event_name columns
    """
    from pandas.tseries.holiday import (
        USFederalHolidayCalendar,
    )

    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=f"{start_year}-01-01", end=f"{end_year}-12-31")

    # Map dates to holiday names
    holiday_names = {
        1: {1: "New Year's Day"},
        7: {4: "Independence Day"},
        11: {11: "Veterans Day"},
        12: {25: "Christmas Day"},
    }

    records = []
    for date in holidays:
        # Determine holiday name
        month, day = date.month, date.day
        if month in holiday_names and day in holiday_names[month]:
            name = holiday_names[month][day]
        elif month == 1 and 15 <= day <= 21 and date.dayofweek == 0:
            name = "MLK Day"
        elif month == 2 and 15 <= day <= 21 and date.dayofweek == 0:
            name = "Presidents Day"
        elif month == 5 and 25 <= day <= 31 and date.dayofweek == 0:
            name = "Memorial Day"
        elif month == 9 and 1 <= day <= 7 and date.dayofweek == 0:
            name = "Labor Day"
        elif month == 10 and 8 <= day <= 14 and date.dayofweek == 0:
            name = "Columbus Day"
        elif month == 11 and 22 <= day <= 28 and date.dayofweek == 3:
            name = "Thanksgiving"
        else:
            name = "Federal Holiday"

        records.append(
            {
                "date": date,
                "event_type": "holiday",
                "event_name": name,
                "team": None,
            }
        )

    return pd.DataFrame(records)


def generate_sports_schedule(start_year: int, end_year: int) -> pd.DataFrame:
    """Generate approximate sports game dates.

    Note: For production, use official team APIs or sports-reference data.
    This creates approximate schedules based on typical season patterns.

    Parameters
    ----------
    start_year : int
        Start year for calendar
    end_year : int
        End year for calendar (inclusive)

    Returns
    -------
    pd.DataFrame
        DataFrame with date, event_type, event_name, and team columns
    """
    games = []

    for year in range(start_year, end_year + 1):
        # Eagles (Sept-Dec/Jan, ~8-10 home games per regular season)
        # Home games typically on Sundays
        eagles_dates = pd.date_range(f"{year}-09-01", f"{year}-12-31", freq="W-SUN")
        # Select ~8 dates spread across the season
        eagles_home = eagles_dates[::2][:8]  # Every other Sunday, max 8
        for date in eagles_home:
            games.append(
                {
                    "date": date.normalize(),
                    "event_type": "sports",
                    "event_name": "Eagles Home Game",
                    "team": "Eagles",
                }
            )

        # Phillies (Apr-Sept, ~81 home games per season)
        # Distribute roughly evenly across the season
        phillies_start = pd.Timestamp(f"{year}-04-01")
        phillies_end = pd.Timestamp(f"{year}-09-30")
        phillies_dates = pd.date_range(phillies_start, phillies_end, periods=40)
        for date in phillies_dates:
            games.append(
                {
                    "date": date.normalize(),
                    "event_type": "sports",
                    "event_name": "Phillies Home Game",
                    "team": "Phillies",
                }
            )

        # 76ers (Oct-Apr, ~41 home games per season)
        # Season spans two calendar years
        sixers_start = pd.Timestamp(f"{year}-10-20")
        sixers_end = pd.Timestamp(f"{year + 1}-04-10")
        sixers_dates = pd.date_range(sixers_start, sixers_end, periods=20)
        for date in sixers_dates:
            games.append(
                {
                    "date": date.normalize(),
                    "event_type": "sports",
                    "event_name": "76ers Home Game",
                    "team": "76ers",
                }
            )

        # Flyers (Oct-Apr, ~41 home games per season)
        flyers_start = pd.Timestamp(f"{year}-10-05")
        flyers_end = pd.Timestamp(f"{year + 1}-04-05")
        flyers_dates = pd.date_range(flyers_start, flyers_end, periods=20)
        for date in flyers_dates:
            games.append(
                {
                    "date": date.normalize(),
                    "event_type": "sports",
                    "event_name": "Flyers Home Game",
                    "team": "Flyers",
                }
            )

    return pd.DataFrame(games)


def add_special_events(start_year: int, end_year: int) -> pd.DataFrame:
    """Add known special events that may affect crime patterns.

    Includes: July 4th celebrations, New Year's Eve, etc.
    """
    events = []

    for year in range(start_year, end_year + 1):
        # New Year's Eve (distinct from New Year's Day)
        events.append(
            {
                "date": pd.Timestamp(f"{year}-12-31"),
                "event_type": "celebration",
                "event_name": "New Year's Eve",
                "team": None,
            }
        )

        # July 4th weekend (if not already captured)
        events.append(
            {
                "date": pd.Timestamp(f"{year}-07-03"),
                "event_type": "celebration",
                "event_name": "July 4th Eve",
                "team": None,
            }
        )

    return pd.DataFrame(events)


def main():
    """Create event calendar and save to parquet."""
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "data" / "external" / "event_calendar.parquet"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start_year, end_year = 2015, 2025

    print(f"Generating event calendar for {start_year}-{end_year}...")

    # Generate calendars
    holidays = generate_holidays(start_year, end_year)
    print(f"Generated {len(holidays)} holiday records")

    sports = generate_sports_schedule(start_year, end_year)
    print(f"Generated {len(sports)} sports game records")

    special = add_special_events(start_year, end_year)
    print(f"Generated {len(special)} special event records")

    # Combine
    calendar = pd.concat([holidays, sports, special], ignore_index=True)

    # Normalize dates and deduplicate
    calendar["date"] = pd.to_datetime(calendar["date"]).dt.normalize()
    calendar = calendar.drop_duplicates(subset=["date", "event_type", "event_name"])
    calendar = calendar.sort_values("date").reset_index(drop=True)

    # Save
    calendar.to_parquet(output_path, index=False)

    print("\n=== Event Calendar Summary ===")
    print(f"Total events: {len(calendar)}")
    print(f"Date range: {calendar['date'].min().date()} to {calendar['date'].max().date()}")
    print("\nEvents by type:")
    print(calendar["event_type"].value_counts().to_string())
    print("\nSports events by team:")
    print(calendar[calendar["event_type"] == "sports"]["team"].value_counts().to_string())
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
