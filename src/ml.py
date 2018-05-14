from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_predict
import sklearn.metrics
from scipy.stats.stats import pearsonr
import pandas as pd
import numpy as np
from datetime import datetime
import statistics
import matplotlib.pyplot as plt



RideWaits = pd.read_csv("******/DisneyWaits/src/disneyWaitTimes.csv")

def transformData(RideWaits):
    RideWaits["RideId"] = pd.Categorical(RideWaits["RideId"]).codes
    RideWaits["Status"] = pd.Categorical(RideWaits["Status"]).codes
    RideWaits["ParkId"] = pd.Categorical(RideWaits["ParkId"])
    RideWaits["Tier"] = pd.Categorical(RideWaits["Tier"])
    RideWaits["ParkName"] = pd.Categorical(RideWaits["ParkName"])
    RideWaits["IntellectualProp"] = pd.Categorical(RideWaits["IntellectualProp"])
    RideWaits["SimpleStatus"] = pd.Categorical(RideWaits["SimpleStatus"])

    #want to create some more intersting columns:
    #- character experience
    #- involves a princess/IP involved
    #- is it close to a major event?(Anniversary/Christmas/Thanksgiving/Halloween)

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


    RideWaits["inEMH"] = inEMH
    RideWaits["validTime"] = validTime
    RideWaits["EMHDay"] = emhDay
    RideWaits["TimeSinceOpen"] = timeSinceStart
    RideWaits["TimeSinceMidday"] = timeSinceMidDay
    RideWaits["MagicHourType"] = magicHourType
    RideWaits["MagicHourType"] = pd.Categorical(RideWaits["MagicHourType"])
    RideWaits = RideWaits[RideWaits["validTime"] == 1]

    #RideWaits["Month"] = RideWaits["Date"].dt.month
    RideWaits["TimeSinceRideOpen"] = (RideWaits["Date"] - RideWaits["OpeningDate"]).dt.days

    return RideWaits


RideWaits = transformData(RideWaits)
print(RideWaits.info())

keyFeatures = ["Name","MagicHourType", "Tier", "IntellectualProp", "SimpleStatus", "ParkName", "DayOfWeek", "Weekend", "TimeSinceOpen", "CharacterExperience", "TimeSinceMidday", "inEMH", "EMHDay"]
categoryColumns = RideWaits.select_dtypes(include = ['category']).columns
RideWaits["Name"] = pd.Categorical(RideWaits["Name"]).codes
for col in categoryColumns:
    RideWaits[col] = pd.Categorical(RideWaits[col]).codes


print(RideWaits.info())
rf = RandomForestRegressor(random_state = 1, n_estimators = 100)
predictions = cross_val_predict(rf, RideWaits[keyFeatures], RideWaits["Wait"], cv = 5)

rmse = metrics.mean_squared_error(predictions, RideWaits["Wait"])**(1/2)
r2 = metrics.r2_score(predictions, RideWaits["Wait"])
var = metrics.explained_variance_score(predictions,RideWaits["Wait"])
pearsoncorr = pearsonr(predictions, RideWaits["Wait"])
perror = abs(predictions - RideWaits["Wait"])/RideWaits["Wait"]
mperror = statistics.median(perror)
error = abs(predictions - RideWaits["Wait"])
merror = error.mean()

print(rmse)
print(r2)
print(var)
print(pearsoncorr)
print(mperror)
print(statistics.median(error))
print(merror)

fig, ax = plt.subplots(figsize = (20,20))
plt.scatter(RideWaits["Wait"], predictions)
plt.show()

fig,ax = plt.subplots(figsize = (15,15))
plt.scatter(RideWaits["Wait"], error)
plt.show()
