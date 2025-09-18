# Options Trading Analysis Tool

A Python script that analyzes call/put options using:
- **yfinance** for market data  
- **Quasi-Monte Carlo (Sobol sequences)** for pricing  
- **Technical signals (SMA crossover)** for trade identification  
- **Risk assessment (VaR)**  

## Features
- 📊 Auto-selects optimal expiration dates
- 🔍 Identifies undervalued options using QMC pricing
- ⚠️ Calculates 95% Value-at-Risk (VaR) for risk management
- 📈 Real-time visualization of last price vs. SMA
- 🎯 Defaults to analyzing AAPL, AMZN, TGT, TSLA (customizable)

## Installation
1. Ensure Python 3.8+ is installed
2. Install dependencies (CLI only original script):
    ```bash
    pip install yfinance scipy matplotlib pandas numpy
    ```

## Integrated Web Frontend

A Flask API plus HTML/JS frontend lets you run everything in the browser.

### Quick Start
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1   # (PowerShell on Windows)
pip install -r requirements.txt
python api_server.py
```
Visit: http://localhost:5000

### UI Capabilities
- Multiple tickers (comma separated)
- Optional expiration override (blank chooses best 7–60 day expiration)
- Near-ATM subset of calls & puts (12 closest strikes)
- For each option:
   - Last Price, SMA(5), signal
   - Quasi-Monte Carlo valuation (Sobol sequence)
   - 95% VaR of discounted payoff
   - Simple undervaluation advisory
- Chart: Call Last Price vs SMA

### API Endpoint
POST /api/analyze
Body JSON:
```json
{ "tickers": "AAPL,MSFT", "expiration": "2025-01-17" }
```
Response shape:
```json
{
   "results": [
      {
         "ticker": "AAPL",
         "expiration": "2025-01-17",
         "underlying_price": 195.32,
         "calls": [ { "strike": 195, "lastPrice": 4.1, "SMA": 4.2, "Signal": false, "mc_price": 4.35, "var": 0.88, "advice": "Not recommended: Call not significantly undervalued." } ],
         "puts":  [ { "strike": 195, "lastPrice": 3.9, "SMA": 3.8, "Signal": true,  "mc_price": 3.70, "var": 0.75, "advice": "Good trade: Put appears undervalued." } ]
      }
   ]
}
```

### Assumptions & Notes
- Static sigma=0.25 & r=0.01 (enhance with IV later)
- SMA window fixed at 5
- VaR is 5th percentile of discounted payoff distribution
- Quasi Monte Carlo uses Sobol (2^14 samples)

### Potential Enhancements
- Implied volatility integration
- Configurable thresholds & SMA window
- CSV export / caching layer
- WebSocket live updates