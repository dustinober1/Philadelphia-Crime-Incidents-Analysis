**Agents Guide**

- Purpose: concise rules and commands for contributors and agents.
- Environment: use the `crime` conda environment from `environment.yml`.
- Package policy: prefer conda packages; use pip only when conda does not provide a package.

Build / Lint / Test Commands
- Create environment: `conda env create -f environment.yml -n crime`.
- Update environment: `conda env update -f environment.yml`.
- Install dependencies if needed: `pip install -r requirements.txt`.
- Run tests: `pytest -q`.
- Run one file: `pytest -q tests/test_cli_chief.py`.
- Run one test: `pytest -q tests/test_cli_chief.py::test_chief_trends_basic`.
- Run by keyword: `pytest -q -k "keyword"`.
- Lint: `ruff check .`.
- Format: `black .`.
- Sort imports: `isort .`.
- Type check: `mypy .`.

Script Development Guidelines (v1.1)
- Purpose: scripts are reproducible, testable, and documentable analysis commands.
- Location: CLI commands live in `analysis/cli/{group}.py`; outputs go to `reports/{version}/{group}/`.
- Environment: execute in `crime`; document key package versions in `CLAUDE.md`, not in scripts.

Script Structure
- Use command signatures with `typer.Option(...)`, help text, and type hints.
- Use Rich Progress with 5 columns: `SpinnerColumn`, `TextColumn`, `BarColumn`, `TaskProgressColumn`, and `TimeRemainingColumn`.
- Load data with `analysis.data.loading.load_crime_data()` to preserve caching behavior.
- Save outputs with `analysis.visualization.save_figure()` and call `plt.close(fig)` afterward.
- Add graceful fallback behavior for optional dependencies: `prophet`, `sklearn`, and `geopandas`.

Example command pattern:

```python
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
```

Testing
- All command groups should have tests in `tests/test_cli_{group}.py`.
- Use `CliRunner` from `typer.testing` for command invocation.
- Always use `--fast` in tests.
- Use `--version test` to isolate test artifacts from production report paths.
- Verify `exit_code == 0`, expected stdout content, and expected output files.

Documentation
- Top-level help: `python -m analysis.cli --help`.
- Command help: `python -m analysis.cli chief trends --help`.
- Typer auto-generates help from docstrings and `Option()` parameters.

Code Style & Conventions
- Follow PEP 8 and prioritize clear code.
- Avoid wildcard imports.
- Keep command logic maintainable and explicit.

Imports
- Order imports as standard library, third-party, then local modules.
- Keep imports at module top unless deferred imports are needed for optional dependencies.

Types & Annotations
- Add type hints for public APIs and non-trivial internals.
- Use `-> None` for functions that do not return values.
- Prefer built-in generics (`list[int]`, `dict[str, float]`).

Error Handling & Logging
- Do not use bare `except:`.
- Preserve traceback context with `raise` or `raise from`.
- Use `logging` in reusable modules.
- Validate inputs early and fail with clear exceptions.

Data & Paths
- Use shared loaders and utilities from `analysis/`.
- Keep paths relative under `data/` and `reports/`.
- Never commit raw PII.

Agent Automation & CI Workflow
- Keep automation script-first and test-first.
- Keep quality checks deterministic and fast.
- Ensure command docs remain discoverable via `python -m analysis.cli --help`.

Commit Standards
- Commit small, focused changes.
- Reference affected outputs in `reports/` when artifacts change.
- Use clear commit messages tied to one intent.

Agent-specific expectations
- Run relevant tests before proposing or merging changes.
- Prefer deterministic command variants (`--fast`, test output versions) in automation.

Cursor / Copilot rules
- No `.cursor/rules/` or `.cursorrules` files detected.
- No `.github/copilot-instructions.md` file detected.

Where to look
- Environment: `environment.yml`, `requirements.txt`.
- CLI entry point: `analysis/cli/main.py`.
- Command groups: `analysis/cli/chief.py`, `analysis/cli/patrol.py`, `analysis/cli/policy.py`, `analysis/cli/forecasting.py`.
- Shared code: `analysis/`.
- Output artifacts: `reports/`.

Suggested next steps for contributors
- 1) Set up and activate `crime`.
- 2) Run `ruff`, `black`, `mypy`, and `pytest`.
- 3) Validate usage with `python -m analysis.cli --help`.

This file is an operational reference for contributors and agents. Update it when tooling or workflow changes.
