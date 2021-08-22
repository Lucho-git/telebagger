from binance import ThreadedWebsocketManager
from binance.streams import AsyncClient
from trade_classes import Trade, Futures
# from stream_trade import Trade
import asyncio
import time
import pickle

twm = ThreadedWebsocketManager()
twm.start()

stoptrades = []
tradequeue = []
completedtrades = []
restart = []
streamdict = {}
reload = [False]
update = [False]
active = [False]
stop = [False]
onceoff = [False]


# No Error is default, must be explicitly sent by binance
stream = {'error': False}


def coin_trade_data(msg):
    if (msg['e'] != 'error') and (msg['k']['x']):
        k = msg['k']
        e = msg['e']
        i = k['i']
        stream['symbol'] = msg['s']
        stream['time'] = msg['E']
        stream['last'] = float(k['c'])
        stream['high'] = float(k['h'])
        stream['low'] = float(k['l'])
        stream['error'] = False
        # print(stream)
        # custom per trade object functionality
        key = stream['symbol'].lower() + '@' + e + '_' + i

        for u in streamdict[key]:
            u.update_trade(stream)
            u.update_snapshot(stream)
            if not u.status == 'active':
                print("Removing ", u, 'for reason', u.status)
                stoptrades.append(u)
        checkupdate()
    else:
        stream['error'] = True
    if onceoff[0]:
        onceoff[0] = False
        k = msg['k']
        e = msg['e']
        i = k['i']
        stream['symbol'] = msg['s']
        stream['time'] = msg['E']
        stream['last'] = float(k['c'])
        stream['high'] = float(k['h'])
        stream['low'] = float(k['l'])
        stream['error'] = False
        key = stream['symbol'].lower() + '@' + e + '_' + i
        for u in streamdict[key]:
            u.update_trade(stream)
            u.update_snapshot(stream)
            if not u.status == 'active':
                print("Removing ", u, 'for reason', u.status)
                stoptrades.append(u)
        checkupdate()


async def onceoff_f():
    onceoff[0] = True


def checkupdate():
    if stoptrades:
        stoptrade(stoptrades, streamdict, completedtrades)
    if completedtrades:
        savetraderesults(completedtrades)


async def stopstream():
    print("Returning to menu")
    stop[0] = True


async def restart():
    print('Saving stream and closing sockets')
    await save(streamdict)
    active[0] = False
    twm.stop()
    reload[0] = True


async def save(in_streamdict):
    restartstream = in_streamdict
    for d in in_streamdict:
        print(in_streamdict[d])
        twm.stop_socket(in_streamdict[d][0].stream_id)

    with open('savefile', 'wb') as config_dictionary_file:
        pickle.dump(restartstream, config_dictionary_file)
    print('Saved...')
    print(restartstream)


def load():
    # Retrieve loadfile
    restartstream = None
    try:
        with open('savefile', 'rb') as config_dictionary_file:
            restartstream = pickle.load(config_dictionary_file)
            print('Loaded...')
            print(restartstream)
    except:
        print('No Save File')

    # Restart the streams
    if restartstream:
        print("Reloaded....")
        for r in restartstream:
            sym = restartstream[r][0].pair
            twm.start_kline_socket(callback=coin_trade_data, symbol=sym, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
    else:
        restartstream = {}
    streamdict.update(restartstream)


async def addtrade(new_trades):  # import trade in future
    tradequeue.extend(new_trades)
    print("Adding trades", new_trades)
    addstream(tradequeue, streamdict)
    print('bumping')
    await bump()


def addstream(in_tradequeue, in_streamdict):
    for t in in_tradequeue[:]:
        # Checks to see if pair is already being streamed, if so adds trade to that stream
        duplicate = False
        exactcopy = False
        for a in in_streamdict:
            if in_streamdict[a][0].pair == t.pair:
                if len(in_streamdict[a]) > 0:
                    for o in in_streamdict[a]:
                        if o.id == t.id:
                            exactcopy = True
                            print("Exact Copy!")
                if not exactcopy:
                    in_streamdict[a].append(t)
                    t.stream_id = in_streamdict[a][0].stream_id
                duplicate = True
        # If pair is not being streamed, begin streaming pair
        if not duplicate:
            streamID = twm.start_kline_socket(callback=coin_trade_data, symbol=t.pair, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
            print(streamID)
            t.stream_id = streamID
            in_streamdict[t.stream_id] = [t]
        in_tradequeue.remove(t)


def stoptrade(in_stoptrades, in_streamdict, in_completedtrades):
    print('Stopping trades....', in_stoptrades)
    for s in in_stoptrades[:]:
        if len(in_streamdict[s.stream_id]) > 1:
            for t in in_streamdict[s.stream_id][:]:
                if t.id == s.id:
                    print('Removed duplicate instance of:', s.stream_id, "ID:", s.id)
                    in_streamdict[s.stream_id].remove(t)
            in_completedtrades.append(s)
            in_stoptrades.remove(s)
        else:
            twm.stop_socket(s.stream_id)
            in_streamdict.pop(s.stream_id)
            in_completedtrades.append(s)
            print('removing:', s)
            in_stoptrades.remove(s)


def savetraderesults(in_completedtrades):
    for c in in_completedtrades[:]:
        with open('telebagger/Saves/TradeResults.txt', 'a') as f:
            f.write(str(c.savestring))
            f.write('\n\n')
        openstr = 'telebagger/Saves/' + c.origin + '.txt'
        with open(openstr, 'a') as f:
            f.write(str(c.savestring))
            f.write('\n\n')
        in_completedtrades.remove(c)
    print("Recorded a Trade")


async def streamcommand():
    update[0] = True


async def bump():
    if not active[0]:
        await streamer()


async def streamer():
    # Start websocket
    if not active[0]:
        if reload[0]:
            global twm
            twm = ThreadedWebsocketManager()
            twm.start()
            reload[0] = False
        else:
            pass

        # Stub Queue values
        #tradequeue.extend([tr1, tr2, tr3, tr4, tr5])
        #stoptrades.extend([tr1, tr2, tr3, tr4, tr5])

        load()
        addstream(tradequeue, streamdict)

    if streamdict:
        print('Streaming....', streamdict, '\n')
        active[0] = True
        stop[0] = False

    while streamdict:
        '''
        if stoptrades:
            stoptrade(stoptrades, streamdict, completedtrades)

        if completedtrades:
            savetraderesults(completedtrades)
        '''
        if tradequeue:
            addstream(tradequeue, streamdict)

        await asyncio.sleep(1)
        time.sleep(1)

        streamstring = ''
        for i in streamdict:
            streamstring += str(i) + ' #'+str(len(streamdict[i])) + ' | '
        print('Checking for updates....', streamstring, twm)
        if update[0]:
            print('Update Recieved')
            update[0] = False

        if reload[0]:
            break

        if stop[0]:
            break

    print('Returning To Event Menu....')