# Phase 2: Core Analysis - Research

**Researched:** 2026-01-27  
**Domain:** Crime Data Statistical Analysis (Temporal, Geographic, Offense Patterns)  
**Confidence:** HIGH

## Summary

This research document provides the technical foundation for conducting comprehensive statistical analysis of Philadelphia crime incidents (2006-2026). The analysis covers three primary domains: temporal patterns (20-year trends, seasonality, day/hour cycles), geographic patterns (hotspots, spatial autocorrelation, district profiles), and offense patterns (UCR distribution, severity analysis, cross-factor interactions).

**Primary recommendation:** Use the PySAL ecosystem (`esda`, `libpysal`) for spatial statistics, `statsmodels` for temporal decomposition and statistical testing, and `seaborn`/`matplotlib` for publication-quality visualizations. Implement Bonferroni correction via `statsmodels.stats.multitest.multipletests` for all multiple comparisons.

---

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pandas` | >=2.2 | Data manipulation, time series handling | Industry standard; native datetime support |
| `geopandas` | >=0.14 | Spatial data operations, GeoDataFrames | Standard for Python GIS; integrates with pandas |
| `statsmodels` | >=0.14 | Statistical tests, time series decomposition (STL), multiple comparison corrections | Academic standard; implements STL, multipletests |
| `scipy` | >=1.12 | Statistical functions, KDE, hypothesis tests | Foundation for scientific computing |
| `esda` | >=2.8 | Spatial autocorrelation (Moran's I), spatial statistics | PySAL ecosystem; peer-reviewed implementations |
| `libpysal` | >=4.14 | Spatial weights (Queen contiguity), spatial data structures | Required by esda for spatial weights |
| `seaborn` | >=0.13 | Publication-quality statistical visualizations | Built on matplotlib; excellent statistical plots |
| `matplotlib` | >=3.8 | Low-level plotting, figure customization | Publication output control |
| `numpy` | >=1.26 | Numerical operations, array handling | Foundation library |

### Supporting Libraries

| Library | Purpose | When to Use |
|---------|---------|-------------|
| `scipy.stats.gaussian_kde` | Kernel density estimation for geographic heatmaps | For custom KDE calculations beyond seaborn |
| `statsmodels.tsa.seasonal.STL` | Seasonal-trend decomposition using LOESS | For temporal analysis; handles irregular patterns |
| `statsmodels.stats.multitest.multipletests` | Bonferroni and other multiple comparison corrections | Required for all hypothesis testing with >5 comparisons |
| `libpysal.weights.Queen` | Queen contiguity spatial weights for Moran's I | For district-level spatial autocorrelation |

### Installation

```bash
pip install pandas>=2.2 geopandas>=0.14 statsmodels>=0.14 scipy seaborn matplotlib numpy
pip install esda libpysal  # PySAL ecosystem for spatial statistics
```

---

## Architecture Patterns

### Recommended Notebook Structure

```
notebooks/
├── 02_exploratory_analysis.ipynb      # Univariate distributions; hypothesis generation
├── 03_temporal_analysis.ipynb         # Trends, seasonality, hour/day patterns
├── 04_geographic_analysis.ipynb       # Hotspots, districts, KDE, spatial autocorrelation
├── 05_offense_breakdown.ipynb         # UCR distribution, severity, offense trends
├── 06_disparity_analysis.ipynb        # Cross-district comparison, profiles
└── 07_cross_factor_analysis.ipynb     # Interactions, correlations, comprehensive tests
```

### Pattern 1: Temporal Analysis Pipeline

**What:** Standard workflow for analyzing crime trends over time  
**When to use:** All temporal requirements (TEMP-01 through TEMP-07)

```python
# Source: statsmodels documentation + pandas best practices
import pandas as pd
from statsmodels.tsa.seasonal import STL
import matplotlib.pyplot as plt

# 1. Aggregate to time series
daily_counts = df.set_index('dispatch_date_time').resample('D').size()
monthly_counts = daily_counts.resample('ME').sum()

