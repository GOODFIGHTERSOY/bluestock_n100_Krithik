import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

df.to_csv(
    "output/financial_ratios.csv",
    index=False
)

conn.close()

print("financial_ratios.csv exported successfully.")