import pandas as pd
from pathlib import Path

# ============================================================
# FINAL 2025 REMIT CONTEXT CLASSIFICATION
#
# Purpose:
#   The previous REMIT asset concentration table showed that many
#   assets repeat across many 2025 case windows.
#
#   This script creates a more academically cautious classification:
#
#   - repeated_background_external_context
#   - mixed_external_context
#   - case_specific_external_context
#   - weak_or_unclear_external_context
#
#   The key principle:
#   A case is NOT case-specific simply because one small asset appears
#   only once or twice. We only call it case-specific if a meaningful
#   share of dominant/high-capacity REMIT evidence is case-specific.
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
TABLE_DIR = BASE_DIR / "outputs" / "tables"

ASSET_CONCENTRATION_FILE = TABLE_DIR / "2025_remit_asset_concentration_by_case.csv"
CASE_FILE = TABLE_DIR / "2025_case_study_windows.csv"

OUTPUT_FILE = TABLE_DIR / "2025_case_remit_context_final_classification.csv"


def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def classify_final_case_context(case_row, asset_rows):
    case_id = case_row["case_id"]
    case_type = safe_text(case_row.get("case_type", ""))
    regime_group = safe_text(case_row.get("regime_group", ""))
    dominant_time_band = safe_text(case_row.get("dominant_time_band", ""))
    max_price = case_row.get("max_price", "")
    internal_driver = safe_text(case_row.get("internal_driver_summary", ""))

    if asset_rows.empty:
        return {
            "case_id": case_id,
            "case_type": case_type,
            "regime_group": regime_group,
            "dominant_time_band": dominant_time_band,
            "max_price": max_price,
            "internal_driver_summary": internal_driver,
            "dominant_assets": "",
            "dominant_repeated_assets": "",
            "dominant_case_specific_assets": "",
            "dominant_asset_count": 0,
            "repeated_dominant_asset_count": 0,
            "case_specific_dominant_asset_count": 0,
            "max_unavailable_capacity": "",
            "remit_context_type": "weak_or_unclear_external_context",
            "paper_ready_framing": (
                f"For {case_id}, no clear dominant material REMIT asset concentration was identified. "
                f"The case should therefore be interpreted mainly through the internal market fingerprint: {internal_driver}."
            ),
        }

    # Keep only meaningful asset-level evidence.
    # This avoids over-weighting tiny or weak REMIT rows.
    dominant = asset_rows[
        (asset_rows["max_unavailable_capacity"] >= 500)
        | (asset_rows["remit_rows"] >= 5)
    ].copy()

    if dominant.empty:
        dominant = asset_rows.sort_values(
            by=["max_unavailable_capacity", "remit_rows"],
            ascending=[False, False]
        ).head(5).copy()

    dominant = dominant.sort_values(
        by=["max_unavailable_capacity", "remit_rows"],
        ascending=[False, False]
    ).head(8)

    # Repeated assets are those appearing in many case windows.
    # Since there are 12 total cases, >=6 means the asset appears in at least half.
    repeated = dominant[dominant["asset_repetition_across_cases"] >= 6].copy()

    # Case-specific assets are those appearing in only 1 or 2 case windows.
    case_specific = dominant[dominant["asset_repetition_across_cases"] <= 2].copy()

    dominant_assets = dominant["asset_name"].astype(str).tolist()
    repeated_assets = repeated["asset_name"].astype(str).tolist()
    case_specific_assets = case_specific["asset_name"].astype(str).tolist()

    dominant_asset_count = len(dominant_assets)
    repeated_count = len(repeated_assets)
    case_specific_count = len(case_specific_assets)

    repeated_share = repeated_count / dominant_asset_count if dominant_asset_count else 0
    case_specific_share = case_specific_count / dominant_asset_count if dominant_asset_count else 0

    max_unavailable_capacity = dominant["max_unavailable_capacity"].max()

    # Conservative classification
    if dominant_asset_count == 0:
        context_type = "weak_or_unclear_external_context"

    elif repeated_share >= 0.6:
        context_type = "repeated_background_external_context"

    elif case_specific_share >= 0.5 and max_unavailable_capacity >= 500:
        context_type = "case_specific_external_context"

    else:
        context_type = "mixed_external_context"

    dominant_assets_text = ", ".join(dominant_assets[:6])
    repeated_assets_text = ", ".join(repeated_assets[:6])
    case_specific_assets_text = ", ".join(case_specific_assets[:6])

    if context_type == "repeated_background_external_context":
        framing = (
            f"For {case_id}, REMIT evidence shows material asset unavailability during the case window, "
            f"but the dominant assets also recur across multiple 2025 case windows. "
            f"The main repeated assets include {repeated_assets_text}. "
            f"This should be interpreted as repeated external availability background, not direct single-outage causality. "
            f"The primary explanation remains the internal market fingerprint: {internal_driver}, "
            f"within the {regime_group} regime and {dominant_time_band} time band."
        )

    elif context_type == "case_specific_external_context":
        framing = (
            f"For {case_id}, REMIT evidence shows a more case-specific external availability signal. "
            f"The dominant assets include {dominant_assets_text}, with relatively case-specific assets including {case_specific_assets_text}. "
            f"This suggests that asset availability may have reinforced this particular price event. "
            f"However, causality should still be framed cautiously alongside the internal market fingerprint: {internal_driver}."
        )

    elif context_type == "mixed_external_context":
        framing = (
            f"For {case_id}, REMIT evidence provides mixed external context. "
            f"Some dominant assets recur across several case windows, while others appear more limited to this event window. "
            f"The dominant assets include {dominant_assets_text}. "
            f"The evidence is best used as supporting external context rather than proof of direct causality. "
            f"The main interpretation should remain centred on the internal market fingerprint: {internal_driver}."
        )

    else:
        framing = (
            f"For {case_id}, REMIT evidence is weak or unclear after conservative filtering. "
            f"The case should be explained mainly through the internal market fingerprint: {internal_driver}."
        )

    return {
        "case_id": case_id,
        "case_type": case_type,
        "regime_group": regime_group,
        "dominant_time_band": dominant_time_band,
        "max_price": max_price,
        "internal_driver_summary": internal_driver,
        "dominant_assets": dominant_assets_text,
        "dominant_repeated_assets": repeated_assets_text,
        "dominant_case_specific_assets": case_specific_assets_text,
        "dominant_asset_count": dominant_asset_count,
        "repeated_dominant_asset_count": repeated_count,
        "case_specific_dominant_asset_count": case_specific_count,
        "max_unavailable_capacity": max_unavailable_capacity,
        "remit_context_type": context_type,
        "paper_ready_framing": framing,
    }


