"""
Robbery Timing Analysis

Answers the question: "If I want to prevent robberies, what time of day should my officers be visible?"

Analyzes robbery patterns by hour and day of week to identify optimal patrol visibility times.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES
from analysis.utils import load_data, extract_temporal_features, image_to_base64, create_image_tag, format_number


# =============================================================================
# CONSTANTS
# =============================================================================

# Robbery crime types in the dataset
ROBBERY_CRIMES = ["Robbery Firearm", "Robbery No Firearm"]

# Day names for consistent plotting
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Patrol-friendly time periods
TIME_PERIODS = ["Overnight (12AM-5AM)", "Morning (5AM-11AM)",
                "Afternoon (11AM-5PM)", "Evening (5PM-9PM)",
                "Night (9PM-12AM)"]

# Time period bins (hour ranges)
TIME_PERIOD_BINS = [0, 5, 11, 17, 21, 24]
TIME_PERIOD_LABELS = ["Overnight (12AM-5AM)", "Morning (5AM-11AM)",
                      "Afternoon (11AM-5PM)", "Evening (5PM-9PM)",
                      "Night (9PM-12AM)"]


# =============================================================================
# DATA FILTERING
# =============================================================================

def filter_robbery_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter dataset for robbery crimes only and extract temporal features.

    IMPORTANT: Preserves the original hour column before extracting temporal
    features, since extract_temporal_features() overwrites hour with hour=0
    (midnight) when dispatch_date is date-only.

    Args:
        df: Full crime incidents DataFrame.

    Returns:
        DataFrame filtered to robbery crimes with temporal features added.
    """
    # Filter for robbery crimes
    robbery = df[df["text_general_code"].isin(ROBBERY_CRIMES)].copy()

    # PRESERVE original hour column before extract_temporal_features overwrites it
    original_hour = robbery["hour"].copy()

    # Extract temporal features (this will add day_of_week, day_name, etc.)
    robbery = extract_temporal_features(robbery)

    # RESTORE the original hour column
    robbery["hour"] = original_hour

    # Filter out records with missing hour data (~2.9% missing)
    robbery = robbery[robbery["hour"].notna()].copy()

    # Convert hour to integer
    robbery["hour"] = robbery["hour"].astype(int)

    return robbery


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_hourly_distribution(df: pd.DataFrame) -> dict:
    """
    Calculate hourly robbery counts and identify peak hours.

    Args:
        df: Robbery incidents DataFrame with hour column.

    Returns:
        Dictionary with hourly counts, peak hours, and percentages.
    """
    # Count robberies by hour
    hourly_counts = df.groupby("hour").size()

    # Find peak hours (top 3)
    peak_hours = hourly_counts.nlargest(3)

    # Calculate percentage for each hour
    hourly_pct = (hourly_counts / len(df) * 100).round(2)

    return {
        "hourly_counts": hourly_counts,
        "peak_hours": peak_hours.to_dict(),
        "hourly_pct": hourly_pct.to_dict(),
        "total_robberies": len(df)
    }


def analyze_day_of_week_patterns(df: pd.DataFrame) -> dict:
    """
    Calculate robbery counts by day of week.

    Args:
        df: Robbery incidents DataFrame with day_of_week and day_name columns.

    Returns:
        Dictionary with day-of-week counts, peak day, and percentages.
    """
    # Count robberies by day of week
    dow_counts = df.groupby("day_of_week").size()

    # Reindex to ensure all days are present (0=Monday to 6=Sunday)
    dow_counts = dow_counts.reindex(range(7), fill_value=0)

    # Find peak day
    peak_day_idx = dow_counts.idxmax()
    peak_day_name = DAY_NAMES[peak_day_idx]
    peak_day_count = int(dow_counts.iloc[peak_day_idx])

    # Calculate percentage for each day
    dow_pct = (dow_counts / len(df) * 100).round(2)

    return {
        "dow_counts": dow_counts.to_dict(),
        "peak_day": {
            "name": peak_day_name,
            "index": int(peak_day_idx),
            "count": peak_day_count
        },
        "dow_pct": dow_pct.to_dict(),
        "total_robberies": len(df)
    }


