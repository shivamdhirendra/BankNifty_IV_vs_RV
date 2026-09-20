import pandas as pd
from pathlib import Path

# Project folders
index_folder = "../data/raw/BankNiftyDailyPrices"
ce_folder = "../data/raw/BankNiftyOptions_CE"
pe_folder = "../data/raw/BankNiftyOptions_PE"

index_folder = Path(index_folder)
ce_folder = Path(ce_folder)
pe_folder = Path(pe_folder)


# Count and identify every raw files
index_files = sorted(index_folder.glob("*.csv"))
ce_files = sorted(ce_folder.glob("*.csv"))
pe_files = sorted(pe_folder.glob("*.csv"))

print("Bank Nifty price files:", len(index_files))
print("CE option files:", len(ce_files))
print("PE option files:", len(pe_files))

print("\nBank Nifty files:")
for file in index_files:
    print(file.name)

print("\nCE files:", len(ce_files))
print("PE files:", len(pe_files))


# Inspect one file from each dataset
index_sample = pd.read_csv(index_files[0])
ce_sample = pd.read_csv(ce_files[0])
pe_sample = pd.read_csv(pe_files[0])

print("BANK NIFTY PRICE DATA")
print(index_sample.columns.tolist())
print(index_sample.head())

print("\n" + "=" * 60)

print("CE OPTIONS DATA")
print(ce_sample.columns.tolist())
print(ce_sample.head())

print("\n" + "=" * 60)

print("PE OPTIONS DATA")
print(pe_sample.columns.tolist())
print(pe_sample.head())


# Check every option file
expected_columns = [
    "Symbol  ",
    "Date  ",
    "Expiry  ",
    "Option type  ",
    "Strike Price  ",
    "Close  ",
    "No. of contracts  ",
    "Open Int  ",
    "Underlying Value  ",
]


def audit_option_files(files, option_name):
    results = []

    for file in files:
        df = pd.read_csv(file, low_memory=False)

        # Remove extra spaces from column names
        df.columns = df.columns.str.strip()

        # Convert dates
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Expiry"] = pd.to_datetime(df["Expiry"], errors="coerce")

        results.append(
            {
                "File": file.name,
                "Option": option_name,
                "Rows": len(df),
                "First Date": df["Date"].min(),
                "Last Date": df["Date"].max(),
                "Missing Date": df["Date"].isna().sum(),
                "Missing Expiry": df["Expiry"].isna().sum(),
                "Missing Close": df["Close"].isin(["-", "", None]).sum(),
                "Unique Strikes": df["Strike Price"].nunique(),
                "Unique Expiries": df["Expiry"].nunique(),
            }
        )

    return pd.DataFrame(results)


ce_audit = audit_option_files(ce_files, "CE")
pe_audit = audit_option_files(pe_files, "PE")

option_audit = pd.concat([ce_audit, pe_audit], ignore_index=True)

option_audit


# Investigate the Close column in one problematic file
problem_file = ce_files[4]  # 2025 Apr-Jun CE

df_problem = pd.read_csv(problem_file, low_memory=False)

df_problem.columns = df_problem.columns.str.strip()

print("File:", problem_file.name)

print("\nClose data type:")
print(df_problem["Close"].dtype)

print("\nClose value counts for special values:")
print(df_problem["Close"].value_counts(dropna=False).head(15))

print("\nMissing Close:")
print("NaN:", df_problem["Close"].isna().sum())
print("Dash '-':", (df_problem["Close"] == "-").sum())

print("\nSample rows with missing/invalid Close:")
print(df_problem[df_problem["Close"].isna() | (df_problem["Close"] == "-")].head(10))


# Audit all Bank Nifty daily price files
index_results = []

