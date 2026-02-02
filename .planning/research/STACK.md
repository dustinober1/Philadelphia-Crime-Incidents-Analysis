# STACK.md

Project Research — Recommended 2026 stack for Philadelphia crime analysis (Python-first)

Rationale: keep tooling reproducible, well-supported for geospatial/time-series analysis, and familiar to data scientists working in Jupyter notebooks.

Core language
- Python 3.11+

Environment
- Pin environment with `requirements.txt` and `environment.yml` for reproducibility.
- Use `pip` or `mamba/conda` for environment creation; include `pip-tools` for deterministic requirements.

Data & IO
- pandas >= 2.1 — primary tabular processing
- pyarrow >= 12 — fast Parquet read/write
- geopandas >= 1.2 — geospatial joins and vector I/O
- fiona, shapely >= 2.0, rtree/pygeos for fast spatial ops
- sqlalchemy (optional) for metadata or small DB usage

Time series & forecasting
- prophet >= 1.1 (facebook/prophet revival package `prophet`) OR statsmodels >= 0.14 (ARIMA/seasonal models)
- darts (optional) for convenient model comparisons

Modeling & ML
- scikit-learn >= 1.2 — baseline modeling and pipelines
- xgboost >= 1.7 or lightgbm >= 4.x — boosted tree models for classification
- shap/explainability libraries for feature importances (shap >= 0.42)

Mapping & visualization
- matplotlib, seaborn for static plots
- folium or kepler.gl (pydeck) for interactive maps in notebooks
- contextily for background tiles (when using web-mercator projections)
- geopandas.plot and plotly (optional) for rich visuals

Spatial tooling
- pyproj for CRS handling
- libpysal (optional) for spatial statistics and clustering
- scikit-mobility (optional) for movement- or corridor-style analyses

Weather & external APIs
- meteostat or direct NOAA downloads (ISD) for hourly temperature data; Visual Crossing as a paid/free-tier alternative

Census & demographics
- cenpy or census (python-census) to fetch tract-level population; geopandas for spatial joins

Reproducible runs & CI
- jupyterlab + nbconvert for headless execution
- papermill for parameterized notebook runs (useful for repeated experiments)
- pre-commit, black, isort for code hygiene

Storage & data layout (concrete)
- data/raw/ — immutable source files (CSV/Parquet) as received
- data/external/ — external datasets (weather, census shapefiles/parquet)
- data/processed/ — cleaned, canonical Parquet artifacts (e.g., crime_incidents.parquet)
- reports/ — generated figures and Markdown/HTML exports

Recommended exclusions
- Avoid heavy GIS server stacks (GeoServer) for v1 —
  static map artifacts and lightweight folium/pydeck are sufficient

Versions and verification
- Lock major libraries in `requirements.txt` and verify with `pip check` / `conda list` in CI; prefer conservative, well-supported versions.

Why these choices
- pandas/geopandas ecosystem provides best balance of clarity and performance for spatial joins and per-incident analysis in notebooks.
- Prophet/ARIMA are standard, interpretable forecasting choices for short-term incident forecasting; tree-based models are well-suited for violence classification.
