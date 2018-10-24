import pymysql
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import transformations
import config


conn = pymysql.connect(config.host, user=config.username,port=config.port,passwd=config.password)

RideWaits = pd.read_sql_query("call DisneyDB.RideWaitQuery('2,7,8,9')", conn)
starter_data = RideWaits.copy()
RideWaits = transformations.transformData(RideWaits)

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


%%time
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
best_params = {'criterion': 'mse',
 'max_depth': 10,
 'max_features': 'auto',
 'min_samples_leaf': 5,
 'min_samples_split': 2,
 'n_estimators': 100}

rides = list(set(starter_data['Name']))
global todays_predictions
todays_predictions = {}

import threading
num_threads = len(rides)

threads = []
for i in range(num_threads):
    #print(rides[i-1])
    ride = rides[i-1]
    current_ride = starter_data.copy()
    current_ride = starter_data[current_ride['Name'] == ride]
    process = threading.Thread(target = make_daily_prediction, args = [current_ride,ride,time_list, best_params, todays_predictions])
    process.start()
    threads.append(process)

for process in threads:
    process.join()

all_predictions = pd.DataFrame()
for key,value in todays_predictions.items():
    current_frame = value['predictions']
    current_frame = current_frame[['RideId','Time','predicted_wait']]
    current_frame.columns = ['RideId','Time','PredictedWait']
    current_frame['PredictedWait'] = [int(str(x).split(".")[0]) for x in current_frame['PredictedWait']]
    all_predictions = pd.concat([all_predictions, current_frame])

cur = conn.cursor()
for index,row in all_predictions.iterrows():
    query = "insert into DisneyDB.Ride_Waits_Today_Predicted (RideId, Time, PredictedWait) values (%i, '%s', %i)" %(row['RideId'], row['Time'], row['PredictedWait'])
    cur.execute(query)
    conn.commit()




def make_daily_prediction(current_ride,ride, time_list, best_params, todays_predictions):
    ride_predictions = {}
    current_ride_fm = current_ride.copy()
    current_ride_fm = transformations.transformData(current_ride_fm)
    #print(current_ride.shape[0])
    #print(current_ride.columns)
    model_data = model_transformation(current_ride_fm, 1)
    important_columns = [x for x in model_data.columns if x != "Wait"]
    clf = RandomForestRegressor(**best_params)
    #scores = cross_val_score(clf, model_data[important_columns],model_data['Wait'], scoring = "neg_median_absolute_error", cv = 3)
    #ride_score = scores.mean()
    #ride_predictions['score'] = ride_score
    #print(model_data.head())
    clf.fit(model_data[important_columns], model_data['Wait'])
    predictions_frame = pd.DataFrame()
    ride_starter = current_ride.iloc[[0]]

    predictions_frame = pd.concat([ride_starter]*len(time_list),ignore_index = True)
    predictions_frame['Time'] = time_list
    predictions_frame = transformations.transformData(predictions_frame)
    # print(predictions_frame)
    #predictions_frame = transformations.transformData(predictions_frame)
    model_predictions_frame = new_data_transform(predictions_frame, 3, important_columns)
    predictions_frame['predicted_wait'] = clf.predict(model_predictions_frame[important_columns])
    predictions_frame = predictions_frame.round({'predicted_wait': 2})


#     for time in time_list:
#         ride_starter['Time'] = time
#         row_data = ride_starter.copy()
#         #print(row_data)
#         try:
#             row_data = transformations.transformData(row_data)
#         except:
#             continue
#         #print(row_data)
#         predictions_frame = pd.concat([predictions_frame,row_data])
#         #print(predictions_frame.iloc[[predictions_frame.shape[0]-1]])
#         model_predictions_frame = new_data_transform(predictions_frame,3, important_columns)
#         predictions_frame['Wait'] = clf.predict(model_predictions_frame[important_columns])
#         #print(predictions_frame)

    ride_predictions['predictions'] = predictions_frame
    todays_predictions[ride] = ride_predictions



def create_dummies(df,column_name):
    dummies = pd.get_dummies(df[column_name],prefix=column_name)
    df = pd.concat([df,dummies],axis=1)
    df = df.drop([column_name], axis = 1)
    return df

