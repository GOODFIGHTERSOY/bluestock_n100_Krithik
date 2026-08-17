import pandas as pd

from src.analytics.cashflow_kpi import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion,
    capital_allocation_pattern,
)


def test_fcf():

    assert free_cash_flow(100, 40) == 60


def test_fcf_negative():

    assert free_cash_flow(50, 80) == -30


def test_cfo_quality():

    assert cfo_quality_score(120, 100) == 1.2


def test_capex_intensity():

    assert capex_intensity(30, 120) == 0.25


def test_fcf_conversion():

    assert fcf_conversion(100, 40, 60) == 1.0


def test_cash_generator():

    assert capital_allocation_pattern(100, 0) == "Cash Generator"


def test_healthy_growth():

    assert capital_allocation_pattern(100, 60) == "Healthy Growth"


def test_reinvestment():

    assert capital_allocation_pattern(100, 100) == "Reinvestment"


def test_aggressive_expansion():

    assert capital_allocation_pattern(100, 150) == "Aggressive Expansion"


def test_cash_burn():

    assert capital_allocation_pattern(-100, 50) == "Cash Burn"