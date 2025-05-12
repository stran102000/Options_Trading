import numpy as np
from typing import Union, Dict, List

def calculate_probability(S: float, K: float, T: float, 
                        sigma: float, r: float = 0.01) -> float:
    """Calculate probability of price being above/below strike"""
    d2 = (np.log(S/K) + (r - 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d2)

def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    return isinstance(symbol, str) and 1 <= len(symbol) <= 5 and symbol.isalpha()

def format_currency(value: Union[float, int]) -> str:
    """Format numeric value as currency"""
    return f"${value:,.2f}"

def calculate_greeks(S: float, K: float, T: float, 
                   sigma: float, r: float = 0.01) -> Dict[str, float]:
    """Calculate option Greeks"""
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - 
            r * K * np.exp(-r*T) * norm.cdf(d1 - sigma*np.sqrt(T)))
    vega = S * norm.pdf(d1) * np.sqrt(T)
    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega
    }