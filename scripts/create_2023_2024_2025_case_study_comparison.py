import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
TABLES_DIR = BASE_DIR / "outputs" / "tables"

OLD_CASE_FILE = TABLES_DIR / "2023_2024_price_event_case_studies.csv"
NEW_CASE_FILE = TABLES_DIR / "2025_case_study_windows.csv"
OUTPUT_FILE = TABLES_DIR / "2023_2024_2025_case_study_comparison.csv"


def enrich_2023_2024_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    The 2023–2024 case-study file has fewer columns than the 2025 case-study file.
    This function adds paper-ready interpretation fields for the older cases.
    """

    enriched_rows = []

    for _, row in df.iterrows():
        year = int(row.get("year"))
        case_id = str(row.get("case_id", ""))
        max_price = row.get("max_price", None)
        regime_group = str(row.get("regime_group", ""))

        # Defaults
        case_type = "positive_spike_case"
        price_behaviour = "Positive spike event"
        internal_driver_summary = ""
        regime_interpretation = ""
        paper_use = ""

        if year == 2023:
            case_type = "q1_compound_scarcity_spike"
            internal_driver_summary = "compound_scarcity+q1_stress+upper_tail_spike"
            price_behaviour = "Major positive spike event"
            regime_interpretation = (
                "Q1 2023 represents a compound scarcity architecture where elevated price risk "
                "was linked to broad system stress rather than a single isolated driver."
            )
            paper_use = (
                "Use as the main 2023 stress benchmark. This case anchors the paper's argument "
                "that 2023 upper-tail imbalance prices were concentrated in a Q1 scarcity regime."
            )

        elif year == 2024 and "oct" in regime_group.lower():
            case_type = "late_year_transition_spike"
            internal_driver_summary = "late_year_transition+upper_tail_return"
            price_behaviour = "Positive spike event"
            regime_interpretation = (
                "October–November 2024 marks a late-year transition regime where upper-tail "
                "stress began to reappear after a quiet first half of the year."
            )
            paper_use = (
                "Use as a transition case showing that 2024 stress did not emerge in Q1 like 2023, "
                "but began to return later in the year."
            )

        elif year == 2024 and "dec" in regime_group.lower():
            case_type = "december_physical_scarcity_spike"
            internal_driver_summary = "physical_scarcity+low_wind+high_gas+december_stress"
            price_behaviour = "Positive spike event"
            regime_interpretation = (
                "December 2024 represents the main physical scarcity regime of 2024, with upper-tail "
                "events linked to tighter physical system conditions."
            )
            paper_use = (
                "Use as the main 2024 stress benchmark. This case supports the argument that 2024 "
                "scarcity was late-year and physically driven, unlike the broader Q1 2023 stress regime."
            )

        enriched_rows.append(
            {
                "source_period": "2023_2024",
                "year": year,
                "case_id": case_id,
                "case_type": case_type,
                "event_window_start": row.get("date", ""),
                "event_window_end": "",
                "max_price": max_price,
                "min_price": "",
                "avg_price": "",
                "dominant_time_band": row.get("time_bands", ""),
                "regime_group": regime_group,
                "avg_imbalance": "",
                "avg_wind": "",
                "avg_gas": "",
                "avg_interconnectors": "",
                "internal_driver_summary": internal_driver_summary,
                "price_behaviour": price_behaviour,
                "regime_interpretation": regime_interpretation,
                "paper_use": paper_use,
            }
        )

    return pd.DataFrame(enriched_rows)


def prepare_2025_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise the richer 2025 case-study file into the same comparison format.
    """

    required_cols = [
        "case_id",
        "year",
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
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    out = df[required_cols].copy()
    out.insert(0, "source_period", "2025")

    return out


def main():
    if not OLD_CASE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {OLD_CASE_FILE}")

    if not NEW_CASE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {NEW_CASE_FILE}")

    old_cases = pd.read_csv(OLD_CASE_FILE)
    new_cases = pd.read_csv(NEW_CASE_FILE)

    print("2023–2024 columns:")
    print(list(old_cases.columns))
    print()
    print("2025 columns:")
    print(list(new_cases.columns))
    print()

    old_prepared = enrich_2023_2024_cases(old_cases)
    new_prepared = prepare_2025_cases(new_cases)

    combined = pd.concat([old_prepared, new_prepared], ignore_index=True)

    combined = combined.sort_values(
        by=["year", "case_id"],
        ascending=[True, True]
    ).reset_index(drop=True)

    combined.to_csv(OUTPUT_FILE, index=False)

    print("Combined case-study comparison created successfully.")
    print(f"Rows: {len(combined)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print()
    print("Rows by year:")
    print(combined["year"].value_counts().sort_index())
    print()
    print("Rows by case type:")
    print(combined["case_type"].value_counts())


if __name__ == "__main__":
    main()