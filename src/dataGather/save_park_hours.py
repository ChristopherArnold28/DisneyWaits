import config
import disney_parks
import pymysql
import pandas as pd

park_ids = open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/parkIds.txt", "r")
string = park_ids.read()
park_list = str.splitlines(string)
ids = [x.split(':')[1] for x in park_list]

conn = pymysql.connect(config.host, user=config.username,port=config.port,passwd=config.password)
cur = conn.cursor()

for current_id in ids:
    park = disney_parks.Park(current_id)
    current_park_name = park.getParkName().replace("'","")
    query = "select * from DisneyDB.Park where Name = '" + current_park_name + "'"
    park_table = pd.read_sql_query(query, conn)
    if park_table.shape[0] < 1:
        insert_park = "insert into DisneyDB.Park (Name) values ('%s')" %(current_park_name)
        cur.execute(insert_park)
        conn.commit()
        park_table = pd.read_sql_query(query, conn)

    park_db_id = park_table['Id'][0]
    park_hours = park.getTodayParkHours()

    today = park_hours['park_open'].strftime('%Y-%m-%d')
    park_open = park_hours['park_open'].strftime('%I:%M %p') if park_hours['park_open'] is not None else 'None'
    park_close= park_hours['park_close'].strftime('%I:%M %p') if park_hours['park_close'] is not None else 'None'
    emh_open = park_hours['emh_open'].strftime('%I:%M %p') if park_hours['emh_open'] is not None else 'None'
    emh_close = park_hours['emh_close'].strftime('%I:%M %p') if park_hours['emh_close'] is not None else 'None'
    special_open = park_hours['special_open'].strftime('%I:%M %p') if park_hours['special_open'] is not None else 'None'
    special_close = park_hours['special_close'].strftime('%I:%M %p') if park_hours['special_close'] is not None else 'None'
    query = "insert into DisneyDB.ParkHours (Date, ParkId, ParkOpen, ParkClose, EMHOpen, EMHClose, SpecialOpen, SpecialClose) values ('%s', %i, '%s','%s','%s','%s','%s','%s')"%(today, park_db_id, park_open, park_close, emh_open, emh_close,special_open,special_close)
    cur.execute(query)
    conn.commit()
