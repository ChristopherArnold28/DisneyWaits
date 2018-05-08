
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

response = requests.get("https://www.easywdw.com/waits/?park=All")
content = response.content

parser = BeautifulSoup(content, "html.parser")
waits = parser.find_all("tr")
waits = waits[1:]

waitTimes = []

for item in waits:
    current_ride = {}
    table_data = item.find_all("td")
    ride_name = table_data[0].text
    current_ride["ride_name"] = ride_name
    current_ride["location"] = table_data[1].text
    current_ride["wait_time"] = table_data[2].text
    waitTimes.append(current_ride)

ride_table = pd.DataFrame(waitTimes[0:])
#print(ride_table)

import pymysql
import re
from datetime import datetime
from pytz import timezone
tz = timezone('US/Eastern')
import config

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)

cur = conn.cursor()
time = datetime.now(tz)
date = time.date()
time = time.time().strftime("%H:%M")

for index, ride in ride_table.iterrows():
    ride_name = ride["ride_name"]
    location = ride["location"]
    wait_time = ride["wait_time"]
    ride_name = ride_name.replace("'","")
    ride_name = ride_name.replace(u"\u2019","")
    location = location.replace("'","")
    wait_time = wait_time.replace(" Min", "")
    #print(ride_name)
    look_for_ride = "select * from DisneyDB.Ride where Name = '" + ride_name + "'"
    #print(look_for_ride)
    df = pd.read_sql_query(look_for_ride, conn)
    #print(df)
    if len(df.index) == 0:
        insert_ride = "insert into DisneyDB.Ride (Name, Location) values ('" + ride_name + "','" + location + "')"
        cur.execute(insert_ride)
        df = pd.read_sql_query(look_for_ride,conn)
        #print(df)
    conn.commit()
    #print(time)
    ride_id = df['Id'][0]
    insert_wait = "insert into DisneyDB.Ride_Waits (RideId,Date, Time, Wait) values (" + str(ride_id) + ",'"+str(date)+"','"+str(time)+"','"+ wait_time+"')"
    cur.execute(insert_wait)
    conn.commit()
print("success at " + str(time))
