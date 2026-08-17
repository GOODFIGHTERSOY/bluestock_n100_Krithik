import pandas as pd
import numpy as np


def calculate_bank_roce(companies_df, sectors_df):
    """
    Banks and NBFCs don't use conventional ROCE.
    We therefore compare each company's ROCE against
    the average ROCE of its sector.

    Returns:
        DataFrame with
        company_id
        roce_percentage
        sector_average_roce
        roce_difference
        anomaly
    """

    # Merge sector information
    df = companies_df.merge(
        sectors_df,
        left_on="id",
        right_on="company_id",
        how="left"
    )

    # Average ROCE by sector
    sector_avg = (
        df.groupby("broad_sector")["roce_percentage"]
        .mean()
        .reset_index()
        .rename(columns={
            "roce_percentage": "sector_average_roce"
        })
    )

    df = df.merge(
        sector_avg,
        on="broad_sector",
        how="left"
    )

    # Difference from sector average
    df["roce_difference"] = (
        df["roce_percentage"] -
        df["sector_average_roce"]
    )

    # Flag anomaly if deviation >20 percentage points
    df["anomaly"] = (
        df["roce_difference"].abs() > 20
    )

    return df[
        [
            "id",
            "company_name",
            "broad_sector",
            "roce_percentage",
            "sector_average_roce",
            "roce_difference",
            "anomaly"
        ]
    ]