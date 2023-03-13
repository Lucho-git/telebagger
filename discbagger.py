from dotenv import load_dotenv
import config
from types import SimpleNamespace

from trade_stream import TradeStream
import utility
import new_signal
from config import get_telegram_config, get_commands
import database_logging as db
import os
import discord
from discord.ext import commands


class DiscordEvents:
    '''Handles discord events'''
    def __init__(self, trade_stream):
        self.com = config.get_commands()
        self.trade_stream = trade_stream
        self.client, self.key = config.get_discord_config()

    async def start_discord_handler(self, client):
        '''discord message event handler'''
        @client.command()
        async def ping(ctx):
            print('Sending Ping')
            await ctx.send('pong')
        
        @client.event
        async def on_message(message):
            print('Discord Message')
            print(message)
            print(message.content)
            if message.channel.id == 1064541939640324137:
                print('Discord Robot++')
                await self.telegram_command(message)

            if message.author == client.user:
                return
        # async def my_event_handler(event):
        #     try:
        #         signal = await self.generate_signal(event)

        #         if signal.origin.id in self.com.SIGNAL_GROUPS:
        #             await new_signal.new_signal(signal, self.trade_stream)

        #         elif signal.origin.id == '5963551324' or signal.origin.id == '5935711140':
        #             await self.telegram_command(signal)
        #         elif signal.origin.id in self.com.GENERAL_GROUPS:
        #             pass

        #         else:
        #             print('new chat ID:', signal.origin.id, signal.origin.name)
        #             db.gen_log('new chat ID:' + str(signal.origin.id) + signal.origin.name)
        #             #Deal with unrecognized telegram channels

        #     except Exception as e:
        #         db.error_log(str(e) + '\nMessage:' + event.raw_text + '\nExcept:' + str(traceback.format_exc()))


    async def telegram_command(self, signal):
        '''Commands which can be manually triggered through the telegram client'''
        print("Disc Robot Section +++")
        #db.gen_log('Telegram Robot: ' + signal.message)
        # Bot commands
        print('S:',signal.content)

        if signal.content == self.com.STOP:
            await self.trade_stream.close_stream()
            print('Disconnecting Discbagger...')
            await self.client.close()
        # Stream Commands
        # elif signal.message == self.com.STREAM:
        #     await self.trade_stream.streamer()
        # elif signal.message == self.com.STOPSTREAM:
        #     await self.trade_stream.close_stream()
        # elif signal.message == '/savestream':
        #     self.trade_stream.save()
        # elif signal.message == '/loadstream':
        #     await self.trade_stream.load()
        # elif signal.message == self.com.RESTART:
        #     await self.trade_stream.restart_stream()
        # elif signal.message == self.com.MENU:
        #     await self.trade_stream.stopstream()
        # elif signal.message == self.com.HIRN_SIGNAL:
        #     with open('docs/hirn_example.txt', 'r', encoding='utf-8') as f:
        #         signal.message = f.read()
        #     signal.origin.id = '1248393106'
        #     signal.origin.name = 'Hirn'
        #     await new_signal.new_signal(signal, self.trade_stream)
        # elif signal.message == '/hirn2':
        #     with open('docs/hirn_example2.txt', 'r', encoding='utf-8') as f:
        #         signal.message = f.read()
        #     signal.origin.id = '1248393106'
        #     signal.origin.name = 'Hirn'
        #     await new_signal.new_signal(signal, self.trade_stream)
        # elif signal.message == '/newhirn':
        #     signal.origin.id = '1248393106'
        #     signal.origin.name = 'randomHirn'
        #     for m in await self.client.get_messages('https://t.me/HIRN_CRYPTO', limit=20):
        #         if 'Buy Price:' in m.message:
        #             signal.message = m.message
        #             await new_signal.new_signal(signal, self.trade_stream)
        #             break

        # elif signal.message == '/now':
        #     self.trade_stream.update_trades_now()
        # elif signal.message == '/status':
        #     print(self.trade_stream.stream_status())
        # elif signal.message == '/past':
        #     await self.get_past_messages('1248393106')
        # elif signal.message == '/except':
        #     raise Exception('Log this exception please')
        # elif signal.message == '/dump':
        #     await self.trade_stream.dump_stream()
        # elif signal.message == '/smoothdump':
        #     await self.trade_stream.smooth_dump_stream()



    async def setup_scraper(self):
        '''Start recieving discord events'''
        await self.start_discord_handler(self.client)
        #db.gen_log('Launching Telegram Scraper...')
        print('running...')
        await self.client.start(self.key)
        print('finished discord')