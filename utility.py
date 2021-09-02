def failed_message(msg, origin, storage, e):
    path_on_cloud = "trade_results/failed_messages/" + origin + '_failed.txt'
    path_on_local = origin + '_failed.txt'
    storage.child(path_on_cloud).download("./", path_on_local)

    try:
        with open(path_on_local, 'a') as f:
            f.write(msg + '\n')
            f.write('__________________________\n')
            f.write(e)
            f.write('\n\n')
        storage.child(path_on_cloud).put(path_on_local)
    except Exception as ex:
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


def add_message(storage, origin, result):
    path_on_cloud = "trade_results/message_count/" + origin + '_count.txt'
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
