import time
import copy
import fake_trade
from trade_classes import Trade, Futures, STrade, MFutures

tradeheat = [False]
vip_signals_timer = [0]
real = [False]

WAIT_TIME1 = 60 * 1000
WAIT_TIMES = [WAIT_TIME1]


def bag(msg, binance_wrap):
    search_text = msg
    result = None
    result = always_win_message(search_text)
    print('Always Win Message analsis')
    return result


def always_win_message(aw_message):
    validity = valid_trade_message(aw_message)
    trade_type = None
    if validity:
        trade_type = search_coin(aw_message)
    return trade_type


def valid_trade_message(msg):
    caps = msg.upper()
    # if ('/USDT' in msg) or ('SHORT' in caps) or ('LONG' in caps):
    if '/USDT' in msg:
        print("Valid Message")
        return True
    else:
        return False


def search_coin(text):
    # print(text)
    lines = text.split('\n')
    pair = lines[0].split(' ')[0]
    base = pair.split('/')[1]
    pair = pair.split('/')[0] + base

    direction = lines[0].split(' ')[1].lower()
    lev = lines[1].split(' ')[1]
    lev = float(lev.split('x')[0])
    entry = float(lines[2].split(' ')[1])
    t1 = float(lines[3].split(' ')[2])
    t2 = float(lines[4].split(' ')[2])
    t3 = float(lines[5].split(' ')[2])
    t4 = float(lines[6].split(' ')[2])
    t5 = float(lines[7].split(' ')[2])
    sl = float(lines[9].split(' ')[1])
    print('pair', pair, 'direction', direction, 'entry', entry)
    print('lev', lev)
    print('Targets', t1,t2,t3,t4,t5)
    print('SL',sl)
    signal = Trade(pair, base, 'Always Win', 'mfutures')
    signal2 = Trade(pair, base, 'Always Win2', 'mfutures')
    stoploss = [100, 100, 100, 100, 100]
    stopprof = [10, 22.5, 33.75, 25.3, 8.45]
    stopprof2 = [40, 25, 15, 10, 10]
    proftargets = [t1,t2,t3,t4,t5]
    losstargets = [sl,entry,t1,t2,t3]
    signal.conditions = MFutures(stoploss, losstargets, stopprof, proftargets, direction, lev, 'isolation')
    signal2.conditions = MFutures(stoploss, losstargets, stopprof2, proftargets, direction, lev, 'isolation')
    fake_trade.mfutures_trade(signal)
    time.sleep(1)
    fake_trade.mfutures_trade(signal2)

    return [signal, signal2]


'''
def print_past_messages(client):
  msgs = client.get_messages('CryptoVIPsignalTA', limit=2000)
'''