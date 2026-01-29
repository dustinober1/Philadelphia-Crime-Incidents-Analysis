#!/usr/bin/env python3
"""
Red Zones Report Generator

Generates a focused report answering: "I have limited patrols. What are the
'Red Zones' where I need them most?"

Run this script to generate:
    reports/05_red_zones_report.md
    reports/red_zones_map.html

Usage:
    python analysis/09_report_red_zones.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.red_zones import analyze_red_zones, generate_markdown_report
from analysis.config import REPORTS_DIR


def main():
    """Generate the red zones report."""
    print("=" * 60)
    print("Red Zones Analysis")
    print("Question: I have limited patrols. What are the 'Red Zones'")
    print("         where I need them most?")
    print("=" * 60)
    print()

    # Run the analysis
    results = analyze_red_zones()

    # Generate the report
    print("Generating report...")
    report = generate_markdown_report(results)

    # Write to file
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "05_red_zones_report.md"

    with open(report_path, "w") as f:
        f.write(report)

    print()
    print("=" * 60)
    print(f"Report saved to: {report_path}")
    print("=" * 60)

    # Print summary
    summary = results["summary_stats"]
    insights = results["insights"]

    print()
    print("Quick Summary:")
    print(f"  Red Zones Found: {summary['red_zones_found']}")
    print(f"  Incidents in Hotspots: {format_number(summary['incidents_in_hotspots'])} ({summary['pct_in_hotspots']:.1f}%)")
    if insights.get("top_zone"):
        top_zone = insights["top_zone"]
        print(f"  Top Zone: {top_zone['cluster_id']} with {format_number(top_zone['count'])} incidents")
    if insights.get("top_volume_district"):
        vol_dist = insights["top_volume_district"]
        print(f"  Highest Volume District: D{vol_dist['district']} ({format_number(vol_dist['count'])} incidents)")
    print()
    print(f"Interactive Map: {results.get('map_path', 'N/A')}")


def format_number(num: int | float) -> str:
    """Format a number with thousands separators."""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


if __name__ == "__main__":
    main()
