"""
Phase 1: Data Quality Assessment

Analyzes missing data, coordinate validation, duplicates, and generates comprehensive audit reports.
"""

import io
from pathlib import Path
from typing import Dict, Tuple, Optional, Any, Union

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT, STAT_CONFIG, PHILADELPHIA_BBOX, CRIME_DATA_PATH
from analysis.utils import (
    load_data, validate_coordinates, extract_temporal_features,
    get_missing_summary, image_to_base64, create_image_tag, format_number
)
from analysis.reproducibility import set_global_seed, DataVersion, get_analysis_metadata, format_metadata_markdown
from analysis.stats_utils import chi_square_test, bootstrap_ci, apply_fdr_correction


def analyze_data_quality() -> dict:
    """
    Run comprehensive data quality analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    print("Loading data...")
    df = load_data(clean=False)

    results = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
    }

    # ========================================================================
    # 1. Missing Data Analysis
    # ========================================================================
    print("Analyzing missing data...")

    missing_summary = get_missing_summary(df)
    results["missing_summary"] = missing_summary

    # Create missing data heatmap
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    # Sample for heatmap if too large
    sample_df = df.sample(n=min(10000, len(df)), random_state=42)
    missing_sample = sample_df.isnull().astype(int)

    sns.heatmap(missing_sample, cbar=True, cmap="YlOrRd", ax=ax)
    ax.set_title("Missing Data Pattern Heatmap (Sample of 10,000 records)")
    ax.set_xlabel("Columns")
    ax.set_ylabel("Records (Sample)")
    plt.tight_layout()
    results["missing_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Missing data bar chart
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    if not missing_summary.empty:
        missing_plot = missing_summary.head(10).sort_values("missing_count")
        bars = ax.barh(missing_plot["column"], missing_plot["missing_count"], color=COLORS["warning"])
        ax.set_xlabel("Missing Count")
        ax.set_title("Top 10 Columns with Missing Data")
        ax.set_xscale("log")

        # Add count labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f" {format_number(int(width))}", va="center", fontsize=9)
    plt.tight_layout()
    results["missing_bar_chart"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 2. Coordinate Validation
    # ========================================================================
    print("Validating coordinates...")

    df_validated = validate_coordinates(df)
    coord_stats = {
        "total_records": len(df_validated),
        "valid_coordinates": df_validated["valid_coord"].sum(),
        "invalid_coordinates": (~df_validated["valid_coord"]).sum(),
        "valid_pct": (df_validated["valid_coord"].sum() / len(df_validated) * 100),
    }

    # Break down by issue type
    if "coord_issue" in df_validated.columns:
        issue_counts = df_validated["coord_issue"].value_counts()
        coord_stats["by_issue"] = issue_counts.to_dict()

    results["coordinate_stats"] = coord_stats

    # Coordinate issue distribution
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])
    if "coord_issue" in df_validated.columns and not df_validated["coord_issue"].isna().all():
        issue_counts = df_validated["coord_issue"].value_counts()
        colors_list = [COLORS["danger"] if issue != "missing" else COLORS["warning"] for issue in issue_counts.index]
        issue_counts.plot(kind="bar", ax=ax, color=colors_list)
        ax.set_xlabel("Issue Type")
        ax.set_ylabel("Count")
        ax.set_title("Coordinate Issue Distribution")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        # Add count labels
        for i, (idx, val) in enumerate(issue_counts.items()):
            ax.text(i, val, f" {format_number(val)}", va="bottom", fontsize=9)
    plt.tight_layout()
    results["coordinate_issues_chart"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Coordinate scatter plot (sample)
    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES["wide"])
    sample_coords = df_validated.sample(n=min(50000, len(df_validated)), random_state=42)

    # All coordinates
    ax = axes[0]
    valid_mask = sample_coords["valid_coord"]
    ax.scatter(sample_coords.loc[valid_mask, "point_x"],
               sample_coords.loc[valid_mask, "point_y"],
               alpha=0.3, s=1, color=COLORS["primary"], label="Valid")
    if (~valid_mask).sum() > 0:
        ax.scatter(sample_coords.loc[~valid_mask, "point_x"],
                   sample_coords.loc[~valid_mask, "point_y"],
                   alpha=0.5, s=5, color=COLORS["danger"], label="Invalid")
    ax.set_xlabel("Longitude (point_x)")
    ax.set_ylabel("Latitude (point_y)")
    ax.set_title("Coordinate Distribution (Sample)")
    ax.legend()

    # Invalid only
    ax = axes[1]
    invalid_coords = sample_coords[~valid_mask & sample_coords["point_x"].notna() & sample_coords["point_y"].notna()]
    if len(invalid_coords) > 0:
        ax.scatter(invalid_coords["point_x"], invalid_coords["point_y"],
                   alpha=0.5, s=10, color=COLORS["danger"])
        ax.set_xlabel("Longitude (point_x)")
        ax.set_ylabel("Latitude (point_y)")
        ax.set_title(f"Invalid Coordinates Only (n={len(invalid_coords)})")
    else:
        ax.text(0.5, 0.5, "No invalid coordinates\nin sample", ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Invalid Coordinates")
    plt.tight_layout()
    results["coordinate_scatter"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 3. Duplicate Detection
    # ========================================================================
    print("Checking for duplicates...")

    # Check for exact duplicates
    exact_dupes = df.duplicated().sum()

    # Check for duplicate objectid (if exists)
    objectid_dupes = 0
    if "objectid" in df.columns:
        objectid_dupes = df["objectid"].duplicated().sum()

    # Check for duplicate dc_key (if exists)
    dc_key_dupes = 0
    if "dc_key" in df.columns:
        dc_key_dupes = df["dc_key"].duplicated().sum()

    duplicate_stats = {
        "exact_duplicates": int(exact_dupes),
        "duplicate_objectid": int(objectid_dupes),
        "duplicate_dc_key": int(dc_key_dupes),
    }
    results["duplicate_stats"] = duplicate_stats

    # ========================================================================
    # 4. Data Type Summary
    # ========================================================================
    print("Summarizing data types...")

    dtype_summary = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.values,
        "non_null_count": df.count().values,
        "null_count": df.isnull().sum().values,
    })
    dtype_summary["null_pct"] = (dtype_summary["null_count"] / len(df) * 100).round(2)
    results["dtype_summary"] = dtype_summary

    # Data type distribution
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])
    dtype_counts = df.dtypes.value_counts()
    dtype_counts.plot(kind="bar", ax=ax, color=COLORS["primary"])
    ax.set_xlabel("Data Type")
    ax.set_ylabel("Column Count")
    ax.set_title("Data Type Distribution")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    for i, val in enumerate(dtype_counts.values):
        ax.text(i, val, f" {val}", va="bottom", fontsize=10)
    plt.tight_layout()
    results["dtype_distribution"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    print("Data quality analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from data quality analysis results.

    Args:
        results: Dictionary from analyze_data_quality()

    Returns:
        Markdown string with analysis results.
    """
    md = []

    md.append("### Data Quality Assessment\n")
    md.append(f"**Total Records**: {format_number(results['total_records'])}\n")
    md.append(f"**Total Columns**: {results['total_columns']}\n\n")

    # Missing Data Section
    md.append("#### 1. Missing Data Analysis\n\n")

    missing_summary = results["missing_summary"]
    if not missing_summary.empty:
        md.append("| Column | Missing Count | Missing % | Data Type |")
        md.append("|--------|---------------|-----------|-----------|")
        for _, row in missing_summary.iterrows():
            md.append(f"| {row['column']} | {format_number(int(row['missing_count']))} | {row['missing_percentage']}% | {row['dtype']} |")
        md.append("")

        # Missing heatmap
        md.append(results["missing_heatmap"])
        md.append("\n")
        md.append(results["missing_bar_chart"])
        md.append("\n")
    else:
        md.append("*No missing data found in the dataset.*\n")

    # Coordinate Validation Section
    md.append("#### 2. Coordinate Validation\n\n")

    coord_stats = results["coordinate_stats"]
    md.append(f"| Metric | Count | Percentage |")
    md.append("|--------|-------|------------|")
    md.append(f"| Total Records | {format_number(coord_stats['total_records'])} | 100% |")
    md.append(f"| Valid Coordinates | {format_number(coord_stats['valid_coordinates'])} | {coord_stats['valid_pct']:.2f}% |")
    md.append(f"| Invalid Coordinates | {format_number(coord_stats['invalid_coordinates'])} | {(100-coord_stats['valid_pct']):.2f}% |")
    md.append("")

    if "by_issue" in coord_stats:
        md.append("**Issue Breakdown**:\n\n")
        for issue, count in coord_stats["by_issue"].items():
            if pd.notna(issue):
                md.append(f"- **{issue.title()}**: {format_number(count)}")

    md.append("\n")
    md.append(results["coordinate_issues_chart"])
    md.append("\n")
    md.append(results["coordinate_scatter"])
    md.append("\n")

    # Duplicates Section
    md.append("#### 3. Duplicate Detection\n\n")

    dup_stats = results["duplicate_stats"]
    md.append(f"| Check Type | Duplicate Count |")
    md.append("|------------|-----------------|")
    md.append(f"| Exact Duplicate Rows | {format_number(dup_stats['exact_duplicates'])} |")
    md.append(f"| Duplicate objectid | {format_number(dup_stats['duplicate_objectid'])} |")
    md.append(f"| Duplicate dc_key | {format_number(dup_stats['duplicate_dc_key'])} |")
    md.append("")

    # Data Types Section
    md.append("#### 4. Data Types Summary\n\n")

    dtype_summary = results["dtype_summary"]
    md.append("| Column | Data Type | Non-Null Count | Null Count | Null % |")
    md.append("|--------|-----------|----------------|------------|--------|")
    for _, row in dtype_summary.head(20).iterrows():
        md.append(f"| {row['column']} | {row['dtype']} | {format_number(int(row['non_null_count']))} | {format_number(int(row['null_count']))} | {row['null_pct']}% |")
    md.append("")

    md.append(results["dtype_distribution"])
    md.append("\n")

    return "\n".join(md)


