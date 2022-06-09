# 3rd Party libs
from colorama import init
from telethon import TelegramClient, events, sync, utils, tl
from telethon.sessions import StringSession
from dotenv import load_dotenv
import requests
import asyncio
import signal
import sys
import time
import os
import traceback

# Methods within this package
from trade_classes import Trade, Futures, MFutures
from fake_portfolio import Folio, Folios
import always_win
import binance_wrap
import trade_stream
import utility
import hirn
import futures_signals


local = utility.is_local()

load_dotenv()  # gathering environment variables
init()  # Initialising colorama
update = [False]
update2 = [False]

chat_ids = []

if local:
    # Local Telegram Session
    stringsesh = os.getenv('TELEGRAM_LOCALSAVE')
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
    stringsesh = os.getenv('TELEGRAM_SERVERSAVE')
    # Ellas Savestring: stringsesh = os.getenv('TELEGRAMELLASAVE')
    # Stream Commands Heroku Hosted
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

'''
def SendMessageToAlwaysWin(message):
    if '/USDT' in message:
        message = "<@&834911692303237172>\n" + message
    mUrl = "https://ptb.discord.com/api/webhooks/838079506660851762/7-lpGNlqWGGlO08XZJ3RwAvSXpWGDf5J6Z4ro5bsdtogYGGXovVfmYGmCb3Jvr1RvtWG"
    data = {"content": message}
    requests.post(mUrl, json=data)
'''


async def StartTelegramForwarding(client):
    # folios = Folios()
    # folios.recover()

    # Receive Telegram Message Event Handler
    @client.on(events.NewMessage())
    async def my_event_handler(event):

        try:
            sender = await event.get_sender()
            chat = await event.get_chat()
            sender_id = str(sender.id)
            channel_name = utils.get_display_name(sender)
            message = str(event.raw_text)
            msg = "Channel name: " + channel_name + " | ID: " + sender_id
            print(msg)
            # Real code

            if sender_id == "1548802426":                           # Always Win, Signal
                if not event.message.photo:
                    await client.send_message(1576065688, event.message)
                elif message:
                    try:
                        await client.send_message(1576065688, message)
                    except ValueError as e:
                        utility.error_log(str(e) + message)

                valid = always_win.valid_trade_message(message)
                if valid:
                    try:
                        aw = always_win.bag(message)
                        await trade_stream.addtrade(aw)
                    except Exception as e:
                        utility.failed_message(message, 'Always Win', e)

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
                            await trade_stream.addtrade(hir)
                        else:
                            raise ValueError("No Signal / Cooling Down")
                    except Exception as e:
                        utility.failed_message(message, 'Hirn', e)

            # ___________________________________________________________________________________________________

            elif chat.id == 1899129008:  # Telegram Bot
                print("Robot Section +++")
                utility.gen_log('Telegram Robot: ' + message)
                # Bot commands
                if message == STOP:

                    await asyncio.sleep(1)
                    print('Exiting....')
                    await client.disconnect()

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
                            except Exception as e:
                                utility.failed_message(message, 'Hirn', e)
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
                    msgs = await client.get_messages(1548802426, limit=10)
                    if msgs is not None:
                        print("Messages:\n---------")
                        for msg in msgs:
                            print(msg)
                            print(msg.chat_id)
                            print(msg.message)
                            print('______________________')
                            if not msg.photo:
                                await client.send_message(1576065688, msg)
                            else:
                                print('has photo')

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

                elif message == '/except':
                    raise Exception('Log this exception please')
                elif message == '/environ':
                    config = dotenv_values('.env')
                    print(config)

            else:
                recognized = False
                for i in chat_ids:
                    if i == chat.id:
                        recognized = True

                # Unrecognized Telegram Channels
                if not recognized:
                    post = msg + '\n' + message + '\n' + str(sender.id) + '|' + str(chat.id) + '\n_________________\n'
                    # log Post here

        except Exception as e:
            utility.error_log(str(e) + '\n' + str(traceback.format_exc()))

# End of event handler code ___________________________________________________________


# Telegram login and start messsage handling
async def setup_scraper():
    global stringsesh
    api_id = os.getenv('TELEGRAM_ID')
    api_hash = os.getenv('TELEGRAM_HASH')
    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)
    await StartTelegramForwarding(client)

    print("Launching Telebagger...")
    utility.gen_log('Launching Telegram Scraper...')
    await client.start()
    await client.get_dialogs()
    await asyncio.gather(trade_stream.streamer(), trade_stream.timer(), client.run_until_disconnected())


# Currently non functional, TODO: find a way to gracefully shutdown the stream when heroku calls sigterm
def handler_stop_signals(sig, frame):
    print("Am Dying lol")
    print('Aaaaaah it hurts')
    print("Make it stop")
    sys.exit()


# signal.signal(signal.SIGTERM, handler_stop_signals)  # Intializing graceful death on heroku restart
asyncio.run(setup_scraper())
print('Exiting....')

os.kill(os.getpid(), signal.SIGTERM)  # Not sure how this is going to react with heroku servers
print('Still going')
