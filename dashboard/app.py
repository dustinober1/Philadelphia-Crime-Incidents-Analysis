"""
Philadelphia Crime Incidents Dashboard - Main Entry Point.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
from pathlib import Path

from dashboard.config import DISPLAY_CONFIG, PAGE_NAMES

# Configure page
st.set_page_config(
    page_title="Philadelphia Crime Dashboard",
    page_icon=":police_car:",
    layout=DISPLAY_CONFIG["layout"],
    initial_sidebar_state="expanded",
)

# Custom CSS for professional appearance
def _load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main dashboard entry point."""
    _load_custom_css()

    # Title
    st.title(DISPLAY_CONFIG["title"])
    st.markdown(f"<p class='sub-header'>{DISPLAY_CONFIG['subtitle']}</p>", unsafe_allow_html=True)

    # Sidebar info (placeholder for filters in later plans)
    with st.sidebar:
        st.header(":wrench: Filters")
        st.info("Filter controls will be added in subsequent plans (04-03, 04-04, 04-05)")
        st.markdown("---")
        st.caption("Dashboard v1.0 | Philadelphia Crime EDA")

    # Placeholder for tabs (will be implemented in 04-06)
    st.header("Dashboard Under Construction")
    st.info("This dashboard is being built incrementally. See Phase 4 plans:")
    st.markdown("""
    - Plan 04-01: Project structure and configuration (this plan)
    - Plan 04-02: Data loading with caching
    - Plan 04-03: Time range filter controls
    - Plan 04-04: Geographic filter controls
    - Plan 04-05: Crime type filter controls
    - Plan 04-06: Main overview page with tabs and visualizations
    """)

    # Quick stats placeholder
    st.subheader("Quick Stats (Placeholder)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", "3.5M", "2006-2025")
    with col2:
        st.metric("Police Districts", "23", "Philadelphia")
    with col3:
        st.metric("Crime Types", "32", "UCR categories")

if __name__ == "__main__":
    main()
