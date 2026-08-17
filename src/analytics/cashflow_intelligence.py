import pandas as pd

# --------------------------------------------------
# Load Financial Ratios
# --------------------------------------------------

financial = pd.read_csv("output/financial_ratios.csv")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.rename(columns={"id": "company_id"})

# --------------------------------------------------
# Latest Financial Year
# --------------------------------------------------

financial["year"] = financial["year"].astype(str)

latest = (
    financial
    .sort_values("year")
    .drop_duplicates("company_id", keep="last")
)

# --------------------------------------------------
# Merge Company Names
# --------------------------------------------------

if "company_name" in companies.columns:

    latest = latest.merge(

        companies[
            [
                "company_id",
                "company_name"
            ]
        ],

        on="company_id",

        how="left"
    )

# --------------------------------------------------
# CFO Quality Classification
# --------------------------------------------------

def classify_cfo(score):

    if pd.isna(score):
        return "Unknown"

    if score >= 80:
        return "Excellent"

    elif score >= 60:
        return "Good"

    elif score >= 40:
        return "Average"

    return "Poor"


latest["cfo_quality"] = (
    latest["cfo_quality_score"]
    .apply(classify_cfo)
)

# --------------------------------------------------
# CapEx Classification
# --------------------------------------------------

def classify_capex(value):

    if pd.isna(value):
        return "Unknown"

    if value < 20:
        return "Low"

    elif value < 40:
        return "Moderate"

    return "High"


latest["capex_level"] = (
    latest["capex_intensity"]
    .apply(classify_capex)
)

# --------------------------------------------------
# Distress Flag
# --------------------------------------------------

def distress(row):

    reasons = []

    if row["free_cash_flow"] < 0:
        reasons.append("Negative FCF")

    if row["fcf_conversion"] < 40:
        reasons.append("Low Cash Conversion")

    if row["interest_coverage"] < 2:
        reasons.append("Weak Interest Coverage")

    if row["debt_to_equity"] > 1:
        reasons.append("High Debt")

    if len(reasons) == 0:
        return "Healthy"

    return ", ".join(reasons)


latest["distress_flag"] = (
    latest.apply(
        distress,
        axis=1
    )
)

# --------------------------------------------------
# Capital Allocation Matrix
# --------------------------------------------------

def allocation(row):

    if (
        row["free_cash_flow"] > 0
        and
        row["capex_intensity"] < 20
    ):
        return "Efficient Growth"

    elif (
        row["free_cash_flow"] > 0
        and
        row["capex_intensity"] >= 20
    ):
        return "Growth Investing"

    elif (
        row["free_cash_flow"] <= 0
        and
        row["capex_intensity"] >= 20
    ):
        return "Aggressive Investment"

    return "Cash Constrained"


latest["capital_allocation_matrix"] = (
    latest.apply(
        allocation,
        axis=1
    )
)

# --------------------------------------------------
# Final Output
# --------------------------------------------------

columns = [

    "company_id",

    "company_name",

    "free_cash_flow",

    "cfo_quality_score",

    "cfo_quality",

    "capex_intensity",

    "capex_level",

    "fcf_conversion",

    "interest_coverage",

    "debt_to_equity",

    "distress_flag",

    "capital_allocation_matrix"

]

columns = [
    c for c in columns
    if c in latest.columns
]

output = latest[columns]

output.to_excel(
    "output/cashflow_intelligence.xlsx",
    index=False
)

print("=" * 60)
print("Cash Flow Intelligence Generated")
print("=" * 60)
print("Companies :", len(output))
print("Saved : output/cashflow_intelligence.xlsx")