from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime
import math
from datetime import datetime
import pytz
from config import get_binance_config
import utility

MIN_TRADE_VALUE = 10

# Binance Client Object
realclient = get_binance_config

# Get futures balance
def get_futures_balance():
    # Retrieve futures balance
    balance = None
    balances = realclient.futures_account_balance()
    for b in balances:
        if b['asset'] == 'USDT':
            balance = float(b['withdrawAvailable'])
            print('Balance = ', balance)
    return balance


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


def change_margin_type(in_type, symbol):
    isolated = True
    if in_type == 'cross':
        isolated = False
        try:
            realclient.futures_change_margin_type(symbol=symbol, marginType='CROSSED')
        except Exception as e:
            print(e)
    elif in_type == 'isolated':
        print('Changing', symbol, ' to mode: Isolated')
        try:
            realclient.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
        except Exception as e:
            print(e)
    else:
        print('Unreachable code')

    return isolated


def get_coin_precision(symbol):
    coin_precision = None
    # Get futures coin precision
    for i in realclient.futures_exchange_info()['symbols']:
        if i['pair'] == symbol:
            coin_precision = i['quantityPrecision']
            break
    return coin_precision


def get_price_precision(symbol):
    symbol_info = realclient.get_symbol_info(symbol)
    for f in symbol_info['filters']:
        if f['filterType'] == 'PRICE_FILTER':
            tick_size = str(f['tickSize'])
    split = tick_size.split('.')
    split = split[1].split('1')
    price_precision = len(split[0]) + 1
    print('TickPrecision', price_precision)
    return price_precision


def no_liquidate(signal):
    price = signal.price
    if signal.type == 'mfutures':
        current_sl = signal.conditions.losstargets[0]
    elif signal.type == 'futures':
        current_sl = signal.conditions.stoploss
    else:
        print("Can't Identify Signal Type")
        current_sl = 0

    for f in realclient.futures_exchange_info()['symbols']:
        if f['pair'] == signal.pair:
            price_precision = f['pricePrecision']

    margin = 0.75
    if signal.conditions.direction.upper() == 'LONG':
        price = price - (price/signal.conditions.leverage) * margin
        if not (price > current_sl):
            price = current_sl
    else:
        price = price + (price/signal.conditions.leverage) * margin
        if not (price < current_sl):
            price = current_sl
    price = float(round_decimals_down(price, price_precision))
    return price


def mfutures_reduce_orders(signal):
    reduction_percentage = 0.999
    addition_percentage = 1+1-reduction_percentage
    price_precision = get_price_precision(signal.pair)

    new_proftargets = []
    if signal.conditions.direction == 'long':
        for p in signal.conditions.proftargets:
            p = p*reduction_percentage
            p = float(round_decimals_down(p, price_precision))
            new_proftargets.append(p)
    elif signal.conditions.direction == 'short':
        for p in signal.conditions.proftargets:
            p = p*addition_percentage
            p = float(round_decimals_down(p, price_precision))
            new_proftargets.append(p)
    print(new_proftargets)

    signal.conditions.proftargets = new_proftargets


def mfutures_optimize_targets(signal):
    print('preTargets', signal.conditions.proftargets)
    print('Optimizing Results.....')
    price = signal.price
    entry = signal.conditions.expected_entry
    targets = signal.conditions.proftargets
    t1 = targets[0]
    t2 = targets[1]
    if signal.conditions.direction.upper() == 'SHORT':

        if (price-t1) < (entry-t1)/2:
            newprice = (t1+t1+t2)/3
            signal.conditions.proftargets[0] = newprice
            print('Optimized T1')

    elif signal.conditions.direction.upper() == 'LONG':
        print('dif1', price-entry)
        print('dif2', (t1-entry)/2)
        if (price-entry) > (t1-entry)/2:
            newprice = (t1+t1+t2)/3
            signal.conditions.proftargets[0] = newprice
            print('Optimized T1')


