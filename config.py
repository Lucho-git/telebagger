"""Configures Various interconnected components"""
import os
import pyrebase
import pytz
from binance.client import Client
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
import munch
import discord
from discord.ext import commands

# Get environment variables
local = [True]
if os.name == 'nt':
    local[0] = True
    print('Windows Detected...')
else:
    # code is reachable, vscode lying
    local[0] = False
    print('Linux Detected...')

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
        stringsesh = '1BVtsOMQBuyhIoQWYzzU2C-IyIo0X2VTfU4lUdUxZh06BWVCHo9vpxyZuRqyFVS-dmQ2qF48TJKZZBWjHEqnx6E9VVSRxruaqVoeeLWWlFgAR4Vqij25d65tbdI5rKdJzEDkDfz2z5u11WwgAjFnOmdrQLgg4qFnOj8AlJxQyEqxZ3DRgJKy5uMg8nKg_BZx8uvNhAD-PI2NDMS96YJWSSt5LTS63v5GmBDOFq551Tf0zbmUaINqmwVQdHbPel7hTJahlP3UcuGD3ij0o96mu6kwk0bhFgg7QpD8LPJYVNMFFMGiDS7jHnF_2_wrpV_bHJY7Mn-J8qZuYJpm4__cYIk4yBFW_lTg='
    else:
        #stringsesh = os.getenv('TELEGRAM_SERVERSAVE')
        stringsesh = '1BVtsOLsBu0NPznbcJmwVPJcAOaKZsQbaYMV79eL7fX-xPQeBR_KCtgNMRY1pBJimEcZGRPOoyBh7W_9ewyxdhoO2bxMJiJNsup0KLc7OyuoxP6sy_bVnFEQYtmafplDGnWfiWwKggzhZdnYRKD8VVB8KRmjzti4-2CGVplf8xLyhnlWvRZWbIE8S7yNUgcpll7Xi48KGw0gNbBLgUDrMd5jIj2ERGt8fecbO79RzNTqzLsnzyLB_aHjUdHB6Mj1Per2pmITweBkMHcAE5bvrBT_YBerGvReCz7hG3AC72kXo1l9p7zenPf-ZGzcLC_ip2Xl9yEFNBvECC_ZLFyy-6Nl6zzWE2Io='
    return TelegramClient(StringSession(stringsesh), api_id, api_hash)

def get_discord_config():
    """Returns Discord Client"""
    SELF_TOKEN = os.getenv('DISCORD_TOKEN')
    
    bot = commands.Bot(command_prefix='>', self_bot=True)
    return [bot, SELF_TOKEN]

def get_commands():
    """Returns set of telegram commands"""
    if local[0]:
        # Stream Commands Local
        chat_commands = {
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
        'RAND_HIRN_SIGNAL': '/new_hirn',
        'UPDATE_NOW': '/now',
        'STATUS': '/status',
        'PAST': '/past',
        'EXCEPT': '/except',
        'DUMP': '/dump',
        'SMOOTH_DUMP': '/smooth_dump',
        'NEW_PORTFOLIO': '/newport',
        'CLEAR_PORTFOLIO': '/clear_folio',
        'DISPLAY_PORTFOLIO': '/display_folio',
        'SNAPSHOT': '/snapshot',
        'CLOSE_FUTURE': '/close_future',
        'SIGNAL_GROUP': ['1548802426', '1248393106'],
        'GENERAL_GROUP': ['1576065688', '1220789766', '1798277168']
        }
    else:
        # Stream Commands Heroku Hosted
        chat_commands = {
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
        'RAND_HIRN_SIGNAL': '/new_hirn!',
        'UPDATE_NOW': '/now!',
        'STATUS': '/status!',
        'PAST': '/past!',
        'EXCEPT': '/except!',
        'DUMP': '/dump!',
        'SMOOTH_DUMP': '/smooth_dump!',
        'NEW_PORTFOLIO': '/newport!',
        'CLEAR_PORTFOLIO': '/clear_folio!',
        'DISPLAY_PORTFOLIO': '/display_folio!',
        'SNAPSHOT': '/snapshot!',
        'CLOSE_FUTURE': '/close_future!',
        'SIGNAL_GROUP': ['1548802426', '1248393106'],
        'GENERAL_GROUP': ['1576065688', '1220789766']
        }
    return munch.munchify(chat_commands)

def get_storage_paths():
    """Returns filepaths"""
    UNIQUE_ID = 'heroku/'

    if local[0]:
        # Firebase Cloud Storage File Paths
        file_paths = {
        "ADD_MESSAGE": "trade_result/message_count/",
        "SAVE": "save_data/savefile",
        "SAVE_TRADE": "trade_result/",
        "LIVE_VIEW": "live_view/",
        "LOG": 'log/',
        "REALTIME_SAVE": 'signal/',
        "DISCORD_CHANNEL": 'discord_channel/',
        "TELEGRAM_CHANNEL": 'telegram_channel/',
        "SIGNAL_ENDPOINT_URL": 'https://luchodore.pythonanywhere.com/test_data'
        }
    else:
        # Heroku Version
        file_paths = {
        "ADD_MESSAGE": UNIQUE_ID + "trade_results/message_count/",
        "SAVE": UNIQUE_ID + "save_data/savefile",
        "SAVE_TRADE": UNIQUE_ID + "trade_results/",
        "LIVE_VIEW": UNIQUE_ID + "live_view/",
        "LOG": UNIQUE_ID + 'logs/',
        "REALTIME_SAVE": UNIQUE_ID + 'signals/',
        "DISCORD_CHANNEL": UNIQUE_ID + 'discord_channels/',
        "TELEGRAM_CHANNEL": UNIQUE_ID + 'telegram_channels/',
        "SIGNAL_ENDPOINT_URL": 'https://luchodore.pythonanywhere.com/save_data'
        }
    return munch.munchify(file_paths)