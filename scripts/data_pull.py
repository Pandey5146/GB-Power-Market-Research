import requests
import pandas as pd

url = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?publishDateTimeFrom=2023-01-01&publishDateTimeTo=2023-01-03"

response = requests.get(url)
data = response.json()

df = pd.json_normalize(data["data"])

print(df.head())
print(df.columns)
print(df.shape)
print(df["fuelType"].unique())
print(df["fuelType"].nunique())

# Pivot table (long → wide)
df_pivot = df.pivot_table(
    index="startTime",
    columns="fuelType",
    values="generation",
    aggfunc="sum"
)

print(df_pivot.head())

df_pivot = df_pivot.reset_index()

df_pivot["startTime"] = pd.to_datetime(df_pivot["startTime"])

df_pivot = df_pivot.sort_values("startTime")

print(df_pivot.head())

# Create grouped fuel columns
df_pivot["gas_gen"] = df_pivot["CCGT"] + df_pivot["OCGT"]
df_pivot["wind_gen"] = df_pivot["WIND"]
df_pivot["nuclear_gen"] = df_pivot["NUCLEAR"]
df_pivot["biomass_gen"] = df_pivot["BIOMASS"]
df_pivot["hydro_gen"] = df_pivot["NPSHYD"]
df_pivot["pumped_storage"] = df_pivot["PS"]
df_pivot["coal_gen"] = df_pivot["COAL"]
df_pivot["oil_gen"] = df_pivot["OIL"]
df_pivot["other_gen"] = df_pivot["OTHER"]

df_pivot["interconnectors"] = (
    df_pivot["INTELEC"]
    + df_pivot["INTEW"]
    + df_pivot["INTFR"]
    + df_pivot["INTIFA2"]
    + df_pivot["INTIRL"]
    + df_pivot["INTNED"]
    + df_pivot["INTNEM"]
    + df_pivot["INTNSL"]
)

# Keep only the research columns for now
df_clean = df_pivot[
    [
        "startTime",
        "gas_gen",
        "wind_gen",
        "nuclear_gen",
        "biomass_gen",
        "hydro_gen",
        "pumped_storage",
        "coal_gen",
        "oil_gen",
        "other_gen",
        "interconnectors",
    ]
].copy()

print(df_clean.head())
print(df_clean.columns)

# Filter required date range only
df_clean = df_clean[
    (df_clean["startTime"] >= "2023-01-01") &
    (df_clean["startTime"] < "2023-01-04")
].copy()

print(df_clean.head())
print(df_clean.tail())
print(df_clean.shape)

print(df_clean.isna().sum())
df_clean.to_csv("data/processed/fuel_mix_2023_sample.csv", index=False)

# ==============================
# STEP 4.1 — SYSTEM PRICE DATA
# ==============================

url_price = "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2023-01-01"

response_price = requests.get(url_price)
print(response_price.status_code)

data_price = response_price.json()
print(data_price)

# only do this after you confirm the JSON contains a data field
# df_price = pd.json_normalize(data_price["data"])
# print(df_price.head())
# print(df_price.columns)

df_price = pd.json_normalize(data_price["data"])

print(df_price.head())
print(df_price.columns)
print(df_price.shape)

df_price["startTime"] = pd.to_datetime(df_price["startTime"])

df_price_clean = df_price[
    [
        "startTime",
        "systemSellPrice",
        "systemBuyPrice",
        "netImbalanceVolume",
    ]
].copy()

print(df_price_clean.head())
print(df_price_clean.shape)
print(df_price_clean.isna().sum())

df_master = pd.merge(
    df_clean,
    df_price_clean,
    on="startTime",
    how="inner"
)

print(df_master.head())
print(df_master.shape)
print(df_master.isna().sum())

df_master.to_csv("data/processed/market_master_sample.csv", index=False)

print(df_master.describe())