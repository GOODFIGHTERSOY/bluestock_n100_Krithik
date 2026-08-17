import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

st.title("💰 Capital Allocation")

st.markdown(
    "<h4 style='color:#012970;'>Capital Allocation & Cash Flow Analysis</h4>",
    unsafe_allow_html=True,
)

# ==========================================================
# LOAD DATA
# ==========================================================

financial = pd.read_csv("output/financial_ratios.csv")

peer = pd.read_excel(
    "data/raw/peer_groups.xlsx"
)

peer = peer[
    [
        "company_id",
        "peer_group_name"
    ]
]

financial = financial.merge(
    peer,
    on="company_id",
    how="left"
)

# ==========================================================
# LATEST DATA
# ==========================================================

financial["year"] = financial["year"].astype(str)

latest = (
    financial
    .sort_values("year")
    .drop_duplicates("company_id", keep="last")
)

# ==========================================================
# KPI CARDS
# ==========================================================

st.subheader("Capital Allocation Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(latest)
)

if "free_cash_flow" in latest.columns:
    c2.metric(
        "Average FCF",
        f"{latest['free_cash_flow'].mean():.2f}"
    )

if "capex_intensity" in latest.columns:
    c3.metric(
        "Average Capex Intensity",
        f"{latest['capex_intensity'].mean():.2f}"
    )

if "cfo_quality_score" in latest.columns:
    c4.metric(
        "Average CFO Score",
        f"{latest['cfo_quality_score'].mean():.2f}"
    )

st.divider()

# ==========================================================
# SCATTER PLOT
# ==========================================================

if (
    "capex_intensity" in latest.columns
    and
    "free_cash_flow" in latest.columns
):

    st.subheader("Capital Allocation Map")

    fig = px.scatter(

        latest,

        x="capex_intensity",

        y="free_cash_flow",

        size="cfo_quality_score",

        color="capital_allocation_pattern",

        hover_name="company_id",

        color_discrete_sequence=[
            "#012970",
            "#6F42C1",
            "#F05537"
        ]
    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="Capital Allocation Map",

        title_font=dict(

            color="#012970",
            size=22

        ),

        xaxis_title="Capex Intensity",

        yaxis_title="Free Cash Flow",

        legend_title="Allocation Pattern"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ==========================================================
# TOP FREE CASH FLOW
# ==========================================================

if "free_cash_flow" in latest.columns:

    st.subheader("Top Free Cash Flow Companies")

    top_fcf = latest.nlargest(
        10,
        "free_cash_flow"
    )

    fig = px.bar(

        top_fcf,

        x="company_id",

        y="free_cash_flow",

        color_discrete_sequence=["#012970"]

    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="Top Free Cash Flow",

        title_font=dict(color="#012970")

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# CAPEX INTENSITY
# ==========================================================

if "capex_intensity" in latest.columns:

    st.subheader("Highest Capex Intensity")

    top_capex = latest.nlargest(
        10,
        "capex_intensity"
    )

    fig = px.bar(

        top_capex,

        x="company_id",

        y="capex_intensity",

        color_discrete_sequence=["#6F42C1"]

    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="Highest Capex Intensity",

        title_font=dict(color="#012970")

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# CFO QUALITY
# ==========================================================

if "cfo_quality_score" in latest.columns:

    st.subheader("Best CFO Quality")

    top_cfo = latest.nlargest(
        10,
        "cfo_quality_score"
    )

    fig = px.bar(

        top_cfo,

        x="company_id",

        y="cfo_quality_score",

        color_discrete_sequence=["#F05537"]

    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="Best CFO Quality",

        title_font=dict(color="#012970")

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ==========================================================
# DATA TABLE
# ==========================================================

st.subheader("Capital Allocation Data")

columns = [

    "company_id",

    "free_cash_flow",

    "capex_intensity",

    "cfo_quality_score",

    "fcf_conversion",

    "capital_allocation_pattern"

]

columns = [
    c for c in columns
    if c in latest.columns
]

st.dataframe(

    latest[columns],

    use_container_width=True,

    hide_index=True

)

# ==========================================================
# DOWNLOAD
# ==========================================================

csv = latest.to_csv(index=False)

st.download_button(

    "⬇ Download Capital Allocation Data",

    csv,

    file_name="capital_allocation.csv",

    mime="text/csv"

)