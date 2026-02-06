export const metadata = {
  title: "Philadelphia Crime Explorer | About",
  description: "Data sources, methodology, caveats, and contact details for the Philadelphia Crime Explorer project.",
};

export default function AboutPage() {
  return (
    <div className="prose max-w-4xl prose-slate">
      <h1>About / Methodology</h1>
      <p>Source: Philadelphia Police Department, OpenDataPhilly incident records.</p>
      <p>Dataset scope: roughly 1.5M incidents spanning 2006 through the latest available export.</p>
      <p>Methods include trend decomposition, temporal seasonality, spatial aggregation, policy-specific filtering, and forecasting/classification models.</p>
      <p>Limitations: reporting practices, geocoding coverage, and policy context can change over time; these are descriptive and statistical outputs.</p>
      <p>Repository: <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a></p>
      <p>Contact: Dustin Ober</p>
    </div>
  );
}
