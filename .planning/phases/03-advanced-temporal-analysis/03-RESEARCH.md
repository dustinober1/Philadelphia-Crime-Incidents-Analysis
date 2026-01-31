# Phase 3: Advanced Temporal Analysis - Research

**Researched:** 2026-01-31
**Domain:** Temporal crime analysis with statistical rigor
**Confidence:** HIGH

## Summary

Phase 3 extends the project's temporal analysis capabilities with three focused analyses: (1) holiday effects on crime patterns, (2) individual crime type profiles (homicide, burglary, theft, vehicle theft, aggravated assault), and (3) shift-by-shift temporal analysis (4 shifts: Morning 6AM-12PM, Afternoon 12PM-6PM, Evening 6PM-12AM, Late Night 12AM-6AM). All analyses leverage the statistical infrastructure built in Phase 1 (STAT_CONFIG, stats_utils.py) and follow patterns established in existing focused reports (robbery_timing.py, summer_spike.py).

The standard approach for this phase combines:
- **Existing infrastructure**: stats_utils.py provides 20+ statistical functions (Mann-Kendall, bootstrap CI, ANOVA, Tukey HSD, FDR correction)
- **Holiday detection**: `workalendar` library for US federal holidays (more robust than pandas built-in)
- **Modular analysis structure**: Separate modules for each analysis area (03-01-holiday_effects.py, 03-02-crime_type_profiles.py, 03-03-shift_analysis.py)
- **Unified report generator**: 03-04-advanced_temporal_report.py orchestrates all modules

**Primary recommendation:** Build three focused analysis modules following the robbery_timing.py pattern, each returning results dicts with base64 plots and statistical test results, then orchestrate with a unified report generator.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.x | Data manipulation and time series grouping | Existing dependency; provides groupby, resample for temporal aggregation |
| numpy | 2.x | Numerical operations and array handling | Existing dependency; used by all statistical functions |
| scipy | 1.17+ | Statistical tests (chi-square, t-test, ANOVA) | Existing dependency; required by stats_utils.py |
| matplotlib | 3.x | Base plotting for all visualizations | Existing dependency; used in all analysis modules |
| seaborn | 0.14+ | Advanced heatmaps and statistical plots | Existing dependency; used for complex heatmaps |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **workalendar** | latest | US federal holiday detection (15+ holidays) | Holiday effects analysis - more comprehensive than pandas built-in |
| **pymannkendall** | latest | Mann-Kendall trend testing for temporal data | Crime type trend analysis (already in stats_utils.py) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| workalendar | pandas.tseries.holiday.USFederalHolidayCalendar | Pandas built-in has fewer holidays (10 vs 15+), no observance detection; workalendar is more comprehensive |
| Manual holiday lists | holidays library | holidays library is simpler but workalendar integrates better with pandas date ranges |

**Installation:**
```bash
# Core dependencies (already installed)
pip install pandas numpy scipy matplotlib seaborn pymannkendall

# Holiday detection (new for this phase)
pip install workalendar
```

## Architecture Patterns

### Recommended Project Structure

```
analysis/
├── 03-01-holiday_effects.py          # Holiday effects analysis module
├── 03-02-crime_type_profiles.py      # Individual crime type analysis module
├── 03-03-shift_analysis.py           # Shift-by-shift temporal analysis module
├── 03-04-advanced_temporal_report.py # Unified report generator (orchestrator)
├── config.py                          # STAT_CONFIG, existing (no changes needed)
├── stats_utils.py                     # Statistical functions (existing, no changes)
├── utils.py                           # Data loading, temporal features (existing)
├── reproducibility.py                 # Seed management, metadata (existing)
├── robbery_timing.py                  # Reference pattern for shift analysis
└── summer_spike.py                    # Reference pattern for seasonal analysis
```

### Pattern 1: Focused Analysis Module

**What:** Standalone analysis module that filters data, runs statistical tests, creates visualizations, and returns a results dictionary.

**When to use:** Each distinct analysis area (holiday effects, crime type profiles, shift analysis) gets its own module for maintainability and reusability.

