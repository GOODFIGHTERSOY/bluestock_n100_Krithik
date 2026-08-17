import streamlit as st
import pandas as pd

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

st.title("🔎 Stock Screener")

# -----------------------------------------
# Load Data
# -----------------------------------------

df = pd.read_excel("data/raw/financial_ratios.xlsx")

# Latest year only

# Convert year to datetime
df["year_dt"] = pd.to_datetime(df["year"], errors="coerce")

# Keep latest record for each company
df = (
    df.sort_values("year_dt")
      .drop_duplicates("company_id", keep="last")
)

# Remove helper column
df = df.drop(columns="year_dt")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.dropna(subset=["company_name"])

companies = companies.rename(columns={"id": "company_id"})

df = df.merge(
    companies[["company_id", "company_name"]],
    on="company_id",
    how="left"
)

# -----------------------------------------
# Sidebar Filters
# -----------------------------------------

st.sidebar.header("Filters")

roe = st.sidebar.slider(
    "Minimum ROE %",
    0,
    50,
    15
)

opm = st.sidebar.slider(
    "Operating Margin %",
    0,
    60,
    15
)

npm = st.sidebar.slider(
    "Net Margin %",
    0,
    50,
    10
)

de = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    5.0,
    1.0
)

# -----------------------------------------
# Apply Filters
# -----------------------------------------

filtered = df[
    (df["return_on_equity_pct"] >= roe)
    &
    (df["operating_profit_margin_pct"] >= opm)
    &
    (df["net_profit_margin_pct"] >= npm)
    &
    (df["debt_to_equity"] <= de)
]

st.metric(
    "Companies Found",
    len(filtered)
)

st.dataframe(
    filtered,
    use_container_width=True
)

csv = filtered.to_csv(index=False)


st.download_button(
    "⬇ Download CSV",
    csv,
    file_name="screened_companies.csv",
    mime="text/csv"
)