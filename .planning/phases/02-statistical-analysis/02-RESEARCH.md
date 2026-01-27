# Phase 02: Statistical Analysis - Research

**Researched:** 2026-01-27
**Domain:** Statistical Analysis (Pandas/PyArrow)
**Confidence:** HIGH

## Summary

This phase extends the existing `DataProfiler` class to support specific statistical requirements (STAT-01 to STAT-05). The architecture follows the established "Library + Runner" pattern: the `DataProfiler` provides generic statistical methods, while a new runner script applies these methods to the specific Philly Crime domain (injecting column names like `dispatch_date_time` and `text_general_code`).

**Primary recommendation:** Extend `DataProfiler` with generic time-series and bivariate analysis methods; keep domain-specific column logic in the runner script.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.0+ | Data manipulation | Project standard, defined in Phase 1 |
| pyarrow | Latest | Backend engine | Performance, efficient string/types |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | Latest | Numeric ops | Underlying calculations (if needed) |

**Installation:**
(Already installed via `requirements.txt` in Phase 1)

## Architecture Patterns

### Recommended Pattern: Generic Library, Domain Runner

**1. Library (`src/analysis/profiler.py`):**
Extend `DataProfiler` with generic methods. Do NOT hardcode "crime" column names here.
```python
class DataProfiler:
    # Existing methods...
    
    def analyze_time_series(self, date_col: str, freq: str = "D") -> pd.Series:
        """Groups by a date column at a given frequency."""
        pass

    def analyze_bivariate(self, col1: str, col2: str) -> pd.DataFrame:
        """Creates a cross-tabulation of two columns."""
        pass
```

**2. Runner (`scripts/analysis/calculate_statistics.py`):**
Injects domain knowledge.
```python
def main():
    df = load_crime_data()
    profiler = DataProfiler(df)
    
    # STAT-02: Frequencies by type
    print(profiler.check_categorical_breakdown(col="text_general_code"))
    
    # STAT-04: Temporal patterns
    print(profiler.analyze_time_series(date_col="dispatch_date_time", freq="M"))
```

### Anti-Patterns to Avoid
- **Hardcoding Column Names in Class:** Don't put `text_general_code` inside `DataProfiler`. Keep it generic.
- **Printing inside Class:** `DataProfiler` should return DataFrames/Dicts. The Runner script handles `print()`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Frequencies | Manual loops | `df[col].value_counts()` | Optimized C/PyArrow implementation |
| Correlations | Custom math | `df.corr()` | Handles vectorized covariance |
| Time Grouping | String parsing | `df.groupby(pd.Grouper(key=col, freq=freq))` | Handles calendars, leap years, missing dates |
| Crosstabs | Pivot logic | `pd.crosstab(df[a], df[b])` | Single line, highly optimized |

## Common Pitfalls

### Pitfall 1: Date Column Types
**What goes wrong:** `dispatch_date_time` might be loaded as a string (object) or string[pyarrow], not datetime.
**Why it happens:** Parquet metadata might not preserve the exact pandas flavor, or the original ETL saved it as string.
**How to avoid:** In the runner script, strictly enforce conversion before profiling:
```python
df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])
```

### Pitfall 2: Correlation on Categoricals
**What goes wrong:** Calling `corr()` on the whole DF returns an empty matrix or error if no numeric columns exist.
**Why:** Pearson correlation requires numbers. STAT-05 asks for "correlations between different variables" which might imply Categorical vs Categorical (e.g. District vs Crime Type).
**How to avoid:** 
- Use `corr()` for numeric-numeric (Lat/Lon?).
- Use `crosstab` (frequency matrix) for categorical-categorical interactions (this satisfies "patterns" analysis).

### Pitfall 3: Console Output Overload
**What goes wrong:** Printing a DataFrame with 500 rows floods the terminal.
**How to avoid:** Always use `.head()`, `.to_markdown()`, or specifically formatting helper functions in the runner script.

## Code Examples

### Temporal Analysis (STAT-04)
```python
# In DataProfiler
def analyze_temporal_patterns(self, date_col: str, freq: str = 'ME') -> pd.DataFrame:
    """
    Analyzes data over time.
    freq: 'D' (Daily), 'W' (Weekly), 'ME' (Monthly End), 'YE' (Yearly End)
    """
    # Ensure datetime (or rely on caller)
    return self.df.groupby(pd.Grouper(key=date_col, freq=freq)).size().to_frame("count")

# In Runner
# Weekly patterns
weekly_stats = profiler.analyze_temporal_patterns("dispatch_date_time", "W")
```

### Bivariate Frequencies (STAT-02/05)
```python
# In DataProfiler
def analyze_correlation_matrix(self) -> pd.DataFrame:
    """Numeric correlations"""
    return self.df.select_dtypes("number").corr()

def analyze_category_crosstab(self, col1: str, col2: str) -> pd.DataFrame:
    """Frequency of Col1 broken down by Col2"""
    return pd.crosstab(self.df[col1], self.df[col2])
```

## Open Questions

1.  **Crime Category Definition:** Are we using `text_general_code` (broad) or `text_general_code` (granular)? 
    *   *Recommendation:* Runner script should pick `text_general_code` for high-level stats, maybe enable drilling down later.

## Sources

### Primary (HIGH confidence)
- **Pandas 2.0 Docs**: `pd.Grouper`, `value_counts`, `corr`, `crosstab`.
- **Project Context**: `src/analysis/profiler.py` structure.

### Secondary (MEDIUM confidence)
- **PyArrow Backend**: Known compatibility with standard Pandas accessors (`.dt` accessor works on `timestamp[ns][pyarrow]`).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (Pandas is definitive)
- Architecture: HIGH (Follows Phase 1 pattern)
- Pitfalls: MEDIUM (Data-dependent)

**Research date:** 2026-01-27
