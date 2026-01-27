# Pitfalls Research: Common Mistakes in Crime Analysis

## Research Objective
Identify and document common mistakes in crime analysis research, and protective strategies.

## Category 1: Data Quality Pitfalls

### Pitfall 1.1: Ignoring Reporting Lag
**What**: Assuming all crimes are recorded on the incident date. Reality: Crimes reported weeks/months later.

**Consequence**: 
- Recent months appear to have fewer crimes (data not yet entered)
- Year-over-year comparisons are biased if lag varies by season
- Temporal patterns distorted near data cutoff

**Detection**:
- Check dispatch_date_time vs report_received_date
- Histogram of lag distribution
- Look for truncation at data cutoff

**Mitigation**:
- Exclude most recent 1-2 months from final analysis
- Document lag exclusion window explicitly
- Report raw numbers + lag-adjusted estimates

**Example**: "Analysis includes incidents through 2025-11-30; more recent data excluded due to 4-6 week reporting lag."

---

### Pitfall 1.2: Geocoding Bias
**What**: ~5-15% of crime records have missing or invalid coordinates. These aren't randomly distributed.

**Consequence**:
- Some neighborhoods appear safer than they are (if their data is underreported)
- Geographic analysis is biased
- Hotspot maps incomplete

**Pattern**:
- Older records more likely to have missing coordinates
- Certain districts have worse data quality
- Specific crime types (quality-of-life) underreported

**Detection**:
- Count missing lat/lon by district, year, crime type
- Map "coverage" by district (% with valid coordinates)
- Compare districts

**Mitigation**:
- Document % coverage by district
- Include missingness in sensitivity analysis
- Exclude districts with <80% coverage from hotspot analysis (if severe)
- Or: weight analysis by coverage (down-weight high-missing-data districts)

**Example**: "Homicides 99% geocoded (n=8,500), but quality-of-life misdemeanors only 67% geocoded (n=120,000). Analysis weights hotspot estimates accordingly."

---

### Pitfall 1.3: Duplicate Records
**What**: Same incident recorded twice due to data entry error or multi-victim incidents coded as separate rows.

**Consequence**:
- Inflated incident counts
- Distorted trends
- Hotspot maps show false peaks

**Detection**:
- Check for identical (location, time, offense type) within 1-hour window
- Look for cartodb_id duplicates
- Query for exact coordinate duplicates

**Mitigation**:
- De-duplicate on (location, datetime, offense_type)
- Or: keep all records but document multiplicity issue
- Sensitivity analysis: results with/without de-duplication

---

### Pitfall 1.4: Missing Value Patterns (Not Just Counts)
**What**: Assuming missing values are random. They're not.

**Consequence**:
- Biased estimates if missingness correlates with geography or time
- Seasonal analysis fails if summer records more complete than winter
- District-level estimates biased if some districts have worse data entry

**Detection**:
- Missing data heatmap: district × month (is there a pattern?)
- Missing data heatmap: crime type × year
- Compare missing % across seasons, weekdays, hours

**Mitigation**:
- Document missing patterns explicitly
- Stratify analysis by data quality (separate analysis for high-quality vs poor-quality periods)
- Use multiple imputation for missing coordinates (spatial imputation based on similar records)
- Or: restrict analysis to complete cases (loses data, but unbiased)

**Example**: "Summer months (Jun-Aug) have 8% better coordinate coverage than winter. Hotspot analysis restricted to Jun-Aug to ensure consistency."

---

## Category 2: Geographic Pitfalls

### Pitfall 2.1: Confusing Reporting with Actual Crime
**What**: Crime reports reflect policing effort, not victimization. Over-policed areas show more crime.

**Consequence**:
- "High-crime neighborhoods" are often high-policing neighborhoods
- Perpetuates bias against certain areas
- Policy conclusions based on reporting bias

**Detection**:
- Compare police staffing levels to reported crime
- Look for sudden spikes coinciding with enforcement increases (not actual crime increase)
- Compare self-reported victimization (surveys) to police reports

