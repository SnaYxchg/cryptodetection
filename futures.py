# Fetch open interest of all futures tickers every 1 minute
# Re-run everytime when we have new futures pairs na
# Code works only with BUSD and USDT tickers

import requests
import pandas as pd
import time

tickers = []
oi_data = {} # {ticker: oi}
price_data = {} # {ticker: price}

def fetchFuturesTickers():
    # This function fetches all the tickers on binance futures and pushes them in tickers. 

    exchangeInfoURL = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    r = requests.get(url = exchangeInfoURL)
    data = r.json()
    symbols_data = data['symbols']

    usdt_coins = []

    for i in symbols_data:
        ticker = i['symbol']
        if ticker[-4:]== "USDT":
            usdt_coins.append(ticker[:-4])
            tickers.append(ticker)

    for i in symbols_data:
        ticker = i['symbol']
        if ticker[-4:] == "BUSD":
            # We have the BUSD coin, see if it's in the list already.
            busd_coin = ticker[:-4]

            if busd_coin not in usdt_coins:
                tickers.append(ticker)
            

def fetchOI():
    n = 0
    tickers_length = len(tickers)

    for ticker in tickers:
        OI_URL = "https://fapi.binance.com/fapi/v1/openInterest"
        PARAMS = {'symbol': ticker}

        r = requests.get(url = OI_URL, params = PARAMS)
        r = r.json()

        if 'code' in r:
            # Remove non-existing ticker
            tickers.remove(ticker)
        else:
            # Add
            oi_data[ticker] = r['openInterest']
        

def fetchPrices():
    PriceURL = "https://fapi.binance.com/fapi/v1/ticker/price"
    r = requests.get(url = PriceURL)
    r = r.json()
    
    for x in r:
        # x is a dict
        price_data[x['symbol']] = x['price']

def sort_oi():
    l = []
    for i in tickers:
        
        if i in oi_data:
            l.append(oi_data[i])
        else:
            l.append(0)

    return l

def sort_prices():
    l = []
    for i in tickers:
        if i in price_data:
            l.append(price_data[i])
        else:
            l.append(0)

    return l

def main():
    fetchFuturesTickers()
    fetchOI()
    fetchPrices()

    data = {"Ticker": tickers, "Price": sort_prices(), "Open Interest": sort_oi()}
    df = pd.DataFrame(data)

    str_time = str(time.strftime("%d,%m,%y,%H,%M"))
    df.to_csv("futures_data/" + str_time + '.csv', encoding='utf-8', index = False)

    tickers.clear()
    oi_data.clear()
    price_data.clear()
    # To redo everything again. 


# Make sure everything happens in a minute. 