# 2. Handle missing dates (fill gaps with 0)
full_date_range = pd.date_range(
    start=monthly_counts.index.min(),
    end=monthly_counts.index.max(),
    freq='ME'
)
monthly_counts = monthly_counts.reindex(full_date_range, fill_value=0)

# 3. STL decomposition for seasonality
stl = STL(monthly_counts, period=12, robust=True)  # 12 months
result = stl.fit()

# 4. Extract components
trend = result.trend
seasonal = result.seasonal
residual = result.resid

# 5. Calculate seasonal factors (seasonality magnitude)
seasonal_factors = seasonal.groupby(seasonal.index.month).mean()
```

### Pattern 2: Spatial Autocorrelation Analysis

**What:** Formal testing of geographic clustering using Moran's I  
**When to use:** Geographic requirements (GEO-04, cross-factor spatial tests)

```python
# Source: PySAL esda documentation
import geopandas as gpd
from libpysal.weights import Queen
from esda import Moran
import numpy as np

# 1. Create district-level aggregation
district_stats = df.groupby('dc_dist').agg({
    'cartodb_id': 'count',
    'lat': 'mean',
    'lng': 'mean'
}).rename(columns={'cartodb_id': 'crime_count'})

# 2. Create GeoDataFrame with district polygons
# (Requires Philadelphia police district boundaries shapefile)
districts_gdf = gpd.read_file('data/philly_police_districts.shp')
districts_gdf = districts_gdf.merge(
    district_stats,
    left_on='DISTRICT',
    right_on='dc_dist',
    how='left'
)

# 3. Create spatial weights matrix (Queen contiguity)
# Districts are neighbors if they share a boundary
w = Queen.from_dataframe(districts_gdf)
w.transform = 'r'  # Row-standardize weights

# 4. Calculate Moran's I
moran = Moran(districts_gdf['crime_count'], w, permutations=999)

# 5. Report results with confidence
print(f"Moran's I: {moran.I:.3f}")
print(f"Expected I (random): {moran.EI:.3f}")
print(f"Z-score: {moran.z_norm:.3f}")
print(f"P-value (norm): {moran.p_norm:.4f}")
print(f"P-value (simulation): {moran.p_sim:.4f}")
```

### Pattern 3: Kernel Density Estimation (KDE) Heatmaps

**What:** Non-parametric density estimation for geographic hotspots  
**When to use:** Geographic visualization (GEO-02, DASH-03)

```python
# Source: scipy.stats.gaussian_kde documentation
from scipy.stats import gaussian_kde
import numpy as np
import matplotlib.pyplot as plt

# 1. Filter to valid coordinates
df_geo = df.dropna(subset=['lat', 'lng'])

# 2. Sample for performance (KDE is O(n²))
# For 3.5M points, sample 50k or use hexbin instead
sample_size = min(50000, len(df_geo))
df_sample = df_geo.sample(n=sample_size, random_state=42)

# 3. Create KDE
# Note: Use projected coordinates (EPSG:2272) for accurate distances
# Philadelphia coordinates: lat ~39.9-40.1, lng ~-75.3 to -75.0
values = np.vstack([df_sample['lng'], df_sample['lat']])
kde = gaussian_kde(values, bw_method='scott')

# 4. Create evaluation grid
xmin, xmax = df_geo['lng'].min(), df_geo['lng'].max()
ymin, ymax = df_geo['lat'].min(), df_geo['lat'].max()

# Create grid (adjust resolution based on performance needs)
grid_size = 200
X, Y = np.mgrid[xmin:xmax:complex(0, grid_size), ymin:ymax:complex(0, grid_size)]
positions = np.vstack([X.ravel(), Y.ravel()])

# 5. Evaluate KDE
Z = np.reshape(kde(positions).T, X.shape)

# 6. Plot
fig, ax = plt.subplots(figsize=(12, 10))
contour = ax.contourf(X, Y, Z, levels=20, cmap='hot')
ax.scatter(df_sample['lng'], df_sample['lat'], c='white', s=1, alpha=0.1)
plt.colorbar(contour, label='Density')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Crime Density Heatmap (KDE)')
```

### Pattern 4: Multiple Comparison Correction

**What:** Bonferroni correction for family-wise error rate control  
**When to use:** All hypothesis testing with >5 comparisons (per STAT-01)

```python
# Source: statsmodels.stats.multitest documentation
from statsmodels.stats.multitest import multipletests
import numpy as np

