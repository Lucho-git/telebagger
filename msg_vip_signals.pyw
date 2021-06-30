def bag(msg):
  print("bag")
  
  search_text = open("onexample.txt", 'r').read()
  result = None
  result = vip_signals_message(search_text)
  if result:
    vip_string = str(result[0]) +"___" + str(result[1])
    print(vip_string)
    #client.send_message(bot, vip_string)
    #await print_robot(event, search_text)
      
def vip_signals_message(vip_message):
  validity = valid_trade_message(vip_message)
  trade_type = None
  if validity:
    trade_type = search_coin(vip_message)
    #search_text = open("/content/gdrive/MyDrive/MountDrive/large_data.txt", 'r').read()
  return trade_type

def valid_trade_message(vip_message):
  vip_message = vip_message.upper()
  if (('TARGET ' in vip_message) or ('TARGET:' in vip_message)) and ('-' in vip_message):
    print("Valid Message")
    return True
  else:
    return False
 
def search_coin(text):
  coins = []
  with open("binance_spot.txt", "r") as file:
    for line in file:
      line = line.strip()
      coinspaces = str(line + ' ')
      coinslash = str(line + '/')
      coinusdt = str(line + 'USDT')
      coinfullstop = str(line + '.')
      coinbtc = str(line +'BTC')
      if (coinspaces in text) or (coinslash in text) or (coinusdt in text) or (coinfullstop in text) or (coinbtc in text):
        coins.append(line)
  if not coins:
    with open("binance_future.txt", "r") as file:
      for line in file:
        line = line.strip()
        coinspaces = str(line + ' ')
        coinslash = str(line + '/')
        coinusdt = str(line + 'USDT')
        coinfullstop = str(line + '.')
        coinbtc = str(line +'BTC')
        if (coinspaces in text) or (coinslash in text) or (coinusdt in text) or (coinfullstop in text) or (coinbtc in text):
          coins.append(line)
    if coins:
      coins.append('Futures')
    else:
      print("No Coin Found")
  else:
    coins.append('Spot')
  
  #edge cases
  if 'DATA' in coins:
    print("Edge Case DATA")
    coins.remove('ATA')
  if 'YFII' in coins:
    coins.remove('YFI')
  if 'LOOM' in coins:
    coins.remove('OM')
  if 'DEGO' in coins:
    coins.remove('GO')
  if 'HBAR' in coins:
    coins.remove('AR')
  if len(coins)> 2:
    print("Multiple Coins")
    first = 9999999
    for c in coins:
      if not (c == 'Futures') and not (c == 'Spot'):
        current = text.find(c)
        if current < first:
          first = current
          coins[0] = c
  if coins:
    coins[1] = coins[int(len(coins))-1]
  return coins[0:2]
  
  
  
'''
def print_past_messages(client):
  msgs = client.get_messages('CryptoVIPsignalTA', limit=2000)
  if msgs is not None:
    print("Messages:\n---------")
    f = open("vip_examples.txt", "w")

    for msg in msgs:
      if ('buy zone'.upper() in str(msg).upper()) and ('target'.upper() in str(msg).upper())  and ('-' in str(msg)):
        f.write(str(msg.message) +'\n')
        f.write('______________________\n')
    f.close()   
'''
  
  
  
  
  
  
