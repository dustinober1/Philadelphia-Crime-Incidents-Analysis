"""
Statistical utilities for Philadelphia Crime Incidents EDA.

Provides centralized statistical testing functions with automatic test selection
based on data characteristics. All functions include comprehensive docstrings,
type hints, and use SciPy 1.17+ for statistical operations.

Functions:
    test_normality: Test if data follows normal distribution
    compare_two_samples: Two-sample comparison with automatic test selection
    compare_multiple_samples: Multi-group comparison (ANOVA/Kruskal-Wallis)
    cohens_d: Cohen's d effect size for two samples
    cliffs_delta: Cliff's Delta non-parametric effect size
    odds_ratio: Odds ratio for proportion comparisons
    standardized_coefficient: Standardized regression coefficient
    bootstrap_ci: Bootstrap confidence intervals
    apply_fdr_correction: False Discovery Rate correction
    tukey_hsd: Tukey HSD post-hoc test
    chi_square_test: Chi-square test of independence
    correlation_test: Correlation test with automatic selection
    mann_kendall_test: Mann-Kendall trend test for time series
"""

from typing import Tuple, Dict, Literal, Optional, Callable, Union, List, TYPE_CHECKING
import numpy as np
import pandas as pd
from scipy import stats

# Type hint for TukeyHSDResult (avoiding direct import for compatibility)
if TYPE_CHECKING:
    from scipy.stats._hypotests import TukeyHSDResult
else:
    TukeyHSDResult = object


# =============================================================================
# NORMALITY TESTING
# =============================================================================

def test_normality(
    data: np.ndarray,
    alpha: float = 0.05
) -> Tuple[bool, float, float, str]:
    """
    Test whether data follows a normal distribution.

    Automatically selects Shapiro-Wilk (n <= 5000) or D'Agostino-Pearson (n > 5000)
    based on sample size. Shapiro-Wilk is more powerful for small samples,
    while D'Agostino-Pearson is better for larger samples.

    Args:
        data: 1D array of numeric values to test for normality.
        alpha: Significance level for the test. Default is 0.05.

    Returns:
        A tuple containing:
            - is_normal: True if data is normally distributed (p >= alpha)
            - statistic: Test statistic value
            - p_value: P-value from the test
            - test_name: Name of the test performed

    Raises:
        ValueError: If data has fewer than 3 samples (minimum for normality tests).

    Example:
        >>> import numpy as np
        >>> data = np.random.normal(0, 1, 100)
        >>> is_normal, stat, p, test = test_normality(data)
        >>> print(f"Normal: {is_normal}, p-value: {p:.4f}")

    References:
        - Shapiro-Wilk: scipy.stats.shapiro
        - D'Agostino-Pearson: scipy.stats.normaltest
    """
    data = np.asarray(data)
    data = data[~np.isnan(data)]  # Remove NaN values

    if len(data) < 3:
        raise ValueError(
            f"Normality test requires at least 3 samples. Got {len(data)}."
        )

    if len(data) <= 5000:
        # Shapiro-Wilk test for small to medium samples
        # More powerful than other tests for small n
        statistic, p_value = stats.shapiro(data)
        test_name = "Shapiro-Wilk"
    else:
        # D'Agostino-Pearson test for large samples
        # Based on skewness and kurtosis, more robust for large n
        statistic, p_value = stats.normaltest(data)
        test_name = "D'Agostino-Pearson"

    is_normal = p_value >= alpha

    return is_normal, float(statistic), float(p_value), test_name


# =============================================================================
# TWO-SAMPLE COMPARISON
# =============================================================================

def compare_two_samples(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05
) -> Dict[str, Union[str, float, bool]]:
    """
    Compare two samples using appropriate parametric or non-parametric test.

    Tests normality of both samples first, then selects:
    - Independent t-test if both samples are normal
    - Mann-Whitney U test if either sample is non-normal

    Args:
        x: First sample data (1D array).
        y: Second sample data (1D array).
        alpha: Significance level for the test. Default is 0.05.

    Returns:
        Dictionary containing:
            - test_name: Name of the test performed
            - statistic: Test statistic value
            - p_value: P-value from the test
            - is_significant: True if p < alpha (reject null hypothesis)
            - normality_x: Whether x is normally distributed
            - normality_y: Whether y is normally distributed

    Raises:
        ValueError: If either sample has fewer than 2 observations.

    Example:
        >>> import numpy as np
        >>> x = np.random.normal(0, 1, 100)
        >>> y = np.random.normal(0.5, 1, 100)
        >>> result = compare_two_samples(x, y)
        >>> print(f"Test: {result['test_name']}, p: {result['p_value']:.4f}")

    References:
        - scipy.stats.ttest_ind
        - scipy.stats.mannwhitneyu
    """
    x = np.asarray(x)
    y = np.asarray(y)

    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    if len(x) < 2:
        raise ValueError(f"Sample x requires at least 2 observations. Got {len(x)}.")
    if len(y) < 2:
        raise ValueError(f"Sample y requires at least 2 observations. Got {len(y)}.")

    # Test normality for both samples
    normality_x, _, p_x, _ = test_normality(x, alpha=alpha)
    normality_y, _, p_y, _ = test_normality(y, alpha=alpha)

    # Select test based on normality
    if normality_x and normality_y:
        # Parametric: Independent t-test
        statistic, p_value = stats.ttest_ind(x, y)
        test_name = "Independent t-test"
    else:
        # Non-parametric: Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(x, y, alternative='two-sided')
        test_name = "Mann-Whitney U"

    return {
        "test_name": test_name,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "is_significant": p_value < alpha,
        "normality_x": normality_x,
        "normality_y": normality_y,
        "normality_p_x": float(p_x),
        "normality_p_y": float(p_y),
    }