for file in index_files:
    df = pd.read_csv(file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert Close to numeric
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    index_results.append(
        {
            "File": file.name,
            "Rows": len(df),
            "First Date": df["Date"].min(),
            "Last Date": df["Date"].max(),
            "Missing Date": df["Date"].isna().sum(),
            "Missing Close": df["Close"].isna().sum(),
            "Duplicate Dates": df["Date"].duplicated().sum(),
        }
    )

index_audit = pd.DataFrame(index_results)

index_audit


# Combine all Bank Nifty daily price files
index_data = []

for file in index_files:
    df = pd.read_csv(file)

    df.columns = df.columns.str.strip()  # Clean column names

    df["Date"] = pd.to_datetime(
        df["Date"], format="%d-%b-%Y", errors="coerce"
    )  # Convert date

    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # Convert numeric columns

    index_data.append(df)

banknifty = pd.concat(index_data, ignore_index=True)  # Combine

banknifty = banknifty.drop_duplicates(
    subset="Date", keep="first"
)  # Remove duplicate dates

banknifty = banknifty.sort_values("Date").reset_index(drop=True)  # Sort chronologically

print("Rows:", len(banknifty))
print("First date:", banknifty["Date"].min())
print("Last date:", banknifty["Date"].max())
print("Duplicate dates:", banknifty["Date"].duplicated().sum())
print("Missing Close:", banknifty["Close"].isna().sum())

banknifty.head()
# SAVE
banknifty.to_csv("../data/processed/BANKNIFTY_daily_2021_2025.csv", index=False)


# Check total rows
print("Total CE rows:", ce_audit["Rows"].sum())
print("Total PE rows:", pe_audit["Rows"].sum())
print("Total option rows:", ce_audit["Rows"].sum() + pe_audit["Rows"].sum())

# Combine all CE files
ce_data = []

for file in ce_files:
    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()
    ce_data.append(df)

ce_options = pd.concat(ce_data, ignore_index=True)

print("CE rows:", len(ce_options))
print("First date:", ce_options["Date"].min())
print("Last date:", ce_options["Date"].max())
# Python is comparing dates alphabetically rather than chronologically.
# Here, dates are string so convert those innto actual dates.

# Fix CE dates
ce_options["Date"] = pd.to_datetime(
    ce_options["Date"], format="%d-%b-%Y", errors="coerce"
)

ce_options["Expiry"] = pd.to_datetime(
    ce_options["Expiry"], format="%d-%b-%Y", errors="coerce"
)

print("CE rows:", len(ce_options))
print("First date:", ce_options["Date"].min())
print("Last date:", ce_options["Date"].max())
print("Missing dates:", ce_options["Date"].isna().sum())
print("Missing expiries:", ce_options["Expiry"].isna().sum())

# Combine
pe_data = []

for file in pe_files:
    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()
    pe_data.append(df)

pe_options = pd.concat(pe_data, ignore_index=True)

pe_options["Date"] = pd.to_datetime(
    pe_options["Date"], format="%d-%b-%Y", errors="coerce"
)

pe_options["Expiry"] = pd.to_datetime(
    pe_options["Expiry"], format="%d-%b-%Y", errors="coerce"
)

print("PE rows:", len(pe_options))
print("First date:", pe_options["Date"].min())
print("Last date:", pe_options["Date"].max())
print("Missing dates:", pe_options["Date"].isna().sum())
print("Missing expiries:", pe_options["Expiry"].isna().sum())


# Clean numeric columns
numeric_cols = [
    "Strike Price",
    "Open",
    "High",
    "Low",
    "Close",
    "LTP",
    "Settle Price",
    "No. of contracts",
    "Turnover * in  ₹ Lakhs",
    "Premium Turnover ** in   ₹ Lakhs",
    "Open Int",
    "Change in OI",
    "Underlying Value",
]

for col in numeric_cols:
    ce_options[col] = pd.to_numeric(ce_options[col], errors="coerce")
    pe_options[col] = pd.to_numeric(pe_options[col], errors="coerce")

print("CE Close type:", ce_options["Close"].dtype)
print("PE Close type:", pe_options["Close"].dtype)

print("\nCE missing Close:", ce_options["Close"].isna().sum())
print("PE missing Close:", pe_options["Close"].isna().sum())

# Check quality of usable prices
for name, df in [("CE", ce_options), ("PE", pe_options)]:
    print(f"\n{name}")
    print("Zero Close:", (df["Close"] == 0).sum())
    print("Negative Close:", (df["Close"] < 0).sum())
    print("Missing Close:", df["Close"].isna().sum())
    print("Missing OI:", df["Open Int"].isna().sum())
    print("Missing Contracts:", df["No. of contracts"].isna().sum())
    print("Missing Underlying:", df["Underlying Value"].isna().sum())

#
for name, df in [("CE", ce_options), ("PE", pe_options)]:

    valid_close = df["Close"].notna() & (df["Close"] > 0)

    print(f"\n{name}")
    print("Valid Close:", valid_close.sum())
    print("Valid Close + missing OI:", (valid_close & df["Open Int"].isna()).sum())
    print(
        "Valid Close + missing Contracts:",
        (valid_close & df["No. of contracts"].isna()).sum(),
    )
    print(
        "Valid Close + missing Underlying:",
        (valid_close & df["Underlying Value"].isna()).sum(),
    )
# So OI and trading volume cannot be mandatory filters.
# More than half of valid option prices don't have them.
# A valid closing premium is mandatory.


# Create clean option datasets
keep_cols = [
    "Symbol",
    "Date",
    "Expiry",
    "Option type",
    "Strike Price",
    "Close",
    "No. of contracts",
    "Open Int",
    "Underlying Value",
]

ce_clean = ce_options[keep_cols].copy()
pe_clean = pe_options[keep_cols].copy()

print("CE:", ce_clean.shape)
print("PE:", pe_clean.shape)
# SAVE
ce_clean.to_csv("../data/processed/BANKNIFTY_CE_2021_2025.csv", index=False)
pe_clean.to_csv("../data/processed/BANKNIFTY_PE_2021_2025.csv", index=False)


# Load RBI 91-day T-bill data
rbi_file = "../data/external/Auctions of 91-Day Government of India Treasury Bills.xlsx"

rbi = pd.read_excel(rbi_file, header=5)

rbi = rbi[["Date of Auction", "Implicit Yield at Cut-off Price (percent)"]].copy()

rbi["Date of Auction"] = pd.to_datetime(rbi["Date of Auction"], errors="coerce")

rbi["Implicit Yield at Cut-off Price (percent)"] = pd.to_numeric(
    rbi["Implicit Yield at Cut-off Price (percent)"], errors="coerce"
)

# Keep only actual auction observations
rbi = rbi.dropna(
    subset=["Date of Auction", "Implicit Yield at Cut-off Price (percent)"]
)

# Keep our study period
rbi = rbi[
    (rbi["Date of Auction"] >= "2021-01-01") & (rbi["Date of Auction"] <= "2025-12-31")
].copy()

rbi = rbi.sort_values("Date of Auction").reset_index(drop=True)

print("Rows:", len(rbi))
print("First date:", rbi["Date of Auction"].min())
print("Last date:", rbi["Date of Auction"].max())
print("Missing yield:", rbi["Implicit Yield at Cut-off Price (percent)"].isna().sum())

rbi.head()


# Reload RBI data including the previous auction needed for early 2021
rbi_all = pd.read_excel(rbi_file, header=5)

rbi_all = rbi_all[
    ["Date of Auction", "Implicit Yield at Cut-off Price (percent)"]
].copy()

rbi_all["Date of Auction"] = pd.to_datetime(rbi_all["Date of Auction"], errors="coerce")

rbi_all["Implicit Yield at Cut-off Price (percent)"] = pd.to_numeric(
    rbi_all["Implicit Yield at Cut-off Price (percent)"], errors="coerce"
)

rbi_all = rbi_all.dropna()

# Keep the previous auction plus study period
rbi_all = rbi_all[
    (rbi_all["Date of Auction"] >= "2020-12-01")
    & (rbi_all["Date of Auction"] <= "2025-12-31")
].copy()

rbi_all = rbi_all.sort_values("Date of Auction")

# Match each Bank Nifty trading day with the latest available auction yield
rbi_daily = pd.merge_asof(
    banknifty[["Date"]],
    rbi_all,
    left_on="Date",
    right_on="Date of Auction",
    direction="backward",
)

rbi_daily["Risk_Free_Rate"] = (
    rbi_daily["Implicit Yield at Cut-off Price (percent)"] / 100
)

print(rbi_daily.head(10))
print("\nMissing risk-free rates:", rbi_daily["Risk_Free_Rate"].isna().sum())
print("\nFirst risk-free rate:", rbi_daily["Risk_Free_Rate"].iloc[0])
print("\nLast risk-free rate:", rbi_daily["Risk_Free_Rate"].iloc[-1])

# Clean and save RBI 91-day T-bill data
rbi_daily = rbi_daily[["Date", "Risk_Free_Rate"]].copy()
# SAVE
rbi_daily.to_csv("../data/processed/RBI_91D_TBill_daily_2021_2025.csv", index=False)


# Nifty Bank Yield
# Inspect only one file first
yield_files = sorted(Path("../data/external/BankNiftyYield").glob("*.csv"))

print("Yield files:", len(yield_files))

yield_sample = pd.read_csv(yield_files[0])

print("\nColumns:")
print(yield_sample.columns.tolist())

print("\nFirst 5 rows:")
print(yield_sample.head())


# Consolidate
yield_data = []

for file in yield_files:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y", errors="coerce")

    df["Div Yield%"] = pd.to_numeric(df["Div Yield%"], errors="coerce")

    yield_data.append(df[["Date", "Div Yield%"]])

dividend_yield = pd.concat(yield_data, ignore_index=True)

dividend_yield = dividend_yield.drop_duplicates("Date")
dividend_yield = dividend_yield.sort_values("Date").reset_index(drop=True)

dividend_yield["Dividend_Yield"] = (
    dividend_yield["Div Yield%"] / 100
)  # Convert to decimal

print("Rows:", len(dividend_yield))
print("First date:", dividend_yield["Date"].min())
print("Last date:", dividend_yield["Date"].max())
print("Missing dates:", dividend_yield["Date"].isna().sum())
print("Missing dividend yield:", dividend_yield["Dividend_Yield"].isna().sum())

print("\nFirst 5:")
print(dividend_yield.head())


# Missing dividend yield
dividend_daily = pd.merge(
    banknifty[["Date"]],
    dividend_yield[["Date", "Dividend_Yield"]],
    on="Date",
    how="left",
)

print("Trading days:", len(dividend_daily))
print("Missing dividend yield:", dividend_daily["Dividend_Yield"].isna().sum())

print(dividend_daily[dividend_daily["Dividend_Yield"].isna()])

# DY before and after missing date
missing_dates = dividend_daily.loc[dividend_daily["Dividend_Yield"].isna(), "Date"]

for d in missing_dates:
    print("\nAround:", d.date())

    print(
        dividend_yield[
            (dividend_yield["Date"] >= d - pd.Timedelta(days=5))
            & (dividend_yield["Date"] <= d + pd.Timedelta(days=5))
        ][["Date", "Dividend_Yield"]]
    )

# Filling missing values
dividend_daily["Dividend_Yield"] = dividend_daily["Dividend_Yield"].ffill()

print("Missing dividend yield:", dividend_daily["Dividend_Yield"].isna().sum())
print(dividend_daily[dividend_daily["Date"].isin(missing_dates)])

# SAVE
dividend_daily.to_csv(
    "../data/processed/BANKNIFTY_dividend_yield_daily_2021_2025.csv", index=False
)
