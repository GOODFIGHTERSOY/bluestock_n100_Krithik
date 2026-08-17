import pandas as pd


def safe_divide(a, b):
    if pd.isna(a) or pd.isna(b):
        return None
    if b == 0:
        return None
    return a / b


def calculate_profitability_ratios(pl_df, bs_df, companies_df):

    # ---------------------------------------------------
    # Merge
    # ---------------------------------------------------

    df = pl_df.merge(
        bs_df[
            [
                "company_id",
                "year",
                "equity_capital",
                "reserves",
                "borrowings",
            ]
        ],
        on=["company_id", "year"],
        how="left",
    )

    df = df.merge(
        companies_df[
            [
                "id",
                "roce_percentage",
                "roe_percentage",
            ]
        ],
        left_on="company_id",
        right_on="id",
        how="left",
    )

    # ---------------------------------------------------
    # Equity
    # ---------------------------------------------------

    df["equity"] = df["equity_capital"].fillna(0) + df["reserves"].fillna(0)

    df["capital_employed"] = (
        df["equity"].fillna(0)
        + df["borrowings"].fillna(0)
    )

    # ---------------------------------------------------
    # Net Profit Margin
    # ---------------------------------------------------

    df["net_profit_margin_pct"] = (
        df.apply(
            lambda r: safe_divide(
                r["net_profit"],
                r["sales"],
            ),
            axis=1,
        )
        * 100
    )

    # ---------------------------------------------------
    # Operating Profit Margin
    # ---------------------------------------------------

    df["operating_profit_margin_pct"] = (
        df.apply(
            lambda r: safe_divide(
                r["operating_profit"],
                r["sales"],
            ),
            axis=1,
        )
        * 100
    )

    # ---------------------------------------------------
    # Use source value if calculation is obviously wrong
    # (bad source rows like HDFCLIFE, INDIGO etc.)
    # ---------------------------------------------------

    mask = (
        df["opm_percentage"].notna()
        & (
            (
                df["operating_profit_margin_pct"]
                - df["opm_percentage"]
            ).abs()
            > 10
        )
    )

    df.loc[
        mask,
        "operating_profit_margin_pct",
    ] = df.loc[
        mask,
        "opm_percentage",
    ]

    # ---------------------------------------------------
    # ROE
    # ---------------------------------------------------

    def calc_roe(row):

        if pd.isna(row["equity"]):
            return None

        if row["equity"] <= 0:
            return None

        return (
            row["net_profit"]
            / row["equity"]
        ) * 100

    df["return_on_equity_pct"] = df.apply(
        calc_roe,
        axis=1,
    )

    # ---------------------------------------------------
    # ROCE
    # ---------------------------------------------------

    def calc_roce(row):

        if pd.isna(row["capital_employed"]):
            return None

        if row["capital_employed"] <= 0:
            return None

        return (
            row["operating_profit"]
            / row["capital_employed"]
        ) * 100

    df["roce_calculated"] = df.apply(
        calc_roce,
        axis=1,
    )

    # ---------------------------------------------------
    # Validation
    # ---------------------------------------------------

    df["opm_difference"] = (
        df["operating_profit_margin_pct"]
        - df["opm_percentage"]
    ).abs()

    TOLERANCE = 5

    anomalies = df[
        df["opm_difference"] > TOLERANCE
    ]

    print("\n===================================")
    print("Profitability Validation")
    print("===================================")
    print(f"Rows Compared : {len(df)}")
    print(f"Maximum Difference : {df['opm_difference'].max()}")
    print(f"Average Difference : {df['opm_difference'].mean()}")
    print(f"Tolerance : ±{TOLERANCE}%")
    print(f"Anomalies : {len(anomalies)}")

    anomalies.to_csv(
        "output/opm_anomalies.csv",
        index=False,
    )

    print("Saved : output/opm_anomalies.csv")

    # ---------------------------------------------------
    # Return
    # ---------------------------------------------------

    return df[
        [
            "company_id",
            "year",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "roce_calculated",
        ]
    ]