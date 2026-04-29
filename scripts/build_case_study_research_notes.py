import pandas as pd
from pathlib import Path


INPUT_FILE = Path("outputs/tables/2023_2024_price_event_case_studies.csv")
OUTPUT_FILE = Path("outputs/tables/2023_2024_case_study_research_notes.csv")


def classify_mechanism(row):
    date = row["date"]

    if date == "2023-03-07":
        return "compound_scarcity_with_asset_and_interconnector_stress"

    if date == "2024-10-14":
        return "imbalance_amplified_scarcity_with_generation_availability_stress"

    if date == "2024-12-11":
        return "physical_scarcity_low_wind_high_gas_less_imbalance_driven"

    if date == "2024-12-12":
        return "physical_scarcity_with_interconnector_restriction_and_low_wind"

    return "mixed_price_event_mechanism"


def build_core_argument(row):
    date = row["date"]

    if date == "2023-03-07":
        return (
            "This case shows that the largest 2023 spike was not explained by one variable. "
            "It occurred during Q1 stress, evening peak, low wind, very high gas generation, "
            "strongly positive imbalance, reduced interconnector support, and REMIT-reported "
            "thermal/interconnector availability stress."
        )

    if date == "2024-10-14":
        return (
            "This case shows that the 2024 Oct-Nov transition regime produced a genuine scarcity event. "
            "The price spike coincided with very low wind, high gas generation, strongly positive imbalance, "
            "lower interconnector support, and REMIT-reported generation availability reductions."
        )

    if date == "2024-12-11":
        return (
            "This case shows that December 2024 stress was not always imbalance-triggered. "
            "The event occurred with very low wind and extremely high gas generation, while imbalance was not "
            "the dominant signal. This supports the interpretation of December 2024 as a physical scarcity regime."
        )

    if date == "2024-12-12":
        return (
            "This case shows the role of reduced flexibility during a low-wind, high-gas December stress event. "
            "REMIT evidence points to interconnector restrictions and generation availability reductions during "
            "the same wider event window."
        )

    return "This case supports the broader regime-based interpretation of GB imbalance price formation."


def build_paper_note(row):
    date = row["date"]

    if date == "2023-03-07":
        return (
            "Use this as the main 2023 case study. It connects almost every layer of the paper: "
            "Q1 stress regime, evening-peak amplification, high gas, low wind, positive imbalance, "
            "lower interconnector support, and asset availability constraints."
        )

    if date == "2024-10-14":
        return (
            "Use this as the main Oct-Nov 2024 transition case. It demonstrates that late-year stress began "
            "before December and that imbalance escalation still mattered in 2024 under low-wind/high-gas conditions."
        )

    if date == "2024-12-11":
        return (
            "Use this as the first December 2024 physical scarcity case. It is useful because price rose despite "
            "imbalance not being the dominant driver, supporting the low-wind/high-gas scarcity interpretation."
        )

    if date == "2024-12-12":
        return (
            "Use this as the second December 2024 physical scarcity case. It is especially useful for discussing "
            "interconnector restrictions and reduced cross-border flexibility."
        )

    return "Use as supporting event-level evidence."


def build_causality_caution(row):
    return (
        "Do not claim direct single-asset causality. The evidence supports association: "
        "the price event occurred during stressed internal market conditions and contemporaneous "
        "REMIT-reported availability constraints. Use wording such as 'coincided with', "
        "'was consistent with', 'occurred during', or 'suggests contribution'."
    )


def build_future_2025_use(row):
    date = row["date"]

    if date == "2023-03-07":
        return (
            "When analysing 2025, search for similar compound scarcity signatures: low wind, high gas, "
            "positive imbalance, evening peak, low interconnector support, and REMIT availability stress."
        )

    if date == "2024-10-14":
        return (
            "When analysing 2025, check whether transition-season events show similar imbalance-amplified "
            "scarcity under low wind and high gas."
        )

    if date == "2024-12-11":
        return (
            "When analysing 2025, test whether winter price events occur under physical scarcity even when "
            "imbalance is not extreme."
        )

    if date == "2024-12-12":
        return (
            "When analysing 2025, check whether interconnector restrictions amplify winter low-wind/high-gas "
            "price events."
        )

    return "Use this event type as a comparison template for 2025."


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("Input case-study table is empty.")

    notes = df.copy()

    notes["dominant_mechanism"] = notes.apply(classify_mechanism, axis=1)
    notes["core_argument"] = notes.apply(build_core_argument, axis=1)
    notes["paper_use_note"] = notes.apply(build_paper_note, axis=1)
    notes["causality_caution"] = notes.apply(build_causality_caution, axis=1)
    notes["future_2025_comparison_use"] = notes.apply(build_future_2025_use, axis=1)

    notes["recommended_paper_section"] = "Event-level price formation and structural overlays"

    notes["scenario_label_for_future_model"] = notes["dominant_mechanism"]

    final_cols = [
        "case_id",
        "date",
        "year",
        "price_event",
        "max_price",
        "regime_group",
        "time_bands",
        "dominant_mechanism",
        "internal_market_state",
        "external_events_found",
        "highest_association",
        "core_argument",
        "paper_use_note",
        "causality_caution",
        "future_2025_comparison_use",
        "scenario_label_for_future_model",
        "recommended_paper_section",
    ]

    final_df = notes[final_cols].copy()

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\nCASE STUDY RESEARCH NOTES")
    print(final_df)

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
    