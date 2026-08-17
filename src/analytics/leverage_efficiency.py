import pandas as pd


# -----------------------------------------------------
# Helper Function
# -----------------------------------------------------

def safe_divide(a, b):
    """
    Safely divide two numbers.
    Returns None if denominator is zero or values are missing.
    """
    if pd.isna(a) or pd.isna(b):
        return None

    if b == 0:
        return None

    return a / b


# -----------------------------------------------------
# Main Function
# -----------------------------------------------------

def calculate_leverage_efficiency(pl_df, bs_df, companies_df, sectors_df):
    """
    Calculates:
        - Debt to Equity Ratio
        - Interest Coverage Ratio
        - Asset Turnover

    Parameters
    ----------
    pl_df : Profit & Loss dataframe
    bs_df : Balance Sheet dataframe
    companies_df : Companies dataframe
    sectors_df : Sectors dataframe

    Returns
    -------
    DataFrame
    """

    # ---------------------------------------------
    # Merge DataFrames
    # ---------------------------------------------

    df = pl_df.merge(
        bs_df[
            [
                "company_id",
                "year",
                "equity_capital",
                "reserves",
                "borrowings",
                "total_assets",
            ]
        ],
        on=["company_id", "year"],
        how="left",
    )

    df = df.merge(
        sectors_df[
            [
                "company_id",
                "broad_sector",
            ]
        ],
        on="company_id",
        how="left",
    )

    df = df.merge(
        companies_df[
            [
                "id",
                "company_name",
            ]
        ],
        left_on="company_id",
        right_on="id",
        how="left",
    )

    if "id_y" in df.columns:
        df.drop(columns=["id_y"], inplace=True)

    if "id_x" in df.columns:
        df.rename(columns={"id_x": "id"}, inplace=True)

    # ---------------------------------------------
    # Equity
    # ---------------------------------------------

    df["equity"] = (
        df["equity_capital"]
        + df["reserves"]
    )

    # ---------------------------------------------
    # Debt to Equity
    # ---------------------------------------------

    def calc_de(row):

        sector = str(row["broad_sector"]).lower()

        # Bank / Financial carve-out
        if sector == "financials":
            return None

        equity = row["equity"]

        if pd.isna(equity):
            return None

        if equity <= 0:
            return None

        return safe_divide(
            row["borrowings"],
            equity,
        )

    df["debt_to_equity"] = df.apply(
        calc_de,
        axis=1,
    )

    # ---------------------------------------------
    # Interest Coverage Ratio
    # ---------------------------------------------

    def calc_icr(row):

        interest = row["interest"]

        if pd.isna(interest):
            return None

        # Debt-free substitution
        if interest == 0:

            borrowings = row["borrowings"]

            if pd.notna(borrowings) and borrowings == 0:
                return None

            return None

        return safe_divide(
            row["operating_profit"],
            interest,
        )

    df["interest_coverage"] = df.apply(
        calc_icr,
        axis=1,
    )

    # ---------------------------------------------
    # Asset Turnover
    # ---------------------------------------------

    df["asset_turnover"] = df.apply(
        lambda row: safe_divide(
            row["sales"],
            row["total_assets"],
        ),
        axis=1,
    )

    # ---------------------------------------------
    # Return Required Columns
    # ---------------------------------------------

    return df[
        [
            "company_id",
            "year",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
        ]
    ]


# -----------------------------------------------------
# Standalone Testing
# -----------------------------------------------------

if __name__ == "__main__":

    import sqlite3

    DATABASE = "data/nifty100.db"

    conn = sqlite3.connect(DATABASE)

    pl = pd.read_sql("SELECT * FROM profitandloss", conn)

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
        conn,
    )

    companies = pd.read_sql(
        """
        SELECT
            id,
            company_name
        FROM companies
        """,
        conn,
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn,
    )

    result = calculate_leverage_efficiency(
        pl,
        bs,
        companies,
        sectors,
    )

    result.to_csv(
        "output/leverage_efficiency_ratios.csv",
        index=False,
    )

    print(result.head())

    conn.close()