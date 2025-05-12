import numpy as np
import yfinance as yf

def score(symbol, num_simulations=10000):
    try:
        S = yf.Ticker(symbol).info['regularMarketPrice']
        K = S
        T = 30 / 365
        r = 0.01
        sigma = 0.25

        Z = np.random.standard_normal(num_simulations)
        ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * sqrt(T) * Z)
        payoff = np.maximum(ST - K, 0)
        expected_price = np.exp(-r * T) * np.mean(payoff)
        return round(expected_price / S, 4)
    except Exception:
        return 0.5