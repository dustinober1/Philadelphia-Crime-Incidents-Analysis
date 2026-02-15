export const metadata = {
  title: "Philadelphia Crime Explorer | About",
  description: "Data sources, methodology, caveats, and contact details for the Philadelphia Crime Explorer project.",
};

export default function AboutPage() {
  return (
    <div className="prose max-w-4xl prose-slate">
      <h1>About This Project</h1>
      
      <p className="lead text-slate-600">
        An evidence-based exploration of crime patterns in Philadelphia, built on transparent methods 
        and open data. This site presents statistical analysis of over 1.5 million incident records 
        from the Philadelphia Police Department.
      </p>

      <section>
        <h2>Data Sources</h2>
        <p>
          All crime incident data comes from the Philadelphia Police Department&apos;s publicly available 
          records published through <a href="https://opendataphilly.org" target="_blank" rel="noreferrer">OpenDataPhilly</a>. 
          The dataset includes approximately 1.5 million incidents spanning from 2006 through the latest 
          available export.
        </p>
        <p>
          Each incident record includes temporal information (date, time, season), geographic location 
          (latitude/longitude, police district, neighborhood), and categorical details (UCR general classification, 
          specific offense type).
        </p>
      </section>

      <section>
        <h2>Methodology</h2>
        <p>
          Analysis techniques applied to this dataset include:
        </p>
        <ul>
          <li><strong>Trend decomposition:</strong> Separating long-term trends from seasonal and random variation</li>
          <li><strong>Temporal seasonality analysis:</strong> Identifying daily, weekly, and seasonal crime patterns</li>
          <li><strong>Spatial aggregation:</strong> Mapping incident density by district, neighborhood, and geographic coordinates</li>
          <li><strong>Policy-specific filtering:</strong> Isolating crime types relevant to specific policy questions (e.g., retail theft, vehicle-related crimes)</li>
          <li><strong>Forecasting and classification models:</strong> Time series prediction and pattern recognition using statistical and machine learning methods</li>
        </ul>
        <p>
          All visualizations and statistical outputs are generated programmatically from the source data. 
          The complete analytical pipeline is version-controlled and reproducible.
        </p>
      </section>

      <section>
        <h2>Known Limitations</h2>
        <p>
          This analysis is descriptive and statistical in nature. Users should be aware of several 
          important limitations:
        </p>
        <ul>
          <li><strong>Reporting practices evolve:</strong> Police recording and classification procedures 
          may change over time, affecting comparability across years</li>
          <li><strong>Geocoding coverage varies:</strong> Not all incidents have precise location data; 
          some records lack coordinates or have been anonymized for privacy</li>
          <li><strong>Context changes:</strong> Policy environment, enforcement priorities, and community 
          reporting behavior shift over the analysis period</li>
          <li><strong>No causal claims:</strong> Statistical patterns do not establish causation; observed 
          correlations require careful interpretation</li>
          <li><strong>Static snapshot:</strong> This is a historical analysis, not a real-time monitoring system</li>
        </ul>
      </section>

      <section>
        <h2>Update Cadence</h2>
        <p>
          The underlying crime dataset is updated periodically by the Philadelphia Police Department. 
          This analysis was last refreshed using data current as of the repository&apos;s latest commit. 
          Check the footer for the most recent data update timestamp.
        </p>
      </section>

      <section>
        <h2>Contact &amp; Attribution</h2>
        <p>
          This project was developed by <strong>Dustin Ober</strong> as an independent analytical exercise. 
          The complete source code, data processing pipeline, and web interface are available on{' '}
          <a href="https://github.com/dustinober1/Philadelphia-Crime-Incidents-Analysis" target="_blank" rel="noreferrer">
            GitHub
          </a>.
        </p>
        <p>
          For questions, corrections, or collaboration inquiries, please open an issue on the repository 
          or contact directly through GitHub.
        </p>
      </section>
    </div>
  );
}
