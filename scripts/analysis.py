import pandas as pd
from pathlib import Path


DATA_FILE = Path("data/processed/market_master_2025_full_year.csv")

OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "2025_price_event_candidates.csv"
SUMMARY_FILE = OUTPUT_DIR / "2025_price_event_candidates_summary.csv"


def assign_time_band(hour):
    if 0 <= hour <= 5:
        return "night"
    elif 6 <= hour <= 9:
        return "morning_ramp"
    elif 10 <= hour <= 13:
        return "midday"
    elif 14 <= hour <= 15:
        return "afternoon"
    elif 16 <= hour <= 19:
        return "evening_peak"
    else:
        return "late_evening"


def assign_2025_regime_group(month):
    if month == 1:
        return "jan_spike_stress"
    elif month in [2, 3]:
        return "feb_mar_broad_stress"
    elif month in [4, 5]:
        return "apr_may_surplus_shift"
    elif month == 6:
        return "jun_mixed_tail"
    elif month in [7, 8, 9]:
        return "jul_sep_surplus"
    elif month == 10:
        return "oct_mixed_transition"
    elif month in [11, 12]:
        return "nov_dec_quiet"
    else:
        return "unknown"


def assign_likely_internal_driver(row):
    drivers = []

    if row["avg_gas"] > 20000:
        drivers.append("very_high_gas")
    elif row["avg_gas"] > 15000:
        drivers.append("high_gas")

    if row["avg_wind"] < 3000:
        drivers.append("very_low_wind")
    elif row["avg_wind"] < 8000:
        drivers.append("low_wind")
    elif row["avg_wind"] > 10000:
        drivers.append("high_wind")

    if row["avg_imbalance"] > 300:
        drivers.append("very_positive_imbalance")
    elif row["avg_imbalance"] > 150:
        drivers.append("positive_imbalance")
    elif row["avg_imbalance"] < -150:
        drivers.append("negative_imbalance")

    if row["avg_interconnectors"] < 2500:
        drivers.append("lower_interconnector_support")
    elif row["avg_interconnectors"] > 4500:
        drivers.append("higher_interconnector_support")

    if not drivers:
        return "mixed_or_unclear_internal_driver"

    return "+".join(drivers)


def build_cluster_events(df, condition_col, event_type):
    temp = df[df[condition_col]].copy()

    if temp.empty:
        return []

    temp = temp.sort_values("startTime").copy()

    # New cluster starts if gap is more than 30 minutes
    temp["time_gap"] = temp["startTime"].diff()
    temp["new_cluster"] = temp["time_gap"].isna() | (temp["time_gap"] > pd.Timedelta(minutes=30))
    temp["cluster_id"] = temp["new_cluster"].cumsum()

    events = []

    for cluster_id, group in temp.groupby("cluster_id"):
        group = group.sort_values("startTime")

        max_price_idx = group["systemSellPrice"].idxmax()
        max_row = group.loc[max_price_idx]

        min_price_idx = group["systemSellPrice"].idxmin()
        min_row = group.loc[min_price_idx]

        start_time = group["startTime"].min()
        end_time = group["startTime"].max()

        duration_hours = ((end_time - start_time).total_seconds() / 3600) + 0.5

        event = {
            "year": 2025,
            "event_id": f"2025_{event_type}_{cluster_id}",
            "event_type": event_type,
            "start_time": start_time,
            "end_time": end_time,
            "duration_hours": duration_hours,
            "periods_in_event": len(group),

            "max_price": group["systemSellPrice"].max(),
            "min_price": group["systemSellPrice"].min(),
            "avg_price": group["systemSellPrice"].mean(),

            "avg_imbalance": group["netImbalanceVolume"].mean(),
            "avg_wind": group["wind_gen"].mean(),
            "avg_gas": group["gas_gen"].mean(),
            "avg_interconnectors": group["interconnectors"].mean(),

            "time_of_max_price": max_row["startTime"],
            "time_band_at_max_price": max_row["time_band"],
            "regime_group": max_row["regime_group"],

            "price_before_event": None,
            "price_after_event": None,
            "price_change_from_previous": None,

            "research_note": "",
        }

        event["likely_internal_driver"] = assign_likely_internal_driver(event)

        if event_type == "negative_price_cluster":
            event["research_note"] = (
                "Candidate negative-price event. Check high wind, low gas, negative imbalance, "
                "and whether surplus conditions were reinforced by system context."
            )
        elif event_type == "near_spike_cluster":
            event["research_note"] = (
                "Candidate near-spike event. Useful for studying why stressed conditions did not fully "
                "convert into £250+/£300+ spike realization."
            )
        elif event_type == "positive_spike_cluster":
            event["research_note"] = (
                "Candidate positive spike event. Check low wind, high gas, positive imbalance, "
                "evening timing and external availability events."
            )
        elif event_type == "extreme_spike_cluster":
            event["research_note"] = (
                "Candidate extreme spike event. Highest priority for REMIT/external availability checks."
            )

        events.append(event)

    return events


