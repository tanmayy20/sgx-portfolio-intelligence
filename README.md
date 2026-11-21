# SGX Portfolio Intelligence

### Singapore Equity Portfolio Management & Risk Analytics

An interactive portfolio analytics platform built with Python and Streamlit to analyse Singapore-listed equities, construct illustrative portfolios, evaluate risk and return, and compare portfolio performance against the Straits Times Index (STI).

**[View Source Code](https://github.com/tanmayy20/sgx-portfolio-intelligence)**

---

## Project Overview

SGX Portfolio Intelligence is a quantitative investment research dashboard designed to explore portfolio construction, asset allocation, diversification and risk management across Singapore's equity market.

The application combines historical market data with portfolio analytics and visualisation tools to provide an integrated view of investment performance and portfolio risk.

It is designed around concepts commonly used in asset management, equity research and portfolio management.

## Key Features

### 1. Singapore Equity Market Analysis
- Analyse a selected universe of Singapore-listed equities.
- Retrieve historical market data using Yahoo Finance.
- Compare individual securities against the Straits Times Index (^STI).
- Explore equity price performance and historical trends.

### 2. Portfolio Construction & Asset Allocation
- Build equal-weighted and custom-weighted portfolios.
- Calculate illustrative portfolio allocations in SGD.
- Examine sector and individual security exposure.
- Assess portfolio concentration and diversification.

### 3. Portfolio Performance Analytics
- Calculate cumulative portfolio returns.
- Evaluate annualised returns and volatility.
- Measure risk-adjusted performance using the Sharpe ratio.
- Analyse historical maximum drawdowns.
- Compare portfolio performance against the STI benchmark.

### 4. Risk Management
- Historical Value at Risk (VaR).
- Conditional Value at Risk (CVaR).
- Portfolio beta relative to the benchmark.
- Rolling volatility analysis.
- Correlation analysis across portfolio holdings.

### 5. Portfolio Optimisation
- Long-only minimum-variance portfolio modelling.
- Maximum-Sharpe portfolio modelling.
- Portfolio risk-return comparisons.
- Random portfolio simulations to explore allocation trade-offs.

---

## Technology Stack

| Technology | Application |
|---|---|
| Python | Core programming and financial calculations |
| Streamlit | Interactive dashboard |
| Pandas & NumPy | Data manipulation and numerical analysis |
| yfinance | Historical market data |
| Plotly | Interactive financial visualisations |
| SciPy | Portfolio optimisation |

---

## Financial Methodology

The application uses historical adjusted price data to calculate portfolio returns and risk metrics.

| Metric | Methodology |
|---|---|
| Annualised Return | Compounded historical returns |
| Annualised Volatility | Daily return standard deviation × √252 |
| Sharpe Ratio | Excess annualised return / annualised volatility |
| Maximum Drawdown | Largest peak-to-trough portfolio decline |
| Beta | Covariance with benchmark / benchmark variance |
| VaR | Historical return distribution |
| CVaR | Average loss beyond the VaR threshold |

Portfolio optimisation uses historical sample estimates and long-only portfolio constraints. Results are sensitive to the selected time period and historical assumptions.

The illustrative risk-free rate is 2.5% annually and is not intended to represent a live Singapore government yield.

---

## Market Universe

The application is configured for Singapore-listed securities using Yahoo Finance ticker symbols with the `.SI` suffix, alongside the Straits Times Index as a benchmark.

Market data availability depends on the external data provider and may vary.

---

## Dashboard Preview

*Screenshots coming soon.*

---

## Installation & Setup

### Prerequisites
- Python 3.10 or newer
- Git
- Internet connection for market data retrieval

### 1. Clone the repository

```bash
git clone https://github.com/tanmayy20/sgx-portfolio-intelligence.git
cd sgx-portfolio-intelligence
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch the application

```bash
streamlit run dashboard.py
```

The dashboard will open locally at:

`http://localhost:8501`


<img width="1440" height="863" alt="image" src="https://github.com/user-attachments/assets/b1defb2c-0960-4a8b-9781-4a2cbd11df21" />

<img width="1440" height="861" alt="image" src="https://github.com/user-attachments/assets/637ac357-8431-44d9-a03f-e1eb3c066be0" />

<img width="1440" height="863" alt="image" src="https://github.com/user-attachments/assets/1364c121-a138-4a31-b32b-0cb6cb43839d" />

<img width="1440" height="857" alt="image" src="https://github.com/user-attachments/assets/15434f5b-b245-45c7-9da3-6bdd4ba36b2f" />

---

## Future Development Roadmap

Potential enhancements include:

- Dividend-adjusted total return analysis.
- Dedicated Singapore REIT analytics.
- Portfolio rebalancing and transaction tracking.
- Historical stress testing and scenario analysis.
- Integration of Singapore government bond yields as a dated risk-free benchmark.
- Multi-currency portfolio analytics.
- Enhanced performance attribution.

---

## Disclaimer

This project is intended for educational and investment research purposes only. It does not constitute financial advice, investment recommendations, or an offer to buy or sell securities.

Historical performance does not guarantee future results. Market data may be delayed, incomplete or inaccurate. All investment decisions should be independently researched and evaluated.

---

## Author

**Tanmay Singh**

GitHub: [@tanmayy20](https://github.com/tanmayy20)

---

*Built as a practical exploration of portfolio management, quantitative investment analysis and financial risk modelling.*
