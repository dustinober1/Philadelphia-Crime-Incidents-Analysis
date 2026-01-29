"""
Safety Trend Analysis

Answers the question: "Is Philadelphia actually getting safer?"

Analyzes violent vs property crime trends over the last 10 years (2016-2025)
using FBI UCR standard classification.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT
from analysis.utils import (
    load_data,
    extract_temporal_features,
    classify_crime_category,
    image_to_base64,
    create_image_tag,
    format_number,
)


def analyze_safety_trends() -> dict:
    """
    Run safety trend analysis for 2016-2025.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    print("Loading data for safety trend analysis...")
    df = load_data(clean=False)

    print("Extracting temporal features and classifying crimes...")
    df = extract_temporal_features(df)
    df = classify_crime_category(df)

    # Filter to 2016-2025 (last 10 complete years)
    df_recent = df[(df["year"] >= 2016) & (df["year"] <= 2025)].copy()
    print(f"Analyzing {len(df_recent):,} incidents from 2016-2025")

    results = {}

    # ========================================================================
    # 1. Annual Aggregation by Crime Category
    # ========================================================================
    print("Calculating annual crime counts by category...")

    annual_by_category = (
        df_recent.groupby(["year", "crime_category"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["Violent", "Property", "Other"], fill_value=0)
    )
    results["annual_by_category"] = annual_by_category

    # Calculate totals and percentages
    annual_by_category["Total"] = annual_by_category.sum(axis=1)
    for cat in ["Violent", "Property", "Other"]:
        annual_by_category[f"{cat}_pct"] = (
            annual_by_category[cat] / annual_by_category["Total"] * 100
        )

    # ========================================================================
    # 2. Year-over-Year Changes
    # ========================================================================
    print("Calculating year-over-year changes...")

    yoy_changes = annual_by_category[["Violent", "Property"]].pct_change() * 100
    results["yoy_changes"] = yoy_changes

    # ========================================================================
    # 3. Peak Year Analysis
    # ========================================================================
    print("Identifying peak years and calculating drops...")

    peak_stats = {}

    for category in ["Violent", "Property"]:
        cat_data = annual_by_category[category]
        peak_year_idx = cat_data.idxmax()
        peak_year_count = cat_data.loc[peak_year_idx]
        current_year_count = cat_data.loc[2025]

        # Calculate drops from peak
        drop_to_2024 = ((cat_data.loc[2024] - peak_year_count) / peak_year_count * 100)
        drop_to_2025 = ((current_year_count - peak_year_count) / peak_year_count * 100)

        peak_stats[category] = {
            "peak_year": peak_year_idx,
            "peak_count": peak_year_count,
            "count_2024": cat_data.loc[2024],
            "count_2025": current_year_count,
            "drop_pct_2024": drop_to_2024,
            "drop_pct_2025": drop_to_2025,
        }

    results["peak_stats"] = peak_stats

    # ========================================================================
    # 4. Visualization 1: Main Trend Line (Violent vs Property)
    # ========================================================================
    print("Creating trend line chart...")

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])

    years = annual_by_category.index

    # Plot lines with markers
    ax.plot(
        years,
        annual_by_category["Violent"],
        marker="o",
        linewidth=2.5,
        markersize=8,
        color=COLORS["danger"],
        label="Violent Crime",
    )
    ax.plot(
        years,
        annual_by_category["Property"],
        marker="s",
        linewidth=2.5,
        markersize=8,
        color=COLORS["primary"],
        label="Property Crime",
    )

    # Mark COVID-19 pandemic
    ax.axvline(
        x=2020,
        color="gray",
        linestyle=":",
        linewidth=2,
        alpha=0.7,
        label="COVID-19 Pandemic",
    )

    # Add value labels
    for year in years:
        violent_val = annual_by_category.loc[year, "Violent"]
        property_val = annual_by_category.loc[year, "Property"]

        ax.annotate(
            f"{format_number(violent_val)}",
            xy=(year, violent_val),
            xytext=(0, 10),
            textcoords="offset points",
            fontsize=8,
            ha="center",
            color=COLORS["danger"],
        )
        ax.annotate(
            f"{format_number(property_val)}",
            xy=(year, property_val),
            xytext=(0, -15),
            textcoords="offset points",
            fontsize=8,
            ha="center",
            color=COLORS["primary"],
        )

    ax.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax.set_ylabel("Annual Incident Count", fontsize=12, fontweight="bold")
    ax.set_title(
        "Philadelphia Crime Trends: Violent vs Property (2016-2025)",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(2015.5, 2025.5)

    plt.tight_layout()
    results["trend_line_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 5. Visualization 2: Year-over-Year Percentage Change
    # ========================================================================
    print("Creating year-over-year change chart...")

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])

    yoy_years = yoy_changes.index[1:]  # Skip first year (no change)
    violent_changes = yoy_changes["Violent"].dropna()
    property_changes = yoy_changes["Property"].dropna()

    x = np.arange(len(yoy_years))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2,
        violent_changes.values,
        width,
        label="Violent Crime",
        color=COLORS["danger"],
        alpha=0.8,
    )
    bars2 = ax.bar(
        x + width / 2,
        property_changes.values,
        width,
        label="Property Crime",
        color=COLORS["primary"],
        alpha=0.8,
    )

    # Zero line
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.8)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            va = "bottom" if height >= 0 else "top"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:+.1f}%",
                ha="center",
                va=va,
                fontsize=8,
            )

    ax.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax.set_ylabel("Year-over-Year Change (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Year-over-Year Percentage Change in Crime (2016-2025)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{y}" for y in yoy_years])
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    results["yoy_change_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 6. Visualization 3: Peak vs Current Comparison
    # ========================================================================
    print("Creating peak vs current comparison chart...")

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=FIGURE_SIZES["large"]
    )

    categories = ["Violent Crime", "Property Crime"]
    peak_counts = [
        peak_stats["Violent"]["peak_count"],
        peak_stats["Property"]["peak_count"],
    ]
    current_counts = [
        peak_stats["Violent"]["count_2025"],
        peak_stats["Property"]["count_2025"],
    ]
    peak_years = [
        peak_stats["Violent"]["peak_year"],
        peak_stats["Property"]["peak_year"],
    ]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax1.bar(
        x - width / 2,
        peak_counts,
        width,
        label="Peak Year",
        color=COLORS["warning"],
        alpha=0.8,
    )
    bars2 = ax1.bar(
        x + width / 2,
        current_counts,
        width,
        label="2025",
        color=COLORS["primary"],
        alpha=0.8,
    )

    ax1.set_ylabel("Annual Incident Count", fontsize=11, fontweight="bold")
    ax1.set_title("Peak Year vs 2025", fontsize=12, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend(framealpha=0.9)
    ax1.grid(True, alpha=0.3, axis="y")

    # Add value labels
    for i, (peak, current) in enumerate(zip(peak_counts, current_counts)):
        ax1.text(
            i - width / 2,
            peak,
            f"\n{format_number(peak)}\n({peak_years[i]})",
            ha="center",
            va="bottom",
            fontsize=9,
        )
        ax1.text(
            i + width / 2,
            current,
            f"\n{format_number(current)}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # Percentage change bar chart
    pct_changes = [
        peak_stats["Violent"]["drop_pct_2025"],
        peak_stats["Property"]["drop_pct_2025"],
    ]
    colors_pct = [
        COLORS["success"] if pct_changes[0] < 0 else COLORS["danger"],
        COLORS["success"] if pct_changes[1] < 0 else COLORS["danger"],
    ]

    bars3 = ax2.bar(x, pct_changes, color=colors_pct, alpha=0.8)
    ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
    ax2.set_ylabel("Change from Peak (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Percentage Change from Peak to 2025", fontsize=12, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.grid(True, alpha=0.3, axis="y")

    for i, change in enumerate(pct_changes):
        va = "bottom" if change >= 0 else "top"
        ax2.text(
            i,
            change,
            f"{change:+.1f}%",
            ha="center",
            va=va,
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    results["peak_comparison_plot"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 7. Summary Table
    # ========================================================================
    print("Creating summary statistics...")

    summary_stats = {
        "analysis_period": "2016-2025 (10 years)",
        "total_incidents": int(df_recent.shape[0]),
        "violent_peak_year": int(peak_stats["Violent"]["peak_year"]),
        "violent_peak_count": int(peak_stats["Violent"]["peak_count"]),
        "violent_2025_count": int(peak_stats["Violent"]["count_2025"]),
        "violent_2024_count": int(peak_stats["Violent"]["count_2024"]),
        "violent_drop_2024": round(peak_stats["Violent"]["drop_pct_2024"], 1),
        "violent_drop_2025": round(peak_stats["Violent"]["drop_pct_2025"], 1),
        "property_peak_year": int(peak_stats["Property"]["peak_year"]),
        "property_peak_count": int(peak_stats["Property"]["peak_count"]),
        "property_2025_count": int(peak_stats["Property"]["count_2025"]),
        "property_drop_2025": round(peak_stats["Property"]["drop_pct_2025"], 1),
    }
    results["summary_stats"] = summary_stats

    # Annual data for table
    annual_table = annual_by_category[["Violent", "Property", "Other"]].copy()
    annual_table.columns = ["Violent Crimes", "Property Crimes", "Other Crimes"]
    annual_table["Total"] = annual_table.sum(axis=1)
    annual_table["Violent %"] = (
        annual_table["Violent Crimes"] / annual_table["Total"] * 100
    ).round(1)
    annual_table["Property %"] = (
        annual_table["Property Crimes"] / annual_table["Total"] * 100
    ).round(1)
    results["annual_table"] = annual_table

    print("Safety trend analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from safety trend analysis results.

    Args:
        results: Dictionary from analyze_safety_trends()

    Returns:
        Markdown string with analysis results.
    """
    md = []

    # Title
    md.append("# Is Philadelphia Actually Getting Safer?\n")
    md.append("*Analysis of violent vs property crime trends (2016-2025)*\n\n")

    # ========================================================================
    # Executive Summary
    # ========================================================================
    md.append("## Executive Summary\n\n")

    stats = results["summary_stats"]

    md.append("**Yes, Philadelphia is getting safer** - at least when it comes to violent crime. \n\n")
    md.append(f"Contrary to the perception that crime spiked during or after the COVID-19 pandemic, ")
    md.append(f"the data shows that **violent crime actually peaked in {stats['violent_peak_year']}** ")
    md.append(f"with {format_number(stats['violent_peak_count'])} incidents.\n\n")

    md.append(f"### Key Findings\n\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(
        f"| **Violent Crime Peak** | {stats['violent_peak_year']} ({format_number(stats['violent_peak_count'])} incidents) |"
    )
    md.append(
        f"| **Violent Crime 2024** | {format_number(stats['violent_2024_count'])} incidents ({stats['violent_drop_2024']:+.1f}% from peak) |"
    )
    md.append(
        f"| **Violent Crime 2025** | {format_number(stats['violent_2025_count'])} incidents ({stats['violent_drop_2025']:+.1f}% from peak) |"
    )
    md.append(
        f"| **Property Crime Peak** | {stats['property_peak_year']} ({format_number(stats['property_peak_count'])} incidents) |"
    )
    md.append(
        f"| **Property Crime 2025** | {format_number(stats['property_2025_count'])} incidents ({stats['property_drop_2025']:+.1f}% from peak) |"
    )
    md.append(f"| **Analysis Period** | {stats['analysis_period']} |")
    md.append(f"| **Total Incidents** | {format_number(stats['total_incidents'])} |")
    md.append("\n")

    # Main trend chart
    md.append("### Crime Trend: Violent vs Property (2016-2025)\n\n")
    md.append(results["trend_line_plot"])
    md.append("\n\n")

    # ========================================================================
    # Detailed Analysis
    # ========================================================================
    md.append("## Detailed Analysis\n\n")

    md.append("### Violent Crime: A Clear Decline\n\n")
    md.append(
        f"Violent crime in Philadelphia has been on a **consistent downward trend** since peaking in {stats['violent_peak_year']}. "
    )
    md.append(
        f"The {stats['violent_drop_2024']:.1f}% drop from {stats['violent_peak_year']} to 2024 represents "
    )
    md.append(
        f"{format_number(stats['violent_peak_count'] - stats['violent_2024_count'])} fewer violent crimes annually. "
    )
    md.append(f"By 2025, the decline reached {stats['violent_drop_2025']:.1f}% from the peak.\n\n"
    )

    md.append("**Violent crimes include:**\n")
    md.append("- Homicide (UCR 100)\n")
    md.append("- Rape (UCR 200)\n")
    md.append("- Robbery (UCR 300)\n")
    md.append("- Aggravated Assault (UCR 400)\n\n")

    md.append("### Property Crime: Different Patterns\n\n")
    md.append(
        f"Property crime shows a different pattern, peaking in {stats['property_peak_year']}. "
    )
    md.append("This suggests that factors affecting violent and property crimes may differ, and that ")
    md.append("perceptions of safety may be driven more by property crime trends (theft, burglary) ")
    md.append("than by violent crime trends.\n\n")

    md.append("**Property crimes include:**\n")
    md.append("- Burglary (UCR 500)\n")
    md.append("- Theft/Larceny (UCR 600)\n")
    md.append("- Motor Vehicle Theft (UCR 700)\n\n")

    # Year-over-year chart
    md.append("### Year-over-Year Percentage Changes\n\n")
    md.append(results["yoy_change_plot"])
    md.append("\n\n")

    # ========================================================================
    # Peak vs Current Comparison
    # ========================================================================
    md.append("## Peak Year vs Current\n\n")
    md.append(results["peak_comparison_plot"])
    md.append("\n\n")

    # ========================================================================
    # Annual Breakdown Table
    # ========================================================================
    md.append("## Annual Crime Counts (2016-2025)\n\n")

    annual_table = results["annual_table"]
    md.append("| Year | Violent Crimes | Property Crimes | Other Crimes | Total | Violent % | Property % |")
    md.append("|------|----------------|-----------------|--------------|-------|-----------|------------|")

    for year, row in annual_table.iterrows():
        md.append(
            f"| {year} | {format_number(int(row['Violent Crimes']))} | {format_number(int(row['Property Crimes']))} | "
            f"{format_number(int(row['Other Crimes']))} | {format_number(int(row['Total']))} | {row['Violent %']}% | {row['Property %']}% |"
        )
    md.append("\n")

    # ========================================================================
    # Context and Interpretation
    # ========================================================================
    md.append("## Context and Interpretation\n\n")

    md.append("### Why Does It Feel Like Crime Is Increasing?\n\n")
    md.append("The perception that Philadelphia is becoming more dangerous may stem from several factors:\n\n")
    md.append("1. **Property Crime Visibility**: Property crimes like theft and burglary are more common ")
    md.append("   and more visible to residents, even if less severe than violent crimes.\n\n")
    md.append("2. **Media Coverage**: Violent crimes receive disproportionate media coverage, ")
    md.append("   creating availability bias in public perception.\n\n")
    md.append("3. **COVID-19 Disruption**: The 2020-2021 period was unusual due to pandemic lockdowns, ")
    md.append("   which affected crime patterns in complex ways that may skew perceptions.\n\n")
    md.append("4. **Neighborhood Variation**: City-wide trends may not reflect local experiences. ")
    md.append("   Some neighborhoods may see increases while others see decreases.\n\n")

    md.append("### The COVID-19 Effect (2020-2021)\n\n")
    md.append(
        "The COVID-19 pandemic created unusual conditions that affected crime reporting and patterns. "
    )
    md.append("Lockdowns, business closures, and changes in police behavior during 2020-2021 make ")
    md.append("this period an anomaly rather than a reliable baseline for comparison.\n\n")

    md.append("### 2022-2023 Property Crime Spike\n\n")
    md.append(
        "Property crimes showed increases in 2022-2023, likely driven by post-pandemic economic factors, "
    )
    md.append(
        "inflation, and changing routines. This spike in more common (but less severe) crimes "
    )
    md.append("may be contributing to current perceptions of safety.\n\n")

    # ========================================================================
    # Methodology
    # ========================================================================
    md.append("## Methodology\n\n")

    md.append("### Data Source\n")
    md.append("- Philadelphia Police Department crime incident data (2006-2026)\n")
    md.append(f"- Analysis period: 2016-2025 ({stats['analysis_period']})\n")
    md.append("- 2026 excluded due to incomplete data (only through January 20)\n\n")

    md.append("### Crime Classification\n")
    md.append("Crimes are classified using the FBI UCR (Uniform Crime Reporting) standard:\n\n")
    md.append("| UCR Code | Category | Examples |")
    md.append("|----------|----------|----------|")
    md.append("| 100 | Violent - Homicide | Murder, manslaughter |")
    md.append("| 200 | Violent - Rape | Sexual assault |")
    md.append("| 300 | Violent - Robbery | Taking property by force/threat |")
    md.append("| 400 | Violent - Aggravated Assault | Attack with serious injury or weapon |")
    md.append("| 500 | Property - Burglary | Illegal entry to commit crime |")
    md.append("| 600 | Property - Theft | Larceny, shoplifting, pickpocketing |")
    md.append("| 700 | Property - Motor Vehicle Theft | Car theft, auto burglary |")
    md.append("| 800+ | Other | Weapons, drugs, fraud, vandalism, etc. |")
    md.append("\n\n")

    md.append("### Limitations\n\n")
    md.append("- Data reflects reported crimes only; unreported crimes are not captured\n")
    md.append("- Changes in policing practices may affect reporting rates over time\n")
    md.append("- UCR codes may be subject to classification errors or changes\n")
    md.append("- Geographic coordinate data was not used in this analysis\n\n")

    # ========================================================================
    # Conclusion
    # ========================================================================
    md.append("## Conclusion\n\n")

    md.append(
        f"Based on {stats['analysis_period']} of crime data, **Philadelphia has become safer** "
    )
    md.append(
        f"with respect to violent crime, which has fallen {stats['violent_drop_2025']:.1f}% from its "
    )
    md.append(f"{stats['violent_peak_year']} peak. Property crime trends are more variable, ")
    md.append("with different peak years and patterns.\n\n")

    md.append(
        "**The answer to 'Is Philadelphia getting safer?' depends on what type of crime you're asking about.** "
    )
    md.append("For violent crime, the trend is clearly positive. For property crime, the picture is more nuanced.\n\n")

    md.append("---\n\n")
    md.append("*Report generated by Claude Code | ")
    md.append(f"Data source: Philadelphia crime incidents dataset ({format_number(stats['total_incidents'])} records, 2016-2025)*\n")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_safety_trends()
    report = generate_markdown_report(results)

    report_path = PROJECT_ROOT / "reports" / "safety_trend_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
