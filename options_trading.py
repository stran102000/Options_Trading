import yfinance as yf
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from scipy.stats import qmc, norm

def get_best_expiration(ticker, min_days=7, max_days=60):
    """
    Automatically selects an expiration date for the given ticker that falls
    between min_days and max_days from today

    Param:
        ticker (str): Stock symbol (e.g. 'AAPL')
        min_days (int): Minimum days to expiration (e.g. 7)
        max_days (int): Maximum days to expiration (e.g. 60)

    Returns:
        str: Selected expiration date in 'YYYY-MM-DD' format or None if no valid expiration is foudn
    """
    ticker_obj = yf.Ticker(ticker)
    expirations = ticker_obj.options
    now = datetime.datetime.now()
    valid_expirations = []

    for exp in expirations:
        try:
            exp_date = datetime.datetime.strptime(exp, '%Y-%m-%d')
            days_to_exp = (exp_date - now).days
            if min_days <= days_to_exp <= max_days:
                valid_expirations.append(exp)
        except Exception as e:
            print("Error parsing exception {exp}:", {e})
    
    if valid_expirations:
        #Choose the earliest expirations
        best_exp = min(valid_expirations, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        return best_exp
    else:
        return None

def fetch_options_data(ticker, expiration, option_type='call'):
    """
    Fetches the options chain for a given ticker and exp date.

    Param:
        ticker (str): Stock symbol (e.g. 'AAPL')
        expiration (str): Expriation date in 'YYYY-MM-DD' format
    
    Returns:
        DataFrame: Calls options data as a pandas DataFrame.
    """
    stock = yf.Ticker(ticker)
    try:
        #Retrieve option chain for providded expiration
        opt = stock.option_chain(expiration)
        data = opt.calls if option_type == 'call' else opt.puts
        return data
    except Exception as e:
        print("Error fetching data: {e}")
        return pd.DataFrame()

def compute_sma(options_data, window=5):
    """
    Compute the Simple Moving Average (SMA) on the last price.

    Param:
        options_data (DataFrame): Options chain data.
        window (int): Number of periods for the moving average.
    
    Returns:
        DataFrane: Options data with an SMA column.
    """
    #Ensure data is sorted by an index that reflects order (if applicable)
    options_data = options_data.reset_index(drop=True)
    options_data['SMA'] = options_data['lastPrice'].rolling(window=window).mean()
    return options_data

def generate_signals(options_data, option_type):
    """
    Generate trade signals based on on lastPrice relative to the SMA.

    For calls: Signal is True when lastPrice > SMA
    For puts: Signal is True when lastPrice < SMA

    Param:
        options_data (DataFrame): Options chain data with SMA computed.
        option_type (str): option type
    
    Returns:
        DataFrame: Options data with an added 'Signal' column.
    """
    if option_type == 'call':
        options_data['Signal'] = options_data['lastPrice'] > options_data['SMA']
    elif option_type == 'put':
        options_data['Signal'] = options_data['lastPrice'] < options_data['SMA']
    else:
        options_data['Signal'] = False
    return options_data

def quasi_monte_carlo_call_price(S, K, T, r, sigma, num_simulations=2**14):
    """
    Estimate European Call option price using Quasi-Monte Carlo simukation with a Sobol sequence.

    Param:
        S (float): Current price of the underlying asset.
        K (float): Strike price.
        T (float): Time to expiration (in years).
        r (float): Annual risk-free interest rate.
        sigma (float): Volatility of the underlying asset.
        num_simulations (int): Number of simulation paths (Power of 2 for Sobol).

    Returns:
        tuple: (Estimated call option price, 95% Value-at-Risk for the discounted payoff)
    """
    #Create Sobol sequence
    sampler = qmc.Sobol(d=1, scramble=True)
    #Generate samples in [0,1)
    samples = sampler.random_base2(m=int(np.log2(num_simulations)))

    Z = norm.ppf(samples)
    Z = Z.flatten() #Flattern into 1-D array

    #Simulate terminal asset price using risk-neutral dynamics
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)

    #Compute payoffs for call option
    payoffs = np.maximum(ST - K, 0)

    #Discount average payoff to obtain price
    call_price = np.exp(-r * T) * np.mean(payoffs)

    #Calculate risk measure: 95% Value-at-Risk (VaR) of discounted payoff
    discounted_payoffs = np.exp(-r * T) * payoffs
    call_var = np.percentile(discounted_payoffs, 5)

    return call_price, call_var

