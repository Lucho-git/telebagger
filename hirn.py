import time
import utility
import binance_wrap
import trade_classes
from trade_classes import Trade, Futures, STrade

hirn_timer = [0]
last_pair = ['']
tradeheat = [False]
first = [True]
HIRN_REAL = [False]

HIRN_COOLDOWN_TIME = 16000  # In milliseconds
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

    print('message recieved: Tradeheat?', tradeheat[0])
    if not tradeheat[0]:
        try:
            result = search_coin(msg)
            last_pair[0] = get_pair(msg)
            print("secucess trades ")
            print(last_pair[0])
            return result
        except ValueError as e:
            print('Exception in Hirn Signal')
            print(e)

    else:
        raw_server_time = binance_wrap.timenow()
        utility.failed_message(msg, 'Hirn', 'Exception TradeHeat')  # TODO remove later
        duplicate = get_pair(msg)
        if not last_pair[0] == duplicate:
            try:
                result = search_coin(msg)
                return result
            except ValueError as e:
                print('Exception in Hirn Signal')
                print(e)
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
    signals = []
    lines = text.split('\n')
    print(lines[0])
    pair = lines[0].split('#')[1]
    coin = pair.split('/')[0]
    base = pair.split('/')[1]
    pair = pair.split('/')[0] + base
    entry = float(lines[1].split(': ')[1])
    exit_price = lines[2].split(': ')[1]
    exit_price = float(exit_price.split(' ')[0])
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
                lev2 = HIRN_LEVERAGE*2

    sl = entry - (entry/lev)*HIRN_STOPLOSS_REDUCTION
    sl2 = entry - (entry/lev*2)*HIRN_STOPLOSS_REDUCTION

    print('Pair|', pair, '|Direction|', direction, '|Entry|', entry, '|Exit|', exit_price, '|Leverage|', lev)
    print(is_futures)
    print(HIRN_REAL[0])
    if is_futures and HIRN_REAL[0]:
        signal = Trade(pair, base, 'Hirn', 'futures', text)
        signal.conditions = Futures(sl, exit_price, direction, lev, 'isolation')
        try:
            binance_wrap.futures_trade_no_orders(signal, HIRN_TRADE_PERCENT)
            binance_wrap.futures_trade_add_orders(signal)
            # add orders
        except ValueError as e:
            print('Exception in Hirn Real Trade')
            print(e)
        finally:
            print('Starting Fake Trade')
            signal.fake_trade(percent=HIRN_TRADE_PERCENT)
            signals.append(signal)
            print('Completed Fake Trade')
    elif is_futures:
        print('Starting Fake Trade')
        signal = Trade(pair, base, 'Hirn', 'futures', in_message=text)
        signal.conditions = Futures(sl, exit_price, direction, lev, 'isolation')
        signal.fake_trade(percent=HIRN_TRADE_PERCENT)
        signals.append(signal)

        print('Starting Fake Trade2')
        signal2 = Trade(pair, base, 'Hirn2', 'futures', in_message=text)
        signal2.conditions = Futures(sl2, exit_price, direction, lev2, 'isolation')
        signal2.fake_trade(percent=HIRN_TRADE_PERCENT)
        signals.append(signal2)
    else:
        signal = Trade(pair, base, 'Hirn', 'spot', in_message=text)
        signal.conditions = STrade(sl, exit_price)
        signal.fake_trade(percent=HIRN_TRADE_PERCENT)
        signals.append(signal)

    relative_price = abs(float(signal.price) - entry)/entry
    if relative_price > 0.1:
        print('Value Error')
        raise ValueError("MarketValue is more than 10% different than it's expected value")

    return signals
