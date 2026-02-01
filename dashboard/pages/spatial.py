"""
Spatial Maps page renderer.

Displays geographic distribution and district comparisons using analysis module functions.
"""

import streamlit as st
import pandas as pd

from dashboard.components.cache import load_cached_report


def render_spatial_page(df: pd.DataFrame) -> None:
    """
    Render the Spatial Maps page.

    Args:
        df: Filtered DataFrame.
    """
    st.header(":map: Spatial Distribution")

    st.caption("Geographic patterns and district comparisons")

    # Option: Show pre-generated report OR run filtered analysis
    col1, col2 = st.columns([3, 1])

    with col2:
        use_filtered = st.checkbox(
            "Use filtered data",
            value=False,
            help="Uncheck to view full analysis report (faster). Check to analyze current filter."
        )

    if not use_filtered:
        # Display pre-generated report (CONTEXT.md decision: "Existing reports embedded")
        st.info(":memo: Displaying pre-generated spatial analysis from EDA report (full dataset)")

        # Try multiple possible report paths
        report_paths = [
            "reports/04_spatial_analysis_report.md",
            "reports/01_eda_report.md",
        ]

        report_found = False
        for report_path in report_paths:
            try:
                report_content = load_cached_report(report_path)
                if report_content:
                    # Extract spatial section if in EDA report
                    if "01_eda_report.md" in report_path:
                        st.markdown("### Spatial Analysis Section")
                        # Look for spatial section in the report
                        lines = report_content.split("\n")
                        spatial_lines = []
                        in_spatial = False
                        for line in lines:
                            if "## Spatial" in line or "## Geographic" in line:
                                in_spatial = True
                            elif in_spatial and line.startswith("## ") and "Spatial" not in line and "Geographic" not in line:
                                break
                            if in_spatial:
                                spatial_lines.append(line)

                        if spatial_lines:
                            st.markdown("\n".join(spatial_lines))
                        else:
                            # If no spatial section found, show full report
                            st.markdown(report_content)
                    else:
                        st.markdown(report_content)

                    report_found = True
                    break
            except Exception:
                continue

        if not report_found:
            st.warning("""
            **Spatial analysis report not found**

            The spatial analysis report has not been generated yet.

            To generate this report, run:
            ```bash
            python analysis/spatial_analysis.py
            ```
            """)
    else:
        # Run analysis on filtered data
        st.warning(":hourglass: Analyzing filtered data - this may take a moment...")

        try:
            # Coordinate statistics
            st.subheader("Coordinate Statistics")

            if "valid_coord" in df.columns:
                coord_valid = df["valid_coord"].sum()
                coord_pct = (coord_valid / len(df) * 100) if len(df) > 0 else 0

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Valid Coordinates", f"{coord_valid:,}")
                col2.metric("Coverage %", f"{coord_pct:.1f}%")
                col3.metric("Total Records", f"{len(df):,}")

                if coord_valid > 0 and "point_x" in df.columns and "point_y" in df.columns:
                    valid_df = df[df["valid_coord"]]
                    lon_min, lon_max = valid_df["point_x"].min(), valid_df["point_x"].max()
                    lat_min, lat_max = valid_df["point_y"].min(), valid_df["point_y"].max()
                    col4.metric("Bounds", f"{lon_min:.2f}/{lat_min:.2f}")

            # District distribution
            st.subheader("District Distribution")

            if "dc_dist" in df.columns:
                district_counts = df["dc_dist"].value_counts().sort_index()
                st.bar_chart(district_counts)

                # Top 5 districts by crime count
                st.subheader("Top 5 Districts by Incident Count")
                top_districts = district_counts.head(5)
                for district, count in top_districts.items():
                    st.metric(f"District {district}", f"{count:,}")

                # Bottom 5 districts
                st.subheader("Bottom 5 Districts by Incident Count")
                bottom_districts = district_counts.tail(5)
                for district, count in bottom_districts.items():
                    st.metric(f"District {district}", f"{count:,}")

            # Crime category by district
            st.subheader("Crime Category by District")

            if "dc_dist" in df.columns and "crime_category" in df.columns:
                # Create a crosstab for district x category
                district_category = pd.crosstab(
                    df["dc_dist"],
                    df["crime_category"],
                    normalize="index"
                ) * 100

                st.dataframe(district_category.round(1).astype(str) + "%")

            st.caption("Note: For detailed spatial analysis including density maps and hotspots, uncheck 'Use filtered data' to view the pre-generated report.")

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info("Try unchecking 'Use filtered data' to view the pre-generated report.")