def quasi_monte_carlo_put_price(S, K, T, r, sigma, num_simulations=2**14):
    """
    Estimate European Put option price using Quasi-Monte Carlo simulation with a Sobol sequence.

    Param:
        S (float): Current price of the underlying asset.
        K (float): Strike price.
        T (float): Time to expiration (in years).
        r (float): Annual risk-free interest rate.
        sigma (float): Volatility of the underlying asset.
        num_simulations (int): Number of simulation paths (Power of 2 for Sobol).

    Returns:
        tuple: (Estimated put option price, 95% Value-at-Risk for the discounted payoff)
    """
    #Create Sobol sequence
    sampler = qmc.Sobol(d=1, scramble=True)
    #Generate samples in [0,1)
    samples = sampler.random_base2(m=int(np.log2(num_simulations)))

    Z = norm.ppf(samples)
    Z = Z.flatten() #Flattern into 1-D array

    #Simulate terminal asset price using risk-neutral dynamics
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)

    #Compute payoffs for put option
    payoffs = np.maximum(K - ST, 0)

    #Discount average payoff to obtain price
    discounted_payoffs = np.exp(-r * T) * payoffs

    #Estimate the put option price as the average of discounted payoffs
    put_price = np.mean(discounted_payoffs)

    #Calculate risk measure: 95% Value-at-Risk (VaR) of discounted payoff
    put_var = np.percentile(discounted_payoffs, 5)

    return put_price, put_var

def monte_carlo_call_price(S, K, T, r, sigma, num_simulations=10000):
    """
    Estimate European Call option price using Monte Carlo simukation.

    Param:
        S (float): Current price of the underlying asset.
        K (float): Strike price.
        T (float): Time to expiration (in years).
        r (float): Annual risk-free interest rate.
        sigma (float): Volatility of the underlying asset.
        num_simulations (int): Number of simulation paths.

    Returns:
        float: Estimated call option price.
    """
    #Generate random draws from a standard normal distribution
    Z = np.random.standard_normal(num_simulations)
    #Simulate the terminal stock price using the Black-Scholes model dynamics
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    #calculate the payoff for each simulation and discount back to present value
    payoffs = np.maximum(ST - K, 0)
    call_price = np.exp(-r * T) * np.mean(payoffs)
    return call_price

def monte_carlo_put_price(S, K, T, r, sigma, num_simulations=10000):
    """
    Estimate European Call option price using Monte Carlo simukation.

    Param:
        S (float): Current price of the underlying asset.
        K (float): Strike price.
        T (float): Time to expiration (in years).
        r (float): Annual risk-free interest rate.
        sigma (float): Volatility of the underlying asset.
        num_simulations (int): Number of simulation paths.

    Returns:
        float: Estimated put option price.
    """
    #Generate random draws from a standard normal distribution
    Z = np.random.standard_normal(num_simulations)
    #Simulate the terminal stock price using the Black-Scholes model dynamics
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    #calculate the payoff for each simulation and discount back to present value
    payoffs = np.maximum(K-ST, 0)
    put_price = np.exp(-r * T) * np.mean(payoffs)
    return put_price

def evaluate_trade(option_type, market_price, mc_price, var, threshold=0.05, var_threshold=None):
    """
    Compare the market price to Monte Carlo estimate and provide advice.

    For calls: If market price is sufficiently below the MC estimate, it appears undervalued
    For puts: Similarly, if market price is sufficiently below the MC estimate, it might be undervalued
    """
    diff = (mc_price - market_price)/market_price
    advice = ""
    if diff>=threshold:
        advice =  f"Good trade: {option_type.capitalize()} option appears undervalued."
        if var_threshold is not None:
            if var < var_threshold:
                advice += " However, risk is high based on VaR"
            else:
                advice += " Risk level is acceptable."
    else:
        advice = f"Not recommend: {option_type.capitalize()} option doesn't appear significantly undervalued."
    return advice

