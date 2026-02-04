#!/usr/bin/env python3
"""Download and cache boundary data for Phase 2 spatial analysis.

This script downloads:
1. Police district boundaries from OpenDataPhilly
2. Census tract boundaries with population from Census Bureau/Census Reporter

The script is idempotent - it skips downloads if files already exist.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Resolve paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BOUNDARIES_DIR = REPO_ROOT / "data" / "boundaries"

# Police district URLs
POLICE_DISTRICTS_PRIMARY = (
    "https://opendata.arcgis.com/datasets/62ec63afb8824a15953399b1fa819df2_0.geojson"
)
POLICE_DISTRICTS_FALLBACK = (
    "https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+police_districts&format=geojson"
)

# Census tract URLs - using Census Reporter for pre-joined data
# Philadelphia County FIPS: 42101
CENSUS_TRACTS_PRIMARY = (
    "https://api.census.gov/data/2020/acs/acs5?"
    "get=B01003_001E,NAME&for=tract:*&in=state:42&in=county:101"
)
CENSUS_TRACTS_GEOJSON = "https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_42_tract.zip"
# Alternative: Census Reporter API for pre-joined data
CENSUS_REPORTER_TRACTS = (
    "https://api.censusreporter.org/1.0/geo/show/tiger2020?geo_ids=14000US42101*"
)

REQUEST_TIMEOUT = 60  # seconds


def download_json(url: str, timeout: int = REQUEST_TIMEOUT) -> dict:
    """Download JSON from URL with error handling."""
    logger.info(f"Downloading from: {url[:80]}...")
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def download_police_districts(output_path: Path) -> tuple[bool, str]:
    """Download police district boundaries.

    Returns:
        Tuple of (success, source_used)
    """
    if output_path.exists():
        logger.info(f"Police districts already cached: {output_path}")
        gdf = gpd.read_file(output_path)
        logger.info(f"Cached file has {len(gdf)} districts")
        return True, "cached"

    # Try primary URL
    try:
        data = download_json(POLICE_DISTRICTS_PRIMARY)
        source = "primary (ArcGIS)"
    except (requests.RequestException, json.JSONDecodeError) as e:
        logger.warning(f"Primary URL failed: {e}")
        # Try fallback
        try:
            data = download_json(POLICE_DISTRICTS_FALLBACK)
            source = "fallback (Carto)"
        except (requests.RequestException, json.JSONDecodeError) as e2:
            logger.error(f"Fallback URL also failed: {e2}")
            return False, "failed"

    # Save GeoJSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f)

    # Load and standardize
    gdf = gpd.read_file(output_path)

    # Add standardized dist_num column (integer) for joining with crime data
    if "dist_numc" in gdf.columns:
        gdf["dist_num"] = pd.to_numeric(gdf["dist_numc"], errors="coerce").astype("Int64")
    elif "dist_num" in gdf.columns:
        gdf["dist_num"] = pd.to_numeric(gdf["dist_num"], errors="coerce").astype("Int64")

    # Re-save with standardized column
    gdf.to_file(output_path, driver="GeoJSON")

    district_count = len(gdf)
    logger.info(f"Downloaded {district_count} police districts from {source}")

    # Note: Philadelphia has 21 geographic police districts (some numbers skipped)
    # Crime data may reference additional administrative district codes
    if district_count < 20 or district_count > 25:
        logger.warning(f"District count {district_count} outside expected range (20-25)")

    if "dist_num" in gdf.columns:
        logger.info(f"District numbers: {sorted(gdf['dist_num'].dropna().unique())}")

    return True, source


def download_census_tracts_with_pop(output_path: Path) -> tuple[bool, str]:
    """Download census tract boundaries with population data.

    Returns:
        Tuple of (success, source_used)
    """
    if output_path.exists():
        logger.info(f"Census tracts already cached: {output_path}")
        gdf = gpd.read_file(output_path)
        logger.info(f"Cached file has {len(gdf)} tracts")
        if "total_pop" in gdf.columns:
            total_pop = gdf["total_pop"].sum()
            logger.info(f"Total population: {total_pop:,.0f}")
        return True, "cached"

    # Try Census Reporter API first (pre-joined with geography)
    try:
        logger.info("Trying Census Reporter API for pre-joined tract data...")
        response = requests.get(CENSUS_REPORTER_TRACTS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        geojson_data = response.json()

        # Census Reporter returns GeoJSON with properties
        gdf = gpd.GeoDataFrame.from_features(geojson_data["features"], crs="EPSG:4326")
        source = "Census Reporter API"

        # Rename population column if present
        if "population" in gdf.columns:
            gdf = gdf.rename(columns={"population": "total_pop"})
        elif "B01003001" in gdf.columns:
            gdf = gdf.rename(columns={"B01003001": "total_pop"})

    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Census Reporter failed: {e}")

        # Fallback: Download TIGER shapefile + ACS population separately
        try:
            logger.info("Falling back to TIGER + ACS API...")

            # Download ACS population data
            acs_response = requests.get(CENSUS_TRACTS_PRIMARY, timeout=REQUEST_TIMEOUT)
            acs_response.raise_for_status()
            acs_data = acs_response.json()

            # Parse ACS response (first row is headers)
            headers = acs_data[0]
            rows = acs_data[1:]
            pop_df = pd.DataFrame(rows, columns=headers)
            pop_df["GEOID"] = "42" + pop_df["county"] + pop_df["tract"]
            pop_df["total_pop"] = pd.to_numeric(pop_df["B01003_001E"], errors="coerce")
            pop_df = pop_df[["GEOID", "NAME", "total_pop"]]

            # Download TIGER tract shapefile
            logger.info("Downloading TIGER tract boundaries for PA...")
            gdf = gpd.read_file(CENSUS_TRACTS_GEOJSON)

            # Filter to Philadelphia County (42101)
            gdf = gdf[gdf["COUNTYFP"] == "101"].copy()

            # Join population data
            gdf = gdf.merge(pop_df, on="GEOID", how="left")
            gdf = gdf.to_crs("EPSG:4326")
            source = "TIGER + ACS API"

        except (requests.RequestException, Exception) as e2:
            logger.error(f"TIGER + ACS fallback also failed: {e2}")
            return False, "failed"

    # Ensure we have Philadelphia tracts only
    if "COUNTYFP" in gdf.columns:
        gdf = gdf[gdf["COUNTYFP"] == "101"].copy()

    # Validate tract count and population
    tract_count = len(gdf)
    logger.info(f"Downloaded {tract_count} census tracts from {source}")

    if "total_pop" in gdf.columns:
        total_pop = gdf["total_pop"].sum()
        logger.info(f"Total population: {total_pop:,.0f}")

        # Validate population range
        pop_max = gdf["total_pop"].max()
        if pop_max > 15000:
            logger.warning(f"Some tracts have population > 15,000 (max: {pop_max})")

        if total_pop < 1_400_000 or total_pop > 1_700_000:
            logger.warning(f"Total population {total_pop:,.0f} outside expected range (1.4M-1.7M)")
    else:
        logger.warning("No population column found in census tract data")

    if tract_count < 350 or tract_count > 420:
        logger.warning(f"Tract count {tract_count} outside expected range (350-420)")

    # Save to GeoJSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")
    logger.info(f"Saved census tracts to: {output_path}")

    return True, source


def main() -> int:
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Phase 2 Boundary Data Download")
    logger.info("=" * 60)

    BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    # Download police districts
    police_path = BOUNDARIES_DIR / "police_districts.geojson"
    success, source = download_police_districts(police_path)
    results.append(("Police Districts", success, source))

    # Download census tracts
    census_path = BOUNDARIES_DIR / "census_tracts_pop.geojson"
    success, source = download_census_tracts_with_pop(census_path)
    results.append(("Census Tracts", success, source))

    # Summary
    logger.info("=" * 60)
    logger.info("Download Summary")
    logger.info("=" * 60)

    all_success = True
    for name, success, source in results:
        status = "OK" if success else "FAILED"
        logger.info(f"  {name}: {status} (source: {source})")
        if not success:
            all_success = False

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
