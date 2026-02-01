"""
Overview/Stats page renderer.

Displays summary statistics, key metrics, and high-level insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.components.cache import get_data_summary
from dashboard.components import (
    register_plotly_selection,
    update_selection_from_event,
    get_selection_state,
    get_active_filter_kwargs,
    clear_selection_state,
    has_active_selection,
)
from dashboard.config import PLOTLY_CONFIG


def render_overview_page(full_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    """
    Render the Overview/Stats page.

    Args:
        full_df: The complete, unfiltered DataFrame.
        filtered_df: The currently filtered DataFrame.
    """
    st.header(":bar_chart: Overview & Statistics")

    st.caption("High-level metrics and summary statistics for the filtered dataset")

    # Get selection state for cross-filtering
    selection_state = get_selection_state()

    # Display active cross-filter hint
    if selection_state.active_view:
        source_view_name = selection_state.active_view.title()
        st.info(f":link: **Active cross-filter from {source_view_name} view**: Click chart or change sidebar filters to reset")

    # Apply cross-filter if active selection from other views
    if selection_state.active_view and selection_state.active_view != "overview":
        from dashboard.components.cache import apply_filters
        cross_filter_kwargs = get_active_filter_kwargs()
        if cross_filter_kwargs:
            filtered_df = apply_filters(filtered_df, **cross_filter_kwargs)

    # Get summary statistics
    summary = get_data_summary(filtered_df)

    # Key metrics row
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Incidents",
            value=f"{summary['total_records']:,}",
            delta=None,
        )

    with col2:
        years = summary.get('years', 'N/A')
        st.metric(
            label="Time Span",
            value=f"{years} years" if isinstance(years, int) else years,
        )

    with col3:
        districts = summary.get('districts', 'N/A')
        st.metric(
            label="Police Districts",
            value=str(districts),
        )

    with col4:
        coord_pct = summary.get('coord_coverage', {}).get('percentage', 0)
        st.metric(
            label="Valid Coordinates",
            value=f"{coord_pct:.1f}%",
        )

    # Crime category breakdown
    st.subheader("Crime Category Distribution")

    if "crime_category" in full_df.columns:
        # Get counts for the full dataset to show dimmed bars
        full_category_counts = full_df["crime_category"].value_counts().reset_index()
        full_category_counts.columns = ["crime_category", "count"]

        # Get counts for the filtered dataset to show highlighted bars
        filtered_category_counts = filtered_df["crime_category"].value_counts().reset_index()
        filtered_category_counts.columns = ["crime_category", "count"]

        # Merge the two to identify which categories are present in the filtered data
        merged_counts = pd.merge(full_category_counts, filtered_category_counts,
                                 on="crime_category", how="left", suffixes=("_full", "_filtered"))
        merged_counts["count_filtered"] = merged_counts["count_filtered"].fillna(0) # Fill NaN with 0 for non-filtered categories

        # Determine opacity based on whether the category is present in the filtered data
        merged_counts["opacity"] = merged_counts["count_filtered"].apply(lambda x: 0.9 if x > 0 else 0.2)

        # Create RGBA colors dynamically for each bar
        # Define a base color (e.g., Plotly default blue)
        base_color = "rgba(31, 119, 180, {})" # Using Plotly's default blue color with a placeholder for alpha

        merged_counts["color"] = merged_counts["opacity"].apply(lambda alpha: base_color.format(alpha))

        col1, col2, col3 = st.columns(3)

        with col1:
            violent = filtered_category_counts[filtered_category_counts["crime_category"] == "Violent"]["count"].sum() if "Violent" in filtered_category_counts["crime_category"].values else 0
            st.metric("Violent Crimes", f"{violent:,}")

        with col2:
            property_crime = filtered_category_counts[filtered_category_counts["crime_category"] == "Property"]["count"].sum() if "Property" in filtered_category_counts["crime_category"].values else 0
            st.metric("Property Crimes", f"{property_crime:,}")

        with col3:
            other = filtered_category_counts[filtered_category_counts["crime_category"] == "Other"]["count"].sum() if "Other" in filtered_category_counts["crime_category"].values else 0
            st.metric("Other Offenses", f"{other:,}")

        # Create Plotly Express bar chart
        fig = px.bar(merged_counts, x="crime_category", y="count_full",
                     labels={"crime_category": "Crime Category", "count_full": "Number of Incidents"},
                     title="Crime Category Distribution",
                     color="crime_category", # Color by category
                     color_discrete_map={category: color for category, color in zip(merged_counts["crime_category"], merged_counts["color"])}, # Assign colors with dynamic opacity
                     hover_data={"count_full": True, "count_filtered": True, "opacity": False} # Show both counts on hover
                    )

        # Update bars for opacity, making sure the 'filtered' count is shown for active bars
        fig.update_traces(marker_color=merged_counts["color"],
                          hovertemplate="<b>%{x}</b><br>Total: %{y:,}<br>Filtered: %{customdata[0]:,}<extra></extra>",
                          customdata=merged_counts[["count_filtered"]])

        # Register selection and enable on_select
        fig = register_plotly_selection(fig, key="overview_category")
        selection_event = st.plotly_chart(fig, on_select="rerun", key="overview_category_chart", use_container_width=True)

        # Handle selection event
        if selection_event.selection["points"]:
            update_selection_from_event(selection_event, source_view="overview")

    # Temporal breakdown
    st.subheader("Temporal Distribution")

    col1, col2 = st.columns(2)

    with col1:
        if "year" in full_df.columns:
            # Prepare data for full_df and filtered_df
            full_year_counts = full_df["year"].value_counts().sort_index().reset_index()
            full_year_counts.columns = ["year", "count_full"]

            filtered_year_counts = filtered_df["year"].value_counts().sort_index().reset_index()
            filtered_year_counts.columns = ["year", "count_filtered"]

            merged_year_counts = pd.merge(full_year_counts, filtered_year_counts,
                                          on="year", how="left").fillna(0)

            # Determine opacity for each year
            merged_year_counts["opacity"] = merged_year_counts["count_filtered"].apply(lambda x: 1.0 if x > 0 else 0.2)

            # Create Plotly Express line chart
            fig_years = px.line(merged_year_counts, x="year", y="count_full",
                                labels={"year": "Year", "count_full": "Number of Incidents"},
                                title="Yearly Trend",
                                line_shape="spline"
                               )

            # Update traces to apply conditional opacity
            for i, row in merged_year_counts.iterrows():
                fig_years.add_scatter(x=[row["year"]], y=[row["count_full"]],
                                      mode="markers",
                                      marker=dict(size=8,
                                                  color=f"rgba(31, 119, 180, {row['opacity']})", # Use the same blue color as bar chart
                                                  line=dict(width=1, color='DarkSlateGrey')),
                                      name=str(row["year"]),
                                      showlegend=False,
                                      hoverinfo="none" # Hide individual marker hoverinfo
                                     )

            fig_years.update_traces(line=dict(color='rgba(31, 119, 180, 0.5)'), # Dim the line itself
                                    hovertemplate="<b>Year: %{x}</b><br>Total: %{y:,}<br>Filtered: %{customdata[0]:,}<extra></extra>",
                                    customdata=merged_year_counts[["count_filtered"]])

            # Register selection and enable on_select
            fig_years = register_plotly_selection(fig_years, key="overview_years")
            selection_event_years = st.plotly_chart(fig_years, on_select="rerun", key="overview_years_chart", use_container_width=True)

            # Handle selection event
            if selection_event_years.selection["points"]:
                update_selection_from_event(selection_event_years, source_view="overview")

    with col2:
        if "season" in full_df.columns:
            # Prepare data for full_df and filtered_df
            full_season_counts = full_df["season"].value_counts().reset_index()
            full_season_counts.columns = ["season", "count"]

            filtered_season_counts = filtered_df["season"].value_counts().reset_index()
            filtered_season_counts.columns = ["season", "count"]

            merged_season_counts = pd.merge(full_season_counts, filtered_season_counts,
                                            on="season", how="left", suffixes=("_full", "_filtered"))
            merged_season_counts["count_filtered"] = merged_season_counts["count_filtered"].fillna(0)

            # Determine opacity for each season
            merged_season_counts["opacity"] = merged_season_counts["count_filtered"].apply(lambda x: 0.9 if x > 0 else 0.2)

            # Create RGBA colors dynamically
            base_color_season = "rgba(255, 127, 14, {})" # Using Plotly's default orange color

            merged_season_counts["color"] = merged_season_counts["opacity"].apply(lambda alpha: base_color_season.format(alpha))

            # Create Plotly Express bar chart
            fig_seasons = px.bar(merged_season_counts, x="season", y="count_full",
                                 labels={"season": "Season", "count_full": "Number of Incidents"},
                                 title="Seasonal Patterns",
                                 color="season",
                                 color_discrete_map={season: color for season, color in zip(merged_season_counts["season"], merged_season_counts["color"])},
                                 hover_data={"count_full": True, "count_filtered": True, "opacity": False}
                                )

            fig_seasons.update_traces(marker_color=merged_season_counts["color"],
                                      hovertemplate="<b>%{x}</b><br>Total: %{y:,}<br>Filtered: %{customdata[0]:,}<extra></extra>",
                                      customdata=merged_season_counts[["count_filtered"]])

            # Register selection and enable on_select
            fig_seasons = register_plotly_selection(fig_seasons, key="overview_seasons")
            selection_event_seasons = st.plotly_chart(fig_seasons, on_select="rerun", key="overview_seasons_chart", use_container_width=True)

            # Handle selection event
            if selection_event_seasons.selection["points"]:
                update_selection_from_event(selection_event_seasons, source_view="overview")

    # District breakdown
    st.subheader("District Distribution")

    if "dc_dist" in full_df.columns:
        # Prepare data for full_df and filtered_df
        full_district_counts = full_df["dc_dist"].value_counts().sort_index().head(10).reset_index()
        full_district_counts.columns = ["dc_dist", "count"]

        filtered_district_counts = filtered_df["dc_dist"].value_counts().sort_index().reset_index()
        filtered_district_counts.columns = ["dc_dist", "count"]

        merged_district_counts = pd.merge(full_district_counts, filtered_district_counts,
                                          on="dc_dist", how="left", suffixes=("_full", "_filtered"))
        merged_district_counts["count_filtered"] = merged_district_counts["count_filtered"].fillna(0)

        # Determine opacity for each district
        merged_district_counts["opacity"] = merged_district_counts["count_filtered"].apply(lambda x: 0.9 if x > 0 else 0.2)

        # Create RGBA colors dynamically
        base_color_district = "rgba(44, 160, 44, {})" # Using Plotly's default green color

        merged_district_counts["color"] = merged_district_counts["opacity"].apply(lambda alpha: base_color_district.format(alpha))

        # Create Plotly Express bar chart
        fig_districts = px.bar(merged_district_counts, x="dc_dist", y="count_full",
                               labels={"dc_dist": "Police District", "count_full": "Number of Incidents"},
                               title="Top 10 Police Districts by Incident Count (Full Dataset)",
                               color="dc_dist",
                               color_discrete_map={dist: color for dist, color in zip(merged_district_counts["dc_dist"], merged_district_counts["color"])},
                               hover_data={"count_full": True, "count_filtered": True, "opacity": False}
                              )

        fig_districts.update_traces(marker_color=merged_district_counts["color"],
                                    hovertemplate="<b>District: %{x}</b><br>Total: %{y:,}<br>Filtered: %{customdata[0]:,}<extra></extra>",
                                    customdata=merged_district_counts[["count_filtered"]])

        # Register selection and enable on_select
        fig_districts = register_plotly_selection(fig_districts, key="overview_districts")
        selection_event_districts = st.plotly_chart(fig_districts, on_select="rerun", key="overview_districts_chart", use_container_width=True)

        # Handle selection event
        if selection_event_districts.selection["points"]:
            update_selection_from_event(selection_event_districts, source_view="overview")
