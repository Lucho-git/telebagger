from datetime import datetime
import config
import utility
import database_logging as db
class Trade:
    '''Defines a simulated trade'''
    def __init__(self, trade):
        self.client = config.get_binance_config()
        self.status = 'active'
        self.trade = trade
        self.pair = trade.coin + trade.base
        self.start_time = utility.get_timestamp_now()
        self.latest_time = self.start_time
        self.id = self.start_time
        self.max_time_between_updates = 0
        self.entry_price = float(self.client.get_symbol_ticker(symbol=self.pair)['price'])
        self.last_price = self.entry_price
        self.highest_price = 0
        self.lowest_price = 99999999999
        self.closed_value = 1

    def update_trade(self, k):
        '''Recieves updated price information'''

        # Update time since, last update
        update_time_diff = round(int(k['time']) - int(self.latest_time), 2)
        if update_time_diff > self.max_time_between_updates:
            self.max_time_between_updates = update_time_diff
        self.latest_time = k['time']

        # Updating latest trade price values
        self.last_price = k['last']
        if k['low'] < self.lowest_price:
            self.lowest_price = k['low']
        if k['high'] > self.highest_price:
            self.highest_price = k['high']

        self.trade.check_timeout(self)
        self.trade.check_trade(self)

        if self.status != 'active':
            self.closed_value = self.trade.get_value(self)
            self.client = None
            self.save_trade()
            print('Trade', self.pair, ' closed, for reason:', self.status.upper(), 'close_value:', self.closed_value)
            #end of trade behaviours

    def update_snapshot(self):
        '''Console update of trade information'''
        time_started = datetime.fromtimestamp(float(self.start_time) / 1000).strftime('[%H:%M %d-%b-%y]')
        latest_time = datetime.fromtimestamp(float(self.latest_time) / 1000).strftime('[%H:%M %d-%b-%y]')
        ov_string = 'Trade: ' + self.pair + ' | ' + str(self.id) + ' | TimeStarted: ' + time_started + ' | TimeUpdated: ' + str(latest_time) + ' | LongestUpdate: ' + str(round((self.max_time_between_updates/60000), 1)) + 'm | Origin: ' + self.trade.signal.origin.name + ' | Status: ' + self.status
        return ov_string

    def save_trade(self):
        db.save_trade(self)

    def duration(self):
        '''Calcs trade duration'''
        duration = self.latest_time - self.start_time
        duration = str(round((duration) / 3600000, 2))
        return duration

    def __str__(self):
        return self.pair  + '_' + self.trade.signal.origin.name + '_' + str(self.id)
