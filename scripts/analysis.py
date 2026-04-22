import pandas as pd

def run_basic_analysis(df_master):
    print("\nFULL 2023 BASIC SUMMARY")

    df_master["spike_flag"] = (df_master["systemSellPrice"] >= 250).astype(int)

    print("Total rows:", len(df_master))
    print("Total spikes:", int(df_master["spike_flag"].sum()))

    middle_rule = (
        (df_master["netImbalanceVolume"] > 150) |
        ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
    )

    summary_table = pd.DataFrame({
        "group": ["all_periods", "signal_periods", "spike_periods"],
        "count": [
            len(df_master),
            int(middle_rule.sum()),
            int(df_master["spike_flag"].sum())
        ],
        "avg_price": [
            df_master["systemSellPrice"].mean(),
            df_master.loc[middle_rule, "systemSellPrice"].mean(),
            df_master.loc[df_master["spike_flag"] == 1, "systemSellPrice"].mean()
        ],
        "avg_imbalance": [
            df_master["netImbalanceVolume"].mean(),
            df_master.loc[middle_rule, "netImbalanceVolume"].mean(),
            df_master.loc[df_master["spike_flag"] == 1, "netImbalanceVolume"].mean()
        ],
        "avg_wind": [
            df_master["wind_gen"].mean(),
            df_master.loc[middle_rule, "wind_gen"].mean(),
            df_master.loc[df_master["spike_flag"] == 1, "wind_gen"].mean()
        ],
        "avg_gas": [
            df_master["gas_gen"].mean(),
            df_master.loc[middle_rule, "gas_gen"].mean(),
            df_master.loc[df_master["spike_flag"] == 1, "gas_gen"].mean()
        ]
    })

    print("\nFULL 2023 DRIVER COMPARISON")
    print(summary_table.round(2))

    print("\nFULL 2023 CONDITIONAL SPIKE PROBABILITY ANALYSIS")

    spike_flag = df_master["systemSellPrice"] >= 250

    conditions = {
        "imbalance_gt_100": df_master["netImbalanceVolume"] > 100,
        "imbalance_gt_150": df_master["netImbalanceVolume"] > 150,
        "wind_lt_11000": df_master["wind_gen"] < 11000,
        "wind_lt_8000": df_master["wind_gen"] < 8000,
        "gas_gt_10000": df_master["gas_gen"] > 10000,
        "gas_gt_15000": df_master["gas_gen"] > 15000,
    }

    for name, condition in conditions.items():
        total_condition_periods = condition.sum()
        spike_given_condition = (spike_flag & condition).sum()
        probability = spike_given_condition / total_condition_periods if total_condition_periods > 0 else 0

        print(f"\nCondition: {name}")
        print("Periods meeting condition:", int(total_condition_periods))
        print("Spike periods within condition:", int(spike_given_condition))
        print("P(spike | condition):", round(probability, 4))

    print("\nFULL 2023 COMBINED CONDITIONAL SPIKE PROBABILITY ANALYSIS")

    hour = df_master["startTime"].dt.hour

    combined_conditions = {
        "imbalance_gt_150_and_gas_gt_15000":
            (df_master["netImbalanceVolume"] > 150) & (df_master["gas_gen"] > 15000),

        "wind_lt_8000_and_gas_gt_15000":
            (df_master["wind_gen"] < 8000) & (df_master["gas_gen"] > 15000),

        "imbalance_gt_150_and_wind_lt_8000":
            (df_master["netImbalanceVolume"] > 150) & (df_master["wind_gen"] < 8000),

        "imbalance_gt_150_and_hour_16_to_19":
            (df_master["netImbalanceVolume"] > 150) & (hour >= 16) & (hour <= 19),

        "wind_lt_8000_and_hour_16_to_19":
            (df_master["wind_gen"] < 8000) & (hour >= 16) & (hour <= 19),

        "gas_gt_15000_and_hour_16_to_19":
            (df_master["gas_gen"] > 15000) & (hour >= 16) & (hour <= 19),
    }

    for name, condition in combined_conditions.items():
        total_condition_periods = condition.sum()
        spike_given_condition = (spike_flag & condition).sum()
        probability = spike_given_condition / total_condition_periods if total_condition_periods > 0 else 0

        print(f"\nCondition: {name}")
        print("Periods meeting condition:", int(total_condition_periods))
        print("Spike periods within condition:", int(spike_given_condition))
        print("P(spike | combined condition):", round(probability, 4))

    print("\nFULL 2023 TRIPLE-CONDITION SPIKE PROBABILITY ANALYSIS")

    triple_conditions = {
        "imbalance_gt_150_and_wind_lt_8000_and_hour_16_to_19":
            (df_master["netImbalanceVolume"] > 150) &
            (df_master["wind_gen"] < 8000) &
            (hour >= 16) & (hour <= 19),

        "imbalance_gt_150_and_gas_gt_15000_and_hour_16_to_19":
            (df_master["netImbalanceVolume"] > 150) &
            (df_master["gas_gen"] > 15000) &
            (hour >= 16) & (hour <= 19),

        "wind_lt_8000_and_gas_gt_15000_and_hour_16_to_19":
            (df_master["wind_gen"] < 8000) &
            (df_master["gas_gen"] > 15000) &
            (hour >= 16) & (hour <= 19),

        "imbalance_gt_150_and_wind_lt_8000_and_gas_gt_15000":
            (df_master["netImbalanceVolume"] > 150) &
            (df_master["wind_gen"] < 8000) &
            (df_master["gas_gen"] > 15000),
    }

    for name, condition in triple_conditions.items():
        total_condition_periods = condition.sum()
        spike_given_condition = (spike_flag & condition).sum()
        probability = spike_given_condition / total_condition_periods if total_condition_periods > 0 else 0

        print(f"\nCondition: {name}")
        print("Periods meeting condition:", int(total_condition_periods))
        print("Spike periods within condition:", int(spike_given_condition))
        print("P(spike | triple condition):", round(probability, 4))