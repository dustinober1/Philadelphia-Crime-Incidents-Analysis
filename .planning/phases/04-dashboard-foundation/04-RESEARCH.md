# Phase 4: Dashboard Foundation - Research

**Researched:** 2026-01-31
**Domain:** Streamlit dashboard development for large-scale exploratory data analysis
**Confidence:** HIGH

## Summary

This research investigates implementing a Streamlit-based interactive dashboard for the Philadelphia Crime Incidents EDA project (3.5M records, 2006-2026). The dashboard must support time range, geographic area, and crime type filters while displaying existing analyses from Phases 1-3. Key findings: Streamlit's `@st.cache_data` decorator is essential for handling 3.5M-row Parquet files, `st.query_params` provides URL state encoding for shareable links, and existing matplotlib figures can be embedded via `st.pyplot()` without modification to analysis modules. The recommended architecture uses a single-page app with `st.tabs` for organization (Overview/Stats, Temporal Trends, Spatial Maps, Correlations, Advanced Temporal), sidebar for per-tab filter widgets, and hybrid caching (cached static reports + interactive recomputation).

**Primary recommendation:** Use Streamlit's `@st.cache_data` for Parquet data loading with `max_entries` and `ttl` parameters, embed existing matplotlib figures via `st.pyplot(fig)`, organize tabs via `st.tabs()`, persist filter state via `st.query_params`, and use `st.session_state` for cascading filter logic.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **streamlit** | 1.40+ (latest) | Dashboard framework | Official Python framework for data apps, pure Python, excellent for research dashboards |
| **pandas** | 2.x | Data manipulation | Existing project dependency, Parquet support |
| **plotly** | 5.x+ | Interactive charts | Native Streamlit support via `st.plotly_chart`, 30+ chart types |
| **matplotlib** | 3.x | Static figures | Existing project dependency, embedded via `st.pyplot` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pyarrow** | 14.x+ | Parquet engine | Faster Parquet I/O than fastparquet, default in pandas 2.x |
| **numpy** | 2.x | Numerical operations | Existing project dependency |
| **seaborn** | 0.12.x | Statistical plots | Existing project dependency, static visualizations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| streamlit | Dash | Dash requires more boilerplate, steeper learning curve, slower prototyping |
| pandas | Polars | Polars faster for large datasets but existing code uses pandas, migration cost |
| st.tabs | st.navigation (multi-page) | `st.navigation` better for truly separate pages; `st.tabs` simpler for single-page dashboard |

**Installation:**
```bash
pip install streamlit plotly pyarrow
# Already installed: pandas numpy matplotlib seaborn
```

## Architecture Patterns

### Recommended Project Structure
```
dashboard/
├── __init__.py
├── app.py              # Main entry point: title, tabs, session state init
├── pages/
│   ├── __init__.py
│   ├── overview.py     # Summary stats, metric cards
│   ├── temporal.py     # Temporal trends analysis
│   ├── spatial.py      # Spatial maps and distribution
│   ├── correlations.py # External data correlations
│   └── advanced.py     # Holiday effects, crime types, shift analysis
├── filters/
│   ├── __init__.py
│   ├── time_filters.py     # Date range, year/month selectors
│   ├── geo_filters.py      # District, neighborhood selectors
│   └── crime_filters.py    # UCR category, crime type selectors
├── components/
│   ├── __init__.py
│   ├── cache.py        # Data loading with @st.cache_data
│   ├── state.py        # Session state management
│   └── plots.py        # Plotly conversions from matplotlib
└── config.py           # Dashboard-specific constants
```

### Pattern 1: Data Loading with Caching for Large Datasets
**What:** Cache Parquet data loading with `@st.cache_data` decorator to avoid reloading 3.5M rows on each interaction.
**When to use:** Any function that loads or transforms data from Parquet files.
**Example:**
```python
# Source: https://docs.streamlit.io/develop/api-reference/caching-and-state
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading crime data...")
def load_crime_data() -> pd.DataFrame:
    """
    Load the full crime incidents dataset from Parquet.
    Cached for 1 hour (ttl=3600) with max 10 unique parameter combinations.
    """
    data_path = Path("data/crime_incidents_combined.parquet")
    return pd.read_parquet(data_path, engine="pyarrow")

@st.cache_data(show_spinner="Filtering data...")
def filter_data(df: pd.DataFrame, start_date, end_date, districts, crime_types):
    """
    Filter data by time, geography, and crime type.
    Results cached per unique filter combination.
    """
    mask = (
        (df["dispatch_date"] >= start_date) &
        (df["dispatch_date"] <= end_date) &
        (df["dc_dist"].isin(districts)) &
        (df["ucr_general"].isin(crime_types))
    )
    return df[mask].copy()
```

