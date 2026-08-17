import pandas as pd


# -------------------------------------------------
# Safe Division
# -------------------------------------------------

def safe_divide(numerator, denominator):
    if pd.isna(numerator) or pd.isna(denominator):
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# -------------------------------------------------
# Free Cash Flow
# -------------------------------------------------

def free_cash_flow(cfo, capex):

    if pd.isna(cfo) or pd.isna(capex):
        return None

    return cfo - capex


# -------------------------------------------------
# CFO Quality
# -------------------------------------------------

def cfo_quality_score(cfo, net_profit):

    return safe_divide(cfo, net_profit)


# -------------------------------------------------
# CapEx Intensity
# -------------------------------------------------

def capex_intensity(capex, cfo):

    return safe_divide(capex, cfo)


# -------------------------------------------------
# FCF Conversion
# -------------------------------------------------

def fcf_conversion(cfo, capex, net_profit):

    fcf = free_cash_flow(cfo, capex)

    return safe_divide(fcf, net_profit)


# -------------------------------------------------
# Capital Allocation Pattern
# -------------------------------------------------

def capital_allocation_pattern(cfo, capex):

    if pd.isna(cfo) or pd.isna(capex):
        return "Unknown"

    if cfo <= 0 and capex <= 0:
        return "No Operations"

    if cfo > 0 and capex == 0:
        return "Cash Generator"

    if cfo > 0 and capex < cfo:
        return "Healthy Growth"

    if cfo > 0 and capex == cfo:
        return "Reinvestment"

    if cfo > 0 and capex > cfo:
        return "Aggressive Expansion"

    if cfo < 0 and capex > 0:
        return "Cash Burn"

    if cfo < 0 and capex == 0:
        return "Operational Weakness"

    return "Other"


# -------------------------------------------------
# Main Function
# -------------------------------------------------

def calculate_cashflow_kpis(cashflow_df, profit_df):

    """
    cashflow_df : cashflow table
    profit_df   : profitandloss table
    """

    df = cashflow_df.merge(
        profit_df[
            [
                "company_id",
                "year",
                "net_profit"
            ]
        ],
        on=["company_id", "year"],
        how="left"
    )

    # CFO
    df["cash_from_operations_cr"] = df["operating_activity"]

    # Approximate CapEx
    df["capex_cr"] = df["investing_activity"].abs()

    # Free Cash Flow
    df["free_cash_flow"] = df.apply(
        lambda x: free_cash_flow(
            x["cash_from_operations_cr"],
            x["capex_cr"]
        ),
        axis=1
    )

    # CFO Quality
    df["cfo_quality_score"] = df.apply(
        lambda x: cfo_quality_score(
            x["cash_from_operations_cr"],
            x["net_profit"]
        ),
        axis=1
    )

    # CapEx Intensity
    df["capex_intensity"] = df.apply(
        lambda x: capex_intensity(
            x["capex_cr"],
            x["cash_from_operations_cr"]
        ),
        axis=1
    )

    # FCF Conversion
    df["fcf_conversion"] = df.apply(
        lambda x: fcf_conversion(
            x["cash_from_operations_cr"],
            x["capex_cr"],
            x["net_profit"]
        ),
        axis=1
    )

    # Capital Allocation
    df["capital_allocation_pattern"] = df.apply(
        lambda x: capital_allocation_pattern(
            x["cash_from_operations_cr"],
            x["capex_cr"]
        ),
        axis=1
    )

    return df[
        [
            "company_id",
            "year",
            "free_cash_flow",
            "cfo_quality_score",
            "capex_intensity",
            "fcf_conversion",
            "capital_allocation_pattern"
        ]
    ]