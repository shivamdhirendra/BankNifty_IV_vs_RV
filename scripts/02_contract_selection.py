import pandas as pd

ce = pd.read_csv("../data/processed/BANKNIFTY_CE_2021_2025.csv")
pe = pd.read_csv("../data/processed/BANKNIFTY_PE_2021_2025.csv")
banknifty = pd.read_csv("../data/processed/BANKNIFTY_daily_2021_2025.csv")

for df in [ce, pe, banknifty]:
    df["Date"] = pd.to_datetime(df["Date"])

ce["Expiry"] = pd.to_datetime(ce["Expiry"])
pe["Expiry"] = pd.to_datetime(pe["Expiry"])

print("CE:", ce.shape)
print("PE:", pe.shape)
print("Bank Nifty:", banknifty.shape)


for df in [ce, pe]:
    df["DTE"] = (df["Expiry"] - df["Date"]).dt.days

ce = ce.merge(
    banknifty[["Date", "Close"]], on="Date", how="left", suffixes=("", "_Spot")
)

pe = pe.merge(
    banknifty[["Date", "Close"]], on="Date", how="left", suffixes=("", "_Spot")
)

ce.rename(columns={"Close_Spot": "Spot"}, inplace=True)
pe.rename(columns={"Close_Spot": "Spot"}, inplace=True)

print("CE missing Spot:", ce["Spot"].isna().sum())
print("PE missing Spot:", pe["Spot"].isna().sum())

print("\nCE DTE range:", ce["DTE"].min(), "to", ce["DTE"].max())
print("PE DTE range:", pe["DTE"].min(), "to", pe["DTE"].max())


# which dates are causing mismatch
missing_spot_dates = ce.loc[ce["Spot"].isna(), "Date"].drop_duplicates().sort_values()

print("Missing spot dates:", len(missing_spot_dates))
print(missing_spot_dates.tolist()[:50])

# correct
ce = ce[ce["Spot"].notna()].copy()
pe = pe[pe["Spot"].notna()].copy()

print("CE rows after spot filter:", len(ce))
print("PE rows after spot filter:", len(pe))

# Filter valid option prices + 20–40 DTE
for df in [ce, pe]:
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

ce = ce[(ce["Close"] > 0) & (ce["DTE"].between(20, 40))].copy()
pe = pe[(pe["Close"] > 0) & (pe["DTE"].between(20, 40))].copy()

print("CE after filters:", ce.shape)
print("PE after filters:", pe.shape)

# Distance from ATM
ce["Strike_Distance"] = (ce["Strike Price"] - ce["Spot"]).abs()
pe["Strike_Distance"] = (pe["Strike Price"] - pe["Spot"]).abs()

print(ce[["Date", "Spot", "Strike Price", "Strike_Distance"]].head())

# calculate how far each contract's DTE is from target of 30 days
ce["DTE_Distance"] = (ce["DTE"] - 30).abs()
pe["DTE_Distance"] = (pe["DTE"] - 30).abs()

print(ce[["Date", "Expiry", "DTE", "DTE_Distance"]].head())


# Select ATM contracts
def select_atm(df):
    return (
        df.sort_values(
            ["Date", "Strike_Distance", "DTE_Distance", "Open Int"],
            ascending=[True, True, True, False],
        )
        .drop_duplicates("Date")
        .copy()
    )


ce_atm = select_atm(ce)
pe_atm = select_atm(pe)

print("CE ATM contracts:", ce_atm.shape)
print("PE ATM contracts:", pe_atm.shape)

print(
    ce_atm[["Date", "Spot", "Strike Price", "Expiry", "DTE", "Close", "Open Int"]].head(
        10
    )
)

# SAVE
ce_atm.to_csv("../data/processed/BANKNIFTY_CE_ATM_daily.csv", index=False)
pe_atm.to_csv("../data/processed/BANKNIFTY_PE_ATM_daily.csv", index=False)


# Validation Check
print("CE dates:", len(ce_atm["Date"].unique()))
print("PE dates:", len(pe_atm["Date"].unique()))

common_dates = set(ce_atm["Date"]) & set(pe_atm["Date"])

print("Common dates:", len(common_dates))
print("CE only dates:", len(set(ce_atm["Date"]) - set(pe_atm["Date"])))
print("PE only dates:", len(set(pe_atm["Date"]) - set(ce_atm["Date"])))
