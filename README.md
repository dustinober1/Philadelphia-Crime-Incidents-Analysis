# Crime Incidents Philadelphia

This project analyzes crime incidents in Philadelphia using Python scripts.

## Project Structure

```
├── data/
│   ├── raw/          # Raw data files
│   ├── processed/    # Cleaned and processed data
│   └── external/     # External data sources
├── docs/             # Documentation files
├── models/           # Trained models
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
2. Run data collection: `python scripts/helper/scrape.py`
3. Process data: `python scripts/helper/csv_to_parquet.py`
