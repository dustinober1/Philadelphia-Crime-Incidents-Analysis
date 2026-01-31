"""
Phase 3: Categorical Analysis

Analyzes crime types, police districts, and police service areas (PSAs).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT, STAT_CONFIG, CRIME_DATA_PATH
from analysis.utils import load_data, image_to_base64, create_image_tag, format_number, classify_crime_category
from analysis.stats_utils import chi_square_test, compare_multiple_samples, apply_fdr_correction, cohens_d, interpret_cohens_d
from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown, DataVersion


def analyze_categorical_data() -> dict:
    """
    Run comprehensive categorical analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    # Set random seed for reproducibility
    seed = set_global_seed(STAT_CONFIG["random_seed"])
    print(f"Random seed set to: {seed}")

    # Track data version for reproducibility
    data_version = DataVersion(CRIME_DATA_PATH)
    print(f"Data version: {data_version}")

    print("Loading data for categorical analysis...")
    df = load_data(clean=False)

    results = {}

    # Store analysis metadata
    results["analysis_metadata"] = get_analysis_metadata(
        data_version=data_version,
        analysis_type="categorical_analysis",
        random_seed=seed,
        confidence_level=STAT_CONFIG["confidence_level"],
        alpha=STAT_CONFIG["alpha"],
    )

    # ========================================================================
    # 1. Crime Type Analysis
    # ========================================================================
    print("Analyzing crime types...")

    text_general = "text_general_code" if "text_general_code" in df.columns else "text_general_code"
    if text_general not in df.columns:
        # Find the crime type column
        for col in df.columns:
            if "text" in col.lower() or "crime" in col.lower() or "offense" in col.lower():
                text_general = col
                break

    crime_counts = df[text_general].value_counts().reset_index()
    crime_counts.columns = ["crime_type", "count"]
    crime_counts["percentage"] = (crime_counts["count"] / len(df) * 100).round(2)
    crime_counts["cumulative_pct"] = crime_counts["percentage"].cumsum()
    results["crime_counts"] = crime_counts

    # Top 15 crime types bar chart
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["large"])
    top_crimes = crime_counts.head(15)

    bars = ax.barh(top_crimes["crime_type"], top_crimes["count"], color=COLORS["primary"])
    ax.set_xlabel("Count")
    ax.set_ylabel("Crime Type")
    ax.set_title("Top 15 Crime Types by Frequency")
    ax.invert_yaxis()

    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2,
                f" {format_number(int(width))}", va="center", fontsize=9)

    plt.tight_layout()
    results["top_crimes_bar"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Crime type distribution (all 32 types)
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])
    all_crimes = crime_counts.copy()

    # Create horizontal bar for all types
    y_pos = np.arange(len(all_crimes))
    bars = ax.barh(y_pos, all_crimes["count"], color=COLORS["secondary"])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(all_crimes["crime_type"])
    ax.set_xlabel("Count")
    ax.set_title("All Crime Types by Frequency")
    ax.invert_yaxis()

    for i, (bar, pct) in enumerate(zip(bars, all_crimes["percentage"])):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2,
                f" {format_number(int(width))} ({pct}%)", va="center", fontsize=7)

    plt.tight_layout()
    results["all_crimes_bar"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Pareto chart (cumulative percentage)
    fig, ax1 = plt.subplots(figsize=FIGURE_SIZES["large"])

    x_pos = np.arange(len(top_crimes))
    ax1.bar(x_pos, top_crimes["count"], color=COLORS["primary"], alpha=0.7, label="Count")
    ax1.set_xlabel("Crime Type (Rank)")
    ax1.set_ylabel("Count", color=COLORS["primary"])
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(top_crimes["crime_type"], rotation=45, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(x_pos, top_crimes["cumulative_pct"], color=COLORS["danger"],
             marker="o", linewidth=2, markersize=5, label="Cumulative %")
    ax2.set_ylabel("Cumulative Percentage", color=COLORS["danger"])
    ax2.axhline(y=80, color="gray", linestyle="--", alpha=0.5, label="80% threshold")
    ax2.set_ylim(0, 105)

    ax1.set_title("Pareto Chart: Crime Type Distribution (Top 15)")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    plt.tight_layout()
    results["pareto_chart"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # Rare crimes (bottom 10)
    rare_crimes = crime_counts.tail(10).copy()
    results["rare_crimes"] = rare_crimes

    # ========================================================================
    # 2. Police District Analysis
    # ========================================================================
    print("Analyzing police districts...")

    dc_dist_col = "dc_dist" if "dc_dist" in df.columns else "dc_dist"
    if dc_dist_col not in df.columns:
        for col in df.columns:
            if "dist" in col.lower():
                dc_dist_col = col
                break

    district_counts = df[dc_dist_col].value_counts().sort_index().reset_index()
    district_counts.columns = ["district", "count"]
    district_counts["percentage"] = (district_counts["count"] / len(df) * 100).round(2)
    results["district_counts"] = district_counts

    # District bar chart
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    bars = ax.bar(district_counts["district"].astype(str), district_counts["count"], color=COLORS["secondary"])

    # Highlight top and bottom districts
    top_dist = district_counts.loc[district_counts["count"].idxmax()]
    bottom_dist = district_counts.loc[district_counts["count"].idxmin()]

    for i, bar in enumerate(bars):
        if bar.get_height() == top_dist["count"]:
            bar.set_color(COLORS["danger"])
        elif bar.get_height() == bottom_dist["count"]:
            bar.set_color(COLORS["success"])

    ax.set_xlabel("Police District")
    ax.set_ylabel("Crime Count")
    ax.set_title(f"Crime Incidents by Police District (Total: {district_counts['district'].nunique()} districts)")
    plt.xticks(rotation=45, ha="right")

    for i, (dist, count) in enumerate(zip(district_counts["district"], district_counts["count"])):
        ax.text(i, count, f" {format_number(count)}", ha="center", va="bottom", fontsize=7)

    plt.tight_layout()
    results["district_bar_chart"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # District distribution pie chart
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["square"])

    # Group smaller districts
    district_copy = district_counts.copy()
    district_copy["district"] = district_copy["district"].astype(str)
    threshold = 0.02  # 2% threshold
    small_mask = district_copy["percentage"] < threshold

    if small_mask.sum() > 0:
        small_sum = district_copy[small_mask]["count"].sum()
        district_copy = district_copy[~small_mask].copy()
        district_copy = pd.concat([
            district_copy,
            pd.DataFrame({"district": ["Other"], "count": [small_sum], "percentage": [small_sum/len(df)*100]})
        ], ignore_index=True)

    colors_list = plt.cm.tab20(np.linspace(0, 1, len(district_copy)))
    wedges, texts, autotexts = ax.pie(
        district_copy["count"],
        labels=district_copy["district"],
        autopct="%1.1f%%",
        colors=colors_list,
        startangle=90,
    )
    ax.set_title("Crime Distribution by District")

    plt.tight_layout()
    results["district_pie_chart"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 3. UCR Code Analysis
    # ========================================================================
    print("Analyzing UCR codes...")

    ucr_col = "ucr_general" if "ucr_general" in df.columns else "ucr_general"
    if ucr_col not in df.columns:
        for col in df.columns:
            if "ucr" in col.lower():
                ucr_col = col
                break

    ucr_counts = df[ucr_col].value_counts().reset_index()
    ucr_counts.columns = ["ucr_code", "count"]
    ucr_counts["percentage"] = (ucr_counts["count"] / len(df) * 100).round(2)
    results["ucr_counts"] = ucr_counts

    # UCR code bar chart
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
    ucr_sorted = ucr_counts.sort_values("ucr_code")

    bars = ax.bar(ucr_sorted["ucr_code"].astype(str), ucr_sorted["count"], color=COLORS["primary"])
    ax.set_xlabel("UCR Code")
    ax.set_ylabel("Count")
    ax.set_title(f"Crime Distribution by UCR Code ({ucr_sorted['ucr_code'].nunique()} unique codes)")
    plt.xticks(rotation=45, ha="right")

    for i, (code, count) in enumerate(zip(ucr_sorted["ucr_code"], ucr_sorted["count"])):
        ax.text(i, count, f" {format_number(count)}", ha="center", va="bottom", fontsize=7)

    plt.tight_layout()
    results["ucr_bar_chart"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    # ========================================================================
    # 3.5 Statistical Analysis: Chi-Square Tests
    # ========================================================================
    print("Performing chi-square tests for categorical associations...")

    # Chi-square test for crime type uniformity
    # Test if crime types are uniformly distributed
    crime_type_counts = df[text_general].value_counts()
    if len(crime_type_counts) >= 2:
        # Build contingency table comparing observed vs expected uniform distribution
        observed = crime_type_counts.values
        expected = np.full_like(observed, observed.mean(), dtype=float)
        # Chi-square goodness of fit
        chi2_stat = np.sum((observed - expected) ** 2 / expected)
        from scipy.stats import chi2 as chi2_dist
        dof = len(observed) - 1
        p_value_uniformity = 1 - chi2_dist.cdf(chi2_stat, dof)

        results["crime_uniformity_test"] = {
            "chi2_statistic": float(chi2_stat),
            "p_value": float(p_value_uniformity),
            "dof": int(dof),
            "is_significant": p_value_uniformity < STAT_CONFIG["alpha"],
            "interpretation": (
                "Crime types are NOT uniformly distributed" if p_value_uniformity < STAT_CONFIG["alpha"]
                else "Crime types appear uniformly distributed"
            ),
        }
        print(f"  Crime type uniformity: chi2={chi2_stat:.2f}, p={p_value_uniformity:.6e}")

    # Chi-square test for crime-district association
    # Test if crime types and districts are independent
    dc_dist_col = "dc_dist" if "dc_dist" in df.columns else "dc_dist"
    if dc_dist_col not in df.columns:
        for col in df.columns:
            if "dist" in col.lower():
                dc_dist_col = col
                break

    # Create contingency table for top 10 crimes x districts
    top_10_crimes = crime_counts.head(10)["crime_type"].tolist()
    crime_district_crosstab = pd.crosstab(df[dc_dist_col], df[text_general])
    crime_district_top = crime_district_crosstab[top_10_crimes]

    if crime_district_top.shape[0] >= 2 and crime_district_top.shape[1] >= 2:
        district_crime_test = chi_square_test(crime_district_top.values)
        results["crime_district_independence"] = district_crime_test

        # Calculate Cramer's V for effect size
        n = crime_district_top.values.sum()
        phi2 = district_crime_test["statistic"] / n
        min_dim = min(crime_district_top.shape[0] - 1, crime_district_top.shape[1] - 1)
        cramers_v = np.sqrt(phi2 / min_dim) if min_dim > 0 else 0

        # Interpret Cramer's V
        if cramers_v < 0.1:
            v_interpret = "negligible association"
        elif cramers_v < 0.3:
            v_interpret = "weak association"
        elif cramers_v < 0.5:
            v_interpret = "moderate association"
        else:
            v_interpret = "strong association"

        results["crime_district_independence"]["cramers_v"] = float(cramers_v)
        results["crime_district_independence"]["cramers_v_interpretation"] = v_interpret

        print(f"  Crime-district independence: chi2={district_crime_test['statistic']:.2f}, p={district_crime_test['p_value']:.6e}")
        print(f"  Cramer's V: {cramers_v:.3f} ({v_interpret})")

    # UCR category comparison
    print("Performing UCR category comparison...")
    df = classify_crime_category(df)
    ucr_category_counts = df["crime_category"].value_counts()

    # Chi-square test for UCR categories
    if len(ucr_category_counts) >= 2:
        # Expected proportions based on national averages or uniform
        # For this analysis, test if distribution differs from uniform
        ucr_observed = ucr_category_counts.values
        ucr_expected = np.full_like(ucr_observed, ucr_observed.mean(), dtype=float)

        ucr_chi2 = np.sum((ucr_observed - ucr_expected) ** 2 / ucr_expected)
        ucr_dof = len(ucr_observed) - 1
        ucr_p_value = 1 - chi2_dist.cdf(ucr_chi2, ucr_dof)

        results["ucr_category_test"] = {
            "chi2_statistic": float(ucr_chi2),
            "p_value": float(ucr_p_value),
            "dof": int(ucr_dof),
            "is_significant": ucr_p_value < STAT_CONFIG["alpha"],
            "category_counts": {k: int(v) for k, v in ucr_category_counts.items()},
            "category_percentages": {
                k: float(v / ucr_observed.sum() * 100) for k, v in ucr_category_counts.items()
            },
        }
        print(f"  UCR category test: chi2={ucr_chi2:.2f}, p={ucr_p_value:.6e}")

    # Pairwise comparisons between UCR categories (if we had counts per category)
    # For now, report the category distribution
    results["ucr_category_distribution"] = ucr_category_counts.to_dict()

    # ========================================================================
    # 4. PSA Analysis (if available)
    # ========================================================================
    print("Analyzing PSAs...")

    if "psa" in df.columns:
        psa_counts = df["psa"].value_counts().sort_index().reset_index()
        psa_counts.columns = ["psa", "count"]
        results["psa_counts"] = psa_counts

        # Top 20 PSAs
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["wide"])
        top_psas = psa_counts.nlargest(20, "count")

        bars = ax.bar(top_psas["psa"].astype(str), top_psas["count"], color=COLORS["secondary"])
        ax.set_xlabel("PSA (Police Service Area)")
        ax.set_ylabel("Crime Count")
        ax.set_title("Top 20 PSAs by Crime Count")

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height, f" {format_number(int(height))}", ha="center", va="bottom", fontsize=8)

        plt.tight_layout()
        results["psa_bar_chart"] = create_image_tag(image_to_base64(fig))
        plt.close(fig)
    else:
        results["psa_available"] = False

    # ========================================================================
    # 5. Cross-tabulation: Crime Type × District
    # ========================================================================
    print("Creating crime type × district cross-tabulation...")

    cross_tab = pd.crosstab(df[dc_dist_col], df[text_general])
    results["crime_district_crosstab"] = cross_tab

    # Heatmap of top 10 crimes × districts
    fig, ax = plt.subplots(figsize=FIGURE_SIZES["heatmap"])

    top_10_crimes = crime_counts.head(10)["crime_type"].tolist()
    cross_tab_top = cross_tab[top_10_crimes]

    sns.heatmap(cross_tab_top, cmap=COLORS["sequential"], ax=ax, annot=False)
    ax.set_xlabel("Crime Type")
    ax.set_ylabel("Police District")
    ax.set_title("Crime Type Distribution Across Districts (Top 10 Crimes)")

    plt.tight_layout()
    results["crime_district_heatmap"] = create_image_tag(image_to_base64(fig))
    plt.close(fig)

    print("Categorical analysis complete!")
    return results


def generate_markdown_report(results: dict) -> str:
    """
    Generate markdown report from categorical analysis results.

    Args:
        results: Dictionary from analyze_categorical_data()

    Returns:
        Markdown string with analysis results.
    """
    md = []

    # Add analysis configuration section
    if "analysis_metadata" in results:
        md.append(format_metadata_markdown(results["analysis_metadata"]))
        md.append("")

    md.append("### Categorical Analysis\n")

    # Crime Type Section
    md.append("#### 1. Crime Type Distribution\n\n")

    crime_counts = results["crime_counts"]
    md.append(f"**Total Unique Crime Types**: {len(crime_counts)}\n\n")

    # Top 10 crimes table
    md.append("**Top 10 Crime Types**:\n\n")
    md.append("| Rank | Crime Type | Count | Percentage |")
    md.append("|------|------------|-------|------------|")
    for i, row in crime_counts.head(10).iterrows():
        md.append(f"| {i+1} | {row['crime_type']} | {format_number(row['count'])} | {row['percentage']}% |")
    md.append("")

    md.append(results["top_crimes_bar"])
    md.append("\n")
    md.append(results["pareto_chart"])
    md.append("\n")

    # Rare crimes
    md.append("**Rare Crime Types** (Bottom 10):\n\n")
    rare_crimes = results["rare_crimes"]
    md.append("| Crime Type | Count | Percentage |")
    md.append("|------------|-------|------------|")
    for _, row in rare_crimes.iterrows():
        md.append(f"| {row['crime_type']} | {format_number(row['count'])} | {row['percentage']}% |")
    md.append("")

    # District Section
    md.append("#### 2. Police District Analysis\n\n")

    district_counts = results["district_counts"]
    top_dist = district_counts.loc[district_counts["count"].idxmax()]
    bottom_dist = district_counts.loc[district_counts["count"].idxmin()]

    md.append(f"**Total Districts**: {district_counts['district'].nunique()}\n")
    md.append(f"**Highest Crime District**: District {top_dist['district']} ({format_number(top_dist['count'])} incidents, {top_dist['percentage']}%)\n")
    md.append(f"**Lowest Crime District**: District {bottom_dist['district']} ({format_number(bottom_dist['count'])} incidents, {bottom_dist['percentage']}%)\n\n")

    md.append(results["district_bar_chart"])
    md.append("\n")
    md.append(results["district_pie_chart"])
    md.append("\n")

    # District breakdown table
    md.append("**District Breakdown**:\n\n")
    md.append("| District | Count | Percentage |")
    md.append("|----------|-------|------------|")
    for _, row in district_counts.iterrows():
        md.append(f"| {int(row['district'])} | {format_number(row['count'])} | {row['percentage']}% |")
    md.append("")

    # UCR Code Section
    md.append("#### 3. UCR Code Distribution\n\n")

    ucr_counts = results["ucr_counts"]
    md.append(f"**Unique UCR Codes**: {ucr_counts['ucr_code'].nunique()}\n\n")

    md.append(results["ucr_bar_chart"])
    md.append("\n")

    # Statistical Tests Section
    md.append("#### 3.1 Statistical Tests for Categorical Associations\n\n")

    # Crime type uniformity test
    if "crime_uniformity_test" in results:
        ut = results["crime_uniformity_test"]
        md.append("**Crime Type Uniformity Test** (Chi-square goodness-of-fit):\n\n")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Chi-square Statistic | {ut['chi2_statistic']:.4f} |")
        md.append(f"| Degrees of Freedom | {ut['dof']} |")
        md.append(f"| P-value | {ut['p_value']:.6e} |")
        md.append(f"| Significant (alpha={STAT_CONFIG['alpha']}) | {'Yes' if ut['is_significant'] else 'No'} |")
        md.append(f"| Interpretation | {ut['interpretation']} |")
        md.append("")

    # Crime-district independence test
    if "crime_district_independence" in results:
        di = results["crime_district_independence"]
        md.append("**Crime-District Independence Test** (Chi-square test of independence):\n\n")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Chi-square Statistic | {di['statistic']:.4f} |")
        md.append(f"| Degrees of Freedom | {di['dof']} |")
        md.append(f"| P-value | {di['p_value']:.6e} |")
        md.append(f"| Significant (alpha={STAT_CONFIG['alpha']}) | {'Yes' if di['is_significant'] else 'No'} |")
        md.append(f"| Cramer's V | {di['cramers_v']:.4f} |")
        md.append(f"| Effect Size | {di['cramers_v_interpretation']} |")
        md.append("")

        if di['is_significant']:
            md.append("**Interpretation:** Crime types and districts are NOT independent. ")
            md.append("Different districts have significantly different crime type distributions. ")
            md.append(f"{di['cramers_v_interpretation'].capitalize()} between crime type and location.\n\n")
        else:
            md.append("**Interpretation:** No significant association between crime types and districts found.\n\n")

    # UCR category test
    if "ucr_category_test" in results:
        ucr_test = results["ucr_category_test"]
        md.append("**UCR Category Distribution Test** (Chi-square goodness-of-fit):\n\n")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Chi-square Statistic | {ucr_test['chi2_statistic']:.4f} |")
        md.append(f"| Degrees of Freedom | {ucr_test['dof']} |")
        md.append(f"| P-value | {ucr_test['p_value']:.6e} |")
        md.append(f"| Significant (alpha={STAT_CONFIG['alpha']}) | {'Yes' if ucr_test['is_significant'] else 'No'} |")
        md.append("")

        md.append("**UCR Category Distribution:**\n\n")
        md.append("| Category | Count | Percentage |")
        md.append("|----------|-------|------------|")
        for cat, count in ucr_test['category_counts'].items():
            pct = ucr_test['category_percentages'][cat]
            md.append(f"| {cat} | {format_number(count)} | {pct:.2f}% |")
        md.append("")

    # PSA Section
    md.append("#### 4. Police Service Area (PSA) Analysis\n\n")

    if results.get("psa_available", True) and "psa_counts" in results:
        psa_counts = results["psa_counts"]
        md.append(f"**Total PSAs**: {len(psa_counts)}\n")
        md.append("**Top 10 PSAs**:\n\n")
        md.append("| PSA | Count |")
        md.append("|-----|-------|")
        for _, row in psa_counts.head(10).iterrows():
            psa_val = row['psa']
            # Handle both numeric and string PSA values
            try:
                psa_display = int(psa_val)
            except (ValueError, TypeError):
                psa_display = str(psa_val)
            md.append(f"| {psa_display} | {format_number(row['count'])} |")
        md.append("")

        md.append(results["psa_bar_chart"])
        md.append("\n")
    else:
        md.append("*PSA data not available*\n")

    # Cross-tabulation
    md.append("#### 5. Crime Type × District Heatmap\n\n")
    md.append(results["crime_district_heatmap"])
    md.append("\n")

    return "\n".join(md)


if __name__ == "__main__":
    results = analyze_categorical_data()
    report = generate_markdown_report(results)

    report_path = PROJECT_ROOT / "reports" / "03_categorical_analysis_report.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Categorical Analysis Report\n\n")
        f.write(report)

    print(f"\nReport saved to: {report_path}")
