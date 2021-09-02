# 3rd Party libs
from colorama import init
from colorama import Fore, Back, Style
from telethon import TelegramClient, events, sync, utils
from telethon.sessions import StringSession
import requests
import asyncio
import pyrebase
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


config = {  # initialising database connection
    "apiKey": "AIzaSyDl_eUsJkNxN5yW9KS6X0n0tkQFruV8Tbs",
    "authDomain": "telebagger.firebaseapp.com",
    "projectId": "telebagger",
    "storageBucket": "telebagger.appspot.com",
    "messagingSenderId": "332905720250",
    "appId": "1:332905720250:web:e2006e777fa8d980d61583",
    "measurementId": "G-02W82CCF85",
    "databaseURL":  "https://telebagger-default-rtdb.firebaseio.com/"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

init()  # Initialising colorama

update = [False]
update2 = [False]


def SendMessageToAlwaysWin(message):
    if '/USDT' in message:
        message = "<@&834911692303237172>\n" + message
    mUrl = "https://ptb.discord.com/api/webhooks/838079506660851762/7-lpGNlqWGGlO08XZJ3RwAvSXpWGDf5J6Z4ro5bsdtogYGGXovVfmYGmCb3Jvr1RvtWG"
    data = {"content": message}
    response = requests.post(mUrl, json=data)


def StartTelegramForwarding():
    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    stringsesh = '1BVtsOL0Bu4c_nflfOgudjCsjpr3PqxJGtfN6SVKTuxYdxzCr0e4-BXbirG8DuWTRwTYjBXhzqcyUr-hVXTYNgepV_dssSX1_yZMIewmEL1QQAuFWcKSB9WPs4U5O37e2s-CXE2BZwmPGrG_p-FI6AvIPRFD7CDb_PAxqI3j6HWKA-lQf8rvYsO6ozlYWyVZ1di554f_UMa7ijdgi0zwcWKhyAt-uWfX9FY2kjWatZNdOvYWLFNZwx_rgKL_ikZSBcNVmv7yx1A6aIvsGnTX8GMWeEEmmQ__VRVAewJ58V0YCYlWqfbRx96_VP4Whrn4s-Wl09sh517n3LhFuvY3S2JqhAA55bgA='

    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)

    @client.on(events.NewMessage())
    async def my_event_handler(event):
        # print(event.raw_text)

        sender = await event.get_sender()
        chat = await event.get_chat()
        sender_id = str(sender.id)
        channel_name = utils.get_display_name(sender)
        message = event.raw_text
        msg = "Channel name: " + channel_name + " | ID: " + sender_id
        # print(msg)
        if sender_id == "1375168387":
            valid = always_win.valid_trade_message(message)
            if valid:
                try:
                    aw = always_win.bag(message, binance_wrap)
                    utility.add_message(storage, 'Always Win', '[X]')
                    await trade_stream.addtrade(aw)
                except Exception as e:
                    utility.failed_message(message, 'Always Win', storage, e)
                    utility.add_message(storage, 'Always Win', '[-]')

            # Forward Message to my telegram channel
            # await client.send_message(1576065688, event.message)
            pass
        if chat.id == 1312345502:
            valid = msg_vip_signals.valid_trade_message(message)
            if valid:
                try:
                    vip = msg_vip_signals.bag(message, binance_wrap)
                    utility.add_message(storage, 'Vip Signals', '[X]')
                    await trade_stream.addtrade(vip)
                except Exception as e:
                    utility.failed_message(message, 'Vip Signals', storage, e)
                    utility.add_message(storage, 'Vip Signals', '[-]')
        elif chat.id == 1248393106:
            valid = hirn.valid_trade_message(message)
            if valid:
                try:
                    hir = hirn.bag(message)
                    await trade_stream.addtrade(hir)
                except Exception as e:
                    utility.failed_message(message, 'Hirn', storage, e)
                    utility.add_message(storage, 'Hirn', '[-]')

        elif chat.id == 1899129008:
            print("Robot Section +++")
            if str(event.raw_text) == '/stop':
                print('Exiting....')
                await client.disconnect()

            if str(event.raw_text) == '/hirn':
                contents = open("docs/hirn_example.txt", "r", errors="ignore").read()
                hir = hirn.bag(contents)
                await trade_stream.addtrade(hir)

            if str(event.raw_text) == '/vip':
                contents = open("docs/onexample.txt", "r").read()
                utility.failed_message(contents, 'Vip Signals', storage, 'ERROOR MESSAGE')
                utility.add_message(storage, 'Vip Signals', '[-]')
                vip_trades = msg_vip_signals.bag(contents, binance_wrap)
                await trade_stream.addtrade(vip_trades)

            if str(event.raw_text) == '/aw':
                message = event.raw_text
                aw = None
                if '/USDT' in message:
                    aw = always_win.bag(message, binance_wrap)
                if aw:
                    await trade_stream.addtrade(aw)

            elif str(event.raw_text) == '/buycoin':
                signal = Trade('AIONUSDT', 'USDT', 'Manual')
                binance_wrap.market_trade(signal, 0.04, True)
                signal.snapshot()
            elif str(event.raw_text) == '/sellcoin':
                signal = Trade('AIONUSDT', 'USDT', 'Manual')
                binance_wrap.market_trade(signal, 1, False)
                signal.snapshot()
            elif str(event.raw_text) == '/dynasty':
                await client.send_message(1576065688, 'AW MESSAGE')

                # stream commands
            elif str(event.raw_text) == '/stream':
                await trade_stream.streamer()
            elif str(event.raw_text) == '/restart':
                await trade_stream.restart()
            elif str(event.raw_text) == '/update2':
                while update[0]:
                    await trade_stream.stopstream()
                    await asyncio.sleep(360)
            elif str(event.raw_text) == '/update':
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

            elif str(event.raw_text) == '/add':
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
            elif str(event.raw_text) == '/add2':
                tr0 = Trade('AVAXUSDT', 'USDT', 'Always Win', 'mfutures')
                tr0.conditions = MFutures([100, 100, 100, 100, 100], [46, 43, 42.9, 42.3, 41.1], [50, 20, 10, 10, 10],          [42.3, 41.1, 39.6, 35, 30], 'short', 20, 'isolation')
                tr1 = Trade('AVAXUSDT', 'USDT', 'Always Win', 'mfutures')
                tr1.conditions = MFutures([100, 100, 100, 100, 100], [46, 43, 42.9, 42.3, 41.1], [10, 22.5, 33.75, 25.3, 8.45], [42.3, 41.1, 39.6, 35, 30], 'short', 20, 'isolation')
                fake_trade.mfutures_trade(tr0)
                fake_trade.mfutures_trade(tr1)
                newtrades = [tr0, tr1]
                await trade_stream.addtrade(newtrades)

            elif str(event.raw_text) == '/add3':
                tr2 = Trade('SNXUSDT', 'USDT', 'Always Win', 'mfutures')
                tr2.conditions = MFutures([100, 100, 100, 100, 100], [15, 14.08, 13.7, 13.2, 12], [50, 20, 10, 10, 10], [14.08, 13.7, 13.2, 12, 10], 'short', 20, 'isolation')
                fake_trade.mfutures_trade(tr2)
                tr3 = Trade('LRCUSDT', 'USDT', 'Always Win', 'mfutures')
                tr3.conditions = MFutures([100, 100, 100, 100, 100], [0.52, 0.491, 0.483, 0.471, 0.45], [30, 20, 20, 10, 10], [0.483, 0.471, 0.45, 0.35, 0.30], 'short', 20, 'isolation')
                fake_trade.mfutures_trade(tr3)
                newtrades = [tr2, tr3]
                await trade_stream.addtrade(newtrades)

            elif str(event.raw_text) == '/menu':
                await trade_stream.stopstream()
            elif str(event.raw_text) == '/colour':
                print(Fore.RED + 'RED TEXT')

    # End of event handler code ____________________
    print("Starting telegram scraper")
    client.start()
    client.get_dialogs()
    client.run_until_disconnected()


StartTelegramForwarding()
print('We out this bitch')

