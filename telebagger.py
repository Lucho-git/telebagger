# 3rd Party libs
from colorama import init
from colorama import Fore, Back, Style
from telethon import TelegramClient, events, sync, utils, tl
from binance.exceptions import BinanceAPIException, BinanceOrderException
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

import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

local = utility.is_local()

init()  # Initialising colorama
update = [False]
update2 = [False]

chat_ids = []

if local:
    # Local Telegram Session
    stringsesh = '1BVtsOIYBu3-mW8LWNklskWf4ubCwmoTJCMtaTn1yotapoMDSnukfzWHHy0VZdOu5THq8Z8dvfLZ-3QYoqZW7sFja_0uk_ovCdQTOhdzUu72KMnSoqxntyvytcfYQyfVdt1UV7V1d4Zhxy9WlMJEl3IcEeWbCyruidkkVGs4n1cW_vh__Li3PvHfKTuJA5EeZ58KNp1LzmDC-G66T8chUqU-RKHdFt2RT6NEQL-6zJLYyq_VTMgRiv-8HtfEs2OOyI-rsVsOwHC-p7_794gPk_B14HQ02zoWne_QZNesgc2NvsvNdwr_Eqg9D883qD9xEiSHvZNNIiDJJaM6b5IMfH-NZe9022dk='
    # Stream Commands Local
    STOP = '/stop'
    STREAM = '/stream'
    STOPSTREAM = '/stopstream'
    RESTART = '/restart'
    MENU = '/menu'
    ADD = '/add'
    ADD2 = '/add2'
    ADD3 = '/add3'
    UPDATE = '/update'
    UPDATE2 = '/update2'
    PRE_AW = '/pre_aw'
    ALWAYS_WIN_SIGNAL = '/aw'
    HIRN_SIGNAL = '/hirn'
    NEW_PORTFOLIO = '/newport'
    CLEAR_PORTFOLIOS = '/clear_folios'
    DISPLAY_PORTFOLIOS = '/display_folios'
    SNAPSHOT = '/snapshot'
    CLOSE_FUTURES = '/close_futures'

else:
    # Hosted Telegram Session
    stringsesh = '1BVtsOIYBu0ovo28ka-RmvdqJHl7RbsJJpyDOKdEjyfK3-8E5tKCiaHyPmgaTvb1zIB-irRQqHtEOSw0ZL3LAvJTCfkMTuLet_11w1Zr6iaYNc_yrWV9h8r3OPEaTcKjXeEc-Nh9DLNhwjEIJ1EIS5PCPVeoEn9nwlFqfh8dtXbGGl0U3vLcp1-0wsp7tGUw958MZkmvvgFvZyiJ-iKr7FImY_1_Li4dY3S2ex68fz4UPSukfCzPpTJBf_HGX5dDvMT9HYF5xWG2XqlqoueSHRR9x4ylhq6vnkJOtfftSmPXoO2E76Gd80b_1UIbOfQ_y0fy5lvGsMI3_UZXvqV9cVaariRrHUlE='
    # Stream Commands Heroku Hosted
    # Backup:1BVtsOJEBuzPKndfyOcR8Db9PCaurB8JH7jyBTy8H2ur2WZMoPlqEki0GOPEfgnWjXptA40uN1OK3QL8yGCF4CEWbfsBdUvk1b8zhdo0ZF42vSNKgyz6mrupuEKZ9OmQxgXWSHx66vjM70le782D-z8dnreaVxmmSsrMxkU3GCjyQE2fHRZZp2-9njfZMNAVczYimmK2QzHhvvFHpDxXBgJ4WxZp3hg5FICpBo05fy7xc9Y5xV_ZZpRwwixjy0iZOo8o1ZbvLx7AFC8g-RvFWYHK8ZJVJcjp8KyXc95tBQxtdDbRv6EDxVUEQROLH5C5apM9laK-pZQp_LUc5FiGX_nT0iRBrVg4=
    STOP = '/stop!'
    STREAM = '/stream!'
    STOPSTREAM = '/stopstream!'
    RESTART = '/restart!'
    MENU = '/menu!'
    ADD = '/add!'
    ADD2 = '/add2!'
    ADD3 = '/add3!'
    UPDATE = '/update!'
    UPDATE2 = '/update2!'
    PRE_AW = '/pre_aw!'
    ALWAYS_WIN_SIGNAL = '/aw!'
    HIRN_SIGNAL = '/hirn!'
    NEW_PORTFOLIO = '/newport!'
    CLEAR_PORTFOLIOS = '/clear_folios!'
    DISPLAY_PORTFOLIOS = '/display_folios!'
    SNAPSHOT = '/snapshot!'
    CLOSE_FUTURES = '/close_futures!'


def SendMessageToAlwaysWin(message):
    if '/USDT' in message:
        message = "<@&834911692303237172>\n" + message
    mUrl = "https://ptb.discord.com/api/webhooks/838079506660851762/7-lpGNlqWGGlO08XZJ3RwAvSXpWGDf5J6Z4ro5bsdtogYGGXovVfmYGmCb3Jvr1RvtWG"
    data = {"content": message}
    requests.post(mUrl, json=data)


