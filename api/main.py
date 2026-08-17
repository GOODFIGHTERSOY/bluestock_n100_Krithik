from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import sqlite3
import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = "data\\nifty100.db"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Bluestock N100 Analytics API",
    description=(
        "REST API for Bluestock N100 financial analytics, "
        "company profiles, screening, peer analysis, "
        "trends, clustering and valuation."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_connection():

    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Database not found: {DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)


def read_query(
    query,
    params=()
):

    try:

        conn = get_connection()

        df = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        conn.close()

        return df

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


def dataframe_to_records(df):

    if df.empty:
        return []

    # Convert pandas NaN / infinity values
    # into JSON-compatible None values.

    df = df.replace(
        [float("inf"), float("-inf")],
        None
    )

    df = df.astype(
        object
    ).where(
        pd.notnull(df),
        None
    )

    return df.to_dict(
        orient="records"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Bluestock N100 Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": 16,
    }


# ============================================================
# 1. HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "database": os.path.exists(DB_PATH),
    }


# ============================================================
# 2. LIST COMPANIES
# ============================================================

@app.get("/api/companies")
def companies():

    query = """
        SELECT *
        FROM companies
        ORDER BY company_name
    """

    df = read_query(query)

    return {
        "count": len(df),
        "data": dataframe_to_records(df),
    }


# ============================================================
# 3. COMPANY PROFILE
# ============================================================

@app.get("/api/companies/{company_id}")
def company_profile(company_id: str):

    query = """
        SELECT *
        FROM companies
        WHERE id = ?
    """

    df = read_query(
        query,
        (company_id.upper(),)
    )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_id}' not found"
        )

    return dataframe_to_records(df)[0]

    query = """
        SELECT *
        FROM companies
        WHERE id = ?
    """

    df = read_query(
        query,
        (company_id,)
    )

    if df.empty:

        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return dataframe_to_records(df)[0]


# ============================================================
# 4. FINANCIAL RATIOS
# ============================================================

@app.get("/api/companies/{company_id}/ratios")
def company_ratios(
    company_id: str
):

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
    """

    df = read_query(
        query,
        (company_id,)
    )

    return {
        "company_id": company_id,
        "count": len(df),
        "data": dataframe_to_records(df),
    }


# ============================================================
# 5. TREND
# ============================================================

@app.get("/api/companies/{company_id}/trend")
def company_trend(
    company_id: str
):

    query = """
        SELECT
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            roce_calculated,
            debt_to_equity,
            interest_coverage,
            asset_turnover
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
    """

    df = read_query(
        query,
        (company_id,)
    )

    return {
        "company_id": company_id,
        "data": dataframe_to_records(df),
    }


# ============================================================
# 6. CASH FLOW
# ============================================================

@app.get("/api/companies/{company_id}/cashflow")
def company_cashflow(
    company_id: str
):

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
    """

    df = read_query(
        query,
        (company_id,)
    )

    available = [
        column
        for column in [
            "company_id",
            "year",
            "free_cash_flow",
            "cfo_quality_score",
            "capex_intensity",
            "fcf_conversion",
            "capital_allocation_pattern",
        ]
        if column in df.columns
    ]

    return {
        "company_id": company_id,
        "data": dataframe_to_records(
            df[available]
        ),
    }


# ============================================================
# 7. SCREENING
# ============================================================

@app.get("/api/screener")
def screener(

    min_roe: float = Query(
        0,
        description="Minimum ROE percentage"
    ),

    max_debt_equity: float = Query(
        100,
        description="Maximum debt/equity"
    ),

    min_margin: float = Query(
        0,
        description="Minimum net profit margin"
    ),

):

    query = """
        SELECT *
        FROM financial_ratios
        WHERE return_on_equity_pct >= ?
        AND debt_to_equity <= ?
        AND net_profit_margin_pct >= ?
    """

    df = read_query(
        query,
        (
            min_roe,
            max_debt_equity,
            min_margin,
        )
    )

    return {
        "count": len(df),
        "filters": {
            "min_roe": min_roe,
            "max_debt_equity": max_debt_equity,
            "min_margin": min_margin,
        },
        "data": dataframe_to_records(df),
    }


# ============================================================
# 8. PEER GROUPS
# ============================================================

@app.get("/api/peer-groups")
def peer_groups():

    query = """
        SELECT
            peer_group_name,
            COUNT(DISTINCT company_id) AS company_count
        FROM peer_groups
        GROUP BY peer_group_name
        ORDER BY peer_group_name
    """

    df = read_query(query)

    return {
        "count": len(df),
        "data": dataframe_to_records(df)
    }


# ============================================================
# 9. PEER COMPARISON
# ============================================================

@app.get("/api/peer-groups/{group_name}")
def peer_comparison(group_name: str):

    query = """
        SELECT
            pg.peer_group_name,
            pg.company_id,
            c.company_name,
            fr.year,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow,
            fr.cfo_quality_score,
            fr.capex_intensity,
            fr.fcf_conversion

        FROM peer_groups pg

        LEFT JOIN companies c
            ON pg.company_id = c.id

        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id

        WHERE pg.peer_group_name = ?

        ORDER BY
            pg.company_id,
            fr.year
    """

    df = read_query(
        query,
        (group_name,)
    )

    return {
        "peer_group": group_name,
        "count": len(df),
        "data": dataframe_to_records(df)
    }

