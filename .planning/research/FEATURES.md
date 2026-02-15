# Feature Landscape

**Domain:** Static website data visualization for Philadelphia crime analysis
**Researched:** February 15, 2026

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Responsive design | Works on mobile/tablet/desktop | Low | Bootstrap/Tailwind CSS |
| Clear navigation | Easy to find different analysis sections | Low | Header nav with dropdowns |
| Data download links | Allow data export for further analysis | Low | JSON/CSV download buttons |
| Basic charts | Line, bar, area charts for trends | Low | Recharts or similar library |
| Data tables | Tabular data presentation | Low | Simple HTML tables with sorting |
| Mobile-friendly | Touch interactions work | Low | Responsive containers |
| Fast loading | Under 3 seconds initial load | Medium | Static generation, optimized assets |
| Data sources cited | Transparency about data origins | Low | Footer with source attribution |
| About page | Methodology and limitations | Low | Static markdown content |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Interactive maps | Spatial crime patterns exploration | High | Mapbox GL with GeoJSON layers |
| Advanced filtering | Date range, district, crime type filters | Medium | URL state management |
| Multiple visualization types | Heatmaps, choropleths, time series | Medium | Specialized chart libraries |
| Data storytelling | Narrative explanations with insights | Low | Descriptive text with charts |
| API endpoints | Programmatic data access | Low | RESTful JSON APIs |
| Embeddable charts | Share individual visualizations | Medium | iframe/embed codes |
| Progressive disclosure | Layer complexity as user explores | Low | Tabbed interfaces, expandable sections |

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Overwhelming dashboards | Cognitive overload, poor UX | Focused single-purpose pages |
| Complex user accounts | Unnecessary friction for public data | Anonymous access only |
| Social features | Comments, ratings, sharing | Simple GitHub link |
| Heavy animations | Slow performance, distraction | Subtle transitions only |
| Real-time updates | Static site constraint, data staleness | Clear "last updated" timestamps |
| Advanced search | Overkill for structured data | Simple category filtering |
| User-generated content | Moderation burden, liability | Read-only data presentation |

## Feature Dependencies

```
Interactive maps → GeoJSON data sources
Advanced filtering → URL state management
Multiple viz types → Chart library selection
API endpoints → Data export pipeline
Embeddable charts → Unique chart IDs
```

## MVP Recommendation

For MVP, prioritize:
1. Responsive design with clear navigation
2. Basic charts (line/bar/area) for trends
3. Interactive maps for spatial data
4. Data download links
5. About page with methodology

Defer to post-MVP:
- Advanced filtering: Add after core navigation works
- Embeddable charts: Nice-to-have for sharing
- Multiple viz types: Expand chart library gradually

## Sources

- Tableau data visualization best practices (chart types, layouts, interactivity)
- Bloomberg coronavirus dashboard (maps, filtering, multiple views)
- The Guardian datablog (data tables, clear sources, narrative)
- FiveThirtyEight (data storytelling, clean design)
- ProPublica data store (API access, downloads)