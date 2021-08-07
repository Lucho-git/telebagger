from binance import ThreadedWebsocketManager
from binance.streams import AsyncClient
import time
import pickle


class Trade:
    def __init__(self, pair, id):
        self.pair = pair.upper()
        self.id = id
        self.parameters = 'STUB'
        self.stream_id = None

    def __repr__(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) +'}'
        retstr = ''+self.pair+'_'+str(self.id)+''
        return retstr

    def snap(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) + ' | ' + str(self.stream_id) + '}'
        return retstr


tr1 = Trade('BTCUSDT', 22)
tr2 = Trade('ETHUSDT', 6)
tr3 = Trade('ETHUSDT', 15)
tr4 = Trade('DOGEUSDT', 31)
tr5 = Trade('NANOUSDT', 2)


# No Error is default, must be explicitly sent by binance
stream = {'error': False}


def coin_trade_data(msg):
    if (msg['e'] != 'error') and (msg['k']['x']):
        k = msg['k']
        stream['symbol'] = msg['s']
        stream['time'] = msg['E']
        stream['last'] = k['c']
        stream['high'] = k['h']
        stream['low'] = k['l']
        stream['error'] = False
        print(stream)
        # def updatetrade
    else:
        stream['error'] = True


def save(restartstream):
    with open('savefile', 'wb') as config_dictionary_file:
        pickle.dump(restartstream, config_dictionary_file)
    print('Saved...')


def load(twm):
    with open('savefile', 'rb') as config_dictionary_file:
        restartstream = pickle.load(config_dictionary_file)
        print('Loaded...')

    # Restart the streams
    if restartstream:
        for r in restartstream:
            sym = restartstream[r][0].pair
            twm.start_kline_socket(callback=coin_trade_data, symbol=sym, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
    return restartstream


def addstream(tradequeue, activestreams, streamdict, twm):
    for t in tradequeue[:]:
        print('Adding:', t)
        # Checks to see if pair is already being streamed, if so adds trade to that stream
        duplicate = False
        for a in streamdict:
            if streamdict[a][0].pair == t.pair:
                print('Duplicate Stream', t.pair)
                streamdict[a].append(t)
                t.stream_id = streamdict[a][0].stream_id
                duplicate = True

        # If pair is not being streamed, begin streaming pair
        if not duplicate:
            streamID = twm.start_kline_socket(callback=coin_trade_data, symbol=t.pair,
                                              interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
            print(streamID)
            t.stream_id = streamID
            streamdict[t.stream_id] = [t]
        tradequeue.remove(t)


def streamer():
    twm = ThreadedWebsocketManager()
    twm.start()

    tradequeue = [tr1, tr2, tr3, tr4, tr5]
    tradequeue = []
    activestreams = []
    streamdict = {}
    stoptrades = [tr1, tr2, tr3, tr4, tr5]
    stoptrades = []
    completedtrades = []

    # Reload Streams
    streamdict = load(twm)
    restartstream = streamdict
    print('RestartStreams_|', restartstream)
    print('\n')

    # print('ActiveStreams_|', activestreams)
    print('Tradequeue_|', tradequeue)
    addstream(tradequeue, activestreams, streamdict, twm)
    print(streamdict)

    print('Streaming....\n')
    # stoptrades.append(('DOGEUSDT',1))

    for s in stoptrades[:]:
        if len(streamdict[s.stream_id]) > 1:
            print('Matched Duplicate')
            for t in streamdict[s.stream_id][:]:
                if t.id == s.id:
                    print('Removed duplicate instance of:', s.stream_id, "ID:", s.id)
                    streamdict[s.stream_id].remove(t)
            completedtrades.append(s)
            stoptrades.remove(s)
        else:
            print('Matched Stream')
            twm.stop_socket(s.stream_id)
            streamdict.pop(s.stream_id)
            completedtrades.append(s)
            print('removing:', s)
            stoptrades.remove(s)

    reload = True
    if reload:
        restartstream = streamdict
        for d in streamdict:
            time.sleep(1)
            print(streamdict[d])
            twm.stop_socket(streamdict[d][0].stream_id)
    save(restartstream)

    print('\n\n')
    print('Tradequeue_|', tradequeue)
    print('CompletedTrades_|', completedtrades)
    print('StopTrades_|', stoptrades)
    print(streamdict)
    if reload:
        print('RestartStream_|', restartstream)


