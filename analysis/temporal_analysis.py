"""
Phase 2: Temporal Analysis

Analyzes long-term trends, seasonal patterns, and cyclical patterns
in the crime data over time (2006-2026).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT
from analysis.utils import load_data, extract_temporal_features, image_to_base64, create_image_tag, format_number


def analyze_temporal_patterns() -> dict:
    """
    Run comprehensive temporal analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    print("Loading data for temporal analysis...")
    df = load_data(clean=False)

    print("Extracting temporal features...")
    df = extract_temporal_features(df)

    results = {}

    # ========================================================================
    # 1. Long-term Trend Analysis (Yearly)
    # ========================================================================
    print("Analyzing yearly trends...")

    yearly_counts = df.groupby("year").size().reset_index(name="count")
    results["yearly_counts"] = yearly_counts

    # Yearly trend plot
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    years = yearly_counts["year"]
    counts = yearly_counts["count"]

    # Exclude 2026 for trend line (incomplete year)
    complete_mask = years < 2026
    ax.bar(years, counts, color=COLORS["primary"], alpha=0.7, label="Annual Count")

    # Trend line for complete years
    if complete_mask.sum() > 2:
        z = np.polyfit(years[complete_mask], counts[complete_mask], 2)
        p = np.poly1d(z)
        trend_x = np.linspace(years[complete_mask].min(), years[complete_mask].max(), 100)
        ax.plot(trend_x, p(trend_x), "r--", linewidth=2, label="Trend (2nd order)")

    # Mark 2020 as COVID year
    ax.axvline(x=2020, color=COLORS["danger"], linestyle=":", linewidth=2, label="COVID-19 Pandemic")

    ax.set_xlabel("Year")
    ax.set_ylabel("Crime Count")
    ax.set_title("Philadelphia Crime Incidents by Year (2006-2026)")
    ax.legend()

    # Add value labels
    for i, (year, count) in enumerate(zip(years, counts)):
        ax.text(year, count, f" {format_number(count)}", rotation=45, fontsize=8, va="bottom")

    plt.tight_layout()
    results["yearly_trend_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Year-over-year change
    yearly_counts["yoy_change"] = yearly_counts["count"].pct_change() * 100
    yearly_counts["yoy_change_abs"] = yearly_counts["count"].diff()

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    complete_years = yearly_counts[yearly_counts["year"] < 2026]
    bars = ax.bar(complete_years["year"], complete_years["yoy_change"],
                   color=[COLORS["success"] if x >= 0 else COLORS["danger"] for x in complete_years["yoy_change"]])
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_xlabel("Year")
    ax.set_ylabel("Year-over-Year Change (%)")
    ax.set_title("Year-over-Year Percentage Change in Crime Incidents")

    for i, (year, change) in enumerate(zip(complete_years["year"], complete_years["yoy_change"])):
        if pd.notna(change):
            va = "bottom" if change >= 0 else "top"
            ax.text(year, change, f" {change:.1f}%", va=va, fontsize=8)

    plt.tight_layout()
    results["yoy_change_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 2. Monthly/Seasonal Patterns
    # ========================================================================
    print("Analyzing monthly patterns...")

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    monthly_counts = df.groupby("month").size().reset_index(name="count")
    monthly_counts["month_name"] = monthly_counts["month"].apply(lambda x: month_names[x-1])
    results["monthly_counts"] = monthly_counts

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    bars = ax.bar(monthly_counts["month_name"], monthly_counts["count"], color=COLORS["secondary"])
    ax.set_xlabel("Month")
    ax.set_ylabel("Crime Count")
    ax.set_title("Crime Incidents by Month (2006-2026)")
    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f" {format_number(int(height))}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    results["monthly_bar_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Seasonal distribution
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    seasonal_counts = df.groupby("season").size().reindex(season_order)

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])
    colors_season = [COLORS["success"], COLORS["danger"], COLORS["warning"], COLORS["primary"]]
    seasonal_counts.plot(kind="bar", ax=ax, color=colors_season)
    ax.set_xlabel("Season")
    ax.set_ylabel("Crime Count")
    ax.set_title("Crime Incidents by Season")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    for i, val in enumerate(seasonal_counts.values):
        ax.text(i, val, f" {format_number(val)}", va="bottom", fontsize=10)

    plt.tight_layout()
    results["seasonal_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 3. Day of Week Analysis
    # ========================================================================
    print("Analyzing day of week patterns...")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = df.groupby("day_name").size().reindex(day_order)
    results["dow_counts"] = dow_counts

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    bars = ax.bar(day_order, dow_counts.values, color=COLORS["primary"])
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Crime Count")
    ax.set_title("Crime Incidents by Day of Week")
    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f" {format_number(int(height))}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    results["dow_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Weekday vs Weekend comparison
    weekend_comparison = df.groupby("is_weekend").size()
    weekend_comparison.index = ["Weekday", "Weekend"]

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])
    weekend_comparison.plot(kind="bar", ax=ax, color=[COLORS["primary"], COLORS["secondary"]])
    ax.set_xlabel("Day Type")
    ax.set_ylabel("Crime Count")
    ax.set_title("Weekday vs Weekend Crime Comparison")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    for i, val in enumerate(weekend_comparison.values):
        ax.text(i, val, f" {format_number(val)}", va="bottom", fontsize=10)

    plt.tight_layout()
    results["weekend_comparison_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 4. Hour of Day Analysis
    # ========================================================================
    print("Analyzing hourly patterns...")

    hourly_counts = df.groupby("hour").size().reset_index(name="count")
    results["hourly_counts"] = hourly_counts

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    bars = ax.bar(hourly_counts["hour"], hourly_counts["count"], color=COLORS["secondary"])
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Crime Count")
    ax.set_title("Crime Incidents by Hour of Day")
    ax.set_xticks(range(0, 24, 2))

    # Highlight peak hours
    max_hour = hourly_counts.loc[hourly_counts["count"].idxmax()]
    min_hour = hourly_counts.loc[hourly_counts["count"].idxmin()]
    ax.bar(max_hour["hour"], max_hour["count"], color=COLORS["danger"], alpha=0.7, label=f"Peak: {int(max_hour['hour'])}:00")
    ax.bar(min_hour["hour"], min_hour["count"], color=COLORS["success"], alpha=0.7, label=f"Lowest: {int(min_hour['hour'])}:00")
    ax.legend()

    plt.tight_layout()
    results["hourly_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Time period analysis
    time_period_counts = df.groupby("time_period").size()

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])
    time_period_counts.plot(kind="bar", ax=ax, color=COLORS["secondary"])
    ax.set_xlabel("Time Period")
    ax.set_ylabel("Crime Count")
    ax.set_title("Crime Incidents by Time of Day")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")

    for i, val in enumerate(time_period_counts.values):
        ax.text(i, val, f" {format_number(val)}", va="bottom", fontsize=9)

    plt.tight_layout()
    results["time_period_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 5. Month × Year Heatmap
    # ========================================================================
    print("Creating month-year heatmap...")

    # Pivot for heatmap
    pivot_data = df.groupby(["year", "month"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    sns.heatmap(pivot_data, cmap=COLORS["sequential"], annot=False, ax=ax,
                cbar_kws={"label": "Incident Count"})
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.set_title("Monthly Crime Incidents Heatmap (2006-2026)")

    plt.tight_layout()
    results["month_year_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 6. Day of Week × Hour Heatmap
    # ========================================================================
    print("Creating day-hour heatmap...")

    pivot_dh = df.groupby(["day_name", "hour"]).size().unstack(fill_value=0)
    pivot_dh = pivot_dh.reindex(day_order)

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    sns.heatmap(pivot_dh, cmap=COLORS["sequential"], annot=False, ax=ax,
                cbar_kws={"label": "Incident Count"})
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")
    ax.set_title("Crime Incidents by Day and Hour")

    plt.tight_layout()
    results["day_hour_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 7. Time Series Statistics
    # ========================================================================
    print("Calculating time series statistics...")

    # Daily counts
    daily_counts = df.groupby("dispatch_datetime").size()

    ts_stats = {
        "mean_daily_incidents": float(daily_counts.mean()),
        "median_daily_incidents": float(daily_counts.median()),
        "std_daily_incidents": float(daily_counts.std()),
        "min_daily_incidents": int(daily_counts.min()),
        "max_daily_incidents": int(daily_counts.max()),
        "peak_date": str(daily_counts.idxmax().date()),
        "lowest_date": str(daily_counts.idxmin().date()),
    }
    results["time_series_stats"] = ts_stats

    print("Temporal analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from temporal analysis results.

    Args:
        results: Dictionary from analyze_temporal_patterns()

    Returns:
        Markdown string with analysis results.
    """
    md = []

    md.append("### Temporal Analysis\n")

    # Yearly Trends
    md.append("#### 1. Long-term Trends (2006-2026)\n\n")

    yearly_counts = results["yearly_counts"]
    peak_year = yearly_counts.loc[yearly_counts["count"].idxmax()]
    # Get complete years (before 2026)
    complete_years = yearly_counts[yearly_counts["year"] < 2026].copy()
    low_year = complete_years.loc[complete_years["count"].idxmin()]

    md.append(f"**Peak Year**: {peak_year['year']} with {format_number(peak_year['count'])} incidents\n")
    md.append(f"**Lowest Year**: {low_year['year']} with {format_number(low_year['count'])} incidents\n")
    md.append(f"**2026 Note**: Data is incomplete (only through January 20)\n\n")

    md.append(results["yearly_trend_plot"])
    md.append("\n")
    md.append(results["yoy_change_plot"])
    md.append("\n")

    # Monthly Patterns
    md.append("#### 2. Monthly and Seasonal Patterns\n\n")

    monthly_counts = results["monthly_counts"]
    peak_month = monthly_counts.loc[monthly_counts["count"].idxmax()]
    low_month = monthly_counts.loc[monthly_counts["count"].idxmin()]

    md.append(f"**Peak Month**: {peak_month['month_name']} with {format_number(peak_month['count'])} incidents\n")
    md.append(f"**Lowest Month**: {low_month['month_name']} with {format_number(low_month['count'])} incidents\n\n")

    md.append(results["monthly_bar_plot"])
    md.append("\n")
    md.append(results["seasonal_plot"])
    md.append("\n")

    # Day of Week
    md.append("#### 3. Day of Week Patterns\n\n")

    dow_counts = results["dow_counts"]
    peak_dow = dow_counts.idxmax()
    low_dow = dow_counts.idxmin()

    md.append(f"**Peak Day**: {peak_dow} with {format_number(dow_counts[peak_dow])} incidents\n")
    md.append(f"**Lowest Day**: {low_dow} with {format_number(dow_counts[low_dow])} incidents\n\n")

    md.append(results["dow_plot"])
    md.append("\n")
    md.append(results["weekend_comparison_plot"])
    md.append("\n")

    # Hourly Patterns
    md.append("#### 4. Hour of Day Patterns\n\n")

    hourly_counts = results["hourly_counts"]
    peak_hour = hourly_counts.loc[hourly_counts["count"].idxmax()]
    low_hour = hourly_counts.loc[hourly_counts["count"].idxmin()]

    md.append(f"**Peak Hour**: {int(peak_hour['hour'])}:00 with {format_number(peak_hour['count'])} incidents\n")
    md.append(f"**Lowest Hour**: {int(low_hour['hour'])}:00 with {format_number(low_hour['count'])} incidents\n\n")

    md.append(results["hourly_plot"])
    md.append("\n")
    md.append(results["time_period_plot"])
    md.append("\n")

    # Heatmaps
    md.append("#### 5. Temporal Heatmaps\n\n")
    md.append(results["month_year_heatmap"])
    md.append("\n")
    md.append(results["day_hour_heatmap"])
    md.append("\n")

    # Statistics
    md.append("#### 6. Time Series Statistics\n\n")

    ts_stats = results["time_series_stats"]
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Mean Daily Incidents | {ts_stats['mean_daily_incidents']:.1f} |")
    md.append(f"| Median Daily Incidents | {ts_stats['median_daily_incidents']:.1f} |")
    md.append(f"| Std Dev Daily Incidents | {ts_stats['std_daily_incidents']:.1f} |")
    md.append(f"| Maximum Daily Incidents | {format_number(ts_stats['max_daily_incidents'])} ({ts_stats['peak_date']}) |")
    md.append(f"| Minimum Daily Incidents | {format_number(ts_stats['min_daily_incidents'])} ({ts_stats['lowest_date']}) |")
    md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_temporal_patterns()
    report = generate_markdown_report(results)

    report_path = PROJECT_ROOT / "reports" / "02_temporal_analysis_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Temporal Analysis Report\n\n")
        f.write(report)

    print(f"\nReport saved to: {report_path}")
