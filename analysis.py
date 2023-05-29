import spot
import pandas as pd
import os
import futures
from datetime import datetime
import math
from time import sleep, time
from json import dumps
import requests
import smtplib
import dataa
import warnings

warnings.filterwarnings("ignore")

# Have a problems slide and explain open interest thoda sa. 

# We just take data
oi_data = {} # Ticker: ['open interest'...]
price_data = {} # Ticker: ['price'...]
spot_price_data = {}
spot_daily_volume = {} # Ticker: volume

futures_strategy1_blacklist = {} # This will have a 30 minute blacklist. ticker -> blacklistEndUnixTime
futures_strategy2_blacklist = {} # 1 day blacklist. 
futures_strategy3_blacklist = {} # 2 day blacklist. 

spot_strategy1_blacklist = {}
spot_strategy2_blacklist = {}


def firstFilePath():
    now = datetime.today()
    str_time = str(now.strftime("%d,%m,%y,%H,%M"))
    path = "futures_data/" + str_time + ".csv"

    return path

def firstSpotFilePath():
    now = datetime.today()
    str_time = str(now.strftime("%d,%m,%y,%H,%M"))
    path = "spot_data/" + str_time + ".csv"

    return path

def clearBlacklist(): # Mittal?
    for x in futures_strategy1_blacklist.keys():
        if futures_strategy1_blacklist[x] > time():
            del futures_strategy1_blacklist[x]
    
    for x in futures_strategy2_blacklist.keys():
        if futures_strategy2_blacklist[x] > time():
            del futures_strategy2_blacklist[x]

    for x in futures_strategy3_blacklist.keys():
        if futures_strategy3_blacklist[x] > time():
            del futures_strategy3_blacklist[x]
    
    for x in spot_strategy1_blacklist.keys():
        if spot_strategy1_blacklist[x] > time():
            del spot_strategy1_blacklist[x]

    for x in spot_strategy2_blacklist.keys():
        if spot_strategy2_blacklist[x] > time():
            del spot_strategy2_blacklist[x]

def sendEmail(message):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()

    gmail_user='shivam.nayyar@bba.christuniversity.in'
    gmail_pwd=dataa.abc
    
    content = message

    server.login(gmail_user,gmail_pwd)

    server.sendmail('shivam.nayyar@bba.christuniversity.in','shivamnayyar.champ@gmail.com',"Subject: " + content)
    server.quit()


def fillSpotData():
    # Keep filling prices as much as possible, don't break loop if not able to find something. 

    now = datetime.today()
    path = firstSpotFilePath()

    if os.path.isfile(path):
        for x in range(60):
            ts = math.floor(now.timestamp() - (x * 60))
            time = datetime.fromtimestamp(ts)

            path_time = str(time.strftime("%d,%m,%y,%H,%M"))
            path = "spot_data/" + path_time + ".csv"

            if x == 0:
                # Initial insertion
                df = pd.read_csv(path)

                for y in range(len(df)):
                    spot_price_data[df.loc[y, "Ticker"]] = [df.loc[y, "Prices"]]

            elif os.path.isfile(path):
                # Append
                df = pd.read_csv(path)

                for y in range(len(df)):
                    spot_price_data[df.loc[y, "Ticker"]].append(df.loc[y, "Prices"])            
                                  
def fillSpotVolume():
    l1 = []
    for x in spot_price_data:
        l1.append(x)
    
    URL = 'https://api.binance.com/api/v3/ticker/24hr?type=MINI&symbols=' + dumps(l1).replace(" ", "")
    r = requests.get(url = URL)
    data = r.json()

    for i in data:
        spot_daily_volume[i['symbol']] = float(i['quoteVolume'])

    print(spot_daily_volume)


def fillFuturesData():
    # Keep filling oi_data and prices as much as possible. 

    # Assuming that all the csvs are there. 
    now = datetime.today()
    path = firstFilePath()

    if os.path.isfile(path):

        # Fetch futures data and put into dictionaries.
        for x in range(60*24): # Putting last 2 days of data in the array

            ts = math.floor(now.timestamp() - (x * 60))
            time = datetime.fromtimestamp(ts)

            path_time = str(time.strftime("%d,%m,%y,%H,%M"))
            path = "futures_data/" + path_time + ".csv"

            if x == 0:
                # Initial insertion
                df = pd.read_csv(path)

                for y in range(len(df)):
                    oi_data[df.loc[y, "Ticker"]] = [df.loc[y, "Open Interest"]]
                    price_data[df.loc[y, "Ticker"]] = [df.loc[y, "Price"]]

            elif os.path.isfile(path):
                # Append
                df = pd.read_csv(path)

                for y in range(len(df)):
                    oi_data[df.loc[y, "Ticker"]].append(df.loc[y, "Open Interest"])
                    price_data[df.loc[y, "Ticker"]].append(df.loc[y, "Price"])


