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
        #stringsesh = os.getenv('TELEGRAM_LOCALSAVE')
        stringsesh = '1BVtsOIYBu3-mW8LWNklskWf4ubCwmoTJCMtaTn1yotapoMDSnukfzWHHy0VZdOu5THq8Z8dvfLZ-3QYoqZW7sFja_0uk_ovCdQTOhdzUu72KMnSoqxntyvytcfYQyfVdt1UV7V1d4Zhxy9WlMJEl3IcEeWbCyruidkkVGs4n1cW_vh__Li3PvHfKTuJA5EeZ58KNp1LzmDC-G66T8chUqU-RKHdFt2RT6NEQL-6zJLYyq_VTMgRiv-8HtfEs2OOyI-rsVsOwHC-p7_794gPk_B14HQ02zoWne_QZNesgc2NvsvNdwr_Eqg9D883qD9xEiSHvZNNIiDJJaM6b5IMfH-NZe9022dk='
    else:
        #stringsesh = os.getenv('TELEGRAM_SERVERSAVE')
        stringsesh = '1BVtsOIYBu0ovo28ka-RmvdqJHl7RbsJJpyDOKdEjyfK3-8E5tKCiaHyPmgaTvb1zIB-irRQqHtEOSw0ZL3LAvJTCfkMTuLet_11w1Zr6iaYNc_yrWV9h8r3OPEaTcKjXeEc-Nh9DLNhwjEIJ1EIS5PCPVeoEn9nwlFqfh8dtXbGGl0U3vLcp1-0wsp7tGUw958MZkmvvgFvZyiJ-iKr7FImY_1_Li4dY3S2ex68fz4UPSukfCzPpTJBf_HGX5dDvMT9HYF5xWG2XqlqoueSHRR9x4ylhq6vnkJOtfftSmPXoO2E76Gd80b_1UIbOfQ_y0fy5lvGsMI3_UZXvqV9cVaariRrHUlE='
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
        'SIGNAL_GROUPS': ['1548802426', '1248393106'],
        'GENERAL_GROUPS': ['1576065688', '1220789766']
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