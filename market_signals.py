# This code implements algorithmic trading in a paper trading account.
# The code gets buy and sell stock signals from the 'Market signals' API privided through rapidapi.com
# The signals are transformed into buy and sell orders for the paper trading account with alpaca.markets
# Real-time stock quotes are provided by iexcloud.io
# Prerequisites: free accounts with the following providers (or their equivalents):
# 1. https://alpaca.markets                     - to have a paper trading account
# 2. https://www.pythonanywhere.com             - to be able to run this python code as a scheduled task daily 1 min before market close
# 3. https://iexcloud.io                        - to have access to real-time stock quotes
# 4. https://rapidapi.com                       - to have access to 'Market signals' API provided through rapidapi.com

import requests, json

# for security reasons you might want to keep all your API keys in a separate file
# from config_market_signals import API_KEY_NTRL, SECRET_KEY_NTRL, IEX_TOKEN, RAPIDAPI_KEY
# see https://towardsdatascience.com/keeping-things-secret-d9060c73089b
# this has not been done in the code presented below

url_rapidapi = "https://market-signals1.p.rapidapi.com/v1/neutral/1/"   # rapidapi -> market signals -> neutral portfolio API endpoint
BASE_URL = "https://paper-api.alpaca.markets"                           # alpaca base url
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)                          # alpaca account url
ORDERS_URL = "{}/v2/orders".format(BASE_URL)                            # alpaca orders ulr
POSITIONS_URL = "{}/v2/positions".format(BASE_URL)                      # alpaca positions url

API_KEY_NTRL = "XXX"                                                    # input your alpaca API_KEY
SECRET_KEY_NTRL = "XXX"                                                 # input your alpaca SECRET_KEY
IEX_TOKEN = "XXX"                                                       # input your iexcloud.io key

HEADERS_NTRL = {'APCA-API-KEY-ID': API_KEY_NTRL, 'APCA-API-SECRET-KEY': SECRET_KEY_NTRL}

headers_rapidapi = {
    'x-rapidapi-key': "XXX",                                            # Input your x-rapidapi-key
    'x-rapidapi-host': "market-signals1.p.rapidapi.com"
    }

def get_latest_signals():     # gets the latest signals from rapidapi
    response = requests.request("GET", url_rapidapi, headers=headers_rapidapi)
    latest_signals = response.json()
    return(latest_signals)

def get_positions():          # gets open positions from alpaca paper trading account
    r = requests.get(POSITIONS_URL, headers = HEADERS_NTRL)
    rj = json.loads(r.content)
    return rj

def get_account():            # a helper function to get the amount of equity in the paper trading account (see get_equity() below)
    r = requests.get(ACCOUNT_URL, headers = HEADERS_NTRL)
    return json.loads(r.content)

def get_equity():             # gets equity amount in the alpaca paper trading account
    response = get_account()
    equity = float(response['equity'])
    return equity

def close_all_positions():    # closes all positions in the alpaca paper trading account
    positions = get_positions()
    for position in positions:
        if position['side'] == 'long':
            data = {
                "symbol": position['symbol'],
                "qty": abs(int(position['qty'])),
                "side": 'sell',
                "type": "market",
                "time_in_force": "gtc"
                }
            r = requests.post(ORDERS_URL, json = data, headers = HEADERS_NTRL)
            print(json.loads(r.content))        # comment this line out if you do not want to see the details of orders
        elif position['side'] == 'short':
            data = {
                "symbol": position['symbol'],
                "qty": abs(int(position['qty'])),
                "side": 'buy',
                "type": "market",
                "time_in_force": "gtc"
                }
            r = requests.post(ORDERS_URL, json = data, headers = HEADERS_NTRL)
            print(json.loads(r.content))        # comment this line out if you do not want to see the details of orders
        else:
            pass
    return()

def open_all_new_positions():   # opens all positions in the alpaca paper trading account
    latest_signals = get_latest_signals()
    longs_to_be_opened = latest_signals['long_positions']
    shorts_to_be_opened = latest_signals['short_positions']
    equity = get_equity()

    for long_to_be_opened in longs_to_be_opened:
        price_endpoint = 'https://cloud.iexapis.com/stable/tops?token=' + IEX_TOKEN + '&symbols=' + long_to_be_opened
        response = requests.get(price_endpoint)
        price = response.json()[0]['lastSalePrice']
        qty = int((equity*0.9/5)//price)        # '5' is the number of long positions to be opened; '0.9' sets the level of leverage
        # if this level is set at, say '0.5' then 50% of equity is allocated to longs and 50% of equity is allocated to shorts
        data = {
            "symbol": long_to_be_opened,
            "qty": qty,
            "side": 'buy',
            "type": "market",
            "time_in_force": "gtc"
            }
        r = requests.post(ORDERS_URL, json = data, headers = HEADERS_NTRL)
        print(json.loads(r.content))           # comment out this line if you do not want to see the details of orders placed

    for short_to_be_opened in shorts_to_be_opened:
        price_endpoint = 'https://cloud.iexapis.com/stable/tops?token=' + IEX_TOKEN + '&symbols=' + short_to_be_opened
        response = requests.get(price_endpoint)
        price = response.json()[0]['lastSalePrice']
        qty = int((equity*0.9/5)//price)         # '5' is the number of long positions to be opened; '0.9' sets the level of leverage
        # if this level is set at, say '0.5', then 50% of equity is allocated to longs and 50% of equity is allocated to shorts
        data = {
            "symbol": short_to_be_opened,
            "qty": qty,
            "side": 'sell',
            "type": "market",
            "time_in_force": "gtc"
            }
        r = requests.post(ORDERS_URL, json = data, headers = HEADERS_NTRL)
        print(json.loads(r.content))             # comment out this line if you do not want to see the details of orders placed
    return()

def run_one_min_before_market_close():
    get_latest_signals()
    close_all_positions()
    open_all_new_positions()
    return()

run_one_min_before_market_close()



