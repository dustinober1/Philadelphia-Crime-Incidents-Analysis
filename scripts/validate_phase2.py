"""Validate Phase 2 artifacts and cross-reference outputs."""

from pathlib import Path
import sys


def validate_phase2(repo_root: Path) -> dict:
    """Validate all Phase 2 artifacts exist and are valid."""

    # Import here to fail gracefully if not installed
    try:
        import geopandas as gpd
        import pandas as pd
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install geopandas pandas")
        sys.exit(1)

    results = {
        "infrastructure": {},
        "hotspots": {},
        "robbery": {},
        "severity": {},
        "census": {},
        "summary": {"passed": 0, "failed": 0, "warnings": 0},
    }

    # === Infrastructure (02-01) ===
    boundaries_dir = repo_root / "data" / "boundaries"

    # Police districts
    police_path = boundaries_dir / "police_districts.geojson"
    if police_path.exists():
        try:
            gdf = gpd.read_file(police_path)
            results["infrastructure"]["police_districts"] = {
                "exists": True,
                "count": len(gdf),
                "valid": len(gdf) >= 20,  # Expect ~21 districts
            }
            results["summary"]["passed"] += 1
        except Exception as e:
            results["infrastructure"]["police_districts"] = {
                "exists": True,
                "error": str(e),
            }
            results["summary"]["failed"] += 1
    else:
        results["infrastructure"]["police_districts"] = {"exists": False}
        results["summary"]["failed"] += 1

    # Census tracts
    census_path = boundaries_dir / "census_tracts_pop.geojson"
    if census_path.exists():
        try:
            gdf = gpd.read_file(census_path)
            has_pop = "total_pop" in gdf.columns or "population" in gdf.columns
            results["infrastructure"]["census_tracts"] = {
                "exists": True,
                "count": len(gdf),
                "has_population": has_pop,
            }
            results["summary"]["passed"] += 1
        except Exception as e:
            results["infrastructure"]["census_tracts"] = {
                "exists": True,
                "error": str(e),
            }
            results["summary"]["failed"] += 1
    else:
        results["infrastructure"]["census_tracts"] = {"exists": False}
        results["summary"]["failed"] += 1

    # Config
    config_path = repo_root / "config" / "phase2_config.yaml"
    results["infrastructure"]["config"] = {"exists": config_path.exists()}
    results["summary"]["passed" if config_path.exists() else "failed"] += 1

    # === Hotspots (02-02) ===
    reports_dir = repo_root / "reports"

    hotspot_files = [
        ("hotspot_heatmap.png", "Static heatmap"),
        ("hotspot_heatmap.html", "Interactive heatmap"),
        ("hotspot_centroids.geojson", "Cluster centroids"),
    ]

    for filename, desc in hotspot_files:
        path = reports_dir / filename
        results["hotspots"][filename] = {
            "exists": path.exists(),
            "description": desc,
            "size_kb": round(path.stat().st_size / 1024, 1) if path.exists() else 0,
        }
        results["summary"]["passed" if path.exists() else "failed"] += 1

    # Validate centroids content
    centroid_path = reports_dir / "hotspot_centroids.geojson"
    if centroid_path.exists():
        try:
            gdf = gpd.read_file(centroid_path)
            results["hotspots"]["centroids_count"] = len(gdf)
        except Exception:
            pass

    # === Robbery (02-03) ===
    robbery_files = [
        ("robbery_temporal_heatmap.png", "Temporal heatmap"),
        ("robbery_patrol_recommendations.md", "Patrol recommendations"),
    ]

    for filename, desc in robbery_files:
        path = reports_dir / filename
        results["robbery"][filename] = {"exists": path.exists(), "description": desc}
        results["summary"]["passed" if path.exists() else "failed"] += 1

    # === Severity (02-04) ===
    severity_files = [
        ("district_severity_choropleth.png", "Choropleth map"),
        ("district_severity_ranking.csv", "Ranking table"),
        ("districts_scored.geojson", "Scored districts"),
    ]

    for filename, desc in severity_files:
        path = reports_dir / filename
        results["severity"][filename] = {"exists": path.exists(), "description": desc}
        results["summary"]["passed" if path.exists() else "failed"] += 1

    # Validate ranking content
    ranking_path = reports_dir / "district_severity_ranking.csv"
    if ranking_path.exists():
        try:
            df = pd.read_csv(ranking_path)
            results["severity"]["districts_ranked"] = len(df)
            results["severity"]["has_severity_score"] = (
                "Severity Score" in df.columns or "severity_score" in df.columns
            )
        except Exception:
            pass

    # === Census (02-05) ===
    census_files = [
        ("tract_crime_rates.png", "Rate choropleth"),
        ("tract_crime_rates.csv", "Tract rates"),
        ("flagged_tracts_report.md", "Flagged tracts"),
    ]

    for filename, desc in census_files:
        path = reports_dir / filename
        results["census"][filename] = {"exists": path.exists(), "description": desc}
        results["summary"]["passed" if path.exists() else "failed"] += 1

    # Validate rates content
    rates_path = reports_dir / "tract_crime_rates.csv"
    if rates_path.exists():
        try:
            df = pd.read_csv(rates_path)
            results["census"]["tracts_with_rates"] = len(df)
            results["census"]["has_crime_rate"] = (
                "crime_rate" in df.columns or "total_crime_rate" in df.columns
            )
        except Exception:
            pass

    return results


