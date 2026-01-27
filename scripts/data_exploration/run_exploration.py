import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path to ensure src can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data.loader import load_crime_data
from src.analysis.profiler import DataProfiler


def print_section(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def main():
    print("Loading data...")
    try:
        df = load_crime_data()
        print(f"Data loaded successfully. Shape: {df.shape}")
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Ensure you have run the data processing steps first.")
        sys.exit(1)

    profiler = DataProfiler(df)

    print_section("DATASET SUMMARY")
    summary = profiler.get_summary()
    for key, value in summary.items():
        if key == "numerical_stats":
            print("\nNumerical Stats:")
            stats_df = pd.DataFrame(value)
            print(stats_df)
        else:
            print(f"{key}: {value}")

    print_section("DATA TYPES")
    print(profiler.check_types())

    print_section("MISSING VALUES")
    missing = profiler.check_missing_values()
    if not missing.empty and missing["missing_count"].sum() > 0:
        print(missing[missing["missing_count"] > 0])
    else:
        print("No missing values found.")

    print_section("DUPLICATES")
    print(f"Duplicate rows: {profiler.check_duplicates()}")

    print_section("OUTLIERS (Numeric Columns)")
    outliers = profiler.check_outliers()
    if not outliers.empty:
        print(outliers)
    else:
        print("No outliers detected.")

    print_section("CATEGORICAL BREAKDOWN (Top 5)")
    breakdown = profiler.check_categorical_breakdown()
    if breakdown:
        for col, counts in breakdown.items():
            print(f"\nColumn: {col}")
            for cat, count in counts.items():
                print(f"  {cat}: {count}")
    else:
        print("No categorical columns found.")


if __name__ == "__main__":
    main()
