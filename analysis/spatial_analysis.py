"""
Phase 4: Spatial Analysis

Analyzes geographic distribution, clustering, and location patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PHILADELPHIA_BBOX, PROJECT_ROOT, STAT_CONFIG
from analysis.utils import load_data, validate_coordinates, image_to_base64, create_image_tag, format_number
from analysis.stats_utils import compare_multiple_samples, apply_fdr_correction, bootstrap_ci, cohens_d, interpret_cohens_d
from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion


def analyze_spatial_patterns() -> dict:
    """
    Run comprehensive spatial analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    # Set random seed for reproducibility
    seed = set_global_seed(STAT_CONFIG["random_seed"])
    print(f"Random seed set to: {seed}")

    # Track data version for reproducibility
    from analysis.config import CRIME_DATA_PATH
    data_version = DataVersion(CRIME_DATA_PATH)
    print(f"Data version: {data_version}")

    print("Loading data for spatial analysis...")
    df = load_data(clean=False)

    print("Validating coordinates...")
    df = validate_coordinates(df)

    results = {}

    # Store analysis metadata
    results["analysis_metadata"] = get_analysis_metadata(
        data_version=data_version,
        analysis_type="spatial_analysis",
        random_seed=seed,
        confidence_level=STAT_CONFIG["confidence_level"],
        alpha=STAT_CONFIG["alpha"],
    )

    # ========================================================================
    # 1. Coordinate Statistics
    # ========================================================================
    print("Calculating coordinate statistics...")

    valid_coords = df[df["valid_coord"]]

    coord_stats = {
        "total_records": len(df),
        "valid_coordinates": len(valid_coords),
        "invalid_coordinates": len(df) - len(valid_coords),
        "valid_pct": len(valid_coords) / len(df) * 100,
        "lon_min": float(valid_coords["point_x"].min()),
        "lon_max": float(valid_coords["point_x"].max()),
        "lat_min": float(valid_coords["point_y"].min()),
        "lat_max": float(valid_coords["point_y"].max()),
        "lon_mean": float(valid_coords["point_x"].mean()),
        "lat_mean": float(valid_coords["point_y"].mean()),
    }
    results["coord_stats"] = coord_stats

    # ========================================================================
    # 1.5 Statistical Analysis: District Comparison
    # ========================================================================
    print("Performing district-level statistical comparison...")

    # Get district column
    dc_dist_col = "dc_dist" if "dc_dist" in df.columns else "dc_dist"
    if dc_dist_col not in df.columns:
        for col in df.columns:
            if "dist" in col.lower():
                dc_dist_col = col
                break

    # Count crimes per district
    district_counts = valid_coords.groupby(dc_dist_col).size()
    districts_with_data = district_counts[district_counts >= 30].index.tolist()  # Minimum sample size

    if len(districts_with_data) >= 3:
        # Prepare data for comparison: sample coordinates per district
        district_groups = {}
        for district in districts_with_data:
            dist_data = valid_coords[valid_coords[dc_dist_col] == district]
            # Use crime density as metric (sample of valid coordinates)
            district_groups[f"D{int(district)}"] = dist_data["point_x"].values

        # Run omnibus test (Kruskal-Wallis or ANOVA)
        omnibus_result = compare_multiple_samples(
            district_groups,
            alpha=STAT_CONFIG["alpha"]
        )
        results["district_comparison"] = omnibus_result

        # Bootstrap CI for mean crimes per district
        print("Calculating bootstrap confidence intervals...")
        district_mean_cis = {}

        # Use crime density metric: incidents per district (bootstrap over district means)
        district_crime_counts = []
        district_names = []
        for district in districts_with_data:
            dist_count = district_counts[district]
            district_crime_counts.append(dist_count)
            district_names.append(f"D{int(district)}")

        district_crime_counts = np.array(district_crime_counts)

        # Bootstrap CI for overall mean crimes per district
        lower_mean, upper_mean, estimate_mean, se_mean = bootstrap_ci(
            district_crime_counts,
            statistic="mean",
            confidence_level=STAT_CONFIG["confidence_level"],
            n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_state=seed,
        )

        results["district_mean_ci"] = {
            "overall_mean": float(estimate_mean),
            "ci_lower": float(lower_mean),
            "ci_upper": float(upper_mean),
            "std_error": float(se_mean),
            "n_districts": len(districts_with_data),
        }

        # Store individual district counts
        results["district_counts"] = {
            f"D{int(district)}": int(count)
            for district, count in district_counts.items()
        }

        # Calculate hotspot threshold (95th percentile of district counts for practical use)
        hotspot_threshold = np.percentile(district_counts.values, 95)
        lower_ht, upper_ht, estimate_ht, se_ht = bootstrap_ci(
            district_counts.values,
            statistic=lambda x: np.percentile(x, 95),
            confidence_level=STAT_CONFIG["confidence_level"],
            n_resamples=STAT_CONFIG["bootstrap_n_resamples"],
            random_state=seed,
        )
        results["hotspot_threshold_ci"] = {
            "threshold": float(hotspot_threshold),
            "ci_lower": float(lower_ht),
            "ci_upper": float(upper_ht),
            "std_error": float(se_ht),
        }

        print(f"  Omnibus test: {omnibus_result['omnibus_test']}, p={omnibus_result['p_value']:.6f}")
        print(f"  Significant differences: {omnibus_result['is_significant']}")

        # Post-hoc pairwise comparisons if omnibus is significant
        if omnibus_result["is_significant"]:
            print("  Running post-hoc pairwise comparisons...")
            pairwise_results = []
            district_names = list(district_groups.keys())

            for i, dist_a in enumerate(district_names):
                for dist_b in district_names[i+1:]:
                    # Cohen's d for effect size
                    d = cohens_d(district_groups[dist_a], district_groups[dist_b])
                    interpretation = interpret_cohens_d(d)

                    pairwise_results.append({
                        "district_a": dist_a,
                        "district_b": dist_b,
                        "cohens_d": float(d),
                        "effect_size": interpretation,
                        "mean_a": float(np.mean(district_groups[dist_a])),
                        "mean_b": float(np.mean(district_groups[dist_b])),
                    })

            pairwise_df = pd.DataFrame(pairwise_results)

            # Apply FDR correction
            # We don't have p-values from cohens_d, so we use a simple approach
            # In practice, you'd run Mann-Whitney U for each pair
            # For now, just report effect sizes
            results["pairwise_comparisons"] = pairwise_df

            print(f"  Completed {len(pairwise_df)} pairwise comparisons")
    else:
        print(f"  Not enough districts with sufficient data (need >=3, got {len(districts_with_data)})")
        results["district_comparison"] = None

    # ========================================================================
    # 2. Geographic Scatter Plot (Full City View)
    # ========================================================================
    print("Creating city-wide scatter plot...")

    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES["wide"])

    # Sample for visualization
    sample_size = min(100000, len(valid_coords))
    sample = valid_coords.sample(n=sample_size, random_state=42)

    # Left plot: All incidents with transparency
    ax = axes[0]
    scatter = ax.scatter(
        sample["point_x"],
        sample["point_y"],
        alpha=0.3,
        s=1,
        c=COLORS["primary"],
        rasterized=True,
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Philadelphia Crime Incidents Geographic Distribution\n(Sample of {format_number(sample_size)} points)")
    ax.set_aspect("equal", adjustable="box")

    # Right plot: Density heatmap
    ax = axes[1]
    hb = ax.hexbin(
        sample["point_x"],
        sample["point_y"],
        gridsize=50,
        cmap=COLORS["sequential"],
        alpha=0.8,
        mincnt=1,
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Crime Density Heatmap")
    ax.set_aspect("equal", adjustable="box")
    cb = plt.colorbar(hb, ax=ax, label="Incident Count")

    plt.tight_layout()
    results["geo_scatter_density"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 3. High-Resolution Density Map
    # ========================================================================
    print("Creating high-resolution density map...")

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    # Use larger sample for better resolution
    sample_large = valid_coords.sample(n=min(200000, len(valid_coords)), random_state=42)

    hb = ax.hexbin(
        sample_large["point_x"],
        sample_large["point_y"],
        gridsize=80,
        cmap="YlOrRd",
        alpha=0.9,
        mincnt=1,
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("High-Resolution Crime Density Map")
    ax.set_aspect("equal", adjustable="box")
    cb = plt.colorbar(hb, ax=ax, label="Incident Count per Bin")

    plt.tight_layout()
    results["density_map_highres"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 4. Coordinate Bounding Box Analysis
    # ========================================================================
    print("Analyzing coordinate bounds...")

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    # Draw bounding box
    bbox_x = [PHILADELPHIA_BBOX["lon_min"], PHILADELPHIA_BBOX["lon_max"],
              PHILADELPHIA_BBOX["lon_max"], PHILADELPHIA_BBOX["lon_min"],
              PHILADELPHIA_BBOX["lon_min"]]
    bbox_y = [PHILADELPHIA_BBOX["lat_min"], PHILADELPHIA_BBOX["lat_min"],
              PHILADELPHIA_BBOX["lat_max"], PHILADELPHIA_BBOX["lat_max"],
              PHILADELPHIA_BBOX["lat_min"]]

    # Plot actual data bounds
    ax.plot(bbox_x, bbox_y, "g--", linewidth=2, label="Expected Philadelphia BBox", alpha=0.7)

    # Plot actual data extent
    actual_x = [coord_stats["lon_min"], coord_stats["lon_max"],
                coord_stats["lon_max"], coord_stats["lon_min"], coord_stats["lon_min"]]
    actual_y = [coord_stats["lat_min"], coord_stats["lat_min"],
                coord_stats["lat_max"], coord_stats["lat_max"], coord_stats["lat_min"]]
    ax.plot(actual_x, actual_y, "b-", linewidth=2, label="Actual Data Extent")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Coordinate Bounding Box Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal", adjustable="box")

    plt.tight_layout()
    results["bbox_comparison"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 5. District Geographic Distribution
    # ========================================================================
    print("Analyzing district geographic distribution...")

    dc_dist_col = "dc_dist" if "dc_dist" in df.columns else "dc_dist"
    if dc_dist_col not in df.columns:
        for col in df.columns:
            if "dist" in col.lower():
                dc_dist_col = col
                break

    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    # Sample by district for visualization
    sample_per_district = 5000
    district_samples = []

    for district in valid_coords[dc_dist_col].unique():
        dist_data = valid_coords[valid_coords[dc_dist_col] == district]
        if len(dist_data) > 0:
            district_samples.append(dist_data.sample(n=min(sample_per_district, len(dist_data)), random_state=42))

    district_sample = pd.concat(district_samples, ignore_index=True)

    # Create categorical scatter
    districts = sorted(district_sample[dc_dist_col].unique())
    cmap = plt.cm.get_cmap("tab20", len(districts))

    for i, district in enumerate(districts):
        dist_data = district_sample[district_sample[dc_dist_col] == district]
        ax.scatter(dist_data["point_x"], dist_data["point_y"],
                   c=[cmap(i)], s=1, alpha=0.5, label=f"D{int(district)}", rasterized=True)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Crime Distribution by Police District")

    # Create a simplified legend
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) > 26:
        # Show only every other district legend
        step = 2
        ax.legend(handles[::step], labels[::step], loc="upper left",
                  bbox_to_anchor=(1.02, 1), fontsize=7, ncol=2)
    else:
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=7, ncol=2)

    ax.set_aspect("equal", adjustable="box")

    plt.tight_layout()
    results["district_geo_distribution"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 6. Location Block Analysis
    # ========================================================================
    print("Analyzing location blocks...")

    if "location_block" in df.columns:
        location_counts = df["location_block"].value_counts().head(20).reset_index()
        location_counts.columns = ["location", "count"]
        location_counts["percentage"] = (location_counts["count"] / len(df) * 100).round(2)
        results["top_locations"] = location_counts

        # Top locations bar chart
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

        # Truncate long location names
        location_counts["location_short"] = location_counts["location"].str[:40]

        bars = ax.barh(location_counts["location_short"], location_counts["count"], color=COLORS["secondary"])
        ax.set_xlabel("Incident Count")
        ax.set_ylabel("Location Block")
        ax.set_title("Top 20 Crime Location Blocks")
        ax.invert_yaxis()

        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                    f" {format_number(int(width))}", va="center", fontsize=8)

        plt.tight_layout()
        results["top_locations_chart"] = create_image_tag(image_to_base64(fig))
        plt.close(fig)

    # ========================================================================
    # 7. Coordinate Distribution Histograms
    # ========================================================================
    print("Creating coordinate distribution histograms...")

    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES["wide"])

    # Longitude distribution
    ax = axes[0]
    ax.hist(valid_coords["point_x"], bins=100, color=COLORS["primary"], alpha=0.7, edgecolor="black")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Frequency")
    ax.set_title("Longitude Distribution")
    ax.axvline(coord_stats["lon_mean"], color=COLORS["danger"], linestyle="--", linewidth=2, label=f"Mean: {coord_stats['lon_mean']:.4f}")
    ax.legend()

    # Latitude distribution
    ax = axes[1]
    ax.hist(valid_coords["point_y"], bins=100, color=COLORS["secondary"], alpha=0.7, edgecolor="black")
    ax.set_xlabel("Latitude")
    ax.set_ylabel("Frequency")
    ax.set_title("Latitude Distribution")
    ax.axvline(coord_stats["lat_mean"], color=COLORS["danger"], linestyle="--", linewidth=2, label=f"Mean: {coord_stats['lat_mean']:.4f}")
    ax.legend()

    plt.tight_layout()
    results["coord_distribution"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    print("Spatial analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from spatial analysis results.

    Args:
        results: Dictionary from analyze_spatial_patterns()

    Returns:
        Markdown string with analysis results.
    """
    md = []

    # Add analysis configuration section
    if "analysis_metadata" in results:
        md.append(format_metadata_markdown(results["analysis_metadata"]))
        md.append("")

    md.append("### Spatial Analysis\n")

    # Coordinate Statistics
    md.append("#### 1. Coordinate Statistics\n\n")

    coord_stats = results["coord_stats"]
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Records | {format_number(coord_stats['total_records'])} |")
    md.append(f"| Valid Coordinates | {format_number(coord_stats['valid_coordinates'])} |")
    md.append(f"| Invalid Coordinates | {format_number(coord_stats['invalid_coordinates'])} |")
    md.append(f"| Data Coverage | {coord_stats['valid_pct']:.2f}% |")
    md.append(f"| Longitude Range | {coord_stats['lon_min']:.4f} to {coord_stats['lon_max']:.4f} |")
    md.append(f"| Latitude Range | {coord_stats['lat_min']:.4f} to {coord_stats['lat_max']:.4f} |")
    md.append(f"| Center (mean) | ({coord_stats['lon_mean']:.4f}, {coord_stats['lat_mean']:.4f}) |")
    md.append("")

    # District Comparison Statistics
    if results.get("district_comparison") is not None:
        md.append("#### 1.1 District-Level Statistical Comparison\n\n")
        district_comp = results["district_comparison"]

        md.append(f"**Omnibus Test:** {district_comp['omnibus_test']}\n\n")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Test Statistic | {district_comp['statistic']:.4f} |")
        md.append(f"| P-value | {district_comp['p_value']:.6e} |")
        md.append(f"| Significant (alpha={STAT_CONFIG['alpha']}) | {'Yes' if district_comp['is_significant'] else 'No'} |")
        md.append(f"| All Groups Normal | {'Yes' if district_comp['all_normal'] else 'No'} |")
        md.append("")

        # Bootstrap CIs for district statistics
        if "district_mean_ci" in results and "district_counts" in results:
            ci_data = results["district_mean_ci"]
            md.append(f"**99% CI for Mean Crimes per District** (across {ci_data['n_districts']} districts):\n\n")
            md.append(f"| Metric | Value |")
            md.append(f"|--------|-------|")
            md.append(f"| Overall Mean | {int(ci_data['overall_mean']):,} incidents |")
            md.append(f"| 99% CI Lower | {int(ci_data['ci_lower']):,} |")
            md.append(f"| 99% CI Upper | {int(ci_data['ci_upper']):,} |")
            md.append(f"| Std Error | {ci_data['std_error']:.2f} |")
            md.append("")

            # Top districts by count
            md.append("**District Counts** (Top 10):\n\n")
            md.append("| District | Count |")
            md.append("|----------|-------|")

            sorted_districts = sorted(
                results["district_counts"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            for district, count in sorted_districts:
                md.append(f"| {district} | {count:,} |")
            md.append("")

        # Hotspot threshold CI
        if "hotspot_threshold_ci" in results:
            ht_ci = results["hotspot_threshold_ci"]
            md.append(f"**Hotspot Threshold** (99th percentile of district counts):\n\n")
            md.append(f"| Metric | Value |")
            md.append(f"|--------|-------|")
            md.append(f"| Threshold | {int(ht_ci['threshold']):,} incidents |")
            md.append(f"| 99% CI Lower | {int(ht_ci['ci_lower']):,} |")
            md.append(f"| 99% CI Upper | {int(ht_ci['ci_upper']):,} |")
            md.append(f"| Std Error | {ht_ci['std_error']:.2f} |")
            md.append("")

        # Top pairwise comparisons by effect size
        if "pairwise_comparisons" in results and len(results["pairwise_comparisons"]) > 0:
            pairwise = results["pairwise_comparisons"].nlargest(10, "cohens_d", key=abs)
            md.append("**Top 10 District Pairs by Effect Size** (Cohen's d):\n\n")
            md.append("| District A | District B | Cohen's d | Effect Size | Mean A | Mean B |")
            md.append("|------------|------------|-----------|-------------|--------|--------|")
            for _, row in pairwise.iterrows():
                md.append(f"| {row['district_a']} | {row['district_b']} | {row['cohens_d']:.3f} | {row['effect_size']} | {row['mean_a']:.4f} | {row['mean_b']:.4f} |")
            md.append("")

        md.append("**Note:** Standard statistical tests assume independence of observations. ")
        md.append("Spatial data often exhibits autocorrelation, which may affect p-values. ")
        md.append("For true spatial autocorrelation testing (Moran's I), consider using pysal/libpysal.\n\n")

    md.append(results["geo_scatter_density"])
    md.append("\n")

    # Density Maps
    md.append("#### 2. Crime Density Maps\n\n")

    md.append(results["density_map_highres"])
    md.append("\n")

    # Bounding Box
    md.append("#### 3. Geographic Extent\n\n")

    md.append(results["bbox_comparison"])
    md.append("\n")

    # District Distribution
    md.append("#### 4. District Geographic Distribution\n\n")

    md.append(results["district_geo_distribution"])
    md.append("\n")

    # Coordinate Distribution
    md.append("#### 5. Coordinate Distribution Histograms\n\n")

    md.append(results["coord_distribution"])
    md.append("\n")

    # Top Locations
    if "top_locations" in results:
        md.append("#### 6. Top Crime Location Blocks\n\n")

        top_locations = results["top_locations"]
        md.append("| Rank | Location Block | Count | Percentage |")
        md.append("|------|----------------|-------|------------|")
        for i, row in top_locations.head(10).iterrows():
            md.append(f"| {i+1} | {row['location'][:50]} | {format_number(row['count'])} | {row['percentage']}% |")
        md.append("")

        md.append(results["top_locations_chart"])
        md.append("\n")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_spatial_patterns()
    report = generate_markdown_report(results)

    report_path = PROJECT_ROOT / "reports" / "04_spatial_analysis_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Spatial Analysis Report\n\n")
        f.write(report)

    print(f"\nReport saved to: {report_path}")
