import pandas as pd
import os


DATA_PATH = "data/raw"


files = [
    "sectors.xlsx",
    "stock_prices.xlsx",
    "peer_groups.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx"
]


for file in files:

    print("\n" + "=" * 50)
    print("Loading:", file)

    file_path = os.path.join(
        DATA_PATH,
        file
    )

    table_name = file.replace(
        ".xlsx",
        ""
    )

    # Supplementary files have headers in the first row
    df = pd.read_excel(
        file_path,
        header=0
    )

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    print("Rows:", len(df))
    print("Columns:", list(df.columns))