# Example: Testing if each district's crime rate differs from city mean
# This creates 22 tests (one per district)
districts = df['dc_dist'].unique()
p_values = []

for district in districts:
    district_crimes = df[df['dc_dist'] == district]['crime_count']
    other_crimes = df[df['dc_dist'] != district]['crime_count']
    
    # Perform t-test
    from scipy import stats
    _, pval = stats.ttest_ind(district_crimes, other_crimes)
    p_values.append(pval)

p_values = np.array(p_values)

# Apply Bonferroni correction
reject, pvals_corrected, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method='bonferroni'
)

# Results: reject[i] is True if district i significantly differs
# after Bonferroni correction
results = pd.DataFrame({
    'district': districts,
    'p_value_raw': p_values,
    'p_value_corrected': pvals_corrected,
    'significant': reject
})
```

### Pattern 5: Publication-Quality Figure Generation

**What:** Standardized approach for creating report-ready visualizations  
**When to use:** All figure generation (DASH-02, REPORT-05)

```python
# Source: matplotlib + seaborn best practices for academic figures
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# 1. Configure for publication quality
rcParams.update({
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (10, 6),  # Or (12, 8) for full-width
})

# 2. Use colorblind-friendly palettes
# Sequential: viridis, cividis, plasma
# Diverging: coolwarm, RdBu_r
# Categorical: tab10, Set2 (colorblind-friendly)
sns.set_palette('viridis')

