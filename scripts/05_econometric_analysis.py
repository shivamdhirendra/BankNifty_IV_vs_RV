import pandas as pd
import numpy as np
import statsmodels.api as sm

analysis = pd.read_csv("../data/processed/IV_vs_Future_RV20_2021_2025.csv")

analysis["Date"] = pd.to_datetime(analysis["Date"])

print("Dataset:", analysis.shape)
print(analysis.head())
print(analysis[["IV", "RV_20"]].describe())


# baseline regression
X = sm.add_constant(analysis["IV"])
y = analysis["RV_20"]

ols_model = sm.OLS(y, X).fit()

print(ols_model.summary())


# HAC / Newey-West standard errors
hac_model = ols_model.get_robustcov_results(cov_type="HAC", maxlags=19)

print(hac_model.summary())


# Augmented Model
banknifty = pd.read_csv("../data/processed/BANKNIFTY_daily_2021_2025.csv")

banknifty["Date"] = pd.to_datetime(banknifty["Date"])
banknifty = banknifty.sort_values("Date").reset_index(drop=True)

banknifty["Return"] = np.log(banknifty["Close"] / banknifty["Close"].shift(1))

banknifty["RV_current"] = (
    banknifty["Return"]
    .rolling(20)
    .apply(lambda x: np.sqrt(252 * np.mean(x**2)), raw=True)
)

analysis = analysis.merge(banknifty[["Date", "RV_current"]], on="Date", how="left")

analysis = analysis.dropna(subset=["RV_current"]).copy()

print(analysis.shape)
print(analysis[["Date", "IV", "RV_current", "RV_20"]].head(10))


X_aug = sm.add_constant(analysis[["IV", "RV_current"]])
y_aug = analysis["RV_20"]

aug_model = sm.OLS(y_aug, X_aug).fit()

print(aug_model.summary())

# agumented hac
aug_hac = aug_model.get_robustcov_results(cov_type="HAC", maxlags=19)

print(aug_hac.summary())


# calculate future 10-day RV
def future_realised_volatility(returns, window=10):
    rv = np.full(len(returns), np.nan)

    for i in range(len(returns) - window):
        future_returns = returns.iloc[i + 1 : i + 1 + window]

        rv[i] = np.sqrt(252 / window * np.sum(future_returns**2))

    return rv


banknifty["RV_10"] = future_realised_volatility(banknifty["Return"], window=10)

print(banknifty[["Date", "RV_10"]].head(10))
print("\nMissing RV10:", banknifty["RV_10"].isna().sum())

# 10-day robustness regression with HAC standard errors
iv_daily = pd.read_csv("../data/processed/BANKNIFTY_daily_IV_2021_2025.csv")
iv_daily["Date"] = pd.to_datetime(iv_daily["Date"])

robustness_10d = (
    iv_daily[["Date", "IV"]]
    .merge(banknifty[["Date", "RV_10"]], on="Date", how="inner")
    .dropna()
)
X_10 = sm.add_constant(robustness_10d["IV"])
y_10 = robustness_10d["RV_10"]

model_10 = sm.OLS(y_10, X_10).fit()
hac_10 = model_10.get_robustcov_results(cov_type="HAC", maxlags=9)

print(hac_10.summary())


# final diagnostic: residual autocorrelation
from statsmodels.stats.stattools import durbin_watson

baseline_residuals = ols_model.resid
augmented_residuals = aug_model.resid

print("Baseline Durbin-Watson:", durbin_watson(baseline_residuals))
print("Augmented Durbin-Watson:", durbin_watson(augmented_residuals))


# Final result tabel
results_table = pd.DataFrame(
    {
        "Model": [
            "Baseline: 20-day RV",
            "Augmented: 20-day RV + Current RV",
            "Robustness: 10-day RV",
        ],
        "Observations": [1135, 1115, len(robustness_10d)],
        "IV Coefficient": [
            ols_model.params["IV"],
            aug_model.params["IV"],
            model_10.params["IV"],
        ],
        "IV HAC p-value": [hac_model.pvalues[1], aug_hac.pvalues[1], hac_10.pvalues[1]],
        "R-squared": [ols_model.rsquared, aug_model.rsquared, model_10.rsquared],
    }
)
print(results_table)


# SAVE
results_table.to_csv("../data/processed/econometric_results.csv", index=False)


# Figure 1: IV vs Future Realised Volatility (with regression line)
import matplotlib.pyplot as plt

X_plot = sm.add_constant(analysis["IV"])
predicted_rv = ols_model.predict(X_plot)

plt.figure(figsize=(8, 6))

plt.scatter(analysis["IV"], analysis["RV_20"], alpha=0.4)

order = np.argsort(analysis["IV"].values)

plt.plot(analysis["IV"].values[order], predicted_rv.values[order], linewidth=2)

plt.xlabel("Option-Implied Volatility (IV)")
plt.ylabel("Future 20-Day Realised Volatility (RV)")
plt.title("Bank Nifty IV and Future 20-Day Realised Volatility")

plt.tight_layout()

plt.savefig("../reports/IV_vs_Future_RV20.png", dpi=300, bbox_inches="tight")
plt.show()


# Figure 2: how IV and future realised volatility move over time
plt.figure(figsize=(10, 6))

plt.plot(analysis["Date"], analysis["IV"], label="Option-Implied Volatility")

plt.plot(analysis["Date"], analysis["RV_20"], label="Future 20-Day Realised Volatility")

plt.xlabel("Date")
plt.ylabel("Volatility")
plt.title("Bank Nifty Implied vs Future Realised Volatility")

plt.legend()
plt.tight_layout()

plt.savefig("../reports/IV_vs_Future_RV20_TimeSeries.png", dpi=300, bbox_inches="tight")
plt.show()
