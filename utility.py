import pyrebase
import pickle
import numpy as np
import asyncio as aio
import re
import os.path
import pytz
from binance.client import Client
from datetime import datetime

from fake_portfolio import Folio, Folios

local = [False]

config = {  # initialising database connection
    "apiKey": "AIzaSyDl_eUsJkNxN5yW9KS6X0n0tkQFruV8Tbs",
    "authDomain": "telebagger.firebaseapp.com",
    "projectId": "telebagger",
    "messagingSenderId": "332905720250",
    "storageBucket": "telebagger.appspot.com",
    "appId": "1:332905720250:web:e2006e777fa8d980d61583",
    "measurementId": "G-02W82CCF85",
    "databaseURL":  "https://telebagger-default-rtdb.firebaseio.com/"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
unique_id = 'heroku/'  # heroku, lach, tom, cozza


FAILED_MESSAGES_L = 'trade_results/failed_messages/'
ADD_MESSAGE_L = 'trade_results/message_count/'
SAVE_STREAM_L = 'save_data/savefile'
SAVE_FOLIO_L = "save_data/savefolios"
SAVE_TRADE_L = "trade_results/"
RESULTS_L = "trade_results/juice/"
LOG_L = 'logs/'

if local[0]:
    # Firebase Cloud Storage File Paths
    FAILED_MESSAGES = "trade_results/failed_messages/"  # Filepath
    ADD_MESSAGE = "trade_results/message_count/"  # Filepath
    SAVE_STREAM = "save_data/savefile"  # Path and file
    SAVE_FOLIO = "save_data/savefolios"  # Path and file
    SAVE_TRADE = "trade_results/"  # Path
    RESULTS = "trade_results/juice/"  # Path
    LOG = 'logs/'
else:
    # Heroku Version
    FAILED_MESSAGES = unique_id + "trade_results/failed_messages/"  # Filepath
    ADD_MESSAGE = unique_id + "trade_results/message_count/"  # Filepath
    SAVE_STREAM = unique_id + "save_data/savefile"  # Path and file
    SAVE_FOLIO = unique_id + "save_data/savefolios"  # Path and file
    SAVE_TRADE = unique_id + "trade_results/"  # Path
    RESULTS = unique_id + "trade_results/juice/"  # Path
    LOG = unique_id + 'logs/'


def get_binance_client():
    # Binance API Keys, TODO: Switch these to environmental variables if this code ever goes public

    # Lachs Binance Acc
    r_api_key = 'GAOURZ9dgm3BbjmGx1KfLNCS6jicVOOQzmZRJabF9KMdhfp24XzdjweiDqAJ4Lad'  # Put your own api keys here
    r_api_secret = 'gAo0viDK8jwaTXVxlcpjjW9DNoxg4unLC0mSUSHQT0ZamLm47XJUuXASyGi3Q032'

    # Ellas Binance Acc
    r_api_key = 'lQaHpUmEKPEDpquVPpF9WkKfiUNGl6jf6XGTQ6K6KSOOZaa70xN9qbUK3A5Q10DX'
    r_api_secret = 'gxLJI8vbMonUHkIDHIBRnQkDrkEKXPz0xOdHHNDYGRSelwqJTjytt2REDKY1zxyG'

    # Dads Binance Acc
    r_api_key = 'hWQABbUYYwhonkS6FN8LtCr7QRhtAsj1IwbpbuXWGhbdHn9nRbVe5tZDzyMQrfsp'
    r_api_secret = 'G9HH87QyzZtjmUUjfAxsQQJkcDLOwGRCiL3oyL85p7IoBeKD68JMwjPxmBl3Fm6K'

    # Binance Client Object
    realclient = Client(r_api_key, r_api_secret)
    return realclient


def is_local():
    return local[0]


def failed_message(msg, origin, e, file_string):
    path_on_cloud = FAILED_MESSAGES + origin + file_string
    path_on_local = FAILED_MESSAGES_L + origin + '_failed.txt'
    storage.child(path_on_cloud).download("./", path_on_local)
    e = str(e)

    try:
        with open(path_on_local, 'a', encoding="utf8") as f:
            f.write(msg + '\n')
            f.write('__________________________\n')
            f.write(e)
            f.write('\n\n')
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as ex:
        ex = str(ex)
        print(ex)
        print("No Previous File existed I think")
        with open(path_on_local, 'w+', encoding="utf8") as f:
            f.write('Failed ' + origin + ' Messages:\n')
            f.write('==========================\n')
            f.write(msg + '\n')
            f.write('__________________________\n')
            f.write(ex)
            f.write('\n\n')
        storage.child(path_on_cloud).put(path_on_local)
        print("Made new file for ", origin)


def add_message(origin, result):
    path_on_cloud = ADD_MESSAGE + origin + '_count.txt'
    path_on_local = ADD_MESSAGE_L + origin + '_count.txt'
    storage.child(path_on_cloud).download("./", path_on_local)
    try:
        with open(path_on_local, 'a', encoding="utf8") as f:
            f.write(result + '\n')
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as e:
        print(e)
        print("New count file?")
        with open(path_on_local, 'w+', encoding="utf8") as f:
            f.write(origin + 'Signal Count    [-] is Fail  ||  [X] is Success \n')
            f.write('==========================\n')
            f.write(result + '\n')
        storage.child(path_on_cloud).put(path_on_local)


def gen_log(log):
    tz = pytz.timezone('Australia/Perth')
    now = datetime.now(tz)
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')
    path_on_cloud = LOG + 'general_logs/' + date_formatted + '.txt'
    path_on_local = LOG_L + 'general_logs/' + date_formatted + '.txt'
    try:
        storage.child(path_on_cloud).download("./", path_on_local)
        if os.path.exists(path_on_local):
            with open(path_on_local, 'a', encoding="utf8") as f:
                f.write(time_formatted + '| ' + log + '\n')
            storage.child(path_on_cloud).put(path_on_local)
        else:
            with open(path_on_local, 'w+', encoding="utf8") as f:
                f.write('Daily General Logs ' + date_formatted + '\n\n')
                f.write(time_formatted + '| ' + log + '\n')

            storage.child(path_on_cloud).put(path_on_local)
    except Exception as e:
        print('logging Exception: ', e)
        error_log(e)


def error_log(error):
    now = datetime.now()
    date_time_formatted = now.strftime('%d:%m:%Y: %H:%M:%S:')
    path_on_cloud = LOG + 'exceptions' + '.txt'
    path_on_local = LOG_L + 'exceptions' + '.txt'
    try:
        with open(path_on_local, 'a', encoding="utf8") as f:
            f.write(date_time_formatted + '| ' + error + '\n')
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as e:
        print('Exception in exceptor :(')
        print(str(e))


def pickle_save(obj, cloudpath, localpath):
    path_on_cloud = cloudpath
    path_on_local = localpath
    storage.child(path_on_cloud).download("./", path_on_local)
    try:
        with open(path_on_local, 'wb') as stream_save_file:
            pickle.dump(obj, stream_save_file)
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as e:
        print(str(e))
        print("Unexpected Picklesave Error")


def pickle_load(cloudpath, localpath):
    path_on_cloud = cloudpath
    path_on_local = localpath
    ret_obj = None
    storage.child(path_on_cloud).download("./", path_on_local)
    try:
        with open(path_on_local, 'rb') as config_dictionary_file:
            ret_obj = pickle.load(config_dictionary_file)
    except Exception as e:
        print('No Save File')
        print(str(e))
    return ret_obj


def save_stream(restartstream):
    path_on_cloud = SAVE_STREAM
    path_on_local = SAVE_STREAM_L
    pickle_save(restartstream, path_on_cloud, path_on_local)


def load_stream():
    path_on_cloud = SAVE_STREAM
    path_on_local = SAVE_STREAM_L
    loaded = pickle_load(path_on_cloud, path_on_local)
    return loaded


def save_folio(folios):
    path_on_cloud = SAVE_FOLIO
    path_on_local = SAVE_FOLIO_L
    pickle_save(folios, path_on_cloud, path_on_local)


def load_folio():
    path_on_cloud = SAVE_FOLIO
    path_on_local = SAVE_FOLIO_L
    folio = pickle_load(path_on_cloud, path_on_local)
    if not folio:
        folio = None
    return folio


def start_trade_folios(trade, percent):
    folio = load_folio()
    changes = folio.start_trade(trade, percent)
    if changes:
        print('Saving')
        save_folio(folio)
        print('saved')


def end_trade_folios(trade, trade_return):
    load_folio()
    folio = load_folio()
    changes = folio.end_trade(trade, trade_return)
    if changes:
        save_folio(folio)


def save_trade(t):
    # Add trade result to all trades textfile
    path_on_cloud = SAVE_TRADE + 'TradeResults.txt'
    path_on_local = SAVE_TRADE_L + 'TradeResults.txt'
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, 'a', encoding="utf8") as f:
        f.write(str(t.savestring))
        f.write('\n\n')
    storage.child(path_on_cloud).put(path_on_local)
    # Add trade result to specific trade textfile
    path_on_cloud = SAVE_TRADE + t.origin + ".txt"
    path_on_local = SAVE_TRADE_L + t.origin + ".txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, 'a', encoding="utf8") as f:
        f.write(str(t.savestring))
        f.write(t.trade_log)
        f.write('_________________________________\n\n')
    storage.child(path_on_cloud).put(path_on_local)


