def score(symbol):
    try:
        chain = r.options.find_options_by_expiration(symbol, optionType='all')
        if not chain:
            return 0.0
        center = len(chain) // 2
        atm_call = chain[center]
        short_strike = float(atm_call['strike_price'])
        long_call = float(chain[center+2]['strike_price'])
        long_put = float(chain[center-2]['strike_price'])

        net_credit = float(atm_call['ask_price']) * 2 - float(chain[center+2]['bid_price']) - float(chain[center-2]['bid_price'])
        max_loss = long_call - short_strike
        return round(net_credit / max_loss, 4) if max_loss > 0 else 0.0
    except Exception:
        return 0.0