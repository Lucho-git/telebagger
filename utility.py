"""Various Helper commands that are hard to place elsewhere"""
import re
import os
import numpy as np

from datetime import datetime

def format_float(num):
    return np.format_float_positional(num, trim='-')

def strip_ansi_codes(s):
    return re.sub('\033\\[([0-9]+)(;[0-9]+)*m', '', s)

# Converts a Binance server timestamp into a local timestamp in milliseconds
def convert_timestamp_utc8(timestamp):
    '''Converts a utc servertime to utc8 as a number timestring'''
    dt = float(timestamp / 1000)
    utctime = datetime.utcfromtimestamp(dt)
    timedelta = 60 * 60 * 8  # + 8 Hours from UTC
    timestamp = datetime.timestamp(utctime) + timedelta
    return int(timestamp * 1000)

def utc_to_utc8(timestamp):
    '''convert to utc8'''
