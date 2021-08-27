from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime
import math

# Binance API Keys, TODO: Switch these to environmental variables if this code ever goes public
r_api_key = 'GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  # Put your own api keys here
r_api_secret = 'gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032'

# Binance Client Object
realclient = Client(r_api_key, r_api_secret)


# Rounds a decimal value down, to account for binance precision values
def round_decimals_down(number: float, decimals: int = 2):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)
    factor = 10 ** decimals
    return math.floor(number * factor) / factor


# Performs a percentage market trade of any spot coin, using BTC or USDT as the base
def market_trade(signal, percentage, buying):
    symbol = signal.pair
    base = signal.base
    coin = symbol.replace(base, '')
    trade_size = percentage
    market_order = '-1'

    if not buying:
        # buying back btc or usdt
        # find symbol precision
        symbol_info = realclient.get_symbol_info(symbol)
        step_size = 0.0
        for f in symbol_info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
        precision = int(round(-math.log(step_size, 10), 0))

        balance = float(realclient.get_asset_balance(asset=coin)['free'])
        balance = balance * trade_size
        quant = str(float(round_decimals_down(balance, precision)))

        try:
            market_order = realclient.order_market_sell(symbol=symbol, quantity=quant)
            print('Sold Coin')
        except BinanceAPIException:
            print('Exception, probably relating to not enough funds to make trade')

    else:
        # buying amount of signal coin
        balance = float(realclient.get_asset_balance(asset=base)['free'])
        balance = balance * trade_size
        if base == 'USDT':
            precision = 8
        elif base == 'BTC':
            precision = 6
        balance = str(float(round_decimals_down(balance, precision)))

        try:
            market_order = realclient.create_order(symbol=symbol, type="market", side='buy', quoteOrderQty=balance,
                                                   price=None)
            print('Bought Coin')
        except BinanceAPIException:
            print('Exception, probably relating to not enough funds to make trade')

    signal.init_vals(market_order)
    return market_order


def getprice(coinpair):
    return realclient.get_symbol_ticker(symbol=coinpair)['price']


# converts all spot btc to usdt
def btc2usdt():
    balance = float(realclient.get_asset_balance(asset='BTC')['free'])
    mintrade = 10/float(realclient.get_symbol_ticker(symbol='BTCUSDT')['price'])
    if balance > mintrade:
        quant = str(float(round_decimals_down(balance, 6)))
        try:
            market_order = realclient.order_market_sell(symbol='BTCUSDT', quantity=quant)
        except:
            print('Exception converting BTC to USDT')
        print("Converted BTC to USDT")


# Converts all spot usdt to btc
def usdt2btc():
    amount = float(realclient.get_asset_balance(asset='USDT')['free'])
    if amount > 10:
        try:
            market_order = realclient.create_order(symbol='BTCUSDT', type="market", side='buy', quoteOrderQty=amount,
                                                   price=None)
        except:
            print('Exception converting USDT to BTC')
        print("Converted USDT to BTC")


# Checks alls base pairings of a coin, ect   BTCUSDT, BTCBUSD, BTCETH,
def coin_pairs(coinname):
    exchange_info = realclient.get_exchange_info()
    pairs = []
    for s in exchange_info['symbols']:
        if s['baseAsset'] == coinname:
            print(s['symbol'])
            pairs.append(s['symbol'])
    return pairs


# Checks if coin has a USDT pairing
def isUSDTpair(coinname):
    pairs = coin_pairs(coinname)
    for p in pairs:
        if 'USDT' in p:
            return True
    return False


# Checks if coin has a BTC pairing
def isBTCpair(coinname):
    pairs = coin_pairs(coinname)
    for p in pairs:
        if 'BTC' in p:
            return True
    return False


# Gets Server Time
def timenow():
    raw_server_time = realclient.get_server_time()
    return raw_server_time['serverTime']


# Gets Server Time in readable form, TODO CHANGE TO DATE/TIME
def datetimenow():
    raw_server_time = realclient.get_server_time()
    server_time = datetime.fromtimestamp(raw_server_time['serverTime'] / 1000.0)
    return server_time


# Print out a viewable snapshot of current futures account state
def futures_snapshot():
    # get futures info
    tangibles = realclient.futures_account_balance()
    retstring = ''

    for t in tangibles:
        if float(t["balance"]) > 0:
            print(t['asset'], "Balance: ", t['balance'])
            if 'withdrawAvailable' in t:
                perc_withdraw = float(t['withdrawAvailable']) / float(t['balance']) * 100
                print('   Avaliable: ', t["withdrawAvailable"], '\033[94m', round(perc_withdraw, 2), '%', '\033[0m')

    # get futures positions
    positions = realclient.futures_position_information()
    for p in positions:
        if (float(p['positionAmt']) > 0) or (float(p['positionAmt']) < 0):
            # print(p)
            # Determine if position is in profit or loss
            gain = True
            if float(p['unRealizedProfit']) < 0:
                gain = False

            # Calculate percentage profit or loss
            percentage = str(abs((float(p['markPrice']) - float(p['entryPrice'])) / float(p['markPrice']) * 100 * int(
                p['leverage'])))
            if gain:
                percentage = '\033[92m' + percentage + '\033[0m'
            elif not gain:
                percentage = '\033[91m' + '-' + percentage + '\033[0m'

            pos = "\nPair: " + p['symbol']

            if p['marginType'] == 'isolated':
                staked_and_pnl = float(p['isolatedWallet']) + float(p['unRealizedProfit'])
                pos += "\nStaked: " + p['isolatedWallet']
            elif p['marginType'] == 'cross':
                staked = abs(float(p['positionAmt'])) * float(p['entryPrice']) * 1 / int(p['leverage'])
                pos += "\nStaked: " + str(staked)
                staked_and_pnl = staked + float(p['unRealizedProfit'])
            else:
                print("Problem checking margin Type")
            pos += "\nCurrent: " + str(staked_and_pnl)
            pos += "\n\nAmount: " + p['positionAmt']
            pos += "\nEntry: " + p['entryPrice']
            pos += "\nMark: " + p['markPrice']
            pos += "\nLeverage: " + p['leverage']

            pos += "\n\nPNL: " + p['unRealizedProfit']
            pos += "\nPNL Percent: " + str(percentage) + ' %'
            pos += "\nStop Loss: " + "gotta add that shit"
            pos += "\nTake Profit: " + "repeat above"
            pos += "\nLIQ: " + p['liquidationPrice']
            pos += "\nType: " + p['marginType']
            pos += "\n---------------------"
            retstring += pos
        return retstring
