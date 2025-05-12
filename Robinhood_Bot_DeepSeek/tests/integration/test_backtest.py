import pytest
from core.bot import TradingBot
from core.data_handler import DataHandler

@pytest.fixture
def backtest_config():
    return {
        'execution': {'auto_place_trades': False},
        'risk': {'max_portfolio_risk': 0.05},
        'strategies': {
            'iron_butterfly': {'enabled': True}
        }
    }

def test_backtest(backtest_config):
    data = DataHandler(offline_mode=True)
    bot = TradingBot(config=backtest_config, data_handler=data)
    
    results = bot.backtest(
        start='2023-01-01',
        end='2023-03-01',
        symbols=['SPY']
    )
    
    assert 'sharpe_ratio' in results
    assert results['total_trades'] > 0