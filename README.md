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
2. Install dependencies:
   ```bash
   pip install yfinance scipy matplotlib pandas numpy