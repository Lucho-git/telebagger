from datetime import datetime

class Trade:
    '''Defines a simulated trade'''
    def __init__(self, signal):
        self.client = #get from config
        self.status = 'pretrade'
        self.signal = signal
        self.start_time = datetime.now().timestamp()
        self.end_time = None
        self.latest_time = self.start_time
        self.max_time_between_updates = 0
        self.entry_price = float(client.get_symbol_ticker(symbol=self.pair)['price'])
        self.exit_price = None
        self.recent_price = self.entry_price
        self.peak_profit = 0
        self.peak_loss = 0