def get_shift(day, steps):
    previous_steps = {}
    for i in range(1,1+steps):
        current_steps = []
        test_day_current = day.reset_index()
        for index,row in test_day_current.iterrows():
            if index in list(range(i)):
                current_steps.append(0)
            else:
                current_steps.append(test_day_current.loc[index - i,'Wait'])

        name = "previous_step"+str(i)
        previous_steps[name] = current_steps

    for key,value in previous_steps.items():
        day[key] = value

    return day


def shift_data(ride_data, shift_range):
    new_data_frame = pd.DataFrame()
    distinct_rides = list(ride_data['RideId'].unique())
    for ride in distinct_rides:
        this_ride = ride_data[ride_data['RideId'] == ride]
        day_list = list(this_ride['Date'].unique())
        for day in day_list:
            day_data = this_ride[this_ride['Date'] == day]
            new_data = get_shift(day_data, shift_range)
            new_data_frame = pd.concat([new_data_frame, new_data])

    return new_data_frame

def model_transformation(data, num_shifts, start_day = True, by_ride = True):
    ride_waits = data

    if by_ride:
        important_columns = ['Wait','DayOfWeek','Weekend','inEMH','EMHDay','MagicHourType','Month','TimeSinceOpen','TimeSinceMidday','MinutesSinceOpen']
        dummy_columns = ['DayOfWeek','Weekend','inEMH','EMHDay','MagicHourType','Month']
    else:
        important_columns = ['RideId','Date', 'Wait','Name','Tier','Location','IntellectualProp','ParkId','DayOfWeek','Weekend','CharacterExperience','inEMH','EMHDay','TimeSinceOpen','TimeSinceMidday','MagicHourType','MinutesSinceOpen','Month']
        ride_waits = ride_waits[ride_waits['Location'] != ""]
        dummy_columns = ['RideId','Tier','Location','IntellectualProp','ParkId','DayOfWeek','Weekend','CharacterExperience','inEMH','EMHDay','MagicHourType','Month']
        ride_waits = ride_waits.drop(['Name'], axis = 1)
    ride_waits = ride_waits[important_columns]
    ride_waits = ride_waits.dropna(how = "any")

    if start_day == False:
        ride_waits = shift_data(ride_waits,num_shifts)

    for column in dummy_columns:
        ride_waits = create_dummies(ride_waits, column)

    correlation = ride_waits.corr()['Wait']
    key_correlations = correlation[abs(correlation) > .005]
    important_cols = list(key_correlations.index)
    shift_columns = []
    if start_day == False:
        shift_columns = ["previous_step" + str(x+1)  for x in range(num_shifts)]
    important_cols = important_cols + ["Wait","MinutesSinceOpen"] + shift_columns
    important_cols = [x for x in important_cols if x != "Weekend_0"]
    important_cols = list(set(important_cols))
    ride_waits_key = ride_waits[important_cols]


    return ride_waits_key



def new_data_transform(data, num_shifts, important_cols, start_day = True, by_ride = True):
    ride_waits = data

    if by_ride:
        important_columns = ['Wait','DayOfWeek','Weekend','inEMH','EMHDay','MagicHourType','Month','TimeSinceOpen','TimeSinceMidday','MinutesSinceOpen']
        dummy_columns = ['DayOfWeek','Weekend','inEMH','EMHDay','MagicHourType','Month']
    else:
        important_columns = ['RideId','Date', 'Wait','Name','Tier','Location','IntellectualProp','ParkId','DayOfWeek','Weekend','CharacterExperience','inEMH','EMHDay','TimeSinceOpen','TimeSinceMidday','MagicHourType','MinutesSinceOpen','Month']
        ride_waits = ride_waits[ride_waits['Location'] != ""]
        dummy_columns = ['RideId','Tier','Location','IntellectualProp','ParkId','DayOfWeek','Weekend','CharacterExperience','inEMH','EMHDay','MagicHourType','Month']
        ride_waits = ride_waits.drop(['Name'], axis = 1)


    ride_waits = ride_waits[important_columns]

    ride_waits = ride_waits.dropna(how = "any")

    if start_day == False:
        ride_waits = shift_data(ride_waits,num_shifts)
    for column in dummy_columns:
        ride_waits = create_dummies(ride_waits, column)

    missing_cols = [x for x in important_cols if x not in ride_waits.columns]
    for col in missing_cols:
        ride_waits[col] = 0

    return ride_waits
