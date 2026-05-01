import os
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import timedelta

# ============================================================
# 2025 REMIT CASE LINKING SCRIPT
# Purpose:
#   1. Read 2025 case-study windows
#   2. Query Elexon REMIT event identifiers for each case window
#   3. Pull REMIT message details
#   4. Save raw REMIT events near each case
#   5. Create paper-ready case-level REMIT summary
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
TABLE_DIR = BASE_DIR / "outputs" / "tables"
TABLE_DIR.mkdir(parents=True, exist_ok=True)

INPUT_CASE_FILE = TABLE_DIR / "2025_case_study_windows.csv"

RAW_REMIT_OUTPUT = TABLE_DIR / "2025_remit_events_near_case_windows.csv"
SUMMARY_OUTPUT = TABLE_DIR / "2025_case_study_with_remit.csv"
PAPER_OUTPUT = TABLE_DIR / "2025_remit_case_summary_for_paper.csv"

BASE_API_URL = "https://data.elexon.co.uk/bmrs/api/v1"

# Optional: if you have API key in environment variable
# PowerShell example:
#   $env:ELEXON_API_KEY="your_key_here"
API_KEY = os.getenv("ELEXON_API_KEY", "")

HEADERS = {
    "Accept": "application/json"
}

if API_KEY:
    HEADERS["x-api-key"] = API_KEY


# ============================================================
# Helper functions
# ============================================================

def safe_get(row, col, default=""):
    if col in row and pd.notna(row[col]):
        return row[col]
    return default


def normalise_datetime(value):
    """
    Converts date string to ISO format used by the Elexon API.
    """
    if pd.isna(value):
        return None

    ts = pd.to_datetime(value, utc=True)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def query_remit_message_ids(start_time, end_time):
    """
    Query REMIT message IDs by event time window.
    Elexon endpoint:
      GET /remit/list/by-event/stream
    """

    url = f"{BASE_API_URL}/remit/list/by-event/stream"

    params = {
        "from": start_time,
        "to": end_time
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)

        if response.status_code != 200:
            print(f"WARNING: REMIT ID query failed: {response.status_code}")
            print(response.text[:500])
            return []

        data = response.json()

        # The API may return either a list or a dictionary with data inside.
        if isinstance(data, list):
            rows = data
        elif isinstance(data, dict):
            rows = data.get("data", data.get("items", data.get("results", [])))
        else:
            rows = []

        message_ids = []

        for item in rows:
            if not isinstance(item, dict):
                continue

            for possible_key in ["messageId", "messageID", "id", "mrid", "mRID"]:
                if possible_key in item and pd.notna(item[possible_key]):
                    message_ids.append(str(item[possible_key]))
                    break

        return sorted(set(message_ids))

    except Exception as e:
        print(f"ERROR while querying REMIT IDs from {start_time} to {end_time}: {e}")
        return []


def fetch_remit_details(message_ids):
    """
    Pull REMIT message details.
    Elexon endpoint:
      GET /remit?messageId=...
    """

    if not message_ids:
        return []

    all_rows = []

    # Keep batches small to avoid URL/request issues
    batch_size = 25

    for i in range(0, len(message_ids), batch_size):
        batch = message_ids[i:i + batch_size]

        url = f"{BASE_API_URL}/remit"

        # Some API versions accept repeated messageId parameters.
        params = [("messageId", mid) for mid in batch]

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)

            if response.status_code != 200:
                print(f"WARNING: REMIT detail query failed: {response.status_code}")
                print(response.text[:500])
                continue

            data = response.json()

            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                rows = data.get("data", data.get("items", data.get("results", [])))
            else:
                rows = []

            if isinstance(rows, dict):
                rows = [rows]

            all_rows.extend(rows)

            time.sleep(0.2)

        except Exception as e:
            print(f"ERROR while fetching REMIT details: {e}")

    return all_rows


def flatten_remit_event(event):
    """
    REMIT response fields can vary slightly.
    This function extracts likely useful fields without breaking if names differ.
    """

    if not isinstance(event, dict):
        return {}

    def pick(*keys):
        for key in keys:
            if key in event and event[key] not in [None, ""]:
                return event[key]
        return ""

    row = {
        "message_id": pick("messageId", "messageID", "id"),
        "mrid": pick("mrid", "mRID"),
        "revision_number": pick("revisionNumber", "revision"),
        "event_start": pick("eventStartTime", "eventStart", "startTime"),
        "event_end": pick("eventEndTime", "eventEnd", "endTime"),
        "publish_time": pick("publishTime", "publicationTime", "createdDateTime"),
        "asset_id": pick("assetId", "assetID", "registeredResourceName"),
        "asset_name": pick("assetName", "registeredResourceName", "unitName"),
        "fuel_type": pick("fuelType", "fuel", "assetType"),
        "event_type": pick("eventType", "unavailabilityType", "businessType"),
        "status": pick("status", "messageType", "eventStatus"),
        "normal_capacity": pick("normalCapacity", "availableCapacity", "capacity"),
        "unavailable_capacity": pick("unavailableCapacity", "unavailabilityCapacity"),
        "available_capacity": pick("availableCapacity", "availableCapacityMW"),
        "reason": pick("reason", "cause", "remarks")
    }

    # Keep original JSON as string for traceability
    row["raw_event"] = str(event)

    return row


