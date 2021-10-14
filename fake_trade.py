import utility

# Binance Client Object
realclient = utility.get_binance_client()


def fake_trade(trade, bag_id=None, percent=None):
    trade.price = float(realclient.get_symbol_ticker(symbol=trade.pair)['price'])
    trade.time = realclient.get_server_time()['serverTime']
    trade.id = trade.time
    trade.lowest = trade.price
    trade.highest = trade.price
    trade.status = 'active'
    if bag_id and percent:
        trade.bag_id.append(bag_id)
        utility.start_trade_folios(trade, percent)


def fake_trade_copy (trade, bag_id=None, percent=None):
    trade.price = float(realclient.get_symbol_ticker(symbol=trade.pair)['price'])
    trade.time = realclient.futures_time()['serverTime']
    trade.id = trade.time
    trade.lowest = trade.price
    trade.highest = trade.price
    trade.status = 'active'
    if bag_id and percent:
        trade.bag_id.append(bag_id)
        utility.start_trade_folios(trade, percent)


def mfutures_trade(trade, bag_id=None, percent=None):
    trade.price = float(realclient.get_symbol_ticker(symbol=trade.pair)['price'])
    trade.time = realclient.futures_time()['serverTime']
    trade.id = trade.time
    trade.lowest = trade.price
    trade.highest = trade.price
    trade.status = 'active'
    print(bag_id, percent)
    if bag_id and percent:
        trade.bag_id.append(bag_id)
        utility.start_trade_folios(trade, percent)