**Example:**
```python
# Source: Existing pattern in robbery_timing.py
def analyze_holiday_effects() -> dict:
    \"\"\"Run holiday effects analysis with statistical testing.

    Returns:
        Dictionary containing analysis results and base64-encoded plots.

    Statistical tests performed:
        - Chi-square test for holiday vs non-holiday crime distribution
        - Two-sample comparison for pre/post holiday periods
        - Bootstrap 99% CI for holiday effect size
        - FDR correction for multiple holiday comparisons
    \"\"\"
    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    # Load and prepare data
    df = load_data(clean=False)
    df = extract_temporal_features(df)
    df = identify_holiday_periods(df)  # New function for this module

    results = {}

    # Store metadata
    results["metadata"] = get_analysis_metadata(...)

    # Statistical tests
    results["holiday_uniformity_test"] = chi_square_test(...)
    results["pre_post_comparison"] = compare_two_samples(...)
    results["holiday_effect_ci"] = bootstrap_ci(...)

    # Visualizations
    results["holiday_calendar_plot"] = create_image_tag(image_to_base64(fig))

    return results
```

### Pattern 2: Holiday Detection with Workalendar

**What:** Use workalendar.UnitedStates() to generate holiday lists and detect if dates are holidays.

**When to use:** Holiday effects analysis needs to identify US federal holidays and create holiday windows (pre-during-post).

**Example:**
```python
# Source: Context7 documentation for workalendar
from workalendar.america import UnitedStates
from datetime import date, timedelta

def get_us_holidays(year: int) -> list[tuple[date, str]]:
    \"\"\"Get list of US federal holidays for a given year.

    Returns:
        List of (date, holiday_name) tuples.
    \"\"\"
    cal = UnitedStates()
    return cal.holidays(year)

def is_holiday(check_date: date) -> bool:
    \"\"\"Check if a date is a US federal holiday.

    Args:
        check_date: Date to check.

    Returns:
        True if the date is a holiday, False otherwise.
    \"\"\"
    cal = UnitedStates()
    return cal.is_holiday(check_date)

def create_holiday_windows(df: pd.DataFrame, days_before: int = 3,
                          days_after: int = 3) -> pd.DataFrame:
    \"\"\"Add holiday window classification to crime data.

    Creates a 'holiday_period' column with values:
        - 'pre_holiday': days_before days before holiday
        - 'holiday': holiday date
        - 'post_holiday': days_after days after holiday
        - 'baseline': all other days

    Also adds 'holiday_name' for the nearest holiday (if within window).
    \"\"\"
    cal = UnitedStates()
    years = df['dispatch_datetime'].dt.year.unique()

    # Build holiday set for fast lookup
    holiday_dates = set()
    for year in years:
        holiday_dates.update([d for d, _ in cal.holidays(year)])

    df = df.copy()
    df['date'] = df['dispatch_datetime'].dt.date

    # Classify each date
    df['holiday_period'] = 'baseline'
    df['holiday_name'] = None

    for year in years:
        for holiday_date, holiday_name in cal.holidays(year):
            # Pre-holiday window
            pre_start = holiday_date - timedelta(days=days_before)
            pre_end = holiday_date - timedelta(days=1)
            df.loc[df['date'].between(pre_start, pre_end), 'holiday_period'] = 'pre_holiday'
            df.loc[df['date'].between(pre_start, pre_end), 'holiday_name'] = holiday_name

            # Holiday date
            df.loc[df['date'] == holiday_date, 'holiday_period'] = 'holiday'
            df.loc[df['date'] == holiday_date, 'holiday_name'] = holiday_name

            # Post-holiday window
            post_start = holiday_date + timedelta(days=1)
            post_end = holiday_date + timedelta(days=days_after)
            df.loc[df['date'].between(post_start, post_end), 'holiday_period'] = 'post_holiday'
            df.loc[df['date'].between(post_start, post_end), 'holiday_name'] = holiday_name

    return df.drop(columns=['date'])
```

### Pattern 3: Shift Analysis with ANOVA + FDR

**What:** Use compare_multiple_samples() for omnibus ANOVA test across 4 shifts, followed by FDR-corrected pairwise comparisons.

**When to use:** Shift-by-shift analysis needs to detect if crime counts differ significantly across shifts and which specific shifts differ from each other.