# =============================================================================
# MULTI-SAMPLE COMPARISON
# =============================================================================

def compare_multiple_samples(
    groups_dict: Dict[str, np.ndarray],
    alpha: float = 0.05
) -> Dict[str, Union[str, float, Dict, pd.DataFrame]]:
    """
    Compare multiple groups using ANOVA or Kruskal-Wallis test.

    Tests normality for all groups, then:
    - One-way ANOVA + Tukey HSD if all groups are normal
    - Kruskal-Wallis if any group is non-normal

    Args:
        groups_dict: Dictionary mapping group names to data arrays.
        alpha: Significance level for the test. Default is 0.05.

    Returns:
        Dictionary containing:
            - omnibus_test: Name of the omnibus test performed
            - statistic: Test statistic value
            - p_value: P-value from the omnibus test
            - is_significant: True if p < alpha (reject null hypothesis)
            - all_normal: Whether all groups passed normality test
            - post_hoc_results: DataFrame with post-hoc pairwise comparisons
            - normality_by_group: Dict of normality test results per group

    Raises:
        ValueError: If fewer than 2 groups provided, or any group has < 2 obs.

    Example:
        >>> import numpy as np
        >>> groups = {
        ...     'A': np.random.normal(0, 1, 50),
        ...     'B': np.random.normal(0.5, 1, 50),
        ...     'C': np.random.normal(1, 1, 50)
        ... }
        >>> result = compare_multiple_samples(groups)
        >>> print(f"Omnibus p-value: {result['p_value']:.4f}")

    References:
        - scipy.stats.f_oneway (One-way ANOVA)
        - scipy.stats.kruskal (Kruskal-Wallis)
        - scipy.stats.tukey_hsd (Tukey HSD)
    """
    if len(groups_dict) < 2:
        raise ValueError("At least 2 groups required for comparison.")

    # Clean data and test normality for each group
    groups_clean = {}
    normality_by_group = {}

    for name, data in groups_dict.items():
        data_arr = np.asarray(data)
        data_arr = data_arr[~np.isnan(data_arr)]

        if len(data_arr) < 2:
            raise ValueError(
                f"Group '{name}' requires at least 2 observations. Got {len(data_arr)}."
            )

        groups_clean[name] = data_arr
        is_normal, _, p_val, test_name = test_normality(data_arr, alpha=alpha)
        normality_by_group[name] = {
            "is_normal": is_normal,
            "p_value": float(p_val),
            "test_used": test_name,
        }

    all_normal = all(g["is_normal"] for g in normality_by_group.values())
    group_names = list(groups_clean.keys())
    group_data = [groups_clean[name] for name in group_names]

    # Run omnibus test
    if all_normal:
        # Parametric: One-way ANOVA
        statistic, p_value = stats.f_oneway(*group_data)
        omnibus_test = "One-way ANOVA"

        # Post-hoc: Tukey HSD
        try:
            tukey_result = stats.tukey_hsd(*group_data)
            post_hoc_df = _tukey_to_dataframe(tukey_result, group_names)
        except Exception:
            # Fallback if Tukey HSD fails
            post_hoc_df = None
    else:
        # Non-parametric: Kruskal-Wallis
        statistic, p_value = stats.kruskal(*group_data)
        omnibus_test = "Kruskal-Wallis"
        post_hoc_df = None  # Would need Dunn's test for post-hoc

    return {
        "omnibus_test": omnibus_test,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "is_significant": p_value < alpha,
        "all_normal": all_normal,
        "post_hoc_results": post_hoc_df,
        "normality_by_group": normality_by_group,
    }


def _tukey_to_dataframe(
    tukey_result: 'TukeyHSDResult',
    group_names: List[str]
) -> pd.DataFrame:
    """Convert TukeyHSDResult to pandas DataFrame for easier interpretation.

    Extracts pairwise comparisons from scipy.stats._hypotests.TukeyHSDResult.
    """
    comparisons = []

    # Get confidence intervals (scipy uses confidence_interval() method)
    ci = tukey_result.confidence_interval()
    pvalues = tukey_result.pvalue  # Matrix of p-values
    statistics = tukey_result.statistic  # Matrix of mean differences

    n_groups = len(group_names)

    # Extract only upper triangle (unique comparisons, avoid duplicates)
    for i in range(n_groups):
        for j in range(i + 1, n_groups):
            comparisons.append({
                "group_a": group_names[i],
                "group_b": group_names[j],
                "mean_diff": float(statistics[i, j]),
                "ci_lower": float(ci.low[i, j]),
                "ci_upper": float(ci.high[i, j]),
                "p_value": float(pvalues[i, j]),
            })

    return pd.DataFrame(comparisons)


