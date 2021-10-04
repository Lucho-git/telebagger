# 3rd Party libs
from colorama import init
from colorama import Fore, Back, Style
from telethon import TelegramClient, events, sync, utils
from telethon.sessions import StringSession
import requests
import asyncio
from utility import Sleeper
import signal
import sys
import time
import os

# Methods within this package
from trade_classes import Trade, Futures, MFutures
from fake_portfolio import Folio, Folios
import msg_vip_signals
import always_win
import binance_wrap
import trade_stream
import fake_trade
import utility
import hirn
import futures_signals

local = False

init()  # Initialising colorama
update = [False]
update2 = [False]

if local:
    # Local Telegram Session
    stringsesh = '1BVtsOGYBu7hocvoyzqBmRALD8c4MuSJNsBc_sGgFxw4KCc8sKZPCt1jw_ImmKKxXA55rqRyays4deNLkWgEtRO83BjFtB3dDWM_RNnHyenivcOxUwJDSdx8aIJwzeWkQekH37JYy6MqfhvKEXERwXXbdI8U1G1TlMLN6HwgzumiByHlBIMunVoWM75jFE5HJwX8qazJquBJRj2oFDutrk149H4Ouz-NMFgEocFATPPULsZtusrfZ5PztWcPoIMQ5zQIce_tVAFcF-EJ8T7Je3lO5jNxAQd-wYeYzW8G3vveZwyQrwDphQsbcry62gKUNx9tywZqr1XR8drDU_UQdsVoS6ShCE6k='
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
else:
    # Hosted Telegram Session
    stringsesh = '1BVtsOGYBu2t6OaO4arry2L6OBQy3lNP-RsyU27rfpPesJ6kMZ-mC5SfNDxQahcDL5UPWrH9clSKFA11RYHMl8RuN4mTYjq9_O5IvGaq1CNPRglT9mC4qDCH1Zg4cEfUTX_7nlnZNlh7JZ5im2UQGBTa7Sn_WA6VZH0LPOnKDBhr_oKuRbhtc6DDH86OyJVR1TrU6nNhV_R9vFgP1y0T0d9fgFSbpVeYvmWyTYHTouPoUpDHfdhY-0z7ZCoxNj8WckzhE1OM6cAgMxY9SGF3TdKKG6hSkeuOv4OChZNynYiHRBOlffDmvncQ1NUIMsZMx-hBztyDmSzRBJoIJ3KPr_oqyKLFv6RY='
    # Stream Commands Heroku Hosted
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
    global stringsesh

    loop = asyncio.get_event_loop()
    sleeper = Sleeper(loop)

    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)

    folios = Folios()
    folios.recover()

    # Receive Telegram Message Event Handler
    @client.on(events.NewMessage())
    async def my_event_handler(event):

        sender = await event.get_sender()
        chat = await event.get_chat()
        sender_id = str(sender.id)
        channel_name = utils.get_display_name(sender)
        message = str(event.raw_text)
        msg = "Channel name: " + channel_name + " | ID: " + sender_id

        if sender_id == "1548802426":                           # Always Win, Signal
            valid = always_win.valid_trade_message(message)
            if valid:
                try:
                    aw = always_win.bag(message)
                    utility.add_message('Always Win', '[X]')
                    await trade_stream.addtrade(aw)
                except Exception as e:
                    utility.failed_message(message, 'Always Win', e, '_failed.txt')
                    utility.add_message('Always Win', '[-]')

        if chat.id == 1312345502:                               # Vip Signals, Signal
            valid = msg_vip_signals.valid_trade_message(message)
            if valid:
                try:
                    vip = msg_vip_signals.bag(message)
                    utility.add_message('Vip Signals', '[X]')
                    await trade_stream.addtrade(vip)
                except Exception as e:
                    utility.failed_message(message, 'Vip Signals', e, '_failed.txt')
                    utility.add_message('Vip Signals', '[-]')

        elif chat.id == 1248393106:                             # HIRN, Signal
            valid = hirn.valid_trade_message(message)

            if valid and not event.is_reply:
                try:
                    hirn.cooldown()
                except ValueError:
                    print("Hirn Cooling Down")
                try:
                    hir = hirn.bag(message)
                    if hir:
                        utility.add_message('Hirn', '[X]')
                        await trade_stream.addtrade(hir)
                    else:
                        raise ValueError("No Signal / Cooling Down")
                except Exception as e:
                    utility.failed_message(message, 'Hirn', e, '_failed.txt')
                    utility.add_message('Hirn', '[-]')

        elif sender_id == "1350854897":                         # Futures Signals, Signal
            valid = futures_signals.valid_trade_message(message)
            if valid:
                try:
                    futsig = futures_signals.bag(message)
                    utility.add_message('Futures Signals', '[X]')
                    await trade_stream.addtrade(futsig)
                except Exception as e:
                    utility.failed_message(message, 'Futures Signals', e, '_failed.txt')
                    utility.add_message('Futures Signals', '[-]')
        # ___________________________________________________________________________________________________

        elif chat.id == 1899129008:  # Telegram Bot
            print("Robot Section +++")
            # Bot commands
            if message == STOP:
                await trade_stream.restart_schedule(sleeper)
                sleeper.cancel_all_helper()
                await asyncio.sleep(1)
                print('Exiting....')
                await client.disconnect()
                print("End of lin3e")

            # Stream Commands
            elif message == STREAM:
                await trade_stream.streamer()
            elif message == RESTART:
                await trade_stream.restart()
            elif message == MENU:
                await trade_stream.stopstream()

            # Testing Stubs, To be removed at a later stage
            elif message == '/hirn_real':
                with open('docs/hirn_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    valid = hirn.valid_trade_message(msg)
                    try:
                        hirn.cooldown()
                    except ValueError:
                        print("Hirn Cooling Down")
                    if valid:
                        try:
                            hir = hirn.bag(msg)
                            await trade_stream.addtrade(hir)
                        except Exception as e:
                            utility.failed_message(message, 'Hirn', e, '_failed.txt')
                            utility.add_message('Hirn', '[-]')
                    else:
                        print('notvalid')

            elif message == '/futsig':
                with open('docs/futures_signals_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    valid = futures_signals.valid_trade_message(msg)
                    if valid:
                        futsig = futures_signals.bag(msg)
                        await trade_stream.addtrade(futsig)
                    else:
                        print('notvalid')

            elif message == '/real':
                pair = 'ETHUSDT'
                base = 'USDT'
                sigal = Trade(pair, base, 'Futures Signals', 'mfutures')
                stoploss = [1, 1, 1, 1, 1]
                stopprof = [0.2, 0.2, 0.2, 0.2, 0.2]
                loss_targets = [3400, 3430, 3440, 3450, 3460]
                proftargets = [3475, 3480, 3490, 3500, 3510]
                sigal.conditions = MFutures(stoploss, loss_targets, stopprof, proftargets, 'long', '1', 'isolation')
                binance_wrap.mfutures_trade(sigal, 1)

            elif message == '/aw1':
                pass
                with open('docs/aw_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    valid = always_win.valid_trade_message(msg)
                    if valid:
                        aw = always_win.bag(msg)
                        await trade_stream.addtrade(aw)
                    else:
                        print('notval id')

            elif '/newport' in message:
                split = message.split(' ')
                port = Folio(split[1], split[2])
                folios.add_folios(port)
                folios.save()

            elif message == '/clear_folios':
                folios.clear_folios()

            elif message == '/display_folios':
                folios.snapshot()

        else:
            #post = msg + '\n' + message + '\n_________________\n'
            #utility.add_message('New Telegram Groups', post)
            pass

    # End of event handler code ____________________
    print("Launching Telegram Scraper...")
    await client.start()
    await client.get_dialogs()
    await trade_stream.streamer()
    await trade_stream.restart_schedule(sleeper)
    await client.run_until_disconnected()


# Currently non functional, want to find a way to gracefully shutdown the program when heroku calls sigterm
def handler_stop_signals(sig, frame):
    print("Am Dying lol")
    print('Aaaaaah it hurts')
    print("Make it stop")
    sys.exit()


# signal.signal(signal.SIGTERM, handler_stop_signals)  # Intializing graceful death on heroku restart
asyncio.run(StartTelegramForwarding())
print('We out this bitch')

os.kill(os.getpid(), signal.SIGTERM) # Not sure how this is going to react with heroku
print('Still going')
