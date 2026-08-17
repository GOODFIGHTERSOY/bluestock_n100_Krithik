import streamlit as st

from src.dashboard_app.loader import load_db
from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

financial = load_db("financial_ratios")

companies = sorted(financial["company_id"].unique())

company = st.selectbox(
    "Select Company",
    companies
)

st.dataframe(

    financial[
        financial.company_id == company
    ]
)