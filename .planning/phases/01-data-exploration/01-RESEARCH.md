# Phase 01: Data Exploration - Research

**Researched:** 2026-01-27
**Domain:** Python Data Analysis / Pandas
**Confidence:** HIGH

## Summary

Phase 1 focuses on creating a robust, reusable foundation for inspecting the crime incidents dataset. The standard approach involves a "Library + Runner" architecture where core analysis logic resides in `src/` (as reusable classes/functions) and is executed by a script in `scripts/`.

The primary technical recommendation is to leverage **Pandas 2.0+ features**, specifically the PyArrow backend, for significant memory and performance gains when handling the Parquet input. The exploration logic should be encapsulated in a `DataProfiler` class that systematically performs quality, type, outlier, and relationship checks.

**Primary recommendation:** Use `pandas` with `engine="pyarrow"` and `dtype_backend="pyarrow"` for loading, encapsulated in a `DataProfiler` class.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pandas** | 2.3.3 | Data manipulation | Industry standard; v2.0+ offers PyArrow backed types for efficiency. |
| **pyarrow** | 21.0.0 | Parquet engine | Required backend for fast Parquet I/O and nullable data types. |
| **configparser** | (Std Lib) | Configuration | Standard Python library for reading `.ini` files. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pathlib** | (Std Lib) | Path handling | Modern replacement for `os.path`; safer cross-platform path manipulation. |
| **numpy** | 2.3.5 | Numeric ops | Underlying numerical operations (implied by Pandas). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| **Custom Scripts** | `ydata-profiling` | Automates everything but offers less control/understanding for the "User can understand" requirement. |
| **Pandas default** | `polars` | Polars is faster but Pandas is already in the project stack and more widely known for this team. |

## Architecture Patterns

### Recommended Project Structure
```
.
├── config.ini          # Existing config
├── scripts/
│   └── explore_data.py # Runner script (entry point)
└── src/
    ├── analysis/
    │   ├── __init__.py
    │   └── profiler.py # Core DataProfiler class
    └── utils/
        ├── __init__.py
        └── config_loader.py # Helper to read config.ini safely
```

### Pattern 1: Data Profiler Class
**What:** Encapsulate the DataFrame and analysis methods in a class.
**When to use:** When you need to run a sequence of checks (Nulls, Types, Outliers) on the same dataset.
**Example:**
```python
# src/analysis/profiler.py
import pandas as pd

class DataProfiler:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def check_quality(self):
        """Prints missing values and duplicates."""
        print("Missing Values:\n", self.df.isnull().sum())
        print("Duplicates:", self.df.duplicated().sum())
```

### Pattern 2: PyArrow Backend Loading
**What:** Loading Parquet with PyArrow-backed types.
**When to use:** Always for Parquet files in Pandas 2.0+, especially for string-heavy data.
**Example:**
```python
df = pd.read_parquet("data.parquet", engine="pyarrow", dtype_backend="pyarrow")
```

### Anti-Patterns to Avoid
- **Hardcoded Paths:** Never use `pd.read_parquet("data/raw/file.parquet")`. Use `config.ini` + `pathlib`.
- **Global Script Logic:** Don't put all analysis logic in the `if __name__ == "__main__":` block. Move it to functions/classes in `src/`.
- **Manual Type Casting:** Avoid `df['col'] = df['col'].astype('string')` immediately after load; let `read_parquet` handle it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Config Parsing** | Custom line-reading of config | `configparser` | Handles comments, sections, and type conversion reliably. |
| **Outlier Math** | Manual loops/ifs for IQR | `df.quantile(0.25)` | Vectorized, faster, and less error-prone. |
| **File Paths** | String concatenation (`/` vs `\`) | `pathlib.Path` | Handles OS differences and path joining safely. |

## Common Pitfalls

### Pitfall 1: Relative Path Confusion
**What goes wrong:** `FileNotFoundError` when running scripts from different directories.
**Why it happens:** Relative paths in `config.ini` are relative to the *working directory*, not the config file.
**How to avoid:** Define a `PROJECT_ROOT` constant in a utility module using `Path(__file__)` and resolve config paths against it.

### Pitfall 2: Memory Bloat
**What goes wrong:** Script crashes or slows down on large Parquet files.
**Why it happens:** Default Pandas types (object) for strings are memory inefficient.
**How to avoid:** Use `dtype_backend="pyarrow"` in `read_parquet`.

### Pitfall 3: Verbose Output Overload
**What goes wrong:** Printing `df.to_string()` dumps millions of rows.
**Why it happens:** Uncontrolled printing of large dataframes.
**How to avoid:** Use `df.head()`, `df.info()`, or summarize counts before printing.

## Code Examples

### Loading with Config and PyArrow
```python
# src/utils/loader.py
import configparser
from pathlib import Path
import pandas as pd

def load_data() -> pd.DataFrame:
    # 1. Setup paths
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / "config.ini"
    
    # 2. Read Config
    config = configparser.ConfigParser()
    config.read(config_path)
    relative_path = config["data_paths"]["raw_data_path"]
    
    # 3. Load Parquet
    file_path = project_root / relative_path / "incidents.parquet"
    return pd.read_parquet(
        file_path, 
        engine="pyarrow", 
        dtype_backend="pyarrow"
    )
```

### Outlier Detection (IQR)
```python
def detect_outliers(df: pd.DataFrame, column: str):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return len(outliers), outliers.head()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `dtype=object` | `dtype="string[pyarrow]"` | Pandas 2.0 | massive memory reduction for text data |
| `os.path.join` | `pathlib.Path` / `/` operator | Python 3.4+ | Cleaner, safer path manipulation |

## Sources

### Primary (HIGH confidence)
- **Pandas Docs**: `read_parquet` API reference (verified `dtype_backend` param).
- **Project Context**: Verified `config.ini` and `requirements.txt`.

### Secondary (MEDIUM confidence)
- **General Python Practices**: Standard library usage for `configparser` and `pathlib`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - `pandas` and `pyarrow` are installed and standard.
- Architecture: HIGH - Matches user constraint of "Library + Runner".
- Pitfalls: HIGH - Common issues with file paths and memory in this specific stack.

**Research date:** 2026-01-27
**Valid until:** 2026-06-01 (Pandas 3.0 may change defaults, but 2.3 is stable)
