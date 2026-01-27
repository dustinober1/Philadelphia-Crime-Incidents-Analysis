# Coding Conventions

**Analysis Date:** 2026-01-27

## Language & Runtime

**Primary:**
- Python 3.x - Standard Python conventions apply

## Naming Patterns

**Variables:**
- snake_case for variable names: `crime_data`, `incident_count`

**Functions:**
- snake_case for function names: `load_crime_data()`, `calculate_statistics()`

**Constants:**
- UPPER_CASE for constants: `MAX_INCIDENTS`, `DEFAULT_RADIUS`

**Classes:**
- PascalCase for classes: `CrimeAnalyzer`, `IncidentProcessor`

## Code Style

**Formatting:**
- PEP 8 compliant formatting
- 4 space indentation
- Line length: 88-120 characters

**Linting:**
- Not specified - likely follows standard Python practices

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports
3. Local application imports

**Example:**
```python
import os
import json
from datetime import datetime

import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from sklearn.cluster import KMeans

from .utils import helper_function
```

## Documentation

**Docstrings:**
- Google-style or NumPy-style docstrings preferred
- Module, class, and function docstrings for public APIs

**Comments:**
- Inline comments for complex logic
- Descriptive comments explaining data processing steps

## Data Science Specific Conventions

**DataFrames:**
- Use descriptive column names
- Consistent naming for geographic columns (lat, lon, geometry)
- Proper data types (datetime for timestamps, categorical for types)

**Plotting:**
- Consistent figure sizing and styling
- Meaningful titles and labels
- Color schemes appropriate for data visualization

## Error Handling

**Patterns:**
- Try-except blocks for file operations and network requests
- Proper exception types (ValueError, FileNotFoundError, etc.)
- Graceful degradation when optional features unavailable

## Logging

**Approach:**
- Standard logging module usage
- Appropriate log levels (INFO for progress, WARNING for issues, ERROR for failures)

## File Structure (Expected)

**Notebooks:**
- Jupyter notebooks following logical progression (data load → clean → analyze → visualize)

**Scripts:**
- Modular code split into reusable functions
- Clear separation between data loading, processing, and visualization

## Testing Conventions (Expected)

**Style:**
- pytest framework likely used
- Test functions prefixed with `test_`
- Descriptive test names indicating what is being tested

---

*Convention analysis: 2026-01-27*