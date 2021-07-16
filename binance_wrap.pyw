from binance.client import Client
import math

r_api_key='GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  #Put your own api keys here
r_api_secret='gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032'   

realclient = Client(r_api_key, r_api_secret)

def round_decimals_down(number:float, decimals:int=2):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)
    factor = 10 ** decimals
    return math.floor(number * factor) / factor

def market_trade(signal, percentage, buying):
    symbol = signal.symbol
    base = signal.base
    coin = symbol.replace(base,'')
    trade_size = percentage

    if not buying:
      #buying back btc or usdt
      #find symbol precision
      symbol_info = realclient.get_symbol_info(symbol)
      step_size = 0.0
      for f in symbol_info['filters']:
        if f['filterType'] == 'LOT_SIZE':
          step_size = float(f['stepSize'])
      precision = int(round(-math.log(step_size, 10), 0))    
    
      balance = float(realclient.get_asset_balance(asset=coin)['free'])
      balance = balance * trade_size
      quant = str(float(round_decimals_down(balance, precision)))
      market_order = realclient.order_market_sell(symbol=symbol, quantity=quant)
      print('sold nano')
    else:
      #buying amount of signal coin
      balance = float(realclient.get_asset_balance(asset=base)['free'])
      balance = balance * trade_size
      if base == 'USDT':
        precision = 8
      elif base == 'BTC':
        precision = 6
      balance = str(float(round_decimals_down(balance, precision)))
      market_order = realclient.create_order(symbol=symbol, type="market", side='buy', quoteOrderQty=balance, price=None)
      print('bought nano')
    return market_order
    
    
def btc2usdt():
  balance = float(realclient.get_asset_balance(asset='BTC')['free'])
  quant = str(float(round_decimals_down(balance, 6)))
  try:
    market_order = realclient.order_market_sell(symbol='BTCUSDT', quantity=quant)
  except Exception e:
    print('Exception converting BTC to USDT')
    print(e)
  print("Converted BTC to USDT")
  
def usdt2btc():
  symbol = 'BTCUSDT'
  side = 'BUY'
  amount = float(realclient.get_asset_balance(asset='USDT')['free'])
  try:
    market_order = realclient.create_order(symbol=symbol, type="market", side='buy', quoteOrderQty=amount, price=None)
  except Exception e:
    print('Exception converting USDT to BTC')
    print(e)
  print("Converted USDT to BTC")
  
def coin_pairs(coinname):
  exchange_info = realclient.get_exchange_info()
  pairs = []
  for s in exchange_info['symbols']:
    if s['baseAsset'] == coinname:
      print(s['symbol'])
      pairs.append(s['symbol'])
  return pairs
                   
def isUSDTpair(coinname):
  pairs = coin_pairs(coinname)
  for p in pairs:
    if 'USDT' in p:
       return True
  return False
                   
def isBTCpair(coinname):
  pairs = coin_pairs(coinname)
  for p in pairs:
    if 'BTC' in p:
       return True
  return False                   

def futures_snapshot():
  #get futures info
  tangibles = realclient.futures_account_balance()
  retstring = ''
  
  for t in tangibles:
    if float(t["balance"]) > 0:
      print(t['asset'], "Balance: ",t['balance'])
      if 'withdrawAvailable' in t:
        perc_withdraw =  float(t['withdrawAvailable']) / float(t['balance']) *100
        print('   Avaliable: ',t["withdrawAvailable"],'\033[94m', round(perc_withdraw,2), '%', '\033[0m')
       
  #get futures positions    
  positions = realclient.futures_position_information()
  for p in positions:
    if (float(p['positionAmt']) > 0) or (float(p['positionAmt']) < 0):
      #print(p)
      #Determine if position is in profit or loss
      gain = True
      if float(p['unRealizedProfit']) < 0:
        gain = False

    #Calculate percentage profit or loss
      percentage =  str(abs((float(p['markPrice']) - float(p['entryPrice']))  / float(p['markPrice'])*100*int(p['leverage']))) 
      if gain:
        percentage = '\033[92m' + percentage + '\033[0m'
      elif not gain:
        percentage = '\033[91m' + '-'+percentage + '\033[0m'

      pos = "\nPair: " + p['symbol']

      if p['marginType'] == 'isolated':
        staked_and_pnl = float(p['isolatedWallet']) + float(p['unRealizedProfit'])
        pos += "\nStaked: "+p['isolatedWallet']
      elif p['marginType'] == 'cross':
        staked = abs(float(p['positionAmt'])) * float(p['entryPrice']) * 1/int(p['leverage'])
        pos += "\nStaked: "+str(staked)
        staked_and_pnl = staked + float(p['unRealizedProfit'])
      else:
        print("Problem checking margin Type")
      pos += "\nCurrent: " + str(staked_and_pnl)
      pos += "\n\nAmount: "+p['positionAmt']
      pos += "\nEntry: " +p['entryPrice']
      pos += "\nMark: " +p['markPrice']
      pos += "\nLeverage: " +p['leverage']

      pos += "\n\nPNL: " +p['unRealizedProfit']
      pos += "\nPNL Percent: " + str(percentage) + ' %'
      pos += "\nStop Loss: " + "gotta add that shit"
      pos += "\nTake Profit: " + "repeat above"
      pos += "\nLIQ: " +p['liquidationPrice']
      pos += "\nType: " +p['marginType']
      pos += "\n---------------------"
      retstring += pos
    return retstring
