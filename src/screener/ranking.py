import sqlite3
import pandas as pd

DATABASE = "data/nifty100.db"


def normalize(series, reverse=False):

    if series.max() == series.min():
        return pd.Series(1.0, index=series.index)

    norm = (series - series.min()) / (series.max() - series.min())

    if reverse:
        norm = 1 - norm

    return norm


def build_ranking():

    conn = sqlite3.connect(DATABASE)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    sectors = pd.read_sql(
        """
        SELECT company_id,
               broad_sector
        FROM sectors
        """,
        conn
    )

    conn.close()

    df = ratios.merge(
        sectors,
        on="company_id",
        how="left"
    )

    ranked = []

    for sector, group in df.groupby("broad_sector"):

        group = group.copy()

        group["roe_norm"] = normalize(
            group["return_on_equity_pct"]
        )

        group["roce_norm"] = normalize(
            group["roce_calculated"]
        )

        group["npm_norm"] = normalize(
            group["net_profit_margin_pct"]
        )

        group["opm_norm"] = normalize(
            group["operating_profit_margin_pct"]
        )

        group["de_norm"] = normalize(
            group["debt_to_equity"],
            reverse=True
        )

        group["icr_norm"] = normalize(
            group["interest_coverage"]
        )

        group["cfo_norm"] = normalize(
            group["cfo_quality_score"]
        )

        group["asset_norm"] = normalize(
            group["asset_turnover"]
        )

        group["fcf_norm"] = normalize(
            group["fcf_conversion"]
        )

        group["quality_score"] = (
            group["roe_norm"] +
            group["roce_norm"] +
            group["npm_norm"] +
            group["opm_norm"]
        ) / 4

        group["strength_score"] = (
            group["de_norm"] +
            group["icr_norm"] +
            group["cfo_norm"]
        ) / 3

        group["efficiency_score"] = (
            group["asset_norm"] +
            group["fcf_norm"]
        ) / 2

        group["composite_score"] = (
            group["quality_score"] * 0.50
            + group["strength_score"] * 0.30
            + group["efficiency_score"] * 0.20
        ) * 100

        ranked.append(group)

    final = pd.concat(ranked)

    final = final.sort_values(
        "composite_score",
        ascending=False
    )

    final["rank"] = range(
        1,
        len(final) + 1
    )

    final.to_excel(
        "output/screener_output.xlsx",
        index=False
    )

    print("=" * 60)
    print("Ranking Complete")
    print("=" * 60)

    print(final[
        [
            "rank",
            "company_id",
            "year",
            "broad_sector",
            "composite_score"
        ]
    ].head(20))

    print("\nSaved : output/screener_output.xlsx")


if __name__ == "__main__":
    build_ranking()