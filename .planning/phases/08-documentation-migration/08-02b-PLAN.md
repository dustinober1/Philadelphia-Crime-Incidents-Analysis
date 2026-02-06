---
phase: 08-documentation-migration
plan: 02b
type: execute
wave: 1
depends_on: []
files_modified:
  - analysis/config/__init__.py
  - analysis/config/schemas/__init__.py
  - analysis/config/schemas/chief.py
  - analysis/config/schemas/patrol.py
  - analysis/config/schemas/policy.py
  - analysis/config/schemas/forecasting.py
  - analysis/cli/__init__.py
  - analysis/cli/main.py
  - analysis/cli/chief.py
  - analysis/cli/patrol.py
  - analysis/cli/policy.py
  - analysis/cli/forecasting.py
  - analysis/visualization/__init__.py
  - analysis/visualization/style.py
  - analysis/visualization/helpers.py
  - analysis/visualization/plots.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "All config, CLI, and visualization modules have Google-style docstrings"
    - "Docstrings explain purpose, usage, and key exports"
    - "Docstrings follow consistent formatting pattern"
    - "Public functions have type hints and docstrings with Args/Returns/Raises"
  artifacts:
    - path: "analysis/config/__init__.py"
      provides: "Config package docstring"
      contains: "Configuration management"
    - path: "analysis/cli/__init__.py"
      provides: "CLI package docstring"
      contains: "Command-line interface"
    - path: "analysis/visualization/__init__.py"
      provides: "Visualization package docstring"
      contains: "publication-quality|figures"
  key_links:
    - from: "Module docstrings"
      to: "CLAUDE.md"
      via: "Cross-reference documentation"
      pattern: "See CLAUDE.md for usage"

<objective>
Add comprehensive module docstrings to config, CLI, and visualization modules

**Purpose:** Improve code discoverability by adding Google-style docstrings to configuration, CLI, and visualization modules. Docstrings explain module purpose, key exports, and usage patterns.

**Output:** All config, CLI, and visualization modules have module-level docstrings following Google style with Args/Returns/Raises for public functions.

</objective>

<execution_context>
@/Users/dustinober/.claude/get-shit-done/workflows/execute-plan.md
@/Users/dustinober/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/08-documentation-migration/08-RESEARCH.md

# Existing modules to document
@analysis/config/__init__.py
@analysis/cli/__init__.py
@analysis/visualization/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add docstrings to config and CLI modules</name>
  <files>analysis/config/__init__.py analysis/config/schemas/__init__.py analysis/cli/__init__.py analysis/cli/main.py</files>
  <action>
    Add Google-style module docstrings to config and CLI modules:

    **analysis/config/__init__.py:**
    ```python
    """Configuration management for analysis scripts.

    This package provides Pydantic-based configuration management with
    multi-source loading (CLI args > env vars > YAML > defaults).

    Configuration hierarchy:
    1. CLI arguments (highest priority)
    2. Environment variables (CRIME_* prefix)
    3. YAML config files (config/{group}.yaml)
    4. Pydantic defaults (lowest priority)

    Schemas:
        chief: Chief-level analysis config (trends, seasonality, covid)
        patrol: Patrol analysis config (hotspots, robbery, etc.)
        policy: Policy analysis config (retail theft, vehicle crimes, etc.)
        forecasting: Forecasting config (time series, classification)
    """
    ```

    **analysis/config/schemas/__init__.py:**
    ```python
    """Configuration schemas for analysis groups.

    This package contains Pydantic Settings models for configuring analysis
    scripts, with support for YAML files, environment variables, and CLI overrides.

    Schemas:
        BaseConfig: Shared configuration (data paths, output directories)
        ChiefConfig: Chief-level analysis configuration
        PatrolConfig: Patrol analysis configuration
        PolicyConfig: Policy analysis configuration
        ForecastingConfig: Forecasting analysis configuration
    """
    ```

    **analysis/cli/__init__.py:**
    ```python
    """Command-line interface for crime incident analysis.

    This package provides typer-based CLI commands for running crime analysis
    scripts with Rich progress bars and configurable output.

    Entry point: python -m analysis.cli

    Command groups:
        chief: Chief-level analyses (trends, seasonality, covid)
        patrol: Patrol analyses (hotspots, robbery-heatmap, etc.)
        policy: Policy analyses (retail-theft, vehicle-crimes, etc.)
        forecasting: Forecasting analyses (time-series, classification)

    Common arguments:
        --fast: Fast mode with 10% sample (for testing)
        --version: Output version tag (default: v1.0)
        --output-format: Figure format (png, svg, pdf)
    """
    ```

    **analysis/cli/main.py:**
    ```python
    """CLI entry point using typer.

    This module defines the main typer app and command groups for the
    crime analysis CLI system.

    Usage:
        python -m analysis.cli --help
        python -m analysis.cli chief trends --help
        python -m analysis.cli chief trends --fast

    Architecture:
    - typer.App for command registration
    - Rich for console output (progress bars, tables, panels)
    - CliRunner for testing (typer.testing)
    """
    ```
  </action>
  <verify>python -c "import analysis.config; print(analysis.config.__doc__)" && python -c "import analysis.cli; print(analysis.cli.__doc__)"</verify>
  <done>All config and CLI modules have Google-style module docstrings</done>
</task>