def cross_reference_outputs(repo_root: Path) -> dict:
    """Cross-reference Phase 2 outputs for consistency."""

    import geopandas as gpd
    import pandas as pd

    issues = []
    warnings = []
    reports_dir = repo_root / "reports"
    boundaries_dir = repo_root / "data" / "boundaries"

    try:
        # 1. District counts should match across outputs
        severity_path = reports_dir / "districts_scored.geojson"
        police_path = boundaries_dir / "police_districts.geojson"

        if severity_path.exists() and police_path.exists():
            severity_gdf = gpd.read_file(severity_path)
            police_gdf = gpd.read_file(police_path)

            if len(severity_gdf) != len(police_gdf):
                issues.append(
                    f"District count mismatch: severity has {len(severity_gdf)}, boundaries has {len(police_gdf)}"
                )
        else:
            issues.append("Cannot compare district counts - files missing")

        # 2. Census tract counts should be consistent
        tracts_path = boundaries_dir / "census_tracts_pop.geojson"
        rates_path = reports_dir / "tract_crime_rates.csv"

        if tracts_path.exists() and rates_path.exists():
            tracts_gdf = gpd.read_file(tracts_path)
            rates_df = pd.read_csv(rates_path)

            if len(rates_df) > len(tracts_gdf):
                issues.append(
                    f"More tracts with rates ({len(rates_df)}) than in boundaries ({len(tracts_gdf)})"
                )
            elif len(rates_df) < len(tracts_gdf):
                warnings.append(
                    f"Fewer tracts with rates ({len(rates_df)}) than in boundaries ({len(tracts_gdf)}) - some may have been filtered"
                )
        else:
            issues.append("Cannot compare tract counts - files missing")

        # 3. Check hotspot centroids are within Philadelphia bounds
        centroids_path = reports_dir / "hotspot_centroids.geojson"

        if centroids_path.exists() and police_path.exists():
            centroids_gdf = gpd.read_file(centroids_path)
            police_gdf = gpd.read_file(police_path)
            philly_bounds = police_gdf.union_all().bounds  # (minx, miny, maxx, maxy)

            outside_centroids = 0
            for _, row in centroids_gdf.iterrows():
                if not (
                    philly_bounds[0] <= row.geometry.x <= philly_bounds[2]
                    and philly_bounds[1] <= row.geometry.y <= philly_bounds[3]
                ):
                    outside_centroids += 1

            if outside_centroids > 0:
                issues.append(
                    f"{outside_centroids} hotspot centroids outside Philadelphia bounds"
                )
        else:
            warnings.append("Cannot verify centroids bounds - files missing")

    except Exception as e:
        issues.append(f"Cross-reference error: {str(e)}")

    return {"issues": issues, "warnings": warnings, "passed": len(issues) == 0}


def print_results(results: dict, xref: dict) -> None:
    """Print formatted validation results."""

    print("\n" + "=" * 60)
    print("PHASE 2 VALIDATION RESULTS")
    print("=" * 60)

    for category, items in results.items():
        if category == "summary":
            continue
        print(f"\n{category.upper()}")
        print("-" * 40)
        for key, value in items.items():
            if isinstance(value, dict):
                status = "pass" if value.get("exists", False) else "FAIL"
                size_info = (
                    f" ({value.get('size_kb', 0):.1f} KB)"
                    if "size_kb" in value and value.get("exists")
                    else ""
                )
                print(f"  [{status}] {key}{size_info}")
            else:
                print(f"    {key}: {value}")

    print("\n" + "-" * 40)
    print("CROSS-REFERENCE CHECKS")
    print("-" * 40)

    if xref["issues"]:
        for issue in xref["issues"]:
            print(f"  [FAIL] {issue}")
    else:
        print("  [pass] All cross-reference checks passed")

    if xref["warnings"]:
        for warning in xref["warnings"]:
            print(f"  [WARN] {warning}")

    print("\n" + "=" * 60)
    summary = results["summary"]
    xref_status = "passed" if xref["passed"] else "failed"
    print(
        f"SUMMARY: {summary['passed']} passed, {summary['failed']} failed | Cross-ref: {xref_status}"
    )
    print("=" * 60)


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent

    print("Validating Phase 2 artifacts...")
    results = validate_phase2(repo_root)

    print("Running cross-reference checks...")
    xref = cross_reference_outputs(repo_root)

    print_results(results, xref)

    # Exit code based on validation
    all_passed = results["summary"]["failed"] == 0 and xref["passed"]
    sys.exit(0 if all_passed else 1)
