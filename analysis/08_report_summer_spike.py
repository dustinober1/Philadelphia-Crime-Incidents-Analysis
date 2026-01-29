#!/usr/bin/env python3
"""
Summer Crime Spike Report Generator

Generates a focused report answering: "Is the summer crime spike a myth or a fact?"

Run this script to generate:
    reports/03_summer_spike_report.md

Usage:
    python analysis/08_report_summer_spike.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.summer_spike import analyze_summer_spike, generate_markdown_report
from analysis.config import REPORTS_DIR


def main():
    """Generate the summer crime spike report."""
    print("=" * 60)
    print("Summer Crime Spike Analysis")
    print("Question: Is the summer crime spike a myth or a fact?")
    print("=" * 60)
    print()

    # Run the analysis
    results = analyze_summer_spike()

    # Generate the report
    print("Generating report...")
    report = generate_markdown_report(results)

    # Write to file
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "03_summer_spike_report.md"

    with open(report_path, "w") as f:
        f.write(report)

    print()
    print("=" * 60)
    print(f"Report saved to: {report_path}")
    print("=" * 60)

    # Print summary
    seasonal = results["seasonal_comparison"]
    july_jan = results["july_vs_january"]
    peak = results["peak_analysis"]
    consistency = results.get("consistency", {})

    print()
    print("Quick Summary:")
    print(f"  Summer vs Winter: {seasonal['summer_winter_pct_change']:+.1f}% change")
    print(f"  July vs January: {july_jan['pct_increase']:+.1f}% change")
    print(f"  Peak month: {peak['peak_month']} ({format_number(int(peak['peak_value']))} incidents)")
    if consistency:
        print(f"  Consistency: {consistency['summer_higher_years']}/{consistency['total_years']} years had higher summer crime")


def format_number(num: int | float) -> str:
    """Format a number with thousands separators."""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


if __name__ == "__main__":
    main()
