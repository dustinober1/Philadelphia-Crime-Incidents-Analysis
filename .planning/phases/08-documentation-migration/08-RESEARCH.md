# Phase 08: Documentation & Migration - Research

**Researched:** 2026-02-05
**Domain:** Technical Documentation & Code Migration
**Confidence:** HIGH

## Summary

Phase 08 focuses on two primary workstreams: (1) documenting the new v1.1 CLI-based architecture, and (2) migrating all 13 notebooks from v1.0 to CLI scripts, then deleting the notebooks. The phase has strong dependencies on Phases 6-7 (CLI system and testing infrastructure must be complete) and represents the final milestone in the v1.1 refactor.

**Key findings:**
- All 13 CLI commands are implemented and tested (90%+ coverage)
- Documentation exists but is notebook-centric (AGENTS.md, CLAUDE.md, README.md reference notebooks)
- 20 notebook files exist (some are .executed.ipynb duplicates)
- Migration pattern is established: CLI commands already implement notebook logic
- Verification infrastructure exists (pytest, CliRunner, output pattern matching)

**Primary recommendation:** Use a phased approach: (1) document CLI patterns first, (2) create migration guide, (3) verify outputs match, (4) delete notebooks, (5) update project docs.

## Standard Stack

### Documentation Tools
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Markdown | - | Primary documentation format | Universal, GitHub-native, supports code blocks |
| typer | 0.12+ | CLI auto-documentation | Built-in `--help` generation from docstrings |
| pytest | 9.0+ | Verification tests | Existing test infrastructure, coverage measurement |

### Migration Tools
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| jupyter | - | Notebook execution | For extracting analysis logic |
| nbformat | - | Notebook parsing | Programmatic notebook reading |
| papermill | - | Notebook execution | Existing orchestration tool (legacy) |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| CliRunner (typer.testing) | CLI invocation testing | Verify migrated scripts work |
| pytest fixtures | Test data isolation | Fast testing without full datasets |

**Installation:**
```bash
# Documentation tools (already installed via Phase 6)
pip install typer>=0.12 rich>=13.0

# Migration tools (already in environment)
conda install jupyter nbformat
```

## Architecture Patterns

### Documentation Structure

The project uses a multi-tier documentation approach:

```
README.md                 # User-facing quickstart
CLAUDE.md                 # Agent/contributor guidance
AGENTS.md                 # Contribution rules (NOTEBOOK-CENTRIC - needs update)
docs/                     # Additional documentation
  ├── DELIVERY_SUMMARY.md
  ├── FORECASTING_SUMMARY.md
  ├── NOTEBOOK_COMPLETION_REPORT.md (NOTEBOOK-CENTRIC - needs update)
  └── NOTEBOOK_QUICK_REFERENCE.md (NOTEBOOK-CENTRIC - needs update)
.planning/
  ├── PROJECT.md          # Project overview (needs notebook references removed)
  ├── ROADMAP.md          # Development phases (needs v1.1 completion)
  ├── STATE.md            # Current state tracking
  └── phases/XX/          # Phase-specific docs
```

### Pattern 1: CLI Documentation via Typer
**What:** Typer auto-generates help text from function signatures and docstrings
**When to use:** All CLI commands should have comprehensive `--help` output
**Example:**
```python
# Source: analysis/cli/chief.py (existing pattern)
@app.command()
def trends(
    start_year: int = typer.Option(2015, help="Start year for analysis", min=2006, max=2026),
    end_year: int = typer.Option(2024, help="End year for analysis", min=2006, max=2026),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
    output_format: Literal["png", "svg", "pdf"] = typer.Option("png", help="Figure output format"),
) -> None:
    """Generate annual crime trends analysis."""
```

