from datetime import datetime
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
        self.time_generated = datetime.now().timestamp()
        if (not self.loss) and (not self.time):
            self.time = datetime.now().timestamp() + 604800 # 7 Days timeout in seconds

class SpotAdvanced(SpotBasic):
    """Spot advanced allows for multiple exit prices and percentages"""
    def __init__(self, source, signal, base, coin, entry, profit, loss, profit_amount, loss_amount, timeout=None):
        super().__init__(source, signal, base, coin, entry, profit, loss, timeout)
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
