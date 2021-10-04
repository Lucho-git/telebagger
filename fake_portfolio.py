import utility

MIN_TRADE_VALUE = 10


class Folio:
    def __init__(self, name, starting_balance):
        self.name = name
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.avaliable_balance = starting_balance
        self.trades = []

    def start_trade(self, trade_id, percent):
        ft_value = self.avaliable_balance*percent
        if not ft_value > MIN_TRADE_VALUE:
            raise ValueError("Fake Trade Balance " + str(self.name) + " is Too low")

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


class Folios:
    def __init__(self):
        self.folios = []

    def add_folios(self, in_folios):
        print(self.folios)
        self.folios.append(in_folios)
        print(self.folios[0].name)

    def clear_folios(self):
        self.folios = []
        self.save()

    def recover(self):
        recovered_folios = utility.load_folio()
        self.folios = recovered_folios

    def save(self):
        utility.save_folio(self.folios)

    def snapshot(self):
        for f in self.folios:
            snap = f.name + ': $' + f.balance + '\n'
            snap += 'Avaliable Balance: ' + f.avaliable_balance + ' / ' + f.balance + '\n\n'
            print(snap)

    def start_trade(self, trade, percent):
        changes = False
        for f in self.folios:
            for b in trade.bag_id:
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