def main():
    if not ASSET_CONCENTRATION_FILE.exists():
        raise FileNotFoundError(f"Missing file: {ASSET_CONCENTRATION_FILE}")

    if not CASE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {CASE_FILE}")

    asset_concentration = pd.read_csv(ASSET_CONCENTRATION_FILE)
    cases = pd.read_csv(CASE_FILE)

    print("\nLoaded:")
    print(f"Asset concentration rows: {len(asset_concentration)}")
    print(f"Case rows: {len(cases)}")

    required_cols = [
        "case_id",
        "asset_name",
        "remit_rows",
        "max_unavailable_capacity",
        "asset_repetition_across_cases",
    ]

    missing = [c for c in required_cols if c not in asset_concentration.columns]
    if missing:
        raise ValueError(f"Missing required columns in asset concentration file: {missing}")

    asset_concentration["max_unavailable_capacity"] = pd.to_numeric(
        asset_concentration["max_unavailable_capacity"],
        errors="coerce"
    ).fillna(0)

    asset_concentration["remit_rows"] = pd.to_numeric(
        asset_concentration["remit_rows"],
        errors="coerce"
    ).fillna(0)

    asset_concentration["asset_repetition_across_cases"] = pd.to_numeric(
        asset_concentration["asset_repetition_across_cases"],
        errors="coerce"
    ).fillna(0)

    output_rows = []

    for _, case_row in cases.iterrows():
        case_id = case_row["case_id"]
        asset_rows = asset_concentration[
            asset_concentration["case_id"] == case_id
        ].copy()

        output_rows.append(classify_final_case_context(case_row, asset_rows))

    final = pd.DataFrame(output_rows)

    final.to_csv(OUTPUT_FILE, index=False)

    print("\nFinal REMIT context classification created.")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nClassification counts:")
    print(final["remit_context_type"].value_counts())

    print("\nFinal case-level REMIT interpretation:")
    print(
        final[
            [
                "case_id",
                "remit_context_type",
                "dominant_assets",
                "dominant_repeated_assets",
                "dominant_case_specific_assets",
            ]
        ]
    )


if __name__ == "__main__":
    main()