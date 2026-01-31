# Phase 1: Statistical Rigor Layer - Research

**Researched:** 2025-01-30
**Domain:** Statistical testing, effect sizes, confidence intervals, reproducibility
**Confidence:** HIGH

## Summary

This phase adds publication-ready statistical rigor to 11 existing analysis modules. Research confirms Python's scientific ecosystem has mature, well-documented tools for all required functionality: SciPy 1.17+ provides comprehensive hypothesis testing, bootstrap confidence intervals, and FDR correction; `scipy.stats.tukey_hsd` (added in v1.11) handles post-hoc pairwise comparisons; and `pymannkendall` fills the gap for temporal trend testing. Effect size calculations require manual implementation (Cohen's d) or small packages (Cliff's delta), as SciPy's RFC for native Cohen's d is still in progress (September 2025). For reproducibility, standard Python patterns exist: explicit random seeds, data hashing (SHA256), and parameter documentation.

**Primary recommendation:** Use SciPy for all statistical testing (it has everything needed), add `pymannkendall` for Mann-Kendall trend tests, implement Cohen's d manually (simple formula), use `scipy.stats.false_discovery_control` for FDR correction, and create a centralized `stats_utils.py` module for reusable statistical functions.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **SciPy** | 1.17+ | Hypothesis testing, confidence intervals, correlation, FDR correction | Industry standard for statistical computing; includes t-tests, Mann-Whitney U, ANOVA (f_oneway), Kruskal-Wallis, chi-square, bootstrap CIs, Spearman/Pearson correlation, Tukey HSD (v1.11+), false_discovery_control (v1.11+) |
| **NumPy** | Latest | Random seed control, numerical operations | Foundation for reproducibility |
| **pandas** | Latest | Data manipulation, missing data analysis | Already in project; essential for data quality audit |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pymannkendall** | Latest | Mann-Kendall trend test for temporal data | Non-parametric trend detection in long-term crime trends |
| **statsmodels** | Latest | Advanced regression output, econometric-style analysis | Optional: use if detailed regression tables needed; otherwise SciPy suffices |
| **scikit-posthocs** | Latest | Additional post-hoc tests | Optional: only if scipy.stats.tukey_hsd insufficient |
| **cliffs-delta** | 1.0.1+ | Non-parametric effect size | Use when data is non-normal (Cliff's delta instead of Cohen's d) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| scipy.stats.false_discovery_control | statsmodels.stats.multitest.multipletests | SciPy is built-in; statsmodels requires new dependency. Functionality equivalent. |
| scipy.stats.tukey_hsd | statsmodels.stats.multicomp.pairwise_tukeyhsd | SciPy v1.11+ has native implementation; no need for statsmodels dependency |
| Manual Cohen's d | cohens-d-effect-size package | Manual implementation is 5 lines of code; adds unnecessary dependency |

**Installation:**
```bash
# Already installed
# scipy 1.17.0
# numpy, pandas, scikit-learn

# Add for Mann-Kendall trend testing
pip install pymannkendall

# Optional: for non-parametric effect size (Cliff's delta)
pip install cliffs-delta

# Optional: if econometric-style regression output needed
pip install statsmodels
```

## Architecture Patterns

### Recommended Project Structure

```
analysis/
├── config.py              # Existing: constants, may add STAT_CONFIG
├── utils.py               # Existing: data loading, add statistical utilities
├── stats_utils.py         # NEW: centralized statistical testing functions
├── reproducibility.py     # NEW: data versioning, seed management
├── data_quality.py        # UPGRADE: add statistical quality assessment
├── temporal_analysis.py   # UPGRADE: add trend tests, CIs
├── categorical_analysis.py# UPGRADE: add chi-square, effect sizes
├── spatial_analysis.py    # UPGRADE: add spatial correlation tests
├── cross_analysis.py      # UPGRADE: add interaction tests
└── [other modules]        # UPGRADE: add relevant statistical tests
```

### Pattern 1: Statistical Testing Utilities Module

**What:** Centralized `stats_utils.py` containing all reusable statistical functions

**When to use:** For any statistical test that will be called from multiple analysis modules

**Example:**
```python
# analysis/stats_utils.py
from scipy import stats
import numpy as np
from typing import Tuple, Literal, Optional

def test_normality(data: np.ndarray, alpha: float = 0.05) -> Tuple[bool, float, float]:
    """
    Test data for normality using Shapiro-Wilk test.

    Args:
        data: Array of sample data
        alpha: Significance level for rejecting normality

    Returns:
        Tuple of (is_normal, statistic, p_value)
    """
    if len(data) > 5000:
        # Shapiro-Wilk p-value less accurate for n > 5000
        stat, pval = stats.normaltest(data)
    else:
        stat, pval = stats.shapiro(data)

    is_normal = pval > alpha
    return is_normal, stat, pval


def compare_two_samples(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05
) -> dict:
    """
    Compare two samples with appropriate test based on normality.

    Chooses t-test if both samples are normal, Mann-Whitney U otherwise.

    Returns:
        Dictionary with test_name, statistic, p_value, is_significant
    """
    x_normal, _, x_p = test_normality(x, alpha)
    y_normal, _, y_p = test_normality(y, alpha)

    if x_normal and y_normal:
        # Parametric: independent t-test
        stat, pval = stats.ttest_ind(x, y)
        test_name = "Independent t-test"
    else:
        # Non-parametric: Mann-Whitney U
        stat, pval = stats.mannwhitneyu(x, y, alternative='two-sided')
        test_name = "Mann-Whitney U"

    return {
        "test_name": test_name,
        "statistic": stat,
        "p_value": pval,
        "is_significant": pval < alpha,
    }


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate Cohen's d effect size for two samples.

    Interpretation: small=0.2, medium=0.5, large=0.8

    Source: Standard formula, not yet in SciPy (RFC in progress as of Sep 2025)
    """
    nx, ny = len(x), len(y)
    dof = nx + ny - 2

    # Pooled standard deviation
    pooled_sd = np.sqrt(((nx - 1) * np.var(x, ddof=1) +
                         (ny - 1) * np.var(y, ddof=1)) / dof)

    # Cohen's d
    d = (np.mean(x) - np.mean(y)) / pooled_sd
    return d


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> Tuple[float, str]:
    """
    Calculate Cliff's Delta non-parametric effect size.

    Returns:
        Tuple of (effect_size, interpretation)
        Interpretation: negligible=<0.147, small=<0.33, medium=<0.474, large>=0.474
    """
    # Cliff's Delta implementation or use cliffs-delta package
    # ... implementation details ...
    return delta, interpretation


def apply_fdr_correction(
    p_values: np.ndarray,
    method: Literal['bh', 'by'] = 'bh'
) -> np.ndarray:
    """
    Apply False Discovery Rate correction to p-values.

    Args:
        p_values: Array of p-values
        method: 'bh' for Benjamini-Hochberg, 'by' for Benjamini-Yekutieli

    Returns:
        Array of FDR-adjusted p-values

    Source: scipy.stats.false_discovery_control (v1.11+)
    """
    from scipy.stats import false_discovery_control
    return false_discovery_control(p_values, method=method)


def bootstrap_ci(
    data: np.ndarray,
    statistic: callable,
    confidence_level: float = 0.99,
    n_resamples: int = 9999,
    random_state: Optional[int] = None
) -> Tuple[float, float, float]:
    """
    Calculate bootstrap confidence interval for any statistic.

    Args:
        data: Sample data
        statistic: Function that computes the statistic (e.g., np.mean)
        confidence_level: Confidence level (0.99 for 99% CI)
        n_resamples: Number of bootstrap resamples
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (lower_bound, upper_bound, point_estimate)

    Source: scipy.stats.bootstrap (v1.9+)
    """
    from scipy.stats import bootstrap

    res = bootstrap(
        (data,),
        statistic,
        confidence_level=confidence_level,
        n_resamples=n_resamples,
        random_state=random_state
    )

    ci = res.confidence_interval
    return ci.low, ci.high, res.standard_error
```

### Pattern 2: Reproducibility Infrastructure Module

**What:** `reproducibility.py` for data versioning and seed management

**Example:**
```python
# analysis/reproducibility.py
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json


class DataVersion:
    """Track data version for reproducibility."""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.metadata = self._compute_metadata()

    def _compute_metadata(self) -> Dict[str, Any]:
        """Compute SHA256 hash and metadata of data file."""
        sha256_hash = hashlib.sha256()

        with open(self.data_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        # Load just enough for metadata
        df_sample = pd.read_parquet(self.data_path)

        return {
            "sha256": sha256_hash.hexdigest(),
            "row_count": len(df_sample),
            "column_count": len(df_sample.columns),
            "columns": list(df_sample.columns),
            "date_range": (
                str(df_sample["dispatch_date"].min()),
                str(df_sample["dispatch_date"].max())
            ) if "dispatch_date" in df_sample.columns else None,
            "timestamp": datetime.now().isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.metadata


def set_global_seed(seed: int = 42) -> None:
    """
    Set random seeds for all relevant libraries.

    Call at module import for reproducibility.
    """
    np.random.seed(seed)
    # Add others as needed:
    # import random
    # random.seed(seed)
```

### Pattern 3: Test-Then-Decide Normality Assessment

**What:** Always check normality before choosing parametric vs non-parametric tests

**When to use:** Before any comparison of means/medians

**Example:**
```python
def analyze_group_comparison(groups: dict, alpha: float = 0.05):
    """
    Compare multiple groups with appropriate test.

    1. Test each group for normality
    2. If all normal: ANOVA + Tukey HSD
    3. If any non-normal: Kruskal-Wallis + Dunn's test
    """
    # Check normality for each group
    normality_results = {
        name: test_normality(data, alpha=alpha)
        for name, data in groups.items()
    }

    all_normal = all(result[0] for result in normality_results.values())

    if all_normal:
        # Parametric: ANOVA
        samples = [data for data in groups.values()]
        f_stat, p_value = stats.f_oneway(*samples)

        # Post-hoc: Tukey HSD
        tukey_result = stats.tukey_hsd(*samples)
        ci = tukey_result.confidence_interval(confidence_level=0.99)
    else:
        # Non-parametric: Kruskal-Wallis
        samples = [data for data in groups.values()]
        h_stat, p_value = stats.kruskal(*samples)
        # Post-hoc: Dunn's test (via scikit-posthocs or pairwise Mann-Whitney with FDR)

    return {
        "all_normal": all_normal,
        "omnibus_test": "ANOVA" if all_normal else "Kruskal-Wallis",
        "statistic": f_stat if all_normal else h_stat,
        "p_value": p_value,
        "post_hoc": "Tukey HSD" if all_normal else "Dunn's test",
    }
```

### Anti-Patterns to Avoid

- **Using fixed p-value thresholds without context**: Report exact p-values, not just "p < 0.05"
- **Ignoring effect sizes**: Statistical significance != practical significance; always report effect sizes
- **Assuming normality without testing**: Crime data is often skewed (Poisson-like); test first
- **Applying the same test everywhere**: Different data types require different tests
- **Forggetting to document random seeds**: Makes results irreproducible
- **Using Bonferroni for exploratory analysis**: Too conservative; prefer FDR (Benjamini-Hochberg)
- **Reporting only corrected p-values**: Show both raw and FDR-adjusted for transparency

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Normality testing** | Custom Shapiro-Wilk implementation | `scipy.stats.shapiro` or `scipy.stats.normaltest` | Edge cases: n > 5000 accuracy issues |
| **Mann-Whitney U test** | Custom rank-based test | `scipy.stats.mannwhitneyu` | Handles ties, continuity correction automatically |
| **ANOVA** | Custom F-statistic calculation | `scipy.stats.f_oneway` | Numerically stable, well-tested |
| **Tukey HSD** | Custom pairwise comparisons | `scipy.stats.tukey_hsd` (v1.11+) | Controls family-wise error rate correctly |
| **FDR correction** | Custom Benjamini-Hochberg | `scipy.stats.false_discovery_control` | Handles edge cases, supports BY method |
| **Bootstrap CI** | Custom resampling loop | `scipy.stats.bootstrap` | Supports BCa method, vectorized, handles paired data |
| **Chi-square test** | Manual expected frequency calculation | `scipy.stats.chi2_contingency` | Handles sparse tables, provides expected values |
| **Correlation tests** | Manual t-statistic for correlation | `scipy.stats.pearsonr`, `scipy.stats.spearmanr` | Returns p-value directly, handles NaNs |
| **Mann-Kendall trend** | Custom tau calculation | `pymannkendall.original_test` | Handles ties, seasonal decomposition options |

**Key insight:** Statistical functions have numerical edge cases (ties in ranks, sparse contingency tables, large sample corrections) that hand-rolled implementations miss.

## Common Pitfalls

### Pitfall 1: Shapiro-Wilk Sample Size Sensitivity

**What goes wrong:** Shapiro-Wilk test is sensitive to sample size - large samples almost always reject normality even for minor deviations

**Why it happens:** Test accumulates evidence; n=5000 will detect tiny departures from normality

**How to avoid:**
1. Use `scipy.stats.normaltest` for n > 5000 (D'Agostino-Pearson)
2. Combine with visual inspection (Q-Q plots)
3. Consider practical significance: Is deviation large enough to matter?

**Warning signs:** All Shapiro-Wilk tests come back significant with large n

### Pitfall 2: Inappropriate Multiple Testing Correction

**What goes wrong:** Using Bonferroni for exploratory analysis with 23 districts = no significant results

**Why it happens:** Bonferroni is too conservative when many tests; FDR is more appropriate for EDA

**How to avoid:**
1. Default to `scipy.stats.false_discovery_control(method='bh')`
2. Use Bonferroni only for pre-specified key comparisons
3. Report both raw and adjusted p-values

**Warning signs:** Everything becomes non-significant after correction

### Pitfall 3: Non-Independent P-Values in FDR Correction

**What goes wrong:** Applying FDR to correlated tests without adjustment

**Why it happens:** FDR assumes independence; crime data has spatial/temporal correlation

**How to avoid:**
1. For correlated tests, use `method='by'` (Benjamini-Yekutieli) in `false_discovery_control`
2. Or group correlated tests and apply FDR within groups

**Warning signs:** Nearby districts show identical significant patterns

### Pitfall 4: Treating 99% CI and 0.01 Threshold as Equivalent

**What goes wrong:** Declaring results significant when p < 0.01 but 99% CI includes zero

**Why it happens:** 99% CI and p < 0.01 are not mathematically equivalent (two-sided vs one-sided, different approximations)

**How to avoid:**
1. Report both; let reader decide
2. If CI includes zero, acknowledge uncertainty regardless of p-value
3. Don't claim "significant" when CI includes the null value

**Warning signs:** p = 0.009 but CI = [-2, 10] for a difference

### Pitfall 5: Ignoring Effect Size Interpretation

**What goes wrong:** Claiming "significant" for tiny effect (e.g., Cohen's d = 0.05) with large n

**Why it happens:** Statistical power increases with n; tiny differences become significant

**How to avoid:**
1. Always report effect size with p-value
2. Use Cohen's benchmarks: small=0.2, medium=0.5, large=0.8
3. Discuss practical significance: "Statistically significant but practically negligible"

**Warning signs:** p < 0.001 with n=100,000 but tiny difference

### Pitfall 6: Spurious Temporal Correlation (Trend)

**What goes wrong:** Claiming summer heat causes crime when both trend upward over 20 years

**Why it happens:** Shared temporal trend creates spurious correlation

**How to avoid:**
1. Detrend data first (subtract long-term trend)
2. Use Mann-Kendall for trend detection
3. Report correlation on residuals, not raw data

**Warning signs:** Two variables both increase over 20 years and correlate at r=0.8

## Code Examples

### Example 1: Normality Test and Appropriate Test Selection

```python
# Source: scipy.stats.shapiro documentation
import numpy as np
from scipy import stats

# Sample data
group_a = np.array([148, 154, 158, 160, 161, 162, 166, 170, 182, 195, 236])
group_b = np.array([140, 145, 150, 152, 155, 158, 160, 165, 175, 185])

# Test normality
stat_a, p_a = stats.shapiro(group_a)
stat_b, p_b = stats.shapiro(group_b)

alpha = 0.05
if p_a > alpha and p_b > alpha:
    # Both normal: use t-test
    stat, pval = stats.ttest_ind(group_a, group_b)
    print(f"Independent t-test: t={stat:.3f}, p={pval:.4f}")
else:
    # Non-normal: use Mann-Whitney U
    stat, pval = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
    print(f"Mann-Whitney U: U={stat:.1f}, p={pval:.4f}")
```

### Example 2: Bootstrap Confidence Interval

```python
# Source: scipy.stats.bootstrap documentation
from scipy.stats import bootstrap
import numpy as np

def calculate_mean(data, axis):
    return np.mean(data, axis=axis)

# Sample data (e.g., crime counts per district)
crime_counts = np.array([145, 167, 189, 201, 223, 245, 267, 289])

# Calculate 99% bootstrap CI
res = bootstrap(
    (crime_counts,),
    calculate_mean,
    confidence_level=0.99,  # 99% CI as specified in requirements
    n_resamples=10000,
    random_state=42
)

print(f"Mean: {np.mean(crime_counts):.1f}")
print(f"99% CI: [{res.confidence_interval.low:.1f}, {res.confidence_interval.high:.1f}]")
print(f"Standard Error: {res.standard_error:.2f}")
```

### Example 3: FDR Correction for Multiple Comparisons

```python
# Source: scipy.stats.false_discovery_control documentation
from scipy.stats import false_discovery_control
import numpy as np

# P-values from testing 23 districts
p_values = np.array([
    0.001, 0.023, 0.045, 0.089, 0.120, 0.167, 0.201, 0.245,
    0.301, 0.356, 0.412, 0.478, 0.534, 0.589, 0.645, 0.701,
    0.756, 0.812, 0.867, 0.923, 0.978, 0.034, 0.056
])

# Apply Benjamini-Hochberg FDR correction
p_adjusted = false_discovery_control(p_values, method='bh')

# Report results
for i, (p_raw, p_adj) in enumerate(zip(p_values, p_adjusted)):
    sig = "***" if p_adj < 0.01 else "**" if p_adj < 0.05 else "*" if p_adj < 0.10 else ""
    print(f"District {i+1:2d}: p={p_raw:.3f}, p_FDR={p_adj:.3f} {sig}")
```

### Example 4: Tukey HSD Post-Hoc Test

```python
# Source: scipy.stats.tukey_hsd documentation
from scipy.stats import tukey_hsd
import numpy as np

# Crime counts by season (multiple years)
summer = np.array([450, 467, 489, 501, 523, 545, 567, 589])
fall = np.array([412, 425, 438, 451, 464, 477, 490, 503])
winter = np.array([378, 392, 406, 420, 434, 448, 462, 476])
spring = np.array([395, 408, 421, 434, 447, 460, 473, 486])

# Perform Tukey HSD test
result = tukey_hsd(summer, fall, winter, spring)

# Get 99% confidence intervals for pairwise differences
ci = result.confidence_interval(confidence_level=0.99)

print("Pairwise Comparisons (99% CI):")
for i in range(4):
    for j in range(4):
        if i < j:  # Only upper triangle
            names = ["Summer", "Fall", "Winter", "Spring"]
            lower = ci.low[i, j]
            upper = ci.high[i, j]
            print(f"{names[i]} vs {names[j]}: [{lower:.1f}, {upper:.1f}]")
```

### Example 5: Mann-Kendall Trend Test

```python
# Source: pymannkendall package
import pymannkendall as mk
import numpy as np

# Yearly crime counts (2006-2025)
yearly_counts = np.array([
    84567, 82345, 80123, 78901, 77567, 76234, 75890, 74567,
    73234, 71890, 68567, 64234, 58901, 54567, 52345, 51234,
    49890, 48567, 47890, 46543
])

# Perform Mann-Kendall trend test
result = mk.original_test(yearly_counts)

print(f"Trend: {result.trend}")
print(f"Tau: {result.Tau:.4f}")
print(f"P-value: {result.p:.4f}")
print(f"Significant at alpha=0.01: {result.p < 0.01}")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| **Manual FDR implementation** | `scipy.stats.false_discovery_control` (v1.11.0, 2023) | SciPy 1.11.0 | No need for custom BH code or statsmodels dependency |
| **statsmodels for Tukey HSD** | `scipy.stats.tukey_hsd` (v1.11.0, 2023) | SciPy 1.11.0 | Native implementation; better integration with scipy ecosystem |
| **Manual bootstrap** | `scipy.stats.bootstrap` (v1.9.0, 2022) | SciPy 1.9.0 | Supports BCa method, vectorized operations, paired data |
| **Custom CI calculation** | Bootstrap or analytical CIs built into test results | Ongoing | Many scipy test functions now return confidence intervals |
| **External packages for Cohen's d** | Manual 5-line implementation | RFC active (Sep 2025) | SciPy RFC in progress; manual code sufficient for now |

**Deprecated/outdated:**
- **Manual Benjamini-Hochberg implementation**: Use `scipy.stats.false_discovery_control`
- **Using `statsmodels.stats.multitest.multipletests`**: Functionally equivalent but requires extra dependency
- **Assuming t-test normality without testing**: Always use Shapiro-Wilk/normaltest first
- **Reporting only "p < 0.05"**: Report exact p-values, not thresholds
- **Bonferroni for exploratory analysis**: Too conservative; prefer FDR for EDA

## Open Questions

### 1. Effect Size for Non-Normal Multi-Group Comparisons

**What we know:** Kruskal-Wallis is the non-parametric alternative to ANOVA, but there's no universal effect size for multi-group non-parametric comparisons.

**What's unclear:** Best practice for effect size when comparing 23 districts with non-normal data. Options:
- Epsilon-squared (based on H statistic)
- Rank-biserial correlation
- Report median differences with CIs

**Recommendation:** Use median differences with bootstrap CIs as most interpretable for crime counts.

### 2. Spatial Correlation Testing

**What we know:** Crime data has spatial autocorrelation (nearby areas similar). Standard tests assume independence.

**What's unclear:** How to incorporate spatial correlation into statistical testing without specialized spatial statistics packages (e.g., `pysal`, `libpysal`).

**Recommendation:** Document as limitation; consider adding `pysal` in Phase 2 if spatial correlation testing becomes critical.

### 3. Zero-Inflated Count Data

**What we know:** Crime data is count-based (non-negative integers) and often has excess zeros. Standard tests assume continuous data.

**What's unclear:** Whether to use Poisson/negative binomial regression instead of standard tests for some comparisons.

**Recommendation:** For Phase 1, use standard tests on aggregated counts (by month/district). Note zero-inflation as limitation; consider GLM approaches in Phase 2 if needed.

### 4. Time Series Dependence

**What we know:** Temporal data has autocorrelation (today's crime correlated with yesterday's). Standard trend tests assume independence.

**What's unclear:** Mann-Kendall handles some autocorrelation but may need pre-whitening for strong serial dependence.

**Recommendation:** Use Mann-Kendall as specified; document autocorrelation as limitation if detected.

## Sources

### Primary (HIGH confidence)

- **SciPy Documentation** (`/websites/scipy_doc_scipy`):
  - `scipy.stats.ttest_ind` - Independent samples t-test
  - `scipy.stats.mannwhitneyu` - Mann-Whitney U test
  - `scipy.stats.f_oneway` - One-way ANOVA
  - `scipy.stats.kruskal` - Kruskal-Wallis H-test
  - `scipy.stats.shapiro` - Shapiro-Wilk normality test
  - `scipy.stats.chi2_contingency` - Chi-square test of independence
  - `scipy.stats.pearsonr`, `scipy.stats.spearmanr` - Correlation tests
  - `scipy.stats.bootstrap` - Bootstrap confidence intervals (v1.9+)
  - `scipy.stats.false_discovery_control` - FDR correction (v1.11+)
  - `scipy.stats.tukey_hsd` - Tukey HSD post-hoc test (v1.11+)

- **SciPy v1.17.0 Manual** - [false_discovery_control](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html)

- **pymannkendall** - [GitHub: mmhs013/pyMannKendall](https://github.com/mmhs013/pyMannKendall) - Mann-Kendall trend test implementation

### Secondary (MEDIUM confidence)

- [GeeksforGeeks: How to Perform a One-Way ANOVA in Python](https://www.geeksforgeeks.org/python/how-to-perform-a-one-way-anova-in-python/) (July 23, 2025)

- [GeeksforGeeks: Post Hoc analysis](https://www.geeksforgeeks.org/data-science/post-hoc-analysis/) (July 23, 2025)

- [SciPy RFC: Adding Cohen's d to scipy.stats](https://discuss.scientific-python.org/t/rfc-adding-cohen-s-d-effect-size-function-to-scipy-stats/2130) (September 26, 2025)

- [Statology: 5 Effect Size Measures You'll Actually Use](https://www.statology.org/5-effect-size-measures-youll-actually-use/) (October 2025)

- [Statology: Building Reproducible Research Pipelines in Python](https://www.statology.org/building-reproducible-research-pipelines-in-python-from-data-collection-to-reporting/) (July 4, 2025)

- [Stack Overflow: Calculating adjusted p-values in Python](https://stackoverflow.com/questions/25185205/calculating-adjusted-p-values-in-python)

### Tertiary (LOW confidence)

- Various blog posts and tutorials verified against official documentation above

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official documentation
- Architecture: HIGH - Patterns verified against SciPy docs and established best practices
- Pitfalls: HIGH - Based on documented statistical issues and library behaviors

**Research date:** 2025-01-30
**Valid until:** 2025-03-01 (60 days - library versions stable, but RFCs in progress)
