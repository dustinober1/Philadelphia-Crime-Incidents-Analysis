# Phase 1 Plan: Notebook Refactoring - Seasonality Analysis
**Wave:** 2
**Depends on:** Wave 1 (Infrastructure)
**Files modified:** `notebooks/summer_crime_spike_analysis.ipynb`
**Autonomous:** Yes

---

## Goal
Refactor the Summer Crime Spike / Seasonality notebook (CHIEF-02) to use external configuration, produce monthly decomposition with quantified differences, and generate academic-style reports with versioned artifacts.

---

## Tasks

### TASK-2.7: Refactor Data Loading and Configuration
**Objective:** Integrate external configuration and standardize notebook structure for seasonality analysis.

<requirements>
- Add config loading cell at top: load Phase1Config, extract 'seasonality' parameters
- Replace hardcoded values with config references: summer_months [6,7,8], winter_months [1,2,3], significance_level 0.05
- Update data loading to use `analysis.utils.load_data()`
- Add parameter cell for papermill with: VERSION, SUMMER_MONTHS, WINTER_MONTHS, SIGNIFICANCE_LEVEL
- Exclude 2026 data explicitly (partial year)
- Add reproducibility cell documenting environment
</requirements>

<acceptance>
- Config is loaded at notebook start
- Parameters for summer/winter months come from config
- Parameter cell is tagged "parameters" for papermill
- 2026 records are excluded programmatically
- Data loading uses shared utility
- No hardcoded month lists or thresholds remain
</acceptance>

<files>
- UPDATE: `notebooks/summer_crime_spike_analysis.ipynb`
</files>

<context>
Current notebook (from research):
- ~1100 lines, fully functional
- Has boxplots, quantitative comparison, t-test
- Gaps: no external config, missing formal methods section, no artifact versioning
</context>

---

### TASK-2.8: Restructure to Academic Report Format
**Objective:** Reorganize sections to match academic style with explicit methods, assumptions, and limitations.

<requirements>
- Add "Summary" section: brief answer to "Is there a summer spike?" with magnitude (e.g., "+18.3%")
- Create "Methods" section: describe seasonality decomposition approach, month grouping logic, statistical test (t-test)
- Group existing analysis under "Findings" section
- Add "Assumptions" subsection: document assumptions about seasonal patterns, month grouping rationale
- Add "Limitations" section: reporting delays, weather correlation not tested, definition of "summer" is arbitrary
- Add "Data Quality Summary" section
- Include generation timestamp in title
</requirements>

<acceptance>
- Summary states clear answer: "Yes, summer shows X% increase vs winter" or similar
- Methods section documents: which months are summer/winter, which statistical test, why
- At least 3 assumptions documented (e.g., "Assumed summer = June/July/August")
- At least 3 limitations listed
- Data quality table shows records analyzed, excluded, date range
- Title includes timestamp placeholder
</acceptance>

<files>
- UPDATE: `notebooks/summer_crime_spike_analysis.ipynb`
</files>

---

### TASK-2.9: Enhance Month-Level Visualizations
**Objective:** Create publication-quality boxplots and seasonal charts with heavy annotations.

<requirements>
- Update monthly boxplot to use colorblind-safe palette from config.COLORS
- Add annotations to boxplot: label summer months (highlight background), label winter months, show median values
- Add numeric summary to chart: "July: median=X, Jan: median=Y, difference=Z%"
- Create supplemental line chart showing month-by-month average crime counts with error bars
- Add 300 DPI save parameter to all figures
- Include timestamp in figure subtitles
- Annotate peak summer month and lowest winter month
</requirements>

<acceptance>
- Boxplot uses colors from config.COLORS
- Summer months (6,7,8) have highlighted background or distinct color
- At least 4 annotations on main chart: summer highlight, winter highlight, median labels, percent difference
- Line chart shows all 12 months with error bars (std or CI)
- All figures saved at 300 DPI
- Peak month (likely July) and lowest month are explicitly labeled
</acceptance>

<files>
- UPDATE: `notebooks/summer_crime_spike_analysis.ipynb`
</files>

<context>
From research: "18.3% increase July vs January" — ensure this type of quantification is visible on charts
</context>

---

### TASK-2.10: Quantify Seasonal Differences
**Objective:** Produce clear numeric summary of month-to-month percentage differences as required by CHIEF-02.

