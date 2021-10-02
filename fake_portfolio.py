import utility


class Folio:
    def __init__(self, name, starting_balance):
        self.name = name
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.avaliable_balance = starting_balance


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
