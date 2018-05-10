import pandas as pd
import numpy as np
from datetime import datetime

RideWaits = pd.read_csv("******/DisneyWaitTimes/DisneyWaits/src/disneyWaitTimes.csv")

#print(RideWaits.head())

RideWaits["RideId"] = pd.Categorical(RideWaits["RideId"]).codes
RideWaits["Status"] = pd.Categorical(RideWaits["Status"]).codes
RideWaits["ParkId"] = pd.Categorical(RideWaits["ParkId"])
RideWaits["Tier"] = pd.Categorical(RideWaits["Tier"])


#want to create some more intersting columns:
#- character experience
#- involves a princess
#- age of ride
#- hours since park open
#- hours until park close
#- emh that day or not
#- remove times after close or before open
#- get day of the week
#- month
#print(RideWaits["ParkOpen"].value_counts())
#print(RideWaits["EMHOpen"].value_counts())
RideWaits["Date"] = pd.to_datetime(RideWaits["Date"], infer_datetime_format = True)
RideWaits["OpeningDate"] = pd.to_datetime(RideWaits["OpeningDate"], infer_datetime_format = True)
RideWaits["Time"] = pd.to_datetime(RideWaits["Time"], format = '%H:%M').dt.time
RideWaits["ParkOpen"] = pd.to_datetime(RideWaits["ParkOpen"], format = '%I:%M %p').dt.strftime('%H:%M')
RideWaits["ParkOpen"] = pd.to_datetime(RideWaits["ParkOpen"], format = '%H:%M').dt.time
RideWaits["ParkClose"] = pd.to_datetime(RideWaits["ParkClose"], format = '%I:%M %p').dt.strftime('%H:%M')
RideWaits["ParkClose"] = pd.to_datetime(RideWaits["ParkClose"], format = '%H:%M').dt.time
RideWaits["DayOfWeek"] = [datetime.weekday(x) for x in RideWaits["Date"]]
RideWaits["EMHOpen"] = pd.to_datetime(RideWaits["EMHOpen"], format = '%I:%M %p', errors = 'coerce').dt.strftime('%H:%M')
RideWaits["EMHClose"] = pd.to_datetime(RideWaits["EMHClose"], format = '%I:%M %p', errors = 'coerce').dt.strftime('%H:%M')
RideWaits["EMHOpen"] = pd.to_datetime(RideWaits["EMHOpen"], format = '%H:%M', errors = 'coerce').dt.time
RideWaits["EMHClose"] = pd.to_datetime(RideWaits["EMHClose"], format = '%H:%M', errors = 'coerce').dt.time

validTime = []
inEMH = []
emhDay = []

for index, row in RideWaits.iterrows():
    tempTime = datetime.now()
    cTime = row["Time"]
    pOpen = row["ParkOpen"]
    pClose = row["ParkClose"]
    currentParkTime = tempTime.replace(hour = cTime.hour, minute = cTime.minute, second = 0, microsecond = 0)
    parkOpen = tempTime.replace(hour = pOpen.hour, minute = pOpen.minute, second = 0, microsecond = 0)
    parkClose = tempTime.replace(hour = pClose.hour, minute = pClose.minute, second = 0, microsecond = 0)
    if parkClose < parkOpen:
        parkClose = parkClose.replace(day = parkClose.day + 1)
    if (pd.isnull(row["EMHOpen"])== False) & (pd.isnull(row["EMHClose"]) == False):
        eOpen = row["EMHOpen"]
        eClose = row["EMHClose"]
        emhOpen = tempTime.replace(hour = eOpen.hour, minute = eOpen.minute, second = 0, microsecond = 0)
        emhClose = tempTime.replace(hour = eClose.hour, minute = eClose.minute, second = 0, microsecond = 0)
        if emhClose < emhOpen:
            emhClose = emhClose.replace(day = emhClose.day + 1)
        emh = "ok"
        emhDay.append(1)
    else:
        emh = "none"
        emhDay.append(0)
    if (currentParkTime < parkClose) & (currentParkTime > parkOpen):
        validtime = 1
        inemh = 0
        #print("Current Time is: " + str(currentParkTime) + " and ParkHours are "+ str(parkOpen) +" to " + str(parkClose) + " " +str(validtime))
        validTime.append(1)
        inEMH.append(0)
    else:
        if (emh == "ok") & ((currentParkTime < emhClose) & (currentParkTime > emhOpen)):
            validTime.append(1)
            inEMH.append(1)
        else:
            validTime.append(0)
            inEMH.append(0)

RideWaits["inEMH"] = inEMH
RideWaits["validTime"] = validTime
RideWaits["EMHDay"] = emhDay
RideWaits = RideWaits[RideWaits["validTime"] == 1]
