# Phase 7: Visualization & Testing - Research

**Researched:** 2026-02-04
**Domain:** Python data visualization, testing frameworks, CLI testing
**Confidence:** HIGH

## Summary

This phase focuses on two critical infrastructure areas: (1) creating a reusable visualization module with multi-format output support, and (2) achieving 90%+ test coverage for all analysis code including CLI scripts. The research confirms that matplotlib, seaborn, and the existing project color palette form the standard visualization stack for this type of work. For CLI testing, typer.testing.CliRunner is the established pattern. For image comparison testing, pytest-mpl is the standard tool.

**Primary recommendation:** Use matplotlib/seaborn with a centralized style module for all visualizations; use pytest with typer.testing.CliRunner for CLI end-to-end tests; create sample data fixtures in tests/conftest.py to avoid loading the full 3.4M-row dataset.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| matplotlib | 3.8+ | Static figure generation (PNG, SVG, PDF) | De facto standard for Python scientific visualization |
| seaborn | 0.13+ | Statistical plotting, consistent styling | Built on matplotlib, provides attractive defaults |
| pytest | 9.0+ | Test framework with fixtures and coverage | Industry standard with rich plugin ecosystem |
| typer.testing.CliRunner | 0.12+ | CLI command testing for typer apps | Official typer testing utility |
| pytest-cov | 7.0+ | Coverage reporting | Standard pytest coverage plugin |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-mpl | latest | Image comparison testing for matplotlib | When verifying figure output consistency |
| plotly | latest | Interactive HTML visualizations | For interactive dashboards (future use) |
| folium | latest | Interactive maps | For geographic visualizations (existing use) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| matplotlib | bokeh, plotly | Web-first vs print-first; matplotlib better for publication-quality static output |
| pytest-mpl | matplotlib.testing.compare | pytest-mpl provides pytest integration; compare requires manual setup |
| typer.testing.CliRunner | subprocess, click.testing | CliRunner is native to typer; alternatives require more setup |

**Installation:**
```bash
# Core visualization (already installed via conda)
conda install matplotlib seaborn

# Testing (already in requirements-dev.txt)
pip install -r requirements-dev.txt

# Optional: image comparison testing
pip install pytest-mpl
```

## Architecture Patterns

### Recommended Project Structure
```
analysis/
├── visualization/
│   ├── __init__.py          # Exports: save_figure, setup_style, COLORS
│   ├── style.py              # matplotlib rcParams, theme configuration
│   ├── plots.py              # Reusable plot functions (line, bar, heatmap, etc.)
│   ├── maps.py               # Geographic visualization utilities
│   └── forecast_plots.py     # Existing forecast-specific plots
tests/
├── conftest.py               # Shared fixtures: sample_data, tmp_output_dir
├── test_classification.py    # Existing: 100% coverage
├── test_temporal.py          # Existing: 100% coverage
├── test_data_loading.py      # Existing: 85% coverage
├── test_cli_chief.py         # NEW: CLI command tests
├── test_cli_patrol.py        # NEW: CLI command tests
├── test_cli_policy.py        # NEW: CLI command tests
├── test_cli_forecasting.py   # NEW: CLI command tests
└── fixtures/
    ├── sample_crime_data.csv # Small representative dataset (~1000 rows)
    └── expected_outputs/     # Baseline figures for comparison
```

### Pattern 1: Multi-Format Figure Saving
**What:** Centralized save function supporting PNG, SVG, HTML, JSON formats
**When to use:** All CLI commands that generate visualizations
**Example:**
```python
# Source: /matplotlib/matplotlib (Context7)
from pathlib import Path
import matplotlib.pyplot as plt
import json

def save_figure(
    fig: plt.Figure,
    output_path: Path,
    output_format: str = "png",
    dpi: int = 300,
) -> None:
    """Save figure in multiple formats.

    Args:
        fig: Matplotlib figure object
        output_path: Base output path (extension will be added)
        output_format: One of 'png', 'svg', 'pdf', 'html', 'json'
        dpi: Resolution for raster formats
    """
    output_path = Path(output_path)

    if output_format in ("png", "pdf", "svg"):
        fig.savefig(output_path.with_suffix(f".{output_format}"),
                   dpi=dpi, bbox_inches='tight', facecolor='white')
    elif output_format == "html":
        # Convert to plotly for interactive HTML
        import plotly.tools as tls
        py_fig = tls.mpl_to_plotly(fig)
        py_fig.write_html(output_path.with_suffix(".html"))
    elif output_format == "json":
        # Save figure metadata and data as JSON
        fig_data = {
            "title": fig.axes[0].get_title(),
            "width": fig.get_size_inches()[0],
            "height": fig.get_size_inches()[1],
        }
        output_path.with_suffix(".json").write_text(json.dumps(fig_data))
```

