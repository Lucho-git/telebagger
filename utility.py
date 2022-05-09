import pyrebase
import pickle
import numpy as np
import asyncio as aio
import re
import os
import pytz
from binance.client import Client
from datetime import datetime

from fake_portfolio import Folio, Folios

local = [False]

# Set operating timezone
tz = pytz.timezone('Australia/Perth')

config = {  # initialising database connection
    "apiKey": "AIzaSyDl_eUsJkNxN5yW9KS6X0n0tkQFruV8Tbs",
    "authDomain": "telebagger.firebaseapp.com",
    "projectId": "telebagger",
    "messagingSenderId": "332905720250",
    "storageBucket": "telebagger.appspot.com",
    "appId": "1:332905720250:web:e2006e777fa8d980d61583",
    "measurementId": "G-02W82CCF85",
    "databaseURL":  "https://telebagger-default-rtdb.firebaseio.com/",
    "serviceAccount": "docs/db_admin.json",
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()


unique_id = 'heroku/'  # heroku, lach, tom, cozza


ADD_MESSAGE_L = 'trade_results/message_count/'
SAVE_L = 'save_data/'
STREAM_L = 'savefile'
FOLIO_L = 'savefolios'
SAVE_TRADE_L = "trade_results/"
RESULTS_L = "trade_results/juice/"
LOG_L = 'logs/'

if local[0]:
    # Firebase Cloud Storage File Paths
    ADD_MESSAGE = "trade_results/message_count/"  # Filepath
    SAVE = "save_data/"  # Path
    STREAM = 'savefile'
    FOLIO = 'savefolios'
    SAVE_TRADE = "trade_results/"  # Path
    RESULTS = "trade_results/juice/"  # Path
    LOG = 'logs/'
else:
    # Heroku Version
    ADD_MESSAGE = unique_id + "trade_results/message_count/"  # Filepath
    SAVE = unique_id + "save_data/"  # Path
    STREAM = 'savefile'
    FOLIO = 'savefolios'
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


def failed_message(msg, origin, e):
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    path_on_cloud = SAVE_TRADE + origin + '/failed/' + month_year + '.txt'
    d_path_on_local = SAVE_TRADE_L + origin + '/failed/'
    f_path_on_local = d_path_on_local + month_year + '.txt'

    if os.path.exists(d_path_on_local):
        storage.child(path_on_cloud).download("./", f_path_on_local)
        with open(f_path_on_local, 'a', encoding="utf8") as f:
            f.write(msg + '\n')
            f.write('__________________________\n')
            f.write(str(e))
            f.write('\n\n')
        storage.child(path_on_cloud).put(f_path_on_local)
    else:
        os.makedirs(d_path_on_local)
        failed_message(msg, origin, e)


def gen_log(log):
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')
    path_on_cloud = LOG + 'general_logs/' + month_year + '/' + date_formatted + '.txt'
    d_path_on_local = LOG_L + 'general_logs/' + month_year + '/'
    f_path_on_local = d_path_on_local + date_formatted + '.txt'

    log = log.replace('\n', str('\n'+time_formatted+'| '))

    # Access and update cloud logs
    if os.path.exists(d_path_on_local):
        storage.child(path_on_cloud).download("./", f_path_on_local)
        if os.path.exists(f_path_on_local):
            with open(f_path_on_local, 'a', encoding="utf8") as f:
                f.write(time_formatted + '| ' + log + '\n\n')
            storage.child(path_on_cloud).put(f_path_on_local)
        else:
            with open(f_path_on_local, 'w+', encoding="utf8") as f:
                f.write('Daily General Logs ' + date_formatted + '\n\n')
                f.write(time_formatted + '| ' + log + '\n\n')
            storage.child(path_on_cloud).put(f_path_on_local)
    else:
        os.makedirs(d_path_on_local)
        gen_log(log)


def error_log(error):
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')

    path_on_cloud = LOG + 'exceptions/' + month_year + '/' + date_formatted + '.txt'
    d_path_on_local = LOG_L + 'exceptions/' + month_year + '/'
    f_path_on_local = d_path_on_local + date_formatted + '.txt'
    try:
        if os.path.exists(d_path_on_local):
            print(str(error))
            storage.child(path_on_cloud).download("./", f_path_on_local)
            with open(f_path_on_local, 'a', encoding="utf8") as f:
                f.write(time_formatted + '| ' + str(error) + '\n\n')
            storage.child(path_on_cloud).put(f_path_on_local)
        else:
            os.makedirs(d_path_on_local)
            error_log(error)
    except Exception as e:
        print('Exception in exceptor :(')
        print(str(e))


def pickle_save(obj, cloudpath, localpath):
    path_on_cloud = SAVE + cloudpath
    path_on_local = SAVE + localpath

    if os.path.exists(SAVE):
        storage.child(path_on_cloud).download("./", path_on_local)
        try:
            with open(path_on_local, 'wb') as stream_save_file:
                pickle.dump(obj, stream_save_file)
            storage.child(path_on_cloud).put(path_on_local)
        except Exception as e:
            print(str(e))
            print("Unexpected Picklesave Error")
    else:
        os.makedirs(SAVE)
        pickle_save(obj, cloudpath, localpath)


def pickle_load(path_on_cloud, path_on_local):
    ret_obj = None
    if os.path.exists(SAVE):
        storage.child(path_on_cloud).download("./", path_on_local)
        try:
            with open(path_on_local, 'rb') as config_dictionary_file:
                ret_obj = pickle.load(config_dictionary_file)
        except FileNotFoundError as e:
            print(str(e))
    else:
        os.makedirs(SAVE)
        pickle_load(path_on_cloud, path_on_local)
    return ret_obj


def save_stream(restartstream):
    path_on_cloud = STREAM
    path_on_local = STREAM
    pickle_save(restartstream, path_on_cloud, path_on_local)


def load_stream():
    path_on_cloud = SAVE + STREAM
    path_on_local = SAVE + STREAM
    loaded = pickle_load(path_on_cloud, path_on_local)
    return loaded


def save_folio(folios):
    path_on_cloud = SAVE + FOLIO
    path_on_local = SAVE + FOLIO_L
    pickle_save(folios, path_on_cloud, path_on_local)


def load_folio():
    path_on_cloud = SAVE + FOLIO
    path_on_local = SAVE + FOLIO_L
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
    now = datetime.now(tz)
    date_string = now.strftime('%B-%Y')
    day_string = now.strftime("%d/%B/%Y")

    m_path_on_cloud = SAVE_TRADE + t.origin + '/' + date_string + '.txt'
    j_path_on_cloud = SAVE_TRADE + t.origin + '/' + 'juice/' + date_string + '.txt'
    gj_path_on_cloud = SAVE_TRADE + t.origin + '/' + 'juice/' + 'last30.txt'

    dm_path_on_local = SAVE_TRADE_L + t.origin + '/'
    dj_path_on_local = dm_path_on_local + 'juice/'
    m_path_on_local = dm_path_on_local + date_string + '.txt'
    j_path_on_local = dj_path_on_local + date_string + '.txt'
    gj_path_on_local = dj_path_on_local + 'last30.txt'

    # Check file structure exists, if not create it
    if os.path.exists(dj_path_on_local):

        # Store in monthly trade group breakdown
        storage.child(m_path_on_cloud).download("./", m_path_on_local)
        with open(m_path_on_local, 'a', encoding="utf8") as f:
            f.write(str(t.savestring))
            f.write(t.trade_log)
            f.write('_________________________________\n\n')
        storage.child(m_path_on_cloud).put(m_path_on_local)

        # Store the essential trading metric overview
        storage.child(j_path_on_cloud).download("./", j_path_on_local)
        with open(j_path_on_local, 'a', encoding="utf8") as f:
            tradevalue = float(t.closed_diff)/100 + 1
            tradevalue = round(tradevalue, 2)
            f.write(str(tradevalue) + ' | ' + t.pair + ' | ' + str(t.duration) + ' Hours\n')
        storage.child(j_path_on_cloud).put(j_path_on_local)

        storage.child(gj_path_on_cloud).download("./", gj_path_on_local)
        tradevalue = float(t.closed_diff)/100
        tradevalue = round(tradevalue, 2)
        data = str(tradevalue) + ',' + day_string
        # Pushing Data to database
        db_data = {"TradeValue:": str(tradevalue), "DateFinished": day_string}
        database.push(db_data)

        contents = []
        try:
            with open(gj_path_on_local, 'r') as f:
                contents = f.readlines()
        except (FileNotFoundError, IOError):
            print('New File')

        if len(contents) > 29:
            del contents[29]
        contents.insert(0, data + '\n')

        with open(gj_path_on_local, 'w+')as f:
            for c in contents:
                if c != '\n' and c:
                    f.write(c)
        storage.child(gj_path_on_cloud).put(gj_path_on_local)
        realtime_save_trade(tradevalue-1, t, now)

    else:
        os.makedirs(dj_path_on_local)
        save_trade(t)


def realtime_save_trade(tradevalue, t, now):
    date_string = now.strftime('%B-%Y')
    day_string = now.strftime("%d-%B")

    signal_group = t.origin
    newvalue = [tradevalue, day_string]

    last7 = database.child('signals/' + signal_group + '/Last-7').get()
    last30 = database.child('signals/' + signal_group + '/Last-30').get()
    monthly = database.child('signals/' + signal_group + '/Month/' + date_string).get()
    last7 = last7.val()['values']
    last30 = last30.val()['values']
    monthly = monthly.val()['values']

    if len(last7) > 6:
        del last7[0]
    last7.append(newvalue)

    if len(last30) > 29:
        del last30[0]
    last30.append(newvalue)
    monthly.append(newvalue)
    data7 = {"label": signal_group + " Signals Last-7", "values": last7, "info": {'TradePair': t.pair, 'Duration(hrs)': str(t.duration)}}
    data30 = {"label": signal_group + " Signals Last-30", "values": last30, "info": {'TradePair': t.pair, 'Duration(hrs)': str(t.duration)}}
    monthly = {"label": signal_group + ' ' + date_string, "values": monthly, "info": {'TradePair': t.pair, 'Duration(hrs)': str(t.duration)}}

    database.child('signals/' + signal_group + '/Last-7').set(data7)
    database.child('signals/' + signal_group + '/Last-30').set(data30)
    database.child('signals/' + signal_group + '/Month/' + date_string).set(monthly)


'''
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
'''


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
    return int(timestamp * 1000)



