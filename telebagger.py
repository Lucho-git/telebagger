# 3rd Party libraries

from telethon import events, utils
from dotenv import load_dotenv
import requests
import asyncio
import sys
import time
import os
import traceback
import config
from types import SimpleNamespace


# Local imports

from trade_stream import TradeStream
import utility
import new_signal
from config import get_telegram_config, get_commands
import database_logging as db

class TelegramEvents:
    '''Handles telegram events'''
    def __init__(self, trade_stream, clientChannel):
        self.com = config.get_commands()
        self.trade_stream = trade_stream
        self.clientChannel = clientChannel
        self.client = config.get_telegram_config()
    

    async def exit_self(self):
        '''Polls to see if should disconnect'''
        while True:
            msg = await self.clientChannel[1].get()
            if msg == 'close':
                print('Disconnecting Telebagger...')
                await self.client.disconnect()
                break

    async def generate_signal(self, event):
        '''Builds a signal from the telegram event'''
        origin = SimpleNamespace()
        signal = SimpleNamespace()
        sender_obj = await event.get_sender()
        chat = await event.get_chat()
        sender = str(chat.id)
        origin.name = utils.get_display_name(sender_obj)
        origin.id = sender
        signal.origin, signal.message, signal.timestamp = origin, event.raw_text, event.date
        return signal

    async def get_past_messages(self, channel_id):
        '''Gets past messages from a channel'''
        msgs = await self.client.get_messages(str(channel_id), limit=20)
        if msgs is not None:
            print("Messages:\n---------")
            for msg in msgs:
                print(msg)
                print(msg.chat_id)
                print(msg.signal.message)
                print('______________________')
                if not msg.photo:
                    #await self.client.send_message(1576065688, msg)
                    pass
                else:
                    print('has photo')

    async def telegram_command(self, signal):
        '''Commands which can be manually triggered through the telegram client'''
        print("Robot Section +++")
        db.gen_log('Telegram Robot: ' + signal.message)
        # Bot commands
        if signal.message == self.com.STOP:
            await self.trade_stream.close_stream()
            print('Disconnecting Telebagger...')
            await self.clientChannel[0].put('close')
            await self.client.disconnect()
        # Stream Commands
        elif signal.message == self.com.STREAM:
            await self.trade_stream.streamer()
        elif signal.message == self.com.STOPSTREAM:
            await self.trade_stream.close_stream()
        elif signal.message == '/savestream':
            self.trade_stream.save()
        elif signal.message == '/loadstream':
            await self.trade_stream.load()
        elif signal.message == self.com.RESTART:
            await self.trade_stream.restart_stream()
        elif signal.message == self.com.MENU:
            await self.trade_stream.stopstream()
        elif signal.message == self.com.HIRN_SIGNAL:
            with open('docs/hirn_example.txt', 'r', encoding='utf-8') as f:
                signal.message = f.read()
            signal.origin.id = '1248393106'
            signal.origin.name = 'Hirn'
            await new_signal.new_signal(signal, self.trade_stream)
        elif signal.message == '/hirn2':
            with open('docs/hirn_example2.txt', 'r', encoding='utf-8') as f:
                signal.message = f.read()
            signal.origin.id = '1248393106'
            signal.origin.name = 'Hirn'
            await new_signal.new_signal(signal, self.trade_stream)
        elif signal.message == '/newhirn':
            signal.origin.id = '1248393106'
            signal.origin.name = 'randomHirn'
            for m in await self.client.get_messages('https://t.me/HIRN_CRYPTO', limit=20):
                if 'Buy Price:' in m.message:
                    signal.message = m.message
                    await new_signal.new_signal(signal, self.trade_stream)
                    break

        elif signal.message == '/now':
            self.trade_stream.update_trades_now()
        elif signal.message == '/status':
            print(self.trade_stream.stream_status())
        elif signal.message == '/past':
            await self.get_past_messages('1248393106')
        elif signal.message == '/except':
            raise Exception('Log this exception please')
        elif signal.message == '/dump':
            await self.trade_stream.dump_stream()
        elif signal.message == '/smoothdump':
            await self.trade_stream.smooth_dump_stream()
        elif '/get ' in signal.message:
            try:
                data = db.get_from_realtime(signal.message.split('/get ')[1])
                for user in data.each():
                    print(f"{user.key()}: {user.val()}")
            except Exception as e:
                print(e)
        elif '/newdiscchannel ' in signal.message:
            #Format like  /newchannel guildid-channelid nameofchannel category(ignore/signal)
            channelinfo = signal.message.split(' ')
            channel_id_combo, channel_name, channel_category = channelinfo[1], channelinfo[2], channelinfo[3]
            if channel_category not in ['signal', 'ignore']:
                raise Exception('Wrong channel category, should be "signal" or "ignore"')
            db.add_discord_channel(channel_id_combo, channel_name, channel_category)
        elif '/newtelechannel ' in signal.message:
            channelinfo = signal.message.split(' ')
            channel_id, channel_name, channel_category = channelinfo[1], channelinfo[2], channelinfo[3]
            if len(channel_id) == 10:
                db.add_telegram_channel(channel_id, channel_name, channel_category)

    async def start_telegram_handler(self, client):
        '''telegram message event handler'''
        @client.on(events.NewMessage())
        async def my_event_handler(event):
            try:
                signal = await self.generate_signal(event)

                if signal.origin.id in self.com.SIGNAL_GROUP:
                    await new_signal.new_signal(signal, self.trade_stream)

                elif signal.origin.id == '5894740183' or signal.origin.id == '5935711140':
                    await self.telegram_command(signal)
                elif signal.origin.id in self.com.GENERAL_GROUP:
                    pass

                else:
                    print('new chat ID:', signal.origin.id, signal.origin.name)
                    db.gen_log('new chat ID:' + str(signal.origin.id) + signal.origin.name)
                    #Deal with unrecognized telegram channels

            except Exception as e:
                db.error_log(str(e) + '\nMessage:' + event.raw_text + '\nExcept:' + str(traceback.format_exc()))

    async def run(self):
        '''Start recieving telegram events'''
        await self.start_telegram_handler(self.client)
        db.gen_log('Launching Telegram Scraper...')
        await self.client.start()
        print('Ready...')
        await self.client.run_until_disconnected()