import pandas as pd
import os


# =========================================
# DATA LOCATION
# =========================================

DATA_PATH = "data/raw"


# =========================================
# ALL 12 EXCEL FILES
# =========================================

files = [

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


# =========================================
# LOAD ONE EXCEL FILE
# =========================================

def load_excel_file(
    file_name
):

    file_path = os.path.join(

        DATA_PATH,

        file_name

    )


    # All 12 files have headers
    # in the first row

    df = pd.read_excel(

        file_path,

        header=0

    )


    # Remove spaces from column names

    df.columns = (

        df.columns

        .astype(str)

        .str.strip()

        .str.lower()

    )


    return df


# =========================================
# NORMALIZE COMPANY IDs
# =========================================

def normalize_company_id(
    df
):

    # Companies table uses "id"

    if "id" in df.columns:

        df["id"] = (

            df["id"]

            .astype(str)

            .str.strip()

            .str.upper()

        )


    # Other tables use "company_id"

    if "company_id" in df.columns:

        df["company_id"] = (

            df["company_id"]

            .astype(str)

            .str.strip()

            .str.upper()

        )


    return df


# =========================================
# REMOVE DUPLICATES
# =========================================

def remove_duplicates(
    df,
    table_name
):

    financial_tables = [

        "profitandloss",

        "balancesheet",

        "cashflow"

    ]


    # Financial tables should have
    # one record per company and year

    if table_name in financial_tables:

        if (

            "company_id" in df.columns

            and

            "year" in df.columns

        ):

            before = len(df)


            df = df.drop_duplicates(

                subset=[

                    "company_id",

                    "year"

                ],

                keep="first"

            )


            after = len(df)


            removed = before - after


            if removed > 0:

                print(

                    f"{table_name}: "

                    f"Removed {removed} duplicates"

                )


    return df


# =========================================
# REMOVE INVALID COMPANY IDs
# =========================================

def remove_invalid_company_ids(

    df,

    table_name,

    valid_company_ids

):

    if "company_id" not in df.columns:

        return df


    before = len(df)


    invalid = ~df["company_id"].isin(

        valid_company_ids

    )


    invalid_ids = (

        df.loc[

            invalid,

            "company_id"

        ]

        .drop_duplicates()

        .tolist()

    )


    if len(invalid_ids) > 0:

        print(

            f"{table_name}: "

            f"Removing {invalid.sum()} "

            f"rows with invalid company_id"

        )


        print(

            "Invalid IDs:",

            invalid_ids

        )


    df = df[

        ~invalid

    ].copy()


    return df


# =========================================
# LOAD ALL 12 FILES
# =========================================

def load_all_files():

    data = {}


    # =====================================
    # STEP 1
    # Load companies first
    # =====================================

    companies = load_excel_file(

        "companies.xlsx"

    )


    companies = normalize_company_id(

        companies

    )


    companies = companies.drop_duplicates(

        subset=["id"],

        keep="first"

    )


    data["companies"] = companies


    # Valid company IDs

    valid_company_ids = set(

        companies["id"]

    )


    print(

        "Loaded: companies.xlsx"

    )


    print(

        "Companies:",

        len(companies)

    )


    # =====================================
    # STEP 2
    # Load remaining files
    # =====================================

    for file in files[1:]:


        table_name = file.replace(

            ".xlsx",

            ""

        )


        print(

            "\nLoading:",

            file

        )


        # Load Excel

        df = load_excel_file(

            file

        )


        # Normalize IDs

        df = normalize_company_id(

            df

        )


        # Remove duplicate records

        df = remove_duplicates(

            df,

            table_name

        )


        # Remove invalid company IDs

        df = remove_invalid_company_ids(

            df,

            table_name,

            valid_company_ids

        )


        # Save DataFrame

        data[table_name] = df


        print(

            "Rows:",

            len(df)

        )


        print(

            "Columns:",

            list(df.columns)

        )


    return data


# =========================================
# RUN DIRECTLY
# =========================================

if __name__ == "__main__":

    all_data = load_all_files()


    print(

        "\n================================"

    )

    print(

        "All 12 files loaded!"

    )

    print(

        "================================"

    )


    for name, df in all_data.items():

        print(

            name,

            "->",

            df.shape

        )