# Crime Incidents Philadelphia - Notebook-Driven Analysis Platform

Analyze crime incidents in Philadelphia using an interactive Jupyter notebook suite. This project transforms script-based analysis into an interactive, step-by-step workflow for exploring temporal and spatial crime patterns.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project directory
cd Crime\ Incidents\ Philadelphia

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Jupyter

```bash
jupyter lab notebooks/
# or
jupyter notebook notebooks/00_start_here.ipynb
```

### 3. Follow the Notebook Workflow

1. **Start Here**: Open `00_start_here.ipynb` for overview and navigation
2. **Phase 1**: Data Ingestion (`phase_01_data_ingestion/`) - Download and consolidate data
3. **Phase 2**: Exploration (`phase_02_exploration/`) - Understand data structure
4. **Phase 3**: Processing (`phase_03_processing/`) - Clean and create features
5. **Phase 4**: Analysis (`phase_04_analysis/`) - Temporal and categorical analysis
6. **Phase 5**: Visualization (`phase_05_visualization/`) - Maps and dashboards
7. **Phase 6**: Modeling (`phase_06_modeling/`) - Forecasting and classification

## 📊 Project Structure

```
.
├── notebooks/                  # Jupyter notebooks (NEW!)
│   ├── 00_start_here.ipynb     # Master index & workflow guide
│   ├── phase_01_data_ingestion/
│   │   └── 01_scrape_and_consolidate.ipynb
│   ├── phase_02_exploration/
│   │   ├── 01_data_overview.ipynb
│   │   └── 02_data_quality_assessment.ipynb
│   ├── phase_03_processing/
│   │   ├── 01_data_cleaning.ipynb
│   │   └── 02_feature_engineering.ipynb
│   ├── phase_04_analysis/
│   │   ├── 01_temporal_analysis.ipynb
│   │   ├── 02_categorical_analysis.ipynb
│   │   └── 03_statistical_summaries.ipynb
│   ├── phase_05_visualization/
│   │   ├── 01_crime_maps_and_hotspots.ipynb
│   │   └── 02_trend_analysis_dashboards.ipynb
│   └── phase_06_modeling/
│       ├── 01_forecasting_exploration.ipynb
│       └── 02_classification_models.ipynb
├── data/                       # Data storage
│   ├── raw/                    # Original downloads
│   └── processed/              # Consolidated Parquet files
├── scripts/
│   └── helper/                 # ETL/helper scripts
│       ├── scrape.py           # Download data from API
│       └── csv_to_parquet.py   # Consolidate and optimize
├── src/                        # Reusable library code
│   ├── data/                   # Data loading
│   ├── analysis/               # Statistical analysis
│   ├── geospatial/             # Spatial analysis
│   └── utils/                  # Configuration
├── visualizations/             # Generated maps and charts
├── requirements.txt            # Python dependencies
├── config.ini                  # Configuration settings
└── README.md                   # This file
```

## 📚 Workflow Overview

### Phase 1: Data Ingestion
- Download monthly crime data from OpenDataPhilly API
- Consolidate into single Parquet file
- Optimize data types for efficient storage
- **Output**: `crime_incidents_combined.parquet`

### Phase 2: Exploration
- Load and inspect data structure
- Profile columns, types, and distributions
- Assess data quality (missing values, duplicates, outliers)
- Validate geographic coordinates
- **Output**: Quality assessment report

### Phase 3: Processing
- Handle missing values
- Remove duplicates
- Standardize date/time formats
- Create temporal features (year, month, season, weekday)
- Create spatial features (distance to center, zones)
- **Output**: `crime_incidents_enriched.parquet`

### Phase 4: Analysis
- **Temporal**: Trends over years/months, seasonality, weekly patterns
- **Categorical**: Top crime types, top districts, cross-tabulations
- **Statistical**: Distributions, correlations, summary statistics
- **Output**: Analysis tables and insights

