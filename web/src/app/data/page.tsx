"use client";

import useSWR from "swr";

import { fetcher } from "@/lib/api";
import { DownloadButton } from "@/components/DownloadButton";

type DatasetCardProps = {
  title: string;
  description: string;
  data: Record<string, unknown>[] | undefined;
  filename: string;
  format?: "geojson" | "standard";
};

function DatasetCard({ title, description, data, filename, format = "standard" }: DatasetCardProps) {
  const isLoading = !data;
  const isEmpty = data && data.length === 0;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-sm text-slate-600 mb-4">{description}</p>
      
      {isLoading ? (
        <div className="flex gap-2">
          <div className="h-9 w-28 animate-pulse rounded bg-slate-100" />
          <div className="h-9 w-28 animate-pulse rounded bg-slate-100" />
        </div>
      ) : isEmpty ? (
        <p className="text-sm text-slate-500">No data available</p>
      ) : (
        <div className="flex gap-2">
          <DownloadButton data={data} filename={filename} format="json" />
          <DownloadButton data={data} filename={filename} format="csv" />
          {format === "geojson" && (
            <span className="ml-2 inline-flex items-center text-xs text-slate-500">
              (GeoJSON format)
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default function DataPage() {
  // Trend data endpoints
  const { data: annual } = useSWR("/api/v1/trends/annual", fetcher);
  const { data: monthly } = useSWR("/api/v1/trends/monthly", fetcher);
  const { data: covid } = useSWR("/api/v1/trends/covid", fetcher);
  const { data: seasonality } = useSWR("/api/v1/trends/seasonality", fetcher);
  const { data: robberyHeatmap } = useSWR("/api/v1/trends/robbery-heatmap", fetcher);

  // Spatial data endpoints
  const { data: districts } = useSWR("/api/v1/spatial/districts", fetcher);
  const { data: tracts } = useSWR("/api/v1/spatial/tracts", fetcher);
  const { data: hotspots } = useSWR("/api/v1/spatial/hotspots", fetcher);
  const { data: corridors } = useSWR("/api/v1/spatial/corridors", fetcher);

  // Policy data endpoints
  const { data: retailTheft } = useSWR("/api/v1/policy/retail-theft", fetcher);
  const { data: vehicleCrimes } = useSWR("/api/v1/policy/vehicle-crimes", fetcher);
  const { data: composition } = useSWR("/api/v1/policy/composition", fetcher);
  const { data: events } = useSWR("/api/v1/policy/events", fetcher);

  return (
    <div className="prose max-w-5xl prose-slate">
      {/* Hero Section */}
      <div className="not-prose mb-10">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Data & Transparency</h1>
        <p className="text-lg text-slate-700">
          Download all available crime data, review source citations, and understand our analytical methodology. 
          All datasets are available in JSON and CSV formats for external analysis.
        </p>
      </div>

      {/* Data Downloads Section */}
      <section className="not-prose mb-12">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Available Data Downloads</h2>
        
        {/* Trend Data */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Trend Data</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <DatasetCard
              title="Annual Trends"
              description="Violent, Property, and Other incidents aggregated by year"
              data={annual}
              filename="annual-trends"
            />
            <DatasetCard
              title="Monthly Trends"
              description="Crime incidents aggregated by month across all years"
              data={monthly}
              filename="monthly-trends"
            />
            <DatasetCard
              title="COVID-19 Impact"
              description="Crime patterns before, during, and after COVID-19 pandemic periods"
              data={covid}
              filename="covid-impact"
            />
            <DatasetCard
              title="Seasonality Patterns"
              description="Day-of-week and time-of-day crime patterns"
              data={seasonality}
              filename="seasonality"
            />
            <DatasetCard
              title="Robbery Heatmap"
              description="Hour-by-day matrix of robbery incident counts"
              data={robberyHeatmap}
              filename="robbery-heatmap"
            />
          </div>
        </div>

        {/* Spatial Data */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Spatial Data</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <DatasetCard
              title="Police Districts"
              description="Crime statistics aggregated by police district boundaries"
              data={districts}
              filename="police-districts"
              format="geojson"
            />
            <DatasetCard
              title="Census Tracts"
              description="Crime density by census tract with demographic context"
              data={tracts}
              filename="census-tracts"
              format="geojson"
            />
            <DatasetCard
              title="Crime Hotspots"
              description="High-density crime clusters identified via spatial analysis"
              data={hotspots}
              filename="crime-hotspots"
              format="geojson"
            />
            <DatasetCard
              title="High-Crime Corridors"
              description="Linear street segments with elevated crime rates"
              data={corridors}
              filename="crime-corridors"
              format="geojson"
            />
          </div>
        </div>

        {/* Policy Data */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Policy-Focused Data</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <DatasetCard
              title="Retail Theft"
              description="Shoplifting and retail-related crime incidents over time"
              data={retailTheft}
              filename="retail-theft"
            />
            <DatasetCard
              title="Vehicle Crimes"
              description="Auto theft, carjacking, and vehicle-related incidents"
              data={vehicleCrimes}
              filename="vehicle-crimes"
            />
            <DatasetCard
              title="Crime Composition"
              description="Breakdown of crime types as percentage of total incidents"
              data={composition}
              filename="crime-composition"
            />
            <DatasetCard
              title="Special Events"
              description="Crime patterns during major city events and time periods"
              data={events}
              filename="special-events"
            />
          </div>
        </div>
      </section>

      {/* Data Sources Section */}
      <section className="mb-12">
        <h2>Data Sources</h2>
        <p>
          All crime incident data originates from the{" "}
          <a 
            href="https://www.opendataphilly.org/datasets/crime-incidents/" 
            target="_blank" 
            rel="noreferrer"
            className="text-blue-700 underline hover:text-blue-800"
          >
            Philadelphia Police Department
          </a>
          , published through the City of Philadelphia&apos;s open data initiative via{" "}
          <a 
            href="https://www.opendataphilly.org/" 
            target="_blank" 
            rel="noreferrer"
            className="text-blue-700 underline hover:text-blue-800"
          >
            OpenDataPhilly
          </a>
          . The dataset contains over 1.5 million incident records from 2006 to the present.
        </p>
        <p>
          Spatial boundary data (police districts, census tracts) comes from the{" "}
          <a 
            href="https://www.census.gov/" 
            target="_blank" 
            rel="noreferrer"
            className="text-blue-700 underline hover:text-blue-800"
          >
            U.S. Census Bureau
          </a>{" "}
          and{" "}
          <a 
            href="https://www.opendataphilly.org/" 
            target="_blank" 
            rel="noreferrer"
            className="text-blue-700 underline hover:text-blue-800"
          >
            OpenDataPhilly
          </a>
          &apos;s geographic datasets.
        </p>
      </section>

      {/* Methodology Section */}
      <section className="mb-12">
        <h2>Methodology</h2>
        <p>
          Our analytical pipeline applies several statistical and geospatial techniques to the raw incident data:
        </p>
        <ul>
          <li>
            <strong>Temporal aggregation:</strong> Incidents are grouped by year, month, day-of-week, and hour 
            to identify patterns over time
          </li>
          <li>
            <strong>Trend decomposition:</strong> Statistical methods separate long-term trends from seasonal 
            variation and random noise
          </li>
          <li>
            <strong>Spatial clustering:</strong> Geographic hotspot analysis identifies areas with statistically 
            significant crime concentration
          </li>
          <li>
            <strong>Category classification:</strong> Incidents are grouped into policy-relevant categories 
            (Violent, Property, Other) based on UCR codes
          </li>
          <li>
            <strong>Change detection:</strong> Year-over-year and period-over-period comparisons highlight 
            significant shifts in crime patterns
          </li>
        </ul>
        <p>
          All processing is automated and reproducible. The complete pipeline source code is available in the{" "}
          <a 
            href="https://github.com/dustinober1/Philadelphia-Crime-Incidents-Analysis" 
            target="_blank" 
            rel="noreferrer"
            className="text-blue-700 underline hover:text-blue-800"
          >
            GitHub repository
          </a>
          .
        </p>
      </section>

      {/* Limitations Section */}
      <section className="mb-12">
        <h2>Known Limitations</h2>
        <p>
          Users should be aware of several important constraints when interpreting this data:
        </p>
        <ul>
          <li>
            <strong>Reporting practices change over time:</strong> Police recording procedures, classification 
            standards, and data collection methods have evolved, affecting year-to-year comparability
          </li>
          <li>
            <strong>Geocoding coverage varies:</strong> Not all incidents have precise location coordinates. 
            Some records are missing geographic data or have been anonymized for privacy protection
          </li>
          <li>
            <strong>Context shifts:</strong> Enforcement priorities, community reporting behavior, and policy 
            environments change throughout the analysis period
          </li>
          <li>
            <strong>No causal claims:</strong> Statistical correlations do not establish causation. Observed 
            patterns require careful interpretation and domain expertise
          </li>
          <li>
            <strong>Historical snapshot:</strong> This is a retrospective analysis, not a real-time monitoring 
            system. Data is updated periodically based on PPD releases
          </li>
        </ul>
      </section>

      {/* Attribution Section */}
      <section className="not-prose mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Attribution</h2>
        <p className="text-slate-700 mb-4">
          If you use this data in research, journalism, or policy analysis, please cite the original source:
        </p>
        <div className="rounded-lg bg-slate-50 border border-slate-200 p-4">
          <p className="font-mono text-sm text-slate-800">
            Philadelphia Police Department. Crime Incidents. Available from OpenDataPhilly:{" "}
            <a 
              href="https://www.opendataphilly.org/datasets/crime-incidents/" 
              target="_blank" 
              rel="noreferrer"
              className="text-blue-700 underline break-all hover:text-blue-800"
            >
              https://www.opendataphilly.org/datasets/crime-incidents/
            </a>
          </p>
        </div>
      </section>
    </div>
  );
}
