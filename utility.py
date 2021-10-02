import pyrebase
import pickle
import numpy as np
import asyncio as aio

local = False

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

if local:
    # Firebase Cloud Storage File Paths
    FAILED_MESSAGES = "trade_results/failed_messages/"  # Filepath
    ADD_MESSAGE = "trade_results/message_count/"  # Filepath
    SAVE_STREAM = "save_data/savefile"  # Path and file
    SAVE_FOLIO = "save_data/savefolios" #Path and file
    SAVE_TRADE = "trade_results/"  # Path
    RESULTS = "trade_results/juice/"  # Path
else:
    # Heroku Version
    FAILED_MESSAGES = "heroku/trade_results/failed_messages/"  # Filepath
    ADD_MESSAGE = "heroku/trade_results/message_count/"  # Filepath
    SAVE_STREAM = "heroku/save_data/savefile"  # Path and file
    SAVE_FOLIO = "heroku/save_data/savefolios"  # Path and file
    SAVE_TRADE = "heroku/trade_results/"  # Path
    RESULTS = "heroku/trade_results/juice/"  # Path


def failed_message(msg, origin, e, file_string):
    path_on_cloud = FAILED_MESSAGES + origin + file_string
    path_on_local = origin + '_failed.txt'
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
    path_on_local = origin + '_count.txt'
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
    path_on_local = "save_data/savefile"
    pickle_save(restartstream, path_on_cloud, path_on_local)


def load_stream():
    path_on_cloud = SAVE_STREAM
    path_on_local = "save_data/savefile"
    loaded = pickle_load(path_on_cloud, path_on_local)
    return loaded


def save_folio(folios):
    path_on_cloud = SAVE_FOLIO
    path_on_local = "save_data/savefolios"
    pickle_save(folios, path_on_cloud, path_on_local)


def load_folio():
    path_on_cloud = SAVE_FOLIO
    path_on_local = "save_data/savefolios"
    folio = pickle_load(path_on_cloud, path_on_local)
    return folio


def save_trade(t):
    # Add trade result to all trades textfile
    path_on_cloud = SAVE_TRADE + 'TradeResults.txt'
    path_on_local = "save_data/TradeResults.txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open('save_data/TradeResults.txt', 'a', encoding="utf8") as f:
        f.write(str(t.savestring))
        f.write('\n\n')
    storage.child(path_on_cloud).put(path_on_local)
    # Add trade result to specific trade textfile
    path_on_cloud = SAVE_TRADE + t.origin + ".txt"
    path_on_local = "save_data/" + t.origin + ".txt"
    storage.child(path_on_cloud).download("./", path_on_local)
    with open(path_on_local, 'a', encoding="utf8") as f:
        f.write(str(t.savestring))
        f.write(t.trade_log)
        f.write('_________________________________\n\n')
    storage.child(path_on_cloud).put(path_on_local)


def trade_results(t):
    path_on_cloud = RESULTS + t.bag_id + '.txt'
    path_on_local = 'save_data/juice/' + t.bag_id + '.txt'
    storage.child(path_on_cloud).download("./", path_on_local)

    tradevalue = float(t.closed_diff)/100 + 1
    tradevalue = round(tradevalue, 2)
    with open(path_on_local, 'a') as f:
        f.write(str(tradevalue))
        if t.portfolio_amount:
            f.write(' | ')
            f.write(t.portfolio_amount)
        f.write('\n')
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
