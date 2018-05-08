from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import pymysql

locations = [{"name":"Magic Kingdom", "linkName":"magic-kingdom"},
            {"name":"EpCot","linkName":"epcot"},
            {"name":"Hollywood Studios","linkName":"hollywood-studios"},
            {"name":"Animal Kingdom","linkName":"animal-kingdom"}]
import config

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)

cur = conn.cursor()

for location in locations:
    locationName = location["name"]
    linkName = location["linkName"]
    locationQuery = "select * from DisneyDB.Park where name = '" + locationName +"'"
    df = pd.read_sql_query(locationQuery,conn)
    if len(df.index) == 0:
        insertLocation = "insert into DisneyDB.Park (Name) values ('"+ locationName + "')"
        cur.execute(insertLocation)
        df = pd.read_sql_query(locationQuery,conn)
        conn.commit()
    locationId = df['Id'][0]
    siteString = "https://touringplans.com//" + linkName + "/attractions.json"
    r = requests.get(siteString)
    jsonData = r.json()
    #print(jsonData)
    for ride in jsonData:
        tableName = ride["name"]
        rideName = ride["permalink"]
        #tableName = tableName.replace(" ", "-")
        tableName = tableName.replace("'","")
        tableName = tableName.replace(u"\u2019","")
        tableName = tableName.replace("&", "and")
        tableName = tableName.replace(": "," - ")
        print(rideName)
        attractionString = "https://touringplans.com/"+linkName+"/attractions/"+rideName+".json"
        rideRequest = requests.get(attractionString)
        rideJson = rideRequest.json()
        #print(rideJson["name"] + " opened on " + str(rideJson["opened_on"]))
        rideQuery = "select * from DisneyDB.Ride where name = '"+ tableName + "'"
        rideTable = pd.read_sql_query(rideQuery, conn)
        if len(rideTable.index) == 0:
            insertRide = "insert into DisneyDB.Ride (Name, OpeningDate, Tier, ParkId) values ('" + tableName + "','"+ str(rideJson["opened_on"]) + "','"+ str(rideJson["scope_and_scale_code"])+ "',"+str(locationId)+")"
        else:
            rideId = rideTable['Id'][0]
            insertRide = "update DisneyDB.Ride set OpeningDate='"+ str(rideJson["opened_on"]) + "', Tier = '"+ str(rideJson["scope_and_scale_code"])+ "', ParkId = "+str(locationId)+" where Id = "+ str(rideId)
        cur.execute(insertRide)
        conn.commit()
