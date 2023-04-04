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

    #communication clientChannel, so discord and telegram can exit simeltaneously
    c1 = asyncio.Queue()
    c2 = asyncio.Queue()
    clientChannel = [c1,c2]

    discbagger = DiscordEvents(trade_stream, clientChannel)
    telebagger = TelegramEvents(trade_stream, clientChannel)
    #This ensures program exits smoothly on command
    asyncio.create_task(telebagger.exit_self())
    asyncio.create_task(discbagger.exit_self())

    print('Connecting to telebagger...')
    # including trade_stream introduces a bug which stops telebagger from exiting gracefully
    await asyncio.gather(telebagger.run(), discbagger.run(), trade_stream.launch_stream())
    print('Exiting....')
if __name__ == '__main__':
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


    