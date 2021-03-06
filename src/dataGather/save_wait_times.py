import config
import disney_parks
import pymysql
import pandas as pd
from disney_attractions import Attraction
from disney_entertainment import Entertainment
from datetime import datetime
from pytz import timezone


conn = pymysql.connect(config.host, user=config.username,port=config.port,passwd=config.password)
cur = conn.cursor()

park_ids = open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/parkIds.txt", "r")
string = park_ids.read()
park_list = str.splitlines(string)
ids = [x.split(':')[-1] for x in park_list]

att_ids = open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/attractionIds.txt", "r")
string = att_ids.read()
att_list = str.splitlines(string)
attraction_ids = [x.split(':')[-1] for x in att_list]

ent_ids = open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/entertainment.txt", "r")
string = ent_ids.read()
ent_list = str.splitlines(string)
entertainment_ids = [x.split(':')[-1] for x in ent_list]

exc = open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/exclude_list.txt", "r")
string = exc.read()
exc_list = str.splitlines(string)
exclude_list = [x.split(':')[-1] for x in exc_list]

for current_id in ids:
    tz = timezone('US/Eastern')
    park = disney_parks.Park(current_id)
    current_park_name = park.getParkName().replace("'","")
    print("Working On Park:" + str(current_park_name))

    query = "select * from DisneyDB.Park where Name = '" + current_park_name + "'"
    park_table = pd.read_sql_query(query, conn)
    if park_table.shape[0] < 1:
        insert_park = "insert into DisneyDB.Park (Name) values ('%s')" %(current_park_name)
        cur.execute(insert_park)
        conn.commit()
        park_table = pd.read_sql_query(query, conn)

    park_db_id = park_table['Id'][0]
    if (park_db_id == 10) or (park_db_id == 11):
        tz = timezone('US/Pacific')
    #get our wait times

    time = datetime.now(tz)
    date = time.date()
    time = time.time().strftime("%H:%M")

    wait_times = park.getCurrentWaitTimes()
    for key, wait_dict in wait_times.items():
        is_attraction = False
        is_entertainment = False
        if key in attraction_ids:
            is_attraction = True
            #print("this is an attraction")
        elif key in entertainment_ids:
            is_entertainment = True
            #print("this is entertainment")
        elif key in exclude_list:
            print("exclude this ride")
            continue
        else:
            check_sum = 0
            print("new key: "+ str(key))
            #print(wait_dict)
            try:
                Attraction(str(key))
                print("Worked as an attraction with key: " + str(key))
                ### write to the attractions.txt file and move forward
                current_attraction = Attraction(str(key))
                name = current_attraction.getAttractionName()
                name = name.replace(":"," ")
                file_string = "\n"+name+":"+str(key)
                with open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/attractionIds.txt","a") as myfile:
                    myfile.write(file_string)
                is_attraction = True
            except:
                print("not an attraction")
                check_sum = check_sum + 1

            try:
                Entertainment(str(key))
                print("Worked as an entertainment with key: " + str(key))
                ###write to the entertainments.txt file and move forward with this key
                current_entertainment = Entertainment(str(key))
                name = current_entertainment.getEntertainmentName()
                name = name.replace(":"," ")
                file_string = "\n"+name+":"+str(key)
                with open("/home/ec2-user/DisneyWaitTimes/DisneyWaits/src/dataGather/entertainment.txt","a") as myfile:
                    myfile.write(file_string)
                is_entertainment = True
            except:
                print("not an entertainment")
                check_sum = check_sum + 1

            if check_sum == 2:
                continue

        #print(key)
        #print(wait_dict)
        #check if that id exists in the ride table
        key = key.strip()
        search_query = "select * from DisneyDB.Ride where Id = " + key
        ride_table = pd.read_sql_query(search_query, conn)
        #print(ride_table.shape)
        if ride_table.shape[0] < 1:
            if is_attraction:
                print("saving a new attraction" + str(key))
                current_attraction = Attraction(str(key))
                name = current_attraction.getAttractionName()
                #print(name)
                location = current_attraction.getAncestorLand()

            elif is_entertainment:
                print("saving a new entertainment" + str(key))
                current_entertainment = Entertainment(str(key))
                name = current_entertainment.getEntertainmentName()
                #print(name)
                location = current_entertainment.getAncestorLand()

            query = "insert into DisneyDB.Ride (Id, Name, Location, ParkId) values (%i, '%s', '%s', %i)"%(int(key),name,location,park_db_id)
            #print(query)
            cur.execute(query)
            conn.commit()

            ride_table = pd.read_sql_query(search_query, conn)

        db_ride_id = ride_table["Id"][0]


        if 'wait_time' in wait_dict:
            current_wait = wait_dict['wait_time']
            query = "insert into DisneyDB.Ride_Waits_Today (RideId, Date, Time, Wait) values (%i, '%s','%s', %i)"%(db_ride_id, date, time, current_wait)
            cur.execute(query)
            conn.commit()

        current_status = "No Status to Report"
        fastpass_availability = "Not a fastpass attraction"
        if 'status' in wait_dict:
            current_status = wait_dict['status']

        if 'fast_pass_info' in wait_dict:
            fast_pass_dict = wait_dict['fast_pass_info']
            if fast_pass_dict['available'] == True:
                if 'startTime' in fast_pass_dict:
                    if fast_pass_dict['startTime'] == "FASTPASS is Not Available":
                        fastpass_availability = "FASTPASS+ attraction, please check in park kiosk for next available window"
                    if 'endTime' in fast_pass_dict:
                        startTime = fast_pass_dict['startTime'][0:5]
                        endTime = fast_pass_dict['endTime'][0:5]
                        endTimeDate = datetime.strptime(endTime,"%H:%M").strftime("%I:%M %p")
                        startTimeDate = datetime.strptime(startTime, "%H:%M").strftime("%I:%M %p")
                        endTimeString = str(endTimeDate)
                        startTimeString = str(startTimeDate)
                        endTimeString = endTimeString[1:] if endTimeString.startswith("0") else endTimeString
                        startTimeString = startTimeString[1:] if startTimeString.startswith("0") else startTimeString
                        fastpass_availability = "Next Fastpass  between " + startTimeString + " - " + endTimeString
                else:
                    fastpass_availability = "FASTPASS+ attraction, please check in park kiosk for next available window"
            if fast_pass_dict['available'] == False:
                fastpass_availability = "Not a fastpass attraction"
        query = "replace into DisneyDB.Ride_Current_Status (RideId, Status, FastPassAvailable) values (%i, '%s', '%s')"%(db_ride_id, current_status, fastpass_availability)
        cur.execute(query)
        conn.commit()




print("success at " + str(time))
