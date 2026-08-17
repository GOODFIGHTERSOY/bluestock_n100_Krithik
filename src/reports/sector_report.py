# src/reports/sector_report.py

import os
import pandas as pd

from reportlab.platypus import Spacer

from src.reports.report_utils import (
    SECTORS_DIR,
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

OUTPUT_DIR = SECTORS_DIR


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
    # Latest financial year
    # --------------------------------------------------------

    financial["year"] = pd.to_numeric(
        financial["year"],
        errors="coerce"
    )

    financial = (
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

    peer_columns = [
        "company_id",
        "peer_group_name"
    ]

    peer_columns = [
        c
        for c in peer_columns
        if c in peer_groups.columns
    ]

    data = financial.merge(
        peer_groups[peer_columns],
        on="company_id",
        how="left"
    )

    # --------------------------------------------------------
    # Company names
    # --------------------------------------------------------

    company_columns = [
        "company_id",
        "company_name"
    ]

    company_columns = [
        c
        for c in company_columns
        if c in companies.columns
    ]

    if len(company_columns) > 1:

        data = data.merge(
            companies[company_columns],
            on="company_id",
            how="left"
        )

    return data


# ============================================================
# HELPERS
# ============================================================

def value(row, column, default="N/A"):

    if column not in row.index:
        return default

    result = row[column]

    if pd.isna(result):
        return default

    return result


def mean_metric(df, column):

    if column not in df.columns:
        return "N/A"

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    if values.dropna().empty:
        return "N/A"

    return values.mean()


def percentage_metric(df, column):

    result = mean_metric(
        df,
        column
    )

    if result == "N/A":
        return "N/A"

    return format_percent(result)


def number_metric(df, column):

    result = mean_metric(
        df,
        column
    )

    if result == "N/A":
        return "N/A"

    return format_number(result)


# ============================================================
# SECTOR SUMMARY
# ============================================================

def sector_summary(df):

    summary = {

        "Companies":
            len(df),

        "Average ROE":
            percentage_metric(
                df,
                "return_on_equity_pct"
            ),

        "Average ROCE":
            percentage_metric(
                df,
                "roce_calculated"
            ),

        "Average Net Margin":
            percentage_metric(
                df,
                "net_profit_margin_pct"
            ),

        "Average Operating Margin":
            percentage_metric(
                df,
                "operating_profit_margin_pct"
            ),

        "Average Debt / Equity":
            number_metric(
                df,
                "debt_to_equity"
            ),

        "Average Interest Coverage":
            number_metric(
                df,
                "interest_coverage"
            ),

        "Average Asset Turnover":
            number_metric(
                df,
                "asset_turnover"
            ),

        "Average FCF":
            number_metric(
                df,
                "free_cash_flow"
            ),
    }

    return summary


# ============================================================
# COMPANY RANKING
# ============================================================

def company_ranking(df):

    ranking_columns = [
        "company_name",
        "return_on_equity_pct",
        "roce_calculated",
        "net_profit_margin_pct",
        "free_cash_flow"
    ]

    available = [
        c
        for c in ranking_columns
        if c in df.columns
    ]

    ranked = df[available].copy()

    if "return_on_equity_pct" in ranked.columns:

        ranked[
            "return_on_equity_pct"
        ] = pd.to_numeric(
            ranked["return_on_equity_pct"],
            errors="coerce"
        )

        ranked = ranked.sort_values(
            "return_on_equity_pct",
            ascending=False
        )

    return ranked


# ============================================================
# BUILD SECTOR REPORT
# ============================================================

def build_sector_report(
    sector_name,
    sector_df
):

    styles = get_report_styles()

    story = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.extend(
        title_block(
            f"{sector_name} Sector Report",
            f"Bluestock N100 | Generated {report_date()}"
        )
    )

    # --------------------------------------------------------
    # KPI section
    # --------------------------------------------------------

    story.append(
        section_header(
            "Sector Overview",
            styles
        )
    )

    kpis = [

        (
            "Companies",
            str(len(sector_df))
        ),

        (
            "Avg ROE",
            percentage_metric(
                sector_df,
                "return_on_equity_pct"
            )
        ),

        (
            "Avg ROCE",
            percentage_metric(
                sector_df,
                "roce_calculated"
            )
        ),

        (
            "Avg Net Margin",
            percentage_metric(
                sector_df,
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
    # Sector metrics
    # --------------------------------------------------------

    story.append(
        section_header(
            "Sector Financial Metrics",
            styles
        )
    )

    summary = sector_summary(
        sector_df
    )

    summary_rows = [
        [key, val]
        for key, val in summary.items()
    ]

    story.append(
        make_table(
            [
                "Metric",
                "Sector Value"
            ],
            summary_rows,
            col_widths=[
                95,
                80
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
    # Company ranking
    # --------------------------------------------------------

    story.append(
        section_header(
            "Company Performance Ranking",
            styles
        )
    )

    ranked = company_ranking(
        sector_df
    )

    ranking_rows = []

    for _, row in ranked.iterrows():

        ranking_rows.append(
            [
                safe_text(
                    value(
                        row,
                        "company_name"
                    )
                ),

                (
                    format_percent(
                        value(
                            row,
                            "return_on_equity_pct"
                        )
                    )
                    if value(
                        row,
                        "return_on_equity_pct",
                        None
                    ) is not None
                    else "N/A"
                ),

                (
                    format_percent(
                        value(
                            row,
                            "roce_calculated"
                        )
                    )
                    if value(
                        row,
                        "roce_calculated",
                        None
                    ) is not None
                    else "N/A"
                ),

                (
                    format_percent(
                        value(
                            row,
                            "net_profit_margin_pct"
                        )
                    )
                    if value(
                        row,
                        "net_profit_margin_pct",
                        None
                    ) is not None
                    else "N/A"
                ),

                (
                    format_number(
                        value(
                            row,
                            "free_cash_flow"
                        )
                    )
                    if value(
                        row,
                        "free_cash_flow",
                        None
                    ) is not None
                    else "N/A"
                ),
            ]
        )

    if ranking_rows:

        story.append(
            make_table(
                [
                    "Company",
                    "ROE",
                    "ROCE",
                    "Net Margin",
                    "FCF"
                ],
                ranking_rows,
                col_widths=[
                    65,
                    25,
                    25,
                    30,
                    30
                ],
                styles=styles
            )
        )

    else:

        story.append(
            methodology_note(
                "No company-level financial records were "
                "available for this sector.",
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
    # Cash flow analysis
    # --------------------------------------------------------

    story.append(
        section_header(
            "Cash Flow Analysis",
            styles
        )
    )

    cashflow_rows = [

        [
            "Positive FCF Companies",
            int(
                (
                    pd.to_numeric(
                        sector_df.get(
                            "free_cash_flow",
                            pd.Series(dtype=float)
                        ),
                        errors="coerce"
                    ) > 0
                ).sum()
            )
        ],

        [
            "Negative FCF Companies",
            int(
                (
                    pd.to_numeric(
                        sector_df.get(
                            "free_cash_flow",
                            pd.Series(dtype=float)
                        ),
                        errors="coerce"
                    ) < 0
                ).sum()
            )
        ],

        [
            "Average CFO Quality",
            number_metric(
                sector_df,
                "cfo_quality_score"
            )
        ],

        [
            "Average CapEx Intensity",
            percentage_metric(
                sector_df,
                "capex_intensity"
            )
        ],

        [
            "Average FCF Conversion",
            percentage_metric(
                sector_df,
                "fcf_conversion"
            )
        ],
    ]

    story.append(
        make_table(
            [
                "Cash Flow Indicator",
                "Value"
            ],
            cashflow_rows,
            col_widths=[
                95,
                80
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
    # Methodology
    # --------------------------------------------------------

    story.append(
        methodology_note(
            "Sector values represent averages across the latest "
            "available financial year for each company. Missing "
            "values are excluded from individual metric averages.",
            styles
        )
    )

    return story


# ============================================================
# GENERATE ONE SECTOR PDF
# ============================================================

def generate_sector_pdf(
    sector_name,
    sector_df
):

    filename = (
        clean_filename(
            sector_name
        )
        + ".pdf"
    )

    filepath = os.path.join(
        OUTPUT_DIR,
        filename
    )

    story = build_sector_report(
        sector_name,
        sector_df
    )

    build_report(
        filepath,
        story,
        title="Bluestock N100 | Sector Report"
    )

    return filepath


# ============================================================
# GENERATE ALL SECTOR REPORTS
# ============================================================

def generate_all_sector_reports():

    print("=" * 70)
    print("Bluestock N100 Sector Report Generator")
    print("=" * 70)

    ensure_report_directories()

    data = load_data()

    if data.empty:

        print(
            "ERROR: No financial data found."
        )

        return

    if "peer_group_name" not in data.columns:

        print(
            "ERROR: peer_group_name column "
            "is missing."
        )

        return

    sectors = sorted(
        data[
            "peer_group_name"
        ]
        .dropna()
        .astype(str)
        .unique()
    )

    print(
        "Sector groups found:",
        len(sectors)
    )

    generated = 0

    for sector in sectors:

        sector_df = data[
            data["peer_group_name"].astype(str)
            == sector
        ].copy()

        try:

            filepath = generate_sector_pdf(
                sector,
                sector_df
            )

            generated += 1

            print(
                f"[{generated}/{len(sectors)}] "
                f"{sector} -> {filepath}"
            )

        except Exception as exc:

            print(
                f"ERROR generating "
                f"{sector}: {exc}"
            )

    print()
    print("=" * 70)
    print("Sector report generation completed")
    print("=" * 70)
    print(
        "Generated:",
        generated
    )
    print(
        "Output:",
        OUTPUT_DIR
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_all_sector_reports()