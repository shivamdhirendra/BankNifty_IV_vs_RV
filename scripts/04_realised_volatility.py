import pandas as pd
import numpy as np

banknifty = pd.read_csv("../data/processed/BANKNIFTY_daily_2021_2025.csv")

iv_daily = pd.read_csv("../data/processed/BANKNIFTY_daily_IV_2021_2025.csv")

banknifty["Date"] = pd.to_datetime(banknifty["Date"])
iv_daily["Date"] = pd.to_datetime(iv_daily["Date"])

banknifty = banknifty.sort_values("Date").reset_index(drop=True)
iv_daily = iv_daily.sort_values("Date").reset_index(drop=True)

print("Bank Nifty:", banknifty.shape)
print("Daily IV:", iv_daily.shape)


# calculate Bank Nifty returns
banknifty["Return"] = np.log(banknifty["Close"] / banknifty["Close"].shift(1))

print(banknifty[["Date", "Close", "Return"]].head())
print("\nMissing returns:", banknifty["Return"].isna().sum())


# calculate future 20-day realised volatility
def future_realised_volatility(returns, window=20):
    rv = np.full(len(returns), np.nan)

    for i in range(len(returns) - window):
        future_returns = returns.iloc[i + 1 : i + 1 + window]

        rv[i] = np.sqrt(252 / window * np.sum(future_returns**2))

    return rv


banknifty["RV_20"] = future_realised_volatility(banknifty["Return"], window=20)

print(banknifty[["Date", "Return", "RV_20"]].head(10))
print("\nMissing RV:", banknifty["RV_20"].isna().sum())

# merge IV with future RV
analysis = iv_daily[["Date", "IV"]].merge(
    banknifty[["Date", "RV_20"]], on="Date", how="inner"
)

analysis = analysis.dropna(subset=["IV", "RV_20"]).copy()

print("Analysis dataset:", analysis.shape)

print("\nFirst observations:")
print(analysis.head(10))

print("\nMissing values:")
print(analysis[["IV", "RV_20"]].isna().sum())

print("\nSummary:")
print(analysis[["IV", "RV_20"]].describe())

# SAVE
analysis.to_csv("../data/processed/IV_vs_Future_RV20_2021_2025.csv", index=False)
