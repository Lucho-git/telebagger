"""Module interacts with the database, for saving and loading various data/logs"""
from datetime import datetime
import os
import pickle
import pytz

from config import get_firebase_config, get_storage_paths

paths = get_storage_paths()
firebase = get_firebase_config()
storage = firebase.storage()
database = firebase.database()
tz = pytz.timezone('Australia/Perth')

def realtime_save_trade(tradevalue, trade, now):
    '''Saves trade information to be displayed on website'''
    date_string = now.strftime('%B-%Y')
    day_string = now.strftime("%d-%B")

    signal_group = trade.origin
    newvalue = [tradevalue, day_string, {'Tradepair': trade.pair, 'Duration(Hrs)': str(trade.duration)}]

    last7 = database.child(paths.REALTIME_SAVE + signal_group + '/Last-7').get()
    last30 = database.child(paths.REALTIME_SAVE + signal_group + '/Last-30').get()
    monthly = database.child(paths.REALTIME_SAVE + signal_group + '/Month/' + date_string).get()

    if last7.val():
        last7 = last7.val()['values']
    else:
        last7 = []
    if last30.val():
        last30 = last30.val()['values']
    else:
        last30 = []
    if monthly.val():
        monthly = monthly.val()['values']
    else:
        monthly = []

    last7.insert(0,newvalue)
    last30.insert(0,newvalue)
    monthly.append(newvalue)
    if len(last7) > 6:
        del last7[7]

    if len(last30) > 29:
        del last30[30]
    data7 = {"label": "Last-7", "values": last7}
    data30 = {"label": "Last-30", "values": last30}
    monthly = {"label": date_string, "values": monthly}

    database.child(paths.REALTIME_SAVE + signal_group + '/Last-7').set(data7)
    database.child(paths.REALTIME_SAVE + signal_group + '/Last-30').set(data30)
    database.child(paths.REALTIME_SAVE + signal_group + '/Month/' + date_string).set(monthly)



def save_trade(trade):
    '''Saves trades to database'''
    now = datetime.now(tz)
    date_string = now.strftime('%B-%Y')

    m_path_on_cloud = paths.SAVE_TRADE + trade.signal.origin.name + '/' + date_string + '.txt'
    j_path_on_cloud = paths.SAVE_TRADE + trade.signal.origin.name + '/' + 'juice/' + date_string + '.txt'
    dm_path_on_local = paths.SAVE_TRADE + trade.origin + '/'
    dj_path_on_local = dm_path_on_local + 'juice/'
    m_path_on_local = dm_path_on_local + date_string + '.txt'
    j_path_on_local = dj_path_on_local + date_string + '.txt'


    # Check file structure exists, if not create it
    if os.path.exists(dj_path_on_local):

        # Store in monthly trade group breakdown
        storage.child(m_path_on_cloud).download("./", m_path_on_local)
        with open(m_path_on_local, 'a', encoding="utf8") as f:
            f.write(str(trade.update_snapshot()))
            #f.write(trade.trade_log)
            f.write('_________________________________\n\n')
        storage.child(m_path_on_cloud).put(m_path_on_local)

        # Store the profit/loss multiplier, pair and duration
        storage.child(j_path_on_cloud).download("./", j_path_on_local)
        with open(j_path_on_local, 'a', encoding="utf8") as f:
            tradevalue = float(trade.closed_diff)/100 + 1
            tradevalue = round(tradevalue, 2)
            f.write(str(tradevalue) + ' | ' + trade.pair + ' | ' + str(trade.duration) + ' Hours\n')
        storage.child(j_path_on_cloud).put(j_path_on_local)

        # Store website data in realtime DB
        tradevalue = float(trade.closed_diff)/100
        tradevalue = round(tradevalue, 2)

        realtime_save_trade(tradevalue, trade, now)

    else:
        #os.makedirs = f_path_on_local.split('/')[0:-1]
        os.makedirs(dj_path_on_local)
        save_trade(trade)