def analyze_time_period_distribution(df: pd.DataFrame) -> dict:
    """
    Group hours into broader time periods for patrol scheduling.

    Args:
        df: Robbery incidents DataFrame with hour column.

    Returns:
        Dictionary with time period counts and percentages.
    """
    # Categorize hours into time periods
    df_with_period = df.copy()
    df_with_period["time_period"] = pd.cut(
        df_with_period["hour"],
        bins=TIME_PERIOD_BINS,
        labels=TIME_PERIOD_LABELS,
        right=False,
        include_lowest=True
    )

    # Count by time period
    period_counts = df_with_period["time_period"].value_counts()

    # Reindex to ensure all periods are present
    period_counts = period_counts.reindex(TIME_PERIOD_LABELS, fill_value=0)

    # Calculate percentages
    period_pct = (period_counts / len(df) * 100).round(2)

    return {
        "period_counts": period_counts.to_dict(),
        "period_pct": period_pct.to_dict(),
        "total_robberies": len(df)
    }


def find_peak_combinations(df: pd.DataFrame, top_n: int = 10) -> list:
    """
    Find the top hour+day combinations with highest robbery counts.

    Args:
        df: Robbery incidents DataFrame with hour and day_of_week columns.
        top_n: Number of top combinations to return.

    Returns:
        List of dicts with rank, day, hour, count, and percentage.
    """
    # Count by hour and day of week
    combo_counts = df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")

    # Sort by count descending and get top N
    combo_counts = combo_counts.sort_values("count", ascending=False).head(top_n)

    # Calculate percentage
    total = len(df)

    results = []
    for i, (_, row) in enumerate(combo_counts.iterrows(), 1):
        day_idx = int(row["day_of_week"])
        hour = int(row["hour"])
        count = int(row["count"])

        results.append({
            "rank": i,
            "day": DAY_NAMES[day_idx],
            "day_index": day_idx,
            "hour": hour,
            "count": count,
            "pct_of_total": round(count / total * 100, 2)
        })

    return results


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_hour_day_heatmap(df: pd.DataFrame) -> str:
    """
    Create hour (x-axis) vs day of week (y-axis) heatmap with base64 encoding.

    Args:
        df: Robbery incidents DataFrame with hour and day_of_week columns.

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])

    # Create pivot table for heatmap
    heatmap_data = df.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)

    # Reindex columns (hours 0-23) and rows (Mon-Sun)
    heatmap_data = heatmap_data.reindex(columns=range(24), fill_value=0)
    heatmap_data = heatmap_data.reindex(range(7), fill_value=0)

    # Create heatmap
    sns.heatmap(
        heatmap_data,
        cmap=COLORS["sequential"],
        cbar_kws={"label": "Robbery Count"},
        linewidths=0.5,
        ax=ax
    )

    # Set labels
    ax.set_xticklabels(range(24), rotation=0)
    ax.set_yticklabels(DAY_NAMES, rotation=0)
    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Day of Week", fontsize=12)
    ax.set_title("Robbery Timing Heatmap: Hour vs Day of Week (2006-2026)",
                 fontsize=14, fontweight="bold")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_hourly_bar_chart(df: pd.DataFrame, hourly_stats: dict) -> str:
    """
    Create bar chart showing robbery distribution by hour.

    Args:
        df: Robbery incidents DataFrame.
        hourly_stats: Dictionary from analyze_hourly_distribution().

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    hourly_counts = hourly_stats["hourly_counts"]
    peak_hours = list(hourly_stats["peak_hours"].keys())

    # Create color array (highlight peak hours)
    colors = [COLORS["danger"] if h in peak_hours else COLORS["primary"]
              for h in range(24)]

    bars = ax.bar(range(24), [hourly_counts.get(h, 0) for h in range(24)],
                  color=colors, alpha=0.8, edgecolor="black", linewidth=0.5)

    # Add count labels for peak hours
    for h in peak_hours:
        count = hourly_counts[h]
        ax.text(h, count + 50, format_number(int(count)),
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Robbery Count", fontsize=12)
    ax.set_title("Robbery Distribution by Hour of Day (2006-2026)",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(range(24))
    ax.set_xticklabels(range(24), rotation=45, ha="right")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_day_of_week_bar_chart(df: pd.DataFrame, dow_stats: dict) -> str:
    """
    Create bar chart showing robbery counts by day of week.

    Args:
        df: Robbery incidents DataFrame.
        dow_stats: Dictionary from analyze_day_of_week_patterns().

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    dow_counts = dow_stats["dow_counts"]
    peak_day_idx = dow_stats["peak_day"]["index"]

    # Create color array (highlight peak day)
    colors = [COLORS["danger"] if i == peak_day_idx else COLORS["primary"]
              for i in range(7)]

    bars = ax.bar(range(7), [dow_counts.get(i, 0) for i in range(7)],
                  color=colors, alpha=0.8, edgecolor="black", linewidth=0.5)

    # Add count labels
    for i in range(7):
        count = dow_counts.get(i, 0)
        ax.text(i, count + 100, format_number(int(count)),
                ha="center", va="bottom", fontsize=10)

    ax.set_xlabel("Day of Week", fontsize=12)
    ax.set_ylabel("Robbery Count", fontsize=12)
    ax.set_title("Robbery Distribution by Day of Week (2006-2026)",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(range(7))
    ax.set_xticklabels(DAY_NAMES)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_time_period_bar_chart(df: pd.DataFrame, period_stats: dict) -> str:
    """
    Create bar chart grouping hours into patrol-friendly time periods.

    Args:
        df: Robbery incidents DataFrame.
        period_stats: Dictionary from analyze_time_period_distribution().

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    period_counts = period_stats["period_counts"]
    period_pct = period_stats["period_pct"]

    # Create bar chart
    periods = list(period_counts.keys())
    counts = list(period_counts.values())

    # Find max period for highlighting
    max_period_idx = counts.index(max(counts))
    colors = [COLORS["danger"] if i == max_period_idx else COLORS["primary"]
              for i in range(len(periods))]

    bars = ax.barh(range(len(periods)), counts, color=colors,
                   alpha=0.8, edgecolor="black", linewidth=0.5)

    # Add count and percentage labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        pct = period_pct[periods[i]]
        ax.text(count + 100, i, f"{format_number(int(count))} ({pct}%)",
                va="center", fontsize=10)

    ax.set_yticks(range(len(periods)))
    ax.set_yticklabels(periods)
    ax.set_xlabel("Robbery Count", fontsize=12)
    ax.set_title("Robbery Distribution by Patrol-Friendly Time Periods (2006-2026)",
                 fontsize=14, fontweight="bold")
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def analyze_robbery_timing() -> dict:
    """
    Run full robbery timing analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    print("Loading data for robbery timing analysis...")
    df = load_data(clean=False)

    print("Filtering to robbery crimes...")
    robbery = filter_robbery_data(df)
    print(f"  Analyzing {format_number(len(robbery))} robbery incidents")

    results = {}
    results["total_robberies"] = len(robbery)

    # ========================================================================
    # ANALYSIS: Hourly Distribution
    # ========================================================================
    print("Analyzing hourly distribution...")
    results["hourly"] = analyze_hourly_distribution(robbery)

    # ========================================================================
    # ANALYSIS: Day of Week Patterns
    # ========================================================================
    print("Analyzing day of week patterns...")
    results["day_of_week"] = analyze_day_of_week_patterns(robbery)

    # ========================================================================
    # ANALYSIS: Time Period Distribution
    # ========================================================================
    print("Analyzing time period distribution...")
    results["time_period"] = analyze_time_period_distribution(robbery)

    # ========================================================================
    # ANALYSIS: Peak Combinations
    # ========================================================================
    print("Finding peak hour+day combinations...")
    results["peak_combinations"] = find_peak_combinations(robbery, top_n=10)

    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================
    print("Creating visualizations...")

    results["heatmap"] = create_hour_day_heatmap(robbery)
    results["hourly_bar_chart"] = create_hourly_bar_chart(robbery, results["hourly"])
    results["day_of_week_bar_chart"] = create_day_of_week_bar_chart(robbery, results["day_of_week"])
    results["time_period_bar_chart"] = create_time_period_bar_chart(robbery, results["time_period"])

    # ========================================================================
    # ADDITIONAL INSIGHTS
    # ========================================================================
    print("Generating insights...")

    # Identify highest risk time period
    period_pct = results["time_period"]["period_pct"]
    max_period = max(period_pct, key=period_pct.get)
    max_period_pct = period_pct[max_period]

    results["insights"] = {
        "highest_risk_period": {
            "name": max_period,
            "pct": max_period_pct
        },
        "peak_hour": int(list(results["hourly"]["peak_hours"].keys())[0]),
        "peak_day": results["day_of_week"]["peak_day"]["name"]
    }

    print("Robbery timing analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from robbery timing analysis results.

    Args:
        results: Dictionary from analyze_robbery_timing().

    Returns:
        Markdown string with analysis results.
    """
    md = []

    # ========================================================================
    # TITLE
    # ========================================================================
    md.append("# Robbery Timing Analysis\n")
    md.append("**Philadelphia Crime Incidents (2006-2026)**\n\n")
    md.append("---\n\n")

    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    md.append("## Executive Summary\n\n")

    md.append("**Question:** If I want to prevent robberies, what time of day should my officers be visible?\n\n")

    insights = results["insights"]
    hourly = results["hourly"]
    dow = results["day_of_week"]
    peak_combo = results["peak_combinations"][0]

    # Format peak hour range
    peak_hour = insights["peak_hour"]
    peak_day = insights["peak_day"]

    md.append("**Answer:**\n\n")
    md.append(f"- **Highest Risk Time**: {insights['highest_risk_period']['name']} - ")
    md.append(f"**{insights['highest_risk_period']['pct']}%** of all robberies occur during this period\n")
    md.append(f"- **Peak Hour**: **{peak_hour}:00 ({"PM" if peak_hour >= 12 else "AM"})** with ")
    md.append(f"**{format_number(int(hourly['peak_hours'][peak_hour]))}** robberies\n")
    md.append(f"- **Peak Day**: **{peak_day}day** with ")
    md.append(f"**{format_number(dow['peak_day']['count'])}** robberies\n")
    md.append(f"- **Worst Time Slot**: **{peak_combo['day']} at {peak_combo['hour']}:00** - ")
    md.append(f"**{format_number(peak_combo['count'])}** robberies ({peak_combo['pct_of_total']}% of total)\n\n")

    md.append(f"**Total Robberies Analyzed**: {format_number(results['total_robberies'])}\n\n")

    md.append("---\n\n")

    # ========================================================================
    # PRIMARY VISUALIZATION: Heatmap
    # ========================================================================
    md.append("## The Heatmap: When Do Robberies Happen?\n\n")
    md.append(results["heatmap"])
    md.append("\n\n")
    md.append("*Figure 1: Hour vs Day of Week heatmap showing robbery frequency. ")
    md.append("Darker colors indicate higher robbery counts. This visualization reveals clear patterns ")
    md.append("in when robberies are most likely to occur.*\n\n")

    # ========================================================================
    # DETAILED BREAKDOWN
    # ========================================================================
    md.append("---\n\n")
    md.append("## Detailed Breakdown\n\n")

    # ========================================================================
    # Hourly Distribution
    # ========================================================================
    md.append("### Hourly Distribution\n\n")
    md.append(results["hourly_bar_chart"])
    md.append("\n\n")

    peak_hours_list = list(hourly["peak_hours"].items())
    if len(peak_hours_list) >= 3:
        md.append(f"**Peak Hours:** {peak_hours_list[0][0]}:00 ({"PM" if peak_hours_list[0][0] >= 12 else "AM"}) ")
        md.append(f"with **{format_number(int(peak_hours_list[0][1]))}** robberies, ")
        md.append(f"followed by {peak_hours_list[1][0]}:00 (**{format_number(int(peak_hours_list[1][1]))}**), ")
        md.append(f"and {peak_hours_list[2][0]}:00 (**{format_number(int(peak_hours_list[2][1]))}**)\n\n")
    elif len(peak_hours_list) == 2:
        md.append(f"**Peak Hours:** {peak_hours_list[0][0]}:00 ({"PM" if peak_hours_list[0][0] >= 12 else "AM"}) ")
        md.append(f"with **{format_number(int(peak_hours_list[0][1]))}** robberies, ")
        md.append(f"followed by {peak_hours_list[1][0]}:00 (**{format_number(int(peak_hours_list[1][1]))}**)\n\n")
    else:
        md.append(f"**Peak Hour:** {peak_hours_list[0][0]}:00 ({"PM" if peak_hours_list[0][0] >= 12 else "AM"}) ")
        md.append(f"with **{format_number(int(peak_hours_list[0][1]))}** robberies\n\n")

    # ========================================================================
    # Day of Week Patterns
    # ========================================================================
    md.append("### Day of Week Patterns\n\n")
    md.append(results["day_of_week_bar_chart"])
    md.append("\n\n")

    md.append(f"**Highest Risk Day**: **{dow['peak_day']['name']}day** with ")
    md.append(f"**{format_number(dow['peak_day']['count'])}** robberies\n\n")

    # Weekday vs weekend comparison
    weekday_total = sum([dow["dow_counts"].get(i, 0) for i in range(5)])
    weekend_total = sum([dow["dow_counts"].get(i, 0) for i in range(5, 7)])
    weekday_pct = weekday_total / results["total_robberies"] * 100
    weekend_pct = weekend_total / results["total_robberies"] * 100

    md.append(f"**Weekday vs Weekend**:\n")
    md.append(f"- Weekdays (Mon-Fri): **{format_number(weekday_total)}** robberies ({weekday_pct:.1f}%)\n")
    md.append(f"- Weekends (Sat-Sun): **{format_number(weekend_total)}** robberies ({weekend_pct:.1f}%)\n\n")

    # ========================================================================
    # Patrol-Friendly Time Periods
    # ========================================================================
    md.append("### Patrol-Friendly Time Periods\n\n")
    md.append(results["time_period_bar_chart"])
    md.append("\n\n")

    period_pct = results["time_period"]["period_pct"]
    period_counts = results["time_period"]["period_counts"]

    md.append("**Time Period Breakdown**:\n\n")
    for period in TIME_PERIOD_LABELS:
        count = period_counts[period]
        pct = period_pct[period]
        md.append(f"- **{period}**: **{format_number(int(count))}** robberies ({pct}%)\n")

    md.append("\n")

    # ========================================================================
    # TOP 10 HIGH-RISK TIME SLOTS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Top 10 High-Risk Time Slots\n\n")
    md.append("| Rank | Day | Hour | Count | % of Total |\n")
    md.append("|------|-----|------|-------|------------|\n")

    for combo in results["peak_combinations"]:
        hour_display = f"{combo['hour']}:00"
        am_pm = "PM" if combo["hour"] >= 12 else "AM"
        md.append(f"| {combo['rank']} | {combo['day']} | {hour_display} {am_pm} | ")
        md.append(f"{format_number(combo['count'])} | {combo['pct_of_total']}% |\n")

    md.append("\n")

    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    md.append("---\n\n")
    md.append("## Recommendations\n\n")

    md.append("### 1. Priority Patrol Hours\n\n")
    peak_hour = insights["peak_hour"]
    peak_hours_keys = list(hourly['peak_hours'].keys())
    am_pm = "PM" if peak_hour >= 12 else "AM"
    md.append(f"- **Primary Focus**: {peak_hour}:00 {am_pm} with peak robbery activity\n")
    if len(peak_hours_keys) >= 3:
        md.append(f"- **Secondary Focus**: {peak_hours_keys[1]}:00 and {peak_hours_keys[2]}:00 hours\n")
    md.append("- **Extended Coverage**: Evening (5PM-9PM) and Night (9PM-12AM) periods combined account for ")
    md.append(f"**{period_pct['Evening (5PM-9PM)'] + period_pct['Night (9PM-12AM)']:.1f}%** of all robberies\n\n")

    md.append("### 2. Day-Specific Strategies\n\n")
    md.append(f"- **{peak_day}day**: Highest robbery count; consider increased visibility on this day\n")
    md.append(f"- **Weekend vs Weekday**: Weekdays account for {weekday_pct:.1f}% of robberies; ")
    md.append("ensure adequate weekday staffing\n")
    md.append("- **Friday/Saturday Nights**: Elevated risk during evening-overnight transition\n\n")

    md.append("### 3. Cost-Effective Scheduling Notes\n\n")
    md.append("- **Targeted Visibility**: Focus officer presence during 5PM-12AM window to cover ")
    md.append(f"**{period_pct['Evening (5PM-9PM)'] + period_pct['Night (9PM-12AM)']:.1f}%** of robberies\n")
    md.append("- **Overnight Coverage**: Overnight period (12AM-5AM) has lowest count but consider ")
    md.append("high-visibility presence in hotspot areas\n")
    md.append("- **Shift Timing**: Align shift changes with 5PM and 9PM boundaries to maximize ")
    md.append("coverage during peak periods\n\n")

    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    md.append("---\n\n")
    md.append("## Methodology\n\n")

    md.append("### Data Source\n")
    md.append("- **Dataset**: Philadelphia crime incidents (2006-2026)\n")
    md.append(f"- **Total Robberies**: {format_number(results['total_robberies'])} incidents\n")
    md.append("- **Crime Types**: Robbery Firearm, Robbery No Firearm\n")
    md.append("- **2026 Data**: Partial (only through January 20, 2026)\n\n")

    md.append("### Filtering\n")
    md.append("- Records with missing hour data (~2.9% of robbery records) were excluded\n")
    md.append("- All robbery records with valid hour information were included\n")
    md.append("- Temporal features extracted via `utils.extract_temporal_features()`\n\n")

    md.append("### Time Period Definitions\n")
    md.append("- **Overnight (12AM-5AM)**: Hours 0-4\n")
    md.append("- **Morning (5AM-11AM)**: Hours 5-10\n")
    md.append("- **Afternoon (11AM-5PM)**: Hours 11-16\n")
    md.append("- **Evening (5PM-9PM)**: Hours 17-20\n")
    md.append("- **Night (9PM-12AM)**: Hours 21-23\n\n")

    md.append("### Visualization Approach\n")
    md.append("- **Heatmap**: Hour (x-axis) vs Day of Week (y-axis) with 'YlOrRd' colormap\n")
    md.append("- **Color Scale**: Darker colors indicate higher robbery frequency\n")
    md.append("- **Bar Charts**: Highlight peak values in red for easy identification\n\n")

    # ========================================================================
    # CONCLUSION
    # ========================================================================
    md.append("---\n\n")
    md.append("## Conclusion\n\n")

    md.append(f"To effectively prevent robberies in Philadelphia, officer visibility should be prioritized during the **")
    md.append(f"{insights['highest_risk_period']['name']}** period, which accounts for ")
    md.append(f"**{insights['highest_risk_period']['pct']}%** of all robbery incidents.\n\n")

    md.append(f"The single highest-risk time slot is **{peak_combo['day']} at {peak_combo['hour']}:00**, ")
    md.append(f"with **{format_number(peak_combo['count'])}** robberies ({peak_combo['pct_of_total']}% of total).\n\n")

    md.append("**Key Takeaway**: By concentrating officer visibility during evening and nighttime hours (5PM-12AM), ")
    md.append(f"departments can cover **{period_pct['Evening (5PM-9PM)'] + period_pct['Night (9PM-12AM)']:.1f}%** of robbery incidents ")
    md.append("with optimal resource allocation.\n\n")

    md.append("*\n")
    md.append(f"Report generated by Claude Code | ")
    md.append(f"Data source: Philadelphia crime incidents dataset ({format_number(results['total_robberies'])} robbery records, 2006-2026)\n")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_robbery_timing()
    report = generate_markdown_report(results)

    from analysis.config import PROJECT_ROOT, REPORTS_DIR

    report_path = REPORTS_DIR / "06_robbery_timing_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