<requirements>
- Calculate percent change: (summer_avg - winter_avg) / winter_avg * 100
- Create summary table: month, mean crimes, median crimes, std, rank
- Compute pairwise comparisons: July vs January, July vs February, June vs January
- Run statistical significance test (t-test) comparing summer vs winter distributions
- Display results as formatted markdown table
- Store numeric summary in variable for inclusion in final report
</requirements>

<acceptance>
- Summary statement: "Summer months show X% increase compared to winter months (p < 0.05)"
- Table shows all 12 months with statistics
- Pairwise comparison clearly states: "July has X% more crimes than January"
- T-test result is displayed with p-value
- Summary is formatted as markdown table in output
</acceptance>

<files>
- UPDATE: `notebooks/summer_crime_spike_analysis.ipynb`
</files>

---

### TASK-2.11: Implement Versioned Artifact Generation
**Objective:** Save all outputs with versioned filenames and generate manifest.

<requirements>
- Import artifact_manager functions
- Update `plt.savefig()` calls to use versioned paths: `get_output_path('seasonality', 'png', version=VERSION)`
- Save artifacts: seasonality_boxplot_vX.X.png, monthly_trend_vX.X.png
- Generate markdown report with summary, findings, and numeric results
- Save report: seasonality_report_vX.X.md
- Create manifest JSON with all artifacts
- Include PNG metadata (title, timestamp)
</requirements>

<acceptance>
- At least 2 PNG files saved to reports/ with version in filename
- Markdown report generated and saved
- Manifest includes version, timestamp, git hash, artifact list
- All files tracked in manifest with SHA256 hashes
- Manifest saved as `reports/seasonality_manifest_vX.X.json`
</acceptance>

<files>
- UPDATE: `notebooks/summer_crime_spike_analysis.ipynb`
</files>

---

### TASK-2.12: Test Headless Execution
**Objective:** Verify notebook runs successfully via papermill with parameter injection.

<requirements>
- Test with: `papermill summer_crime_spike_analysis.ipynb output.ipynb -p VERSION "v1.0" -p SUMMER_MONTHS "[6,7,8]" -p WINTER_MONTHS "[1,2,3]"`
- Verify parameter injection works for month lists
- Ensure all artifacts generate correctly
- Add error handling for edge cases (empty months, invalid date ranges)
- Test fast mode with sample data
</requirements>

<acceptance>
- Papermill execution completes without errors
- Summer/winter month parameters are correctly injected
- All expected artifacts exist after execution
- Error handling prevents crashes on edge cases
- Fast mode completes in < 30 seconds
</acceptance>

<files>
- UPDATE: `notebooks/summer_crime_spike_analysis.ipynb`
</files>

---

## Verification Criteria

### Must-Have Outcomes
1. **Config-driven**: Summer/winter months and significance level from config
2. **Quantified results**: Clear percentage difference stated (e.g., "18.3% increase")
3. **Publication-quality boxplots**: Colorblind-safe, heavily annotated, 300 DPI
4. **Academic format**: Summary, Methods, Findings, Limitations
5. **Versioned artifacts**: Boxplot, line chart, report, manifest

### Success Metrics
- Numeric summary: "Summer shows X% increase vs winter (p < 0.05)"
- Boxplot has 4+ annotations
- Statistical test (t-test) shows p-value
- Markdown report includes month-by-month table
- Headless execution via papermill succeeds

### Quality Checks
- [ ] No hardcoded month lists (all from config)
- [ ] Parameter cell tagged "parameters"
- [ ] All figures 300 DPI
- [ ] Colorblind-safe palette used
- [ ] T-test result displayed with p-value
- [ ] Percent difference calculated correctly
- [ ] Error handling for statistical operations

---

## Dependencies
- **Blocks on**: Wave 1 (analysis module, config, artifact_manager)
- **Data**: crime_incidents_combined.parquet
- **Configuration**: config/phase1_config.yaml (seasonality section)

---

## Estimated Effort
**Time:** 3-4 hours
**Complexity:** Medium (similar to Task 2.1-2.6 but for different notebook)

---

## Notes
- The notebook already has good statistical validation (t-test); preserve that
- Focus on making the numeric comparison very clear and prominent
- Boxplot annotations should make summer spike visually obvious
- If extending analysis, consider adding seasonal decomposition (trend + seasonal + residual)
