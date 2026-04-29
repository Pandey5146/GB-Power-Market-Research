import pandas as pd
from pathlib import Path


INPUT_FILE = Path("outputs/tables/2023_2024_asset_event_price_impact.csv")
OUTPUT_FILE = Path("outputs/tables/2023_2024_price_event_case_studies.csv")


def summarise_external_events(group):
    event_parts = []

    for _, row in group.iterrows():
        external_type = row["external_event_type"]
        unavailable = row["total_unavailable_capacity_mw"]
        assets = row["key_assets"]
        association = row["association_assessment"]

        event_parts.append(
            f"{external_type}: {unavailable:.1f} MW reported unavailable across {assets} "
            f"({association})"
        )

    return " | ".join(event_parts)


def build_case_interpretation(row):
    year = int(row["year"])
    max_price = row["max_price"]
    wind = row["avg_wind"]
    gas = row["avg_gas"]
    imbalance = row["avg_imbalance"]
    interconnectors = row["avg_interconnectors"]
    date = row["date"]
    regime = row["regime_group"]

    if year == 2023 and date == "2023-03-07":
        return (
            f"The {date} event was a compound scarcity event. Price reached £{max_price:.2f}/MWh "
            f"while wind was low at {wind:.1f} MW, gas generation was high at {gas:.1f} MW, "
            f"imbalance was strongly positive at {imbalance:.1f}, and interconnector flow was relatively low "
            f"at {interconnectors:.1f} MW. REMIT evidence shows contemporaneous interconnector and thermal "
            f"generation availability reductions. This supports a high-confidence association between the price "
            f"event and wider scarcity/availability stress, but not causality from any single unit."
        )

    if year == 2024 and date == "2024-10-14":
        return (
            f"The {date} event occurred in the 2024 Oct-Nov transition regime. Price reached £{max_price:.2f}/MWh "
            f"with very low wind at {wind:.1f} MW, high gas generation at {gas:.1f} MW, strongly positive imbalance "
            f"at {imbalance:.1f}, and relatively low interconnector support at {interconnectors:.1f} MW. "
            f"REMIT evidence shows thermal and wind availability reductions around the event window. "
            f"This supports interpreting the event as an imbalance-amplified scarcity episode."
        )

    if year == 2024 and date == "2024-12-11":
        return (
            f"The {date} event occurred in the December 2024 stress regime. Price reached £{max_price:.2f}/MWh "
            f"while wind was very low at {wind:.1f} MW and gas generation was extremely high at {gas:.1f} MW. "
            f"Unlike the October event, imbalance was not the dominant trigger at {imbalance:.1f}. "
            f"REMIT records show generation, wind, flexibility and interconnector-related capacity events in the wider window. "
            f"This supports the interpretation that the event was mainly a physical scarcity / low-wind high-gas episode."
        )

    if year == 2024 and date == "2024-12-12":
        return (
            f"The {date} event occurred during the December 2024 stress regime. Price reached £{max_price:.2f}/MWh "
            f"with wind still very low at {wind:.1f} MW and gas generation very high at {gas:.1f} MW. "
            f"REMIT evidence shows interconnector restrictions and generation availability reductions during the event window. "
            f"This supports interpreting the event as a low-wind, high-thermal, reduced-flexibility scarcity episode."
        )

    return (
        f"Price reached £{max_price:.2f}/MWh during {regime}. The event coincided with stressed internal "
        f"market conditions and REMIT-reported external capacity events."
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("Input impact table is empty.")

    # Convert event time
    df["price_event_start"] = pd.to_datetime(df["price_event_start"], errors="coerce", utc=True)
    df["date"] = df["price_event_start"].dt.strftime("%Y-%m-%d")

    # Focus on the 4 main case-study dates
    case_dates = [
        "2023-03-07",
        "2024-10-14",
        "2024-12-11",
        "2024-12-12",
    ]

    df = df[df["date"].isin(case_dates)].copy()

    if df.empty:
        raise ValueError("No rows found for the selected case-study dates.")

    grouped = (
        df.groupby(["price_event_year", "date", "price_event_regime_group"], dropna=False)
        .agg(
            max_price=("price_event_max_price", "max"),
            avg_imbalance=("price_event_avg_imbalance", "mean"),
            avg_wind=("price_event_avg_wind", "mean"),
            avg_gas=("price_event_avg_gas", "mean"),
            avg_interconnectors=("price_event_avg_interconnectors", "mean"),
            time_bands=("price_event_time_band", lambda x: "; ".join(sorted(set(x.dropna().astype(str))))),
            external_events_found=("external_event_type", lambda x: "; ".join(sorted(set(x.dropna().astype(str))))),
            highest_association=("association_assessment", lambda x: "high_confidence_association" if "high_confidence_association" in set(x) else "; ".join(sorted(set(x.dropna().astype(str))))),
        )
        .reset_index()
    )

    grouped = grouped.rename(
        columns={
            "price_event_year": "year",
            "price_event_regime_group": "regime_group",
        }
    )

    # Build detailed external event summary
    external_summary = (
        df.groupby(["price_event_year", "date"], dropna=False)
        .apply(summarise_external_events)
        .reset_index(name="external_event_summary")
    )

    external_summary = external_summary.rename(columns={"price_event_year": "year"})

    grouped = grouped.merge(external_summary, on=["year", "date"], how="left")

    grouped["case_id"] = [
        f"Case {i+1}" for i in range(len(grouped))
    ]

    grouped["price_event"] = grouped.apply(
        lambda row: f"{row['date']} price event reaching £{row['max_price']:.2f}/MWh",
        axis=1,
    )

    grouped["internal_market_state"] = grouped.apply(
        lambda row: (
            f"avg_imbalance={row['avg_imbalance']:.1f}; "
            f"avg_wind={row['avg_wind']:.1f} MW; "
            f"avg_gas={row['avg_gas']:.1f} MW; "
            f"avg_interconnectors={row['avg_interconnectors']:.1f} MW; "
            f"time_band={row['time_bands']}; "
            f"regime={row['regime_group']}"
        ),
        axis=1,
    )

    grouped["interpretation_for_paper"] = grouped.apply(build_case_interpretation, axis=1)

    final_cols = [
        "case_id",
        "date",
        "year",
        "price_event",
        "max_price",
        "regime_group",
        "time_bands",
        "internal_market_state",
        "external_events_found",
        "external_event_summary",
        "highest_association",
        "interpretation_for_paper",
    ]

    final_df = grouped[final_cols].copy()

    final_df = final_df.sort_values(["year", "date"]).reset_index(drop=True)

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\nPRICE EVENT CASE STUDIES")
    print(final_df)

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()