def mfutures_fix_zeros(signal):
    price = signal.price
    entry = signal.conditions.expected_entry
    # if difference between entry is greater than 50%, see if we can fix a 0 count error
    absolute_diff = abs((entry-price)/entry)*100
    zero_value = [None, None]
    if absolute_diff > 50:
        # abnormal entry price
        # try different 0 values
        for x in range(4):
            test_entry = entry / (10**x)
            test_entry2 = entry * (10**x)
            diff = abs((test_entry - price)/test_entry)*100
            diff2 = abs((test_entry2 - price)/test_entry2)*100
            print('testentry', test_entry, 'price', price, 'diff', diff)
            print('testentry2', test_entry2, 'price', price, 'diff2', diff2)
            if diff < absolute_diff:
                print('Wrong number of Zeros Divide')
                absolute_diff = diff
                zero_value[0] = x
                zero_value[1] = 'divide'
                signal.conditions.expected_entry = entry/10**x

            if diff2 < absolute_diff:
                print('Wrong number of Zeros Multiply')
                absolute_diff = diff2
                zero_value[0] = x
                zero_value[1] = 'multi'
                signal.conditions.expected_entry = entry*10**x

        if zero_value[0]:
            print('Adjust other values')
            print(zero_value)
            adjustment = 10 ** (zero_value[0])
            if zero_value[1] == 'multi':
                new_targets = []
                for x in signal.conditions.proftargets:
                    j = x*adjustment
                    print('from ', x, 'to', j)
                    new_targets.append(j)
                signal.conditions.proftargets = new_targets
            elif zero_value[1] == 'divide':
                new_targets = []
                for x in signal.conditions.proftargets:
                    j = x/adjustment
                    new_targets.append(j)
                signal.conditions.proftargets = new_targets
            print('After adjustments', signal.conditions.proftargets)

            bad_signal = False
            for f in range(len(signal.conditions.proftargets)-1):
                firsttarget = signal.conditions.proftargets[f]
                secondtarget = signal.conditions.proftargets[f+1]
                target_diff = abs((firsttarget-secondtarget)/firsttarget)*100
                print('targetdiff', target_diff)
                if target_diff > 50:
                    raise ValueError('Problem Resolving target values')
        else:
            raise ValueError('Entry Value difference too large')

    print('Entry diff', round(absolute_diff, 2))


def futures_trade_no_orders(signal, trade_size, bag_id=None):
    # Stop 100% margin errors
    if trade_size == 1:
        trade_size = 0.99

    # Retrieve futures balance
    balance = get_futures_balance()

    # Define investment amount
    amount = balance * trade_size
    # Cancel trade if low funds
    if amount < MIN_TRADE_VALUE:
        print('Low Funds')
        raise ValueError("Funds too low to take this trade, Balance: " + str(balance))

    # Portfolios String, can remove
    signal.portfolio_amount = '[' + str(amount) + '/' + str(realclient.futures_account_balance()[1]['balance']) + ']'

    # Define buying direction
    side = ''
    if signal.conditions.direction.upper() == 'LONG':
        side = 'BUY'
    elif signal.conditions.direction.upper() == 'SHORT':
        side = 'SELL'

    isolated = True
    change_margin_type('isolated', signal.pair)
    for f in realclient.futures_exchange_info()['symbols']:
        if f['pair'] == signal.pair:
            pass
    # Get futures coin precision
    coin_precision = None
    for i in realclient.futures_exchange_info()['symbols']:
        if i['pair'] == signal.pair:
            coin_precision = i['quantityPrecision']
            break

    # Set Trade Leverage
    realclient.futures_change_leverage(symbol=signal.pair, leverage=int(signal.conditions.leverage))

    pair_price = float(realclient.get_symbol_ticker(symbol=signal.pair)['price'])  # Get coin price
    q = amount*signal.conditions.leverage / pair_price  # Define trade quantities
    q = round_decimals_down(q, coin_precision)  # Round trade Quantities

    # BUY Order
    trade_receipt = realclient.futures_create_order(symbol=signal.pair, side=side, type='MARKET', quantity=q, isolated=isolated)
    trade_time = trade_receipt['updateTime']

    trade_id = trade_receipt['orderId']
    receipt = realclient.futures_get_order(orderId=trade_id, symbol=signal.pair)
    receipt['transactTime'] = utility.convert_timestamp_utc8(receipt['transactTime'])
    receipt['time'] = utility.convert_timestamp_utc8(receipt['time'])
    signal.init_trade_futures(trade_id, receipt)

    # Add receipt to filled orders
    signal.conditions.filled_orders.append(receipt)

    if bag_id:
        signal.bag_id.append(bag_id)
    print("Made Futures Order")
    return True


