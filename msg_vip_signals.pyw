import time
import copy
import fake_trade
from trade_classes import Trade, Futures

tradeheat = [False]
vip_signals_timer = [0]
real = [False]

WAIT_TIME1 = 60 * 1000
WAIT_TIME2 = 120 * 1000
WAIT_TIME3 = 180 * 1000
WAIT_TIME4 = 300 * 1000
WAIT_TIME5 = 10000 * 1000
WAIT_TIMES = [WAIT_TIME1,WAIT_TIME2,WAIT_TIME3,WAIT_TIME4,WAIT_TIME5]

def bag(msg, binance_wrap):
    search_text = msg
    result = None
    result = vip_signals_message(search_text)
    print('Vip Message analsis')

    raw_server_time = binance_wrap.timenow()
    print(raw_server_time)
    if raw_server_time < vip_signals_timer[0]:
        tradeheat[0] = True
        print("Cooling Down")
    else:
        tradeheat[0] = False

    if result and not tradeheat[0]:
        trade_decimal = 1
        # TODO, add global variable to top of file
        vip_string = str(result[0]) + "___" + str(result[1])
        print(vip_string)
        if binance_wrap.isUSDTpair(result[0]):
            pair = result[0] + 'USDT'
            base = 'USDT'
        elif binance_wrap.isBTCpair(result[0]):
            pair = result[0] + 'BTC'
            base = 'BTC'
        else:
            raise Exception('No USDT or BTC pair')
        # Swap to base currency
        if base == 'BTC':
            binance_wrap.usdt2btc()
        elif base == 'USDT':
            binance_wrap.btc2usdt()
        # Create a signal based on message values, buys x amount of coin
        signals = []
        for w in WAIT_TIMES:
            signal = Trade(pair, base, 'VIP Signals', 'spot')
            fake_trade.spot_trade(signal)
            signal.timelimit = signal.time + w
            signals.append(signal)
        first_trade_time = signals[0].time
        # Perform 1st trade, and copy results

        if real[0]:
            print(binance_wrap.getprice(pair))
            binance_wrap.market_trade(signal, trade_decimal, True)
            trade1 = copy.deepcopy(signal)
            print(signal.snapshot())

            # Record trade results
            filename = 'VIPTRADES/' + str(signal.tradetime) + '.txt'
            with open(filename, 'w') as f:
                f.write(signal.snapshot())

            # waits 2 minutes after buying signals
            # This section can be improved, maybe use a limit sell order instead of market
            time.sleep(130)
            # 2 minutes later, sell the signaled coin, recording the results

            # Perform 2nd trade, then compare with 1st trade to see difference
            binance_wrap.market_trade(signal, trade_decimal, False)
            trade2 = copy.deepcopy(signal)
            print(signal.snapshot())
            difference = signal.trade_diff(trade1, trade2)
            print(difference)
            filename2 = 'VIPTRADES/' + str(signal.tradetime) + '.txt'
            with open(filename2, 'w') as f:
                f.write(signal.snapshot())
                f.write(difference)

            # if spot portfolio is left in BTC, transfer back to USDT
            if base == 'BTC':
                binance_wrap.usdt2btc()

        # Wait 180 seconds before allowing new vip trades
        vip_signals_timer[0] = first_trade_time + 720000
        return signals

    else:
        print('Not a signal')


def vip_signals_message(vip_message):
    validity = valid_trade_message(vip_message)
    trade_type = None
    if validity:
        trade_type = search_coin(vip_message)
    return trade_type


def valid_trade_message(vip_message):
    vip_message = vip_message.upper()
    if (('TARGET ' in vip_message) or ('TARGET:' in vip_message) or ('TARGETS ' in vip_message) or (
            'TARGETS:' in vip_message)) and ('-' in vip_message):
        print("Valid Message")
        return True
    else:
        return False


def search_coin(text):
    coins = []
    with open("binance_spot.txt", "r") as file:
        for line in file:
            line = line.strip()
            coinspaces = str(line + ' ')
            coinslash = str(line + '/')
            coinusdt = str(line + 'USDT')
            coinfullstop = str(line + '.')
            coinbtc = str(line + 'BTC')
            if (coinspaces in text) or (coinslash in text) or (coinusdt in text) or (coinfullstop in text) or (
                    coinbtc in text):
                coins.append(line)
    if not coins:
        with open("binance_future.txt", "r") as file:
            for line in file:
                line = line.strip()
                coinspaces = str(line + ' ')
                coinslash = str(line + '/')
                coinusdt = str(line + 'USDT')
                coinfullstop = str(line + '.')
                coinbtc = str(line + 'BTC')
                if (coinspaces in text) or (coinslash in text) or (coinusdt in text) or (coinfullstop in text) or (
                        coinbtc in text):
                    coins.append(line)
        if coins:
            coins.append('Futures')
        else:
            print("No Coin Found")
    else:
        coins.append('Spot')

    # edge cases
    if 'DATA' in coins:
        print("Edge Case DATA")
        coins.remove('ATA')
    if 'YFII' in coins:
        coins.remove('YFI')
    if 'LOOM' in coins:
        coins.remove('OM')
    if 'DEGO' in coins:
        coins.remove('GO')
    if 'HBAR' in coins:
        coins.remove('AR')
    if len(coins) > 2:
        print("Multiple Coins")
        first = 9999999
        for c in coins:
            if not (c == 'Futures') and not (c == 'Spot'):
                current = text.find(c)
                if current < first:
                    first = current
                    coins[0] = c
    if coins:
        coins[1] = coins[int(len(coins)) - 1]
    return coins[0:2]


'''
def print_past_messages(client):
  msgs = client.get_messages('CryptoVIPsignalTA', limit=2000)
  if msgs is not None:
    print("Messages:\n---------")
    f = open("vip_examples.txt", "w")
    for msg in msgs:
      if ('buy zone'.upper() in str(msg).upper()) and ('target'.upper() in str(msg).upper())  and ('-' in str(msg)):
        f.write(str(msg.message) +'\n')
        f.write('______________________\n')
    f.close()   
'''