### Pattern 2: Consistent Styling with Color Palettes
**What:** Centralized style configuration using existing COLORS from analysis.config
**When to use:** All visualization code for consistent branding
**Example:**
```python
# Source: analysis/config.py (existing) + matplotlib docs
from analysis.config import COLORS
import matplotlib.pyplot as plt
import seaborn as sns

def setup_style():
    """Configure matplotlib/seaborn with project style."""
    # Use existing color palette
    color_cycle = [COLORS["Violent"], COLORS["Property"], COLORS["Other"]]
    sns.set_palette(color_cycle)

    # Configure matplotlib rcParams
    plt.rcParams.update({
        'figure.figsize': (12, 6),
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 12,
        'axes.labelweight': 'bold',
        'axes.grid': True,
        'axes.grid.alpha': 0.3,
        'legend.framealpha': 0.9,
        'legend.fontsize': 10,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',
    })

# Call once at module import
setup_style()
```

### Pattern 3: CLI Testing with CliRunner
**What:** Test typer CLI commands using CliRunner from typer.testing
**When to use:** End-to-end testing of all 13 CLI commands
**Example:**
```python
# Source: /websites/typer_tiangolo (Context7)
from typer.testing import CliRunner
from analysis.cli.main import app
from pathlib import Path

runner = CliRunner()

def test_chief_trends_command():
    """Test chief trends CLI command."""
    result = runner.invoke(app, ["chief", "trends", "--start-year", "2020", "--fast"])
    assert result.exit_code == 0
    assert "Annual Trends Analysis" in result.output
    assert "Analysis complete" in result.output

def test_chief_trends_output_files():
    """Test that trends command creates expected output files."""
    result = runner.invoke(app, ["chief", "trends", "--fast", "--version", "test"])
    assert result.exit_code == 0

    # Check output files exist
    output_dir = Path("reports/test/chief")
    assert output_dir.exists()
    assert (output_dir / "annual_trends_report_summary.txt").exists()
```

### Pattern 4: Sample Data Fixtures
**What:** Use pytest fixtures to provide small sample datasets
**When to use:** Unit tests and fast integration tests
**Example:**
```python
# Source: /websites/pytest_en_stable (Context7)
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

@pytest.fixture
def sample_crime_df() -> pd.DataFrame:
    """Create a small sample crime DataFrame for testing.

    This fixture avoids loading the full 3.4M-row dataset.
    Returns 100 rows representing diverse crime types and dates.
    """
    np.random.seed(42)
    return pd.DataFrame({
        "objectid": range(1, 101),
        "dispatch_date": pd.date_range("2020-01-01", periods=100, freq="D"),
        "ucr_general": np.random.choice([100, 200, 300, 500, 600, 700, 800], 100),
        "point_x": np.random.uniform(-75.3, -74.95, 100),
        "point_y": np.random.uniform(39.85, 40.15, 100),
        "dc_dist": np.random.choice(range(1, 24), 100),
    })

@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    return output_dir
```

### Anti-Patterns to Avoid
- **Hard-coding colors in plot functions:** Use centralized COLORS from analysis.config
- **Loading full dataset in tests:** Use sample fixtures for fast tests
- **Testing CLI via subprocess:** Use CliRunner for better error handling and output capture
- **Ignoring figure output in tests:** Use pytest-mpl or file existence checks for visual outputs
- **Scattered style configuration:** Centralize in one visualization module

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image comparison | Custom RMS calculation | pytest-mpl plugin | Handles tolerance, baseline management, diff images |
| CLI output testing | subprocess + stdout parsing | typer.testing.CliRunner | Provides exit_code, output, exception attributes |
| Color cycle management | Manual color lists | seaborn.set_palette() + cycler | Automatic color cycling, consistent styling |
| Figure format conversion | Custom format handlers | matplotlib's built-in format support | PNG, SVG, PDF supported natively |
| Test data generation | Hardcoded DataFrames | pytest fixtures with faker | Isolated, reusable, parameterizable |

**Key insight:** Matplotlib already supports multi-format output via fig.savefig(); pytest already has mature fixture and coverage systems. Building custom solutions adds maintenance burden without benefit.

## Common Pitfalls

### Pitfall 1: Loading Full Dataset in Tests
**What goes wrong:** Tests take 30+ seconds, developers stop running them frequently
**Why it happens:** Copying pattern from production code without considering test performance
**How to avoid:** Create sample fixtures with 100-1000 representative rows
**Warning signs:** Test suite takes > 10 seconds, pytest marked @slow on most tests

### Pitfall 2: Inconsistent Figure Styling
**What goes wrong:** Different figures have different fonts, colors, sizes
**Why it happens:** Each notebook/script sets its own plt.rcParams
**How to avoid:** Centralize style configuration in analysis.visualization.style
**Warning signs:** Style code duplicated across multiple files

### Pitfall 3: Brittle Image Comparison Tests
**What goes wrong:** Tests fail due to minor rendering differences across platforms
**Why it happens:** Pixel-perfect comparison is too strict
**How to avoid:** Use pytest-mpl with tolerance parameter; test file existence/content for non-critical visual tests
**Warning signs:** Image tests fail only on CI or specific OS