This pattern generates:
```bash
$ python -m analysis.cli chief trends --help
Usage: python -m analysis.cli chief trends [OPTIONS]

 Generate annual crime trends analysis.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --start-year           INTEGER RANGE              Start year for analysis    │
│                        [2006<=x<=2026]            [default: 2015]            │
│ --end-year             INTEGER RANGE              End year for analysis      │
│                        [2006<=x<=2026]            [default: 2024]            │
│ --version              TEXT                       Output version tag         │
│                                                   [default: v1.0]            │
│ --fast                                            Fast mode with 10% sample  │
│ --output-format        [png|svg|pdf]              Figure output format       │
│                                                   [default: png]             │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Pattern 2: Migration Verification
**What:** Use pytest with CliRunner to verify CLI output matches notebook artifacts
**When to use:** After each notebook migration, before deletion
**Example:**
```python
# Source: tests/test_cli_chief.py (existing pattern)
from typer.testing import CliRunner
from analysis.cli.main import app

runner = CliRunner()

def test_chief_trends_basic(self, tmp_output_dir: Path) -> None:
    """Test basic execution of trends command with --fast flag."""
    result = runner.invoke(
        app,
        ["chief", "trends", "--fast", "--version", "test"],
    )

    # Verify command executed successfully
    assert result.exit_code == 0, f"Command failed: {result.output}"

    # Verify expected output content
    assert "Annual Trends Analysis" in result.stdout
    assert "Analysis complete" in result.stdout

    # Verify output files created
    output_dir = Path("reports/test/chief")
    assert output_dir.exists()
    assert (output_dir / "annual_trends_report_trend.png").exists()
```

### Anti-Patterns to Avoid
- **Deleting notebooks before verification:** Always verify CLI outputs match notebook artifacts first
- **Documentation drift:** Don't update README.md without also updating CLAUDE.md and AGENTS.md
- **Incomplete migration:** Don't delete notebooks until all 13 are migrated and verified
- **Skipping archival:** Keep v1.0 notebook artifacts in `reports/v1.0/` for historical reference

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI help generation | Custom `--help` parsing | typer's auto-generated help | Typer reads docstrings, consistent formatting |
| Output verification | Custom comparison scripts | pytest + CliRunner pattern matching | Existing test infrastructure, fixtures for isolation |
| Configuration docs | Manual config reference | YAML + pydantic schemas | Self-documenting, type-safe |
| Migration guides | Ad-hoc notes | Structured MIGRATION.md with examples | Reusable pattern for future contributors |

**Key insight:** The CLI system (Phase 6) already provides documentation via `--help`. The migration guide should reference this, not duplicate it.

## Common Pitfalls

### Pitfall 1: Documentation Inconsistency
**What goes wrong:** README.md says "use notebooks" but CLAUDE.md says "use CLI"
**Why it happens:** Documentation updated piecemeal during refactoring
**How to avoid:** Create a documentation checklist, update all files in one pass
**Warning signs:** Conflicting instructions in different docs, references to deleted files

### Pitfall 2: Premature Notebook Deletion
**What goes wrong:** Notebooks deleted before CLI outputs are verified to match
**Why it happens:** Eagerness to complete migration, pressure to "clean up"
**How to avoid:** Strict verification protocol: (1) migrate, (2) test, (3) verify, (4) archive, (5) delete
**Warning signs:** "Let's just delete these, the CLI works"

### Pitfall 3: Incomplete Output Verification
**What goes wrong:** CLI runs but produces different visualizations or statistics than notebooks
**Why it happens:** Subtle logic differences, random seeds, data sampling
**How to avoid:** Use pattern matching in tests (not exact values), visual inspection of figures
**Warning signs:** Tests pass but figures look different, missing statistics in output

### Pitfall 4: Lost Historical Context
**What goes wrong:** Deleting all notebook artifacts breaks ability to compare v1.0 vs v1.1
**Why it happens:** "Clean slate" mentality, not thinking about reproducibility
**How to avoid:** Archive `reports/v1.0/` before deleting notebooks, keep manifests
**Warning signs:** No reference artifacts for comparison

### Pitfall 5: Breaking Existing Workflows
**What goes wrong:** Users who relied on notebook execution can no longer run analyses
**Why it happens:** CLI migration changes invocation patterns
**How to avoid:** Document migration path clearly, keep `./run_phase1.sh` working (invoke CLI)
**Warning signs:** "Just use the CLI" without explaining how it replaces notebooks

## Code Examples

### Creating a Migration Guide
```markdown
# Notebook to CLI Migration Guide

