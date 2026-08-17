import sqlite3
import pandas as pd

DATABASE = "data/nifty100.db"
PEER_FILE = "data/raw/peer_groups.xlsx"


# ----------------------------------------------------
# Metrics to Rank
# ----------------------------------------------------

METRICS = [
    "return_on_equity_pct",
    "roce_calculated",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow",
    "cfo_quality_score",
]


# ----------------------------------------------------
# Calculate Peer Percentiles
# ----------------------------------------------------

def calculate_peer_percentiles():

    print("=" * 60)
    print("Loading Financial Ratios...")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    print(f"Financial Ratio Rows : {len(ratios)}")

    print("\nLoading Peer Groups...")

    peer = pd.read_excel(PEER_FILE)

    print(f"Peer Group Rows : {len(peer)}")

    # ------------------------------------------------
    # Merge
    # ------------------------------------------------

    df = ratios.merge(
        peer,
        on="company_id",
        how="left"
    )

    print(f"Merged Rows : {len(df)}")

    results = []

    # ------------------------------------------------
    # Rank Each Peer Group
    # ------------------------------------------------

    for group_name, group in df.groupby("peer_group_name"):

        print(f"\nProcessing Peer Group : {group_name}")

        group = group.copy()

        for metric in METRICS:

            if metric not in group.columns:
                print(f"Skipping {metric}")
                continue

            temp = group[
                [
                    "company_id",
                    "year",
                    "peer_group_name",
                    metric
                ]
            ].copy()

            temp.rename(
                columns={
                    metric: "metric_value"
                },
                inplace=True
            )

            temp["metric"] = metric

            # -----------------------------
            # Debt to Equity
            # Lower is Better
            # -----------------------------

            if metric == "debt_to_equity":

                temp["percent_rank"] = (
                    1
                    - temp["metric_value"].rank(
                        pct=True,
                        method="average"
                    )
                ) * 100

            # -----------------------------
            # Remaining Metrics
            # Higher is Better
            # -----------------------------

            else:

                temp["percent_rank"] = (
                    temp["metric_value"].rank(
                        pct=True,
                        method="average"
                    )
                ) * 100

            results.append(temp)

    # ------------------------------------------------
    # Combine
    # ------------------------------------------------

    final = pd.concat(
        results,
        ignore_index=True
    )

    final.rename(
        columns={
            "metric_value": "value"
        },
        inplace=True
    )

    final = final[
        [
            "company_id",
            "year",
            "peer_group_name",
            "metric",
            "value",
            "percent_rank",
        ]
    ]

    print("\n" + "=" * 60)
    print("Peer Percentiles Generated")
    print("=" * 60)

    print(final.head())

    final.to_csv(
        "output/peer_percentiles.csv",
        index=False
    )

    print("\nSaved : output/peer_percentiles.csv")

    return final


# ----------------------------------------------------
# Run Standalone
# ----------------------------------------------------

if __name__ == "__main__":

    calculate_peer_percentiles()