# =============================================================================
# EFFECT SIZE
# =============================================================================

def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate Cohen's d effect size for two samples.

    Cohen's d measures the standardized difference between two means.
    Interpretation:
        - Small effect: |d| >= 0.2
        - Medium effect: |d| >= 0.5
        - Large effect: |d| >= 0.8

    Args:
        x: First sample data.
        y: Second sample data.

    Returns:
        Cohen's d effect size. Positive values indicate x > y,
        negative values indicate y > x.

    Raises:
        ValueError: If either sample has fewer than 2 observations,
            or if pooled standard deviation is zero (no variance).

    Example:
        >>> import numpy as np
        >>> x = np.random.normal(0, 1, 100)
        >>> y = np.random.normal(0.5, 1, 100)
        >>> d = cohens_d(x, y)
        >>> print(f"Cohen's d: {d:.3f}")

    References:
        - Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    nx = len(x)
    ny = len(y)

    if nx < 2:
        raise ValueError(f"Sample x requires at least 2 observations. Got {nx}.")
    if ny < 2:
        raise ValueError(f"Sample y requires at least 2 observations. Got {ny}.")

    # Calculate mean difference
    mean_diff = np.mean(x) - np.mean(y)

    # Calculate pooled standard deviation
    # Using formula: sqrt(((nx-1)*var_x + (ny-1)*var_y) / (nx+ny-2))
    var_x = np.var(x, ddof=1)  # Sample variance (ddof=1)
    var_y = np.var(y, ddof=1)

    pooled_sd = np.sqrt(((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2))

    if pooled_sd == 0:
        raise ValueError(
            "Pooled standard deviation is zero. "
            "Both samples have identical values with no variance."
        )

    cohens_d_value = mean_diff / pooled_sd

    return float(cohens_d_value)


def interpret_cohens_d(d: float) -> str:
    """
    Interpret Cohen's d effect size using conventional benchmarks.

    Args:
        d: Cohen's d value.

    Returns:
        Interpretation string (negligible, small, medium, or large).

    Example:
        >>> interpret_cohens_d(0.3)
        'small effect'
        >>> interpret_cohens_d(1.2)
        'large effect'
    """
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible effect"
    elif abs_d < 0.5:
        return "small effect"
    elif abs_d < 0.8:
        return "medium effect"
    else:
        return "large effect"


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> Tuple[float, str]:
    """
    Calculate Cliff's Delta non-parametric effect size.

    Cliff's Delta measures the ordinal dominance between two samples.
    More robust than Cohen's d for non-normal data or ordinal data.

    The statistic ranges from -1 to +1:
    - delta = +1: All values in x are greater than all values in y
    - delta = 0: No dominance (equal distributions)
    - delta = -1: All values in y are greater than all values in x

    Interpretation (Romano et al., 2006):
    - negligible: |d| < 0.147
    - small: 0.147 <= |d| < 0.33
    - medium: 0.33 <= |d| < 0.474
    - large: |d| >= 0.474

    Args:
        x: First sample data.
        y: Second sample data.

    Returns:
        Tuple of (effect_size, interpretation) where:
        - effect_size: Cliff's Delta value (-1 to +1)
        - interpretation: String description of effect size magnitude

    Raises:
        ValueError: If either sample has fewer than 2 observations.

    Example:
        >>> import numpy as np
        >>> x = np.array([1, 2, 3, 4, 5])
        >>> y = np.array([2, 3, 4, 5, 6])
        >>> delta, interp = cliffs_delta(x, y)
        >>> print(f"Cliff's Delta: {delta:.3f} ({interp})")

    References:
        - Cliff, N. (1993). Dominance statistics: Ordinal analyses to
          answer ordinal questions.
        - Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006).
          Appropriate statistics for ordinal level data.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]

    nx = len(x)
    ny = len(y)

    if nx < 2:
        raise ValueError(f"Sample x requires at least 2 observations. Got {nx}.")
    if ny < 2:
        raise ValueError(f"Sample y requires at least 2 observations. Got {ny}.")

    # Calculate Cliff's Delta
    # Delta = (P(x > y) - P(x < y)) where P is proportion
    # Using vectorized operations for efficiency
    # Create matrices of comparisons
    x_matrix = x.reshape(-1, 1)  # Column vector
    y_matrix = y.reshape(1, -1)  # Row vector

    # Count dominance: where x > y and where x < y
    greater = np.sum(x_matrix > y_matrix)
    less = np.sum(x_matrix < y_matrix)

    # Cliff's Delta
    delta = (greater - less) / (nx * ny)

    # Interpretation based on Romano et al. (2006)
    abs_delta = abs(delta)
    if abs_delta < 0.147:
        interpretation = "negligible"
    elif abs_delta < 0.33:
        interpretation = "small"
    elif abs_delta < 0.474:
        interpretation = "medium"
    else:
        interpretation = "large"

    return float(delta), interpretation


def odds_ratio(
    counts1: np.ndarray,
    counts2: np.ndarray,
    ci_level: float = 0.99
) -> Dict[str, Union[float, bool]]:
    """
    Calculate odds ratio with confidence interval for two proportions.

    Odds ratio is commonly used in epidemiology and crime research for
    comparing the odds of an event occurring between two groups.

    The odds ratio represents the ratio of the odds of an event in group 1
    to the odds of the same event in group 2.
    - OR = 1: Equal odds in both groups
    - OR > 1: Higher odds in group 1
    - OR < 1: Higher odds in group 2

    Args:
        counts1: Array of [successes, failures] for group 1
        counts2: Array of [successes, failures] for group 2
        ci_level: Confidence level (default 0.99 for 99% CI)

    Returns:
        Dict with:
        - or: Odds ratio value
        - ci_lower: Lower bound of confidence interval
        - ci_upper: Upper bound of confidence interval
        - p_value: P-value from Fisher's exact test
        - is_significant: Whether p < 0.01 (matches 99% CI)
        - ci_level: The confidence level used

    Raises:
        ValueError: If counts don't have 2 elements or contain invalid values.

    Example:
        >>> import numpy as np
        >>> # Summer: 1000 crimes out of 10000 observations
        >>> # Winter: 800 crimes out of 10000 observations
        >>> result = odds_ratio(np.array([1000, 9000]), np.array([800, 9200]))
        >>> print(f"OR: {result['or']:.3f}, 99% CI: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")

    References:
        - Fisher's exact test: scipy.stats.fisher_exact
        - Woolf method for log-odds ratio CI
    """
    counts1 = np.asarray(counts1)
    counts2 = np.asarray(counts2)

    if counts1.shape != (2,) or counts2.shape != (2,):
        raise ValueError(
            f"counts1 and counts2 must be arrays of shape (2,). "
            f"Got {counts1.shape} and {counts2.shape}."
        )

    if np.any(counts1 < 0) or np.any(counts2 < 0):
        raise ValueError("Counts cannot be negative.")

    # 2x2 contingency table
    #         Group1   Group2
    # Success  a       b
    # Failure  c       d
    a, b = counts1[0], counts2[0]
    c, d = counts1[1], counts2[1]

    # Check for zero cells
    if (b == 0 and c > 0) or (c == 0 and b > 0):
        # OR would be 0 or infinite
        # Add small continuity correction (Haldane-Anscombe correction)
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5

    table = [[a, b], [c, d]]

    # Odds ratio
    numerator = a * d
    denominator = b * c

    if denominator == 0:
        if numerator == 0:
            or_val = 1.0  # Indeterminate case, assume no effect
        else:
            or_val = float('inf')
    else:
        or_val = numerator / denominator

    # Fisher's exact test for p-value
    try:
        _, p_value = stats.fisher_exact(table, alternative='two-sided')
    except ValueError:
        # Fallback to chi-square if Fisher's fails
        _, p_value, _, _ = stats.chi2_contingency(table, correction=True)

    # Log-based CI for odds ratio (Woolf method)
    # Add small continuity correction to avoid log(0)
    if or_val == float('inf'):
        log_or = np.log((a * d + 0.5) / (b * c + 0.5))
    elif or_val == 0:
        log_or = np.log((a * d + 0.5) / (b * c + 0.5))
    else:
        log_or = np.log(or_val) if or_val > 0 else 0

    # Standard error of log odds ratio
    se = np.sqrt(1/(a + 0.5) + 1/(b + 0.5) + 1/(c + 0.5) + 1/(d + 0.5))

    # Z-score for confidence level
    z = stats.norm.ppf(1 - (1 - ci_level) / 2)

    log_ci_low = log_or - z * se
    log_ci_high = log_or + z * se

    ci_lower = np.exp(log_ci_low)
    ci_upper = np.exp(log_ci_high)

    return {
        "or": or_val,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": float(p_value),
        "is_significant": float(p_value) < 0.01,
        "ci_level": ci_level
    }


def standardized_coefficient(
    x: np.ndarray,
    y: np.ndarray
) -> Dict[str, Union[float, bool]]:
    """
    Calculate standardized regression coefficient (beta) for correlation.

    The standardized coefficient represents the change in Y (in standard deviation units)
    for a 1 standard deviation increase in X. It's the slope of the regression line
    when both variables are z-scored.

    Also known as:
    - Beta coefficient in standardized regression
    - Path coefficient in path analysis
    - Effect size for linear relationships

    Interpretation:
    - beta = 0: No linear relationship
    - |beta| < 0.2: Weak effect
    - 0.2 <= |beta| < 0.5: Small to moderate effect
    - 0.5 <= |beta| < 0.8: Moderate to large effect
    - |beta| >= 0.8: Large effect

    Args:
        x: Predictor variable (1D array)
        y: Outcome variable (1D array, same length as x)

    Returns:
        Dict with:
        - beta: Standardized coefficient (slope when both variables z-scored)
        - ci_lower: Lower bound of 99% bootstrap CI
        - ci_upper: Upper bound of 99% bootstrap CI
        - p_value: P-value for testing beta = 0
        - is_significant: Whether p < 0.01
        - interpretation: Effect size interpretation

    Raises:
        ValueError: If x and y have different lengths or < 3 observations.

    Example:
        >>> import numpy as np
        >>> x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> y = np.array([2, 4, 5, 4, 5, 7, 8, 6, 9, 11])
        >>> result = standardized_coefficient(x, y)
        >>> print(f"Beta: {result['beta']:.3f}, 99% CI: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")

    References:
        - Standardized regression: Cohen et al. (2003). Applied Multiple Regression.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove pairwise NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]

    if len(x) != len(y):
        raise ValueError(f"x and y must have same length. Got {len(x)} and {len(y)}.")
    if len(x) < 3:
        raise ValueError(f"Standardized coefficient requires at least 3 observations. Got {len(x)}.")

    # Z-score both variables
    x_mean = np.mean(x)
    x_std = np.std(x, ddof=1)
    y_mean = np.mean(y)
    y_std = np.std(y, ddof=1)

    if x_std == 0 or y_std == 0:
        raise ValueError("Cannot compute standardized coefficient: one variable has zero variance.")

    x_z = (x - x_mean) / x_std
    y_z = (y - y_mean) / y_std

    # Simple regression of y_z on x_z
    result = stats.linregress(x_z, y_z)

    # Bootstrap CI for beta
    def beta_stat(data):
        x_b, y_b = data
        x_mean = np.mean(x_b)
        x_std = np.std(x_b, ddof=1)
        y_mean = np.mean(y_b)
        y_std = np.std(y_b, ddof=1)

        if x_std == 0 or y_std == 0:
            return 0.0

        x_z = (x_b - x_mean) / x_std
        y_z = (y_b - y_mean) / y_std
        return np.polyval(np.polyfit(x_z, y_z, 1), x_z).mean()  # Slope via polyfit

    # Use scipy's bootstrap
    try:
        res = stats.bootstrap(
            data=(x, y),
            statistic=lambda data, axis: np.polyfit(
                (data[0] - np.mean(data[0])) / np.std(data[0], ddof=1),
                (data[1] - np.mean(data[1])) / np.std(data[1], ddof=1),
                1
            )[0] if axis is None else 0,
            confidence_level=0.99,
            n_resamples=9999,
            random_state=42,
            method='BCa'
        )
        ci_lower = float(res.confidence_interval.low)
        ci_upper = float(res.confidence_interval.high)
    except Exception:
        # Fallback: use simple percentile CI from manual bootstrap
        n_boot = 9999
        boot_betas = []
        rng = np.random.default_rng(42)

        for _ in range(n_boot):
            idx = rng.choice(len(x), size=len(x), replace=True)
            x_boot = x[idx]
            y_boot = y[idx]

            x_std = np.std(x_boot, ddof=1)
            y_std = np.std(y_boot, ddof=1)

            if x_std > 0 and y_std > 0:
                x_z_boot = (x_boot - np.mean(x_boot)) / x_std
                y_z_boot = (y_boot - np.mean(y_boot)) / y_std
                beta = np.corrcoef(x_z_boot, y_z_boot)[0, 1]
                boot_betas.append(beta)

        boot_betas = np.array(boot_betas)
        ci_lower = float(np.percentile(boot_betas, 0.5))
        ci_upper = float(np.percentile(boot_betas, 99.5))

    # Interpretation
    abs_beta = abs(result.slope)
    if abs_beta < 0.2:
        interpretation = "weak effect"
    elif abs_beta < 0.5:
        interpretation = "small to moderate effect"
    elif abs_beta < 0.8:
        interpretation = "moderate to large effect"
    else:
        interpretation = "large effect"

    return {
        "beta": float(result.slope),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": float(result.pvalue),
        "is_significant": result.pvalue < 0.01,
        "interpretation": interpretation
    }


