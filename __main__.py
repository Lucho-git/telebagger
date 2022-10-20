"""Main entry point for telebagger"""
import asyncio
import os
import signal
from colorama import init
from telebagger import TelegramEvents
from trade_stream import TradeStream

async def run_multiple_tasks(telegram, trade_stream):
    '''Starts telegram scraper and trade stream loops'''
    tasks =  await asyncio.gather(telegram.setup_scraper(), trade_stream.launch_stream())
    return tasks
    
def run():
    '''Bagger'''
    init()  # Initialising colorama
    trade_stream = TradeStream()
    print('Connecting to telegram...')
    telegram = TelegramEvents(trade_stream)
    telegram.init_client()

    # New asyncio policy
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = asyncio.gather(telegram.setup_scraper(), trade_stream.launch_stream())

    loop.run_until_complete(bot)
    loop.close()
    print('Exiting....')
    os.kill(os.getpid(), signal.SIGTERM)  # Not sure how this is going to react with herok


if __name__ == '__main__':
    run()
