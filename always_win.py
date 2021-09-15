import time
import fake_trade
from trade_classes import Trade, MFutures


def bag(msg):
    result = search_coin(msg)
    return result


def valid_trade_message(msg):
    caps = msg.upper()
    # if ('/USDT' in msg) or ('SHORT' in caps) or ('LONG' in caps):
    if '/USDT' in msg:
        print("Valid Message")
        return True
    else:
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

    signal = Trade(pair, base, 'Always Win', 'mfutures')
    signal2 = Trade(pair, base, 'Always Win2', 'mfutures')
    stoploss = [100, 100, 100, 100, 100]
    stopprof = [10, 22.5, 33.75, 25.3, 8.45]
    stopprof2 = [40, 25, 15, 10, 10]
    proftargets = [t1, t2, t3, t4, t5]
    losstargets = [sl, entry, t1, t2, t3]
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