# def plot_lastprice_and_sma(options_data):
#     """
#     Plot the last price and SMA for a visual comparison.

#     Param:
#         options_data (DataFrame): Options chain data with SMA computed.
#     """
#     # plt.figure(figsize=(10,6))
#     ax.cla()
#     ax.plot(options_data.index, options_data['lastPrice'], marker='o', label='Last Price')
#     ax.plot(options_data.index, options_data['SMA'], marker='x', label='SMA')
#     ax.set_xlabel('Option Index')
#     ax.set_ylabel('Price')
#     ax.set_title('Last Price vs SMA for Options')
#     ax.legend()
#     ax.grid(True)
#     plt.draw()
#     plt.pause(0.1)


def main():
    tickers_input = input("Enter ticker symbols separated by commes (e.g. AAPL, MSFT) (or press enter for default list): ").strip()
    if tickers_input:
        tickers = [x.strip().upper() for x in tickers_input.split(",")]
    else:
        #Default list
        tickers = ["AAPL", "AMZN", "GOOGL", "TGT", "TSLA"]
    
    
    
    expiration_input = input("Enter options expiration date (YYYY-MM-DD) or leave blank for auto-selection: ").strip()

    

    # print(f"Monitoring options data for {ticker} expiring on {expiration}...\n")
    # ticker_1 = yf.Ticker("AAPL")
    # opt = ticker_1.option_chain("2025-04-11")
    # print(opt.puts.head())
    # print(opt.calls.head())

    # plt.ion()
    # fig, ax = plt.subplots(figsize=(10,6))

    #Set desired multiplier for sell price
    #Change as needed
    sell_multiplier_call = 1.5
    sell_multiplier_put = 1.5

    while True:
        print("=" * 80)
        for ticker in tickers:
            print(f"\nAnalyzing {ticker} ...")
            #Determine expiration date for this ticker
            if expiration_input == "":
                expiration = get_best_expiration(ticker, min_days=7, max_days=60)
                if expiration is None:
                    print("No suitable expiration found within the specified range.")
                    return
                print(f"Auto-selected expiration: {expiration}")
            else:
                expiration = expiration_input

            #Fetch call and put data
            calls = fetch_options_data(ticker, expiration, option_type='call')
            puts = fetch_options_data(ticker, expiration, option_type='put')
            print(puts[['contractSymbol', 'lastPrice']].head())

            #Process calls
            if calls.empty:
                print("No data available for calls. Retrying...")
            else:
                calls = compute_sma(calls, window=5)
                calls = generate_signals(calls, option_type='call')
                bullish_calls = calls[calls['Signal']]

            #Process Puts
            if puts.empty:
                print("No data available for puts. Retrying...")
            else:
                puts = compute_sma(puts, window=5)
                puts = generate_signals(puts, option_type='put')
                bullish_puts = puts[puts['Signal']]

            #Retrieve current udnerlying price
            underlying = yf.Ticker(ticker)
            try:
                S = float(underlying.info['regularMarketPrice'])
            except Exception as e:
                print(f"Error fetching underlying price: {e}")
                S = None
            
            if S is not None:
                #Calculate time to expiration in years
                expiration_date = datetime.datetime.strptime(expiration, "%Y-%m-%d")
                T_days = (expiration_date - datetime.datetime.now()).days
                T = T_days / 365 if T_days > 0 else 0.01 #Avoid 0 or negative T

                #Set risk-free rate and volatility assumptions
                r = 0.01        #Example: r = 0.01, 1% risk-free rate
                sigma = 0.25    #Example: sigma = 0.25, 25% volatility

                #Estimate call options
                if not calls.empty and not bullish_calls.empty:
                    best_call = bullish_calls.loc[bullish_calls['volume'].idxmax()]
                    K_call = best_call['strike']
                    market_call_price = best_call['lastPrice']

                    #Set acceptable risk threshold (Minimum acceptable VaR of $2.00)
                    acceptable_var_threshold = 2.00     #Adjust as needed

                    #Quasi-Monte Carlo
                    qmc_call_price, var_95_call = quasi_monte_carlo_call_price(S, K_call, T, r, sigma)
                    call_advice = evaluate_trade('call', market_call_price, qmc_call_price, var=var_95_call, threshold=0.05, var_threshold=acceptable_var_threshold)

                    # mc_call_price = monte_carlo_call_price(S, K_call, T, r, sigma)
                    # call_advice = evaluate_trade('call', market_call_price, mc_call_price, threshold=0.05)

                    #Suggested prices with multiplier
                    suggested_buy_call = market_call_price
                    suggested_sell_call = suggested_buy_call * sell_multiplier_call
                    
                    print("Selected Call Option")
                    print(best_call.to_string())
                    print(f"Underlying Price: {S:.2f}")
                    print(f"Market Call Price: {market_call_price:.2f}")
                    print(f"Quasi-Monte Carlo Estimated Call Price: {qmc_call_price:.2f}")
                    print(f"95% VaR on Discounted Payoff: {var_95_call:.2f}")
                    # print(f"Monte Carlo Estimated Call Price: {mc_call_price:.2f}")
                    print(f"Trade Advice: {call_advice}")
                    print(f"Recommended Contract to Buy: {best_call['contractSymbol']}")
                    print(f"Suggested Buy Price: {suggested_buy_call:.2f}")
                    print(f"Suggested Sell Price: {suggested_sell_call:.2f}")

                else:
                    print("\nNo bullish call signals found.\n")

                #Evaluate put options
                if not puts.empty and not bullish_puts.empty:
                    best_put = bullish_puts.loc[bullish_puts['volume'].idxmax()]
                    K_put = best_put['strike']
                    market_put_price = best_put['lastPrice']

                    #Set acceptable risk threshold (Minimum acceptable VaR of $2.00)
                    acceptable_var_threshold = 2.00     #Adjust as needed

                    #Quasi-Monte Carlo
                    qmc_put_price, var_95_put = quasi_monte_carlo_put_price(S, K_put, T, r, sigma)
                    put_advice = evaluate_trade('put', market_put_price, qmc_put_price, var=var_95_put, threshold=0.05, var_threshold=acceptable_var_threshold)

                    # mc_put_price = monte_carlo_put_price(S, K_put, T, r, sigma)
                    # put_advice = evaluate_trade('put', market_put_price, mc_put_price, threshold=0.05)

                    #Suggested prices with multiplier
                    suggested_buy_put = market_put_price
                    suggested_sell_put = suggested_buy_put * sell_multiplier_put

                    print("Selected Put Option")
                    print(best_put.to_string())
                    print(f"Underlying Price: {S:.2f}")
                    print(f"Market Put Price: {market_put_price:.2f}")
                    print(f"Quasi-Monte Carlo Estimated Put Price: {qmc_put_price:.2f}")
                    print(f"95% VaR on Discounted Payoff: {var_95_put:.2f}")
                    # print(f"Monte Carlo Estimated Put Price: {mc_put_price:.2f}")
                    print(f"Trade Advice: {put_advice}")
                    print(f"Recommended Contract to Buy: {best_put['contractSymbol']}")
                    print(f"Suggested Buy Price: {suggested_buy_put:.2f}")
                    print(f"Suggested Sell Price: {suggested_sell_put:.2f}")
                else:
                    print("\nNo bullish put signals found.")

                #Update call options plot for visual reference
                # if not calls.empty:
                #     ax.cla()
                #     ax.plot(calls.index, calls['lastPrice'], marker='o', label='Last Price')
                #     ax.plot(calls.index, calls['SMA'], marker='x', label='SMA')
                #     ax.set_xlabel('Option Index')
                #     ax.set_ylabel('Price')
                #     ax.set_title('Last Price vs SMA for Options')
                #     ax.legend()
                #     ax.grid(True)
                #     plt.draw()
                #     plt.pause(0.1)

        print("-" * 40)
        #Pause for 60 seconds before next update
        time.sleep(60)

if __name__ == "__main__":
    main()