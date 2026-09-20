Using Bank Nifty option prices to measure implied volatility and testing whether that implied volatility can predict future realised volatility of the Bank Nifty.

Time - 1st January 2021 to 31st December 2025 

DATASET                        SOURCE    PURPOSE
1) Bank Nifty daily index      -> NSE    -> Spot price + return
2) Bank Nifty options          -> NSE    -> Option premiums, strikes, expiry, OI, volume
3) 91-day T-bill yield         -> RBI    -> Risk-free rate
4) Bank Nifty dividend yield   -> NSE    -> Dividend yield for BSM


Research Paper Title -> Information Content of Bank Nifty Option-Implied Volatility in Predicting Future Realised Volatility: An Econometric Analysis


Final Project Structure:

BankNifty Implied vs Realised Volatility
|
| Data Collection
| Data Cleaning
| Option Contract Selection
| Black-Scholes Implied Volatility
| Realised Volatility
| Econometric Analysis
     |OLS
     |HAC / Newey-West
     |Diagnostics
     |Robustness
