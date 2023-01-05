'''Defines a user account and the user settings'''

import config
import utility
import database_logging as db
from binance.client import Client

class Trade:
    '''Defines a user'''
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.signal_preferences = [{}]
        self.binance_client = UserBinance()

    def load_binance_client(self):
        '''Loads active binance session'''
        self.binance_client.load_binance_client()






class UserBinance:
    '''Defines a users binance settings'''
    def __init__(self):
        self.porfolio_allocation = 1
        self.sell_between_btcusd = 0
        self.api_secret = None
        self.api_key = None
        self.client = None

    def add_api_keys(self, secret, key):
        '''Adds api keys to user'''
        self.api_secret = secret
        self.api_key = key


    def load_binance_client(self):
        '''loads binance client'''
        self.client = Client(self.api_key, self.api_secret)