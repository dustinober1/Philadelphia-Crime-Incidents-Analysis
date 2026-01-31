"""
Holiday Effects Analysis

Analyzes crime patterns around major U.S. federal holidays to determine if
holiday periods exhibit significant differences in crime rates compared to
baseline periods.

This analysis helps inform resource allocation decisions by identifying
high-risk holiday periods for police departments.

Enhanced with statistical significance testing, effect sizes, and FDR
correction for multiple holiday comparisons.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT, REPORTS_DIR, STAT_CONFIG
from analysis.utils import (
    load_data, extract_temporal_features, image_to_base64,
    create_image_tag, format_number
)
from analysis.stats_utils import (
    chi_square_test, compare_two_samples, cohens_d,
    bootstrap_ci, apply_fdr_correction
)
from analysis.reproducibility import (
    set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion
)


# =============================================================================
# HOLIDAY CONSTANTS
# =============================================================================

# Holiday analysis window: days before and after holiday to include
HOLIDAY_WINDOW_DAYS = 3

# Baseline weeks: weeks before/after holiday period for comparison
BASELINE_WEEKS = 2

# Holiday period labels
HOLIDAY_PERIOD_LABELS = ["pre_holiday", "holiday", "post_holiday", "baseline"]
HOLIDAY_PERIOD_NAMES = {
    "pre_holiday": "Pre-Holiday (3 days before)",
    "holiday": "Holiday Day",
    "post_holiday": "Post-Holiday (3 days after)",
    "baseline": "Baseline (non-holiday)"
}


# =============================================================================
# HOLIDAY DETECTION
# =============================================================================

def get_us_holidays(year: int) -> List[Tuple[pd.Timestamp, str]]:
    """
    Get all U.S. federal holidays for a given year using workalendar.

    Uses workalendar.usa.UnitedStates to automatically calculate holidays,
    including moving holidays like Thanksgiving (4th Thursday) and
    Memorial Day (last Monday).

    Args:
        year: Year to get holidays for

    Returns:
        List of tuples: (holiday_date, holiday_name)

    Examples:
        >>> holidays = get_us_holidays(2024)
        >>> len(holidays) >= 10  # At least 10 federal holidays
        True
    """
    try:
        from workalendar.usa import UnitedStates
    except ImportError:
        raise ImportError(
            "workalendar is required for holiday detection. "
            "Install with: pip install workalendar"
        )

    cal = UnitedStates()
    holidays = cal.holidays(year)

    # workalendar 17.0+ returns a list of (date, name) tuples
    # Older versions returned a dict
    if isinstance(holidays, dict):
        holiday_list = [(pd.Timestamp(date), name) for date, name in holidays.items()]
    else:
        # New API returns list of tuples
        holiday_list = [(pd.Timestamp(date), name) for date, name in holidays]

    return holiday_list


def identify_holiday_periods(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify holiday periods in the dataset.

    Creates classification for each day as:
    - 'pre_holiday': 3 days before a holiday
    - 'holiday': The holiday day itself
    - 'post_holiday': 3 days after a holiday
    - 'baseline': All other days

    Also creates 'holiday_name' column for the specific holiday name.

    Args:
        df: DataFrame with dispatch_datetime column

    Returns:
        DataFrame with added columns: holiday_period, holiday_name

    Examples:
        >>> df = pd.DataFrame({'dispatch_datetime': pd.date_range('2024-01-01', periods=10)})
        >>> df = extract_temporal_features(df)
        >>> df = identify_holiday_periods(df)
        >>> 'holiday_period' in df.columns
        True
    """
    df = df.copy()

    # Initialize columns
    df["holiday_period"] = "baseline"
    df["holiday_name"] = None

    # Get unique years in the dataset
    if "year" not in df.columns:
        df = extract_temporal_features(df)

    years = df["year"].unique()

    # Iterate through each year and identify holidays
    for year in years:
        if year < 2006 or year > 2026:  # Skip years outside dataset range
            continue

        holidays = get_us_holidays(year)

        for holiday_date, holiday_name in holidays:
            # Define date ranges
            pre_start = holiday_date - pd.Timedelta(days=HOLIDAY_WINDOW_DAYS)
            post_end = holiday_date + pd.Timedelta(days=HOLIDAY_WINDOW_DAYS)

            # Mark pre-holiday period
            pre_mask = (df["dispatch_datetime"].dt.date >= pre_start.date()) & \
                       (df["dispatch_datetime"].dt.date < holiday_date.date())
            df.loc[pre_mask, "holiday_period"] = "pre_holiday"
            df.loc[pre_mask, "holiday_name"] = holiday_name

            # Mark holiday day
            holiday_mask = df["dispatch_datetime"].dt.date == holiday_date.date()
            df.loc[holiday_mask, "holiday_period"] = "holiday"
            df.loc[holiday_mask, "holiday_name"] = holiday_name

            # Mark post-holiday period
            post_mask = (df["dispatch_datetime"].dt.date > holiday_date.date()) & \
                        (df["dispatch_datetime"].dt.date <= post_end.date())
            df.loc[post_mask, "holiday_period"] = "post_holiday"
            df.loc[post_mask, "holiday_name"] = holiday_name

    # Categorical ordering for plots
    df["holiday_period"] = pd.Categorical(
        df["holiday_period"],
        categories=HOLIDAY_PERIOD_LABELS,
        ordered=True
    )

    return df


# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

def calculate_daily_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily crime counts for statistical analysis.

    Args:
        df: DataFrame with dispatch_datetime and holiday_period columns

    Returns:
        DataFrame with columns: date, year, month, day, holiday_period, crime_count
    """
    # Group by date and holiday period
    daily = df.groupby([
        df["dispatch_datetime"].dt.date,
        "holiday_period"
    ]).size().reset_index(name="crime_count")

    daily.columns = ["date", "holiday_period", "crime_count"]
    daily["date"] = pd.to_datetime(daily["date"])
    daily["year"] = daily["date"].dt.year
    daily["month"] = daily["date"].dt.month
    daily["day"] = daily["date"].dt.day

    return daily


def analyze_per_holiday_effects(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Analyze crime effects for each individual holiday.

    For each holiday, compares daily counts during the holiday period
    (pre + holiday + post) against baseline days.

    Args:
        df: DataFrame with holiday_period and holiday_name columns

    Returns:
        Dictionary with holiday names as keys and statistics as values
    """
    # Get daily counts per holiday
    daily = calculate_daily_counts(df)

    # Merge back holiday info - ensure date types match
    df_with_holiday = df[["dispatch_datetime", "holiday_name"]].copy()
    df_with_holiday["date"] = pd.to_datetime(df_with_holiday["dispatch_datetime"].dt.date)
    daily["date"] = pd.to_datetime(daily["date"])

    daily = daily.merge(
        df_with_holiday[["date", "holiday_name"]],
        on="date",
        how="left"
    )

    # Get unique holidays
    holidays = df[df["holiday_name"].notna()]["holiday_name"].unique()

    results = {}

    for holiday in holidays:
        # Get holiday period data (pre + holiday + post)
        holiday_data = daily[
            (daily["holiday_name"] == holiday) &
            (daily["holiday_period"].isin(["pre_holiday", "holiday", "post_holiday"]))
        ]["crime_count"].values

        # Get baseline data (same year, non-holiday period)
        holiday_years = df[df["holiday_name"] == holiday]["year"].unique()

        baseline_data = daily[
            (daily["holiday_period"] == "baseline") &
            (daily["year"].isin(holiday_years))
        ]["crime_count"].values

        if len(holiday_data) < 3 or len(baseline_data) < 10:
            continue

        # Statistical comparison
        test_result = compare_two_samples(
            holiday_data, baseline_data,
            alpha=STAT_CONFIG["alpha"]
        )

        # Effect size
        try:
            effect_size = cohens_d(holiday_data, baseline_data)
        except Exception:
            effect_size = 0.0

        # Bootstrap CI
        try:
            ci_lower, ci_upper, point_est, se = bootstrap_ci(
                holiday_data,
                statistic='mean',
                confidence_level=STAT_CONFIG["confidence_level"],
                n_resamples=2000,
                random_state=STAT_CONFIG["random_seed"]
            )
        except Exception:
            ci_lower, ci_upper, point_est, se = np.nan, np.nan, np.mean(holiday_data), 0

        results[holiday] = {
            "holiday_mean": float(np.mean(holiday_data)),
            "baseline_mean": float(np.mean(baseline_data)),
            "holiday_std": float(np.std(holiday_data, ddof=1)),
            "baseline_std": float(np.std(baseline_data, ddof=1)),
            "n_holiday_days": len(holiday_data),
            "n_baseline_days": len(baseline_data),
            "pct_change": float((np.mean(holiday_data) - np.mean(baseline_data)) / np.mean(baseline_data) * 100),
            "test_result": test_result,
            "cohens_d": float(effect_size),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "point_estimate": float(point_est),
            "standard_error": float(se)
        }

    return results


