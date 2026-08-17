import sqlite3
import pandas as pd

DATABASE = "data/nifty100.db"


def load_db(table_name):
    """
    Load any SQLite table into a DataFrame.
    """

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        f"SELECT * FROM {table_name}",
        conn
    )

    conn.close()

    return df