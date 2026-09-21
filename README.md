# Bank Nifty Implied vs Realised Volatility

## About the Project
This project looks at whether **implied volatility from Bank Nifty options can give an indication of future realised volatility**.
I used Bank Nifty index and options data from **January 2021 to December 2025** and built the analysis step by step in Python.
The main question is: **Does Bank Nifty option-implied volatility contain information about volatility that actually occurs in the following days?**

## Data Used
The project uses:
* Bank Nifty daily price data
* Bank Nifty Call (CE) and Put (PE) option data
* 91-day Government of India Treasury Bill yields
* Bank Nifty dividend-yield data

The data covers **2021–2025**.
The original raw data is not uploaded to GitHub because of file size. Those folders are kept locally and are excluded from GitHub using .gitignore.

## What I Did
**1. Cleaned the data**
Combined the Bank Nifty price and option files and handled missing and non-numeric values.

**2. Selected option contracts**
For each trading day, I selected approximately **30-day-to-expiry, at-the-money options** for both calls and puts.

**3. Calculated implied volatility**
Used the Black–Scholes model and solved backwards from the observed option price to obtain implied volatility.

**4. Calculated realised volatility**
Calculated Bank Nifty log returns and used them to measure realised volatility over future 20-trading-day periods.

**5. Tested the relationship**
Used regression analysis to check whether current implied volatility is related to future realised volatility.

**I also**:
* used HAC/Newey-West standard errors
* controlled for current realised volatility
* repeated the analysis using a 10-day future volatility period as a robustness check

## Main Results
| Model                                     | Observations | IV Coefficient | HAC p-value |    R² |
|                                           |              |                |             |       |
| Baseline: Future 20-day RV                |        1,135 |         0.2381 |     < 0.001 | 0.257 |
| Augmented: Future 20-day RV + Current RV  |        1,115 |         0.1348 |       0.004 | 0.306 |
| Robustness: Future 10-day RV              |        1,141 |         0.2386 |     < 0.001 | 0.202 |

The results show a **positive and statistically significant relationship** between implied volatility and subsequent realised volatility.

The relationship remains significant even after controlling for current realised volatility and when using a shorter 10-day forecasting period.

## Tools Used
* Python
* Pandas
* NumPy
* Statsmodels
* Matplotlib
* VS Code
* Git & GitHub

## What This Project Helped Me Work With
Through this project, I worked with:
* Financial market data
* Options data
* Black–Scholes implied volatility
* Realised volatility
* Time-series data
* Regression analysis
* HAC/Newey-West standard errors
* Data cleaning and processing in Python
* Git and GitHub for project management

## Data Sources
* NSE India — Bank Nifty index and options data
* RBI — Government of India 91-day Treasury Bill data
* NSE India — Bank Nifty dividend-yield data

## Note
This project is an academic research project. The results describe the relationship observed in the **2021–2025 sample** and should not be interpreted as proof of a causal relationship.

## Author
**Shivam Kumar**
MSc Financial Economics, Gokhale Institute of Politics and Economics