def trade_results(t):
    for b in t.bag_id:
        path_on_cloud = RESULTS + b + '.txt'
        path_on_local = RESULTS_L + b + '.txt'
        if t.closed_diff:
            storage.child(path_on_cloud).download("./", path_on_local)

            tradevalue = float(t.closed_diff)/100 + 1
            tradevalue = round(tradevalue, 2)
            with open(path_on_local, 'a') as f:
                f.write(str(tradevalue))
                f.write('\n')
            storage.child(path_on_cloud).put(path_on_local)

    if t.bag_id:
        end_trade_folios(t, tradevalue)


def get_binance_spot_list():
    path_on_cloud = "docs/binance_spot.txt"
    path_on_local = "docs/binance_spot.txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, "r") as file:
        return file.read().split('\n')


def get_binance_futures_list():
    path_on_cloud = "docs/binance_future.txt"
    path_on_local = "docs/binance_future.txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, "r") as file:
        return file.read().split('\n')


def format_float(num):
    return np.format_float_positional(num, trim='-')


def strip_ansi_codes(s):
    return re.sub('\033\\[([0-9]+)(;[0-9]+)*m', '', s)


# Converts a Binance server timestamp into a local timestamp in milliseconds
def binance_timestamp_local(timestamp):
    dt = float(timestamp / 1000)
    utctime = datetime.utcfromtimestamp(dt)
    timedelta = 60 * 60 * 8  # + 8 Hours from UTC
    timestamp = datetime.timestamp(utctime) + timedelta
    return timestamp * 1000


class Sleeper:
    # Group sleep calls allowing instant cancellation of all
    def __init__(self, loop):
        self.loop = loop
        self.tasks = set()

    async def sleep(self, delay, result=None):
        coro = aio.sleep(delay, result=result, loop=self.loop)
        task = aio.ensure_future(coro)
        self.tasks.add(task)
        try:
            return await task
        except aio.CancelledError:
            return result
        finally:
            self.tasks.remove(task)

    def cancel_all_helper(self):
        # Cancel all pending sleep tasks
        cancelled = set()
        for task in self.tasks:
            if task.cancel():
                cancelled.add(task)
        return cancelled

    async def cancel_all(self):
        # Coroutine cancelling tasks
        cancelled = self.cancel_all_helper()
        await aio.wait(self.tasks)
        self.tasks -= cancelled
        return len(cancelled)



