import pyrebase
import pickle
import numpy as np

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

# Firebase Cloud Storage File Paths
'''
FAILED_MESSAGES = "trade_results/failed_messages/"  # Filepath
ADD_MESSAGE = "trade_results/message_count/"  # Filepath
SAVE_STREAM = "save_data/savefile"  # Path and file
SAVE_TRADE = "trade_results/"  # Path
'''
# Heroku Version
FAILED_MESSAGES = "heroku/trade_results/failed_messages/"  # Filepath
ADD_MESSAGE = "heroku/trade_results/message_count/"  # Filepath
SAVE_STREAM = "heroku/save_data/savefile"  # Path and file
SAVE_TRADE = "heroku/trade_results/"  # Path


def failed_message(msg, origin, e):
    path_on_cloud = FAILED_MESSAGES + origin + '_failed.txt'
    path_on_local = origin + '_failed.txt'
    storage.child(path_on_cloud).download("./", path_on_local)
    e = str(e)

    try:
        with open(path_on_local, 'a') as f:
            f.write(msg + '\n')
            f.write('__________________________\n')
            f.write(e)
            f.write('\n\n')
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as ex:
        ex = str(ex)
        print(ex)
        print("No Previous File existed I think")
        with open(path_on_local, 'w+') as f:
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
    path_on_local = origin + '_count.txt'
    storage.child(path_on_cloud).download("./", path_on_local)
    try:
        with open(path_on_local, 'a') as f:
            f.write(result + '\n')
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as e:
        print(e)
        print("New count file?")
        with open(path_on_local, 'w+') as f:
            f.write(origin + 'Signal Count    [-] is Fail  ||  [X] is Success \n')
            f.write('==========================\n')
            f.write(result + '\n')
        storage.child(path_on_cloud).put(path_on_local)


def save_stream(restartstream):
    path_on_cloud = SAVE_STREAM
    path_on_local = "save_data/savefile"
    storage.child(path_on_cloud).download("./", path_on_local)
    try:
        with open(path_on_local, 'wb') as stream_save_file:
            pickle.dump(restartstream, stream_save_file)
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as e:
        print(str(e))
        print("Unexpected Savefile Error")


def load_stream():
    restartstream = None
    path_on_cloud = SAVE_STREAM
    path_on_local = "savefile"
    storage.child(path_on_cloud).download("./", path_on_local)
    try:
        with open(path_on_local, 'rb') as config_dictionary_file:
            restartstream = pickle.load(config_dictionary_file)
    except Exception as e:
        print('No Save File')
        print(str(e))
    return restartstream


def save_trade(t):
    # Add trade result to all trades textfile
    path_on_cloud = SAVE_TRADE + 'TradeResults.txt'
    path_on_local = "save_data/TradeResults.txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open('save_data/TradeResults.txt', 'a') as f:
        f.write(str(t.savestring))
        f.write('\n\n')
    storage.child(path_on_cloud).put(path_on_local)
    # Add trade result to specific trade textfile
    path_on_cloud = SAVE_TRADE + t.origin + ".txt"
    path_on_local = "save_data/" + t.origin + ".txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, 'a') as f:
        f.write(str(t.savestring))
        f.write(t.trade_log)
        f.write('_________________________________\n\n')
    storage.child(path_on_cloud).put(path_on_local)


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
