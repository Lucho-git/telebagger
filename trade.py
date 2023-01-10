from datetime import datetime
import config
import utility
import database_logging as db
class Trade:
    '''Defines a trade'''
    def __init__(self, trade):
        self.exchange = 'binance'
        self.status = 'active'
        self.conditions = trade
        self.pair = trade.coin + trade.base
        self.start_time = self.get_time()
        self.latest_time = self.start_time
        self.id = self.start_time
        self.max_time_between_updates = 0
        self.entry_price = self.get_price()
        self.last_price = self.entry_price
        self.highest_price = self.entry_price
        self.lowest_price = self.entry_price
        self.closed_value = self.value()

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

        self.conditions.check_timeout(self)
        self.conditions.check_trade(self)

        if self.status != 'active':
            self.closed_value = self.conditions.get_value(self)
            self.save_trade()
            print('Trade', self.pair, ' closed, for reason:', self.status.upper(), 'close_value:', self.closed_value)
            #end of trade behaviours

    def update_snapshot(self):
        '''Console update of trade information'''
        time_started = datetime.fromtimestamp(float(self.start_time) / 1000).strftime('[%H:%M %d-%b-%y]')
        latest_time = datetime.fromtimestamp(float(self.latest_time) / 1000).strftime('[%H:%M %d-%b-%y]')
        ov_string = self.pair + ' | ' + str(self.id) + ' | ' + str(self.get_price()) + ' | ' + self.percent_value() + ' | ' + self.easy_duration() + ' | LongestUpdate: ' + str(round((self.max_time_between_updates/60000), 1)) + 'm | ' + self.conditions.source + ' | ' + self.status
        return ov_string

    def __str__(self):
        return self.pair  + '_' + self.conditions.source + '_' + str(self.id)

    def save_trade(self):
        '''Saves trade to database'''
        db.save_closed_trade(self)

    def duration(self):
        '''Calcs trade duration'''
        duration = self.latest_time - self.start_time
        duration = str(round((duration) / 1000, 2))
        return duration

    def duration_hours(self):
        '''returns duration in hours'''
        time = float(self.duration())
        time = time/3600
        return str(round(time, 2))

    def easy_duration(self):
        '''Returns most readable time duration'''
        time = float(self.duration())
        unit = 'seconds'
        if time > 60:
            time = time/60
            unit = 'minutes'
        if time > 60:
            time = time/60
            unit = 'hours'
            if time > 24:
                time = time/24
                unit = 'days'

        time = str(round(time, 2))
        return str(time) + ' ' + unit

    def value(self):
        'Returns value as a decimal'
        return self.conditions.get_value(self)

    def percent_value(self):
        'Returns value as a percentage'
        percent = self.value()*100
        percent = str(round(percent, 1)) + '%'
        return percent

    def get_time(self):
        '''gets trade start time'''
        return self.conditions.get_time()


    def get_price(self):
        '''gets trade entry'''
        return self.conditions.get_price()