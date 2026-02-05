# Phase 06: Configuration & CLI System - Research

**Researched:** 2026-02-04
**Domain:** CLI frameworks, configuration management, Python packaging
**Confidence:** HIGH

## Summary

Phase 06 requires building a configuration system and CLI entry points for 13 data analysis scripts. The research identified established Python patterns for: (1) CLI construction using typer with Rich integration for progress feedback, (2) configuration management using pydantic-settings with YAML, CLI, and environment variable sources, (3) modular CLI architecture for multiple analysis commands, and (4) progress bar patterns for long-running data operations.

**Key findings:**
- **typer** is the standard CLI framework for Python in 2026, with excellent Rich integration
- **pydantic-settings** provides the official solution for multi-source configuration (YAML + CLI + env vars)
- Modular CLI structure using `typer.Typer()` instances per analysis area is the recommended pattern
- Rich's `Progress` context manager with multiple task columns is the standard for data pipeline feedback
- Python's `-m` module execution (`__main__.py`) enables clean CLI entry points without console_scripts

**Primary recommendation:** Use typer for CLI construction, pydantic-settings for configuration merging (YAML defaults → env vars → CLI args), Rich for progress bars, and organize 13 CLI scripts under `analysis/cli/` with a main typer app for command grouping.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **typer** | 0.12+ | CLI framework with type hints | Official recommendation, excellent UX, Rich integration |
| **pydantic** | 2.12+ | Data validation | Already in project, type-safe configuration |
| **pydantic-settings** | 2.0+ | Multi-source config loading | Official pydantic library for YAML/CLI/env var merging |
| **rich** | 13.0+ | Terminal output and progress bars | Standard for beautiful CLI output, integrates with typer |
| **pyyaml** | 6.0+ | YAML parsing | Required for pydantic-settings YAML support |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **click** | 8.0+ | Alternative CLI framework | Only if typer is insufficient (not recommended) |
| **python-dotenv** | 1.0+ | .env file loading | For local development environment variables |
| **confz** | 2.0+ | Alternative config library | Not recommended - pydantic-settings is official |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| typer | click, argparse | typer has better type hints and Rich integration |
| pydantic-settings | dynaconf, python-dotenv, omegaconf | pydantic-settings is official and integrates with pydantic v2 |
| rich | tqdm, rich | rich is more feature-rich and integrates with typer |
| YAML config | TOML, JSON, INI | YAML is more readable for hierarchical config |

**Installation:**
```bash
# Add to requirements-dev.txt (dev dependencies)
pip install typer>=0.12 rich>=13.0 pydantic-settings>=2.0
# pydantic and pyyaml already required
```

## Architecture Patterns

### Recommended Project Structure

```
analysis/
├── __init__.py
├── cli/                          # NEW: CLI entry points
│   ├── __init__.py
│   ├── __main__.py               # Enables: python -m analysis.cli
│   ├── main.py                   # Main typer app with command groups
│   ├── chief.py                  # Chief analyses (trends, seasonality, covid)
│   ├── patrol.py                 # Patrol analyses (hotspots, robbery, etc.)
│   ├── policy.py                 # Policy analyses (retail theft, vehicle, etc.)
│   └── forecasting.py            # Forecasting analyses (time series, classification)
├── config/                       # NEW: Configuration system
│   ├── __init__.py
│   ├── settings.py               # Pydantic settings models
│   ├── cli_config.py             # CLI argument to config merge logic
│   └── schemas/                  # Pydantic models for each analysis
│       ├── __init__.py
│       ├── chief.py              # Trends, seasonality, COVID schemas
│       ├── patrol.py             # Hotspots, robbery, district, census schemas
│       ├── policy.py             # Retail theft, vehicle, composition, events schemas
│       └── forecasting.py        # Time series, classification schemas
├── data/                         # EXISTS: Data layer
├── utils/                        # EXISTS: Utility modules
└── visualization/                # FUTURE: Visualization utilities

config/
├── global.yaml                   # NEW: Global shared config
├── chief.yaml                    # NEW: Chief analyses config (trends, seasonality, covid)
├── patrol.yaml                   # NEW: Patrol analyses config
├── policy.yaml                   # NEW: Policy analyses config
└── forecasting.yaml              # NEW: Forecasting analyses config
```

### Pattern 1: Multi-Source Configuration with pydantic-settings