<task type="auto">
  <name>Task 2: Add docstrings to CLI command modules</name>
  <files>analysis/cli/chief.py analysis/cli/patrol.py analysis/cli/policy.py analysis/cli/forecasting.py</files>
  <action>
    Add Google-style module docstrings to all CLI command group modules. Follow this pattern:

    **analysis/cli/chief.py:**
    ```python
    """Chief-level analysis commands.

    This module provides CLI commands for high-level trend analysis,
    addressing questions like "Is Philadelphia getting safer?" and
    "How did COVID change the crime landscape?"

    Commands:
        trends: Annual crime trends analysis
        seasonality: Seasonal patterns and summer spike analysis
        covid: Pre/during/post COVID comparison

    All commands support --fast mode for quick testing with 10% data sample.
    """
    ```

    **analysis/cli/patrol.py:**
    ```python
    """Patrol analysis commands.

    This module provides CLI commands for spatial and temporal hotspot
    analysis to support patrol deployment decisions.

    Commands:
        hotspots: Spatial clustering of crime incidents
        robbery-heatmap: Temporal heatmap for robbery incidents
        district-severity: Per-district severity scoring
        census-rates: Crime rates per census tract (population-normalized)
    """
    ```

    **analysis/cli/policy.py:**
    ```python
    """Policy analysis commands.

    This module provides CLI commands for policy-focused deep dives,
    measuring impacts on specific crime types.

    Commands:
        retail-theft: Retail theft trend analysis
        vehicle-crimes: Vehicle crime corridor analysis
        composition: Crime composition breakdown
        events: Event-day impact analysis
    """
    ```

    **analysis/cli/forecasting.py:**
    ```python
    """Forecasting and prediction commands.

    This module provides CLI commands for time series forecasting and
    violence classification to support operational alerts.

    Commands:
        time-series: Prophet-based time series forecasting
        classification: Violence classification with feature importance

    Note: time-series command requires prophet package (optional dependency).
    """
    ```
  </action>
  <verify>grep -q "Chief-level analysis commands" analysis/cli/chief.py && grep -q "Patrol analysis commands" analysis/cli/patrol.py</verify>
  <done>All CLI command group modules have Google-style module docstrings</done>
</task>

<task type="auto">
  <name>Task 3: Add docstrings to visualization modules</name>
  <files>analysis/visualization/__init__.py analysis/visualization/style.py analysis/visualization/helpers.py analysis/visualization/plots.py</files>
  <action>
    Add Google-style module docstrings to all visualization modules:

    **analysis/visualization/__init__.py:**
    ```python
    """Publication-quality visualization utilities.

    This package provides reusable visualization functions with consistent
    styling, multi-format output (PNG, SVG, PDF), and memory-efficient
    figure handling.

    Modules:
        style: Matplotlib style configuration (color palette, fonts, etc.)
        helpers: Figure saving with plt.close() to prevent memory leaks
        plots: Reusable plot types (line, bar, heatmap, scatter)

    Example:
        >>> from analysis.visualization import setup_style, plot_line, save_figure
        >>> setup_style()
        >>> fig, ax = plot_line(df, x='year', y='count')
        >>> save_figure(fig, 'output.png', output_format='png')
        >>> plt.close(fig)
    """
    ```

    **analysis/visualization/style.py:**
    ```python
    """Matplotlib style configuration.

    This module provides functions for setting up consistent matplotlib
    styling across all analysis scripts.

    Functions:
        setup_style: Configure matplotlib rcParams with project style

    Style configuration:
    - Color palette: COLORS from analysis.config
    - Font: sans-serif (Arial, Helvetica, DejaVu Sans)
    - Figure size: (10, 6) default
    - DPI: 300 for publication quality
    """
    ```

    **analysis/visualization/helpers.py:**
    ```python
    """Figure saving helpers with memory leak prevention.

    This module provides utilities for saving figures in multiple formats
    and ensuring proper cleanup to prevent matplotlib memory leaks.

    Functions:
        save_figure: Save figure to file with format handling
        get_output_path: Construct output path with versioning

    Important: Always call plt.close(fig) after save_figure() to prevent
    memory leaks in long-running scripts and tests.
    """
    ```

    **analysis/visualization/plots.py:**
    ```python
    """Reusable plot types for crime analysis.

    This module provides high-level plotting functions for common chart
    types used across all analysis scripts.

    Functions:
        plot_line: Line chart for time series
        plot_bar: Bar chart for categorical comparisons
        plot_heatmap: Heatmap for temporal/spatial patterns
        plot_scatter: Scatter plot for correlations

    All plots use project color palette (COLORS) and consistent styling.
    """
    ```
  </action>
  <verify>python -c "import analysis.visualization; print(analysis.visualization.__doc__)" && grep -q "Publication-quality" analysis/visualization/__init__.py</verify>
  <done>All visualization modules have Google-style module docstrings</done>
</task>

</tasks>

<verification>
After completion, verify:
1. All config, CLI, and visualization modules have module-level docstrings
2. Docstrings follow Google style (Args, Returns, Raises for functions)
3. Docstrings explain module purpose, key exports, and usage examples
4. `python -c "import MODULE; print(MODULE.__doc__)"` prints formatted docstring
5. mypy shows no docstring-related errors
</verification>

<success_criteria>
1. Developer can `import analysis.config` and see module documentation
2. Docstrings enable IDE autocomplete tooltips with usage examples
3. Consistent formatting across all config, CLI, and visualization modules
4. All docstrings pass pydocstyle or similar linter (if available)
</success_criteria>

<output>
After completion, create `.planning/phases/08-documentation-migration/08-02b-SUMMARY.md` documenting:
- Number of modules documented (expected: 12 modules)
- Module categories (config: 2, cli: 5, visualization: 4, schemas: 4)
- Total lines of documentation added
- Any functions missing docstrings (if any)
</output>
