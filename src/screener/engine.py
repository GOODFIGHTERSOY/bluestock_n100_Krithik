import sqlite3
from unittest import result
import pandas as pd
import yaml


def load_config(config_path="config/screener_config.yaml"):
    """
    Load YAML configuration.
    """
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def load_financial_ratios(database):
    """
    Load financial_ratios table.
    """
    conn = sqlite3.connect(database)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    return df


def build_query(filters):
    """
    Convert YAML filters into pandas query string.
    """

    conditions = []

    for column, condition in filters.items():
        conditions.append(f"`{column}` {condition}")

    return " & ".join(conditions)


def apply_filters(df, filters):
    """
    Apply screener filters using pandas query.
    """

    query = build_query(filters)

    print("\nGenerated Query:\n")
    print(query)

    screened = df.query(query)

    return screened


def run_all_screeners():

    config = load_config()

    database = config["database"]

    presets = config["presets"]

    df = load_financial_ratios(database)

    print(f"\nUniverse Size : {len(df)} companies\n")

    print("=" * 60)
    print("Columns Loaded from financial_ratios")
    print("=" * 60)
    print(df.columns.tolist())
    print("=" * 60)

    for preset_name, filters in presets.items():

        print("=" * 60)
        print(f"Running Preset : {preset_name}")
        print("=" * 60)

        screened = apply_filters(df, filters)

        print(f"Companies Selected : {len(screened)}")

        output_file = f"output/{preset_name}_screener.csv"

        screened.to_csv(
            output_file,
            index=False
        )

        print(f"Saved : {output_file}")

if __name__ == "__main__":

    run_all_screeners()
    

    