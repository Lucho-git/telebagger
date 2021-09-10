# 3rd Party libs
from colorama import init
from colorama import Fore, Back, Style
from telethon import TelegramClient, events, sync, utils
from telethon.sessions import StringSession
import requests
import asyncio
import signal
import sys
import time

# Methods within this package
from trade_classes import Trade, Futures, MFutures
import msg_vip_signals
import always_win
import binance_wrap
import trade_stream
import fake_trade
import utility
import hirn

init()  # Initialising colorama

update = [False]
update2 = [False]
'''
# Stream Commands Local
STOP = '/stop'
STREAM = '/stream'
RESTART = '/restart'
MENU = '/menu'
ADD = '/add'
ADD2 = '/add2'
ADD3 = '/add3'
UPDATE = '/update'
UPDATE2 = '/update2'
'''
# Stream Commands Heroku Version
STOP = '/stop!'
STREAM = '/stream!'
RESTART = '/restart!'
MENU = '/menu!'
ADD = '/add!'
ADD2 = '/add2!'
ADD3 = '/add3!'
UPDATE = '/update!'
UPDATE2 = '/update2!'





def SendMessageToAlwaysWin(message):
    if '/USDT' in message:
        message = "<@&834911692303237172>\n" + message
    mUrl = "https://ptb.discord.com/api/webhooks/838079506660851762/7-lpGNlqWGGlO08XZJ3RwAvSXpWGDf5J6Z4ro5bsdtogYGGXovVfmYGmCb3Jvr1RvtWG"
    data = {"content": message}
    requests.post(mUrl, json=data)


