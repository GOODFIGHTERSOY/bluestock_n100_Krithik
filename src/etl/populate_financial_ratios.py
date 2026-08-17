import sqlite3
import pandas as pd

from src.analytics.profitability_ratio import calculate_profitability_ratios
from src.analytics.leverage_efficiency import calculate_leverage_efficiency
from src.analytics.cashflow_kpi import calculate_cashflow_kpis
from src.analytics.bank_roce import calculate_bank_roce

DATABASE = "data/nifty100.db"


def populate_financial_ratios():

    conn = sqlite3.connect(DATABASE)

    print("=" * 60)
    print("Reading source tables...")
    print("=" * 60)

    # ---------------------------------------------------
    # Profit & Loss
    # ---------------------------------------------------

    pl = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn
    )

    # ---------------------------------------------------
    # Balance Sheet
    # ---------------------------------------------------

    bs = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings,
            total_assets
        FROM balancesheet
        """,
        conn
    )

    # ---------------------------------------------------
    # Companies
    # ---------------------------------------------------

    companies = pd.read_sql(
        """
        SELECT
            id,
            company_name,
            roce_percentage,
            roe_percentage
        FROM companies
        """,
        conn
    )

    # ---------------------------------------------------
    # Sectors
    # ---------------------------------------------------

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn
    )

    # ---------------------------------------------------
    # Cash Flow
    # ---------------------------------------------------

    cashflow = pd.read_sql(
        "SELECT * FROM cashflow",
        conn
    )

    print("Source tables loaded successfully.\n")

    # ===================================================
    # Profitability Ratios
    # ===================================================

    print("Calculating Profitability Ratios...")

    profitability_df = calculate_profitability_ratios(
        pl,
        bs,
        companies
    )

    # ===================================================
    # Leverage & Efficiency
    # ===================================================

    print("Calculating Leverage & Efficiency Ratios...")

    leverage_df = calculate_leverage_efficiency(
        pl,
        bs,
        companies,
        sectors
    )

    # ===================================================
    # Cash Flow KPIs
    # ===================================================

    print("Calculating Cash Flow KPIs...")

    cashflow_df = calculate_cashflow_kpis(
        cashflow,
        pl
    )

    # ===================================================
    # Bank / NBFC ROCE Validation
    # ===================================================

    print("Checking Bank/NBFC ROCE...")

    bank_roce_df = calculate_bank_roce(
        companies,
        sectors
    )

    bank_roce_df.to_csv(
        "output/roce_anomalies.csv",
        index=False
    )

    print("Saved: output/roce_anomalies.csv")

    # ===================================================
    # Merge All Ratios
    # ===================================================

    print("Merging ratio tables...")

    final_df = profitability_df.merge(
        leverage_df,
        on=["company_id", "year"],
        how="left"
    )

    final_df = final_df.merge(
        cashflow_df,
        on=["company_id", "year"],
        how="left"
    )

    print(f"Rows generated: {len(final_df)}")

    # ===================================================
    # Save to SQLite
    # ===================================================

    print("Writing financial_ratios table...")

    final_df.to_sql(
        "financial_ratios",
        conn,
        if_exists="replace",
        index=False
    )

    conn.commit()

    print("\n" + "=" * 60)
    print("financial_ratios table updated successfully!")
    print("=" * 60)

    conn.close()


if __name__ == "__main__":
    populate_financial_ratios()