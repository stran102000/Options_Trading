from config import AUTO_PLACE_ORDER
from broker.robinhood_interface import get_price, place_order

def allocate_portfolio(scores, budget):
    sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for symbol, score in sorted_stocks:
        price = get_price(symbol)
        if price == 0: continue
        shares = round((budget / len(scores)) / price, 4)
        print(f"[RECOMMENDED] Buy {shares} of {symbol} at ${price:.2f}")
        if AUTO_PLACE_ORDER:
            place_order(symbol, shares)