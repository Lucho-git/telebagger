"""Main entry point for telebagger"""
import asyncio
import os
import signal
import nest_asyncio
from colorama import init
from telebagger import TelegramEvents
from discbagger import DiscordEvents
from trade_stream import TradeStream
nest_asyncio.apply()

async def run_multiple_tasks(telegram, trade_stream):
    '''Starts telegram scraper and trade stream loops'''
    tasks =  await asyncio.gather(telegram.setup_scraper(), trade_stream.launch_stream())
    return tasks
    
async def main():
    '''Bagger'''
    init()  # Initialising colorama
    trade_stream = TradeStream() # Init trade stream
    discbagger = DiscordEvents(trade_stream)
    telebagger = TelegramEvents(trade_stream)
    print('Connecting to telebagger...')

    await asyncio.gather(telebagger.setup_scraper(), discbagger.setup_scraper())
    print('Exiting....')

if __name__ == '__main__':
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())