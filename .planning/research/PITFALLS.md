# Pitfalls Research

**Domain:** Crime Analysis EDA Projects (Correlation Analysis & Interactive Dashboards)
**Researched:** 2025-01-30
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Spurious Time Series Correlations

**What goes wrong:**
Finding statistically significant correlations between crime and external factors (temperature, economic indicators) that are artifacts of shared long-term trends rather than meaningful relationships. For example, both crime and ice cream sales may rise in summer not because they're related, but because both are seasonal.

**Why it happens:**
Time series data with shared drift (both increasing or decreasing over 20 years) produce high correlation coefficients even when no causal relationship exists. When correlating 20-year crime trends with 20-year economic data, the shared trend dominates.

**Consequences:**
- Publication of false findings that cannot be replicated
- Misallocation of resources based on invalid relationships
- Loss of research credibility when correlations fail to hold

**Prevention:**
- Always detrend time series before correlation analysis (first-differencing or residualization)
- Use cross-correlation with lag analysis to test temporal precedence
- Apply Granger causality tests as a minimum bar (not proof, but better than raw correlation)
- Split data: discover patterns in one time period, validate in another

**Warning signs:**
- Correlation coefficients > 0.7 across long time spans are suspicious
- No theoretical mechanism explains the relationship
- Correlation appears only when using full 20-year span, disappears in sub-periods
- Multiple tested correlations showing similar strength (likely all spurious)

**Phase to address:**
External Data Integration phase — before reporting any correlation results

---

### Pitfall 2: Modifiable Areal Unit Problem (MAUP)

**What goes wrong:**
Crime patterns and hotspot locations change dramatically depending on the spatial aggregation level. A correlation that appears significant at the census tract level may vanish at the police district level, and hotspots identified at one scale may not exist at another.

**Why it happens:**
Crime data can be aggregated to many spatial units: police districts, census tracts, zip codes, neighborhoods, street segments. The choice of unit is arbitrary (modifiable) but significantly affects statistical results and spatial patterns.

**Consequences:**
- Hotspot maps that are artifacts of chosen boundaries, not real patterns
- Policy recommendations based on areas that appear high-crime only due to aggregation choice
- Published findings that cannot be replicated with different (equally valid) spatial units

**Prevention:**
- Always conduct multi-scale analysis: report results at multiple spatial resolutions
- Use coordinate-based point analysis where possible (avoid aggregation entirely)
- If aggregation is necessary, test robustness across at least 3 different spatial unit definitions
- Explicitly report MAUP as a limitation in any spatial analysis

**Warning signs:**
- Results change dramatically when changing spatial unit
- Hotspots align suspiciously well with arbitrary boundaries
- No justification given for choice of spatial aggregation level

**Phase to address:**
Spatial Analysis / External Data Integration phases — all spatial correlation work

---

### Pitfall 3: Missing Coordinate Selection Bias

**What goes wrong:**
Spatial analyses that filter out records with missing coordinates (~25% of this dataset) create biased results. The missing coordinates are not random — they are systematically associated with certain crime types, locations, or time periods, skewing all spatial findings.

**Why it happens:**
Analysts filter to `valid_coord=True` to enable mapping, assuming the remaining data is representative. In reality, geocoding success varies by crime type (e.g., domestic incidents often lack precise addresses), neighborhood (some areas resist precise location recording), and time period (geocoding improved over 20 years).

**Consequences:**
- Hotspot maps that underrepresent certain crime categories
- District-level comparisons that are invalid
- Any spatial statistic applied to the filtered sample is biased

**Prevention:**
- Always compare characteristics of valid vs. missing coordinate records
- Report the "missingness profile": which crimes/times/areas are underrepresented
- Use weighting if the missingness pattern is systematic and can be modeled
- Explicitly state spatial analyses apply only to geocoded subset

**Warning signs:**
- No comparison between full dataset and geocoded subset
- Crime type distribution changes significantly after coordinate filter
- Results not caveated with geocoding bias limitations

**Phase to address:**
Data Quality Audit phase — before any spatial analysis

---

### Pitfall 4: Incomplete Year Trend Artifacts

**What goes wrong:**
Including partial 2026 data (only January 1-20) in trend analysis creates dramatic artificial drops that appear as significant trends. Any annual comparison or year-over-year analysis that includes 2026 will be severely distorted.