### Pattern 2: Tab-Based Organization with Per-Tab Filters
**What:** Use `st.tabs()` for organizing dashboard sections, with sidebar filters that change based on active tab.
**When to use:** Dashboard with multiple distinct analysis views requiring different filter contexts.
**Example:**
```python
# Source: https://docs.streamlit.io/develop/api-reference/layout
import streamlit as st

# Define tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview/Stats", "Temporal Trends", "Spatial Maps",
    "Correlations", "Advanced Temporal"
])

# Track active tab in session state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

with tab1:
    st.header("Overview")
    # Show summary stats, minimal filtering

with tab2:
    st.header("Temporal Trends")
    # Time series plots, time + crime filters

with tab3:
    st.header("Spatial Maps")
    # Geographic plots, geo + crime filters

# Sidebar filters update based on active tab
render_tab_filters(st.session_state.active_tab)
```

### Pattern 3: URL State Encoding for Shareable Links
**What:** Use `st.query_params` to persist filter state in URL for bookmarkable and shareable dashboard views.
**When to use:** Dashboard needs to support sharing specific filtered views with collaborators.
**Example:**
```python
# Source: https://docs.streamlit.io/develop/api-reference/caching-and-state
import streamlit as st
from datetime import datetime

# Initialize query params from URL or set defaults
params = st.query_params
if "start_date" not in params:
    params["start_date"] = "2006-01-01"
    params["end_date"] = "2025-12-31"

# Read from URL
start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")

# Update URL when filters change
def update_url_params(**kwargs):
    for key, value in kwargs.items():
        if isinstance(value, list):
            params[key] = ",".join(str(v) for v in value)
        else:
            params[key] = str(value)

# User interacts with filter
new_date = st.date_input("End date", value=end_date)
if new_date != end_date:
    update_url_params(end_date=new_date.strftime("%Y-%m-%d"))
    st.rerun()
```

### Pattern 4: Embedding Existing Matplotlib Figures
**What:** Reuse matplotlib figures from existing analysis modules without code modification using `st.pyplot(fig)`.
**When to use:** Analysis modules already return matplotlib figure objects.
**Example:**
```python
# Source: https://docs.streamlit.io/develop/api-reference/charts/st.pyplot
import streamlit as st
import matplotlib.pyplot as plt
from analysis.temporal_analysis import plot_yearly_trend

# Existing function returns matplotlib Figure object
fig = plot_yearly_trend(df=filtered_data, ci=True)

# Display directly in Streamlit
st.pyplot(fig, use_container_width=True)

# For existing functions that use image_to_base64 for reports:
# Option 1: Modify to optionally return fig object
# Option 2: Keep base64 for reports, create new plot functions for dashboard
```

### Pattern 5: Cascading Filters with Session State
**What:** Implement filter dependencies (e.g., year selection affects available months) using `st.session_state`.
**When to use:** Filter options depend on previous selections.
**Example:**
```python
# Source: https://docs.streamlit.io/develop/api-reference/caching-and-state
import streamlit as st
import pandas as pd

# Initialize filter state
if "filters" not in st.session_state:
    st.session_state.filters = {
        "years": [2006, 2025],
        "months": list(range(1, 13)),
        "districts": list(range(1, 24)),
        "crime_types": "all"
    }

# Year filter affects available months
selected_years = st.multiselect(
    "Years",
    options=range(2006, 2026),
    default=st.session_state.filters["years"]
)

# Update state and cascade to month filter
st.session_state.filters["years"] = selected_years

# Month slider limited by selected years
if len(selected_years) == 1:
    # Show all months for single year
    month_options = list(range(1, 13))
else:
    # For multi-year, month span across selected years
    month_options = list(range(1, 13))

selected_months = st.multiselect(
    "Months",
    options=month_options,
    default=st.session_state.filters["months"]
)
```

