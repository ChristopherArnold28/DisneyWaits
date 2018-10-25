from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import pymysql
import pandas as pd
import numpy as np
import transformations
import config



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




def get_conf_interval(clf, df):
    conf_high_list = []
    conf_low_list = []
    for index, row in df.iterrows():
        current_row = df.loc[[index]]
        all_predictions = [estimator.predict(current_row) for estimator in clf.estimators_]
        mean = np.mean(all_predictions)
        pred_std = np.std(all_predictions)
        conf_high = (mean + 2*pred_std)
        conf_low = (mean - 2*pred_std)
        conf_high_list.append(conf_high)
        conf_low_list.append(conf_low)

    df['confidence_high'] = conf_high_list
    df['confidence_low'] = conf_low_list
    return df



def make_daily_prediction(current_ride,ride, time_list, best_params, todays_predictions, todays_hours):
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
    #need to change the park hours and date
    current_park_id = predictions_frame['ParkId'][0]
    todays_hours = park_hours[park_hours['ParkId'] == current_park_id]
    todays_date = todays_hours['Date'].iloc[0]
    park_open = todays_hours['ParkOpen'].iloc[0]
    park_close = todays_hours['ParkClose'].iloc[0]
    emh_open = todays_hours['EMHOpen'].iloc[0]
    emh_close = todays_hours['EMHClose'].iloc[0]

    predictions_frame['Date'] = todays_date
    predictions_frame['EMHOpen'] = emh_open
    predictions_frame['ParkOpen'] = park_open
    predictions_frame['ParkClose'] = park_close
    predictions_frame['EMHClose'] = emh_close


    predictions_frame['Time'] = time_list
    predictions_frame = transformations.transformData(predictions_frame)
    # print(predictions_frame)
    #predictions_frame = transformations.transformData(predictions_frame)
    model_predictions_frame = new_data_transform(predictions_frame, 3, important_columns)
    predictions_frame['predicted_wait'] = clf.predict(model_predictions_frame[important_columns])
    model_predictions_frame = get_conf_interval(clf,model_predictions_frame[important_columns])
    predictions_frame['confidence_high'] = model_predictions_frame['confidence_high']
    predictions_frame['confidence_low'] = model_predictions_frame['confidence_low']

    ride_predictions['predictions'] = predictions_frame
    todays_predictions[ride] = ride_predictions
