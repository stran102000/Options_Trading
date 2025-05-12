from typing import Dict, Tuple
import numpy as np

class RiskManager:
    def __init__(self, config: Dict):
        self.config = config
        self.max_portfolio_risk = config['max_portfolio_risk']
        self.max_position_risk = config['max_position_risk']
        self.sector_limits = config.get('sector_limits', {})
        self.daily_loss_limit = config.get('daily_loss_limit', 0.1)
        
    def validate_trade(self, trade: Dict, portfolio: Dict) -> Tuple[bool, str]:
        """Comprehensive trade validation"""
        checks = [
            (self._check_portfolio_risk(trade, portfolio), "portfolio_risk"),
            (self._check_position_size(trade, portfolio), "position_size"),
            (self._check_sector_limits(trade, portfolio), "sector_limit"),
            (self._check_daily_loss(portfolio), "daily_loss"),
            (self._check_liquidity(trade), "liquidity")
        ]
        
        for passed, reason in checks:
            if not passed:
                return False, reason
        return True, "approved"
    
    def market_safe(self, market_data: Dict) -> bool:
        """Check overall market conditions"""
        if market_data.get('vix', 0) > 40:
            return False
        if market_data.get('sp500_change', 0) < -0.05:
            return False
        return True
    
    def _check_portfolio_risk(self, trade: Dict, portfolio: Dict) -> bool:
        """Check against max portfolio risk"""
        trade_risk = trade.get('max_loss', 0) * trade.get('quantity', 0)
        portfolio_value = portfolio.get('value', 0)
        return trade_risk <= portfolio_value * self.max_portfolio_risk
    
    def _check_position_size(self, trade: Dict, portfolio: Dict) -> bool:
        """Check position size limits"""
        position_size = trade.get('quantity', 0) * trade.get('price', 0)
        portfolio_value = portfolio.get('value', 0)
        return position_size <= portfolio_value * self.max_position_risk
    
    def _check_sector_limits(self, trade: Dict, portfolio: Dict) -> bool:
        """Check sector concentration limits"""
        sector = self._get_sector(trade['symbol'])
        if not sector:
            return True
            
        current_sector_exposure = sum(
            p['value'] for p in portfolio['positions'].values() 
            if self._get_sector(p['symbol']) == sector
        )
        
        new_trade_value = trade.get('quantity', 0) * trade.get('price', 0)
        sector_limit = self.sector_limits.get(sector, 0.2)
        
        return (current_sector_exposure + new_trade_value) <= portfolio['value'] * sector_limit
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector for a symbol (simplified)"""
        # In practice, you'd use an API or database
        sectors = {
            'AAPL': 'technology',
            'MSFT': 'technology',
            'AMZN': 'consumer',
            'SPY': 'index'
        }
        return sectors.get(symbol, 'other')
    
    def _check_daily_loss(self, portfolio: Dict) -> bool:
        """Check daily loss limits"""
        if not portfolio.get('history'):
            return True
            
        today_pnl = portfolio['value'] - portfolio['history'][-1]['value']
        return today_pnl >= -portfolio['value'] * self.daily_loss_limit
    
    def _check_liquidity(self, trade: Dict) -> bool:
        """Check liquidity requirements"""
        # Simplified - would check actual volume/order book
        return trade.get('symbol') in ['SPY', 'QQQ', 'AAPL', 'MSFT']