# =============================================================================
# BOOTSTRAP CONFIDENCE INTERVALS
# =============================================================================

def bootstrap_ci(
    data: np.ndarray,
    statistic: Union[Callable, str],
    confidence_level: float = 0.99,
    n_resamples: int = 9999,
    random_state: Optional[int] = None,
) -> Tuple[float, float, float, float]:
    """
    Calculate bootstrap confidence interval for any statistic.

    Bootstrap resampling provides non-parametric confidence intervals
    without assuming normality.

    Args:
        data: 1D array of sample data.
        statistic: Either a callable that computes the statistic on a 1D array,
                   or a string: 'mean', 'median', 'std', 'var'.
        confidence_level: Confidence level (0-1). Default is 0.99.
        n_resamples: Number of bootstrap resamples. Default is 9999.
        random_state: Random seed for reproducibility. Default is None.

    Returns:
        A tuple containing:
            - lower_bound: Lower bound of confidence interval
            - upper_bound: Upper bound of confidence interval
            - point_estimate: Observed statistic value on original data
            - standard_error: Standard error of the bootstrap distribution

    Raises:
        ValueError: If data has fewer than 2 observations, or if
            confidence_level is not between 0 and 1.

    Example:
        >>> import numpy as np
        >>> data = np.random.normal(0, 1, 100)
        >>> lower, upper, estimate, se = bootstrap_ci(data, 'mean', 0.99)
        >>> print(f"99% CI: [{lower:.3f}, {upper:.3f}]")

    References:
        - scipy.stats.bootstrap
        - Efron, B., & Tibshirani, R. J. (1994). An Introduction to the Bootstrap.
    """
    data = np.asarray(data)
    data = data[~np.isnan(data)]

    if len(data) < 2:
        raise ValueError(f"Bootstrap requires at least 2 observations. Got {len(data)}.")
    if not 0 < confidence_level < 1:
        raise ValueError(f"confidence_level must be between 0 and 1. Got {confidence_level}.")

    # Convert string statistic names to functions
    if isinstance(statistic, str):
        statistic_map = {
            'mean': np.mean,
            'median': np.median,
            'std': np.std,
            'var': np.var,
        }
        if statistic not in statistic_map:
            raise ValueError(
                f"Unknown statistic '{statistic}'. "
                f"Use one of: {list(statistic_map.keys())} or provide a callable."
            )
        statistic_func = statistic_map[statistic]
    else:
        statistic_func = statistic

    # Run bootstrap
    result = stats.bootstrap(
        data=(data,),
        statistic=statistic_func,
        confidence_level=confidence_level,
        n_resamples=n_resamples,
        random_state=random_state,
        method='BCa',  # Bias-corrected and accelerated
    )

    lower_bound = float(result.confidence_interval.low)
    upper_bound = float(result.confidence_interval.high)
    point_estimate = float(result.bootstrap_distribution.mean())
    standard_error = float(result.standard_error)

    return lower_bound, upper_bound, point_estimate, standard_error


