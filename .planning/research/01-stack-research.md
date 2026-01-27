# Stack Research: Crime Data Analysis Standards & Tools

## Research Objective
Investigate standards for crime data analysis, Python tools, and visualization best practices for academic reports.

## Crime Data Analysis Standards

### Industry-Standard Approaches
1. **Uniform Crime Reporting (UCR) Framework** - FBI's standardization for classifying crime
   - 8 major crime categories (murder, rape, robbery, aggravated assault, burglary, theft, motor vehicle theft, arson)
   - Used across US law enforcement; Philadelphia data uses this
   - Academic analysis typically disaggregates to subtype level

2. **Hierarchical Crime Classification**
   - Part I crimes (violent/property) vs Part II
   - Philadelphia's dataset uses UCR general codes
   - Analysis should respect this hierarchy for defensible groupings

3. **Temporal Standards**
   - Day-of-week analysis (accounting for weekend/weekday patterns)
   - Hour-of-day analysis (shift effects, opportunity patterns)
   - Seasonal decomposition (summer peaks, winter troughs common)
   - Year-over-year comparisons with trend isolation
   - Long-term trend analysis (linear regression, LOESS smoothing)

4. **Geographic Analysis Standards**
   - Police districts/sectors as primary aggregation unit
   - Kernel density estimation (KDE) for hotspot mapping
   - Spatial autocorrelation testing (Moran's I, Local Indicators of Spatial Association)
   - Geographic data quality assessment (address geocoding accuracy, coordinate validation)

5. **Statistical Rigor Requirements**
   - Confidence intervals (95% standard) for rate estimates
   - Hypothesis testing before claiming significance
   - Effect size reporting alongside p-values
   - Normality testing before parametric statistics
   - Multiple comparison corrections (Bonferroni, FDR)

### Academic Publication Standards
- Reproducibility: Code and data documented, random seeds set
- Methodology chapter detailing data collection, cleaning, analysis decisions
- Limitations section acknowledging biases, data gaps, generalizability bounds
- Statistical reporting: Mean ± SD or median [IQR], not just "higher/lower"
- Visualization: Publication-quality figures with clear legends, proper scaling

## Python Tools Landscape

### Data Processing & Analysis
| Tool | Purpose | Notes |
|------|---------|-------|
| **pandas** | Tabular data manipulation | Standard; excellent for crime datasets with mixed types |
| **polars** | High-performance DataFrames | Faster than pandas; good for 3.5M+ rows |
| **dask** | Parallel/out-of-core computation | If dataset exceeds RAM (unlikely for 3.5M crime records) |
| **numpy** | Numerical computation | Foundational; used by all statistics libraries |
| **scipy** | Statistical functions | hypothesis testing, distributions, clustering |

### Geospatial Analysis
| Tool | Purpose | Notes |
|------|---------|-------|
| **geopandas** | Spatial DataFrames | Essential for district/PSA aggregation |
| **shapely** | Geometric operations | Underlying geopandas; used for buffering, overlays |
| **folium** | Interactive web maps | Standard for academic dashboards (based on Leaflet) |
| **contextily** | Basemap tiles for mapping | OSM/Stamen/USGS backgrounds for context |
| **scikit-learn** | Clustering (KMeans for hotspots) | Machine learning utilities |

### Statistical Analysis
| Tool | Purpose | Notes |
|------|---------|-------|
| **scipy.stats** | Hypothesis testing, distributions | T-tests, ANOVA, Kruskal-Wallis, chi-square |
| **statsmodels** | Regression, time series analysis | OLS for trend analysis; seasonal decomposition |
| **pingouin** | Effect sizes, multiple comparisons | Cohen's d, eta-squared; correction methods |

### Visualization
| Tool | Purpose | Notes |
|------|---------|-------|
| **matplotlib** | Static publication-quality plots | Industry standard for academic figures |
| **seaborn** | Statistical visualization | Built on matplotlib; excellent for distributions, heatmaps |
| **plotly** | Interactive dashboards | Excellent for exploratory; web-based output |
| **folium** | Interactive geographic maps | Web-based; embeddable in dashboards |
| **altair** | Declarative visualization | Elegant for exploratory analysis; JSON-serializable |

### Report Generation
| Tool | Purpose | Notes |
|------|---------|-------|
| **jupyter** | Notebooks for analysis & documentation | Standard in academic data science |
| **nbconvert** | Convert notebooks to PDF/HTML/markdown | For generating formal reports |
| **pandoc** | Document format conversion | Markdown → PDF via LaTeX |
| **reportlab** | PDF generation programmatically | Fine-grained control for custom layouts |
| **sphinx** | Documentation generation | Build formal technical reports |

## Best Practices for Academic Crime Reports

### Notebook Organization
```
analysis/
├── 01_data_loading.ipynb           # Load, validate, document schema
├── 02_exploratory_analysis.ipynb   # Initial distributions, missing data
├── 03_temporal_analysis.ipynb      # Trends, seasonality, day/hour effects
├── 04_geographic_analysis.ipynb    # Hotspots, clustering, districts
├── 05_offense_breakdown.ipynb      # UCR categorization, severity patterns
├── 06_disparity_analysis.ipynb     # Cross-district comparisons
├── 07_cross_factor_analysis.ipynb  # Correlations, patterns
├── 08_dashboard.ipynb              # Interactive visualizations
├── 09_report_generation.ipynb      # Compile final document
└── data/                           # Processed datasets, intermediate results
```

### Data Documentation
- **Data Dictionary**: Every column documented (source, units, missing value coding, validation rules)
- **Data Quality Report**: Missing value patterns by column and time period
- **Provenance Documentation**: Original source, download date, version, URL
- **Processing Log**: All transformations with justification

### Reproducibility Checklist
- [ ] Random seeds set (pandas random_state, numpy.random.seed)
- [ ] Package versions documented (requirements.txt with pinned versions)
- [ ] Input data versioned (git LFS or documented source)
- [ ] Analysis parameters exposed as cell variables (not hardcoded)
- [ ] Outputs timestamped and versioned
- [ ] README in analysis folder explains execution order

### Visualization Standards for Academic Publication
1. **Figure Quality**: ≥300 DPI for print, vector format where possible (PDF, SVG)
2. **Color**: Colorblind-friendly palettes (viridis, cividis, colorbrewer)
3. **Legends**: Clear, complete; no abbreviations without explanation
4. **Axes**: Labeled with units; proper scale selection
5. **Captions**: Substantive; explain what figure shows and key takeaway
6. **Source**: "Data source: Philadelphia crime incidents, 2006-2026" notation

### Statistical Reporting Examples
- ❌ "Crime increased significantly"
- ✓ "Robbery incidents increased from 12.4 per 100k (95% CI: 12.1-12.7) in 2006 to 14.2 per 100k (95% CI: 13.8-14.6) in 2025, representing a 14.5% increase (p < 0.001)"

## Tool Recommendations for This Project

### Must-Have
- **pandas** + **geopandas** (data manipulation + spatial analysis)
- **scipy.stats** + **statsmodels** (statistical testing + trends)
- **matplotlib** + **seaborn** (publication-quality static plots)
- **plotly** + **folium** (interactive dashboard)
- **jupyter** (analysis environment)

### Nice-to-Have
- **polars** (performance if pandas becomes bottleneck)
- **pingouin** (effect sizes; saves time vs manual calculation)
- **altair** (elegant exploratory visualizations)

### Infrastructure
- Parquet format (existing; good for large datasets)
- Git for version control (already in place)
- nbconvert for notebook → report conversion

## Key Insights

1. **Crime data is never "clean"**: Expect ~5-15% missing coordinates, ~2-8% date anomalies, significant reporting lags. Document all handling decisions.

2. **UCR hierarchy matters**: Don't flatten all crimes to single metric. Stratify by category; patterns differ (robbery is concentrated, larceny is diffuse).

3. **Temporal confounds are real**: Day-of-week effect is massive (~40% weekday/weekend difference for theft). Remove before testing other hypotheses.

4. **Geographic bias is systematic**: Over-policed districts have higher reported crime. Academic analysis must acknowledge reporting bias, not conflate with actual victimization.

5. **Statistical testing can mislead**: With 3.5M observations, even tiny differences achieve p < 0.001. Always report effect sizes and confidence intervals.

6. **Reproducibility tools matter**: Pinned environment, random seeds, documented decisions save months if analysis needs to be re-run or challenged.

---

*Prepared: 2026-01-27 | Evidence Level: Industry standards + academic best practices*
