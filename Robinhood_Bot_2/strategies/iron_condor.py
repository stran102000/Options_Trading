import robin_stocks.robinhood as r

def score(symbol):
    try:
        chain = r.options.find_options_by_expiration(symbol, expirationDate=None, strikePrice=None, optionType='all')
        calls = [c for c in chain if c['type'] == 'call']
        puts = [p for p in chain if p['type'] == 'put']
        if len(calls) < 2 or len(puts) < 2:
            return 0.0

        # Use a simple net credit / risk score
        short_call = float(calls[-2]['strike_price'])
        long_call = float(calls[-1]['strike_price'])
        short_put = float(puts[0]['strike_price'])
        long_put = float(puts[1]['strike_price'])

        net_credit = float(calls[-2]['ask_price']) + float(puts[0]['ask_price']) \
                   - float(calls[-1]['bid_price']) - float(puts[1]['bid_price'])

        max_loss = (long_call - short_call)  # assume symmetric
        return round(net_credit / max_loss, 4) if max_loss > 0 else 0.0
    except Exception:
        return 0.0