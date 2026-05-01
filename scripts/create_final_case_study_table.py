from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
TABLE_DIR = BASE_DIR / "outputs" / "tables"

CASE_COMPARISON_FILE = TABLE_DIR / "2023_2024_2025_case_study_comparison.csv"
REMIT_CLASSIFICATION_FILE = TABLE_DIR / "2025_case_remit_context_final_classification.csv"

OUTPUT_FILE = TABLE_DIR / "2023_2024_2025_final_case_study_table.csv"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    # utf-8-sig helps Excel read/write cleanly
    return pd.read_csv(path, encoding="utf-8-sig")


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def fix_encoding_text(value):
    text = clean_text(value)

    replacements = {
        "â€“": "–",
        "â€”": "—",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "Â£": "£",
        "Â": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def classify_2025_price_behaviour(row):
    case_type = clean_text(row.get("case_type", ""))

    if "negative_price" in case_type:
        return "Negative-price cluster / lower-tail event"

    if "near_spike" in case_type:
        return "Near-spike / partial upper-tail conversion"

    if "extreme_positive" in case_type:
        return "Extreme positive spike / upper-tail discontinuity"

    return "Positive spike event / upper-tail price stress"


def classify_2025_regime_interpretation(row):
    regime = clean_text(row.get("regime_group", ""))
    driver = clean_text(row.get("internal_driver_summary", ""))

    if regime == "jan_spike_stress":
        return (
            "January 2025 represents a clear scarcity-led upper-tail regime, where "
            "very low wind output, very high gas generation and system tightness "
            "created repeated positive imbalance price stress."
        )

    if regime == "jun_mixed_tail":
        return (
            "June 2025 represents a mixed-tail regime, where both positive spike risk "
            "and negative-price risk appeared depending on the direction of imbalance, "
            "wind output and interconnector support."
        )

    if regime == "jul_sep_surplus":
        return (
            "July–September 2025 represents a surplus-sensitive regime, where high wind "
            "and negative imbalance increased lower-tail risk, although some evening "
            "near-spike conditions still occurred."
        )

    if regime == "oct_mixed_transition":
        return (
            "October 2025 represents an autumn transition regime, where upper-tail "
            "stress reappeared under low wind, high gas generation and tighter evening "
            "or intraday conditions."
        )

    if regime == "feb_mar_broad_stress":
        return (
            "February–March 2025 represents a broad stress and surplus interaction "
            "period, where high wind and negative imbalance contributed to lower-tail "
            "price formation."
        )

    if regime == "apr_may_surplus_shift":
        return (
            "April–May 2025 represents a surplus-shift regime, where lower thermal "
            "demand and negative imbalance increased exposure to negative or low prices."
        )

    return (
        "This case reflects a regime-dependent price formation pattern where internal "
        f"market conditions were characterised by {driver}."
    )


def classify_2025_paper_use(row):
    case_id = clean_text(row.get("case_id", ""))
    case_type = clean_text(row.get("case_type", ""))

    if "jan_08" in case_id:
        return (
            "Use as the main 2025 upper-tail case study. This event demonstrates the "
            "largest observed 2025 price discontinuity and anchors the 2025 scarcity "
            "extension of the paper."
        )

    if "jan_20" in case_id:
        return (
            "Use as a secondary January scarcity case. It supports the argument that "
            "January 2025 contained repeated scarcity events rather than one isolated spike."
        )

    if "jan_22" in case_id:
        return (
            "Use as a morning-ramp scarcity case. It shows that 2025 upper-tail stress "
            "was not limited to the evening peak."
        )

    if "jun_30" in case_id:
        return (
            "Use as the main summer positive-spike case. It shows that spike risk in "
            "2025 was not purely a winter phenomenon."
        )

    if "jul_01" in case_id:
        return (
            "Use as a near-spike comparison case. It helps explain why stressed "
            "conditions sometimes convert only partially into upper-tail prices."
        )

    if "oct_13" in case_id:
        return (
            "Use as the main autumn transition case. It shows renewed upper-tail "
            "stress under low wind, high gas and tightening system conditions."
        )

    if "oct_14" in case_id or "oct_22" in case_id:
        return (
            "Use as a repeated October evening-spike case. It supports the argument "
            "that autumn 2025 contained recurring mixed-transition stress."
        )

    if "negative_price" in case_type:
        return (
            "Use as a lower-tail comparison case. It shows that the same regime-based "
            "framework can explain negative-price formation as well as positive spikes."
        )

    return (
        "Use as supporting evidence for the 2025 extension of the regime-based "
        "imbalance price formation framework."
    )


def build_final_interpretation(row):
    year = int(row["year"]) if pd.notna(row["year"]) else ""

    case_type = fix_encoding_text(row.get("case_type", ""))
    max_price = fix_encoding_text(row.get("max_price", ""))
    regime_group = fix_encoding_text(row.get("regime_group", ""))
    time_band = fix_encoding_text(row.get("dominant_time_band", ""))
    internal_driver = fix_encoding_text(row.get("internal_driver_summary", ""))
    remit_context = fix_encoding_text(row.get("remit_context_type", ""))
    repeated_assets = fix_encoding_text(row.get("dominant_repeated_assets", ""))
    specific_assets = fix_encoding_text(row.get("dominant_case_specific_assets", ""))

    if year in [2023, 2024]:
        return (
            f"This {year} case provides historical evidence for the regime-based "
            f"price-formation framework. The case reached a maximum price of {max_price} "
            f"in the {regime_group} regime. It is used as part of the 2023–2024 foundation "
            f"showing that imbalance price spikes were linked to system regime conditions "
            f"rather than random isolated events."
        )

    if year == 2025:
        text = (
            f"This 2025 {case_type} case reached a maximum price of {max_price} "
            f"in the {regime_group} regime. The dominant time band was {time_band}. "
            f"The internal market fingerprint was {internal_driver}. "
        )

        if remit_context:
            text += (
                f"The REMIT overlay classifies this case as {remit_context}. "
                f"This means the event should be interpreted primarily through the internal "
                f"market regime, while external asset-availability conditions acted as a "
                f"reinforcing background context. "
            )

        if repeated_assets:
            text += f"The dominant repeated REMIT assets were {repeated_assets}. "

        if specific_assets:
            text += f"Case-specific REMIT assets included {specific_assets}. "

        text += (
            "Therefore, this case supports the paper's central argument that GB imbalance "
            "price tails are regime-led, with REMIT availability evidence acting as a "
            "contextual reinforcement rather than simple one-outage causality."
        )

        return text

    return ""


def main():
    case_df = read_csv(CASE_COMPARISON_FILE)
    remit_df = read_csv(REMIT_CLASSIFICATION_FILE)

    print("Loaded files:")
    print(f"Case comparison rows: {len(case_df)}")
    print(f"REMIT classification rows: {len(remit_df)}")

    # Clean encoding across all text columns
    for df in [case_df, remit_df]:
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(fix_encoding_text)

    remit_cols = [
        "case_id",
        "remit_context_type",
        "dominant_repeated_assets",
        "dominant_case_specific_assets",
    ]

    missing_remit_cols = [c for c in remit_cols if c not in remit_df.columns]
    if missing_remit_cols:
        raise ValueError(f"Missing REMIT columns: {missing_remit_cols}")

    remit_df = remit_df[remit_cols].copy()

    final_df = case_df.merge(
        remit_df,
        on="case_id",
        how="left"
    )

    final_df["remit_context_type"] = final_df["remit_context_type"].fillna(
        "not_reassessed_in_2025_remit_overlay"
    )

    final_df["dominant_repeated_assets"] = final_df["dominant_repeated_assets"].fillna("")
    final_df["dominant_case_specific_assets"] = final_df["dominant_case_specific_assets"].fillna("")

    required_cols = [
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
    ]

    for col in required_cols:
        if col not in final_df.columns:
            final_df[col] = ""

    # Fill missing 2025 explanatory columns
    mask_2025 = final_df["year"].astype(str) == "2025"

    final_df.loc[mask_2025, "price_behaviour"] = final_df.loc[mask_2025].apply(
        classify_2025_price_behaviour,
        axis=1
    )

    final_df.loc[mask_2025, "regime_interpretation"] = final_df.loc[mask_2025].apply(
        classify_2025_regime_interpretation,
        axis=1
    )

    final_df.loc[mask_2025, "paper_use"] = final_df.loc[mask_2025].apply(
        classify_2025_paper_use,
        axis=1
    )

    final_df["final_paper_interpretation"] = final_df.apply(
        build_final_interpretation,
        axis=1
    )

    # Final encoding clean again
    for col in final_df.columns:
        if final_df[col].dtype == "object":
            final_df[col] = final_df[col].apply(fix_encoding_text)

    final_cols = [
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
        "final_paper_interpretation",
    ]

    final_df = final_df[final_cols]

    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print()
    print("Final paper-ready case-study table created.")
    print(f"Rows: {len(final_df)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print()
    print("Rows by year:")
    print(final_df["year"].value_counts().sort_index())

    print()
    print("Rows by REMIT context:")
    print(final_df["remit_context_type"].value_counts())

    print()
    print("2025 columns now filled check:")
    print(
        final_df.loc[
            final_df["year"].astype(str) == "2025",
            [
                "case_id",
                "price_behaviour",
                "regime_interpretation",
                "paper_use",
            ],
        ].head()
    )


if __name__ == "__main__":
    main()