def classify_materiality(row):
    """
    Simple materiality flag based on unavailable capacity where available.
    """

    cap = row.get("unavailable_capacity", "")

    try:
        cap_float = float(cap)
    except Exception:
        cap_float = None

    if cap_float is None:
        return "unknown"

    if cap_float >= 500:
        return "high"
    if cap_float >= 100:
        return "medium"
    if cap_float > 0:
        return "low"

    return "none"


def classify_association(case_row, remit_rows):
    """
    Case-level REMIT association classification.
    """

    if len(remit_rows) == 0:
        return "no_clear_remit_association"

    materialities = remit_rows["materiality"].fillna("").tolist()

    if "high" in materialities:
        return "strong_external_association"

    if "medium" in materialities:
        return "moderate_external_association"

    if len(remit_rows) >= 5:
        return "moderate_external_association"

    return "weak_external_association"


def build_remit_summary(remit_rows):
    if len(remit_rows) == 0:
        return "No REMIT events were found in the case-study check window."

    assets = (
        remit_rows["asset_name"]
        .replace("", pd.NA)
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    event_types = (
        remit_rows["event_type"]
        .replace("", pd.NA)
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    material_counts = remit_rows["materiality"].value_counts().to_dict()

    asset_text = ", ".join(assets[:5]) if assets else "asset names not clearly available"
    event_text = ", ".join(event_types[:5]) if event_types else "event types not clearly available"

    return (
        f"{len(remit_rows)} REMIT event rows were found. "
        f"Main assets: {asset_text}. "
        f"Event types: {event_text}. "
        f"Materiality counts: {material_counts}."
    )


def build_paper_interpretation(case_row, association_strength, remit_summary):
    internal_driver = safe_get(case_row, "internal_driver_summary")
    case_type = safe_get(case_row, "case_type")
    max_price = safe_get(case_row, "max_price")
    regime = safe_get(case_row, "regime_group")

    if association_strength == "strong_external_association":
        return (
            f"This {case_type} case reached a maximum price of {max_price} in the {regime} regime. "
            f"The internal market fingerprint was {internal_driver}. "
            f"REMIT evidence shows a strong external availability association, suggesting that asset-level availability conditions may have reinforced the observed price stress. "
            f"{remit_summary}"
        )

    if association_strength == "moderate_external_association":
        return (
            f"This {case_type} case reached a maximum price of {max_price} in the {regime} regime. "
            f"The internal market fingerprint was {internal_driver}. "
            f"REMIT evidence shows a moderate external association. This suggests that availability conditions were relevant to the wider case window, although the event should still be interpreted primarily through the internal market regime evidence. "
            f"{remit_summary}"
        )

    if association_strength == "weak_external_association":
        return (
            f"This {case_type} case reached a maximum price of {max_price} in the {regime} regime. "
            f"The internal market fingerprint was {internal_driver}. "
            f"Only weak REMIT association was identified, so the case is mainly explained by internal market conditions rather than a clearly identifiable external availability event. "
            f"{remit_summary}"
        )

    return (
        f"This {case_type} case reached a maximum price of {max_price} in the {regime} regime. "
        f"The internal market fingerprint was {internal_driver}. "
        f"No clear REMIT-linked availability event was identified in the check window. "
        f"This supports interpreting the case primarily through internal market conditions."
    )


# ============================================================
# Main script
# ============================================================

def main():
    if not INPUT_CASE_FILE.exists():
        raise FileNotFoundError(
            f"Could not find input file:\n{INPUT_CASE_FILE}\n\n"
            f"Expected file: outputs/tables/2025_case_study_windows.csv"
        )

    cases = pd.read_csv(INPUT_CASE_FILE)

    print("\nLoaded 2025 case-study windows")
    print(f"Rows: {len(cases)}")
    print(f"Input: {INPUT_CASE_FILE}")

    all_remit_rows = []
    summary_rows = []

    for idx, case in cases.iterrows():
        case_id = safe_get(case, "case_id")
        print(f"\nChecking REMIT for case {idx + 1}/{len(cases)}: {case_id}")

        api_from = safe_get(case, "api_from")
        api_to = safe_get(case, "api_to")

        if not api_from or not api_to:
            api_from = normalise_datetime(safe_get(case, "event_window_start"))
            api_to = normalise_datetime(safe_get(case, "event_window_end"))

        if not api_from or not api_to:
            print("  Skipped: missing API window")
            continue

        print(f"  Window: {api_from} to {api_to}")

        message_ids = query_remit_message_ids(api_from, api_to)
        print(f"  REMIT message IDs found: {len(message_ids)}")

        details = fetch_remit_details(message_ids)
        print(f"  REMIT detail rows found: {len(details)}")

        case_remit_rows = []

        for event in details:
            flat = flatten_remit_event(event)

            flat["case_id"] = case_id
            flat["case_type"] = safe_get(case, "case_type")
            flat["case_regime_group"] = safe_get(case, "regime_group")
            flat["case_max_price"] = safe_get(case, "max_price")
            flat["case_min_price"] = safe_get(case, "min_price")
            flat["case_avg_price"] = safe_get(case, "avg_price")
            flat["case_internal_driver_summary"] = safe_get(case, "internal_driver_summary")
            flat["case_api_from"] = api_from
            flat["case_api_to"] = api_to

            flat["materiality"] = classify_materiality(flat)

            case_remit_rows.append(flat)
            all_remit_rows.append(flat)

        case_remit_df = pd.DataFrame(case_remit_rows)

        association_strength = classify_association(case, case_remit_df)
        remit_summary = build_remit_summary(case_remit_df)
        paper_interpretation = build_paper_interpretation(case, association_strength, remit_summary)

        if len(case_remit_df) > 0:
            main_assets = (
                case_remit_df["asset_name"]
                .replace("", pd.NA)
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            main_event_types = (
                case_remit_df["event_type"]
                .replace("", pd.NA)
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            material_events = case_remit_df[
                case_remit_df["materiality"].isin(["high", "medium"])
            ]

            material_count = len(material_events)

            largest_unavailable_capacity = pd.to_numeric(
                case_remit_df["unavailable_capacity"],
                errors="coerce"
            ).max()

        else:
            main_assets = []
            main_event_types = []
            material_count = 0
            largest_unavailable_capacity = ""

        summary_rows.append({
            "case_id": case_id,
            "year": safe_get(case, "year"),
            "case_type": safe_get(case, "case_type"),
            "event_window_start": safe_get(case, "event_window_start"),
            "event_window_end": safe_get(case, "event_window_end"),
            "max_price": safe_get(case, "max_price"),
            "min_price": safe_get(case, "min_price"),
            "avg_price": safe_get(case, "avg_price"),
            "dominant_time_band": safe_get(case, "dominant_time_band"),
            "regime_group": safe_get(case, "regime_group"),
            "avg_imbalance": safe_get(case, "avg_imbalance"),
            "avg_wind": safe_get(case, "avg_wind"),
            "avg_gas": safe_get(case, "avg_gas"),
            "avg_interconnectors": safe_get(case, "avg_interconnectors"),
            "internal_driver_summary": safe_get(case, "internal_driver_summary"),
            "api_from": api_from,
            "api_to": api_to,
            "remit_events_found": len(case_remit_df),
            "material_remit_events_found": material_count,
            "main_remit_assets": " | ".join(main_assets[:10]),
            "main_remit_event_types": " | ".join(main_event_types[:10]),
            "largest_unavailable_capacity": largest_unavailable_capacity,
            "remit_association_strength": association_strength,
            "remit_summary": remit_summary,
            "final_case_interpretation": paper_interpretation
        })

        time.sleep(0.3)

    raw_df = pd.DataFrame(all_remit_rows)
    summary_df = pd.DataFrame(summary_rows)

    raw_df.to_csv(RAW_REMIT_OUTPUT, index=False)
    summary_df.to_csv(SUMMARY_OUTPUT, index=False)

    paper_cols = [
        "case_id",
        "case_type",
        "max_price",
        "regime_group",
        "internal_driver_summary",
        "remit_events_found",
        "material_remit_events_found",
        "main_remit_assets",
        "main_remit_event_types",
        "largest_unavailable_capacity",
        "remit_association_strength",
        "final_case_interpretation"
    ]

    paper_df = summary_df[paper_cols].copy()
    paper_df.to_csv(PAPER_OUTPUT, index=False)

    print("\nDONE")
    print(f"Raw REMIT events saved to: {RAW_REMIT_OUTPUT}")
    print(f"Case-level REMIT summary saved to: {SUMMARY_OUTPUT}")
    print(f"Paper-ready REMIT summary saved to: {PAPER_OUTPUT}")

    print("\nSummary by REMIT association strength:")
    if len(summary_df) > 0:
        print(summary_df["remit_association_strength"].value_counts())
    else:
        print("No summary rows created.")


if __name__ == "__main__":
    main()