# =============================================================================
# COMPREHENSIVE DATA QUALITY AUDIT FUNCTIONS
# =============================================================================

def analyze_missing_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze missing data patterns across columns, crime types, districts, and years.

    Performs comprehensive missing data analysis including:
    - Missing data by column with percentages
    - Missing data by crime type (text_general_code)
    - Missing data by district (dc_dist)
    - Missing data by year
    - Missingness correlation matrix (which columns tend to be missing together)
    - Statistical tests for missingness bias

    Args:
        df: DataFrame with crime incident data

    Returns:
        Dictionary containing all missing data analyses with statistical tests
    """
    results = {}

    # 1. Missing data by column
    missing_by_col = df.isnull().sum()
    missing_pct = (missing_by_col / len(df) * 100).round(2)
    results["by_column"] = pd.DataFrame({
        "column": df.columns,
        "missing_count": missing_by_col.values,
        "missing_pct": missing_pct.values,
        "dtype": df.dtypes.values
    }).sort_values("missing_count", ascending=False)

    # 2. Missing data by crime type (for coordinate columns primarily)
    if "text_general_code" in df.columns:
        crime_missing = df.groupby("text_general_code").apply(
            lambda x: pd.Series({
                "total": len(x),
                "missing_coords": x["point_x"].isna().sum() if "point_x" in x.columns else 0,
                "missing_district": x["dc_dist"].isna().sum() if "dc_dist" in x.columns else 0
            })
        ).reset_index()

        crime_missing["coords_missing_pct"] = (
            crime_missing["missing_coords"] / crime_missing["total"] * 100
        ).round(2)
        crime_missing["district_missing_pct"] = (
            crime_missing["missing_district"] / crime_missing["total"] * 100
        ).round(2)

        results["by_crime_type"] = crime_missing.sort_values("missing_coords", ascending=False)

        # Statistical test: Is missingness independent of crime type?
        # Chi-square test for coordinate missingness by crime type
        if "point_x" in df.columns:
            contingency = pd.crosstab(
                df["text_general_code"],
                df["point_x"].isna().replace({True: "Missing", False: "Present"})
            )
            if contingency.shape[0] > 1 and contingency.shape[1] > 1:
                chi_result = chi_square_test(contingency)
                results["missingness_bias_crime_type"] = {
                    "test": "Chi-square test of independence",
                    "hypothesis": "Coordinate missingness is independent of crime type",
                    "statistic": chi_result["statistic"],
                    "p_value": chi_result["p_value"],
                    "dof": chi_result["dof"],
                    "is_significant": chi_result["p_value"] < STAT_CONFIG["alpha"],
                    "interpretation": (
                        "Missing data IS related to crime type (biased missingness)"
                        if chi_result["p_value"] < STAT_CONFIG["alpha"]
                        else "Missing data is independent of crime type"
                    )
                }

    # 3. Missing data by district
    district_col = None
    for col in ["dc_dist", "police_districts", "district"]:
        if col in df.columns:
            district_col = col
            break

    if district_col:
        district_missing = df.groupby(district_col).apply(
            lambda x: pd.Series({
                "total": len(x),
                "missing_coords": x["point_x"].isna().sum() if "point_x" in x.columns else 0
            })
        ).reset_index()
        district_missing["coords_missing_pct"] = (
            district_missing["missing_coords"] / district_missing["total"] * 100
        ).round(2)
        results["by_district"] = district_missing.sort_values("missing_coords", ascending=False)

        # Statistical test: Is missingness independent of district?
        if "point_x" in df.columns:
            contingency = pd.crosstab(
                df[district_col],
                df["point_x"].isna().replace({True: "Missing", False: "Present"})
            )
            # Filter to districts with sufficient data
            contingency = contingency[contingency.sum(axis=1) >= 5]
            if contingency.shape[0] > 1 and contingency.shape[1] > 1:
                chi_result = chi_square_test(contingency)
                results["missingness_bias_district"] = {
                    "test": "Chi-square test of independence",
                    "hypothesis": "Coordinate missingness is independent of district",
                    "statistic": chi_result["statistic"],
                    "p_value": chi_result["p_value"],
                    "dof": chi_result["dof"],
                    "is_significant": chi_result["p_value"] < STAT_CONFIG["alpha"],
                    "interpretation": (
                        "Missing data IS related to district (biased missingness)"
                        if chi_result["p_value"] < STAT_CONFIG["alpha"]
                        else "Missing data is independent of district"
                    )
                }

    # 4. Missing data by year (temporal pattern)
    if "dispatch_date" in df.columns:
        df_temp = df.copy()
        # Handle categorical/period dtypes
        dates_series = df_temp["dispatch_date"]
        if pd.api.types.is_categorical_dtype(dates_series) or hasattr(dates_series, 'dtype') and str(dates_series.dtype).startswith('period'):
            dates_series = dates_series.astype(str)
        df_temp["year"] = pd.to_datetime(dates_series, errors="coerce").dt.year

        year_missing = df_temp.groupby("year").apply(
            lambda x: pd.Series({
                "total": len(x),
                "missing_coords": x["point_x"].isna().sum() if "point_x" in x.columns else 0
            })
        ).reset_index()
        year_missing["coords_missing_pct"] = (
            year_missing["missing_coords"] / year_missing["total"] * 100
        ).round(2)
        results["by_year"] = year_missing

    # 5. Missingness correlation (which columns tend to be missing together)
    # Use only columns with some missing data for clarity
    missing_cols = df.columns[df.isnull().any()].tolist()
    if len(missing_cols) > 1:
        missing_corr = df[missing_cols].isnull().corr()
        results["missingness_correlation"] = missing_corr

    return results


def coordinate_coverage_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze coordinate coverage across the dataset.

    Performs comprehensive coordinate analysis including:
    - Overall coordinate coverage statistics
    - Coverage by crime type
    - Coverage by district
    - Coverage by year (temporal bias check)
    - Breakdown of invalid coordinates

    Args:
        df: DataFrame with validated coordinates (must have valid_coord column)

    Returns:
        Dictionary containing all coordinate coverage analyses
    """
    results = {}

    # Ensure coordinates are validated
    if "valid_coord" not in df.columns:
        df = validate_coordinates(df)

    total = len(df)
    valid = df["valid_coord"].sum()
    invalid = total - valid
    valid_pct = (valid / total * 100)

    # Overall statistics
    results["overall"] = {
        "total_records": total,
        "valid_count": int(valid),
        "invalid_count": int(invalid),
        "valid_pct": round(valid_pct, 2),
        "invalid_pct": round(100 - valid_pct, 2)
    }

    # Invalid coordinate breakdown
    if "coord_issue" in df.columns:
        issue_counts = df["coord_issue"].value_counts()
        results["by_issue"] = issue_counts.to_dict()

    # Coverage by crime type
    if "text_general_code" in df.columns:
        crime_coverage = df.groupby("text_general_code").apply(
            lambda x: pd.Series({
                "total": len(x),
                "valid_coords": x["valid_coord"].sum(),
                "invalid_coords": (~x["valid_coord"]).sum()
            })
        ).reset_index()
        crime_coverage["coverage_pct"] = (
            crime_coverage["valid_coords"] / crime_coverage["total"] * 100
        ).round(2)
        crime_coverage = crime_coverage.sort_values("coverage_pct")
        results["by_crime_type"] = crime_coverage

        # Statistical test: Is coordinate coverage independent of crime type?
        contingency = pd.crosstab(
            df["text_general_code"],
            df["valid_coord"].replace({True: "Valid", False: "Invalid"})
        )
        if contingency.shape[0] > 1 and contingency.shape[1] > 1:
            chi_result = chi_square_test(contingency)
            results["coverage_bias_crime_type"] = {
                "test": "Chi-square test of independence",
                "hypothesis": "Coordinate coverage is independent of crime type",
                "statistic": chi_result["statistic"],
                "p_value": chi_result["p_value"],
                "dof": chi_result["dof"],
                "is_significant": chi_result["p_value"] < STAT_CONFIG["alpha"],
                "interpretation": (
                    "Coordinate coverage IS related to crime type (biased coverage)"
                    if chi_result["p_value"] < STAT_CONFIG["alpha"]
                    else "Coordinate coverage is independent of crime type"
                )
            }

    # Coverage by district
    district_col = None
    for col in ["dc_dist", "police_districts", "district"]:
        if col in df.columns:
            district_col = col
            break

    if district_col:
        district_coverage = df.groupby(district_col).apply(
            lambda x: pd.Series({
                "total": len(x),
                "valid_coords": x["valid_coord"].sum(),
                "invalid_coords": (~x["valid_coord"]).sum()
            })
        ).reset_index()
        district_coverage["coverage_pct"] = (
            district_coverage["valid_coords"] / district_coverage["total"] * 100
        ).round(2)
        district_coverage = district_coverage.sort_values("coverage_pct")
        results["by_district"] = district_coverage

        # Statistical test: Is coordinate coverage independent of district?
        contingency = pd.crosstab(
            df[district_col],
            df["valid_coord"].replace({True: "Valid", False: "Invalid"})
        )
        # Filter to districts with sufficient data
        contingency = contingency[contingency.sum(axis=1) >= 5]
        if contingency.shape[0] > 1 and contingency.shape[1] > 1:
            chi_result = chi_square_test(contingency)
            results["coverage_bias_district"] = {
                "test": "Chi-square test of independence",
                "hypothesis": "Coordinate coverage is independent of district",
                "statistic": chi_result["statistic"],
                "p_value": chi_result["p_value"],
                "dof": chi_result["dof"],
                "is_significant": chi_result["p_value"] < STAT_CONFIG["alpha"],
                "interpretation": (
                    "Coordinate coverage IS related to district (biased coverage)"
                    if chi_result["p_value"] < STAT_CONFIG["alpha"]
                    else "Coordinate coverage is independent of district"
                )
            }

    # Coverage by year (temporal bias check)
    if "dispatch_date" in df.columns:
        df_temp = df.copy()
        # Handle categorical/period dtypes
        dates_series = df_temp["dispatch_date"]
        if pd.api.types.is_categorical_dtype(dates_series) or hasattr(dates_series, 'dtype') and str(dates_series.dtype).startswith('period'):
            dates_series = dates_series.astype(str)
        df_temp["year"] = pd.to_datetime(dates_series, errors="coerce").dt.year

        year_coverage = df_temp.groupby("year").apply(
            lambda x: pd.Series({
                "total": len(x),
                "valid_coords": x["valid_coord"].sum(),
                "invalid_coords": (~x["valid_coord"]).sum()
            })
        ).reset_index()
        year_coverage["coverage_pct"] = (
            year_coverage["valid_coords"] / year_coverage["total"] * 100
        ).round(2)
        results["by_year"] = year_coverage

    return results


