# Phase 1 Plan: Integration & Testing
**Wave:** 3  
**Depends on:** Wave 1 (Infrastructure), Wave 2 (All Notebook Refactoring)  
**Files modified:** `analysis/orchestrate_phase1.py`, test files, documentation  
**Autonomous:** Yes  

---

## Goal
Integrate all three refactored notebooks into the orchestration pipeline, verify end-to-end headless execution, create comprehensive documentation, and validate that all Phase 1 success criteria are met.

---

## Tasks

### TASK-3.1: End-to-End Orchestration Testing
**Objective:** Verify the orchestrator can execute all three notebooks sequentially without manual intervention.

<requirements>
- Run full orchestration: `python analysis/orchestrate_phase1.py --version v1.0`
- Verify execution order: annual_trend → seasonality → covid (or parallel if safe)
- Check that all artifacts are generated in `reports/`
- Verify execution log captures all notebook outputs
- Test parameter injection for all three notebooks
- Verify manifest generation at end
- Test failure recovery: if one notebook fails, log error and continue (or stop, depending on --continue flag)
</requirements>

<acceptance>
- Running orchestrator completes all three notebooks
- Execution log shows: "Starting annual_trend...", "Completed in Xs", for each notebook
- All artifacts present in reports/: 6+ PNGs, 3 markdown reports, 3 manifests
- Global manifest (phase1_manifest_vX.X.json) generated with all artifacts
- If one notebook fails (simulated error), orchestrator handles gracefully
- Total execution time < 5 minutes (without fast mode)
</acceptance>

<files>
- UPDATE: `analysis/orchestrate_phase1.py`
- CREATE: `reports/execution.log`
- CREATE: `reports/phase1_manifest_vX.X.json`
</files>

<context>
Orchestrator should support:
- `--version v1.0`: specify version for all outputs
- `--config-path config/custom.yaml`: use custom config
- `--fast`: run with sample data (10%)
- `--notebook annual_trend`: run single notebook only
- `--continue`: continue after notebook failure
</context>

---

### TASK-3.2: Artifact Validation
**Objective:** Verify all generated artifacts meet quality standards and match success criteria.

<requirements>
- Check all PNG files are 300 DPI (use image metadata inspection)
- Verify all figures use colorblind-safe palette (visual inspection or automated check)
- Validate all markdown reports follow template format (Summary, Methods, Findings, Limitations)
- Check manifest JSON files are valid and complete (all required fields)
- Verify SHA256 hashes in manifests match actual file hashes
- Confirm timestamps are present in all outputs
- Check versioning is consistent across all artifacts
</requirements>

<acceptance>
- All PNGs are 300 DPI (checked programmatically)
- All reports have required sections (can grep for "## Summary", "## Methods", etc.)
- All manifests are valid JSON and parse without errors
- SHA256 hashes validate (recompute and compare)
- Timestamps are ISO format and recent
- Version numbers match across related artifacts (e.g., all v1.0)
</acceptance>

<files>
- CREATE: `analysis/validate_artifacts.py` (validation script)
</files>

---

### TASK-3.3: Create Comprehensive Documentation
**Objective:** Document Phase 1 execution, configuration options, and troubleshooting in README.

<requirements>
- Add "Phase 1: High-Level Trends & Seasonality" section to README.md
- Document orchestrator usage with examples: basic run, single notebook, fast mode, custom config
- Describe configuration file structure and key parameters
- List all generated artifacts with descriptions
- Add troubleshooting section: common errors and solutions
- Include example output showing successful execution log snippet
- Document version numbering scheme
</requirements>

<acceptance>
- README.md has "Phase 1" section with clear instructions
- At least 4 usage examples provided
- Configuration parameters documented (what each one does)
- Artifact list shows: filename pattern, description, typical size
- Troubleshooting covers: config not found, papermill errors, missing data
- Example log output helps users know what success looks like
</acceptance>

<files>
- UPDATE: `README.md`
</files>

---

### TASK-3.4: Create Quick-Start Script
**Objective:** Provide turnkey script for first-time users to run Phase 1 with defaults.

<requirements>
- Create `run_phase1.sh` (or `run_phase1.py`) wrapper script
- Check prerequisites: crime data exists, config exists, reports/ directory
- Run orchestrator with sensible defaults: version=v1.0, standard config
- Display progress to console
- Report summary at end: "Generated X artifacts in Y seconds"
- Include help message: `./run_phase1.sh --help`
</requirements>

<acceptance>
- Running `./run_phase1.sh` executes full Phase 1 pipeline
- Script checks for required files before starting
- Progress shown in real-time
- Summary message displays artifact count and execution time
- `--help` shows usage options
- Works on both macOS and Linux (use bash/python for portability)
</acceptance>

<files>
- CREATE: `run_phase1.sh` or `run_phase1.py`
</files>

---

