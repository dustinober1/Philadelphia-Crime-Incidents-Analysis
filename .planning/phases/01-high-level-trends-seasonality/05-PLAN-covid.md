# Phase 1 Plan: Notebook Refactoring - COVID Impact Analysis
**Wave:** 2
**Depends on:** Wave 1 (Infrastructure)
**Files modified:** `notebooks/covid_lockdown_crime_landscape.ipynb`
**Autonomous:** Yes

---

## Goal
Refactor the COVID Lockdown Crime Landscape notebook (CHIEF-03) to use external configuration, produce comparative analysis of pre/during/post COVID periods with displacement analysis, and generate academic-style reports with versioned artifacts.

---

## Tasks

### TASK-2.13: Refactor Data Loading and Configuration
**Objective:** Integrate external configuration for COVID period definitions and standardize structure.

<requirements>
- Add config loading cell: load Phase1Config, extract 'covid' parameters
- Replace hardcoded period definitions with config: lockdown_date "2020-03-01", before_years [2018,2019], during_years [2020,2021], after_start_year 2023
- Update data loading to use `analysis.utils.load_data()`
- Add parameter cell for papermill: VERSION, LOCKDOWN_DATE, BEFORE_YEARS, DURING_YEARS, AFTER_START_YEAR
- Exclude 2026 data explicitly
- Add reproducibility cell
</requirements>

<acceptance>
- Config loaded at notebook start
- COVID period boundaries come from config (not hardcoded)
- Parameter cell tagged "parameters"
- 2026 excluded programmatically
- Data loading uses shared utility
- Period definitions are clear: Before (2018-2019), During (2020-2021), After (2023-present)
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

<context>
Current notebook (from research):
- ~850 lines, fully functional
- Has lockdown annotation, displacement analysis (Residential vs Commercial burglary)
- Good reproducibility documentation already
- Gaps: no external config, missing formal limitations section, no versioning
</context>

---

### TASK-2.14: Restructure to Academic Report Format
**Objective:** Organize into Summary → Methods → Findings → Limitations format with explicit period definitions.

<requirements>
- Add "Summary" section: 1-2 paragraphs answering "How did COVID change the crime landscape?"
- Create "Methods" section: document period definitions (Before/During/After), lockdown date rationale, displacement analysis approach
- Organize existing analysis under "Findings" section
- Add "Assumptions" subsection: lockdown date choice (March 1, 2020), period boundary rationale, displacement hypothesis
- Add "Limitations" section: confounding factors (economic changes, policy changes), delayed reporting, short post-COVID period
- Add "Data Quality Summary"
- Include timestamp in title
</requirements>

<acceptance>
- Summary states high-level finding: increase/decrease/no change + displacement pattern
- Methods clearly define three periods with date ranges
- Lockdown date (March 2020) is justified in assumptions
- At least 3 limitations documented (confounders, reporting, short post period)
- Data quality table shows records per period
- Title includes timestamp
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

---

### TASK-2.15: Enhance Time Series Visualization with Annotations
**Objective:** Create publication-quality annotated time series showing lockdown impact clearly.

<requirements>
- Update time series chart to use colorblind-safe palette from config.COLORS
- Add vertical line marking lockdown date (March 1, 2020) in red with dashed style
- Add text annotation at lockdown line: "COVID-19 Lockdown"
- Add shaded regions for three periods: Before (light blue), During (light red), After (light green)
- Label each period with text annotations
- Add annotations for key events: peak Before period, minimum During period, recovery in After period
- Save at 300 DPI with timestamp
- Add trend lines for each period (optional but recommended)
</requirements>

<acceptance>
- Lockdown vertical line clearly visible at March 2020
- Three periods have distinct visual treatment (shading or background color)
- At least 5 annotations: lockdown marker, 3 period labels, peak/minimum points
- Colors are colorblind-safe
- Figure saved at 300 DPI
- Timestamp in subtitle
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

<context>
From research: "annotated time series chart (lockdown marked)" — make lockdown date very prominent
Heavy annotation: label every notable point
</context>

---

### TASK-2.16: Implement Displacement Analysis
**Objective:** Analyze burglary displacement (Residential vs Commercial) as required by CHIEF-03 success criteria.

<requirements>
- Filter data for burglary-related crimes (ucr codes for burglary)
- Classify burglaries as Residential vs Commercial based on location or offense codes
- Calculate period-over-period change: Before → During → After for each type
- Create comparative bar chart or line chart showing Residential vs Commercial trends
- Quantify displacement: "Residential burglaries increased X% while Commercial decreased Y%"
- Run statistical test (chi-square or t-test) comparing distributions
- Display results as formatted table
</requirements>

