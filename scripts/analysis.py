import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

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

        print("\nFALSE POSITIVE PRICE ANALYSIS FOR MIDDLE RULE")
        
        spike_flag = df_master["systemSellPrice"] >= 250
        
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        
        false_positive_rows = df_master[(~spike_flag) & (middle_rule)].copy()
        print("Total false positives:", len(false_positive_rows))
        print("\nFalse positive price summary:")
        print(false_positive_rows["systemSellPrice"].describe())
        print("\nTop 10 highest false positive prices:")
        print(false_positive_rows.nlargest(10, "systemSellPrice")[[
            "startTime",
            "systemSellPrice",
            "netImbalanceVolume",
            "wind_gen",
            "gas_gen"
        ]])

        print("\nPRICE BAND ANALYSIS FOR MIDDLE RULE")
        
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        
        df_band = df_master.copy()
        
        df_band["price_band"] = pd.cut(
            df_band["systemSellPrice"],
            bins=[-9999, 0, 100, 200, 250, 9999],
            labels=["negative", "0_to_100", "100_to_200", "200_to_250", "250_plus"]
        )
        
        signal_band_counts = df_band[middle_rule]["price_band"].value_counts().sort_index()
        
        print(signal_band_counts)

        print("\nAVERAGE PRICE COMPARISON")
        
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        
        all_avg_price = df_master["systemSellPrice"].mean()
        signal_avg_price = df_master.loc[middle_rule, "systemSellPrice"].mean()
        spike_avg_price = df_master.loc[df_master["systemSellPrice"] >= 250, "systemSellPrice"].mean()
        print("Average price - all periods:", round(all_avg_price, 2))
        print("Average price - model signal periods:", round(signal_avg_price, 2))
        print("Average price - spike periods:", round(spike_avg_price, 2))

        print("\nDRIVER COMPARISON: ALL vs SIGNAL vs SPIKE")
        
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        
        spike_flag = df_master["systemSellPrice"] >= 250
        summary_table = pd.DataFrame({
            "group": ["all_periods", "signal_periods", "spike_periods"],
            "avg_price": [
                df_master["systemSellPrice"].mean(),
                df_master.loc[middle_rule, "systemSellPrice"].mean(),
                df_master.loc[spike_flag, "systemSellPrice"].mean()
            ],
            
            "avg_imbalance": [
                df_master["netImbalanceVolume"].mean(),
                df_master.loc[middle_rule, "netImbalanceVolume"].mean(),
                df_master.loc[spike_flag, "netImbalanceVolume"].mean()
            ],
            
            "avg_wind": [
                df_master["wind_gen"].mean(),
                df_master.loc[middle_rule, "wind_gen"].mean(),
                df_master.loc[spike_flag, "wind_gen"].mean()
            ],
            
            "avg_gas": [
                df_master["gas_gen"].mean(),
                df_master.loc[middle_rule, "gas_gen"].mean(),
                df_master.loc[spike_flag, "gas_gen"].mean()
            ]
        })
        
        print(summary_table.round(2))

        print("\nTIME-OF-DAY COMPARISON: ALL vs SIGNAL vs SPIKE")
        
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        
        spike_flag = df_master["systemSellPrice"] >= 250
        df_master["hour"] = df_master["startTime"].dt.hour
        
        print("\nAverage price by hour - all periods:")
        print(df_master.groupby("hour")["systemSellPrice"].mean().round(2))
        print("\nSignal count by hour:")
        print(df_master.loc[middle_rule].groupby("hour").size())
        print("\nSpike count by hour:")
        print(df_master.loc[spike_flag].groupby("hour").size())

        print("\nJANUARY REGIME SUMMARY TABLE")
        
        middle_rule = (
            (df_master["netImbalanceVolume"] > 150) |
            ((df_master["wind_gen"] < 11000) & (df_master["gas_gen"] > 10000))
        )
        
        spike_flag = df_master["systemSellPrice"] >= 250
        summary_table = pd.DataFrame({
            "group": ["all_periods", "signal_periods", "spike_periods"],
            "count": [
                len(df_master),
                middle_rule.sum(),
                spike_flag.sum()
            ],
        
        "avg_price": [
            df_master["systemSellPrice"].mean(),
            df_master.loc[middle_rule, "systemSellPrice"].mean(),
            df_master.loc[spike_flag, "systemSellPrice"].mean()
            ],
        
        "avg_imbalance": [
            df_master["netImbalanceVolume"].mean(),
            df_master.loc[middle_rule, "netImbalanceVolume"].mean(),
            df_master.loc[spike_flag, "netImbalanceVolume"].mean()
            ],
        
        "avg_wind": [
            df_master["wind_gen"].mean(),
            df_master.loc[middle_rule, "wind_gen"].mean(),
            df_master.loc[spike_flag, "wind_gen"].mean()
            ],
        
        "avg_gas": [
            df_master["gas_gen"].mean(),
            df_master.loc[middle_rule, "gas_gen"].mean(),
            df_master.loc[spike_flag, "gas_gen"].mean()
            ]
        })
        
        print(summary_table.round(2))

        print("\nCONDITIONAL SPIKE PROBABILITY ANALYSIS")
        
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
            print("Periods meeting condition:", total_condition_periods)
            print("Spike periods within condition:", spike_given_condition)
            print("P(spike | condition):", round(probability, 4))
        
        print("\nCOMBINED CONDITIONAL SPIKE PROBABILITY ANALYSIS")
        spike_flag = df_master["systemSellPrice"] >= 250
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
            print("Periods meeting condition:", total_condition_periods)
            print("Spike periods within condition:", spike_given_condition)
            print("P(spike | combined condition):", round(probability, 4))
        
        print("\nTRIPLE-CONDITION SPIKE PROBABILITY ANALYSIS")
        spike_flag = df_master["systemSellPrice"] >= 250
        hour = df_master["startTime"].dt.hour
        
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
            print("Periods meeting condition:", total_condition_periods)
            print("Spike periods within condition:", spike_given_condition)
            print("P(spike | triple condition):", round(probability, 4))

        print("\nLOGISTIC REGRESSION: SPIKE PROBABILITY MODEL")
        # target
        df_logit = df_master.copy()
        df_logit["spike_flag"] = (df_logit["systemSellPrice"] >= 250).astype(int)
        df_logit["hour"] = df_logit["startTime"].dt.hour
        
        # features
        feature_cols = ["netImbalanceVolume", "wind_gen", "gas_gen", "hour"]
        X = df_logit[feature_cols]
        y = df_logit["spike_flag"]
        
        # fit model
        logit_model = LogisticRegression(max_iter=1000)
        logit_model.fit(X, y)
        
        # coefficients
        coef_table = pd.DataFrame({
            "feature": feature_cols,
            "coefficient": logit_model.coef_[0]
        })
        
        print("\nModel coefficients:")
        print(coef_table)
        
        # predicted probabilities
        df_logit["predicted_spike_probability"] = logit_model.predict_proba(X)[:, 1]
        print("\nAverage predicted spike probability:")
        print(round(df_logit["predicted_spike_probability"].mean(), 4))
        
        print("\nTop 10 periods by predicted spike probability:")
        print(
            df_logit.sort_values("predicted_spike_probability", ascending=False)[[
                "startTime",
                "systemSellPrice",
                "netImbalanceVolume",
                "wind_gen",
                "gas_gen",
                "hour",
                "predicted_spike_probability"
            ]].head(10)
        )
        
        # optional binary prediction at 0.5 threshold
        df_logit["predicted_spike_class"] = (df_logit["predicted_spike_probability"] >= 0.5).astype(int)
        print("\nConfusion matrix at 0.5 probability threshold:")
        print(confusion_matrix(y, df_logit["predicted_spike_class"]))
        print("\nClassification report at 0.5 probability threshold:")
        print(classification_report(y, df_logit["predicted_spike_class"], digits=3))

        print("\nLOGISTIC REGRESSION THRESHOLD TEST")
        thresholds = [0.10, 0.20, 0.30, 0.40, 0.50]
        
        for threshold in thresholds:
            predicted_class = (df_logit["predicted_spike_probability"] >= threshold).astype(int)
            cm = confusion_matrix(y, predicted_class)
            tn, fp, fn, tp = cm.ravel()
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            
            print(f"\nThreshold: {threshold}")
            print("True Positives:", tp)
            print("False Positives:", fp)
            print("False Negatives:", fn)
            print("True Negatives:", tn)
            print("Precision:", round(precision, 4))
            print("Recall:", round(recall, 4))
    
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


