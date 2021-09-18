from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime
import math
import time
MIN_TRADE_VALUE = 10

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


def futures_trade(signal, percentage):
    symbol = signal.pair
    margin = 0.99
    balance = float(realclient.futures_account_balance()[1]['withdrawAvailable'])  # Get available funds
    if balance*margin*percentage < MIN_TRADE_VALUE:
        print('Low Funds')
        raise ValueError("Funds too low to take this trade")

    if signal.conditions.direction == 'long':
        side = 'BUY'
    elif signal.conditions.direction == 'short':
        side = 'SELL'
    isolated = True
    if signal.conditions.mode == 'cross':
        isolated = False
        try:
            realclient.futures_change_margin_type(symbol=symbol, mode='CROSS')
        except:
            print('already cross')
    else:
        try:
            realclient.futures_change_margin_type(symbol=symbol, mode='ISOLATED')
        except:
            print('already iso')

    # Get futures coin precision
    coin_precision = None
    for i in realclient.futures_exchange_info()['symbols']:
        if i['pair'] == symbol:
            coin_precision = i['quantityPrecision']
            break

    # Calculate trade values
    amount = balance*margin*percentage*signal.conditions.leverage
    amount = str(float(round_decimals_down(amount, coin_precision)))  # Round Base amount
    pair_price = float(realclient.get_symbol_ticker(symbol=symbol)['price'])  # Get coin price
    q = float(amount) / pair_price  # Define trade quantities
    q = float(round_decimals_down(q, coin_precision))  # Round trade Quantities

    realclient.futures_change_leverage(symbol=symbol, leverage=signal.conditions.leverage)
    print(balance*percentage)
    trade_receipt = realclient.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=q, isolated=isolated)

    # Move all this shit into trade_classes
    signal.id = trade_receipt['orderId']
    signal.receipt = realclient.futures_get_order(orderId=signal.id, symbol=symbol)
    signal.time = signal.receipt['time']
    signal.price = float(signal.receipt['avgPrice'])
    signal.lowest = signal.price
    signal.highest = signal.price
    signal.amount = float(signal.receipt['executedQty'])
    signal.status = 'active'

    sell_orders = []
    if side == 'BUY':
        side = 'SELL'
    elif side == 'SELL':
        side = 'BUY'

    trade_qty = float(trade_receipt['origQty'])

    print(signal.conditions.stoploss)
    receipt_sl = realclient.futures_create_order(symbol=symbol, side=side, type='STOP_MARKET', quantity=trade_qty, stopPrice=signal.conditions.stoploss,
                                              timeInForce='GTC', reduceOnly=True)
    signal.conditions.orders.append(receipt_sl)
    receipt_tp = realclient.futures_create_order(symbol=symbol, side=side, type='LIMIT', quantity=trade_qty, price=signal.conditions.stopprof,
                                              timeInForce='GTC', reduceOnly=True)
    signal.conditions.orders.append(receipt_tp)
    return signal


def futures_update(sell_orders):
    stop_orders = False
    symbol = sell_orders[0]['symbol']
    for s in sell_orders:
        stopstatus = realclient.futures_get_order(orderId=s['orderId'], symbol=symbol)['status']
        if stopstatus == 'filled':
            stop_orders = True
    if stop_orders:
        for s in sell_orders:
            realclient.futures_cancel_order(orderId=s['orderId'], symbol=symbol)