**Mitigation**:
- Explicitly acknowledge this bias in limitations section
- Caveat: "Reported crime reflects both victimization and enforcement intensity"
- Consider alternative data sources (hospital records for assault, insurance for burglary)
- Avoid framing as "most dangerous neighborhoods"; instead "most reported crimes"
- Sensitivity analysis: how does removing high-policing districts change rankings?

**Example**: "Police presence significantly predicts reported crime (r=0.72, p<0.001). Analysis acknowledges that reported crime reflects both victimization and enforcement."

---

### Pitfall 2.2: MAUP (Modifiable Areal Unit Problem)
**What**: Results depend on how you draw geographic boundaries. Districts vs precincts vs census tracts → different conclusions.

**Consequence**:
- Hotspot map looks different if you use districts vs PSAs vs neighborhoods
- Correlations can flip when you change aggregation level
- No "true" geographic pattern; multiple valid representations

**Detection**:
- Run same analysis at multiple geographic levels
- See if hotspots stay same or shift
- Look for boundary effects (why does district line matter?)

**Mitigation**:
- Use multiple geographic levels (district + PSA + smaller areas)
- Acknowledge MAUP in limitations
- Use point-based analysis (KDE) instead of aggregate counts where possible
- Justify chosen geographic level (administrative boundaries for policy, finer for analysis)

**Example**: "Analysis uses official police districts (22 total) for consistency with Philadelphia Police Department structure. District-level results differ from census-tract-level analysis; sensitivity analysis in Appendix C documents this."

---

### Pitfall 2.3: Ignoring Spatial Autocorrelation
**What**: Crime in neighboring locations is correlated (spatial autocorrelation). Can't treat as independent observations.

