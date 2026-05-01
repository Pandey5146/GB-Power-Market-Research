import ast
import pandas as pd
from pathlib import Path

# ============================================================
# STRICT 2025 REMIT CASE REFINEMENT
#
# Purpose:
#   The first REMIT script proved that REMIT data connects to
#   the 2025 case-study windows.
#
#   This script makes the REMIT interpretation stricter:
#     1. Reads raw REMIT rows near 2025 case windows
#     2. Parses event start/end times
#     3. Removes duplicates where possible
#     4. Keeps only materially relevant REMIT events
#     5. Produces a cautious paper-ready REMIT interpretation
#
# Why this is needed:
#   The first output showed every case as "strong_external_association".
#   That is too broad for a research paper because many REMIT events can
#   exist in the market at any time.
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
TABLE_DIR = BASE_DIR / "outputs" / "tables"

RAW_REMIT_FILE = TABLE_DIR / "2025_remit_events_near_case_windows.csv"
CASE_FILE = TABLE_DIR / "2025_case_study_windows.csv"

OUTPUT_STRICT_RAW = TABLE_DIR / "2025_remit_events_near_case_windows_strict_filtered.csv"
OUTPUT_STRICT_SUMMARY = TABLE_DIR / "2025_case_study_remit_strict_summary.csv"
OUTPUT_PAPER = TABLE_DIR / "2025_case_study_remit_paper_ready.csv"


# ============================================================
# Helpers
# ============================================================

def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_datetime(series):
    return pd.to_datetime(series, errors="coerce", utc=True)


def parse_raw_event(raw_text):
    """
    The first REMIT script saved the original REMIT JSON as a string.
    This helper tries to recover fields from it if some flattened columns
    were blank.
    """
    if pd.isna(raw_text):
        return {}

    try:
        parsed = ast.literal_eval(str(raw_text))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return {}

    return {}


def pick_from_raw(raw_dict, keys):
    for key in keys:
        if key in raw_dict and raw_dict[key] not in [None, ""]:
            return raw_dict[key]
    return ""


def enrich_missing_fields(df):
    """
    Try to recover useful fields from raw_event where earlier flattening
    missed them.
    """

    recovered_rows = []

    for _, row in df.iterrows():
        raw_dict = parse_raw_event(row.get("raw_event", ""))

        recovered_asset_name = pick_from_raw(
            raw_dict,
            [
                "assetName",
                "asset_name",
                "unitName",
                "registeredResourceName",
                "registeredResourceId",
                "bmUnitId",
                "bmuId",
                "eicCode",
                "participantId",
            ],
        )

        recovered_fuel_type = pick_from_raw(
            raw_dict,
            [
                "fuelType",
                "fuel_type",
                "assetType",
                "powerStationFuelType",
            ],
        )

        recovered_event_start = pick_from_raw(
            raw_dict,
            [
                "eventStartTime",
                "eventStart",
                "startTime",
                "unavailabilityStartTime",
            ],
        )

        recovered_event_end = pick_from_raw(
            raw_dict,
            [
                "eventEndTime",
                "eventEnd",
                "endTime",
                "unavailabilityEndTime",
            ],
        )

        recovered_unavailable_capacity = pick_from_raw(
            raw_dict,
            [
                "unavailableCapacity",
                "unavailabilityCapacity",
                "unavailableCapacityMw",
                "unavailableCapacityMW",
            ],
        )

        recovered_available_capacity = pick_from_raw(
            raw_dict,
            [
                "availableCapacity",
                "availableCapacityMw",
                "availableCapacityMW",
            ],
        )

        recovered_normal_capacity = pick_from_raw(
            raw_dict,
            [
                "normalCapacity",
                "normalCapacityMw",
                "normalCapacityMW",
                "installedCapacity",
            ],
        )

        if not safe_text(row.get("asset_name", "")) and recovered_asset_name:
            row["asset_name"] = recovered_asset_name

        if not safe_text(row.get("fuel_type", "")) and recovered_fuel_type:
            row["fuel_type"] = recovered_fuel_type

        if not safe_text(row.get("event_start", "")) and recovered_event_start:
            row["event_start"] = recovered_event_start

        if not safe_text(row.get("event_end", "")) and recovered_event_end:
            row["event_end"] = recovered_event_end

        if not safe_text(row.get("unavailable_capacity", "")) and recovered_unavailable_capacity:
            row["unavailable_capacity"] = recovered_unavailable_capacity

        if not safe_text(row.get("available_capacity", "")) and recovered_available_capacity:
            row["available_capacity"] = recovered_available_capacity

        if not safe_text(row.get("normal_capacity", "")) and recovered_normal_capacity:
            row["normal_capacity"] = recovered_normal_capacity

        recovered_rows.append(row)

    return pd.DataFrame(recovered_rows)


def classify_materiality(capacity):
    cap = pd.to_numeric(capacity, errors="coerce")

    if pd.isna(cap):
        return "unknown"

    if cap >= 500:
        return "high"
    if cap >= 100:
        return "medium"
    if cap > 0:
        return "low"

    return "none"


