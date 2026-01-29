#!/usr/bin/env python3
"""
COVID-19 Lockdown Impact Report Generator

Generates a focused report answering: "How did the COVID-19 lockdowns impact
Philadelphia's crime landscape?"

Run this script to generate:
    reports/04_covid_lockdown_report.md

Usage:
    python analysis/10_report_covid_lockdown.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analysis.covid_lockdown import analyze_covid_lockdown, generate_markdown_report
from analysis.config import REPORTS_DIR


def main():
    """Generate the COVID-19 lockdown impact report."""
    print("=" * 60)
    print("COVID-19 Lockdown Impact Analysis")
    print("Question: How did the COVID-19 lockdowns impact Philadelphia's crime landscape?")
    print("=" * 60)
    print()

    # Run the analysis
    results = analyze_covid_lockdown()

    # Generate the report
    print("Generating report...")
    report = generate_markdown_report(results)

    # Write to file
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "04_covid_lockdown_report.md"

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
    print(f"  Pre-lockdown annual avg: {format_number(int(stats['pre_lockdown_annual']))} incidents")
    print(f"  Lockdown annual avg: {format_number(int(stats['lockdown_annual']))} incidents ({stats['lockdown_change']:+.1f}%)")
    print(f"  Post-lockdown annual avg: {format_number(int(stats['post_lockdown_annual']))} incidents ({stats['post_change_from_pre']:+.1f}% vs pre)")
    print()

    burglary = results["burglary_stats"]["Lockdown (2020-2022)"]
    print("  Burglary displacement during lockdown:")
    print(f"    Residential: {burglary['residential_pct_change']:+.1f}%")
    print(f"    Commercial: {burglary['commercial_pct_change']:+.1f}%")


def format_number(num: int | float) -> str:
    """Format a number with thousands separators."""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


if __name__ == "__main__":
    main()
