import pandas as pd

df = pd.read_csv("data/processed/market_master_2023_full_year.csv")
df["startTime"] = pd.to_datetime(df["startTime"])
df = df.sort_values("startTime").reset_index(drop=True)

expected_index = pd.date_range(
    start="2023-01-01 00:00:00+00:00",
    end="2023-12-31 23:30:00+00:00",
    freq="30min"
)

actual_index = pd.DatetimeIndex(df["startTime"])

missing_timestamps = expected_index.difference(actual_index)
duplicate_timestamps = actual_index[actual_index.duplicated()]

print("Expected rows:", len(expected_index))
print("Actual rows:", len(df))
print("Missing rows:", len(missing_timestamps))
print("Duplicate rows:", len(duplicate_timestamps))

print("\nFirst 20 missing timestamps:")
print(missing_timestamps[:20])