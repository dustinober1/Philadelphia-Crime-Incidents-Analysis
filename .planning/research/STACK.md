# Technology Stack

**Project:** Philadelphia Crime Incidents Analysis Static Website
**Researched:** February 15, 2026

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Astro | 5.17.x | Static site generator with islands architecture | Optimized for content-driven websites with minimal JavaScript by default; islands enable interactive data visualizations without full SPA overhead; excellent static export for GitHub Pages; faster than alternatives for data-heavy sites |

### Data Visualization Libraries
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| D3.js | 7.9.0 | Custom interactive charts and data visualizations | Industry standard for bespoke data visualizations; unparalleled flexibility for complex crime data charts; mature ecosystem with extensive examples; canvas/SVG rendering options |
| Observable Plot | 0.6.17 | Simplified chart creation | Higher-level API than D3 for common chart types; reduces boilerplate for standard visualizations like trends and comparisons; excellent for dashboards |

### Mapping
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Mapbox GL JS | 3.x | Interactive crime hotspot maps | Professional mapping with vector tiles; supports GeoJSON overlays for district boundaries and crime data; better performance than Leaflet for complex maps; Philadelphia-themed styling options |

### Styling & UI
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Tailwind CSS | 4.x | Utility-first CSS framework | Rapid responsive design for professional appearance; excellent for Philadelphia-themed aesthetic; smaller bundle size than component libraries; consistent spacing and typography for data presentations |

### Build Tool
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Vite | 6.x | Fast build tool and dev server | Bundled with Astro; lightning-fast HMR for development; optimized production builds; tree-shaking for minimal bundle sizes |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Framework | Astro | Next.js static export | Overkill for static site; heavier bundle; slower build times; unnecessary SSR complexity |
| Framework | Astro | SvelteKit | Less mature static export; smaller community for data viz integrations; steeper learning curve |
| Framework | Astro | Eleventy | Less JavaScript ecosystem integration; more complex for interactive islands; slower for large datasets |
| Data Viz | D3.js + Observable Plot | Chart.js only | Less flexible for custom crime data visualizations; canvas-only rendering limits styling options |
| Data Viz | D3.js + Observable Plot | Vega-Lite | JSON specification approach less familiar to JavaScript developers; additional compilation step |
| Mapping | Mapbox GL JS | Leaflet | Less performant for complex overlays; fewer styling options; dated appearance |
| Styling | Tailwind CSS | Bootstrap | Larger bundle size; less flexible for custom Philadelphia theming; component bloat |

## Installation

```bash
# Create new Astro project
npm create astro@latest philadelphia-crime-viz --template minimal

# Install data visualization dependencies
npm install d3 @observablehq/plot mapbox-gl

# Install styling
npm install tailwindcss @tailwindcss/vite

# Install dev dependencies for build optimization
npm install -D @astrojs/tailwind autoprefixer
```

## Sources

- [Astro releases](https://github.com/withastro/astro/releases) - Latest stable 5.17.x as of Feb 2026
- [D3.js releases](https://github.com/d3/d3/releases) - v7.9.0 from Mar 2024, stable
- [Observable Plot releases](https://github.com/observablehq/plot/releases) - v0.6.17 from Feb 2025
- [Chart.js documentation](https://www.chartjs.org/docs/latest/) - v4.5.1 as of Oct 2025
- [Mapbox GL JS API](https://docs.mapbox.com/mapbox-gl-js/api/) - v3.x current
- [Tailwind CSS installation](https://tailwindcss.com/docs/installation) - v4.x current
- [Jamstack generators](https://jamstack.org/generators/) - Ecosystem survey showing Astro dominance for 2025</content>
<parameter name="filePath">/Users/dustinober/Projects/Philadelphia-Crime-Incidents-Analysis/.planning/research/STACK.md