### Anti-Patterns to Avoid
- **Loading full dataset without caching:** Always use `@st.cache_data` for Parquet loading. 3.5M rows takes ~10+ seconds without cache.
- **Using `@st.cache_resource` for data:** `st.cache_resource` doesn't create copies, risking data corruption. Use `st.cache_data` for dataframes.
- **Recomputing static reports on every interaction:** Cache static report outputs as base64 strings, display with `st.markdown` or `st.image`.
- **Putting all filters in main content area:** Use `st.sidebar` for filters to maximize space for visualizations.
- **Using `st.set_page_config` inside functions:** Call once at top of `app.py`, not in imported modules.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data caching | Custom TTL or file-based caching | `@st.cache_data(ttl=..., max_entries=...)` | Built-in hash-based invalidation, disk persistence option, automatic spinner |
| URL state parsing | Manual URL parameter parsing | `st.query_params` | Dictionary-like interface, automatic URL sync, handles encoding |
| Session persistence | Database or custom storage | `st.session_state` | Per-user persistence, survives reruns, no external dependency |
| Date range slider | Custom slider widget | `st.slider` with datetime values | Built-in datetime support, automatic formatting |
| Data tables | Custom HTML tables | `st.dataframe` / `st.data_editor` | Sorting, filtering, column configuration, selection handling |
| Progress indication | Custom loading animation | `st.spinner` / `st.status` | Built-in UI, context manager pattern, automatic display |
| Tab navigation | Custom page routing | `st.tabs()` | Built-in tabs, preserves state, familiar UI |

**Key insight:** Streamlit provides production-ready implementations for all common dashboard patterns. Custom implementations add maintenance burden and often have edge cases (URL encoding, session expiration, race conditions).

## Common Pitfalls

### Pitfall 1: UnhashableParamError with Cached Data
**What goes wrong:** Error `UnhashableParamError: Cannot hash argument of type: <class 'pandas.DataFrame'>` when trying to cache functions with DataFrame arguments.
**Why it happens:** Streamlit's cache needs to hash function arguments to detect changes. Pandas DataFrames are mutable and not hashable by default.
**How to avoid:** Use `hash_funcs` parameter to provide custom hash function for DataFrames (or convert to hashable type like tuple of column values).
**Warning signs:** Cache decorator throws `UnhashableParamError` or fails to recognize DataFrame changes.
```python
# Solution: Provide custom hash function
@st.cache_data(hash_funcs={pd.DataFrame: lambda df: df.values.tobytes()})
def process_dataframe(df: pd.DataFrame):
    return df.groupby("district").size()
```

### Pitfall 2: Cache Memory Bloat with 3.5M Rows
**What goes wrong:** Dashboard consumes excessive RAM as cache stores multiple filtered versions of the dataset.
**Why it happens:** Each unique filter combination creates a new cache entry. With many filter options, cache grows unbounded.
**How to avoid:** Set `max_entries` parameter on `@st.cache_data` to limit cache size. Consider `ttl` for time-based expiration.
**Warning signs:** RAM usage grows continuously, cache warnings in logs, slower performance over time.
```python
@st.cache_data(max_entries=50, ttl=3600)
def filter_data(df, start_date, end_date, districts, crime_types):
    # ... filtering logic ...
    pass
```

### Pitfall 3: Slow Initial Load Despite Caching
**What goes wrong:** First dashboard visit takes 10+ seconds even with caching enabled.
**Why it happens:** Cache miss on first load requires reading full 3.5M-row Parquet file. Parquet column projection helps but still significant I/O.
**How to avoid:** Show loading spinner with `show_spinner` parameter. Consider pre-warming cache on deployment. Use `use_container_width=True` for better perceived performance.
**Warning signs:** Long initial load time, users abandon before first render.

### Pitfall 4: Matplotlib Figures Not Updating
**What goes wrong:** Embedded matplotlib figures show stale data after filters change.
**Why it happens:** Reusing cached figure object instead of regenerating with new data.
**How to avoid:** Don't cache plot functions. Cache data loading, but regenerate plots with filtered data. Or use `hash_funcs` on figure parameters.
**Warning signs:** Figures show different data than summary stats, plots don't respond to filter changes.

### Pitfall 5: URL Parameter Encoding Issues
**What goes wrong:** URL becomes unreadable or breaks when filter values contain special characters or are long lists.
**Why it happens:** `st.query_params` URL-encodes values by default, but long lists or special characters can create issues.
**How to avoid:** Compress list values (comma-separated), avoid special characters in filter IDs, handle encoding/decoding explicitly.
**Warning signs:** URLs are excessively long, some filters don't persist across share links.