# =============================================================================
# MULTIPLE TESTING CORRECTION
# =============================================================================

def apply_fdr_correction(
    p_values: np.ndarray,
    method: Literal['bh', 'by'] = 'bh'
) -> np.ndarray:
    """
    Apply False Discovery Rate (FDR) correction to p-values.

    Controls the expected proportion of false positives among rejected hypotheses.
    Less conservative than Bonferroni, more powerful for large numbers of tests.

    Methods:
        - 'bh': Benjamini-Hochberg (standard FDR)
        - 'by': Benjamini-Yekutieli (more conservative, valid under dependence)

    Args:
        p_values: Array of p-values to correct.
        method: FDR correction method ('bh' or 'by'). Default is 'bh'.

    Returns:
        Array of adjusted p-values (same length as input).

    Raises:
        ValueError: If p_values is empty or contains invalid values.

    Example:
        >>> import numpy as np
        >>> p_values = np.array([0.001, 0.01, 0.05, 0.1, 0.5])
        >>> adjusted = apply_fdr_correction(p_values)
        >>> print(f"Adjusted p-values: {adjusted}")

    References:
        - Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate.
        - scipy.stats.false_discovery_control
    """
    p_values = np.asarray(p_values)

    if len(p_values) == 0:
        raise ValueError("p_values array cannot be empty.")

    if np.any((p_values < 0) | (p_values > 1)):
        raise ValueError("p_values must be between 0 and 1.")

    # Map method names for scipy
    method_map = {
        'bh': 'bh',
        'by': 'by',
    }

    if method not in method_map:
        raise ValueError(f"Unknown method '{method}'. Use 'bh' or 'by'.")

    # Apply FDR correction
    adjusted_p = stats.false_discovery_control(p_values, method=method_map[method])

    return adjusted_p