<acceptance>
- Burglary data filtered correctly (verify with sample counts)
- Residential and Commercial categories clearly defined
- Chart shows divergent trends (expected: Residential up, Commercial down during lockdown)
- Numeric summary: "Residential +X%, Commercial -Y% during lockdown"
- Statistical test shows significance (p-value displayed)
- Table shows counts for Residential and Commercial across three periods
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

<context>
Displacement hypothesis: During lockdown, people stayed home → commercial areas empty → burglars shifted to residential targets
</context>

---

### TASK-2.17: Comparative Pre/During/Post Analysis
**Objective:** Produce clear comparison of crime patterns across three COVID periods.

<requirements>
- Calculate aggregate crime counts for each period: Before, During, After
- Compute percent change: (During - Before) / Before * 100, (After - During) / During * 100
- Break down by crime category: Violent, Property, Other
- Create grouped bar chart comparing the three periods
- Add table showing: Period, Total Crimes, Violent %, Property %, Other %, Change from Previous
- Identify which crime types increased/decreased most during lockdown
- Test for statistical significance (ANOVA or chi-square)
</requirements>

<acceptance>
- Table clearly shows three periods with counts and percentages
- Bar chart visually compares periods side-by-side
- Percent change calculated for During vs Before and After vs During
- At least one category shows significant change (e.g., "Property crimes down 15% during lockdown")
- Statistical test result displayed (p-value)
- Interpretation provided: which types changed most
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

---

### TASK-2.18: Implement Versioned Artifact Generation
**Objective:** Save all outputs with versioned filenames and generate manifest.

<requirements>
- Import artifact_manager functions
- Update `plt.savefig()` calls to use versioned paths: `get_output_path('covid', 'png', version=VERSION)`
- Save artifacts: covid_timeline_vX.X.png, burglary_displacement_vX.X.png, period_comparison_vX.X.png
- Generate markdown report with summary, period comparison, displacement analysis
- Save report: covid_report_vX.X.md
- Create manifest JSON
- Include metadata in PNGs
</requirements>

<acceptance>
- At least 3 PNG files saved with version in filename
- Markdown report generated with all findings
- Manifest includes version, timestamp, git hash, artifacts
- All artifacts tracked with SHA256
- Manifest saved as `reports/covid_manifest_vX.X.json`
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

---

### TASK-2.19: Test Headless Execution
**Objective:** Verify notebook runs via papermill with COVID period parameters.

<requirements>
- Test: `papermill covid_lockdown_crime_landscape.ipynb output.ipynb -p VERSION "v1.0" -p LOCKDOWN_DATE "2020-03-01" -p BEFORE_YEARS "[2018,2019]"`
- Verify period parameters are injected correctly
- Ensure displacement analysis completes
- Add error handling for missing burglary data
- Test fast mode
</requirements>

<acceptance>
- Papermill execution succeeds
- Period boundaries correctly applied from parameters
- All artifacts generated
- Error handling prevents crashes
- Fast mode completes in < 30 seconds
</acceptance>

<files>
- UPDATE: `notebooks/covid_lockdown_crime_landscape.ipynb`
</files>

---

## Verification Criteria

### Must-Have Outcomes
1. **Config-driven**: COVID period definitions from config (lockdown date, year ranges)
2. **Annotated timeline**: Lockdown marker, period shading, key points labeled
3. **Displacement analysis**: Residential vs Commercial burglary trends quantified
4. **Period comparison**: Clear Before/During/After comparison with percent changes
5. **Versioned artifacts**: Timeline, displacement chart, comparison chart, report, manifest

### Success Metrics
- Lockdown date clearly marked on timeline (vertical line + annotation)
- Displacement result: "Residential +X%, Commercial -Y%"
- Period comparison shows at least one significant change
- All three periods have data (Before: 2018-2019, During: 2020-2021, After: 2023+)
- Headless execution via papermill succeeds

### Quality Checks
- [ ] No hardcoded COVID dates (all from config)
- [ ] Parameter cell tagged "parameters"
- [ ] Lockdown annotation prominent and clear
- [ ] Three periods visually distinct (shading or color)
- [ ] Burglary classification documented
- [ ] Statistical tests for displacement and period comparison
- [ ] All figures 300 DPI
- [ ] Error handling for edge cases

---

## Dependencies
- **Blocks on**: Wave 1 (analysis module, config, artifact_manager)
- **Data**: crime_incidents_combined.parquet
- **Configuration**: config/phase1_config.yaml (covid section)

---

## Estimated Effort
**Time:** 4-5 hours
**Complexity:** Medium-High (displacement analysis adds complexity)

---

## Notes
- Displacement analysis is unique to this notebook; may need custom burglary classification logic
- Period definitions should be very clear since they're central to the analysis
- Lockdown date (March 1, 2020) should be highly visible on charts
- Consider adding supplemental analysis: other crime types that changed (vehicle theft, assault, etc.)
- If burglary classification is unclear, document assumptions explicitly