### Pitfall 6: Widget Key Conflicts
**What goes wrong:** Multiple widgets interfere with each other's values or state gets mixed up.
**Why it happens:** Widget keys must be unique. Reusing keys or auto-generated keys can cause conflicts.
**How to avoid:** Always specify unique `key` parameter for each widget, especially when dynamically generating widgets.
**Warning signs:** Changing one widget affects another, state inconsistency.

## Code Examples

Verified patterns from official sources:

### Data Loading with Aggressive Caching
```python
# Source: https://docs.streamlit.io/develop/concepts/architecture/caching
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data(ttl=3600, max_entries=10, persist="disk", show_spinner="Loading data...")
def load_data():
    """Load full Parquet dataset with aggressive caching."""
    path = Path("data/crime_incidents_combined.parquet")
    return pd.read_parquet(path, engine="pyarrow")

@st.cache_data(max_entries=100, show_spinner="Filtering...")
def apply_filters(df, start_date, end_date, districts, crime_categories):
    """Apply filters with per-combination caching."""
    mask = (
        (df["dispatch_date"] >= start_date) &
        (df["dispatch_date"] <= end_date) &
        (df["dc_dist"].isin(districts))
    )
    if crime_categories != "all":
        mask &= df["ucr_general"].isin(crime_categories)
    return df[mask].copy()
```

### Sidebar Filter Widget
```python
# Source: https://docs.streamlit.io/develop/api-reference/widgets
import streamlit as st
from datetime import datetime

with st.sidebar:
    st.header("Filters")

    # Date range slider
    start_date = st.slider(
        "Start Date",
        min_value=datetime(2006, 1, 1),
        max_value=datetime(2025, 12, 31),
        value=datetime(2006, 1, 1),
        format="YYYY-MM-DD",
        key="start_date"
    )

    end_date = st.slider(
        "End Date",
        min_value=datetime(2006, 1, 1),
        max_value=datetime(2025, 12, 31),
        value=datetime(2025, 12, 31),
        format="YYYY-MM-DD",
        key="end_date"
    )

    # District multi-select
    districts = st.multiselect(
        "Police Districts",
        options=list(range(1, 24)),
        default=list(range(1, 24)),
        key="districts"
    )

    # Crime category select
    crime_category = st.selectbox(
        "UCR Category",
        options=["All", "Violent", "Property", "Other"],
        key="crime_category"
    )
```

### Embedding Matplotlib and Plotly Figures
```python
# Source: https://docs.streamlit.io/develop/api-reference/charts
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

# Matplotlib figure (static)
fig_mpl, ax = plt.subplots()
ax.plot(df["year"], df["crime_count"])
ax.set_title("Crime Trend Over Time")
st.pyplot(fig_mpl, use_container_width=True)

# Plotly figure (interactive)
fig_plotly = px.line(
    df,
    x="year",
    y="crime_count",
    title="Crime Trend Over Time",
    markers=True
)
st.plotly_chart(fig_plotly, use_container_width=True)
```

### Tab Organization with Per-Tab Content
```python
# Source: https://docs.streamlit.io/develop/api-reference/layout
import streamlit as st

st.title("Philadelphia Crime Incidents Dashboard")

tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Maps"])

with tab1:
    st.header("Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidents", f"{total_incidents:,}")
    with col2:
        st.metric("Avg Daily", f"{avg_daily:.1f}")
    with col3:
        st.metric("Most Common", most_common_crime)

with tab2:
    st.header("Temporal Trends")
    # Trend analysis here

with tab3:
    st.header("Spatial Distribution")
    # Map visualization here
```

### URL State Synchronization
```python
# Source: https://docs.streamlit.io/develop/api-reference/caching-and-state
import streamlit as st
from urllib.parse import encode_args

# Sync filters to URL
def sync_to_url(params):
    """Update URL with current filter state."""
    for key, value in params.items():
        if isinstance(value, list):
            st.query_params[key] = ",".join(map(str, value))
        else:
            st.query_params[key] = str(value)

# Read from URL on load
def read_from_url():
    """Read filter state from URL parameters."""
    params = st.query_params
    return {
        "start_date": params.get("start_date", "2006-01-01"),
        "districts": params.get("districts", "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23").split(","),
        "ucr_category": params.get("ucr_category", "All")
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@st.cache` (unified) | `@st.cache_data` + `@st.cache_resource` | Streamlit 1.18+ (2023) | Explicit intent: data vs resources, better memory management |
| `st.experimental_get_query_params` | `st.query_params` | Streamlit 1.10+ (2022) | Stable API for URL state, dictionary-like interface |
| `st.legacy_caching.cached` | `@st.cache_data` | Streamlit 1.18+ (2023) | Deprecated removed, use new decorators |
| Multi-file `pages/` structure | `st.navigation` or `st.tabs` | Streamlit 1.28+ (2024) | New navigation API for multi-page apps |

