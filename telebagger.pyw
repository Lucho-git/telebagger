#3rd Party libs
from telethon import TelegramClient, events, sync, utils
from telethon.sessions import StringSession
import requests

#Methods within this package
from trade_classes import Trade, FTrade, MFTrade
import msg_vip_signals
import binance_wrap


def SendMessageToAlwaysWin(message):
    pass
    #TODO            remove stub
    if '/USDT' in message:
        message= "<@&834911692303237172>\n" + message
    mUrl = "https://ptb.discord.com/api/webhooks/838079506660851762/7-lpGNlqWGGlO08XZJ3RwAvSXpWGDf5J6Z4ro5bsdtogYGGXovVfmYGmCb3Jvr1RvtWG"
    data = {"content": message}
    response = requests.post(mUrl, json=data)

def StartTelegramForwarding():
    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    stringsesh = '1BVtsOHgBu5DuJXuehRfDlGAdXz0SidTkr6lFXo_csesUWmcScUvpi6WfkvoxIpkT78gUAfVl8aj8s-EvaWQ9Le4epxt2WyjPI9mbBpQRgYGIGM8YKKhFs0TMHv8P5EwWOxxOgKnka2RtW-J4aLNFv4zLmR9ekS2wDhLVhNlMhS6gnEoCVAmdxcLH3Qc7005IGuz7Ff2HqYXUYoKz5gDRbzC7gjF086Ux_vK52OSnWjo0XdkUH9qG2aPWohIY0cqeRHCtXIlYkESYcmifKkhcL1C_ZTapxsawrdYrOyuHUYP-fWVEPLFj4XjypFZrlaLUmLz8EL2VxkxG2p1vqFIjmgLI_VcWMSU='
    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)
    
    @client.on(events.NewMessage()) 
    async def my_event_handler(event):
        print(event.raw_text)

        sender = await event.get_sender()
        chat = await event.get_chat()
        sender_id = str(sender.id)
        channel_name = utils.get_display_name(sender)
        msg = "Channel name: " + channel_name + " | ID: " + sender_id
        print(msg)
        if sender_id == "1375168387":
            SendMessageToAlwaysWin(event.raw_text)
        if chat.id == 1312345502:
            msg_vip_signals.bag(event.raw_text)
        elif chat.id == 1899129008:
            print("Robot Section +++")
            if str(event.raw_text) == '/stop':
              print('Exiting....')
              await client.disconnect()
            #stub for testing
            if str(event.raw_text) == '/vip':
                msg_vip_signals.bag(event.raw_text, binance_wrap)
            if str(event.raw_text) == '/trade':
                print(binance_wrap.futures_snapshot())
            if str(event.raw_text) == '/buynano':
                #signal - trade object
                #percentage - percentage of funds, as a decimal
                #buying,  boolean true or false to buy or sell
                signal = Trade('NANOUSDT','USDT')
                #(self, pair, base, entryprice, stoploss, exitprice, status, tradetime, amount):
                rec = binance_wrap.market_trade(signal, 1, True)
            if str(event.raw_text) == '/sellnano':
                signal = Trade('NANOUSDT','USDT', '-1', '-1', '-1', 'PreTrade', 'Now', '-1')
                rec = binance_wrap.market_trade(signal, 1, False)
                
    print("Starting telegram scraper")
    client.start()
    client.get_dialogs()
    client.run_until_disconnected()

StartTelegramForwarding()
