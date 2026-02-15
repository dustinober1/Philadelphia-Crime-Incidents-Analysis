# Architecture Patterns

**Domain:** Static data visualization website
**Researched:** February 15, 2026

## Recommended Architecture

For professional data visualization websites, especially static sites hosted on GitHub Pages, the typical architecture follows a component-based structure with clear separation of concerns:

- **Presentation Layer**: HTML/CSS for layout and styling
- **Data Layer**: JSON/GeoJSON files for data storage
- **Visualization Layer**: JavaScript libraries for rendering charts/maps
- **Interaction Layer**: Event handlers for user interactions

Data flows from static files → JavaScript loaders → visualization components → DOM updates.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| Layout Components | Page structure, navigation, responsive grid | All other components |
| Data Loader | Fetch and parse JSON/GeoJSON data files | Visualization components |
| Visualization Components | Render charts, maps, tables using libraries | Data loader, interaction handlers |
| Interaction Components | Handle user inputs (filters, tooltips, legends) | Visualization components |
| UI Components | Buttons, modals, form controls | Layout, interaction components |

### Data Flow

1. **Static Data Files** (JSON/GeoJSON) → Loaded at build time or runtime via fetch
2. **Data Processing** → Parsed and transformed in JavaScript
3. **Visualization Rendering** → Libraries like D3.js, Chart.js, Mapbox create SVG/Canvas elements
4. **User Interactions** → Events trigger data filtering/re-rendering
5. **DOM Updates** → Efficient updates using virtual DOM (React) or direct manipulation (vanilla JS)

Direction: Unidirectional data flow preferred, with state management for complex interactions.

## Patterns to Follow

### Pattern 1: Component-Based Architecture
**What:** Modular components for each visualization type (charts, maps, tables)
**When:** Building scalable, maintainable data viz sites
**Example:**
```javascript
// Chart component
const CrimeTrendsChart = ({ data, filters }) => {
  useEffect(() => {
    // Render chart logic
  }, [data, filters]);
  return <div ref={chartRef} />;
}
```

### Pattern 2: Responsive Design First
**What:** Mobile-first responsive layouts with adaptive chart containers
**When:** Public-facing websites accessed on multiple devices
**Example:** CSS Grid/Flexbox for fluid layouts that work on mobile/tablet/desktop

### Pattern 3: Progressive Enhancement
**What:** Basic functionality without JavaScript, enhanced with interactions
**When:** Accessibility and performance are critical

## Anti-Patterns to Avoid

### Anti-Pattern 1: Monolithic JavaScript Files
**What:** All visualization code in one large, unorganized file
**Why bad:** Hard to maintain, poor performance, difficult debugging
**Instead:** Modular components with code splitting and lazy loading

### Anti-Pattern 2: Synchronous Data Loading
**What:** Blocking page load while waiting for data to fetch
**Why bad:** Poor user experience, slow perceived performance
**Instead:** Asynchronous loading with loading states and error handling

### Anti-Pattern 3: Over-Complex Interactions
**What:** Too many filters, controls, and options overwhelming users
**Why bad:** High cognitive load, poor usability, feature fatigue
**Instead:** Progressive disclosure - show basic view first, advanced options on demand

## Scalability Considerations

| Concern | Small Site (<10 visualizations) | Medium Site (10-50 visualizations) | Large Site (>50 visualizations) |
|---------|--------------------------------|-----------------------------------|-------------------------------|
| Bundle Size | Single JavaScript file | Code splitting by route/page | Lazy loading of components |
| Data Loading | Inline JSON in HTML | Static JSON files | CDN-hosted data files |
| Performance | Direct DOM manipulation | Virtual DOM (React) | WebGL acceleration for complex viz |
| Maintenance | Manual updates | Component library | Full design system with Storybook |

## Build Order Implications

Suggested build order based on component dependencies:

1. **Foundation** (Layout, styling, basic HTML structure) - No dependencies, can be built first
2. **Data Infrastructure** (Loaders, parsers, data transformation utilities) - Depends on data format decisions
3. **Core Visualizations** (Basic charts, maps, tables) - Depends on data infrastructure being available
4. **Interactions** (Filters, tooltips, legends, user controls) - Depends on visualization components
5. **Advanced Features** (Animations, complex multi-chart interactions) - Depends on all core components

This order minimizes rework as data schemas evolve and visualization requirements become clearer during development.

## Sources

- WebSearch: "data visualization website architecture 2024" (MEDIUM confidence - multiple sources agree on component separation and responsive design)
- Official Docs: Next.js static export documentation (HIGH confidence for static site generation)
- Context7: React component patterns for data visualization (HIGH confidence)
- Community: D3.js and Chart.js examples on GitHub (MEDIUM confidence for visualization patterns)
- Industry: Analysis of NYT interactive features and Guardian data journalism (MEDIUM confidence for professional patterns)</content>
<parameter name="filePath">/Users/dustinober/Projects/Philadelphia-Crime-Incidents-Analysis/.planning/research/ARCHITECTURE.md