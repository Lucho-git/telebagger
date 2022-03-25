from binance import ThreadedWebsocketManager
from binance.streams import AsyncClient
from trade_classes import Trade, Futures
import asyncio
import time
import utility
import threading
import binance_wrap

from datetime import datetime, timezone
import pytz

twm = ThreadedWebsocketManager()
twm.start()

stoptrades = []
tradequeue = []
completedtrades = []
restart = []
streamdict = {}
reload = [False]
active = [False]
stop = [False]
restart = [True]

RESTART_TIMER = 60  # 60 second restart checks
RESTART_LIMIT = 60  # 60 * 60 second restart schedule (1 hour)
RESTART_COUNTER = [0]  # Current count

# Not Error is default, must be explicitly set as error by binance
stream = {'error': False}


def coin_trade_data(msg):
    if (msg['e'] != 'error') and (msg['k']['x']):
        k = msg['k']
        e = msg['e']
        i = k['i']
        stream['symbol'] = msg['s']
        stream['time'] = utility.binance_timestamp_local(int(msg['E']))
        stream['last'] = float(k['c'])
        stream['high'] = float(k['h'])
        stream['low'] = float(k['l'])
        stream['error'] = False
        # print(stream)
        # custom per trade object functionality
        key = stream['symbol'].lower() + '@' + e + '_' + i

        for u in streamdict[key]:
            # updates trade every minute
            u.update_trade(stream)
            u.update_snapshot(stream)
            if not u.status == 'active':
                print("Removing ", u, 'for reason', u.status)
                stoptrades.append(u)
        checkupdate()
    else:
        stream['error'] = True


def checkupdate():
    if stoptrades:
        stoptrade(stoptrades, streamdict, completedtrades)
        if completedtrades:
            savetraderesults(completedtrades)
        RESTART_COUNTER[0] = RESTART_LIMIT


async def stopstream():
    print("Returning to menu")
    stop[0] = True


async def close_stream():
    print('Saving stream and closing sockets')
    await save(streamdict)
    active[0] = False
    twm.stop()
    reload[0] = True


# Restarts the stream, and schedules a restart timer to ensure streams run smoothly
async def restart_stream():
    utility.gen_log(str(stream_status()))
    restart[0] = False
    await close_stream()
    await asyncio.gather(streamer(), timer())


# Restart functionality on a timer system, that will call itself again apon being restarted, Can be Switched off using restart[0] variable
async def timer():
    restart_counter = 0
    if not restart[0]:
        await asyncio.sleep(RESTART_TIMER)
        restart[0] = True
    while restart_counter < RESTART_LIMIT and restart[0]:
        await asyncio.sleep(RESTART_TIMER)
        restart_counter += 1
        print(str(restart_counter) + '->' + str(RESTART_LIMIT))
    if not restart[0]:
        print("Closing Restart Loop")
        return
    if streamdict:
        print("Scheduled Restart")
        await restart_stream()
    else:
        print("Empty Restart")
        utility.gen_log(str(stream_status()))
        await asyncio.gather(streamer(), timer())


async def save(in_streamdict):
    restartstream = in_streamdict
    for d in in_streamdict:
        print(in_streamdict[d])
        twm.stop_socket(in_streamdict[d][0].stream_id)

    utility.save_stream(restartstream)
    print('Saved...')
    print(restartstream)


def load():
    # Retrieve loadfile
    restartstream = utility.load_stream()
    # Restart the streams
    if restartstream:
        print("Reloaded Stream....")
        print(restartstream)
        for r in restartstream:
            sym = restartstream[r][0].pair
            twm.start_kline_socket(callback=coin_trade_data, symbol=sym, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
    else:
        restartstream = {}
    streamdict.update(restartstream)


async def addtrade(new_trades):  # import trade in future
    tradequeue.extend(new_trades)
    for t in new_trades:
        utility.gen_log(str(t.overview()))
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


def stream_status():
    status = ''
    first_run_check = True
    for s in streamdict:
        for u in streamdict[s]:
            if not first_run_check:
                status += '\n'
                print('Adding Line')
            status += u.overview()
            first_run_check = False
    if status == '':
        status = 'Trade Stream is Empty'
    return status


def savetraderesults(in_completedtrades):
    for c in in_completedtrades[:]:
        # Save trade to database
        utility.gen_log(str(c.overview()))
        utility.save_trade(c)
        if c.bag_id:
            utility.trade_results(c)
        # Remove trade fom list
        in_completedtrades.remove(c)
    print("Recorded Trade to Database")


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
        load()
        addstream(tradequeue, streamdict)

    if streamdict:
        print('Streaming....', streamdict, '\n')
        active[0] = True
        stop[0] = False

    while streamdict:
        await asyncio.sleep(1)

        '''
        streamstring = ''
        for i in streamdict:
            streamstring += str(i) + ' #'+str(len(streamdict[i])) + ' | '
        # print('Checking for updates....', streamstring, twm)
        print(streamstring)
        '''

        if reload[0] or stop[0]:
            break

    print('Returning To Event Menu....')