### Phase 5: Visualization
- **Maps**: Interactive Folium maps with heatmaps and markers
- **Dashboards**: Plotly interactive dashboards
- **Trend Charts**: Time-series and comparative visualizations
- **Output**: HTML reports in `visualizations/` directory

### Phase 6: Modeling (Starter Templates)
- **Forecasting**: Time-series prediction templates
- **Classification**: Crime type/district prediction templates
- **Next Steps**: Expand with production models

## 🔑 Key Features

✅ **Interactive**: Run cells step-by-step, modify parameters, explore in real-time  
✅ **Modular**: Each notebook focuses on one phase  
✅ **Reusable**: Leverage library code in `src/` to avoid duplication  
✅ **Documented**: Markdown explains objectives and interpretations  
✅ **Shareable**: Export notebooks as HTML for stakeholders  
✅ **Reproducible**: Full pipeline documented and auditable  

## 🛠️ Reusable Modules

Notebooks import and use these library functions:

- **`src.data.loader`**: Load Parquet files
- **`src.analysis.profiler`**: Data profiling and statistical analysis
- **`src.geospatial.analyzer`**: Spatial analysis and mapping
- **`src.utils.config`**: Configuration management

## 📋 Data Refresh Strategy

### Option A: Refresh at Session Start (Recommended)
- Run Phase 1 notebook at beginning of analysis session
- Ensures latest data available
- Takes 5-10 minutes

### Option B: External Scheduled Refresh
- Set up cron job or GitHub Actions
- Refresh data automatically (e.g., daily)
- Notebooks always work with current data

### Option C: Manual Refresh
- Run refresh steps on-demand
- Lower overhead but requires manual action

## 🔍 Example Analyses

Each notebook includes complete examples:

**Temporal Trends**
```
Phase 4 → 01_temporal_analysis.ipynb
- Annual crime trends
- Seasonal patterns (monthly, weekly)
- Peak crime times
```

**Geographic Patterns**
```
Phase 5 → 01_crime_maps_and_hotspots.ipynb
- Interactive Folium maps
- Heatmap density analysis
- District-level statistics
```

**Crime Classification**
```
Phase 5 → 02_trend_analysis_dashboards.ipynb
- Plotly dashboards
- Multi-series trend comparisons
- Year×Month heatmaps
```

## 📦 Dependencies

Core packages:
- **pandas**: Data manipulation
- **geopandas**: Spatial data
- **folium**: Interactive maps
- **plotly**: Interactive dashboards
- **scikit-learn**: ML models
- **jupyter**: Notebooks

Optional (for Phase 6):
- **statsmodels**: Time-series analysis
- **prophet**: Forecasting

## 🚢 Deployment

### Share Results
1. Export notebooks as HTML: File → Export → HTML
2. Share maps: Open `visualizations/*.html` in browser
3. Create reports: Combine notebook cells with markdown

### Run Scheduled Updates
```bash
# Add to crontab for daily refresh (example)
0 2 * * * cd /path/to/project && python scripts/helper/refresh_data.py
```

### Integrate with Dashboards
- Use generated HTML visualizations in dashboards
- Build APIs around notebook outputs
- Schedule notebook execution with Papermill

## 📝 Configuration

Edit `config.ini` to customize:
- Data paths
- API endpoints
- Output directories

## 🤝 Contributing

To add new analyses:
1. Create new notebook in appropriate phase directory
2. Follow existing structure and naming conventions
3. Use reusable code from `src/`
4. Document objectives in markdown cells

## 📧 Support

For issues or questions:
1. Check the master index: `notebooks/00_start_here.ipynb`
2. Review phase-specific documentation
3. Examine existing notebooks for examples

## 📄 License

[Add your license information]

---

**Version**: 1.0 (Notebook-Driven Architecture)  
**Last Updated**: 2026-01-27  
**Data Source**: [OpenDataPhilly](https://opendataphilly.org/)
