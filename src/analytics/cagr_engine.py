import pandas as pd
import numpy as np


def safe_cagr(start_value, end_value, years):
    """
    Calculates CAGR safely.

    Returns None if:
    - start <= 0
    - end <= 0
    - years <= 0
    """

    if (
        start_value is None
        or end_value is None
        or years <= 0
    ):
        return None

    if start_value <= 0:
        return None

    if end_value <= 0:
        return None

    return ((end_value / start_value) ** (1 / years) - 1) * 100


def calculate_metric_cagr(df, value_column, years):
    """
    Calculates CAGR for one metric.

    Parameters
    ----------
    df : company dataframe sorted by year
    value_column : sales / net_profit / eps
    years : 3 / 5 / 10
    """

    if len(df) < years + 1:
        return None

    df = df.sort_values("year")

    start = df.iloc[-(years + 1)][value_column]
    end = df.iloc[-1][value_column]

    return safe_cagr(start, end, years)


def revenue_cagr(df, years):
    return calculate_metric_cagr(df, "sales", years)


def pat_cagr(df, years):
    return calculate_metric_cagr(df, "net_profit", years)


def eps_cagr(df, years):
    return calculate_metric_cagr(df, "eps", years)


def turnaround_flag(df):
    """
    Company is considered a turnaround if:

    earliest PAT < 0
    latest PAT > 0
    """

    if len(df) < 2:
        return False

    df = df.sort_values("year")

    first = df.iloc[0]["net_profit"]
    last = df.iloc[-1]["net_profit"]

    return bool(first < 0 and last > 0)


def calculate_all_cagr(df):
    """
    Returns dictionary of all metrics.
    """

    return {

        "revenue_cagr_3y":
            revenue_cagr(df, 3),

        "revenue_cagr_5y":
            revenue_cagr(df, 5),

        "revenue_cagr_10y":
            revenue_cagr(df, 10),

        "pat_cagr_3y":
            pat_cagr(df, 3),

        "pat_cagr_5y":
            pat_cagr(df, 5),

        "pat_cagr_10y":
            pat_cagr(df, 10),

        "eps_cagr_3y":
            eps_cagr(df, 3),

        "eps_cagr_5y":
            eps_cagr(df, 5),

        "eps_cagr_10y":
            eps_cagr(df, 10),

        "turnaround":
            turnaround_flag(df)

    }