**What:** Load configuration from YAML files, allow environment variable overrides, and finally CLI argument overrides using pydantic-settings' source priority system.

**When to use:** All 13 analysis scripts need consistent configuration with local overrides.

**Example:**

```python
# analysis/config/settings.py
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource, PydanticBaseSettingsSource
from typing import Tuple

class ClusteringConfig(BaseModel):
    eps_degrees: float = 0.002
    min_samples: int = 50
    algorithm: str = "DBSCAN"

class AnalysisConfig(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="config/patrol.yaml",
        env_prefix="CRIME_",
        env_nested_delimiter="__",
    )

    version: str = "v1.0"
    output_dir: Path = Field(default=Path("reports"))
    dpi: int = 300
    fast_sample_frac: float = 0.1

    clustering: ClusteringConfig = Field(default_factory=ClusteringConfig)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Priority: CLI args (init) > env vars > YAML > defaults
        return (
            init_settings,      # CLI arguments (highest priority)
            env_settings,       # Environment variables
            YamlConfigSettingsSource(settings_cls),  # YAML files
            dotenv_settings,    # .env files
        )

# Usage: settings = AnalysisConfig()  # Auto-loads from YAML, env, CLI
```

**Source:** Context7 - `/pydantic/pydantic-settings` (YamlConfigSettingsSource, settings_customise_sources)

### Pattern 2: Modular CLI with typer Subcommands

**What:** Create separate typer instances for each analysis area, then combine them under a main app using `app.add_typer()`.

**When to use:** Organizing 13 CLI commands into logical groups (Chief, Patrol, Policy, Forecasting).

**Example:**

```python
# analysis/cli/main.py
import typer
from . import chief, patrol, policy, forecasting

app = typer.Typer(
    name="crime-analysis",
    help="Philadelphia Crime Incidents Analysis CLI",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(chief.app, name="chief", help="Chief-level trend analyses")
app.add_typer(patrol.app, name="patrol", help="Patrol operations analyses")
app.add_typer(policy.app, name="policy", help="Policy evaluation analyses")
app.add_typer(forecasting.app, name="forecasting", help="Forecasting and prediction analyses")

@app.command()
def version():
    """Show version information."""
    from analysis.config import __version__
    typer.echo(f"Crime Analysis CLI v{__version__}")

if __name__ == "__main__":
    app()

# analysis/cli/chief.py
import typer
from rich.console import Console
from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

app = typer.Typer(help="Chief-level analyses (trends, seasonality, COVID)")
console = Console()

@app.command()
def trends(
    start_year: int = typer.Option(2015, help="Start year for analysis"),
    end_year: int = typer.Option(2024, help="End year for analysis"),
    version: str = typer.Option("v1.0", help="Output version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10%% sample"),
):
    """Generate annual crime trends analysis."""
    from analysis.config.schemas.chief import TrendsConfig
    from analysis.config.cli_config import merge_cli_args

    # Load base config from YAML/env
    config = TrendsConfig()

    # Merge CLI arguments
    config = merge_cli_args(config, {
        "start_year": start_year,
        "end_year": end_year,
        "version": version,
        "fast_mode": fast,
    })

    console.print(f"[bold blue]Running trends analysis[/bold blue]")
    console.print(f"  Period: {config.start_year}-{config.end_year}")
    console.print(f"  Version: {config.version}")
    console.print(f"  Fast mode: {config.fast_mode}")

    # Run analysis with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("Loading data...", total=100)

        # Analysis logic here
        progress.update(task, advance=50)
        progress.update(task, description="Processing...")

        progress.update(task, advance=50)

    console.print("[green]:heavy_check_mark:[/green] Analysis complete")
```

**Source:** Context7 - `/fastapi/typer` (nested subcommands, add_typer pattern)

### Pattern 3: Rich Progress Bars for Data Operations

**What:** Use Rich's `Progress` context manager with multiple columns for status, progress bar, percentage, and time remaining.

**When to use:** Any long-running operation (data loading, clustering, forecasting) that takes >1 second.

**Example:**

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.console import Console

console = Console()

