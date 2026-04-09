import pandas as pd

df = pd.read_csv("data/processed/market_master_2023_january.csv")

print(df.shape)
print(df.columns)
print(df.head())