import numpy as np
from scipy.stats import norm
from qmcpy import Sobol
from typing import Dict

class PricingModels:
    def __init__(self):
        self.sobol = Sobol(d=1, scramble=True)
        
    def black_scholes(self, S: float, K: float, T: float, 
                     r: float, sigma: float, option_type: str = 'call') -> Dict:
        """Black-Scholes with Greeks"""
        try:
            d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            
            if option_type == 'call':
                price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
                delta = norm.cdf(d1)
            else:
                price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
                delta = -norm.cdf(-d1)
                
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            vega = S * norm.pdf(d1) * np.sqrt(T) / 100
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                   r * K * np.exp(-r*T) * norm.cdf(d2 if option_type == 'call' else -d2)) / 365
            
            return {
                'price': price,
                'greeks': {
                    'delta': delta,
                    'gamma': gamma,
                    'vega': vega,
                    'theta': theta
                },
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def quasi_monte_carlo(self, S: float, K: float, T: float, 
                         r: float, sigma: float, option_type: str = 'call',
                         n_simulations: int = 10000) -> Dict:
        """QMC pricing with Sobol sequences"""
        try:
            u = self.sobol.random(n_simulations).flatten()
            z = norm.ppf(u)
            ST = S * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*z)
            
            if option_type == 'call':
                payoff = np.maximum(ST - K, 0)
            else:
                payoff = np.maximum(K - ST, 0)
                
            price = np.exp(-r*T) * np.mean(payoff)
            
            # Calculate Greeks using pathwise method
            delta = np.mean(np.where(ST > K, ST/S, 0)) * np.exp(-r*T) if option_type == 'call' else -np.mean(np.where(ST < K, ST/S, 0)) * np.exp(-r*T)
            
            return {
                'price': float(price),
                'greeks': {
                    'delta': float(delta),
                    'gamma': None,  # Would require additional calculations
                    'vega': None,
                    'theta': None
                },
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def binomial_tree(self, S: float, K: float, T: float, 
                     r: float, sigma: float, n_steps: int = 100,
                     option_type: str = 'call', american: bool = False) -> Dict:
        """Binomial tree pricing"""
        try:
            dt = T / n_steps
            u = np.exp(sigma * np.sqrt(dt))
            d = 1 / u
            p = (np.exp(r * dt) - d) / (u - d)
            
            # Price tree
            price_tree = np.zeros((n_steps + 1, n_steps + 1))
            price_tree[0, 0] = S
            for i in range(1, n_steps + 1):
                price_tree[i, 0] = price_tree[i-1, 0] * u
                for j in range(1, i + 1):
                    price_tree[i, j] = price_tree[i-1, j-1] * d
            
            # Payoff at expiration
            payoff_tree = np.zeros((n_steps + 1, n_steps + 1))
            for j in range(n_steps + 1):
                if option_type == 'call':
                    payoff_tree[n_steps, j] = max(price_tree[n_steps, j] - K, 0)
                else:
                    payoff_tree[n_steps, j] = max(K - price_tree[n_steps, j], 0)
            
            # Backward induction
            for i in range(n_steps - 1, -1, -1):
                for j in range(i + 1):
                    if american:
                        if option_type == 'call':
                            intrinsic = max(price_tree[i, j] - K, 0)
                        else:
                            intrinsic = max(K - price_tree[i, j], 0)
                    else:
                        intrinsic = 0
                    
                    discounted = np.exp(-r * dt) * (p * payoff_tree[i+1, j] + (1-p) * payoff_tree[i+1, j+1])
                    payoff_tree[i, j] = max(discounted, intrinsic)
            
            return {
                'price': payoff_tree[0, 0],
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }