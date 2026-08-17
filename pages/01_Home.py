import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

# ----------------------------------------
# Load Data
# ----------------------------------------

financial = pd.read_excel("data/raw/financial_ratios.xlsx")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

# Keep only valid companies
companies = companies.dropna(subset=["company_name"])

company_names = sorted(companies["company_name"].unique())

# ----------------------------------------
# Title
# ----------------------------------------

st.title("🏠 Bluestock N100 Dashboard")
st.markdown("### Nifty 100 Company Financial Analytics")

st.divider()

# ----------------------------------------
# Company Search
# ----------------------------------------

selected_company = st.selectbox(
    "Search Company",
    company_names
)

company_id = companies.loc[
    companies["company_name"] == selected_company,
    "id"
].iloc[0]

company_df = financial[
    financial["company_id"] == company_id
].copy()

company_df = company_df.sort_values("year")

if company_df.empty:
    st.warning("No financial data available.")
    st.stop()

latest = company_df.iloc[-1]

# ----------------------------------------
# KPI Cards
# ----------------------------------------

st.subheader("Key Financial Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "ROE",
    f"{latest['return_on_equity_pct']:.2f}%"
)

col2.metric(
    "Operating Margin",
    f"{latest['operating_profit_margin_pct']:.2f}%"
)

col3.metric(
    "Net Profit Margin",
    f"{latest['net_profit_margin_pct']:.2f}%"
)

col4.metric(
    "Debt / Equity",
    f"{latest['debt_to_equity']:.2f}"
)

st.divider()

# ----------------------------------------
# Charts Row 1
# ----------------------------------------

c1, c2 = st.columns(2)

with c1:

    fig = px.bar(
        company_df,
        x="year",
        y="return_on_equity_pct",
        title="10-Year Return on Equity"
    )

    st.plotly_chart(fig, use_container_width=True)

with c2:

    fig = px.bar(
        company_df,
        x="year",
        y="operating_profit_margin_pct",
        title="10-Year Operating Margin"
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------
# Charts Row 2
# ----------------------------------------

c3, c4 = st.columns(2)

with c3:

    fig = px.bar(
        company_df,
        x="year",
        y="net_profit_margin_pct",
        title="10-Year Net Profit Margin"
    )

    st.plotly_chart(fig, use_container_width=True)

with c4:

    fig = px.bar(
        company_df,
        x="year",
        y="free_cash_flow_cr",
        title="10-Year Free Cash Flow"
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------
# Additional Metrics
# ----------------------------------------

st.subheader("Additional Financial Metrics")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "EPS",
    f"{latest['earnings_per_share']:.2f}"
)

m2.metric(
    "Book Value",
    f"{latest['book_value_per_share']:.2f}"
)

m3.metric(
    "Interest Coverage",
    f"{latest['interest_coverage']:.2f}"
)

m4.metric(
    "Asset Turnover",
    f"{latest['asset_turnover']:.2f}"
)

st.divider()

# ----------------------------------------
# Historical Data
# ----------------------------------------

st.subheader("Historical Financial Ratios")

st.dataframe(
    company_df,
    use_container_width=True
)