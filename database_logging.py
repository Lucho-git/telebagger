"""Module interacts with the database, for saving and loading various data/logs"""
from datetime import datetime
import os
import pickle
import json
import jsonpickle
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

    signal_group = trade.conditions.signal.origin.name
    newvalue = [tradevalue-1, day_string, {'Tradepair': trade.pair, 'Duration(Hrs)': trade.duration_hours()}]

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
        try:
            del last7[7]
        except Exception as e:
            error_log(('Caught Exception:' + str(e)))
            error_log(('Array of length: ' + len(last7) + '|' + str(last7)))


    if len(last30) > 29:
        del last30[30]
    data7 = {"label": "Last-7", "values": last7}
    data30 = {"label": "Last-30", "values": last30}
    monthly = {"label": date_string, "values": monthly}

    print('Saving to realtime...',paths.REALTIME_SAVE + signal_group)
    database.child(paths.REALTIME_SAVE + signal_group + '/Last-7').set(data7)
    database.child(paths.REALTIME_SAVE + signal_group + '/Last-30').set(data30)
    database.child(paths.REALTIME_SAVE + signal_group + '/Month/' + date_string).set(monthly)

def update_live_view(trade):
    '''Saves a trade to live_view'''
    json_filepath = paths.LIVE_VIEW + 'active/' + str(trade.id) + '.txt'
    json_dir = json_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    # Save json to live_view/active
    storage.child(json_filepath).download("./", json_filepath)
    with open(json_filepath, 'w', encoding="utf8") as f:
        f.write(jsonpickle.encode(trade, make_refs=False, unpicklable=False))
    storage.child(json_filepath).put(json_filepath)

def close_live_view(closed_filepath, trade):
    '''Changes json trade from active to closed'''
    # Checks for json in active trades
    active_filepath = closed_filepath.replace('closed', 'active')
    active_dirpath = active_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(active_dirpath):
        os.makedirs(active_dirpath)

    # reoves json from live_view/active
    active_exists = False
    for filename in os.listdir(active_dirpath):
        if str(trade.id) in filename:
            os.remove(active_filepath)
            active_exists = True
    if not active_exists:
        error_log('Closing_trade' + str(trade.id) + 'does not seem to exist')
        return

    # Save json to live_view/closed
    storage.child(closed_filepath).download("./", closed_filepath)
    with open(closed_filepath, 'w', encoding="utf8") as f:
        f.write(jsonpickle.encode(trade, make_refs=False, unpicklable=False))
    storage.child(closed_filepath).put(closed_filepath)

def save_closed_trade(trade):
    '''Saves trades to database'''
    now = datetime.now(tz)
    date_string = now.strftime('%B-%Y')

    json_filepath = paths.LIVE_VIEW + 'closed/' + str(trade.id) + '.txt'
    monthly_filepath = paths.SAVE_TRADE + trade.conditions.signal.origin.name + '/' + date_string + '.txt'
    juice_filepath = paths.SAVE_TRADE + trade.conditions.signal.origin.name + '/juice/' + date_string + '.txt'

    # Check file structure exists, if not create it
    filepaths = [json_filepath, monthly_filepath, juice_filepath]
    for p in filepaths:
        p = p.rsplit('/', 1)[0]+'/'
        if not os.path.exists(p):
            os.makedirs(p)

    # Store entire trade as json
    close_live_view(json_filepath, trade)

    # Store in monthly trade group breakdown
    storage.child(monthly_filepath).download("./", monthly_filepath)
    with open(monthly_filepath, 'a', encoding="utf8") as f:
        f.write(str(trade.update_snapshot()))
        #f.write(trade.conditions_log)
        f.write('_________________________________\n\n')
    storage.child(monthly_filepath).put(monthly_filepath)

    # Store the profit/loss multiplier, pair and duration
    storage.child(juice_filepath).download("./", juice_filepath)
    with open(juice_filepath, 'a', encoding="utf8") as f:
        tradevalue = trade.closed_value
        tradevalue = round(tradevalue, 2)
        f.write(str(tradevalue) + ' | ' + trade.pair + ' | ' + str(trade.duration()) + ' Hours\n')
    storage.child(juice_filepath).put(juice_filepath)

    # Store website data in realtime DB
    tradevalue = float(trade.closed_value)
    tradevalue = round(tradevalue, 2)

    realtime_save_trade(tradevalue, trade, now)


