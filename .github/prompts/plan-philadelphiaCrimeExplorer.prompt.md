## Plan: Philadelphia Crime Explorer — Web Conversion

**TL;DR:** Convert the existing CLI-driven crime analysis project into a public-facing Next.js website backed by a FastAPI server on Cloud Run, with Firestore for Q&A, Mapbox GL JS for interactive maps, and all hosted on Firebase. The Python analysis pipeline stays intact — a new "data export" step pre-aggregates results into API-ready JSON. Visitors explore interactive charts/maps and submit questions you answer via a simple admin page.

**Architecture Overview:**
```
[Firebase Hosting]          [Cloud Run]              [Firestore]
  Next.js static    →→→    FastAPI API     →→→     Q&A questions
  export (SSG)              serves pre-agg          pre-agg data cache
                            JSON + GeoJSON
                            
[Mapbox GL JS]             [Existing Python]
  Interactive maps          analysis/ pipeline
  choropleth, heat          → new export commands
```

---

**Steps**

### Phase 1: Project Scaffolding & Monorepo Setup (Days 1–2)

1. Create a monorepo structure at the project root. Add a `web/` directory for the frontend and an `api/` directory for the FastAPI backend. Keep the existing `analysis/`, `data/`, and `reports/` directories untouched.

   ```
   web/                    ← Next.js app
   api/                    ← FastAPI app
   analysis/               ← existing (unchanged)
   data/                   ← existing (unchanged)
   pipeline/               ← new: data export scripts
   ```

2. Initialize the Next.js app inside `web/` using `npx create-next-app@latest web --typescript --tailwind --app --src-dir`. Choose App Router, TypeScript, Tailwind CSS, ESLint.

3. Initialize the FastAPI app inside `api/` with this structure:
   - `api/main.py` — FastAPI app entry point with CORS middleware
   - `api/routers/trends.py` — endpoints for chief-level data
   - `api/routers/spatial.py` — endpoints for maps/GeoJSON
   - `api/routers/policy.py` — endpoints for policy analyses
   - `api/routers/questions.py` — Q&A CRUD with Firestore
   - `api/routers/forecasting.py` — forecast data
   - `api/models/schemas.py` — Pydantic response models
   - `api/services/data_loader.py` — loads pre-aggregated JSON
   - `api/requirements.txt` — FastAPI, uvicorn, firebase-admin, pydantic
   - `api/Dockerfile` — Cloud Run container

4. Create `pipeline/` directory with a `export_data.py` script that runs your existing analysis functions and writes JSON files to `api/data/` for the API to serve. This is the bridge between your analysis code and the web.

5. Add a root-level `Makefile` or `justfile` with commands: `make dev-web`, `make dev-api`, `make export-data`, `make deploy`.

---

### Phase 2: Data Export Pipeline (Days 3–5)

Build a Python script at `pipeline/export_data.py` that reuses your existing `analysis/` modules to pre-aggregate data into JSON files the API will serve. This runs manually whenever you want to refresh site data.

6. **Trends export** — Use `analysis.data.loading.load_crime_data()` and `analysis.data.preprocessing.aggregate_by_period()` to produce:
   - `api/data/annual_trends.json` — yearly counts by category (Violent/Property/Other), ~20 rows
   - `api/data/monthly_trends.json` — monthly time series by category, ~240 rows
   - `api/data/covid_comparison.json` — pre/during/post COVID aggregated stats

7. **Seasonality export** — Using `analysis.utils.temporal.extract_temporal_features()`:
   - `api/data/seasonality.json` — crime counts by month, day-of-week, and hour
   - `api/data/robbery_heatmap.json` — hour × day-of-week matrix for the Patrol robbery heatmap

8. **Spatial export** — Using the existing GeoJSON files and `analysis.utils.spatial`:
   - Copy `data/boundaries/police_districts.geojson` → `api/data/geo/districts.geojson` (enrich with severity scores from the analysis)
   - Copy `data/boundaries/census_tracts_pop.geojson` → `api/data/geo/tracts.geojson` (enrich with crime rates)
   - Generate `api/data/geo/hotspot_centroids.geojson` from the DBSCAN pipeline
   - Generate `api/data/geo/corridors.geojson` for vehicle crime corridors
   - **Important**: Strip individual incident point data for privacy — only serve aggregated centroids and polygons

