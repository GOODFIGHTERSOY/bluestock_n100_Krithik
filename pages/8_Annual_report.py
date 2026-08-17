import streamlit as st
import pandas as pd

from src.dashboard_app.config import configure_page, sidebar

configure_page()
sidebar()

st.title("📄 Annual Reports")

# ---------------------------------------------------
# Load Company Data
# ---------------------------------------------------

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.dropna(subset=["company_name"])

# ---------------------------------------------------
# Company Selection
# ---------------------------------------------------

company = st.selectbox(
    "Select Company",
    sorted(companies["company_name"].unique())
)

info = companies[
    companies["company_name"] == company
].iloc[0]

# ---------------------------------------------------
# Company Details
# ---------------------------------------------------

st.header(company)

if "about_company" in info.index and pd.notna(info["about_company"]):
    st.write(info["about_company"])

st.divider()

# ---------------------------------------------------
# Official Links
# ---------------------------------------------------

st.subheader("Official Resources")

col1, col2, col3 = st.columns(3)

with col1:

    if pd.notna(info.get("website")):
        st.link_button(
            "🌐 Company Website",
            info["website"]
        )

with col2:

    if pd.notna(info.get("nse_profile")):
        st.link_button(
            "📈 NSE Company Profile",
            info["nse_profile"]
        )

with col3:

    if pd.notna(info.get("bse_profile")):
        st.link_button(
            "📊 BSE Company Profile",
            info["bse_profile"]
        )

st.divider()

# ---------------------------------------------------
# Annual Reports
# ---------------------------------------------------

st.subheader("Annual Reports")

st.info(
"""
Most Indian listed companies publish their Annual Reports
inside the Investor Relations section accessible through the
official NSE Company Profile.

Click the button below to open the company's NSE page,
then navigate to:

**Announcements → Annual Reports**

or

**Investor Relations → Annual Reports**
"""
)

if pd.notna(info.get("nse_profile")):

    st.link_button(
        "📄 Open Annual Reports via NSE",
        info["nse_profile"]
    )

else:

    st.warning("NSE Profile unavailable.")

st.divider()

# ---------------------------------------------------
# Download Company Information
# ---------------------------------------------------

st.download_button(
    "⬇ Download Company Details",
    pd.DataFrame([info]).to_csv(index=False),
    file_name=f"{company}_details.csv",
    mime="text/csv"
)