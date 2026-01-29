#!/usr/bin/env python3
"""
Robbery Timing Report Generator

Generates a focused report answering: "If I want to prevent robberies,
what time of day should my officers be visible?"

Run this script to generate:
    reports/06_robbery_timing_report.md

Usage:
    python analysis/11_report_robbery_timing.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.robbery_timing import analyze_robbery_timing, generate_markdown_report
from analysis.config import REPORTS_DIR


def main():
    """Generate the robbery timing report."""
    print("=" * 60)
    print("Robbery Timing Analysis")
    print("Question: When should officers be visible to prevent robberies?")
    print("=" * 60)
    print()

    # Run the analysis
    results = analyze_robbery_timing()

    # Generate the report
    print("Generating report...")
    report = generate_markdown_report(results)

    # Write to file
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "06_robbery_timing_report.md"

    with open(report_path, "w") as f:
        f.write(report)

    print()
    print("=" * 60)
    print(f"Report saved to: {report_path}")
    print("=" * 60)

    # Print summary
    insights = results["insights"]
    peak_combo = results["peak_combinations"][0]

    print()
    print("Quick Summary:")
    print(f"  Total robberies analyzed: {format_number(results['total_robberies'])}")
    print(f"  Highest risk period: {insights['highest_risk_period']['name']}")
    print(f"  Peak hour: {insights['peak_hour']}:00 ({'PM' if insights['peak_hour'] >= 12 else 'AM'})")
    print(f"  Peak day: {insights['peak_day']}day")
    print(f"  Worst time slot: {peak_combo['day']} at {peak_combo['hour']}:00")
    print(f"  Robberies in worst slot: {format_number(peak_combo['count'])}")


def format_number(num: int | float) -> str:
    """Format a number with thousands separators."""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


if __name__ == "__main__":
    main()