**Why it happens:**
Analysts apply `year >= 2006` filters without excluding incomplete years. The dataset appears complete (no nulls), so the partial year problem isn't caught until visual inspection reveals anomalies.

**Consequences:**
- False conclusion that crime plummeted in 2026
- Any trend analysis ending in 2026 shows artificial decline
- Seasonal analysis distorted by 20 days of January only

**Prevention:**
- Define a function `is_complete_year(df, year)` that checks record count against expected
- Automatically flag and exclude years with < 90% expected records
- Visualize annual record counts as a first step in any temporal analysis
- Add explicit EXCLUDE_2026 constant to config

**Warning signs:**
- Sudden dramatic change in final year of time series
- Annual counts vary by more than 20% from baseline without explanation
- Month-level plot shows final year has only 1-2 months of data

**Phase to address:**
Data Quality Audit phase — before any trend analysis

---

## Moderate Pitfalls

### Pitfall 5: Data Dredging Without Multiple Testing Correction

**What goes wrong:**
Testing dozens of correlations (crime types × weather variables × economic indicators × districts) without correction guarantees false discoveries. With 100 tests at p < 0.05, expect 5 significant results by chance alone.

**Why it happens:**
Exploratory analysis encourages testing many hypotheses. Without pre-registration or correction, analysts report only significant findings, creating an illusion of discovery.

**Consequences:**
- Published findings fail to replicate
- Resources wasted investigating spurious relationships
- Research credibility damaged

**Prevention:**
- Track ALL tests performed, not just significant ones
- Apply Benjamini-Hochberg FDR correction to p-values
- Split sample: discovery (50%) and validation (50%)
- Pre-specify primary hypotheses before analysis

**Warning signs:**
- Many correlations tested, only "interesting" ones reported
- No mention of multiple testing correction
- Results presented without validation on holdout data

**Phase to address:**
Correlation Analysis phase — before extracting insights

---

### Pitfall 6: Temporal Misalignment in External Data

**What goes wrong:**
Crime data (daily) is correlated with external data aggregated at different temporal scales (monthly economic indicators, weekly weather averages) without proper alignment. This creates artificial correlations or masks real ones.

**Why it happens:**
External datasets come in different temporal granularities. Analysts resample without considering the impact on correlation strength and lag structures.

