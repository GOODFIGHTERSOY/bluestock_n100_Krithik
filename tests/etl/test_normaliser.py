from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)


# =========================
# YEAR TESTS - 20
# =========================

def test_year_1():
    assert normalize_year(2023) == 2023


def test_year_2():
    assert normalize_year("2023") == 2023


def test_year_3():
    assert normalize_year("FY2023") == 2023


def test_year_4():
    assert normalize_year("FY 2023") == 2023


def test_year_5():
    assert normalize_year("FY23") == 2023


def test_year_6():
    assert normalize_year("FY 23") == 2023


def test_year_7():
    assert normalize_year("2022-23") == 2023


def test_year_8():
    assert normalize_year("2023-24") == 2024


def test_year_9():
    assert normalize_year("2022") == 2022


def test_year_10():
    assert normalize_year("2024") == 2024


def test_year_11():
    assert normalize_year(2022) == 2022


def test_year_12():
    assert normalize_year(2024) == 2024


def test_year_13():
    assert normalize_year("FY22") == 2022


def test_year_14():
    assert normalize_year("FY24") == 2024


def test_year_15():
    assert normalize_year("2021-22") == 2022


def test_year_16():
    assert normalize_year("2020-21") == 2021


def test_year_17():
    assert normalize_year("FY2021") == 2021


def test_year_18():
    assert normalize_year("FY2022") == 2022


def test_year_19():
    assert normalize_year(None) is None


def test_year_20():
    assert normalize_year("") is None


# =========================
# TICKER TESTS - 20
# =========================

def test_ticker_1():
    assert normalize_ticker("TCS") == "TCS"


def test_ticker_2():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_3():
    assert normalize_ticker(" TCS ") == "TCS"


def test_ticker_4():
    assert normalize_ticker("TCS.NS") == "TCS"


def test_ticker_5():
    assert normalize_ticker("TCS.BO") == "TCS"


def test_ticker_6():
    assert normalize_ticker("tcs.ns") == "TCS"


def test_ticker_7():
    assert normalize_ticker("tcs.bo") == "TCS"


def test_ticker_8():
    assert normalize_ticker("INFY") == "INFY"


def test_ticker_9():
    assert normalize_ticker("infy") == "INFY"


def test_ticker_10():
    assert normalize_ticker(" INFY ") == "INFY"


def test_ticker_11():
    assert normalize_ticker("INFY.NS") == "INFY"


def test_ticker_12():
    assert normalize_ticker("INFY.BO") == "INFY"


def test_ticker_13():
    assert normalize_ticker("RELIANCE") == "RELIANCE"


def test_ticker_14():
    assert normalize_ticker("reliance") == "RELIANCE"


def test_ticker_15():
    assert normalize_ticker("RELIANCE.NS") == "RELIANCE"


def test_ticker_16():
    assert normalize_ticker("RELIANCE.BO") == "RELIANCE"


def test_ticker_17():
    assert normalize_ticker("HDFCBANK") == "HDFCBANK"


def test_ticker_18():
    assert normalize_ticker("hdfcbank") == "HDFCBANK"


def test_ticker_19():
    assert normalize_ticker(None) is None


def test_ticker_20():
    assert normalize_ticker("") == ""