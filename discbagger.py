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
            print(message)
            print('Event Occured')
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
        client.add_listener(on_message)




    async def setup_scraper(self):
        '''Start recieving discord events'''
        await self.start_discord_handler(self.client)
        #db.gen_log('Launching Telegram Scraper...')
        print('running...')
        await self.client.start(self.key)
        print('finished discord')