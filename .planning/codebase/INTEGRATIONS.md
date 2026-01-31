# External Integrations

**Analysis Date:** 2026-01-30

## External APIs

**None Currently Used**

The project operates entirely on local data. No external API calls are made in the current codebase.

**Potential Future Integrations:**
- Philadelphia open data portal for updated crime data
- Geocoding services for address validation (not currently implemented)
- Weather data APIs for seasonal correlation analysis

## Databases

**File-Based Data Storage Only**

| Source | Type | Location | Purpose |
|--------|------|----------|---------|
| Crime Incidents | Parquet file | `data/crime_incidents_combined.parquet` | Main dataset (~3.5M records) |

**No Database Connections:**
- No SQL/NoSQL databases
- No ORM (SQLAlchemy, Django ORM)
- No database connection pooling
- All data loaded via pandas `read_parquet()`

## Authentication

**Not Applicable**

- No user authentication system
- No API keys or secrets
- No OAuth/OIDC
- No session management

This is a local analysis project with no web interface or user accounts.

## Webhooks

**None**

- No webhook receivers
- No webhook senders
- No event-driven integrations

## File I/O Operations

**Read Operations:**
| Format | Library | Source |
|--------|---------|--------|
| Parquet | pandas/pyarrow | `data/crime_incidents_combined.parquet` |

**Write Operations:**
| Format | Destination | Purpose |
|--------|-------------|---------|
| Markdown | `reports/*.md` | Analysis reports |
| PNG (base64) | Embedded in markdown | Charts and graphs |
| HTML | `reports/*.html` | Interactive maps |
| Parquet | `data/processed/` | Cleaned datasets |

## Third-Party Services

**Geographic Data:**
- **folium** - Uses OpenStreetMap tiles for map backgrounds
  - No API key required for basic tiles
  - Leaflet.js client-side rendering

**Data Processing Libraries:**
- **scikit-learn** - DBSCAN clustering algorithm
  - Local computation only
- **scipy** - Statistical functions
  - Local computation only

## Local Dependencies

**Python Standard Library:**
- `pathlib` - Path operations
- `datetime` - Date/time handling
- `io` - Base64 encoding for images
- `json` - JSON serialization

**No External Service Dependencies:**
- All computation is local
- No cloud services (AWS, GCP, Azure)
- No CDN usage
- No external analytics

## Data Pipeline

**Current Flow:**
```
Local Parquet File
    ↓
pandas.read_parquet()
    ↓
In-memory DataFrame
    ↓
Analysis & Visualization
    ↓
Markdown + HTML Reports
```

**No streaming or real-time data processing.**

---

*Integrations analysis: 2026-01-30*
