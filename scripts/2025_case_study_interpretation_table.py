from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path("outputs/tables/2025_price_event_candidates.csv")
OUTPUT_FILE = Path("outputs/tables/2025_case_study_windows.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD EVENT CANDIDATES
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

events = pd.read_csv(INPUT_FILE)

events["start_time"] = pd.to_datetime(events["start_time"], utc=True)
events["end_time"] = pd.to_datetime(events["end_time"], utc=True)

print(f"Loaded event candidates: {events.shape}")


# ============================================================
# CASE STUDY WINDOWS
# ============================================================

case_windows = [
    {
        "case_id": "2025_case_01_jan_08_extreme_spike",
        "year": 2025,
        "case_type": "extreme_positive_spike",
        "event_window_start": "2025-01-08 10:00:00+00:00",
        "event_window_end": "2025-01-08 21:30:00+00:00",
        "why_selected_for_paper": "Largest 2025 price event. Captures the main £2900/MWh extreme spike episode and sharp intraday price discontinuity.",
    },
    {
        "case_id": "2025_case_02_jan_20_evening_scarcity",
        "year": 2025,
        "case_type": "evening_scarcity_spike",
        "event_window_start": "2025-01-20 05:00:00+00:00",
        "event_window_end": "2025-01-20 21:00:00+00:00",
        "why_selected_for_paper": "Important January scarcity event with very high gas generation, low wind and lower interconnector support.",
    },
    {
        "case_id": "2025_case_03_jan_22_morning_ramp_scarcity",
        "year": 2025,
        "case_type": "morning_ramp_scarcity_spike",
        "event_window_start": "2025-01-22 04:30:00+00:00",
        "event_window_end": "2025-01-22 09:00:00+00:00",
        "why_selected_for_paper": "Morning ramp scarcity case with exceptionally low wind and very high gas generation.",
    },
    {
        "case_id": "2025_case_04_jun_30_mixed_tail_spike",
        "year": 2025,
        "case_type": "mixed_tail_positive_spike",
        "event_window_start": "2025-06-30 14:30:00+00:00",
        "event_window_end": "2025-06-30 21:30:00+00:00",
        "why_selected_for_paper": "Non-January spike event showing mixed-tail behaviour with strong positive imbalance and reduced interconnector support.",
    },
    {
        "case_id": "2025_case_05_jul_01_near_spike",
        "year": 2025,
        "case_type": "near_spike_continuation",
        "event_window_start": "2025-07-01 15:00:00+00:00",
        "event_window_end": "2025-07-01 19:30:00+00:00",
        "why_selected_for_paper": "Near-spike case useful for comparing stressed conditions that nearly converted into a full £250+/MWh event.",
    },
    {
        "case_id": "2025_case_06_oct_13_autumn_spike",
        "year": 2025,
        "case_type": "autumn_mixed_transition_spike",
        "event_window_start": "2025-10-13 09:30:00+00:00",
        "event_window_end": "2025-10-13 19:30:00+00:00",
        "why_selected_for_paper": "Autumn transition event with low wind, high gas and positive imbalance conditions.",
    },
    {
        "case_id": "2025_case_07_oct_14_evening_spike",
        "year": 2025,
        "case_type": "autumn_evening_spike",
        "event_window_start": "2025-10-14 15:00:00+00:00",
        "event_window_end": "2025-10-14 19:00:00+00:00",
        "why_selected_for_paper": "Short evening spike during the October mixed-transition regime.",
    },
    {
        "case_id": "2025_case_08_oct_22_evening_spike",
        "year": 2025,
        "case_type": "autumn_evening_spike",
        "event_window_start": "2025-10-22 13:30:00+00:00",
        "event_window_end": "2025-10-22 19:30:00+00:00",
        "why_selected_for_paper": "October evening event with high gas, very low wind and positive imbalance.",
    },
    {
        "case_id": "2025_case_09_mar_30_negative_price_cluster",
        "year": 2025,
        "case_type": "negative_price_cluster",
        "event_window_start": "2025-03-30 01:30:00+00:00",
        "event_window_end": "2025-03-30 18:00:00+00:00",
        "why_selected_for_paper": "Major negative-price cluster showing downward-price formation under surplus and negative imbalance conditions.",
    },
    {
        "case_id": "2025_case_10_apr_05_negative_price_cluster",
        "year": 2025,
        "case_type": "negative_price_cluster",
        "event_window_start": "2025-04-05 03:00:00+00:00",
        "event_window_end": "2025-04-05 17:30:00+00:00",
        "why_selected_for_paper": "Deep April negative-price case during the surplus-shift regime.",
    },
    {
        "case_id": "2025_case_11_jun_22_negative_price_cluster",
        "year": 2025,
        "case_type": "negative_price_cluster",
        "event_window_start": "2025-06-22 00:30:00+00:00",
        "event_window_end": "2025-06-22 17:30:00+00:00",
        "why_selected_for_paper": "Long June negative-price cluster during the mixed-tail regime.",
    },
    {
        "case_id": "2025_case_12_sep_06_negative_price_cluster",
        "year": 2025,
        "case_type": "negative_price_cluster",
        "event_window_start": "2025-09-06 07:00:00+00:00",
        "event_window_end": "2025-09-06 23:30:00+00:00",
        "why_selected_for_paper": "Large summer/autumn negative-price case showing surplus conditions and sharp lower-tail behaviour.",
    },
]


# ============================================================
# BUILD CASE STUDY TABLE
# ============================================================

rows = []

for case in case_windows:
    window_start = pd.to_datetime(case["event_window_start"], utc=True)
    window_end = pd.to_datetime(case["event_window_end"], utc=True)

    matched = events[
        (events["start_time"] >= window_start)
        & (events["start_time"] <= window_end)
    ].copy()

    if matched.empty:
        row = {
            **case,
            "events_found": 0,
            "max_price": None,
            "min_price": None,
            "avg_price": None,
            "max_price_time": None,
            "dominant_time_band": None,
            "regime_group": None,
            "avg_imbalance": None,
            "avg_wind": None,
            "avg_gas": None,
            "avg_interconnectors": None,
            "linked_event_types": None,
            "linked_event_ids": None,
            "external_check_window_start": None,
            "external_check_window_end": None,
            "internal_driver_summary": None,
            "api_from": None,
            "api_to": None,
        }
        rows.append(row)
        continue

    max_price_idx = matched["max_price"].idxmax()

    linked_event_types = "|".join(sorted(matched["event_type"].dropna().unique()))
    linked_event_ids = "|".join(matched["event_id"].dropna().astype(str).tolist())

    dominant_time_band = (
        matched["time_band_at_max_price"]
        .dropna()
        .mode()
    )

    regime_group = (
        matched["regime_group"]
        .dropna()
        .mode()
    )

    likely_internal_driver = (
        matched["likely_internal_driver"]
        .dropna()
        .mode()
    )

    row = {
        **case,
        "events_found": len(matched),
        "max_price": round(matched["max_price"].max(), 4),
        "min_price": round(matched["min_price"].min(), 4),
        "avg_price": round(matched["avg_price"].mean(), 4),
        "max_price_time": matched.loc[max_price_idx, "time_of_max_price"],
        "dominant_time_band": dominant_time_band.iloc[0] if not dominant_time_band.empty else None,
        "regime_group": regime_group.iloc[0] if not regime_group.empty else None,
        "avg_imbalance": round(matched["avg_imbalance"].mean(), 4),
        "avg_wind": round(matched["avg_wind"].mean(), 4),
        "avg_gas": round(matched["avg_gas"].mean(), 4),
        "avg_interconnectors": round(matched["avg_interconnectors"].mean(), 4),
        "linked_event_types": linked_event_types,
        "linked_event_ids": linked_event_ids,
        "external_check_window_start": matched["external_check_window_start"].min(),
        "external_check_window_end": matched["external_check_window_end"].max(),
        "internal_driver_summary": likely_internal_driver.iloc[0] if not likely_internal_driver.empty else None,
        "api_from": matched["api_from"].min(),
        "api_to": matched["api_to"].max(),
    }

    rows.append(row)


case_df = pd.DataFrame(rows)


# ============================================================
# SAVE
# ============================================================

case_df.to_csv(OUTPUT_FILE, index=False)

print("\n2025 CASE STUDY WINDOWS")
print(case_df)

print(f"\nSaved to: {OUTPUT_FILE}")

print("\nCHECK")
print(f"Case windows created: {len(case_df)}")
print(f"Total matching candidate rows used across windows: {case_df['events_found'].sum()}")

zero_cases = case_df[case_df["events_found"] == 0]

print("\nCases with zero matched rows:")
print(zero_cases[["case_id", "event_window_start", "event_window_end"]])