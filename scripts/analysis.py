import pandas as pd
from pathlib import Path


# ==============================
# FILE PATHS
# ==============================

DATA_PATHS = {
    2023: Path("data/processed/market_master_2023_full_year.csv"),
    2024: Path("data/processed/market_master_2024_full_year.csv"),
}

OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "2023_2024_threshold_by_regime_group.csv"


# ==============================
# HELPER FUNCTIONS
# ==============================

def find_column(df, possible_names, required=True):
    lower_map = {col.lower(): col for col in df.columns}

    for name in possible_names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]

    if required:
        raise ValueError(
            f"Could not find any of these columns: {possible_names}\n"
            f"Available columns are: {list(df.columns)}"
        )

    return None


def assign_regime_group(row):
    """
    Assigns the paper's existing regime groups.

    2023:
    - q1_stress: Jan-Mar
    - apr_sep_quiet: Apr-Sep
    - oct_nov_transition: Oct-Nov
    - dec_windy: Dec

    2024:
    - q1_quiet: Jan-Mar
    - apr_sep_quiet: Apr-Sep
    - oct_nov_transition: Oct-Nov
    - dec_stress: Dec
    """
    year = row["year"]
    month = row["month"]

    if year == 2023:
        if month in [1, 2, 3]:
            return "q1_stress"
        elif month in [4, 5, 6, 7, 8, 9]:
            return "apr_sep_quiet"
        elif month in [10, 11]:
            return "oct_nov_transition"
        elif month == 12:
            return "dec_windy"

    elif year == 2024:
        if month in [1, 2, 3]:
            return "q1_quiet"
        elif month in [4, 5, 6, 7, 8, 9]:
            return "apr_sep_quiet"
        elif month in [10, 11]:
            return "oct_nov_transition"
        elif month == 12:
            return "dec_stress"

    return "unknown"


def prepare_dataset(df, year):
    price_col = find_column(
        df,
        ["systemSellPrice", "system_sell_price", "price", "ssp"],
        required=True,
    )

    imbalance_col = find_column(
        df,
        ["netImbalanceVolume", "imbalance", "net_imbalance_volume", "niv", "NIV"],
        required=True,
    )

    wind_col = find_column(
        df,
        ["wind_gen", "wind", "WIND", "wind_generation", "avg_wind"],
        required=True,
    )

    gas_col = find_column(
        df,
        ["gas_gen", "gas", "GAS", "gas_generation", "avg_gas"],
        required=True,
    )

    interconnector_col = find_column(
        df,
        ["interconnectors", "INTERCONNECTORS", "interconnector", "avg_interconnectors"],
        required=True,
    )

    time_col = find_column(
        df,
        ["startTime", "start_time", "settlementStartTime", "datetime", "timestamp"],
        required=True,
    )

    df = df.copy()

    df["year"] = year
    df["price"] = pd.to_numeric(df[price_col], errors="coerce")
    df["imbalance"] = pd.to_numeric(df[imbalance_col], errors="coerce")
    df["wind_generation"] = pd.to_numeric(df[wind_col], errors="coerce")
    df["gas_generation"] = pd.to_numeric(df[gas_col], errors="coerce")
    df["interconnectors_total"] = pd.to_numeric(df[interconnector_col], errors="coerce")

    df["timestamp"] = pd.to_datetime(df[time_col], errors="coerce")
    df["month"] = df["timestamp"].dt.month

    df["regime_group"] = df.apply(assign_regime_group, axis=1)

    return df


def threshold_by_regime_group_for_year(df, year, thresholds):
    """
    For each regime group and threshold:
    - count periods above threshold
    - calculate probability within regime group
    - calculate average drivers during threshold periods
    """
    results = []

    if year == 2023:
        regime_order = [
            "q1_stress",
            "apr_sep_quiet",
            "oct_nov_transition",
            "dec_windy",
        ]
    else:
        regime_order = [
            "q1_quiet",
            "apr_sep_quiet",
            "oct_nov_transition",
            "dec_stress",
        ]

    for regime_group in regime_order:
        regime_df = df[df["regime_group"] == regime_group].copy()
        rows_in_regime = len(regime_df)

        for threshold in thresholds:
            above_df = regime_df[regime_df["price"] >= threshold].copy()
            periods_above_threshold = len(above_df)

            if rows_in_regime == 0:
                probability_above_threshold = 0
            else:
                probability_above_threshold = periods_above_threshold / rows_in_regime

            if periods_above_threshold == 0:
                results.append(
                    {
                        "year": year,
                        "regime_group": regime_group,
                        "threshold": threshold,
                        "rows_in_regime": rows_in_regime,
                        "periods_above_threshold": 0,
                        "probability_above_threshold": 0,
                        "avg_price": None,
                        "avg_imbalance": None,
                        "avg_wind": None,
                        "avg_gas": None,
                        "avg_interconnectors": None,
                    }
                )
            else:
                results.append(
                    {
                        "year": year,
                        "regime_group": regime_group,
                        "threshold": threshold,
                        "rows_in_regime": rows_in_regime,
                        "periods_above_threshold": periods_above_threshold,
                        "probability_above_threshold": probability_above_threshold,
                        "avg_price": above_df["price"].mean(),
                        "avg_imbalance": above_df["imbalance"].mean(),
                        "avg_wind": above_df["wind_generation"].mean(),
                        "avg_gas": above_df["gas_generation"].mean(),
                        "avg_interconnectors": above_df["interconnectors_total"].mean(),
                    }
                )

    return pd.DataFrame(results)


# ==============================
# MAIN ANALYSIS
# ==============================

def main():
    thresholds = [100, 150, 200, 250, 300]

    all_results = []

    for year, path in DATA_PATHS.items():
        print(f"\nLoading {year}: {path}")

        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

        df = pd.read_csv(path)
        print(f"{year} rows loaded: {len(df):,}")

        df = prepare_dataset(df, year)

        result = threshold_by_regime_group_for_year(df, year, thresholds)
        all_results.append(result)

    final_table = pd.concat(all_results, ignore_index=True)

    final_table = final_table.round(
        {
            "probability_above_threshold": 4,
            "avg_price": 4,
            "avg_imbalance": 4,
            "avg_wind": 4,
            "avg_gas": 4,
            "avg_interconnectors": 4,
        }
    )

    final_table.to_csv(OUTPUT_FILE, index=False)

    print("\nTHRESHOLD BY REGIME-GROUP ANALYSIS")
    print(final_table)

    print(f"\nSaved table to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()