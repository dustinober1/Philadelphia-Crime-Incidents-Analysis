"""
Spatial Maps page renderer.

Displays geographic distribution and district comparisons using analysis module functions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.components.cache import load_cached_report
from dashboard.components import (
    register_plotly_selection,
    update_selection_from_event,
    get_selection_state,
    get_active_filter_kwargs,
    clear_selection_state,
    has_active_selection,
)
from dashboard.config import PLOTLY_CONFIG


def render_spatial_page(full_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    """
    Render the Spatial Maps page.

    Args:
        full_df: The complete, unfiltered DataFrame.
        filtered_df: The currently filtered DataFrame.
    """
    st.header(":map: Spatial Distribution")

    st.caption("Geographic patterns and district comparisons")

    # Get selection state for cross-filtering
    selection_state = get_selection_state()

    # Display active cross-filter hint and clear button
    if selection_state.active_view and selection_state.active_view != "spatial":
        source_view_name = selection_state.active_view.title()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f":link: **Active cross-filter from {source_view_name} view**")
        with col2:
            if st.button(":x: Clear", key="spatial_clear"):
                clear_selection_state()
                st.rerun()

    # Apply cross-filter if active selection from other views
    if selection_state.active_view and selection_state.active_view != "spatial":
        from dashboard.components.cache import apply_filters
        cross_filter_kwargs = get_active_filter_kwargs()
        if cross_filter_kwargs:
            filtered_df = apply_filters(filtered_df, **cross_filter_kwargs)

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

            if "valid_coord" in filtered_df.columns:
                coord_valid = filtered_df["valid_coord"].sum()
                coord_pct = (coord_valid / len(filtered_df) * 100) if len(filtered_df) > 0 else 0

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Valid Coordinates", f"{coord_valid:,}")
                col2.metric("Coverage %", f"{coord_pct:.1f}%")
                col3.metric("Total Records", f"{len(filtered_df):,}")

                if coord_valid > 0 and "point_x" in filtered_df.columns and "point_y" in filtered_df.columns:
                    valid_df = filtered_df[filtered_df["valid_coord"]]
                    lon_min, lon_max = valid_df["point_x"].min(), valid_df["point_x"].max()
                    lat_min, lat_max = valid_df["point_y"].min(), valid_df["point_y"].max()
                    col4.metric("Bounds", f"{lon_min:.2f}/{lat_min:.2f}")

            # District distribution
            st.subheader("District Distribution")

            if "dc_dist" in filtered_df.columns:
                district_counts = filtered_df["dc_dist"].value_counts().sort_index().reset_index()
                district_counts.columns = ["dc_dist", "count"]

                # Create Plotly bar chart with selection support
                fig_districts = px.bar(district_counts, x="dc_dist", y="count",
                                       labels={"dc_dist": "Police District", "count": "Number of Incidents"},
                                       title="Incidents by District")

                fig_districts = register_plotly_selection(fig_districts, key="spatial_districts")
                selection_event = st.plotly_chart(fig_districts, on_select="rerun", key="spatial_districts_chart", use_container_width=True)

                # Handle selection event
                if selection_event.selection["points"]:
                    update_selection_from_event(selection_event, source_view="spatial")

                # Top 5 districts by crime count
                st.subheader("Top 5 Districts by Incident Count")
                top_districts = district_counts.nlargest(5, "count")
                for _, row in top_districts.iterrows():
                    st.metric(f"District {int(row['dc_dist'])}", f"{int(row['count']):,}")

                # Bottom 5 districts
                st.subheader("Bottom 5 Districts by Incident Count")
                bottom_districts = district_counts.nsmallest(5, "count")
                for _, row in bottom_districts.iterrows():
                    st.metric(f"District {int(row['dc_dist'])}", f"{int(row['count']):,}")

            # Crime category by district
            st.subheader("Crime Category by District")

            if "dc_dist" in filtered_df.columns and "crime_category" in filtered_df.columns:
                # Create a crosstab for district x category
                district_category = pd.crosstab(
                    filtered_df["dc_dist"],
                    filtered_df["crime_category"],
                    normalize="index"
                ) * 100

                st.dataframe(district_category.round(1).astype(str) + "%")

            st.caption("Note: For detailed spatial analysis including density maps and hotspots, uncheck 'Use filtered data' to view the pre-generated report.")

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info("Try unchecking 'Use filtered data' to view the pre-generated report.")
