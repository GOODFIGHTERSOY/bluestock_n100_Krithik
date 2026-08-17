import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go

DATABASE = "data/nifty100.db"

OUTPUT_FOLDER = "reports/radar_charts"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Metrics to display
METRICS = [
    "return_on_equity_pct",
    "roce_calculated",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "asset_turnover",
    "interest_coverage",
    "cfo_quality_score",
]


def main():

    conn = sqlite3.connect(DATABASE)

    peer = pd.read_csv("output/peer_percentiles.csv")

    conn.close()

    companies = peer["company_id"].unique()

    print(f"Generating {len(companies)} radar charts...")

    for company in companies:

        company_df = peer[peer["company_id"] == company]

        latest = (
            company_df
            .sort_values("year")
            .drop_duplicates("metric", keep="last")
        )

        latest = latest[
            latest["metric"].isin(METRICS)
        ]

        latest = latest.sort_values("metric")

        labels = latest["metric"].tolist()

        values = latest["percent_rank"].fillna(0).tolist()

        # close polygon
        labels.append(labels[0])
        values.append(values[0])

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name=company
            )
        )

        fig.update_layout(

            title=company,

            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0,100]
                )
            ),

            showlegend=False
        )

        fig.write_image(
            f"{OUTPUT_FOLDER}/{company}.png",
            width=700,
            height=700
        )

        print(f"Generated {company}")

    print("\nDone!")


if __name__ == "__main__":
    main()