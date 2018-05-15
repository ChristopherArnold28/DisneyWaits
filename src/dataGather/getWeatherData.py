import pyowm
import config
owm = pyowm.OWM(config.weatherAPI)
#observations = owm.weather_at_place('Bay Lake,US')

reg = owm.city_id_registry()
ids = reg.ids_for('Celebration')
id = ids[0][0]

obs = owm.weather_at_id(id)
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

import pymysql
import re
from datetime import datetime
from pytz import timezone
tz = timezone('US/Eastern')
import config

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)
location = "Disney World"
cur = conn.cursor()
time = datetime.now(tz)
date = time.date()
time = time.time().strftime("%H:%M")

insert_weather = "insert into DisneyDB.Weather (Date , Time, Status, Temperature, CloudCover, SimpleStatus, RainAccumulation,Location) values ('"+str(date) + "','" +str(time) + "','"+ status + "'," + str(temp) + ","+ str(cloud_cover) + ",'"+ simple_status + "'," + str(rain_accumulation) +",'"+ location+"')"
cur.execute(insert_weather)
conn.commit()
