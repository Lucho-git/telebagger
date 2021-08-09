from binance import ThreadedWebsocketManager
from binance.streams import AsyncClient
import time
import pickle
import random

stoptrades = []
tradequeue = []
streamdict = {}


class Trade:
    def __init__(self, pair, id):
        self.pair = pair.upper()
        self.id = id
        self.parameters = 'STUB'
        self.stream_id = None
        self.active = True

    def __repr__(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) +'}'
        retstr = ''+self.pair+'_'+str(self.id)+''
        return retstr

    def snapshot(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) + ' | ' + str(self.stream_id) + '}\n'
        retstr += 'Trade ended in Profit/Loss, Entry price here, Exit price here, TradePercentage = +/- x%'
        return retstr

    def stopchance(self):
        num = random.randrange(1, 3, 1)
        if num == 1:
            self.active = False


tr1 = Trade('BTCUSDT', 22)
tr1.stream_id = 'btcusdt@kline_1m'
tr2 = Trade('ETHUSDT', 6)
tr2.stream_id = 'ethusdt@kline_1m'
tr3 = Trade('ETHUSDT', 15)
tr3.stream_id = 'ethusdt@kline_1m'
tr4 = Trade('DOGEUSDT', 31)
tr4.stream_id = 'dogeusdt@kline_1m'
tr5 = Trade('NANOUSDT', 2)
tr5.stream_id = 'nanousdt@kline_1m'


# No Error is default, must be explicitly sent by binance
stream = {'error': False}


def coin_trade_data(msg):
    if (msg['e'] != 'error') and (msg['k']['x']):
        k = msg['k']
        e = msg['e']
        i = k['i']
        stream['symbol'] = msg['s']
        stream['time'] = msg['E']
        stream['last'] = k['c']
        stream['high'] = k['h']
        stream['low'] = k['l']
        stream['error'] = False

        print(stream)
        # custom per trade object functionality
        key = stream['symbol'].lower() + '@' + e + '_' + i
        for u in streamdict[key]:
            u.stopchance()
            if not u.active:
                stoptrades.append(u)
                print('REMOVED', u)
    else:
        stream['error'] = True


def save(in_streamdict, twm):
    restartstream = in_streamdict
    for d in in_streamdict:
        time.sleep(1)
        print(in_streamdict[d])
        twm.stop_socket(in_streamdict[d][0].stream_id)

    with open('savefile', 'wb') as config_dictionary_file:
        pickle.dump(restartstream, config_dictionary_file)
    print('Saved...')


def load(in_streamdict, twm):
    # Retrieve loadfile
    with open('savefile', 'rb') as config_dictionary_file:
        restartstream = pickle.load(config_dictionary_file)
        print('Loaded...')

    # Restart the streams
    if restartstream:
        for r in restartstream:
            sym = restartstream[r][0].pair
            twm.start_kline_socket(callback=coin_trade_data, symbol=sym, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
    else:
        restartstream = {}
    in_streamdict = restartstream


def addtrade(trade):
    tradequeue.append(trade)


def addstream(in_tradequeue, in_streamdict, twm):
    for t in in_tradequeue[:]:
        # Checks to see if pair is already being streamed, if so adds trade to that stream
        duplicate = False
        for a in in_streamdict:
            if in_streamdict[a][0].pair == t.pair:
                in_streamdict[a].append(t)
                t.stream_id = in_streamdict[a][0].stream_id
                duplicate = True

        # If pair is not being streamed, begin streaming pair
        if not duplicate:
            streamID = twm.start_kline_socket(callback=coin_trade_data, symbol=t.pair,
                                              interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
            print(streamID)
            t.stream_id = streamID
            in_streamdict[t.stream_id] = [t]
        in_tradequeue.remove(t)


def stoptrade(in_stoptrades, in_streamdict, completedtrades, twm):
    for s in in_stoptrades[:]:
        if len(in_streamdict[s.stream_id]) > 1:
            print('Matched Duplicate')
            for t in in_streamdict[s.stream_id][:]:
                if t.id == s.id:
                    print('Removed duplicate instance of:', s.stream_id, "ID:", s.id)
                    in_streamdict[s.stream_id].remove(t)
            completedtrades.append(s)
            in_stoptrades.remove(s)
        else:
            twm.stop_socket(s.stream_id)
            in_streamdict.pop(s.stream_id)
            completedtrades.append(s)
            print('removing:', s)
            in_stoptrades.remove(s)


def savetraderesults(completedtrades):
    for c in completedtrades[:]:
        with open('telebagger/Saves/TradeResults.txt', 'a') as f:
            f.write(str(c.snapshot()))
            f.write('\n\n')
        completedtrades.remove(c)
    print("Saved Results....")


def streamer():
    # Start websocket
    twm = ThreadedWebsocketManager()
    twm.start()

    # Stub Queue values
    tradequeue.extend([tr1, tr2, tr3, tr4, tr5])
    # tradequeue = []
    # stoptrades = [tr1, tr2, tr3, tr4, tr5]
    completedtrades = []

    # Reload Streams
    load(streamdict, twm)

    addstream(tradequeue, streamdict, twm)

    print(streamdict)
    print('Streaming....', streamdict, '\n')

    while streamdict:
        if stoptrades:
            stoptrade(stoptrades, streamdict, completedtrades, twm)

        #  print('Completedtrades:', completedtrades)
        if completedtrades:
            savetraderesults(completedtrades)
        time.sleep(1)

    time.sleep(10)
    reload = True
    if reload:
        save(streamdict, twm)


