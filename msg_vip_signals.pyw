def bag(msg):
  print("bag")
  print(msg)
  
  
  
  '''
async def print_past_messages(client):
  msgs = await client.get_messages('CryptoVIPsignalTA', limit=2000)
  if msgs is not None:
    print("Messages:\n---------")
    for msg in msgs:
      if ('buy zone'.upper() in str(msg).upper()) and ('target'.upper() in str(msg).upper())  and ('-' in str(msg)):
        print(msg.message)
        print('______________________')
        
        
        
        
      #search_text = open("/content/gdrive/MyDrive/MountDrive/example.txt", 'r').read()
      #result = None
      #result = await vip_signals_message(search_text)
      #if result:
        #vip_string = str(result[0]) +"___" + str(result[1])
        #await client.send_message(bot, vip_string)
      #await print_robot(event, search_text)
      
      
      async def vip_signals_message(vip_message):
  validity = valid_trade_message(vip_message)
  trade_type = None
  if validity:
    trade_type = search_coin(vip_message)
    #search_text = open("/content/gdrive/MyDrive/MountDrive/large_data.txt", 'r').read()
  return trade_type


def valid_trade_message(vip_message):
  vip_message = vip_message.upper()
  if ('BUY ZONE' in vip_message) and ('TARGET' in vip_message) and ('-' in vip_message):
    return True
  else:
    return False
'''

  
  
  
  
  
