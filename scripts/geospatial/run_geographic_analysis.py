#!/usr/bin/env python3
"""
Geographic analysis script for Philadelphia crime incidents.
Performs spatial analysis, generates interactive maps, and identifies hotspots.
"""

import sys
import argparse
import json
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.data.loader import load_crime_data
from src.geospatial.analyzer import GeoAnalyzer


def main():
    """Main function to run geographic analysis on crime data."""
    parser = argparse.ArgumentParser(
        description="Perform geographic analysis on Philadelphia crime incidents"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="crime_incidents_combined.parquet",
        help="Input file path (relative to data/processed/). Default: crime_incidents_combined.parquet",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="visualizations",
        help="Output directory for results. Default: visualizations",
    )
    parser.add_argument(
        "--generate-maps",
        type=bool,
        default=True,
        help="Whether to generate interactive maps. Default: True",
    )
    parser.add_argument(
        "--district-col",
        type=str,
        default="district",
        help="Column name for geographic district/area. Default: district",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("PHILADELPHIA CRIME INCIDENTS - GEOGRAPHIC ANALYSIS")
    print("=" * 80)

    try:
        # Create output directory if it doesn't exist
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the crime data
        print("\nStep 1: Loading crime data...")
        df = load_crime_data(args.input)
        print(f"✓ Loaded {len(df)} crime incidents")

        # Initialize GeoAnalyzer
        print("\nStep 2: Initializing geographic analyzer...")
        analyzer = GeoAnalyzer(df)
        print("✓ GeoAnalyzer initialized")

        # Initialize GeoDataFrame from coordinates
        print("\nStep 3: Creating GeoDataFrame from coordinates...")
        gdf = analyzer.initialize_geodataframe(lat_col="latitude", lon_col="longitude")
        print(f"✓ Created GeoDataFrame with {len(gdf)} geometries")

        # Validate coordinates
        print("\nStep 4: Validating coordinates...")
        is_valid = analyzer.validate_coordinates(
            df, lat_col="latitude", lon_col="longitude"
        )
        if is_valid:
            print("✓ All coordinates are valid")

        # Generate interactive map if requested
        if args.generate_maps:
            print("\nStep 5: Generating interactive map...")
            map_file = str(output_dir / "crime_incidents_map.html")
            map_obj = analyzer.create_interactive_map(
                lat_col="latitude",
                lon_col="longitude",
                crime_type_col="ucr_general",
                output_file=map_file,
            )
            print(f"✓ Interactive map saved to {map_file}")

            # Identify hotspots
            print("\nStep 6: Identifying geographic hotspots...")
            hotspots = analyzer.identify_hotspots(
                lat_col="latitude",
                lon_col="longitude",
                bandwidth=0.01,
                grid_size=50,
            )
            hotspots_file = str(output_dir / "hotspots.json")
            with open(hotspots_file, "w") as f:
                json.dump(hotspots, f, indent=2)
            print(f"✓ Identified {len(hotspots['hotspots'])} top hotspots")
            print(f"✓ Hotspot data saved to {hotspots_file}")

        # Analyze spatial distribution
        print("\nStep 7: Analyzing spatial distribution patterns...")
        distribution = analyzer.analyze_spatial_distribution(
            lat_col="latitude", lon_col="longitude"
        )
        distribution_file = str(output_dir / "spatial_distribution.json")
        with open(distribution_file, "w") as f:
            json.dump(distribution, f, indent=2)
        print(f"✓ Spatial distribution analysis saved to {distribution_file}")
        print(f"  - Total incidents: {distribution['total_incidents']}")
        print(
            f"  - Latitude range: {distribution['latitude_range']['min']:.4f} to {distribution['latitude_range']['max']:.4f}"
        )
        print(
            f"  - Longitude range: {distribution['longitude_range']['min']:.4f} to {distribution['longitude_range']['max']:.4f}"
        )

        # Compare area density
        if args.district_col and args.district_col in df.columns:
            print(f"\nStep 8: Comparing crime density across {args.district_col}s...")
            area_density = analyzer.compare_area_density(
                area_col=args.district_col,
                lat_col="latitude",
                lon_col="longitude",
            )
            density_file = str(output_dir / "area_density.parquet")
            area_density.to_parquet(density_file)
            print(f"✓ Area density analysis saved to {density_file}")
            print(f"✓ Analyzed {len(area_density)} areas")
            print("\nTop 5 highest density areas:")
            for idx, row in area_density.head(5).iterrows():
                print(
                    f"  - {row['area']}: {row['density_per_sq_degree']:.4f} incidents/sq°"
                )

        # Save summary statistics
        print("\nStep 9: Saving summary statistics...")
        summary = {
            "total_incidents": len(df),
            "total_areas": len(df[args.district_col].unique())
            if args.district_col in df.columns
            else 0,
            "data_columns": list(df.columns),
            "spatial_distribution": distribution,
        }
        summary_file = str(output_dir / "analysis_summary.json")
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary statistics saved to {summary_file}")

        print("\n" + "=" * 80)
        print("✓ GEOGRAPHIC ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nResults saved to: {output_dir.absolute()}")
        print("Files generated:")
        print(f"  - crime_incidents_map.html (interactive map)")
        print(f"  - hotspots.json (KDE-based hotspot coordinates and density)")
        print(f"  - spatial_distribution.json (distribution statistics)")
        print(f"  - area_density.parquet (density by {args.district_col})")
        print(f"  - analysis_summary.json (summary statistics)")

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure the processed crime data exists in data/processed/")
        return 1
    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
