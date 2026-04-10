import pandas as pd

df = pd.read_csv("data/processed/market_master_2023_january.csv")
df["startTime"] = pd.to_datetime(df["startTime"])
df = df.sort_values("startTime").reset_index(drop=True)

# define spike
SPIKE_THRESHOLD = 250
df["spike"] = (df["systemSellPrice"] > SPIKE_THRESHOLD).astype(int)

# define simple imbalance rule
df["imbalance_rule"] = (df["netImbalanceVolume"] > 100).astype(int)

# only look at actual spikes
spikes = df[df["spike"] == 1].copy()

# among spike rows, check whether rule captured them
captured = spikes[spikes["imbalance_rule"] == 1]
missed = spikes[spikes["imbalance_rule"] == 0]

print("Total spikes:", len(spikes))
print("Captured by imbalance > 100:", len(captured))
print("Missed by imbalance > 100:", len(missed))

print("\nCaptured spikes:")
print(captured[[
    "startTime",
    "systemSellPrice",
    "netImbalanceVolume",
    "wind_gen",
    "gas_gen"
]])

print("\nMissed spikes:")
print(missed[[
    "startTime",
    "systemSellPrice",
    "netImbalanceVolume",
    "wind_gen",
    "gas_gen"
]])