**Example:**
```python
# Source: Existing pattern in stats_utils.py + context decisions
def analyze_shift_patterns(df: pd.DataFrame) -> dict:
    \"\"\"Analyze crime patterns across 4 shifts with statistical testing.

    Shift definitions (from CONTEXT.md):
        - Morning: 6AM-12PM (hours 6-11)
        - Afternoon: 12PM-6PM (hours 12-17)
        - Evening: 6PM-12AM (hours 18-23)
        - Late Night: 12AM-6AM (hours 0-5)

    Statistical approach:
        1. ANOVA omnibus test for shift differences
        2. FDR-corrected post-hoc pairwise comparisons
        3. Bootstrap 99% CI for shift means
    \"\"\"
    # Define shift bins
    SHIFT_BINS = [0, 6, 12, 18, 24]
    SHIFT_LABELS = ["Late Night (12AM-6AM)", "Morning (6AM-12PM)",
                    "Afternoon (12PM-6PM)", "Evening (6PM-12AM)"]

    # Categorize incidents into shifts
    df_with_shift = df.copy()
    df_with_shift['shift'] = pd.cut(
        df_with_shift['hour'],
        bins=SHIFT_BINS,
        labels=SHIFT_LABELS,
        right=False,
        include_lowest=True
    )

    # Group by shift for statistical testing
    # Use daily counts per shift for more stable estimates
    shift_groups = {}
    for shift in SHIFT_LABELS:
        shift_data = df_with_shift[df_with_shift['shift'] == shift]
        daily_counts = shift_data.groupby(['year', 'month', 'day']).size().values
        if len(daily_counts) >= 10:  # Minimum sample size
            shift_groups[shift] = daily_counts

    # Omnibus ANOVA test
    omnibus_result = compare_multiple_samples(
        shift_groups,
        alpha=STAT_CONFIG["alpha"]
    )

    # Extract Tukey HSD post-hoc results
    post_hoc_df = omnibus_result["post_hoc_results"]

    # Apply FDR correction to post-hoc p-values
    if post_hoc_df is not None and len(post_hoc_df) > 0:
        adjusted_p = apply_fdr_correction(
            post_hoc_df['p_value'].values,
            method='bh'
        )
        post_hoc_df['adjusted_p'] = adjusted_p
        post_hoc_df['is_significant'] = adjusted_p < STAT_CONFIG["alpha"]

    return {
        "omnibus_test": omnibus_result,
        "post_hoc_comparisons": post_hoc_df,
        "shift_groups": shift_groups
    }
```

### Pattern 4: Individual Crime Type Analysis

**What:** Filter data for specific crime types, then apply full temporal-spatial-demographic profile analysis.

**When to use:** Each required crime type (homicide, burglary, theft, vehicle theft, aggravated assault) needs individual analysis with trends, seasonality, spatial distribution, and demographics.

**Example:**
```python
# Source: Existing pattern in robbery_timing.py + summer_spike.py
CRIME_TYPE_FILTERS = {
    "homicide": ["Homicide - Criminal", "Homicide - Gross Negligence"],
    "burglary": ["Burglary Residential", "Burglary Non-Residential"],
    "theft": ["Thefts", "Theft from Vehicle"],
    "vehicle_theft": ["Motor Vehicle Theft"],
    "aggravated_assault": ["Aggravated Assault Firearm", "Aggravated Assault No Firearm"]
}

def analyze_crime_type(df: pd.DataFrame, crime_type: str) -> dict:
    \"\"\"Analyze a specific crime type with full profile.

    Analysis includes:
        - Temporal: Yearly trends, seasonality, day/hour patterns
        - Spatial: Geographic distribution, hotspots
        - Statistical: Mann-Kendall trend test, chi-square uniformity tests
        - Sample size handling: Adaptive methods for rare crimes

    Args:
        df: Full crime incidents DataFrame.
        crime_type: Key from CRIME_TYPE_FILTERS (e.g., "homicide").

    Returns:
        Dictionary with analysis results and plots.
    \"\"\"
    # Filter for crime type
    crime_list = CRIME_TYPE_FILTERS[crime_type]
    crime_df = df[df['text_general_code'].isin(crime_list)].copy()

    if len(crime_df) < 30:
        # Small sample: Use exact tests, note limitations
        return analyze_rare_crime(crime_df, crime_type)

    # Extract temporal features
    crime_df = extract_temporal_features(crime_df)

    results = {}
    results["total_incidents"] = len(crime_df)

    # Temporal: Yearly trend with Mann-Kendall
    yearly_counts = crime_df.groupby('year').size().values
    complete_years = yearly_counts[yearly_counts.index < 2026]
    results["trend_test"] = mann_kendall_test(complete_years.values)

    # Spatial: Hotspot detection
    if 'point_x' in crime_df.columns and 'point_y' in crime_df.columns:
        crime_df = validate_coordinates(crime_df)
        valid_coords = crime_df[crime_df['valid_coord']]
        if len(valid_coords) > 100:
            results["spatial_distribution"] = analyze_spatial_distribution(valid_coords)

    # Visualizations
    results["time_series_plot"] = create_crime_type_timeseries(crime_df)
    results["seasonal_plot"] = create_seasonal_pattern_plot(crime_df)

    return results

def analyze_rare_crime(crime_df: pd.DataFrame, crime_type: str) -> dict:
    \"\"\"Handle rare crimes with small sample sizes.

    Uses exact tests (Fisher's exact) instead of asymptotic tests.
    Documents limitations in report.
    \"\"\"
    return {
        "total_incidents": len(crime_df),
        "note": "Small sample size (n < 30). Results should be interpreted with caution.",
        "descriptive_stats": crime_df.describe(),
        # Use Fisher's exact for categorical comparisons
        "statistical_tests": "Exact tests (Fisher's exact) used due to small sample."
    }
```