**Consequences:**
- Missed real correlations due to temporal aggregation
- False correlations from aggregation artifacts
- Incorrect lag inference (e.g., concluding weather affects crime with 2-week lag when it's actually same-day)

**Prevention:**
- Document temporal resolution of all datasets before integration
- Use the finest common temporal resolution (daily for weather)
- Test multiple lags when theory is uncertain
- Report aggregation decisions and their impact on results

**Warning signs:**
- Temporal resolution not documented in analysis
- No justification for chosen aggregation level
- Only one lag tested when theory allows multiple

**Phase to address:**
External Data Integration phase

---

### Pitfall 7: Dashboard Performance Collapse at Scale

**What goes wrong:**
Dashboard built with Streamlit or Dash works well with 100K records but becomes unusably slow with 3.5M records. Filters take minutes to respond, maps fail to render, and the tool is abandoned.

**Why it happens:**
Prototyping with samples (`df.sample(100000)`) works fine, but production uses full dataset. Neither Streamlit nor Dash handles multi-million record datasets without optimization.

**Consequences:**
- Dashboard becomes unusable despite functional features
- Interactive exploration fails, defeating the purpose
- Need to rebuild with different architecture

**Prevention:**
- For Streamlit: use `@st.cache_data` aggressively, downsample for visualization, implement pagination for data tables
- For Dash: use clientside callbacks, WebGL charts, `plotly-resampler` for large datasets
- General: pre-compute aggregations, use database indexing, implement progressive loading
- Test with full dataset early, not just samples

**Warning signs:**
- Development uses sampled data but production will use full dataset
- No caching strategy implemented
- Charts render entire dataset regardless of filter

**Phase to address:**
Dashboard Development phase — architecture decision point

---

### Pitfall 8: Cherry-Picking Time Ranges in Visualizations

**What goes wrong:**
Dashboard allows arbitrary time range selection, and users unconsciously select ranges that show dramatic patterns (e.g., "crime spike in 2020") while ignoring longer context. This exploits confirmation bias to create misleading narratives.

**Why it happens:**
Interactive filters are a feature, but default views and suggested ranges can guide users toward cherry-picked conclusions. The tool doesn't provide context about what's "normal."

**Consequences:**
- Users form incorrect conclusions about crime trends
- Stakeholders make decisions based on anomalous periods presented as representative
- Dashboard loses credibility as an objective tool

**Prevention:**
- Always show longer-term context alongside selected range
- Display statistical significance of changes
- Default to showing full time range, not zoomed-in views
- Add annotations for known events (COVID, policy changes)
- Implement "compare to same period previous year" feature

**Warning signs:**
- Default view zoomed to recent period only
- No indication whether displayed change is statistically significant
- No context about typical variation

**Phase to address:**
Dashboard Development phase — UX design

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skipping statistical tests | Faster initial results | Invalid findings, retraction risk | Never for academic publication |
| Using samples for dashboard dev | Quick iteration | Performance issues in production | Only if full dataset tested early |
| Hardcoding spatial boundaries | Immediate mapping capability | MAUP issues, non-reproducible | Only for initial exploration |
| Skipping data quality documentation | Faster to "results" | Hidden bias, unreproducible research | Never |
| Reusing same data for discovery and validation | Apparent significance | Overfitting, false discoveries | Never |

## Dashboard-Specific Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Full dataset on every interaction | Unresponsive UI | Aggressive caching, pre-aggregation, progressive loading |
| No default view | Analysis paralysis | Provide sensible starting filters with context |
| Overwhelming with too many filters | Decision fatigue | Layer filters, use "basic" vs "advanced" modes |
| Missing data not visualized | False sense of completeness | Show data completeness indicators, mark sparse periods |
| No export functionality | Results trapped in dashboard | Add CSV/image export, permalink generation |
| Mobile-unresponsive spatial plots | Useless on tablets/phones | Test responsive design, provide alternative views |

## Research Validity Pitfalls

### HARKing (Hypothesizing After Results are Known)

**What goes wrong:** Framing exploratory findings as if they were pre-registered hypotheses. Analysis discovers a pattern (e.g., "crime increases on hot days"), then writes it as if this was predicted beforehand.

**Prevention:**
- Distinguish confirmatory from exploratory analyses explicitly
- Report all tests performed, not just significant ones
- Use holdout validation for any exploratory finding
- Label analyses clearly: "Exploratory: requires validation"

### Confirmation Bias in Visualization

**What goes wrong:** Visualizations are designed to show expected patterns rather than test them. Color scales, axis ranges, and chart types are chosen to make expected relationships visually obvious.

**Prevention:**
- Pre-specify visualization approach for each hypothesis
- Use consistent, neutral color scales (e.g., RdBu diverging, not "good to bad" gradient)
- Show uncertainty intervals on all estimates
- Include null/expected comparisons

### p-Value Fixation

**What goes wrong:** Reporting only "p < 0.05" without effect sizes, confidence intervals, or practical significance. Tiny effects become "significant" with 3.5M records.

**Prevention:**
- Always report effect sizes with confidence intervals
- Discuss practical significance: "X% increase in crime per 10degF temperature rise"
- Use Bayesian methods for large datasets where p-values become overly sensitive
- Focus on "Does this matter?" not just "Is this non-zero?"

## Data Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Weather data | Using daily average temperature | Max temperature often matters more for outdoor activity |
| Economic data | Assigning annual values to all days | Recognize lag effects; quarterly data may be more appropriate |
| Policing data | Assuming arrest rate = crime rate | Arrest rates reflect enforcement priorities, not just crime |
| Geographic boundaries | Assuming stability over 20 years | District/tract boundaries change; use historical boundaries or note limitation |

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Data Quality Audit | Incomplete year artifacts, missing coordinate bias | Profile completeness by year, compare valid vs missing |
| External Data Sourcing | Temporal misalignment, incompatible spatial units | Document resolutions before integration |
| Correlation Analysis | Spurious correlations, multiple testing, data dredging | Pre-register hypotheses, FDR correction, train/test split |
| Spatial Analysis | MAUP, coordinate bias, hotspot instability | Multi-scale analysis, point-based methods, bias documentation |
| Dashboard Development | Performance collapse, cherry-picking UX, missing context | Test at scale early, provide context, sensible defaults |
| Report Generation | Overstating findings, hiding limitations, HARKing | Explicit limitations section, distinguish exploratory/confirmatory |

## "Looks Done But Isn't" Checklist

- [ ] **Correlation analysis:** Often missing multiple testing correction — verify Benjamini-Hochberg applied
- [ ] **Spatial hotspots:** Often single-scale only — verify multi-scale robustness tested
- [ ] **Trend analysis:** Often includes incomplete years — verify 2026 excluded and completeness checked
- [ ] **Dashboard filters:** Often no context for selection — verify baseline/typical values shown
- [ ] **External data:** Often temporal misalignment ignored — verify resolution documented and aligned
- [ ] **Missing data bias:** Often assumed random — verify characteristics of missing vs present data compared
- [ ] **Effect sizes:** Often only p-values reported — verify confidence intervals and practical significance included

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Spurious correlations published | HIGH | Retraction or correction paper; conduct proper analysis with detrending and validation |
| MAUP not addressed | MEDIUM | Re-run analysis at multiple scales; update with caveat; describe as "preliminary" |
| Dashboard unusable at scale | HIGH | Re-architect with caching/sampling; may require framework switch |
| Incomplete year effects | LOW | Re-run excluding 2026; document correction |
| Missing multiple testing correction | MEDIUM | Apply FDR correction; re-evaluate which findings survive |

## Sources

### Statistical Pitfalls
- [Common pitfalls in statistical analysis: The use of correlation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5079093/) — PubMed Central, 2016
- [Spurious Correlations in Time Series Data: A Note](https://www.researchgate.net/publication/306376553_Spurious_Correlations_in_Time_Series_Data_A_Note) — ResearchGate
- [An Investigation of Weather and Annual Crime Rates](https://minds.wisconsin.edu/bitstream/handle/1793/78481/Martin%20Reichhoff%20Thesis.pdf) — M. Reichhoff, 2017

### Spatial Analysis & MAUP
- [Issues in the aggregation and spatial analysis of crime](https://www.tandfonline.com/doi/full/10.1080/19475683.2012.691901) — Taylor & Francis, 2012
- [Measuring the Influence of Multiscale Geographic Space on Crime](https://www.mdpi.com/2220-9964/12/10/437) — MDPI, 2023
- [Modifiable areal unit problem](https://en.wikipedia.org/wiki/Modifiable_areal_unit_problem) — Wikipedia

### Geocoding & Missing Data Bias
- [Potential biases due to geocoding error in spatial analyses](https://www.sciencedirect.com/science/article/abs/pii/S1353829208001081) — ScienceDirect
- [Address matching bias: ignorance is not bliss](https://www.emerald.com/pijpsm/article-pdf/30/1/32/2096439/13639510710725613.pdf) — Emerald, 2007

### Dashboard Design
- [7 Most Common Dashboard Design Mistakes to Avoid](https://www.yellowfinbi.com/blog/most-common-dashboard-design-mistakes-to-avoid) — Yellowfin BI
- [Bad Dashboard Examples: 10 Common Mistakes](https://databox.com/bad-dashboard-examples) — Databox, 2025
- [Cherry-picking in data visualization](https://medium.com/@hamzamlwh/the-most-common-misleading-errors-in-data-visualization-aa30bd1c89d4) — Medium

### Performance & Scale
- [Six Tips for Improving Your Streamlit App Performance](https://discuss.streamlit.io/t/six-tips-for-improving-your-streamlit-app-performance/15232) — Streamlit Community
- [Performance | Dash for Python Documentation](https://dash.plotly.com/performance) — Plotly Dash
- [Challenges in Scaling Dashboards for Millions of Users](https://www.researchgate.net/publication/391056527_Challenges_in_Scaling_Dashboards_for_Millions_of_Users) — ResearchGate, 2025

### Data Integration
- [Integrating Data Across Misaligned Spatial Units](https://www.cambridge.org/core/journals/political-analysis/article/integrating-data-across-misaligned-spatial-units/0EB1F25861F9CAF940D6DB07333C8345) — Cambridge
- [Crime Spatiotemporal Prediction Through Urban Region](https://www.mdpi.com/2504-2289/9/12/301) — MDPI, 2025

### Visualization Ethics
- [Visualization Guardrails: Designing Interventions Against Cherry-Picking](https://dl.acm.org/doi/full/10.1145/3706598.3713385) — ACM, 2025
- [What are misleading data visualizations](https://funnel.io/blog/what-are-misleading-visualizations-and-how-do-you-avoid-them) — Funnel

---

*Pitfalls research for: Crime Analysis EDA Projects*
*Researched: 2025-01-30*
