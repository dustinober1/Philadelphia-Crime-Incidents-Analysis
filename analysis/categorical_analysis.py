"""
Phase 3: Categorical Analysis

Analyzes crime types, police districts, and police service areas (PSAs).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT
from analysis.utils import load_data, image_to_base64, create_image_tag, format_number


def analyze_categorical_data() -> dict:
    """
    Run comprehensive categorical analysis.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.
    """
    print("Loading data for categorical analysis...")
    df = load_data(clean=False)

    results = {}

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
