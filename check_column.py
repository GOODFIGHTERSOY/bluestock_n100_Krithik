from src.etl.loader import load_all_files

data = load_all_files()

for table, df in data.items():

    print("\n====================")
    print(table)
    print("====================")

    print(
        list(df.columns)
    )