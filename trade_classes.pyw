class Trade:
  def __init__(self, pair, entryprice, stoploss, exitprice, status, tradetime, amount):
    self.pair = pair
    self.entryprice = entryprice
    self.stoploss = stoploss
    self.exitprice = exitprice
    self.lowest = entryprice
    self.highest = stoploss
    self.status = status
    self.tradetime = tradetime
    self.amount = amount

  def validate_trade(self):
    valid = True
    if not self.pair:
      valid = False
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
  def __init__(self, pair, entryprice, stoploss, exitprice, status, tradetime, amount, direction, leverage, mode):
    super().__init__(pair, entryprice, stoploss, exitprice, status, tradetime, amount)
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
  def __init__(self, pair, entryprice, stoploss, exitprice, status, tradetime, amount, direction, leverage, mode, m_tp, m_tpa, m_sl, wait_entry):
    super().__init__(pair, entryprice, stoploss, exitprice, status, tradetime, amount, direction, leverage, mode)
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
