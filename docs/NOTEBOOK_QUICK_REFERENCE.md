# Quick Reference: Philadelphia Safety Trend Analysis Notebook

## TL;DR - What You Get

A complete, self-contained Jupyter notebook that answers: **"Is Philadelphia actually getting safer?"**

**Answer**: ✅ **YES** - Down 15-23% from peak years (2020-2023), though not necessarily below 2015 baseline

---

## Quick Stats

| Metric | 2015 | 2020 | 2023 | 2025 | Change |
|--------|------|------|------|------|--------|
| **Total Crimes** | 176,768 | 134,411 | 169,023 | 152,551 | -13.7% decade |
| **Violent** | 17,812 | 19,467* | 18,616 | 14,910 | -23.4% from peak |
| **Property** | 74,786 | 66,812 | 105,166* | 88,727 | -15.7% from peak |

*Peak years for each category

---

## File Location
📍 `notebooks/philadelphia_safety_trend_analysis.ipynb`

---

## Running It

### 1. Navigate to project
```bash
cd "/Users/dustinober/Projects/Crime Incidents Philadelphia"
```

### 2. Activate environment  
```bash
source .venv/bin/activate
```

### 3. Run Jupyter
```bash
jupyter notebook notebooks/philadelphia_safety_trend_analysis.ipynb
```

---

## What Each Section Does

| # | Section | Output |
|---|---------|--------|
| 1 | Load Data | Dataset overview (3.5M records) |
| 2 | Annual Aggregation | Crime counts by year |
| 3 | Crime Classification | Violent vs. Property split |
| 4 | YoY Trends | Percentage changes & moving averages |
| 5 | Peak Analysis | Peak years & % drop calculations |
| 6 | Visualization | Dual-panel trend chart (saved as PNG) |
| 7 | Insights | Summary stats, findings, verdict |

---

## Main Outputs

### Console Outputs
- Dataset info and validation
- Annual crime aggregations
- Classification distributions
- Peak year identification
- Percentage change analysis
- Multi-perspective insights

### Saved Files
1. **Chart**: `reports/philadelphia_safety_trend_chart.png`
2. **Summary CSV**: `reports/philadelphia_crime_trend_summary.csv`
3. **Trends CSV**: `reports/philadelphia_crime_annual_trends.csv`

---

## Key Insights

✅ **Violent crimes down 23.4%** since 2020 peak  
✅ **Property crimes down 15.7%** since 2023 peak  
✅ **Overall 13.7% decrease** from 2015 to 2025  
✅ **Trend is improving** - past 2-3 years show recovery  
✅ **Perception justified** - city objectively safer than peak years

---

## Data Source

- **File**: `data/crime_incidents_combined.parquet`
- **Records**: 3,496,353 incidents
- **Time Period**: 2006-2026 (notebook filters to 2015-2025)
- **Columns**: 16 features including date, location, crime type

---

## Crime Categories

### Violent Crimes Detected
Aggravated Assault, Robbery, Homicide, Rape, Weapon Violations, Kidnapping, Arson

### Property Crimes Detected
Burglary, Theft, Motor Vehicle Theft, Vandalism/Criminal Mischief, Stolen Property, Receiving Stolen Property, Fraud, Embezzlement, Forgery

---

## Documentation

📖 **Comprehensive Guide**: `notebooks/README_philadelphia_safety_analysis.md`

📊 **Completion Report**: `NOTEBOOK_COMPLETION_REPORT.md`

---

## Requirements

- Python 3.13+
- pandas, numpy, matplotlib, seaborn
- Jupyter notebook
- ~2-3 minutes runtime

---

## Questions?

Refer to:
- `.github/instructions/jupyternotebookprocessing.instructions.md` (project guidelines)
- Inline code comments (each section well documented)
- Notebook markdown cells (explain methodology)

---

**Status**: ✅ Ready to execute  
**Compliance**: ✅ Follows all project guidelines  
**Testing**: ✅ Code validated  
**Documentation**: ✅ Comprehensive

---

*Created: February 1, 2026*  
*Analysis Period: 2015-2025 (11 years)*  
*Answer: Philadelphia IS getting safer (objectively, from peak years)*
