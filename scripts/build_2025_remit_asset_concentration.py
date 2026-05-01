import pandas as pd
from pathlib import Path

# ============================================================
# 2025 REMIT ASSET CONCENTRATION TABLE
#
# Purpose:
#   The earlier REMIT summary showed that every 2025 case has
#   strong external REMIT context. However, this may still be too
#   broad because the same assets appear repeatedly across cases.
#
#   This script creates an asset-level concentration table so we
#   can identify:
#     - which assets dominate each case window
#     - whether the same assets repeat across many windows
#     - whether REMIT should be treated as direct case evidence
#       or broader external availability context
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
TABLE_DIR = BASE_DIR / "outputs" / "tables"

STRICT_REMIT_FILE = TABLE_DIR / "2025_remit_events_near_case_windows_strict_filtered.csv"
CASE_FILE = TABLE_DIR / "2025_case_study_windows.csv"

OUTPUT_ASSET_CONCENTRATION = TABLE_DIR / "2025_remit_asset_concentration_by_case.csv"
OUTPUT_ASSET_REPETITION = TABLE_DIR / "2025_remit_asset_repetition_across_cases.csv"
OUTPUT_CASE_REMIT_CLASSIFICATION = TABLE_DIR / "2025_case_remit_context_classification.csv"


def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def classify_asset_role(row):
    """
    Classifies the REMIT evidence role of an asset within a case.

    This does NOT claim causality.
    It only describes whether the asset is materially relevant in the window.
    """

    rows = row["remit_rows"]
    max_cap = row["max_unavailable_capacity"]
    avg_cap = row["avg_unavailable_capacity"]

    if max_cap >= 1000 and rows >= 3:
        return "major_material_asset_in_case_window"

    if max_cap >= 500 and rows >= 2:
        return "material_asset_in_case_window"

    if max_cap >= 100:
        return "moderate_asset_context"

    return "minor_asset_context"


def classify_case_context(case_row, asset_rows):
    """
    Creates a cautious case-level REMIT interpretation.
    """

    case_id = case_row["case_id"]
    case_type = safe_text(case_row.get("case_type", ""))
    regime = safe_text(case_row.get("regime_group", ""))
    driver = safe_text(case_row.get("internal_driver_summary", ""))
    max_price = safe_text(case_row.get("max_price", ""))

    if asset_rows.empty:
        return {
            "case_id": case_id,
            "case_type": case_type,
            "regime_group": regime,
            "max_price": max_price,
            "internal_driver_summary": driver,
            "dominant_remit_assets": "",
            "remit_context_type": "no_clear_asset_level_context",
            "paper_ready_remit_framing": (
                f"For {case_id}, no clear material asset-level REMIT concentration was found. "
                f"The case should be interpreted primarily through the internal market regime: {driver}."
            ),
        }

    major_assets = asset_rows[
        asset_rows["asset_role"].isin(
            [
                "major_material_asset_in_case_window",
                "material_asset_in_case_window",
            ]
        )
    ].copy()

    dominant_assets = (
        major_assets.sort_values(
            by=["max_unavailable_capacity", "remit_rows"],
            ascending=[False, False],
        )["asset_name"]
        .dropna()
        .astype(str)
        .head(5)
        .tolist()
    )

    dominant_assets_text = ", ".join(dominant_assets)

    repeated_background_assets = asset_rows[
        asset_rows["asset_repetition_across_cases"] >= 6
    ]

    case_specific_assets = asset_rows[
        asset_rows["asset_repetition_across_cases"] <= 2
    ]

    if len(case_specific_assets) >= 1:
        context_type = "case_specific_external_context"
        framing = (
            f"For {case_id}, REMIT evidence shows asset-level external context during the {case_type} case. "
            f"The dominant assets were {dominant_assets_text}. "
            f"Some assets appear relatively case-specific, so the REMIT evidence can be discussed as a potentially relevant external reinforcement. "
            f"However, the primary explanation should remain the internal market fingerprint: {driver}, within the {regime} regime."
        )

    elif len(repeated_background_assets) >= 1:
        context_type = "repeated_background_external_context"
        framing = (
            f"For {case_id}, REMIT evidence shows material asset unavailability during the case window, with dominant assets including {dominant_assets_text}. "
            f"However, several of these assets recur across many 2025 case windows, so the evidence should be framed as repeated external availability background rather than direct single-event causality. "
            f"The case should be interpreted primarily through the internal market fingerprint: {driver}, within the {regime} regime, with REMIT providing supporting external context."
        )

    else:
        context_type = "general_external_context"
        framing = (
            f"For {case_id}, REMIT evidence provides general external availability context during the {case_type} case. "
            f"The dominant assets were {dominant_assets_text}. "
            f"The REMIT data supports the idea that asset availability conditions formed part of the wider market environment, but it should not be treated as proof of direct causality."
        )

    return {
        "case_id": case_id,
        "case_type": case_type,
        "regime_group": regime,
        "max_price": max_price,
        "internal_driver_summary": driver,
        "dominant_remit_assets": dominant_assets_text,
        "remit_context_type": context_type,
        "paper_ready_remit_framing": framing,
    }


