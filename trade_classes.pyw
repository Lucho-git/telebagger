
from binance.client import Client
r_api_key='GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  #Put your own api keys here
r_api_secret='gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032'   
client = Client(r_api_key, r_api_secret)


class Trade:
  def __init__(self, pair, base, origin):
    self.pair = pair.upper()
    self.base = base.upper()
    self.status = 'Pre_Trade'
    self.price = None
    self.tradetime = None
    self.amount = None
    self.receipt = None
    self.numtrades = 0
    self.origin = origin
    self.fee = None
    
  def get_price(self, fills):
    total = 0
    totalqty = 0
    totalfees = 0
    for f in fills:
      price = float(f['price'])
      qty = float(f['qty'])
      fee = float(f['commission'])
      totalqty += qty
      total += price*qty
      totalfees += fee
    total = total/totalqty
    self.fee = totalfees
    return total
    
  def init_vals(self, receipt):
    self.receipt = receipt
    fills = receipt['fills']
    self.price = self.get_price(fills) 
    self.tradetime = receipt['transactTime']
    if receipt['executedQty']:
      self.status = 'Completed'
      self.amount = receipt['executedQty']
    self.numtrades += 1
  def snapshot(self):
    snapshot = 'SnapShot: \n'
    snapshot += 'Pair: '+self.pair +'\n'
    snapshot += 'Time: '+str(self.tradetime) +'\n'
    snapshot += 'Amount: '+str(self.amount) +'\n'
    snapshot += 'Price: '+str(self.price) +'\n'
    snapshot += 'Status: '+self.status +'\n'
    snapshot += 'Number Trades: '+str(self.numtrades) +'\n'
    snapshot += 'Signal Origin: '+self.origin +'\n'
    
    return snapshot
  
class Signal:
  def __init__(self, pair, base, entryprice, stoploss, exitprice, status, tradetime, amount):
    self.pair = pair.upper()
    self.base = base.upper()
    self.entryprice = entryprice
    self.stoploss = stoploss
    self.exitprice = exitprice
    self.lowest = entryprice
    self.highest = stoploss
    self.status = status
    self.tradetime = tradetime
    self.amount = amount

  def validate_trade(self):
    reason = ''
    valid = True
    if not self.pair:
      valid = False
    elif ('USDT' in self.pair) and ('BTC' in self.pair):
      valid = False
      reason = 'BTC/USDT pair not allowed'
    if not ((self.base == 'BTC') or (self.base == 'USDT')):
      valid = False
      reason = 'neither BTC or USDT is the base currency'      
    if not self.entryprice or self.isinstance(entryprice, str):
      valid = False
    if not self.stoploss or isinstance(self.stoploss, str):
      valid = False
    if not self.exitprice or isinstance(self.exitprice, str):
      valid = False
    if not self.status:
      valid = False
    if not self.tradetime:
      valid = False      
    return valid


  def trade_status(self):
    print('Pair:', self.pair)
    print('Status:',self.status)
    if self.status == 'tookprofit':
      profit = self.exitprice - self.entryprice
      print("Profit: $", profit, sep='')
    elif self.status == 'stoploss':
      loss = entryprice - stoploss
      print("Lost:", loss)
    elif self.status == 'ongoing':
      pass

class FTrade(Trade):
  def __init__(self, pair, base, entryprice, stoploss, exitprice, status, tradetime, amount, direction, leverage, mode):
    super().__init__(pair, base, entryprice, stoploss, exitprice, status, tradetime, amount)
    self.direction = direction
    self.leverage = leverage
    self.mode = mode

  def validate_trade(self):
    valid = super().validate_trade()
    if not self.direction:
      valid = False
    if not self.leverage:
      valid = False
    if not self.mode:
      valid = False
    return valid

  def trade_status(self):
    print('Pair:', self.pair)
    print('Status:',self.status)
    if self.status == 'tookprofit':
      profit = self.exitprice - self.entryprice
      profit = profit*self.leverage
      print("Profit: $", profit, sep='')
    elif self.status == 'stoploss':
      loss = self.entryprice - self.stoploss
      loss = loss*self.leverage
      print("Lost:", loss)
    elif self.status == 'ongoing':
      pass    
    print("Futures")

class MFTrade(FTrade):
  def __init__(self, pair, base, entryprice, stoploss, exitprice, status, tradetime, amount, direction, leverage, mode, m_tp, m_tpa, m_sl, wait_entry):
    super().__init__(pair, base, entryprice, stoploss, exitprice, status, tradetime, amount, direction, leverage, mode)
    self.m_tp = m_tp
    self.m_tpa = m_tpa
    self.m_sl = m_sl
    self.wait_entry = wait_entry

  def validate_trade(self):
    valid = super().validate_trade()
    if not self.m_tp:
      valid = False
    if not self.m_tpa:
      valid = False
    if not self.mode:
      valid = False

  def trade_status(self):
    super().trade_status()
    print("Multiple Futures")

def tradediff(trade1,trade2):
  price_diff = trade2.price - trade1.price
  value_diff = str(price_diff * trade2.price)
  perc_diff = str(round(price_diff/trade2.price,3))
  trade_time = str(trade2.time - trade1.time)
  snapshot = 'Bought ' + trade1.pair + ' at ' + str(trade1.price) + ' | Sold at ' + str(trade2.price) + '\n'
  snapshot += 'Trade Value of ' + value_diff + '\n'
  snapshot += 'Percentage ' + perc_diff + '\n'
  snapshot += 'Trading fees ' + str(trade1.fee + trade2.fee) +'\n'
  snapshot += 'Trade time ' + trade_time
  return snapshot
