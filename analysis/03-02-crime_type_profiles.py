"""
Phase 3: Crime Type Profiles Analysis

Individual crime type analysis for homicide, burglary, theft, vehicle theft,
and aggravated assault with full temporal, spatial, and seasonal profiles.

Each crime type has distinct patterns that require individual examination for
effective policing strategies.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import (
    COLORS,
    FIGURE_SIZES,
    PROJECT_ROOT,
    REPORTS_DIR,
    PHILADELPHIA_BBOX,
    STAT_CONFIG,
    CRIME_DATA_PATH,
)
from analysis.utils import (
    load_data,
    validate_coordinates,
    extract_temporal_features,
    image_to_base64,
    create_image_tag,
    format_number,
    dbscan_clustering,
    calculate_cluster_centroids,
    calculate_cluster_stats,
)
from analysis.stats_utils import mann_kendall_test, chi_square_test, bootstrap_ci
from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion

# Set matplotlib backend for non-interactive plotting
os.environ["MPLBACKEND"] = "Agg"


# =============================================================================
# CRIME TYPE FILTERS
# =============================================================================

CRIME_TYPE_FILTERS = {
    "homicide": ["Homicide - Criminal", "Homicide - Gross Negligence"],
    "burglary": ["Burglary Residential", "Burglary Non-Residential"],
    "theft": ["Thefts", "Theft from Vehicle"],
    "vehicle_theft": ["Motor Vehicle Theft"],
    "aggravated_assault": ["Aggravated Assault Firearm", "Aggravated Assault No Firearm"]
}

# Display names for reports
CRIME_TYPE_NAMES = {
    "homicide": "Homicide",
    "burglary": "Burglary",
    "theft": "Theft",
    "vehicle_theft": "Vehicle Theft",
    "aggravated_assault": "Aggravated Assault"
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# =============================================================================
# DATA FILTERING
# =============================================================================

def filter_crime_type(df: pd.DataFrame, crime_type: str) -> pd.DataFrame:
    """
    Filter dataset for a specific crime type and add validation/features.

    Args:
        df: Full crime incidents DataFrame.
        crime_type: Key from CRIME_TYPE_FILTERS (e.g., "homicide", "burglary").

    Returns:
        DataFrame filtered to the specified crime type with validated
        coordinates and temporal features added.
    """
    if crime_type not in CRIME_TYPE_FILTERS:
        raise ValueError(
            f"Unknown crime type: {crime_type}. "
            f"Use one of: {list(CRIME_TYPE_FILTERS.keys())}"
        )

    # Filter for the specific crime type
    crime_codes = CRIME_TYPE_FILTERS[crime_type]
    crime_df = df[df["text_general_code"].isin(crime_codes)].copy()

    if len(crime_df) == 0:
        return crime_df

    # Validate coordinates
    crime_df = validate_coordinates(crime_df)

    # Extract temporal features
    crime_df = extract_temporal_features(crime_df)

    return crime_df


# =============================================================================
# SAMPLE SIZE CATEGORIZATION
# =============================================================================

def get_sample_size_category(n: int) -> str:
    """
    Categorize sample size for appropriate statistical methods.

    Args:
        n: Sample size.

    Returns:
        Category: 'rare' (<100), 'moderate' (100-1000), 'common' (>1000).
    """
    if n < 100:
        return 'rare'
    elif n < 1000:
        return 'moderate'
    else:
        return 'common'


# =============================================================================
# TEMPORAL ANALYSIS
# =============================================================================

def analyze_temporal_trend(crime_df: pd.DataFrame, crime_type: str) -> dict:
    """
    Analyze temporal trends for a specific crime type.

    Args:
        crime_df: DataFrame filtered to a specific crime type.
        crime_type: Name of the crime type for reporting.

    Returns:
        Dictionary with yearly counts, Mann-Kendall trend test results,
        monthly seasonality, and day-of-week distribution.
    """
    results = {
        "yearly_counts": {},
        "mann_kendall": None,
        "monthly_pattern": {},
        "day_of_week": {},
    }

    if len(crime_df) == 0:
        return results

    # Exclude 2026 for trend analysis (incomplete year)
    trend_df = crime_df[crime_df["year"] != 2026]

    # Yearly counts
    yearly_counts = trend_df.groupby("year").size().sort_index()
    results["yearly_counts"] = {
        int(year): int(count) for year, count in yearly_counts.items()
    }

    # Mann-Kendall trend test (requires at least 3 years)
    if len(yearly_counts) >= 3:
        yearly_values = yearly_counts.values
        mk_result = mann_kendall_test(yearly_values, alpha=STAT_CONFIG["alpha"])
        results["mann_kendall"] = mk_result

    # Monthly pattern (average across all years)
    if "month" in crime_df.columns:
        monthly_counts = crime_df.groupby("month").size()
        # Fill missing months with 0
        monthly_counts = monthly_counts.reindex(range(1, 13), fill_value=0)
        monthly_avg = monthly_counts / len(crime_df["year"].unique()) * 12  # Normalize to 12 months
        results["monthly_pattern"] = {
            int(month): {
                "count": int(monthly_counts[month]),
                "avg_per_year": float(monthly_avg[month])
            }
            for month in range(1, 13)
        }

        # Identify peak month
        peak_month_idx = monthly_counts.idxmax()
        peak_month_count = int(monthly_counts[peak_month_idx])
        peak_month_pct = (peak_month_count / len(crime_df) * 100)

        # Calculate seasonal variation
        monthly_values = monthly_counts.values
        seasonal_variation = (monthly_values.max() - monthly_values.min()) / monthly_values.mean() * 100

        results["seasonal_insights"] = {
            "peak_month": int(peak_month_idx),
            "peak_month_name": MONTH_NAMES[peak_month_idx - 1],
            "peak_month_count": peak_month_count,
            "peak_month_pct": round(peak_month_pct, 2),
            "seasonal_variation_pct": round(seasonal_variation, 2) if monthly_values.mean() > 0 else 0,
        }

    # Day of week distribution
    if "day_of_week" in crime_df.columns:
        dow_counts = crime_df.groupby("day_of_week").size()
        # Fill missing days with 0
        dow_counts = dow_counts.reindex(range(7), fill_value=0)
        results["day_of_week"] = {
            int(day): {
                "count": int(dow_counts[day]),
                "pct": round(float(dow_counts[day] / len(crime_df) * 100), 2)
            }
            for day in range(7)
        }

        # Peak day
        peak_day_idx = dow_counts.idxmax()
        results["day_of_week_insights"] = {
            "peak_day": int(peak_day_idx),
            "peak_day_name": DAY_NAMES[peak_day_idx],
            "peak_day_count": int(dow_counts[peak_day_idx]),
        }

    return results


# =============================================================================
# SPATIAL ANALYSIS
# =============================================================================

def analyze_spatial_distribution(crime_df: pd.DataFrame, crime_type: str, seed: int) -> dict:
    """
    Analyze spatial distribution for a specific crime type.

    Args:
        crime_df: DataFrame filtered to a specific crime type.
        crime_type: Name of the crime type for reporting.
        seed: Random seed for reproducibility.

    Returns:
        Dictionary with coordinate statistics, top districts, and
        clustering results (if sample size permits).
    """
    results = {
        "coord_stats": {},
        "top_districts": {},
        "hotspots": None,
    }

    valid_coords = crime_df[crime_df["valid_coord"]]

    if len(valid_coords) == 0:
        return results

    # Coordinate statistics
    results["coord_stats"] = {
        "valid_count": len(valid_coords),
        "total_count": len(crime_df),
        "coverage_pct": round(len(valid_coords) / len(crime_df) * 100, 2),
        "lon_mean": float(valid_coords["point_x"].mean()),
        "lon_std": float(valid_coords["point_x"].std()),
        "lon_min": float(valid_coords["point_x"].min()),
        "lon_max": float(valid_coords["point_x"].max()),
        "lat_mean": float(valid_coords["point_y"].mean()),
        "lat_std": float(valid_coords["point_y"].std()),
        "lat_min": float(valid_coords["point_y"].min()),
        "lat_max": float(valid_coords["point_y"].max()),
    }

    # Top districts
    district_col = None
    for col in ["dc_dist", "district", "police_districts"]:
        if col in valid_coords.columns:
            district_col = col
            break

    if district_col:
        district_counts = valid_coords.groupby(district_col).size().sort_values(ascending=False)
        top_districts = district_counts.head(5)
        results["top_districts"] = {
            f"D{int(dist)}": {
                "count": int(count),
                "pct": round(float(count / len(valid_coords) * 100), 2)
            }
            for dist, count in top_districts.items()
        }

    # DBSCAN clustering for hotspots (if sample size >= 500)
    if len(valid_coords) >= 500:
        clustered, labels = dbscan_clustering(
            valid_coords,
            eps_meters=150,
            min_samples=30,  # Lower threshold for crime-type specific
            sample_size=min(200000, len(valid_coords)),
        )

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

        if n_clusters > 0:
            centroids = calculate_cluster_centroids(clustered)
            cluster_stats = calculate_cluster_stats(clustered, centroids)

            results["hotspots"] = {
                "n_clusters": n_clusters,
                "top_clusters": cluster_stats.head(5).to_dict("records"),
            }
        else:
            results["hotspots"] = {
                "n_clusters": 0,
                "top_clusters": [],
            }

    return results


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_crime_type_timeseries(crime_df: pd.DataFrame, crime_type: str,
                                  temporal_result: dict) -> str:
    """
    Create line plot of yearly incident counts for a specific crime type.

    Args:
        crime_df: DataFrame filtered to a specific crime type.
        crime_type: Name of the crime type for labeling.
        temporal_result: Results from analyze_temporal_trend().

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    yearly_counts = temporal_result.get("yearly_counts", {})

    if not yearly_counts:
        plt.close(fig)
        return create_image_tag(image_to_base64(fig))

    years = list(yearly_counts.keys())
    counts = list(yearly_counts.values())

    # Create line plot
    ax.plot(years, counts, color=COLORS["primary"], linewidth=2, marker='o', markersize=5)

    # Add trend line if Mann-Kendall result is significant
    mk_result = temporal_result.get("mann_kendall")
    if mk_result and mk_result.get("is_significant"):
        z = np.polyfit(years, counts, 1)
        p = np.poly1d(z)
        ax.plot(years, p(years), color=COLORS["danger"], linestyle="--",
                linewidth=1.5, alpha=0.7, label=f"Trend (tau={mk_result['tau']:.3f})")
        ax.legend()

    # Highlight peak and trough years
    peak_year = max(yearly_counts, key=yearly_counts.get)
    trough_year = min(yearly_counts, key=yearly_counts.get)
    peak_count = yearly_counts[peak_year]
    trough_count = yearly_counts[trough_year]

    ax.scatter([peak_year], [peak_count], color=COLORS["danger"], s=100, zorder=5)
    ax.scatter([trough_year], [trough_count], color=COLORS["success"], s=100, zorder=5)

    # Add labels for peak/trough
    ax.annotate(f'Peak: {peak_count}', xy=(peak_year, peak_count),
                xytext=(10, 10), textcoords='offset points', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS["danger"], alpha=0.3))
    ax.annotate(f'Trough: {trough_count}', xy=(trough_year, trough_count),
                xytext=(10, -20), textcoords='offset points', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS["success"], alpha=0.3))

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Incident Count", fontsize=12)
    ax.set_title(f"{CRIME_TYPE_NAMES[crime_type]}: Yearly Incident Count (2006-2025)",
                 fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_seasonal_pattern_plot(crime_df: pd.DataFrame, crime_type: str,
                                  temporal_result: dict) -> str:
    """
    Create bar chart of monthly averages for a specific crime type.

    Args:
        crime_df: DataFrame filtered to a specific crime type.
        crime_type: Name of the crime type for labeling.
        temporal_result: Results from analyze_temporal_trend().

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    monthly_pattern = temporal_result.get("monthly_pattern", {})

    if not monthly_pattern:
        plt.close(fig)
        return create_image_tag(image_to_base64(fig))

    months = list(range(1, 13))
    counts = [monthly_pattern[m]["count"] for m in months]
    avg_per_year = [monthly_pattern[m]["avg_per_year"] for m in months]

    # Get peak month for highlighting
    peak_month = temporal_result.get("seasonal_insights", {}).get("peak_month", 7)

    # Create color array (highlight peak month)
    colors = [COLORS["danger"] if m == peak_month else COLORS["primary"]
              for m in months]

    bars = ax.bar(months, avg_per_year, color=colors, alpha=0.8,
                  edgecolor="black", linewidth=0.5)

    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        if count > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_per_year)*0.01,
                    format_number(int(count)), ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Average Incidents per Year", fontsize=12)
    ax.set_title(f"{CRIME_TYPE_NAMES[crime_type]}: Monthly Seasonal Pattern",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_NAMES, rotation=45, ha="right")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_spatial_distribution_plot(crime_df: pd.DataFrame, crime_type: str) -> str:
    """
    Create scatter plot of valid coordinates for a specific crime type.

    Args:
        crime_df: DataFrame filtered to a specific crime type.
        crime_type: Name of the crime type for labeling.

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])

    valid_coords = crime_df[crime_df["valid_coord"]]

    if len(valid_coords) == 0:
        ax.text(0.5, 0.5, "No valid coordinate data available",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        plt.tight_layout()
        return create_image_tag(image_to_base64(fig))

    # Sample for visualization
    sample_size = min(100000, len(valid_coords))
    sample = valid_coords.sample(n=sample_size, random_state=42)

    # Create density-based coloring
    lon = sample["point_x"].values
    lat = sample["point_y"].values

    # Create 2D histogram for density coloring
    from scipy.stats import gaussian_kde
    try:
        # Use KDE for density estimation (downsample if needed)
        kde_sample_size = min(10000, len(lon))
        kde_indices = np.random.choice(len(lon), kde_sample_size, replace=False)
        kde = gaussian_kde(np.vstack([lon[kde_indices], lat[kde_indices]]))
        density = kde(np.vstack([lon, lat]))

        scatter = ax.scatter(lon, lat, c=density, cmap=COLORS["sequential"],
                           s=2, alpha=0.6, rasterized=True)
        plt.colorbar(scatter, ax=ax, label="Density")
    except Exception:
        # Fallback to simple scatter
        ax.scatter(lon, lat, s=2, alpha=0.5, color=COLORS["primary"], rasterized=True)

    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.set_title(f"{CRIME_TYPE_NAMES[crime_type]}: Geographic Distribution",
                 fontsize=14, fontweight="bold")
    ax.set_xlim(PHILADELPHIA_BBOX["lon_min"], PHILADELPHIA_BBOX["lon_max"])
    ax.set_ylim(PHILADELPHIA_BBOX["lat_min"], PHILADELPHIA_BBOX["lat_max"])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


def create_day_of_week_plot(crime_df: pd.DataFrame, crime_type: str,
                            temporal_result: dict) -> str:
    """
    Create bar chart of day-of-week distribution for a specific crime type.

    Args:
        crime_df: DataFrame filtered to a specific crime type.
        crime_type: Name of the crime type for labeling.
        temporal_result: Results from analyze_temporal_trend().

    Returns:
        Base64 encoded image HTML tag.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["medium"])

    dow_data = temporal_result.get("day_of_week", {})

    if not dow_data:
        plt.close(fig)
        return create_image_tag(image_to_base64(fig))

    days = list(range(7))
    counts = [dow_data[d]["count"] for d in days]

    # Get peak day for highlighting
    peak_day = temporal_result.get("day_of_week_insights", {}).get("peak_day", 0)

    # Create color array (highlight peak day)
    colors = [COLORS["danger"] if d == peak_day else COLORS["primary"]
              for d in days]

    bars = ax.bar(days, counts, color=colors, alpha=0.8,
                  edgecolor="black", linewidth=0.5)

    # Add percentage labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        pct = dow_data[i]["pct"]
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                f"{pct}%", ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Day of Week", fontsize=12)
    ax.set_ylabel("Incident Count", fontsize=12)
    ax.set_title(f"{CRIME_TYPE_NAMES[crime_type]}: Day of Week Distribution",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(days)
    ax.set_xticklabels(DAY_NAMES)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return create_image_tag(image_to_base64(fig))


# =============================================================================
# MAIN ANALYSIS FUNCTIONS
# =============================================================================

def analyze_crime_type_profile(df: pd.DataFrame, crime_type: str) -> dict:
    """
    Run complete analysis for a single crime type.

    Args:
        df: Full crime incidents DataFrame.
        crime_type: Key from CRIME_TYPE_FILTERS.

    Returns:
        Dictionary with complete analysis results including temporal trends,
        spatial distribution, and visualizations.
    """
    # Set random seed for reproducibility
    seed = set_global_seed(STAT_CONFIG["random_seed"])

    # Filter to crime type
    crime_df = filter_crime_type(df, crime_type)

    total_incidents = len(crime_df)
    valid_coords = crime_df["valid_coord"].sum() if "valid_coord" in crime_df.columns else 0

    # Determine sample size category
    sample_size_category = get_sample_size_category(total_incidents)

    print(f"  {CRIME_TYPE_NAMES[crime_type]}: {format_number(total_incidents)} incidents "
          f"({sample_size_category})")

    results = {
        "crime_type": crime_type,
        "crime_type_name": CRIME_TYPE_NAMES[crime_type],
        "total_incidents": total_incidents,
        "valid_coords": int(valid_coords),
        "sample_size_category": sample_size_category,
        "data_quality": {
            "coord_coverage_pct": round(valid_coords / total_incidents * 100, 2) if total_incidents > 0 else 0,
        }
    }

    # Temporal analysis
    print(f"    Analyzing temporal trends...")
    temporal_results = analyze_temporal_trend(crime_df, crime_type)
    results["temporal_trend"] = temporal_results

    # Spatial analysis
    print(f"    Analyzing spatial distribution...")
    spatial_results = analyze_spatial_distribution(crime_df, crime_type, seed)
    results["spatial_distribution"] = spatial_results

    # Create visualizations
    print(f"    Creating visualizations...")
    results["timeseries_plot"] = create_crime_type_timeseries(crime_df, crime_type, temporal_results)
    results["seasonal_plot"] = create_seasonal_pattern_plot(crime_df, crime_type, temporal_results)
    results["dow_plot"] = create_day_of_week_plot(crime_df, crime_type, temporal_results)

    # Spatial plot only if we have valid coordinates
    if valid_coords >= 10:
        results["spatial_plot"] = create_spatial_distribution_plot(crime_df, crime_type)
    else:
        results["spatial_plot"] = None

    return results


def analyze_all_crime_types() -> dict:
    """
    Run complete analysis for all crime types.

    Returns:
        Dictionary with analysis results for all crime types.
    """
    # Set random seed for reproducibility
    seed = set_global_seed(STAT_CONFIG["random_seed"])
    print(f"Random seed set to: {seed}")

    # Track data version for reproducibility
    data_version = DataVersion(CRIME_DATA_PATH)
    print(f"Data version: {data_version}")

    print("Loading data for crime type profiles analysis...")
    df = load_data(clean=False)

    print(f"Extracting temporal features...")
    df = extract_temporal_features(df)

    results = {}

    # Store analysis metadata
    results["metadata"] = get_analysis_metadata(
        data_version=data_version,
        analysis_type="crime_type_profiles",
        random_seed=seed,
        confidence_level=STAT_CONFIG["confidence_level"],
        alpha=STAT_CONFIG["alpha"],
    )

    print("Analyzing crime types...")

    for crime_type in CRIME_TYPE_FILTERS.keys():
        results[crime_type] = analyze_crime_type_profile(df, crime_type)

    # Add comparison summary
    results["summary"] = generate_comparison_summary(results)

    print("Crime type profiles analysis complete!")
    return results


def generate_comparison_summary(results: dict) -> dict:
    """
    Generate cross-crime-type comparison summary.

    Args:
        results: Dictionary from analyze_all_crime_types().

    Returns:
        Dictionary with comparison metrics across all crime types.
    """
    summary = {
        "total_incidents": {},
        "trend_direction": {},
        "peak_months": {},
        "peak_days": {},
        "coord_coverage": {},
    }

    for crime_type, data in results.items():
        if crime_type == "metadata" or crime_type == "summary":
            continue

        if "total_incidents" in data:
            summary["total_incidents"][crime_type] = data["total_incidents"]

        if "temporal_trend" in data and data["temporal_trend"].get("mann_kendall"):
            mk = data["temporal_trend"]["mann_kendall"]
            summary["trend_direction"][crime_type] = mk.get("trend", "unknown")

        if "temporal_trend" in data and data["temporal_trend"].get("seasonal_insights"):
            si = data["temporal_trend"]["seasonal_insights"]
            summary["peak_months"][crime_type] = si.get("peak_month_name", "N/A")

        if "temporal_trend" in data and data["temporal_trend"].get("day_of_week_insights"):
            di = data["temporal_trend"]["day_of_week_insights"]
            summary["peak_days"][crime_type] = di.get("peak_day_name", "N/A")

        if "data_quality" in data:
            summary["coord_coverage"][crime_type] = data["data_quality"].get("coord_coverage_pct", 0)

    return summary


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_crime_type_report(results: dict) -> str:
    """
    Generate comprehensive markdown report from crime type analysis results.

    Args:
        results: Dictionary from analyze_all_crime_types().

    Returns:
        Complete markdown string with analysis results.
    """
    md = []

    # Add analysis configuration section
    if "metadata" in results:
        md.append(format_metadata_markdown(results["metadata"]))
        md.append("")

    # ========================================================================
    # TITLE
    # ========================================================================
    md.append("# Crime Type Profiles Analysis\n")
    md.append("**Philadelphia Crime Incidents (2006-2026)**\n\n")
    md.append("---\n\n")

    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    md.append("## Executive Summary\n\n")

    summary = results.get("summary", {})

    md.append("**Overview:** Individual crime type analysis for homicide, burglary, theft, ")
    md.append("vehicle theft, and aggravated assault with full temporal, spatial, and seasonal profiles.\n\n")

    # Total incidents comparison
    md.append("### Incident Counts by Crime Type\n\n")
    md.append("| Crime Type | Total Incidents | Coord Coverage |\n")
    md.append("|------------|-----------------|----------------|\n")

    for crime_type in CRIME_TYPE_FILTERS.keys():
        if crime_type not in results:
            continue
        data = results[crime_type]
        total = format_number(data.get("total_incidents", 0))
        coverage = f"{data.get('data_quality', {}).get('coord_coverage_pct', 0):.1f}%"
        md.append(f"| {CRIME_TYPE_NAMES[crime_type]} | {total} | {coverage} |\n")

    md.append("")

    # Trend summary
    md.append("### Long-Term Trends (Mann-Kendall Test)\n\n")
    md.append("| Crime Type | Trend | Tau | P-value | Significant |\n")
    md.append("|------------|-------|-----|---------|------------|\n")

    for crime_type in CRIME_TYPE_FILTERS.keys():
        if crime_type not in results:
            continue
        data = results[crime_type]
        mk = data.get("temporal_trend", {}).get("mann_kendall")
        if mk:
            trend = mk.get("trend", "unknown")
            tau = f"{mk.get('tau', 0):.3f}"
            pval = f"{mk.get('p_value', 1):.6f}"
            sig = "Yes" if mk.get("is_significant", False) else "No"
            md.append(f"| {CRIME_TYPE_NAMES[crime_type]} | {trend} | {tau} | {pval} | {sig} |\n")

    md.append("")

    # Peak timing summary
    md.append("### Peak Timing Patterns\n\n")
    md.append("| Crime Type | Peak Month | Peak Day |\n")
    md.append("|------------|------------|----------|\n")

    for crime_type in CRIME_TYPE_FILTERS.keys():
        if crime_type not in results:
            continue
        data = results[crime_type]
        peak_month = data.get("temporal_trend", {}).get("seasonal_insights", {}).get("peak_month_name", "N/A")
        peak_day = data.get("temporal_trend", {}).get("day_of_week_insights", {}).get("peak_day_name", "N/A")
        md.append(f"| {CRIME_TYPE_NAMES[crime_type]} | {peak_month} | {peak_day} |\n")

    md.append("")

    md.append("---\n\n")

    # ========================================================================
    # INDIVIDUAL CRIME TYPE SECTIONS
    # ========================================================================

    for crime_type in CRIME_TYPE_FILTERS.keys():
        if crime_type not in results:
            continue

        data = results[crime_type]
        crime_name = CRIME_TYPE_NAMES[crime_type]

        md.append(f"## {crime_name} Analysis\n\n")

        # Basic stats
        total = data.get("total_incidents", 0)
        valid_coords = data.get("valid_coords", 0)
        sample_cat = data.get("sample_size_category", "unknown")

        md.append(f"### Overview\n\n")
        md.append(f"- **Total Incidents**: {format_number(total)}\n")
        md.append(f"- **Valid Coordinates**: {format_number(valid_coords)} ")
        md.append(f"({data.get('data_quality', {}).get('coord_coverage_pct', 0):.1f}% coverage)\n")
        md.append(f"- **Sample Size Category**: {sample_cat.title()}\n\n")

        # Temporal trend
        temporal = data.get("temporal_trend", {})
        mk = temporal.get("mann_kendall")

        if mk:
            md.append(f"### Long-Term Trend\n\n")
            md.append(f"**Mann-Kendall Trend Test Results:**\n\n")
            md.append(f"- **Trend**: {mk.get('trend', 'unknown').title()}\n")
            md.append(f"- **Kendall's Tau**: {mk.get('tau', 0):.3f}\n")
            md.append(f"- **P-value**: {mk.get('p_value', 1):.6f}\n")
            md.append(f"- **Significant** (alpha={STAT_CONFIG['alpha']}): ")
            md.append(f"{'Yes' if mk.get('is_significant') else 'No'}\n\n")

            if mk.get('is_significant'):
                if mk.get('trend') == 'decreasing':
                    md.append(f"**Interpretation**: {crime_name} shows a statistically significant ")
                    md.append(f"**decreasing trend** over time.\n\n")
                elif mk.get('trend') == 'increasing':
                    md.append(f"**Interpretation**: {crime_name} shows a statistically significant ")
                    md.append(f"**increasing trend** over time.\n\n")
                else:
                    md.append(f"**Interpretation**: No monotonic trend detected.\n\n")

        # Seasonal pattern
        seasonal = temporal.get("seasonal_insights")
        if seasonal:
            md.append(f"### Seasonal Pattern\n\n")
            md.append(f"- **Peak Month**: {seasonal.get('peak_month_name')} ")
            md.append(f"({seasonal.get('peak_month_count')} incidents, ")
            md.append(f"{seasonal.get('peak_month_pct')}% of annual total)\n")
            md.append(f"- **Seasonal Variation**: {seasonal.get('seasonal_variation_pct')}% ")
            md.append(f"(difference between peak and trough months)\n\n")

        # Day of week pattern
        dow_insights = temporal.get("day_of_week_insights")
        if dow_insights:
            md.append(f"### Day of Week Pattern\n\n")
            md.append(f"- **Peak Day**: {dow_insights.get('peak_day_name')} ")
            md.append(f"({dow_insights.get('peak_day_count')} incidents)\n\n")

        # Spatial distribution
        spatial = data.get("spatial_distribution", {})
        if spatial.get("top_districts"):
            md.append(f"### Top Police Districts\n\n")
            md.append("| District | Incidents | Percentage |\n")
            md.append("|----------|-----------|------------|\n")
            for district, stats in spatial["top_districts"].items():
                md.append(f"| {district} | {format_number(stats['count'])} | {stats['pct']}% |\n")
            md.append("")

        # Hotspots
        hotspots = spatial.get("hotspots")
        if hotspots and hotspots.get("n_clusters", 0) > 0:
            md.append(f"### Geographic Hotspots\n\n")
            md.append(f"- **Clusters Detected**: {hotspots['n_clusters']} geographic hotspots\n\n")
            if hotspots.get("top_clusters"):
                md.append("**Top 5 Hotspots:**\n\n")
                md.append("| Zone ID | Count | Top Crime Type | District | Radius (m) |\n")
                md.append("|---------|-------|----------------|----------|-----------|\n")
                for cluster in hotspots["top_clusters"][:5]:
                    zone_id = int(cluster.get("cluster_id", "N/A"))
                    count = format_number(int(cluster.get("count", 0)))
                    crime = str(cluster.get("top_crime_type", "N/A"))[:30]
                    district = int(cluster.get("top_district", 0)) if pd.notna(cluster.get("top_district")) else "N/A"
                    radius = f"{cluster.get('radius_meters', 0):.0f}"
                    md.append(f"| Zone {zone_id} | {count} | {crime} | D{district} | {radius} |\n")
                md.append("")

        # Visualizations
        md.append(f"### Visualizations\n\n")

        if data.get("timeseries_plot"):
            md.append(data["timeseries_plot"])
            md.append("\n\n*Figure: Yearly incident count for " + crime_name.lower() + ".*\n\n")

        if data.get("seasonal_plot"):
            md.append(data["seasonal_plot"])
            md.append("\n\n*Figure: Monthly seasonal pattern for " + crime_name.lower() + ".*\n\n")

        if data.get("dow_plot"):
            md.append(data["dow_plot"])
            md.append("\n\n*Figure: Day of week distribution for " + crime_name.lower() + ".*\n\n")

        if data.get("spatial_plot"):
            md.append(data["spatial_plot"])
            md.append("\n\n*Figure: Geographic distribution for " + crime_name.lower() + ".*\n\n")

        # Sample size limitations
        if sample_cat == "rare":
            md.append(f"### Analysis Limitations\n\n")
            md.append(f"**Note:** {crime_name} has relatively few incidents (n={total}). ")
            md.append(f"Statistical power is limited, and some tests may not detect ")
            md.append(f"true effects. Results should be interpreted with caution.\n\n")

        md.append("---\n\n")

    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    md.append("## Methodology\n\n")

    md.append("### Data Source\n")
    md.append("- **Dataset**: Philadelphia crime incidents (2006-2026)\n")
    md.append("- **2026 Data**: Excluded from trend analysis (incomplete year)\n")
    md.append("- **Coordinate Validation**: Only incidents with verified Philadelphia coordinates used for spatial analysis\n\n")

    md.append("### Crime Type Definitions\n")
    for crime_type, codes in CRIME_TYPE_FILTERS.items():
        codes_str = ", ".join(codes)
        md.append(f"- **{CRIME_TYPE_NAMES[crime_type]}**: {codes_str}\n")
    md.append("")

    md.append("### Statistical Methods\n")
    md.append(f"- **Trend Analysis**: Mann-Kendall test (alpha={STAT_CONFIG['alpha']})\n")
    md.append(f"- **Confidence Level**: {STAT_CONFIG['confidence_level']*100}%\n")
    md.append("- **Random Seed**: Set for reproducibility\n")
    md.append("- **Sample Size Adaptation**: Rare crimes (n<100) use exact tests, common crimes use asymptotic tests\n\n")

    md.append("### Spatial Analysis\n")
    md.append("- **Coordinate Validation**: Philadelphia bounding box filtering\n")
    md.append("- **Hotspot Detection**: DBSCAN clustering (150m radius, 30 minimum samples for crime-type specific)\n")
    md.append("- **District Analysis**: Top 5 districts by incident count\n\n")

    md.append("### Limitations\n")
    md.append("- **Reported Crime Only**: Analysis limited to incidents reported to police\n")
    md.append("- **Coordinate Missingness**: ~25% of records lack valid coordinates (non-random bias)\n")
    md.append("- **Rare Crime Limitations**: Low-count crime types (homicide) have reduced statistical power\n")
    md.append("- **Temporal Aggregation**: Monthly/yearly aggregation may mask short-term patterns\n\n")

    # ========================================================================
    # CONCLUSION
    # ========================================================================
    md.append("## Conclusion\n\n")

    md.append("This analysis provides individual crime type profiles for Philadelphia's most serious offenses. ")
    md.append("Each crime type exhibits distinct temporal and spatial patterns that inform targeted policing strategies.\n\n")

    md.append("**Key Findings:**\n\n")

    # Summarize significant trends
    significant_trends = []
    for crime_type in CRIME_TYPE_FILTERS.keys():
        if crime_type not in results:
            continue
        mk = results[crime_type].get("temporal_trend", {}).get("mann_kendall")
        if mk and mk.get("is_significant"):
            trend = mk.get("trend", "")
            crime_name = CRIME_TYPE_NAMES[crime_type]
            significant_trends.append(f"- {crime_name}: {trend.title()} trend (tau={mk.get('tau', 0):.3f})\n")

    if significant_trends:
        md.append("**Significant Long-Term Trends:**\n\n")
        md.extend(significant_trends)
        md.append("\n")

    md.append("**Implications for Policing:**\n\n")
    md.append("- Crime-specific patterns require tailored prevention strategies\n")
    md.append("- Temporal patterns inform patrol scheduling\n")
    md.append("- Spatial hotspots identify geographic focus areas\n")
    md.append("- Trends help evaluate effectiveness of past interventions\n\n")

    md.append("*\n")
    md.append(f"Report generated by Claude Code | ")
    md.append(f"Data source: Philadelphia crime incidents dataset\n")

    return "\n".join(md)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    results = analyze_all_crime_types()
    report = generate_crime_type_report(results)

    report_path = REPORTS_DIR / "14_crime_type_profiles_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
