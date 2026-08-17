import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

st.title("📊 Peer Comparison")

# ----------------------------------------
# Load Data
# ----------------------------------------

financial = pd.read_excel("data/raw/financial_ratios.xlsx")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.dropna(subset=["company_name"])

companies = companies.rename(columns={"id":"company_id"})

peer = pd.read_excel("data/raw/peer_groups.xlsx")

latest = financial.sort_values("year").drop_duplicates(
    "company_id",
    keep="last"
)

latest = latest.merge(
    companies[["company_id","company_name"]],
    on="company_id"
)

latest = latest.merge(
    peer[["company_id","peer_group_name"]],
    on="company_id"
)

# ----------------------------------------
# Peer Group
# ----------------------------------------

group = st.selectbox(
    "Peer Group",
    sorted(latest["peer_group_name"].unique())
)

peer_df = latest[
    latest["peer_group_name"] == group
]

company = st.selectbox(
    "Company",
    peer_df["company_name"]
)

selected = peer_df[
    peer_df["company_name"] == company
].iloc[0]

# ----------------------------------------
# Radar Chart
# ----------------------------------------

metrics = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "interest_coverage",
    "asset_turnover"
]

values = [
    selected[m]
    for m in metrics
]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=values,
        theta=[
            "ROE",
            "Operating Margin",
            "Net Margin",
            "Interest Coverage",
            "Asset Turnover"
        ],
        fill="toself",
        name=company
    )
)

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------
# Peer Table
# ----------------------------------------

st.subheader("Peer Companies")

st.dataframe(
    peer_df[
        [
            "company_name",
            "return_on_equity_pct",
            "operating_profit_margin_pct",
            "net_profit_margin_pct",
            "interest_coverage",
            "asset_turnover"
        ]
    ],
    use_container_width=True
)