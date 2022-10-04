# 3rd Party libs

from telethon import TelegramClient, events, sync, utils, tl
from telethon.sessions import StringSession
from dotenv import load_dotenv
import requests
import asyncio
import sys
import time
import os
import traceback
import config
from types import SimpleNamespace


# Methods within this package
from trade_classes import Trade, Futures, MFutures
import always_win
import binance_wrap
import trade_stream
import utility
import signal_groups
import hirn
import futures_signals
from config import get_telegram_config, get_telegram_commands
import database_logging as db

class TelegramEvents():
    '''Handles telegram events'''
    def __init__(self):
        self.com = config.get_telegram_commands()

    def init_client(self):
        '''Breaks when I put this inside of init for some reason?'''
        self.client = config.get_telegram_config() # pylint: disable=W0201

    async def generate_signal(self, event):
        '''Builds a signal from the telegram event'''
        origin = SimpleNamespace()
        signal = SimpleNamespace()
        sender_obj = await event.get_sender()
        #chat = await event.get_chat()
        sender = str(sender_obj.id)
        origin.name = utils.get_display_name(sender_obj)
        origin.id = sender
        signal.origin, signal.message, signal.timestamp = origin, event.raw_text, event.date

        return signal

    async def get_past_messages(self, channel_id):
        '''Gets past messages from a channel'''
        msgs = await self.client.get_messages(channel_id, limit=10)
        if msgs is not None:
            print("Messages:\n---------")
            for msg in msgs:
                print(msg)
                print(msg.chat_id)
                print(msg.signal.message)
                print('______________________')
                if not msg.photo:
                    await self.client.send_message(1576065688, msg)
                else:
                    print('has photo')

    async def telegram_command(self, signal):
        '''Commands which can be manually triggered through the telegram client'''
        print("Robot Section +++")
        db.gen_log('Telegram Robot: ' + signal.message)
        # Bot commands
        if signal.message == self.com.STOP:
            print('Disconnecting Telebagger...')
            await self.client.disconnect()
        # Stream Commands
        elif signal.message == self.com.STREAM:
            await trade_stream.streamer()
        elif signal.message == self.com.STOPSTREAM:
            await trade_stream.close_stream()
        elif signal.message == self.com.RESTART:
            await trade_stream.restart_stream()
        elif signal.message == self.com.MENU:
            await trade_stream.stopstream()
        elif signal.message == self.com.HIRN_SIGNAL:
            with open('docs/hirn_example.txt', 'r', encoding='utf-8') as f:
                signal.message = f.read()
            signal.origin.id = '1248393106'
            signal.origin.name = 'Hirn'
            await signal_groups.new_signal(signal)
        elif signal.message == '/status':
            print(trade_stream.stream_status())
        elif signal.message == '/past':
            self.get_past_messages('1548802426')
        elif signal.message == '/except':
            raise Exception('Log this exception please')


    async def start_telegram_handler(self, client):
        '''telegram message event handler'''
        @client.on(events.NewMessage())
        async def my_event_handler(event):
            try:
                signal = await self.generate_signal(event)

                if signal.origin.id in self.com.SIGNAL_GROUPS:
                    await signal_groups.new_signal(signal)

                elif signal.origin.id == '1646848328':
                    await self.telegram_command(signal)

                else:
                    print('New Message:', signal)
                    pass
                    #db.error_log('Unrecognized channel', str(signal))
                    #Deal with unrecognized telegram channels

            except Exception as e:
                db.error_log(str(e) + '\nMessage:' + event.raw_text + '\nExcept:' + str(traceback.format_exc()))

    async def setup_scraper(self):
        '''Start recieving telegram events'''
        self.init_client()
        await self.start_telegram_handler(self.client)
        db.gen_log('Launching Telegram Scraper...')
        await self.client.start()
        await self.client.get_dialogs()
        print('Enter loop')
        await asyncio.gather(self.client.run_until_disconnected())
        #trade_stream.streamer(), trade_stream.timer()