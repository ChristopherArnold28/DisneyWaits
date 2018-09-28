import config
import pymysql
import pandas as pd


conn = pymysql.connect(config.host, user=config.username,port=config.port,passwd=config.password)

today_wait_times = pd.read_sql_query('select * from DisneyDB.Ride_Waits_Today', conn)
cur = conn.cursor()

for i, r in today_wait_times.iterrows():
    db_ride_id = r['RideId']
    date = r['Date']
    time = r['Time']
    current_wait = r['Wait']
    query = "insert into DisneyDB.Ride_Waits (RideId, Date, Time, Wait) values (%i, '%s','%s', %i)"%(db_ride_id, date, time, current_wait)
    cur.execute(query)

query = 'delete from DisneyDB.Ride_Waits_Today where id >0'

cur.execute(query)
conn.commit()
