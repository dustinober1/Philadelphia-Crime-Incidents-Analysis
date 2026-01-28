#!/usr/bin/env python3
"""
Test script to execute the offense breakdown analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Import config for UCR constants
import sys

sys.path.append(".")
from scripts.config import (
    UCR_VIOLENT,
    UCR_PROPERTY,
    COL_UCR_GENERAL,
    COL_TEXT_GENERAL,
    COL_DATE,
    COL_DISTRICT,
    COL_PSA,
    COL_LAT,
    COL_LON,
)

# Set plotting style
plt.style.use("default")
sns.set_palette("husl")

# Configure figure size and DPI for publication quality
FIG_WIDTH = 12
FIG_HEIGHT = 8
DPI = 300

# Create output directories
Path("output/figures/offense/").mkdir(parents=True, exist_ok=True)
Path("output/tables/offense/").mkdir(parents=True, exist_ok=True)

print("Libraries imported and directories created successfully.")

# Load cleaned data from data/processed/crime_incidents_cleaned.parquet
print("Loading cleaned crime data...")
df = pd.read_parquet("data/processed/crime_incidents_cleaned.parquet")
print(f"Data loaded successfully. Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# UCR code inventory
print("UCR code inventory:")
ucr_codes = df[COL_UCR_GENERAL].value_counts()
print(f"Number of unique UCR codes: {len(ucr_codes)}")
print("\nTop 20 UCR codes by frequency:")
print(ucr_codes.head(20))

# Calculate frequency and percentage for each code
ucr_freq_pct = pd.DataFrame(
    {"frequency": ucr_codes, "percentage": (ucr_codes / len(df)) * 100}
)
ucr_freq_pct["cumulative_percentage"] = ucr_freq_pct["percentage"].cumsum()

print("\nUCR code frequencies and percentages:")
print(ucr_freq_pct.head(20))

# Create visualization of top 20 UCR codes by frequency
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
top_20_ucr = ucr_codes.head(20)
sns.barplot(x=top_20_ucr.values, y=top_20_ucr.index.astype(str))
plt.title("Top 20 UCR Codes by Frequency", fontsize=16, fontweight="bold")
plt.xlabel("Frequency", fontsize=12)
plt.ylabel("UCR Code", fontsize=12)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/ucr_distribution_top20.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/ucr_distribution_top20.png")


# Create pie chart of UCR category distribution
# First, define UCR category mapping based on observed values
def categorize_offense(ucr_code):
    """Categorize offense based on UCR code"""
    if pd.isna(ucr_code):
        return "Unknown"

    # Convert to int for comparison if needed
    try:
        ucr_int = int(float(ucr_code))
    except (ValueError, TypeError):
        return "Unknown"

    # According to FBI UCR classification
    # Violent crimes: 100-400 range
    if 100 <= ucr_int <= 400:
        if ucr_int == 100:
            return "Homicide"
        elif ucr_int == 200:
            return "Rape"
        elif ucr_int == 300:
            return "Robbery"
        elif ucr_int == 400:
            return "Aggravated Assault"
        else:
            return "Violent Crime"
    # Property crimes: 500-700 range
    elif 500 <= ucr_int <= 700:
        if ucr_int == 500:
            return "Burglary"
        elif ucr_int == 600:
            return "Larceny"
        elif ucr_int == 700:
            return "Motor Vehicle Theft"
        else:
            return "Property Crime"
    # Other crimes: Outside the standard ranges
    else:
        return "Other"


# Apply categorization
df["offense_category"] = df[COL_UCR_GENERAL].apply(categorize_offense)

# Create pie chart
category_counts = df["offense_category"].value_counts()

plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
plt.pie(
    category_counts.values,
    labels=category_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=colors,
)
plt.title("Distribution of Offense Categories", fontsize=16, fontweight="bold")
plt.axis("equal")
plt.tight_layout()
plt.savefig("output/figures/offense/ucr_category_pie.png", dpi=DPI, bbox_inches="tight")
plt.close()  # Close to free memory
print("Saved: output/figures/offense/ucr_category_pie.png")
print(f"Category distribution:\n{category_counts}")

# Text general code analysis
print("Analyzing text_general_code descriptions...")
text_general_counts = df[COL_TEXT_GENERAL].value_counts()
print(f"Number of unique text general codes: {len(text_general_counts)}")
print("\nTop 20 text general codes by frequency:")
print(text_general_counts.head(20))

# Create visualization of top 20 text general codes
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
top_20_text = text_general_counts.head(20)
sns.barplot(x=top_20_text.values, y=top_20_text.index.astype(str))
plt.title("Top 20 Text General Codes by Frequency", fontsize=16, fontweight="bold")
plt.xlabel("Frequency", fontsize=12)
plt.ylabel("Text General Code", fontsize=12)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/text_general_code_top20.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/text_general_code_top20.png")

# Create and save UCR distribution table
ucr_distribution_df = pd.DataFrame(
    {
        "ucr_code": ucr_freq_pct.index,
        "frequency": ucr_freq_pct["frequency"],
        "percentage": ucr_freq_pct["percentage"],
        "cumulative_percentage": ucr_freq_pct["cumulative_percentage"],
    }
)

# Save to CSV
ucr_distribution_df.to_csv("output/tables/offense/ucr_distribution.csv", index=False)
print("Saved: output/tables/offense/ucr_distribution.csv")
print(f"\nUCR distribution (first 10 rows):\n{ucr_distribution_df.head(10)}")

# Offense hierarchy validation
print("Validating offense hierarchy against expected proportions...")

# Calculate actual distribution
total_records = len(df)
violent_records = len(
    df[
        df["offense_category"].str.contains(
            "Violent|Homicide|Rape|Robbery|Aggravated Assault"
        )
    ]
)
property_records = len(
    df[
        df["offense_category"].str.contains(
            "Property|Burglary|Larceny|Motor Vehicle Theft"
        )
    ]
)
other_records = len(df[df["offense_category"] == "Other"])

violent_pct = (violent_records / total_records) * 100
property_pct = (property_records / total_records) * 100
other_pct = (other_records / total_records) * 100

print(
    f"Expected hierarchy: Violent ~10%, Property ~20%, Quality-of-life ~70% (approximated as 'Other' here)"
)
print(f"Actual distribution:")
print(f"  Violent: {violent_pct:.2f}% (Expected: ~10%)")
print(f"  Property: {property_pct:.2f}% (Expected: ~20%)")
print(f"  Other: {other_pct:.2f}% (Quality-of-life approx)")

# Additional validation for Philadelphia
print(f"\nValidation against Philadelphia patterns:")
print(
    f"- Violent crime percentage ({violent_pct:.2f}%) {'matches' if 5 <= violent_pct <= 15 else 'does not match'} typical Philadelphia range (5-15%)"
)
print(
    f"- Property crime percentage ({property_pct:.2f}%) {'matches' if 15 <= property_pct <= 30 else 'does not match'} typical range (15-30%)"
)


# Severity classification scheme
# Using our categorization from above
def classify_severity(category):
    """Classify severity based on offense category"""
    if pd.isna(category):
        return "Unknown"

    if "Violent" in category or category in [
        "Homicide",
        "Rape",
        "Robbery",
        "Aggravated Assault",
    ]:
        return "Violent"
    elif "Property" in category or category in [
        "Burglary",
        "Larceny",
        "Motor Vehicle Theft",
    ]:
        return "Property"
    else:
        return "Quality-of-Life"


# Create severity column in dataframe
df["severity"] = df["offense_category"].apply(classify_severity)

# Calculate distribution: % violent, % property, % other
severity_dist = df["severity"].value_counts()
severity_pct = (severity_dist / len(df)) * 100

print("Severity distribution:")
for severity, count in severity_dist.items():
    pct = severity_pct[severity]
    print(f"  {severity}: {count:,} ({pct:.2f}%)")

# Calculate overall statistics
total_records = len(df)
violent_pct_overall = (len(df[df["severity"] == "Violent"]) / total_records) * 100
property_pct_overall = (len(df[df["severity"] == "Property"]) / total_records) * 100
quality_pct_overall = (
    len(df[df["severity"] == "Quality-of-Life"]) / total_records
) * 100

print(f"\nOverall severity percentages:")
print(f"  Violent: {violent_pct_overall:.2f}%")
print(f"  Property: {property_pct_overall:.2f}%")
print(f"  Quality-of-Life: {quality_pct_overall:.2f}%")

# Create pie chart of severity distribution
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
severity_counts = df["severity"].value_counts()
colors = [
    "#d62728",
    "#ff7f0e",
    "#1f77b4",
]  # Red, Orange, Blue for Violent, Property, QOL
plt.pie(
    severity_counts.values,
    labels=severity_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=colors,
)
plt.title("Distribution of Crime Severity Levels", fontsize=16, fontweight="bold")
plt.axis("equal")
plt.tight_layout()
plt.savefig(
    "output/figures/offense/severity_distribution.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/severity_distribution.png")

# Severity by geographic context (district)
print("Analyzing severity by district...")

# Calculate severity distribution by district
district_severity = (
    df.groupby([COL_DISTRICT, "severity"]).size().reset_index(name="count")
)
district_total = df.groupby(COL_DISTRICT).size().reset_index(name="total")

# Combine to get percentages
district_severity_pct = district_severity.merge(district_total, on=COL_DISTRICT)
district_severity_pct["percentage"] = (
    district_severity_pct["count"] / district_severity_pct["total"]
) * 100

# Pivot for easier plotting
severity_pivot = district_severity_pct.pivot(
    index=COL_DISTRICT, columns="severity", values="percentage"
).fillna(0)

# Identify districts with highest violent crime proportions
high_violent_districts = severity_pivot.nlargest(10, "Violent")[
    ["Violent"]
].sort_values(by="Violent", ascending=True)
print("Top 10 districts by violent crime percentage:")
for idx, row in high_violent_districts.iterrows():
    print(f"  District {idx}: {row['Violent']:.2f}%")

# Create stacked bar chart: district × severity
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
severity_pivot.plot(kind="barh", stacked=True, color=["#d62728", "#ff7f0e", "#1f77b4"])
plt.title("Severity Distribution by District", fontsize=16, fontweight="bold")
plt.xlabel("Percentage of Total Crimes", fontsize=12)
plt.ylabel("District", fontsize=12)
plt.legend(title="Severity Level", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(
    "output/figures/offense/severity_by_district_stacked.png",
    dpi=DPI,
    bbox_inches="tight",
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/severity_by_district_stacked.png")

# Save severity by district data
severity_pivot.to_csv("output/tables/offense/severity_by_district.csv")
print("Saved: output/tables/offense/severity_by_district.csv")

# Chi-square test for independence between district and severity
from scipy.stats import chi2_contingency

# Create contingency table
contingency_table = pd.crosstab(df[COL_DISTRICT], df["severity"])

# Perform chi-square test
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print(f"Chi-square test for district-severity independence:")
print(f"  Chi-square statistic: {chi2:.2f}")
print(f"  P-value: {p_value:.2e}")
print(f"  Degrees of freedom: {dof}")
print(
    f"  Result: {'Significant association' if p_value < 0.05 else 'No significant association'} between district and severity"
)

# Severity by temporal context
print("Analyzing severity by temporal context...")

# Convert date column to datetime if not already
df[COL_DATE] = pd.to_datetime(df[COL_DATE])

# Extract year and hour
df["year"] = df[COL_DATE].dt.year
df["hour"] = df[COL_DATE].dt.hour

# Calculate severity distribution by year
yearly_severity = df.groupby(["year", "severity"]).size().reset_index(name="count")
yearly_total = df.groupby("year").size().reset_index(name="total")
yearly_severity_pct = yearly_severity.merge(yearly_total, on="year")
yearly_severity_pct["percentage"] = (
    yearly_severity_pct["count"] / yearly_severity_pct["total"]
) * 100

# Pivot for plotting
yearly_pivot = yearly_severity_pct.pivot(
    index="year", columns="severity", values="percentage"
).fillna(0)

# Create line plot: severity proportions over 20 years
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
for col in yearly_pivot.columns:
    plt.plot(yearly_pivot.index, yearly_pivot[col], marker="o", label=col, linewidth=2)
plt.title("Severity Proportions Over Time (2006-2026)", fontsize=16, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Percentage of Total Crimes", fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/severity_trends_20yr.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/severity_trends_20yr.png")

# Save yearly data
yearly_pivot.to_csv("output/tables/offense/severity_by_year.csv")
print("Saved: output/tables/offense/severity_by_year.csv")

# Calculate severity distribution by hour of day
hourly_severity = df.groupby(["hour", "severity"]).size().reset_index(name="count")
hourly_total = df.groupby("hour").size().reset_index(name="total")
hourly_severity_pct = hourly_severity.merge(hourly_total, on="hour")
hourly_severity_pct["percentage"] = (
    hourly_severity_pct["count"] / hourly_severity_pct["total"]
) * 100

# Pivot for heatmap
hourly_pivot = hourly_severity_pct.pivot(
    index="hour", columns="severity", values="percentage"
).fillna(0)

# Create heatmap: hour × severity
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
sns.heatmap(
    hourly_pivot.T,
    annot=True,
    fmt=".1f",
    cmap="YlOrRd",
    cbar_kws={"label": "Percentage"},
)
plt.title("Crime Severity by Hour of Day", fontsize=16, fontweight="bold")
plt.xlabel("Hour of Day", fontsize=12)
plt.ylabel("Severity Level", fontsize=12)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/severity_by_hour_heatmap.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/severity_by_hour_heatmap.png")

# Save hourly data
hourly_pivot.to_csv("output/tables/offense/severity_by_hour.csv")
print("Saved: output/tables/offense/severity_by_hour.csv")

# Offense diversity analysis
print("Analyzing offense diversity by district...")

# Calculate Shannon diversity index by district
from scipy.stats import entropy


def shannon_diversity(group):
    # Calculate proportions
    props = group.value_counts(normalize=True)
    # Calculate Shannon entropy
    return entropy(props)


# Calculate diversity by district
diversity_by_district = (
    df.groupby(COL_DISTRICT)["offense_category"].apply(shannon_diversity).reset_index()
)
diversity_by_district.columns = [COL_DISTRICT, "shannon_diversity"]


# Calculate Herfindahl index by district (concentration measure)
def herfindahl_index(group):
    props = group.value_counts(normalize=True)
    return sum(props**2)


herfindahl_by_district = (
    df.groupby(COL_DISTRICT)["offense_category"].apply(herfindahl_index).reset_index()
)
herfindahl_by_district.columns = [COL_DISTRICT, "herfindahl_index"]

# Combine diversity metrics
diversity_metrics = diversity_by_district.merge(herfindahl_by_district, on=COL_DISTRICT)

print(
    f"Shannon diversity (entropy) by district (top 10 most diverse):\n{diversity_metrics.nlargest(10, 'shannon_diversity')}"
)
print(
    f"\nHerfindahl index (concentration) by district (top 10 most concentrated):\n{diversity_metrics.nsmallest(10, 'herfindahl_index')}"
)

# Create visualization of diversity by district
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
top_20_diverse = diversity_metrics.nlargest(20, "shannon_diversity")
sns.barplot(data=top_20_diverse, y=COL_DISTRICT, x="shannon_diversity")
plt.title(
    "Top 20 Most Diverse Districts (Shannon Diversity Index)",
    fontsize=16,
    fontweight="bold",
)
plt.xlabel("Shannon Diversity Index", fontsize=12)
plt.ylabel("District", fontsize=12)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/offense_diversity_map.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/offense_diversity_map.png")

# Save diversity data
diversity_metrics.to_csv(
    "output/tables/offense/offense_diversity_by_district.csv", index=False
)
print("Saved: output/tables/offense/offense_diversity_by_district.csv")

# Overall offense trends
print("Analyzing overall offense trends...")

# Time series for each major UCR category
monthly_trends = (
    df.groupby([df[COL_DATE].dt.to_period("M"), "severity"])
    .size()
    .reset_index(name="count")
)
monthly_trends["date"] = monthly_trends["date"].dt.to_timestamp()

# Calculate trend slopes with confidence intervals
from scipy import stats
import statsmodels.api as sm

# For each severity category, calculate trend
trend_results = []
for severity in df["severity"].unique():
    if pd.notna(severity):
        severity_data = monthly_trends[monthly_trends["severity"] == severity].copy()
        if len(severity_data) > 2:  # Need at least 3 points for trend
            # Prepare data for regression
            x_vals = np.arange(len(severity_data))
            y_vals = severity_data["count"].values

            # Add constant for intercept
            X = sm.add_constant(x_vals)
            model = sm.OLS(y_vals, X).fit()

            # Extract coefficients
            slope = model.params[1]
            ci_lower, ci_upper = model.conf_int()[1]  # Confidence interval for slope
            p_value = model.pvalues[1]

            trend_results.append(
                {
                    "severity": severity,
                    "slope": slope,
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper,
                    "p_value": p_value,
                    "significant": p_value < 0.05,
                }
            )

# Display results
trend_df = pd.DataFrame(trend_results)
print("Trend analysis by severity category:")
for _, row in trend_df.iterrows():
    print(
        f"{row['severity']}: Slope={row['slope']:.2f}, 95% CI=[{row['ci_lower']:.2f}, {row['ci_upper']:.2f}], p={row['p_value']:.4f}, {'Significant' if row['significant'] else 'Not Significant'}"
    )

# Top 10 most common offenses: trend over time
print("Analyzing trends for top 10 most common offenses...")

# Get top 10 most common text general codes
top_10_offenses = df[COL_TEXT_GENERAL].value_counts().head(10).index.tolist()

# Create time series for top 10 offenses
top_offense_trends = (
    df[df[COL_TEXT_GENERAL].isin(top_10_offenses)]
    .groupby([df[COL_DATE].dt.to_period("M"), COL_TEXT_GENERAL])
    .size()
    .reset_index(name="count")
)
top_offense_trends["date"] = top_offense_trends["date"].dt.to_timestamp()

# Calculate trends for each of the top 10 offenses
offense_trend_results = []
for offense in top_10_offenses:
    offense_data = top_offense_trends[
        top_offense_trends[COL_TEXT_GENERAL] == offense
    ].copy()
    if len(offense_data) > 2:  # Need at least 3 points for trend
        x_vals = np.arange(len(offense_data))
        y_vals = offense_data["count"].values

        # Add constant for intercept
        X = sm.add_constant(x_vals)
        model = sm.OLS(y_vals, X).fit()

        # Extract coefficients
        slope = model.params[1]
        ci_lower, ci_upper = model.conf_int()[1]  # Confidence interval for slope
        p_value = model.pvalues[1]

        offense_trend_results.append(
            {
                "offense": offense,
                "slope": slope,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "p_value": p_value,
                "significant": p_value < 0.05,
            }
        )

offense_trend_df = pd.DataFrame(offense_trend_results)
print("Trend analysis for top 10 offenses:")
for _, row in offense_trend_df.iterrows():
    print(
        f"{row['offense']}: Slope={row['slope']:.2f}, 95% CI=[{row['ci_lower']:.2f}, {row['ci_upper']:.2f}], p={row['p_value']:.4f}, {'Significant' if row['significant'] else 'Not Significant'}"
    )

# Create small multiples line chart for top offenses
fig, axes = plt.subplots(5, 2, figsize=(FIG_WIDTH, FIG_HEIGHT * 2))
axes = axes.flatten()

for i, offense in enumerate(top_10_offenses):
    if i < 10:  # Only plot first 10
        offense_data = top_offense_trends[
            top_offense_trends[COL_TEXT_GENERAL] == offense
        ]
        axes[i].plot(
            offense_data["date"],
            offense_data["count"],
            marker=".",
            markersize=3,
            linewidth=1,
        )
        axes[i].set_title(f"{offense}", fontsize=10)
        axes[i].grid(True, alpha=0.3)
        if i >= 8:  # Only add x-label to bottom row
            axes[i].set_xlabel("Year")
        if i % 2 == 0:  # Only add y-label to left column
            axes[i].set_ylabel("Count")

plt.tight_layout()
plt.savefig(
    "output/figures/offense/top_offenses_trends.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/top_offenses_trends.png")

# Offense composition changes
print("Analyzing offense composition changes by year...")

# Calculate offense mix by year (% of total for each category)
yearly_composition = df.groupby(["year", "severity"]).size().reset_index(name="count")
yearly_totals = df.groupby("year").size().reset_index(name="total")
yearly_composition = yearly_composition.merge(yearly_totals, on="year")
yearly_composition["percentage"] = (
    yearly_composition["count"] / yearly_composition["total"]
) * 100

# Pivot for stacked area chart
composition_pivot = yearly_composition.pivot(
    index="year", columns="severity", values="percentage"
).fillna(0)

# Create stacked area chart: year × offense category
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
composition_pivot.plot.area(stacked=True, ax=plt.gca())
plt.title(
    "Offense Composition by Year (Stacked Area Chart)", fontsize=16, fontweight="bold"
)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Percentage of Total Crimes", fontsize=12)
plt.legend(title="Severity Category", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(
    "output/figures/offense/offense_composition_stacked_area.png",
    dpi=DPI,
    bbox_inches="tight",
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/offense_composition_stacked_area.png")

# Save composition data
composition_pivot.to_csv("output/tables/offense/offense_composition_by_year.csv")
print("Saved: output/tables/offense/offense_composition_by_year.csv")

# Emerging and declining offenses
print("Identifying emerging and declining offenses...")

# Calculate percent change 2006-2010 vs. 2021-2025
# First, get average counts for early period (2006-2010)
early_period = df[(df["year"] >= 2006) & (df["year"] <= 2010)]
early_counts = early_period[COL_TEXT_GENERAL].value_counts()

# Get average counts for late period (2021-2025)
late_period = df[(df["year"] >= 2021) & (df["year"] <= 2025)]
late_counts = late_period[COL_TEXT_GENERAL].value_counts()

# Combine and calculate percent change
change_analysis = pd.DataFrame(
    {"early_avg": early_counts, "late_avg": late_counts}
).fillna(0)

# Calculate percent change (avoid division by zero)
change_analysis["percent_change"] = (
    (change_analysis["late_avg"] - change_analysis["early_avg"])
    / np.where(change_analysis["early_avg"] > 0, change_analysis["early_avg"], 1)
) * 100

# Sort by percent change
change_analysis_sorted = change_analysis.sort_values(
    "percent_change", key=abs, ascending=False
)

# Get fastest growing and declining offenses
fastest_growing = change_analysis_sorted.nlargest(10, "percent_change")
fastest_declining = change_analysis_sorted.nsmallest(10, "percent_change")

print("Fastest growing offense types (2006-2010 vs 2021-2025):")
for idx, row in fastest_growing.head(10).iterrows():
    print(f"  {idx}: {row['percent_change']:+.1f}%")

print(f"\nFastest declining offense types (2006-2010 vs 2021-2025):")
for idx, row in fastest_declining.head(10).iterrows():
    print(f"  {idx}: {row['percent_change']:+.1f}%")

# Create diverging bar chart: change by offense type
top_changes = (
    pd.concat([fastest_growing.head(10), fastest_declining.head(10)])
    .drop_duplicates()
    .head(10)
)

plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
colors = ["red" if x < 0 else "blue" for x in top_changes["percent_change"]]
bars = plt.barh(
    range(len(top_changes)), top_changes["percent_change"], color=colors, alpha=0.7
)
plt.yticks(range(len(top_changes)), top_changes.index)
plt.xlabel("Percent Change (%)", fontsize=12)
plt.title(
    "Top Changes in Offense Types (2006-2010 vs 2021-2025)",
    fontsize=16,
    fontweight="bold",
)
plt.axvline(x=0, color="black", linestyle="-", linewidth=0.8)
plt.grid(axis="x", alpha=0.3)

# Add value labels on bars
for i, (idx, row) in enumerate(top_changes.iterrows()):
    plt.text(
        row["percent_change"] + (0.5 if row["percent_change"] >= 0 else -0.5),
        i,
        f"{row['percent_change']:+.1f}%",
        va="center",
        ha="left" if row["percent_change"] >= 0 else "right",
        fontsize=9,
    )

plt.tight_layout()
plt.savefig(
    "output/figures/offense/offense_change_diverging.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/offense_change_diverging.png")

# Save change data
change_analysis.to_csv("output/tables/offense/offense_change_2006_2025.csv")
print("Saved: output/tables/offense/offense_change_2006_2025.csv")

# Seasonality by offense type
print("Analyzing seasonality by offense type...")

# Calculate seasonal patterns for each offense type
# Group by month to see seasonality
df["month"] = df[COL_DATE].dt.month

# Use top 5 most common offenses for seasonality analysis
top_5_offenses = df[COL_TEXT_GENERAL].value_counts().head(5).index.tolist()

# Calculate monthly patterns for top 5 offenses
seasonal_patterns = (
    df[df[COL_TEXT_GENERAL].isin(top_5_offenses)]
    .groupby(["month", COL_TEXT_GENERAL])
    .size()
    .reset_index(name="count")
)
monthly_totals = df.groupby("month").size().reset_index(name="monthly_total")
seasonal_patterns = seasonal_patterns.merge(monthly_totals, on="month")
seasonal_patterns["fraction_of_month"] = (
    seasonal_patterns["count"] / seasonal_patterns["monthly_total"]
)

# Calculate seasonal amplitude by offense type
seasonal_amplitude = {}
for offense in top_5_offenses:
    offense_data = seasonal_patterns[seasonal_patterns[COL_TEXT_GENERAL] == offense]
    if len(offense_data) > 0:
        counts = offense_data["count"].values
        seasonal_amplitude[offense] = {
            "amplitude": counts.max() - counts.min(),
            "avg": counts.mean(),
            "cv": counts.std() / counts.mean()
            if counts.mean() != 0
            else 0,  # Coefficient of variation
        }

# Display seasonal amplitudes
print("Seasonal amplitude by offense type:")
for offense, metrics in seasonal_amplitude.items():
    print(f"  {offense}: Amplitude={metrics['amplitude']:.1f}, CV={metrics['cv']:.3f}")

# Compare summer vs winter by offense type
summer_months = [6, 7, 8]  # June, July, August
winter_months = [12, 1, 2]  # December, January, February

summer_data = seasonal_patterns[seasonal_patterns["month"].isin(summer_months)]
winter_data = seasonal_patterns[seasonal_patterns["month"].isin(winter_months)]

# Average summer and winter counts by offense
summer_avg = summer_data.groupby(COL_TEXT_GENERAL)["count"].mean().rename("summer_avg")
winter_avg = winter_data.groupby(COL_TEXT_GENERAL)["count"].mean().rename("winter_avg")

seasonality_comparison = pd.concat([summer_avg, winter_avg], axis=1).fillna(0)
seasonality_comparison["summer_to_winter_ratio"] = np.where(
    seasonality_comparison["winter_avg"] > 0,
    seasonality_comparison["summer_avg"] / seasonality_comparison["winter_avg"],
    np.inf,  # If winter avg is 0, set ratio to infinity
)

print(f"\nSummer to Winter ratio by offense type:")
for idx, row in seasonality_comparison.iterrows():
    ratio = row["summer_to_winter_ratio"]
    if ratio == np.inf:
        print(f"  {idx}: Summer much higher than winter (winter=0)")
    else:
        print(f"  {idx}: {ratio:.2f}x more common in summer")

# Create seasonal comparison chart
fig, axes = plt.subplots(5, 1, figsize=(FIG_WIDTH, FIG_HEIGHT * 2))
if len(top_5_offenses) == 1:
    axes = [axes]

for i, offense in enumerate(top_5_offenses):
    offense_data = seasonal_patterns[seasonal_patterns[COL_TEXT_GENERAL] == offense]
    axes[i].plot(
        offense_data["month"],
        offense_data["count"],
        marker="o",
        linewidth=2,
        label=offense,
    )
    axes[i].set_title(f"Monthly Pattern for {offense}", fontsize=12)
    axes[i].set_xlabel("Month")
    axes[i].set_ylabel("Count")
    axes[i].grid(True, alpha=0.3)
    axes[i].set_xticks(range(1, 13))

plt.tight_layout()
plt.savefig(
    "output/figures/offense/seasonality_by_offense.png", dpi=DPI, bbox_inches="tight"
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/seasonality_by_offense.png")

# Save seasonality data
seasonality_comparison.to_csv("output/tables/offense/seasonality_by_offense.csv")
print("Saved: output/tables/offense/seasonality_by_offense.csv")

# Offense co-occurrence analysis
print("Performing offense co-occurrence analysis...")

# Which offenses tend to occur in the same districts?
# Group by district and offense category
district_offense_matrix = (
    df.groupby([COL_DISTRICT, "offense_category"]).size().unstack(fill_value=0)
)

# Calculate correlation matrix of offense types by district
correlation_matrix = district_offense_matrix.corr()

# Identify offense clusters
print(f"Correlation matrix shape: {correlation_matrix.shape}")
print(f"High correlations (>0.5) between offense types:")
high_corr_pairs = []
for i in range(len(correlation_matrix.columns)):
    for j in range(i + 1, len(correlation_matrix.columns)):
        corr_val = correlation_matrix.iloc[i, j]
        if corr_val > 0.5:
            high_corr_pairs.append(
                (correlation_matrix.columns[i], correlation_matrix.columns[j], corr_val)
            )

for pair in sorted(high_corr_pairs, key=lambda x: x[2], reverse=True)[:10]:
    print(f"  {pair[0]} - {pair[1]}: {pair[2]:.3f}")

# Create correlation heatmap
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    center=0,
    square=True,
    fmt=".2f",
    cbar_kws={"label": "Correlation"},
)
plt.title(
    "Correlation Matrix: Offense Types by District", fontsize=16, fontweight="bold"
)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/offense_correlation_heatmap.png",
    dpi=DPI,
    bbox_inches="tight",
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/offense_correlation_heatmap.png")

# Save correlation matrix
correlation_matrix.to_csv("output/tables/offense/offense_correlation_matrix.csv")
print("Saved: output/tables/offense/offense_correlation_matrix.csv")

# Create additional comprehensive trend visualization
# Trends by category over time
plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
for severity in ["Violent", "Property", "Quality-of-Life"]:
    if severity in yearly_pivot.columns:
        plt.plot(
            yearly_pivot.index,
            yearly_pivot[severity],
            marker="o",
            label=severity,
            linewidth=2,
        )
plt.title("Trends by Offense Category (2006-2026)", fontsize=16, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Percentage of Total Crimes", fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "output/figures/offense/offense_trends_by_category.png",
    dpi=DPI,
    bbox_inches="tight",
)
plt.close()  # Close to free memory
print("Saved: output/figures/offense/offense_trends_by_category.png")

# Save trend data with confidence intervals
trend_output = pd.DataFrame(trend_results)
trend_output.to_csv("output/tables/offense/offense_trends.csv", index=False)
print("Saved: output/tables/offense/offense_trends.csv")

print("\nOffense breakdown analysis completed successfully!")
print("All required files have been created.")
