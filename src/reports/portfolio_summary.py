# src/reports/portfolio_summary.py

import os
import pandas as pd

from reportlab.platypus import Spacer

from src.reports.report_utils import (
    REPORTS_DIR,
    ensure_report_directories,
    get_report_styles,
    title_block,
    section_header,
    kpi_row,
    make_table,
    methodology_note,
    report_date,
    build_report,
    format_number,
    format_percent,
    clean_filename,
    safe_text,
)


# ============================================================
# FILE PATHS
# ============================================================

FINANCIAL_FILE = "output/financial_ratios.csv"

PEER_GROUP_FILE = "data/raw/peer_groups.xlsx"

COMPANIES_FILE = "data/raw/companies.xlsx"

OUTPUT_FILE = os.path.join(
    REPORTS_DIR,
    "portfolio_summary.pdf"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    financial = pd.read_csv(
        FINANCIAL_FILE
    )

    peer_groups = pd.read_excel(
        PEER_GROUP_FILE
    )

    companies = pd.read_excel(
        COMPANIES_FILE,
        header=1
    )

    # --------------------------------------------------------
    # Normalise company ID
    # --------------------------------------------------------

    if "id" in companies.columns:

        companies = companies.rename(
            columns={
                "id": "company_id"
            }
        )

    # --------------------------------------------------------
    # Latest financial record
    # --------------------------------------------------------

    financial["year"] = pd.to_numeric(
        financial["year"],
        errors="coerce"
    )

    latest = (
        financial
        .sort_values("year")
        .drop_duplicates(
            "company_id",
            keep="last"
        )
    )

    # --------------------------------------------------------
    # Peer groups
    # --------------------------------------------------------

    if "peer_group_name" in peer_groups.columns:

        latest = latest.merge(
            peer_groups[
                [
                    "company_id",
                    "peer_group_name"
                ]
            ],
            on="company_id",
            how="left"
        )

    # --------------------------------------------------------
    # Company names
    # --------------------------------------------------------

    if (
        "company_id" in companies.columns
        and
        "company_name" in companies.columns
    ):

        latest = latest.merge(
            companies[
                [
                    "company_id",
                    "company_name"
                ]
            ],
            on="company_id",
            how="left"
        )

    return latest


# ============================================================
# HELPERS
# ============================================================

def numeric_series(
    df,
    column
):

    if column not in df.columns:

        return pd.Series(
            dtype=float
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


def average(
    df,
    column
):

    values = numeric_series(
        df,
        column
    )

    if values.dropna().empty:

        return None

    return values.mean()


def avg_percent(
    df,
    column
):

    value = average(
        df,
        column
    )

    if value is None:

        return "N/A"

    return format_percent(
        value
    )


def avg_number(
    df,
    column
):

    value = average(
        df,
        column
    )

    if value is None:

        return "N/A"

    return format_number(
        value
    )


# ============================================================
# TOP COMPANIES
# ============================================================

def top_companies(
    df,
    metric,
    ascending=False,
    count=10
):

    if (
        metric not in df.columns
        or
        "company_name" not in df.columns
    ):

        return pd.DataFrame()

    result = df[
        [
            "company_name",
            metric
        ]
    ].copy()

    result[metric] = pd.to_numeric(
        result[metric],
        errors="coerce"
    )

    result = (
        result
        .dropna(subset=[metric])
        .sort_values(
            metric,
            ascending=ascending
        )
        .head(count)
    )

    return result


# ============================================================
# BUILD PORTFOLIO REPORT
# ============================================================

def build_portfolio_report(
    data
):

    styles = get_report_styles()

    story = []

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.extend(
        title_block(
            "Bluestock N100 Portfolio Summary",
            f"Portfolio-level financial analysis | "
            f"Generated {report_date()}"
        )
    )

    # --------------------------------------------------------
    # PORTFOLIO KPIs
    # --------------------------------------------------------

    story.append(
        section_header(
            "Portfolio Overview",
            styles
        )
    )

    kpis = [

        (
            "Companies",
            str(
                data["company_id"]
                .nunique()
            )
            if "company_id" in data.columns
            else str(len(data))
        ),

        (
            "Avg ROE",
            avg_percent(
                data,
                "return_on_equity_pct"
            )
        ),

        (
            "Avg ROCE",
            avg_percent(
                data,
                "roce_calculated"
            )
        ),

        (
            "Avg Net Margin",
            avg_percent(
                data,
                "net_profit_margin_pct"
            )
        ),

    ]

    story.append(
        kpi_row(
            kpis,
            styles
        )
    )

    story.append(
        Spacer(
            1,
            7
        )
    )

    # --------------------------------------------------------
    # FINANCIAL HEALTH
    # --------------------------------------------------------

    story.append(
        section_header(
            "Portfolio Financial Health",
            styles
        )
    )

    financial_rows = [

        [
            "Average ROE",
            avg_percent(
                data,
                "return_on_equity_pct"
            )
        ],

        [
            "Average ROCE",
            avg_percent(
                data,
                "roce_calculated"
            )
        ],

        [
            "Average Net Profit Margin",
            avg_percent(
                data,
                "net_profit_margin_pct"
            )
        ],

        [
            "Average Operating Margin",
            avg_percent(
                data,
                "operating_profit_margin_pct"
            )
        ],

        [
            "Average Debt / Equity",
            avg_number(
                data,
                "debt_to_equity"
            )
        ],

        [
            "Average Interest Coverage",
            avg_number(
                data,
                "interest_coverage"
            )
        ],

        [
            "Average Asset Turnover",
            avg_number(
                data,
                "asset_turnover"
            )
        ],

    ]

    story.append(
        make_table(
            [
                "Metric",
                "Portfolio Average"
            ],
            financial_rows,
            col_widths=[
                100,
                75
            ],
            styles=styles
        )
    )

    story.append(
        Spacer(
            1,
            7
        )
    )

    # --------------------------------------------------------
    # CASH FLOW
    # --------------------------------------------------------

    story.append(
        section_header(
            "Cash Flow Intelligence",
            styles
        )
    )

    fcf = numeric_series(
        data,
        "free_cash_flow"
    )

    positive_fcf = int(
        (fcf > 0).sum()
    )

    negative_fcf = int(
        (fcf < 0).sum()
    )

    cashflow_rows = [

        [
            "Average Free Cash Flow",
            avg_number(
                data,
                "free_cash_flow"
            )
        ],

        [
            "Average CFO Quality Score",
            avg_number(
                data,
                "cfo_quality_score"
            )
        ],

        [
            "Average CapEx Intensity",
            avg_percent(
                data,
                "capex_intensity"
            )
        ],

        [
            "Average FCF Conversion",
            avg_percent(
                data,
                "fcf_conversion"
            )
        ],

        [
            "Companies with Positive FCF",
            positive_fcf
        ],

        [
            "Companies with Negative FCF",
            negative_fcf
        ],

    ]

    story.append(
        make_table(
            [
                "Indicator",
                "Value"
            ],
            cashflow_rows,
            col_widths=[
                100,
                75
            ],
            styles=styles
        )
    )

    story.append(
        Spacer(
            1,
            7
        )
    )

    # --------------------------------------------------------
    # TOP ROE COMPANIES
    # --------------------------------------------------------

    story.append(
        section_header(
            "Top Companies by ROE",
            styles
        )
    )

    top_roe = top_companies(
        data,
        "return_on_equity_pct",
        ascending=False
    )

    rows = []

    for _, row in top_roe.iterrows():

        rows.append(
            [
                safe_text(
                    row["company_name"]
                ),
                format_percent(
                    row[
                        "return_on_equity_pct"
                    ]
                )
            ]
        )

    if rows:

        story.append(
            make_table(
                [
                    "Company",
                    "ROE"
                ],
                rows,
                col_widths=[
                    120,
                    55
                ],
                styles=styles
            )
        )

    story.append(
        Spacer(
            1,
            7
        )
    )

    # --------------------------------------------------------
    # TOP FCF COMPANIES
    # --------------------------------------------------------

    story.append(
        section_header(
            "Top Companies by Free Cash Flow",
            styles
        )
    )

    top_fcf = top_companies(
        data,
        "free_cash_flow",
        ascending=False
    )

    rows = []

    for _, row in top_fcf.iterrows():

        rows.append(
            [
                safe_text(
                    row["company_name"]
                ),
                format_number(
                    row["free_cash_flow"]
                )
            ]
        )

    if rows:

        story.append(
            make_table(
                [
                    "Company",
                    "Free Cash Flow"
                ],
                rows,
                col_widths=[
                    120,
                    55
                ],
                styles=styles
            )
        )

    story.append(
        Spacer(
            1,
            7
        )
    )

    # --------------------------------------------------------
    # SECTOR DISTRIBUTION
    # --------------------------------------------------------

    if "peer_group_name" in data.columns:

        story.append(
            section_header(
                "Sector / Peer Group Distribution",
                styles
            )
        )

        sector_counts = (
            data[
                "peer_group_name"
            ]
            .fillna("Unknown")
            .value_counts()
        )

        sector_rows = []

        for sector, count in sector_counts.items():

            sector_rows.append(
                [
                    safe_text(
                        sector
                    ),
                    int(count)
                ]
            )

        story.append(
            make_table(
                [
                    "Sector / Peer Group",
                    "Companies"
                ],
                sector_rows,
                col_widths=[
                    120,
                    55
                ],
                styles=styles
            )
        )

        story.append(
            Spacer(
                1,
                7
            )
        )

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    story.append(
        methodology_note(
            "Portfolio metrics are calculated using the latest "
            "available financial record for each company. "
            "Sector distribution is based on the project's "
            "peer-group classification. Missing values are "
            "excluded from metric averages.",
            styles
        )
    )

    return story


# ============================================================
# GENERATE PDF
# ============================================================

def generate_portfolio_summary():

    print("=" * 70)
    print("Bluestock N100 Portfolio Summary Generator")
    print("=" * 70)

    ensure_report_directories()

    data = load_data()

    if data.empty:

        print(
            "ERROR: No financial data available."
        )

        return

    print(
        "Companies:",
        data["company_id"].nunique()
        if "company_id" in data.columns
        else len(data)
    )

    story = build_portfolio_report(
        data
    )

    build_report(
        OUTPUT_FILE,
        story,
        title="Bluestock N100 | Portfolio Summary"
    )

    print()
    print("=" * 70)
    print("Portfolio summary generated successfully")
    print("=" * 70)
    print(
        "Saved:",
        OUTPUT_FILE
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_portfolio_summary()