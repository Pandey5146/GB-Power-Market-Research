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

OUTPUT_FILE = OUTPUT_DIR / "2023_2024_threshold_robustness_summary.csv"


# ==============================
# HELPER FUNCTIONS
# ==============================

def find_column(df, possible_names, required=True):
    """
    Finds a column from a list of possible names.
    This keeps the script robust if column names differ slightly.
    """
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


def create_gas_column(df):
    """
    Creates a gas column.

    Preferred:
    - use existing gas column if available

    Otherwise:
    - sum CCGT and OCGT if both/one exist
    """
    gas_col = find_column(df, ["gas", "GAS", "gas_generation", "avg_gas", "gas_gen"], required=False)

    if gas_col:
        df["gas_generation"] = df[gas_col]
        return df

    ccgt_col = find_column(df, ["CCGT", "ccgt"], required=False)
    ocgt_col = find_column(df, ["OCGT", "ocgt"], required=False)

    if ccgt_col or ocgt_col:
        df["gas_generation"] = 0

        if ccgt_col:
            df["gas_generation"] += df[ccgt_col]

        if ocgt_col:
            df["gas_generation"] += df[ocgt_col]

        return df

    raise ValueError(
        "Could not create gas_generation column. "
        "Expected either gas/GAS or CCGT/OCGT columns."
    )


def create_interconnector_column(df):
    """
    Creates an aggregate interconnector column.

    Preferred:
    - use existing interconnectors column if available

    Otherwise:
    - sum common GB interconnector fuel-type columns if available
    """
    interconnector_col = find_column(
        df,
        [
            "interconnectors",
            "INTERCONNECTORS",
            "interconnector",
            "avg_interconnectors",
        ],
        required=False,
    )

    if interconnector_col:
        df["interconnectors_total"] = df[interconnector_col]
        return df

    possible_link_cols = [
        "IFA",
        "IFA2",
        "BritNed",
        "BRITNED",
        "Nemo",
        "NEMO",
        "NSL",
        "EWIC",
        "Moyle",
        "MOYLE",
        "ElecLink",
        "ELECLINK",
        "Viking",
        "VIKING",
        "NORTH SEA LINK",
    ]

    available_links = [col for col in possible_link_cols if col in df.columns]

    if available_links:
        df["interconnectors_total"] = df[available_links].sum(axis=1)
        return df

    raise ValueError(
        "Could not create interconnectors_total column. "
        "Expected interconnectors/INTERCONNECTORS or individual interconnector columns."
    )


def prepare_dataset(df):
    """
    Standardises the required columns for threshold robustness analysis.
    """
    price_col = find_column(
        df,
        ["systemSellPrice", "system_sell_price", "price", "ssp"],
        required=True,
    )

    imbalance_col = find_column(
        df,
        [
            "imbalance",
            "netImbalanceVolume",
            "net_imbalance_volume",
            "niv",
            "NIV",
            "avg_imbalance",
        ],
        required=True,
    )

    wind_col = find_column(
        df,
        ["wind", "WIND", "wind_generation", "avg_wind", "wind_gen"],
        required=True,
    )

    time_col = find_column(
        df,
        ["startTime", "start_time", "settlementStartTime", "datetime", "timestamp"],
        required=True,
    )

    df = df.copy()

    df["price"] = pd.to_numeric(df[price_col], errors="coerce")
    df["imbalance"] = pd.to_numeric(df[imbalance_col], errors="coerce")
    df["wind_generation"] = pd.to_numeric(df[wind_col], errors="coerce")

    df = create_gas_column(df)
    df = create_interconnector_column(df)

    df["gas_generation"] = pd.to_numeric(df["gas_generation"], errors="coerce")
    df["interconnectors_total"] = pd.to_numeric(df["interconnectors_total"], errors="coerce")

    df["timestamp"] = pd.to_datetime(df[time_col], errors="coerce")
    df["hour"] = df["timestamp"].dt.hour

    # Same evening peak logic used earlier
    df["is_evening_peak"] = df["hour"].between(16, 19, inclusive="both")

    return df


def threshold_robustness_for_year(df, year, thresholds):
    """
    Builds threshold robustness summary for one year.
    """
    results = []
    total_rows = len(df)

    for threshold in thresholds:
        subset = df[df["price"] >= threshold].copy()

        if len(subset) == 0:
            results.append(
                {
                    "year": year,
                    "threshold": threshold,
                    "periods_above_threshold": 0,
                    "probability_above_threshold": 0,
                    "avg_price": None,
                    "avg_imbalance": None,
                    "avg_wind": None,
                    "avg_gas": None,
                    "avg_interconnectors": None,
                    "share_imbalance_gt_150": None,
                    "share_wind_lt_8000": None,
                    "share_gas_gt_15000": None,
                    "share_evening_peak": None,
                }
            )
            continue

        results.append(
            {
                "year": year,
                "threshold": threshold,
                "periods_above_threshold": len(subset),
                "probability_above_threshold": len(subset) / total_rows,
                "avg_price": subset["price"].mean(),
                "avg_imbalance": subset["imbalance"].mean(),
                "avg_wind": subset["wind_generation"].mean(),
                "avg_gas": subset["gas_generation"].mean(),
                "avg_interconnectors": subset["interconnectors_total"].mean(),
                "share_imbalance_gt_150": (subset["imbalance"] > 150).mean(),
                "share_wind_lt_8000": (subset["wind_generation"] < 8000).mean(),
                "share_gas_gt_15000": (subset["gas_generation"] > 15000).mean(),
                "share_evening_peak": subset["is_evening_peak"].mean(),
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

        df = prepare_dataset(df)

        result = threshold_robustness_for_year(df, year, thresholds)
        all_results.append(result)

    final_table = pd.concat(all_results, ignore_index=True)

    # Round for clean paper-ready table
    final_table = final_table.round(
        {
            "probability_above_threshold": 4,
            "avg_price": 4,
            "avg_imbalance": 4,
            "avg_wind": 4,
            "avg_gas": 4,
            "avg_interconnectors": 4,
            "share_imbalance_gt_150": 4,
            "share_wind_lt_8000": 4,
            "share_gas_gt_15000": 4,
            "share_evening_peak": 4,
        }
    )

    final_table.to_csv(OUTPUT_FILE, index=False)

    print("\nTHRESHOLD ROBUSTNESS SUMMARY")
    print(final_table)

    print(f"\nSaved table to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()