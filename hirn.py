import fake_trade
import time
import utility
import binance_wrap
from trade_classes import Trade, Futures, STrade
hirn_timer = [0]
last_pair = ['']
tradeheat = [False]
first = [True]

HIRN_COOLDOWN_TIME = 60000  # In milliseconds
HIRN_LEVERAGE = 10  # Trade Leverage for Futures trades
HIRN_TRADE_PERCENT = 0.4  # How much remaining balance should be invested on each trade
HIRN_STOPLOSS_REDUCTION = 0.75   # Stoploss value to avoid getting liquidated


def am_first():
    first[0] = False


def cooldown():
    if not first[0]:
        time.sleep(5)
    am_first()

    raw_server_time = binance_wrap.timenow()
    if raw_server_time < hirn_timer[0]:
        tradeheat[0] = True
        raise ValueError('Hirn Signal while Cooling Down')
    else:
        tradeheat[0] = False
        hirn_timer[0] = raw_server_time + HIRN_COOLDOWN_TIME
        first[0] = True


def bag(msg):

    print('message recieved', tradeheat[0])
    if not tradeheat[0]:
        result = search_coin(msg)
        print("secucess trades !!!!!!!!!!!!")

        raw_server_time = binance_wrap.timenow()
        utility.failed_message(msg, 'HIRN_DOUBLE_TEST', str(raw_server_time) + str(tradeheat[0]), '_doubleups.txt')  # TODO remove later
        last_pair[0] = get_pair(msg)
        print("secucess trades ")
        print(last_pair[0])
        return result
    else:
        raw_server_time = binance_wrap.timenow()
        utility.failed_message(msg, 'HIRN_DOUBLE_TEST', str(raw_server_time) + str(tradeheat[0]), '_doubleups.txt')  # TODO remove later
        duplicate = get_pair(msg)
        print('compared')
        print(duplicate)
        print(last_pair[0])
        if not last_pair[0] == duplicate:
            result = search_coin(msg)
            return result
        else:
            print('Duplicate Message')
    return None


def valid_trade_message(msg):
    if 'Buy #' in msg:
        print("Valid Message")
        return True
    else:
        return False


def get_pair(text):
    lines = text.split('\n')
    print(lines[0])
    pair = lines[0].split('#')[1]
    base = pair.split('/')[1]
    pair = pair.split('/')[0] + base
    return pair


def search_coin(text):
    lines = text.split('\n')
    print(lines[0])
    pair = lines[0].split('#')[1]
    coin = pair.split('/')[0]
    base = pair.split('/')[1]
    pair = pair.split('/')[0] + base
    entry = float(lines[1].split(': ')[1])
    exit_price = lines[2].split(': ')[1]
    exit_price = float(exit_price.split(' ')[0])
    direction = ''
    lev = 1
    if entry > exit_price:
        direction = 'short'
    else:
        direction = 'long'
    is_futures = None
    if base == 'USDT':
        futureslist = utility.get_binance_futures_list()
        is_futures = False
        # TODO this method can identify coins within coins, e.g.  HINT contains INT,
        for f in futureslist:
            if f == coin:
                is_futures = True
                lev = HIRN_LEVERAGE

    sl = entry - (entry/lev)*HIRN_STOPLOSS_REDUCTION
    print('Pair|', pair, '|Direction|', direction, '|Entry|', entry, '|Exit|', exit_price, '|Leverage|', lev)
    if is_futures:
        signal = Trade(pair, base, 'Hirn', 'futures')
        signal.conditions = Futures(sl, exit_price, direction, lev, 'isolation')
        try:
            binance_wrap.futures_trade(signal, HIRN_TRADE_PERCENT, bag_id='hirn_real')
        except ValueError:
            print('Trading')
            fake_trade.futures_trade(signal, bag_id='port1', percent=HIRN_TRADE_PERCENT)
            print('Trading2')


    else:
        signal = Trade(pair, base, 'Hirn', 'spot')
        signal.conditions = STrade(sl, exit_price)
        fake_trade.spot_trade(signal, bag_id='port1', percent=HIRN_TRADE_PERCENT)

    relative_price = abs(float(signal.price) - entry)/entry
    if relative_price > 0.1:
        raise ValueError("MarketValue is more than 10% different than it's expected value")

    return [signal]
