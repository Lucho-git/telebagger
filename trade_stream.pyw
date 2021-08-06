from binance import ThreadedWebsocketManager
from binance.streams import AsyncClient
import time


class Trade:
    def __init__(self, pair, id):
        self.pair = pair.upper()
        self.id = id
        self.paremeters = 'STUB'


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
        #
    else:
        stream['error'] = True


def streamer():
    twm = ThreadedWebsocketManager()
    twm.start()

    tradequeue = ['BTCUSDT', 'ETHUSDT', 'NANOUSDT', 'DOGEUSDT', 'BTCUSDT']
    activestreams = []
    stoptrades = []
    completedtrades = []
    restartstream = []

    for t in tradequeue[:]:
        tr = Trade(t, 1)
        print('Adding:', t)
        # Checks to see if pair is already being streamed, if so adds trade to that stream
        duplicate = False
        for a in activestreams:
            if a[1]:
                if a[1][0].pair == t:
                    tr.id += 1
                    a[1].append(tr)
                    duplicate = True

        # If pair is not being streamed, begin streaming pair
        if not duplicate:
            streamID = twm.start_kline_socket(callback=coin_trade_data, symbol=t,
                                              interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
            print(streamID)
            activestreams.append((streamID, [tr]))
        tradequeue.remove(t)
        print(activestreams)
        print(tradequeue)

    print(activestreams)
    print('Streaming....\n')
    # stoptrades.append(('DOGEUSDT',1))

    while activestreams:
        while stoptrades:
            for a in activestreams[:]:
                if a[1]:
                    streamname = a[1][0].pair
                for s in stoptrades[:]:
                    # remove duplicate trade
                    if (streamname == s[0]) and (len(a[1]) > 1):
                        # Later replace name stub, with specific Trade object identifier, probably use the trade time as Unique Key
                        print("Matched Duplicate:", streamname, 'And:', s)
                        for id in a[1][:]:
                            if id.id == s[1]:
                                print('Removed duplicate instance of:', streamname, "ID:", id.id)
                                a[1].remove(id)
                        print(a, 'After Removeal')
                        stoptrades.remove(s)
                        completedtrades.append(streamname)
                    # remove trade and stopstream
                    elif (streamname == s[0]):
                        print("Matched:", streamname, 'And:', s)
                        twm.stop_socket(a[0])
                        removed = a
                        activestreams.remove(a)
                        stoptrades.remove(s)
                        completedtrades.append(removed)
                        print('1 Removed Stream:', removed)
        #  stoptrades.extend([ ('BTCUSDT',1) ,('ETHUSDT',1) ,('NANOUSDT',1) ,('BTCUSDT',2)])

        reload = True
        if reload:
            for a in activestreams[:]:
                time.sleep(20)
                restartstream.append(a)
                twm.stop_socket(a[0])
                activestreams.remove(a)

    print('\n\n')
    print('Tradequeue_|', tradequeue)
    print('CompletedTrades_|', completedtrades)
    print('ActiveStreams_|', activestreams)
    print('StopTrades_|', stoptrades)
    print('RestartStream_|', restartstream)