from binance.client import Client
from colorama import init
from colorama import Fore, Back, Style
import datetime
import re
init(strip=True)

r_api_key = 'GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  # Put your own api keys here
r_api_secret = 'gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032'
client = Client(r_api_key, r_api_secret)


class Futures:
    def __init__(self, stoploss, stopprof, direction, leverage, mode):
        self.stoploss = stoploss
        self.stopprof = stopprof
        self.status = 'PreTrade'
        self.direction = direction
        self.leverage = leverage
        self.mode = mode


class MFutures:
    def __init__(self, stoploss, losstargets, stopprof, proftargets, direction, leverage, mode):
        self.stoploss = stoploss
        self.losstargets = losstargets
        self.stopprof = stopprof
        self.proftargets = proftargets
        self.targetnum = 0
        self.status = 'PreTrade'
        self.direction = direction
        self.leverage = leverage
        self.mode = mode
        self.amount_left = 100
        self.trade_amounts = 0
        self.new_lowest = 99999999999999
        self.new_highest = 0


class MTrade:
    def __init__(self, stoploss, losstargets, stopprof, proftargets):
        self.stoploss = stoploss
        self.losstargets = losstargets
        self.stopprof = stopprof
        self.proftargets = proftargets
        self.numtargets = len(proftargets)


class STrade:
    def __init__(self, stoploss, stopprof):
        self.stoploss = stoploss
        self.stopprof = stopprof


