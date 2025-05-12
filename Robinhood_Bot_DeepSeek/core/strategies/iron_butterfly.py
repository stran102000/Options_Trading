import numpy as np
from scipy.stats import norm
from qmcpy import Sobol
from typing import Dict
from ..pricing_models import PricingModels

class IronButterfly:
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config['enabled']
        self.pricing = PricingModels()
        self.sobol = Sobol(d=1, scramble=True)
        
    def analyze(self, symbol: str, price: float, iv: float) -> Dict:
        """Full strategy analysis with QMC pricing"""
        if not self.enabled:
            return None
            
        strikes = self._calculate_strikes(price)
        days_to_exp = self.config['max_dte']
        t = days_to_exp / 365.25
        
        # Price all legs using QMC
        legs = {
            'sell_call': self._price_option(price, strikes['sell_call'], t, iv, 'call'),
            'sell_put': self._price_option(price, strikes['sell_put'], t, iv, 'put'),
            'buy_call': self._price_option(price, strikes['buy_call'], t, iv, 'call'),
            'buy_put': self._price_option(price, strikes['buy_put'], t, iv, 'put')
        }
        
        # Calculate strategy metrics
        net_credit = legs['sell_call']['price'] + legs['sell_put']['price'] - \
                    legs['buy_call']['price'] - legs['buy_put']['price']
        
        if net_credit < self.config['min_credit']:
            return None
            
        max_loss = (strikes['sell_call'] - strikes['buy_call']) - net_credit
        pop = self._calculate_probability(price, strikes, iv, t)
        
        return {
            'symbol': symbol,
            'strategy': 'iron_butterfly',
            'expiration_days': days_to_exp,
            'strikes': strikes,
            'legs': legs,
            'metrics': {
                'net_credit': net_credit,
                'max_loss': max_loss,
                'probability_of_profit': pop,
                'risk_reward': net_credit / max_loss,
                'greeks': self._calculate_greeks(legs)
            }
        }
    
    def _calculate_strikes(self, price: float) -> Dict:
        """Calculate strikes based on width percentage"""
        width = self.config['width_percent']
        return {
            'sell_call': round(price * (1 + width/2), 2),
            'sell_put': round(price * (1 - width/2), 2),
            'buy_call': round(price * (1 + width), 2),
            'buy_put': round(price * (1 - width), 2)
        }
    
    def _price_option(self, S: float, K: float, T: float, iv: float, option_type: str) -> Dict:
        """Price single option leg"""
        return self.pricing.quasi_monte_carlo(
            S=S, K=K, T=T, r=0.01, sigma=iv,
            option_type=option_type,
            n_simulations=self.config.get('qmc_simulations', 10000)
        )
    
    def _calculate_probability(self, S: float, strikes: Dict, iv: float, T: float) -> float:
        """Calculate probability of profit using QMC"""
        u = self.sobol.random(5000).flatten()
        z = norm.ppf(u)
        ST = S * np.exp((0.01 - 0.5*iv**2)*T + iv*np.sqrt(T)*z)
        in_range = ((ST >= strikes['sell_put']) & (ST <= strikes['sell_call'])).mean()
        return float(in_range)
    
    def _calculate_greeks(self, legs: Dict) -> Dict:
        """Calculate portfolio Greeks"""
        greeks = {
            'delta': 0,
            'gamma': 0,
            'theta': 0,
            'vega': 0
        }
        
        for leg, values in legs.items():
            multiplier = -1 if 'sell' in leg else 1
            greeks['delta'] += values['greeks']['delta'] * multiplier
            greeks['gamma'] += values['greeks']['gamma'] * multiplier
            greeks['theta'] += values['greeks']['theta'] * multiplier
            greeks['vega'] += values['greeks']['vega'] * multiplier
            
        return greeks