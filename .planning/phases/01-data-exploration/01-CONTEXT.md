# Phase 1: Data Exploration - Context

**Gathered:** 2026-01-27
**Status:** Ready for planning

<domain>
## Phase Boundary

User can load and understand the structure and quality of the crime incidents dataset. This phase focuses on the tooling to inspect the data, not the deep statistical analysis (Phase 2) or visualization (Phase 4).

</domain>

<decisions>
## Implementation Decisions

### Execution Interface
- **Format:** Python scripts (standard .py files), not Jupyter notebooks.
- **Architecture:** "Library + Runner" pattern. Core logic goes in `src/`, triggered by a runner script.
- **Feedback:** Verbose logging to the terminal (print details of checks as they happen).

### Configuration & Input
- **Config:** Use a `config.ini` file to define file paths and settings.
- **Input Format:** Single `.parquet` file (already downloaded).
- **Partitioning:** Script expects a single file, not a partitioned folder.

### Claude's Discretion
- Exact library structure in `src/`.
- Specific quality checks to run (nulls, types, etc. are implied by roadmap).
- Logging format implementation.

</decisions>

<specifics>
## Specific Ideas

- "The data has already been downloaded and is in a .parquet file."
- Work should be done via a Pull Request (PR).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-data-exploration*
*Context gathered: 2026-01-27*
