"""Download highway and transit corridor data for Phase 3."""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import LineString


def download_highways_osm(bbox: tuple) -> gpd.GeoDataFrame:
    """Download highway data from OpenStreetMap.

    Parameters
    ----------
    bbox : tuple
        Bounding box as (min_lat, min_lon, max_lat, max_lon)

    Returns
    -------
    gpd.GeoDataFrame
        Highway geometries
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"="motorway"]["ref"~"I 95|I-95|I 76|I-76|I 676|I-676|US 1|US-1"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      way["highway"="trunk"]["ref"~"I 95|I-95|I 76|I-76|I 676|I-676|US 1|US-1"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      way["highway"="motorway_link"]["ref"~"I 95|I-95|I 76|I-76|I 676|I-676"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out geom;
    """

    response = requests.get(overpass_url, params={"data": query}, timeout=120)
    response.raise_for_status()
    data = response.json()

    # Convert to GeoDataFrame
    features = []
    for element in data.get("elements", []):
        if element.get("type") == "way" and "geometry" in element:
            coords = [(n["lon"], n["lat"]) for n in element["geometry"]]
            if len(coords) >= 2:
                ref = element.get("tags", {}).get("ref", "Unknown")
                # Normalize highway names
                name = ref.replace("-", " ").strip()
                features.append(
                    {
                        "geometry": LineString(coords),
                        "name": name,
                        "type": "highway",
                        "osm_id": element.get("id"),
                    }
                )

    if features:
        return gpd.GeoDataFrame(features, crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=["geometry", "name", "type", "osm_id"], crs="EPSG:4326")


def create_fallback_highways() -> gpd.GeoDataFrame:
    """Create approximate highway centerlines as fallback.

    Used when OSM download fails.
    """
    # Approximate I-95 through Philadelphia
    i95_coords = [
        (-75.0495, 39.8559),  # South Philadelphia
        (-75.1264, 39.8876),  # Near airport
        (-75.1381, 39.9283),  # Center City east
        (-75.1200, 39.9600),  # North of Center City
        (-75.0892, 40.0170),  # Northeast Philadelphia
        (-75.0175, 40.1356),  # Near Bucks County
    ]

    # Approximate I-76 (Schuylkill Expressway)
    i76_coords = [
        (-75.1556, 39.9552),  # Center City (30th St)
        (-75.1900, 39.9580),  # University City
        (-75.2252, 39.9596),  # West Philadelphia
        (-75.2600, 39.9700),  # Manayunk approach
        (-75.2879, 39.9783),  # Manayunk
    ]

    # Approximate I-676 (Vine Street Expressway)
    i676_coords = [
        (-75.1200, 39.9570),  # I-95 junction
        (-75.1400, 39.9580),  # Callowhill
        (-75.1550, 39.9575),  # City Hall area
        (-75.1750, 39.9555),  # Benjamin Franklin Parkway
    ]

    # Approximate US-1 (Roosevelt Boulevard)
    us1_coords = [
        (-75.1000, 40.0500),  # Northeast Philly
        (-75.0800, 40.0800),  # Further north
        (-75.0600, 40.1000),  # Near Bucks
    ]

    features = [
        {
            "geometry": LineString(i95_coords),
            "name": "I 95",
            "type": "highway",
            "osm_id": None,
        },
        {
            "geometry": LineString(i76_coords),
            "name": "I 76",
            "type": "highway",
            "osm_id": None,
        },
        {
            "geometry": LineString(i676_coords),
            "name": "I 676",
            "type": "highway",
            "osm_id": None,
        },
        {
            "geometry": LineString(us1_coords),
            "name": "US 1",
            "type": "highway",
            "osm_id": None,
        },
    ]

    return gpd.GeoDataFrame(features, crs="EPSG:4326")


def create_septa_lines() -> gpd.GeoDataFrame:
    """Create simplified SEPTA subway line geometries.

    Note: For production, use official SEPTA GTFS data.
    These are approximate centerlines for corridor analysis.
    """
    # Market-Frankford Line (east-west, roughly)
    mfl_coords = [
        (-75.0825, 40.0170),  # Frankford Transportation Center
        (-75.0977, 40.0184),  # Church Street area
        (-75.1050, 40.0100),  # Berks area
        (-75.1186, 40.0070),  # Temple University
        (-75.1318, 39.9997),  # Spring Garden
        (-75.1450, 39.9530),  # Race-Vine
        (-75.1556, 39.9546),  # City Hall
        (-75.1620, 39.9540),  # 15th St
        (-75.1700, 39.9540),  # 22nd St
        (-75.1763, 39.9552),  # 30th Street
        (-75.2000, 39.9600),  # 46th St area
        (-75.2096, 39.9623),  # 69th Street Terminal
    ]

    # Broad Street Line (north-south)
    bsl_coords = [
        (-75.1719, 39.9050),  # AT&T Station (NRG)
        (-75.1680, 39.9170),  # Pattison
        (-75.1650, 39.9280),  # Oregon
        (-75.1620, 39.9380),  # Snyder
        (-75.1600, 39.9460),  # Tasker-Morris
        (-75.1590, 39.9546),  # Ellsworth-Federal
        (-75.1575, 39.9630),  # Walnut-Locust
        (-75.1556, 39.9546),  # City Hall
        (-75.1556, 39.9650),  # Race-Vine
        (-75.1556, 39.9750),  # Spring Garden
        (-75.1556, 39.9850),  # Fairmount
        (-75.1556, 39.9950),  # Girard
        (-75.1556, 40.0050),  # Cecil B. Moore
        (-75.1500, 40.0200),  # Erie
        (-75.1480, 40.0335),  # Fern Rock
    ]

    features = [
        {
            "geometry": LineString(mfl_coords),
            "name": "Market-Frankford Line",
            "type": "subway",
            "osm_id": None,
        },
        {
            "geometry": LineString(bsl_coords),
            "name": "Broad Street Line",
            "type": "subway",
            "osm_id": None,
        },
    ]

    return gpd.GeoDataFrame(features, crs="EPSG:4326")


def main():
    """Download corridor data and save to GeoJSON."""
    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / "data" / "boundaries" / "corridors.geojson"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Philadelphia bounding box (min_lat, min_lon, max_lat, max_lon)
    bbox = (39.85, -75.30, 40.15, -74.95)

    # Try OSM first, fall back to manual if it fails
    print("Attempting to download highway data from OpenStreetMap...")
    try:
        highways = download_highways_osm(bbox)
        if len(highways) > 0:
            print(f"Downloaded {len(highways)} highway segments from OSM")
        else:
            print("No highways found in OSM response, using fallback...")
            highways = create_fallback_highways()
            print(f"Created {len(highways)} fallback highway segments")
    except Exception as e:
        print(f"OSM download failed: {e}")
        print("Using fallback manual highway definitions...")
        highways = create_fallback_highways()
        print(f"Created {len(highways)} fallback highway segments")

    # Create SEPTA lines
    septa = create_septa_lines()
    print(f"Created {len(septa)} SEPTA subway line segments")

    # Combine and save
    corridors = gpd.GeoDataFrame(pd.concat([highways, septa], ignore_index=True), crs="EPSG:4326")

    # Clean up the data
    corridors["name"] = corridors["name"].fillna("Unknown")
    corridors["type"] = corridors["type"].fillna("unknown")

    corridors.to_file(output_path, driver="GeoJSON")
    print(f"\nSaved {len(corridors)} corridor features to {output_path}")

    # Summary
    print("\nCorridor Summary:")
    print(corridors.groupby("type")["name"].value_counts().to_string())


if __name__ == "__main__":
    main()
