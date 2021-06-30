from binance.client import Client


r_api_key='GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  #Put your own api keys here
r_api_secret='gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032' 

realclient = Client(r_api_key, r_api_secret)

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
