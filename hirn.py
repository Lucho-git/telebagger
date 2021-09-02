import fake_trade
from trade_classes import Trade, Futures


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
    pair = lines[0].split('#')[1]
    base = pair.split('/')[1]
    pair = pair.split('/')[0] + base
    lev = 10
    entry = float(lines[1].split(': ')[1])
    exit_price = lines[2].split(': ')[1]
    exit_price = float(exit_price.split(' ')[0])
    direction = ''
    if entry > exit_price:
        direction = 'short'
    else:
        direction = 'long'
    sl = entry - (entry/lev)

    print('pair|', pair, '|direction|', direction, '|entry|', entry, '|exit|', exit_price)
    print('lev', lev)

    signal = Trade(pair, base, 'Hirn', 'futures')

    signal.conditions = Futures(sl, exit_price, direction, lev, 'isolation')
    fake_trade.futures_trade(signal)
    return [signal]
