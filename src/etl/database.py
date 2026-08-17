import pandas as pd
import sqlite3
import os
import time


# =========================================================
# PATHS
# =========================================================

DATA_PATH = "data/raw"

DATABASE_PATH = "data/nifty100.db"

AUDIT_PATH = "output/load_audit.csv"


# =========================================================
# ALL 12 EXCEL FILES
# =========================================================

FILES = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
    "analysis.xlsx",
    "sectors.xlsx",
    "stock_prices.xlsx",
    "peer_groups.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx"
]


# =========================================================
# TABLE LOAD ORDER
#
# companies MUST be loaded first because all other
# tables use company_id as a foreign key.
# =========================================================

TABLE_ORDER = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "documents",
    "prosandcons",
    "analysis",
    "sectors",
    "stock_prices",
    "peer_groups",
    "financial_ratios",
    "market_cap"
]


# =========================================================
# CREATE DATABASE FOLDER
# =========================================================

os.makedirs(
    "data",
    exist_ok=True
)

os.makedirs(
    "output",
    exist_ok=True
)


# =========================================================
# CREATE DATABASE SCHEMA
# =========================================================

def create_schema(connection):

    print("\nCreating database schema...")

    schema = """

    PRAGMA foreign_keys = ON;

    -- =====================================================
    -- 1. COMPANIES
    -- =====================================================

    CREATE TABLE IF NOT EXISTS companies (
        id TEXT PRIMARY KEY,
        company_logo TEXT,
        company_name TEXT,
        chart_link TEXT,
        about_company TEXT,
        website TEXT,
        nse_profile TEXT,
        bse_profile TEXT,
        face_value REAL,
        book_value REAL,
        roce_percentage REAL,
        roe_percentage REAL
    );


    -- =====================================================
    -- 2. PROFIT AND LOSS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS profitandloss (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        year TEXT,
        sales REAL,
        expenses REAL,
        operating_profit REAL,
        opm_percentage REAL,
        other_income REAL,
        interest REAL,
        depreciation REAL,
        profit_before_tax REAL,
        tax_percentage REAL,
        net_profit REAL,
        eps REAL,
        dividend_payout REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 3. BALANCE SHEET
    -- =====================================================

    CREATE TABLE IF NOT EXISTS balancesheet (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        year TEXT,
        equity_capital REAL,
        reserves REAL,
        borrowings REAL,
        other_liabilities REAL,
        total_liabilities REAL,
        fixed_assets REAL,
        cwip REAL,
        investments REAL,
        other_asset REAL,
        total_assets REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 4. CASH FLOW
    -- =====================================================

    CREATE TABLE IF NOT EXISTS cashflow (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        year TEXT,
        operating_activity REAL,
        investing_activity REAL,
        financing_activity REAL,
        net_cash_flow REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 5. DOCUMENTS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        year TEXT,
        annual_report TEXT,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 6. PROS AND CONS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS prosandcons (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        pros TEXT,
        cons TEXT,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 7. ANALYSIS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS analysis (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        compounded_sales_growth REAL,
        compounded_profit_growth REAL,
        stock_price_cagr REAL,
        roe REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 8. SECTORS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS sectors (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        broad_sector TEXT,
        sub_sector TEXT,
        index_weight_pct REAL,
        market_cap_category TEXT,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 9. STOCK PRICES
    -- =====================================================

    CREATE TABLE IF NOT EXISTS stock_prices (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        date TEXT,
        open_price REAL,
        high_price REAL,
        low_price REAL,
        close_price REAL,
        volume REAL,
        adjusted_close REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 10. PEER GROUPS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS peer_groups (
        id INTEGER PRIMARY KEY,
        peer_group_name TEXT,
        company_id TEXT NOT NULL,
        is_benchmark INTEGER,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 11. FINANCIAL RATIOS
    -- =====================================================

    CREATE TABLE IF NOT EXISTS financial_ratios (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        year TEXT,
        net_profit_margin_pct REAL,
        operating_profit_margin_pct REAL,
        return_on_equity_pct REAL,
        debt_to_equity REAL,
        interest_coverage REAL,
        asset_turnover REAL,
        free_cash_flow_cr REAL,
        capex_cr REAL,
        earnings_per_share REAL,
        book_value_per_share REAL,
        dividend_payout_ratio_pct REAL,
        total_debt_cr REAL,
        cash_from_operations_cr REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );


    -- =====================================================
    -- 12. MARKET CAP
    -- =====================================================

    CREATE TABLE IF NOT EXISTS market_cap (
        id INTEGER PRIMARY KEY,
        company_id TEXT NOT NULL,
        year TEXT,
        market_cap_crore REAL,
        enterprise_value_crore REAL,
        pe_ratio REAL,
        pb_ratio REAL,
        ev_ebitda REAL,
        dividend_yield_pct REAL,

        FOREIGN KEY (company_id)
            REFERENCES companies(id)
    );

    """

    connection.executescript(schema)

    print("Database schema created!")


