import pandas as pd


def process_fuel_data(df):
    df_pivot = df.pivot_table(
        index="startTime",
        columns="fuelType",
        values="generation",
        aggfunc="sum"
    )

    df_pivot = df_pivot.reset_index()
    df_pivot["startTime"] = pd.to_datetime(df_pivot["startTime"])
    df_pivot = df_pivot.sort_values("startTime")

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

    df_clean = df_clean[
        (df_clean["startTime"] >= "2023-01-01") &
        (df_clean["startTime"] < "2023-02-01")
    ].copy()

    return df_clean


def process_price_data(df_price):
    df_price["startTime"] = pd.to_datetime(df_price["startTime"])

    df_price_clean = df_price[
        [
            "startTime",
            "systemSellPrice",
            "systemBuyPrice",
            "netImbalanceVolume",
        ]
    ].copy()

    return df_price_clean


def merge_data(df_clean, df_price_clean):
    df_master = pd.merge(
        df_clean,
        df_price_clean,
        on="startTime",
        how="inner"
    )
    return df_master