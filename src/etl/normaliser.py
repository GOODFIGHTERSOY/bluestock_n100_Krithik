import re
import pandas as pd


def normalize_year(value):
    """
    Normalize various year formats into a 4-digit integer.

    Examples:
        FY2023   -> 2023
        FY23     -> 2023
        FY 23    -> 2023
        2022-23  -> 2023
        2023-24  -> 2024
        Mar 2024 -> 2024
        2024     -> 2024
    """

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    # FY2023
    match = re.fullmatch(r"FY(\d{4})", value)
    if match:
        return int(match.group(1))

    # FY23 or FY 23
    match = re.fullmatch(r"FY\s*(\d{2})", value)
    if match:
        return 2000 + int(match.group(1))

    # 2022-23
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match:
        return 2000 + int(match.group(2))

    # Mar 2024
    match = re.search(r"(20\d{2})", value)
    if match:
        return int(match.group(1))

    # Plain year
    match = re.fullmatch(r"(20\d{2})", value)
    if match:
        return int(match.group(1))

    return None
import re

def normalize_ticker(ticker):
    """
    Normalize company ticker symbols.

    Examples:
        ' tcs ' -> 'TCS'
        'INFY.NS' -> 'INFY'
        'reliance' -> 'RELIANCE'
    """
    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    # Remove exchange suffix like .NS or .BO
    ticker = re.sub(r"\.(NS|BO)$", "", ticker)

    return ticker