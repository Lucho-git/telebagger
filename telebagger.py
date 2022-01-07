# 3rd Party libs
from colorama import init
from colorama import Fore, Back, Style
from telethon import TelegramClient, events, sync, utils
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

local = utility.is_local()

init()  # Initialising colorama
update = [False]
update2 = [False]

chat_ids = []

if local:
    # Local Telegram Session
    stringsesh = '1BVtsOJEBuzzZQ-O2BIsgWcUfS_ZXmJF2mPAlPmAUaCarcopkPY3kmWm9RmIDfkEl71R7LPMWFua2aL9Lf5i-nJ-qiO7k0GQ1isA45cwnGXVF53wfFmwi7oG7TMAKEEjinC0zz_awWmawpQtonaUMUFNCyjf7zFrAZ-A20nUKYy4EwuMdaOsV3H-ugZnutqahxgByZRnNmHjrP9jalgQn8DCf5cDC3nSItTJHP_OuH1QfXPu7MCoU6GOcyM63dU2BeEhLiR0YKXwPRdYGiHvuvZ0M8DVjd6lYfwflxFd3IKOlIg7R9ir_WkhhjrUCgDgnCykCHGwMXtap-7YVpN05agcl-EQxxhQ='
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
    stringsesh = '1BVtsOJEBuw5_wjvpcl72vb_KFrG6S54BY6H3WHfV8_Xg4j-z21Bm34P5NiqO98MifyYN9bF4ZqCeGgGhgZdC87nZHxhSBzQ3IgVXyzmZTkqMRayUaq_KbFDltzfyy-ykgG6re7H7Hey6EC9lxSTSKVYiiCevlD5Kie35HM7pDRXd-UVDlcI4atjQlqnnYW5QN1lKcbzPk5mHGCCHf8sti38OeDQU94y4x13OmqBa6K9U8skO8WAFLaDQ3silE1wdKRhwV0ssfoqtxxacJnCRIYdM1C9qV_3mOkCpUs0J4X7629b3AxCVgdRlE-ypQX4B9rhQpk9AWozKV118eMfDhOW4I5Bzz-k='
    # Stream Commands Heroku Hosted
    # Backup:1BVtsOJEBuzPKndfyOcR8Db9PCaurB8JH7jyBTy8H2ur2WZMoPlqEki0GOPEfgnWjXptA40uN1OK3QL8yGCF4CEWbfsBdUvk1b8zhdo0ZF42vSNKgyz6mrupuEKZ9OmQxgXWSHx66vjM70le782D-z8dnreaVxmmSsrMxkU3GCjyQE2fHRZZp2-9njfZMNAVczYimmK2QzHhvvFHpDxXBgJ4WxZp3hg5FICpBo05fy7xc9Y5xV_ZZpRwwixjy0iZOo8o1ZbvLx7AFC8g-RvFWYHK8ZJVJcjp8KyXc95tBQxtdDbRv6EDxVUEQROLH5C5apM9laK-pZQp_LUc5FiGX_nT0iRBrVg4=
    STOP = '/stop!'
    STREAM = '/stream!'
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
            await client.send_message(1576065688, event.message)
            valid = always_win.valid_trade_message(message)
            if valid:
                try:
                    aw = always_win.bag(message)
                    utility.add_message('Always Win', '[X]')
                    await trade_stream.addtrade(aw)
                except Exception as e:
                    utility.failed_message(message, 'Always Win', e, '_failed.txt')
                    utility.add_message('Always Win', '[-]')
            else:
                try:
                    valid2 = always_win.valid_trade_message(message)
                except ValueError:
                    print("Problem with PreSignal Validation")
                if valid2:
                    print("PreSignal Message")
        if sender.id == '1312345502':                               # Vip Signals, Signal
            valid = msg_vip_signals.valid_trade_message(message)
            if valid:
                try:
                    vip = msg_vip_signals.bag(message)
                    utility.add_message('Vip Signals', '[X]')
                    await trade_stream.addtrade(vip)
                except Exception as e:
                    utility.failed_message(message, 'Vip Signals', e, '_failed.txt')
                    utility.add_message('Vip Signals', '[-]')

        elif sender.id == '1248393106':                             # HIRN, Signal
            print("HIRN MESSAAAGGEEGE")
            post = 'real hirn message log' + str(chat.id)
            utility.add_message('real hirn message log', post)
            # todo remove utility logs above once finished debugging

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
            elif message == HIRN_SIGNAL:
                post = 'fake hirn message log' + str(chat.id)
                utility.add_message('fake hirn message log', post)
                # todo remove utility logs above once finished debugging
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
                trade_stream.stream_status()

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
                print(post)

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

os.kill(os.getpid(), signal.SIGTERM)  # Not sure how this is going to react with heroku
print('Still going')
