"""Validation script for Phase 3 artifacts."""

from pathlib import Path

import pandas as pd


def validate_phase3_artifacts(
    repo_root: Path,
) -> dict[str, list[tuple[str, bool, str]]]:
    """Validate all Phase 3 artifacts.

    Returns dict with validation results by notebook.
    """
    reports_dir = repo_root / "reports"

    results = {
        "retail_theft": [],
        "vehicle_crimes": [],
        "crime_composition": [],
        "event_impacts": [],
    }

    # Retail Theft (POLICY-01)
    checks = [
        ("retail_theft_trend.png", "PNG visualization exists"),
        ("retail_theft_monthly_heatmap.png", "Monthly heatmap exists"),
        ("retail_theft_verdict.md", "Verdict report exists"),
        ("retail_theft_annual.csv", "Annual data CSV exists"),
    ]
    for artifact, desc in checks:
        path = reports_dir / artifact
        exists = path.exists()
        results["retail_theft"].append((artifact, exists, desc))

    # Validate verdict in report
    report_path = reports_dir / "retail_theft_verdict.md"
    if report_path.exists():
        content = report_path.read_text()
        has_verdict = "SUPPORTED" in content or "NOT SUPPORTED" in content
        results["retail_theft"].append(("verdict", has_verdict, "Report contains verdict"))

    # Vehicle Crimes (POLICY-02)
    checks = [
        ("vehicle_crimes_corridor_map.png", "Static map exists"),
        ("vehicle_corridor_analysis.md", "Summary report exists"),
        ("vehicle_crimes_corridor_stats.csv", "Corridor stats CSV exists"),
        ("vehicle_crimes_per_corridor.csv", "Per-corridor breakdown exists"),
        ("vehicle_crimes_hourly_corridor.png", "Hourly patterns comparison exists"),
    ]
    for artifact, desc in checks:
        path = reports_dir / artifact
        exists = path.exists()
        results["vehicle_crimes"].append((artifact, exists, desc))

    # Validate quantification
    stats_path = reports_dir / "vehicle_crimes_corridor_stats.csv"
    if stats_path.exists():
        try:
            stats = pd.read_csv(stats_path)
            has_pct = "pct_of_crimes" in stats.columns or "pct_within" in stats.columns
            pct_col = "pct_of_crimes" if "pct_of_crimes" in stats.columns else "pct_within"
            pct_valid = stats[pct_col].between(0, 100).all() if has_pct else False
            results["vehicle_crimes"].append(
                ("quantification", has_pct and pct_valid, "Valid % quantification")
            )
        except Exception as e:
            results["vehicle_crimes"].append(("quantification", False, f"Error: {e}"))

    # Crime Composition (POLICY-03)
    checks = [
        ("crime_composition_stacked.png", "Stacked area chart exists"),
        ("crime_composition_pct.png", "Percentage chart exists"),
        ("violent_ratio_trend.png", "Violent ratio trend exists"),
        ("crime_composition_analysis.md", "Summary report exists"),
        ("crime_composition_annual.csv", "Annual data CSV exists"),
    ]
    for artifact, desc in checks:
        path = reports_dir / artifact
        exists = path.exists()
        results["crime_composition"].append((artifact, exists, desc))

    # Event Impacts (HYP-EVENTS)
    checks = [
        ("event_impact_chart.png", "Main comparison chart exists"),
        ("event_impact_by_category.png", "Category comparison exists"),
        ("event_impact_summary.md", "Summary report exists"),
        ("event_impact_results.csv", "Results CSV exists"),
    ]
    for artifact, desc in checks:
        path = reports_dir / artifact
        exists = path.exists()
        results["event_impacts"].append((artifact, exists, desc))

    # Validate statistical results
    results_path = reports_dir / "event_impact_results.csv"
    if results_path.exists():
        try:
            df = pd.read_csv(results_path)
            has_pvalue = "p_value" in df.columns
            has_ci = "ci_lower" in df.columns and "ci_upper" in df.columns
            results["event_impacts"].append(
                ("statistics", has_pvalue and has_ci, "Has p-values and CIs")
            )
        except Exception as e:
            results["event_impacts"].append(("statistics", False, f"Error: {e}"))

    return results


def cross_reference_checks(repo_root: Path) -> list[tuple[str, bool, str]]:
    """Run cross-reference validation checks."""
    reports_dir = repo_root / "reports"
    checks = []

    # Check 1: Retail theft annual data has expected columns
    try:
        retail = pd.read_csv(reports_dir / "retail_theft_annual.csv")
        has_year = "year" in retail.columns
        has_count = "count" in retail.columns
        checks.append(
            (
                "retail_structure",
                has_year and has_count,
                "Retail data has year and count",
            )
        )
    except Exception as e:
        checks.append(("retail_structure", False, f"Error: {e}"))

    # Check 2: Event impacts have results for multiple event types
    try:
        events = pd.read_csv(reports_dir / "event_impact_results.csv")
        n_event_types = events["event_type"].nunique()
        valid = n_event_types >= 3  # At least holidays, sports, and one team
        checks.append(("event_types", valid, f"{n_event_types} event types analyzed"))
    except Exception as e:
        checks.append(("event_types", False, f"Error: {e}"))

    # Check 3: Composition data covers expected years
    try:
        composition = pd.read_csv(reports_dir / "crime_composition_annual.csv")
        years = composition["year"].tolist() if "year" in composition.columns else []
        has_2020 = 2020 in years
        has_2024 = 2024 in years
        checks.append(
            (
                "composition_years",
                has_2020 and has_2024,
                "Composition includes 2020 and 2024",
            )
        )
    except Exception as e:
        checks.append(("composition_years", False, f"Error: {e}"))

    return checks


def print_validation_report(results: dict, cross_checks: list = None) -> tuple[int, int]:
    """Print validation report and return pass/fail counts."""
    total_pass = 0
    total_fail = 0

    print("\n" + "=" * 60)
    print("PHASE 3 ARTIFACT VALIDATION")
    print("=" * 60)

    for notebook, checks in results.items():
        print(f"\n{notebook.upper().replace('_', ' ')}")
        print("-" * 40)
        for artifact, passed, desc in checks:
            status = "PASS" if passed else "FAIL"
            icon = "✓" if passed else "✗"
            print(f"  {icon} [{status}] {desc}")
            if passed:
                total_pass += 1
            else:
                total_fail += 1

    if cross_checks:
        print("\nCROSS-REFERENCE CHECKS")
        print("-" * 40)
        for check_name, passed, desc in cross_checks:
            status = "PASS" if passed else "FAIL"
            icon = "✓" if passed else "✗"
            print(f"  {icon} [{status}] {desc}")
            if passed:
                total_pass += 1
            else:
                total_fail += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {total_pass} passed, {total_fail} failed")
    print("=" * 60)

    return total_pass, total_fail


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    results = validate_phase3_artifacts(repo_root)
    cross_checks = cross_reference_checks(repo_root)
    passed, failed = print_validation_report(results, cross_checks)
    exit(0 if failed == 0 else 1)
