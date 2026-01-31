# Coding Conventions

**Analysis Date:** 2026-01-30

## Naming Patterns

**Files:**
- Snake_case for all Python files and directory names
- Descriptive names that match their purpose:
  - `config.py` - Centralized configuration constants
  - `utils.py` - Shared utility functions
  - `data_quality.py` - Data quality assessment module
  - `temporal_analysis.py` - Time-based analysis
  - `spatial_analysis.py` - Geographic analysis
  - `categorical_analysis.py` - Category-based analysis
  - `cross_analysis.py` - Multi-dimensional analysis
- Report generators use prefix pattern: `06_`, `07_`, etc. for order indication

**Functions:**
- Snake_case for all function names
- Clear, descriptive names that indicate action or purpose:
  - `analyze_*()` - Main analysis functions that return results dicts
  - `load_data()` - Data loading utility
  - `validate_coordinates()` - Data validation
  - `extract_temporal_features()` - Feature engineering
  - `classify_*()` - Classification functions
  - `get_*_summary()` - Summary statistics generation
- Verbs for functions that perform actions
- Nouns for functions that return data structures

**Variables:**
- Snake_case for all variable names
- Descriptive names that clearly indicate purpose:
  - `df` - Standard for pandas DataFrames
  - `fig`, `ax` - For matplotlib figures and axes
  - `results` - For dictionaries containing analysis outputs
  - `sample_size` - For numeric sampling parameters
  - `missing_threshold` - For configuration values
  - `valid_coord` - For boolean flags
- Single-letter variables only for mathematical contexts (e.g., `x`, `y`, `z` in polynomial fitting)

**Constants:**
- UPPER_SNAKE_CASE for all constants
- Grouped by purpose with clear separation:
  - `PROJECT_ROOT`, `DATA_DIR`, `REPORTS_DIR` - Path constants
  - `FIGURE_SIZES`, `COLORS` - Configuration constants
  - `VIOLENT_CRIME_UCR`, `PROPERTY_CRIME_UCR` - Classification constants
  - `DBSCAN_CONFIG`, `CLUSTERING_SAMPLE_SIZE` - Analysis parameters

## Code Style

**Formatting:**
- Black code formatter is used (inferred from consistent formatting)
- Line length: Soft limit at 88 characters (Black standard)
- Indentation: 4 spaces
- Trailing commas in multiline structures
- Single quotes for string literals (unless double quotes contain single quotes)

**Linting:**
- No explicit linting configuration found
- Code follows PEP 8 style guide
- Docstrings follow Google style format

## Import Organization

**Order:**
1. Standard library imports (alphabetical)
2. Third-party imports (alphabetical)
3. Local imports (absolute paths, alphabetical)

**Pattern:**
```python
# Standard library
import io
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Local imports
from analysis.config import COLORS, FIGURE_SIZES, PROJECT_ROOT
from analysis.utils import load_data, validate_coordinates, extract_temporal_features
```

**Path Aliases:**
- No path aliases configured
- All imports use absolute paths: `from analysis.utils import ...`
- No relative imports within the analysis package

## Error Handling

**Patterns:**
- Explicit error handling with try-except blocks for file operations
- Custom exceptions not defined using standard Python exceptions
- Validation before operations to prevent errors

**Examples:**
```python
# File existence check
if not path.exists():
    raise FileNotFoundError(f"Data file not found: {path}")

# Data validation
if "point_x" not in df.columns or "point_y" not in df.columns:
    raise ValueError("DataFrame missing required coordinate columns")

# Coordinate validation
valid_mask = (
    df["point_x"].notna()
    & df["point_y"].notna()
    & (df["point_x"] >= LON_MIN)
    & (df["point_x"] <= LON_MAX)
)
```

## Comments

**When to Comment:**
- For complex algorithms (e.g., DBSCAN clustering)
- For business logic explanations (e.g., UCR classification)
- For data processing steps with non-obvious transformations
- For configuration constants with rationale

**Docstring/TSDoc:**
- All public functions have docstrings
- Google style format for docstrings
- Args and Returns documented with types
- Examples provided for complex functions

**Comment Patterns:**
```python
def validate_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and flag coordinate data.

    Adds columns indicating whether coordinates are valid.

    Args:
        df: DataFrame with point_x (longitude) and point_y (latitude) columns.

    Returns:
        DataFrame with added coordinate validation columns.
    """
    # Implementation with inline comments for complex logic
```

## Function Design

**Size:**
- Functions typically 20-100 lines
- Split logical sections with comment separators
- Single responsibility principle applied
- Long functions broken into smaller helper functions

**Parameters:**
- Default values provided for optional parameters
- Type hints used for all parameters and returns
- Parameter validation at function start
- Keyword arguments preferred for boolean flags

**Return Values:**
- Consistent return types within modules
- Analysis functions return dict with standardized structure
- Helper functions return processed data
- Void functions only for side effects (e.g., plotting)

## Module Design

**Exports:**
- Explicit exports not used (no __all__ defined)
- All public functions imported directly
- No internal underscore-prefixed functions (all functions are public)

**Barrel Files:**
- No barrel files (__init__.py is empty)
- Direct imports from specific modules

**Module Organization:**
- Each analysis module has one main analyze_*() function
- Shared utilities in utils.py
- Configuration centralized in config.py
- Report generators are separate from analysis modules

## Type Hints

**Usage:**
- Consistent use of type hints throughout codebase
- Union types used for optional parameters: `int | None`
- Collection types specified: `list`, `dict`, `tuple`
- DataFrame types: `pd.DataFrame`
- NumPy types: `np.ndarray`

**Pattern:**
```python
def dbscan_clustering(
    df: pd.DataFrame,
    eps_meters: int | None = None,
    min_samples: int | None = None,
    sample_size: int | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
```

---

*Convention analysis: 2026-01-30*
```