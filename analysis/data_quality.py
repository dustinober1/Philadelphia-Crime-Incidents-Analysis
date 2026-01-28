"""
Phase 1: Data Quality Assessment

Analyzes missing data, coordinate validation, and duplicates.
"""

import io
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT
from analysis.utils import load_data, validate_coordinates, extract_temporal_features, get_missing_summary, image_to_base64, create_image_tag, format_number


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


if __name__ == "__main__":
    results = analyze_data_quality()
    report = generate_markdown_report(results)

    # Save report
    report_path = PROJECT_ROOT / "reports" / "01_data_quality_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Data Quality Assessment Report\n\n")
        f.write(report)

    print(f"\nReport saved to: {report_path}")
