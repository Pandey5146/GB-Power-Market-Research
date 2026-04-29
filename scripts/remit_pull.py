import os
import time
import requests
import pandas as pd
from pathlib import Path


# ==============================
# FILE PATHS
# ==============================

INPUT_FILE = Path("outputs/tables/2023_2024_remit_query_windows.csv")
OUTPUT_FILE = Path("outputs/tables/2023_2024_filtered_remit_events_near_price_events.csv")


# ==============================
# API SETTINGS
# ==============================

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

API_KEY = os.getenv("ELEXON_API_KEY")

HEADERS = {
    "Accept": "application/json",
}

if API_KEY:
    HEADERS["Ocp-Apim-Subscription-Key"] = API_KEY


# ==============================
# SETTINGS
# ==============================

MAX_WINDOWS_TO_CHECK = None
MAX_MESSAGES_PER_WINDOW = 30

RELEVANT_ASSET_TYPES = [
    "generation",
    "interconnector",
    "production",
    "wind",
    "ccgt",
    "ocgt",
    "bm unit",
]

RELEVANT_KEYWORDS = [
    "unavailable",
    "unavailability",
    "outage",
    "maintenance",
    "de-load",
    "deload",
    "fault",
    "trip",
    "reduced",
    "capacity",
    "shutdown",
    "constraint",
]


# ==============================
# HELPER FUNCTIONS
# ==============================

def safe_get_json(url, params=None, retries=2, sleep_seconds=1):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=25,
            )

            if response.status_code == 200:
                return response.json()

            print(f"Request failed: {response.status_code}")
            print(response.text[:500])

        except Exception as e:
            print(f"Request error on attempt {attempt}: {e}")

        time.sleep(sleep_seconds)

    return None


def extract_rows(payload):
    if payload is None:
        return []

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        return (
            payload.get("data")
            or payload.get("results")
            or payload.get("items")
            or []
        )

    return []


def extract_message_ids(payload):
    rows = extract_rows(payload)

    message_ids = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        for key in ["messageId", "id", "mrid", "mRID"]:
            if key in row and row[key]:
                message_ids.append(row[key])
                break

    return list(dict.fromkeys(message_ids))


def list_remit_message_ids_by_event_time(api_from, api_to):
    url = f"{BASE_URL}/remit/list/by-event"

    params = {
        "from": api_from,
        "to": api_to,
    }

    payload = safe_get_json(url, params=params)
    return extract_message_ids(payload)


def fetch_remit_message_detail(message_id):
    url = f"{BASE_URL}/remit/{message_id}"

    payload = safe_get_json(url)
    rows = extract_rows(payload)

    if not rows and isinstance(payload, dict):
        rows = [payload]

    return rows


def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value).lower()


def is_relevant_remit_row(row):
    """
    Keeps rows that look relevant to outage/unavailability/capacity changes.
    """
    text_fields = [
        safe_text(row.get("remit_eventType", "")),
        safe_text(row.get("remit_unavailabilityType", "")),
        safe_text(row.get("remit_assetType", "")),
        safe_text(row.get("remit_fuelType", "")),
        safe_text(row.get("remit_cause", "")),
        safe_text(row.get("remit_relatedInformation", "")),
        safe_text(row.get("remit_messageHeading", "")),
    ]

    combined_text = " ".join(text_fields)

    has_keyword = any(keyword in combined_text for keyword in RELEVANT_KEYWORDS)

    unavailable_capacity = pd.to_numeric(
        row.get("remit_unavailableCapacity", None),
        errors="coerce"
    )

    normal_capacity = pd.to_numeric(
        row.get("remit_normalCapacity", None),
        errors="coerce"
    )

    available_capacity = pd.to_numeric(
        row.get("remit_availableCapacity", None),
        errors="coerce"
    )

    has_capacity_signal = (
        pd.notna(unavailable_capacity) and unavailable_capacity > 0
    ) or (
        pd.notna(normal_capacity)
        and pd.notna(available_capacity)
        and available_capacity < normal_capacity
    )

    return has_keyword or has_capacity_signal


def simplify_event_type(row):
    fuel = str(row.get("remit_fuelType", "")).lower()
    asset_type = str(row.get("remit_assetType", "")).lower()
    cause = str(row.get("remit_cause", "")).lower()
    related = str(row.get("remit_relatedInformation", "")).lower()
    combined = " ".join([fuel, asset_type, cause, related])

    if "interconnector" in combined:
        return "interconnector_unavailability"
    if "wind" in combined:
        return "wind_unavailability"
    if "gas" in combined or "ccgt" in combined or "ocgt" in combined:
        return "thermal_gas_unavailability"
    if "maintenance" in combined or "de-load" in combined or "deload" in combined:
        return "maintenance_or_deload"
    if "fault" in combined or "trip" in combined:
        return "fault_or_trip"
    return "other_unavailability_or_capacity_change"


