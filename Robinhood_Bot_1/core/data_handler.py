import pandas as pd
import robin_stocks as rs
from typing import Dict, Optional
import yfinance as yf
import os
from datetime import datetime

class DataHandler:
    def __init__(self, offline_mode: bool = False):
        self.offline_mode = offline_mode
        self.cache = {}
        
    def get_market_state(self) -> Dict:
        """Get current market conditions"""
        if self.offline_mode:
            return self._load_cached_state()
            
        try:
            # Get major indices
            sp500 = rs.get_stock_quote('SPY')['last_extended_hours_trade_price'] or rs.get_stock_quote('SPY')['last_trade_price']
            vix = rs.get_stock_quote('VIXY')['last_extended_hours_trade_price'] or rs.get_stock_quote('VIXY')['last_trade_price']
            
            return {
                'sp500': float(sp500),
                'vix': float(vix),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching market state: {str(e)}")
            return {}
    
    def get_historical(self, symbol: str, interval: str = '1d', 
                      period: str = '1y') -> Optional[pd.DataFrame]:
        """Get historical price data"""
        cache_key = f"{symbol}_{interval}_{period}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            if self.offline_mode:
                data = self._load_from_disk(symbol)
            else:
                data = yf.download(symbol, period=period, interval=interval)
                
            if data.empty:
                return None
                
            # Calculate technical indicators
            data = self._calculate_indicators(data)
            self.cache[cache_key] = data
            return data
            
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to data"""
        data['sma_20'] = data['Close'].rolling(20).mean()
        data['sma_50'] = data['Close'].rolling(50).mean()
        data['rsi'] = self._calculate_rsi(data['Close'])
        return data
    
    def _calculate_rsi(self, series: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window).mean()
        avg_loss = loss.rolling(window).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _load_from_disk(self, symbol: str) -> pd.DataFrame:
        """Load historical data from local storage"""
        path = f"data/historical/{symbol}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=['Date'], index_col='Date')
            return df
        raise FileNotFoundError(f"No historical data found for {symbol}")