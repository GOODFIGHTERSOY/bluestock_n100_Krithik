# src/reports/company_tearsheet.py

import os
import re
import pandas as pd

from reportlab.platypus import (
    Spacer,
    PageBreak,
)

from src.reports.report_utils import (
    TEARSHEETS_DIR,
    ensure_report_directories,
    get_report_styles,
    title_block,
    section_header,
    kpi_row,
    make_table,
    key_value_table,
    pros_cons_table,
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

COMPANIES_FILE = "data/raw/companies.xlsx"

PROS_CONS_FILE = "output/pros_cons_generated.csv"

CASHFLOW_FILE = "output/cashflow_intelligence.xlsx"

OUTPUT_DIR = TEARSHEETS_DIR


# ============================================================
# LOAD DATA
# ============================================================

def load_companies():

    companies = pd.read_excel(
        COMPANIES_FILE,
        header=1
    )

    # Handle the company master file used in your project.
    # The actual ID column is normally "id".

    if "id" in companies.columns:
        companies = companies.rename(
            columns={"id": "company_id"}
        )

    # Sometimes company_id may already exist.
    if "company_id" not in companies.columns:

        possible_id_columns = [
            c for c in companies.columns
            if str(c).lower().strip() in [
                "id",
                "company id",
                "company_id"
            ]
        ]

        if possible_id_columns:
            companies = companies.rename(
                columns={
                    possible_id_columns[0]: "company_id"
                }
            )

    return companies


def load_financial():

    financial = pd.read_csv(
        FINANCIAL_FILE
    )

    financial["year"] = pd.to_numeric(
        financial["year"],
        errors="coerce"
    )

    return financial


def load_optional_file(path, reader):

    if not os.path.exists(path):
        print(f"Optional file not found: {path}")
        return pd.DataFrame()

    try:
        return reader(path)

    except Exception as exc:
        print(
            f"Could not load {path}: {exc}"
        )

        return pd.DataFrame()


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data():

    financial = load_financial()

    companies = load_companies()

    # --------------------------------------------------------
    # Latest financial record per company
    # --------------------------------------------------------

    latest = (
        financial
        .sort_values("year")
        .drop_duplicates(
            "company_id",
            keep="last"
        )
    )

    # --------------------------------------------------------
    # Company master
    # --------------------------------------------------------

    company_columns = [
        "company_id",
        "company_name",
        "website",
        "nse_profile",
        "bse_profile",
        "face_value",
        "book_value",
    ]

    company_columns = [
        c for c in company_columns
        if c in companies.columns
    ]

    if "company_id" in companies.columns:

        latest = latest.merge(
            companies[company_columns],
            on="company_id",
            how="left"
        )

    # --------------------------------------------------------
    # Pros / Cons
    # --------------------------------------------------------

    pros_cons = load_optional_file(
        PROS_CONS_FILE,
        pd.read_csv
    )

    if not pros_cons.empty:

        if "company_id" in pros_cons.columns:

            useful = [
                c
                for c in [
                    "company_id",
                    "pros",
                    "cons"
                ]
                if c in pros_cons.columns
            ]

            latest = latest.merge(
                pros_cons[useful],
                on="company_id",
                how="left"
            )

    # --------------------------------------------------------
    # Cash Flow Intelligence
    # --------------------------------------------------------

    cashflow = load_optional_file(
        CASHFLOW_FILE,
        pd.read_excel
    )

    if not cashflow.empty:

        if "company_id" in cashflow.columns:

            useful = [
                c
                for c in [
                    "company_id",
                    "cfo_quality",
                    "capex_level",
                    "distress_flag",
                    "capital_allocation_matrix"
                ]
                if c in cashflow.columns
            ]

            latest = latest.merge(
                cashflow[useful],
                on="company_id",
                how="left"
            )

    return latest


# ============================================================
# VALUE HELPERS
# ============================================================

def get_value(row, column, default="N/A"):

    if column not in row.index:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    return value


def percentage(row, column):

    value = get_value(row, column)

    if value == "N/A":
        return "N/A"

    return format_percent(value)


def number(row, column):

    value = get_value(row, column)

    if value == "N/A":
        return "N/A"

    return format_number(value)


# ============================================================
# COMPANY NAME
# ============================================================

def get_company_name(row):

    name = get_value(
        row,
        "company_name",
        None
    )

    if name is not None and name != "N/A":

        return str(name)

    return f"Company {get_value(row, 'company_id')}"


# ============================================================
# PROS / CONS
# ============================================================

def split_points(value):

    if value is None:
        return []

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    # Generated file uses semicolon-separated rules.
    parts = re.split(
        r";|\n",
        value
    )

    return [
        p.strip()
        for p in parts
        if p.strip()
    ]


# ============================================================
# PAGE 1
# ============================================================

def build_page_one(
    row,
    styles
):

    company_name = get_company_name(row)

    company_id = get_value(
        row,
        "company_id"
    )

    year = get_value(
        row,
        "year"
    )

    story = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.extend(
        title_block(
            company_name,
            f"Company Tearsheet | Company ID: {company_id} | "
            f"Latest financial year: {year}"
        )
    )

    # --------------------------------------------------------
    # KPI row
    # --------------------------------------------------------

    story.append(
        section_header(
            "Key Financial Indicators",
            styles
        )
    )

    kpis = [

        (
            "ROE",
            percentage(
                row,
                "return_on_equity_pct"
            )
        ),

        (
            "ROCE",
            percentage(
                row,
                "roce_calculated"
            )
        ),

        (
            "Net Margin",
            percentage(
                row,
                "net_profit_margin_pct"
            )
        ),

        (
            "Operating Margin",
            percentage(
                row,
                "operating_profit_margin_pct"
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
    # Financial metrics
    # --------------------------------------------------------

    story.append(
        section_header(
            "Financial Snapshot",
            styles
        )
    )

    financial_data = {

        "Debt to Equity":
            number(
                row,
                "debt_to_equity"
            ),

        "Interest Coverage":
            number(
                row,
                "interest_coverage"
            ),

        "Asset Turnover":
            number(
                row,
                "asset_turnover"
            ),

        "Free Cash Flow":
            number(
                row,
                "free_cash_flow"
            ),

        "CFO Quality Score":
            number(
                row,
                "cfo_quality_score"
            ),

        "FCF Conversion":
            percentage(
                row,
                "fcf_conversion"
            ),

        "CapEx Intensity":
            percentage(
                row,
                "capex_intensity"
            ),

        "EPS":
            number(
                row,
                "earnings_per_share"
            ),

        "Book Value / Share":
            number(
                row,
                "book_value_per_share"
            ),

        "Dividend Payout":
            percentage(
                row,
                "dividend_payout_ratio_pct"
            ),

    }

    story.append(
        key_value_table(
            financial_data,
            styles
        )
    )

    story.append(
        Spacer(
            1,
            6
        )
    )

    # --------------------------------------------------------
    # Cash flow intelligence
    # --------------------------------------------------------

    story.append(
        section_header(
            "Cash Flow Intelligence",
            styles
        )
    )

    cashflow_data = {

        "CFO Quality":
            safe_text(
                get_value(
                    row,
                    "cfo_quality"
                )
            ),

        "CapEx Level":
            safe_text(
                get_value(
                    row,
                    "capex_level"
                )
            ),

        "Distress Pattern":
            safe_text(
                get_value(
                    row,
                    "distress_flag"
                )
            ),

        "Capital Allocation":
            safe_text(
                get_value(
                    row,
                    "capital_allocation_matrix"
                ),

            ),
    }

    story.append(
        key_value_table(
            cashflow_data,
            styles
        )
    )

    story.append(
        Spacer(
            1,
            5
        )
    )

    # --------------------------------------------------------
    # Methodology
    # --------------------------------------------------------

    story.append(
        methodology_note(
            "Metrics are based on the latest available financial "
            "record in the project dataset. Missing values are shown "
            "as N/A.",
            styles
        )
    )

    return story


# ============================================================
# PAGE 2
# ============================================================

def build_page_two(
    row,
    styles
):

    company_name = get_company_name(row)

    story = []

    # --------------------------------------------------------
    # Page title
    # --------------------------------------------------------

    story.extend(
        title_block(
            f"{company_name} — Analysis",
            f"Generated on {report_date()}"
        )
    )

    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    story.append(
        section_header(
            "Profitability & Efficiency",
            styles
        )
    )

    profitability_rows = [

        [
            "Return on Equity",
            percentage(
                row,
                "return_on_equity_pct"
            )
        ],

        [
            "ROCE",
            percentage(
                row,
                "roce_calculated"
            )
        ],

        [
            "Net Profit Margin",
            percentage(
                row,
                "net_profit_margin_pct"
            )
        ],

        [
            "Operating Profit Margin",
            percentage(
                row,
                "operating_profit_margin_pct"
            )
        ],

        [
            "Asset Turnover",
            number(
                row,
                "asset_turnover"
            )
        ],

    ]

    story.append(
        make_table(
            [
                "Metric",
                "Value"
            ],
            profitability_rows,
            col_widths=[
                90,
                85
            ],
            styles=styles
        )
    )

    story.append(
        Spacer(
            1,
            6
        )
    )

    # --------------------------------------------------------
    # Leverage
    # --------------------------------------------------------

    story.append(
        section_header(
            "Leverage & Financial Risk",
            styles
        )
    )

    leverage_rows = [

        [
            "Debt to Equity",
            number(
                row,
                "debt_to_equity"
            )
        ],

        [
            "Interest Coverage",
            number(
                row,
                "interest_coverage"
            )
        ],

        [
            "Total Debt",
            number(
                row,
                "total_debt_cr"
            )
        ],

        [
            "Cash From Operations",
            number(
                row,
                "cash_from_operations_cr"
            )
        ],

    ]

    story.append(
        make_table(
            [
                "Metric",
                "Value"
            ],
            leverage_rows,
            col_widths=[
                90,
                85
            ],
            styles=styles
        )
    )

    story.append(
        Spacer(
            1,
            6
        )
    )

    # --------------------------------------------------------
    # Pros / Cons
    # --------------------------------------------------------

    story.append(
        section_header(
            "Automated Pros & Cons",
            styles
        )
    )

    pros = split_points(
        get_value(
            row,
            "pros",
            ""
        )
    )

    cons = split_points(
        get_value(
            row,
            "cons",
            ""
        )
    )

    if not pros:

        pros = [
            "No automated positive signal available."
        ]

    if not cons:

        cons = [
            "No automated negative signal available."
        ]

    story.append(
        pros_cons_table(
            pros[:12],
            cons[:12],
            styles
        )
    )

    story.append(
        Spacer(
            1,
            6
        )
    )

    # --------------------------------------------------------
    # Company links
    # --------------------------------------------------------

    story.append(
        section_header(
            "Company References",
            styles
        )
    )

    links = {

        "Company Website":
            get_value(
                row,
                "website"
            ),

        "NSE Profile":
            get_value(
                row,
                "nse_profile"
            ),

        "BSE Profile":
            get_value(
                row,
                "bse_profile"
            ),

    }

    story.append(
        key_value_table(
            links,
            styles
        )
    )

    story.append(
        Spacer(
            1,
            5
        )
    )

    # --------------------------------------------------------
    # Disclaimer
    # --------------------------------------------------------

    story.append(
        methodology_note(
            "This tearsheet is generated automatically from the "
            "Bluestock N100 analytics pipeline. It is intended for "
            "analytical and educational purposes and should not be "
            "treated as investment advice.",
            styles
        )
    )

    return story


# ============================================================
# GENERATE ONE TEARSHEET
# ============================================================

def generate_company_tearsheet(
    row,
    output_dir=OUTPUT_DIR
):

    styles = get_report_styles()

    company_name = get_company_name(row)

    filename = (
        clean_filename(company_name)
        + ".pdf"
    )

    filepath = os.path.join(
        output_dir,
        filename
    )

    story = []

    # Page 1
    story.extend(
        build_page_one(
            row,
            styles
        )
    )

    # Page 2
    story.append(
        PageBreak()
    )

    story.extend(
        build_page_two(
            row,
            styles
        )
    )

    build_report(
        filepath,
        story,
        title="Bluestock N100 | Company Tearsheet"
    )

    return filepath


# ============================================================
# GENERATE ALL TEARSHEETS
# ============================================================

def generate_all_tearsheets():

    print("=" * 70)
    print("Bluestock N100 Company Tearsheet Generator")
    print("=" * 70)

    ensure_report_directories()

    df = prepare_data()

    if df.empty:

        print(
            "ERROR: No company data available."
        )

        return

    print(
        "Companies found:",
        len(df)
    )

    generated = 0

    for index, row in df.iterrows():

        try:

            filepath = generate_company_tearsheet(
                row
            )

            generated += 1

            print(
                f"[{generated}/{len(df)}] "
                f"{get_company_name(row)}"
            )

        except Exception as exc:

            print(
                f"ERROR generating "
                f"{get_company_name(row)}: {exc}"
            )

    print()
    print("=" * 70)
    print("Tearsheet generation completed")
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

    generate_all_tearsheets()