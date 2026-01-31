"""
Correlation analysis module for Philadelphia Crime Incidents EDA.

Provides functions to analyze correlations between crime patterns and external
factors including economic indicators (unemployment rate) and weather data.

Functions:
    analyze_economic_crime_correlation: Correlation between crime and economic variables
    compute_district_level_correlation: Placeholder for district-level analysis
    compare_periods: Compare crime rates between high/low economic periods
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