def apply_holiday_fdr_correction(holiday_results: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Apply FDR correction to p-values from multiple holiday comparisons.

    Args:
        holiday_results: Dictionary from analyze_per_holiday_effects()

    Returns:
        Same dictionary with adjusted p-values added
    """
    # Extract p-values
    holidays = list(holiday_results.keys())
    p_values = np.array([
        holiday_results[h]["test_result"]["p_value"]
        for h in holidays
    ])

    # Apply FDR correction
    adjusted_p = apply_fdr_correction(p_values, method='bh')

    # Add adjusted p-values to results
    for i, holiday in enumerate(holidays):
        holiday_results[holiday]["adjusted_p_value"] = float(adjusted_p[i])
        holiday_results[holiday]["is_significant_fdr"] = adjusted_p[i] < STAT_CONFIG["alpha"]

    return holiday_results


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_holiday_calendar_heatmap(df: pd.DataFrame) -> str:
    """
    Create a heatmap showing crime rates by day of year with holidays highlighted.

    Args:
        df: DataFrame with dispatch_datetime and holiday_name columns

    Returns:
        Base64 encoded image HTML tag
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])

    # Aggregate by day of year
    df["day_of_year"] = df["dispatch_datetime"].dt.dayofyear
    df["month_day"] = df["dispatch_datetime"].dt.strftime("%m-%d")

    # Get average daily crime count by day of year
    daily_avg = df.groupby(["day_of_year", "month_day"]).size().reset_index(name="count")
    daily_avg["avg_count"] = daily_avg["count"] / df["year"].nunique()

    # Create pivot table for heatmap (day vs month)
    daily_avg["month"] = daily_avg["month_day"].str[:2].astype(int)
    daily_avg["day"] = daily_avg["month_day"].str[3:].astype(int)

    # Create a more readable heatmap - month rows, day columns
    pivot_data = []
    for month in range(1, 13):
        month_data = daily_avg[daily_avg["month"] == month]
        days_in_month = month_data["day"].max()

        row = []
        for day in range(1, 32):  # Max 31 days
            if day > days_in_month or len(month_data[month_data["day"] == day]) == 0:
                row.append(np.nan)
            else:
                row.append(month_data[month_data["day"] == day]["avg_count"].values[0])

        pivot_data.append(row)

    pivot_df = pd.DataFrame(
        pivot_data,
        index=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        columns=range(1, 32)
    )

    # Create heatmap
    sns.heatmap(
        pivot_df,
        cmap=COLORS["sequential"],
        cbar_kws={"label": "Average Daily Crime Count"},
        linewidths=0.1,
        linecolor="gray",
        ax=ax
    )

    ax.set_xlabel("Day of Month", fontsize=12)
    ax.set_ylabel("Month", fontsize=12)
    ax.set_title("Crime Rate Calendar Heatmap with Holiday Periods Highlighted",
                 fontsize=14, fontweight="bold")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_daily_comparison_boxplot(daily_df: pd.DataFrame) -> str:
    """
    Create box plot comparing daily crime counts across holiday periods.

    Args:
        daily_df: DataFrame from calculate_daily_counts()

    Returns:
        Base64 encoded image HTML tag
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    # Order by holiday period
    period_order = ["baseline", "pre_holiday", "holiday", "post_holiday"]
    period_labels = [
        "Baseline\n(non-holiday)",
        "Pre-Holiday\n(3 days before)",
        "Holiday\n(observed day)",
        "Post-Holiday\n(3 days after)"
    ]

    # Create color mapping
    colors = [COLORS["primary"], COLORS["warning"], COLORS["danger"], COLORS["warning"]]

    # Prepare data for plotting
    plot_data = []
    plot_colors = []
    for i, period in enumerate(period_order):
        period_data = daily_df[daily_df["holiday_period"] == period]["crime_count"]
        plot_data.append(period_data)
        plot_colors.extend([colors[i]] * len(period_data))

    # Create box plot
    bp = ax.boxplot(plot_data, labels=period_labels, patch_artist=True)

    # Color the boxes
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel("Daily Crime Count", fontsize=12)
    ax.set_title("Daily Crime Counts by Holiday Period",
                 fontsize=14, fontweight="bold")
    plt.xticks(rotation=0, ha="center")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_holiday_effects_barplot(holiday_results: Dict[str, Dict]) -> str:
    """
    Create horizontal bar plot showing percent change for each holiday.

    Args:
        holiday_results: Dictionary from analyze_per_holiday_effects()

    Returns:
        Base64 encoded image HTML tag
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    # Sort by absolute percent change
    sorted_holidays = sorted(
        holiday_results.keys(),
        key=lambda h: abs(holiday_results[h]["pct_change"]),
        reverse=True
    )

    holidays = []
    pct_changes = []
    colors_list = []
    significant = []

    for holiday in sorted_holidays[:15]:  # Top 15
        result = holiday_results[holiday]
        holidays.append(holiday[:30])  # Truncate long names
        pct_changes.append(result["pct_change"])

        # Color based on direction and significance
        if result.get("is_significant_fdr", False):
            if result["pct_change"] > 0:
                colors_list.append(COLORS["danger"])  # Red for increase
            else:
                colors_list.append(COLORS["success"])  # Green for decrease
        else:
            colors_list.append(COLORS["primary"])  # Blue for non-significant

        significant.append(result.get("is_significant_fdr", False))

    # Create horizontal bar plot
    y_pos = range(len(holidays))
    bars = ax.barh(y_pos, pct_changes, color=colors_list, alpha=0.8, edgecolor="black", linewidth=0.5)

    # Add value labels
    for i, (bar, pct) in enumerate(zip(bars, pct_changes)):
        x_pos = pct + (1 if pct >= 0 else -1)
        ax.text(x_pos, i, f"{pct:+.1f}%",
                va="center", ha="left" if pct >= 0 else "right",
                fontsize=9, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(holidays, fontsize=9)
    ax.set_xlabel("Percent Change from Baseline (%)", fontsize=12)
    ax.set_title("Crime Rate Changes During Holiday Periods (Top 15)\n"
                 "* = Statistically significant after FDR correction",
                 fontsize=14, fontweight="bold")
    ax.axvline(x=0, color="black", linestyle="-", linewidth=0.8)
    ax.grid(True, alpha=0.3, axis="x")

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["danger"], label="Significant Increase"),
        Patch(facecolor=COLORS["success"], label="Significant Decrease"),
        Patch(facecolor=COLORS["primary"], label="Not Significant")
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


