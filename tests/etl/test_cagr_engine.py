import pandas as pd

from src.analytics.cagr_engine import (
    safe_cagr,
    turnaround_flag,
    revenue_cagr
)


def test_safe_cagr():

    cagr = safe_cagr(100, 200, 5)

    assert round(cagr, 2) == 14.87


def test_negative_start():

    assert safe_cagr(-100, 200, 5) is None


def test_zero_start():

    assert safe_cagr(0, 100, 5) is None


def test_turnaround_true():

    df = pd.DataFrame({

        "year": [2019, 2020, 2021],

        "net_profit": [-10, -2, 5]

    })

    assert turnaround_flag(df)


def test_turnaround_false():

    df = pd.DataFrame({

        "year": [2019, 2020, 2021],

        "net_profit": [10, 15, 20]

    })

    assert turnaround_flag(df) is False


def test_revenue_cagr():

    df = pd.DataFrame({

        "year": [2019, 2020, 2021, 2022],

        "sales": [100, 120, 140, 180]

    })

    assert revenue_cagr(df, 3) > 0