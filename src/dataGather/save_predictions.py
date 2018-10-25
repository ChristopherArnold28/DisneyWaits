import pymysql
import pandas as pd
import numpy as np
import transformations
import config
import prediction_helper

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)

#gather all historical data to build model
RideWaits = pd.read_sql_query("call DisneyDB.RideWaitQuery('2,7,8,9')", conn)


starter_data = RideWaits.copy()

#transform data for model bulding
RideWaits = transformations.transformData(RideWaits)

print("Gathered Data")

from datetime import datetime
from pytz import timezone
tz = timezone('US/Eastern')
dtime = datetime.now(tz)
dtime = dtime.replace(hour = 7,minute = 0, second = 0, microsecond = 0)
date = dtime.date()
time = dtime.time().strftime("%H:%M")
from datetime import datetime
from dateutil.relativedelta import relativedelta

def date_range(start_date, end_date, increment, period):
    result = []
    nxt = start_date
    delta = relativedelta(**{period:increment})
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result

end_time = dtime.replace(hour = 23, minute = 45, second = 0, microsecond = 0)
time_list = date_range(dtime, end_time, 15, 'minutes')
time_list = [x.time().strftime("%H:%M") for x in time_list]


park_hours = pd.read_sql_query("select * from DisneyDB.ParkHours where Date = '" + str(date) + "'", conn)


best_params = {'criterion': 'mse',
 'max_depth': 10,
 'max_features': 'auto',
 'min_samples_leaf': 5,
 'min_samples_split': 2,
 'n_estimators': 100}

rides = list(set(starter_data['Name']))
#rides = ["Expedition Everest - Legend of the Forbidden Mountain","Gran Fiesta Tour Starring The Three Caballeros","Star Wars Launch Bay: Encounter Kylo Ren"]
global todays_predictions
todays_predictions = {}

import threading
num_threads = len(rides)

threads = []
for i in range(num_threads):
    print(rides[i-1])
    ride = rides[i-1]
    current_ride = starter_data.copy()
    current_ride = starter_data[current_ride['Name'] == ride]
    process = threading.Thread(target = prediction_helper.make_daily_prediction, args = [current_ride,ride,time_list, best_params, todays_predictions, todays_hours])
    process.start()
    threads.append(process)

for process in threads:
    process.join()

all_predictions = pd.DataFrame()
for key,value in todays_predictions.items():
    current_frame = value['predictions']
    current_frame = current_frame[['RideId','Time','predicted_wait','confidence_high','confidence_low']]
    current_frame.columns = ['RideId','Time','PredictedWait','ConfidenceHigh','ConfidenceLow']
    current_frame['PredictedWait'] = [int(str(x).split(".")[0]) for x in current_frame['PredictedWait']]
    current_frame['ConfidenceHigh'] = [int(str(x).split(".")[0]) for x  in current_frame['ConfidenceHigh']]
    current_frame['ConfidenceLow'] = [int(str(x).split(".")[0]) for x in current_frame['ConfidenceLow']]
    all_predictions = pd.concat([all_predictions, current_frame])

print("Done first threading model loop")

RideIds = list(set(RideWaits['RideId']))
rides_not_predicted = [x for x in RideIds if x not in list(set(all_predictions["RideId"]))]
print(str(len(rides_not_predicted)) + " not predicted in first pass")

if len(rides_not_predicted) > 0:
    best_params = {'criterion': 'mse',
     'max_depth': 10,
     'max_features': 'auto',
     'min_samples_leaf': 5,
     'min_samples_split': 2,
     'n_estimators': 100}

    #rides = list(set(starter_data['Name']))
    rides = rides_not_predicted
    todays_predictions = {}

    import threading
    num_threads = len(rides)

    threads = []
    for i in range(num_threads):
        print(rides[i-1])
        ride = rides[i-1]
        current_ride = starter_data.copy()
        current_ride = starter_data[current_ride['RideId'] == ride]
        process = threading.Thread(target = prediction_helper.make_daily_prediction, args = [current_ride,ride,time_list, best_params, todays_predictions, todays_hours])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    more_predictions = pd.DataFrame()
    for key,value in todays_predictions.items():
        current_frame = value['predictions']
        current_frame = current_frame[['RideId','Time','predicted_wait','confidence_high','confidence_low']]
        current_frame.columns = ['RideId','Time','PredictedWait','ConfidenceHigh','ConfidenceLow']
        current_frame['PredictedWait'] = [int(str(x).split(".")[0]) for x in current_frame['PredictedWait']]
        current_frame['ConfidenceHigh'] = [int(str(x).split(".")[0]) for x  in current_frame['ConfidenceHigh']]
        current_frame['ConfidenceLow'] = [int(str(x).split(".")[0]) for x in current_frame['ConfidenceLow']]
        more_predictions = pd.concat([more_predictions, current_frame])


    all_predictions = pd.concat([all_predictions, more_predictions])

rides_not_predicted = [x for x in RideIds if x not in list(set(all_predictions["RideId"]))]
if len(rides_not_predicted) > 0:
    best_params = {'criterion': 'mse',
     'max_depth': 10,
     'max_features': 'auto',
     'min_samples_leaf': 5,
     'min_samples_split': 2,
     'n_estimators': 100}

    #rides = list(set(starter_data['Name']))
    rides = rides_not_predicted
    todays_predictions = {}

    import threading
    num_threads = len(rides)

    threads = []
    for i in range(num_threads):
        print(rides[i-1])
        ride = rides[i-1]
        current_ride = starter_data.copy()
        current_ride = starter_data[current_ride['RideId'] == ride]
        process = threading.Thread(target = prediction_helper.make_daily_prediction, args = [current_ride,ride,time_list, best_params, todays_predictions, todays_hours])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    more_predictions = pd.DataFrame()
    for key,value in todays_predictions.items():
        current_frame = value['predictions']
        current_frame = current_frame[['RideId','Time','predicted_wait','confidence_high','confidence_low']]
        current_frame.columns = ['RideId','Time','PredictedWait','ConfidenceHigh','ConfidenceLow']
        current_frame['PredictedWait'] = [int(str(x).split(".")[0]) for x in current_frame['PredictedWait']]
        current_frame['ConfidenceHigh'] = [int(str(x).split(".")[0]) for x  in current_frame['ConfidenceHigh']]
        current_frame['ConfidenceLow'] = [int(str(x).split(".")[0]) for x in current_frame['ConfidenceLow']]
        more_predictions = pd.concat([more_predictions, current_frame])


    all_predictions = pd.concat([all_predictions, more_predictions])

print("Saving predictions")

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)
cur = conn.cursor()
query = "delete from DisneyDB.Ride_Waits_Today_Predicted where RideId > 0"
cur.execute(query)
conn.commit()

for index,row in all_predictions.iterrows():
    query = "insert into DisneyDB.Ride_Waits_Today_Predicted (RideId, Time, PredictedWait, ConfidenceHigh, ConfidenceLow) values (%i, '%s', %i, %i, %i)" %(row['RideId'], row['Time'], row['PredictedWait'], row['ConfidenceHigh'],row['ConfidenceLow'])
    cur.execute(query)
    conn.commit()

print("Saving predictions, function complete")