def futures_trade_add_orders(signal):
    # Set Initial Stoploss just above liquidation, or the given SL if it is closer
    liquidation_sl = no_liquidate(signal)
    signal.conditions.stoploss = liquidation_sl

    # Set price precision
    price_precision = get_price_precision(signal.pair)
    signal.conditions.stopprof = round(signal.conditions.stopprof, price_precision)
    trade_qty = float(signal.receipt['origQty'])
    stop_order_receipts = []

    # Switch from buying to selling, or from shorting to rebuying
    if signal.conditions.direction == 'short':
        side = 'BUY'
    elif signal.conditions.direction == 'long':
        side = 'SELL'

    # Order to Sell 100% of trade if it hits STOPLOSS
    print(signal.pair, side, trade_qty, signal.conditions.stoploss)
    stoploss_receipt = realclient.futures_create_order(symbol=signal.pair, side=side, type='STOP_MARKET', quantity=trade_qty, stopPrice=signal.conditions.stoploss, timeInForce='GTC', reduceOnly=True)
    # Record Pending Order
    stop_order_receipts.append(stoploss_receipt)

    print(signal.pair, side, trade_qty, signal.conditions.stopprof)
    # Place the take profit order
    receipt = realclient.futures_create_order(symbol=signal.pair, side=side, type='LIMIT', quantity=trade_qty, price=signal.conditions.stopprof, timeInForce='GTC', reduceOnly=True)

    # Record orders placed
    stop_order_receipts.append(receipt)
    # Record all orders
    signal.conditions.orders = stop_order_receipts
    print('Completed Futures Sell Orders')


def mfutures_trade_add_orders(signal):
    # Set Initial Stoploss just above liquidation, or the given SL if it is closer
    liquidation_sl = no_liquidate(signal)
    signal.conditions.losstargets[0] = liquidation_sl

    coin_precision = get_coin_precision(signal.pair)
    trade_qty = float(signal.receipt['origQty'])

    units = trade_qty
    step = 1/(10**coin_precision)

    if not coin_precision == 0:
        units = int(trade_qty / step)
    print('Units:', units)

    # If signal is posted with incorrect zeros, will try to fix it up
    mfutures_fix_zeros(signal)
    # Adjust target values, if signal comes too late compared to the price
    mfutures_optimize_targets(signal)
    # Slightly increase/reduce proftargets, to stay ahead of exact values and others
    mfutures_reduce_orders(signal)

    # Get profittargets, target distribution and losstargets,
    proftargets = signal.conditions.proftargets
    profit_dist = signal.conditions.stopprof
    profit_qty = []
    losstargets = signal.conditions.losstargets
    stop_order_receipts = []

    # Switch from buying to selling, or from shorting to rebuying
    if signal.conditions.direction == 'short':
        side = 'BUY'
    elif signal.conditions.direction == 'long':
        side = 'SELL'

    # Take profit quantities math
    tot = 0
    for d in profit_dist:
        qty = float(math.floor((d * units)/100))
        profit_qty.append(qty)
        tot += qty

    # Dealing with remainders, first add a unit remainder to any targets with 0 qty, afterwards place front to back
    leftovers = units - tot
    for x in range(int(leftovers)):
        allocated = False
        i = 0
        while not allocated and i < len(profit_qty):
            if not (profit_qty[i] > 0):
                profit_qty[i] += 1
                allocated = True
            else:
                i += 1
        if not allocated:
            profit_qty[x] += 1

    # Setting TakeProfit quantities
    prof_qty = []
    for p in profit_qty:
        if not coin_precision == 0:
            p = round((float(p) * float(step)), coin_precision)
        prof_qty.append(p)
    profit_qty = prof_qty
    print(profit_qty)

    # Order to Sell 100% of trade if it hits STOPLOSS
    stoploss_receipt = realclient.futures_create_order(symbol=signal.pair, side=side, type='STOP_MARKET', quantity=trade_qty, stopPrice=losstargets[0], timeInForce='GTC', reduceOnly=True)
    # Record Pending Order
    stop_order_receipts.append(stoploss_receipt)

    # Place a take profit order for each target
    # P is for price, T is for target
    for p, t in zip(profit_qty, proftargets):
        if p > 0:
            # Place reduce order
            receipt = realclient.futures_create_order(symbol=signal.pair, side=side, type='LIMIT', quantity=p, price=t, timeInForce='GTC', reduceOnly=True)
            # Record orders placed
            stop_order_receipts.append(receipt)
        else:
            print('Quantity too small to place order')
            # If a target has no quantity to sell, don't place the order

    # Record all orders
    signal.conditions.orders = stop_order_receipts


def mfutures_trade(signal, trade_size, bag_id=None):
    futures_trade_no_orders(signal, trade_size, bag_id=bag_id)
    mfutures_trade_add_orders(signal)


