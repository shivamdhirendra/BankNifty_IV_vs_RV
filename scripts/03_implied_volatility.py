import pandas as pd
import numpy as np
from scipy.optimize import brentq

ce = pd.read_csv("../data/processed/BANKNIFTY_CE_ATM_daily.csv")
pe = pd.read_csv("../data/processed/BANKNIFTY_PE_ATM_daily.csv")

banknifty = pd.read_csv("../data/processed/BANKNIFTY_daily_2021_2025.csv")
rf = pd.read_csv("../data/processed/RBI_91D_TBill_daily_2021_2025.csv")
dividend = pd.read_csv("../data/processed/BANKNIFTY_dividend_yield_daily_2021_2025.csv")

for df in [ce, pe, banknifty, rf, dividend]:
    df["Date"] = pd.to_datetime(df["Date"])

ce["Expiry"] = pd.to_datetime(ce["Expiry"])
pe["Expiry"] = pd.to_datetime(pe["Expiry"])

print("CE:", ce.shape)
print("PE:", pe.shape)
print("Bank Nifty:", banknifty.shape)
print("Dividend yield:", dividend.shape)
print("Risk-free:", rf.shape)

# merge market inputs
ce = ce.merge(rf[["Date", "Risk_Free_Rate"]], on="Date", how="left")
ce = ce.merge(dividend[["Date", "Dividend_Yield"]], on="Date", how="left")
pe = pe.merge(rf[["Date", "Risk_Free_Rate"]], on="Date", how="left")
pe = pe.merge(dividend[["Date", "Dividend_Yield"]], on="Date", how="left")

print("CE missing risk-free:", ce["Risk_Free_Rate"].isna().sum())
print("CE missing dividend:", ce["Dividend_Yield"].isna().sum())
print("PE missing risk-free:", pe["Risk_Free_Rate"].isna().sum())
print("PE missing dividend:", pe["Dividend_Yield"].isna().sum())

# Black-Scholes pricing functions
from scipy.stats import norm


def black_scholes_call(S, K, T, r, q, sigma):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

    d2 = d1 - sigma * np.sqrt(T)

    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def black_scholes_put(S, K, T, r, q, sigma):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

    d2 = d1 - sigma * np.sqrt(T)

    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)


# solve for implied volatility
def implied_volatility(option_price, S, K, T, r, q, option_type):
    def objective(sigma):
        if option_type == "CE":
            theoretical_price = black_scholes_call(S, K, T, r, q, sigma)
        else:
            theoretical_price = black_scholes_put(S, K, T, r, q, sigma)

        return theoretical_price - option_price

    try:
        return brentq(objective, 0.0001, 5.0)
    except ValueError:
        return np.nan


# check IV on first CE
row = ce.iloc[0]

S = row["Spot"]
K = row["Strike Price"]
T = row["DTE"] / 365
r = row["Risk_Free_Rate"]
q = row["Dividend_Yield"]
market_price = row["Close"]

iv = implied_volatility(market_price, S, K, T, r, q, "CE")

print("Date:", row["Date"])
print("Spot:", S)
print("Strike:", K)
print("DTE:", row["DTE"])
print("Market Price:", market_price)
print("Risk-Free Rate:", r)
print("Dividend Yield:", q)
print("Implied Volatility:", iv)
print("Implied Volatility (%):", iv * 100)


# apply to all CE and PE observations
ce["IV"] = ce.apply(
    lambda row: implied_volatility(
        row["Close"],
        row["Spot"],
        row["Strike Price"],
        row["DTE"] / 365,
        row["Risk_Free_Rate"],
        row["Dividend_Yield"],
        "CE",
    ),
    axis=1,
)

pe["IV"] = pe.apply(
    lambda row: implied_volatility(
        row["Close"],
        row["Spot"],
        row["Strike Price"],
        row["DTE"] / 365,
        row["Risk_Free_Rate"],
        row["Dividend_Yield"],
        "PE",
    ),
    axis=1,
)

print("CE IV missing:", ce["IV"].isna().sum())
print("PE IV missing:", pe["IV"].isna().sum())

print("\nCE IV summary:")
print(ce["IV"].describe())

print("\nPE IV summary:")
print(pe["IV"].describe())

# find failed CE
failed_ce = ce[ce["IV"].isna()]

print(
    failed_ce[
        [
            "Date",
            "Spot",
            "Strike Price",
            "Expiry",
            "DTE",
            "Close",
            "Risk_Free_Rate",
            "Dividend_Yield",
        ]
    ]
)

# checking if there are another numerical anomalies
print("Failed CE:", ce["IV"].isna().sum())
print("Failed PE:", pe["IV"].isna().sum())

print("\nCE IV > 100%:", (ce["IV"] > 1).sum())
print("PE IV > 100%:", (pe["IV"] > 1).sum())

print("\nCE IV <= 0:", (ce["IV"] <= 0).sum())
print("PE IV <= 0:", (pe["IV"] <= 0).sum())


# combine CE and PE into one daily IV
iv_daily = ce[["Date", "IV"]].merge(
    pe[["Date", "IV"]], on="Date", how="inner", suffixes=("_CE", "_PE")
)

iv_daily["IV"] = iv_daily[["IV_CE", "IV_PE"]].mean(axis=1)

print(iv_daily.shape)
print(iv_daily.head())
print("\nMissing daily IV:", iv_daily["IV"].isna().sum())
print("\nDaily IV summary:")
print(iv_daily["IV"].describe())

# SAVE
iv_daily.to_csv("../data/processed/BANKNIFTY_daily_IV_2021_2025.csv", index=False)
