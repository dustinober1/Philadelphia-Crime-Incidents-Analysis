# Crime Incidents Philadelphia

This project analyzes crime incidents in Philadelphia using Jupyter notebooks.

## Project Structure

```
├── data/
│   ├── raw/          # Raw data files
│   ├── processed/    # Cleaned and processed data
│   └── external/     # External data sources
├── docs/             # Documentation files
├── models/           # Trained models
├── notebooks/        # Jupyter notebooks organized by purpose
│   ├── 00_project_summary.ipynb
│   ├── data_exploration/
│   │   ├── 01_data_overview.ipynb
│   │   └── 02_data_quality_assessment.ipynb
│   ├── data_processing/
│   │   ├── 01_data_cleaning.ipynb
│   │   └── 02_feature_engineering.ipynb
│   ├── modeling/
│   │   ├── 01_model_exploration.ipynb
│   │   └── 02_model_training.ipynb
│   └── visualization/
│       ├── 01_crime_visualization.ipynb
│       └── 02_trend_analysis.ipynb
├── src/              # Source code modules
│   ├── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   ├── features/
│   └── models/
├── visualizations/   # Static visualization outputs
│   └── __init__.py
├── config.ini        # Configuration settings
├── project_plan.md   # Project planning document
└── requirements.txt  # Python dependencies
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Start Jupyter: `jupyter notebook` or `jupyter lab`
3. Navigate to the notebooks/ directory to begin exploring the analysis
