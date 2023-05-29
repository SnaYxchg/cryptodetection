import requests
import pandas as pd
import time

# Just take tickers from the csv file

futuresTickers = ['BTCUSDT', 'ETHUSDT', 'BCHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT', 'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT', 'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT', 'SXPUSDT', 'KAVAUSDT', 'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT', 'DEFIUSDT', 'YFIUSDT', 'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'SRMUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT', 'AVAXUSDT', 'FTMUSDT', 'HNTUSDT', 'ENJUSDT', 'FLMUSDT', 'TOMOUSDT', 'RENUSDT', 'KSMUSDT', 'NEARUSDT', 'AAVEUSDT', 'FILUSDT', 'RSRUSDT', 'LRCUSDT', 'MATICUSDT', 'OCEANUSDT', 'CVCUSDT', 'BELUSDT', 'CTKUSDT', 'AXSUSDT', 'ALPHAUSDT', 'ZENUSDT', 'SKLUSDT', 'GRTUSDT', '1INCHUSDT', 'CHZUSDT', 'SANDUSDT', 'ANKRUSDT', 'BTSUSDT', 'LITUSDT', 'UNFIUSDT', 'REEFUSDT', 'RVNUSDT', 'SFPUSDT', 'XEMUSDT', 'BTCSTUSDT', 'COTIUSDT', 'CHRUSDT', 'MANAUSDT', 'ALICEUSDT', 'HBARUSDT', 'ONEUSDT', 'LINAUSDT', 'STMXUSDT', 'DENTUSDT', 'CELRUSDT', 'HOTUSDT', 'MTLUSDT', 'OGNUSDT', 'NKNUSDT', 'SCUSDT', 'DGBUSDT', '1000SHIBUSDT', 'BAKEUSDT', 'GTCUSDT', 'BTCDOMUSDT', 'TLMUSDT', 'IOTXUSDT', 'AUDIOUSDT', 'RAYUSDT', 'C98USDT', 'MASKUSDT', 'ATAUSDT', 'DYDXUSDT', '1000XECUSDT', 'GALAUSDT', 'CELOUSDT', 'ARUSDT', 'KLAYUSDT', 'ARPAUSDT', 'CTSIUSDT', 'LPTUSDT', 'ENSUSDT', 'PEOPLEUSDT', 'ANTUSDT', 'ROSEUSDT', 'DUSKUSDT', 'FLOWUSDT', 'IMXUSDT', 'API3USDT', 'GMTUSDT', 'APEUSDT', 'BNXUSDT', 'WOOUSDT', 'FTTUSDT', 'JASMYUSDT', 'DARUSDT', 'GALUSDT', 'OPUSDT', 'INJUSDT', 'STGUSDT', 'FOOTBALLUSDT', 'SPELLUSDT', '1000LUNCUSDT', 'LUNA2USDT', 'LDOUSDT', 'CVXUSDT', 'ICPUSDT', 'APTUSDT', 'QNTUSDT', 'BLUEBIRDUSDT', 'DODOBUSD', 'ANCBUSD', 'LEVERBUSD', 'AUCTIONBUSD', 'AMBBUSD', 'PHBBUSD']
futuresCoins = []

pureSpotCoins = []
allSpotTickers = [] # Every single spot ticker
pureSpotTickers = []

pureSpotPriceData = {} # Ticker: price

# Can filter for delisted coins as well in the future 

def fetchOnlySpotCoinsAndSetPrices():
    allSpotCoins = []

    for x in futuresTickers:
        futuresCoins.append(x[:-4])
    
    URL = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url = URL)
    data = r.json()

    for x in data:
        allSpotTickers.append(x['symbol'])
        coin = x['symbol']
        
        # Choose if last 4 characters are busd and usdt coins
        if coin[-4:] == "BUSD" or coin[-4:] == "USDT":
            allSpotCoins.append(x['symbol'][:-4])
    
    # Removing duplicates and futures coins
    spotCoins = [*set(allSpotCoins)]
    for x in spotCoins:
        # Removing UP DOWN BEAR BULL
        if x not in futuresCoins and x[-2:] != "UP" and x[-4:] not in ["DOWN", "BULL", "BEAR"]:
            pureSpotCoins.append(x)
    
    # Setting prices of usdt pure spot
    for x in pureSpotCoins: 
        USDTsymbol = x + "USDT"
        for y in data: # adding all usdt ones
            if y['symbol'] == USDTsymbol:
                pureSpotPriceData[USDTsymbol] = y['price']
                pureSpotTickers.append(USDTsymbol)
                break

    # Setting prices of busd pure spot
    for x in pureSpotCoins:

        USDTsymbol = x + "USDT"
        BUSDsymbol = x + "BUSD"

        for z in data: # adding pure busd ones
            if z['symbol'] == BUSDsymbol and USDTsymbol not in pureSpotPriceData:
                pureSpotPriceData[BUSDsymbol] = z['price']
                pureSpotTickers.append(BUSDsymbol)
                break

def sort_prices():
    sorted_prices = []

    for x in pureSpotTickers:
        sorted_prices.append(pureSpotPriceData[x])

    return sorted_prices

def main():
    fetchOnlySpotCoinsAndSetPrices()

    data = {"Ticker": pureSpotTickers, "Prices": sort_prices()}

    df = pd.DataFrame(data)

    str_time = str(time.strftime("%d,%m,%y,%H,%M"))
    df.to_csv('spot_data/' + str_time + '.csv', encoding='utf-8', index = False)