async def StartTelegramForwarding(client):
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
        print(msg)
        # Real code

        if sender_id == "1548802426":                           # Always Win, Signal
            # Changed to sending text only, as sending the full message is no longer functional, I suspect Always win guy did something to his data to try and prevent copycats
            await client.send_message(1576065688, message)
            valid = always_win.valid_trade_message(message)
            if valid:
                try:
                    aw = always_win.bag(message)
                    utility.add_message('Always Win', '[X]')
                    await trade_stream.addtrade(aw)
                except Exception as e:
                    utility.failed_message(message, 'Always Win', e, '_failed.txt')
                    utility.add_message('Always Win', '[-]')
                utility.gen_log('Signal from Always Win')
            else:
                try:
                    valid2 = always_win.valid_trade_message(message)
                except ValueError:
                    print("Problem with PreSignal Validation")
                if valid2:
                    print("PreSignal Message")
        elif sender_id == '1312345502':                               # Vip Signals, Signal
            valid = msg_vip_signals.valid_trade_message(message)
            if valid:
                try:
                    vip = msg_vip_signals.bag(message)
                    utility.add_message('Vip Signals', '[X]')
                    await trade_stream.addtrade(vip)
                except Exception as e:
                    utility.failed_message(message, 'Vip Signals', e, '_failed.txt')
                    utility.add_message('Vip Signals', '[-]')

        elif sender_id == '1248393106':                             # HIRN, Signal
            print('Hirn Message')
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
                utility.gen_log('Signal from HIRN')

        # ___________________________________________________________________________________________________

        elif chat.id == 1899129008:  # Telegram Bot
            print("Robot Section +++")
            utility.gen_log('Telegram Robot: ' + message)
            # Bot commands
            if message == STOP:
                # await trade_stream.restart_schedule(sleeper)
                # sleeper.cancel_all_helper()
                # todo figure out if sleeper access is necessary here
                await asyncio.sleep(1)
                print('Exiting....')
                await client.disconnect()
                print("End of lin3e")

            # Stream Commands
            elif message == STREAM:
                await trade_stream.streamer()
            elif message == STOPSTREAM:
                await trade_stream.close_stream()
            elif message == RESTART:
                await trade_stream.restart_stream()
            elif message == MENU:
                await trade_stream.stopstream()

            # Testing Stubs, To be removed at a later stage
            elif message == HIRN_SIGNAL:
                post = 'fake hirn message log' + str(chat.id)
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
                            if hir:
                                await trade_stream.addtrade(hir)
                                utility.add_message('Hirn', '[-]')
                        except Exception as e:
                            utility.failed_message(message, 'Hirn', e, '_failed.txt')
                            utility.add_message('Hirn', '[-]')
                    else:
                        print('notvalid')

            elif message == '/status':
                print(trade_stream.stream_status())

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

            elif message == '/past':
                msgs = await client.get_messages('HIRN_CRYPTO', limit=5)
                if msgs is not None:
                    print("Messages:\n---------")
                    for msg in msgs:
                        print(msg)
                        print(msg.chat_id)
                        print(msg.message)
                        print('______________________')

            elif message == ALWAYS_WIN_SIGNAL:
                with open('docs/aw_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    valid = always_win.valid_trade_message(msg)
                    if valid:
                        aw = always_win.bag(msg)
                        await trade_stream.addtrade(aw)
                    else:
                        print('notval id')
            elif message == PRE_AW:
                with open('docs/pre_aw_example.txt', encoding="utf8") as f:
                    msg = f.read()
                    always_win.valid_trade_message_2(msg)

            elif NEW_PORTFOLIO in message:
                split = message.split(' ')
                if NEW_PORTFOLIO == split[0]:
                    port = Folio(split[1], split[2])
                    folios.add_folios(port)
                    folios.save()

            elif message == CLEAR_PORTFOLIOS:
                folios.clear_folios()

            elif message == DISPLAY_PORTFOLIOS:
                folios.recover()
                if folios.folios:
                    print('Folios:')
                    folios.snapshot()
                else:
                    print('Folios is empty')

            elif message == SNAPSHOT:
                print(binance_wrap.futures_snapshot())

            elif message == CLOSE_FUTURES:
                binance_wrap.close_all_futures()
        else:
            recognized = False
            for i in chat_ids:
                if i == chat.id:
                    recognized = True

            # Unrecognized Telegram Channels
            if not recognized:
                post = msg + '\n' + message + '\n' + str(sender.id) + '|' + str(chat.id) + '\n_________________\n'
                utility.add_message('New Telegram Groups', post)

    # End of event handler code ____________________


async def setup_scraper():
    global stringsesh
    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)
    await StartTelegramForwarding(client)

    print("Launching Telegram Scraper...")
    utility.gen_log('Launching Telegram Scraper...\n')
    await client.start()
    await client.get_dialogs()
    #loop = asyncio.get_event_loop()
    await asyncio.gather(trade_stream.streamer(), trade_stream.timer(), client.run_until_disconnected())


# Currently non functional, want to find a way to gracefully shutdown the program when heroku calls sigterm
def handler_stop_signals(sig, frame):
    print("Am Dying lol")
    print('Aaaaaah it hurts')
    print("Make it stop")
    sys.exit()


# signal.signal(signal.SIGTERM, handler_stop_signals)  # Intializing graceful death on heroku restart
asyncio.run(setup_scraper())
print('We out this bitch')

os.kill(os.getpid(), signal.SIGTERM)  # Not sure how this is going to react with heroku
print('Still going')