# Checks to see if any of the signals orders have been filled, and if they have then update the signal status
def futures_update(signal):
    sell_orders = signal.conditions.orders
    stop_orders = False
    symbol = sell_orders[0]['symbol']
    stoplossstatus = realclient.futures_get_order(orderId=sell_orders[0]['orderId'], symbol=symbol)['status']
    stopprofstatus = realclient.futures_get_order(orderId=sell_orders[1]['orderId'], symbol=symbol)['status']

    # todo too many if statements here, I think can handle this with 2 if statements
    if stoplossstatus == 'FILLED':
        stop_orders = True
        signal.status = 'stoploss'
        signal.closed = float(realclient.futures_get_order(orderId=sell_orders[0]['orderId'], symbol=symbol)['stopPrice'])
    elif stoplossstatus == 'EXPIRED':
        print('Changing ')
        stop_orders = True
        signal.status = 'manual'
    elif stopprofstatus == 'FILLED':
        stop_orders = True
        signal.status = 'stopprof'
        signal.closed = float(realclient.futures_get_order(orderId=sell_orders[1]['orderId'], symbol=symbol)['stopPrice'])
    elif stopprofstatus == 'EXPIRED':
        stop_orders = True
        signal.status = 'manual'
    if stop_orders:
        for s in sell_orders:
            if realclient.futures_get_order(orderId=s['orderId'], symbol=symbol)['status'] == 'NEW':
                try:
                    realclient.futures_cancel_order(orderId=s['orderId'], symbol=symbol)
                except ValueError:
                    print('Order Already Canceled')
        return True
    return False


def update_stoploss(new_sl, current_order):
    old_id = current_order['orderId']
    symbol = current_order['symbol']
    side = current_order['side']
    o_type = current_order['type']
    quantity = current_order['origQty']
    # Remove Old stoploss order
    realclient.futures_cancel_order(orderId=old_id, symbol=symbol)
    # Place updated stoploss order
    print('Cancled and new sl price', new_sl)
    new_order = realclient.futures_create_order(symbol=symbol, side=side, type=o_type, quantity=quantity, stopPrice=new_sl, timeInForce='GTC', reduceOnly=True)
    return new_order


# Performs a multi exit futures trade, based on a signals object data
def mfutures_update(signal):
    # Boolean which represents an update has occured
    changes = False
    # Get current Orders
    stop_order_receipts = signal.conditions.orders

    if signal.status == 'active':
        # Checks if the last profit target order has completed
        proforder = realclient.futures_get_order(orderId=stop_order_receipts[len(stop_order_receipts)-1]['orderId'], symbol=signal.pair)
        profstatus = proforder['status']
        if not profstatus == 'NEW':
            signal.conditions.filled_orders.append(proforder)
            # If all profit targets are hit, cancel the stoploss order
            stoporder = realclient.futures_get_order(orderId=stop_order_receipts[0]['orderId'], symbol=signal.pair)
            stopstatus = stoporder['status']
            o_id = stoporder['orderId']
            if stopstatus == 'NEW':
                realclient.futures_cancel_order(orderId=o_id, symbol=signal.pair)

            # Order closed because all profits hit
            if profstatus == 'FILLED':
                signal.status = 'stopprof'
                signal.closed = float(proforder['stopPrice'])
                print('W W W W W W W W w W')
            # Order closed manually through binance
            elif profstatus == 'EXPIRED':
                signal.status = 'stoploss'
                signal.closed = float(signal.latest)
            changes = True

        else:
            # Check to see if any profit targets have been hit, and if they have update the stoploss to a new target
            skipfirst = False
            count = 0
            for s in stop_order_receipts:
                order = realclient.futures_get_order(orderId=s['orderId'], symbol=signal.pair)
                if skipfirst:
                    count += 1
                    if order['status'] == 'FILLED':
                        # Recording Order Details
                        signal.conditions.filled_orders.append(order)
                        # Removing Order from active orders
                        for o in signal.conditions.orders:
                            if o['orderId'] == order['orderId']:
                                signal.conditions.orders.remove(o)
                        print('Saved and removed an order')
                        stop_order_receipts[0] = update_stoploss(signal.conditions.losstargets[len(signal.conditions.filled_orders)-1], stop_order_receipts[0])
                        changes = True
                skipfirst = True

    # Checks if the stoploss target has been completed
    stoporder = realclient.futures_get_order(orderId=stop_order_receipts[0]['orderId'], symbol=signal.pair)
    stopstatus = stoporder['status']
    if not stopstatus == 'NEW':
        # Record Filled order
        signal.conditions.filled_orders.append(stoporder)
        # Remove order from active orders
        for o in signal.conditions.orders:
            if o['orderId'] == stoporder['orderId']:
                signal.conditions.orders.remove(o)
        # Remove the rest of active orders
        for o in signal.conditions.orders[:]:
            signal.conditions.orders.remove(o)

        if signal.status == 'active':
            signal.status = 'stoploss'
            signal.closed = float(stoporder['stopPrice'])
            print('Stopping ', signal.pair, ' at stopPrice:', signal.closed)
        changes = True
    return changes


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


