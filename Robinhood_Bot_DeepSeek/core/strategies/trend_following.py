import numpy as np
import pandas as pd
from typing import Dict, Optional
from ..utils.helpers import calculate_technical_indicators

class TrendFollowing:
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config['enabled']
        
    def analyze(self, data: pd.DataFrame) -> Optional[Dict]:
        """Analyze for trend following opportunities"""
        if not self.enabled or len(data) < 50:
            return None
            
        indicators = calculate_technical_indicators(data)
        latest = indicators.iloc[-1]
        
        # Bullish signal
        if (latest['close'] > latest['sma_50'] and 
            latest['sma_20'] > latest['sma_50'] and
            latest['rsi'] < 70):
            return {
                'symbol': data['symbol'].iloc[0],
                'strategy': 'trend_following',
                'direction': 'long',
                'entry': latest['close'],
                'stop_loss': latest['close'] * (1 - self.config['stop_loss_pct']),
                'take_profit': latest['close'] * (1 + self.config['take_profit_pct']),
                'indicators': latest.to_dict()
            }
            
        # Bearish signal
        elif (latest['close'] < latest['sma_50'] and 
              latest['sma_20'] < latest['sma_50'] and
              latest['rsi'] > 30):
            return {
                'symbol': data['symbol'].iloc[0],
                'strategy': 'trend_following',
                'direction': 'short',
                'entry': latest['close'],
                'stop_loss': latest['close'] * (1 + self.config['stop_loss_pct']),
                'take_profit': latest['close'] * (1 - self.config['take_profit_pct']),
                'indicators': latest.to_dict()
            }
            
        return None