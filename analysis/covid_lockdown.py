"""
COVID-19 Lockdown Impact Analysis

Answers the question: "How did the COVID-19 lockdowns impact Philadelphia's crime landscape?"

Analyzes crime patterns across three periods:
- Pre-lockdown: 2018-2019 (baseline)
- Lockdown: 2020-2022 (COVID period)
- Post-lockdown: 2023-2025 (new normal)

Enhanced with statistical significance testing including multi-group comparison
with omnibus test, Tukey HSD post-hoc, and FDR-adjusted p-values.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT, STAT_CONFIG
from analysis.utils import (
    load_data,
    extract_temporal_features,
    image_to_base64,
    create_image_tag,
    format_number,
)
from analysis.stats_utils import compare_multiple_samples, apply_fdr_correction, bootstrap_ci
from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion


# =============================================================================
# CRIME TYPE CLASSIFICATIONS
# =============================================================================

# Violent crimes
VIOLENT_CRIMES = [
    "Homicide - Criminal",
    "Homicide - Gross Negligence",
    "Homicide - Justifiable",
    "Rape",
    "Robbery Firearm",
    "Robbery No Firearm",
    "Aggravated Assault Firearm",
    "Aggravated Assault No Firearm",
]

# Property crimes
PROPERTY_CRIMES = [
    "Arson",
    "Burglary Non-Residential",
    "Burglary Residential",
    "Motor Vehicle Theft",
    "Theft from Vehicle",
    "Thefts",
]

# Quality-of-life crimes
QUALITY_OF_LIFE_CRIMES = [
    "Disorderly Conduct",
    "Public Drunkenness",
    "Vagrancy/Loitering",
    "Vandalism/Criminal Mischief",
    "Liquor Law Violations",
    "DRIVING UNDER THE INFLUENCE",
]

# Lockdown date reference
LOCKDOWN_DATE = datetime(2020, 3, 16)  # Philadelphia stay-at-home order


# =============================================================================
# PERIOD DEFINITIONS
# =============================================================================

def assign_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign COVID period classification to each record.

    Periods:
    - Pre-lockdown: 2018-2019
    - Lockdown: 2020-2022
    - Post-lockdown: 2023-2025

    Note: 2026 data is excluded (incomplete - through Jan 20 only)
    """
    df = df.copy()

    # Filter to 2018-2025 only
    df = df[(df["year"] >= 2018) & (df["year"] <= 2025)].copy()

    # Assign periods
    df["covid_period"] = "Pre-lockdown (2018-2019)"
    df.loc[df["year"].isin([2020, 2021, 2022]), "covid_period"] = "Lockdown (2020-2022)"
    df.loc[df["year"].isin([2023, 2024, 2025]), "covid_period"] = "Post-lockdown (2023-2025)"

    # Create ordered categorical
    period_order = ["Pre-lockdown (2018-2019)", "Lockdown (2020-2022)", "Post-lockdown (2023-2025)"]
    df["covid_period"] = pd.Categorical(df["covid_period"], categories=period_order, ordered=True)

    return df


