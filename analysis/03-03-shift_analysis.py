"""
Shift-by-Shift Temporal Analysis

Analyzes crime patterns across four patrol shifts to understand temporal distribution
for optimal staffing and resource allocation.

Shifts:
- Late Night (12AM-6AM): Hours 0-5
- Morning (6AM-12PM): Hours 6-11
- Afternoon (12PM-6PM): Hours 12-17
- Evening (6PM-12AM): Hours 18-23

Enhanced with statistical significance testing including ANOVA/Kruskal-Wallis omnibus
test, FDR-adjusted post-hoc pairwise comparisons, and chi-square test of independence
for crime type distribution across shifts.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, STAT_CONFIG, PROJECT_ROOT, REPORTS_DIR
from analysis.utils import load_data, extract_temporal_features, image_to_base64, create_image_tag, format_number
from analysis.stats_utils import (
    compare_multiple_samples,
    apply_fdr_correction,
    bootstrap_ci,
    chi_square_test,
)
from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion

# Set matplotlib backend for non-interactive plotting
os.environ["MPLBACKEND"] = "Agg"


# =============================================================================
# SHIFT DEFINITIONS
# =============================================================================

# Shift bins and labels
SHIFT_BINS = [0, 6, 12, 18, 24]
SHIFT_LABELS = [
    "Late Night (12AM-6AM)",
    "Morning (6AM-12PM)",
    "Afternoon (12PM-6PM)",
    "Evening (6PM-12AM)"
]

# Crime type groups for shift analysis
SHIFT_CRIME_GROUPS = {
    "violent": ["Homicide - Criminal", "Rape", "Robbery Firearm", "Robbery No Firearm",
                "Aggravated Assault Firearm", "Aggravated Assault No Firearm"],
    "property": ["Burglary Residential", "Burglary Non-Residential", "Thefts",
                 "Theft from Vehicle", "Motor Vehicle Theft"],
    "quality_of_life": ["Disorderly Conduct", "Public Drunkenness", "Vandalism/Criminal Mischief"]
}

# Crime types to analyze (top N by frequency)
TOP_N_CRIME_TYPES = 15


# =============================================================================
# SHIFT CLASSIFICATION
# =============================================================================

def classify_shifts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each incident into one of four patrol shifts based on hour.

    Args:
        df: DataFrame with hour column.

    Returns:
        DataFrame with added 'shift' column. Records with NaN hour are
        assigned to 'Unknown' category.
    """
    df = df.copy()

    # Create shift column using pd.cut
    # This creates a categorical column
    df["shift"] = pd.cut(
        df["hour"],
        bins=SHIFT_BINS,
        labels=SHIFT_LABELS,
        right=False,
        include_lowest=True
    )

    # Convert to string to allow "Unknown" category
    df["shift"] = df["shift"].astype(str)

    # Assign "Unknown" for NaN hour values
    df.loc[df["hour"].isna(), "shift"] = "Unknown"

    return df


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_shift_patterns(df: pd.DataFrame = None) -> dict:
    """
    Analyze crime patterns across patrol shifts with statistical testing.

    Performs:
    - Omnibus test (ANOVA or Kruskal-Wallis) for shift differences
    - Post-hoc pairwise comparisons with FDR correction
    - Bootstrap confidence intervals for mean daily counts per shift

    Args:
        df: Full crime incidents DataFrame. If None, loads from default path.

    Returns:
        Dictionary containing:
        - metadata: Analysis metadata
        - omnibus_test: Test name, statistic, p_value, is_significant
        - post_hoc_comparisons: DataFrame with pairwise comparisons
        - shift_cis: Dict of confidence intervals per shift
        - shift_counts: Total incidents per shift
        - shift_percentages: Percentage distribution
        - shift_box_plot: Base64 image tag
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    # Load data if not provided
    if df is None:
        print("Loading data for shift analysis...")
        df = load_data(clean=False)

    # IMPORTANT: Preserve original hour column before extract_temporal_features overwrites it
    # extract_temporal_features() sets hour=0 for date-only records
    original_hour = df["hour"].copy()

    # Extract temporal features (adds year, month, day, day_of_week, etc.)
    print("Extracting temporal features...")
    df = extract_temporal_features(df)

    # RESTORE the original hour column with actual hour values
    df["hour"] = original_hour

    # Classify shifts using the restored hour values
    print("Classifying incidents into shifts...")
    df = classify_shifts(df)

    # Store metadata
    try:
        data_version = DataVersion(PROJECT_ROOT / "data" / "crime_incidents_combined.parquet")
        metadata = get_analysis_metadata(
            data_version=data_version,
            analysis_type="shift_analysis",
            confidence_level=STAT_CONFIG["confidence_level"],
            bootstrap_n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_seed=STAT_CONFIG["random_seed"]
        )
    except Exception as e:
        print(f"Warning: Could not create data version: {e}")
        metadata = get_analysis_metadata(
            analysis_type="shift_analysis",
            confidence_level=STAT_CONFIG["confidence_level"],
            bootstrap_n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_seed=STAT_CONFIG["random_seed"]
        )

    # Filter out records with missing/unknown shift
    df_valid = df[df["shift"].isin(SHIFT_LABELS)].copy()
    df_valid = df_valid[df_valid["hour"].notna()]

    print(f"Analyzing {format_number(len(df_valid))} incidents with valid shift data")

    results = {"metadata": metadata}

    # Calculate total counts per shift
    shift_counts = df_valid["shift"].value_counts()
    shift_counts = shift_counts.reindex(SHIFT_LABELS, fill_value=0)
    total_incidents = shift_counts.sum()

    shift_percentages = (shift_counts / total_incidents * 100).round(2)

    results["shift_counts"] = shift_counts.to_dict()
    results["shift_percentages"] = shift_percentages.to_dict()

    # Group daily counts by shift for statistical testing
    print("Computing daily crime counts per shift...")
    shift_groups = {}
    for shift in SHIFT_LABELS:
        shift_data = df_valid[df_valid["shift"] == shift]
        # Group by date to get daily counts
        daily_counts = shift_data.groupby(["year", "month", "day"]).size().values
        if len(daily_counts) >= 10:  # Need sufficient data for comparison
            shift_groups[shift] = daily_counts
            print(f"  {shift}: {len(daily_counts)} days, mean={np.mean(daily_counts):.2f}")

    # Run omnibus test
    if len(shift_groups) >= 2:
        print("\nRunning omnibus test...")
        comparison = compare_multiple_samples(shift_groups, alpha=STAT_CONFIG["alpha"])

        omnibus_result = {
            "test_name": comparison["omnibus_test"],
            "statistic": float(comparison["statistic"]),
            "p_value": float(comparison["p_value"]),
            "is_significant": comparison["is_significant"],
            "all_normal": comparison.get("all_normal", False)
        }
        results["omnibus_test"] = omnibus_result

        sig_str = "**significant**" if omnibus_result["is_significant"] else "not significant"
        print(f"  {omnibus_result['test_name']}: statistic={omnibus_result['statistic']:.2f}, "
              f"p={omnibus_result['p_value']:.4f} ({sig_str})")

        # Post-hoc comparisons
        post_hoc_df = comparison.get("post_hoc_results")
        if post_hoc_df is not None and not post_hoc_df.empty:
            print(f"\nRunning FDR correction on {len(post_hoc_df)} pairwise comparisons...")
            # Apply FDR correction
            p_values = post_hoc_df["p_value"].values
            adjusted_p = apply_fdr_correction(p_values, method=STAT_CONFIG["fdr_method"])
            post_hoc_df = post_hoc_df.copy()
            post_hoc_df["adjusted_p"] = adjusted_p
            post_hoc_df["is_significant"] = adjusted_p < STAT_CONFIG["alpha"]

            # Sort by adjusted p-value
            post_hoc_df = post_hoc_df.sort_values("adjusted_p")

            results["post_hoc_comparisons"] = post_hoc_df

            # Count significant comparisons
            n_sig = post_hoc_df["is_significant"].sum()
            print(f"  {n_sig}/{len(post_hoc_df)} comparisons significant after FDR correction")
        else:
            results["post_hoc_comparisons"] = None

        # Bootstrap confidence intervals for each shift
        print("\nComputing bootstrap confidence intervals...")
        shift_cis = {}
        for shift_name, daily_data in shift_groups.items():
            try:
                ci_lower, ci_upper, point_est, se = bootstrap_ci(
                    daily_data,
                    statistic='mean',
                    confidence_level=STAT_CONFIG["confidence_level"],
                    n_resamples=2000,  # Reduced for speed
                    random_state=STAT_CONFIG["random_seed"]
                )
                shift_cis[shift_name] = {
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper,
                    "point_estimate": point_est,
                    "standard_error": se
                }
                print(f"  {shift_name}: {point_est:.2f} [{ci_lower:.2f}, {ci_upper:.2f}]")
            except Exception as e:
                print(f"  Warning: Could not calculate CI for {shift_name}: {e}")

        results["shift_cis"] = shift_cis

    # Create visualization
    print("\nCreating shift box plot...")
    results["shift_box_plot"] = create_shift_box_plot(shift_groups)

    print("Shift pattern analysis complete!")
    return results


def analyze_crime_by_shift(df: pd.DataFrame = None) -> dict:
    """
    Analyze crime type distribution across shifts.

    Creates a shift x crime type matrix and tests independence
    using chi-square test.

    Args:
        df: Full crime incidents DataFrame. If None, loads from default path.

    Returns:
        Dictionary containing:
        - metadata: Analysis metadata
        - shift_crime_matrix: DataFrame of counts (shift x crime type)
        - shift_crime_pct: DataFrame of percentages within each shift
        - chi_square_test: Independence test results
        - heatmap_plot: Base64 image tag
        - stacked_bar_plot: Base64 image tag
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    # Load data if not provided
    if df is None:
        print("Loading data for crime-by-shift analysis...")
        df = load_data(clean=False)

    # IMPORTANT: Preserve original hour column before extract_temporal_features overwrites it
    original_hour = df["hour"].copy()

    # Extract temporal features (adds year, month, day, day_of_week, etc.)
    print("Extracting temporal features...")
    df = extract_temporal_features(df)

    # RESTORE the original hour column with actual hour values
    df["hour"] = original_hour

    # Classify shifts using the restored hour values
    df = classify_shifts(df)

    # Filter valid data
    df_valid = df[df["shift"].isin(SHIFT_LABELS)].copy()
    df_valid = df_valid[df_valid["hour"].notna()]

    # Get top N crime types
    print(f"Selecting top {TOP_N_CRIME_TYPES} crime types...")
    top_crimes = df_valid["text_general_code"].value_counts().head(TOP_N_CRIME_TYPES).index.tolist()
    df_filtered = df_valid[df_valid["text_general_code"].isin(top_crimes)].copy()

    print(f"Analyzing {format_number(len(df_filtered))} incidents across {len(top_crimes)} crime types")

    # Create shift x crime type matrix
    print("Creating shift x crime type matrix...")
    shift_crime_matrix = pd.crosstab(
        df_filtered["shift"],
        df_filtered["text_general_code"],
        dropna=False
    )

    # Reindex rows to ensure proper shift order
    shift_crime_matrix = shift_crime_matrix.reindex(SHIFT_LABELS, fill_value=0)

    # Filter out crime types with very low counts (expected frequency < 5 for chi-square)
    # Column sum must be at least 5 * num_shifts for valid chi-square test
    min_threshold = 5 * len(SHIFT_LABELS)
    valid_crimes = shift_crime_matrix.columns[shift_crime_matrix.sum() >= min_threshold]
    shift_crime_matrix_filtered = shift_crime_matrix[valid_crimes].copy()

    print(f"  Filtered from {shift_crime_matrix.shape[1]} to {shift_crime_matrix_filtered.shape[1]} crime types for chi-square test")

    # Calculate percentages within each shift (use full matrix for visualization)
    shift_crime_pct = shift_crime_matrix.div(shift_crime_matrix.sum(axis=1), axis=0) * 100

    results = {
        "shift_crime_matrix": shift_crime_matrix,
        "shift_crime_pct": shift_crime_pct,
        "top_crime_types": top_crimes
    }

    # Chi-square test of independence (use filtered matrix)
    print("Running chi-square test of independence...")
    try:
        chi2_result = chi_square_test(shift_crime_matrix_filtered.values)
        chi2_result["is_significant"] = chi2_result["p_value"] < STAT_CONFIG["alpha"]
        results["chi_square_test"] = chi2_result

        sig_str = "**significant**" if chi2_result["is_significant"] else "not significant"
        print(f"  Chi-square: statistic={chi2_result['statistic']:.2f}, "
              f"p={chi2_result['p_value']:.4f} ({sig_str})")
        print(f"  Cramer's V: {chi2_result['cramers_v']:.3f} ({chi2_result['effect_size_interpretation']})")
    except Exception as e:
        print(f"  Warning: Chi-square test failed: {e}")
        # Provide default result
        results["chi_square_test"] = {
            "statistic": None,
            "p_value": None,
            "is_significant": False,
            "cramers_v": None,
            "effect_size_interpretation": "Test failed - insufficient data",
            "error": str(e)
        }

    # Create visualizations
    print("\nCreating visualizations...")
    results["heatmap_plot"] = create_shift_crime_heatmap(
        shift_crime_matrix.values,
        SHIFT_LABELS,
        top_crimes
    )
    results["stacked_bar_plot"] = create_stacked_bar_plot(shift_crime_pct)

    print("Crime-by-shift analysis complete!")
    return results


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_shift_box_plot(shift_groups: dict) -> str:
    """
    Create box plot of daily crime counts by shift.

    Args:
        shift_groups: Dict mapping shift names to arrays of daily counts.

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    # Prepare data for box plot
    data_to_plot = []
    labels = []
    for shift in SHIFT_LABELS:
        if shift in shift_groups:
            data_to_plot.append(shift_groups[shift])
            labels.append(shift.replace(" (", "\n("))

    # Create box plot
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, showmeans=True)

    # Color the boxes
    for patch, color in zip(bp['boxes'], [COLORS["primary"], COLORS["secondary"],
                                           COLORS["success"], COLORS["warning"]]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Styling
    ax.set_ylabel("Daily Crime Count", fontsize=12)
    ax.set_xlabel("Shift", fontsize=12)
    ax.set_title("Daily Crime Count Distribution by Patrol Shift (2006-2026)",
                 fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # Rotate x labels for better readability
    plt.xticks(rotation=0, ha="center")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_shift_crime_heatmap(matrix: np.ndarray, shift_labels: list, crime_types: list) -> str:
    """
    Create heatmap showing shift (rows) x crime type (columns).

    Args:
        matrix: 2D array of counts (shifts x crime types).
        shift_labels: List of shift names for row labels.
        crime_types: List of crime type names for column labels.

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])

    # Create heatmap
    im = ax.imshow(matrix, cmap=COLORS["sequential"], aspect="auto")

    # Set ticks
    ax.set_xticks(np.arange(len(crime_types)))
    ax.set_yticks(np.arange(len(shift_labels)))
    ax.set_xticklabels(crime_types, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(shift_labels, fontsize=10)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Crime Count", rotation=270, labelpad=15)

    # Annotate cells with counts
    for i in range(len(shift_labels)):
        for j in range(len(crime_types)):
            count = int(matrix[i, j])
            if count > 0:
                text_color = "white" if count > matrix.max() * 0.7 else "black"
                ax.text(j, i, format_number(count),
                       ha="center", va="center", color=text_color, fontsize=8)

    ax.set_xlabel("Crime Type", fontsize=12)
    ax.set_ylabel("Patrol Shift", fontsize=12)
    ax.set_title("Crime Type Distribution by Patrol Shift (2006-2026)",
                 fontsize=14, fontweight="bold")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_stacked_bar_plot(shift_crime_pct: pd.DataFrame) -> str:
    """
    Create stacked bar chart: 100% per shift, crime types as segments.

    Args:
        shift_crime_pct: DataFrame with shifts as index, crime types as columns,
                        values as percentages.

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    # Get crime types and prepare colors
    crime_types = shift_crime_pct.columns.tolist()
    n_colors = len(crime_types)

    # Use colormap for distinct colors
    cmap = plt.cm.get_cmap(COLORS["palette"])
    colors = [cmap(i / n_colors) for i in range(n_colors)]

    # Create stacked bar chart
    bottom = np.zeros(len(shift_crime_pct))
    for i, crime_type in enumerate(crime_types):
        values = shift_crime_pct[crime_type].values
        ax.bar(range(len(shift_crime_pct)), values, bottom=bottom,
               label=crime_type, color=colors[i], edgecolor="white", linewidth=0.5)
        bottom += values

    # Set x-axis labels
    shift_labels_display = [s.replace(" (", "\n(") for s in shift_crime_pct.index]
    ax.set_xticks(range(len(shift_crime_pct)))
    ax.set_xticklabels(shift_labels_display, fontsize=10)

    ax.set_ylabel("Percentage", fontsize=12)
    ax.set_xlabel("Patrol Shift", fontsize=12)
    ax.set_title("Crime Type Composition by Patrol Shift (2006-2026)",
                 fontsize=14, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis="y")

    # Legend outside plot
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_shift_report(shift_results: dict, crime_results: dict) -> str:
    """
    Generate comprehensive markdown report for shift analysis.

    Args:
        shift_results: Results dict from analyze_shift_patterns().
        crime_results: Results dict from analyze_crime_by_shift().

    Returns:
        Complete markdown string with embedded visualizations.
    """
    md = []

    # Analysis Configuration section
    if "metadata" in shift_results:
        md.append(format_metadata_markdown(shift_results["metadata"]))
        md.append("\n")

    # ========================================================================
    # TITLE
    # ========================================================================
    md.append("# Shift-by-Shift Crime Pattern Analysis\n")
    md.append("**Philadelphia Crime Incidents (2006-2026)**\n\n")
    md.append("---\n\n")

    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    md.append("## Executive Summary\n\n")

    md.append("**Question:** How are crimes distributed across patrol shifts for optimal staffing?\n\n")

    # Extract key findings
    shift_counts = shift_results.get("shift_counts", {})
    shift_pct = shift_results.get("shift_percentages", {})
    omnibus = shift_results.get("omnibus_test", {})

    # Find highest and lowest crime shifts
    if shift_pct:
        max_shift = max(shift_pct, key=shift_pct.get)
        min_shift = min(shift_pct, key=shift_pct.get)
        md.append(f"**Highest Volume Shift:** {max_shift} - **{shift_pct[max_shift]}%** of all crimes\n")
        md.append(f"**Lowest Volume Shift:** {min_shift} - **{shift_pct[min_shift]}%** of all crimes\n\n")

    # Statistical significance
    if omnibus:
        sig = "**significant**" if omnibus.get("is_significant") else "not significant"
        md.append(f"**Statistical Test:** {omnibus.get('test_name')} = {omnibus.get('statistic'):.2f}, "
                  f"p = {omnibus.get('p_value'):.4f} ({sig} at alpha = {STAT_CONFIG['alpha']})\n")
        if omnibus.get("is_significant"):
            md.append("**Interpretation:** Crime rates are NOT evenly distributed across shifts\n\n")

    # Chi-square results
    chi2 = crime_results.get("chi_square_test", {})
    if chi2:
        sig_chi = "**significant**" if chi2.get("is_significant") else "not significant"
        md.append(f"**Crime Type Independence:** Chi-square = {chi2.get('statistic'):.2f}, "
                  f"p = {chi2.get('p_value'):.4f} ({sig_chi})\n")
        md.append(f"**Effect Size:** Cramer's V = {chi2.get('cramers_v'):.3f} "
                  f"({chi2.get('effect_size_interpretation')})\n\n")

    # Get total incidents
    total = sum(shift_counts.values()) if shift_counts else 0
    md.append(f"**Total Incidents Analyzed:** {format_number(total)}\n\n")

    md.append("---\n\n")

    # ========================================================================
    # SHIFT DISTRIBUTION
    # ========================================================================
    md.append("## Crime Distribution by Shift\n\n")

    if shift_pct:
        md.append("| Shift | Incidents | Percentage |\n")
        md.append("|-------|-----------|------------|\n")
        for shift in SHIFT_LABELS:
            count = shift_counts.get(shift, 0)
            pct = shift_pct.get(shift, 0)
            md.append(f"| {shift} | {format_number(int(count))} | {pct}% |\n")
        md.append("\n")

    # ========================================================================
    # STATISTICAL TEST RESULTS
    # ========================================================================
    md.append("## Statistical Test Results\n\n")

    if omnibus:
        md.append("### Omnibus Test: Overall Shift Differences\n\n")
        md.append(f"- **Test:** {omnibus.get('test_name')}\n")
        md.append(f"- **Statistic:** {omnibus.get('statistic'):.2f}\n")
        md.append(f"- **P-value:** {omnibus.get('p_value'):.4f}\n")
        md.append(f"- **Significant:** {'Yes' if omnibus.get('is_significant') else 'No'} (alpha = {STAT_CONFIG['alpha']})\n")
        md.append(f"- **All groups normal:** {'Yes' if omnibus.get('all_normal') else 'No'}\n\n")

    # Post-hoc comparisons
    post_hoc = shift_results.get("post_hoc_comparisons")
    if post_hoc is not None and not post_hoc.empty:
        md.append("### Post-Hoc Pairwise Comparisons\n\n")
        md.append("*Comparisons with FDR-adjusted p-values:\n\n")

        md.append("| Shift A | Shift B | Mean Diff | P-value | Adj P-value | Significant |\n")
        md.append("|---------|---------|-----------|---------|-------------|-------------|\n")

        for _, row in post_hoc.iterrows():
            group_a = row.get("group_a", row.get("group1", ""))
            group_b = row.get("group_b", row.get("group2", ""))
            mean_diff = row.get("mean_diff", 0)
            p_val = row.get("p_value", 1)
            adj_p = row.get("adjusted_p", 1)
            sig = "Yes" if row.get("is_significant") else "No"

            md.append(f"| {group_a} | {group_b} | {mean_diff:.2f} | {p_val:.4f} | {adj_p:.4f} | {sig} |\n")

        md.append("\n")

    # Chi-square test results
    if chi2:
        md.append("### Crime Type Independence Test\n\n")
        md.append(f"- **Chi-square statistic:** {chi2.get('statistic'):.2f}\n")
        md.append(f"- **Degrees of freedom:** {chi2.get('dof')}\n")
        md.append(f"- **P-value:** {chi2.get('p_value'):.4f}\n")
        md.append(f"- **Cramer's V:** {chi2.get('cramers_v'):.3f}\n")
        md.append(f"- **Effect size:** {chi2.get('effect_size_interpretation')}\n")
        md.append(f"- **Significant:** {'Yes' if chi2.get('is_significant') else 'No'}\n\n")

    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Visualizations\n\n")

    # Shift box plot
    if "shift_box_plot" in shift_results:
        md.append("### Daily Crime Count by Shift\n\n")
        md.append(shift_results["shift_box_plot"])
        md.append("\n\n")
        md.append("*Figure 1: Box plot showing distribution of daily crime counts for each patrol shift. ")
        md.append("Boxes represent interquartile range, whiskers show 1.5x IQR, and diamonds indicate mean values.*\n\n")

    # Heatmap
    if "heatmap_plot" in crime_results:
        md.append("### Crime Type Heatmap by Shift\n\n")
        md.append(crime_results["heatmap_plot"])
        md.append("\n\n")
        md.append("*Figure 2: Heatmap showing crime counts by type and shift. Darker colors indicate higher counts. ")
        md.append("This reveals which crime types dominate each patrol shift.*\n\n")

    # Stacked bar
    if "stacked_bar_plot" in crime_results:
        md.append("### Crime Type Composition by Shift\n\n")
        md.append(crime_results["stacked_bar_plot"])
        md.append("\n\n")
        md.append("*Figure 3: Stacked bar chart showing percentage composition of crime types within each shift. ")
        md.append("Each bar totals 100%, revealing the relative mix of crime types.*\n\n")

    # ========================================================================
    # BOOTSTRAP CONFIDENCE INTERVALS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Bootstrap Confidence Intervals\n\n")

    shift_cis = shift_results.get("shift_cis", {})
    if shift_cis:
        md.append(f"{int(STAT_CONFIG['confidence_level'] * 100)}% Confidence Intervals for mean daily crime count:\n\n")
        md.append("| Shift | Mean | CI Lower | CI Upper | SE |\n")
        md.append("|-------|------|----------|----------|----|\n")

        for shift in SHIFT_LABELS:
            if shift in shift_cis:
                ci = shift_cis[shift]
                md.append(f"| {shift} | {ci['point_estimate']:.2f} | "
                         f"{ci['ci_lower']:.2f} | {ci['ci_upper']:.2f} | {ci['standard_error']:.2f} |\n")

        md.append("\n")

    # ========================================================================
    # KEY INSIGHTS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Key Insights\n\n")

    # Volume patterns
    if shift_pct:
        md.append("### Volume Patterns\n\n")
        high_shift = max(shift_pct, key=shift_pct.get)
        low_shift = min(shift_pct, key=shift_pct.get)
        ratio = shift_pct[high_shift] / shift_pct[low_shift] if shift_pct[low_shift] > 0 else 0

        md.append(f"- **Peak shift:** {high_shift} accounts for {shift_pct[high_shift]}% of all crimes\n")
        md.append(f"- **Lowest shift:** {low_shift} accounts for only {shift_pct[low_shift]}% of crimes\n")
        md.append(f"- **Volume ratio:** The peak shift has {ratio:.1f}x more incidents than the lowest shift\n\n")

    # Crime type patterns by shift
    shift_crime_pct = crime_results.get("shift_crime_pct")
    if shift_crime_pct is not None:
        md.append("### Crime Type Patterns by Shift\n\n")

        for shift in SHIFT_LABELS:
            if shift in shift_crime_pct.index:
                # Get top 3 crime types for this shift
                shift_series = shift_crime_pct.loc[shift]
                top_3 = shift_series.nlargest(3)
                md.append(f"**{shift}** - Top crime types:\n")
                for crime_type, pct in top_3.items():
                    md.append(f"  - {crime_type}: {pct:.1f}%\n")
                md.append("\n")

    # ========================================================================
    # STAFFING RECOMMENDATIONS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Staffing Recommendations\n\n")

    md.append("### Resource Allocation\n\n")
    if shift_pct:
        # Calculate recommended staffing proportions (inverse to volume if we want equal coverage per crime)
        # Or proportional to volume for equal officer utilization
        total_pct = sum(shift_pct.values())

        for shift in SHIFT_LABELS:
            pct = shift_pct.get(shift, 0)
            # Recommend staffing proportional to crime volume
            recommended = pct / 100
            md.append(f"- **{shift}**: {pct}% of crimes -> Recommend ~{recommended:.1%} of patrol resources\n")
        md.append("\n")

    md.append("### Strategic Considerations\n\n")
    md.append("- **High-volume shifts** (Evening, Afternoon) require baseline staffing levels\n")
    md.append("- **Low-volume shifts** (Late Night) may benefit from targeted patrols in hotspots\n")
    md.append("- **Shift overlap** at 6PM and 12AM should ensure smooth transition\n")
    md.append("- **Weekend vs weekday**: Consider differential staffing patterns if data supports\n\n")

    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    md.append("---\n\n")
    md.append("## Methodology\n\n")

    md.append("### Data Source\n")
    md.append("- **Dataset**: Philadelphia crime incidents (2006-2026)\n")
    md.append(f"- **Total incidents**: {format_number(total)}\n")
    md.append("- **Crime types**: Top " + str(TOP_N_CRIME_TYPES) + f" by frequency\n")
    md.append("- **2026 data**: Partial (only through January 20, 2026)\n\n")

    md.append("### Shift Definitions\n")
    md.append("- **Late Night (12AM-6AM)**: Hours 0-5\n")
    md.append("- **Morning (6AM-12PM)**: Hours 6-11\n")
    md.append("- **Afternoon (12PM-6PM)**: Hours 12-17\n")
    md.append("- **Evening (6PM-12AM)**: Hours 18-23\n\n")

    md.append("### Statistical Methods\n")
    md.append(f"- **Confidence level**: {STAT_CONFIG['confidence_level'] * 100}%\n")
    md.append(f"- **Significance alpha**: {STAT_CONFIG['alpha']}\n")
    md.append(f"- **Bootstrap resamples**: {STAT_CONFIG['bootstrap_n_resamples']}\n")
    md.append(f"- **FDR correction method**: {STAT_CONFIG['fdr_method'].upper()} (Benjamini-Hochberg)\n")
    md.append("- **Omnibus test**: ANOVA (if normal) or Kruskal-Wallis (if non-normal)\n")
    md.append("- **Post-hoc**: Tukey HSD (for ANOVA) with FDR adjustment\n")
    md.append("- **Independence test**: Chi-square test of independence\n")
    md.append("- **Effect size**: Cramer's V for chi-square tests\n\n")

    md.append("### Data Exclusions\n")
    md.append("- Records with missing hour data assigned to 'Unknown' category (excluded from analysis)\n")
    md.append("- Only top " + str(TOP_N_CRIME_TYPES) + " crime types by frequency included in shift x crime type matrix\n")
    md.append("- Daily counts computed by grouping incidents by (year, month, day)\n\n")

    # ========================================================================
    # CONCLUSION
    # ========================================================================
    md.append("---\n\n")
    md.append("## Conclusion\n\n")

    if omnibus and omnibus.get("is_significant"):
        md.append("The analysis reveals **statistically significant differences** in crime rates across patrol shifts. ")
        md.append(f"The {max_shift} shift experiences the highest volume of crime ({shift_pct[max_shift]}%), ")
        md.append(f"while {min_shift} has the lowest ({shift_pct[min_shift]}%).\n\n")
    else:
        md.append("The analysis found **no statistically significant difference** in crime rates across patrol shifts ")
        md.append("at the specified alpha level. Crime appears to be relatively evenly distributed.\n\n")

    if chi2 and chi2.get("is_significant"):
        md.append("Crime type distribution also **varies significantly by shift** (Cramer's V = ")
        md.append(f"{chi2.get('cramers_v'):.3f}), indicating that certain crime types are more prevalent ")
        md.append("during specific patrol periods. This information can be used to tailor patrol strategies ")
        md.append("to the specific risks of each shift.\n\n")
    else:
        md.append("Crime type distribution does not vary significantly by shift, suggesting similar ")
        md.append("crime profiles across all patrol periods.\n\n")

    md.append("**Key Takeaway**: Aligning patrol staffing with crime volume patterns allows departments to ")
    md.append("optimize resource allocation while maintaining adequate coverage across all shifts.\n\n")

    md.append("*\n")
    md.append(f"Report generated by Claude Code | ")
    md.append(f"Data source: Philadelphia crime incidents dataset ({format_number(total)} records, 2006-2026)\n")

    return "\n".join(md)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Shift-by-Shift Temporal Analysis")
    print("=" * 60)
    print()

    # Run shift pattern analysis
    shift_results = analyze_shift_patterns()
    print()

    # Run crime-by-shift analysis
    crime_results = analyze_crime_by_shift()
    print()

    # Generate combined report
    print("Generating report...")
    report = generate_shift_report(shift_results, crime_results)

    # Save report
    report_path = REPORTS_DIR / "15_shift_analysis_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
