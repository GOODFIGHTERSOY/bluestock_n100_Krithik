import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

st.title("📈 Trend Analysis")
st.markdown(
    "<h4 style='color:#012970;'>Financial Performance Trends</h4>",
    unsafe_allow_html=True,
)

# ==========================================================
# LOAD DATA
# ==========================================================

financial = pd.read_csv("output/financial_ratios.csv")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.rename(columns={"id": "company_id"})

# Merge company names if available
if "company_name" in companies.columns:

    financial = financial.merge(
        companies[["company_id", "company_name"]],
        on="company_id",
        how="left",
    )

# ==========================================================
# COMPANY SELECTOR
# ==========================================================

if "company_name" in financial.columns:

    company = st.selectbox(
        "Select Company",
        sorted(financial["company_name"].dropna().unique())
    )

    company_df = financial[
        financial["company_name"] == company
    ].copy()

else:

    company = st.selectbox(
        "Select Company ID",
        sorted(financial["company_id"].unique())
    )

    company_df = financial[
        financial["company_id"] == company
    ].copy()

# ==========================================================
# YEAR SORT
# ==========================================================

company_df["year"] = company_df["year"].astype(str)

company_df = company_df.sort_values("year")

# ==========================================================
# METRICS
# ==========================================================

metrics = {

    "return_on_equity_pct": "Return on Equity (%)",

    "roce_calculated": "ROCE (%)",

    "net_profit_margin_pct": "Net Profit Margin (%)",

    "operating_profit_margin_pct": "Operating Profit Margin (%)",

    "debt_to_equity": "Debt to Equity",

    "interest_coverage": "Interest Coverage",

    "asset_turnover": "Asset Turnover",

    "free_cash_flow": "Free Cash Flow",

    "cfo_quality_score": "CFO Quality Score",

    "fcf_conversion": "FCF Conversion",

    "capex_intensity": "Capex Intensity"

}

available_metrics = [
    x for x in metrics.keys()
    if x in company_df.columns
]

metric = st.selectbox(
    "Metric",
    available_metrics,
    format_func=lambda x: metrics[x]
)

# ==========================================================
# CHART
# ==========================================================

fig = px.line(

    company_df,

    x="year",

    y=metric,

    markers=True,

    color_discrete_sequence=["#6F42C1"]

)

fig.update_traces(

    line=dict(
        width=4
    ),

    marker=dict(

        size=9,

        color="#F05537"

    )

)

fig.update_layout(

    title=dict(

        text=metrics[metric],

        font=dict(

            size=22,

            color="#012970"

        )

    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    font=dict(

        color="black"

    ),

    xaxis=dict(

        title="Year",

        showgrid=True,

        gridcolor="#ECECEC",

        linecolor="#012970"

    ),

    yaxis=dict(

        title=metrics[metric],

        showgrid=True,

        gridcolor="#ECECEC",

        linecolor="#012970"

    ),

    hoverlabel=dict(

        bgcolor="white",

        font_color="black"

    )

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# DATA TABLE
# ==========================================================

st.markdown("### 📊 Trend Data")

display_cols = ["year", metric]

st.dataframe(
    company_df[display_cols],
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# SUMMARY
# ==========================================================

st.markdown("### 📈 Summary Statistics")

summary = company_df[metric].describe().to_frame()

summary.columns = ["Value"]

st.dataframe(
    summary,
    use_container_width=True
)