def main():
    if not STRICT_REMIT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {STRICT_REMIT_FILE}")

    if not CASE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {CASE_FILE}")

    remit = pd.read_csv(STRICT_REMIT_FILE)
    cases = pd.read_csv(CASE_FILE)

    print("\nLoaded files")
    print(f"Strict REMIT rows: {len(remit)}")
    print(f"Cases: {len(cases)}")

    # Clean fields
    remit["asset_name"] = remit["asset_name"].fillna("").astype(str).str.strip()
    remit["event_type"] = remit["event_type"].fillna("").astype(str).str.strip()
    remit["unavailable_capacity"] = pd.to_numeric(
        remit["unavailable_capacity"],
        errors="coerce"
    )

    # Remove blank asset names
    remit = remit[remit["asset_name"] != ""].copy()

    # Asset concentration by case
    group_cols = ["case_id", "asset_name", "event_type"]

    asset_case = (
        remit.groupby(group_cols, dropna=False)
        .agg(
            remit_rows=("asset_name", "size"),
            max_unavailable_capacity=("unavailable_capacity", "max"),
            avg_unavailable_capacity=("unavailable_capacity", "mean"),
            first_event_start=("event_start", "min"),
            last_event_end=("event_end", "max"),
        )
        .reset_index()
    )

    asset_case["max_unavailable_capacity"] = asset_case["max_unavailable_capacity"].round(2)
    asset_case["avg_unavailable_capacity"] = asset_case["avg_unavailable_capacity"].round(2)

    asset_case["asset_role"] = asset_case.apply(classify_asset_role, axis=1)

    # How often each asset appears across case windows
    asset_repetition = (
        asset_case.groupby("asset_name")
        .agg(
            cases_appeared_in=("case_id", "nunique"),
            total_remit_rows=("remit_rows", "sum"),
            max_unavailable_capacity=("max_unavailable_capacity", "max"),
            event_types=("event_type", lambda x: " | ".join(sorted(set(x.dropna().astype(str))))),
        )
        .reset_index()
        .sort_values(
            by=["cases_appeared_in", "max_unavailable_capacity", "total_remit_rows"],
            ascending=[False, False, False],
        )
    )

    asset_case = asset_case.merge(
        asset_repetition[["asset_name", "cases_appeared_in"]],
        on="asset_name",
        how="left"
    )

    asset_case = asset_case.rename(
        columns={"cases_appeared_in": "asset_repetition_across_cases"}
    )

    asset_case = asset_case.sort_values(
        by=[
            "case_id",
            "max_unavailable_capacity",
            "remit_rows",
            "asset_name",
        ],
        ascending=[True, False, False, True],
    )

    asset_case.to_csv(OUTPUT_ASSET_CONCENTRATION, index=False)
    asset_repetition.to_csv(OUTPUT_ASSET_REPETITION, index=False)

    # Build case-level classification
    case_rows = []

    for _, case in cases.iterrows():
        case_id = case["case_id"]
        asset_rows = asset_case[asset_case["case_id"] == case_id].copy()

        case_rows.append(classify_case_context(case, asset_rows))

    case_context = pd.DataFrame(case_rows)
    case_context.to_csv(OUTPUT_CASE_REMIT_CLASSIFICATION, index=False)

    print("\nDONE")
    print(f"Asset concentration saved to: {OUTPUT_ASSET_CONCENTRATION}")
    print(f"Asset repetition saved to: {OUTPUT_ASSET_REPETITION}")
    print(f"Case REMIT classification saved to: {OUTPUT_CASE_REMIT_CLASSIFICATION}")

    print("\nTop repeated assets across 2025 case windows:")
    print(asset_repetition.head(15))

    print("\nCase-level REMIT context classification:")
    print(case_context[["case_id", "remit_context_type", "dominant_remit_assets"]])


if __name__ == "__main__":
    main()