# 3. Create figure with proper labeling
def save_publication_figure(fig, filename, output_dir='output/figures'):
    """Save figure in multiple formats for publication."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # PNG for web/preview
    fig.savefig(
        f'{output_dir}/{filename}.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )
    
    # PDF for publication (vector graphics)
    fig.savefig(
        f'{output_dir}/{filename}.pdf',
        bbox_inches='tight',
        facecolor='white'
    )
    
    # SVG for web/interactive
    fig.savefig(
        f'{output_dir}/{filename}.svg',
        bbox_inches='tight',
        facecolor='white'
    )

# 4. Example: Time series with confidence intervals
fig, ax = plt.subplots(figsize=(12, 6))

# Plot trend line
ax.plot(monthly_counts.index, monthly_counts.values, 
        color='steelblue', linewidth=1.5, label='Monthly Count')

# Add 95% confidence interval (if calculated)
# ax.fill_between(dates, lower_ci, upper_ci, alpha=0.3, color='steelblue')

# Styling
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Number of Incidents', fontweight='bold')
ax.set_title('Philadelphia Crime Incidents: 20-Year Trend (2006-2026)', 
             fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='upper right')

# Remove top and right spines for cleaner look
sns.despine()

plt.tight_layout()
save_publication_figure(fig, 'temporal_trend_20yr')
```

### Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | What to Do Instead |
|--------------|--------------|-------------------|
| **Using default matplotlib colors** | Not colorblind-friendly; poor contrast | Use `viridis`, `cividis`, or `tab10` palettes |
| **No multiple comparison correction** | Inflated Type I error with many tests | Always use `multipletests(method='bonferroni')` for >5 tests |
| **KDE on raw lat/lon** | Distorts distances (degrees != meters) | Project to EPSG:2272 (PA South State Plane) first |
| **Ignoring missing dates in time series** | Creates artificial gaps in analysis | Use `reindex()` with `fill_value=0` for complete series |
| **Point estimates without CIs** | Overstates precision; not defensible | Always report 95% CI with point estimates |
| **Aggregating before filtering** | Includes invalid/outlier data | Filter data quality issues before aggregation |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Seasonal decomposition** | Custom moving averages | `statsmodels.tsa.seasonal.STL` | Handles edge effects, robust to outliers, statistically sound |
| **Spatial autocorrelation** | Custom neighbor calculations | `esda.Moran` + `libpysal.weights.Queen` | Peer-reviewed implementation, proper significance testing |
| **Multiple comparison correction** | Manual Bonferroni | `statsmodels.stats.multitest.multipletests` | Handles various methods, returns corrected p-values |
| **KDE bandwidth selection** | Fixed bandwidth | `scipy.stats.gaussian_kde` with Scott/Silverman rules | Data-adaptive, theoretically justified |
| **Statistical testing** | Manual t-test loops | `scipy.stats` functions | Proper handling of edge cases, validated implementations |
| **Confidence intervals** | Manual z-score calculations | `statsmodels.stats.proportion.proportion_confint` | Handles small samples, various methods |
| **Geographic projections** | Manual coordinate math | `geopandas.GeoDataFrame.to_crs()` | Handles datum transformations correctly |

**Key insight:** Crime data analysis has well-established statistical methods. Custom implementations risk methodological errors that undermine peer review defensibility. The PySAL ecosystem (`esda`, `libpysal`) is specifically designed for spatial crime analysis and is the academic standard.

---

## Common Pitfalls

### Pitfall 1: Temporal Aggregation Bias

**What goes wrong:** Aggregating to annual totals masks important seasonal patterns; using incomplete recent months creates artificial downward trends.

**Why it happens:** Raw data has reporting lag (last 30 days excluded per project decisions); different crime types have different seasonal patterns that average out.

**How to avoid:** 
- Always exclude the last 30 days (already decided in Phase 1)
- Analyze both monthly and annual granularity
- Use STL decomposition to separate trend from seasonality
- Report seasonality magnitude separately from trend

**Warning signs:** Sudden drop in recent months; flat annual trends despite known seasonal variation.

### Pitfall 2: Spatial Autocorrelation Misinterpretation

**What goes wrong:** Interpreting Moran's I as "crime is clustered" without considering that population is also clustered; failing to account for spatial autocorrelation in subsequent analyses.

**Why it happens:** Crime clusters where people live; high Moran's I may reflect population distribution, not crime-specific patterns.

**How to avoid:**
- Calculate Moran's I on crime *rates* (per 100k population), not raw counts
- Report both count-based and rate-based spatial autocorrelation
- Use population as a control variable in spatial regression (if pursued)
- Document that spatial autocorrelation tests assume stationarity

**Warning signs:** Moran's I near 1.0 with no adjustment for population; interpreting clustering without comparing to population density.

### Pitfall 3: Multiple Comparisons Inflation

**What goes wrong:** Conducting 50+ statistical tests (district comparisons, offense type trends, temporal patterns) and reporting significant findings without correction.

**Why it happens:** Natural exploratory analysis leads to many tests; uncorrected p-values overstate evidence.

**How to avoid:**
- Pre-register primary hypotheses (STAT-01 requirement)
- Use `multipletests(method='bonferroni')` for all exploratory tests
- Report both raw and corrected p-values
- Distinguish primary (pre-registered) from exploratory (corrected) findings

**Warning signs:** Many "significant" findings at p<0.05; no mention of multiple comparison correction in methodology.

### Pitfall 4: MAUP (Modifiable Areal Unit Problem)

**What goes wrong:** Crime patterns appear different when aggregated to districts vs. neighborhoods vs. census tracts; conclusions depend on arbitrary geographic boundaries.

**Why it happens:** District boundaries don't align with actual crime hotspots; aggregation masks within-district variation.

**How to avoid:**
- Analyze at multiple geographic scales (district + neighborhood)
- Use point-level KDE in addition to areal aggregation
- Report sensitivity: "Hotspot locations stable across district and neighborhood aggregations"
- Document that district-level analysis is subject to MAUP

**Warning signs:** Dramatically different conclusions at different geographic scales; no discussion of geographic sensitivity.

### Pitfall 5: Reporting Lag Contamination

**What goes wrong:** Recent data shows artificially low crime counts due to reporting delays; creates false "improvement" trends.

**Why it happens:** Crimes are reported days/weeks after occurrence; recent months are systematically incomplete.

**How to avoid:**
- Exclude last 30 days (already decided)
- Document exclusion in methodology
- Perform sensitivity analysis: compare trends with/without recent months
- Report lag distribution by crime type

**Warning signs:** Sharp drop in last 1-2 months; no mention of reporting lag handling.

### Pitfall 6: Ecological Fallacy

**What goes wrong:** Making individual-level inferences from district-level patterns (e.g., "District X has high violent crime, therefore residents of District X are more likely to be violent").

**Why it happens:** Natural tendency to generalize from aggregate data; politically charged implications.

**How to avoid:**
- Explicitly document ecological fallacy risk (DISP-02 requirement)
- Use cautious language: "District X has higher reported crime rates" not "District X is more dangerous"
- Note that district patterns reflect both victimization and reporting/enforcement intensity
- Avoid stigmatizing language in all reporting

**Warning signs:** Individual-level language for aggregate findings; no limitations section discussing ecological inference.

---

## Code Examples

### Example 1: Complete Temporal Analysis Workflow

```python
# Source: Adapted from statsmodels STL documentation + pandas best practices
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import STL
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned data
df = pd.read_parquet('data/processed/crime_incidents_cleaned.parquet')

# Ensure datetime
df['dispatch_date_time'] = pd.to_datetime(df['dispatch_date_time'])

# Exclude last 30 days (reporting lag)
cutoff_date = df['dispatch_date_time'].max() - pd.Timedelta(days=30)
df_analysis = df[df['dispatch_date_time'] <= cutoff_date].copy()

# Create monthly time series
monthly = df_analysis.set_index('dispatch_date_time').resample('ME').size()
monthly.name = 'crime_count'

# Fill any missing months with 0 (indicates no crimes reported)
full_range = pd.date_range(start=monthly.index.min(), 
                           end=monthly.index.max(), 
                           freq='ME')
monthly = monthly.reindex(full_range, fill_value=0)

# STL decomposition
stl = STL(monthly, period=12, robust=True)
result = stl.fit()

# Calculate trend statistics
trend_slope = stats.linregress(np.arange(len(result.trend)), 
                               result.trend).slope
annual_change = trend_slope * 12  # Convert monthly to annual change

# Calculate seasonal factors
seasonal_by_month = result.seasonal.groupby(result.seasonal.index.month).mean()
summer_peak = seasonal_by_month[[6, 7, 8]].mean()  # Jun-Aug
winter_low = seasonal_by_month[[12, 1, 2]].mean()   # Dec-Feb
seasonality_magnitude = (summer_peak - winter_low) / monthly.mean() * 100

# Visualization
fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

# Original
axes[0].plot(monthly.index, monthly.values, color='gray', alpha=0.7)
axes[0].set_ylabel('Count')
axes[0].set_title('Original Time Series')
axes[0].grid(True, alpha=0.3)

# Trend
axes[1].plot(result.trend.index, result.trend.values, color='steelblue', linewidth=2)
axes[1].set_ylabel('Count')
axes[1].set_title(f'Trend Component (Annual change: {annual_change:+.1f} incidents/year)')
axes[1].grid(True, alpha=0.3)

# Seasonal
axes[2].plot(result.seasonal.index, result.seasonal.values, color='green')
axes[2].set_ylabel('Count')
axes[2].set_title(f'Seasonal Component (Summer vs Winter: {seasonality_magnitude:+.1f}%)')
axes[2].grid(True, alpha=0.3)

# Residual
axes[3].plot(result.resid.index, result.resid.values, color='red', alpha=0.7)
axes[3].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
axes[3].set_ylabel('Count')
axes[3].set_xlabel('Year')
axes[3].set_title('Residual Component')
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/figures/stl_decomposition.png', dpi=300, bbox_inches='tight')
```

### Example 2: Hour-of-Day and Day-of-Week Analysis

```python
# Source: pandas + seaborn documentation
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Extract time components
df_analysis['hour'] = df_analysis['dispatch_date_time'].dt.hour
df_analysis['day_of_week'] = df_analysis['dispatch_date_time'].dt.dayofweek  # 0=Monday
df_analysis['day_name'] = df_analysis['dispatch_date_time'].dt.day_name()

# Create hour × day heatmap
hourly_daily = df_analysis.groupby(['day_of_week', 'hour']).size().unstack()

# Reorder days to start with Monday
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hourly_daily.index = day_order

# Visualization
fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(hourly_daily, cmap='YlOrRd', annot=False, fmt='g', 
            cbar_kws={'label': 'Number of Incidents'}, ax=ax)
ax.set_xlabel('Hour of Day', fontweight='bold')
ax.set_ylabel('Day of Week', fontweight='bold')
ax.set_title('Crime Incidents by Hour and Day of Week', fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('output/figures/hour_day_heatmap.png', dpi=300, bbox_inches='tight')

# Calculate weekend vs weekday
weekend_days = ['Saturday', 'Sunday']
df_analysis['is_weekend'] = df_analysis['day_name'].isin(weekend_days)

weekend_avg = df_analysis[df_analysis['is_weekend']].groupby('hour').size().mean()
weekday_avg = df_analysis[~df_analysis['is_weekend']].groupby('hour').size().mean()
weekend_effect = (weekend_avg - weekday_avg) / weekday_avg * 100

print(f"Weekend effect: {weekend_effect:+.1f}% vs weekdays")
```

### Example 3: District Profile Generation

```python
# Source: pandas aggregation patterns
import pandas as pd
import numpy as np

def generate_district_profile(df, district_id):
    """Generate comprehensive profile for a single district."""
    
    district_data = df[df['dc_dist'] == district_id]
    
    # Basic metrics
    total_crimes = len(district_data)
    date_range = district_data['dispatch_date_time'].agg(['min', 'max'])
    years_span = (date_range['max'] - date_range['min']).days / 365.25
    annual_average = total_crimes / years_span
    
    # Top offenses
    top_offenses = (district_data['text_general_code']
                   .value_counts()
                   .head(5)
                   .to_dict())
    
    # Temporal patterns
    monthly_pattern = (district_data
                      .set_index('dispatch_date_time')
                      .resample('ME')
                      .size())
    
    # Trend (simple linear regression on monthly counts)
    from scipy import stats
    x = np.arange(len(monthly_pattern))
    slope, _, _, p_value, _ = stats.linregress(x, monthly_pattern.values)
    
    trend_direction = 'increasing' if slope > 0 else 'decreasing'
    annual_change_pct = (slope * 12) / monthly_pattern.mean() * 100
    
    # Seasonality (coefficient of variation by month)
    monthly_pattern.index = monthly_pattern.index.month
    seasonal_cv = monthly_pattern.groupby(level=0).mean().std() / monthly_pattern.mean()
    
    return {
        'district_id': district_id,
        'total_crimes': total_crimes,
        'annual_average': annual_average,
        'top_offenses': top_offenses,
        'trend_direction': trend_direction,
        'annual_change_pct': annual_change_pct,
        'trend_significant': p_value < 0.05,
        'seasonal_variability': seasonal_cv,
        'geocoding_coverage': district_data['lat'].notna().mean() * 100
    }

# Generate profiles for all districts
districts = df_analysis['dc_dist'].unique()
profiles = [generate_district_profile(df_analysis, d) for d in districts]
profiles_df = pd.DataFrame(profiles)
```

### Example 4: Cross-Factor Analysis (Chi-Square)

```python
# Source: scipy.stats documentation
from scipy.stats import chi2_contingency
import pandas as pd

# Test: Is offense type distribution independent of district?
# Create contingency table
contingency = pd.crosstab(
    df_analysis['dc_dist'],
    df_analysis['ucr_general']
)

# Chi-square test
chi2, p_value, dof, expected = chi2_contingency(contingency)

# Effect size (Cramer's V)
n = contingency.sum().sum()
cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))

print(f"Chi-square: {chi2:.2f}")
print(f"p-value: {p_value:.2e}")
print(f"Cramer's V (effect size): {cramers_v:.3f}")
print(f"Degrees of freedom: {dof}")

# Interpretation
if p_value < 0.05:
    print("Result: Offense distribution varies significantly by district")
else:
    print("Result: Offense distribution is similar across districts")

# Standardized residuals for identifying specific associations
residuals = (contingency - expected) / np.sqrt(expected)
# Large positive residuals indicate district-offense combinations 
# that occur more than expected
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Classical decomposition (moving averages) | STL (LOESS-based) | 1990s | Better handles outliers, robust to anomalies |
| Raw p-values for multiple tests | Bonferroni/FDR correction | Standard practice | Controls family-wise error rate |
| Simple choropleth maps | KDE heatmaps + spatial statistics | 2010s | Reveals point-level patterns, formal clustering tests |
| Single geographic scale | Multi-scale sensitivity analysis | Current best practice | Addresses MAUP concerns |
| Point estimates only | Estimates + 95% CIs | Current standard | Proper uncertainty quantification |

**Deprecated/outdated:**
- **Classical decomposition:** Use STL instead; handles outliers better
- **Uncorrected multiple comparisons:** Always apply Bonferroni or FDR correction
- **Raw count comparisons:** Normalize by population for valid comparisons
- **Fixed KDE bandwidth:** Use adaptive (Scott/Silverman) methods

---

## Open Questions

### 1. Philadelphia Police District Boundaries
- **What we know:** Need shapefile for district-level spatial analysis
- **What's unclear:** Whether boundaries changed 2006-2026; which version to use
- **Recommendation:** Use most recent boundaries; document any changes; sensitivity test if boundaries changed

### 2. Population Data for Rate Calculations
- **What we know:** GEO-03 requires per-capita rates
- **What's unclear:** Which population data source to use (Census? PPD estimates?); year to use for 20-year span
- **Recommendation:** Use 2020 Census as baseline; document that rates assume stable population; note limitation in report

### 3. UCR Code Mapping
- **What we know:** `ucr_general` column contains codes
- **What's unclear:** Exact mapping to FBI UCR categories; whether codes changed over time
- **Recommendation:** Document observed codes in data; create mapping based on observed values; validate against known UCR hierarchy

### 4. Confidence Interval Methods
- **What we know:** STAT-04 requires 95% CIs for all estimates
- **What's unclear:** Which CI method for proportions (Wald, Wilson, Clopper-Pearson?); for rates
- **Recommendation:** Use `statsmodels.stats.proportion.proportion_confint` with Wilson method for proportions; normal approximation for large counts

---

## Sources

### Primary (HIGH confidence)
- PySAL `esda` documentation: https://pysal.org/esda/generated/esda.Moran.html - Moran's I implementation
- PySAL `libpysal` documentation: https://pysal.org/libpysal/generated/libpysal.weights.Queen.html - Spatial weights
- Statsmodels STL documentation: https://statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html - Temporal decomposition
- Statsmodels multipletests: https://statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html - Multiple comparisons
- SciPy KDE documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html - Kernel density
- Seaborn documentation: https://seaborn.pydata.org/generated/seaborn.kdeplot.html - Visualization
- GeoPandas documentation: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.sjoin.html - Spatial operations

### Secondary (MEDIUM confidence)
- Crime analysis best practices literature (Chainey & Ratcliffe, 2005; Eck et al.)
- Philadelphia crime patterns from prior research (summertime peaks, weekday variation)

### Tertiary (LOW confidence)
- General data visualization guidelines (Tufte, Few)
- Academic reporting standards (APA, ASA)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified with official documentation
- Architecture patterns: HIGH - Based on documented API usage
- Pitfalls: MEDIUM-HIGH - Based on established crime analysis literature
- Implementation details: HIGH - Code examples verified against documentation

**Research date:** 2026-01-27  
**Valid until:** 2026-04-27 (90 days for stable libraries)

**Key dependencies to monitor:**
- PySAL ecosystem (esda, libpysal) - Active development
- statsmodels - Stable, well-maintained
- geopandas - Active development, may have API changes
