import pandas as pd
from pathlib import Path


# ==============================
# FILE PATHS
# ==============================

DATA_FILES = {
    2023: Path("data/processed/market_master_2023_full_year.csv"),
    2024: Path("data/processed/market_master_2024_full_year.csv"),
    2025: Path("data/processed/market_master_2025_full_year.csv"),
}

OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "2023_2024_2025_annual_market_summary.csv"


# ==============================
# HELPERS
# ==============================

def load_and_prepare(year, file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file for {year}: {file_path}")

    df = pd.read_csv(file_path)

    required_cols = [
        "startTime",
        "gas_gen",
        "wind_gen",
        "interconnectors",
        "systemSellPrice",
        "netImbalanceVolume",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(
            f"{year} is missing required columns: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )

    df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
    df = df.sort_values("startTime").reset_index(drop=True)

    df["year"] = year

    df["is_negative_price"] = df["systemSellPrice"] < 0
    df["is_price_ge_100"] = df["systemSellPrice"] >= 100
    df["is_price_ge_150"] = df["systemSellPrice"] >= 150
    df["is_near_spike_200_to_250"] = (
        (df["systemSellPrice"] >= 200) & (df["systemSellPrice"] < 250)
    )
    df["is_spike_250"] = df["systemSellPrice"] >= 250
    df["is_spike_300"] = df["systemSellPrice"] >= 300

    return df


# ==============================
# MAIN
# ==============================

def main():
    annual_rows = []

    for year, file_path in DATA_FILES.items():
        print(f"\nLoading {year}: {file_path}")

        df = load_and_prepare(year, file_path)

        total_rows = len(df)

        annual_rows.append(
            {
                "year": year,
                "rows": total_rows,

                "min_time": df["startTime"].min(),
                "max_time": df["startTime"].max(),

                "avg_price": df["systemSellPrice"].mean(),
                "min_price": df["systemSellPrice"].min(),
                "max_price": df["systemSellPrice"].max(),

                "avg_imbalance": df["netImbalanceVolume"].mean(),
                "avg_wind": df["wind_gen"].mean(),
                "avg_gas": df["gas_gen"].mean(),
                "avg_interconnectors": df["interconnectors"].mean(),

                "negative_price_periods": int(df["is_negative_price"].sum()),
                "negative_price_probability": df["is_negative_price"].mean(),

                "periods_price_ge_100": int(df["is_price_ge_100"].sum()),
                "probability_price_ge_100": df["is_price_ge_100"].mean(),

                "periods_price_ge_150": int(df["is_price_ge_150"].sum()),
                "probability_price_ge_150": df["is_price_ge_150"].mean(),

                "near_spike_periods_200_to_250": int(df["is_near_spike_200_to_250"].sum()),
                "near_spike_probability_200_to_250": df["is_near_spike_200_to_250"].mean(),

                "spike_250_periods": int(df["is_spike_250"].sum()),
                "spike_250_probability": df["is_spike_250"].mean(),

                "spike_300_periods": int(df["is_spike_300"].sum()),
                "spike_300_probability": df["is_spike_300"].mean(),
            }
        )

    annual = pd.DataFrame(annual_rows)

    annual = annual.round(
        {
            "avg_price": 4,
            "min_price": 4,
            "max_price": 4,
            "avg_imbalance": 4,
            "avg_wind": 4,
            "avg_gas": 4,
            "avg_interconnectors": 4,
            "negative_price_probability": 4,
            "probability_price_ge_100": 4,
            "probability_price_ge_150": 4,
            "near_spike_probability_200_to_250": 4,
            "spike_250_probability": 4,
            "spike_300_probability": 4,
        }
    )

    annual.to_csv(OUTPUT_FILE, index=False)

    print("\n2023–2024–2025 ANNUAL MARKET SUMMARY")
    print(annual)

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()