# =============================================================================
# TUKEY HSD POST-HOC TEST
# =============================================================================

def tukey_hsd(
    *samples: np.ndarray,
    confidence_level: float = 0.99
) -> 'TukeyHSDResult':
    """
    Perform Tukey's Honest Significant Difference (HSD) post-hoc test.

    Tukey HSD compares all pairs of group means while controlling
    family-wise error rate. Use after a significant ANOVA result.

    Note: scipy.stats.tukey_hsd uses 95% CI by default. The confidence_level
    parameter is stored in the result for reference, but actual intervals
    computed by scipy.stats.tukey_hsd are 95%. For custom confidence levels,
    access result.confint(confidence_level=...) directly.

    Args:
        *samples: Variable number of sample arrays (one per group).
        confidence_level: Desired confidence level for interpretation (0-1).
                          Note: scipy computes 95% CI by default. Default is 0.99.

    Returns:
        TukeyHSDResult object containing:
            - mean_diffs: Mean differences for each pair
            - confint: Confidence intervals (95% by scipy default)
            - pvalues: P-values for each comparison
            - groups: Number of groups

    Raises:
        ValueError: If fewer than 2 samples provided.

    Example:
        >>> import numpy as np
        >>> a = np.random.normal(0, 1, 50)
        >>> b = np.random.normal(0.5, 1, 50)
        >>> c = np.random.normal(1, 1, 50)
        >>> result = tukey_hsd(a, b, c)
        >>> print(result)
        >>> # For 99% CI: result.confint(confidence_level=0.99)

    References:
        - scipy.stats.tukey_hsd
        - Tukey, J. W. (1949). Comparing individual means in the analysis of variance.
    """
    if len(samples) < 2:
        raise ValueError("At least 2 samples required for Tukey HSD.")

    # Clean each sample
    samples_clean = []
    for i, sample in enumerate(samples):
        arr = np.asarray(sample)
        arr = arr[~np.isnan(arr)]
        if len(arr) < 2:
            raise ValueError(f"Sample {i} requires at least 2 observations. Got {len(arr)}.")
        samples_clean.append(arr)

    # scipy.stats.tukey_hsd doesn't accept confidence_level parameter
    # It computes 95% CI by default. For other levels, call confint() on result.
    result = stats.tukey_hsd(*samples_clean)

    return result