# =========================================================
# NORMALIZE COLUMN NAMES
# =========================================================

def normalize_columns(df):

    # Remove spaces from beginning and end
    df.columns = df.columns.astype(str).str.strip()

    # Convert column names to lowercase
    df.columns = df.columns.str.lower()

    # Rename known columns
    df = df.rename(
        columns={
            "annual_report": "annual_report",
            "year": "year"
        }
    )

    return df


# =========================================================
# LOAD ONE EXCEL FILE
# =========================================================

def read_excel_file(file_name):

    file_path = os.path.join(
        DATA_PATH,
        file_name
    )

    print("\nLoading:", file_name)

    if not os.path.exists(file_path):

        print(
            "WARNING: File not found:",
            file_path
        )

        return None

    try:

        # Core 7 files have an extra row before the header
        core_files = [
            "companies.xlsx",
            "profitandloss.xlsx",
            "balancesheet.xlsx",
            "cashflow.xlsx",
            "documents.xlsx",
            "prosandcons.xlsx",
            "analysis.xlsx"
        ]

        # Decide which row contains the header
        if file_name in core_files:
            header_row = 1
        else:
            header_row = 0

        # Read Excel file
        df = pd.read_excel(
            file_path,
            header=header_row
        )

        # Normalize column names
        df = normalize_columns(df)

        print(
            "Rows:",
            len(df)
        )

        print(
            "Columns:",
            df.columns.tolist()
        )

        return df

    except Exception as e:

        print(
            "ERROR reading file:",
            file_name
        )

        print(
            "Reason:",
            e
        )

        return None


# =========================================================
# LOAD ALL EXCEL FILES INTO MEMORY
# =========================================================

def load_all_excel_files():

    data = {}

    for file_name in FILES:

        table_name = file_name.replace(
            ".xlsx",
            ""
        )

        df = read_excel_file(
            file_name
        )

        if df is not None:

            data[table_name] = df

    return data


# =========================================================
# CLEAN DATAFRAME BEFORE DATABASE INSERT
# =========================================================

def clean_dataframe(df, table):

    # Make a copy
    df = df.copy()

    # Normalize column names
    df = normalize_columns(df)

    # Remove completely empty rows
    df = df.dropna(
        how="all"
    )

    # Remove duplicate exact rows
    df = df.drop_duplicates()

    # Clean company_id
    if "company_id" in df.columns:

        df["company_id"] = (
            df["company_id"]
            .astype(str)
            .str.strip()
        )

    # Clean year
    if "year" in df.columns:

        df["year"] = (
            df["year"]
            .astype(str)
            .str.strip()
        )

    # Clean date
    if "date" in df.columns:

        df["date"] = (
            df["date"]
            .astype(str)
            .str.strip()
        )

    return df


# =========================================================
# CHECK FOREIGN KEYS
# =========================================================

def check_company_ids(
    df,
    table,
    valid_company_ids
):

    if table == "companies":

        return df

    if "company_id" not in df.columns:

        return df

    # Find invalid IDs
    invalid_ids = set(
        df.loc[
            ~df["company_id"].isin(
                valid_company_ids
            ),
            "company_id"
        ]
    )

    if len(invalid_ids) > 0:

        print(
            "\nWARNING:",
            table,
            "contains invalid company IDs:"
        )

        print(
            sorted(
                invalid_ids
            )
        )

        print(
            "These rows will NOT be loaded."
        )

        # Remove invalid rows
        df = df[
            df["company_id"].isin(
                valid_company_ids
            )
        ].copy()

    return df


# =========================================================
# LOAD ONE TABLE INTO SQLITE
# =========================================================

def load_table(
    connection,
    table,
    df,
    valid_company_ids
):

    print("\n" + "=" * 50)

    print(
        "Loading table:",
        table
    )

    # Clean dataframe
    df = clean_dataframe(
        df,
        table
    )

    # Check foreign key values
    df = check_company_ids(
        df,
        table,
        valid_company_ids
    )

    print(
        "Final rows:",
        len(df)
    )

    print(
        "Final columns:",
        df.columns.tolist()
    )

    # If no rows remain
    if len(df) == 0:

        print(
            "No rows to load."
        )

        return 0

    # Check database columns
    cursor = connection.cursor()

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    database_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    print(
        "Database columns:",
        database_columns
    )

    # Find columns in Excel but not database
    extra_columns = [
        column
        for column in df.columns
        if column not in database_columns
    ]

    if len(extra_columns) > 0:

        print(
            "WARNING: Extra columns found:",
            extra_columns
        )

        # Keep only database columns
        df = df[
            [
                column
                for column in df.columns
                if column in database_columns
            ]
        ]

    # Find missing columns
    missing_columns = [
        column
        for column in database_columns
        if column not in df.columns
        and column != "id"
    ]

    if len(missing_columns) > 0:

        print(
            "WARNING: Missing columns:",
            missing_columns
        )

    # Insert data
    try:
        df.to_sql(
            table,
            connection,
            if_exists="append",
            index=False
        )

        print(
            table,
            "loaded successfully!"
        )

        return len(df)

    except Exception as e:
        print("\nERROR while loading:", table)
        print("Error type:", type(e))

        print("Error message:", repr(e))

        # Try to show the real SQLite error
        if hasattr(e, "__cause__") and e.__cause__:
            print("Original error:", repr(e.__cause__))

        # Print the data that caused the problem
        print("\nDataFrame information:")
        print("Rows:", len(df))
        print("Columns:", df.columns.tolist())

        print("\nFirst 3 rows:")
        print(df.head(3))

        raise e

