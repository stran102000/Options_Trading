import logging
import time
from typing import Dict, List
from datetime import datetime, timedelta
import yaml
from .execution import ExecutionEngine
from .risk_management import RiskManager
from .data_handler import DataHandler
from .strategies import IronCondor, IronButterfly, TrendFollowing
from .utils.helpers import calculate_portfolio_value
from .utils.logger import setup_logger

logger = setup_logger('trading_bot')

class TradingBot:
    def __init__(self, config_path: str = "config/live_config.yml"):
        self.config = self._load_config(config_path)
        self.execution_engine = ExecutionEngine(self.config)
        self.risk_manager = RiskManager(self.config)
        self.data_handler = DataHandler(offline_mode=self.config.get('offline_mode', False))
        self.strategies = self._initialize_strategies()
        self.portfolio = self._initialize_portfolio()
        self.emergency_stop = False

    def _load_config(self, path: str) -> Dict:
        with open(path) as f:
            return yaml.safe_load(f)

    def _initialize_strategies(self) -> Dict:
        return {
            'iron_condor': IronCondor(self.config['strategies']['iron_condor']),
            'iron_butterfly': IronButterfly(self.config['strategies']['iron_butterfly']),
            'trend_following': TrendFollowing(self.config['strategies']['trend_following'])
        }

    def _initialize_portfolio(self) -> Dict:
        return {
            'cash': self.config['account']['initial_balance'],
            'positions': {},
            'history': [],
            'last_updated': datetime.now()
        }

    def run(self):
        """Main trading loop"""
        logger.info("Starting trading bot")
        try:
            while not self.emergency_stop:
                start_time = time.time()
                
                self._check_emergency_stop()
                market_data = self.data_handler.get_market_state()
                
                if not self.risk_manager.market_safe(market_data):
                    logger.warning("Market conditions unsafe - skipping cycle")
                    time.sleep(60)
                    continue
                
                opportunities = self._find_opportunities(market_data)
                self._process_opportunities(opportunities)
                
                cycle_time = time.time() - start_time
                sleep_time = max(0, self.config['polling_interval'] - cycle_time)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        finally:
            self._shutdown()

    def _find_opportunities(self, market_data: Dict) -> List[Dict]:
        """Find trading opportunities across all strategies"""
        opportunities = []
        symbols = self.config['watchlist']
        
        for symbol in symbols:
            try:
                # Get current market data for symbol
                price = market_data['prices'].get(symbol)
                iv = market_data['iv'].get(symbol)
                
                if not price or not iv:
                    continue
                    
                # Generate opportunities from all strategies
                if self.strategies['iron_condor'].enabled:
                    opportunities.append(
                        self.strategies['iron_condor'].analyze(symbol, price, iv)
                    )
                    
                if self.strategies['iron_butterfly'].enabled:
                    opportunities.append(
                        self.strategies['iron_butterfly'].analyze(symbol, price, iv)
                    )
                    
                if self.strategies['trend_following'].enabled:
                    hist_data = self.data_handler.get_historical(symbol)
                    opportunities.append(
                        self.strategies['trend_following'].analyze(hist_data)
                    )
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                
        return [opp for opp in opportunities if opp is not None]

    def _process_opportunities(self, opportunities: List[Dict]):
        """Validate and execute trading opportunities"""
        for opportunity in opportunities:
            try:
                valid, reason = self.risk_manager.validate_trade(opportunity, self.portfolio)
                if not valid:
                    logger.debug(f"Skipping opportunity: {reason}")
                    continue
                    
                trade = self._prepare_trade(opportunity)
                result = self.execution_engine.execute(trade)
                
                if result['status'] == 'filled':
                    self._update_portfolio(trade)
                    logger.info(f"Trade executed: {trade}")
                    
            except Exception as e:
                logger.error(f"Error processing opportunity: {str(e)}")

    def _check_emergency_stop(self):
        """Check for emergency stop file"""
        if Path('emergency_stop').exists():
            self.emergency_stop = True
            logger.warning("Emergency stop triggered - shutting down")

    def _shutdown(self):
        """Clean shutdown procedure"""
        logger.info("Shutting down trading bot")
        self.execution_engine.close()