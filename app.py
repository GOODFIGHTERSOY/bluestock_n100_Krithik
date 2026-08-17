import streamlit as st

from src.dashboard_app.config import (
    configure_page,
    sidebar,
)

configure_page()

sidebar()

st.title("📈 Bluestock N100 Analytics Platform")

st.markdown(
"""
Welcome to the Bluestock N100 Financial Analytics Platform.

This application provides:

- Company Financial Analysis
- Stock Screening
- Peer Group Comparison
- Company Rankings
- Financial KPI Dashboard

Use the navigation menu on the left to begin.
"""
)

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Companies",
        "92"
    )

with col2:
    st.metric(
        "Financial Records",
        "1670"
    )

with col3:
    st.metric(
        "Peer Groups",
        "11"
    )

with col4:
    st.metric(
        "Screeners",
        "6"
    )

st.divider()

st.subheader("🚀 Platform Modules")

c1, c2 = st.columns(2)

with c1:

    st.info(
        """
### Available Modules

- Dashboard

- Company Analysis

- Screener

- Peer Comparison

- Rankings
"""
    )

with c2:

    st.warning(
        """
### Technology Stack

- Python

- SQLite

- Pandas

- Streamlit

- Plotly

- OpenPyXL
"""
    )

st.divider()

st.success(
    "Bluestock N100 Analytics Platform is ready."
)