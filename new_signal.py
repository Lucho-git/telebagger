'''This module contains references to all of the different trade groups, sends signal info to them and recieves trade info'''

import hirn
from trade import Trade

hirn_controller = hirn.HirnSignal()

async def get_trades(signal):
    '''Sends signal to the specified group'''
    if signal.origin.name == '1548802426':
        print('Always Win Message')

    elif signal.origin.id == '1248393106':
        return hirn_controller.new_signal(signal)


async def new_signal(signal, trade_stream):
    '''Controller for signals coming from a signal group'''
    # Get trade details from signal
    trades = await get_trades(signal)
    # Build and Initiate trades
    # Add trade to trade_stream
    add_trades = []
    for t in trades or []:
        new_trade = Trade(t)
        add_trades.append(new_trade)
        #print(vars(new_trade))
    await trade_stream.add_trade_to_stream(add_trades)
