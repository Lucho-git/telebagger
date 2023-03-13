'''Holds all trades, and streams binance websocket data to update trades with'''
import asyncio

from binance import ThreadedWebsocketManager
from binance.streams import AsyncClient

import config
import utility
import database_logging as db


RESTART_TIMER = 60  # 60 second restart checks
RESTART_LIMIT = 60  # 60 * 60 second restart schedule (1 hour)

class TradeStream:
    '''Holds active trades, supplies current price information every minute, closes trades'''
    def __init__(self):
        self.twm = ThreadedWebsocketManager()
        self.twm.start()
        self.stream_view = True
        self.reload = False
        self.active = True
        self.restart = True
        self.streaming_trades = {}
        self.stop_trade_queue = []
        self.start_trade_queue = []
        self.finished_trades = []


    def coin_trade_data(self, msg):
        '''Receives live price information from binance every minute'''
        stream = {'error': False}

        if (msg['e'] != 'error') and (msg['k']['x']):
            k = msg['k']
            e = msg['e']
            i = k['i']
            stream['symbol'] = msg['s']
            stream['time'] = utility.convert_timestamp_utc8(int(msg['E']))
            stream['last'] = float(k['c'])
            stream['high'] = float(k['h'])
            stream['low'] = float(k['l'])
            stream['error'] = False

            key = stream['symbol'].lower() + '@' + e + '_' + i

            #Add a trycatch here, in case trades are removed, while trying to update them - race condition
            for trade in self.streaming_trades[key]:
                # updates trade every minute
                trade.update_trade(stream)
                #u.update_snapshot(stream)
                if self.stream_view:
                    print(trade.update_snapshot())
                if not trade.status == 'active':
                    self.stop_trade_queue.append(trade)
            self.checkupdate()
        else:
            stream['error'] = True

    def checkupdate(self):
        '''Checks to see if any tradequeues need updating'''
        if self.stop_trade_queue:
            closed_trades = self.stoptrade()
            if closed_trades:
                pass
                #self.savetraderesults(closed_trades)
            #RESTART_COUNTER[0] = RESTART_LIMIT
            self.save()

    def update_live_view(self):
        '''Saves state of active trades in live_view/active'''
        for t in self.get_trade_list():
            db.update_live_view(t)

    async def smooth_dump_stream(self):
        '''Sets all active trades to dumped, and stops the stream without saving'''
        print('Dumping...')
        for stream_socket, t in self.streaming_trades.items():
            for trade in t:
                trade.status = 'dumped'


    async def dump_stream(self):
        '''Sets all active trades to dumped, and stops the stream without saving'''
        print('Dumping...')
        for stream_socket, t in self.streaming_trades.items():
            for trade in t:
                trade.status = 'dumped'
                self.stop_trade_queue.append(trade)
            self.twm.stop_socket(stream_socket)
        self.checkupdate()


    async def close_stream(self):
        '''Saves the stream and closes streamsockets'''
        self.save()
        for stream_socket in self.streaming_trades:
            self.twm.stop_socket(stream_socket)
        self.streaming_trades = {}
        pending_tasks = asyncio.all_tasks()

        # While this loop appears to do nothing, without it the program freezes here :)
        # Can remove this block, for a warning
        for task in pending_tasks:
            pass
        asyncio.gather(*pending_tasks, return_exceptions=True)
        self.twm.stop()


    async def launch_stream(self):
        '''Starts up websocket and checks for previous stream data'''
        self.twm = ThreadedWebsocketManager()
        self.twm.start()
        asyncio.gather(self.restart_timer(), self.load())


    async def restart_stream(self):
        '''Restarts the stream, and schedules a restart timer to ensure streams run smoothly'''
        db.gen_log(str(self.stream_status()))
        await self.close_stream()
        await self.launch_stream()


    async def restart_timer(self):
        '''Restart functionality on a timer system, that will call itself again apon being restarted, Can be Switched off using restart[0] variable'''
        restart_counter = 0
        if not self.restart:
            return
        while restart_counter < RESTART_LIMIT and self.restart:
            await asyncio.sleep(RESTART_TIMER)
            restart_counter += 1
            print(str(restart_counter) + '->' + str(RESTART_LIMIT))
        if not self.restart:
            print("Closing auto-restart...")
            return
        if self.streaming_trades:
            print("Scheduled Restart...")
            await asyncio.gather(self.restart_stream())
        else:
            print(self.stream_status())
            db.gen_log(str(self.stream_status()))
            await asyncio.gather(self.restart_stream())


    def save(self):
        '''Saves the state of streaming trades'''
        print('Saving...')
        db.save_stream(self.streaming_trades)


    async def load(self):
        '''Loads stream state from savefile'''
        self.streaming_trades = db.load_stream()
        # Restart the streams
        if self.streaming_trades:
            print(self.stream_status())
            for i in self.streaming_trades.items():
                self.twm.start_kline_socket(callback=self.coin_trade_data, symbol=i[1][0].pair, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
        else:
            self.streaming_trades = {}


    async def add_trade_to_stream(self, new_trade):
        '''Adds a new pair to stream pricedata if it's not already being streamed'''
        self.start_trade_queue.extend(new_trade)

        for t in self.start_trade_queue[:]:
            duplicate = False
            exactcopy = False
            for a in self.streaming_trades: # pylint: disable=C0206
                if self.streaming_trades[a][0].pair == t.pair:
                    if len(self.streaming_trades[a]) > 0:
                        for o in self.streaming_trades[a]:
                            if o.id == t.id:
                                exactcopy = True    
                                print("Exact Copy!")
                    if not exactcopy:
                        self.streaming_trades[a].append(t)
                        t.stream_id = self.streaming_trades[a][0].stream_id
                    duplicate = True
            # If pair is not being streamed, begin streaming pair
            if not duplicate:
                streamID = self.twm.start_kline_socket(callback=self.coin_trade_data, symbol=t.pair, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
                print('Added', streamID, 'to stream')
                t.stream_id = streamID
                self.streaming_trades[t.stream_id] = [t]
            db.gen_log('Started Trade: ' + t.pair + ' | ' + str(t.id))
            self.start_trade_queue.remove(t)
            db.update_live_view(t)

        self.save()
        if self.stream_view:
            print(self.stream_status())


    def stoptrade(self):
        '''Removes closed trades from trade_stream'''
        closed_trades = []
        for stoptrade in self.stop_trade_queue[:]:
            print("Removing ", stoptrade, 'for reason', stoptrade.status)
            #If many trades on a socket, remove the trade and leave socket open
            if len(self.streaming_trades[stoptrade.stream_id]) > 1:
                for trade in self.streaming_trades[stoptrade.stream_id][:]:
                    if trade.id == stoptrade.id:
                        self.streaming_trades[stoptrade.stream_id].remove(trade)
                closed_trades.append(stoptrade)
                self.stop_trade_queue.remove(stoptrade)
            #Only trade in the socket, so remove the trade and stop the socket
            else:
                self.twm.stop_socket(stoptrade.stream_id)
                self.streaming_trades.pop(stoptrade.stream_id)
                closed_trades.append(stoptrade)
                self.stop_trade_queue.remove(stoptrade)
        return closed_trades


    def stream_status(self):
        '''Prints out the status of the stream'''
        status = '\n___Streaming___\n\n'

        for tradename, trade in self.streaming_trades.items():
            multiplier = ''
            if len(trade) > 1:
                multiplier = ' x'+str(len(trade))
            numspaces = (19 - len(tradename))
            status += str(tradename) + str(' '*numspaces) + multiplier + '\n'
        status += '_______________\n'
        return status


    def get_trade_list(self):
        '''returns all streaming trades in a list'''
        trade_list = []
        for t in self.streaming_trades:
            for trade in t:
                trade_list.append(trade)
        return trade_list

    def update_trades_now(self):
        '''Gathers socket data and sends it instantly'''
        for trades in list(self.streaming_trades.items()):
            trade = trades[1][0]
            time = str(utility.get_timestamp_now())
            time = int(time) - 60*1000
            klines = config.get_binance_config().get_historical_klines(symbol=trade.pair, interval=config.get_binance_config().KLINE_INTERVAL_1MINUTE , start_str=time)
            k = klines[0]
            new_k = {'t': k[0], 'T': k[6], 's': trade.pair, 'i': '1m', 'f': '-1', 'L': '-1', 'o': k[1], 'c': k[2], 'h': k[3], 'l': k[4], 'v': k[5], 'n': k[8], 'x': True, 'q': k[7], 'V': k[9], 'Q': k[10], 'B': k[11]}
            now_kline_msg = {'e': 'kline', 'E': k[0], 's': trade.pair, 'k': new_k}
            self.coin_trade_data(now_kline_msg)