import utility
'''
Defines a set of conditions and parameters, 
for a signal to become a trade.

These values should be static

'''
class SpotBasic:
    '''Spot basic is a market spot order, with a takeprofit value, optional stoploss or
    timelimit to exit trade,if no stoploss is entered then a mandatory 7 day limit is applied'''
    def __init__(self, source, signal, coin, base, entry, profit, loss=None, timeout=None):
        self.source = source
        self.signal = signal
        self.coin = coin
        self.base = base
        self.entry = entry
        self.profit = profit
        self.loss = loss
        self.timeout = timeout
        self.time_generated = utility.get_timestamp_now()
        if (not self.loss) and (not self.timeout):
            self.timeout = utility.get_timestamp_now() + 604800000 # 7 Days timeout in seconds

    def check_timeout(self, trade):
        '''Checks to see if trade has timed out'''
        if self.timeout:
            if trade.latest_time > self.timeout:
                trade.status = 'timeout'

    def check_trade(self, trade):
        '''Checks to see if trade conditions have been met'''
        if trade.highest_price > self.profit:
            trade.status = 'profit'
            return
        if trade.lowest_price < self.loss:
            trade.status = 'loss'

    def get_value(self, trade):
        '''Returns current value of the trade'''
        raw_change = trade.entry_price - trade.last_price
        decimal_change = raw_change/trade.entry_price
        return decimal_change + 1

class SpotAdvanced(SpotBasic):
    """Spot advanced allows for multiple exit prices and percentages"""
    def __init__(self, source, signal, coin, base, entry, profit, loss, profit_amount, loss_amount, timeout=None):
        super().__init__(source, signal, coin, base, entry, profit, loss, timeout)
        self.profit_amount = profit_amount
        self.loss_amount = loss_amount

class FutureBasic(SpotBasic):
    '''Futures basic is a market futures order, can only be ISO,
    must have stoploss before liquidation value'''
    def __init__(self, source, signal, coin, direction, leverage, entry, profit, loss=None, timeout=None):
        super().__init__(source, signal, 'USD', coin, entry, profit, loss, timeout)
        self.direction = direction
        self.leverage = leverage

class FutureAdvanced(SpotAdvanced):
    '''Futures advanced combines all of the previous features in a derivatives market'''
    def __init__(self, source, signal, coin, entry, profit, loss, profit_amount, loss_amount, direction, leverage, timeout=None):
        super().__init__(source, signal, 'USD', coin, entry, profit, loss, profit_amount, loss_amount, timeout)
        self.direction = direction
        self.leverage = leverage