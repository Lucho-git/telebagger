import pyrebase
from datetime import datetime

config = {  # initialising database connection
    "apiKey": "AIzaSyDl_eUsJkNxN5yW9KS6X0n0tkQFruV8Tbs",
    "authDomain": "telebagger.firebaseapp.com",
    "databaseURL": "https://telebagger-default-rtdb.firebaseio.com/",
    "projectId": "telebagger",
    "storageBucket": "telebagger.appspot.com",
    "messagingSenderId": "332905720250",
    "appId": "1:332905720250:web:e2006e777fa8d980d61583",
    "measurementId": "G-02W82CCF85",
    "serviceAccount": "docs/db_admin.json",
}


firebaseConfig = {
  "apiKey": "AIzaSyDl_eUsJkNxN5yW9KS6X0n0tkQFruV8Tbs",
  "authDomain": "tester-be16c.firebaseapp.com",
  "databaseURL": "https://tester-be16c-default-rtdb.firebaseio.com/",
  "projectId": "tester-be16c",
  "storageBucket": "tester-be16c.appspot.com",
  "messagingSenderId": "332905720250",
  "appId": "1:332905720250:web:e2006e777fa8d980d61583",
  "measurementId": "G-02W82CCF85",
}


firebase = pyrebase.initialize_app(config)

storage = firebase.storage()
database = firebase.database()

now = datetime.now()
date_string = now.strftime('%B-%Y')
day_string = now.strftime("%d-%B")


signal_group = 'Hirn'
newvalue = [0.4, day_string]


last7 = database.child('signals/' + signal_group + '/Last-7').get()
last30 = database.child('signals/' + signal_group + '/Last-30').get()
monthly = database.child('signals/' + signal_group + '/Month/' + date_string).get()
last7 = last7.val()['values']
last30 = last30.val()['values']
monthly = monthly.val()['values']

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
