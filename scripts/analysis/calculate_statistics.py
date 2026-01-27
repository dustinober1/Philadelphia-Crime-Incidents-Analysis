#!/usr/bin/env python3
"""
Statistical analysis script for Philadelphia crime incidents data.
Generates descriptive statistics, trends, and correlations.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.analysis.profiler import DataProfiler
from src.data.loader import load_crime_data


def main():
    """Main function to run statistical analysis on crime data."""
    print("=" * 80)
    print("PHILADELPHIA CRIME INCIDENTS - STATISTICAL ANALYSIS REPORT")
    print("=" * 80)

    try:
        # Load the crime data
        print("\nLoading crime data...")
        df = load_crime_data()

        # Ensure dispatch_date_time is converted to datetime if not already
        if "dispatch_date_time" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["dispatch_date_time"]):
                df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])

        print(f"Data loaded successfully. Shape: {df.shape}")

        # Initialize the DataProfiler
        profiler = DataProfiler(df)

        # 1. General Stats: get_summary() (STAT-01)
        print("\n" + "=" * 80)
        print("GENERAL STATISTICS")
        print("=" * 80)
        summary = profiler.get_summary()
        print(f"Dataset shape: {summary['shape']}")
        print(f"Memory usage: {summary['memory_usage']} bytes")
        print(f"Columns: {len(summary['columns'])}")
        if summary["numerical_stats"]:
            print(f"Numerical statistics:")
            for stat, values in summary["numerical_stats"].items():
                print(f"  {stat}: {values}")

        # 2. Frequencies: analyze_group_stats for text_general_code (crime type) and dc_dist (district) (STAT-02, STAT-03)
        print("\n" + "=" * 80)
        print("TOP CRIMES BY TYPE")
        print("=" * 80)
        if "text_general_code" in df.columns:
            try:
                crime_frequencies = profiler.analyze_group_stats("text_general_code")
                print("Top 10 Crime Types:")
                for idx, (crime_type, count) in enumerate(
                    crime_frequencies.head(10).iterrows(), 1
                ):
                    print(f"{idx:2d}. {crime_type:<40} : {count['count']:>8,}")
            except Exception as e:
                print(f"Error analyzing crime types: {e}")
        else:
            print("Column 'text_general_code' not found in dataset")

        print("\n" + "=" * 80)
        print("DISTRICT BREAKDOWN")
        print("=" * 80)
        if "dc_dist" in df.columns:
            try:
                district_frequencies = profiler.analyze_group_stats("dc_dist")
                print("Top 10 Districts by Crime Count:")
                for idx, (district, count) in enumerate(
                    district_frequencies.head(10).iterrows(), 1
                ):
                    print(f"{idx:2d}. {str(district):<40} : {count['count']:>8,}")
            except Exception as e:
                print(f"Error analyzing districts: {e}")
        else:
            print("Column 'dc_dist' not found in dataset")

        # 3. Time Analysis: analyze_time_series on dispatch_date_time (Monthly freq) (STAT-04)
        print("\n" + "=" * 80)
        print("TIME TRENDS (MONTHLY)")
        print("=" * 80)
        if "dispatch_date_time" in df.columns:
            try:
                monthly_trends = profiler.analyze_time_series(
                    "dispatch_date_time", freq="M"
                )
                print("Monthly Crime Trends (First 10 months):")
                for idx, (date, count) in enumerate(
                    monthly_trends.head(10).iterrows(), 1
                ):
                    print(
                        f"{idx:2d}. {date.strftime('%Y-%m'):<12} : {count['count']:>8,}"
                    )

                print(f"\nMonthly Crime Trends (Last 10 months):")
                for idx, (date, count) in enumerate(
                    monthly_trends.tail(10).iterrows(), len(monthly_trends) - 9
                ):
                    print(
                        f"{idx:2d}. {date.strftime('%Y-%m'):<12} : {count['count']:>8,}"
                    )

                print(
                    f"\nOverall Period: {monthly_trends.index.min().strftime('%Y-%m')} to {monthly_trends.index.max().strftime('%Y-%m')}"
                )
                print(f"Average Monthly Crimes: {monthly_trends['count'].mean():.1f}")
                highest_idx = monthly_trends["count"].idxmax()
                lowest_idx = monthly_trends["count"].idxmin()
                print(
                    f"Highest Month: {highest_idx.strftime('%Y-%m')} ({monthly_trends.loc[highest_idx, 'count']:,} crimes)"
                )
                print(
                    f"Lowest Month: {lowest_idx.strftime('%Y-%m')} ({monthly_trends.loc[lowest_idx, 'count']:,} crimes)"
                )
            except Exception as e:
                print(f"Error analyzing time trends: {e}")
        else:
            print("Column 'dispatch_date_time' not found in dataset")

        # 4. Correlations: analyze_bivariate_categorical for Type vs District (STAT-05)
        print("\n" + "=" * 80)
        print("CRIME TYPE vs DISTRICT CORRELATION")
        print("=" * 80)
        if "text_general_code" in df.columns and "dc_dist" in df.columns:
            try:
                # Get top 5 crime types and top 5 districts to make the cross-tab manageable
                top_crimes = (
                    df["text_general_code"].value_counts().head(5).index.tolist()
                )
                top_districts = df["dc_dist"].value_counts().head(5).index.tolist()

                # Filter dataframe to top crimes and districts
                filtered_df = df[
                    df["text_general_code"].isin(top_crimes)
                    & df["dc_dist"].isin(top_districts)
                ]

                # Create a subset profiler for the filtered data
                filtered_profiler = DataProfiler(filtered_df.copy())
                correlation_table = filtered_profiler.analyze_bivariate_categorical(
                    "text_general_code", "dc_dist"
                )

                print("Cross-tabulation of Top 5 Crime Types vs Top 5 Districts:")
                print(correlation_table)

                # Additional correlation analysis
                print(f"\nAdditional correlation insights:")
                print(f"- Total combinations analyzed: {correlation_table.size}")
                print(
                    f"- Most common crime-district pair: {correlation_table.unstack().idxmax()}"
                )

            except Exception as e:
                print(f"Error analyzing crime type vs district correlation: {e}")
        else:
            print("Either 'text_general_code' or 'dc_dist' column not found in dataset")

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        return df, profiler

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    df, profiler = main()
