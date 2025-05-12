import pytest
from core.strategies import IronButterfly, IronCondor

@pytest.fixture
def ib_config():
    return {
        'width_percent': 0.02,
        'min_credit': 0.80,
        'pricing': {
            'default_model': 'quasi_monte_carlo',
            'qmc': {'simulations': 5000, 'scramble': True}
        }
    }

def test_iron_butterfly_pnl_calculation(ib_config):
    ib = IronButterfly(ib_config)
    analysis = ib.analyze('SPY', 400, 0.2, 21)
    
    # Test profitable scenario
    pnl = ib.calculate_pnl(analysis, 400)  # At midpoint
    assert pnl > 0
    
    # Test max loss scenario
    pnl = ib.calculate_pnl(analysis, 420)  # Above upper strike
    assert pnl == -analysis['metrics']['max_loss']