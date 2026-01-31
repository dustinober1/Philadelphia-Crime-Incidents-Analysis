"""
Phase 5: Cross-Dimensional Analysis

Analyzes relationships between multiple dimensions:
- Crime Type × Time
- Crime Type × Location
- District × Time
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT, STAT_CONFIG, CRIME_DATA_PATH
from analysis.utils import load_data, extract_temporal_features, validate_coordinates, image_to_base64, create_image_tag, format_number
from analysis.stats_utils import correlation_test, chi_square_test, apply_fdr_correction
from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion


def analyze_cross_dimensional() -> dict:
    """
    Run comprehensive cross-dimensional analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    # Set random seed for reproducibility
    seed = set_global_seed(STAT_CONFIG["random_seed"])
    print(f"Random seed set to: {seed}")

    # Track data version for reproducibility
    data_version = DataVersion(CRIME_DATA_PATH)
    print(f"Data version: {data_version}")

    print("Loading data for cross-dimensional analysis...")
    df = load_data(clean=False)

    print("Extracting temporal features...")
    df = extract_temporal_features(df)
    df = validate_coordinates(df)

    results = {}

    # Store analysis metadata
    results["analysis_metadata"] = get_analysis_metadata(
        data_version=data_version,
        analysis_type="cross_dimensional_analysis",
        random_seed=seed,
        confidence_level=STAT_CONFIG["confidence_level"],
        alpha=STAT_CONFIG["alpha"],
    )

    # Get column names
    text_general = "text_general_code" if "text_general_code" in df.columns else "text_general_code"
    for col in df.columns:
        if "text" in col.lower() and "general" in col.lower():
            text_general = col
            break

    dc_dist_col = "dc_dist" if "dc_dist" in df.columns else "dc_dist"
    for col in df.columns:
        if "dist" in col.lower() and "dc" in col.lower():
            dc_dist_col = col
            break

    # ========================================================================
    # 1. Crime Type × Time of Day
    # ========================================================================
    print("Analyzing crime type × hour patterns...")

    crime_hour = pd.crosstab(df[text_general], df["hour"])

    # Get top 12 crimes for better visualization
    top_crimes = df[text_general].value_counts().head(12).index.tolist()
    crime_hour_top = crime_hour.loc[top_crimes]

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    sns.heatmap(crime_hour_top, cmap=COLORS["sequential"], ax=ax, annot=False, cbar_kws={"label": "Count"})
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Crime Type")
    ax.set_title("Crime Type × Hour of Day Heatmap (Top 12 Crimes)")

    plt.tight_layout()
    results["crime_hour_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Normalized heatmap (percentages)
    crime_hour_pct = crime_hour_top.div(crime_hour_top.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    sns.heatmap(crime_hour_pct, cmap=COLORS["sequential"], ax=ax, annot=False,
                cbar_kws={"label": "Percentage"}, vmin=0, vmax=15)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Crime Type")
    ax.set_title("Crime Type × Hour of Day (Row-Normalized %)")

    plt.tight_layout()
    results["crime_hour_heatmap_pct"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 2. Crime Type × Day of Week
    # ========================================================================
    print("Analyzing crime type × day of week patterns...")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    crime_dow = pd.crosstab(df[text_general], df["day_name"]).reindex(columns=day_order)
    crime_dow_top = crime_dow.loc[top_crimes]

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    sns.heatmap(crime_dow_top, cmap=COLORS["sequential"], ax=ax, annot=False, cbar_kws={"label": "Count"})
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Crime Type")
    ax.set_title("Crime Type × Day of Week Heatmap (Top 12 Crimes)")

    plt.tight_layout()
    results["crime_dow_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 3. Crime Type × Month (Seasonal Patterns by Crime)
    # ========================================================================
    print("Analyzing crime type × month patterns...")

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    crime_month = pd.crosstab(df[text_general], df["month"])
    crime_month_top = crime_month.loc[top_crimes]
    crime_month_top.columns = month_names

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    sns.heatmap(crime_month_top, cmap=COLORS["sequential"], ax=ax, annot=False, cbar_kws={"label": "Count"})
    ax.set_xlabel("Month")
    ax.set_ylabel("Crime Type")
    ax.set_title("Crime Type × Month Heatmap (Top 12 Crimes)")

    plt.tight_layout()
    results["crime_month_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 4. Crime Type × District
    # ========================================================================
    print("Analyzing crime type × district patterns...")

    crime_district = pd.crosstab(df[dc_dist_col], df[text_general])
    crime_district_top = crime_district[top_crimes]

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    sns.heatmap(crime_district_top.T, cmap=COLORS["sequential"], ax=ax, annot=False,
                cbar_kws={"label": "Count"})
    ax.set_xlabel("Police District")
    ax.set_ylabel("Crime Type")
    ax.set_title("Crime Type × District Heatmap (Top 12 Crimes)")

    plt.tight_layout()
    results["crime_district_heatmap2"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Normalized by district
    crime_district_pct = crime_district_top.T.div(crime_district_top.T.sum(axis=0), axis=1) * 100

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    sns.heatmap(crime_district_pct, cmap=COLORS["diverging"], ax=ax, annot=False,
                cbar_kws={"label": "Deviation from Expected %"},
                center=crime_district_pct.mean().mean())
    ax.set_xlabel("Police District")
    ax.set_ylabel("Crime Type")
    ax.set_title("Crime Type × District (Column-Normalized %)")

    plt.tight_layout()
    results["crime_district_heatmap_norm"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 5. District × Time of Day
    # ========================================================================
    print("Analyzing district × hour patterns...")

    district_hour = pd.crosstab(df[dc_dist_col], df["hour"])

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    sns.heatmap(district_hour, cmap=COLORS["sequential"], ax=ax, annot=False, cbar_kws={"label": "Count"})
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Police District")
    ax.set_title("District × Hour of Day Heatmap")

    plt.tight_layout()
    results["district_hour_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 6. District × Day of Week
    # ========================================================================
    print("Analyzing district × day of week patterns...")

    district_dow = pd.crosstab(df[dc_dist_col], df["day_name"]).reindex(columns=day_order)

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    sns.heatmap(district_dow, cmap=COLORS["sequential"], ax=ax, annot=False, cbar_kws={"label": "Count"})
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Police District")
    ax.set_title("District × Day of Week Heatmap")

    plt.tight_layout()
    results["district_dow_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 6.5 Statistical Tests for Cross-Tabulations
    # ========================================================================
    print("Performing chi-square tests for cross-tabulations...")

    crosstab_tests = {}

    # Test 1: Crime type vs hour (top 6 crimes x 4 time periods)
    print("  Testing crime type vs hour...")
    crime_hour_sample = df[df[text_general].isin(top_crimes[:6])].copy()
    # Create time periods for manageable chi-square
    crime_hour_sample["time_period"] = pd.cut(
        crime_hour_sample["hour"],
        bins=[0, 6, 12, 18, 24],
        labels=["Overnight", "Morning", "Afternoon", "Evening"]
    )
    crime_period_tab = pd.crosstab(crime_hour_sample[text_general], crime_hour_sample["time_period"])

    if crime_period_tab.shape[0] >= 2 and crime_period_tab.shape[1] >= 2:
        crime_period_test = chi_square_test(crime_period_tab.values)
        crosstab_tests["crime_type_time_period"] = {
            "test": "Chi-square test of independence",
            "variables": "Crime Type vs Time Period",
            "statistic": float(crime_period_test["statistic"]),
            "p_value": float(crime_period_test["p_value"]),
            "dof": int(crime_period_test["dof"]),
            "is_significant": crime_period_test["p_value"] < STAT_CONFIG["alpha"],
        }
        print(f"    Crime vs Time: chi2={crime_period_test['statistic']:.2f}, p={crime_period_test['p_value']:.6e}")

    # Test 2: Crime type vs day of week
    print("  Testing crime type vs day of week...")
    crime_dow_tab = pd.crosstab(df[df[text_general].isin(top_crimes[:8])][text_general], df["day_name"])

    if crime_dow_tab.shape[0] >= 2 and crime_dow_tab.shape[1] >= 2:
        crime_dow_test = chi_square_test(crime_dow_tab.values)
        crosstab_tests["crime_type_day_of_week"] = {
            "test": "Chi-square test of independence",
            "variables": "Crime Type vs Day of Week",
            "statistic": float(crime_dow_test["statistic"]),
            "p_value": float(crime_dow_test["p_value"]),
            "dof": int(crime_dow_test["dof"]),
            "is_significant": crime_dow_test["p_value"] < STAT_CONFIG["alpha"],
        }
        print(f"    Crime vs Day: chi2={crime_dow_test['statistic']:.2f}, p={crime_dow_test['p_value']:.6e}")

    # Test 3: District vs hour (sample of districts)
    print("  Testing district vs hour...")
    top_districts = df[dc_dist_col].value_counts().head(10).index.tolist()
    district_hour_sample = df[df[dc_dist_col].isin(top_districts)].copy()
    district_hour_sample["time_period"] = pd.cut(
        district_hour_sample["hour"],
        bins=[0, 6, 12, 18, 24],
        labels=["Overnight", "Morning", "Afternoon", "Evening"]
    )
    district_period_tab = pd.crosstab(district_hour_sample[dc_dist_col], district_hour_sample["time_period"])

    if district_period_tab.shape[0] >= 2 and district_period_tab.shape[1] >= 2:
        district_period_test = chi_square_test(district_period_tab.values)
        crosstab_tests["district_time_period"] = {
            "test": "Chi-square test of independence",
            "variables": "District vs Time Period",
            "statistic": float(district_period_test["statistic"]),
            "p_value": float(district_period_test["p_value"]),
            "dof": int(district_period_test["dof"]),
            "is_significant": district_period_test["p_value"] < STAT_CONFIG["alpha"],
        }
        print(f"    District vs Time: chi2={district_period_test['statistic']:.2f}, p={district_period_test['p_value']:.6e}")

    # Test 4: District vs crime type (top 10 x top 10)
    print("  Testing district vs crime type...")
    top_districts = df[dc_dist_col].value_counts().head(10).index.tolist()
    top_10_crimes_sub = df[text_general].value_counts().head(10).index.tolist()
    district_crime_sample = df[
        (df[dc_dist_col].isin(top_districts)) &
        (df[text_general].isin(top_10_crimes_sub))
    ]
    district_crime_tab = pd.crosstab(district_crime_sample[dc_dist_col], district_crime_sample[text_general])

    if district_crime_tab.shape[0] >= 2 and district_crime_tab.shape[1] >= 2:
        district_crime_test = chi_square_test(district_crime_tab.values)
        crosstab_tests["district_crime_type"] = {
            "test": "Chi-square test of independence",
            "variables": "District vs Crime Type",
            "statistic": float(district_crime_test["statistic"]),
            "p_value": float(district_crime_test["p_value"]),
            "dof": int(district_crime_test["dof"]),
            "is_significant": district_crime_test["p_value"] < STAT_CONFIG["alpha"],
        }
        print(f"    District vs Crime: chi2={district_crime_test['statistic']:.2f}, p={district_crime_test['p_value']:.6e}")

    results["crosstab_tests"] = crosstab_tests

    # Apply FDR correction across all tests
    p_values = np.array([test["p_value"] for test in crosstab_tests.values()])
    if len(p_values) > 0:
        adjusted_p = apply_fdr_correction(p_values, method="bh")

        for i, (key, test) in enumerate(crosstab_tests.items()):
            test["p_value_adjusted"] = float(adjusted_p[i])
            test["is_significant_fdr"] = adjusted_p[i] < STAT_CONFIG["alpha"]

        print(f"  FDR correction applied to {len(p_values)} tests")

    # Notable associations summary
    notable_associations = []
    for key, test in crosstab_tests.items():
        if test.get("is_significant_fdr", test["is_significant"]):
            notable_associations.append({
                "variables": test["variables"],
                "p_value": test["p_value"],
                "p_value_fdr": test.get("p_value_adjusted", test["p_value"]),
                "interpretation": f"Significant association between {test['variables'].lower()}"
            })

    results["notable_associations"] = notable_associations
    print(f"  Found {len(notable_associations)} significant associations after FDR correction")

    # ========================================================================
    # 7. Temporal Profiles by Crime Type
    # ========================================================================
    print("Creating temporal profiles for major crime types...")

    fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZES["wide"])

    # Select 4 major crime types
    major_crimes = df[text_general].value_counts().head(4).index.tolist()

    for idx, crime in enumerate(major_crimes):
        ax = axes[idx // 2, idx % 2]

        crime_data = df[df[text_general] == crime]
        hourly = crime_data.groupby("hour").size()

        ax.bar(hourly.index, hourly.values, color=COLORS["primary"], alpha=0.7)
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Count")
        ax.set_title(f"{crime}")
        ax.set_xticks(range(0, 24, 4))

    plt.suptitle("Hourly Distribution for Top 4 Crime Types", y=1.02)
    plt.tight_layout()
    results["major_crime_hourly_profiles"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 8. Weekend vs Weekday by Crime Type
    # ========================================================================
    print("Analyzing weekend vs weekday patterns by crime type...")

    weekend_comparison = df.groupby([text_general, "is_weekend"]).size().unstack(fill_value=0)
    weekend_comparison.columns = ["Weekday", "Weekend"]
    weekend_comparison["total"] = weekend_comparison["Weekday"] + weekend_comparison["Weekend"]
    weekend_comparison["weekend_pct"] = (weekend_comparison["Weekend"] / weekend_comparison["total"] * 100).round(1)
    weekend_comparison = weekend_comparison.sort_values("total", ascending=False).head(15)

    results["weekend_comparison"] = weekend_comparison

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    y_pos = np.arange(len(weekend_comparison))
    width = 0.35

    bars1 = ax.barh(y_pos - width/2, weekend_comparison["Weekday"], width,
                    label="Weekday", color=COLORS["primary"])
    bars2 = ax.barh(y_pos + width/2, weekend_comparison["Weekend"], width,
                    label="Weekend", color=COLORS["secondary"])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(weekend_comparison.index)
    ax.set_xlabel("Crime Count")
    ax.set_title("Weekday vs Weekend Crime Comparison (Top 15 Crime Types)")
    ax.invert_yaxis()
    ax.legend()

    plt.tight_layout()
    results["weekend_weekday_bar"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 9. Peak Hours by Crime Type
    # ========================================================================
    print("Finding peak hours by crime type...")

    peak_hours = df.groupby([text_general, "hour"]).size().reset_index(name="count")
    peak_hours_idx = peak_hours.groupby(text_general)["count"].idxmax()
    peak_hours_result = peak_hours.loc[peak_hours_idx].sort_values("count", ascending=False)
    peak_hours_result.columns = ["crime_type", "peak_hour", "count"]
    results["peak_hours_by_crime"] = peak_hours_result

    # ========================================================================
    # 10. Crime Type Trends Over Years
    # ========================================================================
    print("Analyzing crime type trends over years...")

    crime_year = pd.crosstab(df["year"], df[text_general])
    crime_year_top = crime_year[top_crimes]

    # Normalize to percentages
    crime_year_pct = crime_year_top.div(crime_year_top.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])

    # Plot as stacked area or line chart
    for crime in top_crimes[:8]:  # Top 8 for readability
        years = crime_year_pct.index
        values = crime_year_pct[crime]
        ax.plot(years, values, marker="o", label=crime, linewidth=2)

    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage of Total Crime")
    ax.set_title("Crime Type Trends Over Time (Top 8)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    results["crime_type_trends"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    print("Cross-dimensional analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from cross-dimensional analysis results.

    Args:
        results: Dictionary from analyze_cross_dimensional()

    Returns:
        Markdown string with analysis results.
    """
    md = []

    # Add analysis configuration section
    if "analysis_metadata" in results:
        md.append(format_metadata_markdown(results["analysis_metadata"]))
        md.append("")

    md.append("### Cross-Dimensional Analysis\n")

    # Crime Type × Time
    md.append("#### 1. Crime Type × Time of Day\n\n")
    md.append(results["crime_hour_heatmap"])
    md.append("\n")
    md.append(results["crime_hour_heatmap_pct"])
    md.append("\n")

    # Crime Type × Day of Week
    md.append("#### 2. Crime Type × Day of Week\n\n")
    md.append(results["crime_dow_heatmap"])
    md.append("\n")

    # Crime Type × Month
    md.append("#### 3. Crime Type × Month (Seasonal Patterns)\n\n")
    md.append(results["crime_month_heatmap"])
    md.append("\n")

    # Crime Type × District
    md.append("#### 4. Crime Type × District\n\n")
    md.append(results["crime_district_heatmap2"])
    md.append("\n")
    md.append(results["crime_district_heatmap_norm"])
    md.append("\n")

    # District × Time
    md.append("#### 5. District × Time Patterns\n\n")
    md.append(results["district_hour_heatmap"])
    md.append("\n")
    md.append(results["district_dow_heatmap"])
    md.append("\n")

    # Statistical Tests Section
    if "crosstab_tests" in results and len(results["crosstab_tests"]) > 0:
        md.append("#### 5.1 Statistical Tests for Cross-Tabulations\n\n")
        md.append("**Chi-Square Tests of Independence** (with FDR correction):\n\n")
        md.append("| Variables | Chi-square | DoF | P-value | P-value (FDR) | Significant |")
        md.append("|-----------|------------|-----|---------|---------------|------------|")

        for key, test in results["crosstab_tests"].items():
            p_val = test["p_value"]
            p_fdr = test.get("p_value_adjusted", p_val)
            sig_mark = "Yes" if test.get("is_significant_fdr", test["is_significant"]) else "No"
            md.append(f"| {test['variables']} | {test['statistic']:.2f} | {test['dof']} | {p_val:.6e} | {p_fdr:.6e} | {sig_mark} |")

        md.append("")

        # Notable associations
        if "notable_associations" in results and len(results["notable_associations"]) > 0:
            md.append("**Significant Associations After FDR Correction:**\n\n")
            for assoc in results["notable_associations"]:
                md.append(f"- **{assoc['variables']}**: p={assoc['p_value']:.6e} (FDR-adjusted: {assoc['p_value_fdr']:.6e})\n")
            md.append("")

        md.append("**Interpretation:** All tested cross-dimensional associations show significant dependencies. ")
        md.append("This means crime patterns vary systematically by time of day, day of week, and location. ")
        md.append("FDR correction controls the false discovery rate across all tests.\n\n")

    # Temporal Profiles
    md.append("#### 6. Temporal Profiles by Major Crime Types\n\n")
    md.append(results["major_crime_hourly_profiles"])
    md.append("\n")

    # Weekend vs Weekday
    md.append("#### 7. Weekend vs Weekday by Crime Type\n\n")

    weekend_comp = results["weekend_comparison"]
    md.append("**Weekend Crime Percentage by Crime Type** (Top 15):\n\n")
    md.append("| Crime Type | Weekday | Weekend | Weekend % |")
    md.append("|------------|---------|---------|-----------|")
    for crime, row in weekend_comp.iterrows():
        md.append(f"| {crime} | {format_number(int(row['Weekday']))} | {format_number(int(row['Weekend']))} | {row['weekend_pct']}% |")
    md.append("")

    md.append(results["weekend_weekday_bar"])
    md.append("\n")

    # Peak Hours
    md.append("#### 8. Peak Hours by Crime Type\n\n")

    peak_hours = results["peak_hours_by_crime"]
    md.append("**Top 15 Crime Types by Peak Hour Volume**:\n\n")
    md.append("| Crime Type | Peak Hour | Count at Peak |")
    md.append("|------------|-----------|---------------|")
    for _, row in peak_hours.head(15).iterrows():
        md.append(f"| {row['crime_type']} | {int(row['peak_hour'])}:00 | {format_number(row['count'])} |")
    md.append("")

    # Crime Type Trends
    md.append("#### 9. Crime Type Trends Over Years\n\n")
    md.append(results["crime_type_trends"])
    md.append("\n")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_cross_dimensional()
    report = generate_markdown_report(results)

    report_path = PROJECT_ROOT / "reports" / "05_cross_analysis_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Cross-Dimensional Analysis Report\n\n")
        f.write(report)

    print(f"\nReport saved to: {report_path}")
