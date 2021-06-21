from telethon import TelegramClient, events, sync, utils
from telethon.sessions import StringSession
import requests


def SendMessageToAlwaysWin(message):
    if '/USDT' in message:
        message= "<@&834911692303237172>\n" + message
    mUrl = "https://ptb.discord.com/api/webhooks/838079506660851762/7-lpGNlqWGGlO08XZJ3RwAvSXpWGDf5J6Z4ro5bsdtogYGGXovVfmYGmCb3Jvr1RvtWG"
    data = {"content": message}
    response = requests.post(mUrl, json=data)

def StartTelegramForwarding():
    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    stringsesh = '1BVtsOIIBuxkl8w5skOHjonDCR_DFvM7luxNQA8itLwXv1CYkUSzhUh-sjw6I-qA6esNDR7JLmxUhCdXXE96vb6wMxPTmbWRDTDD626CeEmGa3ohLgJaoH1CeG_28DuYLqnNVsumwhp-rVqFb4Ksvo7GNgnCOiNUOpMthcHT2neKufl6c31LpedhxGoBCnbZIFc4peEK_hwqlJgW7uQAVD2p8LD0LVR70EQxjXnwJ-ROfWScorMUrcV7C2NA1Fg71KFhWpGSoyfkKzgdAD7OIM3E5TdXLdpX-7g4lwQCloCL1GODnhGQD28eAwcHZ4Y7b_OWO3Ueeej7esgIbzx7NAJGJkfTTifI='
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
        elif chat.id == 1899129008:
            print("Robot Section +++")
            if str(event.raw_text) == '/stop':
              print('Exiting....')
              await client.disconnect()

    print("Starting telegram scraper")
    client.start()
    client.get_dialogs()
    client.run_until_disconnected()

StartTelegramForwarding()