class Trade:
    def __init__(self, pair, base, origin, in_type):
        self.pair = pair.upper()
        self.base = base.upper()
        self.status = 'Pre_Trade'
        self.price = None
        self.time = None
        self.id = None
        self.stream_id = None
        self.amount = None
        self.receipt = None
        self.numtrades = 0
        self.origin = origin
        self.fee = None
        self.type = in_type
        self.conditions = None
        self.timelimit = None
        self.lowest = None
        self.highest = None
        self.closed = None
        self.savestring = None
        self.real = False
        self.trade_log = ''

    def get_price(self, fills):
        total = 0
        totalqty = 0
        totalfees = 0
        for f in fills:
            price = float(f['price'])
            qty = float(f['qty'])
            fee = float(f['commission'])
            totalqty += qty
            total += price * qty
            totalfees += fee
        total = total / totalqty
        self.fee = totalfees
        return total

    def init_trade_vals(self, receipt):
        self.receipt = receipt
        fills = receipt['fills']
        self.price = self.get_price(fills)
        self.time = receipt['transactTime']
        if receipt['executedQty']:
            self.status = 'Completed'
            self.amount = receipt['executedQty']
        self.numtrades += 1

    def strip_ansi_codes(self, s):
        return re.sub('\033\\[([0-9]+)(;[0-9]+)*m', '', s)

    def percent_diff(self, now):
        diff = float(now) - self.price

        if self.type == 'spot':
            percentage = round((diff / self.price * 100), 2)
            percentage = str(percentage)
            if diff < 0:
                percentage = Fore.RED + "- " + percentage + "%" + Style.RESET_ALL
            elif diff > 0:
                percentage = Fore.LIGHTGREEN_EX + "+ " + percentage + "%" + Style.RESET_ALL
            else:
                percentage = Fore.LIGHTBLUE_EX + "+ " + percentage + "%" + Style.RESET_ALL
            return percentage
        elif self.type == 'futures' or self.type == 'mfutures':
            percentage = diff / self.price * 100 * self.conditions.leverage
            if diff < 0:
                if self.conditions.direction == 'short':
                    percentage = percentage*-1
                    percentage = Fore.LIGHTGREEN_EX + "+ " + str(round(percentage, 2)) + "%" + Style.RESET_ALL
                elif self.conditions.direction == 'long':
                    percentage = percentage * -1
                    percentage = Fore.RED + "- " + str(round(percentage, 2)) + "%" + Style.RESET_ALL
            elif diff > 0:
                if self.conditions.direction == 'short':
                    percentage = Fore.RED + "- " + str(round(percentage, 2)) + "%" + Style.RESET_ALL
                elif self.conditions.direction == 'long':
                    percentage = Fore.LIGHTGREEN_EX + "+ " + str(round(percentage, 2)) + "%" + Style.RESET_ALL
            else:
                percentage = Fore.LIGHTBLUE_EX + "+ " + str(round(percentage, 2)) + "%" + Style.RESET_ALL
            return percentage

    def snapshot(self):
        snapshot = 'SnapShot: \n'
        snapshot += 'Pair: ' + self.pair + '\n'
        snapshot += 'Time: ' + str(self.time) + '\n'
        snapshot += 'Amount: ' + str(self.amount) + '\n'
        snapshot += 'Price: ' + str(self.price) + '\n'
        snapshot += 'Status: ' + self.status + '\n'
        snapshot += 'Number Trades: ' + str(self.numtrades) + '\n'
        snapshot += 'Signal Origin: ' + self.origin + '\n'
        return snapshot

    def trade_diff(self, trade1, trade2):
        price_diff = trade2.price - trade1.price
        value_diff = str(price_diff * trade2.price)
        perc_diff = str(round(price_diff / trade2.price, 3))
        trade_time = str(trade2.time - trade1.time)
        snapshot = 'Bought ' + trade1.pair + ' at ' + str(trade1.price) + ' | Sold at ' + str(trade2.price) + '\n'
        snapshot += 'Trade Value of ' + value_diff + '\n'
        snapshot += 'Percentage ' + perc_diff + '\n'
        snapshot += 'Trading fees ' + str(trade1.fee + trade2.fee) + '\n'
        snapshot += 'Trade time ' + trade_time
        return snapshot

    def __repr__(self):
        retstr = ' {TradeObj | ' + self.pair + ' | ' + str(self.id) + '}'
        retstr = '' + self.pair + '_' + str(self.id) + ''
        return retstr

    def percentage_result(self, limit, direction):
        percentage = abs(self.price - limit)/self.price * 100
        percentage = percentage * self.conditions.leverage
        if direction == 'loss':
            if self.conditions.leverage == 'short':
                if limit > self.price:
                    percentage = percentage * (-1)
            elif self.conditions.leverage == 'long':
                if limit < self.price:
                    percentage = percentage * (-1)
        return percentage

    def update_mfutures(self):
        direction = self.conditions.direction
        if direction == 'long':
            losslimit = self.conditions.losstargets[self.conditions.targetnum]
            proflimit = self.conditions.proftargets[self.conditions.targetnum]

            if self.conditions.new_lowest < losslimit:
                # amount_left = amount_left - stoploss_amount
                amount = self.conditions.stoploss[self.conditions.targetnum]
                self.trade_log = 'Selling ' + str(amount) + '% of ' + self.pair + ' for ' + str(self.percentage_result(losslimit, 'loss'))
                print(self.trade_log)
                self.conditions.amount_left = self.conditions.amount_left - (self.conditions.amount_left * amount/100)
                self.conditions.trade_amounts += self.percentage_result(losslimit, 'loss') * amount/100
                if self.conditions.amount_left == 0:
                    self.status = 'stoploss'
                    self.closed = self.conditions.losstargets[self.conditions.targetnum]
                elif self.conditions.amount_left > 0:
                    self.conditions.targetnum += 1
                    self.conditions.new_highest = self.price
                    self.conditions.new_lowest = self.price
                else:
                    print("longLoss Numbers not adding to 100, error")

            elif self.conditions.new_highest > proflimit:
                amount = self.conditions.stopprof[self.conditions.targetnum]
                self.trade_log = 'Selling ' + str(amount) + '% of ' + self.pair + ' for ' + str(self.percentage_result(proflimit, 'prof'))
                print(self.trade_log)
                self.conditions.amount_left = self.conditions.amount_left - amount
                self.conditions.trade_amounts += self.percentage_result(proflimit, 'prof') * amount/100
                if self.conditions.amount_left == 0:
                    self.status = 'stopprof'
                    self.closed = self.conditions.proftargets[self.conditions.targetnum]
                elif self.conditions.amount_left > 0:
                    self.conditions.targetnum += 1
                    self.conditions.new_highest = self.price
                    self.conditions.new_lowest = self.price
                else:
                    print('longProfit Numbers not adding to 100, error')

        elif direction == 'short':
            proflimit = self.conditions.proftargets[self.conditions.targetnum]
            losslimit = self.conditions.losstargets[self.conditions.targetnum]
            print(self.conditions.new_highest, '>', losslimit)
            if self.conditions.new_lowest < proflimit:
                amount = self.conditions.stopprof[self.conditions.targetnum]
                self.trade_log = 'Selling ' + str(amount) + '% of ' + self.pair + ' for ' + str(self.percentage_result(losslimit, 'prof'))
                print(self.trade_log)
                self.conditions.amount_left = self.conditions.amount_left - amount
                self.conditions.trade_amounts += self.percentage_result(proflimit, 'prof') * amount/100
                if self.conditions.amount_left == 0:
                    self.status = 'stopprof'
                    self.closed = self.conditions.proftargets[self.conditions.targetnum]
                elif self.conditions.amount_left > 0:
                    self.conditions.targetnum += 1
                    self.conditions.new_highest = self.price
                    self.conditions.new_lowest = self.price
                else:
                    print('shortProfit Numbers not adding to 100, error')
            elif self.conditions.new_highest > losslimit:
                amount = self.conditions.stoploss[self.conditions.targetnum]
                self.trade_log = 'Selling ' + str(amount) + '% of ' + self.pair + ' for ' + str(self.percentage_result(losslimit, 'loss'))
                print(self.trade_log)
                self.conditions.amount_left = self.conditions.amount_left - (self.conditions.amount_left * amount/100)
                self.conditions.trade_amounts += self.percentage_result(losslimit, 'loss') * amount/100
                if self.conditions.amount_left == 0:
                    self.status = 'stoploss'
                    self.closed = self.conditions.stoploss[self.conditions.targetnum]
                elif self.conditions.amount_left > 0:
                    self.conditions.targetnum += 1
                    self.conditions.new_highest = self.price
                    self.conditions.new_lowest = self.price
                else:
                    print("shortLoss Numbers not adding to 100, error")

    def update_futures(self):
        direction = self.conditions.direction
        if direction == 'long':
            if self.conditions.new_lowest < self.conditions.stoploss:
                self.status = 'stoploss'
                self.closed = self.conditions.stoploss
            if self.conditions.new_highest > self.conditions.stopprof:
                self.status = 'stopprof'
                self.closed = self.conditions.stopprof
        elif direction == 'short':
            if self.conditions.new_lowest < self.conditions.stopprof:
                self.status = 'stopprof'
                self.closed = self.conditions.stopprof
            if self.conditions.new_highest > self.conditions.stoploss:
                self.status = 'stoploss'
                self.closed = self.conditions.stopprof

    def update_trade(self, k):
        if k['low'] < self.lowest:
            self.lowest = k['low']
        if k['high'] > self.highest:
            self.highest = k['high']

        if self.status == 'active' and self.type == 'futures':
            self.update_futures()
        elif self.status == 'active' and self.type == 'mfutures':
            if k['low'] < self.conditions.new_lowest:
                self.conditions.new_lowest = k['low']
            if k['low'] < self.conditions.new_highest:
                self.conditions.new_highest = k['high']
            self.update_mfutures()
        elif self.status == 'active' and self.type == 'mtrade':
            pass

        if self.timelimit:
            if k['time'] > self.timelimit:
                self.status = 'time'
                self.closed = k['last']

        if not self.status == 'active':
            self.trade_complete(k)
            print(self.savestring)

    def update_snapshot(self, k):
        now = float(k['last'])
        leverage = ''
        direction = ''
        if self.type == 'mfutures' or self.type == 'futures':
            leverage = '[' + str(self.conditions.leverage) + 'x]'
            direction = '['+self.conditions.direction+']'

        print('\n')
        start_time = datetime.datetime.fromtimestamp(float(self.time) / 1000).strftime('%Y-%m-%d_%H:%M')
        time_passed = round((k['time'] - self.time) / 3600000, 2)
        print(self.pair, leverage,direction, '--', start_time, '(', time_passed, ') hrs')
        print('_______________________________')
        print('Buy Price:', Fore.LIGHTBLUE_EX, self.price, Style.RESET_ALL)
        print('Lowest:', self.lowest, '|', self.percent_diff(self.lowest))
        print('Highest:', self.highest, '|', self.percent_diff(self.highest))
        print('Now:', k['last'], '|', self.percent_diff(now))
        print('===============================')
        if self.type == 'futures':
            print('Targets:', Fore.RED, self.conditions.stoploss, '|', Fore.LIGHTBLUE_EX, now,'|',Fore.LIGHTGREEN_EX, self.conditions.stopprof, Style.RESET_ALL)
            print('_______________________________')
        elif self.type == 'mfutures':
            print('NextTargets:', Fore.RED, self.conditions.losstargets[self.conditions.targetnum], '|', Fore.LIGHTBLUE_EX, now,'|',Fore.LIGHTGREEN_EX, self.conditions.proftargets[self.conditions.targetnum], Style.RESET_ALL)
            print('Amount:', self.conditions.trade_amounts)
            print('Amountleft:', self.conditions.amount_left)
            # Making List Pretty
            str_prof_targets = list(map(str, self.conditions.proftargets))
            str_prof_targets[self.conditions.targetnum] = Fore.LIGHTBLUE_EX + str_prof_targets[self.conditions.targetnum] + Style.RESET_ALL
            prof_targets = '['
            last = str_prof_targets[len(str_prof_targets)-1]
            for t in str_prof_targets:
                prof_targets += t
                if t == last:
                    break
                prof_targets += ', '
            prof_targets += ']'
            # _________________
            str_loss_targets = list(map(str, self.conditions.losstargets))
            str_loss_targets[self.conditions.targetnum] = Fore.LIGHTBLUE_EX + str_loss_targets[self.conditions.targetnum] + Style.RESET_ALL
            loss_targets = '['
            last = str_loss_targets[len(str_loss_targets)-1]
            for t in str_loss_targets:
                loss_targets += t
                if t == last:
                    break
                loss_targets += ', '
            loss_targets += ']'
            # Done Making List Pretty

            print('Target:', self.conditions.targetnum)
            print('Profit Targets:', prof_targets, ' | ', 'StopLoss Targets', loss_targets)
            print('_______________________________')

    def trade_complete(self, k):
        time_passed = str(round((k['time'] - self.time) / 3600000, 2))
        start_time = datetime.datetime.fromtimestamp(float(self.time) / 1000).strftime('%Y-%m-%d_%H:%M')
        end_time = datetime.datetime.fromtimestamp(float(k['time']) / 1000).strftime('%Y-%m-%d_%H:%M')
        print('Here close', self.closed)
        percent = self.strip_ansi_codes(str(self.percent_diff(self.closed)))

        savestr = ''
        savestr += self.pair + '\n'
        savestr += 'TimeStarted: ' + start_time + ' | ' + end_time + '\n'
        savestr += 'Duration: ' + time_passed + ' hrs\n'
        savestr += 'Pricechange: ' + str(self.price) + ' | ' + str(self.closed) + ' | ' + percent + '\n'
        savestr += 'Status: ' + self.status + '\n'
        savestr += 'Origin: ' + self.origin + '\n'

        self.savestring = savestr