# =============================================================================
# CHI-SQUARE TEST
# =============================================================================

def chi_square_test(
    contingency_table: Union[np.ndarray, pd.DataFrame]
) -> Dict[str, Union[float, int, np.ndarray, str]]:
    """
    Perform chi-square test of independence on a contingency table.

    Tests whether two categorical variables are independent.
    Requires expected frequencies >= 5 for valid results.

    Args:
        contingency_table: 2D array or DataFrame of observed frequencies.

    Returns:
        Dictionary containing:
            - statistic: Chi-square test statistic
            - p_value: P-value of the test
            - dof: Degrees of freedom
            - expected_freq: Array of expected frequencies under independence
            - cramers_v: Cramer's V effect size
            - effect_size_interpretation: Interpretation of Cramer's V
            - is_significant: Whether to reject null hypothesis (p < 0.05 default)

    Raises:
        ValueError: If contingency table is not 2D or has insufficient data.

    Example:
        >>> import numpy as np
        >>> observed = np.array([[10, 20, 30], [20, 15, 25]])
        >>> result = chi_square_test(observed)
        >>> print(f"Chi-square: {result['statistic']:.3f}, p: {result['p_value']:.4f}")
        >>> print(f"Cramer's V: {result['cramers_v']:.3f} ({result['effect_size_interpretation']})")

    References:
        - scipy.stats.chi2_contingency
        - Cramer, C. (1946). Mathematical Methods of Statistics.
    """
    if isinstance(contingency_table, pd.DataFrame):
        contingency_table = contingency_table.values

    contingency_table = np.asarray(contingency_table)

    if contingency_table.ndim != 2:
        raise ValueError("Contingency table must be 2-dimensional.")

    if contingency_table.size < 4:
        raise ValueError("Contingency table too small for chi-square test.")

    # Perform chi-square test
    statistic, p_value, dof, expected_freq = stats.chi2_contingency(contingency_table)

    # Calculate Cramer's V (effect size for chi-square test)
    n = contingency_table.sum()  # Total sample size
    min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)

    if min_dim == 0:
        cramers_v = 0.0
    else:
        cramers_v = np.sqrt(statistic / (n * min_dim))

    # Interpret Cramer's V effect size
    # Based on Cohen (1988) and Rea & Parker (1992)
    if min_dim <= 2:
        # For 2x2 or 2xk tables
        if abs(cramers_v) < 0.1:
            interpretation = "negligible association"
        elif abs(cramers_v) < 0.3:
            interpretation = "weak association"
        elif abs(cramers_v) < 0.5:
            interpretation = "moderate association"
        else:
            interpretation = "strong association"
    else:
        # For larger tables (effect sizes tend to be smaller)
        if abs(cramers_v) < 0.05:
            interpretation = "negligible association"
        elif abs(cramers_v) < 0.15:
            interpretation = "weak association"
        elif abs(cramers_v) < 0.25:
            interpretation = "moderate association"
        else:
            interpretation = "strong association"

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "dof": int(dof),
        "expected_freq": expected_freq,
        "cramers_v": float(cramers_v),
        "effect_size_interpretation": interpretation,
        "is_significant": p_value < 0.05,
    }


# =============================================================================
# CORRELATION TEST
# =============================================================================

