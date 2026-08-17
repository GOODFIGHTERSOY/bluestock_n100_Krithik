import os
import sqlite3

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import app


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = "data\\nifty100.db"

client = TestClient(app)


# ============================================================
# DATABASE FIXTURE
# ============================================================

@pytest.fixture
def db():
    if not os.path.exists(DB_PATH):
        pytest.skip("Database not found")

    conn = sqlite3.connect(DB_PATH)

    yield conn

    conn.close()


@pytest.fixture
def ratios(db):
    return pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        db
    )


# ============================================================
# CATEGORY 1 — DATABASE TESTS
# ============================================================

def test_01_database_exists():
    assert os.path.exists(DB_PATH)


def test_02_database_connection(db):
    assert db is not None


def test_03_companies_table_exists(db):
    result = db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='companies'
    """).fetchone()

    assert result is not None


def test_04_financial_ratios_table_exists(db):
    result = db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='financial_ratios'
    """).fetchone()

    assert result is not None


def test_05_sectors_table_exists(db):
    result = db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='sectors'
    """).fetchone()

    assert result is not None


def test_06_peer_groups_table_exists(db):
    result = db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='peer_groups'
    """).fetchone()

    assert result is not None


def test_07_companies_have_records(db):
    count = db.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    assert count > 0


def test_08_company_count_is_92(db):
    count = db.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    assert count == 92


def test_09_company_ids_not_null(db):
    count = db.execute("""
        SELECT COUNT(*)
        FROM companies
        WHERE id IS NULL
    """).fetchone()[0]

    assert count == 0


def test_10_company_names_not_null(db):
    count = db.execute("""
        SELECT COUNT(*)
        FROM companies
        WHERE company_name IS NULL
    """).fetchone()[0]

    assert count == 0


def test_11_financial_ratios_have_records(db):
    count = db.execute(
        "SELECT COUNT(*) FROM financial_ratios"
    ).fetchone()[0]

    assert count > 0


def test_12_sector_records_exist(db):
    count = db.execute(
        "SELECT COUNT(*) FROM sectors"
    ).fetchone()[0]

    assert count > 0


def test_13_peer_group_records_exist(db):
    count = db.execute(
        "SELECT COUNT(*) FROM peer_groups"
    ).fetchone()[0]

    assert count > 0


def test_14_company_ids_are_unique(db):
    total = db.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    unique = db.execute(
        "SELECT COUNT(DISTINCT id) FROM companies"
    ).fetchone()[0]

    assert total == unique


# ============================================================
# CATEGORY 2 — DATA QUALITY TESTS
# ============================================================

def test_15_financial_company_ids_valid(db):
    result = pd.read_sql_query("""
        SELECT DISTINCT fr.company_id
        FROM financial_ratios fr
        LEFT JOIN companies c
        ON fr.company_id = c.id
        WHERE c.id IS NULL
    """, db)

    assert result.empty


def test_16_sector_company_ids_valid(db):
    result = pd.read_sql_query("""
        SELECT DISTINCT s.company_id
        FROM sectors s
        LEFT JOIN companies c
        ON s.company_id = c.id
        WHERE c.id IS NULL
    """, db)

    assert result.empty


def test_17_peer_company_ids_valid(db):
    result = pd.read_sql_query("""
        SELECT DISTINCT pg.company_id
        FROM peer_groups pg
        LEFT JOIN companies c
        ON pg.company_id = c.id
        WHERE c.id IS NULL
    """, db)

    assert result.empty


def test_18_company_names_not_empty(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM companies
        WHERE company_name IS NULL
        OR TRIM(company_name) = ''
    """, db)

    assert result.empty


def test_19_company_ids_not_empty(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM companies
        WHERE id IS NULL
        OR TRIM(id) = ''
    """, db)

    assert result.empty


def test_20_roe_reasonable(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM financial_ratios
        WHERE return_on_equity_pct IS NOT NULL
        AND (
            return_on_equity_pct < -50000
            OR return_on_equity_pct > 50000
        )
    """, db)

    assert result.empty


def test_21_debt_equity_non_negative(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM financial_ratios
        WHERE debt_to_equity IS NOT NULL
        AND debt_to_equity < 0
    """, db)

    assert result.empty


def test_22_net_margin_reasonable(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM financial_ratios
        WHERE net_profit_margin_pct IS NOT NULL
        AND (
            net_profit_margin_pct < -1000
            OR net_profit_margin_pct > 1000
        )
    """, db)

    assert result.empty


def test_23_financial_year_not_null(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM financial_ratios
        WHERE year IS NULL
    """, db)

    assert result.empty


def test_24_sector_names_not_empty(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM sectors
        WHERE broad_sector IS NULL
        OR TRIM(broad_sector) = ''
    """, db)

    assert result.empty


def test_25_peer_group_names_not_empty(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM peer_groups
        WHERE peer_group_name IS NULL
        OR TRIM(peer_group_name) = ''
    """, db)

    assert result.empty


