import pytest
from core.pricing_models import PricingModels

@pytest.fixture
def pricing():
    return PricingModels()

def test_qmc_pricing(pricing):
    result = pricing.quasi_monte_carlo(
        S=100, K=105, T=0.25, r=0.01, sigma=0.2
    )
    assert result['status'] == 'success'
    assert 0 < result['price'] < 20