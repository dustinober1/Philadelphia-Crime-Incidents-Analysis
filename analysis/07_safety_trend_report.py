#!/usr/bin/env python3
"""
Safety Trend Report Generator

Generates a focused report answering: "Is Philadelphia actually getting safer?"

Run this script to generate:
    reports/safety_trend_report.md

Usage:
    python analysis/07_safety_trend_report.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.safety_trend_analysis import analyze_safety_trends, generate_markdown_report
from analysis.config import REPORTS_DIR


def main():
    """Generate the safety trend report."""
    print("=" * 60)
    print("Safety Trend Analysis")
    print("Question: Is Philadelphia actually getting safer?")
    print("=" * 60)
    print()

    # Run the analysis
    results = analyze_safety_trends()

    # Generate the report
    print("Generating report...")
    report = generate_markdown_report(results)

    # Write to file
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "safety_trend_report.md"

    with open(report_path, "w") as f:
        f.write(report)

    print()
    print("=" * 60)
    print(f"Report saved to: {report_path}")
    print("=" * 60)

    # Print summary
    stats = results["summary_stats"]
    print()
    print("Quick Summary:")
    print(f"  Violent crime peak: {stats['violent_peak_year']} ({format_number(stats['violent_peak_count'])} incidents)")
    print(f"  Violent crime 2025: {format_number(stats['violent_2025_count'])} incidents ({stats['violent_drop_2025']:+.1f}% from peak)")
    print(f"  Property crime peak: {stats['property_peak_year']} ({format_number(stats['property_peak_count'])} incidents)")
    print()


def format_number(num: int | float) -> str:
    """Format a number with thousands separators."""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


if __name__ == "__main__":
    main()
