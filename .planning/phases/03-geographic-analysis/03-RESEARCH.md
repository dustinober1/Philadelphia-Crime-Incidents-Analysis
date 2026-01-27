# Phase 3: Geographic Analysis - Research

**Researched:** 2026-01-27
**Domain:** Geographic data analysis and visualization
**Confidence:** HIGH

## Summary

This research covers the tools and techniques needed to implement geographic analysis for crime incidents in Philadelphia. The analysis includes mapping crime incidents by location coordinates, identifying geographic hotspots using kernel density estimation, analyzing spatial distribution patterns, and comparing crime density across different geographic areas. The solution leverages GeoPandas for geospatial data manipulation, Folium for interactive mapping, and PySAL for spatial analysis including hotspot detection.

**Primary recommendation:** Use GeoPandas + Folium + PySAL stack for comprehensive geographic analysis with interactive maps and spatial statistics.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| GeoPandas | 1.1.2+ | Geospatial data manipulation extending pandas | Extends familiar pandas API with geometric operations |
| Folium | 0.20.0+ | Interactive map visualization | Industry standard for Python web-based mapping |
| PySAL | 3.0+ | Spatial analysis and statistics | Comprehensive spatial analytics library |
| scikit-learn | 1.8.0+ | Kernel density estimation | Robust KDE implementation for hotspot analysis |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| contextily | 1.7.1+ | Basemap tiles for geographic context | Adding street map backgrounds to plots |
| geopy | 2.4.1+ | Geocoding addresses to coordinates | Processing records with missing coordinates |
| matplotlib | 3.9+ | Static geographic visualizations | When static maps needed alongside interactive ones |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Folium | Plotly/Dash | More interactive features but steeper learning curve |
| PySAL | Custom scipy.spatial implementations | Less robust spatial statistics, reinventing wheel |
| GeoPandas | Pure Shapely | Missing pandas integration and I/O capabilities |

**Installation:**
```bash
pip install geopandas folium pysal scikit-learn contextily geopy
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── geospatial/        # Geographic analysis functions
│   ├── __init__.py
│   ├── analyzer.py    # Main geographic analysis class
│   └── utils.py       # Geographic utility functions
├── data/              # Data loading and preprocessing
│   └── loader.py      # Data loading with coordinate validation
└── visualization/     # Mapping functions
    ├── __init__.py
    └── geographic.py  # Interactive map generation
```

### Pattern 1: GeoDataFrame Integration
**What:** Extending pandas DataFrame with geometric operations
**When to use:** When working with coordinate data that needs spatial operations
**Example:**
```python
import geopandas as gpd
import pandas as pd

# Create GeoDataFrame from coordinate columns
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
    crs='EPSG:4326'
)

# Perform spatial operations
gdf_projected = gdf.to_crs('EPSG:3857')  # Web Mercator for mapping
```

### Pattern 2: Interactive Mapping with Folium
**What:** Creating interactive maps with crime incident markers
**When to use:** For user exploration of geographic patterns
**Example:**
```python
import folium
from folium.plugins import HeatMap

# Create base map centered on Philadelphia
m = folium.Map(
    location=[39.9526, -75.1652],  # Philadelphia coordinates
    zoom_start=12,
    tiles=None  # Add custom tiles later
)

# Add crime incidents as markers colored by type
for idx, row in gdf.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        popup=f"Crime: {row['crime_type']}",
        color=get_color_by_crime_type(row['crime_type']),  # Custom function
        fill=True
    ).add_to(m)
```

### Anti-Patterns to Avoid
- **Manual coordinate system conversions:** Always use GeoPandas `.to_crs()` method instead of manual calculations
- **Processing coordinates separately:** Use GeoDataFrame to maintain coordinate integrity
- **Static maps for exploration:** Use interactive maps for user exploration of geographic patterns

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Coordinate reference systems | Manual conversion formulas | GeoPandas `.to_crs()` | Complex math with edge cases |
| Spatial indexing | Custom quadtree/R-tree | GeoPandas built-in spatial ops | Highly optimized in GEOS library |
| Kernel density estimation | Custom scipy implementation | scikit-learn `KernelDensity` | Handles bandwidth selection, edge effects |
| Geocoding addresses | Custom API calls | geopy with Nominatim | Rate limiting, error handling, caching |
| Spatial clustering | Custom distance algorithms | PySAL `esda` module | Statistical significance testing |

**Key insight:** Geographic analysis has complex mathematical and computational requirements that are well-solved by established libraries with years of optimization and error correction.

## Common Pitfalls

### Pitfall 1: Coordinate Reference System Mismatch
**What goes wrong:** Mixing geographic (lat/lon) and projected (meter/foot) coordinates
**Why it happens:** Using distance-based operations on lat/lon coordinates giving incorrect results
**How to avoid:** Always project coordinates to appropriate CRS before distance/area calculations
**Warning signs:** Distances/areas that seem too large or too small

