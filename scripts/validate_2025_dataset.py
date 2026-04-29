import pandas as pd
from pathlib import Path


DATA_FILE = Path("data/processed/market_master_2025_full_year.csv")

OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VALIDATION_OUTPUT = OUTPUT_DIR / "2025_dataset_validation_summary.csv"
MISSING_TIMESTAMPS_OUTPUT = OUTPUT_DIR / "2025_missing_timestamps.csv"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing file: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required_cols = [
        "startTime",
        "gas_gen",
        "wind_gen",
        "interconnectors",
        "systemSellPrice",
        "systemBuyPrice",
        "netImbalanceVolume",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(
            f"Missing required columns: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )

    df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
    df = df.sort_values("startTime").reset_index(drop=True)

    expected_range = pd.date_range(
        start="2025-01-01 00:00:00+00:00",
        end="2025-12-31 23:30:00+00:00",
        freq="30min",
    )

    actual_times = set(df["startTime"].dropna())
    missing_times = [t for t in expected_range if t not in actual_times]

    missing_df = pd.DataFrame({"missing_startTime": missing_times})
    missing_df.to_csv(MISSING_TIMESTAMPS_OUTPUT, index=False)

    validation = pd.DataFrame(
        [
            {
                "year": 2025,
                "total_rows": len(df),
                "expected_rows": len(expected_range),
                "missing_timestamps": len(missing_times),
                "duplicate_timestamps": df["startTime"].duplicated().sum(),
                "null_timestamps": df["startTime"].isna().sum(),
                "min_time": df["startTime"].min(),
                "max_time": df["startTime"].max(),
                "spike_250_count": int((df["systemSellPrice"] >= 250).sum()),
                "spike_300_count": int((df["systemSellPrice"] >= 300).sum()),
                "near_spike_200_to_250_count": int(
                    ((df["systemSellPrice"] >= 200) & (df["systemSellPrice"] < 250)).sum()
                ),
                "negative_price_count": int((df["systemSellPrice"] < 0).sum()),
                "avg_price": df["systemSellPrice"].mean(),
                "avg_imbalance": df["netImbalanceVolume"].mean(),
                "avg_wind": df["wind_gen"].mean(),
                "avg_gas": df["gas_gen"].mean(),
                "avg_interconnectors": df["interconnectors"].mean(),
            }
        ]
    )

    validation = validation.round(
        {
            "avg_price": 4,
            "avg_imbalance": 4,
            "avg_wind": 4,
            "avg_gas": 4,
            "avg_interconnectors": 4,
        }
    )

    validation.to_csv(VALIDATION_OUTPUT, index=False)

    print("\n2025 DATASET VALIDATION SUMMARY")
    print(validation)

    print(f"\nSaved validation summary to: {VALIDATION_OUTPUT}")
    print(f"Saved missing timestamps to: {MISSING_TIMESTAMPS_OUTPUT}")

    if len(missing_df) > 0:
        print("\nFirst missing timestamps:")
        print(missing_df.head(20))


if __name__ == "__main__":
    main()