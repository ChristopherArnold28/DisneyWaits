import pandas as pd
import numpy as np
from datetime import datetime

def transformData(RideWaits):
    RideWaits["RideId"] = pd.Categorical(RideWaits["RideId"]).codes
    RideWaits["Status"] = pd.Categorical(RideWaits["Status"]).codes
    RideWaits["ParkId"] = pd.Categorical(RideWaits["ParkId"])
    RideWaits["Tier"] = pd.Categorical(RideWaits["Tier"])
    RideWaits["ParkName"] = pd.Categorical(RideWaits["ParkName"])
    RideWaits["IntellectualProp"] = pd.Categorical(RideWaits["IntellectualProp"])

    #want to create some more intersting columns:
    #- is it close to a major event?(Anniversary/Christmas/Thanksgiving/Halloween)
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
    RideWaits["Weekend"] = [0 if x == 0 or x == 1 or x ==2 or x==3 or x==4 else 1 for x in RideWaits["DayOfWeek"]]
    RideWaits["Weekend"].value_counts()
    RideWaits["CharacterExperience"] = [1 if "Meet" in x else 0 for x in RideWaits["Name"]]
    validTime = []
    inEMH = []
    emhDay = []
    timeSinceStart = []
    timeSinceMidDay = []
    magicHourType = []
    timeSinceOpenMinutes = []

    for index, row in RideWaits.iterrows():
        tempTime = datetime.now()
        cTime = row["Time"]
        pOpen = row["ParkOpen"]
        pClose = row["ParkClose"]
        currentParkTime = tempTime.replace(hour = cTime.hour, minute = cTime.minute, second = 0, microsecond = 0)
        parkOpen = tempTime.replace(hour = pOpen.hour, minute = pOpen.minute, second = 0, microsecond = 0)
        parkClose = tempTime.replace(hour = pClose.hour, minute = pClose.minute, second = 0, microsecond = 0)
        if parkClose < parkOpen:
            try:
                parkClose = parkClose.replace(day = parkClose.day + 1)
            except:
                try:
                    parkClose = parkClose.replace(month = parkClose.month + 1, day = 1)
                except:
                    parkClose = parkClose.replace(year = 1, month = 1, day = 1)

        if (pd.isnull(row["EMHOpen"])== False) & (pd.isnull(row["EMHClose"]) == False):
            eOpen = row["EMHOpen"]
            eClose = row["EMHClose"]
            emhOpen = tempTime.replace(hour = eOpen.hour, minute = eOpen.minute, second = 0, microsecond = 0)
            emhClose = tempTime.replace(hour = eClose.hour, minute = eClose.minute, second = 0, microsecond = 0)
            if emhClose < emhOpen:
                try:
                    emhClose = emhClose.replace(day = emhClose.day + 1)
                except:
                    try:
                        emhClose = emhClose.replace(month = emhClose.month + 1, day = 1)
                    except:
                        emhClose = emhClose.replace(year = 1,month = 1, day = 1)
            emh = "ok"
            emhDay.append(1)
            if emhClose.hour == parkOpen.hour:
                magicHourType.append("Morning")
            else:
                magicHourType.append("Night")
        else:
            emh = "none"
            emhDay.append(0)
            magicHourType.append("None")
        if (currentParkTime < parkClose) & (currentParkTime > parkOpen):
            #print("Current Time is: " + str(currentParkTime) + " and ParkHours are "+ str(parkOpen) +" to " + str(parkClose) + " " +str(validtime))
            tSinceOpen = currentParkTime.hour - parkOpen.hour
            tSinceOpenMinutes = currentParkTime - parkOpen
            tSinceMidDay = abs(currentParkTime.hour - 14)
            if currentParkTime.hour < parkOpen.hour:
                tSinceOpen = currentParkTime.hour + 24 - parkOpen.hour
                tSinceOpenMinutes = currentParkTime.replace(day = currentParkTime.day + 1) - parkOpen
                tSinceMidDay = abs(currentParkTime.hour - 14 + 24)
            validTime.append(1)
            inEMH.append(0)
        else:
            if (emh == "ok") & ((currentParkTime < emhClose) & (currentParkTime > emhOpen)):
                validTime.append(1)
                inEMH.append(1)
                if (emhClose.hour == parkOpen.hour):
                    tSinceOpen = currentParkTime.hour - emhOpen.hour
                    tSinceOpenMinutes = currentParkTime - emhOpen
                    tSinceMidDay = abs(currentParkTime.hour - 14)

                else:
                    if currentParkTime.hour < parkOpen.hour:
                        tSinceOpen = currentParkTime.hour + 24 - parkOpen.hour
                        tSinceOpenMinutes = currentParkTime.replace(day = currentParkTime.day + 1) - parkOpen
                        tSinceMidDay = abs(currentParkTime.hour - 14 + 24)
                    else:
                        tSinceOpen = currentParkTime.hour - parkOpen.hour
                        tSinceOpenMinutes = currentParkTime - parkOpen
                        tSinceMidDay = abs(currentParkTime.hour - 14)
            else:
                validTime.append(0)
                inEMH.append(0)
        timeSinceStart.append(tSinceOpen)
        timeSinceMidDay.append(tSinceMidDay)
        timeSinceOpenMinutes.append(tSinceOpenMinutes)


    RideWaits["inEMH"] = inEMH
    RideWaits["validTime"] = validTime
    RideWaits["EMHDay"] = emhDay
    RideWaits["TimeSinceOpen"] = timeSinceStart
    RideWaits["TimeSinceMidday"] = timeSinceMidDay
    RideWaits["MagicHourType"] = magicHourType
    RideWaits["MinutesSinceOpen"] = [x.total_seconds()/60 for x in timeSinceOpenMinutes]
    RideWaits["SimpleStatus"] = pd.Categorical(RideWaits["SimpleStatus"])
    RideWaits = RideWaits[RideWaits["validTime"] == 1]
    #RideWaits["Month"] = RideWaits["Date"].dt.month
    RideWaits["MagicHourType"] = pd.Categorical(RideWaits["MagicHourType"])
    RideWaits["TimeSinceRideOpen"] = (RideWaits["Date"] - RideWaits["OpeningDate"]).dt.days

    return RideWaits