### Pitfall 4: CLI Tests Missing Output File Checks
**What goes wrong:** CLI exits successfully but no files created
**Why it happens:** Tests only check exit_code, not side effects
**How to avoid:** Assert expected files exist and contain expected content
**Warning signs:** Empty reports/ directories after test runs

### Pitfall 5: Coverage Gaps in Error Paths
**What goes wrong:** 90% coverage target missed due to untested exception handling
**Why it happens:** Focus on happy path, error paths not exercised
**How to avoid:** Write tests for invalid inputs, missing files, permission errors
**Warning signs:** try/except blocks with no corresponding tests

## Code Examples

Verified patterns from official sources:

### Multi-Format Save with DPI Control
```python
# Source: /matplotlib/matplotlib (Context7)
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Save multiple formats from same figure
plt.savefig('figure.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('figure.svg', format='svg', bbox_inches='tight')
plt.savefig('figure.pdf', format='pdf', bbox_inches='tight')
```

### CliRunner for Typer CLI Testing
```python
# Source: /websites/typer_tiangolo (Context7)
from typer.testing import CliRunner
from analysis.cli.main import app

runner = CliRunner()

def test_command_with_args():
    result = runner.invoke(app, ["chief", "trends", "--start-year", "2020"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

### Pytest Fixture for Sample Data
```python
# Source: /websites/pytest_en_stable (Context7)
import pytest

@pytest.fixture
def sample_data():
    """Fixture providing isolated data for each test."""
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### Shared Fixtures via conftest.py
```python
# Source: /websites/pytest_en_stable (Context7)
# tests/conftest.py
import pytest

@pytest.fixture
def shared_resource():
    """Available to all tests in this directory."""
    return "shared"

# tests/test_something.py
def test_uses_shared(shared_resource):
    assert shared_resource == "shared"  # No import needed
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hard-coded DPI in each savefig() | Global dpi in plt.rcParams + local override | matplotlib 3.0+ | Easier to maintain publication quality |
| subprocess for CLI tests | typer.testing.CliRunner | typer 0.12+ | Better exception handling, output capture |
| Manual image comparison | pytest-mpl with tolerance | 2019+ | Platform-tolerant image regression testing |
| Per-file style configuration | Centralized style module | Industry standard | Consistent branding, easier updates |

**Deprecated/outdated:**
- **plt.style.use('seaborn-darkgrid')**: Changed to 'seaborn-v0_8-darkgrid' in seaborn 0.12
- **string arguments for aggregation**: 'M'/'Y' deprecated, use 'ME'/'YE' (already handled)
- **pytest.config.warnoldest**: Moved to pytest.ini warnings filter

## Open Questions

1. **HTML output format for figures:**
   - What we know: matplotlib doesn't natively save HTML
   - What's unclear: Whether to use plotly conversion or simple mpld3
   - Recommendation: Support PNG/SVG/PDF initially; defer HTML until use case emerges

2. **Image regression testing:**
   - What we know: pytest-mpl is standard for matplotlib figure testing
   - What's unclear: Whether to store baseline images in repo or generate on first run
   - Recommendation: Start with file existence tests; add image regression if visual correctness becomes an issue

3. **CLI test data isolation:**
   - What we know: Need to test 13 commands without hitting full dataset
   - What's unclear: Whether to mock load_crime_data or use --fast flag universally
   - Recommendation: Use --fast flag in all CLI tests; creates smaller but still valid test runs

## Sources

### Primary (HIGH confidence)
- /matplotlib/matplotlib - Multi-format figure saving, DPI configuration, style sheets
- /websites/pytest_en_stable - Fixture usage, conftest.py patterns, test configuration
- /websites/typer_tiangolo - CliRunner usage for testing typer CLI apps
- analysis/config.py - Existing COLORS constant (Violent: #E63946, Property: #457B9D, Other: #A8DADC)
- analysis/visualization/forecast_plots.py - Existing visualization pattern (returns Figure objects)
- tests/test_classification.py - Existing test patterns (parametrized tests, clear organization)
- pyproject.toml - Existing pytest configuration with 90% coverage target

### Secondary (MEDIUM confidence)
- WebSearch "pytest test typer CLI command CliRunner 2026" - Verified CliRunner usage patterns
- WebSearch "matplotlib pytest test figure output image comparison 2026" - Verified pytest-mpl is standard
- WebSearch "pytest fixtures sample data test helpers conftest.py 2026" - Verified fixture best practices

### Tertiary (LOW confidence)
- WebSearch "seaborn matplotlib consistent color palette project theme 2026" - Generic color palette example (not directly applicable as project already has COLORS defined)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Matplotlib, seaborn, pytest are industry standards; typer.testing.CliRunner is official typer testing method
- Architecture: HIGH - Patterns verified from official documentation (Context7) and existing codebase patterns
- Pitfalls: HIGH - Based on common issues seen in data science projects and verified against documentation
- Image testing: MEDIUM - pytest-mpl is standard but usage patterns vary by project

**Research date:** 2026-02-04
**Valid until:** 2026-03-06 (30 days - stable domain)
