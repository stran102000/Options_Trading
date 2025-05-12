import pytest
from unittest.mock import patch, MagicMock
from core.execution import ExecutionEngine

@pytest.fixture
def mock_config():
    return {
        'execution': {
            'auto_place_trades': True,
            'confirm_before_trade': False,
            'max_slippage': 0.01
        },
        'safeguards': {
            'required_confirmations': 1,
            'timeout_seconds': 30
        }
    }

def test_stock_order_execution(mock_config):
    with patch('robin_stocks.order_buy_market') as mock_order:
        engine = ExecutionEngine(mock_config)
        result = engine.execute({
            'asset_type': 'stock',
            'symbol': 'AAPL',
            'quantity': 10,
            'side': 'buy',
            'order_type': 'market'
        })
        assert result['status'] == 'filled'
        mock_order.assert_called_once()

def test_option_order_execution(mock_config):
    with patch('robin_stocks.order_option_spread') as mock_order:
        engine = ExecutionEngine(mock_config)
        result = engine.execute({
            'asset_type': 'options',
            'strategy': 'iron_condor',
            'symbol': 'SPY',
            'quantity': 1,
            'legs': [...]
        })
        assert result['status'] == 'filled'