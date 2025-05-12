from scipy.stats import norm
from math import log, sqrt, exp
import yfinance as yf

def score(symbol):
    try:
        S = yf.Ticker(symbol).info['regularMarketPrice']
        K = S  # assume at-the-money
        T = 30 / 365
        r = 0.01
        sigma = 0.25  # fixed or could be inferred

        d1 = (log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)

        call_price = S * norm.cdf(d1) - K * exp(-r*T) * norm.cdf(d2)
        return round(call_price / S, 4)
    except Exception:
        return 0.5