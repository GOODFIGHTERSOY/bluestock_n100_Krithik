import pandas as pd
import os
from src.etl.loader import load_all_files
from src.etl.normaliser import normalize_year

# Where our Excel files are stored
DATA_PATH = "data/raw"

# Where validation errors will be saved
OUTPUT_PATH = "output/validation_failures.csv"

# =========================================================
# Store all validation failures here
# =========================================================

failures = []
def run_validation():

    # Load data through loader
    # This also removes duplicate company_id + year records
    data = load_all_files()

    print("\nStarting validation...")

def add_failure(
    rule,
    table,
    message,
    severity="WARNING"
):
    """
    Add one validation failure
    to our failures list.
    """

    failures.append({
        "rule": rule,
        "table": table,
        "severity": severity,
        "message": message
    })


# =========================================================
# DQ-01: Primary Key Uniqueness
# =========================================================

def check_primary_key(df, table):

    # Check whether ID column exists
    if "id" not in df.columns:
        return

    # Find duplicate IDs
    duplicates = df["id"].duplicated()

    # Count duplicates
    count = duplicates.sum()

    if count > 0:

        add_failure(
            "DQ-01",
            table,
            f"{count} duplicate id values found",
            "CRITICAL"
        )


# =========================================================
# DQ-02: Company ID + Year Uniqueness
# =========================================================

def check_company_year(df, table):

    if "company_id" not in df.columns:
        return

    if "year" not in df.columns:
        return

    duplicates = df.duplicated(
        subset=[
            "company_id",
            "year"
        ]
    )

    if duplicates.any():

        count = duplicates.sum()

        add_failure(
            "DQ-02",
            table,
            f"{count} duplicate company_id + year combinations",
            "CRITICAL"
        )


# =========================================================
# DQ-03: Foreign Key Integrity
# =========================================================

def check_foreign_key(
    df,
    table,
    companies
):

    if "company_id" not in df.columns:
        return

    if "company_id" not in companies.columns:
        return

    valid_ids = set(
        companies["company_id"]
    )

    invalid = df[
        ~df["company_id"].isin(
            valid_ids
        )
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-03",
            table,
            f"{len(invalid)} invalid company_id values",
            "CRITICAL"
        )


# =========================================================
# DQ-04: Balance Sheet Check
# =========================================================

def check_balance_sheet(df):

    required = [
        "total_assets",
        "total_liabilities"
    ]

    if not all(
        column in df.columns
        for column in required
    ):
        return

    difference = (
        df["total_assets"]
        - df["total_liabilities"]
    ).abs()

    invalid = difference[
        difference > 0.01
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-04",
            "balancesheet",
            f"{len(invalid)} balance sheet mismatches",
            "WARNING"
        )


# =========================================================
# DQ-05: OPM Check
# =========================================================

def check_opm(df):

    if "opm" not in df.columns:
        return

    invalid = df[
        (df["opm"] < -100)
        |
        (df["opm"] > 100)
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-05",
            "profitandloss",
            f"{len(invalid)} invalid OPM values",
            "WARNING"
        )


# =========================================================
# DQ-06: Positive Sales
# =========================================================

def check_sales(df):

    if "sales" not in df.columns:
        return

    sales = pd.to_numeric(
        df["sales"],
        errors="coerce"
    )

    invalid = sales[
        sales <= 0
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-06",
            "profitandloss",
            f"{len(invalid)} non-positive sales values",
            "WARNING"
        )

# =========================================================
# DQ-07: Missing Company ID
# =========================================================

def check_missing_company_id(
    df,
    table
):

    if "company_id" not in df.columns:
        return

    missing = df[
        df["company_id"].isna()
    ]

    if len(missing) > 0:

        add_failure(
            "DQ-07",
            table,
            f"{len(missing)} missing company_id values",
            "CRITICAL"
        )


# =========================================================
# DQ-08: Missing Year
# =========================================================

def check_missing_year(
    df,
    table
):

    if "year" not in df.columns:
        return

    missing = df[
        df["year"].isna()
    ]

    if len(missing) > 0:

        add_failure(
            "DQ-08",
            table,
            f"{len(missing)} missing year values",
            "WARNING"
        )


# =========================================================
# DQ-09: Invalid Year
# =========================================================

def check_invalid_year(df, table):

    if "year" not in df.columns:
        return

    # Normalize the year column
    years = df["year"].apply(
        normalize_year
    )

    # Valid years are either:
    # 4-digit numbers OR TTM

    invalid = []

    for year in years:

        if year == "TTM":
            continue

        if year is None:
            invalid.append(year)
            continue

        if year < 1900 or year > 2100:
            invalid.append(year)

    if len(invalid) > 0:

        add_failure(
            "DQ-09",
            table,
            f"{len(invalid)} invalid year values",
            "WARNING"
        )
# =========================================================
# DQ-10: Negative Stock Price
# =========================================================

