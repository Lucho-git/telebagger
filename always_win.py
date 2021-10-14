import time
import fake_trade
import binance_wrap
from trade_classes import Trade, MFutures

AW_TRADE_PERCENTAGE = 0.4
AW_WAIT_SIGNAL = [None]


def bag(msg):
    if valid_trade_message(msg):
        print('Valid Message')
        info = search_coin(msg)
        print(AW_WAIT_SIGNAL[0])
        if AW_WAIT_SIGNAL[0]:
            if info[0] == AW_WAIT_SIGNAL[0].pair:
                result = add_orders(info, AW_WAIT_SIGNAL[0])
                print("Add sell orders to trade")
                AW_WAIT_SIGNAL[0] = None
            else:
                print("PROBLEMS???")
        else:
            result = signal_trade(info)
    else:
        valid_trade_message_2(msg)
        result = None
    return result


def valid_trade_message(msg):
    caps = msg.upper()
    # if ('/USDT' in msg) or ('SHORT' in caps) or ('LONG' in caps):
    if '/USDT' in msg:
        print("Signal Message")
        return True
    else:
        return False


def valid_trade_message_2(msg):
    msg = msg.upper()
    if 'SHORT' in msg or 'LONG' in msg:
        lines = msg.split('\n')
        l1 = lines[0].split(' ')
        if 'SHORT' in l1[0] or 'LONG' in l1[0]:
            pair = l1[1].upper() + 'USDT'
            base = 'USDT'
            signal = Trade(pair, base, 'Always Win', 'futures')
            fake_trade.fake_trade(signal, percent=AW_TRADE_PERCENTAGE, bag_id='AW1')
            AW_WAIT_SIGNAL[0] = signal
            # AW_WAIT_SIGNAL[0] = binance_wrap.futures_trade_no_orders(signal, AW_TRADE_PERCENTAGE, 'AW1')
            print('Signal Incoming:', pair)
            return True
    return False


def search_coin(text):
    print(text)
    text = text.replace('  ', ' ')
    text = text.replace('   ', ' ')
    lines = text.split('\n')

    pair = ''
    base = 'USDT'

    if 'SHORT' in lines[0]:
        pair = lines[0].split('SHORT')[0]
        direction = 'short'
    elif 'LONG' in lines[0]:
        pair = lines[0].split('LONG')[0]
        direction = 'long'
    else:
        raise ValueError("Short or Long not found")
    pair = pair.replace(' ', '')
    pair = pair.replace('/', '')
    print(pair)

    lev = lines[1].split(' ')[1]
    lev = float(lev.split('x')[0])
    entry = float(lines[2].split(' ')[1])
    t1 = float(lines[3].split(' ')[2])
    t2 = float(lines[4].split(' ')[2])
    t3 = float(lines[5].split(' ')[2])
    t4 = float(lines[6].split(' ')[2])
    t5 = float(lines[7].split(' ')[2])
    sl = float(lines[9].split(' ')[1])
    print('Pair|', pair, '|Direction|', direction, '|Entry|', entry, '|Stoploss|', sl, '|Leverage|', lev)
    return [pair, base, direction,lev, entry, t1, t2, t3, t4, t5, sl]


# TODO Later need to allow for multiple signals, so can track different sell percentages
def add_orders(info, signal):
    direction = info[2]
    lev = info[3]
    entry = info[4]
    sl = info[10]
    t1 = info[5]
    t2 = info[6]
    t3 = info[7]
    t4 = info[8]
    t5 = info[9]

    stopprof = [40, 25, 15, 10, 10]
    proftargets = [t1, t2, t3, t4, t5]
    losstargets = [sl, entry, t1, t2, t3]

    fake_trade.fake_trade(signal, percent=AW_TRADE_PERCENTAGE, bag_id='AW1')

    copy_signal = Trade(signal.pair, signal.base, 'Always Win2', 'mfutures')
    copy_signal = fake_trade.fake_trade_copy(copy_signal, signal, percent=AW_TRADE_PERCENTAGE, bag_id='AW2')

    signal.conditions = MFutures(losstargets, stopprof, proftargets, direction, lev, 'isolation')
    copy_signal.conditions = MFutures(losstargets, stopprof, proftargets, direction, lev, 'isolation')
    signal.type = 'mfutures'
    return [signal, copy_signal]


def signal_trade(info):
    pair = info[0]
    base = info[1]
    direction = info[2]
    lev = info[3]
    entry = info[4]
    sl = info[10]

    t1 = info[5]
    t2 = info[6]
    t3 = info[7]
    t4 = info[8]
    t5 = info[9]

    signal = Trade(pair, base, 'Always Win', 'mfutures')
    signal2 = Trade(pair, base, 'Always Win2', 'mfutures')
    stopprof = [10, 22.5, 33.75, 25.3, 8.45]
    stopprof2 = [40, 25, 15, 10, 10]
    proftargets = [t1, t2, t3, t4, t5]
    losstargets = [sl, entry, t1, t2, t3]
    signal.conditions = MFutures(losstargets, stopprof, proftargets, direction, lev, 'isolation')
    signal2.conditions = MFutures(losstargets, stopprof2, proftargets, direction, lev, 'isolation')
    fake_trade.fake_trade(signal, bag_id='AW1', percent=AW_TRADE_PERCENTAGE)
    fake_trade.fake_trade(signal2, bag_id='AW2', percent=AW_TRADE_PERCENTAGE)

    return [signal, signal2]


'''
def print_past_messages(client):
  msgs = client.get_messages('CryptoVIPsignalTA', limit=2000)
'''