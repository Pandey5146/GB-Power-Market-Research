import pandas as pd
from pathlib import Path


INPUT_FILE = Path("outputs/tables/2023_2024_filtered_remit_events_near_price_events.csv")
OUTPUT_FILE = Path("outputs/tables/2023_2024_asset_event_price_impact.csv")


def classify_association(row):
    """
    Careful, non-causal association classification.
    """
    max_price = row["price_event_max_price"]
    wind = row["price_event_avg_wind"]
    gas = row["price_event_avg_gas"]
    imbalance = row["price_event_avg_imbalance"]
    interconnectors = row["price_event_avg_interconnectors"]
    external_type = row["external_event_type"]
    total_unavailable = row["total_unavailable_capacity_mw"]

    scarcity_signals = 0

    if pd.notna(wind) and wind < 3000:
        scarcity_signals += 1
    if pd.notna(gas) and gas > 20000:
        scarcity_signals += 1
    if pd.notna(imbalance) and imbalance > 150:
        scarcity_signals += 1
    if pd.notna(interconnectors) and interconnectors < 3000:
        scarcity_signals += 1
    if pd.notna(max_price) and max_price >= 300:
        scarcity_signals += 1
    if pd.notna(total_unavailable) and total_unavailable >= 500:
        scarcity_signals += 1

    if external_type == "interconnector_unavailability" and scarcity_signals >= 4:
        return "high_confidence_association"

    if external_type == "thermal_gas_unavailability" and scarcity_signals >= 4:
        return "high_confidence_association"

    if scarcity_signals >= 3:
        return "medium_confidence_association"

    if scarcity_signals >= 2:
        return "low_to_medium_confidence_association"

    return "low_confidence_or_context_only"


def build_research_interpretation(row):
    external_type = row["external_event_type"]
    price = row["price_event_max_price"]
    wind = row["price_event_avg_wind"]
    gas = row["price_event_avg_gas"]
    imbalance = row["price_event_avg_imbalance"]
    interconnectors = row["price_event_avg_interconnectors"]
    assets = row["key_assets"]
    unavailable = row["total_unavailable_capacity_mw"]

    base = (
        f"Price event reached £{price:.2f}/MWh with average wind {wind:.1f} MW, "
        f"gas {gas:.1f} MW, imbalance {imbalance:.1f}, and interconnectors {interconnectors:.1f} MW. "
    )

    if external_type == "interconnector_unavailability":
        return (
            base
            + f"REMIT records show interconnector unavailability involving {assets}, "
            + f"with total reported unavailable capacity around {unavailable:.1f} MW. "
            + "This suggests the price event coincided with reduced cross-border flexibility under stressed system conditions."
        )

    if external_type == "thermal_gas_unavailability":
        return (
            base
            + f"REMIT records show thermal/gas availability reductions involving {assets}, "
            + f"with total reported unavailable capacity around {unavailable:.1f} MW. "
            + "This suggests the price event coincided with reduced dispatchable capacity in an already stressed system."
        )

    if external_type == "wind_unavailability":
        return (
            base
            + f"REMIT records show wind unit unavailability involving {assets}, "
            + f"with reported unavailable capacity around {unavailable:.1f} MW. "
            + "This may have contributed to the low-wind scarcity background, but should not be treated as a single direct cause."
        )

    return (
        base
        + f"REMIT records show external capacity events involving {assets}. "
        + "This should be treated as contextual evidence rather than direct causal proof."
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("Input REMIT file is empty.")

    # Convert capacities and price/system fields
    numeric_cols = [
        "price_event_max_price",
        "price_event_avg_imbalance",
        "price_event_avg_wind",
        "price_event_avg_gas",
        "price_event_avg_interconnectors",
        "remit_unavailableCapacity",
        "remit_normalCapacity",
        "remit_availableCapacity",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Keep only rows with a positive unavailable capacity
    df = df[df["remit_unavailableCapacity"].fillna(0) > 0].copy()

    # Drop clearly irrelevant rows where event dates are impossible or missing
    df["remit_eventStartTime"] = pd.to_datetime(df["remit_eventStartTime"], errors="coerce", utc=True)
    df["remit_eventEndTime"] = pd.to_datetime(df["remit_eventEndTime"], errors="coerce", utc=True)
    df["price_event_start"] = pd.to_datetime(df["price_event_start"], errors="coerce", utc=True)
    df["price_event_end"] = pd.to_datetime(df["price_event_end"], errors="coerce", utc=True)

    # Keep REMIT events that overlap the price event window +/- the query already selected
    # This protects against very stale weird rows.
    df = df[
        (df["remit_eventStartTime"].notna()) &
        (df["remit_eventEndTime"].notna()) &
        (df["remit_eventStartTime"] <= df["price_event_end"] + pd.Timedelta(hours=2)) &
        (df["remit_eventEndTime"] >= df["price_event_start"] - pd.Timedelta(hours=2))
    ].copy()

    # Prefer Active/Inactive over Dismissed, but do not remove Dismissed entirely yet.
    # Dismissed can still reflect a revised event; later we can refine.
    group_cols = [
        "price_event_id",
        "price_event_type",
        "price_event_year",
        "price_event_start",
        "price_event_end",
        "price_event_max_price",
        "price_event_avg_imbalance",
        "price_event_avg_wind",
        "price_event_avg_gas",
        "price_event_avg_interconnectors",
        "price_event_time_band",
        "price_event_regime_group",
        "simplified_external_event_type",
    ]

    grouped = (
        df.groupby(group_cols, dropna=False)
        .agg(
            active_event_count=("remit_message_id", "count"),
            total_unavailable_capacity_mw=("remit_unavailableCapacity", "sum"),
            largest_unavailable_capacity_mw=("remit_unavailableCapacity", "max"),
            key_assets=("remit_affectedUnit", lambda x: "; ".join(sorted(set(x.dropna().astype(str)))[:10])),
            fuel_types=("remit_fuelType", lambda x: "; ".join(sorted(set(x.dropna().astype(str)))[:10])),
            event_statuses=("remit_eventStatus", lambda x: "; ".join(sorted(set(x.dropna().astype(str)))[:10])),
            event_causes=("remit_cause", lambda x: "; ".join(sorted(set(x.dropna().astype(str)))[:10])),
            earliest_external_event_start=("remit_eventStartTime", "min"),
            latest_external_event_end=("remit_eventEndTime", "max"),
        )
        .reset_index()
    )

    grouped = grouped.rename(columns={
        "simplified_external_event_type": "external_event_type"
    })

    grouped["association_assessment"] = grouped.apply(classify_association, axis=1)
    grouped["research_interpretation"] = grouped.apply(build_research_interpretation, axis=1)

    grouped = grouped.sort_values(
        [
            "price_event_year",
            "price_event_start",
            "association_assessment",
            "total_unavailable_capacity_mw",
        ],
        ascending=[True, True, True, False]
    ).reset_index(drop=True)

    grouped.to_csv(OUTPUT_FILE, index=False)

    print("\nASSET EVENT PRICE IMPACT TABLE")
    print(grouped)

    print(f"\nSaved to: {OUTPUT_FILE}")

    print("\nSUMMARY")
    summary = (
        grouped
        .groupby(["price_event_year", "external_event_type", "association_assessment"])
        .agg(
            rows=("price_event_id", "count"),
            max_price=("price_event_max_price", "max"),
            max_total_unavailable_capacity=("total_unavailable_capacity_mw", "max"),
        )
        .reset_index()
    )

    print(summary)


if __name__ == "__main__":
    main()