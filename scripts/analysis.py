import pandas as pd

def build_interconnector_condition_table(file_path, year):
    df = pd.read_csv(file_path)
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["spike_flag"] = (df["systemSellPrice"] >= 250).astype(int)

    p10 = df["interconnectors"].quantile(0.10)
    p25 = df["interconnectors"].quantile(0.25)
    p75 = df["interconnectors"].quantile(0.75)
    p90 = df["interconnectors"].quantile(0.90)

    conditions = {
        "interconnectors_lt_p25": df["interconnectors"] < p25,
        "interconnectors_lt_p10": df["interconnectors"] < p10,
        "interconnectors_gt_p75": df["interconnectors"] > p75,
        "interconnectors_gt_p90": df["interconnectors"] > p90,
    }

    rows = []
    for name, condition in conditions.items():
        periods_meeting_condition = int(condition.sum())
        spike_periods_within_condition = int((df["spike_flag"] & condition).sum())
        probability = (
            spike_periods_within_condition / periods_meeting_condition
            if periods_meeting_condition > 0 else 0
        )

        rows.append({
            "year": year,
            "condition": name,
            "threshold_value": round(
                p25 if name == "interconnectors_lt_p25"
                else p10 if name == "interconnectors_lt_p10"
                else p75 if name == "interconnectors_gt_p75"
                else p90,
                4
            ),
            "periods_meeting_condition": periods_meeting_condition,
            "spike_periods_within_condition": spike_periods_within_condition,
            "spike_probability_given_condition": round(probability, 4)
        })

    return pd.DataFrame(rows)

table_2023 = build_interconnector_condition_table("data/processed/market_master_2023_full_year.csv", 2023)
table_2024 = build_interconnector_condition_table("data/processed/market_master_2024_full_year.csv", 2024)

table = pd.concat([table_2023, table_2024], ignore_index=True)
table.to_csv("outputs/tables/2023_2024_interconnector_condition_table.csv", index=False)

print("\n2023 VS 2024 INTERCONNECTOR CONDITION TABLE")
print(table)
print("\nSaved: outputs/tables/2023_2024_interconnector_condition_table.csv")