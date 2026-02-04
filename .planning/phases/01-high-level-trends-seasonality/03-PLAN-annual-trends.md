# Phase 1 Plan: Notebook Refactoring - Annual Trends
**Wave:** 2
**Depends on:** Wave 1 (Infrastructure)
**Files modified:** `notebooks/philadelphia_safety_trend_analysis.ipynb`
**Autonomous:** Yes

---

## Goal
Refactor the Annual Crime Trends notebook (CHIEF-01) to use external configuration, generate versioned artifacts, and produce academic-style reports. Transform from standalone analysis to production-ready component.

---

## Tasks

### TASK-2.1: Refactor Data Loading and Configuration
**Objective:** Replace hardcoded parameters with config-driven approach and standardize notebook structure.

<requirements>
- Add config loading cell at top: load Phase1Config, extract 'annual_trend' parameters
- Replace all hardcoded values with config references: start_year, end_year, min_complete_months
- Update data loading to use `analysis.utils.load_data()`
- Add parameter cell (for papermill injection) with default values from config
- Ensure 2026 data is explicitly excluded (per research: partial year)
- Add reproducibility cell documenting: Python version, package versions, execution date
</requirements>

<acceptance>
- Notebook runs without errors when config is present
- No hardcoded years or thresholds remain in code cells
- Parameter cell is properly tagged for papermill (add tags: ["parameters"])
- Data loading uses shared utility function
- 2026 records are filtered out programmatically
- Reproducibility cell outputs environment details
</acceptance>

<files>
- UPDATE: `notebooks/philadelphia_safety_trend_analysis.ipynb`
</files>

<context>
Current notebook structure (from research):
- ~1000 lines, fully functional
- Has TOC, statistical testing, good visualizations
- Main gaps: no external config, hardcoded paths, no formal report sections
</context>

---

### TASK-2.2: Restructure to Academic Report Format
**Objective:** Reorganize notebook sections to match academic style: Summary → Methods → Findings → Limitations.

<requirements>
- Add "Summary" section at top with 1-2 paragraph executive summary (to be written after analysis completes)
- Create "Methods" section documenting: data sources, date range, analysis approach, statistical tests used
- Rename/reorganize existing analysis cells under "Findings" section
- Add "Assumptions" subsection under Methods: document data quality assumptions, classification logic, trend definition
- Add "Limitations" section at end: partial 2026 data, reporting delays, classification changes
- Add "Data Quality Summary" section with table showing: total records, date range, missing data, excluded records
- Add generation timestamp to title
</requirements>

<acceptance>
- Notebook follows Summary → Methods → Findings → Limitations flow
- Methods section explicitly documents data sources and analytical approach
- At least 3 assumptions are documented
- At least 3 limitations are listed
- Data quality summary table includes: total records, date range, missing %, excluded count
- Title includes generation timestamp variable: `{timestamp}`
</acceptance>

<files>
- UPDATE: `notebooks/philadelphia_safety_trend_analysis.ipynb`
</files>

---

### TASK-2.3: Enhance Visualizations
**Objective:** Upgrade visualizations to publication quality with heavy annotations, colorblind-safe palette, and 300 DPI output.

<requirements>
- Update color palette to use `COLORS` from `analysis.config` (verify colorblind-safe)
- Add heavy annotations to annual trend chart: label peak year, label recent minimum, annotate trend line with slope and p-value
- Add COVID lockdown marker (vertical line at March 2020) with text annotation
- Ensure all figures are 300 DPI on save
- Add generation timestamp to figure subtitles
- Include sample size (N=X incidents) in chart titles where appropriate
- Ensure consistent font sizes (title: 16, labels: 12, annotations: 10)
</requirements>

<acceptance>
- All visualizations use colors from config.COLORS
- Annual trend chart has at least 4 annotations: peak, minimum, trend line stats, COVID marker
- Figures are saved with `dpi=300` parameter
- All figures include timestamp in subtitle or annotation
- Font sizes are consistent across all charts
- Trend line annotation shows: slope (crimes/year) and p-value
</acceptance>

<files>
- UPDATE: `notebooks/philadelphia_safety_trend_analysis.ipynb`
</files>

<context>
Heavy annotation philosophy (from research): "Every notable point labeled and explained"
</context>

---

### TASK-2.4: Implement Versioned Artifact Generation
**Objective:** Update all save operations to use versioned filenames and generate manifest.

