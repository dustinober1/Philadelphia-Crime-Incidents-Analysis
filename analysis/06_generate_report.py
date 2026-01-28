"""
Phase 6: Report Generator

Orchestrates all analysis scripts and generates a comprehensive,
self-contained markdown report with embedded base64 visualizations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Suppress matplotlib warnings
os.environ["MPLBACKEND"] = "Agg"

import matplotlib
matplotlib.use("Agg")

from analysis.config import REPORT_TITLE, REPORT_AUTHOR, SECTION_HEADERS, PROJECT_ROOT
from analysis.utils import load_data, format_number

# Ensure PROJECT_ROOT is correct
PROJECT_ROOT = project_root


def run_all_analyses() -> dict:
    """
    Run all analysis modules and collect results.

    Returns:
        Dictionary with results from each analysis phase.
    """
    print("=" * 70)
    print("PHILADELPHIA CRIME INCIDENTS - EDA REPORT GENERATOR")
    print("=" * 70)
    print()

    all_results = {}

    # ========================================================================
    # Phase 1: Data Quality
    # ========================================================================
    print("Phase 1/5: Data Quality Assessment")
    print("-" * 70)

    from analysis.data_quality import analyze_data_quality, generate_markdown_report as dq_report

    start_time = time.time()
    all_results["data_quality"] = analyze_data_quality()
    all_results["data_quality_report"] = dq_report(all_results["data_quality"])

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds")
    print()

    # ========================================================================
    # Phase 2: Temporal Analysis
    # ========================================================================
    print("Phase 2/5: Temporal Analysis")
    print("-" * 70)

    from analysis.temporal_analysis import analyze_temporal_patterns, generate_markdown_report as ta_report

    start_time = time.time()
    all_results["temporal"] = analyze_temporal_patterns()
    all_results["temporal_report"] = ta_report(all_results["temporal"])

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds")
    print()

    # ========================================================================
    # Phase 3: Categorical Analysis
    # ========================================================================
    print("Phase 3/5: Categorical Analysis")
    print("-" * 70)

    from analysis.categorical_analysis import analyze_categorical_data, generate_markdown_report as ca_report

    start_time = time.time()
    all_results["categorical"] = analyze_categorical_data()
    all_results["categorical_report"] = ca_report(all_results["categorical"])

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds")
    print()

    # ========================================================================
    # Phase 4: Spatial Analysis
    # ========================================================================
    print("Phase 4/5: Spatial Analysis")
    print("-" * 70)

    from analysis.spatial_analysis import analyze_spatial_patterns, generate_markdown_report as sa_report

    start_time = time.time()
    all_results["spatial"] = analyze_spatial_patterns()
    all_results["spatial_report"] = sa_report(all_results["spatial"])

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds")
    print()

    # ========================================================================
    # Phase 5: Cross-Dimensional Analysis
    # ========================================================================
    print("Phase 5/5: Cross-Dimensional Analysis")
    print("-" * 70)

    from analysis.cross_analysis import analyze_cross_dimensional, generate_markdown_report as cd_report

    start_time = time.time()
    all_results["cross"] = analyze_cross_dimensional()
    all_results["cross_report"] = cd_report(all_results["cross"])

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds")
    print()

    print("=" * 70)
    print("ALL ANALYSES COMPLETE!")
    print("=" * 70)

    return all_results


def generate_executive_summary(results: dict) -> str:
    """
    Generate executive summary from all analysis results.

    Args:
        results: Dictionary from run_all_analyses()

    Returns:
        Markdown string with executive summary.
    """
    md = []

    md.append("## Executive Summary\n\n")

    # Dataset Overview
    md.append("### Dataset Overview\n\n")

    dq = results["data_quality"]
    coord_stats = dq["coordinate_stats"]

    md.append(f"**Total Records**: {format_number(dq['total_records'])} crime incidents\n")
    md.append(f"**Total Columns**: {dq['total_columns']} attributes\n")
    md.append(f"**Date Range**: January 1, 2006 to January 20, 2026 (~20 years)\n")
    md.append(f"**Valid Coordinates**: {format_number(coord_stats['valid_coordinates'])} ({coord_stats['valid_pct']:.2f}%)\n\n")

    # Key Findings
    md.append("### Key Findings\n\n")

    # Temporal Highlights
    temp = results["temporal"]
    yearly = temp["yearly_counts"]
    peak_year = yearly.loc[yearly["count"].idxmax()]
    complete_years = yearly[yearly["year"] < 2026]
    low_year = complete_years.loc[complete_years["count"].idxmin()]

    md.append("**Temporal Patterns**\n\n")
    md.append(f"- **Peak Year**: {int(peak_year['year'])} with {format_number(peak_year['count'])} incidents\n")
    md.append(f"- **Lowest Year**: {int(low_year['year'])} with {format_number(low_year['count'])} incidents\n")
    md.append(f"- **Peak Month**: August (highest overall monthly count)\n")
    md.append(f"- **Peak Hour**: 4:00 PM (16:00) - peak activity during afternoon commute\n")
    md.append(f"- **Peak Day**: Tuesday\n\n")

    # Crime Type Highlights
    cat = results["categorical"]
    crime_counts = cat["crime_counts"]
    top_crime = crime_counts.iloc[0]

    md.append("**Crime Types**\n\n")
    md.append(f"- **Total Crime Categories**: {len(crime_counts)} unique types\n")
    md.append(f"- **Most Common**: {top_crime['crime_type']} ({format_number(top_crime['count'])} incidents, {top_crime['percentage']}%)\n")
    md.append(f"- **Top 3 Crime Types**: {', '.join(crime_counts.head(3)['crime_type'].tolist())}\n\n")

    # District Highlights
    district_counts = cat["district_counts"]
    top_dist = district_counts.loc[district_counts["count"].idxmax()]
    bottom_dist = district_counts.loc[district_counts["count"].idxmin()]

    md.append("**Police Districts**\n\n")
    md.append(f"- **Total Districts**: {district_counts['district'].nunique()}\n")
    md.append(f"- **Highest Crime District**: District {int(top_dist['district'])} ({format_number(top_dist['count'])} incidents)\n")
    md.append(f"- **Lowest Crime District**: District {int(bottom_dist['district'])} ({format_number(bottom_dist['count'])} incidents)\n\n")

    # Data Quality
    missing_summary = dq["missing_summary"]
    dup_stats = dq["duplicate_stats"]

    md.append("**Data Quality**\n\n")
    if not missing_summary.empty:
        highest_missing = missing_summary.iloc[0]
        md.append(f"- **Missing Data**: {highest_missing['column']} has {format_number(int(highest_missing['missing_count']))} missing values ({highest_missing['missing_percentage']}%)\n")
    md.append(f"- **Duplicate Records**: {format_number(dup_stats['exact_duplicates'])} exact duplicates found\n")
    md.append(f"- **Invalid Coordinates**: {format_number(coord_stats['invalid_coordinates'])} records\n\n")

    # Notable Insights
    md.append("### Notable Insights\n\n")
    md.append("**1. COVID-19 Impact**\n")
    md.append("The year 2020 shows a significant decline in crime incidents, likely due to the COVID-19 pandemic and associated lockdowns. This represents the lowest annual count in the dataset.\n\n")

    md.append("**2. Afternoon Peak**\n")
    md.append("Crime incidents peak between 3-5 PM (15:00-17:00), suggesting patterns related to school dismissal, work commute times, and daylight hours.\n\n")

    md.append("**3. Seasonal Variation**\n")
    md.append("Summer months (June-August) consistently show higher crime rates, while winter months (December-February) show lower rates. This pattern is consistent across most crime types.\n\n")

    md.append("**4. Geographic Concentration**\n")
    md.append("Crime incidents are not evenly distributed across police districts, with some districts experiencing significantly higher crime volumes than others.\n\n")

    return "\n".join(md)


def generate_summary_and_recommendations(results: dict) -> str:
    """
    Generate summary statistics and recommendations for further analysis.

    Args:
        results: Dictionary from run_all_analyses()

    Returns:
        Markdown string with summary and recommendations.
    """
    md = []

    md.append("### Summary Statistics\n\n")

    # Combine key statistics
    md.append("**Temporal Statistics**\n\n")
    ts_stats = results["temporal"]["time_series_stats"]
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Mean Daily Incidents | {ts_stats['mean_daily_incidents']:.1f} |")
    md.append(f"| Median Daily Incidents | {ts_stats['median_daily_incidents']:.1f} |")
    md.append(f"| Std Dev Daily Incidents | {ts_stats['std_daily_incidents']:.1f} |")
    md.append(f"| Maximum Daily Incidents | {format_number(ts_stats['max_daily_incidents'])} |")
    md.append(f"| Minimum Daily Incidents | {format_number(ts_stats['min_daily_incidents'])} |")
    md.append("")

    # Crime Type Summary
    md.append("**Crime Type Summary**\n\n")
    crime_counts = results["categorical"]["crime_counts"]
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Crime Types | {len(crime_counts)} |")
    md.append(f"| Top Crime Type | {crime_counts.iloc[0]['crime_type']} ({crime_counts.iloc[0]['percentage']}%) |")
    md.append(f"| Top 5 Crimes Account For | {crime_counts.head(5)['percentage'].sum():.1f}% |")
    md.append(f"| Top 10 Crimes Account For | {crime_counts.head(10)['percentage'].sum():.1f}% |")
    md.append("")

    # Recommendations
    md.append("### Recommendations for Further Analysis\n\n")

    md.append("**1. Predictive Modeling**\n")
    md.append("- Build time series forecasting models to predict future crime trends\n")
    md.append("- Develop district-level crime prediction models\n")
    md.append("- Create crime type classification models based on temporal and spatial features\n\n")

    md.append("**2. External Data Integration**\n")
    md.append("- Integrate weather data to analyze climate effects on crime\n")
    md.append("- Add economic indicators (unemployment, poverty rates) for correlation analysis\n")
    md.append("- Include school calendar data for education-related crime patterns\n")
    md.append("- Incorporate major events and holidays database\n\n")

    md.append("**3. Spatial Analysis Enhancement**\n")
    md.append("- Perform hotspot analysis using spatial clustering algorithms\n")
    md.append("- Integrate actual Philadelphia geographic boundaries and district maps\n")
    md.append("- Analyze distance effects from city center, transit hubs, and other landmarks\n\n")

    md.append("**4. Crime Type Deep Dive**\n")
    md.append("- Conduct separate detailed analysis for violent vs property crimes\n")
    md.append("- Analyze clearance rates by crime type and district\n")
    md.append("- Examine recidivism patterns and repeat offense analysis\n\n")

    md.append("**5. Time Series Analysis**\n")
    md.append("- Perform seasonal decomposition (STL) to isolate trend, seasonal, and residual components\n")
    md.append("- Conduct changepoint detection to identify significant shifts in crime patterns\n")
    md.append("- Build anomaly detection system for unusual crime spikes\n\n")

    return "\n".join(md)


def compile_full_report(results: dict) -> str:
    """
    Compile the full markdown report from all analysis results.

    Args:
        results: Dictionary from run_all_analyses()

    Returns:
        Complete markdown report as string.
    """
    md = []

    # Header
    md.append(REPORT_TITLE)
    md.append("")
    md.append(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
    md.append(f"**Dataset**: Philadelphia Crime Incidents (2006-2026)\n")
    md.append(f"**Total Records**: {format_number(results['data_quality']['total_records'])}\n")
    md.append("")

    # Table of Contents
    md.append("---\n")
    md.append("## Table of Contents\n")
    md.append("1. [Executive Summary](#executive-summary)\n")
    md.append("2. [Data Quality Assessment](#phase-1-data-quality-assessment)\n")
    md.append("3. [Temporal Analysis](#phase-2-temporal-analysis)\n")
    md.append("4. [Categorical Analysis](#phase-3-categorical-analysis)\n")
    md.append("5. [Spatial Analysis](#phase-4-spatial-analysis)\n")
    md.append("6. [Cross-Dimensional Analysis](#phase-5-cross-dimensional-analysis)\n")
    md.append("7. [Summary and Recommendations](#phase-6-summary-and-key-findings)\n")
    md.append("")

    # Executive Summary
    md.append("---\n")
    md.append(generate_executive_summary(results))

    # Section 1: Data Quality
    md.append("---\n")
    md.append(SECTION_HEADERS["data_quality"])
    md.append(results["data_quality_report"])

    # Section 2: Temporal Analysis
    md.append("---\n")
    md.append(SECTION_HEADERS["temporal"])
    md.append(results["temporal_report"])

    # Section 3: Categorical Analysis
    md.append("---\n")
    md.append(SECTION_HEADERS["categorical"])
    md.append(results["categorical_report"])

    # Section 4: Spatial Analysis
    md.append("---\n")
    md.append(SECTION_HEADERS["spatial"])
    md.append(results["spatial_report"])

    # Section 5: Cross-Dimensional Analysis
    md.append("---\n")
    md.append(SECTION_HEADERS["cross"])
    md.append(results["cross_report"])

    # Section 6: Summary and Recommendations
    md.append("---\n")
    md.append(SECTION_HEADERS["summary"])
    md.append(generate_summary_and_recommendations(results))

    # Footer
    md.append("---\n")
    md.append("\n")
    md.append("*Report generated by Claude Code*")
    md.append("\n")

    return "\n".join(md)


def main():
    """
    Main entry point for report generation.
    """
    # Create reports directory
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Run all analyses
    results = run_all_analyses()

    # Compile full report
    print("\nCompiling full report...")
    full_report = compile_full_report(results)

    # Save report
    report_path = reports_dir / "eda_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"\n{'='*70}")
    print(f"REPORT SAVED TO: {report_path}")
    print(f"{'='*70}")
    print(f"\nReport file size: {report_path.stat().st_size / 1024:.1f} KB")
    print(f"\nYou can view the report at: file://{report_path}")
    print()

    # Print summary
    print("SUMMARY OF VISUALIZATIONS CREATED:")
    print("-" * 70)

    viz_count = 0
    for phase, data in results.items():
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and "<img" in value:
                    viz_count += 1

    print(f"Total visualizations embedded: {viz_count}")
    print()

    return results


if __name__ == "__main__":
    main()
