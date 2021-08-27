from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

r_api_key = 'GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  # Put your own api keys here
r_api_secret = 'gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032'

# Binance Client Object
realclient = Client(r_api_key, r_api_secret)


def spot_trade(trade):
    symbol = trade.pair
    base = trade.base
    coin = symbol.replace(trade.base, '')
    trade.price = float(realclient.get_symbol_ticker(symbol=trade.pair)['price'])
    trade.time = realclient.get_server_time()['serverTime']
    trade.id = trade.time
    trade.lowest = trade.price
    trade.highest = trade.price
    trade.status = 'active'
    print(trade.pair)
    print(trade.id)
    print(trade.status)


def futures_trade(trade):
    symbol = trade.pair
    base = trade.base
    coin = symbol.replace(trade.base, '')
    trade.price = float(realclient.get_symbol_ticker(symbol=trade.pair)['price'])
    trade.time = realclient.futures_time()['serverTime']
    trade.id = trade.time
    trade.lowest = trade.price
    trade.highest = trade.price
    trade.status = 'active'
    print(trade.pair)
    print(trade.id)
    print(trade.status)


def mfutures_trade(trade):
    symbol = trade.pair
    base = trade.base
    coin = symbol.replace(trade.base, '')
    trade.price = float(realclient.get_symbol_ticker(symbol=trade.pair)['price'])
    trade.time = realclient.futures_time()['serverTime']
    trade.id = trade.time
    trade.lowest = trade.price
    trade.highest = trade.price
    trade.status = 'active'
