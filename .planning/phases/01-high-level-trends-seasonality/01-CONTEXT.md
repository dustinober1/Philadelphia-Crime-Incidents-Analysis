# Phase 1: High-Level Trends & Seasonality - Context

**Gathered:** 2026-02-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce audited, reproducible answers to three core questions:
1. Is Philadelphia getting safer? (10-year annual trend)
2. Is there a summer spike? (Monthly seasonality decomposition)
3. How did COVID change the landscape? (Pre/during/post COVID comparison with displacement analysis)

Deliverables: Three Jupyter notebooks that run headless via nbconvert and generate artifacts (PNGs, Markdown reports) in `reports/`.

</domain>

<decisions>
## Implementation Decisions

### Report format & structure
- **Style:** Academic-style technical reports with methods, assumptions, and limitations clearly documented
- **Section order:** Summary-first approach (brief summary at top, then methods, findings, limitations)
- **Assumptions:** Document everything — data issues, modeling choices, interpretation caveats
- **Timestamps:** Include generation timestamps in report body (aids reproducibility audits)

### Visualization design
- **Quality level:** Publication-ready — high-res, print-ready with clean typography and careful color choices
- **Annotations:** Heavy annotations — every notable point labeled and explained (e.g., COVID lockdown markers, trend changes)
- **Color scheme:** Consistent palette across all Phase 1 analyses for visual coherence
- **Accessibility:** Colorblind-safe palettes required (professional standards matter)

### Data quality handling
- **Data quality summary:** Each report includes an explicit summary table/section documenting all quality issues found
- **Record counts:** Conditional inclusion — show counts (e.g., 'N=12,450 incidents') only when sample size affects interpretation
- **Claude's Discretion:**
  - Missing data handling — choose appropriate approach based on severity (document and proceed, fail loudly, or impute)
  - Outlier detection — choose appropriate method per analysis (statistical detection, include and note, etc.)

### Reproducibility mechanics
- **Artifact naming:** Version numbers (e.g., `annual_trend_v1.md`, `annual_trend_v2.md`) to preserve analysis history
- **Parameter configuration:** External config file (JSON/YAML) loaded by notebooks — no hardcoded parameters
- **Headless execution:** Python orchestration script with logging and error handling (runs all three notebooks, manages outputs)
- **Dependencies:** pyproject.toml or Poetry for dependency management (match modern Python standards)

</decisions>

<specifics>
## Specific Ideas

- Heavy annotation philosophy: "Every notable point labeled and explained" — err on the side of over-explaining in visualizations
- Academic rigor: Document assumptions and limitations extensively, treat these as research outputs
- Success criterion from roadmap: "All analyses run headless via nbconvert and generate artifacts in `reports/`" — Python orchestrator should handle this seamlessly

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-high-level-trends-seasonality*
*Context gathered: 2026-02-02*
