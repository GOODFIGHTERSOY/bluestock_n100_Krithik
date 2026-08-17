import sqlite3
import pandas as pd


# =========================================================
# DATABASE PATH
# =========================================================

DATABASE_PATH = "data/nifty100.db"


# =========================================================
# COMPANIES TO REVIEW
# =========================================================

COMPANIES = [
    "ABB",
    "ADANIENSOL",
    "ADANIENT",
    "ADANIGREEN",
    "ADANIPORTS"
]


# =========================================================
# TIME-SERIES TABLES
# =========================================================

TIME_SERIES_TABLES = [
    "profitandloss",
    "balancesheet",
    "cashflow",
    "documents",
    "stock_prices",
    "financial_ratios",
    "market_cap"
]


# =========================================================
# CONNECT TO DATABASE
# =========================================================

connection = sqlite3.connect(
    DATABASE_PATH
)


# =========================================================
# CHECK EACH COMPANY
# =========================================================

for company in COMPANIES:

    print("\n")
    print("=" * 60)
    print("CHECKING COMPANY:", company)
    print("=" * 60)

    for table in TIME_SERIES_TABLES:

        print("\nTable:", table)

        query = f"""
        SELECT *
        FROM {table}
        WHERE company_id = ?
        """

        df = pd.read_sql_query(
            query,
            connection,
            params=(company,)
        )

        print(
            "Number of rows:",
            len(df)
        )

        if len(df) > 0:

            print(
                "First 3 rows:"
            )

            print(
                df.head(3).to_string(
                    index=False
                )
            )

        else:

            print(
                "WARNING: No data found"
            )


# =========================================================
# CLOSE DATABASE
# =========================================================

connection.close()

print("\n")
print("=" * 60)
print("DATA QUALITY REVIEW COMPLETED")
print("=" * 60)