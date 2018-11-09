import config
import pymysql
from twilio.rest import Client
import pandas as pd
from datetime import datetime
from pytz import timezone

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)

notifications_table = pd.read_sql_query("select * from DisneyDB.User_Notifications", conn)

users_list = list(notifications_table['UserId'].unique())

#delete any notifications that are invalid
for user in users_list:
    invalid_rides = []
    user_frame = notifications_table[notifications_table['UserId'] == user]
    rides_to_check = list(user_frame['RideId'].unique())
    user_favorites = pd.read_sql_query("select * from DisneyDB.User_Ride_Favorites where UserId = " + str(user), conn)
    for ride in rides_to_check:
        ride_frame = user_frame[user_frame['RideId'] == ride]
        ride_details = pd.read_sql_query("select * from DisneyDB.Ride where Id = " + str(ride), conn)
        park_id = ride_details['ParkId'].iloc[0]
        date = pd.to_datetime(ride_frame['DateEnd']).iloc[0].date()
        print(date)
        tz = timezone('US/Eastern')
        if (park_id == 10) or (park_id == 11):
            tz = timezone('US/Pacific')

        current_date = datetime.now(tz).date()
        if (current_date >  date):
            invalid_rides.append(ride)


        ride_in_favorites = user_favorites[user_favorites['RideId'] == ride]
        if ride_in_favorites.shape[0] <1:
            invalid_rides.append(ride)

    if len(invalid_rides) > 0:
        invalid_rides = [str(x) for x in invalid_rides]
        invalid_rides_string = ",".join(invalid_rides)
        query = "delete from DisneyDB.User_Notifications where UserId = "+str(user)+" and RideId in (" + invalid_rides_string +")"
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

notifications_table = pd.read_sql_query("select * from DisneyDB.User_Notifications", conn)
users_list = list(notifications_table['UserId'].unique())


#inner loop over all rides in the users frame
for user in users_list:
    user_frame = notifications_table[notifications_table['UserId'] == user]
    user_frame['DateStart'] = pd.to_datetime(user_frame['DateStart'])
    user_frame['DateStart'] = [x.date() for x in user_frame['DateStart']]


    rides_to_check = list(user_frame['RideId'].unique())
    rides_to_check_str = [str(x) for x in rides_to_check]
    rides_string = ",".join(rides_to_check_str)
    check_operational_query = "select * from DisneyDB.Ride_Current_Status where RideId in (" + rides_string +")"
    check_operational = pd.read_sql_query(check_operational_query, conn)
    rides = list(check_operational[check_operational['Status'] == "Operating"]['RideId'].unique())
    for ride in rides:
        print(ride)
        ride_frame = user_frame[user_frame['RideId'] == ride]
        start_date = ride_frame['DateStart'].iloc[0]
        get_name_query = "select * from DisneyDB.Ride where Id = "+ str(ride)
        get_name = pd.read_sql_query(get_name_query, conn)
        park_id = get_name['ParkId'].iloc[0]
        tz = timezone('US/Eastern')
        if (park_id == 10) or (park_id == 11):
            tz = timezone('US/Pacific')

        current_date = datetime.now(tz).date()

        if current_date<start_date:
            #print("too early for this one")
            continue

        name = get_name['Name'].iloc[0]
        ride_lat = get_name['Latitude'].iloc[0]
        ride_lng = get_name['Longitude'].iloc[0]
        waits_query = "select * from DisneyDB.Ride_Waits_Today rwt join DisneyDB.Ride_Waits_Today_Predicted rwtp on rwt.RideId = rwtp.RideId and LEFT(rwt.Time,4) = LEFT(rwtp.Time,4) where rwt.RideId =" + str(ride)
        waits = pd.read_sql_query(waits_query, conn)
        current_time = waits.iloc[waits.shape[0]-1]
        if current_time['Wait'] < current_time['ConfidenceLow']:
            message = "Wait for " + name + " Much lower than expected! GO NOW for "+ str(current_time['Wait']) +" minute wait. To navigate now go here: https://www.google.com/maps/dir//" + str(ride_lat) + ","+str(ride_lng) + "/ - Your friendly Disney Waits Notification!"
            account_sid = config.twilio_account_num
            auth_token = config.twilio_auth_token
            client = Client(account_sid, auth_token)
            client.messages.create(
              to=str(user_frame['PhoneNumber'].iloc[0]),
              from_=config.twilio_number,
              body=message)

        else:
            print(name + " wait is not lower")
# check check to see if the current wait is outside the cofidence interval

# grab current wait time, grab predictions from right now, check how it falls in the confidence interval
