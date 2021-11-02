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


def fake_trade_copy(new_trade, old_trade, bag_id=None, percent=None):
    new_trade.price = old_trade.price
    new_trade.time = old_trade.time + 1
    new_trade.id = old_trade.id + 1
    new_trade.lowest = old_trade.lowest
    new_trade.highest = old_trade.highest
    new_trade.status = old_trade.status
    if bag_id and percent:
        new_trade.bag_id.append(bag_id)
        utility.start_trade_folios(new_trade, percent)
    return new_trade