**Consequence**:
- Standard errors underestimated (falsely high confidence in estimates)
- Statistical tests too liberal (claim significance when shouldn't)
- Confidence intervals too narrow

**Detection**:
- Calculate Moran's I (global spatial autocorrelation)
- Calculate LISA (Local Indicators of Spatial Association) for local clusters
- Map residuals to see if clusters exist

**Mitigation**:
- Use spatial regression models (CAR, SAR models) if testing hypotheses
- Or: report Moran's I and acknowledge spatial dependence
- Use bootstrap resampling with spatial blocks (preserves autocorrelation)
- Acknowledge in limitations: "Standard errors may underestimate uncertainty due to spatial autocorrelation"

**Example**: "Moran's I = 0.68 (p<0.001), indicating strong spatial autocorrelation. Reported confidence intervals are likely optimistic; wider confidence intervals in Appendix A account for this."

---

## Category 3: Temporal Pitfalls

### Pitfall 3.1: Simpson's Paradox in Aggregation
**What**: Trend appears one way overall, but opposite direction in subgroups.

**Consequence**:
- Conclude "crime is increasing" when actually increasing only in low-crime areas (and decreasing in high-crime)
- Wrong policy implications

**Detection**:
- Always stratify trends (by district, by crime type)
- If subgroups show opposite trends, Simpson's Paradox likely

**Mitigation**:
- Report both aggregate and stratified trends
- Explain why they differ (usually: composition change)
- Weight appropriately if aggregating

**Example**: "Overall homicides increased 5% (2006-2025). However, this masks regional shifts: South Philadelphia homicides decreased 15% while Northeast increased 30%. Compositional change (more incidents in high-rate areas) drives aggregate increase."

---

### Pitfall 3.2: Seasonal Confounding
**What**: Comparing periods without accounting for seasonal variation. Weekends vs weekdays, summer vs winter.

**Consequence**:
- Conclude policy change "worked" when it's just seasonal
- Apparent trends are just seasonal cycles
- Year-over-year comparisons biased if compared seasons differ

**Detection**:
- Plot data by month/weekday; obvious seasonal pattern?
- Use seasonal decomposition (STL) to separate trend from seasonality
- Compare same months across years, not arbitrary periods

**Mitigation**:
- Always seasonally adjust before comparing
- Compare same-season year-over-year (July 2023 vs July 2024)
- Use Poisson regression with season as control variable
- Report both raw and seasonally adjusted trends

**Example**: "July-August crimes are 15% higher than November-December (seasonal effect). Trend analysis uses seasonal adjustment (STL decomposition) to isolate year-over-year changes."

---

### Pitfall 3.3: Regression to the Mean
**What**: Extreme values (unusually high month) tend to revert to average next month. Mistaken for intervention effect.

**Consequence**:
- Policy starts after "bad month" → next month improves (natural regression) → assume policy worked

**Detection**:
- Did intervention start after extreme event? (policy after bad month → looks effective)
- Is improvement in intervention group + worsening in control group? (suggests real effect)
- Or: opposite direction in control group suggests regression to the mean

**Mitigation**:
- Use control group (crimes not targeted by intervention)
- Document timing of interventions
- Longer follow-up (2+ years, not just next month)
- Use pre/post interrupted time series (formal test for level/slope change)

---

## Category 4: Statistical Pitfalls

### Pitfall 4.1: Multiple Comparisons Problem
**What**: Testing many hypotheses; some will be "significant" by chance (p<0.05).

**Example**: Test 100 offense types for change → expect ~5 to be significant by chance alone.

**Consequence**:
- False positives (spurious findings)
- Report "significant" effects that are noise

**Detection**:
- Count # of tests performed
- Any finding with p-value near 0.05? (suspicious if many tests)
- Look for non-replicable findings (don't appear in other data)

**Mitigation**:
- **Multiple comparison correction**: Bonferroni (conservative), FDR (less conservative), or Holm's step-down
- **Pre-register hypotheses**: Planned vs exploratory analyses labeled differently
- **Focus on effect size + CIs**: Not just p-values
- Report: "After Bonferroni correction for k=100 tests, α_corrected = 0.0005"

**Example**: "Tested 85 crime types for trend significance. After Bonferroni correction (α=0.0006), only 12 showed significant trends. Exploratory findings on the remaining 73 types reported without corrected p-values."

---

### Pitfall 4.2: p-Hacking / Degrees of Freedom
**What**: Try different analyses until you find something "significant". (Was 95% significance threshold, but if you try 20 ways to analyze data, one will be "significant" by chance.)

**Consequence**:
- Report non-replicable findings
- Biased toward significant results (publication bias)

**Detection**:
- Unexpectedly many significant findings? (suspicious)
- Findings don't replicate? (suggests p-hacking)

**Mitigation**:
- **Pre-register analysis plan** before looking at data
- **Clearly label**: What was planned vs exploratory
- **Report all analyses**, not just significant ones
- **Effect size + CIs**, not just p-values

**Example**: "Primary analysis (pre-registered): Trend test for top 5 crime types. Secondary analysis (exploratory): 85 additional types tested; results reported without multiple-comparison correction."

---

### Pitfall 4.3: Ignoring Confounders
**What**: Conclude A causes B, ignoring that C causes both (confounding).

**Example**: High-arrest areas have more crime. Does more policing cause crime? No — confound is that high-crime areas get more police.

**Consequence**:
- Backwards conclusions (enforcement causes crime; actually, crime drives enforcement)
- Wrong policy implications

**Detection**:
- Does the proposed causal mechanism make sense?
- Are there obvious third variables?
- Does direction of causation match temporal order?

**Mitigation**:
- Use causal language carefully ("is associated with" not "causes")
- Identify and measure confounders
- Stratified analysis (compare within same confound level)
- Regression with confound as control variable
- Explicit limitations: "Findings are associational; causality cannot be inferred"

**Example**: "Districts with more police presence have higher reported crime (r=0.68). However, police deployment is endogenous to crime levels (confounding). Interpretation: high-crime areas receive more police, not vice versa."

---

### Pitfall 4.4: Ignoring Data Distribution (Parametric Assumptions)
**What**: Using t-tests or ANOVA on data that violate normality/homogeneity assumptions.

**Consequence**:
- p-values and CIs wrong
- False positives/negatives

**Detection**:
- Plot distribution; is it normal?
- Levene's test for homogeneity of variance
- Q-Q plots

**Mitigation**:
- Check assumptions first
- Use non-parametric alternatives (Mann-Whitney U, Kruskal-Wallis) if violated
- Or: transform data (log, sqrt) to normalize
- Report both parametric and non-parametric results if assumptions borderline

**Example**: "Crime counts are Poisson-distributed (not normal). Tested for differences using Kruskal-Wallis test (non-parametric). Both parametric and non-parametric results reported; conclusions consistent across methods."

---

## Category 5: Interpretation Pitfalls

### Pitfall 5.1: Ecological Fallacy
**What**: Conclude about individuals from aggregate data.

**Example**: "Districts with high poverty have high crime. Therefore, poor people commit more crimes." ← WRONG (ecological fallacy)

**Consequence**:
- Stigmatizes populations
- Wrong policy implications

**Mitigation**:
- Avoid individual-level conclusions from aggregate data
- Use appropriate language: "Districts with higher poverty rates report more crimes" ≠ "poor people commit more crimes"
- Acknowledge multiple interpretations (poverty, policing, opportunity structures)

---

### Pitfall 5.2: Ignoring Base Rates
**What**: Focusing on relative changes while ignoring absolute magnitude.

**Example**: "X crimes increased 50%! (from 2 per month to 3 per month)" ← Still rare; "50% increase" is misleading.

**Consequence**:
- Exaggerates importance of findings
- Public alarm unjustified

**Mitigation**:
- Always report absolute numbers AND relative changes
- Use base rate: "increased by 50%, from 2 to 3 incidents per month (0.006% of all crime)"
- Visualize: show absolute magnitude, not just percentage change

**Example**: "Simple assault increased 8% (2006-2025), from 45,000 to 48,600 annual incidents. Proportionally, this represents only 0.4 percentage point increase in total crime share."

---

## Protective Practices (Do These First!)

1. **Data Quality Audit (First Notebook)**
   - Missing values by district, year, crime type
   - Coordinate validation
   - Duplicate detection
   - Document all findings

2. **Pre-Register Hypotheses**
   - Write down planned analysis BEFORE looking at data
   - Clearly distinguish primary vs exploratory analyses

3. **Exploratory Data Analysis (Separate Notebook)**
   - Univariate distributions
   - Outliers and anomalies
   - Initial patterns (for hypothesis generation)
   - Explicitly labeled "exploratory"

4. **Stratified Analysis**
   - Always break down by subgroups (district, crime type, season)
   - Don't hide subgroup patterns in aggregate

5. **Sensitivity Analysis**
   - Include/exclude different data subsets
   - Results stable? (If change dramatically, finding is fragile)
   - Document assumptions and show impact

6. **Peer Review**
   - Have colleague review analysis and interpretation
   - Ask: "What could be wrong?" "What's missing?"
   - Document feedback and responses

7. **Explicit Limitations**
   - List all known issues
   - Acknowledge confounding, data quality, generalizability bounds
   - Propose future work to address limitations

---

## Key Insights

1. **Data quality is foundational**: Garbage in → garbage out. Invest heavily in cleaning and auditing.

2. **Reporting bias is systematic**: Crime data reflects policing, not victimization. Acknowledge always.

3. **Temporal confounds are powerful**: Seasonal variation, reporting lag, regression to mean — must account for these.

4. **Geographic analysis is tricky**: Spatial autocorrelation, MAUP, ecological fallacy — requires care.

5. **Statistics can lie if you let it**: Multiple comparisons, p-hacking, ignoring confounds — careful methodology essential.

6. **Transparency > Perfect**: Document assumptions, limitations, and methodological choices. Readers can then judge.

7. **Replication is gold standard**: If findings replicate on different data, more credible.

---

## Protective Checklist for Report

- [ ] Data quality audit documented
- [ ] Missing value patterns analyzed and reported
- [ ] Geocoding coverage by district noted
- [ ] Seasonal adjustment applied before trend claims
- [ ] Multiple geographic levels shown (not just districts)
- [ ] Spatial autocorrelation acknowledged
- [ ] Multiple comparisons correction applied (if >5 tests)
- [ ] Confounders identified and discussed
- [ ] Parametric assumptions checked
- [ ] Results stratified by subgroups (not just aggregate)
- [ ] Limitations section explicit and comprehensive
- [ ] Findings interpretable without over-claiming causation
- [ ] Base rates reported alongside percentages
- [ ] Peer review completed and feedback addressed
- [ ] Sensitivity analyses in appendix

---

*Prepared: 2026-01-27 | Evidence Level: Statistical methodology + crime analysis case studies*