def test_26_benchmark_flag_valid(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM peer_groups
        WHERE is_benchmark IS NOT NULL
        AND is_benchmark NOT IN (0, 1)
    """, db)

    assert result.empty


def test_27_sector_weights_non_negative(db):
    result = pd.read_sql_query("""
        SELECT *
        FROM sectors
        WHERE index_weight_pct < 0
    """, db)

    assert result.empty


def test_28_financial_company_count(db):
    result = pd.read_sql_query("""
        SELECT COUNT(DISTINCT company_id) AS count
        FROM financial_ratios
    """, db)

    assert result.iloc[0]["count"] > 0


def test_29_peer_company_count(db):
    result = pd.read_sql_query("""
        SELECT COUNT(DISTINCT company_id) AS count
        FROM peer_groups
    """, db)

    assert result.iloc[0]["count"] > 0


# ============================================================
# CATEGORY 3 — ANALYTICS TESTS
# ============================================================

def test_30_ratios_not_empty(ratios):
    assert not ratios.empty


def test_31_required_ratio_columns(ratios):

    required = [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow",
        "cfo_quality_score",
        "capex_intensity",
        "fcf_conversion",
        "capital_allocation_pattern"
    ]

    for column in required:
        assert column in ratios.columns


def test_32_company_id_present(ratios):
    assert ratios["company_id"].notna().any()


def test_33_year_present(ratios):
    assert ratios["year"].notna().any()


def test_34_roe_numeric(ratios):
    values = pd.to_numeric(
        ratios["return_on_equity_pct"],
        errors="coerce"
    )

    assert values.notna().any()


def test_35_net_margin_numeric(ratios):
    values = pd.to_numeric(
        ratios["net_profit_margin_pct"],
        errors="coerce"
    )

    assert values.notna().any()


def test_36_debt_equity_numeric(ratios):
    values = pd.to_numeric(
        ratios["debt_to_equity"],
        errors="coerce"
    )

    assert values.notna().any()


def test_37_interest_coverage_numeric(ratios):
    values = pd.to_numeric(
        ratios["interest_coverage"],
        errors="coerce"
    )

    assert values.notna().any()


def test_38_asset_turnover_numeric(ratios):
    values = pd.to_numeric(
        ratios["asset_turnover"],
        errors="coerce"
    )

    assert values.notna().any()


def test_39_free_cash_flow_numeric(ratios):
    values = pd.to_numeric(
        ratios["free_cash_flow"],
        errors="coerce"
    )

    assert values.notna().any()


def test_40_cfo_quality_numeric(ratios):
    values = pd.to_numeric(
        ratios["cfo_quality_score"],
        errors="coerce"
    )

    assert values.notna().any()


def test_41_capex_intensity_numeric(ratios):
    values = pd.to_numeric(
        ratios["capex_intensity"],
        errors="coerce"
    )

    assert values.notna().any()


def test_42_fcf_conversion_numeric(ratios):
    values = pd.to_numeric(
        ratios["fcf_conversion"],
        errors="coerce"
    )

    assert values.notna().any()


def test_43_roe_no_infinity(ratios):
    values = pd.to_numeric(
        ratios["return_on_equity_pct"],
        errors="coerce"
    ).dropna()

    assert not np.isinf(values).any()


def test_44_debt_equity_no_infinity(ratios):
    values = pd.to_numeric(
        ratios["debt_to_equity"],
        errors="coerce"
    ).dropna()

    assert not np.isinf(values).any()


def test_45_multiple_companies(ratios):
    assert ratios["company_id"].nunique() > 1


def test_46_multiple_years(ratios):
    assert ratios["year"].nunique() > 1


def test_47_latest_year_valid(ratios):
    assert ratios["year"].max() >= ratios["year"].min()


# ============================================================
# CATEGORY 4 — API TESTS
# ============================================================

def test_48_root():
    response = client.get("/")

    assert response.status_code == 200


def test_49_health():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_50_companies():
    response = client.get("/api/companies")

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert data["count"] > 0


def test_51_companies_count():
    response = client.get("/api/companies")

    data = response.json()

    assert data["count"] == 92


def test_52_company_abb():
    response = client.get("/api/companies/ABB")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == "ABB"


def test_53_invalid_company():
    response = client.get(
        "/api/companies/DOESNOTEXIST"
    )

    assert response.status_code == 404


def test_54_company_ratios():
    response = client.get(
        "/api/companies/ABB/ratios"
    )

    assert response.status_code == 200


def test_55_company_trend():
    response = client.get(
        "/api/companies/ABB/trend"
    )

    assert response.status_code == 200


def test_56_company_cashflow():
    response = client.get(
        "/api/companies/ABB/cashflow"
    )

    assert response.status_code == 200


def test_57_screener():
    response = client.get(
        "/api/screener"
    )

    assert response.status_code == 200


def test_58_screener_filters():
    response = client.get(
        "/api/screener"
        "?min_roe=10"
        "&max_debt_equity=2"
        "&min_margin=5"
    )

    assert response.status_code == 200


def test_59_peer_groups():
    response = client.get(
        "/api/peer-groups"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data


def test_60_sectors():
    response = client.get(
        "/api/sectors"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data


def test_61_capital_allocation():
    response = client.get(
        "/api/capital-allocation"
    )

    assert response.status_code == 200


def test_62_valuation():
    response = client.get(
        "/api/valuation"
    )

    assert response.status_code in [200, 404]


def test_63_annual_reports():
    response = client.get(
        "/api/annual-reports"
    )

    assert response.status_code == 200


def test_64_portfolio_summary():
    response = client.get(
        "/api/portfolio-summary"
    )

    assert response.status_code == 200