def run_analysis_with_progress():
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        # Multiple concurrent tasks
        load_task = progress.add_task("Loading crime data...", total=100)
        clean_task = progress.add_task("Cleaning coordinates...", total=100)
        cluster_task = progress.add_task("Running DBSCAN clustering...", total=100)

        # Update tasks
        progress.update(load_task, advance=100)
        progress.update(clean_task, advance=100)
        progress.update(cluster_task, advance=50)

        # For indeterminate progress
        with console.status("[bold green]Processing analysis..."):
            # Long-running operation here
            pass

        progress.update(cluster_task, advance=50)

# For simple iterable progress
from rich.progress import track

for item in track(data, description="Processing records"):
    process(item)
```

**Source:** Context7 - `/textualize/rich` (Progress, track, status patterns)

### Pattern 4: Module Entry Point with `__main__.py`

**What:** Create `analysis/cli/__main__.py` to enable `python -m analysis.cli` execution.

**When to use:** Main CLI entry point for the entire package.

**Example:**

```python
# analysis/cli/__main__.py
from .main import app

if __name__ == "__main__":
    app()
```

**Usage:**
```bash
python -m analysis.cli --help
python -m analysis.cli chief trends --help
python -m analysis.cli chief trends --start-year 2020 --fast
```

**Source:** Python.org documentation, WebSearch verified (2026)

### Anti-Patterns to Avoid

- **Monolithic CLI file:** Putting all 13 commands in one file creates unmaintainable code. Use separate modules per command group.
- **Hard-coded configuration:** Avoid hard-coding paths and parameters in CLI scripts. Use YAML config files with pydantic validation.
- **No progress feedback:** For data operations taking >1 second, always show progress. Users need feedback for long-running tasks.
- **Mixed config sources without priority:** Clearly define priority: CLI args > env vars > YAML > defaults. Use pydantic-settings source customization.
- **Console scripts for development:** Don't use `[project.scripts]` in pyproject.toml for development tools. Use `python -m` module execution instead.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument parsing | Custom argparse wrappers | typer | Type hints, auto-help, Rich integration |
| Config file loading | Custom YAML parsers | pydantic-settings | Validation, multiple sources, type safety |
| Progress bars | Custom spinners/print statements | Rich Progress | Multi-task, time estimation, beautiful output |
| Environment variable parsing | os.getenv() calls | pydantic-settings | Type conversion, nested structures, prefixing |
| CLI command grouping | Custom subcommand routers | typer.add_typer() | Standard pattern, help generation |

**Key insight:** Custom configuration systems always miss edge cases (type conversion, validation, source priority). pydantic-settings handles YAML/CLI/env var merging with validation out of the box.

## Common Pitfalls

### Pitfall 1: Missing Dependencies

**What goes wrong:** typer, rich, and pydantic-settings are not in the project's dependency lists.

**Why it happens:** These are CLI/dev tools and weren't needed for notebook-based analysis.

**How to avoid:** Add to `requirements-dev.txt` before starting Phase 6. Verify installation with `python -c "import typer, rich, pydantic_settings"`.

**Warning signs:** ImportError when running `python -m analysis.cli`, missing typer in conda environment.

### Pitfall 2: Configuration Priority Confusion

**What goes wrong:** Users expect CLI args to override YAML, but the merge logic is inverted.

**Why it happens:** Incorrect source order in `settings_customise_sources()`.

**How to avoid:** Always return sources in priority order: (init_settings, env_settings, YamlConfigSettingsSource, ...). Test by setting same value in YAML and CLI arg.

**Warning signs:** CLI arguments don't seem to affect output, confusing behavior when both YAML and CLI specify same parameter.

### Pitfall 3: Nested Configuration with Environment Variables

**What goes wrong:** Environment variables like `CRIME_CLUSTERING_EPS_DEGREES` don't map to nested config `clustering.eps_degrees`.

**Why it happens:** Missing `env_nested_delimiter` in SettingsConfigDict.

**How to avoid:** Always set `env_nested_delimiter="__"` for nested configs. Document the env var pattern (e.g., `CRIME__CLUSTERING__EPS_DEGREES`).

**Warning signs:** Environment variables are ignored, only top-level env vars work.

### Pitfall 4: Typer Type Hint Mismatches

**What goes wrong:** Typer can't parse CLI arguments because type hints don't match Pydantic field types.

**Why it happens:** Typer uses type hints for parsing, but pydantic-settings may use different types.

**How to avoid:** Ensure typer function parameter types match pydantic field types exactly. Use `typer.Option[type]` for explicit typing.

**Warning signs:** "Invalid value" errors from typer, type conversion errors.

### Pitfall 5: Progress Bar Context Leaks

**What goes wrong:** Progress bars don't clear or leave output artifacts when exceptions occur.

**Why it happens:** Not using Rich's context managers properly.

**How to avoid:** Always use `with Progress() as progress:` or `with console.status():`. Ensure exceptions are handled inside context.

**Warning signs:** Progress bars remain after script completion, terminal output corrupted.

## Code Examples

### Multi-Source Configuration (YAML + CLI + Env)

```python
# analysis/config/schemas/chief.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class TrendsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="config/chief.yaml",
        env_prefix="CRIME_TRENDS_",
    )

    start_year: int = Field(default=2015, ge=2006, le=2026)
    end_year: int = Field(default=2024, ge=2006, le=2026)
    version: str = "v1.0"
    fast_mode: bool = False
    output_format: str = Field(default="png", pattern="^(png|svg|html|json)$")

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings,
                                   dotenv_settings, file_secret_settings):
        from pydantic_settings import YamlConfigSettingsSource
        return (
            init_settings,  # CLI args (highest)
            env_settings,   # Env vars
            YamlConfigSettingsSource(settings_cls),  # YAML
        )
