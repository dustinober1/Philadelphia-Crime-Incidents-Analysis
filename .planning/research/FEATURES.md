# FEATURES.md

Project Research — Features matrix for Philadelphia crime analysis

Table Stakes (must-have):
- Year-over-year trend analyses for Violent vs Property crime
- Monthly seasonality analysis and month-level visualizations
- Geospatial hotspot detection and district-level summaries
- Ability to filter and analyze by offense codes (retail theft, robbery, vehicle crimes)
- Reproducible notebooks with pinned environment and exportable report artifacts

Differentiators (competitive/insightful):
- Weighted severity scoring and choropleth visualizations for policy prioritization
- Hour × Weekday heatmaps for specific offenses (robbery) to inform shift timing
- Integrated weather correlation analysis (hourly temperature joins)
- Per-tract crime rates normalized by census population
- Event-impact analysis (sports games, holidays) for localized effect studies

Anti-features (deliberately excluded):
- Real-time dashboards or streaming ingestion (out of scope for v1)
- Predictive policing systems that output patrol recommendations in an automated manner (ethical/policy risk)

Complexity notes & dependencies:
- Weather joins require hourly alignment and may need imputation for missing hours
- Census tract joins require accurate CRS alignment and tract shapefiles
- Severity scoring needs clear weight definitions agreed with stakeholders (suggest starting weights and iterate)
