import fake_trade
import utility
import binance_wrap
from trade_classes import Trade, Futures, STrade
hirn_timer = [0]
tradeheat = [False]

HIRN_LEVERAGE = 15
HIRN_TRADE_PERCENT = 0.4
HIRN_STOPLOSS_REDUCTION = 0.8

def bag(msg):
    raw_server_time = binance_wrap.timenow()

    if raw_server_time < hirn_timer[0]:
        tradeheat[0] = True
        print("Cooling Down")
    else:
        tradeheat[0] = False
    result = search_coin(msg)
    tradetime = result[0].time
    hirn_timer[0] = tradetime + 60000
    return result


def valid_trade_message(msg):
    if 'Buy #' in msg:
        print("Valid Message")
        return True
    else:
        return False


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
            binance_wrap.futures_trade(signal, 1)
        except ValueError:
            fake_trade.futures_trade(signal)
    else:
        signal = Trade(pair, base, 'Hirn', 'spot')
        signal.conditions = STrade(sl, exit_price)
        fake_trade.spot_trade(signal)

    relative_price = abs(float(signal.price) - entry)/entry
    if relative_price > 0.1:
        raise ValueError("MarketValue is more than 10% different than it's expected value")

    return [signal]
