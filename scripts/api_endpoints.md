# High-Value API Endpoints for Validation

Based on analysis of all API router files, here are the high-value endpoints that should be validated:

## Trends Endpoints (/api/v1/trends)
- `/api/v1/trends/annual` - Annual crime trends data
- `/api/v1/trends/monthly` - Monthly crime trends data
- `/api/v1/trends/covid` - COVID-19 impact comparison data
- `/api/v1/trends/seasonality` - Seasonal pattern data
- `/api/v1/trends/robbery-heatmap` - Robbery heatmap data

## Spatial Endpoints (/api/v1/spatial)
- `/api/v1/spatial/districts` - District boundaries GeoJSON
- `/api/v1/spatial/tracts` - Census tract boundaries GeoJSON
- `/api/v1/spatial/hotspots` - Crime hotspot centroids GeoJSON
- `/api/v1/spatial/corridors` - Crime corridor GeoJSON

## Policy Endpoints (/api/v1/policy)
- `/api/v1/policy/retail-theft` - Retail theft trend data
- `/api/v1/policy/vehicle-crimes` - Vehicle crime trend data
- `/api/v1/policy/composition` - Crime composition data
- `/api/v1/policy/events` - Event impact data

## Forecasting Endpoints (/api/v1/forecasting)
- `/api/v1/forecasting/time-series` - Time series forecast data
- `/api/v1/forecasting/classification` - Classification features data

## Questions Endpoints (/api/v1/questions)
- `/api/v1/questions` - Community Q&A functionality

## Metadata Endpoints (/api/v1/metadata)
- `/api/v1/metadata` - System metadata

## Selected High-Value Endpoints for Validation
Based on usage frequency and business importance, the following endpoints are prioritized for validation:

1. `/api/v1/trends/annual` - Critical for trend analysis
2. `/api/v1/spatial/districts` - Essential for spatial analysis
3. `/api/v1/policy/retail-theft` - Important for policy decisions
4. `/api/v1/forecasting/time-series` - Key for forecasting capabilities
5. `/api/v1/trends/monthly` - Important for monthly trend tracking
6. `/api/v1/spatial/hotspots` - Critical for hotspot identification
7. `/api/v1/metadata` - Essential for system status

## Expected Response Structures
- Trends endpoints typically return arrays of objects with date/category and count/value fields
- Spatial endpoints return GeoJSON objects with features array
- Policy endpoints return arrays of objects with trend/impact data
- Forecasting endpoints return objects with prediction data and confidence intervals
- Metadata endpoint returns system information object

## Recommended Timeout Values
- Simple endpoints (metadata): 2 seconds
- Medium complexity (trends, policy): 3 seconds
- Complex endpoints (spatial, forecasting): 5 seconds