def strict_relevance_flag(row):
    """
    Strict filter:
      - Keep production, transmission or consumption unavailability
      - Keep only medium/high unavailable capacity
      - Keep rows with event timing information where possible
    """

    event_type = safe_text(row.get("event_type", "")).lower()
    materiality = safe_text(row.get("strict_materiality", "")).lower()

    relevant_event_type = (
        "production unavailability" in event_type
        or "transmission unavailability" in event_type
        or "consumption unavailability" in event_type
    )

    relevant_materiality = materiality in ["medium", "high"]

    if relevant_event_type and relevant_materiality:
        return True

    return False


def classify_case_association(case_row, case_remit):
    """
    More cautious association logic.

    We do NOT call something strong just because hundreds of REMIT rows exist.
    Strong requires:
      - several materially relevant REMIT rows
      - at least one high-capacity event
      - clear event type relevance
    """

    if len(case_remit) == 0:
        return "no_clear_remit_association"

    high_count = (case_remit["strict_materiality"] == "high").sum()
    medium_high_count = case_remit["strict_materiality"].isin(["medium", "high"]).sum()

    largest_cap = pd.to_numeric(
        case_remit["unavailable_capacity"],
        errors="coerce"
    ).max()

    event_types = " ".join(case_remit["event_type"].fillna("").astype(str).str.lower().unique())

    has_supply_or_network_event = (
        "production unavailability" in event_types
        or "transmission unavailability" in event_types
    )

    if (
        medium_high_count >= 10
        and high_count >= 2
        and pd.notna(largest_cap)
        and largest_cap >= 500
        and has_supply_or_network_event
    ):
        return "strong_external_context"

    if (
        medium_high_count >= 3
        and pd.notna(largest_cap)
        and largest_cap >= 100
        and has_supply_or_network_event
    ):
        return "moderate_external_context"

    if medium_high_count > 0:
        return "weak_external_context"

    return "no_clear_remit_association"


