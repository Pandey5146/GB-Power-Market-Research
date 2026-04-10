import matplotlib.pyplot as plt

def run_basic_analysis(df_master):

    print(df_master.describe())

    corr = df_master.corr(numeric_only=True)
    corr_price = corr["systemSellPrice"].sort_values(ascending=False)

    print("\nCorrelation with Price:\n")
    print(corr_price)

    # Hourly analysis
    df_master["hour"] = df_master["startTime"].dt.hour

    hourly_price = df_master.groupby("hour")["systemSellPrice"].mean()

    print("\nAverage Price by Hour:\n")
    print(hourly_price)

    df_master["price_event"] = "normal"
    df_master.loc[df_master["systemSellPrice"] < 0, "price_event"] = "negative_price"
    df_master.loc[df_master["systemSellPrice"] >= 200, "price_event"] = "high_price"
    df_master.loc[df_master["systemSellPrice"] >= 250, "price_event"] = "extreme_price"
    print("\nPrice Event Counts:")
    print(df_master["price_event"].value_counts())
    print("\nAverage Imbalance by Price Event:")
    print(df_master.groupby("price_event")["netImbalanceVolume"].mean())
    print("\nAverage Wind by Price Event:")
    print(df_master.groupby("price_event")["wind_gen"].mean())
    print("\nAverage Gas by Price Event:")
    print(df_master.groupby("price_event")["gas_gen"].mean())

    # ==============================
    # STEP 7 — VOLATILITY ANALYSIS
    # ==============================

    print("\nPrice Standard Deviation:")
    print(df_master["systemSellPrice"].std())

    print("\nTop 5 Highest Prices:")
    print(df_master.nlargest(5, "systemSellPrice")[["startTime", "systemSellPrice"]])

    print("\nTop 5 Lowest Prices:")
    print(df_master.nsmallest(5, "systemSellPrice")[["startTime", "systemSellPrice"]])

    # ==============================
    # # STEP 13 — SIMPLE SPIKE RULE
    # # ==============================
    df_master["spike_flag"] = df_master["systemSellPrice"] >= 250
    # Check how many spikes happen above threshold imbalance
    threshold = 100
    spike_subset = df_master[df_master["spike_flag"] == True]
    high_imbalance_spikes = spike_subset[spike_subset["netImbalanceVolume"] > threshold]
    print("\nTotal spikes:", len(spike_subset))
    print("Spikes with imbalance > 100:", len(high_imbalance_spikes))
    print("\nPercentage of spikes explained by imbalance > 100:")
    print(len(high_imbalance_spikes) / len(spike_subset))

    # ==============================
    # # STEP 12 — IMBALANCE THRESHOLDS
    # # ==============================
    print("\nImbalance Distribution:")
    print(df_master["netImbalanceVolume"].describe())
    # Check imbalance for extreme prices only
    extreme = df_master[df_master["price_event"] == "extreme_price"]
    print("\nExtreme Price Imbalance Stats:")
    print(extreme["netImbalanceVolume"].describe())

    # ==============================
    # # STEP 14 — MULTI-FACTOR SPIKE ANALYSIS
    # ==============================
    # Define spike
    df_master["spike_flag"] = df_master["systemSellPrice"] >= 250
    
    # Conditions
    df_master["high_imbalance"] = df_master["netImbalanceVolume"] > 100
    df_master["low_wind"] = df_master["wind_gen"] < 8000
    df_master["high_gas"] = df_master["gas_gen"] > 8000
    
    # Check how many spikes meet ALL conditions
    multi_condition = df_master[
    (df_master["spike_flag"]) &
    (df_master["high_imbalance"]) &
    (df_master["low_wind"]) &
    (df_master["high_gas"])
    ]
    print("\nSpikes explained by multi-factor model:")
    print(len(multi_condition))
    print("Total spikes:", df_master["spike_flag"].sum())
    print("\nPercentage explained:")
    print(len(multi_condition) / df_master["spike_flag"].sum())

    # ==============================
    # # STEP 15 — IMPROVED MODEL
    # # ==============================
    df_master["spike_flag"] = df_master["systemSellPrice"] >= 250
    
    # Conditions
    high_imbalance = df_master["netImbalanceVolume"] > 100
    low_wind = df_master["wind_gen"] < 11000
    high_gas = df_master["gas_gen"] > 8000
    
    # New logic (OR instead of AND)
    df_master["model_signal"] = (
    high_imbalance |
    (low_wind & high_gas)
    )
    model_hits = df_master[
    (df_master["spike_flag"]) &
    (df_master["model_signal"])
    ]
    print("\nImproved model results:")
    print("Explained spikes:", len(model_hits))
    print("Total spikes:", df_master["spike_flag"].sum())
    print("Spike recall:", len(model_hits) / df_master["spike_flag"].sum())

    missed_spikes = df_master[
    (df_master["spike_flag"]) &
    (~df_master["model_signal"])
    ]
    print("\nMissed spikes by improved model:")
    print(missed_spikes[[
    "startTime",
    "systemSellPrice",
    "netImbalanceVolume",
    "wind_gen",
    "gas_gen"
    ]])
    print("\nTHRESHOLD SENSITIVITY ANALYSIS")
    thresholds = [200, 250, 300]

    for spike_threshold in thresholds:
        spike_flag = df_master["systemSellPrice"] >= spike_threshold

        imbalance_rule = df_master["netImbalanceVolume"] > 100
        hybrid_rule = (
            (df_master["netImbalanceVolume"] > 100) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 8000))
        )

        total_spikes = spike_flag.sum()
        imbalance_hits = (spike_flag & imbalance_rule).sum()
        hybrid_hits = (spike_flag & hybrid_rule).sum()

        print(f"\nSpike threshold >= {spike_threshold}")
        print("Total spikes:", total_spikes)
        print("Imbalance-only hits:", imbalance_hits)
        print("Imbalance-only recall:", imbalance_hits / total_spikes if total_spikes > 0 else 0)
        print("Hybrid model hits:", hybrid_hits)
        print("Hybrid model recall:", hybrid_hits / total_spikes if total_spikes > 0 else 0)
        
        print("\nPRECISION CHECK FOR THRESHOLD >= 250")
        spike_flag = df_master["systemSellPrice"] >= 250
        hybrid_rule = (
            (df_master["netImbalanceVolume"] > 100) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 8000))
        )
        true_positives = (spike_flag & hybrid_rule).sum()
        false_positives = ((~spike_flag) & hybrid_rule).sum()
        predicted_spikes = hybrid_rule.sum()
        print("Predicted spike signals:", predicted_spikes)
        print("True positives:", true_positives)
        print("False positives:", false_positives)
        print("Precision:", true_positives / predicted_spikes if predicted_spikes > 0 else 0)

        print("\nSTRICTER RULE TEST FOR THRESHOLD >= 250")
        
        spike_flag = df_master["systemSellPrice"] >= 250
        stricter_rule = (
            (df_master["netImbalanceVolume"] > 200) |
            ((df_master["wind_gen"] < 9000) & (df_master["gas_gen"] > 15000))
        )
        true_positives = (spike_flag & stricter_rule).sum()
        false_positives = ((~spike_flag) & stricter_rule).sum()
        predicted_spikes = stricter_rule.sum()
        recall = true_positives / spike_flag.sum() if spike_flag.sum() > 0 else 0
        precision = true_positives / predicted_spikes if predicted_spikes > 0 else 0
        print("Predicted spike signals:", predicted_spikes)
        print("True positives:", true_positives)
        print("False positives:", false_positives)
        print("Recall:", recall)
        print("Precision:", precision)

        print("\nMISSED SPIKES UNDER STRICTER RULE")
        missed_stricter = df_master[
            spike_flag & (~stricter_rule)
        ]
        print(missed_stricter[[
            "startTime",
            "systemSellPrice",
            "netImbalanceVolume",
            "wind_gen",
            "gas_gen"
        ]])

        print("\nMIDDLE RULE TEST FOR THRESHOLD >= 250")
        spike_flag = df_master["systemSellPrice"] >= 250
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        true_positives = (spike_flag & middle_rule).sum()
        false_positives = ((~spike_flag) & middle_rule).sum()
        predicted_spikes = middle_rule.sum()
        recall = true_positives / spike_flag.sum() if spike_flag.sum() > 0 else 0
        precision = true_positives / predicted_spikes if predicted_spikes > 0 else 0
        print("Predicted spike signals:", predicted_spikes)
        print("True positives:", true_positives)
        print("False positives:", false_positives)
        print("Recall:", recall)
        print("Precision:", precision)
    
     # ==============================
     # # STEP 8 — VISUAL ANALYSIS
     # # ==============================
     # # Wind vs Price
    plt.figure()
    plt.scatter(df_master["wind_gen"], df_master["systemSellPrice"])
    plt.xlabel("Wind Generation")
    plt.ylabel("System Price")
    plt.title("Wind vs Price")
    plt.show()
    
    # Gas vs Price
    plt.figure()
    plt.scatter(df_master["gas_gen"], df_master["systemSellPrice"])
    plt.xlabel("Gas Generation")
    plt.ylabel("System Price")
    plt.title("Gas vs Price")
    plt.show()
    
    # Imbalance vs Price
    plt.figure()
    plt.scatter(df_master["netImbalanceVolume"], df_master["systemSellPrice"])
    plt.xlabel("Net Imbalance Volume")
    plt.ylabel("System Price")
    plt.title("Imbalance vs Price")
    plt.show()