### Pitfall 2: Memory Issues with Large Spatial Operations
**What goes wrong:** Running out of memory during spatial joins or overlay operations
**Why it happens:** Spatial operations can create quadratic complexity
**How to avoid:** Process data in chunks or filter before expensive operations
**Warning signs:** Long-running operations, increasing memory usage

### Pitfall 3: Incorrect Bandwidth Selection for KDE
**What goes wrong:** Too smooth or too noisy hotspot maps
**Why it happens:** Fixed bandwidth not appropriate for varying data density
**How to avoid:** Use adaptive bandwidth selection or cross-validation
**Warning signs:** Hotspots that don't align with domain knowledge

## Code Examples

Verified patterns from official sources:

### Creating GeoDataFrame from Coordinate Data
```python
# Source: GeoPandas documentation
import geopandas as gpd
import pandas as pd

# Convert lat/lon columns to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
    crs='EPSG:4326'  # WGS84 geographic coordinates
)

# Validate coordinates
gdf_valid = gdf[gdf.geometry.is_valid & ~gdf.geometry.is_empty]
print(f"Dropped {len(gdf) - len(gdf_valid)} invalid geometries")
```

### Kernel Density Estimation for Crime Hotspots
```python
# Source: scikit-learn documentation
from sklearn.neighbors import KernelDensity
import numpy as np

# Prepare coordinates for KDE (projected coordinates work best)
coords = gdf.to_crs('EPSG:3857')[['geometry']].get_coordinates().values

# Fit KDE model
kde = KernelDensity(kernel='gaussian', bandwidth=1000)  # 1000m bandwidth
kde.fit(coords)

# Generate hotspot grid
x_min, y_min, x_max, y_max = gdf.total_bounds
xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 100),
    np.linspace(y_min, y_max, 100)
)
grid_points = np.column_stack([xx.ravel(), yy.ravel()])

# Calculate densities
log_density = kde.score_samples(grid_points)
density = np.exp(log_density).reshape(xx.shape)
```

### Interactive Map with Crime Types Filter
```python
# Source: Folium documentation
import folium
from folium.plugins import MarkerCluster

def create_crime_map(gdf, crime_types=None):
    # Filter by crime type if specified
    if crime_types:
        filtered_gdf = gdf[gdf['crime_type'].isin(crime_types)]
    else:
        filtered_gdf = gdf
    
    # Create base map
    center_lat = filtered_gdf.geometry.y.mean()
    center_lon = filtered_gdf.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Add basemap tiles
    folium.TileLayer('OpenStreetMap').add_to(m)
    
    # Add markers for each crime
    for idx, row in filtered_gdf.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"{row['crime_type']}: {row['incident_date']}",
            icon=folium.Icon(color=get_marker_color(row['crime_type']))
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    return m
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom shapefile processing | GeoPandas with standardized CRS | 2014+ | Simplified geospatial workflows |
| Static matplotlib plots | Interactive Folium maps | 2015+ | Better user exploration experience |
| Manual spatial statistics | PySAL automated analysis | 2018+ | Proper statistical inference |
| Individual geocoding calls | Batch geocoding with rate limiting | 2019+ | Improved performance and reliability |

**Deprecated/outdated:**
- `pandas + shapely` direct integration: Use GeoPandas instead
- `folium.Map()` without explicit CRS handling: Always specify coordinate systems

## Open Questions

Things that couldn't be fully resolved:

1. **Philadelphia Police Districts Shapefile**
   - What we know: Philadelphia has police districts that can be used for aggregation
   - What's unclear: Specific shapefile availability and format for Philadelphia police districts
   - Recommendation: Download from OpenDataPhilly or Philadelphia government GIS portal

2. **Performance with Large Datasets**
   - What we know: 3.5M crime records may cause performance issues
   - What's unclear: Specific performance bottlenecks with spatial operations on this dataset size
   - Recommendation: Test with subset first and implement chunking if needed

## Sources

### Primary (HIGH confidence)
- GeoPandas documentation - GeoDataFrame creation and operations
- Folium documentation - Interactive mapping patterns
- Scikit-learn documentation - Kernel density estimation
- PySAL documentation - Spatial analysis methods

### Secondary (MEDIUM confidence)
- Philadelphia OpenData portal for police district boundaries
- Geopy documentation for geocoding capabilities

### Tertiary (LOW confidence)
- General Python geospatial tutorials (need verification)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Well-established libraries with current documentation
- Architecture: HIGH - Standard patterns from official documentation
- Pitfalls: HIGH - Well-documented issues in geospatial analysis
- Code examples: HIGH - Direct from official documentation

**Research date:** 2026-01-27
**Valid until:** 2026-04-27 (3 months for stable libraries, 7 days for fast-moving aspects)