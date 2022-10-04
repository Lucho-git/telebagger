import hirn

hirn_controller = hirn.HirnSignal()

'''Controller for signals coming from a signal group'''
async def new_signal(signal):
    '''Sends signal to the specified group'''
    if signal.origin.name == '1548802426':
        print('Always Win Message')

    elif signal.origin.id == '1248393106':
        print('Hirn Message')
        print(signal)
        trades = hirn_controller.new_signal(signal)
