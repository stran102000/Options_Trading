import os
from config import PAPER_TRADING
import robin_stocks.robinhood as r

def login_robinhood():
    username = os.getenv("RH_USERNAME")
    password = os.getenv("RH_PASSWORD")
    if not username or not password:
        raise ValueError("Set RH_USERNAME and RH_PASSWORD environment variables.")
    r.authentication.login(username, password, store_session=True)
    print("[LOGIN SUCCESS]")

def get_price(symbol):
    quote = r.stocks.get_latest_price(symbol)
    return float(quote[0]) if quote else 0.0

def place_order(symbol, shares):
    if PAPER_TRADING:
        print(f"[SIMULATED ORDER] {shares:.4f} shares of {symbol}")
    else:
        r.orders.order_buy_fractional_by_quantity(symbol, quantity=shares, timeInForce='gfd')