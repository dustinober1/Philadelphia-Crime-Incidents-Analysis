"""
Correlation analysis module for Philadelphia Crime Incidents EDA.

Analyzes correlations between crime patterns and external factors including
weather (temperature, precipitation) and economic indicators (unemployment,
poverty rates). All correlations include statistical testing with detrending
to avoid spurious correlations from long-term trend drift.

Functions:
    analyze_weather_crime_correlation: Correlation between crime and weather variables
    compute_lagged_correlation: Lagged correlations for delayed weather effects
    analyze_economic_crime_correlation: Correlation between crime and economic variables
    compute_district_level_correlation: Placeholder for district-level analysis
    compare_periods: Compare crime rates between high/low economic periods
    generate_correlation_report: Generate markdown report from correlation results
    detrend_series: Remove trend from time series data
    interpret_correlation_effect: Interpret correlation coefficient magnitude
    interpret_cohens_d: Interpret Cohen's d effect size
"""

import warnings
from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats

from analysis.config import STAT_CONFIG, TEMPORAL_CONFIG, get_analysis_range
from analysis.external_data import aggregate_crime_by_period, align_temporal_data, fetch_fred_data
from analysis.reproducibility import get_analysis_metadata, set_global_seed
from analysis.stats_utils import apply_fdr_correction, bootstrap_ci, cohens_d, compare_two_samples, correlation_test
from analysis.utils import extract_temporal_features, load_data, validate_coordinates


# =============================================================================
# TIME SERIES DETRENDING
# =============================================================================


def detrend_series(series: pd.Series, method: str = "linear") -> pd.Series:
    """
    Remove trend from a time series for correlation analysis.

    Detrending is critical when correlating economic indicators with crime data,
    as both series often have long-term trends that create spurious correlations.

    Args:
        series: Time series data with datetime index.
        method: Detrending method ('linear' or 'diff').

    Returns:
        Detrended series as pandas Series with original index.

    Raises:
        ValueError: If method is not recognized or series has insufficient data.

    Example:
        >>> import pandas as pd
        >>> dates = pd.date_range('2020-01-01', periods=24, freq='M')
        >>> values = np.arange(24) + np.random.randn(24) * 0.5
        >>> ts = pd.Series(values, index=dates)
        >>> detrended = detrend_series(ts)
        >>> print(f'Trend removed, mean near zero: {detrended.mean():.4f}')
    """
    series = series.copy()

    # Remove NaN values for fitting
    valid_mask = series.notna()
    if valid_mask.sum() < 3:
        raise ValueError("Series must have at least 3 non-NaN values for detrending.")

    series_valid = series[valid_mask]

    if method == "linear":
        # Fit linear trend
        x = np.arange(len(series_valid))
        y = series_valid.values

        # Simple linear regression: y = mx + b
        slope, intercept = np.polyfit(x, y, 1)

        # Calculate trend values
        trend = slope * x + intercept

        # Create detrended series
        detrended_values = series_valid.values - trend

        # Reindex to original series
        result = series.copy()
        result.loc[valid_mask] = detrended_values

    elif method == "diff":
        # First difference: y_t - y_{t-1}
        result = series.diff().dropna()

    else:
        raise ValueError(f"Unknown detrending method: {method}. Use 'linear' or 'diff'.")

    return result


# =============================================================================
# ECONOMIC CORRELATION ANALYSIS
# =============================================================================