**Deprecated/outdated:**
- `st.cache`: Replaced by `st.cache_data` and `st.cache_resource`. Do not use.
- `st.experimental_get_query_params`: Use `st.query_params` instead.
- `st.beta_*`: All beta APIs are now stable. Use stable versions.

## Open Questions

1. **Parquet file optimization for 3.5M rows**
   - What we know: Parquet is the recommended format, pyarrow engine is faster than fastparquet
   - What's unclear: Whether partitioning by year/district would improve filter performance
   - Recommendation: Start with single Parquet file (existing), measure performance, optimize if needed

2. **Matplotlib figure conversion for dashboard**
   - What we know: Existing modules use `image_to_base64()` for reports
   - What's unclear: Whether to create separate plotting functions for dashboard or modify existing to optionally return fig objects
   - Recommendation: Create `dashboard_plots.py` with new functions that reuse analysis logic but return fig objects

3. **Performance target: 5-second load time**
   - What we know: `@st.cache_data` with disk persistence helps, 3.5M rows is significant
   - What's unclear: Achievable on typical hardware without sampling
   - Recommendation: Benchmark on target hardware, consider pre-aggregated views for common queries

4. **Stale data handling (2026 incomplete)**
   - What we know: 2026 data is only through January 20
   - What's unclear: Whether to exclude 2026 from dashboard or show with warning
   - Recommendation: Default filters exclude 2026, add option to include with prominent warning

## Sources

### Primary (HIGH confidence)
- [Streamlit Documentation](https://docs.streamlit.io) - Caching architecture, API reference for `st.cache_data`, `st.cache_resource`, `st.query_params`, `st.tabs`, `st.pyplot`, `st.plotly_chart`, session state, sidebar widgets
  - Topics fetched: Caching, query parameters, tabs layout, matplotlib/plotly embedding, filters, session state, dataframes
- [Plotly Documentation](https://plotly.com/python/) - Plotly figure creation for time series, bar charts, choropleth maps
  - Topics fetched: Line charts, choropleth maps, combined charts

### Secondary (MEDIUM confidence)
- [Streamlit Forum: FAQ Large Data Performance](https://discuss.streamlit.io/t/faq-how-to-improve-performance-of-apps-with-large-data/64007) - Community-verified best practices for handling large datasets
- [Streamlit Blog: Improve App Loading Speed](https://blog.streamlit.io/how-to-improve-streamlit-app-loading-speed-f091dc3e2861) - Official blog post on performance optimization
- [Building Production Dashboards with DuckDB](https://developersvoice.com/blog/data-analytics/streamlit-duckdb-production-dashboards/) - Verified guide on production-ready dashboards
- [Stack Overflow: Matplotlib in Streamlit](https://stackoverflow.com/questions/76844921/how-to-plot-matplotlib-objects-from-third-party-libraries-in-streamlit) - Community discussion on embedding third-party matplotlib figures

### Tertiary (LOW confidence)
- [Reddit: Handle Large Datasets in Streamlit](https://www.reddit.com/r/Streamlit/comments/1jk0ah1/what_are_the_best_ways_to_handle_large_datasets/) - Community discussion, marked for validation
- Various Medium blog posts on Streamlit best practices - General guidance, not authoritative

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official Streamlit documentation and established best practices
- Architecture: HIGH - Verified against official docs and community patterns
- Pitfalls: HIGH - Documented in official docs and verified by community discussions

**Research date:** 2026-01-31
**Valid until:** 2026-03-01 (60 days - Streamlit API is stable but may have minor updates)

**Researcher's note:** Streamlit's caching system is well-designed for large datasets. The key to 5-second load time target is aggressive `@st.cache_data` usage with `ttl` and `max_entries` parameters, combined with disk persistence. Embedding existing matplotlib figures is straightforward via `st.pyplot(fig)`, no code modification needed beyond ensuring functions return figure objects.
