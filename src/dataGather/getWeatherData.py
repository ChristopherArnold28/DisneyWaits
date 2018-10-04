import pyowm
import config
import pymysql
import re
from datetime import datetime
from pytz import timezone
import pandas as pd

owm = pyowm.OWM(config.weatherAPI)
conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)
#observations = owm.weather_at_place('Bay Lake,US')

#get the list of park to loop through
query = "select * from DisneyDB.Park"
parks_table = pd.read_sql_query(query, conn)

for index,row in parks_table.iterrows():
    tz = timezone('US/Eastern')
    park_db_id = row['Id']
    park_latitude = row['Latitude']
    park_longitude = row['Longitude']

    obs = owm.weather_at_coords(park_latitude, park_longitude)
    weather = obs.get_weather()

    status = weather.get_detailed_status()
    temp = weather.get_temperature('fahrenheit')['temp']
    simple_status = weather.get_status()
    rain_accumulation = weather.get_rain()
    if len(rain_accumulation.keys()) < 1:
        rain_accumulation = 0
    else:
        rain_accumulation = rain_accumulation['3h']
    cloud_cover = weather.get_clouds()
    icon_name = weather.get_weather_icon_name()

    cur = conn.cursor()
    if (park_db_id == 10) or (park_db_id == 11):
        tz = timezone('US/Pacific')
    time = datetime.now(tz)
    date = time.date()
    time = time.time().strftime("%H:%M")

    insert_weather = "insert into DisneyDB.Weather (Date , Time, Status, Temperature, CloudCover, SimpleStatus, RainAccumulation,IconName,ParkId) values ('"+str(date) + "','" +str(time) + "','"+ status + "'," + str(temp) + ","+ str(cloud_cover) + ",'"+ simple_status + "'," + str(rain_accumulation) +",'"+ str(icon_name) + "',"+str(park_db_id) + ")"
    cur.execute(insert_weather)
    conn.commit()
