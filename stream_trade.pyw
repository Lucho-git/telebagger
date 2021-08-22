import random

class Trade:
    def __init__(self, pair, id):
        self.pair = pair.upper()
        self.id = id
        self.parameters = 'STUB'
        self.stream_id = None
        self.active = True

    def __repr__(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) +'}'
        retstr = ''+self.pair+'_'+str(self.id)+''
        return retstr

    def snapshot(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) + ' | ' + str(self.stream_id) + '}\n'
        retstr += 'Trade ended in Profit/Loss, Entry price here, Exit price here, TradePercentage = +/- x%'
        return retstr

    def stopchance(self):
        num = random.randrange(1, 3, 1)
        if num == 1:
            self.active = False
            print(self.pair, self.id, ' Got the dice roll')
        else:
            print(self.pair, self.id, 'Got lucky this time')