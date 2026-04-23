import pandas as pd

# 2023
df_2023 = pd.read_csv("data/processed/market_master_2023_full_year.csv")
df_2023["startTime"] = pd.to_datetime(df_2023["startTime"])
df_2023["month"] = df_2023["startTime"].dt.month
df_2023["spike_flag"] = (df_2023["systemSellPrice"] >= 250).astype(int)
df_2023["regime_group"] = "other"
df_2023.loc[df_2023["month"].isin([1, 2, 3]), "regime_group"] = "q1_stress"
df_2023.loc[df_2023["month"].isin([4, 5, 6, 7, 8, 9]), "regime_group"] = "apr_sep_quiet"
df_2023.loc[df_2023["month"].isin([10, 11]), "regime_group"] = "oct_nov_transition"
df_2023.loc[df_2023["month"].isin([12]), "regime_group"] = "dec_windy"

table_2023 = df_2023.groupby("regime_group").agg(
    rows=("startTime", "count"),
    spikes=("spike_flag", "sum"),
    spike_probability=("spike_flag", "mean"),
    avg_price=("systemSellPrice", "mean"),
    avg_imbalance=("netImbalanceVolume", "mean"),
    avg_wind=("wind_gen", "mean"),
    avg_gas=("gas_gen", "mean")
).reset_index()
table_2023["year"] = 2023

# 2024
df_2024 = pd.read_csv("data/processed/market_master_2024_full_year.csv")
df_2024["startTime"] = pd.to_datetime(df_2024["startTime"])
df_2024["month"] = df_2024["startTime"].dt.month
df_2024["spike_flag"] = (df_2024["systemSellPrice"] >= 250).astype(int)
df_2024["regime_group"] = "other"
df_2024.loc[df_2024["month"].isin([1, 2, 3]), "regime_group"] = "q1_quiet"
df_2024.loc[df_2024["month"].isin([4, 5, 6, 7, 8, 9]), "regime_group"] = "apr_sep_quiet"
df_2024.loc[df_2024["month"].isin([10, 11]), "regime_group"] = "oct_nov_transition"
df_2024.loc[df_2024["month"].isin([12]), "regime_group"] = "dec_stress"

table_2024 = df_2024.groupby("regime_group").agg(
    rows=("startTime", "count"),
    spikes=("spike_flag", "sum"),
    spike_probability=("spike_flag", "mean"),
    avg_price=("systemSellPrice", "mean"),
    avg_imbalance=("netImbalanceVolume", "mean"),
    avg_wind=("wind_gen", "mean"),
    avg_gas=("gas_gen", "mean")
).reset_index()
table_2024["year"] = 2024

comparison = pd.concat([table_2023, table_2024], ignore_index=True)
comparison = comparison[[
    "year", "regime_group", "rows", "spikes", "spike_probability",
    "avg_price", "avg_imbalance", "avg_wind", "avg_gas"
]].round(4)

comparison.to_csv("outputs/tables/2023_2024_regime_fingerprint_comparison.csv", index=False)

print("\n2023 VS 2024 REGIME FINGERPRINT COMPARISON")
print(comparison)
print("\nSaved: outputs/tables/2023_2024_regime_fingerprint_comparison.csv")