# =========================================================
# MAIN DATABASE LOADER
# =========================================================
connection = sqlite3.connect(
    DATABASE_PATH
)
# Start with a fresh database every time
cursor = connection.cursor()

for table in TABLE_ORDER:
    cursor.execute(
        f"DROP TABLE IF EXISTS {table}"
    )

connection.commit()

print("Old tables deleted. Starting fresh database.")
def load_database():

    start_time = time.time()

    print(
        "\n======================================"
    )

    print(
        "STARTING DATABASE LOAD"
    )

    print(
        "======================================"
    )


    # -----------------------------------------------------
    # CONNECT TO DATABASE
    # -----------------------------------------------------

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    # Enable foreign keys
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )


    try:

        # -------------------------------------------------
        # CREATE SCHEMA
        # -------------------------------------------------

        create_schema(
            connection
        )


        # -------------------------------------------------
        # LOAD ALL EXCEL FILES
        # -------------------------------------------------

        data = load_all_excel_files()


        # -------------------------------------------------
        # CHECK COMPANIES
        # -------------------------------------------------

        if "companies" not in data:

            raise Exception(
                "companies.xlsx was not loaded."
            )


        # -------------------------------------------------
        # GET VALID COMPANY IDS
        # -------------------------------------------------

        companies = data[
            "companies"
        ]

        companies = clean_dataframe(
            companies,
            "companies"
        )


        valid_company_ids = set(
            companies["id"]
            .astype(str)
            .str.strip()
        )


        print(
            "\n======================================"
        )

        print(
            "VALID COMPANY IDs:",
            len(valid_company_ids)
        )

        print(
            "======================================"
        )


        # -------------------------------------------------
        # AUDIT LIST
        # -------------------------------------------------

        audit = []


        # -------------------------------------------------
        # LOAD ALL TABLES IN CORRECT ORDER
        # -------------------------------------------------

        for table in TABLE_ORDER:

            if table not in data:

                print(
                    "\nWARNING:",
                    table,
                    "data not found."
                )

                continue


            df = data[
                table
            ]


            rows_before = len(
                df
            )


            try:

                rows_loaded = load_table(
                    connection,
                    table,
                    df,
                    valid_company_ids
                )


                audit.append({

                    "table":
                        table,

                    "rows_before":
                        rows_before,

                    "rows_loaded":
                        rows_loaded,

                    "status":
                        "SUCCESS",

                    "error":
                        ""

                })


            except Exception as e:

                audit.append({

                    "table":
                        table,

                    "rows_before":
                        rows_before,

                    "rows_loaded":
                        0,

                    "status":
                        "FAILED",

                    "error":
                        str(e)

                })

                # Stop loading
                raise


        # -------------------------------------------------
        # SAVE DATABASE
        # -------------------------------------------------

        connection.commit()


        # -------------------------------------------------
        # SAVE AUDIT FILE
        # -------------------------------------------------

        audit_df = pd.DataFrame(
            audit
        )

        audit_df.to_csv(
            AUDIT_PATH,
            index=False
        )


        # -------------------------------------------------
        # FINAL OUTPUT
        # -------------------------------------------------

        end_time = time.time()

        total_time = (
            end_time
            - start_time
        )


        print(
            "\n======================================"
        )

        print(
            "DATABASE LOADING COMPLETED!"
        )

        print(
            "======================================"
        )

        print(
            "Database:",
            DATABASE_PATH
        )

        print(
            "Audit file:",
            AUDIT_PATH
        )

        print(
            "Time taken:",
            round(
                total_time,
                2
            ),
            "seconds"
        )


        print(
            "\nLOAD AUDIT:"
        )

        print(
            audit_df
        )


    except Exception as e:

        print(
            "\n======================================"
        )

        print(
            "DATABASE LOADING FAILED!"
        )

        print(
            "======================================"
        )

        print(
            "Reason:",
            e
        )


    finally:

        connection.close()

        print(
            "\nDatabase connection closed."
        )


# =========================================================
# RUN PROGRAM
# =========================================================

if __name__ == "__main__":

    load_database()