# ============================================================
# 10. SECTOR ANALYSIS
# ============================================================

@app.get("/api/sectors")
def sectors():

    query = """
        SELECT
            s.broad_sector,
            s.sub_sector,
            COUNT(DISTINCT s.company_id) AS company_count,

            AVG(fr.net_profit_margin_pct)
                AS avg_net_profit_margin,

            AVG(fr.operating_profit_margin_pct)
                AS avg_operating_profit_margin,

            AVG(fr.return_on_equity_pct)
                AS avg_roe,

            AVG(fr.debt_to_equity)
                AS avg_debt_to_equity,

            AVG(fr.interest_coverage)
                AS avg_interest_coverage,

            AVG(fr.asset_turnover)
                AS avg_asset_turnover,

            AVG(fr.free_cash_flow)
                AS avg_free_cash_flow

        FROM sectors s

        LEFT JOIN financial_ratios fr
            ON s.company_id = fr.company_id

        GROUP BY
            s.broad_sector,
            s.sub_sector

        ORDER BY
            s.broad_sector,
            s.sub_sector
    """

    df = read_query(query)

    return {
        "count": len(df),
        "data": dataframe_to_records(df)
    }

# ============================================================
# 11. CAPITAL ALLOCATION
# ============================================================

@app.get("/api/capital-allocation")
def capital_allocation():

    query = """
        SELECT
            company_id,
            year,
            free_cash_flow,
            cfo_quality_score,
            capex_intensity,
            fcf_conversion,
            capital_allocation_pattern
        FROM financial_ratios
        ORDER BY company_id, year
    """

    df = read_query(query)

    return {
        "count": len(df),
        "data": dataframe_to_records(df),
    }


# ============================================================
# 12. CLUSTERS
# ============================================================

@app.get("/api/clusters")
def clusters():

    cluster_file = (
        "output/clustered_companies.csv"
    )

    if not os.path.exists(
        cluster_file
    ):

        raise HTTPException(
            status_code=404,
            detail="Clustered data not generated yet"
        )

    df = pd.read_csv(
        cluster_file
    )

    return {
        "count": len(df),
        "data": dataframe_to_records(df),
    }


# ============================================================
# 13. CLUSTER SUMMARY
# ============================================================

@app.get("/api/clusters/summary")
def cluster_summary():

    summary_file = (
        "output/cluster_summary.csv"
    )

    if not os.path.exists(
        summary_file
    ):

        raise HTTPException(
            status_code=404,
            detail="Cluster summary not generated yet"
        )

    df = pd.read_csv(
        summary_file
    )

    return {
        "count": len(df),
        "data": dataframe_to_records(df),
    }


# ============================================================
# 14. VALUATION
# ============================================================

@app.get("/api/valuation")
def valuation():

    valuation_file = (
        "output/valuation_summary.xlsx"
    )

    if not os.path.exists(
        valuation_file
    ):

        raise HTTPException(
            status_code=404,
            detail="Valuation file not found"
        )

    df = pd.read_excel(
        valuation_file
    )

    return {
        "count": len(df),
        "data": dataframe_to_records(df),
    }


# ============================================================
# 15. ANNUAL REPORTS
# ============================================================

@app.get("/api/annual-reports")
def annual_reports():

    query = """
        SELECT *
        FROM companies
        ORDER BY company_name
    """

    df = read_query(query)

    results = []

    for _, row in df.iterrows():

        company_name = row.get(
            "company_name"
        )

        # NSE company page

        if company_name:

            search_name = str(
                company_name
            ).replace(
                " ",
                "+"
            )

            nse_url = (
                "https://www.nseindia.com/"
                "get-quotes/equity?"
                f"symbol={search_name}"
            )

        else:

            nse_url = None

        results.append(
            {
                "company_id": row.get(
                    "id"
                ),
                "company_name": company_name,
                "nse_profile": nse_url,
            }
        )

    return {
        "count": len(results),
        "data": results,
    }


# ============================================================
# 16. PORTFOLIO SUMMARY
# ============================================================

@app.get("/api/portfolio-summary")
def portfolio_summary():

    query = """
        SELECT
            COUNT(DISTINCT company_id)
                AS companies,

            AVG(return_on_equity_pct)
                AS avg_roe,

            AVG(roce_calculated)
                AS avg_roce,

            AVG(net_profit_margin_pct)
                AS avg_net_margin,

            AVG(
                operating_profit_margin_pct
            )
                AS avg_operating_margin,

            AVG(debt_to_equity)
                AS avg_debt_to_equity,

            AVG(interest_coverage)
                AS avg_interest_coverage,

            AVG(free_cash_flow)
                AS avg_free_cash_flow

        FROM financial_ratios
    """

    df = read_query(query)

    return dataframe_to_records(
        df
    )[0]