def check_stock_price(df):

    if "price" not in df.columns:
        return

    invalid = df[
        df["price"] <= 0
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-10",
            "stock_prices",
            f"{len(invalid)} invalid stock prices",
            "WARNING"
        )


# =========================================================
# DQ-11: Missing Ticker
# =========================================================

def check_ticker(
    df,
    table
):

    if "ticker" not in df.columns:
        return

    missing = df[
        df["ticker"].isna()
    ]

    if len(missing) > 0:

        add_failure(
            "DQ-11",
            table,
            f"{len(missing)} missing ticker values",
            "WARNING"
        )


# =========================================================
# DQ-12: Negative EPS
# =========================================================

def check_eps(df):

    if "eps" not in df.columns:
        return

    invalid = df[
        df["eps"] < 0
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-12",
            "profitandloss",
            f"{len(invalid)} negative EPS values",
            "WARNING"
        )


# =========================================================
# DQ-13: Missing Sales
# =========================================================

def check_missing_sales(df):

    if "sales" not in df.columns:
        return

    missing = df[
        df["sales"].isna()
    ]

    if len(missing) > 0:

        add_failure(
            "DQ-13",
            "profitandloss",
            f"{len(missing)} missing sales values",
            "WARNING"
        )


# =========================================================
# DQ-14: Invalid URL
# =========================================================

def check_url(df):

    if "url" not in df.columns:
        return

    invalid = df[
        ~df["url"]
        .astype(str)
        .str.startswith("http")
    ]

    if len(invalid) > 0:

        add_failure(
            "DQ-14",
            "documents",
            f"{len(invalid)} invalid URLs",
            "WARNING"
        )


# =========================================================
# DQ-15: Duplicate Rows
# =========================================================

def check_duplicate_rows(
    df,
    table
):

    duplicates = df[
        df.duplicated()
    ]

    if len(duplicates) > 0:

        add_failure(
            "DQ-15",
            table,
            f"{len(duplicates)} duplicate rows",
            "WARNING"
        )


# =========================================================
# DQ-16: Empty Rows
# =========================================================

def check_empty_rows(
    df,
    table
):

    empty = df[
        df.isna().all(axis=1)
    ]

    if len(empty) > 0:

        add_failure(
            "DQ-16",
            table,
            f"{len(empty)} completely empty rows",
            "WARNING"
        )


# =========================================================
# Load Excel Files
# =========================================================

def load_files():

    files = [
        "companies.xlsx",
        "profitandloss.xlsx",
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "documents.xlsx",
        "prosandcons.xlsx",
        "analysis.xlsx"
    ]

    data = {}

    for file in files:

        path = os.path.join(
            DATA_PATH,
            file
        )

        if os.path.exists(path):

            name = file.replace(
                ".xlsx",
                ""
            )

            data[name] = pd.read_excel(
                path,
                header=1
            )

            print(
                "Loaded:",
                file
            )

    return data


# =========================================================
# Run All 16 Rules
# =========================================================

def run_validation(data):

    global failures

    failures = []

    companies = data.get(
        "companies",
        pd.DataFrame()
    )


    for table, df in data.items():

        print(
            "\nChecking:",
            table
        )

        # DQ-01
        check_primary_key(
            df,
            table
        )

        # DQ-02
        check_company_year(
            df,
            table
        )

        # DQ-03
        check_foreign_key(
            df,
            table,
            companies
        )

        # DQ-07
        check_missing_company_id(
            df,
            table
        )

        # DQ-08
        check_missing_year(
            df,
            table
        )

        # DQ-09
        check_invalid_year(
            df,
            table
        )

        # DQ-11
        check_ticker(
            df,
            table
        )

        # DQ-15
        check_duplicate_rows(
            df,
            table
        )

        # DQ-16
        check_empty_rows(
            df,
            table
        )


    # Specific table checks

    if "balancesheet" in data:

        check_balance_sheet(
            data["balancesheet"]
        )


    if "profitandloss" in data:

        check_opm(
            data["profitandloss"]
        )

        check_sales(
            data["profitandloss"]
        )

        
        check_missing_sales(
            data["profitandloss"]
        )


    if "stock_prices" in data:

        check_stock_price(
            data["stock_prices"]
        )


    if "documents" in data:

        check_url(
            data["documents"]
        )


    # Create output folder
    os.makedirs(
        "output",
        exist_ok=True
    )


    # Save failures
    result = pd.DataFrame(
        failures
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )


    print(
        "\nValidation completed!"
    )

    print(
        "Total failures:",
        len(result)
    )

    print(
        "Saved to:",
        OUTPUT_PATH
    )


# =========================================================
# Main Program
# =========================================================

if __name__ == "__main__":

    # Load cleaned data using loader.py
    data = load_all_files()

    # Run all validation rules
    run_validation(
        data
    )