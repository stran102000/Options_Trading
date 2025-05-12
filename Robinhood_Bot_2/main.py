from config import *
from broker.robinhood_interface import login_robinhood
from utils.portfolio_allocator import allocate_portfolio
from strategies import load_all_strategies, score_stocks

def main():
    login_robinhood()
    strategies = load_all_strategies(ENABLED_STRATEGIES)
    scores = score_stocks(strategies, STOCK_POOL)
    allocate_portfolio(scores, MAX_BUDGET)

if __name__ == "__main__":
    main()