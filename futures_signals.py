# Signal group, discontinued, legacy code

import fake_trade  # removed
import re
from trade_classes import Trade, MFutures


def bag(msg):
    result = search_coin(msg)
    return result


def valid_trade_message(msg):
    if 'Signal From VIP Channel' in msg:
        print("Valid Message")
        return True
    else:
        return False


def search_coin(text):
    text = text.replace('  ', ' ')
    text = text.replace('   ', ' ')
    text = text.replace('\n\n\n', '\n\n')
    text = text.replace('\n\n', '\n')
    text = text.replace('\n\n ', '\n')
    lines = text.split('\n')
    print('freshs start\n')
    direction = ''
    pair = ''
    if 'Buy' in lines[1]:
        direction = 'long'
        pair = lines[1].split('Buy')[1]
    elif 'Sell' in lines[1]:
        direction = 'short'
        pair = lines[1].split('Sell')[1]
    else:
        raise ValueError('Expected this line to contain Buy or Sell', print(lines[1]))

    pair = pair.split('USDT')[0]
    pair = re.sub('[^a-zA-Z]+', '', pair)
    base = 'USDT'
    pair = pair+base

    entry = lines[2].split('Price:')[1]
    entry = re.sub('[^0-9.]+', '', entry)

    t1 = lines[4].split('1', 1)[1]
    t1 = float(re.sub('[^0-9.]+', '', t1))

    t2 = lines[5].split('2', 1)[1]
    t2 = float(re.sub('[^0-9.]+', '', t2))

    t3 = lines[6].split('3', 1)[1]
    t3 = float(re.sub('[^0-9.]+', '', t3))

    t4 = lines[7].split('4', 1)[1]
    t4 = float(re.sub('[^0-9.]+', '', t4))

    t5 = lines[8].split('5', 1)[1]
    t5 = float(re.sub('[^0-9.]+', '', t5))

    lev = int(re.sub('[^0-9]+', '', lines[9]))
    sl = float(re.sub('[^0-9.]+', '', lines[10]))

    print('Pair|', pair, '|Direction|', direction, '|Entry|', entry, '|Leverage|', lev)

    signal = Trade(pair, base, 'Futures Signals', 'mfutures')
    stopprof = [20, 20, 20, 20, 20]
    proftargets = [t1, t2, t3, t4, t5]
    losstargets = [sl, sl, sl, entry, entry]
    signal.conditions = MFutures(losstargets, stopprof, proftargets, direction, lev, 'isolation')
    fake_trade.mfutures_trade(signal)

    return [signal]
