import utility

MIN_TRADE_VALUE = 10


class Folio:
    def __init__(self, name, starting_balance):
        self.name = name
        self.starting_balance = float(starting_balance)
        self.balance = float(starting_balance)
        self.avaliable_balance = float(starting_balance)
        self.trades = []

    def start_trade(self, trade_id, percent):
        ft_value = float(self.avaliable_balance)*float(percent)
        if not ft_value > MIN_TRADE_VALUE:
            raise ValueError("Fake Trade Balance " + str(self.name) + " is Too low")
        print(self.avaliable_balance)
        print(ft_value)
        self.avaliable_balance -= ft_value
        trade = [trade_id, ft_value]
        self.trades.append(trade)

    def end_trade(self, trade_id, return_val):
        for t in self.trades:
            if t[0] == trade_id:
                ft_value = t[1]
                return_val = return_val * ft_value
                self.avaliable_balance += return_val
                self.balance += return_val
                self.trades.remove(t)

    def snapshot(self):
        snap = ''
        for t in self.trades:
            snap += str(t[0]) + ', $' + str(t[1]) + '\n'
        return snap


class Folios:
    def __init__(self):
        self.folios = []

    def add_folios(self, in_folios):
        print(self.folios)
        self.folios.append(in_folios)
        print('Created Folio', self.folios[0].name)

    def clear_folios(self):
        self.folios = []
        self.save()
        print("Cleared all folios")

    def recover(self):
        recovered_folios = utility.load_folio()
        if recovered_folios:
            self.folios = recovered_folios.folios
        else:
            self.folios = []
        print('recovered folios', self.folios)

    def save(self):
        utility.save_folio(self)

    def snapshot(self):
        print(self.folios)
        for f in self.folios:
            snap = '\n' + f.name + ': $' + str(f.balance) + '\n'
            snap += 'Avaliable Balance: ' + str(f.avaliable_balance) + ' / ' + str(f.balance) + '\n'
            snap += f.snapshot() + '\n'
            print(snap)

    def start_trade(self, trade, percent):
        changes = False
        print('Folio1')
        print(len(self.folios))
        for f in self.folios:
            for b in trade.bag_id:
                print(b, 'vs ', f.name)
                if f.name == b:
                    f.start_trade(trade.id, percent)
                    changes = True
        return changes

    def end_trade(self, trade, trade_return):
        changes = False
        for f in self.folios:
            for b in trade.bag_id:
                if f.name == b:
                    f.end_trade(trade.id, trade_return)
                    changes = True
        return changes
