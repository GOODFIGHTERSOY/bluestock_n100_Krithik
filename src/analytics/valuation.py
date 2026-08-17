import pandas as pd

# -----------------------------
# Load Data
# -----------------------------

financial = pd.read_excel("data/raw/financial_ratios.xlsx")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.rename(columns={"id": "company_id"})

# -----------------------------
# Latest Financials
# -----------------------------

financial["year_dt"] = pd.to_datetime(
    financial["year"],
    errors="coerce"
)

financial = (
    financial
    .sort_values("year_dt")
    .drop_duplicates("company_id", keep="last")
)

# -----------------------------
# Merge
# -----------------------------

df = financial.merge(
    companies,
    on="company_id",
    how="left"
)

# -----------------------------
# Estimated Market Cap
#
# If actual market cap exists,
# use it instead.
# -----------------------------

if "market_cap" not in df.columns:

    df["market_cap"] = (
        df["book_value_per_share"] *
        df["earnings_per_share"] *
        100
    )

# -----------------------------
# FCF Yield
# -----------------------------

df["fcf_yield"] = (
    df["free_cash_flow_cr"] /
    df["market_cap"]
) * 100

# -----------------------------
# Overvaluation Flag
# -----------------------------

df["overvaluation_flag"] = df["fcf_yield"].apply(

    lambda x:
    "Overvalued"
    if x < 2
    else
    "Fairly Valued"
)

# -----------------------------
# Keep Useful Columns
# -----------------------------

summary = df[[
    "company_id",
    "company_name",
    "market_cap",
    "free_cash_flow_cr",
    "fcf_yield",
    "overvaluation_flag"
]]

summary.to_excel(
    "output/valuation_summary.xlsx",
    index=False
)

print("valuation_summary.xlsx created")