import pyrebase
from datetime import datetime

config = {  # initialising database connection
    "apiKey": "AIzaSyDl_eUsJkNxN5yW9KS6X0n0tkQFruV8Tbs",
    "authDomain": "telebagger.firebaseapp.com",
    "projectId": "telebagger",
    "messagingSenderId": "332905720250",
    "storageBucket": "telebagger.appspot.com",
    "appId": "1:332905720250:web:e2006e777fa8d980d61583",
    "measurementId": "G-02W82CCF85",
    "databaseURL":  "https://telebagger-default-rtdb.firebaseio.com/",
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()


#monthly = database.child('signals/' + signal_group + '/Month/').get()
#print(monthly.val()['values'])


'''
path = '/heroku/trade_results/Always Win2/juice/April-2022.txt'
local = 'download.txt'

storage.child(path).download("./", local)
with open(local, 'r', encoding="utf8") as f:
    lines = f.readlines()

linedata = []
for li in lines:
    li = li.split('|')
    print(li)
    if float(li[0]) < 10:
        values = [round(float(li[0])-1, 2), 'X-April', {'pair': li[1], 'duration': li[2].split('\n')[0]}]
        linedata.append(values)

newdata = {"label": 'Always Win2 April-2022', "values": linedata}
#database.child('signals/Always Win2/Month/April-2022').set(newdata)
'''

signal_group = 'Hirn2'

allvalues = []
realtime = database.child('heroku/signals/'+signal_group+'/Month/').get().val()
print(realtime)
if realtime.get('March-2022'):
    for v in realtime['March-2022']['values']:
        allvalues.append(v)
if realtime.get('April-2022'):
    for v in realtime['April-2022']['values']:
        allvalues.append(v)
if realtime.get('May-2022'):
    for v in realtime['May-2022']['values']:
        allvalues.append(v)

allvalues.reverse()
last30 = allvalues[0:30]
last7 = allvalues[0:7]

last7 = {"label": 'Last-7', "values": last7}
last30 = {"label": 'Last-30', "values": last30}

database.child('heroku/signals/'+signal_group+'/Last-7').set(last7)
database.child('heroku/signals/'+signal_group+'/Last-30').set(last30)



'''

if len(last7) > 6:
    del last7[0]
last7.append(newvalue)

if len(last30) > 29:
    del last30[0]
last30.append(newvalue)
monthly.append(newvalue)
data7 = {"label": signal_group + " Signals Last-7", "values": last7}
data30 = {"label": signal_group + " Signals Last-30", "values": last30}
monthly = {"label": signal_group + ' ' + date_string, "values": monthly}

database.child('signals/' + signal_group + '/Last-7').set(data7)
database.child('signals/' + signal_group + '/Last-30').set(data30)
database.child('signals/' + signal_group + '/Month/' + date_string).set(monthly)

[,'-April',{'Tradepair': '', 'Duration(Hrs)': }],
values_month = [
[-0.006,'2-April',{'Tradepair': 'ALPHAUSDT', 'Duration(Hrs)': 0.42}],


'''





'''

signal_group = 'Always Win2'
actual_month = 'May-2022'

realtime = database.child('heroku/signals/'+signal_group+ '/Month/' + actual_month).get().val()

x = 0
for i in realtime['values']:
    #i[2] = {'Tradepair': i[2]['pair'].strip(), 'Duration(Hrs)': i[2]['duration'].split('Hours')[0].strip()}

    #stepsize = 29/len(realtime['values'])
    #x += float(stepsize)
    #datenum = int(x)

    #i[1] = str(datenum) + '-' + i[1].split('-')[1]
    if x < 15:
        i[0] = round(i[0]-1, 2)
    print(i)
    x+=1

print(realtime)

database.child('heroku/signals/' + signal_group + '/Month/' + actual_month).set(realtime)

'''