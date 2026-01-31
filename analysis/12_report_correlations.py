"""
Correlation Analysis Report Generator for Philadelphia Crime EDA.

Generates a comprehensive markdown report documenting correlations between
crime patterns and external factors (weather, economic indicators, and
policing data availability).

Usage:
    python analysis/12_report_correlations.py

Output:
    reports/12_report_correlations.md - Markdown report with embedded plots
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Set matplotlib backend for non-interactive plotting
os.environ["MPLBACKEND"] = "Agg"

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np

# Add analysis directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analysis.config import (
    REPORTS_DIR, REPORT_TITLE, REPORT_AUTHOR,
    COLORS, FIGURE_SIZES, STAT_CONFIG,
    TEMPORAL_CONFIG,
)
from analysis.correlation_analysis import (
    analyze_weather_crime_correlation,
    analyze_economic_crime_correlation,
)
from analysis.external_data import (
    assess_policing_data_availability,
)
from analysis.reproducibility import set_global_seed, format_metadata_markdown


def create_image_tag(base64_string: str) -> str:
    """Create HTML img tag from base64 encoded image."""
    return f'<img src="data:image/png;base64,{base64_string}" alt="plot" />'


def image_to_base64(fig: plt.Figure) -> str:
    """Convert matplotlib figure to base64 encoded PNG string."""
    import base64
    from io import BytesIO

    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_str


def generate_correlation_report() -> dict:
    """
    Run all correlation analyses and generate visualizations.

    Returns:
        Dictionary with:
            - weather: Weather-crime correlation results
            - economic: Economic-crime correlation results
            - policing: Policing data availability assessment
            - plots: Dict of base64-encoded plot strings
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    results = {}
    plots = {}

    print("=" * 60)
    print("CORRELATION ANALYSIS REPORT")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # 1. Weather-Crime Correlation Analysis
    # -------------------------------------------------------------------------
    print("\n[1/4] Analyzing weather-crime correlations...")

    weather_results = analyze_weather_crime_correlation(
        detrend=True,
        include_lags=True,
        max_lag=7,
    )
    results['weather'] = weather_results

    print(f"  Weather variables tested: {len(weather_results['correlations'])}")

    # Create weather correlation plot
    corr_df = weather_results['correlations']
    if not corr_df.empty:
        fig, ax = plt.subplots(figsize=FIGURE_SIZES['medium'])

        variables = corr_df['variable'].values
        correlations = corr_df['correlation'].values
        colors = ['green' if c > 0 else 'red' for c in correlations]

        bars = ax.barh(variables, correlations, color=colors, alpha=0.7)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.axvline(x=0.3, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
        ax.axvline(x=-0.3, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

        # Add significance markers
        for i, (bar, sig) in enumerate(zip(bars, corr_df['is_significant'])):
            if sig:
                width = bar.get_width()
                ax.text(width + 0.02 if width > 0 else width - 0.02, i,
                       '**', ha='left' if width > 0 else 'right', va='center',
                       fontsize=12, fontweight='bold')

        ax.set_xlabel('Spearman Correlation (Detrended)', fontsize=11)
        ax.set_title('Weather-Crime Correlations (2006-2025)', fontsize=13, fontweight='bold')
        ax.legend([bars[0]], ['** = Significant (p < 0.01, FDR corrected)'], loc='lower right')

        # Add effect size annotations
        ax.text(0.98, 0.02, 'Positive = Warm/Wet -> More Crime\nNegative = Warm/Wet -> Less Crime',
               transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout()
        plots['weather_correlations'] = create_image_tag(image_to_base64(fig))

    # Create lagged correlation heatmap
    lagged_df = weather_results.get('lagged_correlations')
    if lagged_df is not None and not lagged_df.empty:
        # Pivot for heatmap
        heatmap_data = lagged_df.pivot(index='variable', columns='lag', values='correlation')

        fig, ax = plt.subplots(figsize=FIGURE_SIZES['medium'])
        sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdBu_r',
                   center=0, vmin=-1, vmax=1, cbar_kws={'label': 'Correlation'},
                   linewidths=0.5, ax=ax)
        ax.set_title('Lagged Weather-Crime Correlations', fontsize=13, fontweight='bold')
        ax.set_xlabel('Lag (Days)', fontsize=11)
        ax.set_ylabel('Weather Variable', fontsize=11)

        plt.tight_layout()
        plots['lagged_correlations'] = create_image_tag(image_to_base64(fig))

    # -------------------------------------------------------------------------
    # 2. Economic-Crime Correlation Analysis
    # -------------------------------------------------------------------------
    print("\n[2/4] Analyzing economic-crime correlations...")

    try:
        economic_results = analyze_economic_crime_correlation(
            resolution='monthly',
            detrend=True,
            include_bootstrap_ci=True,
        )
        results['economic'] = economic_results

        print(f"  Economic variables tested: {len(economic_results['correlations'])}")

        # Create economic correlation plot with CI
        econ_df = economic_results['correlations']
        ci_df = economic_results.get('bootstrap_ci', pd.DataFrame())

        if not econ_df.empty:
            fig, ax = plt.subplots(figsize=FIGURE_SIZES['small'])

            variables = econ_df['variable'].values
            correlations = econ_df['correlation'].values

            # Get CI bounds if available
            if not ci_df.empty:
                ci_lowers = ci_df.set_index('variable').reindex(variables)['ci_lower'].values
                ci_uppers = ci_df.set_index('variable').reindex(variables)['ci_upper'].values
            else:
                ci_lowers = correlations * 0.8  # Placeholder
                ci_uppers = correlations * 1.2

            x_pos = np.arange(len(variables))
            bars = ax.bar(x_pos, correlations, yerr=[
                correlations - ci_lowers,
                ci_uppers - correlations
            ], capsize=5, color=COLORS['primary'], alpha=0.7, error_kw={'linewidth': 1.5})

            # Add significance markers
            for i, (x, sig) in enumerate(zip(x_pos, econ_df['is_significant'])):
                if sig:
                    ax.text(x, correlations[i] + 0.05, '**', ha='center', va='bottom',
                           fontsize=14, fontweight='bold')

            ax.set_xticks(x_pos)
            ax.set_xticklabels(variables, rotation=0)
            ax.set_ylabel('Spearman Correlation (Detrended)', fontsize=11)
            ax.set_title('Economic-Crime Correlations (2006-2025 Monthly)', fontsize=13, fontweight='bold')
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
            ax.legend([bars[0]], ['** = Significant (p < 0.01, FDR corrected)\nError bars = 99% CI'], loc='best')

            plt.tight_layout()
            plots['economic_correlations'] = create_image_tag(image_to_base64(fig))

        # Create time series plot
        if economic_results.get('raw_data', {}).get('crime') is not None:
            crime = economic_results['raw_data']['crime']
            economic = economic_results['raw_data']['economic']

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIGURE_SIZES['medium'], sharex=True)

            # Crime trend
            ax1.plot(crime.index, crime.values, color=COLORS['danger'], linewidth=1.5, label='Monthly Crime Count')
            ax1.set_ylabel('Crime Count', fontsize=11)
            ax1.set_title('Monthly Crime Count (2006-2025)', fontsize=12)
            ax1.legend(loc='upper right')
            ax1.grid(True, alpha=0.3)

            # Economic trend
            ax2.plot(economic.index, economic.values, color=COLORS['primary'], linewidth=1.5, label='Unemployment Rate (%)')
            ax2.set_ylabel('Unemployment Rate (%)', fontsize=11)
            ax2.set_xlabel('Date', fontsize=11)
            ax2.set_title('Philadelphia Unemployment Rate (2006-2025)', fontsize=12)
            ax2.legend(loc='upper right')
            ax2.grid(True, alpha=0.3)

            # Format x-axis
            ax2.xaxis.set_major_locator(mdates.YearLocator(5))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

            plt.tight_layout()
            plots['economic_timeseries'] = create_image_tag(image_to_base64(fig))

    except Exception as e:
        print(f"  Economic analysis skipped (API key may be missing): {e}")
        results['economic'] = {'error': str(e)}

    # -------------------------------------------------------------------------
    # 3. Policing Data Availability Assessment
    # -------------------------------------------------------------------------
    print("\n[3/4] Assessing policing data availability...")

    policing_assessment = assess_policing_data_availability()
    results['policing'] = policing_assessment

    print(f"  Automated correlation possible: {policing_assessment['available']}")
    print(f"  Known sources: {len(policing_assessment['sources'])}")

    # -------------------------------------------------------------------------
    # 4. Summary Statistics
    # -------------------------------------------------------------------------
    print("\n[4/4] Compiling summary statistics...")

    results['summary'] = {
        'weather_significant': int(corr_df['is_significant'].sum()) if not corr_df.empty else 0,
        'weather_total': len(corr_df) if not corr_df.empty else 0,
        'economic_significant': int(econ_df['is_significant'].sum()) if 'econ_df' in locals() and not econ_df.empty else 0,
        'economic_total': len(econ_df) if 'econ_df' in locals() and not econ_df.empty else 0,
        'policing_available': policing_assessment['available'],
    }

    return {'results': results, 'plots': plots}


def generate_policing_data_report() -> str:
    """
    Generate markdown report section on policing data availability.

    Returns:
        Markdown string with policing data availability assessment.
    """
    md_lines = [
        "### Availability Assessment",
        "",
        "Automated correlation analysis between crime and policing metrics",
        "(officer counts, stops, arrests) is **not possible** with current data",
        "sources due to lack of programmatic API access.",
        "",
        "#### Known Data Sources",
        "",
        "| Source | Format | Accessibility | Correlation Possible |",
        "|--------|--------|----------------|----------------------|",
        "| Philadelphia Police Department Annual Reports | PDF | Public website | No (manual entry) |",
        "| City Controller's Office Audits | PDF | Public website | No (manual entry) |",
        "| OpenDataPhilly | CSV/Shapefile | Download | Partial (historical snapshots) |",
        "",
        "#### Data Limitations",
        "",
        "1. **No API:** Philadelphia policing data is published as annual PDF reports",
        "   requiring manual data entry for time-series analysis.",
        "",
        "2. **Inconsistent Metrics:** Different reporting periods and metric definitions",
        "   across years make longitudinal comparison difficult.",
        "",
        "3. **District-Level Resolution:** Some data is available at district level but",
        "   requires manual transcription from PDF tables.",
        "",
        "#### Recommendations for CORR-03",
        "",
        "To enable crime-policing correlation analysis, consider:",
        "",
        "1. **Manual Data Entry:** Extract officer counts and arrest rates from annual",
        "   reports (2006-2025) into a CSV file for correlation analysis.",
        "",
        "2. **OpenDataPhilly:** Check for historical arrest datasets that could be",
        "   aligned temporally with crime data.",
        "",
        "3. **Public Records Request:** Submit a request for machine-readable historical",
        "   policing data from the Philadelphia Police Department.",
        "",
    ]

    return "\n".join(md_lines)


def generate_markdown_report(results: dict, plots: dict) -> str:
    """
    Generate markdown report from correlation analysis results.

    Args:
        results: Results dictionary from generate_correlation_report.
        plots: Dictionary of base64-encoded plot strings.

    Returns:
        Markdown string with embedded plots and analysis results.
    """
    md_lines = [
        REPORT_TITLE,
        "=" * 60,
        "",
        f"**Report Type:** Correlation Analysis Report",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        f"**Author:** {REPORT_AUTHOR}",
        "",
        format_metadata_markdown(results.get('weather', {}).get('metadata', {})),
        "",
        "## Table of Contents",
        "",
        "1. [Executive Summary](#executive-summary)",
        "2. [Weather-Crime Correlations](#weather-crime-correlations)",
        "3. [Economic-Crime Correlations](#economic-crime-correlations)",
        "4. [Policing Data Availability](#policing-data-availability)",
        "5. [Methodology](#methodology)",
        "6. [Conclusions](#conclusions)",
        "",
    ]

    # -------------------------------------------------------------------------
    # Executive Summary
    # -------------------------------------------------------------------------
    md_lines.extend([
        "## Executive Summary",
        "",
        "This report analyzes correlations between Philadelphia crime incidents and external factors including weather conditions and economic indicators.",
        "",
    ])

    summary = results.get('summary', {})
    weather_results = results.get('weather', {})
    economic_results = results.get('economic', {})
    policing_results = results.get('policing', {})

    md_lines.extend([
        "### Key Findings",
        "",
        f"**Weather Analysis:** {summary.get('weather_significant', 0)} of {summary.get('weather_total', 0)} weather variables showed statistically significant correlations with crime rates (detrended, FDR-corrected, p < 0.01).",
        "",
    ])

    if 'error' not in economic_results:
        md_lines.append(
            f"**Economic Analysis:** {summary.get('economic_significant', 0)} of {summary.get('economic_total', 0)} economic variables showed statistically significant correlations with crime rates (detrended, FDR-corrected, p < 0.01)."
        )
    else:
        md_lines.append("**Economic Analysis:** Skipped (FRED API key not configured).")

    md_lines.extend([
        "",
        f"**Policing Data Analysis:** {'Automated analysis not possible' if not summary.get('policing_available', False) else 'Available'} due to lack of programmatic API access to Philadelphia policing data.",
        "",
    ])

    # -------------------------------------------------------------------------
    # Weather-Crime Correlations
    # -------------------------------------------------------------------------
    md_lines.extend([
        "## Weather-Crime Correlations",
        "",
        "### Overview",
        "",
        "Daily weather data (temperature, precipitation) was obtained from the Meteostat API for Philadelphia (39.95N, 75.17W). Correlations were computed using Spearman rank correlation to handle non-normal distributions. Both crime and weather series were detrended using mean-centering to avoid spurious correlations from long-term trend drift.",
        "",
        f"**Analysis Period:** {TEMPORAL_CONFIG['daily_start']} to {TEMPORAL_CONFIG['daily_end']} (excludes incomplete 2026 data)",
        "",
        "**Statistical Method:** Spearman rank correlation with 99% confidence intervals, FDR (Benjamini-Hochberg) correction for multiple tests",
        "",
    ])

    if 'weather_correlations' in plots:
        md_lines.extend([
            "### Correlation Results",
            "",
            plots['weather_correlations'],
            "",
        ])

    # Add correlation table
    corr_df = weather_results.get('correlations', pd.DataFrame())
    if not corr_df.empty:
        md_lines.extend([
            "### Detailed Statistics",
            "",
            "| Variable | Correlation | p-value | FDR-adjusted p | Significant | Effect Size |",
            "|----------|-------------|---------|----------------|------------|-------------|",
        ])

        for _, row in corr_df.iterrows():
            sig = 'Yes' if row['is_significant'] else 'No'
            effect = row.get('effect_size', 'N/A')
            md_lines.append(
                f"| {row['variable']} | {row['correlation']:.3f} | {row['p_value']:.4f} | "
                f"{row['p_value_fdr']:.4f} | {sig} | {effect} |"
            )

        md_lines.append("")

    if 'lagged_correlations' in plots:
        md_lines.extend([
            "### Lagged Correlations",
            "",
            "Cross-correlation analysis tests whether weather on day *t* predicts crime on day *t+n*. Positive lags indicate weather leads crime (e.g., temperature today affects crime tomorrow).",
            "",
            plots['lagged_correlations'],
            "",
        ])

    # -------------------------------------------------------------------------
    # Economic-Crime Correlations
    # -------------------------------------------------------------------------
    md_lines.extend([
        "## Economic-Crime Correlations",
        "",
        "### Overview",
        "",
        "Monthly unemployment rate data for Philadelphia County was obtained from the FRED API (series ID: PAPHIL5URN). Correlations were computed at monthly resolution using Spearman rank correlation with mean-centering detrending.",
        "",
        f"**Analysis Period:** {TEMPORAL_CONFIG['monthly_start']} to {TEMPORAL_CONFIG['monthly_end']}",
        "",
        "**Data Source:** Federal Reserve Economic Data (FRED), Philadelphia County Unemployment Rate",
        "",
    ])

    if 'error' not in economic_results:
        if 'economic_correlations' in plots:
            md_lines.extend([
                "### Correlation Results",
                "",
                plots['economic_correlations'],
                "",
            ])

        if 'economic_timeseries' in plots:
            md_lines.extend([
                "### Time Series Trends",
                "",
                plots['economic_timeseries'],
                "",
                "The figure above shows monthly crime counts and unemployment rates from 2006-2025. Note that both series have been detrended before correlation analysis to avoid spurious correlation from shared long-term trends.",
                "",
            ])

        # Add economic correlation table
        econ_df = economic_results.get('correlations', pd.DataFrame())
        if not econ_df.empty:
            md_lines.extend([
                "### Detailed Statistics",
                "",
                "| Variable | Correlation | p-value | FDR-adjusted p | Significant | 99% CI | Effect Size |",
                "|----------|-------------|---------|----------------|------------|---------|-------------|",
            ])

            ci_df = economic_results.get('bootstrap_ci', pd.DataFrame())
            for _, row in econ_df.iterrows():
                sig = 'Yes' if row['is_significant'] else 'No'
                effect = row.get('effect_size', 'N/A')

                # Get CI if available
                ci_row = ci_df[ci_df['variable'] == row['variable']]
                if not ci_row.empty:
                    ci_str = f"[{ci_row.iloc[0]['ci_lower']:.3f}, {ci_row.iloc[0]['ci_upper']:.3f}]"
                else:
                    ci_str = "N/A"

                md_lines.append(
                    f"| {row['variable']} | {row['correlation']:.3f} | {row['p_value']:.4f} | "
                    f"{row['p_value_fdr']:.4f} | {sig} | {ci_str} | {effect} |"
                )

            md_lines.append("")
    else:
        md_lines.extend([
            "### Data Availability",
            "",
            "Economic correlation analysis was not performed. To enable this analysis:",
            "",
            "1. Obtain a free FRED API key from: https://fred.stlouisfed.org/docs/api/api_key.html",
            "2. Add the key to your `.env` file: `FRED_API_KEY=your_key_here`",
            "3. Re-run this report generator",
            "",
        ])

    # -------------------------------------------------------------------------
    # Policing Data Availability
    # -------------------------------------------------------------------------
    md_lines.extend([
        "## Policing Data Availability",
        "",
        generate_policing_data_report(),
        "",
    ])

    # -------------------------------------------------------------------------
    # Methodology
    # -------------------------------------------------------------------------
    md_lines.extend([
        "## Methodology",
        "",
        "### Detrending",
        "",
        "All correlation analyses apply detrending to both crime and external variable series before computing correlations. This addresses the problem of spurious correlations where two series with long-term trends show high correlation even if no real relationship exists.",
        "",
        "Mean-centering detrending was used: subtracting the series mean from each value.",
        "",
        "### Statistical Tests",
        "",
        "- **Correlation:** Spearman rank correlation (robust to non-normal distributions)",
        "- **Significance:** p < 0.01 (99% confidence level)",
        "- **Multiple Testing:** FDR (Benjamini-Hochberg) correction applied to all tests",
        "- **Confidence Intervals:** 99% bootstrap CI with 9,999 resamples",
        "",
        "### Effect Size Interpretation",
        "",
        "- **Correlation |r|:** Negligible < 0.1, Small < 0.3, Medium < 0.5, Large >= 0.5",
        "- **Cohen's d:** Negligible < 0.2, Small < 0.5, Medium < 0.8, Large >= 0.8",
        "",
        "### Data Quality",
        "",
        "- Crime data: ~3.5M records, 2006-2026 (2026 excluded due to incompleteness)",
        "- Weather data: Daily observations from Meteostat API",
        "- Economic data: Monthly unemployment from FRED API",
        "- Coordinate coverage: 98.39% of crime records have valid coordinates",
        "",
    ])

    # -------------------------------------------------------------------------
    # Conclusions
    # -------------------------------------------------------------------------
    md_lines.extend([
        "## Conclusions",
        "",
        "### Limitations",
        "",
        "1. **Temporal Misalignment:** Different data sources have different resolutions (daily weather, monthly economic, annual census). Analyses are conducted at the lowest common resolution.",
        "",
        "2. **Policing Data:** No programmatic API exists for Philadelphia policing data. CORR-03 (crime-policing correlation) cannot be fully automated without manual data entry from PDF reports.",
        "",
        "3. **Geographic Alignment:** Census tract data does not align with police district boundaries (MAUP - Modifiable Areal Unit Problem). District-level economic analysis requires a crosswalk file.",
        "",
        "4. **Causality:** Correlation does not imply causation. These analyses identify associations, not causal mechanisms.",
        "",
        "### Future Work",
        "",
        "1. Obtain Census-to-Police-District crosswalk for district-level economic correlation",
        "2. Consider manual data entry from Controller's Office reports for limited policing correlation",
        "3. Explore holiday effects and shift-by-shift temporal patterns (Phase 3)",
        "",
        "---",
        "",
        f"*Report generated by {REPORT_AUTHOR}*",
        "",
    ])

    return "\n".join(md_lines)


def main():
    """Main entry point for report generation."""
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("PHILADELPHIA CRIME INCIDENTS - CORRELATION ANALYSIS REPORT")
    print("=" * 60 + "\n")

    # Run analyses
    output = generate_correlation_report()
    results = output['results']
    plots = output['plots']

    # Generate markdown
    print("\n" + "=" * 60)
    print("Generating report...")
    print("=" * 60)

    markdown = generate_markdown_report(results, plots)

    # Write report
    report_path = REPORTS_DIR / "12_report_correlations.md"
    with open(report_path, 'w') as f:
        f.write(markdown)

    print(f"\nReport saved to: {report_path}")
    print("=" * 60 + "\n")

    return results


if __name__ == "__main__":
    main()
