import pytest
from core.risk_management import RiskManager

@pytest.fixture
def risk_config():
    return {
        'max_portfolio_risk': 0.05,
        'max_position_risk': 0.02,
        'daily_loss_limit': 0.1,
        'sector_limits': {
            'technology': 0.3
        }
    }

def test_portfolio_risk_check(risk_config):
    rm = RiskManager(risk_config)
    portfolio = {'net_value': 100000}
    trade = {'max_loss': 4000, 'quantity': 1}  # 4% risk
    
    valid, reason = rm.validate_trade(trade, portfolio)
    assert valid
    assert reason == "approved"

def test_sector_limit_check(risk_config):
    rm = RiskManager(risk_config)
    portfolio = {
        'net_value': 100000,
        'positions': {
            'tech1': {'risk': 25000, 'symbol': 'AAPL'},
            'tech2': {'risk': 5000, 'symbol': 'MSFT'}
        }
    }
    trade = {'risk': 1000, 'symbol': 'GOOG'}
    
    valid, reason = rm.validate_trade(trade, portfolio)
    assert not valid
    assert reason == "sector_limit"