def build_case_summary(case_row, case_remit, association):
    case_type = safe_text(case_row.get("case_type", ""))
    max_price = safe_text(case_row.get("max_price", ""))
    min_price = safe_text(case_row.get("min_price", ""))
    regime = safe_text(case_row.get("regime_group", ""))
    driver = safe_text(case_row.get("internal_driver_summary", ""))
    time_band = safe_text(case_row.get("dominant_time_band", ""))

    total_events = len(case_remit)

    if total_events > 0:
        high_count = int((case_remit["strict_materiality"] == "high").sum())
        medium_count = int((case_remit["strict_materiality"] == "medium").sum())

        largest_cap = pd.to_numeric(
            case_remit["unavailable_capacity"],
            errors="coerce"
        ).max()

        event_types = (
            case_remit["event_type"]
            .replace("", pd.NA)
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        assets = (
            case_remit["asset_name"]
            .replace("", pd.NA)
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        event_type_text = ", ".join(event_types[:5]) if event_types else "not clearly available"
        asset_text = ", ".join(assets[:5]) if assets else "asset names not clearly available"

    else:
        high_count = 0
        medium_count = 0
        largest_cap = ""
        event_type_text = "none"
        asset_text = "none"

    if association == "strong_external_context":
        interpretation = (
            f"This {case_type} case occurred in the {regime} regime and reached a maximum price of {max_price}. "
            f"The internal market fingerprint was {driver}, with the dominant time band classified as {time_band}. "
            f"After stricter filtering, REMIT data shows a strong external availability context: {total_events} materially relevant REMIT rows remained, including {high_count} high-materiality and {medium_count} medium-materiality events. "
            f"The largest unavailable capacity identified was {largest_cap} MW. "
            f"The relevant REMIT event types were: {event_type_text}. "
            f"This means the case should be interpreted as an internally stressed market regime that was likely reinforced by external availability conditions, rather than as a pure single-outage event."
        )

    elif association == "moderate_external_context":
        interpretation = (
            f"This {case_type} case occurred in the {regime} regime and reached a maximum price of {max_price}. "
            f"The internal market fingerprint was {driver}, with the dominant time band classified as {time_band}. "
            f"After stricter filtering, REMIT data shows a moderate external availability context: {total_events} materially relevant REMIT rows remained. "
            f"The largest unavailable capacity identified was {largest_cap} MW. "
            f"The relevant REMIT event types were: {event_type_text}. "
            f"This suggests that external availability conditions were part of the wider market background, but the case should still be explained primarily through the internal regime evidence."
        )

    elif association == "weak_external_context":
        interpretation = (
            f"This {case_type} case occurred in the {regime} regime and reached a maximum price of {max_price}. "
            f"The internal market fingerprint was {driver}. "
            f"Only weak REMIT evidence remained after stricter filtering. "
            f"The case should therefore be interpreted mainly through internal market conditions, with REMIT events treated as background context rather than a main driver."
        )

    else:
        interpretation = (
            f"This {case_type} case occurred in the {regime} regime and reached a maximum price of {max_price}. "
            f"The internal market fingerprint was {driver}. "
            f"No clear materially relevant REMIT event remained after stricter filtering. "
            f"The case should be interpreted primarily as an internal market-regime event."
        )

    return {
        "case_id": case_row.get("case_id", ""),
        "year": case_row.get("year", ""),
        "case_type": case_type,
        "event_window_start": case_row.get("event_window_start", ""),
        "event_window_end": case_row.get("event_window_end", ""),
        "max_price": max_price,
        "min_price": min_price,
        "avg_price": case_row.get("avg_price", ""),
        "dominant_time_band": time_band,
        "regime_group": regime,
        "internal_driver_summary": driver,
        "strict_remit_events_found": total_events,
        "strict_high_materiality_events": high_count,
        "strict_medium_materiality_events": medium_count,
        "largest_unavailable_capacity": largest_cap,
        "main_remit_event_types": event_type_text,
        "main_remit_assets": asset_text,
        "strict_remit_association": association,
        "paper_ready_interpretation": interpretation,
    }


# ============================================================
# Main
# ============================================================

def main():
    if not RAW_REMIT_FILE.exists():
        raise FileNotFoundError(f"Missing raw REMIT file: {RAW_REMIT_FILE}")

    if not CASE_FILE.exists():
        raise FileNotFoundError(f"Missing case file: {CASE_FILE}")

    raw = pd.read_csv(RAW_REMIT_FILE)
    cases = pd.read_csv(CASE_FILE)

    print("\nLoaded files")
    print(f"Raw REMIT rows: {len(raw)}")
    print(f"Cases: {len(cases)}")

    raw = enrich_missing_fields(raw)

    # Parse date columns
    raw["event_start_dt"] = parse_datetime(raw.get("event_start", ""))
    raw["event_end_dt"] = parse_datetime(raw.get("event_end", ""))
    raw["case_api_from_dt"] = parse_datetime(raw.get("case_api_from", ""))
    raw["case_api_to_dt"] = parse_datetime(raw.get("case_api_to", ""))

    # Calculate materiality again after field recovery
    raw["strict_materiality"] = raw["unavailable_capacity"].apply(classify_materiality)

    # Deduplicate as far as possible
    dedupe_cols = []

    for col in ["case_id", "message_id", "mrid", "revision_number", "event_start", "event_end", "asset_name", "event_type"]:
        if col in raw.columns:
            dedupe_cols.append(col)

    if dedupe_cols:
        raw = raw.drop_duplicates(subset=dedupe_cols).copy()
    else:
        raw = raw.drop_duplicates().copy()

    # Keep only rows that pass strict relevance test
    raw["strict_relevance"] = raw.apply(strict_relevance_flag, axis=1)
    strict = raw[raw["strict_relevance"] == True].copy()

    # Optional timing check:
    # If event_start/event_end are available, require overlap with case API window.
    # If timing fields are missing, keep the row but it remains weaker evidence.
    has_timing = strict["event_start_dt"].notna() & strict["event_end_dt"].notna()

    overlaps_case = (
        (strict["event_start_dt"] <= strict["case_api_to_dt"])
        & (strict["event_end_dt"] >= strict["case_api_from_dt"])
    )

    strict = strict[(~has_timing) | (overlaps_case)].copy()

    # Save strict raw output
    strict.to_csv(OUTPUT_STRICT_RAW, index=False)

    summary_rows = []

    for _, case in cases.iterrows():
        case_id = case["case_id"]
        case_remit = strict[strict["case_id"] == case_id].copy()

        association = classify_case_association(case, case_remit)
        summary = build_case_summary(case, case_remit, association)

        summary_rows.append(summary)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(OUTPUT_STRICT_SUMMARY, index=False)

    paper_cols = [
        "case_id",
        "case_type",
        "max_price",
        "regime_group",
        "internal_driver_summary",
        "strict_remit_events_found",
        "strict_high_materiality_events",
        "strict_medium_materiality_events",
        "largest_unavailable_capacity",
        "main_remit_event_types",
        "main_remit_assets",
        "strict_remit_association",
        "paper_ready_interpretation",
    ]

    paper_df = summary_df[paper_cols].copy()
    paper_df.to_csv(OUTPUT_PAPER, index=False)

    print("\nDONE")
    print(f"Strict raw REMIT file saved to: {OUTPUT_STRICT_RAW}")
    print(f"Strict case summary saved to: {OUTPUT_STRICT_SUMMARY}")
    print(f"Paper-ready REMIT file saved to: {OUTPUT_PAPER}")

    print("\nStrict REMIT association counts:")
    print(summary_df["strict_remit_association"].value_counts())

    print("\nRows by case:")
    print(summary_df[["case_id", "strict_remit_events_found", "strict_remit_association"]])


if __name__ == "__main__":
    main()