def detect_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect duplicate records in the dataset.

    Performs multiple types of duplicate detection:
    - Exact duplicate detection (all columns identical)
    - Near-duplicate detection (same coordinates + time)
    - Duplicate key detection (objectid, dc_key)

    Args:
        df: DataFrame with crime incident data

    Returns:
        Dictionary containing duplicate detection results
    """
    results = {}

    # 1. Exact duplicates (all columns)
    exact_dupes = df.duplicated().sum()
    exact_dupe_pct = (exact_dupes / len(df) * 100)
    results["exact_duplicates"] = {
        "count": int(exact_dupes),
        "percentage": round(exact_dupe_pct, 2)
    }

    if exact_dupes > 0:
        # Get examples of duplicates
        dupes = df[df.duplicated(keep=False)].sort_values(list(df.columns))
        results["examples"] = dupes.head(10).to_dict("records")

    # 2. Duplicate key columns
    for key_col in ["objectid", "dc_key", "incident_id"]:
        if key_col in df.columns:
            key_dupes = df[key_col].duplicated().sum()
            results[f"duplicate_{key_col}"] = {
                "count": int(key_dupes),
                "percentage": round((key_dupes / len(df) * 100), 2)
            }

    # 3. Near-duplicates (same coordinates within time window)
    if "point_x" in df.columns and "point_y" in df.columns and "dispatch_date" in df.columns:
        # Filter to valid coordinates
        valid_df = df[df["point_x"].notna() & df["point_y"].notna()].copy()

        if len(valid_df) > 0:
            # Create rounded coordinate grid for near-duplicate detection
            # Using 4 decimal places (~11m precision)
            valid_df["coord_round"] = (
                valid_df["point_x"].round(4).astype(str) + "_" +
                valid_df["point_y"].round(4).astype(str)
            )

            # Count incidents per coordinate
            coord_counts = valid_df["coord_round"].value_counts()
            multi_incident_coords = coord_counts[coord_counts > 1]

            results["near_duplicates"] = {
                "unique_coordinates_with_multiple_incidents": len(multi_incident_coords),
                "total_incidents_in_multi_locations": multi_incident_coords.sum(),
                "percentage": round((multi_incident_coords.sum() / len(valid_df) * 100), 2)
            }

            # Sample of locations with multiple incidents
            if len(multi_incident_coords) > 0:
                sample_coords = multi_incident_coords.head(5)
                sample_details = []
                for coord, count in sample_coords.items():
                    lon, lat = coord.split("_")
                    incidents = valid_df[valid_df["coord_round"] == coord]

                    # Handle date_range with proper type conversion
                    date_range = None
                    if "dispatch_date" in incidents.columns:
                        try:
                            dates = incidents["dispatch_date"]
                            if pd.api.types.is_categorical_dtype(dates) or hasattr(dates, 'dtype') and dates.dtype.name.startswith('period'):
                                dates = dates.astype(str)
                            date_range = (dates.min(), dates.max())
                        except Exception:
                            date_range = None

                    details = {
                        "point_x": float(lon),
                        "point_y": float(lat),
                        "incident_count": int(count),
                        "date_range": date_range
                    }
                    sample_details.append(details)
                results["near_duplicate_examples"] = sample_details

    # 4. Potential duplicate reporting patterns (same date+district+type)
    if all(col in df.columns for col in ["dispatch_date", "text_general_code"]):
        district_col = None
        for col in ["dc_dist", "police_districts", "district"]:
            if col in df.columns:
                district_col = col
                break

        if district_col:
            # Group by date, district, and crime type to find potential over-reporting
            grouping_key = ["dispatch_date", district_col, "text_general_code"]
            grouped = df.groupby(grouping_key).size()
            multi_reports = grouped[grouped > 1]

            results["potential_multiple_reports"] = {
                "count": len(multi_reports),
                "total_incidents": multi_reports.sum(),
                "percentage": round((multi_reports.sum() / len(df) * 100), 2) if len(df) > 0 else 0
            }

    return results


def detect_outliers(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect outliers in numerical and coordinate data.

    Performs outlier detection using:
    - IQR method for numerical columns
    - Coordinate outliers (outside Philadelphia bbox)
    - Temporal outliers (gaps in dates)

    Args:
        df: DataFrame with crime incident data

    Returns:
        Dictionary containing outlier detection results
    """
    results = {}

    # 1. Coordinate outliers (already done in validate_coordinates, summarize here)
    if "valid_coord" in df.columns:
        coord_outliers = (~df["valid_coord"]).sum()
        results["coordinate_outliers"] = {
            "count": int(coord_outliers),
            "percentage": round((coord_outliers / len(df) * 100), 2)
        }

        if "coord_issue" in df.columns:
            issue_breakdown = df[df["coord_issue"].notna()]["coord_issue"].value_counts()
            results["coordinate_outlier_breakdown"] = issue_breakdown.to_dict()

    # 2. Numerical column outliers using IQR method
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    outlier_summary = []
    for col in numerical_cols:
        if col == "dc_dist":
            continue  # Skip categorical-coded columns

        values = df[col].dropna()
        if len(values) < 4:
            continue

        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1

        if IQR > 0:
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = ((values < lower_bound) | (values > upper_bound)).sum()

            outlier_summary.append({
                "column": col,
                "q1": float(Q1),
                "q3": float(Q3),
                "iqr": float(IQR),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_count": int(outliers),
                "outlier_percentage": round((outliers / len(values) * 100), 2)
            })

    results["numerical_outliers"] = pd.DataFrame(outlier_summary)

    # 3. Temporal outliers (dates outside expected range)
    if "dispatch_date" in df.columns:
        # Handle categorical/period dtypes
        dates_series = df["dispatch_date"]
        if pd.api.types.is_categorical_dtype(dates_series) or hasattr(dates_series, 'dtype') and str(dates_series.dtype).startswith('period'):
            dates_series = dates_series.astype(str)
        dates = pd.to_datetime(dates_series, errors="coerce")
        valid_dates = dates.dropna()

        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()

            # Check for dates before 2006 or after current year
            future_dates = (valid_dates > pd.Timestamp.now()).sum()
            pre_2006 = (valid_dates < pd.Timestamp("2006-01-01")).sum()

            results["temporal_outliers"] = {
                "date_range": (min_date.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d")),
                "future_dates": int(future_dates),
                "pre_2006_dates": int(pre_2006),
                "total_temporal_outliers": int(future_dates + pre_2006)
            }

    return results


def temporal_gaps_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze temporal gaps in the data.

    Identifies:
    - Dates with zero incidents
    - Longest gap without data
    - Daily count distribution
    - Missing months/years

    Args:
        df: DataFrame with dispatch_date column

    Returns:
        Dictionary containing temporal gap analysis
    """
    results = {}

    if "dispatch_date" not in df.columns:
        results["error"] = "dispatch_date column not found"
        return results

    # Convert to datetime (handle categorical/period dtypes)
    df_temp = df.copy()
    dates_series = df_temp["dispatch_date"]
    if pd.api.types.is_categorical_dtype(dates_series) or hasattr(dates_series, 'dtype') and str(dates_series.dtype).startswith('period'):
        dates_series = dates_series.astype(str)
    df_temp["dispatch_date"] = pd.to_datetime(dates_series, errors="coerce")

    # Drop null dates
    valid_dates = df_temp["dispatch_date"].dropna()

    if len(valid_dates) == 0:
        results["error"] = "No valid dates found"
        return results

    # Daily counts
    daily_counts = df_temp.groupby(df_temp["dispatch_date"].dt.date).size()

    # Date range
    min_date = valid_dates.min()
    max_date = valid_dates.max()
    full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")

    # Find dates with no incidents
    # Convert to set of date objects for comparison
    all_dates = set(full_date_range.to_pydatetime().tolist())
    all_dates = set(d.date() for d in all_dates)
    observed_dates = set(daily_counts.index.to_list())
    missing_dates = sorted(list(all_dates - observed_dates))

    results["date_range"] = {
        "start": min_date.strftime("%Y-%m-%d"),
        "end": max_date.strftime("%Y-%m-%d"),
        "total_days": len(full_date_range),
        "days_with_incidents": len(observed_dates),
        "days_without_incidents": len(missing_dates)
    }

    # Longest gap
    if len(missing_dates) > 0:
        missing_dates_sorted = sorted(missing_dates)
        gaps = []
        current_gap = [missing_dates_sorted[0]]

        for i in range(1, len(missing_dates_sorted)):
            # Calculate days difference
            delta = (missing_dates_sorted[i] - missing_dates_sorted[i-1]).days if hasattr(missing_dates_sorted[i] - missing_dates_sorted[i-1], 'days') else 1
            if delta == 1:
                current_gap.append(missing_dates_sorted[i])
            else:
                gaps.append(current_gap)
                current_gap = [missing_dates_sorted[i]]
        gaps.append(current_gap)

        longest_gap = max(gaps, key=len)
        # Convert date objects to string
        start_date = longest_gap[0]
        end_date = longest_gap[-1]
        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
        else:
            start_str = str(start_date)
            end_str = str(end_date)

        results["longest_gap"] = {
            "start": start_str,
            "end": end_str,
            "days": len(longest_gap)
        }

        # Sample of missing dates
        missing_sample = []
        for d in missing_dates[:20]:
            if hasattr(d, 'strftime'):
                missing_sample.append(d.strftime("%Y-%m-%d"))
            else:
                missing_sample.append(str(d))
        results["missing_dates_sample"] = missing_sample

    # Daily count statistics
    results["daily_counts"] = {
        "mean": float(daily_counts.mean()),
        "median": float(daily_counts.median()),
        "min": int(daily_counts.min()),
        "max": int(daily_counts.max()),
        "std": float(daily_counts.std())
    }

    # Check for missing months
    df_temp["year_month"] = df_temp["dispatch_date"].dt.to_period("M")
    expected_months = pd.period_range(start=min_date, end=max_date, freq="M")
    actual_months = df_temp["year_month"].unique()
    missing_months = sorted(list(set(expected_months) - set(actual_months)))

    results["missing_months"] = {
        "count": len(missing_months),
        "list": [str(p) for p in missing_months[:10]]
    }

    return results


def calculate_quality_scores(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate overall and component quality scores for the dataset.

    Quality dimensions:
    - Completeness: Proportion of missing data
    - Accuracy: Coordinate validity
    - Consistency: Duplicate records
    - Validity: Values within expected ranges

    Args:
        df: DataFrame with crime incident data

    Returns:
        Dictionary containing quality scores
    """
    results = {}
    total = len(df)

    # 1. Completeness Score (based on missing data)
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isnull().sum().sum()
    completeness = (1 - missing_cells / total_cells) * 100

    results["completeness"] = {
        "score": round(completeness, 2),
        "missing_cells": int(missing_cells),
        "total_cells": total_cells,
        "weight": 0.40  # 40% weight in overall score
    }

    # 2. Accuracy Score (based on coordinate validity)
    if "valid_coord" in df.columns:
        valid_coords = df["valid_coord"].sum()
        accuracy = (valid_coords / total * 100)
    elif "point_x" in df.columns and "point_y" in df.columns:
        valid_coords = df["point_x"].notna().sum() & df["point_y"].notna().sum()
        accuracy = (valid_coords / total * 100)
    else:
        accuracy = 100  # Can't assess, give full score

    results["accuracy"] = {
        "score": round(accuracy, 2),
        "valid_records": int(valid_coords) if "valid_coord" in df.columns else int(valid_coords),
        "total_records": total,
        "weight": 0.30  # 30% weight in overall score
    }

    # 3. Consistency Score (based on duplicates)
    exact_dupes = df.duplicated().sum()
    consistency = (1 - exact_dupes / total) * 100

    results["consistency"] = {
        "score": round(consistency, 2),
        "duplicate_count": int(exact_dupes),
        "percentage": round((exact_dupes / total * 100), 2),
        "weight": 0.15  # 15% weight in overall score
    }

    # 4. Validity Score (based on value ranges - coordinate outliers)
    if "valid_coord" in df.columns:
        invalid_coords = (~df["valid_coord"]).sum()
        validity = (1 - invalid_coords / total) * 100
    else:
        validity = 100  # Can't assess

    results["validity"] = {
        "score": round(validity, 2),
        "invalid_count": int(invalid_coords) if "valid_coord" in df.columns else 0,
        "weight": 0.15  # 15% weight in overall score
    }

    # Calculate weighted overall score
    weights = {
        "completeness": results["completeness"]["weight"],
        "accuracy": results["accuracy"]["weight"],
        "consistency": results["consistency"]["weight"],
        "validity": results["validity"]["weight"]
    }

    overall_score = (
        results["completeness"]["score"] * weights["completeness"] +
        results["accuracy"]["score"] * weights["accuracy"] +
        results["consistency"]["score"] * weights["consistency"] +
        results["validity"]["score"] * weights["validity"]
    )

    results["overall"] = {
        "score": round(overall_score, 2),
        "grade": _quality_grade(overall_score)
    }

    # Bootstrap confidence interval for overall score
    # Sample records and recompute scores
    try:
        bootstrap_scores = []
        n_bootstrap = min(1000, STAT_CONFIG["bootstrap_n_resamples"])

        for _ in range(n_bootstrap):
            sample_idx = np.random.choice(len(df), size=min(10000, len(df)), replace=False)
            sample_df = df.iloc[sample_idx]

            # Quick score estimation
            completeness = (1 - sample_df.isnull().sum().sum() / (len(sample_df) * len(sample_df.columns))) * 100

            if "valid_coord" in sample_df.columns:
                accuracy = (sample_df["valid_coord"].sum() / len(sample_df) * 100)
            else:
                accuracy = 100

            consistency = (1 - sample_df.duplicated().sum() / len(sample_df)) * 100

            score = (
                completeness * weights["completeness"] +
                accuracy * weights["accuracy"] +
                consistency * weights["consistency"] +
                100 * weights["validity"]
            )
            bootstrap_scores.append(score)

        ci_lower = np.percentile(bootstrap_scores, (1 - STAT_CONFIG["confidence_level"]) * 100 / 2)
        ci_upper = np.percentile(bootstrap_scores, 100 - (1 - STAT_CONFIG["confidence_level"]) * 100 / 2)

        results["overall"]["ci_lower"] = round(ci_lower, 2)
        results["overall"]["ci_upper"] = round(ci_upper, 2)
        results["overall"]["confidence_level"] = STAT_CONFIG["confidence_level"]
    except Exception:
        # Bootstrap failed, skip CI
        pass

    return results


def _quality_grade(score: float) -> str:
    """Convert quality score to letter grade."""
    if score >= 95:
        return "A (Excellent)"
    elif score >= 85:
        return "B (Good)"
    elif score >= 70:
        return "C (Fair)"
    elif score >= 60:
        return "D (Poor)"
    else:
        return "F (Very Poor)"


def generate_data_quality_audit() -> Dict[str, Any]:
    """
    Generate a comprehensive data quality audit report.

    This is the main entry point for data quality auditing. It:
    1. Loads and validates the data
    2. Runs all quality analyses (missing, coverage, duplicates, outliers, gaps)
    3. Calculates quality scores
    4. Generates a markdown report with visualizations
    5. Saves the report to reports/01_data_quality_audit.md

    Returns:
        Dictionary containing all analysis results and report path
    """
    # Set seed for reproducibility
    seed = set_global_seed()
    print(f"Random seed set to: {seed}")

    # Load data with version tracking
    print("Loading data...")
    data_version = DataVersion(CRIME_DATA_PATH)
    print(f"Data version: {data_version}")

    df = load_data(clean=False)
    print(f"Loaded {len(df):,} records with {len(df.columns)} columns")

    # Validate coordinates and extract temporal features
    df = validate_coordinates(df)
    df = extract_temporal_features(df)

    # Run all analyses
    print("\n" + "="*50)
    print("Running comprehensive data quality audit...")
    print("="*50)

    results = {
        "data_version": data_version.to_dict(),
        "seed": seed,
    }

    # 1. Missing Data Analysis
    print("\n[1/7] Analyzing missing data patterns...")
    results["missing_data"] = analyze_missing_patterns(df)

    # 2. Coordinate Coverage
    print("[2/7] Analyzing coordinate coverage...")
    results["coordinate_coverage"] = coordinate_coverage_analysis(df)

    # 3. Duplicate Detection
    print("[3/7] Detecting duplicates...")
    results["duplicates"] = detect_duplicates(df)

    # 4. Outlier Detection
    print("[4/7] Detecting outliers...")
    results["outliers"] = detect_outliers(df)

    # 5. Temporal Gaps
    print("[5/7] Analyzing temporal gaps...")
    results["temporal_gaps"] = temporal_gaps_analysis(df)

    # 6. Quality Scores
    print("[6/7] Calculating quality scores...")
    results["quality_scores"] = calculate_quality_scores(df)

    # 7. Generate report
    print("[7/7] Generating audit report...")
    report_content = _generate_audit_markdown(results, df)

    # Save report
    report_path = PROJECT_ROOT / "reports" / "01_data_quality_audit.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report_content)

    results["report_path"] = str(report_path)
    results["quality_score"] = results["quality_scores"]["overall"]["score"]

    print(f"\n{'='*50}")
    print(f"Audit complete!")
    print(f"Overall Quality Score: {results['quality_scores']['overall']['score']}/100 ({results['quality_scores']['overall']['grade']})")
    print(f"Report saved to: {report_path}")
    print(f"{'='*50}")

    return results


def _generate_audit_markdown(results: Dict[str, Any], df: pd.DataFrame) -> str:
    """Generate the markdown content for the audit report."""
    md = []

    # Title
    md.append("# Data Quality Audit")
    md.append("")
    md.append("*Philadelphia Crime Incidents Dataset - Comprehensive Quality Assessment*")
    md.append("")

    # Analysis Configuration
    metadata = get_analysis_metadata(
        data_version=None,  # We'll add this separately
        seed=results.get("seed"),
        analyses=[
            "missing_patterns",
            "coordinate_coverage",
            "duplicate_detection",
            "outlier_detection",
            "temporal_gaps",
            "quality_scoring"
        ]
    )
    metadata["data_version"] = results["data_version"]

    # Add STAT_CONFIG to metadata
    metadata["parameters"]["alpha"] = STAT_CONFIG["alpha"]
    metadata["parameters"]["confidence_level"] = STAT_CONFIG["confidence_level"]
    metadata["parameters"]["fdr_method"] = STAT_CONFIG["fdr_method"]

    md.append(format_metadata_markdown(metadata))
    md.append("")

    # Executive Summary
    md.append("## Executive Summary")
    md.append("")
    qs = results["quality_scores"]["overall"]
    md.append(f"**Overall Quality Score:** {qs['score']}/100 ({qs['grade']})")

    if "ci_lower" in qs:
        cl = qs["confidence_level"]
        md.append(f"**{int(cl*100)}% Confidence Interval:** [{qs['ci_lower']}, {qs['ci_upper']}]")

    md.append("")

    # Component scores
    md.append("**Component Scores:**")
    md.append("")
    md.append("| Dimension | Score | Weight |")
    md.append("|-----------|-------|--------|")
    for dim in ["completeness", "accuracy", "consistency", "validity"]:
        dim_data = results["quality_scores"][dim]
        md.append(f"| {dim.title()} | {dim_data['score']}% | {dim_data['weight']*100:.0f}% |")
    md.append("")

    # Quick stats
    md.append("**Dataset Overview:**")
    md.append("")
    dv = results["data_version"]
    md.append(f"- **Total Records:** {dv['row_count']:,}")
    md.append(f"- **Total Columns:** {dv['column_count']}")
    md.append(f"- **Date Range:** {dv['date_range'][0]} to {dv['date_range'][1] if dv.get('date_range') else 'N/A'}")
    md.append("")

    # Missing Data Analysis
    md.append("## Missing Data Analysis")
    md.append("")

    # By column
    missing_col = results["missing_data"]["by_column"]
    md.append("### Missing Data by Column")
    md.append("")
    md.append("| Column | Missing Count | Missing % | Data Type |")
    md.append("|--------|---------------|-----------|-----------|")
    for _, row in missing_col.head(15).iterrows():
        md.append(f"| {row['column']} | {format_number(int(row['missing_count']))} | {row['missing_pct']}% | {row['dtype']} |")
    md.append("")

    # Missing data bias tests
    if "missingness_bias_crime_type" in results["missing_data"]:
        bias = results["missing_data"]["missingness_bias_crime_type"]
        md.append("**Statistical Test: Missingness by Crime Type**")
        md.append("")
        md.append(f"- **Test:** {bias['test']}")
        md.append(f"- **Hypothesis:** {bias['hypothesis']}")
        md.append(f"- **Chi-square:** {bias['statistic']:,.2f}")
        md.append(f"- **P-value:** {bias['p_value']:.2e}")
        md.append(f"- **Result:** {bias['interpretation']}")
        md.append("")

    if "missingness_bias_district" in results["missing_data"]:
        bias = results["missing_data"]["missingness_bias_district"]
        md.append("**Statistical Test: Missingness by District**")
        md.append("")
        md.append(f"- **Test:** {bias['test']}")
        md.append(f"- **Hypothesis:** {bias['hypothesis']}")
        md.append(f"- **Chi-square:** {bias['statistic']:,.2f}")
        md.append(f"- **P-value:** {bias['p_value']:.2e}")
        md.append(f"- **Result:** {bias['interpretation']}")
        md.append("")

    # Missing by crime type
    if "by_crime_type" in results["missing_data"]:
        md.append("### Missing Coordinates by Crime Type")
        md.append("")
        crime_missing = results["missing_data"]["by_crime_type"].sort_values("coords_missing_pct", ascending=False).head(15)
        md.append("| Crime Type | Total | Missing Coords | Missing % |")
        md.append("|------------|-------|----------------|-----------|")
        for _, row in crime_missing.iterrows():
            md.append(f"| {row['text_general_code']} | {format_number(int(row['total']))} | {format_number(int(row['missing_coords']))} | {row['coords_missing_pct']}% |")
        md.append("")

    # Missing by district
    if "by_district" in results["missing_data"]:
        md.append("### Missing Coordinates by District")
        md.append("")
        dist_missing = results["missing_data"]["by_district"].sort_values("coords_missing_pct", ascending=False).head(15)
        md.append("| District | Total | Missing Coords | Missing % |")
        md.append("|----------|-------|----------------|-----------|")
        for _, row in dist_missing.iterrows():
            district_val = row.get("dc_dist", row.get(list(results["missing_data"]["by_district"].columns)[0]))
            md.append(f"| {district_val} | {format_number(int(row['total']))} | {format_number(int(row['missing_coords']))} | {row['coords_missing_pct']}% |")
        md.append("")

    # Missing data visualization
    md.append("### Missing Data Pattern Visualization")
    md.append("")
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    sample_df = df.sample(n=min(10000, len(df)), random_state=42)
    missing_sample = sample_df.isnull().astype(int)
    sns.heatmap(missing_sample, cbar=True, cmap="YlOrRd", ax=ax)
    ax.set_title("Missing Data Pattern Heatmap (Sample of 10,000 records)")
    ax.set_xlabel("Columns")
    ax.set_ylabel("Records (Sample)")
    plt.tight_layout()
    md.append(create_image_tag(image_to_base64(fig)))
    plt.close(fig)
    md.append("")

    # Coordinate Coverage
    md.append("## Coordinate Coverage Analysis")
    md.append("")

    # Overall
    cov_overall = results["coordinate_coverage"]["overall"]
    md.append("### Overall Coverage")
    md.append("")
    md.append("| Metric | Count | Percentage |")
    md.append("|--------|-------|------------|")
    md.append(f"| Total Records | {format_number(cov_overall['total_records'])} | 100% |")
    md.append(f"| Valid Coordinates | {format_number(cov_overall['valid_count'])} | {cov_overall['valid_pct']}% |")
    md.append(f"| Invalid Coordinates | {format_number(cov_overall['invalid_count'])} | {cov_overall['invalid_pct']}% |")
    md.append("")

    # Coverage bias tests
    if "coverage_bias_crime_type" in results["coordinate_coverage"]:
        bias = results["coordinate_coverage"]["coverage_bias_crime_type"]
        md.append("**Statistical Test: Coverage by Crime Type**")
        md.append("")
        md.append(f"- **Test:** {bias['test']}")
        md.append(f"- **Hypothesis:** {bias['hypothesis']}")
        md.append(f"- **Chi-square:** {bias['statistic']:,.2f}")
        md.append(f"- **P-value:** {bias['p_value']:.2e}")
        md.append(f"- **Result:** {bias['interpretation']}")
        md.append("")

    if "coverage_bias_district" in results["coordinate_coverage"]:
        bias = results["coordinate_coverage"]["coverage_bias_district"]
        md.append("**Statistical Test: Coverage by District**")
        md.append("")
        md.append(f"- **Test:** {bias['test']}")
        md.append(f"- **Hypothesis:** {bias['hypothesis']}")
        md.append(f"- **Chi-square:** {bias['statistic']:,.2f}")
        md.append(f"- **P-value:** {bias['p_value']:.2e}")
        md.append(f"- **Result:** {bias['interpretation']}")
        md.append("")

    # Coverage by crime type
    if "by_crime_type" in results["coordinate_coverage"]:
        md.append("### Coordinate Coverage by Crime Type")
        md.append("")
        crime_cov = results["coordinate_coverage"]["by_crime_type"].head(15)
        md.append("| Crime Type | Total | Valid | Coverage % |")
        md.append("|------------|-------|-------|------------|")
        for _, row in crime_cov.iterrows():
            md.append(f"| {row['text_general_code']} | {format_number(int(row['total']))} | {format_number(int(row['valid_coords']))} | {row['coverage_pct']}% |")
        md.append("")

    # Coverage by district
    if "by_district" in results["coordinate_coverage"]:
        md.append("### Coordinate Coverage by District")
        md.append("")
        dist_col = list(results["coordinate_coverage"]["by_district"].columns)[0]
        dist_cov = results["coordinate_coverage"]["by_district"].head(15)
        md.append("| District | Total | Valid | Coverage % |")
        md.append("|----------|-------|-------|------------|")
        for _, row in dist_cov.iterrows():
            md.append(f"| {row[dist_col]} | {format_number(int(row['total']))} | {format_number(int(row['valid_coords']))} | {row['coverage_pct']}% |")
        md.append("")

    # Coverage visualization
    md.append("### Coordinate Coverage by District")
    md.append("")
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    if "by_district" in results["coordinate_coverage"]:
        dist_cov = results["coordinate_coverage"]["by_district"].sort_values("coverage_pct")
        districts = [str(int(d)) for d in dist_cov[dist_col].head(25)]
        coverages = dist_cov["coverage_pct"].head(25).values

        colors_list = [COLORS["success"] if c >= 75 else COLORS["warning"] if c >= 50 else COLORS["danger"] for c in coverages]
        bars = ax.barh(districts, coverages, color=colors_list)
        ax.set_xlabel("Coverage Percentage")
        ax.set_title("Coordinate Coverage by District")
        ax.axvline(x=75, color=COLORS["success"], linestyle="--", alpha=0.5, label="75% threshold")
        ax.legend()

        for bar, cov in zip(bars, coverages):
            ax.text(cov + 1, bar.get_y() + bar.get_height()/2, f"{cov:.0f}%", va="center", fontsize=8)

    plt.tight_layout()
    md.append(create_image_tag(image_to_base64(fig)))
    plt.close(fig)
    md.append("")

    # Duplicates
    md.append("## Duplicate Detection")
    md.append("")

    dup = results["duplicates"]["exact_duplicates"]
    md.append("### Exact Duplicates")
    md.append("")
    md.append(f"- **Duplicate Records:** {format_number(dup['count'])}")
    md.append(f"- **Percentage:** {dup['percentage']}%")
    md.append("")

    if "duplicate_objectid" in results["duplicates"]:
        obj_dup = results["duplicates"]["duplicate_objectid"]
        md.append(f"- **Duplicate objectid:** {format_number(obj_dup['count'])} ({obj_dup['percentage']}%)")

    if "near_duplicates" in results["duplicates"]:
        near = results["duplicates"]["near_duplicates"]
        md.append("")
        md.append("### Near-Duplicates (Same Location, Multiple Incidents)")
        md.append("")
        md.append(f"- **Unique locations with multiple incidents:** {format_number(near['unique_coordinates_with_multiple_incidents'])}")
        md.append(f"- **Total incidents at multi-incident locations:** {format_number(near['total_incidents_in_multi_locations'])}")
        md.append(f"- **Percentage:** {near['percentage']}%")
        md.append("")

    # Outliers
    md.append("## Outlier Detection")
    md.append("")

    if "coordinate_outliers" in results["outliers"]:
        coord_out = results["outliers"]["coordinate_outliers"]
        md.append("### Coordinate Outliers")
        md.append("")
        md.append(f"- **Invalid Coordinates:** {format_number(coord_out['count'])} ({coord_out['percentage']}%)")
        md.append("")

        if "coordinate_outlier_breakdown" in results["outliers"]:
            md.append("**Issue Breakdown:**")
            for issue, count in results["outliers"]["coordinate_outlier_breakdown"].items():
                md.append(f"- {issue}: {format_number(count)}")
            md.append("")

    if "temporal_outliers" in results["outliers"]:
        temp_out = results["outliers"]["temporal_outliers"]
        md.append("### Temporal Outliers")
        md.append("")
        md.append(f"- **Date Range:** {temp_out['date_range'][0]} to {temp_out['date_range'][1]}")
        md.append(f"- **Future dates:** {temp_out['future_dates']}")
        md.append(f"- **Pre-2006 dates:** {temp_out['pre_2006_dates']}")
        md.append("")

    # Temporal Gaps
    md.append("## Temporal Gaps Analysis")
    md.append("")

    if "date_range" in results["temporal_gaps"]:
        gaps = results["temporal_gaps"]
        md.append("### Date Coverage")
        md.append("")
        md.append(f"- **Date Range:** {gaps['date_range']['start']} to {gaps['date_range']['end']}")
        md.append(f"- **Total Days:** {gaps['date_range']['total_days']}")
        md.append(f"- **Days with Incidents:** {gaps['date_range']['days_with_incidents']}")
        md.append(f"- **Days without Incidents:** {gaps['date_range']['days_without_incidents']}")
        md.append("")

        if "longest_gap" in gaps:
            lg = gaps["longest_gap"]
            md.append("### Longest Gap Without Data")
            md.append("")
            md.append(f"- **Start:** {lg['start']}")
            md.append(f"- **End:** {lg['end']}")
            md.append(f"- **Duration:** {lg['days']} days")
            md.append("")

        if "missing_months" in gaps:
            mm = gaps["missing_months"]
            md.append("### Missing Months")
            md.append("")
            md.append(f"- **Count:** {mm['count']}")
            if mm["list"]:
                md.append(f"- **Examples:** {', '.join(mm['list'][:5])}")
            md.append("")

    # Daily count visualization
    md.append("### Daily Incident Count Distribution")
    md.append("")
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    if "dispatch_date" in df.columns:
        df_temp = df.copy()
        # Handle categorical/period dtypes
        dates_series = df_temp["dispatch_date"]
        if pd.api.types.is_categorical_dtype(dates_series) or hasattr(dates_series, 'dtype') and str(dates_series.dtype).startswith('period'):
            dates_series = dates_series.astype(str)
        df_temp["dispatch_date"] = pd.to_datetime(dates_series, errors="coerce")
        daily_counts = df_temp.groupby(df_temp["dispatch_date"].dt.date).size()

        ax.plot(daily_counts.index, daily_counts.values, color=COLORS["primary"], alpha=0.7, linewidth=0.5)
        ax.set_xlabel("Date")
        ax.set_ylabel("Incident Count")
        ax.set_title("Daily Incident Count (2006-2026)")

        # Add rolling average
        rolling = daily_counts.rolling(window=30, center=True).mean()
        ax.plot(rolling.index, rolling.values, color=COLORS["danger"], linewidth=2, label="30-day rolling average")
        ax.legend()

    plt.tight_layout()
    md.append(create_image_tag(image_to_base64(fig)))
    plt.close(fig)
    md.append("")

    # Quality Score Visualization
    md.append("## Quality Score Summary")
    md.append("")

    # Radar chart for component scores
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"], subplot_kw=dict(projection='polar'))

    categories = ["Completeness", "Accuracy", "Consistency", "Validity"]
    values = [
        results["quality_scores"]["completeness"]["score"],
        results["quality_scores"]["accuracy"]["score"],
        results["quality_scores"]["consistency"]["score"],
        results["quality_scores"]["validity"]["score"],
    ]

    # Close the plot
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    ax.plot(angles, values, 'o-', linewidth=2, color=COLORS["primary"])
    ax.fill(angles, values, alpha=0.25, color=COLORS["primary"])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.set_title(f"Data Quality Dimensions (Overall: {results['quality_scores']['overall']['score']}/100)")
    ax.grid(True)

    plt.tight_layout()
    md.append(create_image_tag(image_to_base64(fig)))
    plt.close(fig)
    md.append("")

    # Analysis Limitations & Recommendations
    md.append("## Analysis Limitations & Recommendations")
    md.append("")

    coverage = results["coordinate_coverage"]["overall"]["valid_pct"]

    md.append("### Recommendations for Analysis")
    md.append("")

    if coverage < 75:
        md.append("**WARNING:** Coordinate coverage is below 75%. Spatial analyses should be interpreted with caution.")
        md.append("")
        md.append("Recommended actions:")
        md.append("- Exclude spatial analyses that require precise coordinates")
        md.append("- Use district-level aggregations where possible")
        md.append("- Consider multiple imputation for missing coordinates (with caution)")
        md.append("- Clearly document coordinate missingness in all spatial reports")
        md.append("")

    if results["duplicates"]["exact_duplicates"]["percentage"] > 1:
        md.append("**NOTE:** Duplicate records detected. Consider deduplication before analysis.")
        md.append("")

    # Safe analyses
    md.append("### Analyses Considered Safe")
    md.append("")
    md.append("- Temporal trend analysis (minimal impact from missing coordinates)")
    md.append("- Categorical analysis by crime type (complete data)")
    md.append("- District-level aggregations (using district column, not coordinates)")
    md.append("")

    # Analyses requiring caution
    md.append("### Analyses Requiring Caution")
    md.append("")
    if coverage < 90:
        md.append("- Point-level spatial analysis (hotspot detection, clustering)")
        md.append("- Crime mapping at incident level")
        md.append("")
    if results["missing_data"]["by_column"]["missing_pct"].max() > 20:
        md.append("- Analyses involving columns with >20% missing data")
        md.append("")

    # Statistical validity
    md.append("### Statistical Validity")
    md.append("")
    md.append("All statistical tests use 99% confidence intervals for conservative inference. ")
    md.append("Missing data patterns have been tested for bias (chi-square tests of independence). ")
    md.append("")

    if "missingness_bias_crime_type" in results["missing_data"]:
        if results["missing_data"]["missingness_bias_crime_type"]["is_significant"]:
            md.append("**Finding:** Missing data is NOT independent of crime type. This indicates potential bias in coordinate reporting by crime type.")
            md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    # Check for command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--audit":
        # Run comprehensive audit
        results = generate_data_quality_audit()
    else:
        # Run legacy analysis
        results = analyze_data_quality()
        report = generate_markdown_report(results)

        # Save report
        report_path = PROJECT_ROOT / "reports" / "01_data_quality_report.md"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, "w") as f:
            f.write("# Data Quality Assessment Report\n\n")
            f.write(report)

        print(f"\nReport saved to: {report_path}")
