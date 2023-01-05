import time
import utility
import binance_wrap
import trade_classes
import database_logging as db
from trade_conditions import FutureBasic, SpotBasic
from datetime import datetime


HIRN_COOLDOWN_TIME = 10  # In seconds
HIRN_LEVERAGE = 10  # Trade Leverage for Futures trades
HIRN_TRADE_PERCENT = 0.4  # How much remaining balance should be invested on each trade
HIRN_STOPLOSS_PERCENTAGE = 0.95   # Stoploss value to avoid getting liquidated
HIRN_TRADE_TIMEOUT = 604800000  # 7 Days in econds

class HirnSignal():
    '''Deals with signals from Hirn'''
    def __init__(self):
        self.timer = datetime.now().timestamp()
        self.tradeheat = False
        self.first = True

    def new_hirn_signal(self, signal):
        '''Entry point, returns nothing, or a trade signal'''
        if not self.validate_signal(signal.message):
            return
        return self.parse_conditions(signal)


    def parse_conditions(self, msg):
        '''returns trade conditions from a valid signal msg'''
        if not self.tradeheat:
            try:
                return self.parse(msg)
            except ValueError as e:
                print('Exception in Hirn Signal')
                print(e)
        else:
            db.failed_message(msg, 'Hirn', 'Exception TradeHeat')
            print('Suspected Tradeheat')
            return

    def validate_signal(self, msg):
        '''Verifies if the message from Hirn is a trade signal'''
        if 'Buy #' in msg:
            try:
                self.cooldown()
                print('\nNew Hirn Signal:\n', msg,'\n')
                return True
            except ValueError:
                print("Hirn Cooling Down")
                return False
        else:
            return False


    def cooldown(self):
        '''Hirn sometimes double posts their messages, this makes sure we are only trading once'''
        if not self.first:
            time.sleep(5)
        self.first = False

        timenow = datetime.now().timestamp()
        if timenow < self.timer:
            self.tradeheat = True
            raise ValueError('Hirn Signal while Cooling Down')
        else:
            self.tradeheat = False
            self.timer = timenow + HIRN_COOLDOWN_TIME
            self.first = True

    def parse(self, signal):
        '''Parses out the signal message into values'''
        lines = signal.message.split('\n')
        pair = lines[0].split('#')[1]
        coin = pair.split('/')[0]
        base = pair.split('/')[1]
        pair = pair.split('/')[0] + base
        entry = float(lines[1].split(': ')[1])
        profit_price = lines[2].split(': ')[1]
        profit_price = float(profit_price.split(' ')[0])
        lev = 1
        if entry > profit_price:
            direction = 'short'
            return
        else:
            direction = 'long'
        loss_price = entry * HIRN_STOPLOSS_PERCENTAGE/lev
        timeout = utility.get_timestamp_now() + HIRN_TRADE_TIMEOUT # 7 Days timeout in seconds
        return [SpotBasic('Hirn', signal, coin, base, entry, profit_price, loss_price, timeout)]