## Overview
This guide explains how v1.0 notebooks map to v1.1 CLI commands.

## Migration Mapping

### Phase 1 (Chief) Notebooks → Chief Commands

| Notebook | CLI Command | Verification Test |
|----------|-------------|-------------------|
| `philadelphia_safety_trend_analysis.ipynb` | `python -m analysis.cli chief trends` | `tests/test_cli_chief.py::TestChiefTrends` |
| `summer_crime_spike_analysis.ipynb` | `python -m analysis.cli chief seasonality` | `tests/test_cli_chief.py::TestChiefSeasonality` |
| `covid_lockdown_crime_landscape.ipynb` | `python -m analysis.cli chief covid` | `tests/test_cli_chief.py::TestChiefCovid` |

### Usage Example

**v1.0 (Notebook):**
\`\`\`bash
jupyter notebook notebooks/philadelphia_safety_trend_analysis.ipynb
# Run all cells, wait 3-5 minutes
\`\`\`

**v1.1 (CLI):**
\`\`\`bash
# Full run
python -m analysis.cli chief trends

# Fast mode (10% sample, ~30 seconds)
python -m analysis.cli chief trends --fast

# Custom date range
python -m analysis.cli chief trends --start-year 2018 --end-year 2022

# SVG output
python -m analysis.cli chief trends --output-format svg
\`\`\`
```

### Updating AGENTS.md (Script-Based Rules)
```markdown
## Script Development Guidelines (v1.1)

### Purpose
Analysis scripts are reproducible, testable, and documentable. Scripts live in `analysis/cli/` and are invoked via `python -m analysis.cli`.

### Location
- CLI commands: `analysis/cli/{group}.py` (chief.py, patrol.py, policy.py, forecasting.py)
- Output artifacts: `reports/{version}/{group}/`

### Environment
Use the `crime` conda environment defined in `environment.yml`. Record key package versions in CLAUDE.md.

### Script Structure
1. **Function signature:** Use typer.Options with help text and type hints
2. **Progress bars:** Use Rich Progress with 5 columns (Spinner, Text, Bar, TaskProgress, TimeRemaining)
3. **Data loading:** Use `analysis.data.loading.load_crime_data()` with caching
4. **Output saving:** Use `analysis.visualization.save_figure()` with plt.close()
5. **Error handling:** Graceful fallback for optional dependencies (prophet, sklearn, geopandas)

### Example Command
\`\`\`python
@app.command()
def trends(
    start_year: int = typer.Option(2015, help="Start year for analysis"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
) -> None:
    """Generate annual crime trends analysis."""
    config = TrendsConfig(start_year=start_year)
    df = load_crime_data(clean=True)
    if fast:
        df = df.sample(frac=0.1, random_state=42)
    # ... analysis logic ...
    save_figure(fig, output_path, output_format=config.output_format)
    plt.close(fig)
\`\`\`

### Testing
- All commands must have tests in `tests/test_cli_{group}.py`
- Use CliRunner from typer.testing
- Use `--fast` flag in tests for speed
- Use `--version test` to avoid cluttering production reports
```

### Updating README.md Quickstart
```markdown
## Quickstart

### Prerequisites
- Python 3.14+
- Conda environment `crime` (see `environment.yml`)

### Installation
\`\`\`bash
# Create conda environment
conda env create -f environment.yml
conda activate crime

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt
\`\`\`

### Running Analyses

**v1.1 CLI (Recommended):**
\`\`\`bash
# Run any analysis
python -m analysis.cli chief trends --fast
python -m analysis.cli patrol hotspots --fast
python -m analysis.cli policy retail-theft --fast
python -m analysis.cli forecasting time-series --fast

# See all commands
python -m analysis.cli --help

# Get command-specific help
python -m analysis.cli chief trends --help
\`\`\`

**Output:** All artifacts saved to `reports/{version}/{group}/` with PNG/SVG/PDF figures and text summaries.
```

