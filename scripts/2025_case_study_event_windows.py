from pathlib import Path
import pandas as pd


# ============================================================
# 2025 CASE STUDY INTERPRETATION TABLE
# ============================================================
# Purpose:
# Convert the 2025 case-study event windows table into a cleaner
# paper-ready interpretation table.
#
# Input:
# outputs/tables/2025_case_study_event_windows.csv
#
# Output:
# outputs/tables/2025_case_study_interpretation_table.csv
# ============================================================


TABLES_DIR = Path("outputs") / "tables"

INPUT_CANDIDATES = [
    TABLES_DIR / "2025_case_study_event_windows.csv",   # actual file in your folder
    TABLES_DIR / "2025_case_study_windows.csv",
    TABLES_DIR / "2025_price_case_studies.csv",
    TABLES_DIR / "2025_case_study_table.csv",
    TABLES_DIR / "2025_case_studies.csv",
]

OUTPUT_FILE = TABLES_DIR / "2025_case_study_interpretation_table.csv"


def find_input_file():
    """Find the first available case-study input file."""
    for file in INPUT_CANDIDATES:
        if file.exists():
            return file

    print("ERROR: Could not find the input case-study file.")
    print("\nI checked these possible files:")
    for file in INPUT_CANDIDATES:
        print(f" - {file}")

    raise FileNotFoundError("No case-study input file found in outputs/tables")


def classify_price_behaviour(row):
    """Create a simple interpretation of the price behaviour."""

    case_type = str(row.get("case_type", "")).lower()
    max_price = row.get("max_price", None)
    min_price = row.get("min_price", None)

    if "negative" in case_type:
        return "Negative-price cluster / downward-price formation"

    if "extreme" in case_type:
        return "Extreme upward price discontinuity"

    if "near" in case_type:
        return "Moderate positive spike / near-spike conversion"

    if pd.notna(max_price):
        if max_price >= 1000:
            return "Extreme upward price discontinuity"
        elif max_price >= 250:
            return "Positive spike event"
        elif max_price >= 200:
            return "Near-spike event"
        elif max_price >= 150:
            return "Elevated-price event"

    if pd.notna(min_price):
        if min_price < 0:
            return "Lower-tail price event"

    return "Mixed price behaviour"


def classify_regime_interpretation(row):
    """Create a short regime interpretation for the paper."""

    driver = str(row.get("internal_driver_summary", "")).lower()
    case_type = str(row.get("case_type", "")).lower()
    regime = str(row.get("regime_group", "")).lower()

    if "negative" in case_type:
        return (
            "Lower-tail surplus regime where negative imbalance, high wind and/or "
            "weak thermal demand created downward pressure on imbalance prices."
        )

    if "very_high_gas" in driver and "very_low_wind" in driver:
        return (
            "Scarcity-led upper-tail regime where low renewable output required "
            "very high gas generation, raising the probability of imbalance price spikes."
        )

    if "positive_imbalance" in driver or "very_positive_imbalance" in driver:
        return (
            "System-stress regime where positive imbalance amplified price formation, "
            "especially when combined with low wind or reduced interconnector support."
        )

    if "near" in case_type:
        return (
            "Near-scarcity regime where physical tightness was present but did not "
            "always convert into an extreme spike."
        )

    if "oct" in regime or "transition" in regime:
        return (
            "Mixed-transition regime where several drivers interacted but no single "
            "dominant scarcity mechanism fully explains the case."
        )

    return (
        "Mixed regime case where price behaviour reflects the interaction of demand, "
        "wind, gas generation, imbalance and interconnector conditions."
    )


def create_paper_use(row):
    """Create paper-use explanation for each case."""

    case_id = str(row.get("case_id", "")).lower()
    case_type = str(row.get("case_type", "")).lower()
    driver = str(row.get("internal_driver_summary", ""))

    if "jan_08" in case_id:
        return (
            "Use as the main 2025 upper-tail case study. This event demonstrates how "
            "extreme price spikes can emerge from the combination of very high gas "
            "generation, very low wind and sharp intraday price jumps."
        )

    if "jan_20" in case_id:
        return (
            "Use as a secondary January scarcity case. It supports the argument that "
            "January 2025 contained repeated scarcity episodes rather than a single "
            "isolated event."
        )

    if "jan_22" in case_id:
        return (
            "Use to show morning-ramp scarcity. This case is useful because the spike "
            "formed outside the main evening peak."
        )

    if "jun_30" in case_id:
        return (
            "Use to show that 2025 spike risk was not purely a winter phenomenon. "
            "The event links positive imbalance and low interconnector support to "
            "summer mixed-tail stress."
        )

    if "jul_01" in case_id:
        return (
            "Use as a near-spike comparison case. This helps explain why stressed "
            "conditions sometimes stop below the main £250/MWh spike threshold."
        )

    if "oct_13" in case_id:
        return (
            "Use as the main autumn transition case. It shows renewed upper-tail "
            "stress under very low wind, high gas and positive imbalance."
        )

    if "oct_14" in case_id:
        return (
            "Use as a short evening-spike example during the October transition regime."
        )

    if "oct_22" in case_id:
        return (
            "Use as another October evening case to show repeated autumn "
            "mixed-transition stress."
        )

    if "mar_30" in case_id:
        return (
            "Use as a major negative-price case showing strong downward-price "
            "formation under very negative imbalance and high wind."
        )

    if "apr_05" in case_id:
        return (
            "Use as an April surplus-shift case. This supports the interpretation "
            "that spring 2025 moved toward greater lower-tail price exposure."
        )

    if "jun_22" in case_id:
        return (
            "Use as a long negative-price event during the mixed-tail regime. It shows "
            "that June contained both negative-price risk and later positive spike risk."
        )

    if "sep_06" in case_id:
        return (
            "Use as a summer/autumn negative-price case showing surplus persistence "
            "and sharp lower-tail behaviour."
        )

    if "negative" in case_type:
        return (
            "Use as a lower-tail case study to explain negative-price formation under "
            f"{driver}."
        )

    return (
        "Use as a supporting case study to explain the interaction of physical system "
        f"drivers: {driver}."
    )


def main():
    input_file = find_input_file()

    print(f"Reading input file: {input_file}")

    df = pd.read_csv(input_file)

    # Ensure output folder exists
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Create interpretation columns
    df["price_behaviour"] = df.apply(classify_price_behaviour, axis=1)
    df["regime_interpretation"] = df.apply(classify_regime_interpretation, axis=1)
    df["paper_use"] = df.apply(create_paper_use, axis=1)

    # Preferred paper-ready column order
    preferred_columns = [
        "case_id",
        "year",
        "case_type",
        "event_window_start",
        "event_window_end",
        "events_found",
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
        "api_from",
        "api_to",
    ]

    # Keep only columns that exist
    output_columns = [col for col in preferred_columns if col in df.columns]

    output_df = df[output_columns].copy()

    # Save output
    output_df.to_csv(OUTPUT_FILE, index=False)

    print("\n2025 CASE STUDY INTERPRETATION TABLE")
    print(output_df)

    print(f"\nSaved to: {OUTPUT_FILE}")

    print("\nCHECK")
    print(f"Rows: {len(output_df)}")

    if "case_type" in output_df.columns:
        print("\nCase types:")
        print(output_df["case_type"].value_counts())


if __name__ == "__main__":
    main()