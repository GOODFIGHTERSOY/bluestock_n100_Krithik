import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

st.title("🏭 Sector Analysis")

st.markdown(
    "<h4 style='color:#012970;'>Sector / Peer Group Performance Analysis</h4>",
    unsafe_allow_html=True,
)

# ==========================================================
# LOAD DATA
# ==========================================================

financial = pd.read_csv("output/financial_ratios.csv")

peer = pd.read_excel(
    "data/raw/peer_groups.xlsx"
)

peer = peer[["company_id", "peer_group_name"]]

financial = financial.merge(
    peer,
    on="company_id",
    how="left"
)

# ==========================================================
# LATEST YEAR ONLY
# ==========================================================

financial["year"] = financial["year"].astype(str)

latest = (
    financial
    .sort_values("year")
    .drop_duplicates("company_id", keep="last")
)

# ==========================================================
# PEER GROUP SELECTOR
# ==========================================================

groups = sorted(
    latest["peer_group_name"]
    .dropna()
    .unique()
)

selected = st.selectbox(
    "Select Peer Group",
    groups
)

sector_df = latest[
    latest["peer_group_name"] == selected
]

# ==========================================================
# KPI CARDS
# ==========================================================

st.subheader("Sector Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(sector_df)
)

if "return_on_equity_pct" in sector_df.columns:
    c2.metric(
        "Average ROE",
        f"{sector_df['return_on_equity_pct'].mean():.2f}%"
    )

if "net_profit_margin_pct" in sector_df.columns:
    c3.metric(
        "Average Margin",
        f"{sector_df['net_profit_margin_pct'].mean():.2f}%"
    )

if "debt_to_equity" in sector_df.columns:
    c4.metric(
        "Average D/E",
        f"{sector_df['debt_to_equity'].mean():.2f}"
    )

st.divider()

# ==========================================================
# TOP ROE
# ==========================================================

if "return_on_equity_pct" in sector_df.columns:

    st.subheader("Top Companies by ROE")

    fig = px.bar(

        sector_df.nlargest(10, "return_on_equity_pct"),

        x="company_id",

        y="return_on_equity_pct",

        color_discrete_sequence=["#012970"]

    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="Top ROE",

        title_font=dict(color="#012970"),

        xaxis_title="Company",

        yaxis_title="ROE (%)"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# NET PROFIT MARGIN
# ==========================================================

if "net_profit_margin_pct" in sector_df.columns:

    st.subheader("Top Net Profit Margin")

    fig = px.bar(

        sector_df.nlargest(10, "net_profit_margin_pct"),

        x="company_id",

        y="net_profit_margin_pct",

        color_discrete_sequence=["#6F42C1"]

    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="Net Profit Margin",

        title_font=dict(color="#012970")

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# ROE vs DEBT
# ==========================================================

if (
    "debt_to_equity" in sector_df.columns
    and
    "return_on_equity_pct" in sector_df.columns
):

    st.subheader("ROE vs Debt")

    fig = px.scatter(

        sector_df,

        x="debt_to_equity",

        y="return_on_equity_pct",

        color="peer_group_name",

        hover_name="company_id",

        color_discrete_sequence=[
            "#012970",
            "#6F42C1",
            "#F05537"
        ],

        size_max=15

    )

    fig.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(color="black"),

        title="ROE vs Debt",

        title_font=dict(color="#012970")

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# DATA TABLE
# ==========================================================

st.subheader("Sector Financial Data")

display_cols = [

    "company_id",

    "return_on_equity_pct",

    "net_profit_margin_pct",

    "debt_to_equity",

    "interest_coverage",

    "asset_turnover"

]

display_cols = [

    c for c in display_cols
    if c in sector_df.columns
]

st.dataframe(

    sector_df[display_cols],

    use_container_width=True,

    hide_index=True

)

# ==========================================================
# DOWNLOAD
# ==========================================================

csv = sector_df.to_csv(index=False)

st.download_button(

    "⬇ Download Sector Data",

    csv,

    file_name=f"{selected}_sector_analysis.csv",

    mime="text/csv"

)