# =============================================================================
# MAIN ANALYSIS ORCHESTRATOR
# =============================================================================

def analyze_holiday_effects() -> Dict[str, Any]:
    """
    Run comprehensive holiday effects analysis with statistical testing.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.

    Statistical tests performed:
        - Chi-square test for holiday vs baseline crime distribution
        - Two-sample comparison (holiday period vs baseline)
        - Cohen's d effect size
        - Bootstrap 99% CI for holiday effect
        - Per-holiday analysis with FDR correction
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    print("Loading data for holiday effects analysis...")
    df = load_data(clean=False)

    print("Extracting temporal features...")
    df = extract_temporal_features(df)

    # Filter out 2026 for trend analysis (incomplete year)
    df_analysis = df[df["year"] < 2026].copy()

    print("Identifying holiday periods...")
    df_analysis = identify_holiday_periods(df_analysis)

    results = {}
    results["total_records"] = len(df_analysis)
    results["total_records_with_2026"] = len(df)

    # Store analysis metadata
    try:
        data_version = DataVersion(PROJECT_ROOT / "data" / "crime_incidents_combined.parquet")
        metadata = get_analysis_metadata(
            data_version=data_version,
            analysis_type="holiday_effects",
            confidence_level=STAT_CONFIG["confidence_level"],
            bootstrap_n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_seed=STAT_CONFIG["random_seed"],
            holiday_window_days=HOLIDAY_WINDOW_DAYS
        )
        results["metadata"] = metadata
    except Exception as e:
        print(f"Warning: Could not create data version: {e}")
        metadata = get_analysis_metadata(
            analysis_type="holiday_effects",
            confidence_level=STAT_CONFIG["confidence_level"],
            bootstrap_n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_seed=STAT_CONFIG["random_seed"],
            holiday_window_days=HOLIDAY_WINDOW_DAYS
        )
        results["metadata"] = metadata

    # ========================================================================
    # HOLIDAY PERIOD DISTRIBUTION
    # ========================================================================
    print("Analyzing holiday period distribution...")
    period_counts = df_analysis["holiday_period"].value_counts()
    results["period_distribution"] = period_counts.to_dict()

    # Count unique holidays
    unique_holidays = df_analysis[df_analysis["holiday_name"].notna()]["holiday_name"].nunique()
    results["unique_holidays_count"] = int(unique_holidays)

    # ========================================================================
    # DAILY COUNT ANALYSIS
    # ========================================================================
    print("Calculating daily counts...")
    daily_df = calculate_daily_counts(df_analysis)
    results["daily_stats"] = {
        "total_days": len(daily_df),
        "baseline_days": int((daily_df["holiday_period"] == "baseline").sum()),
        "pre_holiday_days": int((daily_df["holiday_period"] == "pre_holiday").sum()),
        "holiday_days": int((daily_df["holiday_period"] == "holiday").sum()),
        "post_holiday_days": int((daily_df["holiday_period"] == "post_holiday").sum())
    }

    # ========================================================================
    # STATISTICAL TESTS: Holiday Period vs Baseline
    # ========================================================================
    print("Running holiday vs baseline comparison tests...")

    # Get daily counts for each period
    baseline_counts = daily_df[daily_df["holiday_period"] == "baseline"]["crime_count"].values
    pre_holiday_counts = daily_df[daily_df["holiday_period"] == "pre_holiday"]["crime_count"].values
    holiday_counts = daily_df[daily_df["holiday_period"] == "holiday"]["crime_count"].values
    post_holiday_counts = daily_df[daily_df["holiday_period"] == "post_holiday"]["crime_count"].values

    # Combine all holiday period counts (pre + holiday + post)
    all_holiday_counts = np.concatenate([pre_holiday_counts, holiday_counts, post_holiday_counts])

    # Chi-square test for distribution difference
    contingency = np.array([
        [baseline_counts.sum(), all_holiday_counts.sum()],
        [len(baseline_counts), len(all_holiday_counts)]
    ])
    holiday_baseline_test = chi_square_test(contingency)
    holiday_baseline_test["is_significant"] = holiday_baseline_test["p_value"] < STAT_CONFIG["alpha"]
    results["holiday_baseline_test"] = holiday_baseline_test

    # Two-sample comparison (mean daily counts)
    holiday_comparison = compare_two_samples(
        all_holiday_counts, baseline_counts,
        alpha=STAT_CONFIG["alpha"]
    )
    results["holiday_comparison_test"] = holiday_comparison

    # Cohen's d effect size
    try:
        effect_size = cohens_d(all_holiday_counts, baseline_counts)
    except Exception as e:
        print(f"Warning: Could not calculate Cohen's d: {e}")
        effect_size = 0.0
    results["effect_size"] = float(effect_size)

    # Bootstrap 99% CI for the difference
    try:
        # Bootstrap the difference in means
        n_bootstrap = STAT_CONFIG["bootstrap_n_resamples"]
        boot_diffs = []
        np.random.seed(STAT_CONFIG["random_seed"])

        for _ in range(n_bootstrap):
            boot_holiday = np.random.choice(all_holiday_counts, size=len(all_holiday_counts), replace=True)
            boot_baseline = np.random.choice(baseline_counts, size=len(baseline_counts), replace=True)
            boot_diffs.append(boot_holiday.mean() - boot_baseline.mean())

        boot_diffs = np.array(boot_diffs)
        ci_lower = float(np.percentile(boot_diffs, (1 - STAT_CONFIG["confidence_level"]) / 2 * 100))
        ci_upper = float(np.percentile(boot_diffs, (1 + STAT_CONFIG["confidence_level"]) / 2 * 100))
        observed_diff = float(all_holiday_counts.mean() - baseline_counts.mean())

        results["effect_ci"] = {
            "observed_difference": observed_diff,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "confidence_level": STAT_CONFIG["confidence_level"]
        }
    except Exception as e:
        print(f"Warning: Could not calculate bootstrap CI: {e}")
        results["effect_ci"] = {
            "observed_difference": float(all_holiday_counts.mean() - baseline_counts.mean()),
            "ci_lower": np.nan,
            "ci_upper": np.nan,
            "confidence_level": STAT_CONFIG["confidence_level"]
        }

    print(f"  Holiday vs Baseline: {holiday_comparison['test_name']}, p={holiday_comparison['p_value']:.4f}")
    print(f"  Cohen's d: {effect_size:.3f}")

    # ========================================================================
    # PER-HOLIDAY ANALYSIS
    # ========================================================================
    print("Analyzing individual holidays...")
    holiday_results = analyze_per_holiday_effects(df_analysis)

    # Apply FDR correction
    holiday_results = apply_holiday_fdr_correction(holiday_results)
    results["by_holiday"] = holiday_results

    # Count significant holidays
    significant_count = sum(1 for h in holiday_results.values()
                           if h.get("is_significant_fdr", False))
    results["significant_holidays_count"] = significant_count
    print(f"  Significant holidays after FDR correction: {significant_count}/{len(holiday_results)}")

    # ========================================================================
    # PERIOD-BY-PERIOD ANALYSIS
    # ========================================================================
    print("Analyzing individual holiday periods...")

    period_analysis = {}
    for period_name, period_data in [
        ("pre_holiday", pre_holiday_counts),
        ("holiday", holiday_counts),
        ("post_holiday", post_holiday_counts)
    ]:
        if len(period_data) >= 10:
            test_result = compare_two_samples(period_data, baseline_counts, alpha=STAT_CONFIG["alpha"])
            try:
                effect = cohens_d(period_data, baseline_counts)
            except Exception:
                effect = 0.0

            period_analysis[period_name] = {
                "mean": float(np.mean(period_data)),
                "std": float(np.std(period_data, ddof=1)),
                "n": len(period_data),
                "test_result": test_result,
                "cohens_d": float(effect),
                "pct_change_from_baseline": float(
                    (np.mean(period_data) - np.mean(baseline_counts)) / np.mean(baseline_counts) * 100
                )
            }

    results["period_analysis"] = period_analysis

    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================
    print("Creating visualizations...")

    results["holiday_calendar_plot"] = create_holiday_calendar_heatmap(df_analysis)
    results["daily_count_plot"] = create_daily_comparison_boxplot(daily_df)
    results["holiday_effects_plot"] = create_holiday_effects_barplot(holiday_results)

    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    print("Calculating summary statistics...")

    # Overall means
    results["summary_means"] = {
        "baseline_mean": float(np.mean(baseline_counts)),
        "pre_holiday_mean": float(np.mean(pre_holiday_counts)) if len(pre_holiday_counts) > 0 else 0,
        "holiday_mean": float(np.mean(holiday_counts)) if len(holiday_counts) > 0 else 0,
        "post_holiday_mean": float(np.mean(post_holiday_counts)) if len(post_holiday_counts) > 0 else 0,
        "all_holiday_mean": float(np.mean(all_holiday_counts))
    }

    # Identify highest and lowest impact holidays
    if holiday_results:
        sorted_by_change = sorted(
            holiday_results.items(),
            key=lambda x: x[1]["pct_change"],
            reverse=True
        )
        results["highest_increase"] = {
            "holiday": sorted_by_change[0][0],
            "pct_change": sorted_by_change[0][1]["pct_change"]
        }
        results["largest_decrease"] = {
            "holiday": sorted_by_change[-1][0],
            "pct_change": sorted_by_change[-1][1]["pct_change"]
        }

    print("Holiday effects analysis complete!")
    return results


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_holiday_markdown_report(results: Dict[str, Any]) -> str:
    """
    Generate markdown report from holiday effects analysis results.

    Args:
        results: Dictionary from analyze_holiday_effects()

    Returns:
        Markdown string with analysis results including statistical tests.
    """
    md = []

    # Analysis Configuration section
    if "metadata" in results:
        md.append(format_metadata_markdown(results["metadata"]))
        md.append("\n")

    # ========================================================================
    # TITLE
    # ========================================================================
    md.append("# Holiday Effects Analysis\n")
    md.append("**Philadelphia Crime Incidents (2006-2026)**\n\n")
    md.append("---\n\n")

    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    md.append("## Executive Summary\n\n")

    md.append("**Question:** How do crime rates change during U.S. federal holiday periods?\n\n")

    # Overall findings
    summary_means = results["summary_means"]
    baseline_mean = summary_means["baseline_mean"]
    holiday_mean = summary_means["all_holiday_mean"]
    overall_pct_change = (holiday_mean - baseline_mean) / baseline_mean * 100

    md.append("**Key Findings:**\n\n")
    md.append(f"- **Overall Holiday Effect**: Holiday periods show a ")
    if overall_pct_change > 0:
        md.append(f"**{overall_pct_change:+.1f}% increase** ")
    else:
        md.append(f"**{overall_pct_change:+.1f}% decrease** ")
    md.append(f"in daily crime counts compared to baseline\n")
    md.append(f"  - Baseline: {format_number(int(baseline_mean))} crimes/day\n")
    md.append(f"  - Holiday period: {format_number(int(holiday_mean))} crimes/day\n\n")

    # Period breakdown
    md.append("**Period Breakdown:**\n")
    period_analysis = results.get("period_analysis", {})
    for period_label, period_key in [
        ("Pre-Holiday", "pre_holiday"),
        ("Holiday Day", "holiday"),
        ("Post-Holiday", "post_holiday")
    ]:
        if period_key in period_analysis:
            pa = period_analysis[period_key]
            sig = "**significant**" if pa["test_result"]["is_significant"] else "not significant"
            md.append(f"- **{period_label}**: {format_number(int(pa['mean']))} crimes/day ")
            md.append(f"({pa['pct_change_from_baseline']:+.1f}% vs baseline, {sig})\n")
    md.append("\n")

    # Statistical test results
    if "holiday_comparison_test" in results:
        ht = results["holiday_comparison_test"]
        sig = "**significant**" if ht["is_significant"] else "not significant"
        md.append(f"**Statistical Test**: {ht['test_name']}, p = {ht['p_value']:.4f} ({sig} at alpha = {STAT_CONFIG['alpha']})\n")

    if "effect_size" in results:
        from analysis.stats_utils import interpret_cohens_d
        effect_interpret = interpret_cohens_d(results["effect_size"])
        md.append(f"**Effect Size**: Cohen's d = {results['effect_size']:.3f} ({effect_interpret})\n")

    if "effect_ci" in results:
        ci = results["effect_ci"]
        md.append(f"**99% CI for Difference**: [{format_number(int(ci['ci_lower']))}, {format_number(int(ci['ci_upper']))}]\n")

    md.append(f"\n**Holidays Analyzed**: {results['unique_holidays_count']} U.S. federal holidays\n")
    md.append(f"**Significant Holidays**: {results['significant_holidays_count']}/{len(results['by_holiday'])} show significant effects after FDR correction\n\n")

    md.append("---\n\n")

    # ========================================================================
    # PRIMARY VISUALIZATION: Daily Count Comparison
    # ========================================================================
    md.append("## Daily Crime Counts by Holiday Period\n\n")
    md.append(results["daily_count_plot"])
    md.append("\n\n")
    md.append("*Figure 1: Box plot comparing daily crime counts across baseline and holiday periods. ")
    md.append("Holiday periods include 3 days before, the holiday day, and 3 days after. ")
    md.append("The boxes show the interquartile range with median values indicated.*\n\n")

    # ========================================================================
    # HOLIDAY EFFECTS BAR PLOT
    # ========================================================================
    md.append("---\n\n")
    md.append("## Crime Rate Changes by Holiday\n\n")
    md.append(results["holiday_effects_plot"])
    md.append("\n\n")
    md.append("*Figure 2: Horizontal bar plot showing percent change in crime rates during holiday periods ")
    md.append("compared to baseline. Red bars indicate significant increases, green bars indicate ")
    md.append("significant decreases, and blue bars indicate non-significant changes (after FDR correction).*\n\n")

    # ========================================================================
    # PER-HOLIDAY BREAKDOWN TABLE
    # ========================================================================
    md.append("---\n\n")
    md.append("## Detailed Holiday Breakdown\n\n")
    md.append("| Holiday | Baseline Mean | Holiday Mean | % Change | Cohen's d | p-value | Adj. p-value | Significant? |\n")
    md.append("|---------|---------------|--------------|----------|-----------|---------|--------------|--------------|\n")

    # Sort by absolute percent change
    sorted_holidays = sorted(
        results["by_holiday"].items(),
        key=lambda x: abs(x[1]["pct_change"]),
        reverse=True
    )

    for holiday, stats in sorted_holidays:
        sig_mark = "**" if stats.get("is_significant_fdr", False) else ""
        md.append(f"| {holiday[:40]} | ")
        md.append(f"{format_number(int(stats['baseline_mean']))} | ")
        md.append(f"{format_number(int(stats['holiday_mean']))} | ")
        md.append(f"{stats['pct_change']:+.1f}% | ")
        md.append(f"{stats['cohens_d']:.3f} | ")
        md.append(f"{stats['test_result']['p_value']:.4f} | ")
        md.append(f"{stats.get('adjusted_p_value', 0):.4f} | ")
        md.append(f"{'Yes' if stats.get('is_significant_fdr', False) else 'No'}{sig_mark} |\n")

    md.append("\n**Note:** Holidays marked with ** have statistically significant effects after FDR correction (alpha = 0.01).\n\n")

    # ========================================================================
    # CALENDAR HEATMAP
    # ========================================================================
    md.append("---\n\n")
    md.append("## Crime Rate Calendar Heatmap\n\n")
    md.append(results["holiday_calendar_plot"])
    md.append("\n\n")
    md.append("*Figure 3: Calendar heatmap showing average daily crime counts by day of year. ")
    md.append("Darker colors indicate higher crime rates. This visualization reveals patterns ")
    md.append("in crime distribution throughout the year.*\n\n")

    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    md.append("---\n\n")
    md.append("## Methodology\n\n")

    md.append("### Data Source\n")
    md.append(f"- **Dataset**: Philadelphia crime incidents (2006-2026)\n")
    md.append(f"- **Total Records**: {format_number(results['total_records_with_2026'])} incidents\n")
    md.append(f"- **Analysis Period**: 2006-2025 (2026 excluded due to incomplete data)\n\n")

    md.append("### Holiday Detection\n")
    md.append(f"- **Holidays**: {results['unique_holidays_count']} U.S. federal holidays identified using `workalendar.UnitedStates()`\n")
    md.append(f"- **Holiday Window**: {HOLIDAY_WINDOW_DAYS} days before + holiday day + {HOLIDAY_WINDOW_DAYS} days after (7-day holiday week)\n")
    md.append("- **Moving Holidays**: Calculated dynamically (e.g., Thanksgiving = 4th Thursday of November)\n")
    md.append("- **Baseline**: All non-holiday days in the dataset\n\n")

    md.append("### Statistical Approach\n")
    md.append(f"- **Significance Level**: alpha = {STAT_CONFIG['alpha']} (99% confidence)\n")
    md.append(f"- **Confidence Intervals**: {STAT_CONFIG['confidence_level']*100:.0f}% CI using bootstrap resampling\n")
    md.append(f"- **Effect Size**: Cohen's d for magnitude of differences\n")
    md.append("- **Multiple Testing Correction**: FDR (Benjamini-Hochberg) applied across all holiday comparisons\n")
    md.append(f"- **Bootstrap Resamples**: {STAT_CONFIG['bootstrap_n_resamples']}\n\n")

    md.append("### Period Definitions\n")
    md.append(f"- **Pre-Holiday**: {HOLIDAY_WINDOW_DAYS} days immediately before the holiday\n")
    md.append(f"- **Holiday**: The observed holiday day (or nearest weekday if holiday falls on weekend)\n")
    md.append(f"- **Post-Holiday**: {HOLIDAY_WINDOW_DAYS} days immediately after the holiday\n")
    md.append("- **Baseline**: All other days (non-holiday periods)\n\n")

    # ========================================================================
    # CONCLUSIONS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Conclusions\n\n")

    # Overall verdict
    if results["holiday_comparison_test"]["is_significant"]:
        if overall_pct_change > 2:
            md.append("**Overall Finding**: Holiday periods show a **statistically significant increase** in crime rates. \n\n")
            md.append(f"During holiday periods, Philadelphia experiences approximately **{overall_pct_change:.1f}% more crime** ")
            md.append(f"per day compared to baseline periods. This equates to approximately ")
            md.append(f"**{format_number(int(holiday_mean - baseline_mean))}** additional crimes per day.\n\n")
        elif overall_pct_change < -2:
            md.append("**Overall Finding**: Holiday periods show a **statistically significant decrease** in crime rates. \n\n")
            md.append(f"During holiday periods, Philadelphia experiences approximately **{abs(overall_pct_change):.1f}% less crime** ")
            md.append(f"per day compared to baseline periods.\n\n")
        else:
            md.append("**Overall Finding**: Holiday periods show a **statistically significant but modest** change in crime rates. \n\n")
    else:
        md.append("**Overall Finding**: Holiday periods do **not** show a statistically significant difference in crime rates compared to baseline. \n\n")

    # Notable holidays
    if "highest_increase" in results:
        hi = results["highest_increase"]
        md.append(f"**Highest Impact Holiday**: **{hi['holiday']}** with a **{hi['pct_change']:+.1f}%** change in crime rate.\n\n")

    if "largest_decrease" in results:
        ld = results["largest_decrease"]
        if ld["pct_change"] < 0:  # Only show if actually a decrease
            md.append(f"**Largest Decrease**: **{ld['holiday']}** with a **{ld['pct_change']:.1f}%** reduction in crime rate.\n\n")

    md.append("### Recommendations\n\n")
    md.append("- **Resource Allocation**: Consider adjusting patrol schedules during holidays with significant crime increases\n")
    md.append("- **Further Analysis**: Examine crime type breakdown during high-risk holidays to target specific offenses\n")
    md.append("- **Geographic Analysis**: Assess whether holiday effects vary by police district\n\n")

    # Footer
    md.append("---\n\n")
    md.append("*\n")
    md.append(f"Report generated by Claude Code | ")
    md.append(f"Holiday effects analysis using workalendar for US federal holiday detection\n")

    return "\n".join(md)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    results = analyze_holiday_effects()
    report = generate_holiday_markdown_report(results)

    report_path = REPORTS_DIR / "13_holiday_effects_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