def correlation_test(
    x: np.ndarray,
    y: np.ndarray,
    method: Literal['auto', 'pearson', 'spearman'] = 'auto',
    alpha: float = 0.05
) -> Dict[str, Union[str, float, bool]]:
    """
    Test correlation between two variables with automatic method selection.

    If method='auto':
    - Tests normality of both variables
    - Uses Pearson if both are normal
    - Uses Spearman if either is non-normal

    Args:
        x: First variable data.
        y: Second variable data.
        method: Correlation method ('auto', 'pearson', 'spearman').
        alpha: Significance level for the test. Default is 0.05.

    Returns:
        Dictionary containing:
            - test_name: Name of the correlation test performed
            - correlation: Correlation coefficient
            - p_value: P-value for testing non-correlation
            - is_significant: True if p < alpha (correlation is significant)
            - interpretation: Brief interpretation of correlation strength

    Raises:
        ValueError: If x and y have different lengths or < 3 observations.

    Example:
        >>> import numpy as np
        >>> x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> y = x * 2 + np.random.normal(0, 0.5, 10)
        >>> result = correlation_test(x, y)
        >>> print(f"Correlation: {result['correlation']:.3f}")

    References:
        - scipy.stats.pearsonr
        - scipy.stats.spearmanr
    """
    x = np.asarray(x)
    y = np.asarray(y)

    # Remove pairwise NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]

    if len(x) != len(y):
        raise ValueError(f"x and y must have same length. Got {len(x)} and {len(y)}.")
    if len(x) < 3:
        raise ValueError(f"Correlation requires at least 3 observations. Got {len(x)}.")

    # Determine test method
    if method == 'auto':
        normality_x, _, _, _ = test_normality(x, alpha=alpha)
        normality_y, _, _, _ = test_normality(y, alpha=alpha)

        if normality_x and normality_y:
            method = 'pearson'
        else:
            method = 'spearman'

    # Run correlation test
    if method == 'pearson':
        correlation, p_value = stats.pearsonr(x, y)
        test_name = "Pearson correlation"
    else:  # spearman
        correlation, p_value = stats.spearmanr(x, y)
        test_name = "Spearman correlation"

    # Interpret correlation strength
    abs_corr = abs(correlation)
    if abs_corr < 0.1:
        strength = "negligible"
    elif abs_corr < 0.3:
        strength = "weak"
    elif abs_corr < 0.5:
        strength = "moderate"
    elif abs_corr < 0.7:
        strength = "strong"
    else:
        strength = "very strong"

    direction = "positive" if correlation > 0 else "negative"
    interpretation = f"{strength} {direction} correlation"

    return {
        "test_name": test_name,
        "correlation": float(correlation),
        "p_value": float(p_value),
        "is_significant": p_value < alpha,
        "interpretation": interpretation,
    }


# =============================================================================
# MANN-KENDALL TREND TEST
# =============================================================================

def mann_kendall_test(
    data: np.ndarray,
    alpha: float = 0.05
) -> Dict[str, Union[str, float, bool]]:
    """
    Perform Mann-Kendall trend test for time series data.

    The Mann-Kendall test is a non-parametric test for detecting monotonic
    trends in time series data. It is robust to non-normality and outliers.

    Null hypothesis: There is no monotonic trend in the data.
    Alternative: There is a monotonic trend (increasing or decreasing).

    Args:
        data: 1D array of time-ordered values (earliest to latest).
        alpha: Significance level for the test. Default is 0.05.

    Returns:
        Dictionary containing:
            - trend: Detected trend direction ('increasing', 'decreasing', 'no trend')
            - tau: Kendall's tau statistic (correlation with time order)
            - p_value: P-value of the test
            - is_significant: True if p < alpha (trend detected)
            - slope: Theil-Sen slope estimator (median of all pairwise slopes)

    Raises:
        ValueError: If data has fewer than 3 observations.

    Example:
        >>> import numpy as np
        >>> data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> result = mann_kendall_test(data)
        >>> print(f"Trend: {result['trend']}, p-value: {result['p_value']:.4f}")

    References:
        - pymannkendall.original_test
        - Mann, H. B. (1945). Nonparametric tests against trend.
        - Kendall, M. G. (1975). Rank Correlation Methods.
    """
    try:
        import pymannkendall as mk
    except ImportError:
        raise ImportError(
            "pymannkendall is required for mann_kendall_test. "
            "Install with: pip install pymannkendall"
        )

    data = np.asarray(data)
    data = data[~np.isnan(data)]

    if len(data) < 3:
        raise ValueError(
            f"Mann-Kendall test requires at least 3 observations. Got {len(data)}."
        )

    # Run original Mann-Kendall test
    result = mk.original_test(data, alpha=alpha)

    # Map pymannkendall results to our format
    trend_map = {
        'increasing': 'increasing',
        'decreasing': 'decreasing',
        'no trend': 'no trend',
    }

    return {
        "trend": trend_map.get(result.trend, 'no trend'),
        "tau": float(result.Tau),
        "p_value": float(result.p),
        "is_significant": result.p < alpha,
        "slope": float(result.slope) if hasattr(result, 'slope') else None,
    }