<requirements>
- Import artifact_manager functions
- Update all `plt.savefig()` calls to use versioned paths from config: `get_output_path('annual_trend', 'png', version=VERSION)`
- Save primary outputs: annual_trend_vX.X.png, violent_vs_property_vX.X.png
- Generate markdown report using report template (if implemented in Wave 1, else create inline)
- Save markdown report: annual_trend_report_vX.X.md
- Add final cell that calls `create_version_manifest()` with all generated artifacts
- Include metadata in PNG files (title, author, timestamp)
</requirements>

<acceptance>
- All figures save to `reports/` directory with version in filename
- Markdown report is generated and saved
- Manifest JSON includes: version, timestamp, git hash, list of artifacts with SHA256
- PNG metadata includes creation timestamp
- At least 3 artifacts are listed in manifest
- Manifest is saved as `reports/annual_trend_manifest_vX.X.json`
</acceptance>

<files>
- UPDATE: `notebooks/philadelphia_safety_trend_analysis.ipynb`
</files>

---

### TASK-2.5: Add Data Quality Analysis Cell
**Objective:** Create explicit data quality summary using shared utilities.

<requirements>
- Add cell that calls `generate_data_quality_summary(df)` from report_utils
- Display quality metrics as formatted table: missing dates, duplicate dc_keys, records by year
- Highlight 2026 partial data issue
- Document any outliers or anomalies detected
- Add interpretation notes (e.g., "2026 excluded due to partial year coverage")
</requirements>

<acceptance>
- Data quality cell produces formatted markdown table
- Table includes at least: total records, date range, missing dates count, 2026 partial data note
- Quality summary is stored in variable for inclusion in final report
- Cell output is clear and easy to interpret
</acceptance>

<files>
- UPDATE: `notebooks/philadelphia_safety_trend_analysis.ipynb`
</files>

---

### TASK-2.6: Test Headless Execution
**Objective:** Verify notebook runs successfully via papermill with parameter injection.

<requirements>
- Test execution with: `papermill philadelphia_safety_trend_analysis.ipynb output.ipynb -p VERSION "v1.0" -p START_YEAR 2015 -p END_YEAR 2024`
- Ensure notebook completes without errors
- Verify all artifacts are generated in `reports/`
- Check that parameters are properly injected
- Add try/except blocks for critical operations (file loading, saving)
- Test with --fast mode (sample_frac parameter)
</requirements>

<acceptance>
- Papermill execution completes successfully
- All expected artifacts exist in reports/ after execution
- Parameters from papermill override defaults
- Errors are caught and logged gracefully
- Fast mode reduces data to 10% sample and completes in < 30 seconds
- Output notebook is saved without errors
</acceptance>

<files>
- UPDATE: `notebooks/philadelphia_safety_trend_analysis.ipynb`
</files>

---

## Verification Criteria

### Must-Have Outcomes
1. **Config-driven**: No hardcoded parameters; all driven by phase1_config.yaml
2. **Academic format**: Clear Summary, Methods, Findings, Limitations sections
3. **Publication-quality visualizations**: 300 DPI, colorblind-safe, heavily annotated
4. **Versioned artifacts**: All outputs include version in filename and are tracked in manifest
5. **Headless-ready**: Executes successfully via papermill

### Success Metrics
- Notebook runs end-to-end without errors via papermill
- Generates 3+ artifacts: PNG(s), markdown report, manifest JSON
- Report follows academic structure with all required sections
- All visualizations have 4+ annotations
- Data quality summary identifies 2026 partial data

### Quality Checks
- [ ] No hardcoded years/dates in code cells (all from config)
- [ ] Parameter cell has `parameters` tag for papermill
- [ ] All `plt.savefig()` calls use `dpi=300`
- [ ] Color palette is imported from config.COLORS
- [ ] Timestamp variable is used in titles/filenames
- [ ] Error handling for file operations (try/except)
- [ ] Markdown report matches template format

---

## Dependencies
- **Blocks on**: Wave 1 (analysis module, config system, artifact_manager)
- **Data**: crime_incidents_combined.parquet
- **Configuration**: config/phase1_config.yaml

---

## Estimated Effort
**Time:** 3-4 hours
**Complexity:** Medium (refactoring existing code, not creating from scratch)

---

## Notes
- Focus on refactoring, not rewriting: preserve existing analysis logic
- The notebook already has good statistical testing; preserve that
- Priority order: config integration → structure → visualizations → artifacts
- If report template is not ready from Wave 1, create inline markdown for now
