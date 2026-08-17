import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------

financial = pd.read_excel("data/raw/financial_ratios.xlsx")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.dropna(subset=["company_name"])

# ---------------------------------------------------
# Page Title
# ---------------------------------------------------

st.title("🏢 Company Profile")

company_name = st.selectbox(
    "Select Company",
    sorted(companies["company_name"].unique())
)

company_id = companies.loc[
    companies["company_name"] == company_name,
    "id"
].iloc[0]

company_df = financial[
    financial["company_id"] == company_id
].copy()

company_df = company_df.sort_values("year")

if company_df.empty:
    st.warning("No data available.")
    st.stop()

latest = company_df.iloc[-1]

# ---------------------------------------------------
# Company Information
# ---------------------------------------------------

st.subheader(company_name)

info = companies[
    companies["id"] == company_id
].iloc[0]

col1, col2 = st.columns([1,3])

with col1:

    if "company_logo" in info.index:

        if pd.notna(info["company_logo"]):

            st.image(
                info["company_logo"],
                width=120
            )

with col2:

    if "website" in info.index:

        st.write("**Website:**", info["website"])

    if "about_company" in info.index:

        st.write(info["about_company"])

st.divider()

# ---------------------------------------------------
# KPI Cards
# ---------------------------------------------------

st.subheader("Latest Financial KPIs")

a,b,c,d = st.columns(4)

a.metric(
    "ROE",
    f"{latest['return_on_equity_pct']:.2f}%"
)

b.metric(
    "Operating Margin",
    f"{latest['operating_profit_margin_pct']:.2f}%"
)

c.metric(
    "Net Margin",
    f"{latest['net_profit_margin_pct']:.2f}%"
)

d.metric(
    "Debt / Equity",
    f"{latest['debt_to_equity']:.2f}"
)

e,f,g,h = st.columns(4)

e.metric(
    "Interest Coverage",
    f"{latest['interest_coverage']:.2f}"
)

f.metric(
    "Asset Turnover",
    f"{latest['asset_turnover']:.2f}"
)

g.metric(
    "EPS",
    f"{latest['earnings_per_share']:.2f}"
)

h.metric(
    "Book Value",
    f"{latest['book_value_per_share']:.2f}"
)

st.divider()

# ---------------------------------------------------
# Financial Charts
# ---------------------------------------------------

st.subheader("10-Year Financial Performance")

chart1, chart2 = st.columns(2)

with chart1:

    fig = px.bar(
        company_df,
        x="year",
        y="return_on_equity_pct",
        title="Return on Equity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with chart2:

    fig = px.bar(
        company_df,
        x="year",
        y="operating_profit_margin_pct",
        title="Operating Profit Margin"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

chart3, chart4 = st.columns(2)

with chart3:

    fig = px.bar(
        company_df,
        x="year",
        y="net_profit_margin_pct",
        title="Net Profit Margin"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with chart4:

    fig = px.bar(
        company_df,
        x="year",
        y="free_cash_flow_cr",
        title="Free Cash Flow (Cr)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ---------------------------------------------------
# Balance Sheet Metrics
# ---------------------------------------------------

st.subheader("Balance Sheet Metrics")

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Total Debt (Cr)",
    f"{latest['total_debt_cr']:.2f}"
)

c2.metric(
    "Cash From Operations (Cr)",
    f"{latest['cash_from_operations_cr']:.2f}"
)

c3.metric(
    "CAPEX (Cr)",
    f"{latest['capex_cr']:.2f}"
)

c4.metric(
    "Dividend Payout %",
    f"{latest['dividend_payout_ratio_pct']:.2f}%"
)

st.divider()

# ---------------------------------------------------
# Historical Financial Table
# ---------------------------------------------------

st.subheader("Historical Financial Ratios")

st.dataframe(
    company_df,
    use_container_width=True
)

# ---------------------------------------------------
# Download CSV
# ---------------------------------------------------

csv = company_df.to_csv(index=False)

st.download_button(
    "⬇ Download Company Data",
    csv,
    file_name=f"{company_name}_financials.csv",
    mime="text/csv"
)