### Verification Test Pattern
```python
# Source: tests/test_cli_chief.py (existing)
def test_chief_trends_output_files(self, tmp_output_dir: Path) -> None:
    """Test that trends command creates expected output files."""
    result = runner.invoke(
        app,
        ["chief", "trends", "--fast", "--version", "test"],
    )

    assert result.exit_code == 0, f"Command failed: {result.output}"

    # Check output directory
    output_dir = Path("reports/test/chief")
    assert output_dir.exists()

    # Check for expected output files
    expected_files = [
        "annual_trends_report_summary.txt",
        "annual_trends_report_trend.png",
    ]

    for filename in expected_files:
        file_path = output_dir / filename
        assert file_path.exists(), f"Expected output file not created: {file_path}"
```

## State of the Art

| Old Approach (v1.0) | Current Approach (v1.1) | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Jupyter notebooks | CLI scripts with typer | Phase 6 (2026-02-04) | Better testability, CI/CD integration |
| Manual papermill execution | `python -m analysis.cli` | Phase 6 (2026-02-04) | Simpler invocation, no Jupyter dependency |
| Notebooks as documentation | CLI `--help` + separate docs | Phase 8 (pending) | Self-documenting code |
| AGENTS.md notebook rules | Script-based contribution rules | Phase 8 (pending) | Align docs with new architecture |

**Deprecated/outdated:**
- **Notebook-first development:** Scripts are now primary; notebooks are legacy
- **papermill orchestration:** Replaced by direct CLI invocation
- **Notebook reproducibility cells:** Replaced by version-controlled scripts with tests
- **AGENTS.md notebook rules:** Will be replaced with script development guidelines

## Open Questions

1. **Should we keep any notebooks for reference?**
   - What we know: Documentation says "delete all notebooks"
   - What's unclear: Whether to keep `.executed.ipynb` files as examples
   - Recommendation: Archive to `reports/v1.0/notebooks/` then delete from `notebooks/`

2. **How to handle `run_phase1.sh` script?**
   - What we know: It currently invokes orchestrator with papermill
   - What's unclear: Should it invoke CLI instead, or be deleted?
   - Recommendation: Update to invoke CLI commands, keep for backward compatibility

3. **What about `data_quality_audit_notebook.ipynb`?**
   - What we know: Not in the 13 notebooks to migrate (exploratory, not production)
   - What's unclear: Should it be migrated or deleted?
   - Recommendation: Delete (not a core analysis, exploratory only)

4. **How detailed should the migration guide be?**
   - What we know: Need to map notebooks to CLI commands
   - What's unclear: Should we include step-by-step conversion instructions?
   - Recommendation: Focus on usage patterns, not conversion internals (users invoke CLI, don't modify it)

5. **Should we document the v1.0 → v1.1 diff?**
   - What we know: Major architectural change
   - What's unclear: Is a changelog needed?
   - Recommendation: Add "v1.1 Release Notes" section to README.md

## Sources

### Primary (HIGH confidence)
- `analysis/cli/` - CLI implementation (4 command groups, 13 commands)
- `tests/test_cli_*.py` - Existing test patterns for verification
- `CLAUDE.md` - Current documentation (notebook-centric, needs update)
- `AGENTS.md` - Contribution rules (notebook-centric, needs update)
- `README.md` - Project quickstart (notebook-centric, needs update)
- `.planning/REQUIREMENTS.md` - DOCS and MIGRATE requirements

### Secondary (MEDIUM confidence)
- `.planning/ROADMAP.md` - Phase descriptions and success criteria
- `.planning/STATE.md` - Current state and accumulated decisions
- `pyproject.toml` - Quality tooling configuration
- `.pre-commit-config.yaml` - Pre-commit hooks (pytest hook)

### Tertiary (LOW confidence)
- None for this phase (all information from codebase, no external research needed)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools already installed and used in Phases 6-7
- Architecture: HIGH - CLI system complete and tested, migration pattern established
- Pitfalls: HIGH - Based on common documentation/migration anti-patterns

**Research date:** 2026-02-05
**Valid until:** 2026-03-05 (30 days - documentation patterns stable)

**Note:** This phase involves updating documentation, not implementing new features. All tools and patterns are already established in Phases 6-7. The focus is on communication and verification, not new technical work.
