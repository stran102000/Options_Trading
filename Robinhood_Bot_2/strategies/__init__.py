from .momentum import score as momentum_score
from .monte_carlo import score as montecarlo_score
from .black_scholes import score as blackscholes_score
from .iron_condor import score as ironcondor_score
from .iron_butterfly import score as ironbutterfly_score

def load_all_strategies(enabled):
    strategy_map = {
        'momentum': momentum_score,
        'monte_carlo': montecarlo_score,
        'black_scholes': blackscholes_score,
        'iron_condor': ironcondor_score,
        'iron_butterfly': ironbutterfly_score
    }
    return [strategy_map[name] for name in enabled]

def score_stocks(strategies, stock_pool):
    scores = {}
    for stock in stock_pool:
        total = sum([s(stock) for s in strategies])
        scores[stock] = round(total / len(strategies), 4)
    return scores