async def StartTelegramForwarding():
    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    # Local Session
    stringsesh = '1BVtsOIQBu3LMJ7OLGqK63WxuVxgcdOm3EXqVqNANTsCC6En6KmoxsBlr59lP70lvaFTDjb_0mhyWyL5ndC5R3m-Nmo_75NyW_KPlsVPpwXxsK3CAfjQnIfOMw53X8WTbJUp98SmSmtioS1ZdY5PCFw2OZ7bBzzr_ttQpn_7z6IYhLvD5aEEGRSLoRaviT3uSgg9mKsFzbtZsGZ-R5g49Y7JleJtmqoBZPsPr_o8Uu1glHWHCcgcFv1x-ASRlaN-pf2a4dT1RAFIn30l20AVhIRw2bcrKFkhrfKJBfWPxtnuNvMnjjtix-STUGYV2UoHd6hHn2-hJ1T6JXbN-yugTCR9_ZNTZYhs='
    # Heroku session
    stringsesh = '1BVtsOIQBuxr6ZxLuwVQyGOhCNK5d9pQj3JItDcREpmOAnlKXQjqzWHhMXRrAnS4DVZrnwTjHjH12hX-gBbC0bobd8isvh3Xxoxw5hDQFuOEQNqXIIb80HMvtq4dztayw7Mj0I3FEE0ByBEM_Kr6goGhNsRWp0zYnaAXIUgzA8VXloZT9GZJhm1_HkV0mEO3vQMfd60Z7tTDnCz5_FaL1V7vsTxVPM8NbgwI1sDIKHBZFEwd0soJzNmQLfyD97_SBGUZQmz-3uo5zZNYTJPFZZfm6E-RMkRoWmFnkMtoLGFjs9wRI5zIh-MWxerZZZ4qPjpI3J8yzTmiYcTzdNn6fAROO7w-w9VQ='

    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)

    @client.on(events.NewMessage())
    async def my_event_handler(event):

        sender = await event.get_sender()
        chat = await event.get_chat()
        sender_id = str(sender.id)
        channel_name = utils.get_display_name(sender)
        message = str(event.raw_text)
        msg = "Channel name: " + channel_name + " | ID: " + sender_id
        if sender_id == "1375168387":  # Always Win
            valid = always_win.valid_trade_message(message)
            if valid:
                try:
                    aw = always_win.bag(message)
                    utility.add_message('Always Win', '[X]')
                    await trade_stream.addtrade(aw)
                except Exception as e:
                    utility.failed_message(message, 'Always Win', e)
                    utility.add_message('Always Win', '[-]')
        if chat.id == 1312345502:  # Vip Signals
            valid = msg_vip_signals.valid_trade_message(message)
            if valid:
                try:
                    vip = msg_vip_signals.bag(message, binance_wrap)
                    utility.add_message('Vip Signals', '[X]')
                    await trade_stream.addtrade(vip)
                except Exception as e:
                    utility.failed_message(message, 'Vip Signals', e)
                    utility.add_message('Vip Signals', '[-]')
        elif chat.id == 1248393106:  # HIRN
            valid = hirn.valid_trade_message(message)
            if valid:
                try:
                    hir = hirn.bag(message)
                    await trade_stream.addtrade(hir)
                except Exception as e:
                    utility.failed_message(message, 'Hirn', e)
                    utility.add_message('Hirn', '[-]')

        elif chat.id == 1899129008:  # Telegram Bot
            print("Robot Section +++")
            # stream commands
            if message == STOP:
                print('Exiting....')
                await client.disconnect()
            elif message == STREAM:
                await trade_stream.streamer()
            elif message == RESTART:
                await trade_stream.restart()
            elif message == UPDATE2:
                while update[0]:
                    await trade_stream.stopstream()
                    await asyncio.sleep(360)
            elif message == UPDATE:
                ''' Restart Every Hour'''
                if update[0]:
                    update[0] = False
                else:
                    update[0] = True
                print("Scheduled Restart1")
                while update[0]:
                    print("Scheduled Restart2")
                    await trade_stream.restart()
                    await trade_stream.streamer()
                    await asyncio.sleep(3600)
                    print("Scheduled Restart end")

            elif message == ADD:  # Test Trades
                tr0 = Trade('ETHUSDT', 'USDT', 'manual', 'futures')
                tr0.conditions = Futures(2800, 3200, 'long', 10, 'isolation')
                fake_trade.futures_trade(tr0)

                tr1 = Trade('ETHUSDT', 'USDT', 'manual', 'futures')
                tr1.conditions = Futures(2900, 3300, 'long', 5, 'isolation')
                fake_trade.futures_trade(tr1)

                tr2 = Trade('BTCUSDT', 'USDT', 'manual', 'futures')
                tr2.conditions = Futures(44500, 46000, 'long', 5, 'isolation')
                fake_trade.futures_trade(tr2)

                tr3 = Trade('NANOUSDT', 'USDT', 'manual', 'futures')
                tr3.conditions = Futures(5.5, 6, 'long', 5, 'isolation')
                fake_trade.futures_trade(tr3)

                tr4 = Trade('DOGEUSDT', 'USDT', 'manual', 'futures')
                tr4.conditions = Futures(0.28, 0.3, 'long', 5, 'isolation')
                fake_trade.futures_trade(tr4)

                newtrades = [tr0, tr1, tr2, tr3, tr4]
                await trade_stream.addtrade(newtrades)
            elif message == ADD2:
                tr0 = Trade('AVAXUSDT', 'USDT', 'Always Win', 'mfutures')
                tr0.conditions = MFutures([100, 100, 100, 100, 100], [46, 43, 42.9, 42.3, 41.1], [50, 20, 10, 10, 10],          [42.3, 41.1, 39.6, 35, 30], 'short', 20, 'isolation')
                tr1 = Trade('AVAXUSDT', 'USDT', 'Always Win', 'mfutures')
                tr1.conditions = MFutures([100, 100, 100, 100, 100], [46, 43, 42.9, 42.3, 41.1], [10, 22.5, 33.75, 25.3, 8.45], [42.3, 41.1, 39.6, 35, 30], 'short', 20, 'isolation')
                fake_trade.mfutures_trade(tr0)
                fake_trade.mfutures_trade(tr1)
                newtrades = [tr0, tr1]
                await trade_stream.addtrade(newtrades)

            elif message == ADD3:
                tr2 = Trade('SNXUSDT', 'USDT', 'Always Win', 'mfutures')
                tr2.conditions = MFutures([100, 100, 100, 100, 100], [15, 14.08, 13.7, 13.2, 12], [50, 20, 10, 10, 10], [14.08, 13.7, 13.2, 12, 10], 'short', 20, 'isolation')
                fake_trade.mfutures_trade(tr2)
                tr3 = Trade('LRCUSDT', 'USDT', 'Always Win', 'mfutures')
                tr3.conditions = MFutures([100, 100, 100, 100, 100], [0.52, 0.491, 0.483, 0.471, 0.45], [30, 20, 20, 10, 10], [0.483, 0.471, 0.45, 0.35, 0.30], 'short', 20, 'isolation')
                fake_trade.mfutures_trade(tr3)
                newtrades = [tr2, tr3]
                await trade_stream.addtrade(newtrades)
            elif message == MENU:
                await trade_stream.stopstream()

            elif message == '/hirn':
                pass
                with open('docs/hirn_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    valid = hirn.valid_trade_message(msg)
                    if valid:
                        hir = hirn.bag(msg)
                        await trade_stream.addtrade(hir)
                    else:
                        print('notvalid')

            elif message == '/aw':
                pass
                with open('docs/aw_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    valid = always_win.valid_trade_message(msg)
                    if valid:
                        aw = always_win.bag(msg)
                        await trade_stream.addtrade(aw)
                    else:
                        print('notval   id')

    # End of event handler code ____________________
    print("Launching Telegram Scraper...")
    await client.start()
    await client.get_dialogs()
    await trade_stream.streamer()
    await client.run_until_disconnected()


def handler_stop_signals(sig, frame):
    print("Am Dying lol")
    print('Aaaaaah it hurts')
    print("Make it stop")
    sys.exit()


#signal.signal(signal.SIGTERM, handler_stop_signals)  # Intializing graceful death on heroku restart
asyncio.run(StartTelegramForwarding())
print('We out this bitch')

