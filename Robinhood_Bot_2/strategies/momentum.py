import yfinance as yf

def score(symbol):
    try:
        hist = yf.download(symbol, period='30d', interval='1d')
        if len(hist) < 15:
            return 0.5  # not enough data
        momentum = hist['Close'][-1] / hist['Close'][0] - 1
        return round(momentum, 4)
    except Exception:
        return 0.5