def error_log(error):
    '''Logs exceptions to database'''
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')

    path_on_cloud = paths.LOG + 'exceptions/' + month_year + '/' + date_formatted + '.txt'
    d_path_on_local = paths.LOG + 'exceptions/' + month_year + '/'
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
            #os.makedirs = f_path_on_local.split('/')[0:-1]
            error_log(error)
    except Exception as e:
        print('Exception in exceptor :(')
        print(str(e))




def gen_log(log):
    '''Logs general program runtime for debugging purposes'''
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')
    path_on_cloud = paths.LOG + 'general_logs/' + month_year + '/' + date_formatted + '.txt'
    d_path_on_local = paths.LOG + 'general_logs/' + month_year + '/'
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
        #os.makedirs = f_path_on_local.split('/')[0:-1]
        gen_log(log)


def failed_message(msg, origin, ex):
    '''Exceptions related to specific signal groups messages
    Example: an error in Hirns signal format, or couldn't match the coin type'''
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    path_on_cloud = paths.SAVE_TRADE + origin + '/failed/' + month_year + '.txt'
    # Path on local will error if there is no directory created beforehand, so we have two filepaths
    d_path_on_local = paths.SAVE_TRADE + origin + '/failed/'
    f_path_on_local = d_path_on_local + month_year + '.txt'

    if os.path.exists(d_path_on_local):
        storage.child(path_on_cloud).download("./", f_path_on_local)
        with open(f_path_on_local, 'a', encoding="utf8") as f:
            f.write(msg + '\n')
            f.write('__________________________\n')
            f.write(str(ex))
            f.write('\n\n')
        storage.child(path_on_cloud).put(f_path_on_local)
    else:
        os.makedirs(d_path_on_local)
        #os.makedirs = f_path_on_local.split('/')[0:-1]
        failed_message(msg, origin, ex)


def pickle_save(obj, cloudpath, localpath):
    '''pickle saves'''
    path_on_cloud = paths.SAVE + cloudpath
    path_on_local = paths.SAVE + localpath

    if os.path.exists(paths.SAVE):
        storage.child(path_on_cloud).download("./", path_on_local)
        try:
            with open(path_on_local, 'wb') as stream_save_file:
                pickle.dump(obj, stream_save_file)
            storage.child(path_on_cloud).put(path_on_local)
        except Exception as e:
            print(str(e))
            print("Unexpected Picklesave Error")
    else:
        os.makedirs(paths.SAVE)
        pickle_save(obj, cloudpath, localpath)


def pickle_load(path_on_cloud, path_on_local):
    '''pickle loads'''
    ret_obj = None
    if os.path.exists(paths.SAVE):
        storage.child(path_on_cloud).download("./", path_on_local)
        try:
            with open(path_on_local, 'rb') as config_dictionary_file:
                ret_obj = pickle.load(config_dictionary_file)
        except FileNotFoundError as e:
            print(str(e))
    else:
        os.makedirs(paths.SAVE)
        pickle_load(path_on_cloud, path_on_local)
    return ret_obj


def save_stream(restartstream):
    '''Saves the active tradestream'''
    path_on_cloud = paths.STREAM
    path_on_local = paths.STREAM
    pickle_save(restartstream, path_on_cloud, path_on_local)


def load_stream():
    '''Loads the active tradestream'''
    path_on_cloud = paths.SAVE + paths.STREAM
    path_on_local = paths.SAVE + paths.STREAM
    loaded = pickle_load(path_on_cloud, path_on_local)
    return loaded


def get_binance_spot_list():
    '''Gets list of tradeable binance spot pairs
    DEPRECIATED!'''
    path_on_cloud = "docs/binance_spot.txt"
    path_on_local = "docs/binance_spot.txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, "r") as file:
        return file.read().split('\n')


def get_binance_futures_list():
    '''Gets list of tradeable binance futures pairs
    DEPRECIATED!'''
    path_on_cloud = "docs/binance_future.txt"
    path_on_local = "docs/binance_future.txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, "r") as file:
        return file.read().split('\n')