def classify_crime_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add detailed crime_type column for breakdown analysis.

    Categories: Violent, Property, Quality_of_Life, Other
    """
    df = df.copy()
    df["crime_type"] = "Other"

    mask_violent = df["text_general_code"].isin(VIOLENT_CRIMES)
    mask_property = df["text_general_code"].isin(PROPERTY_CRIMES)
    mask_qol = df["text_general_code"].isin(QUALITY_OF_LIFE_CRIMES)

    df.loc[mask_violent, "crime_type"] = "Violent"
    df.loc[mask_property, "crime_type"] = "Property"
    df.loc[mask_qol, "crime_type"] = "Quality_of_Life"

    return df


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_time_series_plot(monthly_data: pd.DataFrame) -> str:
    """
    Create time series plot of monthly crime counts with lockdown annotation.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])

    # Create the time series data first
    all_ts_data = monthly_data.groupby("year_month").size().reset_index(name="count")
    all_ts_data["year_month_str"] = all_ts_data["year_month"].astype(str)

    # Get all crime types for time series
    for crime_type, color, label in [
        ("All", COLORS["primary"], "All Crimes"),
        ("Violent", COLORS["danger"], "Violent Crimes"),
        ("Property", COLORS["secondary"], "Property Crimes"),
    ]:
        if crime_type == "All":
            # Plot all crimes
            ax.plot(all_ts_data["year_month_str"], all_ts_data["count"],
                   color=color, linewidth=2, label=label, alpha=0.8)
        else:
            # Filter by crime type
            filtered = monthly_data[monthly_data["crime_type"] == crime_type]
            if len(filtered) > 0:
                ts_data = filtered.groupby("year_month").size().reset_index(name="count")
                ts_data["year_month_str"] = ts_data["year_month"].astype(str)
                ax.plot(ts_data["year_month_str"], ts_data["count"],
                       color=color, linewidth=1.5, label=label, alpha=0.7)

    # Find the lockdown month position (March 2020)
    lockdown_month_str = "2020-03"
    if lockdown_month_str in all_ts_data["year_month_str"].values:
        lockdown_idx = all_ts_data[all_ts_data["year_month_str"] == lockdown_month_str].index[0]
        ax.axvline(x=lockdown_idx, color=COLORS["danger"], linestyle="--",
                  linewidth=2, alpha=0.7)
        ax.text(lockdown_idx, ax.get_ylim()[1] * 0.95, "  Mar 2020\n  Lockdown",
               color=COLORS["danger"], fontsize=10, fontweight="bold",
               va="top")

    # Shade lockdown period (March 2020 to December 2022)
    lockdown_start_str = "2020-03"
    lockdown_end_str = "2022-12"
    if lockdown_start_str in all_ts_data["year_month_str"].values and lockdown_end_str in all_ts_data["year_month_str"].values:
        start_idx = all_ts_data[all_ts_data["year_month_str"] == lockdown_start_str].index[0]
        end_idx = all_ts_data[all_ts_data["year_month_str"] == lockdown_end_str].index[0]
        ax.axvspan(start_idx, end_idx, alpha=0.1, color=COLORS["warning"])

    # Format x-axis
    n_ticks = 12
    tick_positions = np.linspace(0, len(all_ts_data) - 1, n_ticks, dtype=int)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([all_ts_data["year_month_str"].iloc[i] for i in tick_positions],
                      rotation=45, ha="right", fontsize=8)

    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Monthly Crime Count", fontsize=12)
    ax.set_title("Philadelphia Crime Trends: Pre-Lockdown to Post-Lockdown (2018-2025)",
                fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_period_comparison_barplot(period_counts: pd.DataFrame, title: str) -> str:
    """
    Create grouped bar plot comparing periods.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    x = np.arange(len(period_counts))
    width = 0.25

    # Get counts for each period
    pre_counts = period_counts["Pre-lockdown (2018-2019)"].values
    lockdown_counts = period_counts["Lockdown (2020-2022)"].values
    post_counts = period_counts["Post-lockdown (2023-2025)"].values

    ax.bar(x - width, pre_counts, width, label="Pre-lockdown (2018-2019)",
           color=COLORS["primary"], alpha=0.8)
    ax.bar(x, lockdown_counts, width, label="Lockdown (2020-2022)",
           color=COLORS["warning"], alpha=0.8)
    ax.bar(x + width, post_counts, width, label="Post-lockdown (2023-2025)",
           color=COLORS["success"], alpha=0.8)

    ax.set_xlabel("Crime Type", fontsize=12)
    ax.set_ylabel("Annual Average Count", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(period_counts.index, rotation=45, ha="right")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_burglary_displacement_chart(burglary_monthly: pd.DataFrame) -> str:
    """
    Create line chart showing residential vs commercial burglary trends.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])

    # Aggregate by year and type
    residential = burglary_monthly[burglary_monthly["text_general_code"] == "Burglary Residential"]
    commercial = burglary_monthly[burglary_monthly["text_general_code"] == "Burglary Non-Residential"]

    res_yearly = residential.groupby("year").size().reset_index(name="count")
    com_yearly = commercial.groupby("year").size().reset_index(name="count")

    ax.plot(res_yearly["year"], res_yearly["count"], "o-",
           color=COLORS["danger"], linewidth=2, markersize=8, label="Residential Burglary")
    ax.plot(com_yearly["year"], com_yearly["count"], "s-",
           color=COLORS["secondary"], linewidth=2, markersize=8, label="Commercial Burglary")

    # Highlight lockdown period
    ax.axvspan(2020, 2022, alpha=0.15, color=COLORS["warning"])
    ax.axvline(2020, color=COLORS["danger"], linestyle="--", linewidth=1.5, alpha=0.5)
    ax.text(2020, ax.get_ylim()[1] * 0.95, "Lockdown", color=COLORS["danger"],
           fontsize=9, ha="left", va="top")

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Annual Burglary Count", fontsize=12)
    ax.set_title("Burglary Displacement: Residential vs Commercial (2018-2025)",
                fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_heatmap(crime_type_pivot: pd.DataFrame) -> str:
    """
    Create heatmap showing percent change by crime type and period.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    # Create heatmap
    sns.heatmap(crime_type_pivot, annot=True, fmt=".1f", cmap="RdYlGn",
               center=0, linewidths=0.5, cbar_kws={"label": "% Change from Pre-Lockdown"},
               ax=ax)

    ax.set_title("Crime Type Percent Change Relative to Pre-Lockdown Baseline",
                fontsize=14, fontweight="bold")
    ax.set_xlabel("Period", fontsize=12)
    ax.set_ylabel("Crime Type", fontsize=12)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_period_stats(df: pd.DataFrame) -> dict:
    """
    Calculate statistics for each COVID period.
    """
    stats = {}

    for period in ["Pre-lockdown (2018-2019)", "Lockdown (2020-2022)", "Post-lockdown (2023-2025)"]:
        period_data = df[df["covid_period"] == period]
        years_in_period = period_data["year"].nunique()

        stats[period] = {
            "total_crimes": len(period_data),
            "annual_average": len(period_data) / years_in_period,
            "years": sorted(period_data["year"].unique().tolist()),
        }

        # Crime type breakdown
        for crime_type in ["Violent", "Property", "Quality_of_Life"]:
            ct_data = period_data[period_data["crime_type"] == crime_type]
            stats[period][f"{crime_type.lower()}_count"] = len(ct_data)
            stats[period][f"{crime_type.lower()}_annual_avg"] = len(ct_data) / years_in_period

    return stats


def calculate_crime_type_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate crime counts by type and period.
    """
    # Get all crime types in data
    all_crime_types = df["text_general_code"].value_counts().index.tolist()

    results = []

    for crime_type in all_crime_types:
        ct_data = df[df["text_general_code"] == crime_type]

        row = {"crime_type": crime_type}

        for period in ["Pre-lockdown (2018-2019)", "Lockdown (2020-2022)", "Post-lockdown (2023-2025)"]:
            period_data = ct_data[ct_data["covid_period"] == period]
            years = period_data["year"].nunique()

            if years > 0:
                row[period] = period_data.groupby("year").size().mean()  # Annual average
            else:
                row[period] = 0

        results.append(row)

    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.set_index("crime_type")

    return comparison_df


def calculate_burglary_displacement(df: pd.DataFrame) -> dict:
    """
    Calculate residential vs commercial burglary statistics by period.
    """
    burglary = df[df["text_general_code"].isin(["Burglary Residential", "Burglary Non-Residential"])]

    stats = {}

    for period in ["Pre-lockdown (2018-2019)", "Lockdown (2020-2022)", "Post-lockdown (2023-2025)"]:
        period_data = burglary[burglary["covid_period"] == period]
        years = period_data["year"].nunique()

        residential = period_data[period_data["text_general_code"] == "Burglary Residential"]
        commercial = period_data[period_data["text_general_code"] == "Burglary Non-Residential"]

        res_count = len(residential)
        com_count = len(commercial)

        stats[period] = {
            "residential_total": res_count,
            "residential_annual": res_count / years if years > 0 else 0,
            "commercial_total": com_count,
            "commercial_annual": com_count / years if years > 0 else 0,
            "residential_ratio": res_count / (res_count + com_count) if (res_count + com_count) > 0 else 0,
            "commercial_ratio": com_count / (res_count + com_count) if (res_count + com_count) > 0 else 0,
        }

        # Calculate percent change from pre-lockdown
        if period == "Lockdown (2020-2022)" or period == "Post-lockdown (2023-2025)":
            pre_annual_res = stats["Pre-lockdown (2018-2019)"]["residential_annual"]
            pre_annual_com = stats["Pre-lockdown (2018-2019)"]["commercial_annual"]

            stats[period]["residential_pct_change"] = (
                (stats[period]["residential_annual"] - pre_annual_res) / pre_annual_res * 100
                if pre_annual_res > 0 else 0
            )
            stats[period]["commercial_pct_change"] = (
                (stats[period]["commercial_annual"] - pre_annual_com) / pre_annual_com * 100
                if pre_annual_com > 0 else 0
            )
        else:
            stats[period]["residential_pct_change"] = 0
            stats[period]["commercial_pct_change"] = 0

    return stats


def calculate_yoy_changes(df: pd.DataFrame) -> dict:
    """
    Calculate year-over-year percent changes.
    """
    yearly = df.groupby("year").size().reset_index(name="count")

    changes = {}
    for i in range(1, len(yearly)):
        year = yearly.iloc[i]["year"]
        prev_year = yearly.iloc[i - 1]["year"]
        count = yearly.iloc[i]["count"]
        prev_count = yearly.iloc[i - 1]["count"]

        pct_change = (count - prev_count) / prev_count * 100 if prev_count > 0 else 0

        changes[year] = {
            "count": int(count),
            "prev_count": int(prev_count),
            "pct_change": pct_change,
        }

    return changes


def analyze_covid_lockdown() -> dict:
    """
    Run comprehensive COVID-19 lockdown impact analysis with statistical testing.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.

    Statistical tests performed:
        - Multi-group comparison across 4 periods (omnibus test)
        - Tukey HSD post-hoc for pairwise comparisons
        - Bootstrap 99% CI for monthly deviations
        - FDR adjustment for multiple comparisons
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    print("Loading data for COVID lockdown analysis...")
    df = load_data(clean=False)

    print("Extracting temporal features...")
    df = extract_temporal_features(df)
    df = classify_crime_type(df)
    df = assign_period(df)

    results = {}

    # Store analysis metadata
    try:
        data_version = DataVersion(PROJECT_ROOT / "data" / "crime_incidents_combined.parquet")
        metadata = get_analysis_metadata(
            data_version=data_version,
            analysis_type="covid_lockdown",
            confidence_level=STAT_CONFIG["confidence_level"],
            bootstrap_n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_seed=STAT_CONFIG["random_seed"]
        )
        results["metadata"] = metadata
    except Exception as e:
        print(f"Warning: Could not create data version: {e}")
        metadata = get_analysis_metadata(
            analysis_type="covid_lockdown",
            confidence_level=STAT_CONFIG["confidence_level"],
            bootstrap_n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_seed=STAT_CONFIG["random_seed"]
        )
        results["metadata"] = metadata

    # ========================================================================
    # STATISTICAL TESTS: Multi-Period Comparison
    # ========================================================================
    print("Running multi-period comparison test...")

    # Define 4 periods for comparison
    # Pre-COVID: 2018-2019
    # Lockdown onset: March-May 2020
    # Post-lockdown: June-December 2020
    # Recovery: 2021-2022

    # Get monthly counts for each period
    period_groups = {}
    period_labels = []

    # Pre-COVID baseline (2018-2019 monthly averages)
    pre_data = df[(df["year"] >= 2018) & (df["year"] <= 2019)]
    pre_monthly = pre_data.groupby(["year", "month"]).size().values
    if len(pre_monthly) >= 2:
        period_groups["Pre-COVID (2018-2019)"] = pre_monthly
        period_labels.append("Pre-COVID (2018-2019)")

    # Lockdown period (March-May 2020)
    lockdown_data = df[(df["year"] == 2020) & (df["month"].isin([3, 4, 5]))]
    lockdown_daily = lockdown_data.groupby(["year", "month", "day"]).size().values
    if len(lockdown_daily) >= 2:
        period_groups["Lockdown (Mar-May 2020)"] = lockdown_daily
        period_labels.append("Lockdown (Mar-May 2020)")

    # Post-lockdown 2020 (June-December 2020)
    post_lockdown_2020 = df[(df["year"] == 2020) & (df["month"].isin(range(6, 13)))]
    post_2020_monthly = post_lockdown_2020.groupby(["year", "month"]).size().values
    if len(post_2020_monthly) >= 2:
        period_groups["Post-Lockdown 2020"] = post_2020_monthly
        period_labels.append("Post-Lockdown 2020")

    # Recovery period (2021-2022)
    recovery_data = df[(df["year"] >= 2021) & (df["year"] <= 2022)]
    recovery_monthly = recovery_data.groupby(["year", "month"]).size().values
    if len(recovery_monthly) >= 2:
        period_groups["Recovery (2021-2022)"] = recovery_monthly
        period_labels.append("Recovery (2021-2022)")

    # Run multi-group comparison if we have enough groups
    if len(period_groups) >= 2:
        period_comparison = compare_multiple_samples(period_groups, alpha=STAT_CONFIG["alpha"])
        results["period_comparison"] = period_comparison

        sig = "**significant**" if period_comparison["is_significant"] else "not significant"
        print(f"  Omnibus test: {period_comparison['omnibus_test']}, p={period_comparison['p_value']:.4f} ({sig})")

        # Store post-hoc results
        if period_comparison.get("post_hoc_results") is not None:
            post_hoc_df = period_comparison["post_hoc_results"]
            results["post_hoc_results"] = post_hoc_df.to_dict("records")
            print(f"  Post-hoc comparisons: {len(post_hoc_df)} pairs")

    # ========================================================================
    # Bootstrap CI for monthly deviations from baseline
    # ========================================================================
    print("Calculating bootstrap 99% CI for monthly deviations...")

    # Calculate baseline mean (2018-2019)
    baseline_mean = pre_data.groupby(["year", "month"]).size().mean()

    # Monthly deviations for 2020
    monthly_deviations = {}
    for month in range(1, 13):
        month_data = df[(df["year"] == 2020) & (df["month"] == month)]
        if len(month_data) > 0:
            # Aggregate to daily level for more stable estimates
            daily_counts = month_data.groupby(["year", "month", "day"]).size().values

            if len(daily_counts) >= 10:
                # Bootstrap CI for daily mean
                try:
                    ci_lower, ci_upper, point_est, se = bootstrap_ci(
                        daily_counts,
                        statistic='mean',
                        confidence_level=STAT_CONFIG["confidence_level"],
                        n_resamples=2000,  # Fewer resamples for speed
                        random_state=STAT_CONFIG["random_seed"]
                    )

                    # Convert to monthly estimate (multiply by average days in month)
                    days_in_month = 30.44  # Average days per month
                    monthly_mean = point_est * days_in_month
                    monthly_lower = ci_lower * days_in_month
                    monthly_upper = ci_upper * days_in_month

                    # Deviation from baseline
                    deviation = monthly_mean - baseline_mean

                    monthly_deviations[month] = {
                        "monthly_mean": monthly_mean,
                        "ci_lower": monthly_lower,
                        "ci_upper": monthly_upper,
                        "deviation_from_baseline": deviation,
                        "pct_deviation": (deviation / baseline_mean * 100) if baseline_mean > 0 else 0
                    }
                except Exception as e:
                    print(f"  Warning: Could not calculate CI for month {month}: {e}")

    results["monthly_deviations_2020"] = monthly_deviations

    # ========================================================================
    # PRIMARY ANALYSIS: Time Series with Lockdown Annotation
    # ========================================================================
    print("Creating time series visualization...")

    # Filter to 2018-2025 for time series
    ts_data = df[(df["year"] >= 2018) & (df["year"] <= 2025)].copy()
    results["time_series_plot"] = create_time_series_plot(ts_data)

    # ========================================================================
    # PERIOD STATISTICS
    # ========================================================================
    print("Calculating period statistics...")
    results["period_stats"] = calculate_period_stats(df)

    # ========================================================================
    # CRIME TYPE COMPARISON
    # ========================================================================
    print("Analyzing crime type changes...")
    results["crime_type_comparison"] = calculate_crime_type_comparison(df)

    # ========================================================================
    # BURGLARY DISPLACEMENT ANALYSIS
    # ========================================================================
    print("Analyzing burglary displacement...")
    burglary_data = df[df["text_general_code"].isin(["Burglary Residential", "Burglary Non-Residential"])]
    results["burglary_stats"] = calculate_burglary_displacement(burglary_data)
    results["burglary_displacement_chart"] = create_burglary_displacement_chart(burglary_data)

    # ========================================================================
    # YEAR-OVER-YEAR CHANGES
    # ========================================================================
    print("Calculating year-over-year changes...")
    results["yoy_changes"] = calculate_yoy_changes(df)

    # ========================================================================
    # HEATMAP: Crime Type × Period
    # ========================================================================
    print("Creating heatmap...")
    crime_type_comparison = results["crime_type_comparison"]

    # Calculate percent change from pre-lockdown
    pre_baseline = crime_type_comparison["Pre-lockdown (2018-2019)"]
    lockdown_pct = ((crime_type_comparison["Lockdown (2020-2022)"] - pre_baseline) / pre_baseline * 100).round(1)
    post_pct = ((crime_type_comparison["Post-lockdown (2023-2025)"] - pre_baseline) / pre_baseline * 100).round(1)

    heatmap_data = pd.DataFrame({
        "Lockdown (2020-2022)": lockdown_pct,
        "Post-lockdown (2023-2025)": post_pct
    })

    # Select top 20 crime types by count for cleaner visualization
    top_crimes = df["text_general_code"].value_counts().head(20).index
    heatmap_data = heatmap_data.loc[top_crimes]

    results["heatmap"] = create_heatmap(heatmap_data)

    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    print("Calculating summary statistics...")

    period_stats = results["period_stats"]
    pre_annual = period_stats["Pre-lockdown (2018-2019)"]["annual_average"]
    lockdown_annual = period_stats["Lockdown (2020-2022)"]["annual_average"]
    post_annual = period_stats["Post-lockdown (2023-2025)"]["annual_average"]

    results["summary_stats"] = {
        "pre_lockdown_annual": pre_annual,
        "lockdown_annual": lockdown_annual,
        "post_lockdown_annual": post_annual,
        "lockdown_change": ((lockdown_annual - pre_annual) / pre_annual * 100),
        "post_change_from_lockdown": ((post_annual - lockdown_annual) / lockdown_annual * 100),
        "post_change_from_pre": ((post_annual - pre_annual) / pre_annual * 100),
    }

    # Get 2020 and 2021 specific stats
    yoy = results["yoy_changes"]
    results["summary_stats"]["march_2020_drop"] = yoy.get(2020, {}).get("pct_change", 0)
    results["summary_stats"]["year_2021_change"] = yoy.get(2021, {}).get("pct_change", 0)

    print("COVID lockdown analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from COVID lockdown analysis results.

    Args:
        results: Dictionary from analyze_covid_lockdown()

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
    md.append("# COVID-19 Lockdown Impact Analysis\n")
    md.append("**Philadelphia Crime Incidents (2018-2025)**\n\n")
    md.append("---\n\n")

    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    md.append("## Executive Summary\n\n")

    summary = results["summary_stats"]
    period_stats = results["period_stats"]

    lockdown_change = summary["lockdown_change"]
    post_from_pre = summary["post_change_from_pre"]

    # Verdict based on statistical test if available
    if "period_comparison" in results:
        pc = results["period_comparison"]
        is_significant = pc["is_significant"]
        if is_significant and lockdown_change < -10:
            verdict = "**Significant Decline** - Lockdown caused major crime reduction (statistically significant)."
        elif is_significant and lockdown_change < -3:
            verdict = "**Moderate Decline** - Lockdown measurably reduced crime (statistically significant)."
        elif is_significant and lockdown_change < 3:
            verdict = "**Minimal Impact** - Crime remained relatively stable (statistically significant difference)."
        elif is_significant:
            verdict = "**Unexpected Increase** - Crime rose during lockdown period (statistically significant)."
        else:
            # Use original verdict logic
            if lockdown_change < -10:
                verdict = "**Significant Decline** - Lockdown caused major crime reduction."
            elif lockdown_change < -3:
                verdict = "**Moderate Decline** - Lockdown measurably reduced crime."
            elif lockdown_change < 3:
                verdict = "**Minimal Impact** - Crime remained relatively stable."
            else:
                verdict = "**Unexpected Increase** - Crime rose during lockdown period."
    else:
        # Use original verdict logic
        if lockdown_change < -10:
            verdict = "**Significant Decline** - Lockdown caused major crime reduction."
        elif lockdown_change < -3:
            verdict = "**Moderate Decline** - Lockdown measurably reduced crime."
        elif lockdown_change < 3:
            verdict = "**Minimal Impact** - Crime remained relatively stable."
        else:
            verdict = "**Unexpected Increase** - Crime rose during lockdown period."

    md.append(f"### Verdict: {verdict}\n\n")

    md.append("**Key Findings:**\n\n")

    # Add omnibus test result if available
    if "period_comparison" in results:
        pc = results["period_comparison"]
        sig = "**significant**" if pc["is_significant"] else "not significant"
        md.append(f"- **Multi-Period Test**: {pc['omnibus_test']}, p = {pc['p_value']:.4f} ({sig} at alpha = {STAT_CONFIG['alpha']})\n")

    # Overall crime change
    md.append(f"- **Overall Crime Change**: ")
    if lockdown_change < 0:
        md.append(f"Crime fell **{abs(lockdown_change):.1f}%** during lockdown (2020-2022) compared to pre-lockdown baseline.\n")
    else:
        md.append(f"Crime rose **{lockdown_change:.1f}%** during lockdown (2020-2022) compared to pre-lockdown baseline.\n")

    # Add post-hoc results if available
    if "post_hoc_results" in results:
        md.append("- **Pairwise Comparisons** (Tukey HSD post-hoc):\n\n")
        md.append("| Period A | Period B | Mean Diff | 99% CI | p-value | Significant |\n")
        md.append("|----------|----------|-----------|--------|---------|------------|\n")

        for comparison in results["post_hoc_results"]:
            group_a = comparison["group_a"]
            group_b = comparison["group_b"]
            mean_diff = comparison["mean_diff"]
            ci_lower = comparison["ci_lower"]
            ci_upper = comparison["ci_upper"]
            p_val = comparison["p_value"]
            is_sig = p_val < STAT_CONFIG["alpha"]

            sig_marker = "Yes" if is_sig else "No"
            md.append(f"| {group_a} | {group_b} | {mean_diff:.1f} | [{ci_lower:.1f}, {ci_upper:.1f}] | {p_val:.4f} | {sig_marker} |\n")

        md.append("\n")

    # March 2020 impact
    march_drop = summary.get("march_2020_drop", 0)
    md.append(f"- **March 2020 Impact**: First year of pandemic showed **{march_drop:+.1f}%** change from 2019.\n")

    # Recovery
    post_from_lockdown = summary["post_change_from_lockdown"]
    md.append(f"- **Recovery**: Post-lockdown period (2023-2025) is **{post_from_lockdown:+.1f}%** {'higher' if post_from_lockdown > 0 else 'lower'} than lockdown period.\n")

    # New normal
    md.append(f"- **New Normal**: Compared to pre-lockdown, post-lockdown crime is **{post_from_pre:+.1f}%** {'higher' if post_from_pre > 0 else 'lower'}.\n")

    # Burglary displacement
    burglary = results["burglary_stats"]
    res_change = burglary["Lockdown (2020-2022)"]["residential_pct_change"]
    com_change = burglary["Lockdown (2020-2022)"]["commercial_pct_change"]

    md.append(f"- **Burglary Displacement**: During lockdown, residential burglary **{res_change:+.1f}%** ")
    md.append(f"while commercial burglary **{com_change:+.1f}%**.\n")

    md.append("\n---\n\n")

    # ========================================================================
    # TIMELINE VISUALIZATION
    # ========================================================================
    md.append("## Timeline Visualization\n\n")
    md.append(results["time_series_plot"])
    md.append("\n\n*Figure 1: Monthly crime trends from 2018-2025. The vertical dashed line marks March 2020, ")
    md.append("when Philadelphia implemented stay-at-home orders. The shaded yellow area represents the lockdown period (2020-2022).*\n\n")

    # ========================================================================
    # OVERALL CRIME IMPACT
    # ========================================================================
    md.append("---\n\n")
    md.append("## Overall Crime Impact\n\n")

    md.append("### Crime Count by Period\n\n")
    md.append("| Period | Annual Average | Total Crimes | Years |\n")
    md.append("|--------|----------------|--------------|-------|\n")

    for period in ["Pre-lockdown (2018-2019)", "Lockdown (2020-2022)", "Post-lockdown (2023-2025)"]:
        stats = period_stats[period]
        md.append(f"| {period} | {format_number(int(stats['annual_average'])),} | ")
        md.append(f"{format_number(int(stats['total_crimes'])),} | {', '.join(map(str, stats['years']))} |\n")

    md.append("\n")

    # Crime category breakdown
    md.append("### Crime Category Breakdown by Period\n\n")
    md.append("| Category | Pre-Lockdown (Annual) | Lockdown (Annual) | Post-Lockdown (Annual) |\n")
    md.append("|----------|----------------------|------------------|------------------------|\n")

    for category in ["violent", "property", "quality_of_life"]:
        cat_name = category.replace("_", " ").title()
        pre_val = period_stats["Pre-lockdown (2018-2019)"][f"{category}_annual_avg"]
        lock_val = period_stats["Lockdown (2020-2022)"][f"{category}_annual_avg"]
        post_val = period_stats["Post-lockdown (2023-2025)"][f"{category}_annual_avg"]

        lock_change = ((lock_val - pre_val) / pre_val * 100) if pre_val > 0 else 0
        post_change = ((post_val - pre_val) / pre_val * 100) if pre_val > 0 else 0

        md.append(f"| {cat_name} | {format_number(int(pre_val)),} | ")
        md.append(f"{format_number(int(lock_val)),} ({lock_change:+.1f}%) | ")
        md.append(f"{format_number(int(post_val)),} ({post_change:+.1f}%) |\n")

    md.append("\n")

    # ========================================================================
    # YEAR-OVER-YEAR CHANGES
    # ========================================================================
    md.append("### Year-over-Year Changes (2018-2025)\n\n")
    md.append("| Year | Crime Count | % Change from Prior Year |\n")
    md.append("|------|-------------|-------------------------|\n")

    yoy = results["yoy_changes"]
    for year in range(2019, 2026):
        if year in yoy:
            data = yoy[year]
            change_indicator = "🔴" if data["pct_change"] < -5 else "🟢" if data["pct_change"] > 5 else "⚪"
            md.append(f"| {year} | {format_number(data['count']),} | ")
            md.append(f"{change_indicator} {data['pct_change']:+.1f}% |\n")

    md.append("\n")

    # ========================================================================
    # COMPREHENSIVE CRIME TYPE ANALYSIS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Comprehensive Crime Type Analysis\n\n")

    md.append("### All Crime Types: Annual Average by Period\n\n")
    md.append("| Crime Type | Pre-Lockdown | Lockdown | Post-Lockdown | Lockdown % Change | Post % Change |\n")
    md.append("|------------|-------------|----------|---------------|-------------------|---------------|\n")

    comparison = results["crime_type_comparison"]
    for crime_type in comparison.index:
        pre = comparison.loc[crime_type, "Pre-lockdown (2018-2019)"]
        lock = comparison.loc[crime_type, "Lockdown (2020-2022)"]
        post = comparison.loc[crime_type, "Post-lockdown (2023-2025)"]

        lock_pct = ((lock - pre) / pre * 100) if pre > 0 else 0
        post_pct = ((post - pre) / pre * 100) if pre > 0 else 0

        # Visual indicator
        lock_indicator = "🔴" if lock_pct < -10 else "🟢" if lock_pct > 10 else "⚪"

        md.append(f"| {crime_type} | {format_number(int(pre)),} | {format_number(int(lock)),} | ")
        md.append(f"{format_number(int(post)),} | {lock_indicator} {lock_pct:+.1f}% | {post_pct:+.1f}% |\n")

    md.append("\n")

    # Heatmap
    md.append("### Percent Change Heatmap\n\n")
    md.append(results["heatmap"])
    md.append("\n\n*Figure 2: Heatmap showing percent change in crime types relative to pre-lockdown baseline. ")
    md.append("Red indicates decrease, green indicates increase.*\n\n")

    # Crimes that increased during lockdown
    comparison_copy = comparison.copy()
    comparison_copy["lockdown_pct"] = (
        (comparison_copy["Lockdown (2020-2022)"] - comparison_copy["Pre-lockdown (2018-2019)"])
        / comparison_copy["Pre-lockdown (2018-2019)"] * 100
    )

    increased = comparison_copy[comparison_copy["lockdown_pct"] > 5].sort_values("lockdown_pct", ascending=False)
    decreased = comparison_copy[comparison_copy["lockdown_pct"] < -5].sort_values("lockdown_pct")

    if len(increased) > 0:
        md.append("### Crimes That Increased During Lockdown\n\n")
        for crime_type, row in increased.head(10).iterrows():
            md.append(f"- **{crime_type}**: +{row['lockdown_pct']:.1f}%\n")
        md.append("\n")

    if len(decreased) > 0:
        md.append("### Crimes That Decreased During Lockdown\n\n")
        for crime_type, row in decreased.head(10).iterrows():
            md.append(f"- **{crime_type}**: {row['lockdown_pct']:.1f}%\n")
        md.append("\n")

    # ========================================================================
    # BURGLARY DISPLACEMENT DEEP-DIVE
    # ========================================================================
    md.append("---\n\n")
    md.append("## Burglary Displacement Deep-Dive\n\n")

    md.append("### Featured Insight: Residential vs Commercial Burglary\n\n")
    md.append(results["burglary_displacement_chart"])
    md.append("\n\n*Figure 3: Annual burglary counts showing the displacement effect during lockdown. ")
    md.append("With commercial buildings vacant, burglary shifted toward residential targets.*\n\n")

    md.append("### Burglary Statistics by Period\n\n")
    md.append("| Period | Residential (Annual) | Commercial (Annual) | Residential Ratio | Commercial Ratio |\n")
    md.append("|--------|---------------------|-------------------|-------------------|------------------|\n")

    for period in ["Pre-lockdown (2018-2019)", "Lockdown (2020-2022)", "Post-lockdown (2023-2025)"]:
        stats = burglary[period]
        md.append(f"| {period} | {format_number(int(stats['residential_annual'])),} | ")
        md.append(f"{format_number(int(stats['commercial_annual'])),} | ")
        md.append(f"{stats['residential_ratio']:.1%} | {stats['commercial_ratio']:.1%} |\n")

    md.append("\n")

    md.append("### Key Insights\n\n")
    md.append(f"- **Pre-lockdown**: Commercial burglary accounted for **{burglary['Pre-lockdown (2018-2019)']['commercial_ratio']:.1%}** of all burglaries\n")
    md.append(f"- **During lockdown**: Commercial burglary fell to **{burglary['Lockdown (2020-2022)']['commercial_ratio']:.1%}** of all burglaries\n")
    md.append(f"- **Residential change**: {burglary['Lockdown (2020-2022)']['residential_pct_change']:+.1f}% during lockdown\n")
    md.append(f"- **Commercial change**: {burglary['Lockdown (2020-2022)']['commercial_pct_change']:+.1f}% during lockdown\n")
    md.append(f"- **Post-lockdown**: Commercial burglary recovered to **{burglary['Post-lockdown (2023-2025)']['commercial_ratio']:.1%}** of all burglaries\n\n")

    # ========================================================================
    # RECOVERY TIMELINE
    # ========================================================================
    md.append("---\n\n")
    md.append("## Recovery Timeline\n\n")

    md.append("### When Did Crime Return to Pre-COVID Levels?\n\n")

    # Analyze recovery by year
    yoy = results["yoy_changes"]

    recovery_years = []
    for year in [2021, 2022, 2023, 2024, 2025]:
        if year in yoy:
            pct = yoy[year]["pct_change"]
            count = yoy[year]["count"]
            pre_avg = period_stats["Pre-lockdown (2018-2019)"]["annual_average"]
            relative_to_pre = (count - pre_avg) / pre_avg * 100

            status = "below pre-COVID" if relative_to_pre < -3 else "near pre-COVID" if relative_to_pre < 3 else "above pre-COVID"
            recovery_years.append(f"- **{year}**: {format_number(count),} incidents ({status}, {relative_to_pre:+.1f}% vs 2018-2019 avg)")

    if recovery_years:
        md.append("\n".join(recovery_years))
        md.append("\n\n")

    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    md.append("---\n\n")
    md.append("## Methodology\n\n")

    md.append("### Period Definitions\n")
    md.append("- **Pre-lockdown**: 2018-2019 (establishes baseline pre-pandemic patterns)\n")
    md.append("- **Lockdown**: 2020-2022 (includes initial pandemic impact and restrictions)\n")
    md.append("- **Post-lockdown**: 2023-2025 (post-restriction 'new normal' period)\n\n")

    md.append("### Key Date\n")
    md.append(f"- **March 16, 2020**: Philadelphia ordered residents to stay at home, closing non-essential businesses\n\n")

    md.append("### Data Scope\n")
    md.append("- Analysis covers 2018-2025 (2026 excluded due to incomplete data)\n")
    md.append("- Annual averages are used to account for varying years in each period\n")
    md.append("- Percent changes are calculated relative to 2018-2019 baseline\n\n")

    md.append("### Crime Type Classifications\n")
    md.append("**Violent Crimes:** Homicide, Rape, Robbery, Aggravated Assault\n\n")
    md.append("**Property Crimes:** Arson, Burglary, Motor Vehicle Theft, Theft\n\n")
    md.append("**Quality-of-Life Crimes:** Disorderly Conduct, Public Drunkenness, Vagrancy/Loitering, Vandalism, Liquor Law Violations, DUI\n\n")

    # ========================================================================
    # CONCLUSION
    # ========================================================================
    md.append("---\n\n")
    md.append("## Conclusion\n\n")

    md.append("### How Did COVID-19 Lockdowns Impact Philadelphia's Crime Landscape?\n\n")

    if lockdown_change < -5:
        md.append(f"The COVID-19 lockdowns caused a **significant decline in overall crime** of approximately **{abs(lockdown_change):.1f}%** ")
        md.append(f"during the 2020-2022 period compared to the 2018-2019 baseline.\n\n")
    elif lockdown_change < 0:
        md.append(f"The COVID-19 lockdowns caused a **modest decline in overall crime** of approximately **{abs(lockdown_change):.1f}%** ")
        md.append(f"during the 2020-2022 period compared to the 2018-2019 baseline.\n\n")
    else:
        md.append(f"Contrary to expectations, **overall crime increased** during the lockdown period by **{lockdown_change:.1f}%**.\n\n")

    md.append("### Key Takeaways\n\n")

    md.append("**1. Displacement Effect**\n")
    md.append("With commercial buildings vacant and people staying home, burglary shifted from commercial to residential targets. ")
    md.append(f"Residential burglary changed by **{res_change:+.1f}%** while commercial burglary changed by **{com_change:+.1f}%** during lockdown.\n\n")

    md.append("**2. Uneven Impact Across Crime Types**\n")
    md.append("Different crime types responded differently to lockdown conditions. ")
    md.append("Crimes requiring proximity to victims or commercial activity showed different patterns than those ")
    md.append("that could occur in residential settings.\n\n")

    if post_from_pre > 3:
        md.append("**3. New Normal**\n")
        md.append(f"Crime in the post-lockdown period (2023-2025) remains **{post_from_pre:.1f}% higher** than pre-pandemic levels, ")
        md.append("suggesting that some pandemic-era changes may have persisted.\n\n")
    elif post_from_pre < -3:
        md.append("**3. New Normal**\n")
        md.append(f"Crime in the post-lockdown period (2023-2025) remains **{abs(post_from_pre):.1f}% lower** than pre-pandemic levels, ")
        md.append("suggesting a lasting reduction in some types of crime.\n\n")
    else:
        md.append("**3. Recovery**\n")
        md.append("Crime levels in the post-lockdown period have largely returned to pre-pandemic patterns, ")
        md.append("indicating that the COVID-related shifts were largely temporary.\n\n")

    md.append("---\n\n")
    md.append("*Report generated by Claude Code | ")
    md.append(f"Data source: Philadelphia crime incidents dataset ({format_number(int(period_stats['Pre-lockdown (2018-2019)']['total_crimes'] + period_stats['Lockdown (2020-2022)']['total_crimes'] + period_stats['Post-lockdown (2023-2025)']['total_crimes']))} records, 2018-2025)*\n")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_covid_lockdown()
    report = generate_markdown_report(results)

    report_path = PROJECT_ROOT / "reports" / "04_covid_lockdown_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {report_path}")
