"""Configures Various interconnected components"""
import os
import pyrebase
import pytz
from binance.client import Client
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
import munch


# Get environment variables
local = [True]
if not os.name == 'nt':
    local[0] = False
else:
    local[0] = True
local[0] = True

load_dotenv()

def get_firebase_config():
    """Init Database Connection"""
    config = {
    "apiKey": str(os.getenv("FIREBASE_API")),
    "authDomain": "telebagger.firebaseapp.com",
    "projectId": "telebagger",
    "messagingSenderId": "332905720250",
    "storageBucket": "telebagger.appspot.com",
    "appId": "1:332905720250:web:e2006e777fa8d980d61583",
    "measurementId": "G-02W82CCF85",
    "databaseURL":  "https://telebagger-default-rtdb.firebaseio.com/",
    }
    return pyrebase.initialize_app(config)

def get_timezone_config():
    """Returns consistent timezon"""
    return pytz.timezone('Australia/Perth')

def get_binance_config():
    """Gets binance client"""
    r_api_key = os.getenv('LACH_BINANCE_KEY')
    r_api_secret = os.getenv('LACH_BINANCE_SECRET')

    realclient = Client(r_api_key, r_api_secret)
    return realclient

def get_telegram_config():
    """Returns Telegram Client"""
    api_id = os.getenv('TELEGRAM_ID')
    api_hash = os.getenv('TELEGRAM_HASH')
    if local[0]:
        stringsesh = os.getenv('TELEGRAM_LOCALSAVE')
    else:
        stringsesh = os.getenv('TELEGRAM_SERVERSAVE')
    return TelegramClient(StringSession(stringsesh), api_id, api_hash)

def get_telegram_commands():
    """Returns set of telegram commands"""
    if local[0]:
        # Stream Commands Local
        commands = {
        'STOP': '/stop',
        'STREAM': '/stream',
        'STOPSTREAM': '/stopstream',
        'RESTART': '/restart',
        'MENU': '/menu',
        'ADD': '/add',
        'ADD2': '/add2',
        'ADD3': '/add3',
        'UPDATE': '/update',
        'UPDATE2': '/update2',
        'PRE_AW': '/pre_aw',
        'ALWAYS_WIN_SIGNAL': '/aw',
        'HIRN_SIGNAL': '/hirn',
        'NEW_PORTFOLIO': '/newport',
        'CLEAR_PORTFOLIOS': '/clear_folios',
        'DISPLAY_PORTFOLIOS': '/display_folios',
        'SNAPSHOT': '/snapshot',
        'CLOSE_FUTURES': '/close_futures',
        'SIGNAL_GROUPS': ['1548802426', '1248393106']
        }
    else:
        # Stream Commands Heroku Hosted
        commands = {
        'STOP': '/stop!',
        'STREAM': '/stream!',
        'STOPSTREAM': '/stopstream!',
        'RESTART': '/restart!',
        'MENU': '/menu!',
        'ADD': '/add!',
        'ADD2': '/add2!',
        'ADD3': '/add3!',
        'UPDATE': '/update!',
        'UPDATE2': '/update2!',
        'PRE_AW': '/pre_aw!',
        'ALWAYS_WIN_SIGNAL': '/aw!',
        'HIRN_SIGNAL': '/hirn!',
        'NEW_PORTFOLIO': '/newport!',
        'CLEAR_PORTFOLIOS': '/clear_folios!',
        'DISPLAY_PORTFOLIOS': '/display_folios!',
        'SNAPSHOT': '/snapshot!',
        'CLOSE_FUTURES': '/close_futures!'
        }
    return munch.munchify(commands)

def get_storage_paths():
    """Returns filepaths"""
    UNIQUE_ID = 'heroku/' 

    if local[0]:
        # Firebase Cloud Storage File Paths
        file_paths = {
        "ADD_MESSAGE": "trade_results/message_count/",
        "SAVE": "save_data/",
        "STREAM": 'savefile',
        "SAVE_TRADE": "trade_results/",
        "LIVE_VIEW": "live_view/",
        "LOG": 'logs/',
        "REALTIME_SAVE": 'signals/'
        }
    else:
        # Heroku Version
        file_paths = {
        "ADD_MESSAGE": UNIQUE_ID + "trade_results/message_count/",
        "SAVE": UNIQUE_ID + "save_data/",
        "STREAM": UNIQUE_ID + 'savefile',
        "SAVE_TRADE": UNIQUE_ID + "trade_results/",
        "LIVE_VIEW": UNIQUE_ID + "live_view/",
        "LOG": UNIQUE_ID + 'logs/',
        "REALTIME_SAVE": UNIQUE_ID + 'signals/'
        }
    return munch.munchify(file_paths)