9. **Policy export** — Using existing UCR filtering logic from `analysis/cli/policy.py`:
   - `api/data/retail_theft_trend.json` — monthly retail theft counts
   - `api/data/vehicle_crime_trend.json` — monthly vehicle crime counts
   - `api/data/crime_composition.json` — top crime categories by year
   - `api/data/event_impact.json` — event-day vs control-day crime comparisons

10. **Forecasting export** — Run the Prophet forecast and save:
    - `api/data/forecast.json` — historical + predicted values with confidence intervals
    - `api/data/classification_features.json` — top feature importances for violence classification

11. **Metadata export**:
    - `api/data/metadata.json` — dataset date range, total incidents, last updated timestamp, data source attribution

12. Add a `--output-dir` option to the export script so it can target different destinations. Run this script with `python -m pipeline.export_data` and commit the resulting JSON files (they'll be small, <5MB total).

---

### Phase 3: FastAPI Backend (Days 6–9)

13. **Entry point** `api/main.py` — Create the FastAPI app with:
    - CORS middleware allowing your Firebase Hosting domain
    - Lifespan handler that loads all JSON files into memory on startup (they're small)
    - Health check endpoint `GET /api/health`
    - Include all routers with `/api/v1` prefix

14. **Trends router** `api/routers/trends.py`:
    - `GET /api/v1/trends/annual` — returns annual crime counts, supports `?category=Violent` filter
    - `GET /api/v1/trends/monthly` — returns monthly time series, supports `?start_year=2020&end_year=2024`
    - `GET /api/v1/trends/covid` — returns COVID comparison data
    - `GET /api/v1/trends/seasonality` — returns seasonal patterns

15. **Spatial router** `api/routers/spatial.py`:
    - `GET /api/v1/spatial/districts` — returns districts GeoJSON with severity scores
    - `GET /api/v1/spatial/tracts` — returns census tracts with crime rates
    - `GET /api/v1/spatial/hotspots` — returns DBSCAN cluster centroids
    - `GET /api/v1/spatial/corridors` — returns vehicle crime corridors

16. **Policy router** `api/routers/policy.py`:
    - `GET /api/v1/policy/retail-theft` — retail theft trend data
    - `GET /api/v1/policy/vehicle-crimes` — vehicle crime trend data
    - `GET /api/v1/policy/composition` — crime category composition
    - `GET /api/v1/policy/events` — event impact analysis

17. **Forecasting router** `api/routers/forecasting.py`:
    - `GET /api/v1/forecasting/time-series` — forecast with confidence intervals
    - `GET /api/v1/forecasting/classification` — violence classification features

18. **Questions router** `api/routers/questions.py` — Firestore integration:
    - `POST /api/v1/questions` — submit a question (fields: `name`, `email` (optional), `question_text`, `created_at`). Add basic rate limiting (e.g., 5 per IP per hour) and input validation (max 1000 chars).
    - `GET /api/v1/questions?status=answered` — list answered questions for public display
    - `GET /api/v1/questions?status=pending` — list pending questions (admin only, protect with a simple API key header `X-Admin-Key`)
    - `PATCH /api/v1/questions/{id}` — update question with answer text (admin only)

19. **Pydantic response models** `api/models/schemas.py` — Define typed response models for every endpoint: `TrendDataPoint`, `SeasonalityData`, `DistrictGeoJSON`, `QuestionSubmission`, `QuestionResponse`, etc. Reuse the color constants from `analysis/config.py`.

20. **Dockerfile** `api/Dockerfile` — Python 3.12 slim image (not 3.14 — use a stable release for production), copy `api/` and `api/data/`, install requirements, run `uvicorn api.main:app --host 0.0.0.0 --port 8080`.

21. **Local dev** — Add a `docker-compose.yml` at root with the API service + hot reload, and document how to run `uvicorn api.main:app --reload` directly.

---

### Phase 4: Firebase Setup (Days 10–11)

22. Initialize Firebase in the project root: `firebase init`. Select **Hosting** (for Next.js static export) and **Firestore** (for Q&A). Choose an existing project or create `philly-crime-explorer`.

23. **Firestore security rules** `firestore.rules` — Since no auth:
    - Collection `questions`: allow public `create` (with field validation — only `name`, `email`, `question_text` fields, `question_text` max 1000 chars). Allow public `read` where `status == "answered"`. Deny all other operations from clients.
    - The FastAPI backend uses Firebase Admin SDK (service account) to bypass rules for admin operations (reading pending, updating with answers).

24. **Firestore indexes** — Create a composite index on `questions` collection: `status` (ASC) + `created_at` (DESC) for the public answered-questions listing.

25. **Firebase Hosting config** `firebase.json`:
    - Set `"public": "web/out"` (Next.js static export output)
    - Add rewrite rules to proxy `/api/**` requests to Cloud Run
    - Configure caching headers: 1 hour for JSON data, 1 year for hashed static assets

26. **Deploy FastAPI to Cloud Run**: 
    - `gcloud run deploy philly-crime-api --source api/ --region us-east1 --allow-unauthenticated`
    - Set environment variables: `GOOGLE_CLOUD_PROJECT`, `ADMIN_API_KEY` (a secret you generate)
    - Configure Firebase Hosting to rewrite `/api/**` → Cloud Run service URL

---

### Phase 5: Next.js Frontend — Layout & Navigation (Days 12–15)

27. **Design system** — Install dependencies in `web/`:
    - `recharts` for interactive charts (lightweight, React-native, better than Plotly for Next.js SSG)
    - `mapbox-gl` + `react-map-gl` for Mapbox integration
    - `@headlessui/react` for accessible UI components (modals, dropdowns)
    - `lucide-react` for icons
    - `clsx` for conditional class names
    - `swr` for client-side data fetching with caching

28. **Layout** `web/src/app/layout.tsx`:
    - Responsive header with site name "Philadelphia Crime Explorer", navigation links
    - Footer with data source attribution ("Source: Philadelphia Police Department, OpenDataPhilly"), last-updated date from metadata API, link to the GitHub repo
    - Use Tailwind CSS with a custom color palette matching your existing brand colors: Violent `#E63946`, Property `#457B9D`, Other `#A8DADC`, plus neutral grays

29. **Navigation pages** — 6 pages total:
    - `/` — Home / Dashboard (overview stats + key charts)
    - `/trends` — Crime Trends (annual, monthly, COVID, seasonality)
    - `/map` — Interactive Map (hotspots, districts, tracts, corridors)
    - `/policy` — Policy Analysis (retail theft, vehicle crimes, composition, events)
    - `/forecast` — Forecasting (time series predictions, classification insights)
    - `/questions` — Community Q&A (browse answered, submit new)

30. **Shared components** in `web/src/components/`:
    - `ChartCard.tsx` — wrapper with title, description, loading state, and the chart
    - `StatCard.tsx` — summary statistic card (e.g., "Total Incidents: 1.5M")
    - `MapContainer.tsx` — Mapbox GL wrapper with standard Philadelphia viewport
    - `LoadingSpinner.tsx` — consistent loading state
    - `QuestionForm.tsx` — question submission form
    - `QuestionList.tsx` — answered questions display
    - `CategoryBadge.tsx` — colored badge for Violent/Property/Other
    - `DateRangeFilter.tsx` — year range slider or dropdown for filtering charts
    - `Navbar.tsx`, `Footer.tsx` — site-wide navigation

31. **API client** `web/src/lib/api.ts` — Type-safe fetch wrapper for all API endpoints. Define TypeScript interfaces matching the Pydantic response models. Use SWR hooks for data fetching with stale-while-revalidate caching.

---

### Phase 6: Next.js Frontend — Dashboard & Trends Page (Days 16–20)

32. **Home page** `/` `web/src/app/page.tsx`:
    - Hero section: "Explore Crime in Philadelphia" with brief description
    - 4 `StatCard` components: total incidents, date range covered, number of districts, latest year's violent crime count
    - A small annual trend line chart (Recharts `LineChart`) showing the last 10 years
    - "What's happening" section: 3 key findings in plain English (e.g., "Violent crime dropped 12% since 2022")
    - CTA cards linking to Trends, Map, Policy, Forecast, and Q&A pages
    - Mobile-responsive grid layout using Tailwind

33. **Trends page** `/trends` `web/src/app/trends/page.tsx`:
    - **Annual trends chart**: Recharts `LineChart` with 3 lines (Violent, Property, Other), year selector, hover tooltips showing exact counts. Use the `#E63946` / `#457B9D` / `#A8DADC` colors from `analysis/config.py`.
    - **Monthly trends chart**: Recharts `AreaChart` with date range filter component, showing monthly granularity
    - **COVID comparison**: Recharts `BarChart` with 3 grouped bars (Pre/During/Post), annotation explaining the date ranges
    - **Seasonality heatmap**: A custom grid component showing crime by month (rows) × category (columns), colored by intensity. Alternatively use Recharts `ScatterChart` with custom cells.
    - **Robbery hour×day heatmap**: Grid component with 24 rows (hours) × 7 columns (days), color intensity = crime count. Add a color scale legend.

34. Each chart section should include:
    - A plain-English insight paragraph below the chart (generated from the data or hardcoded)
    - Data source note
    - "Download data" link to the JSON endpoint

---

### Phase 7: Next.js Frontend — Interactive Map Page (Days 21–26)

35. **Map page** `/map` `web/src/app/map/page.tsx`:
    - Full-width Mapbox GL map centered on Philadelphia (lat 39.95, lng -75.16, zoom 11)
    - Layer toggle panel (sidebar or floating) with checkboxes for:
      - **District severity choropleth** — polygon fill colored by severity score
      - **Census tract crime rates** — polygon fill colored by per-capita rate
      - **Hotspot clusters** — circle markers at DBSCAN centroids, sized by cluster count
      - **Vehicle crime corridors** — line layer showing corridor risk levels
    - Only one polygon layer visible at a time (districts OR tracts), but hotspots can overlay

36. **Map interactions**:
    - Click a district polygon → sidebar shows district name, severity score, top crime types, total incidents
    - Click a census tract → popup shows tract ID, population, crime rate, category breakdown
    - Click a hotspot marker → popup shows cluster size, top crime type, centroid coordinates
    - Hover = highlight effect on polygons
    - Mapbox navigation controls (zoom, compass, fullscreen)

37. **Map technical details**:
    - Load GeoJSON data from API endpoints
    - Use `react-map-gl` `Source` and `Layer` components for each data layer
    - Style layers using Mapbox expressions for data-driven coloring
    - Add a color scale legend component that updates based on active layer
    - Set Mapbox style to `mapbox://styles/mapbox/light-v11` for clean basemap

38. Add a Mapbox access token as an environment variable `NEXT_PUBLIC_MAPBOX_TOKEN` in `web/.env.local`. Document how to get a free Mapbox token in the README.

---

### Phase 8: Next.js Frontend — Policy & Forecast Pages (Days 27–31)

39. **Policy page** `/policy` `web/src/app/policy/page.tsx`:
    - **Retail theft trends**: Recharts `LineChart` with monthly data, optional year-over-year comparison toggle
    - **Vehicle crime trends**: Recharts `LineChart` similar to retail theft
    - **Crime composition**: Recharts `StackedBarChart` showing top categories by year, or a `Treemap` for the latest year
    - **Event impact**: Recharts `BarChart` comparing event days vs. control days, with error bars. Include a short explanation of the methodology (matched control days from `analysis/event_utils.py`)
    - Each section has a summary paragraph with key findings

40. **Forecast page** `/forecast` `web/src/app/forecast/page.tsx`:
    - **Time series forecast**: Recharts `ComposedChart` with:
      - Historical data as a solid line
      - Forecast as a dashed line
      - Confidence intervals as a shaded `Area`
      - Clear label showing "Historical" vs "Forecast" regions
    - **Model description**: Plain-English explanation of Prophet model, what it predicts, and caveats
    - **Violence classification insights**: Horizontal bar chart of top features (from SHAP/feature importance), with explanations of what each feature means
    - **Methodology note** at bottom explaining limitations and that these are statistical models, not guarantees

---

### Phase 9: Q&A Feature (Days 32–35)

41. **Questions page** `/questions` `web/src/app/questions/page.tsx`:
    - **"Ask a Question" section** at top:
      - Form with fields: Name (required), Email (optional, noted as "only for follow-up, not displayed"), Question (required, textarea, max 1000 chars)
      - Submit button → `POST /api/v1/questions`
      - Success message: "Thanks! Your question has been submitted and we'll answer it soon."
      - Client-side validation + honeypot field for basic spam prevention
    - **"Answered Questions" section** below:
      - List of answered Q&A pairs, newest first
      - Each shows: question text, asker's first name, date asked, answer text, date answered
      - Paginated (10 per page)
      - If no answered questions yet, show "Questions are being reviewed — check back soon!"

42. **Admin page** `/admin` `web/src/app/admin/page.tsx`:
    - Simple password-protected page (hardcoded password check or env var `NEXT_PUBLIC_ADMIN_PASSWORD` — this is a low-stakes admin, not a banking app)
    - Lists pending questions with answer textarea for each
    - "Publish Answer" button → `PATCH /api/v1/questions/{id}` with `X-Admin-Key` header
    - "Delete" button for spam
    - Answered questions tab to review past answers

43. **Spam prevention** — In the FastAPI questions endpoint:
    - Rate limit by IP (5 submissions per hour, use an in-memory dict or Firestore counter)
    - Reject if `question_text` is empty or >1000 chars
    - Honeypot hidden field — if filled, silently reject
    - Optional: reject common spam patterns (URLs, all-caps)

---

### Phase 10: SEO, Performance & Polish (Days 36–39)

44. **SEO optimization**:
    - Add `metadata` exports in each page's `page.tsx` with title, description, Open Graph tags
    - Create `web/src/app/sitemap.ts` generating sitemap.xml
    - Add `web/src/app/robots.ts` allowing all crawlers
    - Page titles: "Philadelphia Crime Explorer | Trends", "... | Interactive Map", etc.
    - Meta descriptions summarizing each page's content for Google

45. **Performance**:
    - Use Next.js static export (`output: 'export'` in `web/next.config.ts`) — all pages are statically generated at build time
    - Lazy-load the Mapbox GL component with `next/dynamic` and `ssr: false` (Mapbox needs browser APIs)
    - Lazy-load Recharts components that are below the fold
    - Compress GeoJSON files — the district and tract files can be large; use TopoJSON or simplify geometries with a build step
    - Add `loading.tsx` skeleton components for each page

46. **Responsive design**:
    - Test all pages at mobile (375px), tablet (768px), and desktop (1280px)
    - Charts resize with container using Recharts `ResponsiveContainer`
    - Map takes full width on mobile, with layer controls in a collapsible drawer
    - Navigation collapses to hamburger menu on mobile

47. **Accessibility**:
    - All charts have `aria-label` descriptions
    - Color choices meet WCAG 2.1 AA contrast ratios (verify `#E63946` on white → 4.5:1 ✓)
    - Keyboard navigable map controls
    - Form labels, error messages, and focus management on the Q&A form

48. **About / Methodology page** `/about`:
    - Data source attribution (Philadelphia Police Department, OpenDataPhilly)
    - Dataset description (date range, ~1.5M incidents, what's included)
    - Methodology notes for each analysis type
    - Limitations and caveats
    - Link to GitHub repository
    - Your name / contact info

---

### Phase 11: Deployment Pipeline (Days 40–42)

49. **Firebase Hosting deployment**:
    - In `web/`, run `npm run build` (Next.js static export → `web/out/`)
    - `firebase deploy --only hosting` deploys the static site

50. **Cloud Run deployment**:
    - Create a `cloudbuild.yaml` or use `gcloud run deploy` to build and deploy the API container
    - Set environment variables on Cloud Run: `GOOGLE_CLOUD_PROJECT`, `ADMIN_API_KEY`, `FIRESTORE_COLLECTION_QUESTIONS=questions`
    - Configure Cloud Run to allow unauthenticated access (public API)
    - Set Cloud Run region to `us-east1` (closest to Philadelphia)

51. **Firebase Hosting rewrites** in `firebase.json`:
    ```json
    "rewrites": [
      { "source": "/api/**", "run": { "serviceId": "philly-crime-api", "region": "us-east1" } },
      { "source": "**", "destination": "/index.html" }
    ]
    ```
    This routes API calls to Cloud Run and everything else to the Next.js static site.

52. **CI/CD** — Create `.github/workflows/deploy.yml`:
    - On push to `main`: build Next.js → deploy to Firebase Hosting, build Docker → deploy to Cloud Run
    - On PR: run lint + type-check for `web/` code
    - Manual trigger for data refresh: run `pipeline/export_data.py` → rebuild API container → deploy

53. **Custom domain** — In Firebase Hosting settings, connect your domain (e.g., `phillycrime.info` or similar). Firebase provides free SSL.

---

### Phase 12: Data Refresh Workflow (Day 43)

54. **Manual refresh process** — Document this in `README.md`:
    1. Download updated crime data (from OpenDataPhilly) → replace `data/crime_incidents_combined.parquet`
    2. Run `python -m pipeline.export_data` to regenerate all JSON files
    3. Run `docker build -t philly-crime-api api/` and deploy to Cloud Run
    4. The site automatically shows updated data; the metadata.json `last_updated` field reflects the new date

55. **Data freshness indicator** — The footer of every page shows "Data last updated: {date}" pulled from the `/api/v1/metadata` endpoint.

---

### Verification Checklist

- **API**: Run `uvicorn api.main:app --reload` locally, hit each endpoint with `curl` or the auto-generated Swagger docs at `http://localhost:8000/docs`
- **Frontend**: Run `npm run dev` in `web/`, verify all 6 pages render with sample data, test mobile responsiveness in Chrome DevTools
- **Maps**: Verify all 4 layers load, click interactions work, and legend updates correctly
- **Q&A flow**: Submit a test question, verify it appears in Firestore, answer it via admin page, verify it appears on public questions page
- **Deployment**: Deploy to Firebase + Cloud Run staging project first, test all endpoints via the Firebase Hosting URL, verify rewrites route `/api/**` to Cloud Run
- **Performance**: Run Lighthouse audit — target 90+ on Performance, Accessibility, SEO
- **Data pipeline**: Run `export_data.py` from scratch, verify all JSON files are generated and valid

---

### Key Decisions

- **Recharts over Plotly.js**: Recharts is smaller (40KB vs 1MB+), React-native, and works perfectly with Next.js static export. Plotly is overkill for pre-aggregated data display.
- **Static export over SSR**: Since data refreshes manually, there's no need for server-side rendering. Static export = fastest possible load times and simplest Firebase Hosting deployment.
- **FastAPI on Cloud Run over Firebase Functions**: FastAPI gives you auto-generated API docs (Swagger), native Pydantic validation matching your existing codebase, and no cold start issues with Cloud Run min-instances.
- **Pre-aggregated JSON over live queries**: The 192MB parquet file stays on your machine. Only pre-computed, small JSON (~5MB total) goes to production. This means near-instant API responses and zero risk of exposing raw incident data.
- **No user auth**: Keeps the barrier to entry zero. Admin operations protected by a simple API key header — adequate for a single-admin site.
- **Honeypot + rate limiting over CAPTCHA**: Better user experience, sufficient spam prevention for a niche site. Can add reCAPTCHA later if spam becomes a problem.
