import robin_stocks as rs
from typing import Dict
from pathlib import Path
from .safeguards import TradeConfirmation
from .utils.logger import setup_logger

logger = setup_logger('execution')

class ExecutionEngine:
    def __init__(self, config: Dict):
        self.config = config['execution']
        self.safeguards = TradeConfirmation(config['safeguards'])
        self.authenticated = False
        self._login()
        
    def _login(self):
        """Authenticate with Robinhood"""
        try:
            rs.login(
                username=self.config.get('rh_username'),
                password=self.config.get('rh_password'),
                mfa_code=self.config.get('rh_mfa_code')
            )
            self.authenticated = True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise
        
    def execute(self, order: Dict) -> Dict:
        """Execute order with full safeguards"""
        try:
            if not self.authenticated:
                return {'status': 'error', 'message': 'Not authenticated'}
                
            if Path('emergency_stop').exists():
                return {'status': 'error', 'message': 'Emergency stop active'}
                
            if not self._pre_flight_checks(order):
                return {'status': 'checks_failed'}
                
            if not self.config['auto_place_trades']:
                logger.info(f"Would execute: {order}")
                return {'status': 'recommended'}
                
            if self.config['confirm_before_trade']:
                if not self.safeguards.verify(order):
                    return {'status': 'user_cancelled'}
            
            # Actual execution
            if order['asset_type'] == 'stock':
                return self._execute_stock(order)
            return self._execute_option(order)
            
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _execute_stock(self, order: Dict) -> Dict:
        """Execute stock order"""
        try:
            if order['order_type'] == 'market':
                if order['side'] == 'buy':
                    result = rs.order_buy_market(
                        order['symbol'], 
                        order['quantity']
                    )
                else:
                    result = rs.order_sell_market(
                        order['symbol'], 
                        order['quantity']
                    )
            else:  # limit order
                if order['side'] == 'buy':
                    result = rs.order_buy_limit(
                        order['symbol'],
                        order['quantity'],
                        order['limit_price']
                    )
                else:
                    result = rs.order_sell_limit(
                        order['symbol'],
                        order['quantity'],
                        order['limit_price']
                    )
                    
            return self._parse_result(result)
        except Exception as e:
            logger.error(f"Stock order failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _execute_option(self, order: Dict) -> Dict:
        """Execute multi-leg options order"""
        try:
            legs = []
            for leg in order['legs']:
                legs.append({
                    'option': leg['option_id'],
                    'position_effect': 'open',
                    'side': leg['action'],
                    'ratio': 1
                })
                
            result = rs.order_option_spread(
                order['symbol'],
                order['expiration'],
                legs,
                price=order.get('limit_price'),
                spread_type=order['strategy'].replace('_', ' '),
                time_in_force='gfd'
            )
            
            return self._parse_result(result)
        except Exception as e:
            logger.error(f"Options order failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _parse_result(self, result: Dict) -> Dict:
        """Parse Robinhood API response"""
        if 'id' in result:
            return {
                'status': 'filled',
                'order_id': result['id'],
                'filled_price': float(result.get('average_price', 0))
            }
        return {
            'status': 'error',
            'message': result.get('detail', 'Unknown error')
        }
    
    def _pre_flight_checks(self, order: Dict) -> bool:
        """Pre-execution validation"""
        checks = [
            order.get('quantity', 0) > 0,
            order.get('symbol'),
            order.get('asset_type') in ['stock', 'options']
        ]
        return all(checks)
    
    def close(self):
        """Clean up resources"""
        if self.authenticated:
            rs.logout()