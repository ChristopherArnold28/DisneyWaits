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
            if emhClose.hour == parkOpen.hour:
                magicHourType.append("Morning")
            else:
                magicHourType.append("Night")
        else:
            emh = "none"
            emhDay.append(0)
            magicHourType.append("None")
        if (currentParkTime < parkClose) & (currentParkTime > parkOpen):
            validtime = 1
            inemh = 0
            #print("Current Time is: " + str(currentParkTime) + " and ParkHours are "+ str(parkOpen) +" to " + str(parkClose) + " " +str(validtime))
            tSinceOpen = cTime.hour - parkOpen.hour
            tSinceMidDay = abs(cTime.hour - 14)
            if cTime.hour < parkOpen.hour:
                tSinceOpen = cTime.hour + 24 - parkOpen.hour
                tSinceMidDay = abs(cTime.hour - 14 + 24)
            validTime.append(1)
            inEMH.append(0)
        else:
            if (emh == "ok") & ((currentParkTime < emhClose) & (currentParkTime > emhOpen)):
                validTime.append(1)
                inEMH.append(1)
                if (emhClose.hour == parkOpen.hour):
                    tSinceOpen = cTime.hour - emhOpen.hour
                    tSinceMidDay = abs(cTime.hour - 14)

                else:
                    if cTime.hour < parkOpen.hour:
                        tSinceOpen = cTime.hour + 24 - parkOpen.hour
                        tSinceMidDay = abs(cTime.hour - 14 + 24)
                    else:
                        tSinceOpen = cTime.hour - parkOpen.hour
                        tSinceMidDay = abs(cTime.hour - 14)
            else:
                validTime.append(0)
                inEMH.append(0)
        timeSinceStart.append(tSinceOpen)
        timeSinceMidDay.append(tSinceMidDay)


    RideWaits.loc[:,'inEMH'] = inEMH
    RideWaits.loc[:,'validTime'] = validTime
    RideWaits.loc[:,'EMHDay'] = emhDay
    RideWaits.loc[:,'TimeSinceOpen'] = timeSinceStart
    RideWaits.loc[:,'TimeSinceMidday'] = timeSinceMidDay
    RideWaits.loc[:,'MagicHourType'] = magicHourType
    RideWaits = RideWaits[RideWaits["validTime"] == 1]
    RideWaits.loc[:,'SimpleStatus'] = pd.Categorical(RideWaits["SimpleStatus"])
    #RideWaits["Month"] = RideWaits["Date"].dt.month
    RideWaits.loc[:,'TimeSinceRideOpen'] = (RideWaits["Date"] - RideWaits["OpeningDate"]).dt.days
    RideWaits.loc[:,'MagicHourType'] = pd.Categorical(RideWaits["MagicHourType"])

    return RideWaits