```

### CLI Command with Rich Progress

```python
# analysis/cli/chief.py
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

app = typer.Typer(help="Chief-level trend analyses")
console = Console()

@app.command()
def trends(
    start_year: int = typer.Option(2015, help="Start year", min=2006, max=2026),
    end_year: int = typer.Option(2024, help="End year", min=2006, max=2026),
    version: str = typer.Option("v1.0", help="Version tag"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode with 10% sample"),
):
    """Generate annual crime trends analysis with progress feedback."""
    from analysis.config.schemas.chief import TrendsConfig
    from analysis.config.cli_config import merge_cli_args

    # Load config and merge CLI args
    config = TrendsConfig()
    config = merge_cli_args(config, {
        "start_year": start_year,
        "end_year": end_year,
        "version": version,
        "fast_mode": fast,
    })

    console.print(f"[bold blue]Annual Trends Analysis[/bold blue]")
    console.print(f"Period: {config.start_year}-{config.end_year}")

    # Progress bar for multi-stage workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        load_task = progress.add_task("Loading data...", total=100)
        # ... data loading logic ...
        progress.update(load_task, advance=100, description="Data loaded")

        analyze_task = progress.add_task("Analyzing trends...", total=100)
        # ... analysis logic ...
        progress.update(analyze_task, advance=100, description="Analysis complete")

    console.print("[green]:heavy_check_mark:[/green] Complete")
    console.print(f"Outputs saved to {config.output_dir}/")
```

### CLI to Config Merge Function

```python
# analysis/config/cli_config.py
from typing import Any, Dict
from pydantic_settings import BaseSettings

def merge_cli_args(settings: BaseSettings, cli_args: Dict[str, Any]) -> BaseSettings:
    """Merge CLI arguments into a pydantic-settings instance.

    CLI arguments should take highest priority. This function creates
    a new settings instance with CLI args applied via init_settings.
    """
    # Filter out None values (not provided via CLI)
    filtered_args = {k: v for k, v in cli_args.items() if v is not None}

    # Create new instance with CLI args (init_settings has highest priority)
    return settings.model_copy(update=filtered_args)
```

### Main CLI Entry Point

```python
# analysis/cli/main.py
import typer

app = typer.Typer(
    name="crime-analysis",
    help="Philadelphia Crime Incidents Analysis CLI",
    no_args_is_help=True,
    add_completion=False,
)

from . import chief, patrol, policy, forecasting

app.add_typer(chief.app, name="chief")
app.add_typer(patrol.app, name="patrol")
app.add_typer(policy.app, name="policy")
app.add_typer(forecasting.app, name="forecasting")

@app.command()
def version():
    """Show CLI and library versions."""
    import typer
    from analysis.config import __version__
    typer.echo(f"Crime Analysis CLI v{__version__}")
    typer.echo(f"  typer: {typer.__version__}")
    typer.echo(f"  rich: {typer.rich.__version__}")

if __name__ == "__main__":
    app()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| argparse | typer | ~2020 | Type hints, auto-help, Rich integration |
| Manual config parsing | pydantic-settings | ~2023 | Validation, multi-source, type safety |
| tqdm | rich.Progress | ~2021 | Multi-task, better UX, status messages |
| setup.py console_scripts | pyproject.toml [project.scripts] | ~2022 | Modern packaging, PEP 621 |
| Monolithic CLI files | Modular typer apps | ~2021 | Better organization, maintainability |

**Deprecated/outdated:**
- **argparse** directly: Replaced by typer for better UX
- **ConfigParser** (INI files): Replaced by YAML/pydantic for structured config
- **python-dotenv alone**: Use pydantic-settings which includes dotenv support
- **Click** for new projects: typer is the modern recommendation (Click is valid but older)

## Open Questions

### Question 1: Separate YAML files per analysis vs. single config file?

**What we know:** 13 analyses have different parameters. Current project uses `phase1_config.yaml`, `phase2_config.yaml`, `phase3_config.yaml`.

**What's unclear:** Should each of the 13 scripts have its own YAML file, or group them by phase (chief.yaml, patrol.yaml, policy.yaml, forecasting.yaml)?

**Recommendation:** Group by phase/area (4 files) to match existing structure. This reduces file count while maintaining logical separation. Individual analysis parameters become nested sections within each file.

**Structure:**
```yaml
# config/chief.yaml
version: "v1.0"
output_dir: "reports"

trends:
  start_year: 2015
  end_year: 2024
  min_complete_months: 12

seasonality:
  summer_months: [6, 7, 8]
  winter_months: [1, 2, 3]
  significance_level: 0.05

covid:
  lockdown_date: "2020-03-01"
  before_years: [2018, 2019]
```

### Question 2: Global shared configuration?

**What we know:** All analyses share some parameters (output_dir, dpi, data paths, logging level).

**What's unclear:** Should there be a `global.yaml` that all configs inherit from?

**Recommendation:** Yes, create `config/global.yaml` for shared parameters. Use pydantic-settings' ability to load multiple YAML files in `settings_customise_sources()`.

**Pattern:**
```python
@classmethod
def settings_customise_sources(cls, settings_cls, init_settings, env_settings, ...):
    return (
        init_settings,
        env_settings,
        YamlConfigSettingsSource(settings_cls, yaml_file="config/global.yaml"),
        YamlConfigSettingsSource(settings_cls, yaml_file="config/chief.yaml"),
    )
```

### Question 3: How to handle 13 CLI entry points - monolithic or modular?

**What we know:** Need 13 commands. WebSearch 2026 confirms modular approach with separate typer instances per command group.

**What's unclear:** Should we have 13 separate command files or group them?

**Recommendation:** Group by area (4 groups: chief, patrol, policy, forecasting) with 3-4 commands each. This matches existing phase structure and reduces file clutter.

**Invocation patterns:**
```bash
python -m analysis.cli chief trends        # 3 commands under chief
python -m analysis.cli chief seasonality
python -m analysis.cli chief covid

python -m analysis.cli patrol hotspots     # 4 commands under patrol
python -m analysis.cli patrol robbery-heatmap
python -m analysis.cli patrol district-severity
python -m analysis.cli patrol census-rates
```

## Sources

### Primary (HIGH confidence)

- **/fastapi/typer** - CLI framework with Rich integration, subcommands, progress bars
- **/pydantic/pydantic-settings** - Multi-source configuration (YamlConfigSettingsSource, settings_customise_sources, CLI parsing)
- **/textualize/rich** - Progress bars, track(), status(), console output formatting
- **Python.org documentation** - `__main__.py` module execution pattern (verified via WebSearch)

### Secondary (MEDIUM confidence)

- **projectrules.ai** - CLI structure best practices 2026 (verified via WebSearch)
- **tiangolo.com (Typer docs)** - Nested subcommands, add_typer() pattern (verified via WebSearch)
- **medium.com** - Pydantic settings YAML loader 2026 (verified via WebSearch)

### Tertiary (LOW confidence)

- **WebSearch results only** - Some CLI entry point patterns (marked for validation)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via Context7 or official docs
- Architecture: HIGH - Patterns verified from Context7 and official documentation
- Pitfalls: MEDIUM - Based on common issues documented in library docs, some project-specific

**Research date:** 2026-02-04
**Valid until:** 2026-03-06 (30 days - stable libraries with infrequent breaking changes)
