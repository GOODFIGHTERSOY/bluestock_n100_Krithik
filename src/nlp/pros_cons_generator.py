import pandas as pd
import numpy as np

# ----------------------------------------------------
# Load Files
# ----------------------------------------------------

financial = pd.read_csv("output/financial_ratios.csv")

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies = companies.rename(columns={"id": "company_id"})

# ----------------------------------------------------
# Latest Financials
# ----------------------------------------------------

financial["year"] = financial["year"].astype(str)

latest = (
    financial
    .sort_values("year")
    .drop_duplicates("company_id", keep="last")
)

latest = latest.merge(
    companies[["company_id", "company_name"]],
    on="company_id",
    how="left"
)

# ----------------------------------------------------
# Rule Engine
# ----------------------------------------------------

def generate_pros(row):

    pros = []

    if row.get("return_on_equity_pct",0) > 15:
        pros.append("Strong return on equity.")

    if row.get("roce_calculated",0) > 15:
        pros.append("Healthy return on capital employed.")

    if row.get("net_profit_margin_pct",0) > 15:
        pros.append("Excellent profit margin.")

    if row.get("operating_profit_margin_pct",0) > 20:
        pros.append("Strong operating efficiency.")

    if row.get("debt_to_equity",99) < 0.5:
        pros.append("Low debt burden.")

    if row.get("interest_coverage",0) > 5:
        pros.append("Comfortable interest coverage.")

    if row.get("asset_turnover",0) > 1:
        pros.append("Efficient asset utilization.")

    if row.get("free_cash_flow",0) > 0:
        pros.append("Positive free cash flow.")

    if row.get("cfo_quality_score",0) > 70:
        pros.append("Strong operating cash generation.")

    if row.get("fcf_conversion",0) > 80:
        pros.append("High cash conversion.")

    if row.get("capex_intensity",0) < 20:
        pros.append("Controlled capital expenditure.")

    if len(pros)==0:
        pros.append("Stable financial performance.")

    return "; ".join(pros[:12])


def generate_cons(row):

    cons=[]

    if row.get("return_on_equity_pct",100)<10:
        cons.append("Low return on equity.")

    if row.get("roce_calculated",100)<10:
        cons.append("Weak capital efficiency.")

    if row.get("net_profit_margin_pct",100)<8:
        cons.append("Thin profit margins.")

    if row.get("operating_profit_margin_pct",100)<10:
        cons.append("Weak operating margin.")

    if row.get("debt_to_equity",0)>1:
        cons.append("High debt levels.")

    if row.get("interest_coverage",100)<2:
        cons.append("Low interest coverage.")

    if row.get("asset_turnover",100)<0.5:
        cons.append("Low asset utilization.")

    if row.get("free_cash_flow",1)<0:
        cons.append("Negative free cash flow.")

    if row.get("cfo_quality_score",100)<50:
        cons.append("Weak operating cash flow.")

    if row.get("fcf_conversion",100)<40:
        cons.append("Poor cash conversion.")

    if row.get("capex_intensity",0)>40:
        cons.append("High capital expenditure.")

    if len(cons)==0:
        cons.append("No major financial concerns.")

    return "; ".join(cons[:12])

# ----------------------------------------------------
# Generate
# ----------------------------------------------------

latest["pros"] = latest.apply(
    generate_pros,
    axis=1
)

latest["cons"] = latest.apply(
    generate_cons,
    axis=1
)

output = latest[
    [
        "company_id",
        "company_name",
        "pros",
        "cons"
    ]
]

output.to_csv(
    "output/pros_cons_generated.csv",
    index=False
)

print("Generated:",len(output),"companies")
print("Saved to output/pros_cons_generated.csv")