def mfutures_trade(signal, percentage):
    symbol = signal.pair
    base = 'USDT'
    coin = symbol.replace(base, '')
    margin = 0.99  # Allow for margin errors
    trade_size = percentage  # Percentage of available funds to invest
    balance = float(realclient.futures_account_balance()[1]['withdrawAvailable'])  # Get available funds
    amount = balance * trade_size * margin  # Define investment amount
    base_precision = 2  # Base is always usdt, futures usdt has precision 2
    side = ''
    if signal.conditions.direction == 'long':
        side = 'BUY'
    elif signal.conditions.direction == 'short':
        side = 'SELL'
    isolated = True
    if signal.conditions.mode == 'cross':
        isolated = False

    coin_precision = None
    # Get futures coin precision
    for i in realclient.futures_exchange_info()['symbols']:
        if i['pair'] == symbol:
            coin_precision = i['quantityPrecision']
            break

    amount = str(float(round_decimals_down(amount, coin_precision)))  # Round Base amount
    pair_price = float(realclient.get_symbol_ticker(symbol=symbol)['price'])  # Get coin price
    q = float(amount) / pair_price  # Define trade quantities
    q = float(round_decimals_down(q, coin_precision))  # Round trade Quantities

    trade1_receipt = realclient.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=q, isolated=isolated)
    trade_time = trade1_receipt['updateTime']

    ''' ABOVE is the Buying part of the trade, BELOW is setting up sell orders for takeprofit and stoploss  '''

    print(trade1_receipt)

    info = realclient.futures_exchange_info()['symbols'][1]
    step_size = float(info['filters'][1]['stepSize'])
    tick_size = float(info['filters'][0]['tickSize'])
    trade_qty = float(trade1_receipt['origQty'])
    units = trade_qty/step_size
    loss_amount = trade_qty  # 100% of Trade

    leverage = signal.conditions.leverage
    proftargets = signal.conditions.proftargets
    profit_dist = signal.conditions.stopprof
    profit_qty = []
    losstargets = signal.conditions.losstargets
    stop_order_receipts = []

    if side == 'BUY':
        side = 'SELL'
    elif side == 'SELL':
        side = 'BUY'

    # Take profit quantities math
    tot = 0
    for d in profit_dist:
        qty = float(math.floor(d * units))
        profit_qty.append(qty)
        tot += qty

    # Dealing with remainders
    leftovers = units - tot
    print(leftovers)
    for x in range(int(leftovers)):
        profit_qty[x] += 1

    # Setting TP quantities
    prof_qty = []
    for p in profit_qty:
        p = float(p * step_size)
        prof_qty.append(p)
    print(prof_qty)

    # Order to Sell 100% of trade if it hits STOPLOSS
    stoploss_receipt = realclient.futures_create_order(symbol=symbol, side=side, type='STOP_MARKET', quantity=loss_amount, stopPrice=losstargets[0], timeInForce='GTC', reduceOnly=True)
    stop_order_receipts.append(stoploss_receipt)

    for p, t in zip(prof_qty, proftargets):
        print(p, t)

        receipt = realclient.futures_create_order(symbol=symbol, side=side, type='LIMIT', quantity=p, price=t, timeInForce='GTC', reduceOnly=True)
        stop_order_receipts.append(receipt)
    return stop_order_receipts


def mfutures_update(signal, stop_order_receipts):
    cancel_stoploss = False
    cancel_stopprof = False
    stopstatus = realclient.futures_get_order(orderId=stop_order_receipts[0]['orderId'], symbol=signal.pair)['status']
    if not stopstatus == 'NEW':
        cancel_stopprof = True
    profstatus = realclient.futures_get_order(orderId=stop_order_receipts[len(stop_order_receipts)]['orderId'], symbol=signal.pair)['status']
    if not profstatus == 'NEW':
        cancel_stoploss = True

    if cancel_stopprof or cancel_stoploss:
        for s in stop_order_receipts:
            if s['orderId'] == 'NEW':
                realclient.futures_cancel_order(orderId=s['orderId'], symbol=signal.pair)
    else:
        skipfirst = False
        count = 0
        for s in stop_order_receipts:
            if skipfirst:
                count += 1
                if s['orderId'] == 'Filled':
                    stop_order_receipts[0] = update_stoploss(signal.conditions.losstargets[count], stop_order_receipts[0])
            skipfirst = True


def update_stoploss(new_sl, current_order):
    old_id = current_order['orderId']
    symbol = current_order['symbol']
    side = current_order['side']
    o_type = current_order['type']
    quantity = current_order['origQty']
    realclient.futures_cancel_order(orderId=old_id,symbol=symbol) # Remove Old stoploss order
    # Place updated stoploss order
    return realclient.futures_create_order(symbol=symbol, side=side, type=o_type, quantity=quantity, stopPrice=new_sl, timeInForce='GTC', reduceOnly=True)


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