def percentage_diff(past, future, lev, direction):
    if future == '0':
        return '0'
    percentage = str(abs((float(future) - float(past)) / float(future) * 100 * int(lev)))
    if percentage == '0':
        return percentage
    percentage = str(round(float(percentage), 2))
    if direction == 'LONG':
        if future > past:
            percentage = '\033[92m' + percentage + '%' + '\033[0m'
        else:
            percentage = '\033[91m' + '-' + percentage + '%' + '\033[0m'
    if direction == 'SHORT':
        if future > past:
            percentage = '\033[91m' + '-' + percentage + '%' + '\033[0m'
        else:
            percentage = '\033[92m' + percentage + '%' + '\033[0m'
    return percentage


# Print out a viewable snapshot of current futures account state
def futures_snapshot():
    # get futures info
    tangibles = realclient.futures_account_balance()
    retstring = ''

    for t in tangibles:
        if float(t["balance"]) > 0:
            print(str('\n' + t['asset']), "Balance: ", t['balance'])
            if 'withdrawAvailable' in t:
                perc_withdraw = float(t['withdrawAvailable']) / float(t['balance']) * 100
                print('   Avaliable: ', t["withdrawAvailable"], '\033[94m', round(perc_withdraw, 2), '%', '\033[0m')

    pos = '\n---------------------'

    # get futures positions
    positions = realclient.futures_position_information()
    for p in positions:
        direction = None
        if float(p['positionAmt']) > 0:
            direction = 'LONG'
        elif float(p['positionAmt']) < 0:
            direction = 'SHORT'
        if direction:
            # Calculate percentage profit or loss
            percentage = percentage_diff(p['entryPrice'], p['markPrice'], p['leverage'], direction)

            pos += "\nPair: " + p['symbol']

            if p['marginType'] == 'isolated':
                staked_and_pnl = float(p['isolatedWallet']) + float(p['unRealizedProfit'])
                pos += "\nStaked: " + p['isolatedWallet']
            elif p['marginType'] == 'cross':
                staked = abs(float(p['positionAmt'])) * float(p['entryPrice']) * 1 / int(p['leverage'])
                pos += "\nStaked: " + str(staked)
                staked_and_pnl = staked + float(p['unRealizedProfit'])
            else:
                raise ValueError('Unexpected margin Type')

            pos += "\nCurrent: " + str(staked_and_pnl)
            pos += "\n\nAmount: " + p['positionAmt']
            pos += "\nEntry: " + p['entryPrice']
            pos += "\nMark: " + p['markPrice']
            pos += "\nLeverage: " + p['leverage']

            pos += "\n\nPNL: " + p['unRealizedProfit']
            pos += "\nPNL Percent: " + str(percentage)

            open_orders = realclient.futures_get_open_orders()
            position_orders = []
            for o in open_orders:
                if o['symbol'] == p['symbol']:
                    position_orders.append(o)

            takeprofit = ''
            stoploss = ''
            for o in position_orders:
                if o['origType'] == 'STOP_MARKET':
                    stoploss = str(o['stopPrice']) + '  [' + percentage_diff(p['entryPrice'], o['stopPrice'], p['leverage'], direction)+']'
                elif o['origType'] == 'LIMIT':
                    takeprofit += '\n' + str(o['price']) + '  [' + percentage_diff(p['entryPrice'], o['price'], p['leverage'], direction)+']'

            pos += "\n\nTake Profits: " + str(takeprofit)
            pos += "\nStop Loss: " + str(stoploss) + '\n'

            pos += "\nLIQ: " + p['liquidationPrice']
            pos += "\nType: " + p['marginType']
            pos += "\n---------------------"
            retstring += pos
    return retstring


def close_all_futures():
    orders = realclient.futures_get_open_orders()
    print('Canceling Orders...')
    for o in orders:
        o_id = o['orderId']
        o_sym = o['symbol']
        try:
            realclient.futures_cancel_order(orderId=o_id, symbol=o_sym)
        except Exception as e:
            print(e)

    print('Reducing Positions...')
    positions = realclient.futures_position_information()
    for p in positions:
        if (float(p['positionAmt']) > 0) or (float(p['positionAmt']) < 0):
            amount = float(p['positionAmt'])
            if amount < 0:
                side = 'BUY'
            elif amount > 0:
                side = 'SELL'

            amount = float(str(p['positionAmt']).replace('-', ''))
            realclient.futures_create_order(symbol=p['symbol'], side=side, type='MARKET', quantity=amount, reduceOnly=True)
    print('Clean Futures Account')

