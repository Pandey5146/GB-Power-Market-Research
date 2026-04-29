import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from scripts.data_process import process_fuel_data, process_price_data, merge_data
# from scripts.analysis import run_basic_analysis


# ==============================
# CONFIG
# ==============================

YEAR = 2024
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FUEL_OUTPUT_FILE = OUTPUT_DIR / f"fuel_mix_{YEAR}_full_year.csv"
MASTER_OUTPUT_FILE = OUTPUT_DIR / f"market_master_{YEAR}_full_year.csv"


# ==============================
# HELPERS
# ==============================

def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


def fetch_price_data_range(start_date, end_date):
    all_prices = []
    dates = generate_date_range(start_date, end_date)

    for date in dates:
        print(f"Fetching price data for {date}")

        url = f"https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/{date}"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print(f"Failed for price date {date}: {response.status_code}")
            continue

        data = response.json()

        if "data" not in data:
            print(f"No price data for {date}: {data}")
            continue

        df = pd.json_normalize(data["data"])

        if not df.empty:
            all_prices.append(df)

    if not all_prices:
        raise ValueError("No price data returned for requested range.")

    return pd.concat(all_prices, ignore_index=True)


def fetch_fuel_data_range(start_date, end_date):
    all_fuels = []
    dates = generate_date_range(start_date, end_date)

    # Fetch fuel data one day at a time to avoid large-request failures
    for date in dates:
        next_date = (
            datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        print(f"Fetching fuel data for {date}")

        url = (
            "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH"
            f"?publishDateTimeFrom={date}&publishDateTimeTo={next_date}"
        )

        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print(f"Failed for fuel date {date}: {response.status_code}")
            continue

        data = response.json()

        if "data" not in data:
            print(f"No fuel data for {date}: {data}")
            continue

        df = pd.json_normalize(data["data"])

        if not df.empty:
            all_fuels.append(df)

    if not all_fuels:
        raise ValueError("No fuel data returned for requested range.")

    return pd.concat(all_fuels, ignore_index=True)


# ==============================
# PIPELINE
# ==============================

def run_data_pipeline():
    print("Pipeline started")
    print(f"Building dataset for {YEAR}")
    print(f"Start date: {START_DATE}")
    print(f"End date: {END_DATE}")

    # ==============================
    # STEP 1 — FUEL DATA
    # ==============================

    df_fuel = fetch_fuel_data_range(START_DATE, END_DATE)

    print("\nRaw fuel data shape:", df_fuel.shape)
    print(df_fuel.head())

    df_clean = process_fuel_data(df_fuel)

    print("\nProcessed fuel data shape:", df_clean.shape)
    print(df_clean.head())
    print(df_clean.isna().sum())

    df_clean.to_csv(FUEL_OUTPUT_FILE, index=False)
    print(f"\nSaved fuel file: {FUEL_OUTPUT_FILE}")

    # ==============================
    # STEP 2 — PRICE DATA
    # ==============================

    df_price = fetch_price_data_range(START_DATE, END_DATE)

    print("\nRaw price data shape:", df_price.shape)
    print(df_price.head())

    df_price_clean = process_price_data(df_price)

    print("\nProcessed price data shape:", df_price_clean.shape)
    print(df_price_clean.head())
    print(df_price_clean.isna().sum())

    # ==============================
    # STEP 3 — MERGE
    # ==============================

    df_master = merge_data(df_clean, df_price_clean)

    print("\nMaster dataset shape:", df_master.shape)
    print(df_master.head())
    print(df_master.isna().sum())

    print("\nDate range in master dataset:")
    print("Min:", df_master["startTime"].min())
    print("Max:", df_master["startTime"].max())

    df_master.to_csv(MASTER_OUTPUT_FILE, index=False)
    print(f"\nSaved master file: {MASTER_OUTPUT_FILE}")

    # ==============================
    # STEP 4 — ANALYSIS
    # ==============================

    print("\nDATA PULL COMPLETE")
    print("Do not run analysis here. Use scripts/analysis.py or validation scripts separately.")
    # run_basic_analysis(df_master)


if __name__ == "__main__":
    run_data_pipeline()