def futures_strategy1():
    # OI decrease of >= 10% in 5 minutes. 

    for x in oi_data.keys():
        # Check first 5 mins of the ticker, if available, if not then check whatever we have. 

        oi_length = len(oi_data[x])
        if oi_length >= 5:
            oi_length = 5

        oi_list = oi_data[x][:oi_length]

        max_value = max(oi_list)
        min_value = min(oi_list)

        if max_value == 0 and min_value == 0: # Delisted coins
            negative_change = 0
        else: # Normal cases
            negative_change = (1 - min_value/max_value) * 100 # Negative change, becoming absolute. 
        

        if negative_change >= 10 and oi_list.index(min_value) < oi_list.index(max_value) and x not in futures_strategy1_blacklist:
            email = x + " Open Interest has dropped " + str(int(negative_change)) + "% in the last 5 minutes."
            print(email)
            sendEmail(email)

            futures_strategy1_blacklist[x] = time() + 1800 # 30 minute cooldown


def futures_strategy2():
    # 25% increase in without price breaking a 10% range (within 2 hours). 

    for x in oi_data.keys(): # For every coin
        oi_length = len(oi_data[x])
        if oi_length >= 120: # last 2 hours data
            oi_length = 120
        
        price_length = len(price_data[x])
        if price_length >= 120:
            price_length = 120

        oi_list = oi_data[x][:oi_length]
        price_list = price_data[x][:price_length]

        max_value = max(oi_list)
        min_value = min(oi_list)

        price_range = (max(price_list)/min(price_list) - 1) * 100
        percentage_change = (max_value/min_value - 1) * 100 # Negative change, becoming absolute. 

        if percentage_change >= 25 and oi_list.index(max_value) < oi_list.index(min_value) and price_range <= 10 and x not in futures_strategy1_blacklist:
            email = x + " Open Interest has increased " + str(int(percentage_change)) + "% in the last within the last 2 hours and price stayed between 10% range."
            print(email)
            sendEmail(email)

            futures_strategy1_blacklist[x] = time() + 1800 # 30 minute cooldown

def futures_strategy3():
    # 100% increase in OI within 1 day

    for x in oi_data.keys():
        oi_length = len(oi_data[x])
        if oi_length >= 1440: # last full day data
            oi_length = 1440

        oi_list = oi_data[x][:oi_length]

        max_value = max(oi_list)
        min_value = min(oi_list)

        if max_value == 0 and min_value == 0: # Delisted coins
            percentage_change = 0
        else: # Normal cases
            percentage_change = (max_value/min_value - 1) * 100 # Negative change, becoming absolute. 
        

        if percentage_change >= 30 and oi_list.index(max_value) < oi_list.index(min_value) and x not in futures_strategy3_blacklist:
            email = x + " Open Interest has increased by " + str(int(percentage_change)) + "% within the last day."
            print(email)
            sendEmail(email)

            futures_strategy3_blacklist[x] = time() + (60 * 60 * 24 * 2) # 2 day cooldown


def spot_strategy1():
    # Coin price up 50% in 1 hour, with $5 million in daily volume. Cooldown for 4 hours. 

    for x in spot_price_data.keys():
        length = len(spot_price_data[x])
        if length >= 60: # last 30 minutes price data
            length = 60
        
        l = spot_price_data[x][:length]
        percentage_change = (max(l)/min(l) - 1) * 100
        
        if percentage_change >= 10 and l.index(max(l)) < l.index(min(l)) and x not in spot_strategy1_blacklist and spot_daily_volume[x] >= 5000000 and l[0]/min(l) >= 1.1: # Also current price is also up 100%. 2
            email = x + " has pumped by " + str(int(percentage_change)) + "% within the last 30 minutes!"
            print(email)
            sendEmail(email)

            spot_strategy1_blacklist[x] = time() + (60 * 60 * 4) # 4 hour cooldown

def spot_strategy2():
    # Coin price up 100% in 2 hours, with $5 million in daily volume. Cooldown for 8 hours. 
    for x in spot_price_data.keys():
        length = len(spot_price_data[x])
        if length >= 120: # last 2 hour price data
            length = 120
        
        l = spot_price_data[x][:length]
        percentage_change = (max(l)/min(l) - 1) * 100
        
        if percentage_change >= 20 and l.index(max(l)) < l.index(min(l)) and x not in spot_strategy1_blacklist and spot_daily_volume[x] >= 10000000 and l[0]/min(l) >= 1.2: # Also current price is also up 200% from min price. 3
            email = x + " has pumped by " + str(int(percentage_change)) + "% within the last 30 minutes!"
            print(email)
            sendEmail(email)

            spot_strategy2_blacklist[x] = time() + (60 * 60 * 8) # 8 hour cooldown

def main():
    # clearBlacklist()

    now = datetime.today()

    secondsLeft = 60 - (now.timestamp() % 60) # Seconds left for the next execution. 
    print("Executing in " + str(math.floor(secondsLeft)) + " seconds.")
    
    sleep(secondsLeft)
    
    spot.main()
    fillSpotData()
    fillSpotVolume()


    futures.main()
    
    fillFuturesData()

    spot_strategy1()
    spot_strategy2()

    futures_strategy1()
    futures_strategy2()
    futures_strategy3()

    # Clear data before repeating
    oi_data.clear()
    price_data.clear()
    spot_price_data.clear()
    spot_daily_volume.clear()

    now = datetime.today()

    print("\n" * 5)
    print("Analzyed 200+ pairs in and ran 5 strategies on them within " + str(math.floor(now.timestamp() % 60)) + " seconds.")

    main()


main()