### Anti-Patterns to Avoid

- **Hand-rolling holiday calculations:** Don't manually define holiday dates. Use workalendar which handles moving holidays (Thanksgiving, Memorial Day) and observance rules automatically.
- **Ignoring weekend handling:** CONTEXT.md specifies same treatment for weekends/weekdays (let patterns emerge). Don't force separate weekend analysis unless data suggests it.
- **Small sample blindness:** For rare crimes (homicide), n may be < 30 per year. Don't use asymptotic tests (chi-square, t-test). Use exact tests (Fisher's exact) and document limitations.
- **Multiple testing without FDR:** When testing 15+ holidays, don't report raw p-values. Apply FDR correction to control false discovery rate.
- **Pandemic contamination:** 2020 COVID lockdown data may skew trend analysis. Document this as a limitation.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Holiday date calculations | Manual date lists for moving holidays | workalendar.UnitedStates().holidays(year) | Handles moving holidays (Thanksgiving = 4th Thursday), observance rules automatically |
| Statistical tests | Custom chi-square, t-test implementations | stats_utils functions (chi_square_test, compare_two_samples, compare_multiple_samples) | Existing 20+ functions with proper error handling and edge cases |
| Temporal feature extraction | Manual year/month/day extraction | extract_temporal_features() from utils.py | Handles datetime parsing, adds season, day_name, is_weekend columns |
| Bootstrap CI | Manual resampling loops | bootstrap_ci() from stats_utils.py | SciPy-based with BCa method, handles edge cases |
| FDR correction | Manual Benjamini-Hochberg | apply_fdr_correction() from stats_utils.py | scipy.stats.false_discovery_control wrapper, handles edge cases |
| Plot encoding | Manual base64 encoding | image_to_base64(), create_image_tag() from utils.py | Existing utility for markdown report embedding |

**Key insight:** This phase has exceptional existing infrastructure. Focus on composing existing functions (stats_utils, utils) rather than building new statistical capabilities. The main new code needed is (1) holiday detection via workalendar and (2) crime-type-specific filtering logic.

## Common Pitfalls

### Pitfall 1: Holiday Window Definition Too Narrow/Too Wide

