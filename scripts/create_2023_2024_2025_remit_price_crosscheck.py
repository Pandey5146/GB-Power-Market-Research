from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
TABLES_DIR = BASE_DIR / "outputs" / "tables"

CASE_COMPARISON_FILE = TABLES_DIR / "2023_2024_2025_case_study_comparison.csv"
REMIT_2025_FILE = TABLES_DIR / "2025_case_remit_context_final_classification.csv"

OUTPUT_FILE = TABLES_DIR / "2023_2024_2025_remit_price_crosscheck.csv"


def read_csv_safely(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path)


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def build_2023_2024_interpretation(row):
    year = int(row["year"])
    case_type = clean_text(row.get("case_type", ""))
    regime = clean_text(row.get("regime_group", ""))
    max_price = row.get("max_price", "")

    return (
        f"This {year} case is used as part of the historical regime-based foundation. "
        f"The case type is {case_type}, with a maximum price of {max_price} in the {regime} regime. "
        f"At this stage, the case has not been reassessed using the detailed 2025 REMIT overlay method. "
        f"Therefore, it supports the internal market-regime argument, while REMIT causality is not claimed for this case."
    )


def build_2025_interpretation(row):
    case_type = clean_text(row.get("case_type", ""))
    regime = clean_text(row.get("regime_group", ""))
    max_price = row.get("max_price", "")
    internal = clean_text(row.get("internal_driver_summary", ""))
    remit_context = clean_text(row.get("remit_context_type", ""))
    repeated_assets = clean_text(row.get("dominant_repeated_assets", ""))
    case_assets = clean_text(row.get("dominant_case_specific_assets", ""))

    interpretation = (
        f"This 2025 {case_type} case reached a maximum price of {max_price} in the {regime} regime. "
        f"The internal market fingerprint was {internal}. "
        f"The REMIT overlay classifies this case as {remit_context}. "
    )

    if remit_context == "repeated_background_external_context":
        interpretation += (
            "This means the event should be interpreted primarily through the internal market regime, "
            "while external asset-availability conditions acted as a reinforcing background context. "
        )
    elif remit_context == "case_specific_external_context":
        interpretation += (
            "This means there is stronger case-specific external availability evidence around this event window, "
            "although the price event should still be interpreted alongside the internal market regime. "
        )
    else:
        interpretation += (
            "This means the REMIT evidence is not strong enough to treat external availability as the main explanation. "
        )

    if repeated_assets:
        interpretation += f"Dominant repeated REMIT assets were: {repeated_assets}. "

    if case_assets:
        interpretation += f"Case-specific REMIT assets included: {case_assets}. "

    interpretation += (
        "Overall, this supports the paper's central argument that GB imbalance price tails are regime-led, "
        "with REMIT notifications acting as an external cross-check rather than simple one-outage causality."
    )

    return interpretation


def main():
    cases = read_csv_safely(CASE_COMPARISON_FILE)
    remit_2025 = read_csv_safely(REMIT_2025_FILE)

    print("Loaded:")
    print(f"Case comparison rows: {len(cases)}")
    print(f"2025 REMIT classification rows: {len(remit_2025)}")

    print("\nCase comparison columns:")
    print(list(cases.columns))

    print("\n2025 REMIT classification columns:")
    print(list(remit_2025.columns))

    # Keep only useful REMIT columns if they exist
    remit_cols = [
        "case_id",
        "remit_context_type",
        "dominant_repeated_assets",
        "dominant_case_specific_assets",
    ]

    existing_remit_cols = [col for col in remit_cols if col in remit_2025.columns]
    remit_2025_small = remit_2025[existing_remit_cols].copy()

    merged = cases.merge(
        remit_2025_small,
        on="case_id",
        how="left",
        suffixes=("", "_from_remit")
    )

    # If case comparison already has REMIT columns, use the dedicated 2025 file where available
    for col in ["remit_context_type", "dominant_repeated_assets", "dominant_case_specific_assets"]:
        remit_col = f"{col}_from_remit"
        if remit_col in merged.columns:
            if col in merged.columns:
                merged[col] = merged[remit_col].combine_first(merged[col])
                merged = merged.drop(columns=[remit_col])
            else:
                merged[col] = merged[remit_col]
                merged = merged.drop(columns=[remit_col])

    # Fill 2023/2024 REMIT context
    merged["remit_context_type"] = merged["remit_context_type"].fillna("not_reassessed_in_2025_remit_overlay")
    merged["dominant_repeated_assets"] = merged["dominant_repeated_assets"].fillna("")
    merged["dominant_case_specific_assets"] = merged["dominant_case_specific_assets"].fillna("")

    final_interpretations = []

    for _, row in merged.iterrows():
        year = int(row["year"])

        if year == 2025:
            final_interpretations.append(build_2025_interpretation(row))
        else:
            final_interpretations.append(build_2023_2024_interpretation(row))

    merged["remit_price_crosscheck_interpretation"] = final_interpretations

    final_columns = [
        "source_period",
        "year",
        "case_id",
        "case_type",
        "event_window_start",
        "event_window_end",
        "max_price",
        "min_price",
        "avg_price",
        "dominant_time_band",
        "regime_group",
        "avg_imbalance",
        "avg_wind",
        "avg_gas",
        "avg_interconnectors",
        "internal_driver_summary",
        "price_behaviour",
        "regime_interpretation",
        "paper_use",
        "remit_context_type",
        "dominant_repeated_assets",
        "dominant_case_specific_assets",
        "remit_price_crosscheck_interpretation",
    ]

    existing_final_columns = [col for col in final_columns if col in merged.columns]
    final = merged[existing_final_columns].copy()

    final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\nREMIT-price cross-check table created successfully.")
    print(f"Rows: {len(final)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nRows by year:")
    print(final["year"].value_counts().sort_index())

    print("\nREMIT context classification:")
    print(final["remit_context_type"].value_counts(dropna=False))

    print("\nPreview:")
    preview_cols = [
        "year",
        "case_id",
        "case_type",
        "max_price",
        "regime_group",
        "remit_context_type",
    ]
    existing_preview_cols = [col for col in preview_cols if col in final.columns]
    print(final[existing_preview_cols])


if __name__ == "__main__":
    main()