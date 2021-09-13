import fake_trade
import utility
from trade_classes import Trade, Futures, STrade


def bag(msg):
    result = search_coin(msg)
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
    base = pair.split('/')[1]
    pair = pair.split('/')[0] + base
    lev = 1
    entry = float(lines[1].split(': ')[1])
    exit_price = lines[2].split(': ')[1]
    exit_price = float(exit_price.split(' ')[0])
    direction = ''
    if entry > exit_price:
        direction = 'short'
    else:
        direction = 'long'
    sl = entry - (entry/lev)

    if base == 'USDT':
        futureslist = utility.get_binance_futures_list()
        is_futures = False
        for f in futureslist:
            if f in pair:
                is_futures = True
                lev = 10

    print('Pair|', pair, '|Direction|', direction, '|Entry|', entry, '|Exit|', exit_price, '|Leverage|', lev)

    if is_futures:
        signal = Trade(pair, base, 'Hirn', 'futures')
        signal.conditions = Futures(sl, exit_price, direction, lev, 'isolation')
        fake_trade.futures_trade(signal)
    else:
        sl = entry - (entry/10)
        signal = Trade(pair, base, 'Hirn', 'spot')
        signal.conditions = STrade(sl, exit_price)
        fake_trade.spot_trade(signal)

    relative_price = abs(signal.price - entry)/entry
    if relative_price > 0.1:
        raise ValueError("MarketValue is more than 10% different than it's expected value")

    return [signal]