### TASK-3.5: Validate Success Criteria
**Objective:** Systematically verify all Phase 1 success criteria from roadmap are met.

<requirements>
- **Criterion 1**: Reproducible annual aggregation notebook outputs clean PNG and Markdown summary
- **Criterion 2**: Seasonality notebook has boxplots and numeric summary (e.g., "18.3% increase July vs January")
- **Criterion 3**: COVID notebook has annotated timeline with lockdown marker and displacement analysis
- **Criterion 4**: All analyses run headless via nbconvert and generate artifacts in reports/
- Create validation checklist and verify each item
- Document results in `.planning/phases/01-high-level-trends-seasonality/06-VALIDATION.md`
</requirements>

<acceptance>
- All 4 success criteria verified and documented
- Validation report shows: criterion, status (✅ or ❌), evidence (file path or output snippet)
- Any failures are documented with remediation plan
- Validation report committed to planning directory
</acceptance>

<files>
- CREATE: `.planning/phases/01-high-level-trends-seasonality/06-VALIDATION.md`
</files>

<context>
Success criteria from roadmap:
1. Annual trend: PNG + MD report ✅
2. Seasonality: boxplots + numeric summary ✅
3. COVID: annotated chart + displacement ✅
4. Headless execution ✅
</context>

---

### TASK-3.6: Performance Optimization (Optional)
**Objective:** Optimize notebook execution time if initial runs are slow.

<requirements>
- Profile notebook execution to identify slow operations
- Consider data caching: save cleaned/processed data to intermediate parquet
- Optimize plot generation: reduce figure complexity if needed
- Add progress indicators for long-running operations
- Test parallel execution: run all three notebooks simultaneously if independent
- Document performance benchmarks: execution time per notebook
</requirements>

<acceptance>
- Full pipeline completes in < 5 minutes on standard hardware
- If caching implemented, second run is significantly faster
- Progress indicators help users know notebooks are running (not hung)
- Performance benchmarks documented (useful for future comparison)
- Parallel execution tested and documented (if safe)
</acceptance>

<files>
- UPDATE: `analysis/orchestrate_phase1.py` (if optimization needed)
- CREATE: `docs/performance.md` (optional)
</files>

<note>
This task is optional; only pursue if initial execution is >10 minutes
</note>

---

### TASK-3.7: Create Phase Completion Report
**Objective:** Generate summary report documenting Phase 1 completion, artifacts, and lessons learned.

<requirements>
- Document all deliverables: list of artifacts generated, locations, descriptions
- Summarize key findings from each notebook (high-level answers to the three questions)
- List lessons learned: what worked well, what challenges arose
- Identify improvements for future phases
- Record any deviations from original plan
- Include screenshots or example outputs
- Save as `.planning/phases/01-high-level-trends-seasonality/07-COMPLETION.md`
</requirements>

<acceptance>
- Completion report exists with all sections
- All artifacts listed with descriptions
- Key findings summarized (Is Philly safer? Summer spike? COVID impact?)
- At least 3 lessons learned documented
- Report is comprehensive enough for stakeholder review
</acceptance>

<files>
- CREATE: `.planning/phases/01-high-level-trends-seasonality/07-COMPLETION.md`
</files>

---

## Verification Criteria

### Must-Have Outcomes
1. **Full pipeline works**: `python analysis/orchestrate_phase1.py` runs all three notebooks successfully
2. **All artifacts generated**: 6+ PNGs, 3 reports, 3-4 manifests in reports/
3. **Documentation complete**: README has Phase 1 section with usage examples
4. **Success criteria validated**: All 4 roadmap criteria verified and documented
5. **Quick-start available**: Users can run `./run_phase1.sh` and get results

### Success Metrics
- Orchestrator completes all notebooks in < 5 minutes
- All artifacts pass validation (300 DPI, correct format, etc.)
- Documentation enables new user to run Phase 1 without asking questions
- Validation report shows all criteria met (4/4 ✅)
- Zero manual intervention required for execution

### Quality Checks
- [ ] Execution log is human-readable and informative
- [ ] Error messages are clear and actionable
- [ ] All generated files follow naming convention (versioned)
- [ ] Manifests are complete and accurate
- [ ] Documentation includes troubleshooting guidance
- [ ] Quick-start script checks prerequisites
- [ ] Validation report is thorough and evidence-based

---

## Dependencies
- **Blocks on**: Wave 1 (infrastructure), Wave 2 (all three notebooks refactored)
- **Data**: crime_incidents_combined.parquet
- **Configuration**: config/phase1_config.yaml

---

## Estimated Effort
**Time:** 3-4 hours  
**Complexity:** Medium (integration and testing focus)

---

## Notes
- This wave is about validation and documentation, not new features
- Focus on making Phase 1 reproducible and user-friendly
- The validation report is critical for demonstrating completeness
- Quick-start script lowers barrier to entry for new users
- Performance optimization is optional; prioritize correctness first
