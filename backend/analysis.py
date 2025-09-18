"""Backend analysis utilities extracted from options_tradingV2 for API use.
This module avoids any interactive plotting and focuses on data processing that
can be serialized to JSON for the frontend.
"""
from __future__ import annotations
import datetime
import math
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import qmc, norm

# ----------------------------- Utility Functions ----------------------------- #

def get_best_expiration(ticker: str, min_days: int = 7, max_days: int = 60) -> Optional[str]:
    ticker_obj = yf.Ticker(ticker)
    expirations = ticker_obj.options
    now = datetime.datetime.now()
    valid: List[str] = []
    for exp in expirations:
        try:
            exp_date = datetime.datetime.strptime(exp, '%Y-%m-%d')
            days_to_exp = (exp_date - now).days
            if min_days <= days_to_exp <= max_days:
                valid.append(exp)
        except Exception:
            continue
    if valid:
        return min(valid, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
    return None


def fetch_options_data(ticker: str, expiration: str, option_type: str = 'call') -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    try:
        opt = stock.option_chain(expiration)
        return opt.calls if option_type == 'call' else opt.puts
    except Exception:
        return pd.DataFrame()


def compute_sma(options_data: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    if options_data.empty or 'lastPrice' not in options_data.columns:
        return options_data
    options_data = options_data.reset_index(drop=True).copy()
    options_data['SMA'] = options_data['lastPrice'].rolling(window=window).mean()
    return options_data


def generate_signals(options_data: pd.DataFrame, option_type: str) -> pd.DataFrame:
    if options_data.empty or 'lastPrice' not in options_data.columns or 'SMA' not in options_data.columns:
        return options_data
    if option_type == 'call':
        options_data['Signal'] = options_data['lastPrice'] > options_data['SMA']
    elif option_type == 'put':
        options_data['Signal'] = options_data['lastPrice'] < options_data['SMA']
    else:
        options_data['Signal'] = False
    return options_data

# --------------------------- Pricing Implementations ------------------------- #

def quasi_monte_carlo_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str, num_simulations: int = 2**14) -> Tuple[float, float]:
    sampler = qmc.Sobol(d=1, scramble=True)
    samples = sampler.random_base2(m=int(math.log2(num_simulations)))
    Z = norm.ppf(samples).flatten()
    ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * math.sqrt(T) * Z)
    if option_type == 'call':
        payoffs = np.maximum(ST - K, 0)
    else:
        payoffs = np.maximum(K - ST, 0)
    discounted_payoffs = np.exp(-r * T) * payoffs
    price = float(np.mean(discounted_payoffs))
    var_95 = float(np.percentile(discounted_payoffs, 5))  # 95% VaR (5th percentile)
    return price, var_95

# --------------------------- Evaluation / Selection -------------------------- #

def evaluate_trade(option_type: str, market_price: float, mc_price: float, var: float, threshold: float = 0.05, var_threshold: Optional[float] = None) -> str:
    if market_price <= 0:
        return "Invalid market price"
    diff = (mc_price - market_price) / market_price
    if diff >= threshold:
        advice = f"Good trade: {option_type.capitalize()} appears undervalued."
        if var_threshold is not None:
            if var < var_threshold:
                advice += " However, risk is high based on VaR."
            else:
                advice += " Risk level acceptable."
        return advice
    return f"Not recommended: {option_type.capitalize()} not significantly undervalued."

# ------------------------------- Core Pipeline ------------------------------- #

def analyze_ticker(ticker: str, expiration: Optional[str]) -> Dict[str, Any]:
    # Determine expiration if not provided
    if not expiration:
        expiration = get_best_expiration(ticker)
    if not expiration:
        return {"ticker": ticker, "error": "No valid expiration found"}

    # Underlying price
    underlying = yf.Ticker(ticker)
    try:
        S = float(underlying.info.get('regularMarketPrice'))
    except Exception:
        S = None
    if S is None:
        return {"ticker": ticker, "expiration": expiration, "error": "Could not fetch underlying price"}

    # Time to expiration
    expiration_date = datetime.datetime.strptime(expiration, "%Y-%m-%d")
    T_days = (expiration_date - datetime.datetime.now()).days
    T = T_days / 365 if T_days > 0 else 1 / 365

    r = 0.01  # risk-free
    sigma = 0.25  # assumed volatility (could be improved with IV)

    # Fetch chains
    calls = fetch_options_data(ticker, expiration, 'call')
    puts = fetch_options_data(ticker, expiration, 'put')

    calls = compute_sma(calls, 5)
    calls = generate_signals(calls, 'call')
    puts = compute_sma(puts, 5)
    puts = generate_signals(puts, 'put')

    def reduce(df: pd.DataFrame, option_type: str) -> List[Dict[str, Any]]:
        if df.empty:
            return []
        # Focus on a subset around ATM for brevity
        if 'strike' not in df.columns or 'lastPrice' not in df.columns:
            return []
        df = df.copy()
        df['distance'] = (df['strike'] - S).abs()
        df = df.sort_values('distance').head(12)
        rows: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            strike = float(row['strike'])
            last_price = float(row.get('lastPrice', np.nan))
            if math.isnan(last_price):
                continue
            try:
                mc_price, var_95 = quasi_monte_carlo_price(S, strike, T, r, sigma, option_type)
            except Exception:
                mc_price, var_95 = float('nan'), float('nan')
            advice = evaluate_trade(option_type, last_price, mc_price, var_95)
            rows.append({
                'strike': strike,
                'lastPrice': round(last_price, 2),
                'SMA': (round(float(row['SMA']), 2) if not math.isnan(row.get('SMA', np.nan)) else None),
                'Signal': bool(row.get('Signal', False)),
                'mc_price': round(mc_price, 2) if not math.isnan(mc_price) else None,
                'var': round(var_95, 2) if not math.isnan(var_95) else None,
                'advice': advice
            })
        return rows

    return {
        'ticker': ticker,
        'expiration': expiration,
        'underlying_price': round(S, 2),
        'calls': reduce(calls, 'call'),
        'puts': reduce(puts, 'put')
    }


def analyze(tickers: List[str], expiration: Optional[str]) -> Dict[str, Any]:
    results = [analyze_ticker(t.strip().upper(), expiration) for t in tickers if t.strip()]
    return {"results": results}

if __name__ == "__main__":
    # Simple manual test
    print(analyze(["AAPL"], None))