def build_jump_events(df, jump_threshold=100):
    temp = df.sort_values("startTime").copy()

    temp["previous_price"] = temp["systemSellPrice"].shift(1)
    temp["previous_time"] = temp["startTime"].shift(1)
    temp["price_change"] = temp["systemSellPrice"] - temp["previous_price"]

    # Only compare adjacent settlement periods
    temp["time_gap"] = temp["startTime"] - temp["previous_time"]
    temp = temp[temp["time_gap"] == pd.Timedelta(minutes=30)].copy()

    jump_rows = temp[temp["price_change"] >= jump_threshold].copy()
    reversal_rows = temp[temp["price_change"] <= -jump_threshold].copy()

    events = []

    for idx, row in jump_rows.iterrows():
        event = {
            "year": 2025,
            "event_id": f"2025_large_upward_jump_{idx}",
            "event_type": "large_upward_jump",
            "start_time": row["previous_time"],
            "end_time": row["startTime"],
            "duration_hours": 0.5,
            "periods_in_event": 1,

            "max_price": row["systemSellPrice"],
            "min_price": row["systemSellPrice"],
            "avg_price": row["systemSellPrice"],

            "avg_imbalance": row["netImbalanceVolume"],
            "avg_wind": row["wind_gen"],
            "avg_gas": row["gas_gen"],
            "avg_interconnectors": row["interconnectors"],

            "time_of_max_price": row["startTime"],
            "time_band_at_max_price": row["time_band"],
            "regime_group": row["regime_group"],

            "price_before_event": row["previous_price"],
            "price_after_event": row["systemSellPrice"],
            "price_change_from_previous": row["price_change"],

            "research_note": (
                f"Price moved from {row['previous_price']} to {row['systemSellPrice']} "
                f"in one settlement period. Check internal drivers and external availability context."
            ),
        }

        event["likely_internal_driver"] = "sudden_price_movement_check_internal_and_external_context"
        events.append(event)

    for idx, row in reversal_rows.iterrows():
        event = {
            "year": 2025,
            "event_id": f"2025_large_downward_reversal_{idx}",
            "event_type": "large_downward_reversal",
            "start_time": row["previous_time"],
            "end_time": row["startTime"],
            "duration_hours": 0.5,
            "periods_in_event": 1,

            "max_price": row["previous_price"],
            "min_price": row["systemSellPrice"],
            "avg_price": row["systemSellPrice"],

            "avg_imbalance": row["netImbalanceVolume"],
            "avg_wind": row["wind_gen"],
            "avg_gas": row["gas_gen"],
            "avg_interconnectors": row["interconnectors"],

            "time_of_max_price": row["previous_time"],
            "time_band_at_max_price": row["time_band"],
            "regime_group": row["regime_group"],

            "price_before_event": row["previous_price"],
            "price_after_event": row["systemSellPrice"],
            "price_change_from_previous": row["price_change"],

            "research_note": (
                f"Price moved from {row['previous_price']} to {row['systemSellPrice']} "
                f"in one settlement period. Check whether scarcity conditions reversed or surplus conditions emerged."
            ),
        }

        event["likely_internal_driver"] = "sudden_price_movement_check_internal_and_external_context"
        events.append(event)

    return events


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

    df["month"] = df["startTime"].dt.month
    df["hour"] = df["startTime"].dt.hour
    df["time_band"] = df["hour"].apply(assign_time_band)
    df["regime_group"] = df["month"].apply(assign_2025_regime_group)

    # Event condition flags
    df["negative_price"] = df["systemSellPrice"] < 0
    df["near_spike"] = (df["systemSellPrice"] >= 200) & (df["systemSellPrice"] < 250)
    df["positive_spike"] = df["systemSellPrice"] >= 250
    df["extreme_spike"] = df["systemSellPrice"] >= 300

    all_events = []

    all_events.extend(build_cluster_events(df, "negative_price", "negative_price_cluster"))
    all_events.extend(build_cluster_events(df, "near_spike", "near_spike_cluster"))
    all_events.extend(build_cluster_events(df, "positive_spike", "positive_spike_cluster"))
    all_events.extend(build_cluster_events(df, "extreme_spike", "extreme_spike_cluster"))
    all_events.extend(build_jump_events(df, jump_threshold=100))

    events = pd.DataFrame(all_events)

    if events.empty:
        raise ValueError("No event candidates created.")

    # External REMIT search window: 2 hours before start to 2 hours after end
    events["external_check_window_start"] = events["start_time"] - pd.Timedelta(hours=2)
    events["external_check_window_end"] = events["end_time"] + pd.Timedelta(hours=2)

    events["api_from"] = events["external_check_window_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    events["api_to"] = events["external_check_window_end"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Helpful sorting
    priority_order = {
        "extreme_spike_cluster": 1,
        "positive_spike_cluster": 2,
        "large_upward_jump": 3,
        "near_spike_cluster": 4,
        "negative_price_cluster": 5,
        "large_downward_reversal": 6,
    }

    events["event_priority_rank"] = events["event_type"].map(priority_order).fillna(99)

    events = events.sort_values(
        ["event_priority_rank", "max_price", "start_time"],
        ascending=[True, False, True],
    ).reset_index(drop=True)

    events.to_csv(OUTPUT_FILE, index=False)

    summary = (
        events.groupby(["year", "event_type"])
        .agg(
            event_count=("event_id", "count"),
            max_price=("max_price", "max"),
            min_price=("min_price", "min"),
            avg_duration_hours=("duration_hours", "mean"),
        )
        .reset_index()
        .round(
            {
                "max_price": 4,
                "min_price": 4,
                "avg_duration_hours": 4,
            }
        )
    )

    summary.to_csv(SUMMARY_FILE, index=False)

    print("\n2025 PRICE EVENT CANDIDATES")
    print(events)

    print(f"\nSaved table to: {OUTPUT_FILE}")

    print("\nSUMMARY BY EVENT TYPE")
    print(summary)

    print(f"\nSaved summary to: {SUMMARY_FILE}")

    print("\nCHECK")
    print(f"Total source rows: {len(df)}")
    print(f"Negative price periods: {int(df['negative_price'].sum())}")
    print(f"Near-spike periods 200–250: {int(df['near_spike'].sum())}")
    print(f"Positive spike periods >=250: {int(df['positive_spike'].sum())}")
    print(f"Extreme spike periods >=300: {int(df['extreme_spike'].sum())}")
    print(f"Total event candidates: {len(events)}")


if __name__ == "__main__":
    main()