from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
from datetime import datetime
from pytz import timezone
tz = timezone('US/Eastern')
time = datetime.now(tz)
date = time.date()

link = "https://disneyworld.disney.go.com/calendars/day/"+str(date)+"/"
response = requests.get(link)
content = response.content

parser = BeautifulSoup(content, "html.parser")
parks = parser.find_all('li',itemtype = "http://schema.org/TouristAttraction")

parksHours = []

for park in parks:
    parkName = park.find_all("div", class_ = "pkTitle noMarginTop")[0].text.strip()
    parkName = parkName.replace("Park","")
    parkName = parkName.replace("Disney's","")
    parkName = parkName.replace("Hours","")
    parkName = parkName.strip()
    parkName = parkName.replace("Epcot","EpCot")
    parkHours = park.find_all("div", class_ = "hours operating")[0].text
    hours = parkHours.split(" to ")
    parkOpen = hours[0]
    parkClose = hours[1]
    emhHours = park.find_all("div", class_ = "hours extraMagicHours")
    if len(emhHours)>0:
        emhHours = emhHours[0].text.replace("Extra Magic Hours", "")
        emhHours = emhHours.replace(u"\u2013","")
        emhHours = emhHours.strip()
        ehours = emhHours.split(" to ")
        emhStart = ehours[0]
        emhEnd = ehours[1]
    else:
        emhHours = "None"
        emhStart = "None"
        emhEnd = "None"


    parkHours = {"parkName" : parkName,
                "parkStartTime": parkOpen,
                "parkCloseTime": parkClose,
                "emhStart": emhStart,
                "emhEnd": emhEnd}
    parksHours.append(parkHours)
#print(parksHours)

import pymysql
import config

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)
cur = conn.cursor()
for parkHour in parksHours:
    #print(parkHour["parkName"])
    getParkId = "select * from DisneyDB.Park where Name = '"+ parkHour["parkName"]+ "'"
    df = pd.read_sql_query(getParkId, conn)
    #print(df)
    parkId = df["Id"][0]
    insertParkHours = "insert into DisneyDB.ParkHours (Date, ParkId, ParkOpen, ParkClose, EMHOpen, EMHClose) values ('"+str(date)+"',"+str(parkId)+",'"+str(parkHour["parkStartTime"])+"','"+str(parkHour["parkCloseTime"])+"','"+str(parkHour["emhStart"]) + "','"+str(parkHour["emhEnd"]) + "')"
    cur.execute(insertParkHours)
conn.commit()