def analyze_economic_crime_correlation(
    economic_vars: list = None,
    resolution: str = "monthly",
    detrend: bool = True,
    include_bootstrap_ci: bool = True,
    crime_type_filter: str = None,
) -> Dict:
    """
    Analyze correlation between crime patterns and economic indicators.

    Tests correlations between crime counts and economic variables including
    unemployment rate. Monthly resolution is used because FRED data is
    reported monthly.

    Args:
        economic_vars: List of economic variable names. Defaults to unemployment.
        resolution: Temporal resolution ('monthly' or 'annual').
        detrend: If True, detrends both crime and economic series.
        include_bootstrap_ci: If True, computes 99% bootstrap confidence intervals.
        crime_type_filter: Optional crime category filter ('Violent', 'Property', 'Other').

    Returns:
        Dictionary with:
            - correlations: DataFrame of economic variable, correlation, p_value
            - bootstrap_ci: DataFrame of bootstrap CIs for each correlation
            - raw_data: Dict of aligned crime and economic series
            - detrend_used: Whether detrending was applied
            - resolution: Temporal resolution used
            - metadata: Analysis metadata

    Note:
        Economic variables available from FRED:
            - PAPHIL5URN: Philadelphia County unemployment rate (default)

        For district-level analysis, see compute_district_level_correlation().

    Example:
        >>> results = analyze_economic_crime_correlation()
        >>> print(results['correlations'])
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    # Default to unemployment rate
    if economic_vars is None:
        economic_vars = ['unemployment_rate']

    # Load crime data
    crime_df = load_data()
    crime_df = validate_coordinates(crime_df)
    crime_df = extract_temporal_features(crime_df)

    # Apply crime type filter if specified
    if crime_type_filter:
        from analysis.utils import classify_crime_category
        crime_df = classify_crime_category(crime_df)
        crime_df = crime_df[crime_df['crime_category'] == crime_type_filter]
        if crime_df.empty:
            warnings.warn(f"No crimes found for category: {crime_type_filter}")
            return {
                'correlations': pd.DataFrame(),
                'bootstrap_ci': pd.DataFrame(),
                'raw_data': {},
                'detrend_used': detrend,
                'resolution': resolution,
                'metadata': get_analysis_metadata(crime_type_filter=crime_type_filter),
            }

    # Get date range for resolution
    start_date, end_date = get_analysis_range(resolution)

    # Fetch economic data (unemployment)
    unemployment_df = fetch_fred_data(
        series_id="PAPHIL5URN",
        start_date=start_date,
        end_date=end_date,
    )

    # Align to monthly resolution
    aligned = align_temporal_data(
        crime_df=crime_df,
        unemployment_df=unemployment_df,
        resolution=resolution,
    )

    # Rename unemployment column
    if 'unemployment_rate' in aligned.columns:
        pass  # Already named correctly
    elif 'value' in aligned.columns:
        aligned = aligned.rename(columns={'value': 'unemployment_rate'})

    results = []
    ci_results = []

    for var in economic_vars:
        if var not in aligned.columns:
            warnings.warn(f"Economic variable '{var}' not found in aligned data.")
            continue

        crime = aligned['crime_count'].dropna()
        economic = aligned[var].dropna()

        # Align to common dates
        common_idx = crime.index.intersection(economic.index)
        crime_aligned = crime.loc[common_idx]
        economic_aligned = economic.loc[common_idx]

        if len(crime_aligned) < 3:
            warnings.warn(f"Insufficient data points ({len(crime_aligned)}) for correlation.")
            continue

        # Store raw data
        raw_crime = crime_aligned.copy()
        raw_economic = economic_aligned.copy()

        # Detrend if requested
        if detrend:
            crime_aligned = detrend_series(crime_aligned, method='linear')
            economic_aligned = detrend_series(economic_aligned, method='linear')

        # Compute correlation (Spearman for robustness to non-normality)
        corr_result = correlation_test(
            economic_aligned.values,
            crime_aligned.values,
            method='spearman'
        )

        results.append({
            'variable': var,
            'correlation': corr_result['correlation'],
            'p_value': corr_result['p_value'],
            'test': corr_result['test_name'],
            'n': len(crime_aligned),
            'mean_crime': raw_crime.mean(),
            'std_crime': raw_crime.std(),
            'mean_economic': raw_economic.mean(),
            'std_economic': raw_economic.std(),
        })

        # Bootstrap confidence interval for correlation
        if include_bootstrap_ci:
            def corr_statistic(data):
                """Correlation for bootstrap."""
                x = data[:, 0]
                y = data[:, 1]
                from scipy.stats import spearmanr
                corr, _ = spearmanr(x, y)
                return corr if not np.isnan(corr) else 0.0

            # Stack data for bootstrap
            combined = np.column_stack([economic_aligned.values, crime_aligned.values])

            try:
                ci_result = bootstrap_ci(
                    combined,
                    corr_statistic,
                    confidence_level=STAT_CONFIG['confidence_level'],
                    n_resamples=STAT_CONFIG['bootstrap_n_resamples'],
                    random_state=STAT_CONFIG['bootstrap_random_state'],
                )

                ci_results.append({
                    'variable': var,
                    'ci_lower': ci_result[0],
                    'ci_upper': ci_result[1],
                    'point_estimate': ci_result[2],
                    'stderr': ci_result[3],
                })
            except Exception as e:
                warnings.warn(f"Bootstrap CI failed for {var}: {e}")

    # Create DataFrame and apply FDR correction
    corr_df = pd.DataFrame(results)
    if not corr_df.empty:
        p_values = corr_df['p_value'].values
        corr_df['p_value_fdr'] = apply_fdr_correction(p_values, method=STAT_CONFIG['fdr_method'])
        corr_df['is_significant'] = corr_df['p_value_fdr'] < STAT_CONFIG['alpha']
        corr_df['is_significant_raw'] = corr_df['p_value'] < STAT_CONFIG['alpha']

        # Effect size interpretation
        corr_df['effect_size'] = corr_df['correlation'].abs().apply(_interpret_correlation_effect)

    # Bootstrap CI DataFrame
    ci_df = pd.DataFrame(ci_results) if ci_results else pd.DataFrame()

    return {
        'correlations': corr_df,
        'bootstrap_ci': ci_df,
        'raw_data': {
            'crime': raw_crime if 'raw_crime' in locals() else pd.Series(),
            'economic': raw_economic if 'raw_economic' in locals() else pd.Series(),
        },
        'detrend_used': detrend,
        'resolution': resolution,
        'crime_type_filter': crime_type_filter,
        'metadata': get_analysis_metadata(
            resolution=resolution,
            detrend=detrend,
            economic_vars=economic_vars,
        ),
    }


def _interpret_correlation_effect(abs_r: float) -> str:
    """
    Interpret correlation coefficient as effect size.

    Guidelines for interpreting |r| (Cohen, 1988):
        - Small: 0.1
        - Medium: 0.3
        - Large: 0.5

    Args:
        abs_r: Absolute value of correlation coefficient.

    Returns:
        Interpretation string.
    """
    if abs_r < 0.1:
        return "negligible"
    elif abs_r < 0.3:
        return "small"
    elif abs_r < 0.5:
        return "medium"
    else:
        return "large"


# =============================================================================
# DISTRICT-LEVEL CORRELATION (Placeholder)
# =============================================================================


def compute_district_level_correlation(
    districts: list = None,
    economic_var: str = 'unemployment_rate',
) -> Optional[pd.DataFrame]:
    """
    Compute crime-economic correlation by police district.

    Note: This function is a placeholder for future implementation.
    Requires economic data at district/tract level, which needs:
    1. Census tract to police district crosswalk (OpenDataPhilly)
    2. Census API data aggregation to districts
    3. Alignment with crime data by district

    Args:
        districts: List of district numbers. If None, uses all districts.
        economic_var: Economic variable to correlate (future: poverty_rate, median_income).

    Returns:
        Currently returns None with message about data requirements.

    Todo:
        - Download OpenDataPhilly census-to-district crosswalk
        - Aggregate Census tract data to police districts
        - Implement district-level correlation analysis

    References:
        OpenDataPhilly: https://opendataphilly.org/datasets/
        Police district boundaries available as shapefile
    """
    warnings.warn(
        "District-level economic correlation requires Census tract to "
        "police district crosswalk. See Phase 2 research notes for "
        "OpenDataPhilly crosswalk dataset. "
        "Currently only city-level unemployment correlation is available."
    )
    return None


# =============================================================================
# PERIOD COMPARISON ANALYSIS
# =============================================================================


def compare_periods(
    crime_df: pd.DataFrame = None,
    economic_series: pd.Series = None,
    high_threshold: float = None,
    low_threshold: float = None,
    percentile_high: float = 0.75,
    percentile_low: float = 0.25,
) -> Dict:
    """
    Compare crime rates between high and low economic periods.

    Tests whether crime rates differ significantly between periods of
    high vs low unemployment (or other economic indicator).

    Args:
        crime_df: Crime DataFrame with dispatch_date column.
        economic_series: Economic indicator series (e.g., unemployment).
        high_threshold: Value above which is "high" period. If None, uses top quartile.
        low_threshold: Value below which is "low" period. If None, uses bottom quartile.
        percentile_high: Percentile for high threshold (default: 0.75).
        percentile_low: Percentile for low threshold (default: 0.25).

    Returns:
        Dictionary with:
            - high_crime_mean: Mean crime count during high economic indicator periods
            - low_crime_mean: Mean crime count during low economic indicator periods
            - difference: Absolute difference in means
            - test_result: Mann-Whitney U test results
            - is_significant: Whether difference is statistically significant
            - cohens_d: Cohen's d effect size
            - effect_size: Interpretation of effect size

    Example:
        >>> result = compare_periods(economic_series=unemployment_series)
        >>> print(f'High unemployment crime: {result["high_crime_mean"]:.2f}')
        >>> print(f'Low unemployment crime: {result["low_crime_mean"]:.2f}')
    """
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    if crime_df is None:
        crime_df = load_data()

    crime_df = extract_temporal_features(crime_df)

    # Aggregate to monthly
    crime_monthly = aggregate_crime_by_period(crime_df, period='M')

    # Align with economic series
    if economic_series is None:
        # Try to fetch unemployment data
        start_date, end_date = get_analysis_range('monthly')
        unemployment_df = fetch_fred_data(
            series_id="PAPHIL5URN",
            start_date=start_date,
            end_date=end_date,
        )
        economic_series = unemployment_df['value']

    common_idx = crime_monthly.index.intersection(economic_series.index)
    crime_aligned = crime_monthly.loc[common_idx]['crime_count']
    economic_aligned = economic_series.loc[common_idx]

    # Determine thresholds
    if high_threshold is None:
        high_threshold = economic_aligned.quantile(percentile_high)
    if low_threshold is None:
        low_threshold = economic_aligned.quantile(percentile_low)

    # Split into high/low periods
    high_periods = economic_aligned >= high_threshold
    low_periods = economic_aligned <= low_threshold

    high_crime = crime_aligned[high_periods]
    low_crime = crime_aligned[low_periods]

    # Compute statistics
    test_result = compare_two_samples(
        high_crime.values,
        low_crime.values,
        alpha=STAT_CONFIG['alpha']
    )

    # Cohen's d
    d = cohens_d(high_crime.values, low_crime.values)

    return {
        'high_crime_mean': float(high_crime.mean()),
        'high_crime_std': float(high_crime.std()),
        'high_crime_n': len(high_crime),
        'low_crime_mean': float(low_crime.mean()),
        'low_crime_std': float(low_crime.std()),
        'low_crime_n': len(low_crime),
        'difference': float(high_crime.mean() - low_crime.mean()),
        'percent_diff': float((high_crime.mean() - low_crime.mean()) / low_crime.mean() * 100),
        'test_result': test_result,
        'cohens_d': d,
        'effect_size': _interpret_cohens_d(d),
        'thresholds': {
            'high': high_threshold,
            'low': low_threshold,
            'high_percentile': percentile_high,
            'low_percentile': percentile_low,
        },
        'metadata': get_analysis_metadata(
            high_threshold=high_threshold,
            low_threshold=low_threshold,
        ),
    }


def _interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < STAT_CONFIG['effect_size_small']:
        return "negligible"
    elif abs_d < STAT_CONFIG['effect_size_medium']:
        return "small"
    elif abs_d < STAT_CONFIG['effect_size_large']:
        return "medium"
    else:
        return "large"


# =============================================================================
# WEATHER CORRELATION ANALYSIS
# =============================================================================


def analyze_weather_crime_correlation(
    detrend: bool = True,
    include_lags: bool = True,
    max_lag: int = 7,
) -> Dict:
    """
    Analyze correlation between crime incidence and weather variables.

    Tests correlations between daily crime counts and weather variables
    (temperature, precipitation). Uses Spearman correlation for robustness
    to non-normal data and applies detrending to avoid spurious correlations.

    Args:
        detrend: If True, detrends both crime and weather series before correlation.
        include_lags: If True, computes lagged correlations (weather -> crime).
        max_lag: Maximum lag in days for cross-correlation analysis.

    Returns:
        Dictionary with:
            - correlations: DataFrame of variable, correlation, p_value, is_significant
            - lagged_correlations: DataFrame of lag-specific correlations
            - detrend_used: Whether detrending was applied
            - metadata: Analysis metadata

    Note:
        Weather variables tested:
            - temp: Average daily temperature (C)
            - tmax: Maximum daily temperature (C)
            - tmin: Minimum daily temperature (C)
            - prcp: Daily precipitation (mm)

    Example:
        >>> results = analyze_weather_crime_correlation()
        >>> print(results['correlations'])
    """
    from analysis.external_data import (
        fetch_weather_data,
        detrend_series as external_detrend_series,
        cross_correlation,
    )

    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    # Load data
    crime_df = load_data()
    weather_df = fetch_weather_data()

    # Align to daily resolution
    aligned = align_temporal_data(
        crime_df=crime_df,
        weather_df=weather_df,
        resolution="daily",
    )

    # Weather variables to test (use 'temp' not 'tavg' for Meteostat v2)
    weather_vars = ['temp', 'tmax', 'tmin', 'prcp']

    results = []
    for var in weather_vars:
        if var not in aligned.columns:
            continue

        crime = aligned['crime_count'].dropna()
        weather = aligned[var].dropna()

        # Align to common dates
        common_idx = crime.index.intersection(weather.index)
        crime_aligned = crime.loc[common_idx]
        weather_aligned = weather.loc[common_idx]

        # Detrend if requested
        if detrend:
            crime_aligned = external_detrend_series(crime_aligned, method='mean')
            weather_aligned = external_detrend_series(weather_aligned, method='mean')

        # Compute correlation
        corr_result = correlation_test(
            weather_aligned.values,
            crime_aligned.values,
            method='spearman',
            alpha=STAT_CONFIG['alpha']
        )

        results.append({
            'variable': var,
            'correlation': corr_result['correlation'],
            'p_value': corr_result['p_value'],
            'test': corr_result['test_name'],
            'n': len(crime_aligned),
            'interpretation': corr_result.get('interpretation', ''),
        })

    # Create DataFrame and apply FDR correction
    corr_df = pd.DataFrame(results)
    if not corr_df.empty:
        p_values = corr_df['p_value'].values
        corr_df['p_value_fdr'] = apply_fdr_correction(
            p_values,
            method=STAT_CONFIG['fdr_method']
        )
        corr_df['is_significant'] = corr_df['p_value_fdr'] < STAT_CONFIG['alpha']
        corr_df['is_significant_raw'] = corr_df['p_value'] < STAT_CONFIG['alpha']

    # Lagged correlations
    lagged_results = None
    if include_lags:
        crime_detrended = (
            external_detrend_series(aligned['crime_count'].dropna(), method='mean')
            if detrend
            else aligned['crime_count'].dropna()
        )

        lagged_results = []
        for var in weather_vars:
            if var not in aligned.columns:
                continue
            weather_series = aligned[var].dropna()
            weather_detrended = (
                external_detrend_series(weather_series, method='mean')
                if detrend
                else weather_series
            )

            # Align to common dates
            common_idx = crime_detrended.index.intersection(weather_detrended.index)
            crime_aligned = crime_detrended.loc[common_idx]
            weather_aligned = weather_detrended.loc[common_idx]

            cc = cross_correlation(crime_aligned, weather_aligned, max_lag=max_lag)
            cc['variable'] = var
            lagged_results.append(cc)

        if lagged_results:
            lagged_df = pd.concat(lagged_results, ignore_index=True)

            # FDR correction on lagged tests
            p_values = lagged_df['p_value'].values
            lagged_df['p_value_fdr'] = apply_fdr_correction(
                p_values,
                method=STAT_CONFIG['fdr_method']
            )
            lagged_df['is_significant'] = lagged_df['p_value_fdr'] < STAT_CONFIG['alpha']

            lagged_results = lagged_df

    return {
        'correlations': corr_df,
        'lagged_correlations': lagged_results,
        'detrend_used': detrend,
        'metadata': get_analysis_metadata(),
    }


def compute_lagged_correlation(
    crime_series: pd.Series,
    weather_series: pd.Series,
    lags: list = [1, 2, 3, 7, 14],
    detrend: bool = True,
) -> pd.DataFrame:
    """
    Compute lagged correlations between crime and a weather variable.

    Tests hypotheses like "hot weather today increases crime tomorrow."

    Args:
        crime_series: Daily crime count series with datetime index.
        weather_series: Daily weather variable series with datetime index.
        lags: List of lag periods (days) to test.
        detrend: If True, detrends both series before analysis.

    Returns:
        DataFrame with lag, correlation, p_value, is_significant columns.

    Example:
        >>> cc = compute_lagged_correlation(daily_crime, daily_temp, lags=[1, 7])
        >>> print(cc[cc['lag'] == 1])  # One-day lag effect
    """
    from analysis.external_data import detrend_series as external_detrend_series

    if detrend:
        crime_series = external_detrend_series(crime_series, method='mean')
        weather_series = external_detrend_series(weather_series, method='mean')

    # Align to common dates
    common_idx = crime_series.index.intersection(weather_series.index)
    crime_series = crime_series.loc[common_idx]
    weather_series = weather_series.loc[common_idx]

    results = []
    for lag in lags:
        # Shift weather forward (weather at t -> crime at t+lag)
        if lag > 0:
            crime_lagged = crime_series.iloc[lag:]
            weather_lagged = weather_series.iloc[:-lag]
        else:
            crime_lagged = crime_series
            weather_lagged = weather_series

        # Align lengths
        min_len = min(len(crime_lagged), len(weather_lagged))
        crime_lagged = crime_lagged.iloc[:min_len]
        weather_lagged = weather_lagged.iloc[:min_len]

        if min_len > 10:
            # Compute correlation
            result = correlation_test(
                weather_lagged.values,
                crime_lagged.values,
                method='spearman',
                alpha=STAT_CONFIG['alpha']
            )

            results.append({
                'lag': lag,
                'correlation': result['correlation'],
                'p_value': result['p_value'],
                'test': result['test_name'],
                'n': min_len,
                'interpretation': result.get('interpretation', ''),
            })

    df = pd.DataFrame(results)

    # Apply FDR correction
    if not df.empty:
        df['p_value_fdr'] = apply_fdr_correction(
            df['p_value'].values,
            method=STAT_CONFIG['fdr_method']
        )
        df['is_significant'] = df['p_value_fdr'] < STAT_CONFIG['alpha']

    return df


def generate_correlation_report(results: Dict, title: str = "Correlation Analysis") -> str:
    """
    Generate markdown report from correlation analysis results.

    Args:
        results: Results dictionary from analyze_weather_crime_correlation
                 or analyze_economic_crime_correlation.
        title: Report title.

    Returns:
        Markdown formatted string with results summary.

    Example:
        >>> results = analyze_weather_crime_correlation()
        >>> report = generate_correlation_report(results)
        >>> print(report)
    """
    md_lines = [f"## {title}\n"]

    # Metadata
    if 'metadata' in results:
        md_lines.append("### Analysis Metadata")
        md_lines.append("```yaml")
        for key, value in results['metadata'].items():
            md_lines.append(f"{key}: {value}")
        md_lines.append("```\n")

    # Detrending note
    detrend_used = results.get('detrend_used', False)
    md_lines.append(f"**Detrending Applied:** {'Yes' if detrend_used else 'No'}")
    if detrend_used:
        md_lines.append(
            "*Note: Detrending removes long-term trend components to avoid "
            "spurious correlations from shared drift over the 20-year period.*"
        )
    md_lines.append("")

    # Correlation results
    corr_df = results.get('correlations')
    if corr_df is not None and not corr_df.empty:
        md_lines.append("### Correlation Results\n")

        # Summary table
        md_lines.append("| Variable | Correlation | p-value | FDR p-value | Significant | Interpretation |")
        md_lines.append("|----------|-------------|---------|-------------|-------------|----------------|")

        for _, row in corr_df.iterrows():
            sig_mark = "**Yes**" if row.get('is_significant', False) else "No"
            interp = row.get('interpretation', row.get('effect_size', row.get('test', '')))
            p_val = row.get('p_value_fdr', row['p_value'])
            md_lines.append(
                f"| {row['variable']} | {row['correlation']:.4f} | "
                f"{row['p_value']:.4e} | {p_val:.4e} | {sig_mark} | {interp} |"
            )

        md_lines.append("")

        # Significant findings
        sig_count = corr_df.get('is_significant', pd.Series([False]*len(corr_df))).sum()
        if sig_count > 0:
            md_lines.append(f"#### Significant Correlations ({sig_count} found)\n")
            sig_df = corr_df[corr_df.get('is_significant', False)]
            for _, row in sig_df.iterrows():
                direction = "positive" if row['correlation'] > 0 else "negative"
                strength = row.get('interpretation', row.get('effect_size', 'unknown'))
                md_lines.append(
                    f"- **{row['variable']}**: {strength} {direction} correlation "
                    f"(rho={row['correlation']:.3f}, p={row.get('p_value_fdr', row['p_value']):.4e})"
                )
            md_lines.append("")
        else:
            md_lines.append("#### No Significant Correlations Found\n")
            md_lines.append(
                "*After FDR correction, no variables show statistically significant "
                "correlations with crime at the 99% confidence level.*"
            )
            md_lines.append("")

    # Lagged correlations
    lagged_df = results.get('lagged_correlations')
    if lagged_df is not None and not lagged_df.empty:
        md_lines.append("### Lagged Correlation Results\n")
        md_lines.append(
            "*Lagged correlations test whether weather at time t predicts "
            "crime at time t+lag.*\n"
        )

        # Find significant lags
        sig_lags = lagged_df[lagged_df.get('is_significant', False)]

        if not sig_lags.empty:
            md_lines.append("#### Significant Lag Effects\n")
            md_lines.append("| Variable | Lag | Correlation | p-value | Direction |")
            md_lines.append("|----------|-----|-------------|---------|-----------|")

            for _, row in sig_lags.iterrows():
                direction = "weather leads" if row['lag'] < 0 else "crime leads"
                md_lines.append(
                    f"| {row['variable']} | {row['lag']} | "
                    f"{row['correlation']:.4f} | {row['p_value']:.4e} | {direction} |"
                )
        else:
            md_lines.append("#### No Significant Lag Effects Found\n")
            md_lines.append(
                "*No significant lagged relationships detected at the tested "
                f"lags (1-{lagged_df['lag'].abs().max()} days).*"
            )

        md_lines.append("")

    return "\n".join(md_lines)