def error_log(error):
    '''Logs exceptions to database'''
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')

    error_filepath = paths.LOG + 'exceptions/' + month_year + '/' + date_formatted + '.txt'
    error_dirpath = error_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(error_dirpath):
        os.makedirs(error_dirpath)

    print(str(error))
    storage.child(error_filepath).download("./", error_filepath)
    with open(error_filepath, 'a', encoding="utf8") as f:
        f.write(time_formatted + '| ' + str(error) + '\n\n')
    storage.child(error_filepath).put(error_filepath)



def gen_log(log):
    '''Logs general program runtime for debugging purposes'''
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')
    date_formatted = now.strftime('%d-%b-%y')
    time_formatted = now.strftime('%H:%M:%S:')
    genlog_filepath = paths.LOG + 'general_logs/' + month_year + '/' + date_formatted + '.txt'
    genlog_dirpath = genlog_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(genlog_dirpath):
        os.makedirs(genlog_dirpath)

    log = log.replace('\n', str('\n'+time_formatted+'| '))
    storage.child(genlog_filepath).download("./", genlog_filepath)
    # If file exists, add to it, else create a new one
    with open(genlog_filepath, 'a+', encoding="utf8") as f:
        f.write(time_formatted + '| ' + log + '\n\n')
    storage.child(genlog_filepath).put(genlog_filepath)


def failed_message(msg, origin, ex):
    '''Exceptions related to specific signal groups messages
    Example: an error in Hirns signal format, or couldn't match the coin type'''
    now = datetime.now(tz)
    month_year = now.strftime('%B-%Y')

    failedmsg_filepath = paths.SAVE_TRADE + origin + '/failed/' + month_year + '.txt'
    failedmsg_dirpath = failedmsg_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(failedmsg_dirpath):
        os.makedirs(failedmsg_dirpath)

    storage.child(failedmsg_filepath).download("./", failedmsg_filepath)
    with open(failedmsg_filepath, 'a', encoding="utf8") as f:
        f.write(msg + '\n')
        f.write('__________________________\n')
        f.write(str(ex))
        f.write('\n\n')
    storage.child(failedmsg_filepath).put(failedmsg_filepath)


def save_stream(savestream):
    '''Saves the active tradestream'''
    save_filepath = paths.SAVE
    save_dirpath = save_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(save_dirpath):
        os.makedirs(save_dirpath)

    storage.child(save_filepath).download("./", save_filepath)
    try:
        with open(save_filepath, 'wb') as stream_save_file:
            pickle.dump(savestream, stream_save_file)
        storage.child(save_filepath).put(save_filepath)
    except Exception as e:
        print(str(e))
        print("Unexpected Picklesave Error")


def load_stream():
    '''Loads the active tradestream'''
    load_filepath = paths.SAVE
    load_dirpath = load_filepath.rsplit('/', 1)[0]+'/'
    if not os.path.exists(load_dirpath):
        os.makedirs(load_dirpath)

    load_data = None
    storage.child(load_filepath).download("./", load_filepath)
    try:
        with open(load_filepath, 'rb') as config_dictionary_file:
            load_data = pickle.load(config_dictionary_file)
        storage.child(load_filepath).put(load_filepath)
    except FileNotFoundError as e:
        print(str(e))
    return load_data


def get_from_realtime(pathway):
    for key,value in paths.items():
        if pathway == key:
            pathway = value
            print(f"Matched Key: {key}, Value: {value}")
    return database.child(pathway).get()


def set_to_realtime(pathway, data):
    database.child(pathway).set(data)

def add_to_realtime(pathway, data):
    try:
        existing_data = database.child(pathway).get().val()
        existing_data.update(data)
    except:
        existing_data = data
    database.child(pathway).update(existing_data)

def push_to_realtime(pathway, data):
    database.child(pathway).set(data)

def add_discord_channel(id, name, category):
    splitids = id.split('-')
    guild_id = splitids[0]
    channel_id = splitids[1]
    data = {
        'guild_id': guild_id,
        'channel_id': channel_id,
        'channel_name': name,
        'type': category,
    }
    print('DATA:',data)
    add_to_realtime(paths.DISCORD_CHANNEL +f"/{guild_id}/{channel_id}", data)
    print('Added new discord channel')

def add_telegram_channel(id, name, category):
    data = {
        id: name,
    }
    add_to_realtime(paths.TELEGRAM_CHANNEL +f"/{category}", data)
    print('Added new telegram channel')


def get_discord_channels():
    return get_from_realtime(paths.DISCORD_CHANNEL).val()