# ==============================
# MAIN
# ==============================

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_FILE}")

    windows = pd.read_csv(INPUT_FILE)
    # Focus only on the strongest first case-study dates
    case_study_dates = [
    "2023-03-07",
    "2024-10-14",
    "2024-12-11",
    "2024-12-12",
    ]
    
    windows = windows[
    windows["api_from"].astype(str).str[:10].isin(case_study_dates)
    
    ].copy()

    # Keep only the highest max-price window per date to avoid repeated overlapping REMIT pulls
    windows["case_date"] = windows["api_from"].astype(str).str[:10]
    
    windows = (
        windows
        .sort_values(["case_date", "max_price"], ascending=[True, False])
        .groupby("case_date")
        .head(1)
        .reset_index(drop=True)
        )
    print("\nCASE-STUDY WINDOWS ONLY")
    print(windows[["event_id", "api_from", "api_to", "max_price", "regime_group"]])

    if MAX_WINDOWS_TO_CHECK is not None:
        windows = windows.head(MAX_WINDOWS_TO_CHECK)

    all_rows = []

    for idx, window in windows.iterrows():
        event_id = window["event_id"]
        api_from = window["api_from"]
        api_to = window["api_to"]

        print(f"\nChecking REMIT window {idx + 1}/{len(windows)}")
        print(f"{event_id}: {api_from} to {api_to}")

        message_ids = list_remit_message_ids_by_event_time(api_from, api_to)

        print(f"Message IDs found: {len(message_ids)}")

        if len(message_ids) > MAX_MESSAGES_PER_WINDOW:
            print(
                f"Limiting to first {MAX_MESSAGES_PER_WINDOW} messages "
                f"for this window to avoid API overload."
            )

        for message_id in message_ids[:MAX_MESSAGES_PER_WINDOW]:
            detail_rows = fetch_remit_message_detail(message_id)

            for detail in detail_rows:
                if not isinstance(detail, dict):
                    continue

                output_row = {
                    "price_event_id": event_id,
                    "price_event_type": window.get("event_type", ""),
                    "price_event_year": window.get("year", ""),
                    "price_event_start": window.get("start_time", ""),
                    "price_event_end": window.get("end_time", ""),
                    "price_event_max_price": window.get("max_price", ""),
                    "price_event_min_price": window.get("min_price", ""),
                    "price_event_avg_imbalance": window.get("avg_imbalance", ""),
                    "price_event_avg_wind": window.get("avg_wind", ""),
                    "price_event_avg_gas": window.get("avg_gas", ""),
                    "price_event_avg_interconnectors": window.get("avg_interconnectors", ""),
                    "price_event_time_band": window.get("time_band_at_max_price", ""),
                    "price_event_regime_group": window.get("regime_group", ""),
                    "price_event_likely_internal_driver": window.get("likely_internal_driver", ""),
                    "query_api_from": api_from,
                    "query_api_to": api_to,
                    "remit_message_id": message_id,
                }

                for key, value in detail.items():
                    output_row[f"remit_{key}"] = value

                if is_relevant_remit_row(output_row):
                    output_row["simplified_external_event_type"] = simplify_event_type(output_row)
                    all_rows.append(output_row)

            time.sleep(0.05)

    if all_rows:
        final_df = pd.DataFrame(all_rows)
    else:
        final_df = pd.DataFrame()

    if len(final_df) > 0:
        # Convert capacities if present
        for col in [
            "remit_normalCapacity",
            "remit_availableCapacity",
            "remit_unavailableCapacity",
        ]:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors="coerce")

        # Drop exact duplicate message-event rows
        duplicate_cols = [
            col for col in [
                "price_event_id",
                "remit_mrid",
                "remit_revisionNumber",
                "remit_eventStartTime",
                "remit_eventEndTime",
                "remit_affectedUnit",
                "remit_unavailableCapacity",
            ]
            if col in final_df.columns
        ]

        if duplicate_cols:
            final_df = final_df.drop_duplicates(subset=duplicate_cols)

        # Sort useful rows first
        sort_cols = [
            col for col in [
                "price_event_year",
                "price_event_start",
                "remit_eventStartTime",
                "remit_unavailableCapacity",
            ]
            if col in final_df.columns
        ]

        if sort_cols:
            final_df = final_df.sort_values(
                sort_cols,
                ascending=[True, True, True, False][:len(sort_cols)]
            )

    final_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved filtered REMIT events to: {OUTPUT_FILE}")
    print(f"Rows saved: {len(final_df)}")

    if len(final_df) > 0:
        print("\nSUMMARY BY EVENT TYPE")
        if "simplified_external_event_type" in final_df.columns:
            print(
                final_df
                .groupby(["price_event_year", "simplified_external_event_type"])
                .agg(
                    rows=("remit_message_id", "count"),
                    max_unavailable_capacity=("remit_unavailableCapacity", "max"),
                )
                .reset_index()
            )

        useful_cols = [
            "price_event_id",
            "price_event_type",
            "price_event_max_price",
            "price_event_avg_imbalance",
            "price_event_avg_wind",
            "price_event_avg_gas",
            "price_event_avg_interconnectors",
            "price_event_regime_group",
            "simplified_external_event_type",
            "remit_eventType",
            "remit_unavailabilityType",
            "remit_assetType",
            "remit_fuelType",
            "remit_affectedUnit",
            "remit_normalCapacity",
            "remit_availableCapacity",
            "remit_unavailableCapacity",
            "remit_eventStatus",
            "remit_eventStartTime",
            "remit_eventEndTime",
            "remit_cause",
            "remit_relatedInformation",
        ]

        useful_cols = [col for col in useful_cols if col in final_df.columns]

        print("\nSAMPLE FILTERED ROWS")
        print(final_df[useful_cols].head(30))


if __name__ == "__main__":
    main()