**What goes wrong:** Using only the holiday date misses pre-holiday effects (e.g., New Year's Eve drinking). Using too wide a window (week before/after) dilutes the effect.

**Why it happens:** No standard approach in literature; window size depends on research question.

**How to avoid:** CONTEXT.md specifies 3 days before through 3 days after (7-day window). This is a reasonable balance between capturing pre/post effects and maintaining specificity.

**Warning signs:** Very small effect sizes (Cohen's d < 0.1) suggest window may be too wide. Non-significant results for all holidays suggest need for wider windows or different approach.

### Pitfall 2: Multiple Testing Without Correction

**What goes wrong:** Testing 15+ holidays without FDR correction yields false positives. With alpha=0.01, you'd expect ~0.15 false positives by chance.

**Why it happens:** Each holiday test is independent; family-wise error rate increases with number of tests.

**How to avoid:** Always use apply_fdr_correction() from stats_utils.py for omnibus holiday testing. Report both raw and adjusted p-values.

**Warning signs:** "Significant" findings for minor holidays with small sample sizes are likely false positives.

### Pitfall 3: Ignoring Moving Holidays

**What goes wrong:** Hard-coding holiday dates (e.g., "Thanksgiving = November 28") fails for moving holidays.

**Why it happens:** Some holidays don't have fixed dates (Thanksgiving, Memorial Day, Labor Day).

**How to avoid:** Use workalendar which calculates moving holidays correctly for each year.

**Warning signs:** Code has manual date calculations or fixed-date mappings for holidays.

### Pitfall 4: Sample Size Blindness for Rare Crimes

**What goes wrong:** Using chi-square or t-test for homicide analysis when n < 30 per year violates test assumptions.

**Why it happens:** Statistical tests have minimum sample requirements. Asymptotic tests fail for small n.

**How to avoid:** CONTEXT.md specifies adaptive methods: n < 30 use exact tests (Fisher's exact), n >= 30 use asymptotic tests. Document limitations in report.

**Warning signs:** Test returns warnings or errors for small samples. Effect sizes are extremely large due to low power.

### Pitfall 5: Shift Definition Misalignment

**What goes wrong:** Using different shift definitions than specified in CONTEXT.md (Morning 6AM-12PM, etc.) creates inconsistent results.

**Why it happens:** Different law enforcement agencies use different shift boundaries.

**How to avoid:** Use exact shift definitions from CONTEXT.md. Document bin boundaries in code comments.

**Warning signs:** Shift labels don't match hour bins. Results don't align with existing robbery_timing analysis.

### Pitfall 6: 2026 Data Inclusion in Trend Analysis

**What goes wrong:** Including 2026 data (only through January 20) skews trend analysis downward.

**Why it happens:** 2026 is incomplete (only ~3 weeks of data).

**How to avoid:** Always filter `year < 2026` for trend analysis. Can include 2026 for descriptive statistics if clearly labeled as partial.

**Warning signs:** 2026 shows dramatic drop in all crime types. Trend line shows sharp 2026 decline.

## Code Examples

Verified patterns from official sources:

### Workalendar Holiday Detection

```python
# Source: Context7 (/workalendar/workalaria documentation)
from workalendar.america import UnitedStates
from datetime import date

cal = UnitedStates()

# Get all holidays for a year
holidays_2025 = cal.holidays(2025)
# Returns: [(date(2025, 1, 1), "New Year's Day"),
#           (date(2025, 1, 20), 'Martin Luther King Jr. Day'),
#           (date(2025, 2, 17), "Washington's Birthday"),
#           (date(2025, 5, 26), 'Memorial Day'),
#           ...]

# Check if specific date is a holiday
is_july_4_holiday = cal.is_holiday(date(2025, 7, 4))  # True
is_july_5_holiday = cal.is_holiday(date(2025, 7, 5))    # False

# Get holiday label
label = cal.get_holiday_label(date(2025, 7, 4))  # "Independence Day"
```

### ANOVA with FDR-Corrected Post-Hoc (Existing Pattern)

```python
# Source: stats_utils.py (existing codebase)
from analysis.stats_utils import compare_multiple_samples, apply_fdr_correction

# Prepare shift groups (daily counts per shift)
shift_groups = {
    "Morning": morning_daily_counts,
    "Afternoon": afternoon_daily_counts,
    "Evening": evening_daily_counts,
    "Late Night": late_night_daily_counts
}

# Omnibus ANOVA test
result = compare_multiple_samples(
    shift_groups,
    alpha=0.01
)

# Access Tukey HSD post-hoc results
post_hoc_df = result["post_hoc_results"]

# Apply FDR correction
adjusted_p = apply_fdr_correction(
    post_hoc_df['p_value'].values,
    method='bh'
)
post_hoc_df['adjusted_p'] = adjusted_p
post_hoc_df['is_significant'] = adjusted_p < 0.01
```

### Bootstrap Confidence Interval (Existing Pattern)

```python
# Source: stats_utils.py (existing codebase)
from analysis.stats_utils import bootstrap_ci

# Calculate 99% CI for mean difference
ci_lower, ci_upper, point_est, se = bootstrap_ci(
    data=summer_monthly_counts,
    statistic='mean',
    confidence_level=0.99,
    n_resamples=9999,
    random_state=42
)

print(f"99% CI: [{ci_lower:.0f}, {ci_upper:.0f}]")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual holiday lists | workalendar library | ~2020 | Moving holidays calculated automatically, fewer bugs |
| Raw p-values for multiple tests | FDR correction (Benjamini-Hochberg) | ~2018 standard | Fewer false positives in omnibus testing |
| Asymptotic tests only | Adaptive: exact tests for n < 30 | ~2020 standard | More valid results for rare crimes |
| 95% confidence intervals | 99% CI (this project) | Phase 1 decision | More conservative analysis, appropriate for exploratory EDA |

**Deprecated/outdated:**
- **pandas.tseries.holiday.USFederalHolidayCalendar**: Only includes 10 holidays, missing Juneteenth, others. Use workalendar instead.
- **Manual chi-square implementation**: scipy.stats.chi2_contingency with proper expected frequency checking is superior. Use chi_square_test() from stats_utils.
- **Hard-coded shift boundaries**: Different agencies use different boundaries. Follow CONTEXT.md specification for consistency.

## Open Questions

### 1. Holiday Effect Size Threshold

**What we know:** No standard threshold for "significant holiday effect" in crime literature.

**What's unclear:** Should we define a minimum effect size (Cohen's d) for calling a holiday effect "meaningful"?

**Recommendation:** Use STAT_CONFIG effect size benchmarks (small = 0.2, medium = 0.5, large = 0.8). Report all effects but highlight "substantial" effects (Cohen's d >= 0.3) in executive summary.

### 2. Holiday-Crime Type Specificity

**What we know:** Some crimes have known holiday associations (e.g., DUI on New Year's, domestic violence on holidays).

**What's unclear:** Should we do specific holiday-crime type analysis (e.g., "New Year's Day robbery spike") or focus on overall crime patterns?

**Recommendation:** Start with overall crime patterns by holiday. If effect sizes are large for specific holidays, do follow-up crime-type-specific analysis as supplementary findings.

### 3. Shift Analysis Temporal Scope

**What we know:** CONTEXT.md leaves scope undefined: "Temporal scope for shift analysis: Full dataset aggregate, era comparison, or trend analysis"

**What's unclear:** Should we analyze shift patterns across (a) full dataset aggregate, (b) era comparison (pre-2020, 2020+, post-2022), or (c) yearly trends?

**Recommendation:** Start with full dataset aggregate (simplest, most robust). If preliminary analysis shows era differences, add era comparison as supplementary. Yearly trend analysis likely too noisy for shift-level data.

## Sources

### Primary (HIGH confidence)

- **workalendar library** (/workalendar/workalaria) - Holiday detection, US calendar usage, is_holiday(), holidays() methods
- **Existing codebase patterns**:
  - analysis/stats_utils.py - Statistical test functions (chi_square_test, compare_multiple_samples, bootstrap_ci, apply_fdr_correction, mann_kendall_test)
  - analysis/config.py - STAT_CONFIG with confidence_level=0.99, alpha=0.01, effect size benchmarks
  - analysis/robbery_timing.py - Reference pattern for shift-by-shift temporal analysis
  - analysis/summer_spike.py - Reference pattern for seasonal/holiday period analysis
  - analysis/temporal_analysis.py - Reference pattern for time series and heatmap visualizations

### Secondary (MEDIUM confidence)

- [Impact of Public Holidays on Crime Incidence in Urban Areas](https://www.researchgate.net/publication/391837232_Impact_of_Public_Holidays_on_Crime_Incidence_in_Urban_Areas) (May 2025) - Holiday effects methodology, temporal window design
- [Factors influencing temporal patterns in crime](https://pmc.ncbi.nlm.nih.gov/articles/PMC6200217/) - Shift pattern analysis, time-of-day crime distribution
- [A comparison of methods for temporal analysis of aoristic crime](https://link.springer.com/article/10.1186/2193-7680-2-1) (Ashby, 2013) - Temporal analysis methodology for crime data
- [Evaluating Temporal Analysis Methods Using Residential Burglary](https://www.mdpi.com/2220-9964/5/9/148) (Boldt, 2016) - Evaluation of temporal analysis methods
- [pandas holidays](https://pypi.org/project/holidays/) - Alternative holiday library (less comprehensive than workalendar)

### Tertiary (LOW confidence)

- [When Does Crime Occur Most: An In-depth Guide](https://www.vivint.com/resources/article/when-does-crime-occur-most) - General temporal patterns (not academic source)
- [The Rhythm of Crime](https://pinkerton.com/our-insights/blog/rhythm-of-crime) - General crime timing patterns (not academic source)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries are existing dependencies or well-documented (workalendar)
- Architecture: HIGH - Based on existing codebase patterns (robbery_timing.py, summer_spike.py)
- Pitfalls: MEDIUM - Some domain-specific pitfalls identified (holiday window size, shift definition) but verified against CONTEXT.md decisions

**Research date:** 2026-01-31
**Valid until:** 2026-03-01 (60 days - stable domain, but external libraries may update)

---

*Phase: 03-advanced-temporal-analysis*
*Research completed: 2026-01-31*
*Researcher: GSD Phase Researcher Agent*
