"""Main entry point for telebagger"""
import asyncio
import os
import signal
from colorama import init
from telebagger import TelegramEvents

def run():
    '''Bagger'''
    init()  # Initialising colorama
    print('Connecting to telegram')
    telegram = TelegramEvents()
    telegram.init_client()
    asyncio.run(telegram.setup_scraper())

    print('Exiting....')
    os.kill(os.getpid(), signal.SIGTERM)  # Not sure how this is going to react with heroku servers


if __name__ == '__main__':
    run()
